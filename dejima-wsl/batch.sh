# TODO
# This script doesn't work properly
# -----
# default parameter
# Skew facotr = 0.8
# Prop Rate = 90%

function change_peer_num () {
    cd env_generator
    ./replace.sh  N$1_*
    cd ..
}

function load () {
    ./load.sh $1 1000 1
    ./load.sh $1 1000 $(($1*1000+1))
}

function do_with_N () {
    change_peer_num $1
    ./chprop.sh 100 90
    docker-compose up -d
    sleep 60
    load $1
    ./set_zipf.sh $1 $(($1*2000)) 0.8
    sleep 5
    ./bench.sh $1 600 N$1_newdef_$2 1
    docker-compose down
    docker volume prune -f
}

function do_with_Skew () {
    docker-compose up -d
    sleep 60
    load 30
    ./set_zipf.sh 30 60000 $1
    sleep 5
    ./bench.sh 30 600 Skew$1_newdef_$2 1
    docker-compose down
    docker volume prune -f
}

function do_with_P () {
    change_peer_num 30
    ./chprop.sh 100 $1
    docker-compose up -d
    sleep 60
    load 30
    ./set_zipf.sh 30 60000 0.8
    sleep 5
    ./bench.sh 30 600 P$1_newdef_$2 1
    docker-compose down
    docker volume prune -f
}

# Prop Rate
./chmet.sh two_pl
do_with_P 20 new
