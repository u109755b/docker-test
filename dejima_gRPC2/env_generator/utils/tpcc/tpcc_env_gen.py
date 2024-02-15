from utils.env_generator_template import EnvGenerator
from utils.tpcc import tpcc_env_data

# TPCCEnvGenerator
class TPCCEnvGenerator(EnvGenerator):
    # generate nodes
    def generate_nodes(self):
        with open(f"utils/tpcc/tpcc_00_init.sql") as f:
            init_sql = f.read()
        for i in range(1, self.N+1):
            node_name = f"Peer{i}"
            self._add_node(node_name)
            self._add_init_sql(init_sql, node_name, "00_init.sql")

    # generate edges
    def generate_edges(self):
        # d_warehouse
        dt_name = "d_warehouse"
        self._add_dejima_table(dt_name)
        # edges
        for i in range(1, self.N+1):
            node_name = f"Peer{i}"
            self._add_edge(dt_name, node_name, ["warehouse"])
            # datalog
            datalog = tpcc_env_data.datalog_warehouse
            datalog = datalog.replace("dt_name", dt_name)
            self._add_datalog(datalog, node_name, f"01_{dt_name}.dl")

        # d_district
        dt_name = "d_district"
        self._add_dejima_table(dt_name)
        # edges
        for i in range(1, self.N+1):
            node_name = f"Peer{i}"
            self._add_edge(dt_name, node_name, ["district"])
            # datalog
            datalog = tpcc_env_data.datalog_district
            datalog = datalog.replace("dt_name", dt_name)
            self._add_datalog(datalog, node_name, f"01_{dt_name}.dl")

        # d_customer
        dt_name = "d_customer"
        self._add_dejima_table(dt_name)
        # edges
        for i in range(1, self.N+1):
            node_name = f"Peer{i}"
            self._add_edge(dt_name, node_name, ["customer"])
            # datalog
            datalog = tpcc_env_data.datalog_customer
            datalog = datalog.replace("dt_name", dt_name)
            self._add_datalog(datalog, node_name, f"01_{dt_name}.dl")

        # d_stock
        dt_name = "d_stock"
        self._add_dejima_table(dt_name)
        # edges
        for i in range(1, self.N+1):
            node_name = f"Peer{i}"
            self._add_edge(dt_name, node_name, ["stock"])
            # datalog
            datalog = tpcc_env_data.datalog_stock
            datalog = datalog.replace("dt_name", dt_name)
            self._add_datalog(datalog, node_name, f"01_{dt_name}.dl")
