# Setup

## Requirements
* npm (node.js)
* python
* pip
* Postgres
* virtualenv
* OSX: console-tools (xcode-select --install)

## Installation

### 1. Run following command within the repository (or run bootstrap.sh)
    * virtualenv -p /usr/bin/python2.7 ENV
    * source ENV/bin/activate
    * pip install -r requirements.txt
    * npm install
    * bower install

    * CAUTION: Following commands download around 1.4 GB
    * python -m spacy.en.download all
    * python -m spacy.de.download all

### 2. After install you need to configure the settings file
    * DB (create db with separate user. host and port are empty if lokal)
    * private key

### 3. Create the last24h_sources table per hand in psql
    * python manage.py dbshell
    * create table last24h_sources (
        id integer PRIMARY KEY,
        name varchar(200),
        url varchar(200)
    );

### 4. Run db migration
    * python manage.py migrate --fake

### 5. Run the server
    * python manage.py runserver
