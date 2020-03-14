import numpy as np
import json
import os
import re
import textwrap
from route_settings import default as def_settings
from maps_api import parse_addresses, parse_array, parse_list

def make_dest():
    done = False
    add_list = set()
    print('input "done" at any time to conclude input')
    print('any input errors may be corrected after finishing the list')
    while not done:
        loc = input('add a destination: ')
        if loc == 'done':
            done = True
            continue
        add_list.add(loc)
        print(f'added {loc}')
    cease = False
    while not cease:
        addd = False
        subbb = False
        input('please review the destination list [press enter]')
        for dest in add_list:
            print(dest)
        additions = input('does anything need to be added?[y/n]: ')
        if additions.lower() in ['y', 'ye', 'yes', 'yeah']:
            addmore = True
            addd = True
            while addmore:
                loc = input('add a destination: ')
                add_list.add(loc)
                print(f'added {loc}')
                cont = input('add another?[y/n]: ')
                if cont.lower() not in ['y', 'ye', 'yes', 'yeah']:
                    addmore = False
        subtractions = input('does anything need to be removed?[y/n]: ')
        if subtractions.lower() in ['y', 'ye', 'yes', 'yeah']:
            submore = True
            subbb = True
            while submore:
                loc = input('remove a destination: ')
                add_list.remove(loc)
                print(f'removed {loc}')
                cont = input('remove another?[y/n]: ')
                if cont.lower() not in ['y', 'ye', 'yes', 'yeah']:
                    addmore = False
        if not addd and not subbb:
            cease = True
    return list(add_list)
    
def revise_working(client):
    addresses, omitted, working = parse_addresses(client)
    work = set(working)
    correct = False
    print('{:<25}    {:<25}'.format('addresses', 'working list'))
    for i in range(0, len(addresses)):
        if addresses[i] in work:
            out = '{:<25} ::   ✔'.format(textwrap.shorten(addresses[i], 22, placeholder='...'))
        elif addresses[i] not in work:
            out = '{:<25} ::    '.format(textwrap.shorten(addresses[i], 22, placeholder='...'))
        print(out)
    while not correct:
        nix = True
        while nix:
            drop = input('remove from the working list?[y/n]: ')
            if drop.lower() in ['y', 'yes', 'yeah', 'ye']:
                removal = input('input the address/re to remove: ')
                if removal == 'all':
                    work = set([addresses[0]])
                else:
                    matcher = re.compile(removal)
                    removal_list = []
                    for element in work:
                        if element == addresses[0]:
                            pass
                        elif matcher.search(element) != None:
                            removal_list.append(element)
                    for drop in removal_list:
                        work.remove(drop)
                        print(f'removed {drop}')
            else:
                nix = False
            print(' ')
        pile = True
        while pile:
            add = input('add to the working list?[y/n]: ')
            if add.lower() in ['y', 'yes', 'yeah', 'ye']:
                addition = input('input the address/re to add: ')
                if addition == 'all':
                    work = set(addresses)
                else:
                    matcher = re.compile(addition)
                    addition_list = []
                    for element in addresses:
                        if matcher.search(element) != None:
                            addition_list.append(element)
                    for stuff in addition_list:
                        work.add(stuff)
                        print(f'added {stuff}')
            else:
                pile = False
            print(' ')
        print('{:<25}    {:<25}'.format('addresses', 'working list'))
        print('-----------------------------------------')
        for i in range(0, len(addresses)):
            if addresses[i] in work:
                out = '{:<25} ::   ✔'.format(textwrap.shorten(addresses[i], 22, placeholder='...'))
            elif addresses[i] not in work:
                out = '{:<25} ::    '.format(textwrap.shorten(addresses[i], 22, placeholder='...'))
            print(out)
        print(' ')
        affirm = input('are these changes correct?[y/n]: ')
        if affirm.lower() in ['y', 'yes', 'yeah', 'ye']:
            correct = True
        print(' ')
    return addresses, omitted, list(work)

def get_working_map(client):
    """Reduces the information matrices to reflect the working set.
    
    Filters the entries of the distance and time matrices to omit
    unnecessary addresses. Also returns a reversible map to the
    original list. 

    May later be used for other filterable information, such as
    weather or predictive models.

    Params
    ------
    client :: str
        The current client
    
    Returns
    -------
    shrunk_dist :: numpy.array
        A smaller distance matrix, reflecting only the working set
    shrunk_dur :: numpy.array
        A smaller time matrix, reflecting only the working set
    backmap :: []
        A map between the reduced set and original
    """

    distance = parse_array(client, 'distance')
    duration = parse_array(client, 'time')
    addresses, omitted, working = parse_addresses(client)
    backmap = []
    for i in range(0, len(addresses)):
        if addresses[i] in working:
            backmap.append(i)
    # backmap maps the ith address of the reduced list to the
    # backmap[i]th address of the real list.
    dist_split = np.split(distance, len(addresses))
    dur_split = np.split(duration, len(addresses))
    keeper = []
    copper = []
    for i in backmap:
        keeper.append(dist_split[i])
        copper.append(dur_split[i])
    shrunk_dist = np.vstack(tuple(keeper))
    shrunk_dur = np.vstack(tuple(copper))
    dist_split = np.split(shrunk_dist, len(addresses), axis=1)
    dur_split = np.split(shrunk_dur, len(addresses), axis=1)
    keeper = []
    copper = []
    for i in backmap:
        keeper.append(dist_split[i])
        copper.append(dur_split[i])
    shrunk_dist = np.hstack(tuple(keeper))
    shrunk_dur = np.hstack(tuple(copper))
    return shrunk_dist, shrunk_dur, backmap, addresses

