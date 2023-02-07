import random
import heapq
import time
import os
import json
import numpy as np
import re

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

# dic = {}
# dic['transaction'] = {'commit': 0, 'abort': 0, 'miss': 0}
# dic['detect_update'] = {'commit': 0, 'abort': 0, 'miss': 0}
# dic['transaction']['abort'] += 1
# print(dic)

# msg = {"result": "Nak", "result2": [1, 2]}
# if "result2" in msg:
#     print(msg)
# print(json.dumps(msg))

duration_time = {'get_xid': 0, 'lock': 0, 'base_update': 0, 'view_udpate': 0, 'prop_view': 0, 'communication': 0}

timestamps = [[0.0, 6.21, 13.87, 32.47, 39.38, 654.59], [43.32, 43.56, 61.89, 149.99, 170.33, 651.4], [174.49, 174.69, 176.88, 246.12, 274.38, 649.93], [281.44, 281.63, 335.49, 441.44, 468.93, 648.87], [478.37, 478.58, 488.57, 587.43, 613.52, 647.18], [620.68, 620.85, 622.21, 644.83, 645.8, 645.8]]

for i, timestamp in enumerate(timestamps):
    duration_time['get_xid'] += timestamp[1]-timestamp[0]
    duration_time['lock'] += timestamp[2]-timestamp[1]
    if i == 0:
        duration_time['base_update'] += timestamp[3]-timestamp[2]
    else:
        duration_time['view_udpate'] += timestamp[3]-timestamp[2]
    duration_time['prop_view'] += timestamp[4]-timestamp[3]
    if i != len(timestamps)-1:
        duration_time['communication'] += timestamps[i+1][0]-timestamps[i][4]
        duration_time['communication'] += timestamps[i][-1]-timestamps[i+1][-1]
    # print(timestamp)
for key in duration_time:
    if key == 'communication':
        duration_time[key] /= len(timestamps)-1
    else:
        duration_time[key] /= len(timestamps)
# print(duration_time)


time_ratio_raw = """
Peer15-proxy    | {'get_xid': 4.02, 'lock': 21.13, 'base_update': 10.88, 'view_udpate': 336.29, 'prop_view': 78.12, 'communication': 14.43}
Peer15-proxy    | benchmark finished
Peer3-proxy     | {'get_xid': 4.53, 'lock': 25.39, 'base_update': 22.74, 'view_udpate': 528.42, 'prop_view': 119.63, 'communication': 14.99}
Peer3-proxy     | benchmark finished
Peer1-proxy     | {'get_xid': 5.03, 'lock': 36.28, 'base_update': 116.15, 'view_udpate': 698.04, 'prop_view': 148.61, 'communication': 14.29}
Peer1-proxy     | benchmark finished
Peer11-proxy    | {'get_xid': 4.11, 'lock': 20.79, 'base_update': 10.84, 'view_udpate': 403.19, 'prop_view': 93.95, 'communication': 14.3}
Peer11-proxy    | benchmark finished
Peer12-proxy    | {'get_xid': 4.63, 'lock': 22.76, 'base_update': 516.51, 'view_udpate': 1259.25, 'prop_view': 253.06, 'communication': 12.94}
Peer12-proxy    | benchmark finished
Peer14-proxy    | {'get_xid': 4.24, 'lock': 20.49, 'base_update': 10.99, 'view_udpate': 407.22, 'prop_view': 89.56, 'communication': 14.33}
Peer14-proxy    | benchmark finished
Peer8-proxy     | {'get_xid': 4.22, 'lock': 23.41, 'base_update': 10.98, 'view_udpate': 566.07, 'prop_view': 116.02, 'communication': 14.46}
Peer8-proxy     | benchmark finished
Peer10-proxy    | {'get_xid': 5.78, 'lock': 41.83, 'base_update': 3409.4, 'view_udpate': 345.3, 'prop_view': 567.89, 'communication': 11.64}
Peer10-proxy    | benchmark finished
Peer7-proxy     | {'get_xid': 4.78, 'lock': 28.21, 'base_update': 64.97, 'view_udpate': 544.79, 'prop_view': 123.23, 'communication': 14.27}
Peer7-proxy     | benchmark finished
Peer13-proxy    | {'get_xid': 4.54, 'lock': 13.93, 'base_update': 9.84, 'view_udpate': 1319.41, 'prop_view': 219.55, 'communication': 10.33}
Peer13-proxy    | benchmark finished
Peer4-proxy     | {'get_xid': 4.26, 'lock': 22.99, 'base_update': 20.24, 'view_udpate': 458.97, 'prop_view': 97.36, 'communication': 14.17}
Peer4-proxy     | benchmark finished
Peer5-proxy     | {'get_xid': 4.74, 'lock': 33.72, 'base_update': 23.67, 'view_udpate': 1491.03, 'prop_view': 249.7, 'communication': 11.36}
Peer5-proxy     | benchmark finished
Peer2-proxy     | {'get_xid': 4.41, 'lock': 30.6, 'base_update': 23.04, 'view_udpate': 870.16, 'prop_view': 155.33, 'communication': 12.84}
Peer2-proxy     | benchmark finished
Peer6-proxy     | {'get_xid': 4.11, 'lock': 17.28, 'base_update': 10.79, 'view_udpate': 416.29, 'prop_view': 87.69, 'communication': 12.27}
Peer6-proxy     | benchmark finished
Peer9-proxy     | {'get_xid': 4.22, 'lock': 24.53, 'base_update': 11.73, 'view_udpate': 512.07, 'prop_view': 110.62, 'communication': 14.89}
Peer9-proxy     | benchmark finished
"""

result = {}
cnt = 0

def add_time_ratio(time_ratio):
    global cnt
    cnt += 1
    for name, value in time_ratio.items():
        if name not in result:
            result[name] =  value
        else:
            result[name] += value
            
def print_result(result):
    for name in result:
        result[name] = float('{:.2f}'.format(result[name]/cnt))
    print(result)

pattern = '\{.*\}'
time_ratio_list = re.findall(pattern, time_ratio_raw)
for time_ratio in time_ratio_list:
    time_ratio = json.loads(time_ratio.replace("'", '"'))
    # print(time_ratio)
    add_time_ratio(time_ratio)
print_result(result)

# timestamps = ((np.array(timestamps)-1)*2).tolist()
# timestamps = timestamps.tolist()
# timestamps = map(lambda x: x-1, timestamps[0])
# print(list(timestamps))
# print("{:.1f}".format(timestamps))

# os.makedirs('env_generator/s')

# with open('test.log', mode='a') as f:
#     f.write('test\n')