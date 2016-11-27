#!/bin/sh

# Create virtual ENV
mkvirtualenv scope

# Install all requirements
pip install -r requirements.txt
npm install
python manage.py bower install --settings=conf.settings.local

# Finalize installations
./node_modules/modernizr/bin/modernizr -c node_modules/modernizr/lib/config-all.json
