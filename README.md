flask-skeleton
--------------
![proj-icon](https://raw.githubusercontent.com/axiaoxin/flask-skeleton/master/app/static/img/favicon.ico)

[![Build Status](https://travis-ci.org/axiaoxin/flask-skeleton.svg?branch=master)](https://travis-ci.org/axiaoxin/flask-skeleton)
[![Codacy Badge](https://api.codacy.com/project/badge/Grade/1021dd91bdf54db797485cb1ac6f2cb9)](https://app.codacy.com/app/axiaoxin/flask-skeleton?utm_source=github.com&utm_medium=referral&utm_content=axiaoxin/flask-skeleton&utm_campaign=Badge_Grade_Dashboard)
![version-badge](https://img.shields.io/github/release/axiaoxin/flask-skeleton.svg)
![downloads](https://img.shields.io/github/downloads/axiaoxin/flask-skeleton/total.svg)
![license](https://img.shields.io/github/license/axiaoxin/flask-skeleton.svg)
![issues](https://img.shields.io/github/issues/axiaoxin/flask-skeleton.svg)
[![Say Thanks!](https://img.shields.io/badge/Say%20Thanks-!-1EAEDB.svg)](https://saythanks.io/to/axiaoxin)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](https://github.com/axiaoxin/flask-skeleton/pulls)


The goal is to do business logic development without paying attention to the organization of the flask project
and integration of common tools, no need to write repeatedly.


## Dependencies

- python 2.7
- flask
- peewee
- python-decouple
- redis
- celery
- cerberus
- requests
- ujson
- pyDes
- redis-py-cluster
- Flask-Mail
- gunicorn
- gevent
- raven
- supervisor
- flasgger
- Flask-FlatPages
- flower
- pytest


# Feature

- Clear code organization.
- Validation of production environment.
- Flexible and rich configuration, decoupled by `.env` file
- Respond unified json structure with `code` `msg` `data` fields, and support custom json key's naming style
- Detailed and leveled log, provide a logger easy to log in file by loglevel or in console, request log with requestid and peewee orm sql log, log function call detail info.
- Support redis single client, sentinel client and cluster client.
- Support request rate limit
- Support sentry to collect error log
- Support auto cached the request result
- Provide redis lock
- Integration of celery for async tasks and cron tasks
- Support swagger to auto generate the api docs
- Support flatpages
- Support send email
- Integration of requests for http client, cerberus for validator params, ujson for speed up json parsing.
- Support auto reconnection mysql to support mysql's high availability
- Provide some common tool like retrying or stringcase convert and others in `utils`
- Provice a convenient deploy admin tool


## Develop run

    virtualenv venv
    source venv/bin activate
    pip install -r requirements.txt

    python apiserver.py

## Deploy

    . ./deploy/init.sh

## Docs

Running the server, you can visit the online docs

Static docs: <http://localhost:5000/docs>

API docs: <http://localhost:5000/apidocs>

# How to develop API with flask-skeleton

First, clone the flask-skeleton and install requirements

    git clone git@github.com:axiaoxin/flask-skeleton.git
    cd flask-skeleton
    . ./deploy/init.sh

the `init.sh` will deploy the service by gunicorn and supervisor on your server, it will auto running the server, the `deploy/admin.sh` can do `restart` `stop` `start`.

Second, regisger blueprint in `apiserver.py`, and write your blueprint in `apis` directory

# Develop suggestions

- write apis as blueprint
- blueprint is made up of `routes.py` `views.py` `handlers.py`
- write database orm model in `app/models`
- add default settings in `app/settings.py` support `python-decouple`, change settings by `.env` file
- add third party service in `app/services.py`
- common tools save in `app/utils`
- put your docs in `app/templates/docs`
- write tests
