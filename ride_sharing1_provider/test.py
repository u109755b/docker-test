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
alliance1-proxy   | {'get_xid': 5.4, 'lock': 50.94, 'base_update': 680.08, 'view_udpate': 399.13, 'prop_view': 463.6, 'communication': 6.29}
alliance1-proxy   | benchmark finished
provider4-proxy   | {'get_xid': 8.22, 'lock': 16.31, 'base_update': 16.39, 'view_udpate': 2993.5, 'prop_view': 619.05, 'communication': 9.37}
provider4-proxy   | benchmark finished
provider17-proxy  | {'get_xid': 6.78, 'lock': 15.12, 'base_update': 13.81, 'view_udpate': 2930.01, 'prop_view': 584.27, 'communication': 8.86}
provider17-proxy  | benchmark finished
alliance2-proxy   | {'get_xid': 5.76, 'lock': 46.86, 'base_update': 732.68, 'view_udpate': 448.28, 'prop_view': 463.95, 'communication': 6.51}
alliance2-proxy   | benchmark finished
provider12-proxy  | {'get_xid': 7.04, 'lock': 9.66, 'base_update': 7.51, 'view_udpate': 2772.99, 'prop_view': 582.47, 'communication': 6.23}
provider12-proxy  | benchmark finished
provider16-proxy  | {'get_xid': 9.19, 'lock': 15.64, 'base_update': 18.48, 'view_udpate': 2920.38, 'prop_view': 693.73, 'communication': 8.99}
provider16-proxy  | benchmark finished
provider7-proxy   | {'get_xid': 9.38, 'lock': 14.91, 'base_update': 14.29, 'view_udpate': 2978.85, 'prop_view': 641.16, 'communication': 9.17}
provider7-proxy   | benchmark finished
provider3-proxy   | {'get_xid': 7.9, 'lock': 15.82, 'base_update': 17.56, 'view_udpate': 3028.69, 'prop_view': 629.73, 'communication': 10.5}
provider3-proxy   | benchmark finished
provider2-proxy   | {'get_xid': 6.73, 'lock': 7.72, 'base_update': 6.8, 'view_udpate': 2693.25, 'prop_view': 552.44, 'communication': 5.81}
provider2-proxy   | benchmark finished
provider6-proxy   | {'get_xid': 6.72, 'lock': 11.6, 'base_update': 7.48, 'view_udpate': 2716.67, 'prop_view': 568.08, 'communication': 7.68}
provider6-proxy   | benchmark finished
provider15-proxy  | {'get_xid': 7.82, 'lock': 11.51, 'base_update': 9.0, 'view_udpate': 2761.29, 'prop_view': 572.76, 'communication': 6.48}
provider15-proxy  | benchmark finished
provider10-proxy  | {'get_xid': 7.35, 'lock': 10.37, 'base_update': 7.57, 'view_udpate': 2682.86, 'prop_view': 565.12, 'communication': 7.8}
provider10-proxy  | benchmark finished
provider19-proxy  | {'get_xid': 8.64, 'lock': 11.02, 'base_update': 7.34, 'view_udpate': 2725.23, 'prop_view': 568.09, 'communication': 6.49}
provider19-proxy  | benchmark finished
provider14-proxy  | {'get_xid': 6.65, 'lock': 11.16, 'base_update': 7.56, 'view_udpate': 2721.25, 'prop_view': 593.26, 'communication': 6.94}
provider14-proxy  | benchmark finished
provider13-proxy  | {'get_xid': 7.12, 'lock': 10.81, 'base_update': 8.5, 'view_udpate': 2645.85, 'prop_view': 535.27, 'communication': 5.37}
provider13-proxy  | benchmark finished
provider11-proxy  | {'get_xid': 6.99, 'lock': 14.36, 'base_update': 12.23, 'view_udpate': 2892.35, 'prop_view': 570.57, 'communication': 11.05}
provider11-proxy  | benchmark finished
provider9-proxy   | {'get_xid': 7.91, 'lock': 14.81, 'base_update': 16.49, 'view_udpate': 2794.28, 'prop_view': 616.16, 'communication': 9.1}
provider9-proxy   | benchmark finished
provider8-proxy   | {'get_xid': 7.54, 'lock': 10.45, 'base_update': 7.5, 'view_udpate': 2660.31, 'prop_view': 567.52, 'communication': 5.95}
provider8-proxy   | benchmark finished
provider20-proxy  | {'get_xid': 7.19, 'lock': 13.87, 'base_update': 7.71, 'view_udpate': 2599.69, 'prop_view': 584.01, 'communication': 6.61}
provider20-proxy  | benchmark finished
provider5-proxy   | {'get_xid': 6.98, 'lock': 10.75, 'base_update': 7.0, 'view_udpate': 2672.6, 'prop_view': 538.36, 'communication': 5.28}
provider5-proxy   | benchmark finished
provider1-proxy   | {'get_xid': 7.28, 'lock': 12.98, 'base_update': 14.69, 'view_udpate': 2854.79, 'prop_view': 579.0, 'communication': 11.19}
provider1-proxy   | benchmark finished
provider18-proxy  | {'get_xid': 5.98, 'lock': 8.71, 'base_update': 7.34, 'view_udpate': 2684.01, 'prop_view': 495.28, 'communication': 5.88}
provider18-proxy  | benchmark finished
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