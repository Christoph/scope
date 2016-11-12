Requirements:
    - npm (node.js)
    - python
    - pip
    - Postgres

To install all necessary packages and libraries run
    - source bootstrap.sh

After install you need to configure the settings file
    - DB (create db with separate user. host and port are empty if lokal)
    - private key
    - static root

Create the last24h_sources table per hand in psql
    - python manage.py dbshell:
    create table last24h_sources (
        id integer PRIMARY KEY,
        name varchar(200),
        url varchar(200)
    );

After that run 
    - python manage.py migrate --fake

Now you should be able to run the server
    - python manage.py runserver
