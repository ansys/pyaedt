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

import math
import os
import time
import warnings

import numpy as np

from ansys.aedt.core.base import PyAedtBase
from ansys.aedt.core.generic.constants import AEDT_UNITS
from ansys.aedt.core.generic.file_utils import open_file
from ansys.aedt.core.generic.file_utils import write_csv
from ansys.aedt.core.generic.general_methods import pyaedt_function_handler
from ansys.aedt.core.generic.numbers_utils import Quantity
from ansys.aedt.core.generic.settings import settings

try:
    import pandas as pd
except ImportError:
    pd = None
    warnings.warn(
        "The Pandas module is required to run some functionalities of PostProcess.\nInstall with \n\npip install pandas"
    )


class SolutionData(PyAedtBase):
    """Contains information from the :func:`GetSolutionDataPerVariation` method."""

    def __init__(self, aedtdata):
        start = time.time()
        self.units_sweeps = {}
        self._original_data = aedtdata
        self.number_of_variations = len(aedtdata)
        self._enable_pandas_output = True if settings.enable_pandas_output and pd else False
        self._expressions = None
        self._intrinsics = None
        self._nominal_variation = self._original_data[0]
        self.active_expression = self.expressions[0]
        self._sweeps_names = []
        self.update_sweeps()
        self.variations = self._get_variations()
        self._active_variation = self.variations[0]
        self._compute_intrinsics()
        self.active_intrinsic = {}
        for k, v in self.intrinsics.items():
            self.active_intrinsic[k] = v[0]
        if len(self.intrinsics) > 0:
            self._primary_sweep = list(self.intrinsics.keys())[0]
        else:
            self._primary_sweep = self._sweeps_names[0]
        end = time.time() - start
        print(f"Time to initialize solution data:{end}")
        self.init_solutions_data()
        self._ifft = None
        end = time.time() - start
        print(f"Time to initialize solution data:{end}")

    @property
    def active_variation(self):
        return self._active_variation

    @active_variation.setter
    def active_variation(self, value):
        if value in self.variations:
            self._active_variation = value
            self.nominal_variation = self.variations.index(value)
        else:
            settings.logger.warning("Failed to set active variation")

    @property
    def enable_pandas_output(self):
        """Set/Get a flag to use Pandas to export dict and lists.

        This applies to Solution data output.
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
            return True
        return False

    @pyaedt_function_handler()
    def _get_variations(self):
        variations_lists = []
        for data in self._original_data:
            variations = {}
            for v in data.GetDesignVariableNames():
                variations[v] = data.GetDesignVariableValue(v, False)
                if v not in self.units_sweeps:
                    try:
                        self.units_sweeps[v] = data.GetDesignVariableUnits(v)
                    except Exception:
                        self.units_sweeps[v] = None
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

    def _compute_intrinsics(self):
        if not self._intrinsics:
            self._intrinsics = []
            first = True
            for variation in self._original_data:
                new_intrinsic = {}
                intr = [i for i in self._sweeps_names if i not in variation.GetDesignVariableNames()]
                for el in intr:
                    values = np.unique(np.array(variation.GetSweepValues(el, False), dtype=float))
                    new_intrinsic[el] = values
                    if first:
                        try:
                            self.units_sweeps[el] = variation.GetSweepUnits(el)
                        except Exception:
                            self.units_sweeps[el] = None
                first = False
                self._intrinsics.append(new_intrinsic)
        return True

    @property
    def intrinsics(self):
        """Get intrinsics dictionary on active variation."""
        if not self._intrinsics:
            self._compute_intrinsics()
        return self._intrinsics[self.variations.index(self.active_variation)]

    def intrinsics_by_variation(self, variation):
        """Get intrinsics dictionary on active variation."""
        if not self._intrinsics:
            self._compute_intrinsics()
        if isinstance(variation, int):
            return self._intrinsics[variation]
        else:
            return self._intrinsics[self.variations.index(variation)]

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
    def __get_index(self, input_data):
        return tuple([float(i) for i in input_data])

    @pyaedt_function_handler()
    def _full_keys(self, comb, solution, variation):
        values = [np.array(val, dtype=float) for val in self.intrinsics_by_variation(variation).values()]
        grids = np.meshgrid(*values, indexing="ij")
        param_combinations = np.stack(grids, axis=-1).reshape(-1, len(values))  # shape: (N, num_intrinsics)
        # Convert comb dict to NumPy array
        comb_values = np.array([float(comb[k]) for k in comb], dtype=float)

        # Broadcast comb_values to match param_combinations
        full_keys = np.hstack([np.tile(comb_values, (param_combinations.shape[0], 1)), param_combinations])
        combined_array = np.hstack([full_keys, solution.reshape(-1, 1)])
        return combined_array

    @pyaedt_function_handler()
    def _init_solution_data_real(self):
        """Initialize the real part of the solution data."""
        sols_data = {}

        for expression in self.expressions:
            solution_numpy = None
            for idx, (data, comb) in enumerate(zip(self._original_data, self.variations)):
                solution = np.array(data.GetRealDataValues(expression, False), dtype=float)
                solution_numpy_temp = self._full_keys(comb, solution, idx)
                solution_numpy = (
                    np.vstack([solution_numpy, solution_numpy_temp])
                    if solution_numpy is not None
                    else solution_numpy_temp
                )
            sols_data[expression] = solution_numpy
        return sols_data

    @pyaedt_function_handler()
    def _init_solution_data_imag(self):
        """Initialize the imaginary part of the solution data."""
        sols_data = {}

        for expression in self.expressions:
            solution_numpy = None
            for idx, (data, comb) in enumerate(zip(self._original_data, self.variations)):
                if data.IsDataComplex(expression):
                    solution = np.array(data.GetImagDataValues(expression, False), dtype=float)
                else:
                    real_data_length = len(list(data.GetRealDataValues(expression, False)))
                    solution = np.array([0] * real_data_length, dtype=float)
                solution_numpy_temp = self._full_keys(comb, solution, idx)
                solution_numpy = (
                    np.vstack([solution_numpy, solution_numpy_temp])
                    if solution_numpy is not None
                    else solution_numpy_temp
                )
            sols_data[expression] = solution_numpy
        return sols_data

    @pyaedt_function_handler()
    def _init_solution_data_phase(self):
        data_phase = {}
        for expr in self.expressions:
            data_phase[expr] = np.copy(self._solutions_real[expr])
            data_phase[expr][:, -1] = np.arctan2(self._solutions_imag[expr][:, -1], self._solutions_real[expr][:, -1])
        return data_phase

    @pyaedt_function_handler()
    def _init_solution_data_mag(self):
        _solutions_mag = {}
        self.units_data = {}

        for expr in self.expressions:
            _solutions_mag[expr] = np.copy(self._solutions_real[expr])
            self.units_data[expr] = self.nominal_variation.GetDataUnits(expr)
            _solutions_mag[expr][:, -1] = np.sqrt(
                self._solutions_real[expr][:, -1] * self._solutions_real[expr][:, -1]
                + self._solutions_imag[expr][:, -1] * self._solutions_imag[expr][:, -1]
            )
        return _solutions_mag

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

        .. deprecated:: 0.20.0
           Use :func:`get_expression_data` property instead.

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
        np.array
            List of data.
        """
        warnings.warn("Method `data_magnitude` is deprecated. Use :func:`get_expression_data` property instead.")
        return self.get_expression_data(expression, formula="magnitude", convert_to_SI=convert_to_SI)[1]

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
        np.array
           List of the data converted to the SI unit system.

        """
        sol = data
        if data_units in AEDT_UNITS and units in AEDT_UNITS[data_units]:
            sol = data * AEDT_UNITS[data_units][units]
        return sol

    @pyaedt_function_handler()
    def data_db10(self, expression=None, convert_to_SI=False):
        """Retrieve the data in the database for an expression and convert in db10.

        .. deprecated:: 0.20.0
           Use :func:`get_expression_data` property instead.

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
        np.array
            List of the data in the database for the expression.
        """
        warnings.warn("Method `data_db10` is deprecated. Use :func:`get_expression_data` property instead.")
        return self.get_expression_data(expression, formula="db10", convert_to_SI=convert_to_SI)[1]

    @pyaedt_function_handler()
    def data_db20(self, expression=None, convert_to_SI=False):
        """Retrieve the data in the database for an expression and convert in db20.

        .. deprecated:: 0.20.0
           Use :func:`get_expression_data` property instead.

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
        np.array
            List of the data in the database for the expression.
        """
        warnings.warn("Method `data_db20` is deprecated. Use :func:`get_expression_data` property instead.")
        return self.get_expression_data(expression, formula="db20", convert_to_SI=convert_to_SI)[1]

    @pyaedt_function_handler()
    def data_phase(self, expression=None, radians=True):
        """Retrieve the phase part of the data for an expression.

        .. deprecated:: 0.20.0
           Use :func:`get_expression_data` property instead.

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
        np.array
            Phase data for the expression.
        """
        warnings.warn("Method `data_phase` is deprecated. Use :func:`get_expression_data` property instead.")
        return self.get_expression_data(expression, formula="phaserad" if radians else "phase")[1]

    @property
    def primary_sweep_values(self):
        """Retrieve the primary sweep for a given data and primary variable.

        Returns
        -------
        np.array
            List of the primary sweep valid points for the expression.
        """
        return self.variation_values(self.primary_sweep)

    @staticmethod
    def lookup_column_value(array, match_columns, match_values, output_column=-1):
        """
        Filters rows in a NumPy array based on column-value matches,
        and returns the last column value of all matching rows.

        Parameters
        ----------
        array : np.ndarray
            The input array (2D).
        match_columns : list of int
            Column indices to match.
        match_values : list
            Values to match at each column.
        output_column : any
            Value to return if no match is found.

        Returns
        -------
        np.ndarray or default
            Array of last column values for matching rows, or default if none found.
        """
        mask = np.ones(len(array), dtype=bool)
        for col, val in zip(match_columns, match_values):
            mask &= array[:, col] == val

        matched_rows = array[mask]
        if matched_rows.size == 0:
            return
        if isinstance(output_column, int):
            output_column = [output_column]
        return (
            matched_rows[:, output_column] if len(output_column) > 1 else matched_rows[:, output_column[0]]
        )  # last column

    @pyaedt_function_handler()
    def get_expression_data(
        self, expression=None, formula="real", convert_to_SI=False, use_quantity=False, sweeps=None
    ):
        """Retrieve the real part of the data for an expression.

        Parameters
        ----------
        expression : str, None
            Name of the expression. The default is ``None``,
            in which case the active expression is used.
        formula : str, optional
            Data type to be retrieved. Default is ``real``. Options are ``real``, ``imag``, ``mag``, ``magnitude``,
            ``db10``, ``db20``, ``phase``, ``phaserad``.
        convert_to_SI : bool, optional
            Whether to convert the data to the SI unit system.
            The default is ``False``.
        use_quantity : bool, optional
            Whether to output data in ``Quantity`` format or not.
            It impacts on performances as it returns array of objects.
        sweeps : list, str, optional
            List of sweeps to consider for the data retrieval.
            The default is ``None``, which actually takes the primary sweep.

        Returns
        -------
        (np.array, np.array)
            X and Y data for the expression.
        """
        if not expression:
            expression = self.active_expression
        if expression not in self.expressions:
            settings.logger.error(f"Expression '{expression}' not found.")
            return np.array([]), np.array([])
        if formula is None:
            formula = "real"
        if formula.lower() not in [
            "real",
            "re",
            "im",
            "imag",
            "db10",
            "db20",
            "magnitude",
            "mag",
            "phase",
            "phaserad",
            "phasedeg",
        ]:
            return np.array([]), np.array([])

        temp = self._variation_tuple()
        if formula.lower() in ["re", "real"]:
            solution_data = self._solutions_real[expression]
        elif formula.lower() in ["im", "imag"]:
            solution_data = self._solutions_imag[expression]
        elif formula.lower() in ["mag", "magnitude"]:
            solution_data = self._solutions_mag[expression]
        elif formula.lower() in ["phase", "phaserad", "phasedeg"]:
            solution_data = self._solutions_phase[expression]
        else:
            solution_data = self._solutions_mag[expression]
        if sweeps:
            if isinstance(sweeps, str):
                sweeps = [sweeps]
            position = []
            for sweep in sweeps:
                position.append(list(self._sweeps_names).index(sweep))
        else:
            position = [list(self._sweeps_names).index(self.primary_sweep)]

        sol = self.lookup_column_value(
            solution_data,
            [i for i, _ in enumerate(temp) if i not in position],
            [i for i in temp if temp.index(i) not in position],
        )
        x_axis = self.lookup_column_value(
            solution_data,
            [i for i, _ in enumerate(temp) if i not in position],
            [i for i in temp if temp.index(i) not in position],
            position,
        )

        if convert_to_SI and self._quantity(self.units_data[expression]):
            sol = self._convert_list_to_SI(
                sol, self._quantity(self.units_data[expression]), self.units_data[expression]
            )
            x_axis = self._convert_list_to_SI(
                x_axis, self._quantity(self.units_sweeps[self.primary_sweep]), self.units_sweeps[self.primary_sweep]
            )
        if use_quantity:
            vec_func = np.frompyfunc(lambda x: Quantity(x, self.units_data[expression]), 1, 1)
            sol = vec_func(sol)
            vec_func = np.frompyfunc(lambda x: Quantity(x, self.units_sweeps[self.primary_sweep]), 1, 1)
            x_axis = vec_func(x_axis)

        if formula.lower() == "db10":
            sol = 10 * np.log10(sol)
        elif formula.lower() == "db20":
            sol = 20 * np.log10(sol)
        elif formula.lower() == "phaserad":
            sol = sol * np.pi / 180
        return x_axis, sol

    @pyaedt_function_handler()
    def data_real(self, expression=None, convert_to_SI=False):
        """Retrieve the real part of the data for an expression.

        .. deprecated:: 0.20.0
           Use :func:`get_expression_data` property instead.

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
        warnings.warn("Method `data_real` is deprecated. Use :func:`get_expression_data` property instead.")
        return self.get_expression_data(expression, convert_to_SI=convert_to_SI)[1]

    @pyaedt_function_handler()
    def data_imag(self, expression=None, convert_to_SI=False):
        """Retrieve the imaginary part of the data for an expression.

        .. deprecated:: 0.20.0
           Use :func:`get_expression_data` property instead.

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
        warnings.warn("Method `data_imag` is deprecated. Use :func:`get_expression_data` property instead.")
        return self.get_expression_data(expression, formula="imag", convert_to_SI=convert_to_SI)[1]

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
        return np.any(self._solutions_imag[expression][:, -1] != 0)

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
                header.append(f"{el}")
            else:
                header.append(f"{el} [{unit}]")
        # header = [el for el in self._sweeps_names]
        for el in self.expressions:
            data_unit = self._original_data[0].GetDataUnits(el)
            if data_unit:
                data_unit = f" [{data_unit}]"
            if not self.is_real_only(el):
                header.append(el + f" (Real){data_unit}")
                header.append(el + f" (Imag){data_unit}")
            else:
                header.append(el + f"{data_unit}")

        list_full = [header]
        list_full.extend(self._solutions_real[self.active_expression][:, :-1].tolist())
        for el in self.expressions:
            i = 1
            for v in self._solutions_real[el][:, -1]:
                list_full[i].extend([v])
                i += 1
            i = 1
            if not self.is_real_only(el):
                for v in self._solutions_imag[el][:, -1]:
                    list_full[i].extend([v])
                    i += 1

        return write_csv(output, list_full, delimiter=delimiter)

    @pyaedt_function_handler()
    def _get_data_formula(self, curve, formula=None):
        return self.get_expression_data(curve, formula=formula)[1]

    @pyaedt_function_handler()
    def get_report_plotter(self, curves=None, formula=None, to_radians=False, props=None):
        """Get the `ReportPlotter` on the specified curves.

        Parameters
        ----------
        curves : list, str, optional
            Trace names.
        formula : str, optional
            Trace formula. Default is `None` which takes the real part of the trace.
        to_radians : bool, optional
            Whether is data has to be converted to radians or not. Default is ``False``.

        Returns
        -------
        :class:`ansys.aedt.core.visualization.plot.matplotlib.ReportPlotter`
            Report plotter class.
        """
        from ansys.aedt.core.visualization.plot.matplotlib import ReportPlotter

        if not curves:
            curves = self.expressions
        if isinstance(curves, str):
            curves = [curves]
        # if not formula:
        #     formula = "mag"
        if to_radians:
            sw = self.to_radians(self.primary_sweep_values)
        else:
            sw = self.primary_sweep_values
        new = ReportPlotter()
        for curve in curves:
            if props is None:
                props = {"x_label": self.primary_sweep, "y_label": ""}
            active_intr = ",".join([f"{i}={k}" for i, k in self.active_intrinsic.items() if i != self.primary_sweep])
            if formula:
                name = f"{formula}({curve})_{active_intr}"
            else:
                name = f"({curve})_{active_intr}"
            new.add_trace([sw, self._get_data_formula(curve, formula)], name=name, properties=props)
        return new

    @pyaedt_function_handler(math_formula="formula", xlabel="x_label", ylabel="y_label")
    def plot(
        self,
        curves=None,
        formula=None,
        size=(1920, 1440),
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
        :class:`ansys.aedt.core.visualization.plot.matplotlib.ReportPlotter`
            Matplotlib class object.
        """
        props = {"x_label": x_label, "y_label": y_label}
        if "Phi" in self.units_sweeps.keys() and is_polar:
            if self.units_sweeps["Phi"] == "deg":
                to_radians = False
            else:
                to_radians = True
        elif "Theta" in self.units_sweeps.keys() and is_polar:
            if self.units_sweeps["Theta"] == "deg":
                to_radians = False
            else:
                to_radians = True
        elif is_polar:
            to_radians = True
        else:
            to_radians = False
        report_plotter = self.get_report_plotter(curves=curves, formula=formula, to_radians=to_radians, props=props)
        report_plotter.show_legend = show_legend
        report_plotter.title = title
        report_plotter.size = size
        if is_polar:
            return report_plotter.plot_polar(snapshot_path=snapshot_path, show=show)
        else:
            return report_plotter.plot_2d(snapshot_path=snapshot_path, show=show)

    @pyaedt_function_handler(
        xlabel="x_label", ylabel="y_label", math_formula="formula", x_axis="primary_sweep", y_axis="secondary_sweep"
    )
    def plot_3d(
        self,
        curve=None,
        primary_sweep="Theta",
        secondary_sweep="Phi",
        x_label="",
        y_label="",
        title="",
        formula=None,
        size=(1920, 1440),
        snapshot_path=None,
        show=True,
    ):
        """Create a matplotlib 3D figure based on a list of data.

        Parameters
        ----------
        curve : str
            Curve to be plotted. If None, the first curve will be plotted.
        primary_sweep : str, optional
            Primary sweep variable. The default is ``"Theta"``.
        secondary_sweep : str, optional
            Secondary sweep variable. The default is ``"Phi"``.
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
        from ansys.aedt.core.visualization.plot.matplotlib import ReportPlotter

        if self.primary_sweep == "Phi":
            primary_sweep = "Phi"
            secondary_sweep = "Theta"
        elif self.primary_sweep == "Theta":
            primary_sweep = "Theta"
            secondary_sweep = "Phi"
        if not curve:
            curve = self.active_expression
        if not formula:
            if curve[0:2].lower() == "db":
                formula = "re"  # Avoid taking magnitude for db traces.
            else:
                formula = "mag"
        primary_radians = [i * math.pi / 180 for i in self.variation_values(primary_sweep)]
        secondary_values = self.variation_values(secondary_sweep)

        secondary_radians = []
        r = []
        for el in secondary_values:
            if secondary_sweep in self.active_intrinsic:
                self.active_intrinsic[secondary_sweep] = el
            else:
                self.active_variation[secondary_sweep] = el
            secondary_radians.append(el * math.pi / 180)

            r.append(self.get_expression_data(curve, formula=formula)[1])
        min_r = 1e12
        max_r = -1e12
        for el in r:
            min_r = min(min_r, el.min())
            max_r = max(max_r, el.max())

        if min_r < 0:
            r = [i + np.abs(min_r) for i in r]
        primary_grid, secondary_grid = np.meshgrid(primary_radians, secondary_radians)
        r_grid = np.reshape(r, (len(secondary_radians), len(primary_radians)))
        if self.primary_sweep == "Phi":
            phi_grid = primary_grid
            theta_grid = secondary_grid
        else:
            phi_grid = secondary_grid
            theta_grid = primary_grid
        x = r_grid * np.sin(theta_grid) * np.cos(phi_grid)
        y = r_grid * np.sin(theta_grid) * np.sin(phi_grid)
        z = r_grid * np.cos(theta_grid)
        data_plot = [x, y, z]
        if not x_label:
            x_label = "Phi"
        if not y_label:
            y_label = "Theta"
        if not title:
            title = "Polar Far-Field"
        new = ReportPlotter()
        new.size = size
        new.show_legend = False
        new.title = title
        props = {"x_label": x_label, "y_label": y_label}
        new.add_trace(data_plot, 0, props, curve)

        _ = new.plot_3d(trace=0, snapshot_path=snapshot_path, show=show, color_map_limits=[min_r, max_r])
        return new

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
        e_real_x = np.reshape(self._solutions_real[curve_header + "X"][:, -1], (len(freq), len(v), len(u)))
        e_imag_x = np.reshape(self._solutions_imag[curve_header + "X"][:, -1], (len(freq), len(v), len(u)))
        e_real_y = np.reshape(self._solutions_real[curve_header + "Y"][:, -1], (len(freq), len(v), len(u)))
        e_imag_y = np.reshape(self._solutions_imag[curve_header + "Y"][:, -1], (len(freq), len(v), len(u)))
        e_real_z = np.reshape(self._solutions_real[curve_header + "Z"][:, -1], (len(freq), len(v), len(u)))
        e_imag_z = np.reshape(self._solutions_imag[curve_header + "Z"][:, -1], (len(freq), len(v), len(u)))

        temp_e_comp_x = e_real_x.astype("float64") + complex(0, 1) * e_imag_x.astype("float64")
        temp_e_comp_y = e_real_y.astype("float64") + complex(0, 1) * e_imag_y.astype("float64")
        temp_e_comp_z = e_real_z.astype("float64") + complex(0, 1) * e_imag_z.astype("float64")

        e_comp_x = np.zeros((len(freq), len(v), len(u)), dtype=np.complex128)
        e_comp_y = np.zeros((len(freq), len(v), len(u)), dtype=np.complex128)
        e_comp_z = np.zeros((len(freq), len(v), len(u)), dtype=np.complex128)
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
        x_c_list = [float(i) for i in self.variation_values(u_axis)]
        y_c_list = [float(i) for i in self.variation_values(v_axis)]

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
