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
import traceback


BASH = 'bash'

FISH_READONLY = [
    'PWD', 'SHLVL', 'history', 'pipestatus', 'status', 'version',
    'FISH_VERSION', 'fish_pid', 'hostname', '_', 'fish_private_mode'
]

IGNORED = [
 'PS1', 'XPC_SERVICE_NAME'
]

def ignored(name):
    if name == 'PWD':  # this is read only, but has special handling
        return False
    # ignore other read only variables
    if name in FISH_READONLY:
        return True
    if name in IGNORED or name.startswith("BASH_FUNC"):
        return True
    return False

def escape(string):
    # use json.dumps to reliably escape quotes and backslashes
    return json.dumps(string).replace(r'$', r'\$')

def comment(string):
    return '\n'.join(['# ' + line for line in string.split('\n')])

def gen_script():
    # Use the following instead of /usr/bin/env to read environment so we can
    # deal with multi-line environment variables (and other odd cases).
    env_reader = "python -c 'import os,json; print(json.dumps({k:v for k,v in os.environ.items()}))'"
    args = [BASH, '-c', env_reader]
    output = subprocess.check_output(args, universal_newlines=True)
    old_env = output.strip()

    pipe_r, pipe_w = os.pipe()
    if sys.version_info >= (3, 4):
      os.set_inheritable(pipe_w, True)
    command = 'eval $1 && ({}; alias) >&{}'.format(
        env_reader,
        pipe_w
    )
    args = [BASH, '-c', command, 'bass', ' '.join(sys.argv[1:])]
    subprocess.Popen(args, universal_newlines=True, close_fds=False)
    os.close(pipe_w)
    with os.fdopen(pipe_r) as f:
        new_env = f.readline()
        alias = f.read()
    new_env = new_env.strip()

    old_env = json.loads(old_env)
    new_env = json.loads(new_env)

    script_lines = []

    for k, v in new_env.items():
        if ignored(k):
            continue
        v1 = old_env.get(k)
        if not v1:
            script_lines.append(comment('adding %s=%s' % (k, v)))
        elif v1 != v:
            script_lines.append(comment('updating %s=%s -> %s' % (k, v1, v)))
            # process special variables
            if k == 'PWD':
                script_lines.append('cd %s' % escape(v))
                continue
        else:
            continue
        if k == 'PATH':
            value = ' '.join([escape(directory)
                              for directory in v.split(':')])
        else:
            value = escape(v)
        script_lines.append('set -g -x %s %s' % (k, value))

    for var in set(old_env.keys()) - set(new_env.keys()):
        script_lines.append(comment('removing %s' % var))
        script_lines.append('set -e %s' % var)

    script = '\n'.join(script_lines)

    return script + '\n' + alias

script_file = os.fdopen(3, 'w')

if not sys.argv[1:]:
    print('__bass_usage', file=script_file, end='')
    sys.exit(0)

try:
    script = gen_script()
except subprocess.CalledProcessError as e:
    sys.exit(e.returncode)
except Exception:
    print('Bass internal error!', file=sys.stderr)
    raise # traceback will output to stderr
except KeyboardInterrupt:
    signal.signal(signal.SIGINT, signal.SIG_DFL)
    os.kill(os.getpid(), signal.SIGINT)
else:
    script_file.write(script)
