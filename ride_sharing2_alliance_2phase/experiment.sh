#!/usr/bin/bash

alliance_num=2
provider_num=5


function load_rsab(){
    n=${1:-10}  # num of records for each peer's insert (default n is 10)
    start_id=1
    echo "load_rsab ${n}"
    for i in `seq 1 $provider_num`
    do
        curl -s "localhost:$((alliance_num+i+8000))/load_rsab_provider?start_id=${start_id}&record_num=${n}&step=${provider_num}" >/dev/null
        start_id=$((start_id+1))
    done
}


function set_zipf(){
    skew=${1}
    echo "set_zipf ${skew}"
    for i in `seq 0 $((alliance_num+provider_num))`
    do
        curl -s "localhost:$((i+8000))/change_val?about=zipf&theta=${skew}" >/dev/null
    done
}


function set_read_write_rate(){
    rate=${1}
    echo "set_rate ${rate}"
    for i in `seq 0 $((alliance_num+provider_num))`
    do
        curl -s "localhost:$((i+8000))/change_val?about=set_read_write_rate&rate=${rate}" >/dev/null
    done
}


function query_order(){
    on_off=${1}
    echo "query_order ${on_off}"
    for i in `seq 0 $((alliance_num+provider_num))`
    do
        curl -s "localhost:$((i+8000))/change_val?about=query_order&on_off=${on_off}" >/dev/null
    done
}


function show_lock(){
    echo "show_lock"
    for i in `seq 0 $((alliance_num+provider_num))`
    do
        curl -s "localhost:$((i+8000))/change_val?about=show_lock" >/dev/null
    done
}


function bench_rsab(){
    method=${1:-"2pl"}
    t=${2:-10}    # time (s)
    threads=1   # num of threads for each peer
    result_file="result_file"

    YmdHMS=`TZ=JST-9 date +%m%d-%H%M%S`
    mkdir -p result
    output_file=result/${result_file}_${YmdHMS}.txt
    
    echo "bench_rsab ${method} ${t}"

    (curl -s "localhost:$((8000))/rsab_alliance?bench_time=${t}&method=${method}" | cat >> ${output_file}) &

    # for i in `seq 1 1`
    for i in `seq 1 $alliance_num`
    do
        for j in `seq $threads`
        do
            (curl -s "localhost:$((i+8000))/rsab_alliance?bench_time=${t}&method=${method}" | cat >> ${output_file}) &
        done
    done

    # for i in `seq 1 2`
    for i in `seq 1 $provider_num`
    do
        for j in `seq $threads`
        do
            (curl -s "localhost:$((alliance_num+i+8000))/rsab_provider?bench_time=${t}&method=${method}" | cat >> ${output_file}) &
        done
    done

    sleep ${t}
    sleep 5

    # calculate result
    awk '{commit+=$2} END {print commit}' ${output_file} | tee -a ${output_file}
    awk '{commit+=$3} END {print commit}' ${output_file} | tee -a ${output_file}
}



command_name=$1

if [ $command_name == "load_rsab" ]; then       # load_rsab 10
    load_rsab $2
elif [ $command_name == "set_zipf" ]; then      # set_zipf 0.5
    set_zipf $2
elif [ $command_name == "set_rate" ]; then      # set_rate 20
    set_read_write_rate $2
elif [ $command_name == "query_order" ]; then      # query_order OFF
    query_order $2
elif [ $command_name == "bench_rsab" ]; then    # bench_rsab frs 1200
    bench_rsab $2 $3
elif [ $command_name == "show_lock" ]; then
    show_lock
    
elif [ $command_name == "0" ]; then
    load_rsab 10
    set_read_write_rate 50
    query_order "on"
    # bench_rsab "2pl" 10
    # show_lock
elif [ $command_name == "1" ]; then
    set_read_write_rate 20
    # query_order "on"
    bench_rsab "2pl" 120
    show_lock
elif [ $command_name == "2" ]; then
    for ((rate = 0; rate <= 40; rate += 10)); do
        set_read_write_rate $rate
        
        bench_rsab "2pl" 120
        # show_lock
        
        bench_rsab "frs" 120
        # show_lock
    done
    show_lock
fi