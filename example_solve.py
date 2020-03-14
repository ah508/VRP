from info_work import get_working_map, parse_addresses, parse_list, Setup
import googlemaps
from maps_api import fetch_new
import os
import json
import math
import time
from genius import GENIUS
from route_settings import default
import numpy as np
from tabu import TABU
from proc_func2 import separate
from safekeeping import dist as d_key


def solve(client):
    dist, dur, backmap, addresses = get_working_map(client)
    add_vec = []
    fuel_vec = []
    xpoints = []
    ypoints = []
    for i in backmap:
        hold = addresses[i]
        with open(os.getcwd()+'\\clients\\'+client+'\\customer_info\\'+hold+'.json', 'r') as f:
            custinfo = json.load(f)
        add_vec.append(custinfo['proj_time'])
        fuel_vec.append(custinfo['proj_fuel'])
        ypoints.append(custinfo['lat'])
        xpoints.append(custinfo['lon'])
    add_vec = np.array(add_vec)
    # class Setup:
    #     def __init__(self, dur, dist, tcost, dcost, x, y):
    #         self.d_matrix = dur
    #         self.c_matrix = np.divide(dist, default['fuel_econ'])
    #         self.time_cost = tcost
    #         self.fuel_cost = dcost
    #         for loc in range(0, len(self.d_matrix)):
    #             for dest in range(0, len(self.d_matrix)):
    #                 if self.d_matrix[loc, dest] != 0:
    #                     self.d_matrix[loc, dest] += self.time_cost[dest]
    #         for loc in range(0, len(self.c_matrix)):
    #             for dest in range(0, len(self.c_matrix)):
    #                 if self.c_matrix[loc, dest] != 0:
    #                     self.c_matrix[loc, dest] += self.fuel_cost[dest]
    #         self.xpoints = x
    #         self.ypoints = y
    points = Setup(dur, dist, add_vec, fuel_vec, xpoints, ypoints)
    initials = int(math.sqrt(len(points.xpoints))//2)
    forray = []
    forray_costs = []
    for i in range(0, initials):
        temp_sol = GENIUS(points)
        temp_sol.cycle()
        temp_sol.post_opt()
        forray.append(temp_sol)
        forray_costs.append(temp_sol.route_cost)

    cost_func = cost_def(default['cost_params']['labor'], default['cost_params']['fuel'])
    ideal = forray[forray_costs.index(min(forray_costs))]
    pathlist, pathdirectory = separate(ideal.edges.copy(), ideal.duration, ideal.fuel_cost, default['time_const'], default['fuel_const'], len(default['crew_params']))
    procedure = TABU(points, pathlist, pathdirectory, default['fuel_const'], default['time_const'], len(default['crew_params']), len(points.xpoints), cost_func)
    procedure.tabu_search()
    save = input('save this solution?[y/n]: ')
    if save.lower() in ['y', 'yes', 'ye', 'yeah']:
        t = time.localtime()
        timestamp = str(t.tm_mon) + '/' + str(t.tm_mday) + '/' + str(t.tm_year) + ' @ ' + str(t.tm_hour) + ':' + str(t.tm_min)
        # history = parse_history(procedure.history, points)
        feasible, infeasible = grabinfo(procedure, points)
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
            # 'history' : history,
            'solve parameters' : None
        }
        n1 = 0
        # savepath = os.getcwd()+'\\clients\\'+client+'\\route_info\\solution_dumps'
        savepath = os.getcwd()+'\\clients\\'+client+'\\route_info'
        while n1 < 10:
            name = input('give the solution a name: ')
            if name in os.listdir(savepath):
                print('that file already exists.')
                overwrite = input('would you like to overwrite this file?[y/n]: ')
                if overwrite.lower() in ['yes', 'ye', 'yeah', 'y']:
                    with open(savepath+'\\'+name+'.json', 'w') as f:
                        json.dump(solveinfo, f, cls=npencode)
                    print('saved.')
                    break
                else:
                    rename = input('rename this solution?[y/n]: ')
                    if rename in ['n', 'no', 'nope', 'nay']:
                        print('solution not saved.')
                        break
            else:
                with open(savepath+'\\'+name+'.json', 'w') as f:
                    json.dump(solveinfo, f, cls=npencode)
                print('saved.')
                break
    print(' ')

