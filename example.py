import matplotlib
from matplotlib import pyplot as plt
from matplotlib import animation
import numpy as np
import time
from genius_test import GENIUS
from useful_funcs import PointGrab

point_set = PointGrab()

n_time = time.process_time()

momentotruth = GENIUS(point_set)
momentotruth.cycle()
momentotruth.post_opt()
e_time = time.process_time() - n_time
print(e_time)


def parse_history(history):
    parsed_hist = []
    for moment in history:
        xy = np.zeros((len(moment)+2, 2))
        xy[0, 0] = 0
        xy[0, 1] = 0
        nextvert = 0
        for vertex in range(0, len(moment)+1):
            xy[vertex, 0] = point_set.xpoints[nextvert]
            xy[vertex, 1] = point_set.ypoints[nextvert]
            nextvert = moment[nextvert]
        
        parsed_hist.append(xy)
    return parsed_hist

print(momentotruth.history[-1])
history = parse_history(momentotruth.history)

fig, ax = plt.subplots()
ax.set(xlim=(-5.1, 5.1), ylim=(-5.1, 5.1))
for i, n in enumerate(point_set.names):
    ax.annotate(n, (point_set.xpoints[i], point_set.ypoints[i]))
shape = matplotlib.patches.Polygon(history[0], closed=False, fill=False)
ax.add_patch(shape)

def animate(frame):
    shape.set_xy(history[frame])
    return shape,

animation = animation.FuncAnimation(fig, animate, frames=len(momentotruth.history)-1, interval=300, repeat_delay=5000)
plt.show()