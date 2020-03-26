import numpy as np
import json
import os
import re
import textwrap
import time
from useful_funcs import route_grab, parse_addresses, parse_array, parse_list, Setup, npencode, nonesum, get_settings, indep_cost_def
from visualizers import disp_trace
from route_settings import default as def_settings
from maps_api import fetch_instantiate, fetch_new, instantiate_data, new_data, set_depot

def modify_info(client):
    while True:
        print('-----------------------------------------------------------')
        print('[n]ewset  - instantiate a new customer database')
        print('[a]ddset  - add a customer to the existing database')
        print('[d]epot   - fix the depot')
        print('[s]etinfo - set necessary information for the customer list')
        print('[w]ork    - revise the working customer list')
        print('[e]xit    - return to operations menu')
        print(' ')
        print('what operation would you like to perform?')
        choice = input(': ')
        choice = choice.lower()
        if 'newset'.startswith(choice):
            destinations = make_dest()
            input('please review the destination list one final time [press enter]')
            for loc in destinations:
                print(loc)
            affirm = input('is this correct?[y/n]: ')
            go = False
            if affirm.lower() in ['y', 'ye', 'yes', 'yeah']:
                affirm2 = input('proceed to fetch information?[y/n]: ')
                if affirm2 in ['y', 'yes', 'ye', 'yeah']:
                    go = True
                    fetch_instantiate(client, destinations)
                    instantiate_data(client, destinations)
            if go:
                print('results fetched')
            else:
                print('results not fetched')

        elif 'addset'.startswith(choice):
            new_cust = input('input a new customer: ')
            print(new_cust)
            affirm = input('is this correct?[y/n]: ')
            go = False
            if affirm.lower() in ['y', 'ye', 'yes', 'yeah']:
                affirm2 = input('proceed to fetch information?[y/n]: ')
                if affirm2 in ['y', 'yes', 'ye', 'yeah']:
                    go = True
                    fetch_new(client, new_cust)
                    new_data(client, new_cust)
            if go:
                print('results fetched')
            else:
                print('results not fetched')

        elif 'depot'.startswith(choice):
            set_depot(client)

        elif 'setinfo'.startswith(choice):
            set_info(client)
        
        elif 'work'.startswith(choice):
            addresses, omitted, working = revise_working(client)
            go = False
            affirm2 = input('proceed to modify working list?[y/n]: ')
            if affirm2 in ['y', 'yes', 'ye', 'yeah']:
                go = True
                addr = {
                    'addresses' : addresses,
                    'duds' : omitted,
                    'working' : working
                }
                with open(os.getcwd() + '\\clients\\' + client + '\\customers.json', 'w') as f:
                    json.dump(addr, f)
            if go:
                print('working list modified')
            else:
                print('working list not modified')
        
        elif 'exit'.startswith(choice):
            print('returning to operations menu')
            print(' ')
            break
            
        else:
            print('that was not a recognized option')
        print(' ')

def manage_routes(client):
    while True:
        print('-----------------------------------------------------------')
        print('[s]et         - set an official route')
        print('[t]race       - save a trace from a solution or from scratch')
        print('[i]nfo        - view information from a trace')
        print('[c]ompare     - compare two traces')
        print('[e]xit        - return to the operations menu')
        print(' ')
        print('what would you like to manage?')
        choice = input(': ')
        choice = choice.lower()
        if 'exit'.startswith(choice):
            print('returning to operations menu')
            print(' ')
            break
        
        elif 'set'.startswith(choice):
            print('not yet implemented')

        elif 'trace'.startswith(choice):
            retrace(client)

        elif 'info'.startswith(choice):
            trace_info(client)

        elif 'compare'.startswith(choice):
            trace_compare(client)

        else:
            print('that choice was not recognized')
        print(' ')

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
                    matcher = re.compile(removal, flags=re.I)
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
                    matcher = re.compile(addition, flags=re.I)
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

def solve_pretrace(client):
    sol_info, sol_path = route_grab(client)
    print('would you like the feasible or infeasible solution?')
    while True:
        feas = input(': ')
        feas = feas.lower()
        if feas in ['feasible', 'infeasible']:
            break
        else:
            print('that was not valid input')
    p = 'best ' + feas
    poly = sol_info[p]['poly'][0]
    timestamp = sol_info['timestamp']
    f_cost = sol_info[p]['fuel']
    t_cost = sol_info[p]['time']
    trace_r, trace_n = solve_retrace(sol_info[p]['sol'], sol_info['map'], sol_info['address list'])
    final_trace = {
        'timestamp' : timestamp,
        'source' : sol_path,
        'settings_used' : sol_info['solve parameters']['settings'],
        'poly' : poly,
        'fuel' : f_cost,
        'time' : t_cost,
        'route_nums' : trace_r,
        'route_names' : trace_n
    }
    print('traced!')
    print(' ')
    return final_trace

