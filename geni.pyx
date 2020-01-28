
import matplotlib
from matplotlib import pyplot as plt
import numpy as np
import random as r
import math
import time
import heapq

class GENIUS:
    def __init__(self, points):
        self.points = points
        self.dist = points.d_matrix
        self.offroute = list(range(0, len(points.names)))
        self.history = []
        self.onroute = []
        self.p_neighborhood = {}
        self.edges = [None] * len(points.names)
        self.floating_loss = 0
        self.floating_add = 0
        self.route_cost = 0
        self.initialize()

    def swap(self, vertex):
        if vertex in self.offroute:
            self.onroute.append(vertex)
            self.offroute.remove(vertex)
        elif vertex in self.onroute:
            self.onroute.remove(vertex)
            self.offroute.append(vertex)

    def find_successor(self, vertex, edges):
        if isinstance(vertex, int) or isinstance(vertex, np.int64):
            return edges[vertex]
        elif isinstance(vertex, list):
            successors = {}
            for point in vertex:
                successors[point] = edges[point]
            return successors
        else:
            print('oops, something went wrong with finding successors.')
            print(type(vertex))
            input(':')
            return None

    def find_predecessor(self, vertex, edges):
        if isinstance(vertex, int) or isinstance(vertex, np.int64):
            return edges.index(vertex)
        elif isinstance(vertex, list):
            predecessors = {}
            for point in vertex:
                predecessors[point] = edges.index(point)
            return predecessors
        else:
            print('oops, something went wrong with finding predecessors.')
            print(type(vertex))
            input(':')
            return None

    def reverse(self, edges, start, end):
        holding = edges.copy()
        self.reverse_recurse(holding, start, end)
        return holding
        #might be improved by just returning a diff
        #would remove this as a middleman

    def reverse_recurse(self, edges, start, end):
        tail = self.find_successor(start, edges)
        if tail == end:
            edges[end] = start
            return start
        else:
            new_end = self.reverse_recurse(edges, tail, end)
            edges[new_end] = start
            return start

    def test_valid(self, edgeset, indicator='+'):
        tester = set()
        for i in edgeset:
            if i in tester and i != None:
                print('invalid construction!')
                print(f'flag: {indicator}')
                print(edgeset)
                input(':')
                return False
            if i == edgeset.index(i):
                print('formed a loop!')
                print(f'flag: {indicator}')
                print(edgeset)
                input(':')
                return False
            try:
                if edgeset[i] == None:
                    print('invalid pointer')
                    print(f'flag: {indicator}')
                    print(edgeset)
                    input(':')
                    return False
            except TypeError:
                pass
            tester.add(i)
        return True

    def circuit_cost(self, circuit):
        cost = 0
        for vertex, pointer in enumerate(circuit):
            if pointer != None:
                cost += self.dist[vertex, pointer]
        return cost

    def points_between(self, edges, v1, v2):
        if v1 == v2:
            return []
        return [v1] + self.points_between(edges, self.find_successor(v1, edges), v2)
        
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
        self.history.append(self.edges)
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
        min_pair = ['x', math.inf]
        for key in possible_moves.keys():
            if possible_moves[key] != None:
                if possible_moves[key]['cost'] <= min_pair[1]:
                    min_pair = [key, possible_moves[key]['cost']]
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

    def t1_string(self, pointers, i, j, k, v):
        move = {}
        successor = self.find_successor([i, j, k], pointers)
        move['frame'] = pointers.copy()
        if successor[i] != j:
            move['frame'] = self.reverse(move['frame'], successor[i], j)
        if successor[j] != k:
            move['frame'] = self.reverse(move['frame'], successor[j], k)
        move['frame'][i] = v
        move['frame'][v] = j
        move['frame'][successor[i]] = k
        move['frame'][successor[j]] = successor[k]
        test = self.test_valid(move['frame'])
        if not test:
            return None
        move['cost'] = self.circuit_cost(move['frame'])
        return move
    
    def t2_string(self, pointers, i, j, k, l, v):
        move = {}
        successor = self.find_successor([i, j], pointers)
        predecessor = self.find_predecessor([k, l], pointers)
        move['frame'] = pointers.copy()
        if successor[i] != predecessor[l]:
            move['frame'] = self.reverse(move['frame'], successor[i], predecessor[l])
        if l != j:
            move['frame'] = self.reverse(move['frame'], l, j)
        move['frame'][i] = v
        move['frame'][v] = j
        move['frame'][l] = successor[j]
        move['frame'][predecessor[k]] = predecessor[l]
        move['frame'][successor[i]] = k
        test = self.test_valid(move['frame'])
        if not test:
            return None
        move['cost'] = self.circuit_cost(move['frame'])
        return move
         
    def execute_move(self, move):
        self.edges = move['frame']
        self.route_cost = move['cost']
        self.history.append(self.edges)

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
                self.history.append(self.edges)
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
        min_pair = ['x', math.inf]
        for key in possible_moves.keys():
            if possible_moves[key] != None:
                if possible_moves[key]['cost'] <= min_pair[1]:
                    min_pair = [key, possible_moves[key]['cost']]
        return possible_moves[min_pair[0]]['frame'], min_pair[1]

    def t1_unstring(self, pointers, j, k, v):
        successor = self.find_successor([v, j, k], pointers)
        predecessor = self.find_predecessor([v, j, k], pointers)
        move = pointers.copy()
        if successor[v] != k:
            move = self.reverse(move, successor[v], k)
        if successor[k] != j:
            move = self.reverse(move, successor[k], j)
        move[predecessor[v]] = k
        move[successor[v]] = j
        move[successor[k]] = successor[j]
        move[v] = None
        test = self.test_valid(move, indicator='+')
        if not test:
            return None
        return move
    
    def t2_unstring(self, pointers, j, k, l, v):
        successor = self.find_successor([v, j, k, l], pointers)
        predecessor = self.find_predecessor([v, j, k, l], pointers)
        move = pointers.copy()
        if successor[v] != predecessor[j]:
            move = self.reverse(move, successor[v], predecessor[j])
        if successor[l] != k:
            move = self.reverse(move, successor[l], k)
        move[predecessor[v]] = k
        move[successor[l]] = predecessor[j]
        move[successor[v]] = j
        move[l] = successor[k]
        move[v] = None
        test = self.test_valid(move, indicator='-')
        if not test:
            return None
        return move