import csv
import os

if(__name__=="__main__"):
    txts = os.listdir('../minimax_results')

    final_res = [['UID', '大类', '小类', '关注视频log2归一化']]

    for file in txts:
        with open('../minimax_results/' + file, 'r') as f:
            res = list(csv.reader(f))
            final_res.extend(res[1:])

    with open('../minimax_concatenation.csv', 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerows(final_res)
