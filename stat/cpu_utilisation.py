with open("top.log") as f:
    content = f.readlines()
n = 0
sum = 0
for line in content:
    list = line.split('  ')
    user = list[1]
    user = float(user[0:3].replace(',','.'))
    sys = list[2]
    sys = float(sys[0:3].replace(',','.'))
    sum += user + sys
    n += 1

print sum/n