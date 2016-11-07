#!/usr/bin/env bash
source $(dirname "$0")/env.sh

# clear
rm -rf $PROJECT_ROOT_PATH/logs
rm -rf $PROJECT_ROOT_PATH/deploy/venv

# create virtual env
virtualenv $PROJECT_ROOT_PATH/deploy/venv
source $PROJECT_ROOT_PATH/deploy/venv/bin/activate
pip install -r $PROJECT_ROOT_PATH/requirements.txt

# create log dir
mkdir $PROJECT_ROOT_PATH/logs


# start supervisord
$PROJECT_ROOT_PATH/deploy/venv/bin/supervisord -c $PROJECT_ROOT_PATH/deploy/supervisor/supervisord.conf
$PROJECT_ROOT_PATH/deploy/venv/bin/supervisorctl -c $PROJECT_ROOT_PATH/deploy/supervisor/supervisord.conf update
