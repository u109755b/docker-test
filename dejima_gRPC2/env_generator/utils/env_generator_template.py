import random
from graphviz import Graph
import json
import os
import sys
import shutil
import glob
import subprocess
import re

# add root directory to sys.path
project_root = os.path.dirname(os.path.abspath(__file__))
if project_root not in sys.path:
    sys.path.append(project_root)


# EnvGenerator
class EnvGenerator:
    # get arguments
    def __init__(self, argv):
        self.node_names = []

        try:
            if len(argv) != 3:
                raise Exception("2 arguments required")

            benchmark = argv[1]
            if not benchmark.upper() in ["TPCC", "YCSB"]:
                raise Exception("Benchmark must be 'YCSB' or 'TPCC'")

            N = argv[2]
            if not N.isdigit():
                raise Exception("Invalid argument")

            # B = argv[3]
            # if not B.isdigit():
            #     raise Exception("Invalid argument")

        except Exception as e:
            print(e)
            exit()

        self.benchmark = benchmark.upper()
        self.N = int(N)
        # self.B = B


    # generate basic_graph
    def generate_basic_graph(self):
        # colors
        self.colors = ['#332288', '#88CCEE', '#44AA99', '#117733', '#999933', '#DDCC77', '#CC6677', '#882255', '#AA4499', '#DDDDDD']
        cond_n = len(self.colors)

        # legend
        legend = Graph()
        for i in range(1,cond_n+1):
            g = Graph()
            g.attr(rankdir='LR', rank='same')
            g.node(f'cond{i}', label=f'COND{i}', shape='plaintext')
            g.node(f'ph_cond{i}', label='', shape='plaintext')
            g.edge(f'cond{i}', f'ph_cond{i}', color=self.colors[i-1], style='bold')
            legend.subgraph(g)
        for i in range(1, cond_n):
            legend.edge(f'cond{i}', f'cond{i+1}', style='invis')

        # overall graph G
        self.G = Graph(format='pdf')
        self.G.attr('graph', rankdir='BT')
        self.G.subgraph(legend)


    # create output directory
    def create_output_dir(self):
        self.output_dir_path = f'{self.benchmark}_N{self.N}_V2'

        if os.path.isdir(self.output_dir_path):
            print("A same environment has already been created")
            res = input("Delete the environment and generate new one? (Y or N): ")
            if "Y" in res.upper():
                subprocess.run(f"sudo rm -r {self.output_dir_path}", shell=True)
            else:
                exit()
        os.mkdir(self.output_dir_path)

        shutil.copytree(f'src/{self.benchmark}/db', f'{self.output_dir_path}/db')
        shutil.copytree(f'src/{self.benchmark}/proxy', f'{self.output_dir_path}/proxy')

        self.config = {'dejima_table': {}, 'base_table': {}, 'peer_address': {}}



    """
    ----- Node -----
    """
    # add node
    def _add_node(self, node_name):
        self.node_names.append(node_name)
        self.G.node(node_name)
        self.config['peer_address'][node_name] = f'{node_name}-proxy:8000'
        shutil.copytree(f'src/{self.benchmark}/Peer', f'{self.output_dir_path}/db/setup_files/{node_name}')

    # add init sql
    def _add_init_sql(self, init_sql, node_name, sql_name):
        with open(f"{self.output_dir_path}/db/setup_files/{node_name}/{sql_name}", mode="w") as f:
            f.write(init_sql)

    # generate nodes
    def generate_nodes(self):
        raise Exception("set generate_nodes")


    """
    ----- Edge -----
    """
    # add dejima table
    def _add_dejima_table(self, dt_name, dt_label=None):
        if not dt_label: dt_label = dt_name
        self.G.node(dt_name)
        self.config["dejima_table"][dt_name] = []

    # add edge
    def _add_edge(self, dt_name, node_name, bt_list, dt_label=None, node_label=None):
        if not dt_label: dt_label = dt_name
        if not node_label: node_label = node_name
        # edge for pdf visualization
        self.G.edge(dt_label, node_label, color=random.choice(self.colors), style="bold")
        # config
        self.config["dejima_table"][dt_name].append(node_name)
        if not node_name in self.config['base_table']:
            self.config['base_table'][node_name] = {}
        self.config['base_table'][node_name][dt_name] = bt_list

    # add datalog
    def _add_datalog(self, datalog, node_name, dl_name):
        with open(f"{self.output_dir_path}/db/setup_files/{node_name}/{dl_name}", mode="w") as f:
            f.write(datalog)

    # generate edges
    def generate_edges(self):
        raise Exception("set generate_edges")



    # compile dl to sql
    def compile_dl(self):
        for datalog in glob.glob("{}/db/setup_files/**/*.dl".format(self.output_dir_path), recursive=True):
            sql = "{}.sql".format(datalog[:-3])
            command = "birds -i -e -f {} -o {} --dejima -b src/{}/Peer/dejima_update.sh".format(datalog, sql, self.benchmark)
            print(command)
            subprocess.run(command, shell=True)

    # modify sql for dejima
    def modify_sql(self):
        for filename in glob.glob("{}/db/setup_files/**/01_*.sql".format(self.output_dir_path), recursive=True):
            with open(filename, 'r') as f:
                lines = f.readlines()

            patterns = []
            patterns.append(r'--DELETE FROM public.__dummy__(.*)_detected_deletions;')
            patterns.append(r'--DELETE FROM public.__dummy__(.*)_detected_insertions;')
            patterns.append(r'DROP TABLE IF EXISTS (.*)_detect_update_on_(.*)_flag;')
            replaces = []
            replaces.append([r'DELETE FROM public.__dummy__\1_detected_deletions t where t.txid = $1;'])
            replaces.append([r'DELETE FROM public.__dummy__\1_detected_insertions t where t.txid = $1;'])
            replaces.append([
                r'DROP TABLE IF EXISTS \1_detect_update_on_\2_flag;',
                r'    DROP TABLE IF EXISTS __tmp_delta_del_\1_for_\2;',
                r'    DROP TABLE IF EXISTS __tmp_delta_ins_\1_for_\2;'
            ])
            mask = [True] * len(patterns)

            for i, line in enumerate(lines):
                for j, (pattern, replace) in enumerate(zip(patterns, replaces)):
                    if re.search(pattern, line) and mask[j] == True:
                        replace_string = '\n'.join(replace)
                        lines[i] = re.sub(pattern, replace_string, line)
                        mask[j] = False    

            with open(filename, 'w') as f:
                f.writelines(lines)


    # save data
    def save_data(self):
        # save to dejima_config.json
        with open(self.output_dir_path + '/proxy/dejima_config.json', mode='w', encoding='utf-8') as file:
            json.dump(self.config, file, ensure_ascii=False, indent=2)

        # save to src.dot
        with open(self.output_dir_path + '/src.dot', mode='w', encoding='utf-8') as file:
            file.write(self.G.source)

        # save to graph.pdf
        self.G.render(self.output_dir_path + '/graph', cleanup=True)


    # generate docker-compose.yml
    def generate_docker_compose(self):
        import yaml

        yml = {}
        yml['version'] = '3'

        yml['services'] = {}
        for i, node_name in enumerate(self.node_names):
            peer_name_uc = node_name
            peer_name_lc = node_name.lower()

            # db
            db = yml['services'][f"{peer_name_lc}-db"] = {}
            db['image'] = 'ekayim/dejima-pg'
            db['container_name'] = f"{peer_name_uc}-db"
            # db['ports'] = [f'{50001+i}:5432']
            db['volumes'] = ['./db/postgresql.conf:/etc/postgresql.conf', './db/initialize.sh:/docker-entrypoint-initdb.d/initialize.sh', './db/setup_files:/etc/setup_files']
            db['environment'] = [f'PEER_NAME={peer_name_uc}']
            db['networks'] = {'dejima_net': None}
            db['cap_add'] = ['NET_ADMIN']

            # proxy
            proxy = yml['services'][peer_name_lc+'-proxy'] = {}
            proxy['image'] = 'ouyoshida/dejima-proxy:latest'
            proxy['container_name'] = f"{peer_name_uc}-proxy"
            proxy['command'] = 'python3 /code/server.py'
            proxy['volumes'] = ['./proxy:/code']
            proxy['ports'] = [f'{8001+i}:8000']
            proxy['depends_on'] = [f'{peer_name_lc}-db']
            proxy['environment'] = [f'PEER_NAME={peer_name_uc}']
            proxy['networks'] = {'dejima_net': None}
            proxy['cap_add'] = ['NET_ADMIN']

        yml['networks'] = {'dejima_net': {'driver': 'bridge', 'ipam': {'driver': 'default'}}}

        with open(f"{self.output_dir_path}/docker-compose.yml", mode='w') as f:
            f.write(yaml.dump(yml))

        print("complete")


    # generate environment
    def generate_env(self):
        self.generate_basic_graph()

        self.create_output_dir()
        self.generate_nodes()
        self.generate_edges()

        self.compile_dl()
        self.modify_sql()

        self.save_data()
        self.generate_docker_compose()



# if __name__ == '__main__':
#     env_generator = EnvGenerator(sys.argv)
#     env_generator.generate_env()
