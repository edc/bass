"""
To be used with a companion fish function like this:

        function refish
            set -l _x (python /tmp/bass.py source ~/.nvm/nvim.sh ';' nvm use iojs); source $_x; and rm -f $_x
        end

"""

from __future__ import print_function

import json
import subprocess
import sys
import traceback


BASH = 'bash'


def gen_script():
    divider = '-__-__-__bass___-env-output-__bass_-__-__-__-__'

    # Use the following instead of /usr/bin/env to read environment so we can
    # deal with multi-line environment variables (and other odd cases).
    env_reader = "python -c 'import os,json; print(json.dumps({k:v for k,v in os.environ.items()}))'"
    args = [BASH, '-c', env_reader]
    output = subprocess.check_output(args, universal_newlines=True)
    old_env = output.strip()

    command = '{} && (echo "{}"; {}; echo "{}"; alias)'.format(
        ' '.join(sys.argv[1:]),
        divider,
        env_reader,
        divider,
    )
    args = [BASH, '-c', command]
    output = subprocess.check_output(args, universal_newlines=True)
    stdout, new_env, alias = output.split(divider, 2)
    new_env = new_env.strip()

    old_env = json.loads(old_env)
    new_env = json.loads(new_env)

    skips = ['PS1', 'SHLVL', 'XPC_SERVICE_NAME']

    script_lines = []

    for line in stdout.splitlines():
        script_lines.append("printf %s;printf '\\n'" % json.dumps(line))
    for k, v in new_env.items():
        if k in skips:
            continue
        v1 = old_env.get(k)
        if not v1:
            script_lines.append('# adding %s=%s' % (k, v))
        elif v1 != v:
            script_lines.append('# updating %s=%s -> %s' % (k, v1, v))
            # process special variables
            if k == 'PWD':
                script_lines.append('cd %s' % json.dumps(v))
                continue
        else:
            continue
        if k == 'PATH':
            # use json.dumps to reliably escape quotes and backslashes
            value = ' '.join([json.dumps(directory)
                              for directory in v.split(':')])
        else:
            # use json.dumps to reliably escape quotes and backslashes
            value = json.dumps(v)
        script_lines.append('set -g -x %s %s' % (k, value))
    script = '\n'.join(script_lines)

    return script + '\n' + alias

if not sys.argv[1:]:
    print('__usage', end='')
    sys.exit(0)

try:
    script = gen_script()
except subprocess.CalledProcessError as e:
    print('exit code:', e.returncode, file=sys.stderr)
    print('__error', end='')
except Exception as e:
    print('unknown error:', str(e), file=sys.stderr)
    traceback.print_exc(10, file=sys.stderr)
    print('__error', end='')
else:
    print(script, end='')
