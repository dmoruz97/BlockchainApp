import sys
import os
import numpy as np
import math

name = sys.argv[1]
sample=[]

if os.path.isfile(name):
    with open(name, 'r') as f:
        for cnt, line in enumerate(f):
            val=float(line.split(" ")[2])/1000
            if val!=0:
                sample.append(val)

    print(sample)
    print((np.var(sample)))
    print(np.std(sample))