#!/bin/sh

# Create virtual ENV
mkvirtualenv scope

# Install all requirements
pip install -r requirements.txt
npm install
bower install

# Finalize installations
./node_modules/modernizr/bin/modernizr -c node_modules/modernizr/lib/config-all.json