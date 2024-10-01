import random
from utils.env_generator_template import EnvGenerator
from utils.ycsb import ycsb_env_data

# YCSBEnvGenerator
class YCSBEnvGenerator(EnvGenerator):
    # generate nodes
    def generate_nodes(self):
        with open(f"utils/ycsb/ycsb_00_init.sql") as f:
            init_sql = f.read()
        for i in range(1, self.N+1):
            node_name = f"Peer{i}"
            self._add_node(node_name)
            self._add_init_sql(init_sql, node_name, "00_init.sql")

    # generate edges
    def generate_edges(self):
        # # star topology 1 (dt centered)
        # # dt
        # dt_name = "dt"
        # self._add_dejima_table(dt_name)
        # # edges
        # for i in range(1, self.N+1):
        #     node_name = f"Peer{i}"
        #     self._add_edge(dt_name, node_name, ["bt"])
        #     # datalog
        #     datalog_dt = ycsb_env_data.datalog_dt
        #     datalog_dt = datalog_dt.replace("dt_name", dt_name)
        #     self._add_datalog(datalog_dt, node_name, f"01_{dt_name}.dl")

        # # star topology 2 (peer1 centered)
        # for i in range(2, self.N+1):
        #     # dt
        #     dt_name = f"dt1_{i}"
        #     self._add_dejima_table(dt_name)
        #     # edges
        #     node_name1 = f"Peer1"
        #     node_name2 = f"Peer{i}"
        #     self._add_edge(dt_name, node_name1, ["bt"])
        #     self._add_edge(dt_name, node_name2, ["bt"])
        #     # datalog
        #     datalog_dt = ycsb_env_data.datalog_dt
        #     datalog_dt = datalog_dt.replace("dt_name", dt_name)
        #     self._add_datalog(datalog_dt, node_name1, f"01_{dt_name}.dl")
        #     self._add_datalog(datalog_dt, node_name2, f"01_{dt_name}.dl")

        # straight topology
        for i in range(1, self.N):
            # dt
            dt_name = f"dt{i}_{i+1}"
            self._add_dejima_table(dt_name)
            # edges
            node_name1 = f"Peer{i}"
            node_name2 = f"Peer{i+1}"
            self._add_edge(dt_name, node_name1, ["bt"])
            self._add_edge(dt_name, node_name2, ["bt"])
            # datalog
            datalog_dt = ycsb_env_data.datalog_dt
            datalog_dt = datalog_dt.replace("dt_name", dt_name)
            self._add_datalog(datalog_dt, node_name1, f"01_{dt_name}.dl")
            self._add_datalog(datalog_dt, node_name2, f"01_{dt_name}.dl")

        # # random topology
        # for i in range(2, self.N+1):
        #     # dt
        #     node_i = random.randint(1, i-1)
        #     dt_name = f"dt{node_i}_{i}"
        #     self._add_dejima_table(dt_name)
        #     # edges
        #     node_name1 = f"Peer{node_i}"
        #     node_name2 = f"Peer{i}"
        #     self._add_edge(dt_name, node_name1, ["bt"])
        #     self._add_edge(dt_name, node_name2, ["bt"])
        #     # datalog
        #     datalog_dt = ycsb_env_data.datalog_dt
        #     datalog_dt = datalog_dt.replace("dt_name", dt_name)
        #     self._add_datalog(datalog_dt, node_name1, f"01_{dt_name}.dl")
        #     self._add_datalog(datalog_dt, node_name2, f"01_{dt_name}.dl")
