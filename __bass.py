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
import tempfile


BASH = 'bash'


def gen_script():
    divider = '-__-__-__bass___-env-output-__bass_-__-__-__-__'

    args = [BASH, '-c', 'env']
    output = subprocess.check_output(args, universal_newlines=True)
    old_env = output.splitlines()

    command = '{}; echo "{}"; env'.format(' '.join(sys.argv[1:]), divider)
    args = [BASH, '-c', command]
    output = subprocess.check_output(args, universal_newlines=True)
    stdout, new_env = output.split(divider, 1)
    new_env = new_env.lstrip().splitlines()

    new_env = [line for line in new_env if '{' not in line and '}' not in line]

    old_env = dict([line.split('=', 1) for line in old_env])
    new_env = dict([line.split('=', 1) for line in new_env])

    skips = ['PS1', 'SHLVL', 'XPC_SERVICE_NAME']

    with tempfile.NamedTemporaryFile('w', delete=False) as f:
        for line in stdout.splitlines():
            f.write("printf '%s\\n'\n" % line)
        for k, v in new_env.items():
            if k in skips:
                continue
            v1 = old_env.get(k)
            if not v1:
                f.write('# adding %s=%s\n' % (k, v))
            elif v1 != v:
                f.write('# updating %s=%s -> %s\n' % (k, v1, v))
                # process special variables
                if k == 'PWD':
                    f.write('cd "%s"' % v)
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
            f.write('set -g -x %s %s\n' % (k, value))

    return f.name

try:
    name = gen_script()
except Exception as e:
    sys.stderr.write(str(e) + '\n')
    print('__error')
else:
    print(name)
