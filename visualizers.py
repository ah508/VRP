import numpy as np
import matplotlib
from matplotlib import pyplot as plt
from matplotlib import animation
from useful_funcs import route_grab, parse_addresses
import os
import json
import re
import textwrap

def display_prompt(client):
    while True:
        print('-----------------------------------------------------------')
        print('[b]asic          - view the client customer set')
        print('[t]race          - view a trace')
        print('[c]ompare        - compare traces or solutions')
        print('[h]istory        - [deprecated] view a solution history')
        print('[s]olution       - [deprecated] view a solution')
        print('[e]xit           - return to the operations menu')
        print(' ')
        choice = input('what would you like to display?: ')
        choice = choice.lower()
        try:
            if 'basic'.startswith(choice):
                disp_addresses(client)
            elif 'history'.startswith(choice):
                disp_history(client)
            elif 'solution'.startswith(choice):
                disp_fin(client)
            elif 'trace'.startswith(choice):
                predisp_trace(client)
            elif 'compare'.startswith(choice):
                predisp_trace(client, m=True) #needs a wrapper to determine if sol or trace
            elif 'exit'.startswith(choice):
                print('returning to operation menu')
                print(' ')
                break
            else:
                print('that was not a valid option')
            print(' ')
        except (FileNotFoundError, AttributeError):
            print('invalid input')
            print('returning to operation menu')
            print(' ')

def get_submap(client):
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
    xdiff = (max_x - min_x)*0.1
    max_y = max(ypoints)
    min_y = min(ypoints)
    ydiff = (max_y - min_y)*0.1
    x = [xpoints, min_x-xdiff, max_x+xdiff]
    y = [ypoints, min_y-ydiff, max_y+ydiff]
    return names, color, x, y

def disp_addresses(client):
    names, color, x, y = get_submap(client)
    plt.scatter(x[0], y[0], c=color, alpha=0.7)
    plt.xlim(x[1], x[2])
    plt.ylim(y[1], y[2])
    for i, n in enumerate(names):
        plt.annotate(n, (x[0][i], y[0][i]), fontsize=5)
    plt.show()

def disp_history(client):
    sol_info, sol_path = route_grab(client)
    history = np.array(sol_info['history'])
    names, color, x, y = get_submap(client)
    
    fig, ax = plt.subplots()
    ax.set(xlim=(x[1], x[2]), ylim=(y[1], y[2]))
    for i, n in enumerate(names):
        ax.annotate(n, (x[0][i], y[0][i]), fontsize=5)
    ax.scatter(x[0], y[0], c=color, alpha=0.7)
    shape = matplotlib.patches.Polygon(history[0], closed=False, fill=False)
    ax.add_patch(shape)

    def animate(frame):
        shape.set_xy(history[frame])
        return shape,

    animated = animation.FuncAnimation(fig, animate, frames=len(history), interval=50, repeat_delay=10000)
    plt.show()

def disp_fin(client):
    sol_info, sol_path = route_grab(client)

    b_feas = False
    b_infeas = False
    if sol_info['best feasible']['poly'] != None:
        b_feas = np.array(sol_info['best feasible']['poly'][0])
    b_infeas = np.array(sol_info['best infeasible']['poly'][0])
    names, color, x, y = get_submap(client)
    
    fig, ax = plt.subplots()
    ax.set(xlim=(x[1], x[2]), ylim=(y[1], y[2]))
    for i, n in enumerate(names):
        ax.annotate(n, (x[0][i], y[0][i]), fontsize=5)
    ax.scatter(x[0], y[0], c=color, alpha=0.7, label='locations')
    shapelist = []
    if not isinstance(b_feas, bool):
        shape1 = matplotlib.patches.Polygon(b_feas, closed=False, fill=False, color='g', alpha=.9, label='feasible')
        ax.add_patch(shape1)
        shapelist.append(shape1)
    if not isinstance(b_infeas, bool):
        shape2 = matplotlib.patches.Polygon(b_infeas, closed=False, fill=False, color='r', alpha=.9, label='infeasible')
        ax.add_patch(shape2)
        shapelist.append(shape2)
    leg = ax.legend(loc='upper left', fancybox=True, shadow=True)
    leg.get_frame().set_alpha(0.4)

    shaped = {}
    for legpatch, origpatch in zip(leg.get_patches(), shapelist):
        legpatch.set_picker(5)
        shaped[legpatch] = origpatch

    def onpick(event):
        legpatch = event.artist
        origpatch = shaped[legpatch]
        vis = not origpatch.get_visible()
        origpatch.set_visible(vis)
        if vis:
            legpatch.set_alpha(1.0)
        else:
            legpatch.set_alpha(0.2)
        fig.canvas.draw()

    fig.canvas.mpl_connect('pick_event', onpick)

    plt.show()

def predisp_trace(client, m=False):
    if not m:
        sol_info, name = route_grab(client, p_type='t')
        sol = sol_info['poly']
        disp_trace(client, [name], [sol])
    else:
        name = []
        sol = []
        pattern = re.compile('(?<=\\\)[a-zA-Z_0-9]*(?=\.json)') #this is the dumbest thing
        while True:
            stype = input('is this a [t]race or a [s]olution?: ')
            if 'trace'.startswith(stype):
                sol_info, lname = route_grab(client, p_type='t')
                lname = '\\' + lname
                sol.append(sol_info['poly'])
            elif 'solution'.startswith(stype):
                sol_info, lname = route_grab(client)
                feas = input('[f]easible or [i]nfeasible?: ')
                if 'feasible'.startswith(feas):
                    sol.append(sol_info['best feasible']['poly'][0])
                elif 'infeasible'.startswith(feas):
                    sol.append(sol_info['best infeasible']['poly'][0])
            nname = pattern.search(lname).group(0)
            name.append(nname)
            another = input('another?[y/n]: ')
            if another.lower() not in ['y', 'yes', 'yeah', 'ye']:
                break
        disp_trace(client, name, sol)

def disp_trace(client, sol_name, pre_loc):
    sol = {}
    for i in range(0, len(sol_name)):
        sol[sol_name[i]] = np.array(pre_loc[i])
    
    names, color, x, y = get_submap(client)
    
    fig, ax = plt.subplots()
    ax.set(xlim=(x[1], x[2]), ylim=(y[1], y[2]))
    for i, n in enumerate(names):
        ax.annotate(n, (x[0][i], y[0][i]), fontsize=5)
    shapelist = []
    shaperef = {}
    ax.scatter(x[0], y[0], c=color, alpha=0.7, label='locations')
    val_col = ['k', 'b', 'm', 'c', 'r', 'g']
    for k, v in sol.items():
        shaperef[k] = matplotlib.patches.Polygon(v, closed=False, fill=False, alpha=.9, label=k)
        try:
            shaperef[k].set_color(val_col.pop(-1))
        except IndexError:
            pass
        ax.add_patch(shaperef[k])
        shapelist.append(shaperef[k])
    leg = ax.legend(loc='best', fancybox=True, shadow=True)
    leg.get_frame().set_alpha(0.4)

    shaped = {}
    for legpatch, origpatch in zip(leg.get_patches(), shapelist):
        legpatch.set_picker(5)
        shaped[legpatch] = origpatch

    def onpick(event):
        legpatch = event.artist
        origpatch = shaped[legpatch]
        vis = not origpatch.get_visible()
        origpatch.set_visible(vis)
        if vis:
            legpatch.set_alpha(1.0)
        else:
            legpatch.set_alpha(0.2)
        fig.canvas.draw()

    fig.canvas.mpl_connect('pick_event', onpick)

    plt.show()