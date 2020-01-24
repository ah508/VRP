import matplotlib
from matplotlib import pyplot as plt
import numpy as np
import random as r
import math
import time
import heapq

class GENI:
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

    def complete(self):
        if self.offroute == []:
            return True
        return False

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
            return None

    def find_predecessor(self, vertex, edges):
        if isinstance(vertex, int):
            return edges.index(vertex)
        elif isinstance(vertex, list):
            predecessors = {}
            for point in vertex:
                predecessors[point] = edges.index(point)
            return predecessors
        else:
            print('oops, something went wrong with finding predecessors.')
            return None

    def reverse(self, edges, start, end):
        holding = edges.copy()
        holding[edges[start]] = start
        next_edge = edges[start]
        proceed = True
        i = 0
        while proceed:
            if next_edge == end:
                proceed = False
            holding[edges[next_edge]] = next_edge
            next_edge = edges[next_edge]
            if next_edge == end:
                proceed = False
            if i > 20000:
                print('arbitrary limit exceeded, killing program')
                quit()
            i += 1
        return holding

    def test_valid(self):
        tester = set()
        for i in self.edges:
            if i in tester and i != None:
                print('invalid construction!')
            tester.add(i)

    def circuit_cost(self, circuit):
        cost = 0
        for vertex, pointer in enumerate(circuit):
            if pointer != None:
                cost += self.dist[vertex, pointer]
        return cost

    def edge_cost(self, v1, v2):
        return self.dist[v1, v2]
        
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
        # print(self.route_cost)
        self.history.append(self.edges)
        self.get_neighborhoods(5)

    def cycle(self):
        while self.offroute != []:
            chosen_vertex = r.choice(self.offroute)
            self.insert_vertex(chosen_vertex)
            self.get_neighborhoods(5)
            print("still choochin'")
            print(self.edges)

    def insert_vertex(self, vertex):
        possible_moves = {}
        move_key = 0
        vi = self.p_neighborhood[vertex]
        vj = self.p_neighborhood[vertex]
        for d_set in [self.edges.copy(), self.reverse(self.edges, 0, 0)]:
            # d_diff = self.circuit_cost(d_set) - self.route_cost
            for i in vi:
                vi1 = self.find_successor(i, d_set)
                for j in vj:
                    if i == j:
                        possible_moves[move_key] = self.standard_insert(d_set, i, vi1, vertex)
                        move_key += 1
                    else:  
                        vj1 = self.find_successor(j, d_set)
                        vk = self.p_neighborhood[vi1]
                        vl = self.p_neighborhood[vj1]
                        for k in vk:
                            if k != i and k != j:
                                if j != vi1 and k!= vj1:
                                    possible_moves[move_key] = self.t1_insert(d_set, i, j, k, vertex)
                                    move_key += 1
                            for l in vl:
                                if k != j and k != vj1 and l != i and l != vi1:
                                    possible_moves[move_key] = self.t2_insert(d_set, i, j, k, l, vertex)
                                    move_key += 1
                                print('.')
        min_pair = ['x', math.inf]
        for key in possible_moves.keys():
            # print(possible_moves[key]['cost'])
            if possible_moves[key]['cost'] <= min_pair[1]:
                min_pair = [key, possible_moves[key]['cost']]
        self.swap(vertex)
        self.execute_move(possible_moves[min_pair[0]])
        possible_moves = {}

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

    def standard_insert(self, pointers, i, i1, v):
        move = {}
        move['frame'] = pointers.copy()
        move['frame'][i] = v
        move['frame'][v] = i1
        # print(move['frame'])
        move['cost'] = self.circuit_cost(move['frame'])
        return move

    def t1_insert(self, pointers, i, j, k, v):
        move = {}
        successor = self.find_successor([i, j, k], pointers)
        move['frame'] = pointers.copy()
        move['frame'] = self.reverse(move['frame'], successor[i], j)
        move['frame'] = self.reverse(move['frame'], successor[j], k)
        move['frame'][i] = v
        move['frame'][v] = j
        move['frame'][successor[i]] = k
        move['frame'][successor[j]] = successor[k]
        move['cost'] = self.circuit_cost(move['frame'])
        return move
    
    def t2_insert(self, pointers, i, j, k, l, v):
        move = {}
        successor = self.find_successor([i, j], pointers)
        predecessor = self.find_predecessor([k, l], pointers)
        move['frame'] = pointers.copy()
        move['frame'] = self.reverse(move['frame'], successor[i], predecessor[l])
        move['frame'] = self.reverse(move['frame'], l, j)
        move['frame'][i] = v
        move['frame'][v] = j
        move['frame'][l] = successor[j]
        move['frame'][predecessor[k]] = predecessor[l]
        move['frame'][successor[i]] = k
        move['cost'] = self.circuit_cost(move['frame'])
        return move
         
    def execute_move(self, move):
        self.edges = move['frame']
        self.route_cost = move['cost']
        self.history.append(self.edges)