def grabinfo(solvedcase, p_set):
    try:
        t_cost = []
        d_cost = []
        for circuit in solvedcase.s_star:
            if set(circuit) != set([None]):
                t_cost.append(solvedcase.time_cost(circuit))
                d_cost.append(solvedcase.gas_cost(circuit))
            else:
                t_cost.append(None)
                d_cost.append(None)
        s_shape = parse_history([solvedcase.s_star], p_set)
        feasible = {
            'sol' : solvedcase.s_star,
            'poly' : s_shape,
            'time' : t_cost,
            'fuel' : d_cost
        }
    except AttributeError:
        feasible = {
            'sol' : None,
            'poly' : None,
            'time' : None,
            'fuel' : None
        }
    it_cost = []
    id_cost = []
    for circuit in solvedcase.sn_star:
        if set(circuit) != set([None]):
            it_cost.append(solvedcase.time_cost(circuit))
            id_cost.append(solvedcase.gas_cost(circuit))
        else:
            it_cost.append(None)
            id_cost.append(None)
    sn_shape = parse_history([solvedcase.sn_star], p_set)
    infeasible = {
        'sol' : solvedcase.sn_star,
        'poly' : sn_shape,
        'time' : it_cost,
        'fuel' : id_cost
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
        if isinstance(o, np.int32):
            return(int(o))
        if isinstance(o, np.ndarray):
            return o.tolist()
        return json.JSONEncoder.default(self, o)

def cost_def(labor, fuel):
    def cost_func(time_vec, fuel_vec):
        labor_cost = sum([labor[i]*time_vec[i] for i in range(0, len(labor)) if time_vec[i] != None])
        fuel_cost = sum([fuel[i]*fuel_vec[i] for i in range(0, len(fuel)) if fuel_vec[i] != None])
        return labor_cost + fuel_cost
    return cost_func


############################################################################################      

# def naive_addition(client):
#     print('WARNING')
#     print('this is NOT for quick estimations')
#     goodness = input('are you sure you would like to run this process?: ')
#     if goodness.lower() not in ['yes', 'y']:
#         print('bonk')
#         exit()

#     addresses, omitted, working = parse_addresses(client)

#     new_cust = input('input a new customer: ')
#     lat = input('input latitude: ')
#     lon = input('input longitude: ')
#     est = input('input a projected time: ') #later replace this with several different parameters and build from the model

#     fetch_new(client, new_cust)
    
#     path = os.getcwd() + '\\clients\\' + client
#     with open(path + '\\infodump_vert.json', 'r') as f:
#         vertical = json.load(f)
#     if vertical['destination_addresses'][0] != '':
#         with open(path + '\\infodump_horz.json', 'r') as f:
#             horizontal = json.load(f)
#         distance = parse_list(client, 'distance')
#         duration = parse_list(client, 'time')
#         addresses.append(vertical['destination_addresses'][0])
#         horz_list_dur = []
#         horz_list_dist = []
#         for dest in horizontal['rows'][0]['elements']:
#             horz_list_dur.append(dest['duration']['value'])
#             horz_list_dist.append(dest['distance']['value'])
#         horz_list_dist.append(0)
#         horz_list_dur.append(0)
#         for i in range(0, len(distance)):
#             distance[i].append(vertical['rows'][i]['elements'][0]['distance']['value'])
#             duration[i].append(vertical['rows'][i]['elements'][0]['duration']['value'])
#         distance.append(horz_list_dist)
#         duration.append(horz_list_dur)

#         add_vec = []
#         xpoints = []
#         ypoints = []
#         for hold in addresses[:-1]:
#             with open(os.getcwd()+'\\clients\\'+client+'\\customer_info\\'+hold+'.json', 'r') as f:
#                 custinfo = json.load(f)
#             add_vec.append(custinfo['proj_time'])
#             ypoints.append(custinfo['lat'])
#             xpoints.append(custinfo['lon'])
#         add_vec.append(float(est))
#         xpoints.append(float(lon))
#         ypoints.append(float(lat))
#         add_vec = np.array(add_vec)
#         dist = np.array(distance)
#         dur = np.array(duration)

#         class Setup:
#             def __init__(self, dur, dist, cost, x, y):
#                 self.c_matrix = dist
#                 self.d_matrix = dur
#                 self.costvec = cost
#                 for loc in range(0, len(self.d_matrix)):
#                     for dest in range(0, len(self.d_matrix)):
#                         if self.d_matrix[loc, dest] != 0:
#                             self.d_matrix[loc, dest] += self.costvec[dest]
#                 self.xpoints = x
#                 self.ypoints = y
        
#         points = Setup(dur, dist, add_vec, xpoints, ypoints)
#         initials = int(math.sqrt(len(points.xpoints))//2)
#         forray = []
#         forray_costs = []
#         for i in range(0, initials):
#             temp_sol = GENIUS(points)
#             temp_sol.cycle()
#             temp_sol.post_opt()
#             forray.append(temp_sol)
#             forray_costs.append(temp_sol.route_cost)
#         ideal = forray[forray_costs.index(min(forray_costs))]
#         t_constraint = input('please enter a (general) time constraint [in seconds]: ')
#         r_num = input('please enter a limit on the number of routes: ')
#         d_constraint = input('please enter a (general) distance constraint [in meters]: ')
#         pathlist, pathdirectory = separate(ideal.edges.copy(), ideal.costs, int(t_constraint), int(r_num))
#         # ideal.history.append(pathlist)
#         procedure = TABU(points, pathlist, pathdirectory, int(d_constraint), int(t_constraint), int(r_num), len(points.xpoints))
#         procedure.tabu_search()
#         save = input('save this solution?[y/n]: ')
#         if save.lower() in ['y', 'yes', 'ye', 'yeah']:
#             t = time.localtime()
#             timestamp = str(t.tm_mon) + '/' + str(t.tm_mday) + '/' + str(t.tm_year) + ' @ ' + str(t.tm_hour) + ':' + str(t.tm_min)
#             # history = parse_history(procedure.history, points)
#             feasible, infeasible = grabinfo(procedure, points)
#             selection_frequency = ['{:.3%}'.format(i) for i in procedure.select_freq]
#             solveinfo = {
#                 'timestamp' : timestamp,
#                 'address list' : addresses,
#                 'map' : list(range(0, len(addresses))),
#                 'best feasible' : feasible,
#                 'best infeasible' : infeasible,
#                 'selection freqs' : selection_frequency,
#                 'duration matrix' : dur,
#                 'distance matrix' : dist,
#                 'projection vector' : add_vec,
#                 # 'history' : history,
#                 'solve parameters' : None
#             }
#             n1 = 0
#             savepath = os.getcwd()+'\\clients\\'+client+'\\route_info'
#             while n1 < 10:
#                 name = input('give the solution a name: ')
#                 if name in os.listdir(savepath):
#                     print('that file already exists.')
#                     overwrite = input('would you like to overwrite this file?[y/n]: ')
#                     if overwrite.lower() in ['yes', 'ye', 'yeah', 'y']:
#                         with open(savepath+'\\'+name+'.json', 'w') as f:
#                             json.dump(solveinfo, f, cls=npencode)
#                         print('saved.')
#                         break
#                     else:
#                         rename = input('rename this solution?[y/n]: ')
#                         if rename in ['n', 'no', 'nope', 'nay']:
#                             print('solution not saved.')
#                             break
#                 else:
#                     with open(savepath+'\\'+name+'.json', 'w') as f:
#                         json.dump(solveinfo, f, cls=npencode)
#                     print('saved.')
#                     break
#         print(' ')
#     else:
#         print('failure to locate address')

