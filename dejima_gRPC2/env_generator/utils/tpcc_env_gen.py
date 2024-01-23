import random
import shutil
from utils.env_generator_template import EnvGenerator
from utils import tpcc_env_data

# TPCCEnvGenerator
class TPCCEnvGenerator(EnvGenerator):
    # generate nodes
    def generate_nodes(self):
        for i in range(1, self.N+1):
            shutil.copytree(f'src/{self.benchmark}/Peer', f'{self.output_dir_path}/db/setup_files/Peer{i}')
            self.G.node(f'Peer{i}')
            # self.config['base_table'][f'Peer{i}'] = ['customer']
            self.config['peer_address'][f'Peer{i}'] = f'Peer{i}-proxy:8000'
            # datalog
            shutil.copy(f"utils/tpcc_00_init.sql", f"{self.output_dir_path}/db/setup_files/Peer{i}/00_init.sql")

    # generate edges
    def generate_edges(self):
        # d_customer
        dt_name = "d_customer"
        self._add_dejima_table(dt_name)
        # edges
        for i in range(1, self.N+1):
            node_name = f"Peer{i}"
            self._add_edge(dt_name, node_name, ["customer"])
            # datalog
            datalog_customer = tpcc_env_data.datalog_customer
            datalog_customer = datalog_customer.replace("dt_name", dt_name)
            self._add_datalog(datalog_customer, node_name, f"01_{dt_name}.dl")

        # d_stock
        dt_name = "d_stock"
        self._add_dejima_table(dt_name)
        # edges
        for i in range(1, self.N+1):
            node_name = f"Peer{i}"
            self._add_edge(dt_name, node_name, ["stock"])
            # datalog
            datalog_customer = tpcc_env_data.datalog_stock
            datalog_customer = datalog_customer.replace("dt_name", dt_name)
            self._add_datalog(datalog_customer, node_name, f"01_{dt_name}.dl")
