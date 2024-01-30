import random
from datetime import datetime
import dejima
from dejima import config
from dejima import GlobalBencher
from benchmark.tpcc import tpccutils

class TPCCTxNO(GlobalBencher):
    def _execute(self):
        # prepare parameters
        w_id = random.randint(1, config.warehouse_num)
        # d_id = random.randint(1, 10)
        d_id = random.randint(1, 1)
        # c_id = tpccutils.nurand(1023, 1, 3000, tpccutils.C_FOR_C_ID)
        c_id = next(tpccutils.zipf_gen)
        ol_cnt = random.randint(5, 15)
        rbk = random.randint(1, 100)
        o_entry_d = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        ol_i_id_list = []
        ol_supply_w_id_list = []
        ol_quantity_list = []
        o_all_local = 1
        for i in range(1, ol_cnt+1):
            if i == ol_cnt and rbk == 1:
                ol_i_id_list.append(None)
            else:
                ol_i_id_list.append(tpccutils.nurand(8191, 1, 100000, tpccutils.C_FOR_OL_I_ID))
            if random.randint(1,100) == 1 or config.warehouse_num == 1:
                ol_supply_w_id_list.append(w_id)
            else:
                o_all_local = 0
                while True:
                    ol_supply_w_id = random.randint(1, config.warehouse_num)
                    if ol_supply_w_id == w_id:
                        continue
                    break
                ol_supply_w_id_list.append(ol_supply_w_id)
            ol_quantity_list.append(random.randint(1, 10))


        # create executer
        executer = dejima.get_executer("bench")
        executer.create_tx()
        executer.set_params(self.params)


        # local lock
        miss_flag = True
        lineages = []

        executer.execute_stmt("SELECT * FROM warehouse WHERE W_ID = {} FOR SHARE NOWAIT".format(w_id))
        executer.execute_stmt("SELECT * FROM district WHERE d_w_id = {} AND d_id = {} FOR UPDATE NOWAIT".format(w_id, d_id))
        executer.execute_stmt("SELECT * FROM customer WHERE c_w_id = {} AND c_d_id = {} AND c_id = {} FOR SHARE NOWAIT".format(w_id, d_id, c_id))
        # if tx.cur.fetchone() != None:
        #     miss_flag = False
        for i_id in ol_i_id_list:
            if i_id == None:
                continue
            executer.execute_stmt("SELECT * FROM item WHERE I_ID = {} FOR SHARE NOWAIT".format(i_id))
            executer.execute_stmt("SELECT lineage FROM stock WHERE s_i_id = {} AND s_w_id = {} FOR SHARE NOWAIT".format(i_id, w_id))
            all_records = executer.fetchall()
            if len(all_records) != 0:
                _lineages = [record[0] for record in all_records]
                lineages += _lineages
                miss_flag = False

        if miss_flag:
            executer._restore()
            print("new order miss")
            return "miss"


        # global lock
        if self.locking_method == "frs":
            executer.lock_global(lineages)

        # local execution
        executer.execute_stmt("SELECT w_tax FROM warehouse WHERE W_ID = {}".format(w_id))
        w_tax, *_ = executer.fetchone()
        w_tax = float(w_tax)

        executer.execute_stmt("SELECT d_tax, d_next_o_id FROM district WHERE d_w_id = {} AND d_id = {} FOR UPDATE".format(w_id, d_id))
        d_tax, d_next_o_id = executer.fetchone()

        executer.execute_stmt("SELECT c_discount, c_last, c_credit FROM customer WHERE c_w_id = {} AND c_d_id = {} AND c_id = {}".format(w_id, d_id, c_id))
        c_discount, c_last, c_credit = executer.fetchone()

        executer.execute_stmt("UPDATE district SET d_next_o_id = d_next_o_id + 1 WHERE d_w_id = {} AND d_id = {}".format(w_id, d_id))

        executer.execute_stmt("INSERT INTO oorder (o_id, o_d_id, o_w_id, o_c_id, o_entry_d, o_ol_cnt, o_all_local) VALUES ({}, {}, {}, {}, '{}', {}, {})".format(d_next_o_id, d_id, w_id, c_id, o_entry_d, ol_cnt, o_all_local))

        executer.execute_stmt("INSERT INTO new_order (no_o_id, no_d_id, no_w_id) VALUES ({}, {}, {})".format(d_next_o_id, d_id, w_id))

        # for i, i_id in enumerate(ol_i_id_list):
        for i, lineage in enumerate(lineages):
            i_id = lineage.split(",")[1][:-1]
            # rollback if i_id is unused value
            if i_id == None:
                raise Exception('i_id = None, rollback')

            executer.execute_stmt("SELECT I_PRICE, I_NAME, I_DATA FROM item WHERE I_ID = {}".format(i_id))
            i_price, i_name, i_data = executer.fetchone()

            executer.execute_stmt("SELECT s_quantity, s_data, s_dist_01, s_dist_02, s_dist_03, s_dist_04, s_dist_05, s_dist_06, s_dist_07, s_dist_08, s_dist_09, s_dist_10 FROM stock WHERE s_i_id = {} AND s_w_id = {} FOR UPDATE".format(i_id, w_id))
            s_quantity, s_data, *s_dist_list = executer.fetchone()

            if s_quantity - ol_quantity_list[i] >= 10:
                s_quantity = s_quantity - ol_quantity_list[i]
            else:
                s_quantity = s_quantity + 91 - ol_quantity_list[i]
            if o_all_local == 1:
                s_remote_cnt_inc = 0
            else:
                s_remote_cnt_inc = 1
            executer.execute_stmt("UPDATE stock SET s_quantity = {}, s_ytd = s_ytd + {}, s_order_cnt = s_order_cnt + 1, s_remote_cnt = s_remote_cnt + {} WHERE s_i_id = {} AND s_w_id = {}".format(s_quantity, ol_quantity_list[i], s_remote_cnt_inc, i_id, w_id))

            ol_dist_info = s_dist_list[d_id - 1]
            executer.execute_stmt("INSERT INTO order_line (ol_o_id, ol_d_id, ol_w_id, ol_number, ol_i_id, ol_supply_w_id, ol_quantity, ol_amount, ol_dist_info) VALUES ({}, {}, {}, {}, {}, {}, {}, {}, '{}')".format(d_next_o_id, d_id, w_id, i, i_id, ol_supply_w_id_list[i], ol_quantity_list[i], ol_quantity_list[i] * i_price, ol_dist_info))


        # propagation
        executer.propagate(self.global_params)

        # termination
        commit = executer.terminate()

        return commit
