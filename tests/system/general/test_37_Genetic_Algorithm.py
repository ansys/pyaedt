# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 - 2025 ANSYS, Inc. and/or its affiliates.
# SPDX-License-Identifier: MIT
#
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import random
import time

import numpy as np
import pytest

from ansys.aedt.core.generic.python_optimizers import GeneticAlgorithm as ga


@pytest.fixture(scope="module", autouse=True)
def desktop():
    """Override the desktop fixture to DO NOT open the Desktop when running this test class"""
    return


def test_ga_launch():
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


def test_ga_timeout():
    def f(X):
        time.sleep(random.uniform(0, 0.12))
        return np.sum(X)

    algorithm_param = {
        "max_num_iteration": 3,
        "population_size": 3,
        "mutation_prob": 0.2,
        "elite_ratio": 0.01,
        "crossover_prob": 0.5,
        "parents_portion": 0.5,
        "crossover_type": "uniform",
        "max_iteration_no_improv": None,
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
        progress_bar=False,
    )
    assert model.run()
    assert model.best_function
