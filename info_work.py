import numpy as np
import json
import os
import textwrap
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
    for i in working:
        print(i)
    while not correct:
        nix = True
        while nix:
            drop = input('remove an address from the working list?[y/n]: ')
            if drop.lower() in ['y', 'yes', 'yeah', 'ye']:
                removal = input('input the address to remove: ')
                if removal == addresses[0]:
                    print('you cannot remove the depot')
                elif removal in work:
                    work.remove(removal)
                else:
                    print('that is not a current working address')
            else:
                nix = False
            print(' ')
        pile = True
        while pile:
            add = input('add an address to the working list?[y/n]: ')
            if add.lower() in ['y', 'yes', 'yeah', 'ye']:
                addition = input('input the address to add: ')
                if addition in addresses:
                    work.add(addition)
                else:
                    print('that is not a known address')
            else:
                pile = False
            print(' ')
        for i in range(0, len(set(working) | set(work))):
            try:
                if working[i] in work:
                    out = '{:<20} -----> {:<20}'.format(textwrap.shorten(addresses[i], 17, placeholder='...'), textwrap.shorten(addresses[i], 17, placeholder='...'))
                elif working[i] not in work:
                    out = '{:<20} -----> '.format(textwrap.shorten(working[i], 17, placeholder='...'))
            except IndexError:
                for j in work:
                    if j not in working:
                        out = '                     -----> {:<20}'.format(textwrap.shorten(j, 17, placeholder='...'))
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
    


