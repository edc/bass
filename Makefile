all:
	@echo "Run 'make install' to deploy bass to your function directory."

install:
	install -d ~/.config/fish/functions
	install -m644 functions/__bass.py ~/.config/fish/functions
	install -m644 functions/bass.fish ~/.config/fish/functions

uninstall:
	rm -f ~/.config/fish/functions/__bass.py
	rm -f ~/.config/fish/functions/bass.fish

test:
	fish test/test_bass.fish
	fish test/test_dollar_on_output.fish
	fish test/test_trailing_semicolon.fish
	fish test/test_non_zero_returncode.fish

.PHONY: test
