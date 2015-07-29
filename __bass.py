"""
To be used with a companion fish function like this:

        function refish
            set -l _x (python /tmp/bass.py source ~/.nvm/nvim.sh ';' nvm use iojs); source $_x; and rm -f $_x
        end

"""

import os
import subprocess
import sys
import tempfile


def gen_script():
    fd, name = tempfile.mkstemp()

    divider = '-__-__-__bass___-env-output-__bass_-__-__-__-__'

    old_env = os.popen('/bin/bash -c "env"', 'r').read().splitlines()

    command = '{}; echo "{}"; env'.format(' '.join(sys.argv[1:]), divider)
    stdout, new_env = (subprocess
                       .check_output(['bash', '-c', command])
                       .split(divider, 1))
    new_env = new_env.lstrip().splitlines()

    new_env = [line for line in new_env if '{' not in line and '}' not in line]

    old_env = dict([line.split('=', 1) for line in old_env])
    new_env = dict([line.split('=', 1) for line in new_env])

    skips = ['PS1', 'SHLVL', 'XPC_SERVICE_NAME']

    with os.fdopen(fd, 'w') as f:
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
                value = v.replace(':', ' ')
            else:
                value = '"%s"' % v.replace('"', '\"')
            f.write('set -g -x %s %s\n' % (k, value))

    return name

try:
    name = gen_script()
except Exception as e:
    sys.stderr.write(str(e) + '\n')
    print '__error'
else:
    print name