def manual_pretrace(client):
    trace_r, trace_n = manual_retrace(client)
    t_cost, f_cost, poly, set_name = manual_cost_trace(client, trace_r)
    t = time.localtime()
    timestamp = str(t.tm_mon) + '/' + str(t.tm_mday) + '/' + str(t.tm_year) + ' @ ' + str(t.tm_hour) + ':' + str(t.tm_min)
    final_trace = {
        'timestamp' : timestamp,
        'settings_used' : set_name,
        'source' : 'manual',
        'poly' : poly,
        'fuel' : f_cost,
        'time' : t_cost,
        'route_nums' : trace_r,
        'route_names' : trace_n
    }
    print('traced!')
    print(' ')
    return final_trace

def solve_retrace(routes, backmap, addresses):
    rerouted = []
    renamed = []
    for i in range(0, len(routes)):
        rerouted.append([])
        renamed.append([])
        if routes[i][0] == None:
            continue
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
            if location == None and spec_route == []:
                print('circuit added as empty route')
                break
            elif location == None and spec_route != []:
                raise ValueError('an empty location does not exist')
            else:
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
            loc = input('input a location: ')
            expr = re.compile(loc, flags=re.I)
            filtered = list(filter(expr.search, customers))
            if len(filtered) == 1:
                truloc = filtered[0]
                truloc_index = customers.index(truloc)
            elif len(filtered) == 0 and loc == '':
                truloc = None
                truloc_index = None
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
    settings, name = get_settings(client)
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
    points = Setup(duration, distance, add_vec, fuel_vec, xpoints, ypoints, settings)
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
            init_app = np.vstack((init_app, xy_app)) # I have no idea why I have to do this
        try:
            poly = np.vstack((poly, init_app))
        except ValueError:
            poly = init_app
    return t_cost, f_cost, poly, name

def retrace(client):
    while True:
        print('-----------------------------------------------------------')
        print('[s]olution     - trace from solution')
        print('[m]anual       - trace manually')
        print('[e]xit         - return to the operations menu')
        print(' ')
        print('select an option from above')
        choice = input(': ')
        choice = choice.lower()
        if 'solution'.startswith(choice):
            trace = solve_pretrace(client)
            save = input('would you like to save this trace?[y/n]: ')
            if save.lower() in ['y', 'yes', 'yeah', 'ye']:
                store_trace(client, trace)
        elif 'manual'.startswith(choice):
            trace = manual_pretrace(client)
            save = input('would you like to save this trace?[y/n]: ')
            if save.lower() in ['y', 'yes', 'yeah', 'ye']:
                store_trace(client, trace)
        elif 'exit'.startswith(choice):
            print('returning to operations menu')
            print(' ')
            break
        else:
            print('that option was not recognized')
        print(' ')

def store_trace(client, trace):
    path = os.getcwd() + '\\clients\\' + client + '\\route_info\\holding_routes\\'
    name = input('name this trace: ') + '.json'
    with open(path+name, 'w') as f:
        json.dump(trace, f, cls=npencode)
    print('saved!')
    print(' ')

def trace_info(client):
    path = os.getcwd() + '\\clients\\' + client + '\\route_info\\holding_routes\\'
    race = input('which trace?: ')
    trace = race + '.json'
    with open(path+trace, 'r') as f:
        info = json.load(f)
    ts = info['timestamp']
    sorce = info['source']
    print(f'timestamp : {ts}')
    print(f'source    : {sorce}')
    print('-----------------------------------------------------------')
    while True:
        print('options')
        print('-------')
        print('[p]oly          - view the route polygon')
        print('[f]uel          - view fuel costs (in liters)')
        print('[t]ime          - view time costs (in seconds)')
        print('[c]ost          - view an estimated monetary cost')
        print('[r]outes        - view the routes (sequential addresses)')
        print('[e]xit          - exit this menu')
        print(' ')
        print('choose a value to view')
        choice = input(': ')
        choice = choice.lower()
        if 'exit'.startswith(choice):
            print('exiting menu')
            print(' ')
            break
        elif 'fuel'.startswith(choice):
            for i in range(0, len(info['fuel'])):
                fuel = info['fuel'][i]
                if fuel != None:
                    print(f'route {i}: {fuel} liters')
            input(':')
        elif 'time'.startswith(choice):
            for i in range(0, len(info['time'])):
                tim = info['time'][i]
                if tim != None:
                    print(f'route {i}: {tim} seconds')
            input(':')
        elif 'routes'.startswith(choice):
            for i in range(0, len(info['route_names'])):
                if info['route_names'][i] != []:
                    print(f'route {i}')
                    print('----------')
                    for j in info['route_names'][i]:
                        print(j)
                    print(' ')
            input(':')
        elif 'cost'.startswith(choice):
            recset = input('use recommended settings?[y/n]: ')
            if recset.lower() in ['y', 'yes', 'yeah', 'ye']:
                settings = get_settings(client, preset=info['settings_used'])
            else:
                settings = get_settings(client)
            cost_func = indep_cost_def(settings['cost_params']['labor'], settings['cost_params']['fuel'])
            costs = cost_func(info['time'], info['fuel'])
            for i in range(0, len(costs)):
                cost = round(costs[i], 3)
                if fuel != None:
                    print(f'route {i}: ${cost}')
            input(':')
        elif 'polygon'.startswith(choice):
            disp_trace(client, [race], [info['poly']])
        print(' ')

