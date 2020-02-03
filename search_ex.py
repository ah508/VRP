import os
import json
from search_test import SEARCH
from useful_funcs import PointGrab
import numpy as np
import math
import matplotlib
from matplotlib import pyplot as plt
from matplotlib import animation
import time
from tabu import TABU

point_set = PointGrab()
hispath = os.getcwd() + "\\histories\\" + point_set.ptu + ".json"
stapath = os.getcwd() + "\\starting_paths\\" + point_set.ptu + ".json"
dirpath = os.getcwd() + "\\path_dir\\" + point_set.ptu + ".json"
with open(hispath, 'r') as f:
    old_history = json.load(f)
print(type(old_history))
with open(stapath, 'r') as f:
    start_path = json.load(f)
print(type(start_path))
with open(dirpath, 'r') as f:
    path_dir = json.load(f)
print(type(path_dir))

q = 25
searchproc = TABU(point_set, old_history, start_path, path_dir, 1000, 25, q, 40)
searchproc.tabu_search()
try:
    searchproc.history.append(searchproc.s_star)
except AttributeError:
    searchproc.history.append(searchproc.sn_star)

def parse_history(history):
    parsed_hist = []
    for moment in history:
        xy = []
        xy_app = []
        for path in moment:
            if set(path) == set([None]):
                continue
            xy_app_app = np.array([point_set.xpoints[0], point_set.ypoints[0]])
            nextvert = path[0]
            try:
                xy_app = np.vstack((xy_app, xy_app_app))
            except ValueError:
                xy_app = xy_app_app
            xy_app_app = np.array([point_set.xpoints[nextvert], point_set.ypoints[nextvert]])
            nextvert = path[nextvert]
            xy_app = np.vstack((xy_app, xy_app_app))
            loopsafe = 0
            while nextvert != path[0] and loopsafe < 1000:
                xy_app_app = np.array([point_set.xpoints[nextvert], point_set.ypoints[nextvert]])
                nextvert = path[nextvert]
                xy_app = np.vstack((xy_app, xy_app_app))
                loopsafe += 1
            xy_app_app = np.array([point_set.xpoints[0], point_set.ypoints[0]])
            xy_app = np.vstack((xy_app, xy_app_app))
            try:
                xy = np.vstack((xy, xy_app))
            except ValueError:
                xy = xy_app
        parsed_hist.append(xy)
    return parsed_hist

history = parse_history(searchproc.history)

fig, ax = plt.subplots()
ax.set(xlim=(-5.1, 5.1), ylim=(-5.1, 5.1))
for i, n in enumerate(point_set.names):
    ax.annotate(n, (point_set.xpoints[i], point_set.ypoints[i]))
shape = matplotlib.patches.Polygon(history[0], closed=False, fill=False)
ax.add_patch(shape)

def animate(frame):
    shape.set_xy(history[frame])
    return shape,

animation = animation.FuncAnimation(fig, animate, frames=len(searchproc.history), interval=50, repeat_delay=10000)
plt.show()