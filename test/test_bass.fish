source (dirname (status -f))/../functions/bass.fish

function testfail
	set -l s $argv
	if test $s -ne 0
	    echo (set_color red)failed: bass exited with status $s(set_color normal)
		exit 1
	else
		echo (set_color green)Success(set_color normal)
	end
end

bass 
testfail $status

bass -d
testfail $status

bass -d export X=3
testfail $status

bass export X=3
testfail $status

if test $status -ne 0
	echo (set_color red)failed: bass exited with status $status(set_color normal)
	exit 1
end

if test -z "$X"
	echo (set_color red)failed: $X should be set(set_color normal)
	exit 1
end

echo (set_color green)Success(set_color normal)
