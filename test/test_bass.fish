source (dirname (status -f))/../functions/bass.fish

bass
bass -d
bass -d export X=3
bass export X=3

if test $status -ne 0
	echo 'failed: bass exited with status' $status
	exit 1
end

if test -z "$X"
	echo 'failed: $X should be set'
	exit 1
end

echo 'Success'
