set root (dirname (dirname (status -f)))
source $root/functions/bass.fish

bass false

if test $status -ne 1
	echo 'failed: bass exited with status' $status 'when 1 is expected'
	exit 1
end

echo 'Success'
