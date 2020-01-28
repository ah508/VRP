import numpy as np

def find_successor(vertex, edges):
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

def find_predecessor(vertex, edges):
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

def reverse(edges, start, end):
    holding = edges.copy()
    reverse_recurse(holding, start, end)
    return holding
    #might be improved by just returning a diff
    #would remove this as a middleman

def reverse_recurse(edges, start, end):
    tail = find_successor(start, edges)
    if tail == end:
        edges[end] = start
        return start
    else:
        new_end = reverse_recurse(edges, tail, end)
        edges[new_end] = start
        return start

def points_between(edges, v1, v2):
    if v1 == v2:
        return []
    return [v1] + points_between(edges, find_successor(v1, edges), v2)

def test_valid(edgeset, indicator='+'):
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