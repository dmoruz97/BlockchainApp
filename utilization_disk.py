import sys
import os
import numpy as np
import math

name = "disk.log"
sample=[]

if os.path.isfile(name):
    with open(name, 'r') as f:
        for cnt, line in enumerate(f):
            if line.startswith("DEBUG:root:K"):
                val = float(line.split(" ")[3])
                sample.append(val)

    print(sample)
    print(np.mean(sample))
