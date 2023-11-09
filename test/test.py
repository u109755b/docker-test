import re

res_list = [
    "Peer2 |  commit: 47 (47 0)  18.08 (18.08 0.00)[s],   abort: 10683 (1 10682)  81.56 (0.27 81.29)[s]",
    "Peer6 |  commit: 53 (53 0)  19.44 (19.44 0.00)[s],   abort: 12637 (5 12632)  80.18 (0.55 79.63)[s]",
]

commit_result_list = []
abort_result_list = []
for res in res_list:
    pattern = r'([\d.]+) \(([\d.]+) ([\d.]+)\)  ([\d.]+) \(([\d.]+) ([\d.]+)\)'
    matches = re.findall(pattern, res)
    commit_result_list.append(matches[0])
    abort_result_list.append(matches[1])
commit_result = [sum(map(float, x)) for x in zip(*commit_result_list)]
commit_result = [int(item) if item.is_integer() else round(item, 2) for item in commit_result]
abort_result = [sum(map(float, x)) for x in zip(*abort_result_list)]
abort_result = [int(item) if item.is_integer() else round(item, 2) for item in abort_result]
print("commit:  {} ({} {})  {} ({} {})".format(*commit_result))
print("abort:  {} ({} {})  {} ({} {})".format(*abort_result))


a = []
def b():
    a = [1]
b()
print(a)