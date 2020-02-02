import matplotlib
from matplotlib import pyplot as plt
from matplotlib import animation
import numpy as np
import time
from genius_test import GENIUS
from useful_funcs import PointGrab
from search_test import SEARCH

class TABU(SEARCH):
    def __init__(self, points, history, routes, route_identifiers, max_cap, max_len, q, n_max):
        print('Initializing Values')
        super().__init__(points, history, routes, route_identifiers, max_cap, max_len, q, n_max)
        self.prev_iterations = 0
        self.prev_time = self.time

    def update_parameters(self, **kwargs):
        for name, value in kwargs.items():
            setattr(self, name, value)
    
    def tabu_search(self):
        print('Beginning Search.')
        self.search()
        print(' ')
        print('Phase I complete.')
        print(' ')
        self.summary()
        try:
            self.route_list = self.s_star
        except AttributeError:
            self.route_list = self.sn_star
        self.routeassign()
        self.update_parameters(n_max=2000, alpha=1, beta=1, delta_max=0, cap_ten=set(), dist_ten=set(), tabu={})
        self.max_iter = self.cur_iter + self.n_max
        print(' ')
        print(' ')
        print('Starting Phase II')
        self.search()
        print(' ')
        print('Phase II complete.')
        print(' ')
        self.summary()

    def routeassign(self):
        for i in range(1, self.tot_verts):
            for j in range(0, len(self.route_list)):
                if i in self.route_list[j]:
                    self.route_ref[i] = j

    def summary(self):
        c_time = time.process_time()
        simplefreq = ['{:.3%}'.format(i) for i in self.select_freq]
        print('Summary')
        print('-------')
        print(f'{self.cur_iter - self.prev_iterations} iterations completed in {c_time - self.prev_time} seconds.')
        print(f'Best feasible          : {self.f1_star}')
        print(f'Best infeasible        : {self.f2_star}')
        print(f'Current solution value : {self.sol_cost(self.route_list)[1]}')
        print(f'Number of routes       : {self.m}')
        print(f'ΔMAX                   : {self.delta_max}')
        print(' ')
        print('Frequencies')
        print('-----------')
        print(simplefreq)
        self.prev_iterations = self.cur_iter
        self.prev_time = c_time
