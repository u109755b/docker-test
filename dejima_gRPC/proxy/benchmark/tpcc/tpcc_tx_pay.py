import random
import math
from datetime import datetime
import config
from benchmark.tpcc import tpccutils

class TPCCTxPay:
    # initialize
    def __init__(self, tx, params):
        self.tx = tx
        self.global_xid = params["global_xid"]

        # prepare parameters
        self.w_id = random.randint(1, config.warehouse_num)
        self.d_id = random.randint(1, 10)
        if random.randint(1, 100) <= 85:
            self.c_d_id = self.d_id
            self.c_w_id = self.w_id
        else:
            self.c_d_id = random.randint(1, 10)
            self.c_w_id = random.randint(1, config.warehouse_num)
        # if random.randint(1, 100) <= 40:
        #     self.c_id = tpccutils.nurand(1023, 1, 3000, tpccutils.C_FOR_C_ID)
        #     self.select_with_c_id_flag = True
        # else:
        #     self.c_last = tpccutils.get_last(tpccutils.nurand(255,0,999,tpccutils.C_FOR_C_LAST))
        #     self.select_with_c_id_flag = False
        self.c_id = next(tpccutils.zipf_gen)
        self.c_last = None
        self.select_with_c_id_flag = True

        # h_amount is defined as string
        self.h_amount = '{:.2f}'.format(random.random() * 4999 + 1)
        self.h_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")


    # get local locks, and return lineages
    def get_local_locks(self):
        tx, global_xid = self.tx, self.global_xid
        w_id, d_id = self.w_id, self.d_id
        c_d_id, c_w_id = self.c_d_id, self.c_w_id
        c_id, c_last, select_with_c_id_flag = self.c_id, self.c_last, self.select_with_c_id_flag

        try:
            miss_flag = True
            lineages = []

            tx.cur.execute("SELECT * FROM warehouse WHERE w_id = {} FOR UPDATE NOWAIT".format(w_id))

            tx.cur.execute("SELECT * FROM district WHERE d_w_id = {} AND d_id = {} FOR UPDATE NOWAIT".format(w_id, d_id))

            if select_with_c_id_flag:
                tx.cur.execute("SELECT c_lineage FROM customer WHERE c_w_id = {} AND c_d_id = {} AND c_id = {} FOR UPDATE NOWAIT".format(c_w_id, c_d_id, c_id))
                all_records = tx.cur.fetchall()
                if len(all_records) != 0:
                    lineage, *_ = all_records[0]
                    lineages.append(lineage)
                    miss_flag = False
            else:
                tx.cur.execute("SELECT c_lineage FROM customer WHERE c_w_id = {} AND c_d_id = {} AND c_last = '{}' ORDER BY c_first FOR UPDATE NOWAIT".format(c_w_id, c_d_id, c_last))
                all_records = tx.cur.fetchall()
                if len(all_records) != 0:
                    idx = math.ceil(len(all_records) / 2)
                    lineage, *_ = all_records[idx-1]
                    lineages.append(lineage)
                    miss_flag = False

        except:
            return False
        if miss_flag:
            return "miss"
        return lineages


    # execute local transacion
    def execute_local_tx(self):
        tx, global_xid = self.tx, self.global_xid
        w_id, d_id = self.w_id, self.d_id
        c_d_id, c_w_id = self.c_d_id, self.c_w_id
        c_id, c_last, select_with_c_id_flag = self.c_id, self.c_last, self.select_with_c_id_flag
        h_amount, h_date = self.h_amount, self.h_date

        try:
            tx.cur.execute("SELECT w_name, w_street_1, w_street_2, w_city, w_state, w_zip FROM warehouse WHERE w_id = {} FOR UPDATE".format(w_id))
            w_name, w_street_1, w_street_2, w_city, w_state, w_zip = tx.cur.fetchone()

            tx.cur.execute("UPDATE warehouse SET w_ytd = w_ytd + {} WHERE w_id = {}".format(h_amount, w_id))

            tx.cur.execute("SELECT d_name, d_street_1, d_street_2, d_city, d_state, d_zip FROM district WHERE d_w_id = {} AND d_id = {} FOR UPDATE".format(w_id, d_id))
            d_name, d_street_1, d_street_2, d_city, d_state, d_zip = tx.cur.fetchone()

            tx.cur.execute("UPDATE district SET d_ytd = d_ytd + {} WHERE d_w_id = {} AND d_id = {}".format(h_amount, w_id, d_id))

            if select_with_c_id_flag:
                # case1
                tx.cur.execute("SELECT c_first, c_middle, c_last, c_street_1, c_street_2, c_city, c_state, c_zip, c_phone, c_since, c_credit, c_credit_lim, c_discount, c_balance FROM customer WHERE c_w_id = {} AND c_d_id = {} AND c_id = {}".format(c_w_id, c_d_id, c_id))
                c_first, c_middle, c_last, c_street_1, c_street_2, c_city, c_state, c_zip, c_phone, c_since, c_credit, c_credit_lim, c_discount, c_balance = tx.cur.fetchone()

            else:
                # case2
                tx.cur.execute("SELECT c_id, c_first, c_middle, c_last, c_street_1, c_street_2, c_city, c_state, c_zip, c_phone, c_since, c_credit, c_credit_lim, c_discount, c_balance FROM customer WHERE c_w_id = {} AND c_d_id = {} AND c_last = '{}' ORDER BY c_first".format(c_w_id, c_d_id, c_last))
                all_records = tx.cur.fetchall()
                idx = math.ceil(len(all_records) / 2)
                c_id, c_first, c_middle, c_last, c_street_1, c_street_2, c_city, c_state, c_zip, c_phone, c_since, c_credit, c_credit_lim, c_discount, c_balance = all_records[idx-1]

            if c_credit == "BC":
                tx.cur.execute("SELECT c_data FROM customer WHERE c_w_id = {} AND c_d_id = {} AND c_id = {}".format(c_w_id, c_d_id, c_id))
                c_data, *_ = tx.cur.fetchone()
                c_data = "{} {} {} {} {} {} | ".format(c_id, c_d_id, c_w_id, d_id, w_id, h_amount) + c_data
                c_data = c_data[0:500]
                tx.cur.execute("UPDATE customer SET c_balance = c_balance - {}, c_ytd_payment = c_ytd_payment + {}, c_payment_cnt = c_payment_cnt + 1, c_data = '{}' WHERE c_w_id = {} AND c_d_id = {} AND c_id = {}".format(h_amount, h_amount, c_data, c_w_id, c_d_id, c_id))
            else:
                tx.cur.execute("UPDATE customer SET c_balance = c_balance - {}, c_ytd_payment = c_ytd_payment + {}, c_payment_cnt = c_payment_cnt + 1 WHERE c_w_id = {} AND c_d_id = {} AND c_id = {}".format(h_amount, h_amount, c_w_id, c_d_id, c_id))

            h_data = w_name + "    " + d_name
            tx.cur.execute("INSERT INTO history (h_c_id, h_c_d_id, h_c_w_id, h_d_id, h_w_id, h_date, h_amount, h_data) VALUES ({}, {}, {}, {}, {}, '{}', {}, '{}')".format(c_id, c_d_id, c_w_id, d_id, w_id, h_date, h_amount, h_data))

        except:
            return False
        return True