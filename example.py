import matplotlib
from matplotlib import pyplot as plt
from matplotlib import animation
import numpy as np
import time
from genius_test import GENIUS
from useful_funcs import PointGrab
from proc_func import separate
import json
import os

point_set = PointGrab()
savehist = input('save history? [y/n]')
class npencode(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, np.int64):
            return int(o)
        return json.JSONEncoder.default(self, o)

n_time = time.process_time()

momentotruth = GENIUS(point_set)
momentotruth.cycle()
momentotruth.post_opt()
held_history = momentotruth.history
e_time = time.process_time() - n_time
print(e_time)


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


pathlist, pathdirectory = separate(held_history[-1][0].copy(), point_set.d_matrix, 20, 5)
held_history.append(pathlist)

if savehist.lower() in ['y', 'yes', 'ye', 'yeah']:
    hispath = os.getcwd() + "\\histories\\" + point_set.ptu + ".json"
    with open(hispath, 'w+', encoding='utf8') as f:
        json.dump(held_history, f, cls=npencode)

    patpath = os.getcwd() + "\\starting_paths\\" + point_set.ptu + ".json"
    with open(patpath, 'w+', encoding='utf8') as f:
        json.dump(pathlist, f, cls=npencode)
    
    dirpath = os.getcwd() + "\\path_dir\\" + point_set.ptu + ".json"
    with open(dirpath, 'w+', encoding='utf8') as f:
        json.dump(pathdirectory, f, cls=npencode)

history = parse_history(held_history)


fig, ax = plt.subplots()
ax.set(xlim=(-5.1, 5.1), ylim=(-5.1, 5.1))
for i, n in enumerate(point_set.names):
    ax.annotate(n, (point_set.xpoints[i], point_set.ypoints[i]))
shape = matplotlib.patches.Polygon(history[0], closed=False, fill=False)
ax.add_patch(shape)

def animate(frame):
    shape.set_xy(history[frame])
    return shape,

animation = animation.FuncAnimation(fig, animate, frames=len(held_history), interval=200, repeat_delay=10000)
plt.show()