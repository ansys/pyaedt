import sys
import time

import matplotlib.pyplot as plt
import numpy as np
from func_timeout import func_timeout
from func_timeout import FunctionTimedOut


###############################################################################
###############################################################################
"""Genetic Algorithm (Elitist version) for Python

    An implementation of elitist genetic algorithm for solving problems with
    continuous, integers, or mixed variables.



    Implementation and output:

        methods:
                run(): implements the genetic algorithm

        outputs:
                output_dict:  a dictionary including the best set of variables
            found and the value of the given function associated to it.
            {'variable': , 'function': }

                report: a list including the record of the progress of the
                algorithm over iterations
    """
###############################################################################
"""
        @param function <Callable> - the given objective function to be minimized
        NOTE: This implementation minimizes the given objective function.
        (For maximization multiply function by a negative sign: the absolute
        value of the output would be the actual objective function)

        @param dimension <integer> - the number of decision variables

        @param variable_type <string> - 'bool' if all variables are Boolean;
        'int' if all variables are integer; and 'real' if all variables are
        real value or continuous (for mixed type see @param variable_type_mixed)

        @param variable_boundaries <numpy array/None> - Default None; leave it
        None if variable_type is 'bool'; otherwise provide an array of tuples
        of length two as boundaries for each variable;
        the length of the array must be equal dimension. For example,
        np.array([0,100],[0,200]) determines lower boundary 0 and upper boundary 100 for first
        and upper boundary 200 for second variable where dimension is 2.

        @param variable_type_mixed <numpy array/None> - Default None; leave it
        None if all variables have the same type; otherwise this can be used to
        specify the type of each variable separately. For example if the first
        variable is integer but the second one is real the input is:
        np.array(['int'],['real']). NOTE: it does not accept 'bool'. If variable
        type is Boolean use 'int' and provide a boundary as [0,1]
        in variable_boundaries. Also if variable_type_mixed is applied,
        variable_boundaries has to be defined.

        @param function_timeout <float> - if the given function does not provide
        output before function_timeout (unit is seconds) the algorithm raise error.
        For example, when there is an infinite loop in the given function.

        Parameters
        ----------
        max_num_iteration : int
        population_size : int
        mutation_probability : float
        elite_ration : float
        crossover_probability <float in [0,1]>
        parents_portion <float in [0,1]>
        crossover_type <string> - Default is 'uniform'; 'one_point' or
        'two_point' are other options
        max_iteration_without_improv <int> - maximum number of
        successive iterations without improvement. If None it is ineffective

        @param convergence_curve <True/False> - Plot the convergence curve or not
        Default is True.
        @progress_bar <True/False> - Show progress bar or not. Default is True.

        """


