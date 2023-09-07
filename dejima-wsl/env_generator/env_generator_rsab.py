import random
from graphviz import Graph
import json
import os
import sys

if len(sys.argv) != 3:
    print("2 argument required")
    exit()
benchmark = "RSAB"
N = sys.argv[1]
if not N.isdigit():
    print("Invalid argument.")
    exit()
B = sys.argv[2]
if not B.isdigit():
    print("Invalid argument.")
    exit()
N = int(N)
if N <= 5:
    print("N must be over 5")
    exit()

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
output_dir_path = '{}_N{}_B{}'.format(benchmark, N, B)
if os.path.isdir(output_dir_path):
    print("A same environment has already been created")
    exit()
os.mkdir(output_dir_path)

config = {'dejima_table': {}, 'base_table': {}, 'peer_address': {}}

G = Graph(format='pdf')
G.attr('graph', rankdir='BT')

birds_sqls = {"alliance": [], "provider": []}
for j in range(1,cond_n+1):
    with open("src/{}/dnum_cond{}_al.sql".format(benchmark,j)) as f:
        birds_sqls["alliance"].append(f.read())
    with open("src/{}/dnum_cond{}_pr.sql".format(benchmark,j)) as f:
        birds_sqls["provider"].append(f.read())

# Alliance
for i in range(1, 5+1):
    os.mkdir(output_dir_path + "/Peer{}".format(i))
    with open(output_dir_path + "/Peer{}".format(i) + "/basetable_list.txt", mode="w") as f:
        f.write("mt\n")
    with open("src/{}/00_init_al.sql".format(benchmark)) as f:
        with open(output_dir_path + "/Peer{}".format(i) + "/00_init_al.sql", mode="w") as new_f:
            new_f.write(f.read())
    G.node(str(i))
    config['base_table']['Peer{}'.format(i)] = ['mt']
    config['peer_address']['Peer{}'.format(i)] = 'Peer{}-proxy:8000'.format(i)
    
# Provider
for i in range(6,N+1):
    os.mkdir(output_dir_path + "/Peer{}".format(i))
    with open(output_dir_path + "/Peer{}".format(i) + "/basetable_list.txt", mode="w") as f:
        f.write("bt\n")
    with open("src/{}/00_init_pr.sql".format(benchmark)) as f:
        with open(output_dir_path + "/Peer{}".format(i) + "/00_init_pr.sql", mode="w") as new_f:
            new_f.write(f.read())
    G.node(str(i))
    config['base_table']['Peer{}'.format(i)] = ['bt']
    config['peer_address']['Peer{}'.format(i)] = 'Peer{}-proxy:8000'.format(i)
    
    for j in range(1, 5+1):
        if random.randint(0, 1) == 0:
            continue
        cond = random.randint(0, cond_n - 1)
        target_node = str(j)
        G.edge(str(i),target_node, color=colors[cond], style='bold')
        dt_name = 'd{}_{}'.format(target_node,i)
        config['dejima_table'][dt_name] = ['Peer{}'.format(i), 'Peer{}'.format(target_node)]
        with open(output_dir_path + "/Peer{}".format(i) + "/01_{}_pr.sql".format(dt_name), mode="w") as f:
            f.write(birds_sqls["provider"][cond].replace("dnum", dt_name).replace("<border>", B))
        with open(output_dir_path + "/Peer{}".format(target_node) + "/01_{}_al.sql".format(dt_name), mode="w") as f:
            f.write(birds_sqls["alliance"][cond].replace("dnum", dt_name).replace("<border>", B))


with open(output_dir_path + '/dejima_config.json', mode='w', encoding='utf-8') as file:
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
