import random
import heapq
import time
import os
import json
import numpy as np

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

timestamps = [[0.0, 1.14, 2.34, 4.87, 8.29, 65.15], [11.68, 11.77, 12.20, 32.58, 38.29, 64.4], [43.50, 43.62, 44.47, 58.13, 58.47, 58.47]]

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
print(duration_time)

# timestamps = ((np.array(timestamps)-1)*2).tolist()
# timestamps = timestamps.tolist()
# timestamps = map(lambda x: x-1, timestamps[0])
# print(list(timestamps))
# print("{:.1f}".format(timestamps))

# os.makedirs('env_generator/s')

# with open('test.log', mode='a') as f:
#     f.write('test\n')