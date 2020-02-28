from info_work import get_working_map
import os
import json
import math
import time
from genius import GENIUS
import numpy as np
from tabu import TABU
from proc_func2 import separate

def solve(client):
    dist, dur, backmap, addresses = get_working_map(client)
    add_vec = []
    xpoints = []
    ypoints = []
    for i in backmap:
        hold = addresses[i]
        with open(os.getcwd()+'\\clients\\'+client+'\\customer_info\\'+hold+'.json', 'r') as f:
            custinfo = json.load(f)
        add_vec.append(custinfo['proj_time'])
        xpoints.append(custinfo['lat'])
        ypoints.append(custinfo['lon'])
    class Setup:
        def __init__(self, dur, dist, cost, x, y):
            self.c_matrix = dist
            self.d_matrix = dur
            for row in self.d_matrix:
                row += cost
            self.xpoints = x
            self.ypoints = y
    points = Setup(dur, dist, add_vec, xpoints, ypoints)
    initials = math.sqrt(len(points.xpoints))//2
    forray = []
    forray_costs = []
    for i in range(0, initials):
        temp_sol = GENIUS(points)
        temp_sol.cycle()
        temp_sol.post_opt()
        forray.append(temp_sol)
        forray_costs.append(temp_sol.route_cost)
    ideal = forray[forray_costs.index(min(forray_costs))]
    # ADD INPUT FOR CONSTRAINTS
    pathlist, pathdirectory = separate(ideal.history[-1][0].copy(), ideal.d_matrix, 28800, 5)
    ideal.history.append(pathlist)
    procedure = TABU(points, ideal.history, pathlist, pathdirectory, 128748, 28800, 5, len(points.xpoints))
    procedure.tabu_search()
    save = input('save this solution?[y/n]: ')
    if save.lower() in ['y', 'yes', 'ye', 'yeah']:
        t = time.localtime()
        timestamp = str(t.tm_mon) + '/' + str(t.tm_mday) + '/' + str(t.tm_year) + ' @ ' + str(t.tm_hour) + ':' + str(t.tm_min)
        history = parse_history(procedure.history, points)
        feasible, infeasible = grabinfo(procedure)
        selection_frequency = ['{:.3%}'.format(i) for i in procedure.select_freq]
        solveinfo = {
            'timestamp' : timestamp,
            'address list' : addresses,
            'map' : backmap,
            'best feasible' : feasible,
            'best infeasible' : infeasible,
            'selection freqs' : selection_frequency,
            'duration matrix' : dur,
            'distance matrix' : dist,
            'projection vector' : add_vec,
            'history' : history,
            'solve parameters' : None
        }
        n1 = 0
        savepath = os.getcwd()+'\\clients\\'+client+'\\route_info'
        while n1 < 10:
            name = input('give the solution a name: ')
            if name in os.listdir(savepath):
                print('that file already exists.')
                overwrite = input('would you like to overwrite this file?[y/n]: ')
                if overwrite.lower() in ['yes', 'ye', 'yeah', 'y']:
                    with open(savepath+'\\'+name, 'w') as f:
                        json.dump(solveinfo, f, cls=npencode)
                    print('saved.')
                else:
                    rename = input('rename this solution?[y/n]: ')
                    if rename in ['n', 'no', 'nope', 'nay']:
                        print('solution not saved.')
                        break
            else:
                with open(savepath+'\\'+name, 'w') as f:
                    json.dump(solveinfo, f, cls=npencode)
                print('saved.')
    print(' ')

def grabinfo(solvedcase):
    try:
        t_cost = []
        d_cost = []
        for circuit in solvedcase.s_star:
            if set(circuit) != set([None]):
                t_cost.append(solvedcase.circuit_cost(circuit))
                d_cost.append(solvedcase.point_cost(circuit))
            else:
                t_cost.append(None)
                d_cost.append(None)
        feasible = {
            'sol' : solvedcase.s_star,
            'time' : t_cost,
            'dist' : d_cost
        }
    except AttributeError:
        feasible = {
            'sol' : None,
            'time' : None,
            'dist' : None
        }
    it_cost = []
    id_cost = []
    for circuit in solvedcase.sn_star:
        if set(circuit) != set([None]):
            it_cost.append(solvedcase.circuit_cost(circuit))
            id_cost.append(solvedcase.point_cost(circuit))
        else:
            it_cost.append(None)
            id_cost.append(None)
    infeasible = {
        'sol' : solvedcase.sn_star,
        'time' : it_cost,
        'dist' : id_cost
    }
    return feasible, infeasible
        
# def translate(solution, backmap, initial):
#     translation = []
#     for route in solution:
#         spec = [None] * len(initial)
#         n = 0
#         trace = True
#         tracker1 = 0
#         tracker2 = 0
#         spec[tracker1] = backmap[route[tracker2]]
#         tracker1 = spec[tracker1]
#         tracker2 = route[tracker2]
#         while trace and (n <= len(initial) + 1):
#             spec[tracker1] = backmap[route[tracker2]]
#             tracker1 = spec[tracker1]
#             tracker2 = route[tracker2]
#             if tracker1 == 0:
#                 print(f'trackstatus: {tracker1 == tracker2}')
#                 trace = False
#             n += 1
#         translation.append(spec)
#     return translation

def parse_history(history, point_set):
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
    
class npencode(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, np.int64):
            return int(o)
        return json.JSONEncoder.default(self, o)
        



