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
alliance5-proxy    | {'get_xid': 6.33, 'lock': 63.37, 'base_update': 19.07, 'view_udpate': 69.74, 'prop_view': 28.66, 'communication': 20.93}
alliance5-proxy    | benchmark finished
provider1-proxy    | {'get_xid': 9.71, 'lock': 96.92, 'base_update': 13.68, 'view_udpate': 91.14, 'prop_view': 17.86, 'communication': 13.24}
provider1-proxy    | benchmark finished
provider6-proxy    | {'get_xid': 12.0, 'lock': 101.7, 'base_update': 27.46, 'view_udpate': 118.06, 'prop_view': 31.5, 'communication': 17.62}
provider6-proxy    | benchmark finished
alliance7-proxy    | {'get_xid': 5.9, 'lock': 76.98, 'base_update': 18.64, 'view_udpate': 60.9, 'prop_view': 23.46, 'communication': 18.42}
alliance7-proxy    | benchmark finished
provider2-proxy    | {'get_xid': 12.64, 'lock': 103.27, 'base_update': 27.97, 'view_udpate': 119.42, 'prop_view': 32.58, 'communication': 17.98}
provider2-proxy    | benchmark finished
alliance4-proxy    | {'get_xid': 5.92, 'lock': 64.08, 'base_update': 18.44, 'view_udpate': 69.49, 'prop_view': 28.64, 'communication': 21.06}
alliance4-proxy    | benchmark finished
alliance3-proxy    | {'get_xid': 6.03, 'lock': 64.11, 'base_update': 18.04, 'view_udpate': 71.21, 'prop_view': 28.35, 'communication': 21.07}
alliance3-proxy    | benchmark finished
provider3-proxy    | {'get_xid': 12.12, 'lock': 102.58, 'base_update': 27.4, 'view_udpate': 117.42, 'prop_view': 31.85, 'communication': 17.68}
provider3-proxy    | benchmark finished
provider8-proxy    | {'get_xid': 9.38, 'lock': 96.47, 'base_update': 12.77, 'view_udpate': 84.27, 'prop_view': 16.61, 'communication': 13.33}
provider8-proxy    | benchmark finished
provider5-proxy    | {'get_xid': 12.1, 'lock': 101.24, 'base_update': 27.79, 'view_udpate': 117.91, 'prop_view': 31.79, 'communication': 17.41}
provider5-proxy    | benchmark finished
alliance2-proxy    | {'get_xid': 6.03, 'lock': 62.88, 'base_update': 19.28, 'view_udpate': 70.78, 'prop_view': 28.79, 'communication': 21.09}
alliance2-proxy    | benchmark finished
alliance1-proxy    | {'get_xid': 5.79, 'lock': 78.73, 'base_update': 18.4, 'view_udpate': 61.02, 'prop_view': 24.16, 'communication': 17.52}
alliance1-proxy    | benchmark finished
provider7-proxy    | {'get_xid': 12.26, 'lock': 101.5, 'base_update': 28.59, 'view_udpate': 114.11, 'prop_view': 32.07, 'communication': 18.56}
provider7-proxy    | benchmark finished
provider4-proxy    | {'get_xid': 12.17, 'lock': 101.39, 'base_update': 27.3, 'view_udpate': 116.11, 'prop_view': 31.03, 'communication': 17.81}
provider4-proxy    | benchmark finished
alliance6-proxy    | {'get_xid': 6.23, 'lock': 64.6, 'base_update': 18.4, 'view_udpate': 70.83, 'prop_view': 28.77, 'communication': 20.88}
alliance6-proxy    | benchmark finished
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