set root (dirname (dirname (status -f)))
source $root/functions/bass.fish

bass false

if test $status -ne 1
	echo (set_color red)failed: bass exited with status $status when 1 is expected(set_color normal)
	exit 1
end

echo (set_color green)Success(set_color normal)
