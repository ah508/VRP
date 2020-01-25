import matplotlib
from matplotlib import pyplot as plt
import numpy as np
import time
from genius_test import GENI
from useful_funcs import PointGrab

point_set = PointGrab()

n_time = time.process_time()

momentotruth = GENI(point_set)
momentotruth.cycle()
for i, n in enumerate(point_set.names):
    plt.annotate(n, (point_set.xpoints[i], point_set.ypoints[i]))
for v, v1 in enumerate(momentotruth.edges):
    xcoords= [point_set.xpoints[v], point_set.xpoints[v1]]
    ycoords = [point_set.ypoints[v], point_set.ypoints[v1]]
    plt.plot(xcoords, ycoords, c='b')
e_time = time.process_time() - n_time
print(e_time)

plt.grid
plt.show()