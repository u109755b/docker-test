import numpy as np
from collections import defaultdict
import json

def get_sample_data(file_name, parameter_name):
    result = {}
    with open(file_name, 'r') as f:
        cur_key = ''
        method = ''
        for line in f:
            if line.startswith(parameter_name):
                cur_key = '{}={}'.format(parameter_name, line.split()[1])
                result[cur_key] = {'2pl': [], 'frs': [], 'hybrid': []}
            if line.startswith('bench'):
                method = line.split()[1]    # 2pl or frs
            if line.startswith('commit'):
                commit_num = int(line.split()[1])   # コミット数
                if len(result[cur_key][method]) > 2: continue
                result[cur_key][method].append(commit_num)
            if line.startswith('abort'):
                abort_num = int(line.split()[1])   # アボート数
                if len(result[cur_key][method]) > 2: continue
                result[cur_key][method].append(abort_num)
    return result



t = 120
sample_num=5
file_name_k = 'tx_order_on_hybrid/4records_tx sample{k}.txt'
parameter_name = 'set_rate'
output_mode = 4    # 1:全データ出力,  2:平均値だけ出力,  3:1秒あたりの平均値を出力,  4:倍率を出力,  5: ChatGPT用に出力

file_names = []
results = []    # results[k_sample][parameter_key][method]


for i in range(sample_num):
    k = i+1
    file_name = file_name_k.replace('{k}', str(k))
    result = get_sample_data(file_name, parameter_name)
    results.append(result)


if output_mode == 1: print('parameter - method: [avg_commit, avg_abort]   (raw_data)')
if output_mode == 2: print('parameter - method: avg_commit (avg_abort)')
if output_mode == 3: print('parameter - method: avg_commit/s (avg_abort/s)')
if output_mode == 4: print('parameter - method: relative_avg_commit (relative_avg_abort)')
if output_mode == 5: print('throughput (abort_rate)')

averages_list = defaultdict(lambda: [])
for parameter_key in results[0]:
    averages_for_output = {}
    raws_for_output = {}
    # 結果を計算する
    for method in results[0][parameter_key]:
        raws = []
        for i in range(sample_num):
            raws.append(results[i][parameter_key][method])
        raws = sorted(raws, key=lambda x: x[0])   # ソート
        average = [round(sum(x)/len(x)) for x in zip(*raws[1:-1])]    # 最大値・最小値を省いた平均を取る
        raws_for_output[method] = raws
        averages_for_output[method] = average
        averages_list[method].append(average)
    # 結果を表示する
    for method in results[0][parameter_key]:
        raws = raws_for_output[method]
        average = averages_for_output[method]
        np_average = np.array(averages_for_output[method])
        np_base_avg = np.array(averages_for_output['2pl'])
        with np.errstate(divide='ignore', invalid='ignore'):
            relative_avg = np.divide(np_average, np_base_avg)
            relative_avg = np.nan_to_num(relative_avg, nan=0.0) # 0での除算を0に置き換える
            relative_avg = np.around(relative_avg, decimals=2)
        if output_mode == 1: print('{} - {}: {}   ({})'.format(parameter_key, method, average, raws))
        if output_mode == 2: print('{} - {}: {} ({})'.format(parameter_key, method, average[0], average[1]))
        if output_mode == 3: print('{} - {}: {:.2f} ({:.2f})'.format(parameter_key, method, average[0]/t, average[1]/t))
        if output_mode == 4: print('{} - {}: {} ({})'.format(parameter_key, method, relative_avg[0], relative_avg[1]))
    if output_mode != 5: print('')
if output_mode == 5:
    for method, avg_list in averages_list.items():
        output_list = ['{:.2f} ({:.2f})'.format(item[0]/t, item[1]/t) for item in reversed(avg_list)]
        print('{}: {}'.format(method, ',  '.join(output_list)))
    # print(averages_list.items())
