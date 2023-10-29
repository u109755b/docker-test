#!/usr/bin/bash

command_name=$1

function start(){
    cd ${1}
    docker-compose up
    # cd ../../
}

function remove(){
    dockers=$(docker ps -a | grep "Peer" | awk '{print $1}')
    if [ "$dockers" == "" ]; then
        echo "no dockers found"
        return
    fi
    echo $dockers | xargs docker rm -fv
    echo "removed dockers"
}

function update(){
    # cp -r "./proxy" "./env_generator/src/RSAB/"
    # peer_dirs=$(find ./env_generator/RSAB* -maxdepth 0)
    cp -r "./proxy" "./env_generator/src/YCSB/"
    cp -r "./proxy" "./env_generator/src/TPCC/"
    cp -r "./db/postgresql.conf" "./env_generator/src/YCSB/db/postgresql.conf"
    cp -r "./db/postgresql.conf" "./env_generator/src/TPCC/db/postgresql.conf"
    ycsb_peer_dirs=$(find ./env_generator/YCSB* -maxdepth 0)
    tpcc_peer_dirs=$(find ./env_generator/TPCC* -maxdepth 0)
    peer_dirs="$ycsb_peer_dirs $tpcc_peer_dirs"
    for peer_dir in $peer_dirs; do
        cp "${peer_dir}/proxy/dejima_config.json" "${peer_dir}/dejima_config.json"
        cp -r "./proxy" "${peer_dir}"
        mv "${peer_dir}/dejima_config.json" "${peer_dir}/proxy/dejima_config.json"
        cp -r "./db/postgresql.conf" "${peer_dir}/db/postgresql.conf"
    done
    echo "updated YCSB and TPCC files"
}


if [ $command_name == "start" ]; then
    remove
    update
    start $2
elif [ $command_name == "remove" ]; then
    remove
    update
elif [ $command_name == "update" ]; then
    update
fi