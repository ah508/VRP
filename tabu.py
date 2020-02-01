import matplotlib
from matplotlib import pyplot as plt
from matplotlib import animation
import numpy as np
import time
from genius_test import GENIUS
from useful_funcs import PointGrab
from search_test import SEARCH

class TABU(SEARCH):
    def __init__(self, params):
        super().__init__(params)
        self.params = params

    def update_parameters(self, *args):
        pass