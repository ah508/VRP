import json
import os
import numpy as np
import textwrap
from maps_api import parse_addresses

class PointGrab:
    def __init__(self):
        points_to_use = input('Enter a testing set identifier: ')
        self.ptu = points_to_use
        path = os.getcwd() + "\\point_sets\\" + points_to_use
        found = False
        try:
            with open(path, "r") as f:
                self.bundle = json.load(f)
                found = True
        except FileNotFoundError:
            print('That banner does not exist.')
            quit()
        if found:
            self.sep()

    def sep(self):
        self.xpoints = self.bundle['xpoints']
        self.ypoints = self.bundle['ypoints']
        self.costs = self.bundle['costs']
        self.colors = self.bundle['colors']
        self.names = self.bundle['names']
        self.d_matrix = np.array(self.bundle['d_matrix'])