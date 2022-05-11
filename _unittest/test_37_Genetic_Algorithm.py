import random
import time

import numpy as np

from _unittest.conftest import BasisTest
from pyaedt.generic.python_optimizers import GeneticAlgorithm as ga

# Setup paths for module imports


class TestClass(BasisTest, object):
    def setup_class(self):
        BasisTest.my_setup(self)

    def teardown_class(self):
        BasisTest.my_teardown(self)

    def test_01_ga_launch(self):
        def f(X):
            return np.sum(X)

        dim = 3
        varbound = np.array([[0, 10]] * dim)
        algorithm_param = {
            "max_num_iteration": 3,
            "population_size": 4,
            "mutation_prob": 0.2,
            "elite_ratio": 0.01,
            "crossover_prob": 0.5,
            "parents_portion": 0.5,
            "crossover_type": "uniform",
            "max_iteration_no_improv": 5,
        }

        model = ga(
            function=f,
            dim=dim,
            var_type="real",
            boundaries=varbound,
            goal=0.1,
            algorithm_parameters=algorithm_param,
        )
        assert model.run()
        assert model.best_function

    def test_02_ga_timeout(self):
        def f(X):
            time.sleep(random.uniform(0, 0.12))
            return np.sum(X)

        algorithm_param = {
            "max_num_iteration": 3,
            "population_size": 4,
            "mutation_prob": 0.2,
            "elite_ratio": 0.01,
            "crossover_prob": 0.5,
            "parents_portion": 0.5,
            "crossover_type": "uniform",
            "max_iteration_no_improv": 5,
        }
        varbound = np.array([[0.5, 1.5], [1, 100], [0, 1]])
        vartype = np.array([["real"], ["int"], ["int"]])
        model = ga(
            function=f,
            dim=3,
            var_type_mixed=vartype,
            boundaries=varbound,
            goal=0.1,
            algorithm_parameters=algorithm_param,
            function_timeout=0.1,
        )
        assert model.run()
        assert model.best_function
