from setuptools import setup
import Cython
from Cython.Build import cythonize


setup(
    ext_modules = cythonize('tabu.pyx')
)