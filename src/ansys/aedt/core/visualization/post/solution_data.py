# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 - 2024 ANSYS, Inc. and/or its affiliates.
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

import itertools
import math
import os
import warnings

from ansys.aedt.core.generic.constants import AEDT_UNITS
from ansys.aedt.core.generic.constants import db10
from ansys.aedt.core.generic.constants import db20
from ansys.aedt.core.generic.general_methods import open_file
from ansys.aedt.core.generic.general_methods import pyaedt_function_handler
from ansys.aedt.core.generic.general_methods import write_csv
from ansys.aedt.core.generic.settings import settings
from ansys.aedt.core.visualization.plot.matplotlib import plot_2d_chart
from ansys.aedt.core.visualization.plot.matplotlib import plot_3d_chart
from ansys.aedt.core.visualization.plot.matplotlib import plot_polar_chart

np = None
pd = None

try:
    import numpy as np
except ImportError:
    np = None
    warnings.warn(
        "The NumPy module is required to run some functionalities of PostProcess.\n"
        "Install with \n\npip install numpy"
    )
try:
    import pandas as pd
except ImportError:
    pd = None
    warnings.warn(
        "The Pandas module is required to run some functionalities of PostProcess.\n"
        "Install with \n\npip install pandas"
    )


class SolutionData(object):
    """Contains information from the :func:`GetSolutionDataPerVariation` method."""

    def __init__(self, aedtdata):
        self._original_data = aedtdata
        self.number_of_variations = len(aedtdata)
        self._enable_pandas_output = True if settings.enable_pandas_output and pd else False
        self._expressions = None
        self._intrinsics = None
        self._nominal_variation = None
        self._nominal_variation = self._original_data[0]
        self.active_expression = self.expressions[0]
        self._sweeps_names = []
        self.update_sweeps()
        self.variations = self._get_variations()
        self.active_intrinsic = {}
        for k, v in self.intrinsics.items():
            self.active_intrinsic[k] = v[0]
        if len(self.intrinsics) > 0:
            self._primary_sweep = list(self.intrinsics.keys())[0]
        else:
            self._primary_sweep = self._sweeps_names[0]
        self.active_variation = self.variations[0]
        self.units_sweeps = {}
        for intrinsic in self.intrinsics:
            try:
                self.units_sweeps[intrinsic] = self.nominal_variation.GetSweepUnits(intrinsic)
            except Exception:
                self.units_sweeps[intrinsic] = None
        self.init_solutions_data()
        self._ifft = None

    @property
    def enable_pandas_output(self):
        """
        Set/Get a flag to use Pandas to export dict and lists. This applies to Solution data output.
        If ``True`` the property or method will return a pandas object in CPython environment.
        Default is ``False``.

        Returns
        -------
        bool
        """
        return True if self._enable_pandas_output and pd else False

    @enable_pandas_output.setter
    def enable_pandas_output(self, val):
        if val != self._enable_pandas_output and pd:
            self._enable_pandas_output = val
            self.init_solutions_data()

    @pyaedt_function_handler()
    def set_active_variation(self, var_id=0):
        """Set the active variations to one of available variations in self.variations.

        Parameters
        ----------
        var_id : int
            Index of Variations to assign.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.
        """
        if var_id < len(self.variations):
            self.active_variation = self.variations[var_id]
            self.nominal_variation = var_id
            self._expressions = None
            self._intrinsics = None
            return True
        return False

    @pyaedt_function_handler()
    def _get_variations(self):
        variations_lists = []
        for data in self._original_data:
            variations = {}
            for v in data.GetDesignVariableNames():
                variations[v] = data.GetDesignVariableValue(v)
            variations_lists.append(variations)
        return variations_lists

    @pyaedt_function_handler(variation_name="variation")
    def variation_values(self, variation):
        """Get the list of the specific variation available values.

        Parameters
        ----------
        variation : str
            Name of variation to return.

        Returns
        -------
        list
            List of variation values.
        """
        if variation in self.intrinsics:
            return self.intrinsics[variation]
        else:
            vars_vals = []
            for el in self.variations:
                if variation in el and el[variation] not in vars_vals:
                    vars_vals.append(el[variation])
            return vars_vals

    @property
    def intrinsics(self):
        """Get intrinsics dictionary on active variation."""
        if not self._intrinsics:
            self._intrinsics = {}
            intrinsics = [i for i in self._sweeps_names if i not in self.nominal_variation.GetDesignVariableNames()]
            for el in intrinsics:
                values = list(self.nominal_variation.GetSweepValues(el, False))
                self._intrinsics[el] = [i for i in values]
                self._intrinsics[el] = list(dict.fromkeys(self._intrinsics[el]))
        return self._intrinsics

    @property
    def nominal_variation(self):
        """Nominal variation."""
        return self._nominal_variation

    @nominal_variation.setter
    def nominal_variation(self, val):
        if 0 <= val <= self.number_of_variations:
            self._nominal_variation = self._original_data[val]
        else:
            print(str(val) + " not in Variations")

    @property
    def primary_sweep(self):
        """Primary sweep.

        Parameters
        ----------
        ps : float
            Perimeter of the source.
        """
        return self._primary_sweep

    @primary_sweep.setter
    def primary_sweep(self, ps):
        if ps in self._sweeps_names:
            self._primary_sweep = ps

    @property
    def expressions(self):
        """Expressions."""
        if not self._expressions:
            mydata = [i for i in self._nominal_variation.GetDataExpressions()]
            self._expressions = list(dict.fromkeys(mydata))
        return self._expressions

    @pyaedt_function_handler()
    def update_sweeps(self):
        """Update sweeps.

        Returns
        -------
        dict
            Updated sweeps.
        """

        names = list(self.nominal_variation.GetSweepNames())
        for data in self._original_data:
            for v in data.GetDesignVariableNames():
                if v not in self._sweeps_names:
                    self._sweeps_names.append(v)
        self._sweeps_names.extend((reversed(names)))

    @staticmethod
    @pyaedt_function_handler()
    def _quantity(unit):
        """Get the corresponding AEDT units.

        Parameters
        ----------
        unit : str
            The unit to be looked among the available AEDT units.

        Returns
        -------
            str
            The AEDT units.

        """
        for el in AEDT_UNITS:
            keys_units = [i.lower() for i in list(AEDT_UNITS[el].keys())]
            if unit.lower() in keys_units:
                return el
        return None

    @pyaedt_function_handler()
    def init_solutions_data(self):
        """Initialize the database and store info in variables."""
        self._solutions_real = self._init_solution_data_real()
        self._solutions_imag = self._init_solution_data_imag()
        self._solutions_mag = self._init_solution_data_mag()
        self._solutions_phase = self._init_solution_data_phase()

    @pyaedt_function_handler()
    def _init_solution_data_mag(self):
        _solutions_mag = {}
        self.units_data = {}

        for expr in self.expressions:
            _solutions_mag[expr] = {}
            self.units_data[expr] = self.nominal_variation.GetDataUnits(expr)
            if self.enable_pandas_output:
                _solutions_mag[expr] = np.sqrt(self._solutions_real[expr])
            else:
                for i in self._solutions_real[expr]:
                    _solutions_mag[expr][i] = abs(complex(self._solutions_real[expr][i], self._solutions_imag[expr][i]))
        if self.enable_pandas_output:
            return pd.DataFrame.from_dict(_solutions_mag)
        else:
            return _solutions_mag

    @pyaedt_function_handler()
    def _init_solution_data_real(self):
        """ """
        sols_data = {}

        for expression in self.expressions:
            solution_data = {}

            for data, comb in zip(self._original_data, self.variations):
                solution = list(data.GetRealDataValues(expression, False))
                values = []
                for el in list(self.intrinsics.keys()):
                    values.append(list(dict.fromkeys(data.GetSweepValues(el, False))))

                i = 0
                c = [comb[v] for v in list(comb.keys())]
                for t in itertools.product(*values):
                    solution_data[tuple(c + list(t))] = solution[i]
                    i += 1
            sols_data[expression] = solution_data
        if self.enable_pandas_output:
            return pd.DataFrame.from_dict(sols_data)
        else:
            return sols_data

    @pyaedt_function_handler()
    def _init_solution_data_imag(self):
        """ """
        sols_data = {}

        for expression in self.expressions:
            solution_data = {}
            for data, comb in zip(self._original_data, self.variations):
                if data.IsDataComplex(expression):
                    solution = list(data.GetImagDataValues(expression, False))
                else:
                    l = len(list(data.GetRealDataValues(expression, False)))
                    solution = [0] * l
                values = []
                for el in list(self.intrinsics.keys()):
                    values.append(list(dict.fromkeys(data.GetSweepValues(el, False))))
                i = 0
                c = [comb[v] for v in list(comb.keys())]
                for t in itertools.product(*values):
                    solution_data[tuple(c + list(t))] = solution[i]
                    i += 1
            sols_data[expression] = solution_data
        if self.enable_pandas_output:
            return pd.DataFrame.from_dict(sols_data)
        else:
            return sols_data

    @pyaedt_function_handler()
    def _init_solution_data_phase(self):
        data_phase = {}
        for expr in self.expressions:
            data_phase[expr] = {}
            if self.enable_pandas_output:
                data_phase[expr] = np.arctan2(self._solutions_imag[expr], self._solutions_real[expr])
            else:
                for i in self._solutions_real[expr]:
                    data_phase[expr][i] = math.atan2(self._solutions_imag[expr][i], self._solutions_real[expr][i])
        if self.enable_pandas_output:
            return pd.DataFrame.from_dict(data_phase)
        else:
            return data_phase

    @property
    def full_matrix_real_imag(self):
        """Get the full available solution data in Real and Imaginary parts.

        Returns
        -------
        tuple of dicts
            (Real Dict, Imag Dict)
        """
        return self._solutions_real, self._solutions_imag

    @property
    def full_matrix_mag_phase(self):
        """Get the full available solution data magnitude and phase in radians.

        Returns
        -------
        tuple of dicts
            (Mag Dict, Phase Dict).
        """
        return self._solutions_mag, self._solutions_phase

    @staticmethod
    @pyaedt_function_handler()
    def to_degrees(input_list):
        """Convert an input list from radians to degrees.

        Parameters
        ----------
        input_list : list
            List of inputs in radians.

        Returns
        -------
        list
            List of inputs in degrees.

        """
        if isinstance(input_list, (tuple, list)):
            return [i * 360 / (2 * math.pi) for i in input_list]
        else:
            return input_list * 360 / (2 * math.pi)

    @staticmethod
    @pyaedt_function_handler()
    def to_radians(input_list):
        """Convert an input list from degrees to radians.

        Parameters
        ----------
        input_list : list
            List of inputs in degrees.

        Returns
        -------
        type
            List of inputs in radians.
        """
        if isinstance(input_list, (tuple, list)):
            return [i * 2 * math.pi / 360 for i in input_list]
        else:
            return input_list * 2 * math.pi / 360

    @pyaedt_function_handler()
    def _variation_tuple(self):
        temp = []
        for it in self._sweeps_names:
            try:
                temp.append(self.active_variation[it])
            except KeyError:
                temp.append(self.active_intrinsic[it])
        return temp

    @pyaedt_function_handler()
    def data_magnitude(self, expression=None, convert_to_SI=False):
        """Retrieve the data magnitude of an expression.

        Parameters
        ----------
        expression : str, optional
            Name of the expression. The default is ``None``, in which case the
            active expression is used.
        convert_to_SI : bool, optional
            Whether to convert the data to the SI unit system.
            The default is ``False``.

        Returns
        -------
        list
            List of data.
        """
        if not expression:
            expression = self.active_expression
        elif expression not in self.expressions:
            return False
        temp = self._variation_tuple()
        solution_data = self._solutions_mag[expression]
        sol = []
        position = list(self._sweeps_names).index(self.primary_sweep)
        sw = self.variation_values(self.primary_sweep)
        for el in sw:
            temp[position] = el
            try:
                sol.append(solution_data[tuple(temp)])
            except KeyError:
                sol.append(None)
        if convert_to_SI and self._quantity(self.units_data[expression]):
            sol = self._convert_list_to_SI(
                sol, self._quantity(self.units_data[expression]), self.units_data[expression]
            )
        if self.enable_pandas_output:
            return pd.Series(sol)
        return sol

    @staticmethod
    @pyaedt_function_handler(datalist="data", dataunits="data_units")
    def _convert_list_to_SI(data, data_units, units):
        """Convert a data list to the SI unit system.

        Parameters
        ----------
        data : list
           List of data to convert.
        data_units : str
            Data units.
        units : str
            SI units to convert data into.


        Returns
        -------
        list
           List of the data converted to the SI unit system.

        """
        sol = data
        if data_units in AEDT_UNITS and units in AEDT_UNITS[data_units]:
            sol = [i * AEDT_UNITS[data_units][units] for i in data]
        return sol

    @pyaedt_function_handler()
    def data_db10(self, expression=None, convert_to_SI=False):
        """Retrieve the data in the database for an expression and convert in db10.

        Parameters
        ----------
        expression : str, optional
            Name of the expression. The default is ``None``,
            in which case the active expression is used.
        convert_to_SI : bool, optional
            Whether to convert the data to the SI unit system.
            The default is ``False``.

        Returns
        -------
        list
            List of the data in the database for the expression.
        """
        if not expression:
            expression = self.active_expression
        if self.enable_pandas_output:
            return 10 * np.log10(self.data_magnitude(expression, convert_to_SI))
        return [db10(i) for i in self.data_magnitude(expression, convert_to_SI)]

    @pyaedt_function_handler()
    def data_db20(self, expression=None, convert_to_SI=False):
        """Retrieve the data in the database for an expression and convert in db20.

        Parameters
        ----------
        expression : str, optional
            Name of the expression. The default is ``None``,
            in which case the active expression is used.
        convert_to_SI : bool, optional
            Whether to convert the data to the SI unit system.
            The default is ``False``.

        Returns
        -------
        list
            List of the data in the database for the expression.
        """
        if not expression:
            expression = self.active_expression
        if self.enable_pandas_output:
            return 20 * np.log10(self.data_magnitude(expression, convert_to_SI))
        return [db20(i) for i in self.data_magnitude(expression, convert_to_SI)]

    @pyaedt_function_handler()
    def data_phase(self, expression=None, radians=True):
        """Retrieve the phase part of the data for an expression.

        Parameters
        ----------
        expression : str, None
            Name of the expression. The default is ``None``,
            in which case the active expression is used.
        radians : bool, optional
            Whether to convert the data into radians or degree.
            The default is ``True`` for radians.

        Returns
        -------
        list
            Phase data for the expression.
        """
        if not expression:
            expression = self.active_expression
        coefficient = 1
        if not radians:
            coefficient = 180 / math.pi
        if self.enable_pandas_output:
            return coefficient * np.arctan2(self.data_imag(expression), self.data_real(expression))
        return [coefficient * math.atan2(k, i) for i, k in zip(self.data_real(expression), self.data_imag(expression))]

    @property
    def primary_sweep_values(self):
        """Retrieve the primary sweep for a given data and primary variable.

        Returns
        -------
        list
            List of the primary sweep valid points for the expression.
        """
        if self.enable_pandas_output:
            return pd.Series(self.variation_values(self.primary_sweep))
        return self.variation_values(self.primary_sweep)

    @property
    def primary_sweep_variations(self):
        """Retrieve the variations lists for a given primary variable.

        Returns
        -------
        list
            List of the primary sweep valid points for the expression.

        """
        expression = self.active_expression
        temp = self._variation_tuple()

        solution_data = list(self._solutions_real[expression].keys())
        sol = []
        position = list(self._sweeps_names).index(self.primary_sweep)

        for el in self.primary_sweep_values:
            temp[position] = el
            if tuple(temp) in solution_data:
                sol_dict = {}
                i = 0
                for sn in self._sweeps_names:
                    sol_dict[sn] = temp[i]
                    i += 1
                sol.append(sol_dict)
            else:
                sol.append(None)
        if self.enable_pandas_output:
            return pd.Series(sol)
        return sol

    @pyaedt_function_handler()
    def data_real(self, expression=None, convert_to_SI=False):
        """Retrieve the real part of the data for an expression.

        Parameters
        ----------
        expression : str, None
            Name of the expression. The default is ``None``,
            in which case the active expression is used.
        convert_to_SI : bool, optional
            Whether to convert the data to the SI unit system.
            The default is ``False``.

        Returns
        -------
        list
            List of the real data for the expression.
        """
        if not expression:
            expression = self.active_expression
        temp = self._variation_tuple()

        solution_data = self._solutions_real[expression]
        sol = []
        position = list(self._sweeps_names).index(self.primary_sweep)

        for el in self.primary_sweep_values:
            temp[position] = el
            try:
                sol.append(solution_data[tuple(temp)])
            except KeyError:
                sol.append(None)

        if convert_to_SI and self._quantity(self.units_data[expression]):
            sol = self._convert_list_to_SI(
                sol, self._quantity(self.units_data[expression]), self.units_data[expression]
            )
        if self.enable_pandas_output:
            return pd.Series(sol)
        return sol

    @pyaedt_function_handler()
    def data_imag(self, expression=None, convert_to_SI=False):
        """Retrieve the imaginary part of the data for an expression.

        Parameters
        ----------
        expression : str, optional
            Name of the expression. The default is ``None``,
            in which case the active expression is used.
        convert_to_SI : bool, optional
            Whether to convert the data to the SI unit system.
            The default is ``False``.

        Returns
        -------
        list
            List of the imaginary data for the expression.
        """
        if not expression:
            expression = self.active_expression
        temp = self._variation_tuple()

        solution_data = self._solutions_imag[expression]
        sol = []
        position = list(self._sweeps_names).index(self.primary_sweep)
        for el in self.primary_sweep_values:
            temp[position] = el
            try:
                sol.append(solution_data[tuple(temp)])
            except KeyError:
                sol.append(None)
        if convert_to_SI and self._quantity(self.units_data[expression]):
            sol = self._convert_list_to_SI(
                sol, self._quantity(self.units_data[expression]), self.units_data[expression]
            )
        if self.enable_pandas_output:
            return pd.Series(sol)
        return sol

    @pyaedt_function_handler()
    def is_real_only(self, expression=None):
        """Check if the expression has only real values or not.

        Parameters
        ----------
        expression : str, optional
            Name of the expression. The default is ``None``,
            in which case the active expression is used.

        Returns
        -------
        bool
            ``True`` if the Solution Data for specific expression contains only real values.
        """
        if not expression:
            expression = self.active_expression
        if self.enable_pandas_output:
            return True if self._solutions_imag[expression].abs().sum() > 0.0 else False
        for v in list(self._solutions_imag[expression].values()):
            if float(v) != 0.0:
                return False
        return True

    @pyaedt_function_handler()
    def export_data_to_csv(self, output, delimiter=";"):
        """Save to output csv file the Solution Data.

        Parameters
        ----------
        output : str,
            Full path to csv file.
        delimiter : str,
            CSV Delimiter. Default is ``";"``.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.
        """
        header = []
        des_var = self._original_data[0].GetDesignVariableNames()
        sweep_var = self._original_data[0].GetSweepNames()
        for el in self._sweeps_names:
            unit = ""
            if el in des_var:
                unit = self._original_data[0].GetDesignVariableUnits(el)
            elif el in sweep_var:
                unit = self._original_data[0].GetSweepUnits(el)
            if unit == "":
                header.append("{}".format(el))
            else:
                header.append("{} [{}]".format(el, unit))
        # header = [el for el in self._sweeps_names]
        for el in self.expressions:
            data_unit = self._original_data[0].GetDataUnits(el)
            if data_unit:
                data_unit = " [{}]".format(data_unit)
            if not self.is_real_only(el):

                header.append(el + " (Real){}".format(data_unit))
                header.append(el + " (Imag){}".format(data_unit))
            else:
                header.append(el + "{}".format(data_unit))

        list_full = [header]
        for e, v in self._solutions_real[self.active_expression].items():
            list_full.append(list(e))
        for el in self.expressions:
            i = 1
            for e, v in self._solutions_real[el].items():
                list_full[i].extend([v])
                i += 1
            i = 1
            if not self.is_real_only(el):
                for e, v in self._solutions_imag[el].items():
                    list_full[i].extend([v])
                    i += 1

        return write_csv(output, list_full, delimiter=delimiter)

    @pyaedt_function_handler(math_formula="formula", xlabel="x_label", ylabel="y_label")
    def plot(
        self,
        curves=None,
        formula=None,
        size=(2000, 1000),
        show_legend=True,
        x_label="",
        y_label="",
        title="",
        snapshot_path=None,
        is_polar=False,
        show=True,
    ):
        """Create a matplotlib figure based on a list of data.

        Parameters
        ----------
        curves : list
            Curves to be plotted. The default is ``None``, in which case
            the first curve is plotted.
        formula : str , optional
            Mathematical formula to apply to the plot curve. The default is ``None``,
            in which case only real value of the data stored in the solution data is plotted.
            Options are ``"abs"``, ``"db10"``, ``"db20"``, ``"im"``, ``"mag"``, ``"phasedeg"``,
            ``"phaserad"``, and ``"re"``.
        size : tuple, optional
            Image size in pixels (width, height).
        show_legend : bool
            Whether to show the legend. The default is ``True``.
            This parameter is ignored if the number of curves to plot is
            greater than 15.
        x_label : str
            Plot X label.
        y_label : str
            Plot Y label.
        title : str
            Plot title label.
        snapshot_path : str
            Full path to image file if a snapshot is needed.
        is_polar : bool, optional
            Set to `True` if this is a polar plot.
        show : bool, optional
            Whether if show the plot or not. Default is set to `True`.

        Returns
        -------
        :class:`matplotlib.pyplot.Figure`
            Matplotlib figure object.
        """
        if not curves:
            curves = [self.active_expression]
        if isinstance(curves, str):
            curves = [curves]
        data_plot = []
        sweep_name = self.primary_sweep
        if is_polar:
            sw = self.to_radians(self.primary_sweep_values)
        else:
            sw = self.primary_sweep_values
        for curve in curves:
            if not formula:
                data_plot.append([sw, self.data_real(curve), curve])
            elif formula == "re":
                data_plot.append([sw, self.data_real(curve), "{}({})".format(formula, curve)])
            elif formula == "im":
                data_plot.append([sw, self.data_imag(curve), "{}({})".format(formula, curve)])
            elif formula == "db20":
                data_plot.append([sw, self.data_db20(curve), "{}({})".format(formula, curve)])
            elif formula == "db10":
                data_plot.append([sw, self.data_db10(curve), "{}({})".format(formula, curve)])
            elif formula == "mag":
                data_plot.append([sw, self.data_magnitude(curve), "{}({})".format(formula, curve)])
            elif formula == "phasedeg":
                data_plot.append([sw, self.data_phase(curve, False), "{}({})".format(formula, curve)])
            elif formula == "phaserad":
                data_plot.append([sw, self.data_phase(curve, True), "{}({})".format(formula, curve)])
        if not x_label:
            x_label = sweep_name
        if not y_label:
            y_label = formula
        if not title:
            title = "Simulation Results Plot"
        if len(data_plot) > 15:
            show_legend = False
        if is_polar:
            return plot_polar_chart(data_plot, size, show_legend, x_label, y_label, title, snapshot_path, show=show)
        else:
            return plot_2d_chart(data_plot, size, show_legend, x_label, y_label, title, snapshot_path, show=show)

    @pyaedt_function_handler(xlabel="x_label", ylabel="y_label", math_formula="formula")
    def plot_3d(
        self,
        curve=None,
        x_axis="Theta",
        y_axis="Phi",
        x_label="",
        y_label="",
        title="",
        formula=None,
        size=(2000, 1000),
        snapshot_path=None,
        show=True,
    ):
        """Create a matplotlib 3D figure based on a list of data.

        Parameters
        ----------
        curve : str
            Curve to be plotted. If None, the first curve will be plotted.
        x_axis : str, optional
            X-axis sweep. The default is ``"Theta"``.
        y_axis : str, optional
            Y-axis sweep. The default is ``"Phi"``.
        x_label : str
            Plot X label.
        y_label : str
            Plot Y label.
        title : str
            Plot title label.
        formula : str , optional
            Mathematical formula to apply to the plot curve. The default is ``None``.
            Options are `"abs"``, ``"db10"``, ``"db20"``, ``"im"``, ``"mag"``, ``"phasedeg"``,
            ``"phaserad"``, and ``"re"``.
        size : tuple, optional
            Image size in pixels (width, height). The default is ``(2000, 1000)``.
        snapshot_path : str, optional
            Full path to image file if a snapshot is needed.
            The default is ``None``.
        show : bool, optional
            Whether if show the plot or not. Default is set to `True`.

        Returns
        -------
        :class:`matplotlib.figure.Figure`
            Matplotlib figure object.
        """
        if not curve:
            curve = self.active_expression

        if not formula:
            formula = "mag"
        theta = self.variation_values(x_axis)
        y_axis_val = self.variation_values(y_axis)

        phi = []
        r = []
        for el in y_axis_val:
            self.active_variation[y_axis] = el
            phi.append(el * math.pi / 180)

            if formula == "re":
                r.append(self.data_real(curve))
            elif formula == "im":
                r.append(self.data_imag(curve))
            elif formula == "db20":
                r.append(self.data_db20(curve))
            elif formula == "db10":
                r.append(self.data_db10(curve))
            elif formula == "mag":
                r.append(self.data_magnitude(curve))
            elif formula == "phasedeg":
                r.append(self.data_phase(curve, False))
            elif formula == "phaserad":
                r.append(self.data_phase(curve, True))
        active_sweep = self.active_intrinsic[self.primary_sweep]
        position = self.variation_values(self.primary_sweep).index(active_sweep)
        if len(self.variation_values(self.primary_sweep)) > 1:
            new_r = []
            for el in r:
                new_r.append([el[position]])
            r = new_r
        data_plot = [theta, phi, r]
        if not x_label:
            x_label = x_axis
        if not y_label:
            y_label = y_axis
        if not title:
            title = "Simulation Results Plot"
        return plot_3d_chart(data_plot, size, x_label, y_label, title, snapshot_path, show=show)

    @pyaedt_function_handler()
    def ifft(self, curve_header="NearE", u_axis="_u", v_axis="_v", window=False):
        """Create IFFT of given complex data.

        Parameters
        ----------
        curve_header : curve header. Solution data must contain 3 curves with X, Y and Z components of curve header.
        u_axis : str, optional
            U Axis name. Default is Hfss name "_u"
        v_axis : str, optional
            V Axis name. Default is Hfss name "_v"
        window : bool, optional
            Either if Hanning windowing has to be applied.

        Returns
        -------
        List
            IFFT Matrix.
        """
        u = self.variation_values(u_axis)
        v = self.variation_values(v_axis)

        freq = self.variation_values("Freq")
        if self.enable_pandas_output:
            e_real_x = np.reshape(self._solutions_real[curve_header + "X"].copy().values, (len(freq), len(v), len(u)))
            e_imag_x = np.reshape(self._solutions_imag[curve_header + "X"].copy().values, (len(freq), len(v), len(u)))
            e_real_y = np.reshape(self._solutions_real[curve_header + "Y"].copy().values, (len(freq), len(v), len(u)))
            e_imag_y = np.reshape(self._solutions_imag[curve_header + "Y"].copy().values, (len(freq), len(v), len(u)))
            e_real_z = np.reshape(self._solutions_real[curve_header + "Z"].copy().values, (len(freq), len(v), len(u)))
            e_imag_z = np.reshape(self._solutions_imag[curve_header + "Z"].copy().values, (len(freq), len(v), len(u)))
        else:
            vals_e_real_x = [j for j in self._solutions_real[curve_header + "X"].values()]
            vals_e_imag_x = [j for j in self._solutions_imag[curve_header + "X"].values()]
            vals_e_real_y = [j for j in self._solutions_real[curve_header + "Y"].values()]
            vals_e_imag_y = [j for j in self._solutions_imag[curve_header + "Y"].values()]
            vals_e_real_z = [j for j in self._solutions_real[curve_header + "Z"].values()]
            vals_e_imag_z = [j for j in self._solutions_imag[curve_header + "Z"].values()]

            e_real_x = np.reshape(vals_e_real_x, (len(freq), len(v), len(u)))
            e_imag_x = np.reshape(vals_e_imag_x, (len(freq), len(v), len(u)))
            e_real_y = np.reshape(vals_e_real_y, (len(freq), len(v), len(u)))
            e_imag_y = np.reshape(vals_e_imag_y, (len(freq), len(v), len(u)))
            e_real_z = np.reshape(vals_e_real_z, (len(freq), len(v), len(u)))
            e_imag_z = np.reshape(vals_e_imag_z, (len(freq), len(v), len(u)))

        temp_e_comp_x = e_real_x + 1j * e_imag_x  # Here is the complex FD data matrix, ready for transforming
        temp_e_comp_y = e_real_y + 1j * e_imag_y
        temp_e_comp_z = e_real_z + 1j * e_imag_z

        e_comp_x = np.zeros((len(freq), len(v), len(u)), dtype="complex_")
        e_comp_y = np.zeros((len(freq), len(v), len(u)), dtype="complex_")
        e_comp_z = np.zeros((len(freq), len(v), len(u)), dtype="complex_")
        if window:
            timewin = np.hanning(len(freq))

            for row in range(0, len(v)):
                for col in range(0, len(u)):
                    e_comp_x[:, row, col] = np.multiply(temp_e_comp_x[:, row, col], timewin)
                    e_comp_y[:, row, col] = np.multiply(temp_e_comp_y[:, row, col], timewin)
                    e_comp_z[:, row, col] = np.multiply(temp_e_comp_z[:, row, col], timewin)
        else:
            e_comp_x = temp_e_comp_x
            e_comp_y = temp_e_comp_y
            e_comp_z = temp_e_comp_z

        e_time_x = np.fft.ifft(np.fft.fftshift(e_comp_x, 0), len(freq), 0, None)
        e_time_y = np.fft.ifft(np.fft.fftshift(e_comp_y, 0), len(freq), 0, None)
        e_time_z = np.fft.ifft(np.fft.fftshift(e_comp_z, 0), len(freq), 0, None)
        e_time = np.zeros((np.size(freq), np.size(v), np.size(u)))
        for i in range(0, len(freq)):
            e_time[i, :, :] = np.abs(
                np.sqrt(np.square(e_time_x[i, :, :]) + np.square(e_time_y[i, :, :]) + np.square(e_time_z[i, :, :]))
            )
        self._ifft = e_time

        return self._ifft

    @pyaedt_function_handler(csv_dir="csv_path", name_str="csv_file_header")
    def ifft_to_file(
        self,
        u_axis="_u",
        v_axis="_v",
        coord_system_center=None,
        db_val=False,
        num_frames=None,
        csv_path=None,
        csv_file_header="res_",
    ):
        """Save IFFT matrix to a list of CSV files (one per time step).

        Parameters
        ----------
        u_axis : str, optional
            U Axis name. Default is Hfss name "_u"
        v_axis : str, optional
            V Axis name. Default is Hfss name "_v"
        coord_system_center : list, optional
            List of UV GlobalCS Center.
        db_val : bool, optional
            Whether data must be exported into a database. The default is ``False``.
        num_frames : int, optional
            Number of frames to export. The default is ``None``.
        csv_path : str, optional
            Output path. The default is ``None``.
        csv_file_header : str, optional
            CSV file header. The default is ``"res_"``.

        Returns
        -------
        str
            Path to file containing the list of csv files.
        """
        if not coord_system_center:
            coord_system_center = [0, 0, 0]
        t_matrix = self._ifft
        x_c_list = self.variation_values(u_axis)
        y_c_list = self.variation_values(v_axis)

        adj_x = coord_system_center[0]
        adj_y = coord_system_center[1]
        adj_z = coord_system_center[2]
        if num_frames:
            frames = num_frames
        else:
            frames = t_matrix.shape[0]
        csv_list = []
        if os.path.exists(csv_path):
            files = [os.path.join(csv_path, f) for f in os.listdir(csv_path) if csv_file_header in f and ".csv" in f]
            for file in files:
                os.remove(file)
        else:
            os.mkdir(csv_path)

        for frame in range(frames):
            output = os.path.join(csv_path, csv_file_header + str(frame) + ".csv")
            list_full = [["x", "y", "z", "val"]]
            for i, y in enumerate(y_c_list):
                for j, x in enumerate(x_c_list):
                    y_coord = y + adj_y
                    x_coord = x + adj_x
                    z_coord = adj_z
                    if db_val:
                        val = 10.0 * np.log10(np.abs(t_matrix[frame, i, j]))
                    else:
                        val = t_matrix[frame, i, j]
                    row_lst = [x_coord, y_coord, z_coord, val]
                    list_full.append(row_lst)
            write_csv(output, list_full, delimiter=",")
            csv_list.append(output)

        txt_file_name = csv_path + "fft_list.txt"
        textfile = open_file(txt_file_name, "w")

        for element in csv_list:
            textfile.write(element + "\n")
        textfile.close()
        return txt_file_name
