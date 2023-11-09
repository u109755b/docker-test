target_dir=$1
root_dir=`pwd | xargs dirname`
rm -rf ${root_dir}/db/setup_files/*
cp -r ${target_dir}/Peer* ${root_dir}/db/setup_files/
cp ${target_dir}/docker-compose.yml ${root_dir}/
cp ${target_dir}/dejima_config.json ${root_dir}/proxy
