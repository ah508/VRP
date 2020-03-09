#cython: language_level=3
from proc_func2 import GenFunc
import random as r
import numpy as np
import math
import heapq
import time

class SEARCH(GenFunc):
    def __init__(self, points, routes, route_identifiers, max_cap, max_len, q, n_max): #history removed
        super().__init__(points)
        self.time = time.process_time()
        self.gridlock = 0
        # self.history = history
        self.tot_verts = len(points.costvec)
        self.route_list = routes
        self.route_ref = route_identifiers
        self.m = len(set(self.route_ref)-set([None]))
        self.m_hat = len(self.route_list)
        self.cap_const = max_cap
        self.time_const = max_len
        self.f1_star = math.inf
        self.f2_star = math.inf
        self.alpha = 1
        self.beta = 1
        self.check_sol(routes)
        self.W = list(range(1, self.tot_verts))
        self.q = q
        self.p2 = 5
        self.theta_l = 5
        self.theta_u = 10
        self.g = 0.01
        self.h = 10
        self.max_iter = n_max
        self.n_max = n_max
        self.select_tot = [0] * self.tot_verts
        self.cur_iter = 1
        self.update_freq()
        self.delta_max = 0
        self.us_clear = True
        self.cap_ten = set()
        self.dist_ten = set()
        self.tabu = {}
        # {(vertex, route) : tabu_until}
        self.p_neighborhoods = {}

    def search(self):
        self.stream_header()
        while self.cur_iter < self.max_iter:
            self.m = len(set(self.route_ref)-set([None]))
            self.update_neighbors()
            selected_verts = r.sample(self.W, self.q)
            cost_cur_route = self.sol_cost(self.route_list)
            candidate_set = {}
            cand_tag = 0
            empties = self.get_empty(self.route_list)
            for vertex in selected_verts:
                self.set_p1(vertex)
                transfers = self.neighbor_routes(vertex, empties)
                # for ri in transfers:
                    # if vertex in self.route_list[ri]:
                    #     print('MID HIT')
                    #     print(vertex)
                    #     print(transfers)
                    #     print(self.route_ref)
                    #     print(ri)
                    #     for i in self.route_list:
                    #         print(i)
                    #     input(':')
                transfers = transfers - set([self.route_ref[vertex]])
                del_route = self.extract(vertex, self.route_ref[vertex])
                # if vertex in del_route:
                #     print('EARLY HIT')
                #     print(vertex)
                #     print(transfers)
                #     print(self.route_ref)
                #     print(ri)
                #     for i in self.route_list:
                #         print(i)
                #     input(':')
                for route_index in transfers:
                    route_adjust = self.insert(vertex, route_index)
                    move = self.route_list.copy()
                    move[self.route_ref[vertex]] = del_route
                    move[route_index] = route_adjust
                    cost = list(self.sol_cost(move))
                    if (vertex, route_index) in self.tabu.keys():
                        if self.tabu[(vertex, route_index)] < self.cur_iter:
                            del(self.tabu[(vertex, route_index)])
                        elif cost[2] and cost[0] < self.f1_star:
                            pass
                        elif not cost[2] and cost[1] < self.f2_star:
                            pass
                        else:
                            continue
                    if cost[1] < cost_cur_route[1]:
                        f_val = cost[1]
                    else:
                        f_val = cost[1] + self.delta_max*math.sqrt(self.m)*self.g*self.select_freq[vertex]
                    candidate = {
                        'frame' : move,
                        'cost' : f_val,
                        'f1' : cost[0],
                        'f2' : cost[1],
                        'valid' : cost[2],
                        'vertex' : vertex,
                        'route to' : route_index,
                        'route from' : self.route_ref[vertex]
                    }
                    candidate_set[cand_tag] = candidate
                    cand_tag += 1
            min_pair = self.best_candidate(candidate_set)
            try:
                next_move = candidate_set[min_pair[0]]
            except KeyError:
                self.gridlock += 1
                # print('###########################################################################')
                # print('keyerror')
                # print(min_pair)
                # print(candidate_set)
                # input('halt')
                continue
            if self.us_clear:
                if next_move['f2'] > cost_cur_route[1]:
                    if cost_cur_route[2]:
                        post_opt_route = self.post_opt(self.route_list)
                        cost = self.sol_cost(post_opt_route)
                        next_move = {
                            'frame' : post_opt_route,
                            'cost' : None,
                            'f1' : cost[0],
                            'f2' : cost[1],
                            'valid' : cost[2],
                            'vertex' : None,
                            'route_to' : None, 
                            'route_from' : None
                        }
                        self.us_clear = False
            else:
                self.us_clear = True
            self.execute_move(next_move, cost_cur_route[1])

    def update_freq(self):
        self.select_freq = [x/self.cur_iter for x in self.select_tot]

    def set_p1(self, vertex):
        self.p1 = max(len(set(self.route_list[self.route_ref[vertex]])-set([None])), self.p2)

    def get_empty(self, routes):
        potentials = []
        for index, contents in enumerate(routes):
            if set(contents) == set([None]):
                potentials.append(index)
        return potentials

    def execute_move(self, move, prev_f2):
        f1_bump = False
        f2_bump = False
        if move['valid'] and move['f1'] < self.f1_star:
            self.s_star = move['frame']
            self.f1_star = move['f1']
            f1_bump = True
        if move['f2'] < self.f2_star:
            self.sn_star = move['frame']
            self.f2_star = move['f2']
            f2_bump = True
        self.delta_max = max(self.delta_max, abs(move['f2'] - prev_f2))
        self.stream_body(f1_bump, f2_bump, move['f1'], move['f2'], move['valid'])
        try:
            self.select_tot[move['vertex']] += 1
            self.update_freq()
        except TypeError:
            pass
        self.route_list = move['frame']
        if self.us_clear:
            if move['vertex'] == None:
                input('oops')
            self.route_ref[move['vertex']] = move['route to']
            self.tabu[(move['vertex'], move['route from'])] = self.cur_iter + r.randint(self.theta_l, self.theta_u)
        self.check_ten(move['frame'])
        if f1_bump or f2_bump:
            self.max_iter = self.cur_iter + self.n_max
        self.cur_iter += 1
        # self.history.append(move['frame'])

    def check_ten(self, route):
        self.sol_cost(route, fetch=True)
        if self.cur_iter % self.h == 0:
            if self.dist_ten == set([True]):
                self.beta /= 2
            elif self.dist_ten == set([False]):
                self.beta *= 2
            self.dist_ten.clear()
            if self.cap_ten == set([True]):
                self.alpha /= 2
            elif self.cap_ten == set([False]):
                self.alpha *= 2
            self.cap_ten.clear()
        
    def check_sol(self, solution):
        v_cost, iv_cost, valid = self.sol_cost(solution)
        if valid:
            if v_cost < self.f1_star:
                self.s_star = solution
                self.f1_star = v_cost
        if iv_cost < self.f2_star:
            self.sn_star = solution
            self.f2_star = iv_cost

    def neighbor_routes(self, vertex, empties):
        distances = self.dist[vertex].copy()
        # distances[vertex] = math.inf
        nearest = heapq.nsmallest(self.p1, distances)
        neighbors = []
        for i in nearest:
            if i != 0:
                q = np.where(distances==i)[0][0]
                neighbors.append(q)
                distances[q] == math.inf
        banned = self.route_list[self.route_ref[vertex]]
        neighborhood = set(empties.copy())
        for friend in neighbors:
            if friend not in banned:
                neighborhood.add(self.route_ref[friend])
                # neighborhood.append(self.route_ref[friend])
                # banned.append(self.route_ref[friend])
        return neighborhood

    def update_neighbors(self):
        for vertex in range(0, self.tot_verts):
            self.p_neighborhoods[vertex] = {}
            for route in range(0, self.m_hat):
                self.p_neighborhoods[vertex][route] = self.neighbors_on(route, vertex)
                for i in self.p_neighborhoods[vertex][route]:
                    if i not in self.route_list[route]:
                        print('EARLY HIT')
                        print(self.route_list[route])
                        print(self.p_neighborhoods[vertex][route])
                        input('halt')

    def neighbors_on(self, route_num, vertex):
        distances = self.dist[vertex].copy()
        working_circuit = self.route_list[route_num]
        valid = []
        for i in range(0, len(distances)):
            if i != vertex and i in working_circuit:
                valid.append(distances[i])
            else:
                valid.append(math.inf)
        nearest = heapq.nsmallest(self.p2, valid)
        neighbors = []
        for i in nearest:
            if i != math.inf:
                q = valid.index(i)
                neighbors.append(q)
                valid[q] = math.inf
        return neighbors
    
    def valid_cost(self, routes):
        individ_cost = []
        individ_cap = []
        for route in routes:
            individ_cost.append(self.circuit_cost(route))
            individ_cap.append(self.point_cost(route))
        total_cost = sum(individ_cost)
        return total_cost, individ_cost, individ_cap

    def sol_cost(self, routes, fetch=False):
        if fetch:
            v_cost, cost_vector, cap_vector = self.valid_cost(routes)
            d_check = set()
            c_check = set()
            for r_cost in range(0, len(cost_vector)):
                if max(0, cost_vector[r_cost] - self.time_const[r_cost]) > 0: ################################
                    d_check.add(False)
                else:
                    d_check.add(True)
            for c_cost in range(0, len(cap_vector)):
                if max(0, cap_vector[c_cost] - self.cap_const[c_cost]) > 0: ####################################
                    c_check.add(False)
                else:
                    c_check.add(True)
            self.cap_ten.add(min(c_check))
            self.dist_ten.add(min(d_check))
            return None
        v_cost, cost_vector, cap_vector = self.valid_cost(routes)
        valid = False
        cap_over = 0
        time_over = 0
        for r_cost in range(0, len(cost_vector)):
            time_over += max(0, cost_vector[r_cost] - self.time_const[r_cost]) #####################################
        for c_cost in range(0, len(cap_vector)):
            cap_over += max(0, cap_vector[c_cost] - self.cap_const[c_cost]) ######################################
        time_over_tot = self.beta*time_over
        cap_over_tot = self.alpha*cap_over
        iv_cost = v_cost + cap_over_tot + time_over_tot
        if v_cost == iv_cost:
            valid = True
        return v_cost, iv_cost, valid

    def extract(self, vertex, route_index):
        route = self.route_list[route_index]
        n_vert = len(set(route)-set([None]))
        if n_vert == 0:
            raise NotImplementedError('dude that was an invalid selection')
        elif n_vert == 1:
            raise NotImplementedError("dude you can't have one vertex on a route")
        elif n_vert == 2:
            return [None] * self.tot_verts
        elif n_vert == 3:
            newlist = route.copy()
            prev = self.find_predecessor(vertex, newlist)
            succ = self.find_successor(vertex, newlist)
            newlist[prev] = succ
            newlist[vertex] = None
        else:
            newlist = self.nt_extract(vertex, route, route_index)['frame']
        # print(newlist)
        if vertex in newlist:
            print('check?')
            print(vertex)
            # print(transfers)
            print(self.route_ref)
            print(route_index)
            print(newlist)
            for i in self.route_list:
                print(i)
            input(':')
        return newlist

    def nt_extract(self, vi, edgeset, edgeset_index):
        possible_moves = {}
        move_key = 0
        for d_set in [edgeset, self.reverse(edgeset, 0, 0)]:
            vi1 = self.find_successor(vi, d_set)
            vip = self.find_predecessor(vi, d_set)
            vj = self.p_neighborhoods[vi1][edgeset_index]
            for j in vj:
                if j == vi:
                    continue
                if j == vip:
                    continue
                vj1 = self.find_successor(j, d_set)
                try:
                    i1_to_j = self.points_between(d_set, vi1, j)
                except RecursionError:
                    print('i1toj')
                    print(f'j: {j}')
                    print(f'i1: {vi1}')
                    print(f'vi: {vi}')
                    print('routes:')
                    print(edgeset)
                    input('halt')
                j1_to_i = self.points_between(d_set, vj1, vi)
                vk = self.p_neighborhoods[vip][edgeset_index]
                for k in vk:
                    if k == vi:
                        continue
                    if vip == k:
                        continue
                    if k in i1_to_j:
                        move = self.t1_unstring(d_set, j, k, vi)
                        possible_moves[move_key] = {'frame' : move,
                                                    'cost' : self.circuit_cost(move)}
                        move_key += 1
                    if k in j1_to_i:
                        vk1 = self.find_successor(k, d_set)
                        vl = self.p_neighborhoods[vk1][edgeset_index]
                        j_to_k = self.points_between(d_set, j, k)
                        for l in vl:
                            if vi == l:
                                continue
                            if l not in j_to_k:
                                continue
                            if k != vj1 and l != vi1:
                                # print([j, k, l, vi])
                                move = self.t2_unstring(d_set, j, k, l, vi)
                                possible_moves[move_key] = {'frame' : move,
                                                            'cost' : self.circuit_cost(move)}
                                move_key += 1
                            # if possible_moves == {}:
                            #     print([vi, j, k, l])
                            #     print(edgeset)
        min_pair = self.best_candidate(possible_moves)
        try:
            return possible_moves[min_pair[0]]
        except KeyError:
            return {'frame' : edgeset}

    def insert(self, vertex, route_index):
        route = self.route_list[route_index]
        if vertex in self.route_list[route_index]:
            print('LATE HIT')
            input(':')
        if set(route) == set([None]):
            newlist = [None] * self.tot_verts
            newlist[vertex] = 0
            newlist[0] = vertex
        elif len(set(route)-set([None])) == 2:
            newlist = route.copy()
            o_succ = self.find_successor(0, newlist)
            newlist[vertex] = 0
            newlist[o_succ] = vertex
        else:
            newlist = self.insert_vertex(vertex, route, route_index)['frame']
        return newlist

    def insert_vertex(self, vertex, edgeset, edgeset_index, direction=False):
        possible_moves = {}
        move_key = 0
        vi = self.p_neighborhoods[vertex][edgeset_index]
        vj = self.p_neighborhoods[vertex][edgeset_index]
        if direction:
            direct = [edgeset]
        else:
            direct = [edgeset, self.reverse(edgeset, 0, 0)]
        for d_set in direct:
            for i in vi:
                if i == vertex:
                    print('hit')
                    continue
                vi1 = self.find_successor(i, d_set)
                for j in vj:
                    if j == vertex:
                        continue
                    if i == j:
                        continue
                    try:
                        j_to_i = self.points_between(d_set, j, i)
                    except TypeError:
                        print('jtoi')
                        print(f'j: {j}')
                        print(f'i: {i}')
                        print(f'v: {vertex}')
                        print(f'vi: {vi}')
                        print('route:')
                        print(edgeset)
                        input('halt')
                    i_to_j = self.points_between(d_set, i, j)
                    vj1 = self.find_successor(j, d_set)
                    vk = self.p_neighborhoods[vi1][edgeset_index]
                    vl = self.p_neighborhoods[vj1][edgeset_index]
                    for k in vk:
                        if k == vertex:
                            continue
                        if j == k:
                            continue
                        if k not in j_to_i:
                            continue
                        possible_moves[move_key] = self.t1_string(d_set, i, j, k, vertex)
                        move_key += 1
                        for l in vl:
                            if l == vertex:
                                continue
                            if l == i:
                                continue
                            if l not in i_to_j:
                                continue
                            if k != vj1 and l != vi1:
                                possible_moves[move_key] = self.t2_string(d_set, i, j, k, l, vertex)
                                move_key += 1
        min_pair = self.best_candidate(possible_moves)
        return possible_moves[min_pair[0]]

    def post_opt(self, route_set):
        working_routes = route_set.copy()
        for route in route_set:
            route_index = route_set.index(route)
            tau = route.copy()
            zed_star = self.circuit_cost(route)
            zed = 0
            t = 1
            n = len(route) - 1
            # print(f'Route {route_index} start value: {zed_star}')
            while t != n + 1:
                if tau[t] == None:
                    # print(t)
                    t += 1
                    continue
                if tau[t] == 0:
                    tau, zed = self.reinsert_vertex(0, tau, route_index)
                else:
                    tau, zed = self.reinsert_vertex(t, tau, route_index)
                if zed < zed_star:
                    working_routes[route_index] = tau.copy()
                    zed_star = zed
                    # print(f'Improvement to: {zed}')
                    t = 1
                    # self.history.append(working_routes)
                elif zed >= zed_star:
                    t += 1
        return working_routes

    def reinsert_vertex(self, vi, edgeset, edgeset_index):
        possible_moves = {}
        move_key = 0
        for d_set in [edgeset, self.reverse(edgeset, 0, 0)]:
            vi1 = self.find_successor(vi, d_set)
            vip = self.find_predecessor(vi, d_set)
            vj = self.p_neighborhoods[vi1][edgeset_index]
            for j in vj:
                if j == vi:
                    continue
                if j == vip:
                    continue
                vj1 = self.find_successor(j, d_set)
                try:
                    i1_to_j = self.points_between(d_set, vi1, j)
                except RecursionError:
                    print('i1toj')
                    print(f'j: {j}')
                    print(f'i1: {vi1}')
                    print(f'vi: {vi}')
                    print('routes:')
                    print(edgeset)
                    input('halt')
                j1_to_i = self.points_between(d_set, vj1, vi)
                vk = self.p_neighborhoods[vip][edgeset_index]
                for k in vk:
                    if k == vi:
                        continue
                    if k in i1_to_j:
                        move = self.t1_unstring(d_set, j, k, vi)
                        possible_moves[move_key] = self.insert_vertex(vi, move, edgeset_index, direction=True)
                        move_key += 1
                    if k in j1_to_i:
                        vk1 = self.find_successor(k, d_set)
                        vl = self.p_neighborhoods[vk1][edgeset_index]
                        j_to_k = self.points_between(d_set, j, k)
                        for l in vl:
                            if vi == l:
                                continue
                            if l not in j_to_k:
                                continue
                            if k != vj1 and l != vi1:
                                move = self.t2_unstring(d_set, j, k, l, vi)
                                possible_moves[move_key] = self.insert_vertex(vi, move, edgeset_index, direction=True)
                                move_key += 1
        min_pair = self.best_candidate(possible_moves)
        try:
            return possible_moves[min_pair[0]]['frame'], min_pair[1]
        except KeyError:
            return edgeset, self.circuit_cost(edgeset)

    def stream_header(self):
        print('|F1+|F2+| iter | end |  time  |   E/s   |   F1*   |   F2*   |val|   F1   |   F2   | m |    α    |    ß    | ΔMAX | S |')
        print('|--------------------------------------------------------------------------------------------------------------------|')

    def stream_body(self, f1up, f2up, f1, f2, valid):
        if f1up:
            f1plus = '*'
        else:
            f1plus = ' '
        if f2up:
            f2plus = '*'
        else:
            f2plus = ' '
        if self.us_clear:
            u = ' '
        else:
            u = '*'
        if valid:
            val = '*'
        else:
            val = ' '
        tim = time.process_time() - self.time
        try:
            eps = self.cur_iter/tim
        except ZeroDivisionError:
            eps = 8008.0
        out = '|{:^3}|{:^3}|{:>6}|{:>5}|{:>8.1f}|{:>9.2f}|{:>9g}|{:>9g}|{:^3}|{:>8g}|{:>8g}|{:^3}|{:^9.3f}|{:^9.3f}|{:>6.2f}|{:^3}|'.format(f1plus, f2plus, self.cur_iter, self.max_iter, tim, eps, self.f1_star, self.f2_star, val, f1, f2, self.m, self.alpha, self.beta, self.delta_max, u)
        print(out)