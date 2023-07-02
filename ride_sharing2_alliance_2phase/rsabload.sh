# parameters
# ----------

# num of alliances
alliance_num=$1
# num of providers
provider_num=$2
# num of records for each peer's insert
n=$3
# start id
start_id=$4

for i in `seq 1 $provider_num`
do
		curl -s "localhost:$((alliance_num+i+8000))/load_rsab_provider?start_id=${start_id}&record_num=${n}&step=${provider_num}" >/dev/null
		start_id=$((start_id+1))
done

# for i in `seq 1 $alliance_num`
# do
# 		curl -s "localhost:$((i+8000))/load_rsab_alliance?start_id=${start_id}&record_num=${n}&step=${provider_num}" >/dev/null
# 		start_id=$((start_id+1))
# done

echo "finished"
