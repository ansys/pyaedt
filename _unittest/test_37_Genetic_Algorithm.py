import os
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
            time.sleep(random.uniform(0, 0.12))
            return np.sum(X)

        test_project = os.path.join(self.local_scratch.path, "Test" + ".csv")
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
            population_file=test_project,
        )
        model.run()
        assert model.best_function
