if(__name__=="__main__"):
    arr = [34, 32, 31, 28, 24, 22, 21, 21, 19, 12, 10, 10, 9, 9, 9, 8, 7, 5, 2, 1]
    type = [0] * len(arr)
    splitter = [32, 21, 9]
    while(True):
        for i in range(len(arr)):
            abs_ = [0] * 3
            for j in range(len(splitter)):
                abs_[j] = abs(arr[i] - splitter[j])
            min_abs = abs_[0]
            min_abs_i = 0
            for j in range(1, len(splitter)):
                if(abs_[j] < min_abs):
                    min_abs = abs_[j]
                    min_abs_i = j
            type[i] = min_abs_i
        flag = True
        for i in range(len(splitter)):
            key = 0
            count = 0
            for j in range(len(type)):
                if(type[j] == i):
                    key += arr[j]
                    count += 1
            key /= count
            if(splitter[i] != key):
                splitter[i] = key
                flag = False
        if(flag):
            for i in range(len(type)):
                print(type[i])
            break