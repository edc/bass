install:
	install -d ~/.config/fish/functions
	install __bass.py ~/.config/fish/functions
	install bass.fish ~/.config/fish/functions

uninstall:
	rm -f ~/.config/fish/functions/__bass.py
	rm -f ~/.config/fish/functions/bass.fish
