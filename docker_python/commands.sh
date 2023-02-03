#!/usr/bin/bash

command_name=$1

function start(){
    docker-compose up
}

function remove(){
    dockers=$(docker ps -a | grep "docker_python_python3" | awk '{print $1}')
    if [ "$dockers" == "" ]; then
        echo "no dockers found"
        return
    fi
    echo $dockers | xargs docker rm -fv
    echo "removed dockers"
}

if [ $command_name == "start" ]; then
    remove
    start
elif [ $command_name == "remove" ]; then
    remove
fi