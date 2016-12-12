# Setup

## Requirements
* npm (node.js)
* python
* pip
* Postgres
* virtualenv
* virtualenvwrapper
    * install global
    * Add following lines to .bashrc/.zshrc
    * export WORKON_HOME=$HOME/.virtualenvs
    * export MSYS_HOME=/c/msys/1.0
    * source /usr/local/bin/virtualenvwrapper.sh
* OSX: console-tools (xcode-select --install)

## Installation

### 1. Run following command within the repository (or run bootstrap.sh)
    * mkvirtualenv scope
    * pip install -r requirements.txt
    * npm install
    * python manage.py bower install --settings=conf.settings.local

    in case there is a problem with the binary:
     "sudo ln -s /usr/bin/nodejs /usr/bin/node"


    * CAUTION: Following commands download around 1.4 GB
    * python -m spacy.en.download all
    * python -m spacy.de.download all

    * CAUTION: In case you get an error "pg_config executable not found" when installing psycopg2 from requirements, you may have to (a) reinstall postgresql using "brew install postgresql" on Mac or "sudo apt-get install libpq-dev python-dev" on Linux/ubuntu

### 2. After install you need environment variables within the virtualenv:
    * Add to .virtualenvs/scope/bin/postactivate
        * export DATABASE_NAME='taskbuster_db'
        * export DATABASE_USER='myusername'
        * export DATABASE_PASSWORD='mypassword'
        * export SECRET_KEY='key's
        * export BROKER_URL=""
        * export EMAIL_HOST_PASSWORD=""
        * export OUT_EMAIL="example@scope.ai"

    * Add to .virtualenvs/scope/bin/predeactivate
        * unset DATABASE_NAME
        * unset DATABASE_USER
        * unset DATABASE_PASSWORD
        * unset SECRET_KEY
        * unset BROKER_URL
        * unset EMAIL_HOST_PASSWORD
        * unset OUT_EMAIL


### 3. Create the last24h_sources table per hand in psql
    * python manage.py dbshell
    * create table last24h_sources (
        id integer PRIMARY KEY,
        name varchar(200),
        url varchar(200)
    );

    shouldn't be necessary anymore!

### 4. Run db migration 
    * python manage.py migrate --fake

    for first time: don't use the fake flag
### 5. Run the server
    * python manage.py runserver
