import csv

if(__name__=="__main__"):
    res_num = []
    with open('../corr_small.csv', 'r') as f:
        res = list(csv.reader(f))
        for i in range(1, len(res)):
            res_num.extend(res[i][1:])
    for i in range(len(res_num)):
        res_num[i] = float(res_num[i])
    res_num = sorted(res_num, reverse=True)
    print(res_num)

    res_num_x = [0] * len(res_num)
    res_num_y = [0] * len(res_num)
    with open("../res_small.csv", "w", newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['res_num_x', 'res_num_y', 'res_num'])
        for o in range(len(res_num)):
            for i in range(1, len(res)):
                flag = False
                for j in range(1, len(res[i])):
                    if(str(res_num[o]) == res[i][j]):
                        flag = True
                        res_num_x = res[0][j]
                        res_num_y = res[i][0]
                        writer.writerow([str(res_num_x), str(res_num_y), res_num[o]])
                        break
                if(flag):
                    break