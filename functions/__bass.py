"""
To be used with a companion fish function like this:

        function refish
            set -l _x (python /tmp/bass.py source ~/.nvm/nvim.sh ';' nvm use iojs); source $_x; and rm -f $_x
        end

"""

from __future__ import print_function

import json
import os
import signal
import subprocess
import sys
import tempfile
import traceback


BASH = 'bash'

SCRIPT_FD = 3
STATE_LOAD_FD = 4

FISH_READONLY = [
    b'PWD', b'SHLVL', b'history', b'pipestatus', b'status', b'version',
    b'FISH_VERSION', b'fish_pid', b'hostname', b'_', b'fish_private_mode'
]

IGNORED = [
    b'PS1', b'XPC_SERVICE_NAME'
]

def ignored(name):
    if name == b'PWD':  # this is read only, but has special handling
        return False
    # ignore other read only variables
    if name in FISH_READONLY:
        return True
    if name in IGNORED or name.startswith(b"BASH_FUNC"):
        return True
    if name.startswith(b'%'):
        return True
    return False

def escape(string):
    return ''.join('\\x{:02x}'.format(b) for b in string).encode()

def comment(string):
    return b'\n'.join([b'# ' + line for line in string.split(b'\n')])

def load_env(env_json):
    env = json.loads(env_json)
    def env_encode(env_str):
        # https://docs.python.org/3/library/os.html#file-names-command-line-arguments-and-environment-variables
        return env_str.encode(sys.getfilesystemencoding(), 'surrogateescape')
    return {env_encode(k): env_encode(v) for k, v in env.items()}

def load_state(state):
    lines = iter(state.splitlines())
    bash_state = []
    function_source = b''
    try:
        while True:
            item = next(lines)
            # stop as soon as we get to the function source
            if item.endswith(b' () '):
                function_source += item + b'\n'
                break
            if item.startswith(b'declare '):
                kind, flags, var = item.split(b' ', 2)
                var = var.partition(b'=')[0]
                # skip environment variables
                if b'x' in flags:
                    continue
                # skip bash preinitialized readonly variables
                if var in [b'BASHOPTS', b'BASH_VERSINFO', b'EUID', b'PPID', b'SHELLOPTS', b'UID']:
                    continue
            bash_state.append(item)
        # the rest is function source, don't try to parse it
        while True:
            function_source += next(lines) + b'\n'
    except StopIteration:
        pass
    return bash_state, function_source

def parse_aliases(bash_state):
    aliases = {}
    for line in bash_state:
        command, rest = line.split(b' ', 1)
        if command != b'alias':
            continue
        k, _, v = rest.partition(b'=')
        aliases[k] = v
    return aliases

def parse_functions(bash_state):
    functions = set()
    for line in bash_state:
        #print(line)
        command, rest = line.split(b' ', 1)
        if command != b'declare':
            continue
        flags, name = rest.split(b' ', 1)
        if b'f' not in flags:
            continue
        functions.add(name)
    return functions

def gen_script():
    # Load initial environment and bash state.
    old_env = dict(os.environb)
    state_file = sys.argv[1]
    with open(state_file, 'rb') as f:
        old_bash_state = f.read()
        parse_aliases(load_state(old_bash_state)[0])

    # Use the following instead of /usr/bin/env to read environment so we can
    # deal with multi-line environment variables (and other odd cases).
    env_reader = "%s -c 'import os,json; print(json.dumps(dict(os.environ)))'" % (sys.executable)

    state_save_r, state_save_w = os.pipe()
    command = 'source "{state_file}"; eval "$@" {state_save}>&- && {{ {env_reader}; alias -p; declare -p; declare -F; complete -p; declare -f; }} >&{state_save}'.format(
        env_reader=env_reader,
        state_file=state_file,
        state_save=state_save_w
    )
    args = [BASH, '--norc', '--noprofile', '-c', command, 'bass'] + sys.argv[2:]
    p = subprocess.Popen(args, pass_fds=[state_save_w])
    os.close(state_save_w)
    with os.fdopen(state_save_r, 'rb') as f:
        new_env = f.readline()
        new_bash_state = f.read()
    if p.wait() != 0:
        raise subprocess.CalledProcessError(p.returncode, p.args)

    new_env = load_env(new_env)
    old_bash_state, _ = load_state(old_bash_state)
    new_bash_state, function_source = load_state(new_bash_state)

    # save the bash internal state in this variable so we can immediately resurrect it next time
    saved_bash_state = b''
    for line in new_bash_state:
        saved_bash_state += line + b'\n'
    saved_bash_state += function_source
    with open(state_file, 'wb') as f:
        f.write(saved_bash_state)

    script_lines = []

    # env vars
    for k, v in new_env.items():
        if ignored(k):
            continue
        v1 = old_env.get(k)
        if not v1:
            script_lines.append(comment(b'adding %s=%s' % (k, v)))
        elif v1 != v:
            script_lines.append(comment(b'updating %s=%s -> %s' % (k, v1, v)))
            # process special variables
            if k == b'PWD':
                script_lines.append(b'cd %s' % escape(v))
                continue
        else:
            continue
        if k == b'PATH':
            value = b' '.join([escape(directory)
                              for directory in v.split(b':')])
        else:
            value = escape(v)
        script_lines.append(b'set -g -x %s %s' % (escape(k), value))

    for var in set(old_env.keys()) - set(new_env.keys()):
        script_lines.append(comment(b'removing %s' % var))
        script_lines.append(b'set -e %s' % escape(var))

    # aliases
    old_aliases = parse_aliases(old_bash_state)
    new_aliases = parse_aliases(new_bash_state)

    for k, v in new_aliases.items():
        v1 = old_aliases.get(k)
        if not v1:
            script_lines.append(comment(b'adding alias %s=%s' % (k, v)))
        elif v1 != v:
            script_lines.append(comment(b'updating alias %s=%s -> %s' % (k, v1, v)))
        else:
            continue
        script_lines.append(b'alias %s %s' % (k, v))

    for alias in set(old_aliases.keys()) - set(new_aliases.keys()):
        script_lines.append(comment(b'removing alias %s' % alias))
        script_lines.append(b'functions -e %s' % escape(alias))

    # functions
    old_functions = parse_functions(old_bash_state)
    new_functions = parse_functions(new_bash_state)
    #print(old_functions, new_functions)
    for function in old_functions - new_functions:
        script_lines.append(comment(b'removing function %s' % function))
        script_lines.append(b'function -e %s' % escape(function))
    for function in new_functions - old_functions:
        script_lines.append(comment(b'adding function %s' % function))
        script_lines.append(b'function %s; bass %s $argv; return $status; end' % (escape(function), escape(function)))

    script = b'\n'.join(script_lines)

    return script

script_file = os.fdopen(SCRIPT_FD, 'wb')

if not sys.argv[1:]:
    script_file.write(b'__bass_usage')
    sys.exit(0)

# Ignore ctrl-c in the parent process, to avoid having the parent exit before
# the child. It will still affect the child process.
signal.signal(signal.SIGINT, signal.SIG_IGN)

try:
    script = gen_script()
except subprocess.CalledProcessError as e:
    sys.exit(e.returncode)
except Exception:
    print('Bass internal error!', file=sys.stderr)
    raise # traceback will output to stderr
else:
    script_file.write(script)
