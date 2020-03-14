import argparse
import os
import json
import textwrap
from info_work import modify_info
from example_solve import solve#, naive_addition
from visualizers import display_prompt

parser = argparse.ArgumentParser(description='operate with the VRP toolset')

cur_client = None
print('enter "ops" at any time to see the list of options')

while True:
    print('Which operation would you like to perform?')
    choice = input(': ')
    choice = choice.lower()
    if choice == 'ops':
        print('[ops]     - see this list of options')
        print('[cclient] - change the current client, or add a new one')
        print('[edit]    - change information regarding the current client')
        print('[weather] - forcibly update stored weather information')
        print('[visual]  - view visualizations, history, etc.')
        print('[solve]   - search for a solution')
        print('[manage]  - manage saved routes and route seeds')
        print('[exit]    - exit program')
        print(' ')
        continue

    if cur_client == None and choice not in ['cclient', 'exit']:
        print('please select a client before performing any operations')
        continue
        
    if choice == 'cclient':
        client_list = os.listdir(os.getcwd() + '\\clients')
        cur_client = input('input client to switch to: ')
        if cur_client not in client_list:
            print('that client does not exist')
            new = input('would you like to instantiate this as a new client?[y/n]: ')
            if new.lower() in ['ye', 'yeah', 'yes', 'y']:
                cname = cur_client
                os.mkdir(os.getcwd() + '\\clients\\' + cname)
                os.mkdir(os.getcwd() + '\\clients\\' + cname + '\\customer_info')
                os.mkdir(os.getcwd() + '\\clients\\' + cname + '\\weather_info')
                os.mkdir(os.getcwd() + '\\clients\\' + cname + '\\route_info')
                os.mkdir(os.getcwd() + '\\clients\\' + cname + '\\route_info' + '\\solution_dumps')
                os.mkdir(os.getcwd() + '\\clients\\' + cname + '\\route_info' + '\\routes')
                os.mkdir(os.getcwd() + '\\clients\\' + cname + '\\route_info' + '\\holding_routes')
        print(' ')

    elif choice == 'edit':
        modify_info(cur_client)
        print('-----------------------------------------------------------')
        print(' ')

    elif choice == 'visual':
        display_prompt(cur_client)
        print('-----------------------------------------------------------')
        print(' ')

    elif choice == 'weather':
        pass

    elif choice == 'solve':
        solve(cur_client)
        # naive_addition(cur_client)

    elif choice == 'manage':
        pass

    elif choice == 'exit':
        break

    else:
        print('that was not a recognizable option')
        print(' ')
        continue

    

