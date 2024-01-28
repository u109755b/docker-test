from utils.env_generator_template import EnvGenerator
from utils.tenv import tenv_env_data

# TENVEnvGenerator
class TENVEnvGenerator(EnvGenerator):
    # generate nodes
    def generate_nodes(self):
        with open(f"utils/tenv/tenv_00_init.sql") as f:
            init_sql = f.read()
        for i in range(1, self.N+1):
            node_name = f"Peer{i}"
            self._add_node(node_name)
            self._add_init_sql(init_sql, node_name, "00_init.sql")

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
            datalog_dt = tenv_env_data.datalog_dt
            datalog_dt = datalog_dt.replace("dt_name", dt_name)
            self._add_datalog(datalog_dt, node_name, f"01_{dt_name}.dl")
