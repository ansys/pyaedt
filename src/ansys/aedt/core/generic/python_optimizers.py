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

import sys
import threading

import numpy as np

from ansys.aedt.core.base import PyAedtBase


class ThreadTrace(threading.Thread):
    """Control a thread with python"""

    def __init__(self, *args, **keywords):
        threading.Thread.__init__(self, *args, **keywords)
        self.killed = False

    def start(self):
        self.__run_backup = self.run
        self.run = self.__run
        threading.Thread.start(self)

    def __run(self):
        sys.settrace(self.globaltrace)
        self.__run_backup()
        self.run = self.__run_backup

    def globaltrace(self, frame, event, arg):
        if event == "call":
            return self.localtrace
        else:
            return None

    def localtrace(self, frame, event, arg):
        if self.killed:
            if event == "line":
                raise SystemExit()
        return self.localtrace

    def kill(self):
        self.killed = True


class GeneticAlgorithm(PyAedtBase):
    """Genetic Algorithm for Python

    Basic implementation of elitist genetic algorithm for solving problems with integers, continuous, boolean
    or mixed variables.

    Parameters
    ----------
    function : callable
        The Objective function to be minimized. This implementation minimizes the given objective function.
    dim : int
        Number of variables
    reference_file : str, optional
        Reference file to create the cromosomes. If it is not specified, the function should create the cromose.
    goal : float, optional
        If after 'max_iteration_no_improv' iterations the goal is not improvedaf, the algorithm stops
    var_type: str
        Type of the optimization variables. The default is 'bool'.
        Other options are: 'int' if all variables are integer, and 'real' if all variables are
        real value or continuous
    boundaries:  <numpy array/None>
        By default is None. None if var_type is 'bool', otherwise provide an array of tuples
        of length two as boundaries for each variable, the length of the array must be equal dimension.
        For example, np.array([0,100],[0,200]) determines lower boundary 0 and upper boundary 100 for first
        and upper boundary 200 for second variable where dimension is 2.
    var_type_mixed:  <numpy array/None> -
        By default is None. None if all variables have the same type, otherwise this can be used to specify the type of
        each variable separately.
        For example if the first variable is integer but the second one is real the input is:
        np.array(['int'],['real']). NOTE: it does not accept 'bool'. If variable type is Boolean use 'int' and provide
        a boundary as [0,1] in variable_boundaries.
    function_timeout: float
        If the given function does not provide output before function_timeout (unit is seconds)
        the algorithm raise error.
        For example, when there is an infinite loop in the given function.
    algorithm_parameters: dict
        Genetic algorithm parameters:
            max_num_iteration : int
            population_size : int
            crossover_prob: float
            parents_portion: float
            crossover_type: string
                The default is 'uniform'. Other options are 'one_point' or 'two_point'
            mutation_prob : float
            elite_ration : float
            max_iteration_no_improv: int
                Successive iterations without improvement. If None it is ineffective
    progress_bar: bool
        Show progress bar. The default is True.

    Examples
    --------
    Optimize a defined function using a genetic algorithm.

    >>>import numpy as np
    >>>from ansys.aedt.core.generic.python_optimizers import GeneticAlgorithm as ga
    >>> def f(X):
    >>>     return np.sum(X)
    >>>varbound = np.array([[0, 10]] * 3)
    >>>model = ga(function=f, dimension=3, var_type='real', variable_boundaries=varbound)
    >>>model.run()

    """

    def __init__(
        self,
        function,
        dim,
        reference_file=None,
        population_file=None,
        goal=0,
        var_type="bool",
        boundaries=None,
        var_type_mixed=None,
        function_timeout=0,
        algorithm_parameters=None,
        progress_bar=True,
    ):
        self.population_file = None
        self.goal = 1e10
        if population_file:
            self.population_file = population_file

        self.function = function
        self.dim = int(dim)
        self.goal = float(goal)
        if not var_type == "bool" and not var_type == "int" and not var_type == "real":
            raise ValueError("Variable type is not correct")
        if var_type_mixed is None:
            if var_type == "real":
                self.var_type = np.array([["real"]] * self.dim)
            else:
                self.var_type = np.array([["int"]] * self.dim)
        else:
            if type(var_type_mixed).__module__ != "numpy":
                raise ValueError("var_type must be numpy array")
            if len(var_type_mixed) != self.dim:
                raise ValueError("var_type must have a length equal dimension")
            self.var_type = var_type_mixed

        if var_type != "bool" or type(var_type_mixed).__module__ == "numpy":
            if len(boundaries) != self.dim:
                raise ValueError("boundaries must have a length equal dimension")
            if type(boundaries).__module__ != "numpy":
                raise ValueError("boundaries must be numpy array")

            for i in boundaries:
                if len(i) != 2:
                    raise ValueError("boundary for each variable must be a tuple of length two")
                if i[0] > i[1]:
                    raise ValueError("lower boundaries must be smaller than upper_boundaries")
            self.var_bound = boundaries
        else:
            self.var_bound = np.array([[0, 1]] * self.dim)

        self.timeout = float(function_timeout)
        if progress_bar:
            self.progress_bar = True
        else:
            self.progress_bar = False

        # GA parameters
        if not algorithm_parameters:
            algorithm_parameters = {
                "max_num_iteration": None,
                "population_size": 50,
                "crossover_prob": 0.5,
                "parents_portion": 0.3,
                "crossover_type": "uniform",
                "mutation_prob": 0.2,
                "elite_ratio": 0.05,
                "max_iteration_no_improv": None,
            }
        self.ga_param = algorithm_parameters

        if not (1 >= self.ga_param["parents_portion"] >= 0):
            raise ValueError("parents_portion must be in range [0,1]")

        self.population_size = int(self.ga_param["population_size"])
        self.par_s = int(self.ga_param["parents_portion"] * self.population_size)
        trl = self.population_size - self.par_s
        if trl % 2 != 0:
            self.par_s += 1

        self.prob_mut = self.ga_param["mutation_prob"]

        if not (1 >= self.prob_mut >= 0):
            raise ValueError("mutation_prob must be in range [0,1]")

        self.prob_cross = self.ga_param["crossover_prob"]
        if not (1 >= self.prob_cross >= 0):
            raise ValueError("prob_cross must be in range [0,1]")

        if not (1 >= self.ga_param["elite_ratio"] >= 0):
            raise ValueError("elite_ratio must be in range [0,1]")
        trl = self.population_size * self.ga_param["elite_ratio"]

        if trl < 1 and self.ga_param["elite_ratio"] > 0:
            self.num_elit = 1
        else:
            self.num_elit = int(trl)

        if self.par_s < self.num_elit:
            raise ValueError("number of parents must be greater than number of elits")

        if self.ga_param["max_num_iteration"] is None:
            self.iterate = 0
            for i in range(0, self.dim):
                if self.var_type[i] == "int":
                    self.iterate += (
                        (self.var_bound[i][1] - self.var_bound[i][0]) * self.dim * (100 / self.population_size)
                    )
                else:
                    self.iterate += (self.var_bound[i][1] - self.var_bound[i][0]) * 50 * (100 / self.population_size)
            self.iterate = int(self.iterate)
            if (self.iterate * self.population_size) > 10000000:
                self.iterate = 10000000 / self.population_size
        else:
            self.iterate = int(self.ga_param["max_num_iteration"])

        self.crossover_type = self.ga_param["crossover_type"]
        if (
            not self.crossover_type == "uniform"
            and not self.crossover_type == "one_point"
            and not self.crossover_type == "two_point"
        ):
            raise ValueError("crossover_type must 'uniform', 'one_point', or 'two_point'")

        self.stop_iterations = False
        if self.ga_param["max_iteration_no_improv"] is None:
            self.stop_iterations = self.iterate + 1
        else:
            self.stop_iterations = int(self.ga_param["max_iteration_no_improv"])

        self.integers = np.where(self.var_type == "int")
        self.reals = np.where(self.var_type == "real")
        self.report = []
        self.best_function = []
        self.best_variable = []
        self.output_dict = {}
        self.pop = []
        self.reference_file = reference_file
        self.evaluate_val = 1e10

    def run(self):
        """Implement the genetic algorithm"""
        # Init Population
        pop = np.array([np.zeros(self.dim + 1)] * self.population_size)
        solo = np.zeros(self.dim + 1)
        var = np.zeros(self.dim)

        for p in range(0, self.population_size):
            for i in self.integers[0]:
                var[i] = np.random.randint(self.var_bound[i][0], self.var_bound[i][1] + 1)
                solo[i] = var[i].copy()
            for i in self.reals[0]:
                var[i] = self.var_bound[i][0] + np.random.random() * (self.var_bound[i][1] - self.var_bound[i][0])
                solo[i] = var[i].copy()

            obj = self.sim(var)
            solo[self.dim] = obj
            pop[p] = solo.copy()
            if self.population_file:
                # Save Population in CSV
                np.savetxt(self.population_file, pop, delimiter=",")

        # Sort
        pop = pop[pop[:, self.dim].argsort()]
        self.best_function = pop[0, self.dim].copy()
        self.best_variable = pop[0, : self.dim].copy()

        t = 1
        counter = 0
        while t <= self.iterate:
            if self.progress_bar:
                self.progress(t, self.iterate, status="GA is running...")
            # Sort
            pop = pop[pop[:, self.dim].argsort()]

            if pop[0, self.dim] < self.best_function:
                self.best_function = pop[0, self.dim].copy()
                self.best_variable = pop[0, : self.dim].copy()
                if pop[0, self.dim] > self.goal:
                    counter = 0
            else:
                counter += 1
            if self.best_function < self.goal:
                break
            print(f"\nInfo: Iteration {t}")
            print(f"\nInfo: Goal {self.goal}")
            print(f"\nInfo: Best Function {self.best_function}")
            print(f"\nInfo: Best Variable {self.best_variable}")

            # Report
            self.report.append(pop[0, self.dim])

            # Normalizing objective function
            # normobj = np.zeros(self.population_size)
            minobj = pop[0, self.dim]
            if minobj < 0:
                normobj = pop[:, self.dim] + abs(minobj)

            else:
                normobj = pop[:, self.dim].copy()

            maxnorm = np.amax(normobj)
            normobj = maxnorm - normobj + 1

            # Calculate probability
            sum_normobj = np.sum(normobj)
            # prob = np.zeros(self.population_size)
            prob = normobj / sum_normobj
            cumprob = np.cumsum(prob)

            # Select parents
            par = np.array([np.zeros(self.dim + 1)] * self.par_s)
            # Elite
            for k in range(0, self.num_elit):
                par[k] = pop[k].copy()
            # Random population. Not repeated parents
            for k in range(self.num_elit, self.par_s):
                repeated_parent = True
                count = 0
                while repeated_parent:
                    count += 1
                    index = np.searchsorted(cumprob, np.random.random())
                    is_in_list = np.any(np.all(pop[index] == par, axis=1))
                    if count >= 10 or not is_in_list:
                        repeated_parent = False
                        par[k] = pop[index].copy()

            ef_par_list = np.array([False] * self.par_s)
            par_count = 0
            while par_count == 0:
                for k in range(0, self.par_s):
                    if np.random.random() <= self.prob_cross:
                        ef_par_list[k] = True
                        par_count += 1

            ef_par = par[ef_par_list].copy()

            # New generation
            pop = np.array([np.zeros(self.dim + 1)] * self.population_size)
            # Parents
            for k in range(0, self.par_s):
                pop[k] = par[k].copy()
            # Children. If children is repeated, try up to 10 times
            for k in range(self.par_s, self.population_size, 2):
                repeated_children = True
                count = 0
                while repeated_children:
                    r1 = np.random.randint(0, par_count)
                    r2 = np.random.randint(0, par_count)
                    pvar1 = ef_par[r1, : self.dim].copy()
                    pvar2 = ef_par[r2, : self.dim].copy()

                    ch = self.cross(pvar1, pvar2, self.crossover_type)
                    ch1 = ch[0].copy()
                    ch2 = ch[1].copy()

                    ch1 = self.mut(ch1)
                    ch2 = self.mutmiddle(ch2, pvar1, pvar2)
                    count += 1
                    for population in pop:
                        is_in_list_ch1 = np.all(ch1 == population[:-1])
                        is_in_list_ch2 = np.all(ch2 == population[:-1])
                        if count >= 1000 or (not is_in_list_ch1 and not is_in_list_ch2):
                            repeated_children = False
                        elif is_in_list_ch1 or is_in_list_ch2:
                            repeated_children = True
                            break

                solo[: self.dim] = ch1.copy()
                obj = self.sim(ch1)
                solo[self.dim] = obj
                pop[k] = solo.copy()
                solo[: self.dim] = ch2.copy()
                obj = self.sim(ch2)
                solo[self.dim] = obj
                pop[k + 1] = solo.copy()
                if self.population_file:
                    # Save Population in CSV
                    np.savetxt(self.population_file, pop, delimiter=",")

            t += 1
            if counter > self.stop_iterations or self.best_function == 0:
                pop = pop[pop[:, self.dim].argsort()]
                text = str(t - 1)
                print("\nInfo: GA is terminated after " + text + " iterations")
                break

        # Last generation Info
        # Sort
        if t - 1 == self.iterate:
            text = str(t - 1)
            print("\nInfo: GA is terminated after " + text + " iterations")

        pop = pop[pop[:, self.dim].argsort()]
        self.pop = pop
        self.best_function = pop[0, self.dim].copy()
        self.best_variable = pop[0, : self.dim].copy()
        # Report
        self.report.append(pop[0, self.dim])
        self.output_dict = {"variable": self.best_variable, "function": self.best_function}
        if self.progress_bar:
            show = " " * 100
            sys.stdout.write("\r%s" % (show))
            sys.stdout.flush()

        sys.stdout.write("\r Best solution:\n %s" % (self.best_variable))
        sys.stdout.write("\n\n Objective:\n %s\n" % (self.best_function))

        return True

    def cross(self, x, y, c_type):
        ofs1 = x.copy()
        ofs2 = y.copy()

        if c_type == "one_point":
            ran = np.random.randint(0, self.dim)
            for i in range(0, ran):
                ofs1[i] = y[i].copy()
                ofs2[i] = x[i].copy()

        if c_type == "two_point":
            ran1 = np.random.randint(0, self.dim)
            ran2 = np.random.randint(ran1, self.dim)

            for i in range(ran1, ran2):
                ofs1[i] = y[i].copy()
                ofs2[i] = x[i].copy()

        if c_type == "uniform":
            for i in range(0, self.dim):
                ran = np.random.random()
                if ran < 0.5:
                    ofs1[i] = y[i].copy()
                    ofs2[i] = x[i].copy()

        return np.array([ofs1, ofs2])

    def mut(self, x):
        for i in self.integers[0]:
            ran = np.random.random()
            if ran < self.prob_mut:
                x[i] = np.random.randint(self.var_bound[i][0], self.var_bound[i][1] + 1)

        for i in self.reals[0]:
            ran = np.random.random()
            if ran < self.prob_mut:
                x[i] = self.var_bound[i][0] + np.random.random() * (self.var_bound[i][1] - self.var_bound[i][0])

        return x

    def mutmiddle(self, x, p1, p2):
        for i in self.integers[0]:
            ran = np.random.random()
            if ran < self.prob_mut:
                if p1[i] < p2[i]:
                    x[i] = np.random.randint(p1[i], p2[i])
                elif p1[i] > p2[i]:
                    x[i] = np.random.randint(p2[i], p1[i])
                else:
                    x[i] = np.random.randint(self.var_bound[i][0], self.var_bound[i][1] + 1)

        for i in self.reals[0]:
            ran = np.random.random()
            if ran < self.prob_mut:
                if p1[i] < p2[i]:
                    x[i] = p1[i] + np.random.random() * (p2[i] - p1[i])
                elif p1[i] > p2[i]:
                    x[i] = p2[i] + np.random.random() * (p1[i] - p2[i])
                else:
                    x[i] = self.var_bound[i][0] + np.random.random() * (self.var_bound[i][1] - self.var_bound[i][0])
        return x

    def evaluate(self):
        if not self.reference_file:
            self.evaluate_val = self.function(self.temp)
            return True
        else:
            self.evaluate_val = self.function(self.temp, self.reference_file)
            return True

    def sim(self, X):
        self.temp = X.copy()
        if self.timeout > 0:
            thread = ThreadTrace(target=self.evaluate, daemon=None)
            thread.start()
            thread.join(timeout=self.timeout)
            if thread.is_alive():
                print("After " + str(self.timeout) + " seconds delay the given function does not provide any output")
                thread.kill()
                # after the kill, you must call join to really kill it.
                thread.join()
        else:
            self.evaluate()
        return self.evaluate_val

    def progress(self, count, total, status=""):
        bar_len = 50
        filled_len = int(round(bar_len * count / float(total)))

        percents = round(100.0 * count / float(total), 1)
        bar = "|" * filled_len + "_" * (bar_len - filled_len)

        sys.stdout.write("\r%s %s%s %s" % (bar, percents, "%", status))
        sys.stdout.flush()