class genetical_gorithm:
    def __init__(
        self,
        function,
        dimension,
        variable_type="bool",
        variable_boundaries=None,
        variable_type_mixed=None,
        function_timeout=10,
        algorithm_parameters=None,
        convergence_curve=True,
        progress_bar=True,
    ):
        self.__name__ = "genetic_algorithm"
        #############################################################
        # input function
        assert callable(function), "function must be callable"

        self.f = function
        #############################################################
        # dimension

        self.dim = int(dimension)

        #############################################################
        # input variable type

        assert (
            variable_type == "bool" or variable_type == "int" or variable_type == "real"
        ), "\n variable_type must be 'bool', 'int', or 'real'"
        #############################################################
        # input variables' type (MIXED)

        if variable_type_mixed is None:

            if variable_type == "real":
                self.var_type = np.array([["real"]] * self.dim)
            else:
                self.var_type = np.array([["int"]] * self.dim)

        else:
            assert type(variable_type_mixed).__module__ == "numpy", "\n variable_type must be numpy array"
            assert len(variable_type_mixed) == self.dim, "\n variable_type must have a length equal dimension."

            for i in variable_type_mixed:
                assert i == "real" or i == "int", (
                    "\n variable_type_mixed is either 'int' or 'real' "
                    + "ex:['int','real','real']"
                    + "\n for 'boolean' use 'int' and specify boundary as [0,1]"
                )

            self.var_type = variable_type_mixed
        #############################################################
        # input variables' boundaries

        if variable_type != "bool" or type(variable_type_mixed).__module__ == "numpy":

            assert type(variable_boundaries).__module__ == "numpy", "\n variable_boundaries must be numpy array"

            assert len(variable_boundaries) == self.dim, "\n variable_boundaries must have a length equal dimension"

            for i in variable_boundaries:
                assert len(i) == 2, "\n boundary for each variable must be a tuple of length two."
                assert i[0] <= i[1], "\n lower_boundaries must be smaller than upper_boundaries [lower,upper]"
            self.var_bound = variable_boundaries
        else:
            self.var_bound = np.array([[0, 1]] * self.dim)

        #############################################################
        # Timeout
        self.funtimeout = float(function_timeout)
        #############################################################
        # convergence_curve
        if convergence_curve == True:
            self.convergence_curve = True
        else:
            self.convergence_curve = False
        #############################################################
        # progress_bar
        if progress_bar == True:
            self.progress_bar = True
        else:
            self.progress_bar = False
        #############################################################
        #############################################################
        # input algorithm's parameters
        if not algorithm_parameters:
            algorithm_parameters = {
                "max_num_iteration": None,
                "population_size": 100,
                "mutation_probability": 0.1,
                "elit_ratio": 0.01,
                "crossover_probability": 0.5,
                "parents_portion": 0.3,
                "crossover_type": "uniform",
                "max_iteration_without_improv": None,
            }

        self.param = algorithm_parameters

        self.pop_s = int(self.param["population_size"])

        assert (
            self.param["parents_portion"] <= 1 and self.param["parents_portion"] >= 0
        ), "parents_portion must be in range [0,1]"

        self.par_s = int(self.param["parents_portion"] * self.pop_s)
        trl = self.pop_s - self.par_s
        if trl % 2 != 0:
            self.par_s += 1

        self.prob_mut = self.param["mutation_probability"]

        assert self.prob_mut <= 1 and self.prob_mut >= 0, "mutation_probability must be in range [0,1]"

        self.prob_cross = self.param["crossover_probability"]
        assert self.prob_cross <= 1 and self.prob_cross >= 0, "mutation_probability must be in range [0,1]"

        assert self.param["elit_ratio"] <= 1 and self.param["elit_ratio"] >= 0, "elit_ratio must be in range [0,1]"

        trl = self.pop_s * self.param["elit_ratio"]
        if trl < 1 and self.param["elit_ratio"] > 0:
            self.num_elit = 1
        else:
            self.num_elit = int(trl)

        assert self.par_s >= self.num_elit, "\n number of parents must be greater than number of elits"

        if self.param["max_num_iteration"] == None:
            self.iterate = 0
            for i in range(0, self.dim):
                if self.var_type[i] == "int":
                    self.iterate += (self.var_bound[i][1] - self.var_bound[i][0]) * self.dim * (100 / self.pop_s)
                else:
                    self.iterate += (self.var_bound[i][1] - self.var_bound[i][0]) * 50 * (100 / self.pop_s)
            self.iterate = int(self.iterate)
            if (self.iterate * self.pop_s) > 10000000:
                self.iterate = 10000000 / self.pop_s
        else:
            self.iterate = int(self.param["max_num_iteration"])

        self.c_type = self.param["crossover_type"]
        assert (
            self.c_type == "uniform" or self.c_type == "one_point" or self.c_type == "two_point"
        ), "\n crossover_type must 'uniform', 'one_point', or 'two_point' Enter string"

        self.stop_mniwi = False
        if self.param["max_iteration_without_improv"] == None:
            self.mniwi = self.iterate + 1
        else:
            self.mniwi = int(self.param["max_iteration_without_improv"])

        #############################################################

    def run(self):

        #############################################################
        # Initial Population

        self.integers = np.where(self.var_type == "int")
        self.reals = np.where(self.var_type == "real")

        pop = np.array([np.zeros(self.dim + 1)] * self.pop_s)
        solo = np.zeros(self.dim + 1)
        var = np.zeros(self.dim)

        for p in range(0, self.pop_s):

            for i in self.integers[0]:
                var[i] = np.random.randint(self.var_bound[i][0], self.var_bound[i][1] + 1)
                solo[i] = var[i].copy()
            for i in self.reals[0]:
                var[i] = self.var_bound[i][0] + np.random.random() * (self.var_bound[i][1] - self.var_bound[i][0])
                solo[i] = var[i].copy()

            obj = self.sim(var)
            solo[self.dim] = obj
            pop[p] = solo.copy()

        #############################################################

        #############################################################
        # Report
        self.report = []
        self.test_obj = obj
        self.best_variable = var.copy()
        self.best_function = obj
        ##############################################################

        t = 1
        counter = 0
        while t <= self.iterate:

            if self.progress_bar == True:
                self.progress(t, self.iterate, status="GA is running...")
            #############################################################
            # Sort
            pop = pop[pop[:, self.dim].argsort()]

            if pop[0, self.dim] < self.best_function:
                counter = 0
                self.best_function = pop[0, self.dim].copy()
                self.best_variable = pop[0, : self.dim].copy()
            else:
                counter += 1
            #############################################################
            # Report

            self.report.append(pop[0, self.dim])

            ##############################################################
            # Normalizing objective function

            normobj = np.zeros(self.pop_s)

            minobj = pop[0, self.dim]
            if minobj < 0:
                normobj = pop[:, self.dim] + abs(minobj)

            else:
                normobj = pop[:, self.dim].copy()

            maxnorm = np.amax(normobj)
            normobj = maxnorm - normobj + 1

            #############################################################
            # Calculate probability

            sum_normobj = np.sum(normobj)
            prob = np.zeros(self.pop_s)
            prob = normobj / sum_normobj
            cumprob = np.cumsum(prob)

            #############################################################
            # Select parents
            par = np.array([np.zeros(self.dim + 1)] * self.par_s)

            for k in range(0, self.num_elit):
                par[k] = pop[k].copy()
            for k in range(self.num_elit, self.par_s):
                index = np.searchsorted(cumprob, np.random.random())
                par[k] = pop[index].copy()

            ef_par_list = np.array([False] * self.par_s)
            par_count = 0
            while par_count == 0:
                for k in range(0, self.par_s):
                    if np.random.random() <= self.prob_cross:
                        ef_par_list[k] = True
                        par_count += 1

            ef_par = par[ef_par_list].copy()

            #############################################################
            # New generation
            pop = np.array([np.zeros(self.dim + 1)] * self.pop_s)

            for k in range(0, self.par_s):
                pop[k] = par[k].copy()

            for k in range(self.par_s, self.pop_s, 2):
                r1 = np.random.randint(0, par_count)
                r2 = np.random.randint(0, par_count)
                pvar1 = ef_par[r1, : self.dim].copy()
                pvar2 = ef_par[r2, : self.dim].copy()

                ch = self.cross(pvar1, pvar2, self.c_type)
                ch1 = ch[0].copy()
                ch2 = ch[1].copy()

                ch1 = self.mut(ch1)
                ch2 = self.mutmidle(ch2, pvar1, pvar2)
                solo[: self.dim] = ch1.copy()
                obj = self.sim(ch1)
                solo[self.dim] = obj
                pop[k] = solo.copy()
                solo[: self.dim] = ch2.copy()
                obj = self.sim(ch2)
                solo[self.dim] = obj
                pop[k + 1] = solo.copy()
            #############################################################
            t += 1
            if counter > self.mniwi:
                pop = pop[pop[:, self.dim].argsort()]
                if pop[0, self.dim] >= self.best_function:
                    t = self.iterate
                    if self.progress_bar == True:
                        self.progress(t, self.iterate, status="GA is running...")
                    time.sleep(2)
                    t += 1
                    self.stop_mniwi = True

        #############################################################
        # Sort
        pop = pop[pop[:, self.dim].argsort()]

        if pop[0, self.dim] < self.best_function:
            self.best_function = pop[0, self.dim].copy()
            self.best_variable = pop[0, : self.dim].copy()
        #############################################################
        # Report

        self.report.append(pop[0, self.dim])

        self.output_dict = {"variable": self.best_variable, "function": self.best_function}
        if self.progress_bar == True:
            show = " " * 100
            sys.stdout.write("\r%s" % (show))
        sys.stdout.write("\r The best solution found:\n %s" % (self.best_variable))
        sys.stdout.write("\n\n Objective function:\n %s\n" % (self.best_function))
        sys.stdout.flush()
        re = np.array(self.report)
        if self.convergence_curve == True:
            plt.plot(re)
            plt.xlabel("Iteration")
            plt.ylabel("Objective function")
            plt.title("Genetic Algorithm")
            plt.show()

        if self.stop_mniwi == True:
            sys.stdout.write(
                "\nWarning: GA is terminated due to the" + " maximum number of iterations without improvement was met!"
            )

    ##############################################################################
    ##############################################################################
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

    ###############################################################################

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

    ###############################################################################
    def mutmidle(self, x, p1, p2):
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

    ###############################################################################
    def evaluate(self):
        return self.f(self.temp)

    ###############################################################################
    def sim(self, X):
        self.temp = X.copy()
        obj = None
        try:
            obj = func_timeout(self.funtimeout, self.evaluate)
        except FunctionTimedOut:
            print("given function is not applicable")
        assert obj != None, (
            "After "
            + str(self.funtimeout)
            + " seconds delay "
            + "func_timeout: the given function does not provide any output"
        )
        return obj

    ###############################################################################
    def progress(self, count, total, status=""):
        bar_len = 50
        filled_len = int(round(bar_len * count / float(total)))

        percents = round(100.0 * count / float(total), 1)
        bar = "|" * filled_len + "_" * (bar_len - filled_len)

        sys.stdout.write("\r%s %s%s %s" % (bar, percents, "%", status))
        sys.stdout.flush()

    ###############################################################################


###############################################################################
