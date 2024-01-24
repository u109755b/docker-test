from experiment.experiment import Experiment

class ExperimentYCSB(Experiment):
    # show parameters
    def show_parameter(self):
        print(f"ycsb_start_id: {self.yscb_start_id}")
        print(f"ycsb_record_num: {self.ycsb_record_num}")


    # load data
    def load_data(self):
        print("load_ycsb {} {} {}".format(self.yscb_start_id, self.ycsb_record_num, self.peer_num))

        data = {
            "bench_name": self.bench_name,
            "start_id": self.yscb_start_id,
            "record_num": self.ycsb_record_num,
            "step": self.peer_num,
        }

        for i in range(self.peer_num):
            peer_name = f"Peer{i+1}"
            self.base_load(peer_name, data)
            data["start_id"] += 1
