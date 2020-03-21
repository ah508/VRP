import argparse
import os
import json
import textwrap
from info_work import modify_info, manage_routes
from example_solve import solve#, naive_addition
from visualizers import display_prompt

parser = argparse.ArgumentParser(description='operate with the VRP toolset')

cur_client = None
print('enter "ops" at any time to see the list of options')

while True:
    print('Which operation would you like to perform?')
    choice = input(': ')
    choice = choice.lower()
    if 'ops'.startswith(choice):
        print('[o]ps     - see this list of options')
        print('[cc]lient - change the current client, or add a new one')
        print('[ed]it    - change information regarding the current client')
        print('[w]eather - forcibly update stored weather information')
        print('[v]isual  - view visualizations, history, etc.')
        print('[s]olve   - search for a solution')
        print('[m]anage  - view, manage, and compare saved routes and route seeds')
        print('[e]xit    - exit program')
        print(' ')
        continue

    if cur_client == None and choice not in ['cclient', 'cc', 'exit']:
        print('please select a client before performing any operations')
        continue
        
    if 'cclient'.startswith(choice):
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
                os.mkdir(os.getcwd() + '\\clients\\' + cname + '\\route_info' + '\\route_settings')
        print(' ')

    elif 'exit'.startswith(choice):
        break

    elif 'edit'.startswith(choice):
        modify_info(cur_client)
        print('-----------------------------------------------------------')
        print(' ')

    elif 'visual'.startswith(choice):
        display_prompt(cur_client)
        print('-----------------------------------------------------------')
        print(' ')

    elif 'weather'.startswith(choice):
        pass

    elif 'solve'.startswith(choice):
        solve(cur_client)
        # naive_addition(cur_client)

    elif 'manage'.startswith(choice):
        manage_routes(cur_client)
        print('-----------------------------------------------------------')
        print(' ')

    else:
        print('that was not a recognizable option')
        print(' ')
        continue

    

