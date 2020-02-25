import googlemaps
from safekeeping import dist as key
import os
import json
import numpy as np


def full_instantiate(cur_client, customer_list):
    fetch_instantiate(cur_client, customer_list)
    instantiate_data(cur_client, customer_list)

def fetch_instantiate(cur_client, customer_list):
    path = os.getcwd() + '\\clients\\' + cur_client
    gmap = googlemaps.Client(key=key)
    origins = customer_list
    destinations = customer_list
    dmat = gmap.distance_matrix(origins, destinations, units='metric')
    ###################
    print(type(dmat))
#########################
    with open(path + '\\infodump.json', 'w') as f:
        json.dump(dmat, f)

def instantiate_data(cur_client, customer_list):
    path = os.getcwd() + '\\clients\\' + cur_client
    result = getdump(path)
    addresses = result['destination_addresses']
    omitted = []
    for index in range(0, len(addresses)):
        if addresses[index] == '':
            print(f'location "{customer_list[index]}" could not be located')
            print(f'location "{customer_list[index]}" will not be included in the data')
            omitted.append(customer_list[index])
    convert_time = []
    convert_dist = []
    loc_index = 0
    for loc in addresses:
        if loc == '':
            continue
        convert_time.append([])
        convert_dist.append([])
        for dest in result['rows'][loc_index]['elements']:
            if dest['status'] == 'OK':
                convert_time[loc_index].append(dest['duration']['value'])
                convert_dist[loc_index].append(dest['distance']['value'])
        loc_index += 1
    nadresses = [x for x in addresses if x != '']
    addr = {
        'addresses' : nadresses,
        'duds' : omitted, 
        'working' : nadresses
    }
    pathapp = ['\\time.json', '\\distance.json', '\\customers.json']
    contents = [convert_time, convert_dist, addr]
    for i in range(0, 3):
        jdump(path+pathapp[i], contents[i])

def fetch_new(cur_client, customer):
    path = os.getcwd() + '\\clients\\' + cur_client
    addresses, omitted, working = parse_addresses(cur_client)
    gmap = googlemaps.Client(key=key)
    origin = customer
    destinations = addresses
    origins = addresses
    destination = customer
    frommat = gmap.distance_matrix(origin, destinations, units='metric')
    tomat = gmap.distance_matrix(origins, destination, units='metric')
    with open(path + '\\infodump_horz.json', 'w') as f:
        json.dump(frommat, f)
    with open(path + '\\infodump_vert.json', 'w') as f:
        json.dump(tomat, f)

def new_data(cur_client, customer):
    path = os.getcwd() + '\\clients\\' + cur_client
    addresses, omitted, working = parse_addresses(cur_client)
    with open(path + '\\infodump_vert.json', 'r') as f:
        vertical = json.load(f)
    if vertical['destination_addresses'][0] != '':
        with open(path + '\\infodump_horz.json', 'r') as f:
            horizontal = json.load(f)
        distance = parse_list(cur_client, 'distance')
        duration = parse_list(cur_client, 'time')
        addresses.append(vertical['destination_addresses'][0])
        horz_list_dur = []
        horz_list_dist = []
        for dest in horizontal['rows'][0]['elements']:
            horz_list_dur.append(dest['duration']['value'])
            horz_list_dist.append(dest['distance']['value'])
        horz_list_dist.append(0)
        horz_list_dur.append(0)
        for i in range(0, len(distance)):
            distance[i].append(vertical['rows'][i]['elements'][0]['distance']['value'])
            duration[i].append(vertical['rows'][i]['elements'][0]['duration']['value'])
        distance.append(horz_list_dist)
        duration.append(horz_list_dur)
        addr = {
            'addresses' : addresses,
            'duds' : omitted,
            'working' : addresses
        }
        pathapp = ['\\time.json', '\\distance.json', '\\customers.json']
        contents = [duration, distance, addr]
        for i in range(0, 3):
            jdump(path+pathapp[i], contents[i])
    else:
        print('that address is a dud.')

def parse_array(client, arraytype):
    val = parse_list(client, arraytype)
    return np.array(val)

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

def set_depot(client):
    distance = parse_array(client, 'distance')
    duration = parse_array(client, 'time')
    customers, omissions, working = parse_addresses(client)
    good = False
    print('input "list" to see a list of available addresses')
    while not good:
        depot = input('which address would you like to set as the depot?: ')
        if depot == 'list':
            for i in working:
                print(i)
            print(' ')
            continue
        elif depot not in working:
            print('that address is not within the working list')
            print(' ')
            continue
        elif depot in working:
            good = True
            index = customers.index(depot)
            new_depot = [customers.pop(index)]
            customers = new_depot + customers
            #horizontal splitting
            dist_split = np.hsplit(distance, [index, index+1])
            distance = np.hstack((dist_split[1], dist_split[0], dist_split[2]))
            time_split = np.hsplit(duration, [index, index+1])
            duration = np.hstack((time_split[1], time_split[0], time_split[2]))
            #vertical splitting
            dist_split = np.vsplit(distance, [index, index+1])
            distance = np.vstack((dist_split[1], dist_split[0], dist_split[2]))
            time_split = np.vsplit(duration, [index, index+1])
            duration = np.vstack((time_split[1], time_split[0], time_split[2]))
            #
            path = os.getcwd() + '\\clients\\' + client
            addr = {
                'addresses' : customers,
                'duds' : omissions,
                'working' : working
            }
            pathapp = ['\\time.json', '\\distance.json', '\\customers.json']
            contents = [duration.tolist(), distance.tolist(), addr]
            for i in range(0, 3):
                jdump(path+pathapp[i], contents[i])
        else:
            print('something went wrong')

def jdump(path, contents):
    with open(path, 'w') as f:
        json.dump(contents, f)


    
