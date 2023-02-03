# parameters
# ----------

# num of alliances
alliance_num=$1
# num of providers
provider_num=$2
# time (s)
t=$3
# method
method=$4
# # of threads for each peer
threads=$5
# result file name
result_file=$6

YmdHMS=`TZ=JST-9 date +%m%d-%H%M%S`
mkdir -p result
output_file=result/${result_file}_${YmdHMS}.txt

for i in `seq 1 $alliance_num`
do
    for j in `seq $threads`
    do
	    (curl -s "localhost:$((i+8000))/rsab_alliance?bench_time=${t}&method=${method}" | cat >> ${output_file}) &
    done
done

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