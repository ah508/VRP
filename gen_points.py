import numpy as np
import math
import random
import json
import os

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
        self.d_matrix = self.d_matrix.tolist()
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

t_dict = {
    'xpoints' : point_set.xpoints,
    'ypoints' : point_set.ypoints,
    'costs' : point_set.points_costs,
    'names' : point_set.points_names,
    'colors' : point_set.points_colors,
    'd_matrix' : point_set.d_matrix
}

tag = str(random.randint(0, 1000))
path = os.getcwd() + "\\point_sets\\" + tag
with open(path, 'w+', encoding='utf8') as f:
    json.dump(t_dict, f)


