import random
from graphviz import Graph
import json
import os
import sys
import shutil
import glob
import subprocess
import data_for_rsab

if len(sys.argv) != 2:
    print("2 argument required")
    exit()
N = sys.argv[1]
if not N.isdigit():
    print("Invalid argument.")
    exit()
N = int(N)
benchmark = "RSAB"

# colors = ['green', 'red', 'blue', 'black', 'orange']
colors = ['#332288', '#88CCEE', '#44AA99', '#117733', '#999933', '#DDCC77', '#CC6677', '#882255', '#AA4499', '#DDDDDD']
cond_n = len(colors)
#cond_n = 5

# legend
legend = Graph()
for i in range(1,cond_n+1):
    g = Graph()
    g.attr(rankdir='LR', rank='same')
    g.node('cond{}'.format(i), label='COND{}'.format(i), shape='plaintext')
    g.node('ph_cond{}'.format(i), label='', shape='plaintext')
    g.edge('cond{}'.format(i), 'ph_cond{}'.format(i), color=colors[i-1], style='bold')
    legend.subgraph(g)
for i in range(1, cond_n):
    legend.edge('cond{}'.format(i), 'cond{}'.format(i+1), style='invis')

# main
output_dir_path = '{}_N{}'.format(benchmark, N)
if os.path.isdir(output_dir_path):
    print("A same environment has already been created")
    exit()
os.mkdir(output_dir_path)

shutil.copytree('src/{}/db'.format(benchmark), '{}/db'.format(output_dir_path))
shutil.copytree('src/{}/proxy'.format(benchmark), '{}/proxy'.format(output_dir_path))

config = {'dejima_table': {}, 'base_table': {}, 'peer_address': {}}

G = Graph(format='pdf')
G.attr('graph', rankdir='BT')
edges = {}

# connect nodes
for i in range(1,N+1):
    shutil.copytree('src/{}/Peer'.format(benchmark), '{}/db/setup_files/Peer{}'.format(output_dir_path, i))
    edges[i] = []
    G.node(str(i))
    config['base_table']['Peer{}'.format(i)] = ['bt']
    config['peer_address']['Peer{}'.format(i)] = 'Peer{}-proxy:8000'.format(i)
    if not i == 1:
        cond = random.randint(0, cond_n - 1)
        target_node = str(random.randint(1,i-1))
        # target_node = str(i-1)
        G.edge(str(i),target_node, color=colors[cond], style='bold')
        dt_name = 'd{}_{}'.format(target_node,i)
        config['dejima_table'][dt_name] = ['Peer{}'.format(i), 'Peer{}'.format(target_node)]
        edges[int(target_node)].append(dt_name)
        edges[i].append(dt_name)

for i in edges:
    # 00_init.sql
    columns = []
    for dt_name in edges[i]:
        columns.append("    {} varchar,".format(dt_name))
    columns = "\n".join(columns)
    with open("{}/db/setup_files/Peer{}/00_init.sql".format(output_dir_path, i), mode="w") as f:
        f.write(data_for_rsab.init_sql.replace("columns", columns))
        
    # 01_dnum.dl
    columns = []
    underscores = []
    dt_names = []
    all_flags = []
    for j, dt_name in enumerate(edges[i]):
        dt_alias = "S{}".format(j+1)
        columns.append("'{}':string".format(dt_name))
        underscores.append("_")
        dt_names.append(dt_alias)
        all_flags.append("{}='false'".format(dt_alias))
    columns_ = ", ".join(columns)
    dt_names_ = ",".join(dt_names)
    underscores_ = ",".join(underscores)
    
    for j, dt_name in enumerate(edges[i]):
        dt_alias = "S{}".format(j+1)
        underscores[j] = dt_alias
        dt_names[j] = "_"
        all_flags[j] = "{}='true'".format(dt_alias)
        
        underscores_dt = ",".join(underscores)
        dt_names_under = ",".join(dt_names)
        all_flags_ = ", ".join(all_flags)
        dt_flag = "{}='true'".format(dt_alias)
        
        with open("{}/db/setup_files/Peer{}/01_{}.dl".format(output_dir_path, i, dt_name), mode="w") as f:
            datalog = data_for_rsab.birds_datalog
            datalog = datalog.replace("underscores_dt", underscores_dt).replace("dt_names_under", dt_names_under)
            datalog = datalog.replace("columns", columns_).replace("underscores", underscores_).replace("dt_names", dt_names_)
            datalog = datalog.replace("dt_flag", dt_flag).replace("all_flags", all_flags_)
            f.write(datalog.replace("dt_name", dt_name))
            
        underscores[j] = "_"
        dt_names[j] = dt_alias
        all_flags[j] = "{}='false'".format(dt_alias)
        
# # 01_dnum.sql
for datalog in glob.glob("{}/db/setup_files/**/*.dl".format(output_dir_path), recursive=True):
    sql = "{}.sql".format(datalog[:-3])
    command = "birds -i -e -f {} -o {} --dejima -b src/{}/Peer/dejima_update.sh".format(datalog, sql, benchmark)
    print(command)
    subprocess.run(command, shell=True)

with open(output_dir_path + '/proxy/dejima_config.json', mode='w', encoding='utf-8') as file:
    json.dump(config, file, ensure_ascii=False, indent=2)

with open(output_dir_path + '/src.dot', mode='w', encoding='utf-8') as file:
    file.write(G.source)

G.subgraph(legend)
G.render(output_dir_path + '/graph', cleanup=True)

# generate docker-compose.yml 

import yaml

yml = {}
yml['version'] = '3'

yml['services'] = {}
for i in range(1,N+1):
    peer_name_uc = "Peer{}".format(i)
    peer_name_lc = "peer{}".format(i)

    # db
    db = yml['services'][peer_name_lc+'-db'] = {}
    db['image'] = 'ekayim/dejima-pg'
    db['container_name'] = peer_name_uc+'-db'
    # db['ports'] = ['{}:5432'.format(50000+i)]
    db['volumes'] = ['./db/postgresql.conf:/etc/postgresql.conf', './db/initialize.sh:/docker-entrypoint-initdb.d/initialize.sh', './db/setup_files:/etc/setup_files']
    db['environment'] = ['PEER_NAME={}'.format(peer_name_uc)]
    db['networks'] = {'dejima_net': None}
    db['cap_add'] = ['NET_ADMIN']

    # proxy
    proxy = yml['services'][peer_name_lc+'-proxy'] = {}
    proxy['image'] = 'ekayim/dejima-proxy:latest'
    proxy['container_name'] = peer_name_uc+'-proxy'
    proxy['command'] = 'gunicorn -b 0.0.0.0:8000 --threads {} server:app'.format(N+10)
    proxy['volumes'] = ['./proxy:/code']
    proxy['ports'] = ['{}:8000'.format(8000+i)]
    proxy['depends_on'] = ['{}-db'.format(peer_name_lc)]
    proxy['environment'] = ['PEER_NAME={}'.format(peer_name_uc)]
    proxy['networks'] = {'dejima_net': None}
    proxy['cap_add'] = ['NET_ADMIN']

yml['networks'] = {'dejima_net': {'driver': 'bridge', 'ipam': {'driver': 'default'}}}

with open(output_dir_path + '/docker-compose.yml', mode='w') as f:
    f.write(yaml.dump(yml))

print("complete")
