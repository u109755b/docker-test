import random
import math
from datetime import datetime
from benchmark.tpcc import tpccutils
import config
import dejima
from dejima import GlobalBencher

class TPCCTxPay(GlobalBencher):
    def _execute(self):
        # prepare parameters
        w_id = random.randint(1, config.warehouse_num)
        d_id = random.randint(1, 10)
        if random.randint(1, 100) <= 85:
            c_d_id = d_id
            c_w_id = w_id
        else:
            c_d_id = random.randint(1, 10)
            c_w_id = random.randint(1, config.warehouse_num)
        # if random.randint(1, 100) <= 40:
        #     c_id = tpccutils.nurand(1023, 1, 3000, tpccutils.C_FOR_C_ID)
        #     select_with_c_id_flag = True
        # else:
        #     c_last = tpccutils.get_last(tpccutils.nurand(255,0,999,tpccutils.C_FOR_C_LAST))
        #     select_with_c_id_flag = False
        c_id = next(tpccutils.zipf_gen)
        c_last = None
        select_with_c_id_flag = True

        # h_amount is defined as string
        h_amount = '{:.2f}'.format(random.random() * 4999 + 1)
        h_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")


        # create executer
        executer = dejima.get_executer("bench")
        executer.create_tx()
        executer.set_params(self.benchmark_management, self.result_measurement, self.time_measurement, self.timestamp_management, self.timestamp)


        # local lock
        miss_flag = True
        lineages = []

        executer.execute_stmt("SELECT * FROM warehouse WHERE w_id = {} FOR UPDATE NOWAIT".format(w_id))

        executer.execute_stmt("SELECT * FROM district WHERE d_w_id = {} AND d_id = {} FOR UPDATE NOWAIT".format(w_id, d_id))

        if select_with_c_id_flag:
            executer.execute_stmt("SELECT c_lineage FROM customer WHERE c_w_id = {} AND c_d_id = {} AND c_id = {} FOR UPDATE NOWAIT".format(c_w_id, c_d_id, c_id))
            all_records = executer.fetchall()
            if len(all_records) != 0:
                lineage, *_ = all_records[0]
                lineages.append(lineage)
                miss_flag = False
        else:
            executer.execute_stmt("SELECT c_lineage FROM customer WHERE c_w_id = {} AND c_d_id = {} AND c_last = '{}' ORDER BY c_first FOR UPDATE NOWAIT".format(c_w_id, c_d_id, c_last))
            all_records = executer.fetchall()
            if len(all_records) != 0:
                idx = math.ceil(len(all_records) / 2)
                lineage, *_ = all_records[idx-1]
                lineages.append(lineage)
                miss_flag = False

        if miss_flag:
            executer._restore()
            print("pay miss")
            return "miss"


        # global lock
        if self.locking_method == "frs":
            executer.lock_global(lineages)


        # local execution
        executer.execute_stmt("SELECT w_name, w_street_1, w_street_2, w_city, w_state, w_zip FROM warehouse WHERE w_id = {} FOR UPDATE".format(w_id))
        w_name, w_street_1, w_street_2, w_city, w_state, w_zip = executer.fetchone()

        executer.execute_stmt("UPDATE warehouse SET w_ytd = w_ytd + {} WHERE w_id = {}".format(h_amount, w_id))

        executer.execute_stmt("SELECT d_name, d_street_1, d_street_2, d_city, d_state, d_zip FROM district WHERE d_w_id = {} AND d_id = {} FOR UPDATE".format(w_id, d_id))
        d_name, d_street_1, d_street_2, d_city, d_state, d_zip = executer.fetchone()

        executer.execute_stmt("UPDATE district SET d_ytd = d_ytd + {} WHERE d_w_id = {} AND d_id = {}".format(h_amount, w_id, d_id))

        if select_with_c_id_flag:
            # case1
            executer.execute_stmt("SELECT c_first, c_middle, c_last, c_street_1, c_street_2, c_city, c_state, c_zip, c_phone, c_since, c_credit, c_credit_lim, c_discount, c_balance FROM customer WHERE c_w_id = {} AND c_d_id = {} AND c_id = {}".format(c_w_id, c_d_id, c_id))
            c_first, c_middle, c_last, c_street_1, c_street_2, c_city, c_state, c_zip, c_phone, c_since, c_credit, c_credit_lim, c_discount, c_balance = executer.fetchone()

        else:
            # case2
            executer.execute_stmt("SELECT c_id, c_first, c_middle, c_last, c_street_1, c_street_2, c_city, c_state, c_zip, c_phone, c_since, c_credit, c_credit_lim, c_discount, c_balance FROM customer WHERE c_w_id = {} AND c_d_id = {} AND c_last = '{}' ORDER BY c_first".format(c_w_id, c_d_id, c_last))
            all_records = executer.fetchall()
            idx = math.ceil(len(all_records) / 2)
            c_id, c_first, c_middle, c_last, c_street_1, c_street_2, c_city, c_state, c_zip, c_phone, c_since, c_credit, c_credit_lim, c_discount, c_balance = all_records[idx-1]

        if c_credit == "BC":
            executer.execute_stmt("SELECT c_data FROM customer WHERE c_w_id = {} AND c_d_id = {} AND c_id = {}".format(c_w_id, c_d_id, c_id))
            c_data, *_ = executer.fetchone()
            c_data = "{} {} {} {} {} {} | ".format(c_id, c_d_id, c_w_id, d_id, w_id, h_amount) + c_data
            c_data = c_data[0:500]
            executer.execute_stmt("UPDATE customer SET c_balance = c_balance - {}, c_ytd_payment = c_ytd_payment + {}, c_payment_cnt = c_payment_cnt + 1, c_data = '{}' WHERE c_w_id = {} AND c_d_id = {} AND c_id = {}".format(h_amount, h_amount, c_data, c_w_id, c_d_id, c_id))
        else:
            executer.execute_stmt("UPDATE customer SET c_balance = c_balance - {}, c_ytd_payment = c_ytd_payment + {}, c_payment_cnt = c_payment_cnt + 1 WHERE c_w_id = {} AND c_d_id = {} AND c_id = {}".format(h_amount, h_amount, c_w_id, c_d_id, c_id))

        h_data = w_name + "    " + d_name
        executer.execute_stmt("INSERT INTO history (h_c_id, h_c_d_id, h_c_w_id, h_d_id, h_w_id, h_date, h_amount, h_data) VALUES ({}, {}, {}, {}, {}, '{}', {}, '{}')".format(c_id, c_d_id, c_w_id, d_id, w_id, h_date, h_amount, h_data))


        # propagation
        executer.propagate(self.global_params)

        # termination
        commit = executer.terminate()

        return commit
