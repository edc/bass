function bass
  set -l bash_args $argv
  set -l bass_debug
  if test "$bash_args[1]_" = '-d_'
    set bass_debug true
    set -e bash_args[1]
  end

  set -l script_file (mktemp)
  set -l python "python"
  if command -v python3 >/dev/null 2>&1
      set python "python3"
  end
  command $python (dirname (status -f))/__bass.py $bash_args 3>$script_file
  set -l bass_status $status
  if test $bass_status -ne 0
    return $bass_status
  end

  if test -n "$bass_debug"
    cat $script_file
  end
  source $script_file
  command rm $script_file
end

function __bass_usage
  echo "Usage: bass [-d] <bash-command>"
end
