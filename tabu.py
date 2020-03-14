#cython: language_level=3
import matplotlib
from matplotlib import pyplot as plt
from matplotlib import animation
import numpy as np
import time
import math
from genius import GENIUS
from useful_funcs import PointGrab
from search_test import SEARCH
import heapq

class TABU(SEARCH):
    def __init__(self, points, routes, route_identifiers, max_cap, max_len, q, n_max, cost_func): #history removed
        print('Initializing Values')
        super().__init__(points, routes, route_identifiers, max_cap, max_len, q, n_max, cost_func) #history removed
        self.prev_iterations = 0
        self.prev_time = self.time
        naught = self.sol_cost(routes)
        if naught[2]:
            self.feas_naught = naught[0]
        else:
            self.feas_naught = math.inf
        self.infeas_naught = naught[1]

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
        self.update_parameters(n_max=self.tot_verts*50, alpha=1, beta=1, delta_max=0, cap_ten=set(), dist_ten=set(), tabu={})
        self.max_iter = self.cur_iter + self.n_max
        print(' ')
        print(' ')
        print('Starting Phase II')
        self.search()
        print(' ')
        print('Phase II complete.')
        print(' ')
        self.summary()
        try:
            self.route_list = self.s_star
        except AttributeError:
            self.route_list = self.sn_star
        self.routeassign()
        big_freq = heapq.nlargest(self.tot_verts//2, self.select_freq)
        new_W = []
        for val in big_freq:
            new_W.append(self.select_freq.index(val))
        self.update_parameters(n_max=self.tot_verts, alpha=1, beta=1, delta_max=0, cap_ten=set(), dist_ten=set(), W=new_W, tabu={}, q=len(new_W))
        self.max_iter = self.cur_iter + self.n_max
        print(' ')
        print(' ')
        print('Starting Phase III')
        self.search()
        print(' ')
        print('Phase III complete.')
        print(' ')
        self.summary()
        try:
            self.route_list = self.s_star
        except AttributeError:
            self.route_list = self.sn_star
        # self.history.append(self.route_list)
        route_costs = []
        for route in self.route_list:
            route_costs.append(self.time_cost(route))
        print(' ')
        print('Routes')
        print('------')
        for i in range(0, self.m_hat):
            if set(self.route_list[i]) == set([None]):
                continue
            print(f'Route {i}  |  Cost: {route_costs[i]}')
            print(self.route_list[i])
            print(':::')


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
        print(f'Feasible improvement   : {round(((self.feas_naught/self.f1_star)-1), 3)*100}%')
        print(f'Best infeasible        : {self.f2_star}')
        print(f'Infeasible improvement : {round(((self.infeas_naught/self.f2_star)-1), 3)*100}%')
        print(f'Average E/s            : {(self.cur_iter-self.prev_iterations)/(c_time-self.prev_time)}')
        print(f'Overall Average E/s    : {self.cur_iter/c_time}')
        # print(f'Current solution value : {self.sol_cost(self.route_list)[1]}')
        # print(f'Number of routes       : {self.m}')
        print(f'ΔMAX                   : {self.delta_max}')
        print(f'Gridlock Restarts      : {self.gridlock}')
        print(' ')
        print('Frequencies')
        print('-----------')
        print(simplefreq)
        self.prev_iterations = self.cur_iter
        self.prev_time = c_time
