#!/usr/bin/env bash
proj_base_dir=/path/to/flask-skeleton
proj_name=flask-skeleton

current_proj=$proj_base_dir/$proj_name

update_file=$proj_base_dir/$proj_name.tar.gz
backup_proj=$current_proj.`date '+%Y-%m-%d_%H:%M:%S'`


cd $proj_base_dir

if [ -f $update_file ]; then
    # stop current process
    cd $current_proj/deploy && ./admin.sh stop all && kill $(cat ./supervisor/pids/supervisord.pid)
    cd $proj_base_dir

    # backup current proj
    mv $current_proj $backup_proj

    # update
    tar xzf $update_file
    cp $backup_proj/app/.env $current_proj/app/.env

    # start process
    cd $current_proj/deploy && ./init.sh
    cd $proj_base_dir

    # delete old proj
    ls | grep `date '+%Y-%m-%d' --date '30 days ago'` | xargs rm -rf
else
    echo no $zip_file
fi

