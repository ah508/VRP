import numpy as np
import json
import os

class Setup:
    def __init__(self, dur, dist, tcost, dcost, x, y, settings):
        self.d_matrix = dur
        self.c_matrix = np.divide(dist, settings['fuel_econ'])
        self.time_cost = tcost
        self.fuel_cost = dcost
        for loc in range(0, len(self.d_matrix)):
            for dest in range(0, len(self.d_matrix)):
                if self.d_matrix[loc, dest] != 0:
                    self.d_matrix[loc, dest] += self.time_cost[dest]
        for loc in range(0, len(self.c_matrix)):
            for dest in range(0, len(self.c_matrix)):
                if self.c_matrix[loc, dest] != 0:
                    self.c_matrix[loc, dest] += self.fuel_cost[dest]
        self.xpoints = x
        self.ypoints = y

class npencode(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, np.int64):
            return int(o)
        if isinstance(o, np.int32):
            return(int(o))
        if isinstance(o, np.ndarray):
            return o.tolist()
        return json.JSONEncoder.default(self, o)

def route_grab(client, p_type='s'):
    if p_type == 's':
        reference = 'solution_dumps'
        r_ref = input('which solution would you like to use?: ') + '.json'
    elif p_type == 't':
        reference = 'holding_routes'
        r_ref = input('which trace would you like to use?: ') + '.json'
    elif p_type == 'r':
        reference = 'routes'
        r_ref = input('which route would you like to use?: ') + '.json'
    path = os.getcwd() + '\\clients\\' + client + '\\route_info\\' + reference + '\\' + r_ref
    # path = os.getcwd() + '\\clients\\' + client + '\\route_info\\' + r_ref
    with open(path, 'r') as f:
        sol_info = json.load(f)
    if p_type == 's':
        return sol_info, path
    else:
        return sol_info, r_ref

def parse_array(client, arraytype):
    val = parse_list(client, arraytype)
    return np.array(val, dtype=np.float64)

def parse_list(client, listtype):
    with open(os.getcwd() + '\\clients\\' + client + '\\' + listtype + '.json', 'r') as f:
        val = json.load(f)
    return val

def parse_addresses(client):
    with open(os.getcwd() + '\\clients\\' + client + '\\customers.json', 'r') as f:
        cust = json.load(f)
    customers = cust['addresses']
    omissions = cust['duds']
    working = cust['working']
    return customers, omissions, working

def getdump(path):
    with open(path + '\\infodump.json') as f:
        info = json.load(f)
    return info

def nonesum(iterable):
    val = sum([x for x in iterable if x != None])
    return val

def cost_def(labor, fuel):
    def cost_func(time_vec, fuel_vec):
        labor_cost = sum([labor[i]*time_vec[i] for i in range(0, len(labor)) if time_vec[i] != None])
        fuel_cost = sum([fuel[i]*fuel_vec[i] for i in range(0, len(fuel)) if fuel_vec[i] != None])
        return labor_cost + fuel_cost
    return cost_func

def indep_cost_def(labor, fuel):
    def cost_func(time_vec, fuel_vec):
        labor_cost = [labor[i]*time_vec[i] if time_vec[i] != None else None for i in range(0, len(labor))]
        fuel_cost = [fuel[i]*fuel_vec[i] if fuel_vec[i] != None else None for i in range(0, len(fuel))]
        return [labor_cost[i] + fuel_cost[i] if labor_cost[i] != None else None for i in range(0, len(labor_cost))]
    return cost_func

def get_settings(client, preset=None):
    if preset == None:
        sett = input('which settings would you like to use?: ')
    else:
        sett = preset
    try:
        path = os.getcwd() + '\\clients\\' + client + '\\route_info\\route_settings\\' + sett + '.json'
        with open(path, 'r') as f:
            settings = json.load(f)
    except FileNotFoundError:
        print(f'"{sett}" settings file does not exist')
        input('utilizing default settings')
        sett = 'default'
        path = os.getcwd() + '\\clients\\' + client + '\\route_info\\route_settings\\default.json'
        with open(path, 'r') as f:
            settings = json.load(f)
    return settings