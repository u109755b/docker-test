import random
import shutil
from utils.env_generator_template import EnvGenerator
from utils import ycsb_env_data

# YCSBEnvGenerator
class YCSBEnvGenerator(EnvGenerator):
    # generate nodes
    def generate_nodes(self):
        for i in range(1, self.N+1):
            shutil.copytree(f'src/{self.benchmark}/Peer', f'{self.output_dir_path}/db/setup_files/Peer{i}')
            self.G.node(f'Peer{i}')
            # self.config['base_table'][f'Peer{i}'] = ['customer']
            self.config['peer_address'][f'Peer{i}'] = f'Peer{i}-proxy:8000'
            # datalog
            shutil.copy(f"utils/ycsb_00_init.sql", f"{self.output_dir_path}/db/setup_files/Peer{i}/00_init.sql")

    # generate edges
    def generate_edges(self):
        # dt
        dt_name = "dt"
        self._add_dejima_table(dt_name)
        # edges
        for i in range(1, self.N+1):
            node_name = f"Peer{i}"
            self._add_edge(dt_name, node_name, ["bt"])
            # datalog
            datalog_dt = ycsb_env_data.datalog_dt
            datalog_dt = datalog_dt.replace("dt_name", dt_name)
            self._add_datalog(datalog_dt, node_name, f"01_{dt_name}.dl")
