set root (dirname (dirname (status -f)))
source $root/functions/bass.fish

bass source $root/test/fixtures/alias.sh
set OUT (k\?)
if [ $OUT = "hello" ]
    echo (set_color green)Success(set_color normal)
else
    echo (set_color red)Failure(set_color normal)
    exit 1
end
