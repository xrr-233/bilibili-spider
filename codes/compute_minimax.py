import csv
import os

if(__name__=="__main__"):
    txts = os.listdir('../results')

    for file in txts:
        flag = True
        with open('../results/' + file, "r") as f:
            res = list(csv.reader(f))
            minx = float(res[1][10])
            maxx = float(res[1][10])
            for i in range(2, len(res)):
                if (float(res[i][10]) > maxx):
                    maxx = float(res[i][10])
                if (float(res[i][10]) < minx):
                    minx = float(res[i][10])
            if(maxx - minx == 0):
                flag = False
            else:
                minimax_res = []
                for i in range(1, len(res)):
                    if(maxx - minx > 0):
                        minimax_res.append((float(res[i][10]) - minx) / (maxx - minx))
        if(not flag):
            continue

        with open("../minimax_results/" + file, "w", newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['UID', '大类', '小类', '关注视频log2归一化'])
            for i in range(1, len(res)):
                res[i][3] = minimax_res[i - 1]
                writer.writerow(res[i][0:4])