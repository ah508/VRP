import matplotlib
from matplotlib import pyplot as plt
import numpy as np
import math
import random
import pprint

class Tracker:
    def __init__(self):
        self.xpoints = []
        self.ypoints = []
        self.points_costs = []
        self.points_names = []
        self.points_colors = []
        self.point_update(0, 0, 'origin', color='r')

    def point_update(self, xcoord, ycoord, name, cost=0, color='b'):
        self.xpoints.append(xcoord)
        self.ypoints.append(ycoord)
        self.points_costs.append(cost)
        self.points_colors.append(color)
        self.points_names.append(name)

    def d_formula(self, xdiff, ydiff):
        return math.sqrt(xdiff**2 + ydiff**2)

    def dist_get(self):
        self.d_matrix = np.zeros((len(self.xpoints), len(self.xpoints)))
        for i in range(0, len(self.d_matrix)):
            for j in range(0, len(self.d_matrix)):
                if i != j:
                    xdiff = self.xpoints[j] - self.xpoints[i]
                    ydiff = self.ypoints[j] - self.ypoints[i]
                    dist = self.d_formula(xdiff, ydiff) + self.points_costs[j]
                    self.d_matrix[i][j] = dist

point_set = Tracker()
for i in range(1, 40):
    identifier = str(i)
    nogo = True
    while nogo:
        xloc = random.uniform(-5, 5)
        yloc = random.uniform(-5, 5)
        if xloc not in point_set.xpoints and yloc not in point_set.ypoints:
            nogo = False
    cost = random.uniform(0, 1)
    point_set.point_update(xloc, yloc, identifier, cost=cost)

point_set.dist_get()

def find_nearest(route, distances):
    cur_node = route[-1]
    adjacent = distances[cur_node][:]
    print(adjacent)
    for i in range(0, len(adjacent)):
        if i in route:
            adjacent[i] = 0
    next_min = min(i for i in adjacent if i > 0)
    print(np.where(adjacent==next_min)[0])
    return np.where(adjacent==next_min)[0][0]
    
def greedy_path(points):
    route = [0]
    for i in range(0, len(points.d_matrix)):
        if i < len(points.d_matrix)-1:
            nearest = find_nearest(route, points.d_matrix)
            route.append(nearest)
        else:
            route.append(0)
    print(len(route))
    return route


greed_path = greedy_path(point_set)
print(greed_path)
path_pointsx = [point_set.xpoints[i] for i in greed_path]
path_pointsy = [point_set.ypoints[i] for i in greed_path]

testing = plt.scatter(point_set.xpoints, point_set.ypoints, s=3, c=point_set.points_colors)
for i, n in enumerate(point_set.points_names):
    plt.annotate(n, (point_set.xpoints[i], point_set.ypoints[i]))
gx = plt.plot(path_pointsx, path_pointsy)
plt.grid()
plt.show()



