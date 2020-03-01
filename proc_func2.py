#cython: language_level=3
import numpy as np
import math

class GenFunc:
    """A set of general functions intended for subclassing.
    """
    
    def __init__(self, points):
        self.dist = points.d_matrix
        self.costs = points.c_matrix

    def checkinit(self):
        if hasattr(self, 'dist'):
            pass
        else:
            raise NotImplementedError('distance is not defined')

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
            print(edges)
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
            print(edges)
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

    def points_between(self, edges, v1, v2):
        if v1 == v2:
            return []
        if v1 == None:
            print('big problem')
            print(v2)
            print(edges)
            raise TypeError
        return [v1] + self.points_between(edges, self.find_successor(v1, edges), v2)

    def test_valid(self, edgeset, pre_change=[], indicator='+', v=None, i=None, j=None, k=None, l=None):
        tester = set()
        for i in edgeset:
            if i in tester and i != None:
                print(pre_change)
                print(edgeset)
                print([v, i, j, k, l])
                raise NotImplementedError(f'invalid construction with flag: {indicator}')
            if i == edgeset.index(i):
                print(pre_change)
                print(edgeset)
                print([v, i, j, k, l])
                raise NotImplementedError(f'formed a loop with flag: {indicator}')
            try:
                if edgeset[i] == None:
                    print(pre_change)
                    print(edgeset)
                    print([v, i, j, k, l])
                    raise NotImplementedError(f'invalid pointer with flag: {indicator}')
            except TypeError:
                pass
            tester.add(i)
        return True

    def best_candidate(self, candidates):
        min_pair = ['x', math.inf]
        for key in candidates.keys():
            if candidates[key] != None:
                if candidates[key]['cost'] <= min_pair[1]:
                    min_pair = [key, candidates[key]['cost']]
        return min_pair

    def circuit_cost(self, circuit):
        cost = 0
        for vertex, pointer in enumerate(circuit):
            if pointer != None:
                cost += self.dist[vertex, pointer]
        return cost
    
    def point_cost(self, circuit):
        cost = 0
        for vertex in circuit:
            if vertex != None:
                cost += self.costs[circuit.index(vertex)][vertex]
        return cost

    def t1_string(self, pointers, i, j, k, v):
        if v == i:
            print('hit')
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
        try:
            test = self.test_valid(move['frame'], pre_change=pointers, v=v, i=i, j=j, k=k)
            if not test:
                return None          
        except NotImplementedError:
            print('CAUGHT')
            print([v, i, j, k])
            move['frame'] = pointers
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
        try:
            test = self.test_valid(move['frame'], pre_change=pointers, v=v, i=i, j=j, k=k, l=l)
            if not test:
                return None
        except NotImplementedError:
            print('CAUGHT')
            print([v, i, j, k])
            move['frame'] = pointers
        move['cost'] = self.circuit_cost(move['frame'])
        return move

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
        test = self.test_valid(move, pre_change=pointers, indicator='+', v=v, j=j, k=k)
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
        test = self.test_valid(move, pre_change=pointers, indicator='-', v=v, j=j, k=k, l=l)
        if not test:
            return None
        return move

def separate(path, distances, constraint, path_num):
    # print('something is probably wrong with distance checking')
    path_directory = [None] * len(path)
    path_list = [None] * path_num
    vertices_remaining = len(path) - 1
    for loop in range(0, path_num):
        arbpath = [None] * len(path)
        valid_const = True
        index_track = 0
        dist_track = 0
        home_val = 0
        safety = 0
        while vertices_remaining > 0 and valid_const and safety < 1000:
            d_check = dist_track + distances[index_track, path[index_track]]
            l_check = d_check + distances[path[index_track], 0]
            if l_check <= constraint:
                dist_track += distances[index_track, path[index_track]]
                arbpath[index_track] = path[index_track]
                path[index_track] = None
                if index_track != 0:
                    path_directory[index_track] = loop
                    vertices_remaining -= 1
                index_track = arbpath[index_track]
            elif loop != path_num-1:
                dist_track += home_val
                arbpath[index_track] = 0
                path[0] = path[index_track]
                valid_const = False
                if index_track != 0:
                    path_directory[index_track] = loop
                    vertices_remaining -= 1
            else:
                dist_track += d_check
                arbpath[index_track] = path[index_track]
                path[index_track] = None
                if index_track != 0:
                    path_directory[index_track] = loop
                    vertices_remaining -= 1
                index_track = arbpath[index_track]
            home_val = distances[arbpath[index_track], 0]
            safety += 1
        if safety == 1000:
            raise ResourceWarning('potentially infinite loop')
        path_list[loop] = arbpath
    return path_list, path_directory

# def get_dist(dist, v1, v2):
#     return dist[v1, v2]

