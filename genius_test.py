import numpy as np
import random as r
import math
import time
import heapq
from proc_func import GenFunc

class GENIUS(GenFunc):
    def __init__(self, points):
        super().__init__(points)
        self.points = points
        self.offroute = list(range(0, len(points.names)))
        self.history = []
        self.onroute = []
        self.p_neighborhood = {}
        self.edges = [None] * len(points.names)
        self.route_cost = 0
        self.initialize()

    def swap(self, vertex):
        if vertex in self.offroute:
            self.onroute.append(vertex)
            self.offroute.remove(vertex)
        elif vertex in self.onroute:
            self.onroute.remove(vertex)
            self.offroute.append(vertex)
        
    def initialize(self):
        self.swap(0)
        v1 = r.choice(self.offroute)
        self.swap(v1)
        v2 = r.choice(self.offroute)
        self.swap(v2)
        self.edges[0] = v1
        self.edges[v1] = v2
        self.edges[v2] = 0
        self.route_cost = self.circuit_cost(self.edges)
        self.history.append([self.edges])
        self.get_neighborhoods(5)

    def cycle(self):
        n = 3
        while self.offroute != []:
            chosen_vertex = r.choice(self.offroute)
            self.insert_vertex(chosen_vertex, self.edges)
            self.get_neighborhoods(5)
            n += 1
            print(f'+ {n}')

    def insert_vertex(self, vertex, edgeset, direction=False):
        possible_moves = {}
        move_key = 0
        vi = self.p_neighborhood[vertex]
        vj = self.p_neighborhood[vertex]
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
                    vk = self.p_neighborhood[vi1]
                    vl = self.p_neighborhood[vj1]
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
        if direction:
            return possible_moves[min_pair[0]]
        else:
            self.swap(vertex)
            self.execute_move(possible_moves[min_pair[0]])
            possible_moves = {}
            return None

    def p_neighbors(self, vertex, p):
        distances = self.dist[vertex].copy()
        valid = []
        for i in range(0, len(distances)):
            if i != vertex and i in self.onroute:
                valid.append(distances[i])
            else:
                valid.append(math.inf)
        nearest = heapq.nsmallest(p, valid)
        neighbors = []
        for i in nearest:
            if i != math.inf:
                neighbors.append(np.where(distances==i)[0][0])
        return neighbors

    def get_neighborhoods(self, p):
        for vertex in self.offroute:
            neighborhood = self.p_neighbors(vertex, p)
            self.p_neighborhood[vertex] = neighborhood
        for vertex in self.onroute:
            neighborhood = self.p_neighbors(vertex, p)
            self.p_neighborhood[vertex] = neighborhood

    def execute_move(self, move):
        self.edges = move['frame']
        self.route_cost = move['cost']
        self.history.append([self.edges])

    def post_opt(self):
        tau = self.edges.copy()
        zed = self.route_cost
        t = 1
        n = len(self.edges)
        print(f'Starting cost: {zed}')
        while t != n + 1:
            if t == n:
                tau, zed = self.reinsert_vertex(0, tau)
            else:
                tau, zed = self.reinsert_vertex(t, tau)
            if zed < self.route_cost:
                self.edges = tau.copy()
                self.route_cost = zed
                print(f'Improvement to: {zed}')
                t = 1
                self.history.append([self.edges])
            elif zed >= self.route_cost:
                t += 1

    def reinsert_vertex(self, vi, edgeset):
        possible_moves = {}
        move_key = 0
        for d_set in [edgeset, self.reverse(edgeset, 0, 0)]:
            vi1 = self.find_successor(vi, d_set)
            vip = self.find_predecessor(vi, d_set)
            vj = self.p_neighborhood[vi1]
            for j in vj:
                if j == vi:
                    continue
                if j == vip:
                    continue
                vj1 = self.find_successor(j, d_set)
                i1_to_j = self.points_between(d_set, vi1, j)
                j1_to_i = self.points_between(d_set, vj1, vi)
                vk = self.p_neighborhood[vip]
                for k in vk:
                    if k == vi:
                        continue
                    if vip == k:
                        continue
                    if k in i1_to_j:
                        move = self.t1_unstring(d_set, j, k, vi)
                        if move:
                            possible_moves[move_key] = self.insert_vertex(vi, move, direction=True)
                            move_key += 1
                    if k in j1_to_i:
                        vk1 = self.find_successor(k, d_set)
                        vl = self.p_neighborhood[vk1]
                        j_to_k = self.points_between(d_set, j, k)
                        for l in vl:
                            if vi == l:
                                continue
                            if l not in j_to_k:
                                continue
                            if k != vj1 and l != vi1:
                                move = self.t2_unstring(d_set, j, k, l, vi)
                                if move:
                                    possible_moves[move_key] = self.insert_vertex(vi, move, direction=True)
                                    move_key += 1
                            # if possible_moves == {}:
                            #     print([vi, j, k, l])
                            #     print(edgeset)
        min_pair = ['x', math.inf]
        for key in possible_moves.keys():
            if possible_moves[key] != None:
                if possible_moves[key]['cost'] <= min_pair[1]:
                    min_pair = [key, possible_moves[key]['cost']]
        return possible_moves[min_pair[0]]['frame'], min_pair[1]