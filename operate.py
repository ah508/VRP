import argparse
import os
import json
import textwrap
from info_work import make_dest, revise_working, get_working_map
from maps_api import fetch_instantiate, fetch_new, new_data, instantiate_data, parse_addresses, set_depot
from example_solve import solve

parser = argparse.ArgumentParser(description='operate with the VRP toolset')

cur_client = None
print('enter "ops" at any time to see the list of options')

escape = False
while not escape:
    print('Which operation would you like to perform?')
    choice = input(': ')
    choice = choice.lower()
    if choice == 'ops':
        print('[ops]     - see this list of options')
        print('[nclient] - add a new client to the list')
        print('[cclient] - change the current client')
        print('[newset]  - instantiate a new customer database')
        print('[addset]  - add a customer to the existing database')
        print('[depot]   - fix the depot')
        print('[weather] - forcibly update stored weather information')
        print('[work]    - revise the working customer list')
        print('[solve]   - search for a solution')
        print('[exit]    - exit program')
        print(' ')
        continue

    if cur_client == None and choice not in ['cclient', 'nclient', 'exit']:
        print('please select a client before performing any operations')
        continue

    if choice == 'nclient':
        cname = input('input client name: ')
        try:
            os.mkdir(os.getcwd() + '\\clients\\' + cname)
        except FileExistsError:
            print('client already exists')
            continue
        ##############ADD GENERAL NECESSARY FILE STUFF#################

    elif choice == 'cclient':
        cur_client = input('input client to switch to: ')
        print(' ')

    elif choice == 'newset':
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
                fetch_instantiate(cur_client, destinations)
                instantiate_data(cur_client, destinations)
        if go:
            print('results fetched')
        else:
            print('results not fetched')
        print(' ')

    elif choice == 'addset':
        new_cust = input('input a new customer: ')
        print(new_cust)
        affirm = input('is this correct?[y/n]: ')
        go = False
        if affirm.lower() in ['y', 'ye', 'yes', 'yeah']:
            affirm2 = input('proceed to fetch information?[y/n]: ')
            if affirm2 in ['y', 'yes', 'ye', 'yeah']:
                go = True
                fetch_new(cur_client, new_cust)
                new_data(cur_client, new_cust)
        if go:
            print('results fetched')
        else:
            print('results not fetched')
        print(' ')

    elif choice == 'depot':
        set_depot(cur_client)

    elif choice == 'weather':
        pass

    elif choice == 'work':
        addresses, omitted, working = revise_working(cur_client)
        go = False
        affirm2 = input('proceed to modify working list?[y/n]: ')
        if affirm2 in ['y', 'yes', 'ye', 'yeah']:
            go = True
            addr = {
                'addresses' : addresses,
                'duds' : omitted,
                'working' : working
            }
            with open(os.getcwd() + '\\clients\\' + cur_client + '\\customers.json', 'w') as f:
                json.dump(addr, f)
        if go:
            print('working list modified')
        else:
            print('working list not modified')
        print(' ')

    elif choice == 'solve':
        solve(cur_client)

    elif choice == 'exit':
        escape = True

    else:
        print('that was not a recognizable option')
        continue

    

