#!/usr/bin/env bash
proj_base_dir=/path/to/deploy
proj_name=flask-skeleton

current_proj=$proj_base_dir/$proj_name

upgrade_file=$proj_base_dir/$proj_name.tar.gz
backup_proj=$current_proj.`date '+%Y-%m-%d_%H:%M:%S'`



if [ -f $upgrade_file ]; then
    # backup current proj
    echo backuping...
    cp -r $current_proj $backup_proj

    # update code
    echo updating code...
    tar xzf $upgrade_file
    echo updating settings...
    cp $backup_proj/app/.env $current_proj/app/.env
    echo updating requirements...
    $current_proj/deploy/venv/bin/pip -Ur $current_proj/requirements.txt
    echo updating supervisor...
    $current_proj/deploy/admin.sh update

    # restart
    echo restarting all...
    $current_proj/deploy/admin.sh restart all

    # delete 7 days ago backup
    echo deleting old backup...
    find $proj_base_dir -maxdepth 1 -type d -name "$proj_name.*" -ctime +7 -exec rm -rf {} \;
else
    echo no $upgrade_file
fi
