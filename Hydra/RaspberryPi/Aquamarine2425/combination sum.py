key = [1,2,4,8,16,32,64]
press = [0]*len(key)
def combine(key,target,press):
    sum = 0
    for j in range(len(key)):
        sum = sum + key[j]
    if target > sum or target < 0:
        return "out of range"
    for i in range(len(key)):
        index = len(key)-1-i
        target = target - key[index]
        press[index] = key[index]
        if target < 0:
            target = target + key[index]
            press[index] = 0
        if target == 0:
            return press

print(combine(key,int(input("number:")),press))
# print(press)