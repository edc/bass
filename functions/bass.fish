function bass
  set __bash_args $argv
  if test "$__bash_args[1]_" = '-d_'
    set __bass_debug
    set -e __bash_args[1]
  end

  python (dirname (status -f))/__bass.py $__bash_args | read -z __script
  set __errorflag (string sub -s 1 -l 7 "$__script")
  if test "$__script" = '__usage'
    echo "Usage: bass [-d] <bash-command>"
  else if test "x$__errorflag" = 'x__error'
    echo "Bass encountered an error!"
    set __exitcode (string sub -s 9 "$__script")
    set __exitcode (string trim $__exitcode)
    if test -z $__exitcode
      return 1
    else
      return $__exitcode
    end
  else
    echo -e "$__script" | source -
    if set -q __bass_debug
      echo "$__script"
    end
  end
end
