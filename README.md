# Bass

![](https://travis-ci.org/edc/bass.svg?branch=master)

Bass makes it easy to use utilities written for Bash in [fish shell](https://github.com/fish-shell/fish-shell/).

Regular bash scripts can be used in fish shell just as scripts written in any language with proper shebang or explicitly using the interpreter (i.e. using `bash script.sh`). However, many utilities, such as virtualenv, modify the shell environment and need to be sourced, and therefore cannot be used in fish. Sometimes, counterparts (such as the excellent [virtualfish](http://virtualfish.readthedocs.org/en/latest/)) are created, but that's often not the case.

Bass is created to make it possible to use bash uilities in fish shell without any modification. It works by capturing what environment variables are modified by the utility of interest, and replay the changes in fish.

# Installation

Bass is compatible with fish versions 2.6.0 and later.

## Manual

Use the Makefile.

`make install` will copy two files to `~/.config/fish/functions/`.

`make uninstall` will remove those two files.

Relaunch the shell for the change to take effect.

## Using [Fisher](https://github.com/jorgebucaran/fisher)

```fish
fisher add edc/bass
```

## Using [Fundle](https://github.com/tuvistavie/fundle)

Add

```
fundle plugin 'edc/bass'
```

to your fish config, relaunch the shell and run `fundle install`.

## Using [Oh My Fish](https://github.com/oh-my-fish/oh-my-fish)

```fish
omf install bass
```

# Example

Bass is simple to use. Just prefix your bash utility command with `bass`:

```
> bass export X=3
> echo $X
3
```

Notice that `export X=3` is bash syntax. Bass "transported" the new bash
environment variable back to fish.

Bass has a debug option so you can see what happened:

```
> bass -d export X=4
# updating X=3 -> 4
set -g -x X 4
```

## nvm

Here is a more realistic example, using the excellent
[nvm](https://github.com/creationix/nvm):

```
> bass source ~/.nvm/nvm.sh --no-use ';' nvm use iojs
Now using io.js v1.1.0
```

Note that semicolon is quoted to avoid being consumed by fish.

This example takes advantage of the nvm bash utility to switch to iojs.
After the command, iojs is accessible:

```
> which iojs
/Users/edc/.nvm/versions/io.js/v1.1.0/bin/iojs
```

You can then very easily pack the command as a function and feel more at home:

```
> funced nvm
nvm> function nvm
           bass source ~/.nvm/nvm.sh --no-use ';' nvm $argv
       end

> nvm list
->  iojs-v1.1.0
         system
> nvm ls-remote
        v0.1.14
        v0.1.15
...
```

(`--no-use` is an important option to `nvm.sh`. See [#13](https://github.com/edc/bass/issues/13) for background.)

# Caveats

At the moment, Bass may or may not work with your favorite interactive utilities, such as ssh-add. Reopen and add a comment to [#14](https://github.com/edc/bass/issues/14) if you encounter an issue related to that.
