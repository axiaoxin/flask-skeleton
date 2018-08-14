#!/usr/bin/env bash
proj_base_dir=/path/to/deploy
proj_name=flask-skeleton

current_proj=$proj_base_dir/$proj_name


echo stopping all...
$current_proj/deploy/admin.sh stop all
pkill -f $current_proj/deploy/venv/bin/supervisord

echo move current proj
mv $current_proj $current_proj-removed

echo rollbacking proj...
previous_proj=$(find $proj_base_dir -maxdepth 1 -type d -name "$proj_name.*" | head -n 1)
mv $previous_proj $current_proj

echo starting proj...
export PROJECT_ROOT_PATH=$(dirname $(dirname $(readlink -f $0)))
$PROJECT_ROOT_PATH/deploy/venv/bin/supervisord -c $PROJECT_ROOT_PATH/deploy/supervisor/supervisord.conf
