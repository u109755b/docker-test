#!/usr/bin/bash

function load_ycsb(){
    start_id=1
    echo "load_ycsb ${peer_num} ${record_num}"
    for i in `seq 1 $peer_num`
    do
        curl -s "localhost:$((i+8000))/load?start_id=${start_id}&record_num=${record_num}&step=${peer_num}" >/dev/null
        start_id=$((start_id+1))
        echo "peer ${i} finished"
    done
}


function load_tpcc(){
    echo "load_tpcc ${peer_num}"
    
    echo "local load"
    for i in `seq 1 $peer_num`
    do
        curl -s "localhost:$((i+8000))/localload_TPCC?peer_num=${peer_num}" >/dev/null
        echo "peer ${i} finished"
    done
    
    echo "customer load"
    for i in `seq 1 $peer_num`
    do
        curl -s "localhost:$((i+8000))/customerload_TPCC?peer_num=${peer_num}" >/dev/null
        echo "peer ${i} finished"
    done
}


function load(){
    b_type=${1}
    if [ $b_type == "ycsb" ]; then
        load_ycsb
    elif [ $b_type == "tpcc" ]; then
        load_tpcc
    fi
}


function set_zipf(){
    skew=${1}
    echo "set_zipf ${skew}"

    for i in `seq 1 $peer_num`
    do
        # curl -s "localhost:$((i+8000))/zipf?theta=${skew}&record_num=$((record_num*peer_num))" >/dev/null
        curl -s "localhost:$((i+8000))/change_val?about=zipf&theta=${skew}&record_num=$((record_num*peer_num))" >/dev/null
    done

    echo "finished"
}


function show_lock(){
    echo "show_lock"
    for i in `seq 1 $peer_num`
    do
        curl -s "localhost:$((i+8000))/change_val?about=show_lock" >/dev/null
    done
}


function bench(){
    method=${1:-"2pl"}
    t=${2:-10}    # time (s)
    # threads=1   # num of threads for each peer
    result_file="result_file"

    YmdHMS=`TZ=JST-9 date +%m%d-%H%M%S`
    mkdir -p result
    output_file=result/${result_file}_${YmdHMS}.txt

    echo "bench ${method} ${t}"

    for i in `seq 1 $peer_num`
    do
        for j in `seq $threads`
        do
            if [ $bench_type == "ycsb" ]; then
                (curl -s "localhost:$((i+8000))/ycsb?bench_time=${t}&method=${method}" | cat >> ${output_file}) &
            elif [ $bench_type == "tpcc" ]; then
                (curl -s "localhost:$((i+8000))/tpcc?bench_time=${t}&method=${method}" | cat >> ${output_file}) &
            fi
        done
    done
    sleep ${t}
    sleep $((1+peer_num))

    # calculate result
    # awk '{commit+=$2} END {print commit}' ${output_file} | tee -a ${output_file}

    n=$((peer_num))
    th=$((threads))
    n=$((n*threads))
    sed 's/[()|, ]/ /g; s/\[s\]//g' ${output_file} | awk -v n="$n" '{cn+=$3; cn1+=$4; cn2+=$5; ct+=$6; ct1+=$7; ct2+=$8} 
        END {printf "commit:  %d (%d %d)   %.2f (%.2f %.2f)[s]\n", cn, cn1, cn2, ct/n, ct1/n, ct2/n}'
    sed 's/[()|, ]/ /g; s/\[s\]//g' ${output_file} | awk -v n="$n" '{an+=$10; an1+=$11; an2+=$12; at+=$13; at1+=$14; at2+=$15} 
        END {printf "abort:  %d (%d %d)   %.2f (%.2f %.2f)[s]\n", an, an1, an2, at/n, at1/n, at2/n}'
}


threads=1   # num of threads for each peer
peer_num=20
record_num=100
tx_t=100
test_time=600

default_zipf=0.2     # zipf

bench_type=$1
command_name=$2

function settings(){
    set_zipf $default_zipf
}

# 初期化 - 0
function batch_bench0(){
    load $bench_type
    settings
}
if [ $command_name == "0" ]; then
    batch_bench0
fi

# 単にそれぞれの手法で実行 - 1
function batch_bench1(){
    settings
    echo -e "\n"
    bench "2pl" $tx_t
    echo ""
    bench "frs" $tx_t
    # echo ""
    # bench "hybrid" $tx_t
    # show_lock
}
if [ $command_name == "1" ]; then
    batch_bench1
fi

# zipfの変更 - 2
function batch_bench2(){
    settings
    thetas=(0 0.2 0.4 0.6 0.8 0.99)
    for theta in "${thetas[@]}"; do
        echo -e "\n"
        set_zipf $theta
        bench_rsab "2pl" $tx_t
        echo ""
        bench_rsab "frs" $tx_t
        echo ""
        bench_rsab "hybrid" $tx_t
    done
    show_lock
}
if [ $command_name == "2" ]; then
    batch_bench2
fi

# read_write_rateの変更 - 3
function batch_bench3(){
    settings
    for ((rate = 0; rate <= 80; rate += 20)); do
        echo -e "\n"
        set_read_write_rate $rate
        bench_rsab "2pl" $tx_t
        echo ""
        bench_rsab "frs" $tx_t
        echo ""
    bench_rsab "hybrid" $tx_t
    done
    show_lock
}
if [ $command_name == "3" ]; then
    batch_bench3
fi

# records/Txの変更 - 4
function batch_bench4(){
    settings
    for ((records = 1; records <= 4; records += 1)); do
        echo -e "\n"
        set_records_tx $records
        bench_rsab "2pl" $tx_t
        echo ""
        bench_rsab "frs" $tx_t
        echo ""
    bench_rsab "hybrid" $tx_t
    done
    show_lock
}
if [ $command_name == "4" ]; then
    batch_bench4
fi

# 2次元表の元データ作成 - 5
function batch_bench5(){
    for ((records = 1; records <= 4; records += 1)); do
        default_records_tx=$records
        for (( batch_i = 1; batch_i <= 1; batch_i++ )); do
            batch_bench3
            echo -e "\n"
        done
    done
}
if [ $command_name == "5" ]; then
    batch_bench5
fi




if [ $command_name == "load_rsab" ]; then           # load_rsab 10
    load_rsab $2
elif [ $command_name == "set_zipf" ]; then          # set_zipf 0.5
    set_zipf $2
elif [ $command_name == "set_rate" ]; then          # set_rate 20
    set_read_write_rate $2
elif [ $command_name == "set_records_tx" ]; then    # set_records_tx 4
    set_records_tx $2
elif [ $command_name == "set_query_order" ]; then   # set_query_order OFF
    set_query_order $2
elif [ $command_name == "bench_rsab" ]; then        # bench_rsab frs 1200
    bench_rsab $2 $3
elif [ $command_name == "show_lock" ]; then         # show_lock
    show_lock
fi