import random
import heapq
import time
import json

# s = set()
# s.add(1)
# s.add(2)
# print(list(s))

# que = [[time.time()+10, 1], [time.time()+5, 2], [time.time(), 3]]
# print(que)
# que[0] = que[-1]
# que.pop()
# print(que)
# heapq.heapify(que)
# print(que)
# r = heapq.heappop(que)
# print(r)
# print(heapq.heappop(que))

dic = {}
dic['transaction'] = {'commit': 0, 'abort': 0, 'miss': 0}
dic['detect_update'] = {'commit': 0, 'abort': 0, 'miss': 0}
dic['transaction']['abort'] += 1
# print(dic)

with open('proxy/dejima_config.json') as f:
    dejima_config_dict = json.load(f)
# dt_list = [dt for dt in dejima_config_dict['dejima_table'].keys() if peer_name in dejima_config_dict['dejima_table'][dt]]
# print(dejima_config_dict)
al_list = []
for peer in dejima_config_dict['dejima_table']:
    pass