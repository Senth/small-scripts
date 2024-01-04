#!/bin/bash

# Open neovim if it exists, otherwise use regalur vim
if command -v nvim &> /dev/null; then
	nvim "$@"
else
	/usr/bin/vim
fi