def trace_compare(client):
    path = os.getcwd() + '\\clients\\' + client + '\\route_info\\holding_routes\\'
    race1 = input('input trace 1: ')
    race2 = input('input trace 2: ')
    trace1 = race1 + '.json'
    trace2 = race2 + '.json'
    with open(path+trace1, 'r') as f:
        first = json.load(f)
    with open(path+trace2, 'r') as f:
        second = json.load(f)
    while True:
        print('options')
        print('-------')
        print('[p]oly          - overlay polygons')
        print('[f]uel          - compare fuel costs (in liters)')
        print('[t]ime          - compare time costs (in seconds)')
        print('[c]ost          - compare total projected costs')
        print('[e]xit          - exit this menu')
        print(' ')
        print('choose a value to view')
        choice = input(': ')
        choice = choice.lower()
        if 'exit'.startswith(choice):
            print('exiting menu')
            print(' ')
            break
        elif 'fuel'.startswith(choice):
            ordered1 = sorted(first['fuel'], key=lambda x: (x is None, x))
            ordered2 = sorted(second['fuel'], key=lambda x: (x is None, x))
            comp_print(ordered1, ordered2)
        elif 'time'.startswith(choice):
            ordered1 = sorted(first['time'], key=lambda x: (x is None, x))
            ordered2 = sorted(second['time'], key=lambda x: (x is None, x))
            comp_print(ordered1, ordered2)
        elif 'cost'.startswith(choice):
            recset = input('use recommended settings?[y/n]: ')
            if recset.lower() in ['y', 'yes', 'yeah', 'ye']:
                settings1 = get_settings(client, preset=first['settings_used'])
                settings2 = get_settings(client, preset=second['settings_used'])
            else:
                print('route 1')
                print('-------')
                settings1 = get_settings(client)
                print('route 2')
                print('-------')
                settings2 = get_settings(client)
            cost_func1 = indep_cost_def(settings1['cost_params']['labor'], settings1['cost_params']['fuel'])
            cost_func2 = indep_cost_def(settings2['cost_params']['labor'], settings2['cost_params']['fuel'])
            costs1 = cost_func1(first['time'], first['fuel'])
            costs2 = cost_func2(second['time'], second['fuel'])
            comp_print(costs1, costs2)
        elif 'polygon'.startswith(choice):
            disp_trace(client, [race1, race2], [first['poly'], second['poly']])
        else:
            print('invalid selection')
        print(' ')

def comp_print(el_1, el_2):
    size = max(len(el_1), len(el_2))
    print('in independent ascending order:')
    print(r'route# | trace 1 cost | trace 2 cost |  abs.  diff  | % diff ')
    print('---------------------------------------------------------------')
    for i in range(0, size):
        try:
            out = '{:<7}|{:>14.5f}|{:>14.5f}|{:> 14.5f}|{:> 9.4f}%'.format(i, el_1[i], el_2[i], abs(el_1[i] - el_2[i]), 100*(1 - el_1[i]/el_2[i]))
        except (IndexError, TypeError):
            try:
                out = '{:<7}|{:>14.5f}|{:>14}|{:>14}|{:>10}'.format(i, el_1[i], 'NA', 'NA', 'NA')
            except(IndexError, TypeError):
                try:
                    out = '{:<7}|{:>14}|{:>14.5f}|{:>14}|{:>10}'.format(i, 'NA', el_2[i], 'NA', 'NA')
                except(IndexError, TypeError):
                    continue
        print(out)
    print('_______________________________________________________________')
    out = 'totals |{:>14f}|{:>14f}|{:> 14.5f}|{:> 9.4f}%'.format(nonesum(el_1), nonesum(el_2), abs(nonesum(el_1) - nonesum(el_2)), 100*(1 - nonesum(el_1)/nonesum(el_2)))
    print(out)
    print('---------------------------------------------------------------')
    input(':')

