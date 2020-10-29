set root (dirname (dirname (status -f)))
source $root/functions/bass.fish

bass source $root/test/fixtures/alias.sh
set OUT (k\?)
if [ $OUT = "hello" ]
    echo 'Success'
else
    exit 1
end
