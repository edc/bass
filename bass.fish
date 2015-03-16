function bass
  if test $argv[1] = '-d'
    set __bass_debug
    set __bash_args $argv[2..-1]
  else
    set __bash_args $argv
  end

  set -l __script (python ~/.config/fish/functions/__bass.py $__bash_args)
  if test $__script = '__error'
    echo "Bass encountered an error!"
  else
    source $__script
    if set -q __bass_debug
      cat $__script
    end
    rm -f $__script
  end
end
