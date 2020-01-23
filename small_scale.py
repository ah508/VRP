import matplotlib
from matplotlib import pyplot as plt
import numpy as np
import time
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

# def find_nearest(route, distances):
#     cur_node = route[-1]
#     adjacent = distances[cur_node][:]
#     print(adjacent)
#     for i in range(0, len(adjacent)):
#         if i in route:
#             adjacent[i] = 0
#     next_min = min(i for i in adjacent if i > 0)
#     print(np.where(adjacent==next_min)[0])
#     return np.where(adjacent==next_min)[0][0]

# def greedy_path(points):
#     route = [0]
#     for i in range(0, len(points.d_matrix)):
#         if i < len(points.d_matrix)-1:
#             nearest = find_nearest(route, points.d_matrix)
#             route.append(nearest)
#         else:
#             route.append(0)
#     print(len(route))
#     return route


# greed_path = greedy_path(point_set)
# print(greed_path)
# path_pointsx = [point_set.xpoints[i] for i in greed_path]
# path_pointsy = [point_set.ypoints[i] for i in greed_path]

for edge in greedy_path:
    xcoords= [point_set.xpoints[edge[0]], point_set.xpoints[edge[1]]]
    ycoords = [point_set.ypoints[edge[0]], point_set.ypoints[edge[1]]]
    plt.plot(xcoords, ycoords, c='b')

testing = plt.scatter(point_set.xpoints, point_set.ypoints, s=3, c=point_set.colors)
for i, n in enumerate(point_set.names):
    plt.annotate(n, (point_set.xpoints[i], point_set.ypoints[i]))
# gx = plt.plot(path_pointsx, path_pointsy)

t_time = time.process_time() - s_time
print(t_time)

plt.grid()
plt.show()



