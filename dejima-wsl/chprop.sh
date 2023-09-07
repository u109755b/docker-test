before=$1
after=$2
sed -i "s/<  $before/<  $after/g" db/setup_files/Peer*/01_d*.sql
