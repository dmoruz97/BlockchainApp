with open("disk_utilisation") as f:
    content = f.readlines()
n = 0
sum = 0
for line in content:
    list = line.split(',')
    n += 1
    sum += float(list[-1])

mean = sum/n
print mean
