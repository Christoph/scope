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
        * export DJANGO_SETTINGS_MODULE=conf.settings.local /deployment

    * Add to .virtualenvs/scope/bin/predeactivate
        * unset DATABASE_NAME
        * unset DATABASE_USER
        * unset DATABASE_PASSWORD
        * unset SECRET_KEY
        * unset BROKER_URL
        * unset EMAIL_HOST_PASSWORD
        * unset OUT_EMAIL
        * unset DJANGO_SETTINGS_MODULE


### 3. For Production
    * Bower requires collectstatic for production, so new packages with bower also need to be collected 
    * If you get rif of an app, collectstatic --clear will get rid of stale static files
    * On the local version, Bower has a bower_components folder at the base_dir level that somehow is not produced in deployment (and is included in .gitignore)

### 4. Run db migration 
    * python manage.py migrate --fake

    for first time: don't use the fake flag
### 5. Run the server
    * python manage.py runserver

## Setting up and testing deployment environment

### 1. Celery and Rabbit
    * add /usr/local/sbin to your path
#### Running locally
    * sudo rabbitmq-server (starts server)
    * sudo rabbitmqctl status (check server status)
    * python manage.py celery -A conf worker --loglevel=info (start celery worker(this is with djcelery))

#### Running on server
    * the running of celery on the server is daemonized through supervisor
        *the config file for supervisor is at /etc/supervisor/conf.d/celeryd.conf
        * there is some mess with virtualenvs and the daemonization process. Essentially I haven't been able to get the ENV variables from the virtualenvwrapper into the supervisord session so they are now reproduced in the above config file. THIs is important for changing any of variables. See also    http://stackoverflow.com/questions/12900402/supervisor-and-environment-variables
        *to restart the supervisor process after some change:
            *sudo supervisorctl reread
            *sudo supervisorctl update
        *to check the status of the supervisor process
            *sudo supervisorctl status celery
            *sudo supervisorctl stop/start/restart celery
        *if there are some problems with missing socket files or some SHUTDOWN STATE error, try "sudo service supervisor stop/start"
        *for running it in the shell
        *sudo /etc/init.d/celeryd start 
        *the config file for celeryd lies at /etc/default/celeryd
    *management of rabbit:
        *sudo rabbitmqctl stop_app/start_app

### 2. Gunicorn

### 3. Nginx


