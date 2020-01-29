from proc_func import GenFunc
import random as r
import numpy as np
import math
import heapq



class SEARCH(GenFunc):
    def __init__(self, points, history, routes, route_identifiers, max_cap, max_len, q, n_max, alpha, beta):
        super().__init__(points)
        self.history = history
        self.tot_verts = len(points.names)
        self.route_list = routes
        self.route_ref = route_identifiers
        self.m = len(set(self.route_ref)-set([None]))
        self.m_hat = len(self.route_list)
        self.cap_const = max_cap
        self.time_const = max_len
        self.f1_star = math.inf
        self.f2_star = math.inf
        self.check_sol(routes)
        self.W = list(range(1, self.tot_verts))
        self.q = q
        self.p2 = 5
        self.theta = [5, 10]
        self.g = 0.01
        self.h = 10
        self.max_iter = n_max
        self.select_tot = [0] * self.tot_verts
        self.cur_iter = 1
        self.update_freq()
        self.alpha = alpha
        self.beta = beta
        self.delta_max = 0
        self.tabu = [math.inf] + ([0] * self.tot_verts-1)
        self.p_neighborhoods = {}

    def search(self):
        #preconditions
        condition = False #temporary
        while condition:
            self.m = len(set(self.route_ref)-set([None]))
            self.update_neighbors()
            selected_verts = r.sample(self.W, self.q)
            candidates = {}
            cand_tag = 0
            empties = self.get_empty(self.route_list)
            for vertex in selected_verts:
                self.set_p1(vertex)
                transfers = self.neighbor_routes(vertex, empties)
                del_route = self.extract(vertex, self.route_ref[vertex])
                for route_index in transfers:
                    route_adjust = self.insert(vertex, route_index)





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

    def execute_move(self, move):
        pass

    def check_sol(self, solution):
        v_cost, iv_cost = self.sol_cost(solution)
        if v_cost == iv_cost:
            if v_cost < self.f1_star:
                self.s_star = solution
                self.f1_star = v_cost
        if iv_cost < self.f2_star:
            self.sn_star = solution
            self.f2_star = solution

    def neighbor_routes(self, vertex, empties):
        distances = self.dist[vertex].copy()
        distances[vertex] = math.inf
        nearest = heapq.nsmallest(self.p1, distances)
        neighbors = []
        for i in nearest:
            if i != math.inf:
                neighbors.append(np.where(distances==i)[0][0])
        banned = [self.route_ref[vertex]]
        neighborhood = empties.copy
        for friend in neighbors:
            if self.route_ref[friend] not in banned:
                neighborhood.append(self.route_ref[friend])
                banned.append(self.route_ref[friend])
        return neighborhood

    def update_neighbors(self):
        for vertex in range(0, self.tot_verts):
            self.p_neighborhoods[vertex] = {}
            for route in range(0, self.m_hat):
                self.p_neighborhoods[vertex][route] = self.neighbors_on(route, vertex)

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
                neighbors.append(np.where(distances==i)[0][0])
        return neighbors
    
    def valid_cost(self, routes):
        total_cost = 0
        for route in routes:
            total_cost += self.circuit_cost(route)
        return total_cost

    def sol_cost(self, routes):
        v_cost = self.valid_cost(routes)
        cap_over = 0
        time_over = self.beta*(max(0, v_cost-self.time_const))
        try:
            if self.implementation_notification:
                pass
        except AttributeError:
            print('constraints not yet formally implemented')
            self.implementation_notification = True
        # for route in routes:
            #constraint weightings go here 
        return v_cost, (v_cost + cap_over + time_over)

    def extract(self, vertex, route_index):
        route = self.route_list[route_index]
        n_vert = len(set(route)-set([None]))
        if n_vert == 1:
            print("dude you can't have one vertex on a route")
            raise NotImplementedError
        elif n_vert == 2:
            return [None] * self.tot_verts
        elif n_vert == 3:
            newlist = route.copy()
            prev = self.find_predecessor(vertex, newlist)
            succ = self.find_successor(vertex, newlist)
            newlist[prev] = succ
        else:
            newlist = self.nt_extract(vertex, route, route_index)['frame']
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
                i1_to_j = self.points_between(d_set, vi1, j)
                j1_to_i = self.points_between(d_set, vj1, vi)
                vk = self.p_neighborhoods[vip]
                for k in vk:
                    if k == vi:
                        continue
                    if k in i1_to_j:
                        move = self.t1_unstring(d_set, j, k, vi)
                        if move:
                            possible_moves[move_key] = {'frame' : move,
                                                        'cost' : self.circuit_cost(move)}
                            move_key += 1
                    if k in j1_to_i:
                        vk1 = self.find_successor(k, d_set)
                        vl = self.p_neighborhoods[vk1]
                        j_to_k = self.points_between(d_set, j, k)
                        for l in vl:
                            if vi == l:
                                continue
                            if l not in j_to_k:
                                continue
                            if k != vj1 and l != vi1:
                                move = self.t2_unstring(d_set, j, k, l, vi)
                                if move:
                                    possible_moves[move_key] = {'frame' : move,
                                                                'cost' : self.circuit_cost(move)}
                                    move_key += 1
        min_pair = ['x', math.inf]
        for key in possible_moves.keys():
            if possible_moves[key] != None:
                if possible_moves[key]['cost'] <= min_pair[1]:
                    min_pair = [key, possible_moves[key]['cost']]
        return possible_moves[min_pair[0]]

    def insert(self, vertex, route_index):
        route = self.route_list[route_index]
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
                    continue
                vi1 = self.find_successor(i, d_set)
                for j in vj:
                    if j == vertex:
                        continue
                    if i == j:
                        continue
                    j_to_i = self.points_between(d_set, j, i)
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
                            if i == l:
                                continue
                            if l not in i_to_j:
                                continue
                            if k != vj1 and l != vi1:
                                possible_moves[move_key] = self.t2_string(d_set, i, j, k, l, vertex)
                                move_key += 1
        min_pair = self.best_candidate(possible_moves)
        return possible_moves[min_pair[0]]
    
