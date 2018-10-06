function bass
  set __bash_args $argv
  if test "$__bash_args[1]_" = '-d_'
    set __bass_debug
    set -e __bash_args[1]
  end

  if test -L (status -f)
    set __bass_path (dirname (realpath (status -f)))
    echo $__bass_path
  else
    set __bass_path  (dirname (status -f))
  end

  python $__bass_path/__bass.py $__bash_args | read -z __script

  if test "$__script" = '__usage'
    echo "Usage: bass [-d] <bash-command>"
  else if test "$__script" = '__error'
    echo "Bass encountered an error!"
    return 1
  else
    echo -e "$__script" | source -
    if set -q __bass_debug
      echo "$__script"
    end
  end
end
