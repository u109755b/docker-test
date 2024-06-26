import random
import math
from datetime import datetime
import dejima
from dejima import config
from dejima import GlobalBencher
from benchmark.tpcc import tpccutils

class TPCCTxPay(GlobalBencher):
    def _execute(self):
        # prepare parameters
        w_id = config.w_id   # home w_id
        d_id = random.randint(1, 10)
        if random.randint(1, 100) <= 85:
            c_w_id = w_id
            c_d_id = d_id
        else:
            c_w_id = tpccutils.get_remote_w_id(w_id)
            c_d_id = random.randint(1, 10)
        if random.randint(1, 100) <= 40:
            c_id = tpccutils.nurand(1023, 1, 3000, tpccutils.C_FOR_C_ID)
            select_with_c_id_flag = True
        else:
            c_last = tpccutils.get_last(tpccutils.nurand(255,0,999,tpccutils.C_FOR_C_LAST))
            select_with_c_id_flag = False
        # c_id = next(tpccutils.zipf_gen)
        # c_last = None
        # select_with_c_id_flag = True

        # h_amount is defined as string
        h_amount = '{:.2f}'.format(random.random() * 4999 + 1)
        h_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")


        # create executer
        executer = dejima.get_executer("bench")
        executer.create_tx()
        self.params["tx_type"] = "payment"
        executer.set_params(self.params)


        # local lock
        lineages = []
        miss_flag = False

        executer.execute_stmt("SELECT lineage FROM warehouse WHERE w_id = {} FOR UPDATE NOWAIT".format(w_id), max_retry_cnt=3)
        row = executer.fetchone()
        lineages.append(row[0])

        executer.execute_stmt("SELECT lineage FROM district WHERE d_w_id = {} AND d_id = {} FOR UPDATE NOWAIT".format(w_id, d_id), max_retry_cnt=3)
        row = executer.fetchone()
        lineages.append(row[0])

        if select_with_c_id_flag:
            executer.execute_stmt("SELECT c_lineage FROM customer WHERE c_w_id = {} AND c_d_id = {} AND c_id = {} FOR UPDATE NOWAIT".format(c_w_id, c_d_id, c_id), max_retry_cnt=3)
            row = executer.fetchone()
            lineages.append(row[0])
        else:
            executer.execute_stmt("SELECT c_lineage FROM customer WHERE c_w_id = {} AND c_d_id = {} AND c_last = '{}' ORDER BY c_first FOR UPDATE NOWAIT".format(c_w_id, c_d_id, c_last), max_retry_cnt=3)
            all_rows = executer.fetchall()
            if len(all_rows):
                idx = math.ceil(len(all_rows) / 2)
                lineages.append(all_rows[idx-1][0])
            else:
                miss_flag = True

        if miss_flag:
            executer._restore()
            print("pay miss")
            return "miss"


        # global lock
        executer.lock_global(lineages, self.locking_method)


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
            all_rows = executer.fetchall()
            idx = math.ceil(len(all_rows) / 2)
            c_id, c_first, c_middle, c_last, c_street_1, c_street_2, c_city, c_state, c_zip, c_phone, c_since, c_credit, c_credit_lim, c_discount, c_balance = all_rows[idx-1]

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
