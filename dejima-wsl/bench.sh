# parameters
# ----------
# num of peers
N=$1
# time (s)
t=$2
# method
method=$3
# # of threads for each peer
threads=$4
# result file name
result_file=$5

YmdHMS=`TZ=JST-9 date +%m%d-%H%M%S`
mkdir -p result
output_file=result/${result_file}_${YmdHMS}.txt

for i in `seq 1 $N`
do
    for j in `seq $threads`
    do
	(curl -s "localhost:$((i+8000))/ycsb?bench_time=${t}&method=${method}" | cat >> ${output_file}) &
    done
done
sleep ${t}
sleep 5

# calculate result
awk '{commit+=$2} END {print commit}' ${output_file} | tee -a ${output_file}
