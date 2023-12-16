function bass
  set -l bash_args $argv
  set -l bass_debug
  if test "$bash_args[1]_" = '-d_'
    set bass_debug true
    set -e bash_args[1]
  end

  if not set -q __bass_state_file
    set -g __bass_state_file (mktemp)
  end

  set -l script_file (mktemp)
  set -l python
  if command -v python3 >/dev/null 2>&1
    set python python3
  else
    set python python
  end
  command $python -u -sS (dirname (status -f))/__bass.py $__bass_state_file $bash_args 3>$script_file
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

function __bass_cleanup --on-event fish_exit
  if set -q __bass_state_file
    command rm $__bass_state_file
  end
end
