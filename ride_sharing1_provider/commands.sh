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
    cp -r "./proxy" "./env_generator/src/RSAB/"
    peer_dirs=$(find ./env_generator/RSAB* -maxdepth 0)
    for peer_dir in $peer_dirs; do
        cp "${peer_dir}/proxy/dejima_config.json" "${peer_dir}/dejima_config.json"
        cp -r "./proxy" $peer_dir
        mv "${peer_dir}/dejima_config.json" "${peer_dir}/proxy/dejima_config.json"
    done
    echo "updated RSAB files"
}

function bench(){
    N=$1
    t=$2
    bash rsabbench.sh ${N} ${t} 2pl 1 result_file
    sleep ${t+20}
    bash rsabbench.sh ${N} ${t} frs 1 result_file
    sleep ${t+20}
    bash rsabbench.sh ${N} ${t} hybrid 1 result_file
    sleep ${t+10}
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
elif [ $command_name == "bench" ]; then
    bench $2 $3
fi