import matplotlib
from matplotlib import pyplot as plt
import numpy as np
import time
from genius_test import GENI
from useful_funcs import PointGrab
s_time = time.process_time()

point_set = PointGrab()
def fresh_edge(previous, visited, d_matrix):
    adjacent = d_matrix[previous][:]
    complete = True
    for i in range(0, len(adjacent)):
        if i in visited:
            adjacent[i] = 0
        if i not in visited:
            complete = False
    if not complete:
        next_min = min(i for i in adjacent if i > 0)
        next_index = np.where(adjacent==next_min)[0][0]
        return previous, next_index
    return previous, 0

def greedalg(points):
    connected = set()
    last_point = 0
    connected.add(last_point)
    edge_set = set()
    incomplete = True
    while incomplete:
        next_edge = fresh_edge(last_point, connected, points.d_matrix)
        edge_set.add(next_edge)
        last_point = next_edge[1]
        connected.add(last_point)
        if last_point == 0:
            incomplete = False
    return edge_set

greedy_path = greedalg(point_set)

for edge in greedy_path:
    xcoords= [point_set.xpoints[edge[0]], point_set.xpoints[edge[1]]]
    ycoords = [point_set.ypoints[edge[0]], point_set.ypoints[edge[1]]]
    plt.plot(xcoords, ycoords, c='b')

testing = plt.scatter(point_set.xpoints, point_set.ypoints, s=3, c=point_set.colors)
for i, n in enumerate(point_set.names):
    plt.annotate(n, (point_set.xpoints[i], point_set.ypoints[i]))
t_time = time.process_time() - s_time
print(t_time)
plt.grid()
plt.show()
# plt.clf()

# n_time = time.process_time()

# momentotruth = GENI(point_set)
# momentotruth.cycle()
# for v, v1 in enumerate(momentotruth.edges):
#     xcoords= [point_set.xpoints[v], point_set.xpoints[v1]]
#     ycoords = [point_set.ypoints[v], point_set.ypoints[v1]]
#     plt.plot(xcoords, ycoords, c='b')
# testing2 = plt.scatter(point_set.xpoints, point_set.ypoints, s=3, c=point_set.colors)
# e_time = time.process_time() - n_time
# print(e_time)

# plt.show()