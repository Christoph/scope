#!/bin/sh

# Install virtual env
pip install virtualenv

# Create virtual ENV
virtualenv ENV

# Activate the virtualenv
source ENV/bin/activate

# Install all requirements
pip install -r requirements.txt
npm install
bower install

# Finalize installations
./node_modules/modernizr/bin/modernizr -c node_modules/modernizr/lib/config-all.json
