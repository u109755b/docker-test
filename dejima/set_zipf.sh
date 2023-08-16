# parameters
# ----------
# num of peers
N=$1
# num of records
n=$2
# skew factor
t=$3

for i in `seq 1 $N`
do
    curl -s "localhost:$((i+8000))/zipf?theta=${t}&record_num=${n}" >/dev/null
done

echo "finished"
