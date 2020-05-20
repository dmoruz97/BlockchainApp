import sys
import os
import numpy as np
import math

name = "disk1.log"
sample=[]

if os.path.isfile(name):
    with open(name, 'r') as f:
        for cnt, line in enumerate(f):
            if line.startswith("DEBUG:root:K"):
                val = float(line.split(" ")[3])
                sample.append(val)

    print(sample)
    print(len(sample))

    print(np.mean(sample))
    print(np.var(sample))
    print(np.std(sample))

