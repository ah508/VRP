from info_work import get_working_map
from genius import GENIUS
from search_test import SEARCH
from tabu import TABU

r_add_vec = []

def solve(client):
    dist, dur, backmap = get_working_map(client)
    class Setup:
        def __init__(self, dur, cost):
            self.costs = cost
            self.d_matrix = dur
