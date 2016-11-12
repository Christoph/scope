#!/bin/sh

# Create virtual ENV
virtualenv -p /usr/bin/python2.7 ENV

# Activate the virtualenv
source ENV/bin/activate

# Install all requirements
pip install -r requirements.txt
npm install
bower install

# Finalize installations
./node_modules/modernizr/bin/modernizr -c node_modules/modernizr/lib/config-all.json
