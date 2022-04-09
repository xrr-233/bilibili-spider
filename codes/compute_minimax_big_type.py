import csv
import os

if(__name__=="__main__"):
    txts = os.listdir('../results')
    big_type = [1, 3, 4, 5, 11, 13, 23, 36, 119, 129, 155, 160, 167, 177, 181, 188, 202, 211, 217, 223, 234]
    big_type_num = [0] * len(big_type)

    for file in txts:
        flag = True
        with open('../results/' + file, "r") as f:
            res = list(csv.reader(f))
            for i in range(1, len(res)):
                for j in range(len(big_type)):
                    if(float(res[i][1]) == big_type[j]):
                        big_type_num[j] += float(res[i][10])
            minx = float(big_type_num[0])
            maxx = float(big_type_num[0])
            for i in range(1, len(big_type)):
                if (big_type_num[i] > maxx):
                    maxx = big_type_num[i]
                if (big_type_num[i] < minx):
                    minx = big_type_num[i]
            if(not os.access("../minimax_results/" + file, os.F_OK)):
                flag = False
            else:
                minimax_res = []
                for i in range(1, len(big_type) + 1):
                    minimax_res.append((big_type_num[i - 1] - minx) / (maxx - minx))
        if(not flag):
            continue
        with open("../minimax_results_big_type/" + file, "w", newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['UID', '大类', '关注视频log2和归一化'])
            for i in range(1, len(big_type) + 1):
                res[i][1] = big_type[i - 1]
                res[i][2] = minimax_res[i - 1]
                writer.writerow(res[i][0:3])