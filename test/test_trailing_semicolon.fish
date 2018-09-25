set root (dirname (dirname (status -f)))
source $root/functions/bass.fish

bass (sh $root/test/fixtures/trailing_semicolon.sh)
and if [ "$SEMICOLON_RSTRIPPED" = "1" ]
	echo 'Success'
end
