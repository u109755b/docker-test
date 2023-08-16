# parameters
# ----------
# num of peers
# also used for step parameter
N=$1

for i in `seq 1 $N`
do
		curl -s "localhost:$((i+8000))/localload_TPCC?peer_num=$N" >/dev/null
done

for i in `seq 1 $N`
do
		curl -s "localhost:$((i+8000))/customerload_TPCC?peer_num=$N" >/dev/null
done

echo "finished"
