import numpy as np
import matplotlib
from matplotlib import pyplot as plt
from matplotlib import animation
from maps_api import parse_addresses
import os
import json
import textwrap

def display_prompt(client):
    disp_addresses(client)

def disp_addresses(client):
    addresses, omitted, working = parse_addresses(client)
    backmap = []
    nonmap = []
    for i in range(0, len(addresses)):
        if addresses[i] in working:
            backmap.append(i)
        else:
            nonmap.append(i)
    xpoints = [None] * len(addresses)
    ypoints = [None] * len(addresses)
    color = [None] * len(addresses)
    names = [None] * len(addresses)
    for i in range(0, len(addresses)):
        hold = addresses[i]
        short = textwrap.shorten(hold, 18, placeholder='...')
        with open(os.getcwd()+'\\clients\\'+client+'\\customer_info\\'+hold+'.json', 'r') as f:
            custinfo = json.load(f)
        if i == 0:
            color[i] = 'r'
        elif i in backmap:
            color[i] = 'g'
        elif i in nonmap:
            color[i] = 'k'
        names[i] = short
        ypoints[i] = custinfo['lat']
        xpoints[i] = custinfo['lon']
    max_x = max(xpoints)
    min_x = min(xpoints)
    xdiff = (max_x - min_x)*1.05
    max_y = max(ypoints)
    min_y = min(ypoints)
    ydiff = (max_y - min_y)*1.05

    plt.scatter(xpoints, ypoints, c=color, alpha=0.7)
    plt.xlim(min_x - xdiff, max_x + xdiff)
    plt.ylim(min_y - ydiff, max_y + ydiff)
    for i, n in enumerate(names):
        plt.annotate(n, (xpoints[i], ypoints[i]))
    plt.show()

    

def disp_history(client):
    pass