def set_info(client):
    part_path = os.getcwd() + '\\clients\\' + client + '\\customer_info'
    greased = False
    filelist = os.listdir(part_path)
    print('input "list" at any time to see the customer list')
    while not greased:
        cust_to_edit = input('which customer would you like to edit?: ')
        if cust_to_edit == 'list':
            for f in filelist:
                print(f)
            print(' ')
        elif cust_to_edit == 'all':
            print('ITERATING OVER ALL CUSTOMERS')
            print('----------------------------')
            for f in filelist:
                n_path = part_path + '\\' + f
                edit_info(n_path, f)
            print(' ')
        elif cust_to_edit in filelist:
            n_path = part_path + '\\' + cust_to_edit
            edit_info(n_path, cust_to_edit)
        else:
            print('that customer is not in the database')
        cont = input('continue to edit?[y/n]: ')
        if cont.lower() not in ['y', 'yes', 'yeah', 'ye']:
            greased = True

def edit_info(path, name):
    with open(path, 'r') as cust:
        preview = json.load(cust)
    print(f'-- {name} --')
    for key, value in preview.items():
        if isinstance(value, list):
            tempval = str(value)
        else:
            tempval = value
        print('{:<10} : {:<30}'.format(key, tempval))
    print(' ')
    edit = input('edit these values?[y/n]: ')
    if edit.lower() in ['y', 'yes', 'ye', 'yeah']:
        go = True
        while go:
            val2edit = input('input the key you wish to edit: ')
            if val2edit in preview.keys():
                changeto = input('input the desired value: ')
                try:
                    preview[val2edit] = float(changeto)
                except ValueError:
                    preview[val2edit] = changeto
            else:
                print('that is not a valid key')
            cont = input('edit another value?[y/n]: ')
            if cont.lower() not in ['y', 'yes', 'ye', 'yeah']:
                go = False
    preview['preset'] = True
    with open(path, 'w') as cust:
        json.dump(preview, cust)
    print(' ')
    print(' ')
    
def retrace(routes, backmap, addresses):
    rerouted = []
    renamed = []
    for i in range(0, len(routes)):
        rerouted.append([])
        renamed.append([])
        retracer = 0
        gotracer = routes[i][retracer]
        while gotracer != 0:
            rerouted[i].append(backmap[retracer])
            renamed[i].append(addresses[backmap[retracer]])
            retracer = gotracer
            gotracer = routes[i][gotracer]
        rerouted[i].append(0)
        renamed[i].append(addresses[0])
    return rerouted, renamed

def manual_retrace(client):
    customers, omissions, working = parse_addresses(client)
    routes = []
    names = []
    print('customer list')
    print('-------------')
    for i in customers:
        print(i)
    print(' ')
    nroute = int(input('input the number of routes: '))
    for i in range(0, nroute):
        spec_route = []
        spec_names = []
        while True:
            location, location_index = locgrab(customers)
            spec_route.append(location_index)
            spec_names.append(location)
            if len(spec_route) > 1 and location == spec_names[0]:
                print(f'circuit {i} complete.')
                print(' ')
                break
        routes.append(spec_route)
        names.append(spec_names)
    return routes, names

def locgrab(customers):
    while True:
        try:
            loc = input('input a location')
            expr = re.compile(loc)
            filtered = list(filter(expr.match, customers))
            if len(filtered) == 1:
                truloc = filtered[0]
                truloc_index = customers.index(truloc)
            else:
                raise ValueError
        except ValueError:
            print('that input was not sufficient')
            continue
        break
    return truloc, truloc_index

def manual_cost_trace(client, routes):
    distance = parse_array(client, 'distance')
    duration = parse_array(client, 'time')
    customers, omitted, working = parse_addresses(client)
    add_vec = []
    fuel_vec = []
    xpoints = []
    ypoints = []
    for i in customers:
        with open(os.getcwd()+'\\clients\\'+client+'\\customer_info\\'+i+'.json', 'r') as f:
            custinfo = json.load(f)
        add_vec.append(custinfo['proj_time'])
        fuel_vec.append(custinfo['proj_fuel'])
        ypoints.append(custinfo['lat'])
        xpoints.append(custinfo['lon'])
    add_vec = np.array(add_vec)
    points = Setup(duration, distance, add_vec, fuel_vec, xpoints, ypoints)
    t_cost = [0] * len(routes)
    f_cost = [0] * len(routes)
    poly = []
    for i in range(0, len(routes)):
        init_app = np.array([points.xpoints[routes[i][0]], points.ypoints[routes[i][0]]])
        for j in range(0, len(routes[i])-1):
            try:
                t_cost[i] += points.d_matrix[routes[i][j]][routes[i][j+1]]
                f_cost[i] += points.c_matrix[routes[i][j]][routes[i][j+1]]
                xy_app = np.array([points.xpoints[routes[i][j+1]], points.ypoints[routes[i][j+1]]])
            except IndexError:
                input('somethin dun goofed')
            init_app = np.vstack((init_app, xy_app))
        try:
            poly = np.vstack((poly, init_app))
        except ValueError:
            poly = init_app
    return t_cost, f_cost, poly

        
class Setup:
    def __init__(self, dur, dist, tcost, dcost, x, y):
        self.d_matrix = dur
        self.c_matrix = np.divide(dist, def_settings['fuel_econ'])
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

