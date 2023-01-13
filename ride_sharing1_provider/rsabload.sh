# parameters
# ----------

# num of peers
N=$1
# num of records for each peer's insert
n=$2
# start id
start_id=$3
# max hop
max_hop=$4

for i in `seq 1 $N`
do
		curl -s "localhost:$((i+8000))/loadrsab?start_id=${start_id}&record_num=${n}&step=${N}&max_hop=${max_hop}" >/dev/null
		start_id=$((start_id+1))
done

echo "finished"
