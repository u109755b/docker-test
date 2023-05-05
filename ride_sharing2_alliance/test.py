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

l = list(range(1, 10+1))
l2 = random.sample(l, 3)
print(l2)