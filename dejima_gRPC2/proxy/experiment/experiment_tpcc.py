from experiment.experiment import Experiment

class ExperimentTPCC(Experiment):
    # show parameters
    def show_parameter(self):
        print(f"tpcc_record_num: {self.tpcc_record_num}")


    # load data
    def load_data(self):
        print("load_tpcc {}".format(self.peer_num))

        data = {
            "bench_name": self.bench_name,
            "peer_num": self.peer_num,
            "peer_idx": 1,
        }

        print("local load")
        data["data_name"] = "local"
        for i in range(self.peer_num):
            peer_name = f"Peer{i+1}"
            self.base_load(peer_name, data)
            data["peer_idx"] += 1

        print("stock load")
        data["peer_idx"] = 1
        data["data_name"] = "stock"
        for i in range(self.peer_num):
            peer_name = f"Peer{i+1}"
            self.base_load(peer_name, data)
            data["peer_idx"] += 1

        print("customer load")
        data["data_name"] = "customer"
        for i in range(self.peer_num):
            peer_name = f"Peer{i+1}"
            self.base_load(peer_name, data)
