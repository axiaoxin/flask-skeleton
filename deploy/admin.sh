#!/usr/bin/env bash

source $(dirname "$0")/env.sh

source $PROJECT_ROOT_PATH/deploy/venv/bin/activate


function admin()
{
    cmd=$1
    arg=$2
    supervisorctl -c $PROJECT_ROOT_PATH/deploy/supervisor/supervisord.conf $cmd $arg
}

admin $1 $2
