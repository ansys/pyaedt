"""
This module contains these classes: `FieldPlot`, `PostProcessor`, and `SolutionData`.

This module provides all functionalities for creating and editing plots in the 3D tools.

"""
from __future__ import absolute_import  # noreorder

import itertools
import math
import os
import random
import string
import sys
import warnings
from collections import OrderedDict

import pyaedt.modules.report_templates as rt
from pyaedt.generic.constants import AEDT_UNITS
from pyaedt.generic.constants import db10
from pyaedt.generic.constants import db20
from pyaedt.generic.general_methods import _retry_ntimes, is_ironpython
from pyaedt.generic.general_methods import generate_unique_name
from pyaedt.generic.general_methods import pyaedt_function_handler
from pyaedt.generic.general_methods import write_csv
from pyaedt.generic.plot import plot_2d_chart, plot_polar_chart, plot_3d_chart

if not is_ironpython:
    try:
        import numpy as np
    except ImportError:
        warnings.warn(
            "The NumPy module is required to run some functionalities of PostProcess.\n"
            "Install with \n\npip install numpy\n\nRequires CPython."
        )


TEMPLATES_BY_DESIGN = {
    "HFSS": [
        "Modal Solution Data",
        "Terminal Solution Data",
        "EigenMode Parameters",
        "Fields",
        "Far Fields",
        "Emissions",
        "Near Fields",
        "Antenna Parameters",
    ],
    "Maxwell 3D": [
        "Transient",
        "EddyCurrent",
        "Magnetostatic",
        "Electrostatic",
        "DCConduction",
        "ElectroDCConduction",
        "ElectricTransient",
        "Fields",
    ],
    "Maxwell 2D": [
        "Transient",
        "EddyCurrent",
        "Magnetostatic",
        "Electrostatic",
        "ElectricTransient",
        "ElectroDCConduction",
        "Fields",
    ],
    "Icepak": ["Monitor", "Fields"],
    "Circuit Design": ["Standard", "Eye Diagram", "Spectral"],
    "HFSS 3D Layout": ["Standard", "Fields", "Spectral"],
    "Mechanical": ["Standard", "Fields"],
    "Q3D Extractor": ["Matrix", "CG Fields", "DC R/L Fields", "AC R/L Fields"],
    "2D Extractor": ["Matrix", "CG Fields", "RL Fields"],
    "Twin Builder": ["Standard", "Spectral"],
}
TEMPLATES_BY_NAME = {
    "Standard": rt.Standard,
    "Modal Solution Data": rt.Standard,
    "Terminal Solution Data": rt.Standard,
    "Fields": rt.Fields,
    "CG Fields": rt.Fields,
    "DC R/L Fields": rt.Fields,
    "AC R/L Fields": rt.Fields,
    "Matrix": rt.Standard,
    "Monitor": rt.Standard,
    "Far Fields": rt.FarField,
    "Near Fields": rt.NearField,
    "Eye Diagram": rt.EyeDiagram,
    "EigenMode Parameters": rt.Standard,
    "Spectral": rt.Spectral,
}


class Reports(object):
    """Provides the names of default solution types."""

    def __init__(self, post_app, design_type):
        self._post_app = post_app
        self._design_type = design_type
        self._templates = TEMPLATES_BY_DESIGN.get(self._design_type, None)

    @pyaedt_function_handler()
    def standard(self, expressions=None, setup_name=None):
        """Create a Standard or Default Report object.

        Parameters
        ----------
        expressions : str or list
            Expression List.
        setup_name : str, optional
            Setup Name.

        Returns
        -------
        :class:`pyaedt.modules.report_templates.Standard`

        Examples
        --------

        >>> from pyaedt import Circuit
        >>> cir = Circuit(my_project)
        >>> report = cir.post.reports_by_category.standard("dB(S(1,1))", "LNA")
        >>> report.create()
        >>> solutions = report.get_solution_data()
        """
        if not setup_name:
            setup_name = self._post_app._app.nominal_sweep
        if "Standard" in self._templates:
            rep = rt.Standard(self._post_app, "Standard", setup_name)
            rep.expressions = expressions
            return rep
        elif self._post_app._app.design_solutions.report_type:
            rep = rt.Standard(self._post_app, self._post_app._app.design_solutions.report_type, setup_name)
            rep.expressions = expressions
            return rep
        return

    @pyaedt_function_handler()
    def monitor(self, expressions=None, setup_name=None):
        """Create an Icepak Monitor Report object.

        Parameters
        ----------
        expressions : str or list
            Expression List.
        setup_name : str, optional
            Setup Name.

        Returns
        -------
        :class:`pyaedt.modules.report_templates.Standard`

        Examples
        --------

        >>> from pyaedt import Icepak
        >>> ipk = Icepak(my_project)
        >>> report = ipk.post.reports_by_category.monitor(["monitor_surf.Temperature","monitor_point.Temperature"])
        >>> report = report.create()
        """
        if not setup_name:
            setup_name = self._post_app._app.nominal_sweep
        if "Monitor" in self._templates:
            rep = rt.Standard(self._post_app, "Monitor", setup_name)
            rep.expressions = expressions
            return rep
        return

    @pyaedt_function_handler()
    def fields(self, expressions=None, setup_name=None, polyline=None):
        """Create a Field Report object.

        Parameters
        ----------
        expressions : str or list
            Expression List.
        setup_name : str, optional
            Setup Name.

        Returns
        -------
        :class:`pyaedt.modules.report_templates.Fields`

        Examples
        --------

        >>> from pyaedt import Hfss
        >>> app = Hfss(my_project)
        >>> report = app.post.reports_by_category.fields("Mag_E", "Setup : LastAdaptive", "Polyline1")
        >>> report.create()
        >>> solutions = report.get_solution_data()
        """
        if not setup_name:
            setup_name = self._post_app._app.nominal_sweep
        if "Fields" in self._templates:
            rep = rt.Fields(self._post_app, "Fields", setup_name)
            rep.expressions = expressions
            rep.polyline = polyline
            return rep
        return

    @pyaedt_function_handler()
    def cg_fields(self, expressions=None, setup_name=None, polyline=None):
        """Create a CG Field Report object in Q3d and Q2D.

        Parameters
        ----------
        expressions : str or list
            Expression List.
        setup_name : str, optional
            Setup Name.

        Returns
        -------
        :class:`pyaedt.modules.report_templates.Fields`

        Examples
        --------

        >>> from pyaedt import Q3d
        >>> app = Q3d(my_project)
        >>> report = app.post.reports_by_category.cg_fields("SmoothQ", "Setup : LastAdaptive", "Polyline1")
        >>> report.create()
        >>> solutions = report.get_solution_data()
        """
        if not setup_name:
            setup_name = self._post_app._app.nominal_sweep
        if "CG Fields" in self._templates:
            rep = rt.Fields(self._post_app, "CG Fields", setup_name)
            rep.expressions = expressions
            rep.polyline = polyline
            return rep
        return

    @pyaedt_function_handler()
    def dc_fields(self, expressions=None, setup_name=None, polyline=None):
        """Create a DC Field Report object in Q3d.

        Parameters
        ----------
        expressions : str or list
            Expression List.
        setup_name : str, optional
            Setup Name.

        Returns
        -------
        :class:`pyaedt.modules.report_templates.Fields`

        Examples
        --------

        >>> from pyaedt import Q3d
        >>> app = Q3d(my_project)
        >>> report = app.post.reports_by_category.dc_fields("Mag_VolumeJdc", "Setup : LastAdaptive", "Polyline1")
        >>> report.create()
        >>> solutions = report.get_solution_data()
        """
        if not setup_name:
            setup_name = self._post_app._app.nominal_sweep
        if "DC R/L Fields" in self._templates:
            rep = rt.Fields(self._post_app, "DC R/L Fields", setup_name)
            rep.expressions = expressions
            rep.polyline = polyline
            return rep
        return

    @pyaedt_function_handler()
    def rl_fields(self, expressions=None, setup_name=None, polyline=None):
        """Create an AC RL Field Report object in Q3d and Q2D.

        Parameters
        ----------
        expressions : str or list
            Expression List.
        setup_name : str, optional
            Setup Name.

        Returns
        -------
        :class:`pyaedt.modules.report_templates.Fields`

        Examples
        --------

        >>> from pyaedt import Q3d
        >>> app = Q3d(my_project)
        >>> report = app.post.reports_by_category.rl_fields("Mag_SurfaceJac", "Setup : LastAdaptive", "Polyline1")
        >>> report.create()
        >>> solutions = report.get_solution_data()
        """
        if not setup_name:
            setup_name = self._post_app._app.nominal_sweep
        if "AC R/L Fields" in self._templates or "RL Fields" in self._templates:
            if self._post_app._app.design_type == "Q3D Extractor":
                rep = rt.Fields(self._post_app, "AC R/L Fields", setup_name)
            else:
                rep = rt.Fields(self._post_app, "RL Fields", setup_name)
            rep.expressions = expressions
            rep.polyline = polyline
            return rep
        return

    @pyaedt_function_handler()
    def far_field(self, expressions=None, setup_name=None, sphere_name=None):
        """Create a Field Report object.

        Parameters
        ----------
        expressions : str or list
            Expression List.
        setup_name : str, optional
            Setup Name.
        sphere_name : str, optional
            Name of the sphere on which create the far field.

        Returns
        -------
        :class:`pyaedt.modules.report_templates.FarField`

        Examples
        --------

        >>> from pyaedt import Hfss
        >>> app = Hfss(my_project)
        >>> report = app.post.reports_by_category.far_field("GainTotal", "Setup : LastAdaptive", "3D_Sphere")
        >>> report.primary_sweep = "Phi"
        >>> report.create()
        >>> solutions = report.get_solution_data()
        """
        if not setup_name:
            setup_name = self._post_app._app.nominal_sweep
        if "Far Fields" in self._templates:
            rep = rt.FarField(self._post_app, "Far Fields", setup_name)
            rep.expressions = expressions
            rep.far_field_sphere = sphere_name
            return rep
        return

    @pyaedt_function_handler()
    def antenna_parameters(self, expressions=None, setup_name=None, sphere_name=None):
        """Create an Antenna Parameters Report object.

        Parameters
        ----------
        expressions : str or list
            Expression List.
        setup_name : str, optional
            Setup Name.
        sphere_name : str, optional
            Name of the sphere on which compute antenna parameters.

        Returns
        -------
        :class:`pyaedt.modules.report_templates.AntennaParameters`

        Examples
        --------

        >>> from pyaedt import Hfss
        >>> app = Hfss(my_project)
        >>> report = app.post.reports_by_category.antenna_parameters("GainTotal", "Setup : LastAdaptive", "3D_Sphere")
        >>> report.create()
        >>> solutions = report.get_solution_data()
        """
        if not setup_name:
            setup_name = self._post_app._app.nominal_sweep
        if "Antenna Parameters" in self._templates:
            rep = rt.AntennaParameters(self._post_app, "Antenna Parameters", setup_name, sphere_name)
            rep.expressions = expressions
            return rep
        return

    @pyaedt_function_handler()
    def near_field(self, expressions=None, setup_name=None, near_field_name=None):
        """Create a Field Report object.

        Parameters
        ----------
        expressions : str or list
            Expression List.
        setup_name : str, optional
            Setup Name.

        Returns
        -------
        :class:`pyaedt.modules.report_templates.NearField`

        Examples
        --------

        >>> from pyaedt import Hfss
        >>> app = Hfss(my_project)
        >>> report = app.post.reports_by_category.near_field("GainTotal", "Setup : LastAdaptive", "NF_1")
        >>> report.primary_sweep = "Phi"
        >>> report.create()
        >>> solutions = report.get_solution_data()
        """
        if not setup_name:
            setup_name = self._post_app._app.nominal_sweep
        if "Near Fields" in self._templates:
            rep = rt.NearField(self._post_app, "Near Fields", setup_name)
            rep.expressions = expressions
            return rep
        return

    @pyaedt_function_handler()
    def modal_solution(self, expressions=None, setup_name=None):
        """Create a Standard or Default Report object.

        Parameters
        ----------
        expressions : str or list
            Expression List.
        setup_name : str, optional
            Setup Name.

        Returns
        -------
        :class:`pyaedt.modules.report_templates.Standard`

        Examples
        --------

        >>> from pyaedt import Hfss
        >>> app = Hfss(my_project)
        >>> report = app.post.reports_by_category.modal_solution("dB(S(1,1))")
        >>> report.create()
        >>> solutions = report.get_solution_data()
        """
        if not setup_name:
            setup_name = self._post_app._app.nominal_sweep
        if "Modal Solution Data" in self._templates:
            rep = rt.Standard(self._post_app, "Modal Solution Data", setup_name)
            rep.expressions = expressions
            return rep
        return

    @pyaedt_function_handler()
    def terminal_solution(self, expressions=None, setup_name=None):
        """Create a Standard or Default Report object.

        Parameters
        ----------
        expressions : str or list
            Expression List.
        setup_name : str, optional
            Setup Name.

        Returns
        -------
        :class:`pyaedt.modules.report_templates.Standard`

        Examples
        --------

        >>> from pyaedt import Hfss
        >>> app = Hfss(my_project)
        >>> report = app.post.reports_by_category.terminal_solution("dB(S(1,1))")
        >>> report.create()
        >>> solutions = report.get_solution_data()
        """
        if not setup_name:
            setup_name = self._post_app._app.nominal_sweep
        if "Terminal Solution Data" in self._templates:
            rep = rt.Standard(self._post_app, "Terminal Solution Data", setup_name)
            rep.expressions = expressions
            return rep
        return

    @pyaedt_function_handler()
    def eigenmode(self, expressions=None, setup_name=None):
        """Create a Standard or Default Report object.

        Parameters
        ----------
        expressions : str or list
            Expression List.
        setup_name : str, optional
            Setup Name.

        Returns
        -------
        :class:`pyaedt.modules.report_templates.Standard`

        Examples
        --------

        >>> from pyaedt import Hfss
        >>> app = Hfss(my_project)
        >>> report = app.post.reports_by_category.eigenmode("dB(S(1,1))")
        >>> report.create()
        >>> solutions = report.get_solution_data()
        """
        if not setup_name:
            setup_name = self._post_app._app.nominal_sweep
        if "EigenMode Parameters" in self._templates:
            rep = rt.Standard(self._post_app, "EigenMode Parameters", setup_name)
            rep.expressions = expressions
            return rep
        return

    @pyaedt_function_handler()
    def eye_diagram(self, expressions=None, setup_name=None):
        """Create a Standard or Default Report object.

        Parameters
        ----------
        expressions : str or list
            Expression List.
        setup_name : str, optional
            Setup Name.

        Returns
        -------
        :class:`pyaedt.modules.report_templates.Standard`

        Examples
        --------

        >>> from pyaedt import Circuit
        >>> cir= Circuit()
        >>> new_eye = cir.post.reports_by_category.eye_diagram("V(Vout)")
        >>> new_eye.unit_interval = "1e-9s"
        >>> new_eye.time_stop = "100ns"
        >>> new_eye.create()

        """
        if not setup_name:
            setup_name = self._post_app._app.nominal_sweep
        if "Eye Diagram" in self._templates:
            rep = rt.EyeDiagram(self._post_app, "Eye Diagram", setup_name)
            rep.expressions = expressions
            return rep
        return

    @pyaedt_function_handler()
    def spectral(self, expressions=None, setup_name=None):
        """Create a Spectral Report object.

        Parameters
        ----------
        expressions : str or list, optional
            Expression List.
        setup_name : str, optional
            Setup Name.

        Returns
        -------
        :class:`pyaedt.modules.report_templates.Spectrum`

        Examples
        --------

        >>> from pyaedt import Circuit
        >>> cir= Circuit()
        >>> new_eye = cir.post.reports_by_category.spectral("V(Vout)")
        >>> new_eye.create()

        """
        if not setup_name:
            setup_name = self._post_app._app.nominal_sweep
        if "Spectral" in self._templates:
            rep = rt.Spectral(self._post_app, "Spectrum", setup_name)
            rep.expressions = expressions
            return rep
        return


orientation_to_view = {
    "isometric": "iso",
    "top": "XY",
    "bottom": "XY",
    "right": "XZ",
    "left": "XZ",
    "front": "YZ",
    "back": "YZ",
}


@pyaedt_function_handler()
def _convert_dict_to_report_sel(sweeps):
    if isinstance(sweeps, list):
        return sweeps
    sweep_list = []
    for el in sweeps:
        sweep_list.append(el + ":=")
        if type(sweeps[el]) is list:
            sweep_list.append(sweeps[el])
        else:
            sweep_list.append([sweeps[el]])
    return sweep_list


class SolutionData(object):
    """Contains information from the :func:`GetSolutionDataPerVariation` method."""

    def __init__(self, aedtdata):
        self._original_data = aedtdata
        self.number_of_variations = len(aedtdata)

        self._nominal_variation = None
        self._nominal_variation = self._original_data[0]
        self.active_expression = self.expressions[0]
        self._sweeps = None
        self._sweeps_names = []
        self.update_sweeps()
        self.variations = self._get_variations()
        self.intrinsics = self._get_intrinsics()
        self.active_intrinsic = OrderedDict({})
        for k, v in self.intrinsics.items():
            self.active_intrinsic[k] = v[0]
        if self.intrinsics:
            self._primary_sweep = list(self.intrinsics.keys())[0]
        else:
            self._primary_sweep = self._sweeps_names[0]
        self.active_variation = self.variations[0]
        self.units_sweeps = {}
        self._init_solutions_data()
        self._ifft = None

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
        """
        if var_id < len(self.variations):
            self.active_variation = self.variations[var_id]
            return True
        return False

    @pyaedt_function_handler()
    def _get_variations(self):
        variations_lists = []
        for data in self._original_data:
            variations = OrderedDict({})
            for v in data.GetDesignVariableNames():
                variations[v] = data.GetDesignVariableValue(v)
            variations_lists.append(variations)
        return variations_lists

    @pyaedt_function_handler()
    def _get_intrinsics(self):
        _sweeps = OrderedDict({})
        intrinsics = [i for i in self._sweeps_names if i not in self.nominal_variation.GetDesignVariableNames()]
        for el in intrinsics:
            values = list(self.nominal_variation.GetSweepValues(el, False))
            _sweeps[el] = [i for i in values]
            _sweeps[el] = list(OrderedDict.fromkeys(_sweeps[el]))
        return _sweeps

    @property
    def _sweeps_siunits(self):
        """SI units for the sweep."""
        data = {}
        for el in self._sweeps:
            data[el] = self._convert_list_to_SI(
                self._sweeps[el], self._quantity(self.units_sweeps[el]), self.units_sweeps[el]
            )
        return data

    @property
    def nominal_variation(self):
        """Nominal variation."""
        return self._nominal_variation

    @nominal_variation.setter
    def nominal_variation(self, val):
        if 0 <= val <= self.number_of_variations:
            self._nominal_variation = self._original_data[val]
            self._init_solutions_data()
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
        mydata = [i for i in self._nominal_variation.GetDataExpressions()]
        return list(dict.fromkeys(mydata))

    @pyaedt_function_handler()
    def _init_solutions_data(self):
        self._solutions_real = self._solution_data_real()
        self._solutions_imag = self._solution_data_imag()
        self._solutions_mag = {}
        self.units_data = {}
        if len(self._original_data) > 1:
            for data in self._original_data:
                for v in data.GetDesignVariableNames():
                    if v not in self._sweeps_names:
                        self._sweeps_names.append(v)
        for expr in self.expressions:
            self._solutions_mag[expr] = {}
            self.units_data[expr] = self.nominal_variation.GetDataUnits(expr)
            for i in self._solutions_real[expr]:
                self._solutions_mag[expr][i] = abs(
                    complex(self._solutions_real[expr][i], self._solutions_imag[expr][i])
                )

    @pyaedt_function_handler()
    def update_sweeps(self):
        """Update sweeps.

        Returns
        -------
        dict
            Updated sweeps.
        """

        names = list(self.nominal_variation.GetSweepNames())
        self._sweeps = OrderedDict({})

        for el in names:
            values = list(self.nominal_variation.GetSweepValues(el, False))
            self._sweeps[el] = [i for i in values]
            self._sweeps[el] = list(OrderedDict.fromkeys(self._sweeps[el]))
        for data in self._original_data:
            for v in data.GetDesignVariableNames():
                if v not in self._sweeps:
                    self._sweeps[v] = [data.GetDesignVariableValue(v)]
                    self._sweeps_names.append(v)
                else:
                    self._sweeps[v].append(data.GetDesignVariableValue(v))
        for k, v in self._sweeps.items():
            self._sweeps[k] = list(set(v))
            self._sweeps[k].sort()
        self._sweeps_names.extend((reversed(names)))
        return self._sweeps

    @pyaedt_function_handler()
    def _quantity(self, unit):
        """

        Parameters
        ----------
        unit :


        Returns
        -------

        """
        for el in AEDT_UNITS:
            keys_units = [i.lower() for i in list(AEDT_UNITS[el].keys())]
            if unit.lower() in keys_units:
                return el
        return None

    @pyaedt_function_handler()
    def _solution_data_real(self):
        """ """
        sols_data = {}
        for expression in self.expressions:

            solution = []
            for data in self._original_data:
                solution.extend(list(data.GetRealDataValues(expression, False)))
            values = []
            for el in list(self.intrinsics.keys()):
                values.append(self.intrinsics[el])
            solution_Data = {}
            i = 0
            for comb in self.variations:
                c = [comb[v] for v in list(comb.keys())]
                for t in itertools.product(*values):
                    solution_Data[tuple(c + list(t))] = solution[i]
                    i += 1
            sols_data[expression] = solution_Data
        return sols_data

    @pyaedt_function_handler()
    def _solution_data_imag(self):
        """ """
        sols_data = {}
        for expression in self.expressions:

            solution = []
            for data in self._original_data:
                if data.IsDataComplex(expression):
                    solution.extend(list(data.GetImagDataValues(expression, False)))
                else:
                    l = len(list(data.GetRealDataValues(expression, False)))
                    solution.extend([0] * l)
            values = []
            for el in list(self.intrinsics.keys()):
                values.append(self.intrinsics[el])
            solution_Data = {}
            i = 0
            for comb in self.variations:
                c = [comb[v] for v in list(comb.keys())]
                for t in itertools.product(*values):
                    solution_Data[tuple(c + list(t))] = solution[i]
                    i += 1
            sols_data[expression] = solution_Data
        return sols_data

    @pyaedt_function_handler()
    def to_degrees(self, input_list):
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
        return [i * 360 / (2 * math.pi) for i in input_list]

    @pyaedt_function_handler()
    def to_radians(self, input_list):
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
        return [i * 2 * math.pi / 360 for i in input_list]

    @pyaedt_function_handler()
    def _variation_tuple(self):
        temp = []
        for it in self._sweeps_names:
            try:
                temp.append(self.active_variation[it])
            except:
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
        solution_Data = self._solutions_mag[expression]
        sol = []
        position = list(self._sweeps_names).index(self.primary_sweep)
        for el in self._sweeps[self.primary_sweep]:
            temp[position] = el
            try:
                sol.append(solution_Data[tuple(temp)])
            except KeyError:
                sol.append(None)
        if convert_to_SI and self._quantity(self.units_data[expression]):
            sol = self._convert_list_to_SI(
                sol, self._quantity(self.units_data[expression]), self.units_data[expression]
            )
        return sol

    @pyaedt_function_handler()
    def _convert_list_to_SI(self, datalist, dataunits, units):
        """Convert a data list to the SI unit system.

        Parameters
        ----------
        datalist : list
           List of data to convert.
        dataunits :

        units :


        Returns
        -------
        list
           List of the data converted to the SI unit system.

        """
        sol = datalist
        if dataunits in AEDT_UNITS and units in AEDT_UNITS[dataunits]:
            sol = [i * AEDT_UNITS[dataunits][units] for i in datalist]
        return sol

    @pyaedt_function_handler()
    def data_db(self, expression=None, convert_to_SI=False):
        """Retrieve the data in the database for an expression and convert in db10.

        .. deprecated:: 0.4.8
           Use :func:`data_db10` instead.

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

        return [db10(i) for i in self.data_magnitude(expression, convert_to_SI)]

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
        return [coefficient * math.atan(k / i) for i, k in zip(self.data_real(expression), self.data_imag(expression))]

    @property
    def primary_sweep_values(self):
        """Retrieve the primary sweep for a given data and primary variable.

        Returns
        -------
        list
            List of the primary sweep valid points for the expression.

        """
        return self._sweeps[self.primary_sweep]

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

        solution_Data = list(self._solutions_real[expression].keys())
        sol = []
        position = list(self._sweeps_names).index(self.primary_sweep)

        for el in self._sweeps[self.primary_sweep]:
            temp[position] = el
            if tuple(temp) in solution_Data:
                sol_dict = OrderedDict({})
                i = 0
                for l in self._sweeps_names:
                    sol_dict[l] = temp[i]
                    i += 1
                sol.append(sol_dict)
            else:
                sol.append(None)
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

        solution_Data = self._solutions_real[expression]
        sol = []
        position = list(self._sweeps_names).index(self.primary_sweep)

        for el in self._sweeps[self.primary_sweep]:
            temp[position] = el
            try:
                sol.append(solution_Data[tuple(temp)])
            except KeyError:
                sol.append(None)

        if convert_to_SI and self._quantity(self.units_data[expression]):
            sol = self._convert_list_to_SI(
                sol, self._quantity(self.units_data[expression]), self.units_data[expression]
            )
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

        solution_Data = self._solutions_imag[expression]
        sol = []
        position = list(self._sweeps_names).index(self.primary_sweep)
        for el in self._sweeps[self.primary_sweep]:
            temp[position] = el
            try:
                sol.append(solution_Data[tuple(temp)])
            except KeyError:
                sol.append(None)
        if convert_to_SI and self._quantity(self.units_data[expression]):
            sol = self._convert_list_to_SI(
                sol, self._quantity(self.units_data[expression]), self.units_data[expression]
            )
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
        for e, v in self._solutions_imag[expression].items():
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
        """
        header = [el for el in self._sweeps_names]
        for el in self.expressions:
            if not self.is_real_only(el):
                header.append(el + " (Real)")
                header.append(el + " (Imag)")
            else:
                header.append(el)

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

    @pyaedt_function_handler()
    def plot(
        self,
        curves=None,
        math_formula=None,
        size=(2000, 1000),
        show_legend=True,
        xlabel="",
        ylabel="",
        title="",
        snapshot_path=None,
        is_polar=False,
    ):
        """Create a matplotlib plot based on a list of data.

        Parameters
        ----------
        curves : list
            Curves to be plotted. If None, the first curve will be plotted.
        math_formula : str , optional
            Mathematical formula to apply to the plot curve.
            Valid values are `"re"`, `"im"`, `"db20"`, `"db10"`, `"abs"`, `"mag"`, `"phasedeg"`, `"phaserad"`.
        size : tuple, optional
            Image size in pixel (width, height).
        show_legend : bool
            Either to show legend or not.
        xlabel : str
            Plot X label.
        ylabel : str
            Plot Y label.
        title : str
            Plot Title label.
        snapshot_path : str
            Full path to image file if a snapshot is needed.
        is_polar : bool, optional
            Set to `True` if this is a polar plot.

        Returns
        -------
        :class:`matplotlib.plt`
            Matplotlib fig object.
        """
        if is_ironpython:
            return False  # pragma: no cover
        if not curves:
            curves = [self.active_expression]
        if isinstance(curves, str):
            curves = [curves]
        data_plot = []
        sweep_name = self.primary_sweep
        if not math_formula:
            math_formula = "mag"
        if is_polar:
            sw = self.to_radians(self._sweeps[sweep_name])
        else:
            sw = self._sweeps[sweep_name]

        for curve in curves:
            if math_formula == "re":
                data_plot.append([sw, self.data_real(curve), "{}({})".format(math_formula, curve)])
            elif math_formula == "im":
                data_plot.append([sw, self.data_imag(curve), "{}({})".format(math_formula, curve)])
            elif math_formula == "db20":
                data_plot.append([sw, self.data_db20(curve), "{}({})".format(math_formula, curve)])
            elif math_formula == "db10":
                data_plot.append([sw, self.data_db10(curve), "{}({})".format(math_formula, curve)])
            elif math_formula == "mag":
                data_plot.append([sw, self.data_magnitude(curve), "{}({})".format(math_formula, curve)])
            elif math_formula == "phasedeg":
                data_plot.append([sw, self.data_phase(curve, False), "{}({})".format(math_formula, curve)])
            elif math_formula == "phaserad":
                data_plot.append([sw, self.data_phase(curve, True), "{}({})".format(math_formula, curve)])
        if not xlabel:
            xlabel = sweep_name
        if not ylabel:
            ylabel = math_formula
        if not title:
            title = "Simulation Results Plot"
        if is_polar:
            return plot_polar_chart(data_plot, size, show_legend, xlabel, ylabel, title, snapshot_path)
        else:
            return plot_2d_chart(data_plot, size, show_legend, xlabel, ylabel, title, snapshot_path)

    @pyaedt_function_handler()
    def plot_3d(
        self,
        curve=None,
        x_axis="Theta",
        y_axis="Phi",
        xlabel="",
        ylabel="",
        title="",
        math_formula=None,
        size=(2000, 1000),
        snapshot_path=None,
    ):
        """Create a matplotlib 3d plot based on a list of data.

        Parameters
        ----------
        curve : str
            Curve to be plotted. If None, the first curve will be plotted.
        x_axis : str, optional
            X Axis sweep. Default is `"Theta"`.
        y_axis : str, optional
            Y Axis sweep. Default is `"Phi"`.
        math_formula : str , optional
            Mathematical formula to apply to the plot curve.
            Valid values are `"re"`, `"im"`, `"db20"`, `"db10"`, `"abs"`, `"mag"`, `"phasedeg"`, `"phaserad"`.
        size : tuple, optional
            Image size in pixel (width, height).
        snapshot_path : str
            Full path to image file if a snapshot is needed.
        is_polar : bool, optional
            Set to `True` if this is a polar plot.

        Returns
        -------
        :class:`matplotlib.plt`
            Matplotlib fig object.
        """
        if is_ironpython:
            return False  # pragma: no cover
        if not curve:
            curve = self.active_expression

        if not math_formula:
            math_formula = "mag"
        theta = self.to_radians(self._sweeps[x_axis])
        phi = []
        r = []
        for el in self._sweeps[y_axis]:
            self.active_variation[y_axis] = el
            phi.append(el * math.pi / 180)

            if math_formula == "re":
                r.append(self.data_real(curve))
            elif math_formula == "im":
                r.append(self.data_imag(curve))
            elif math_formula == "db20":
                r.append(self.data_db20(curve))
            elif math_formula == "db10":
                r.append(self.data_db10(curve))
            elif math_formula == "mag":
                r.append(self.data_magnitude(curve))
            elif math_formula == "phasedeg":
                r.append(self.data_phase(curve, False))
            elif math_formula == "phaserad":
                r.append(self.data_phase(curve, True))
        data_plot = [theta, phi, r]
        if not xlabel:
            xlabel = x_axis
        if not ylabel:
            ylabel = y_axis
        if not title:
            title = "Simulation Results Plot"
        return plot_3d_chart(data_plot, size, xlabel, ylabel, title, snapshot_path)

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
        if is_ironpython:
            return False
        u = self._sweeps[u_axis]
        if v_axis:
            v = self._sweeps[v_axis]
        freq = self._sweeps["Freq"]
        vals_real_Ex = [j for j in self._solutions_real[curve_header + "X"].values()]
        vals_imag_Ex = [j for j in self._solutions_imag[curve_header + "X"].values()]
        vals_real_Ey = [j for j in self._solutions_real[curve_header + "Y"].values()]
        vals_imag_Ey = [j for j in self._solutions_imag[curve_header + "Y"].values()]
        vals_real_Ez = [j for j in self._solutions_real[curve_header + "Z"].values()]
        vals_imag_Ez = [j for j in self._solutions_imag[curve_header + "Z"].values()]

        E_realx = np.reshape(vals_real_Ex, (len(freq), len(v), len(u)))
        E_imagx = np.reshape(vals_imag_Ex, (len(freq), len(v), len(u)))
        E_realy = np.reshape(vals_real_Ey, (len(freq), len(v), len(u)))
        E_imagy = np.reshape(vals_imag_Ey, (len(freq), len(v), len(u)))
        E_realz = np.reshape(vals_real_Ez, (len(freq), len(v), len(u)))
        E_imagz = np.reshape(vals_imag_Ez, (len(freq), len(v), len(u)))

        Temp_E_compx = E_realx + 1j * E_imagx  # Here is the complex FD data matrix, ready for transforming
        Temp_E_compy = E_realy + 1j * E_imagy
        Temp_E_compz = E_realz + 1j * E_imagz

        E_compx = np.zeros((len(freq), len(v), len(u)), dtype="complex_")
        E_compy = np.zeros((len(freq), len(v), len(u)), dtype="complex_")
        E_compz = np.zeros((len(freq), len(v), len(u)), dtype="complex_")
        if window:
            timewin = np.hanning(len(freq))

            for row in range(0, len(v)):
                for col in range(0, len(u)):
                    E_compx[:, row, col] = np.multiply(Temp_E_compx[:, row, col], timewin)
                    E_compy[:, row, col] = np.multiply(Temp_E_compy[:, row, col], timewin)
                    E_compz[:, row, col] = np.multiply(Temp_E_compz[:, row, col], timewin)
        else:
            E_compx = Temp_E_compx
            E_compy = Temp_E_compy
            E_compz = Temp_E_compz

        E_time_x = np.fft.ifft(np.fft.fftshift(E_compx, 0), len(freq), 0, None)
        E_time_y = np.fft.ifft(np.fft.fftshift(E_compy, 0), len(freq), 0, None)
        E_time_z = np.fft.ifft(np.fft.fftshift(E_compz, 0), len(freq), 0, None)
        E_time = np.zeros((np.size(freq), np.size(v), np.size(u)))
        for i in range(0, len(freq)):
            E_time[i, :, :] = np.abs(
                np.sqrt(np.square(E_time_x[i, :, :]) + np.square(E_time_y[i, :, :]) + np.square(E_time_z[i, :, :]))
            )
        self._ifft = E_time

        return self._ifft

    @pyaedt_function_handler()
    def ifft_to_file(
        self,
        u_axis="_u",
        v_axis="_v",
        coord_system_center=None,
        db_val=False,
        num_frames=None,
        csv_dir=None,
        name_str="res_",
    ):
        """Save IFFT Matrix to a list of csv files (one per time step).

        Parameters
        ----------
        u_axis : str, optional
            U Axis name. Default is Hfss name "_u"
        v_axis : str, optional
            V Axis name. Default is Hfss name "_v"
        coord_system_center : list, optional
            List of UV GlobalCS Center.
        db_val : bool, optional
            Either if data has to be exported in db or not.
        num_frames : int, optional
            Number of frames to export.
        csv_dir : str
            Output path
        name_str : str, optional
            csv file header.

        Returns
        -------
        str
            Path to file containing the list of csv files.
        """
        if not coord_system_center:
            coord_system_center = [0, 0, 0]
        t_matrix = self._ifft
        x_c_list = self._sweeps[u_axis]
        y_c_list = self._sweeps[v_axis]
        adj_x = coord_system_center[0]
        adj_y = coord_system_center[1]
        adj_z = coord_system_center[2]
        if num_frames:
            frames = num_frames
        else:
            frames = t_matrix.shape[0]
        csv_list = []
        if os.path.exists(csv_dir):
            files = [os.path.join(csv_dir, f) for f in os.listdir(csv_dir) if name_str in f and ".csv" in f]
            for file in files:
                os.remove(file)
        else:
            os.mkdir(csv_dir)

        for frame in range(frames):
            output = os.path.join(csv_dir, name_str + str(frame) + ".csv")
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

        txt_file_name = csv_dir + "fft_list.txt"
        textfile = open(txt_file_name, "w")

        for element in csv_list:
            textfile.write(element + "\n")
        textfile.close()
        return txt_file_name


class FieldPlot:
    """Creates and edits field plots.

    Parameters
    ----------
    postprocessor : :class:`pyaedt.modules.PostProcessor.PostProcessor`

    objlist : list
        List of objects.
    solutionName : str
        Name of the solution.
    quantityName : str
        Name of the plot or the name of the object.
    intrinsincList : dict, optional
        Name of the intrinsic dictionary. The default is ``{}``.

    """

    def __init__(
        self,
        postprocessor,
        objlist=[],
        surfacelist=[],
        linelist=[],
        cutplanelist=[],
        solutionName="",
        quantityName="",
        intrinsincList={},
    ):
        self._postprocessor = postprocessor
        self.oField = postprocessor.ofieldsreporter
        self.volume_indexes = objlist
        self.surfaces_indexes = surfacelist
        self.line_indexes = linelist
        self.cutplane_indexes = cutplanelist
        self.solutionName = solutionName
        self.quantityName = quantityName
        self.intrinsincList = intrinsincList
        self.name = "Field_Plot"
        self.plotFolder = "Field_Plot"
        self.Filled = False
        self.IsoVal = "Fringe"
        self.SmoothShade = True
        self.AddGrid = False
        self.MapTransparency = True
        self.Refinement = 0
        self.Transparency = 0
        self.SmoothingLevel = 0
        self.ArrowUniform = True
        self.ArrowSpacing = 0
        self.MinArrowSpacing = 0
        self.MaxArrowSpacing = 0
        self.GridColor = [255, 255, 255]
        self.PlotIsoSurface = True
        self.PointSize = 1
        self.CloudSpacing = 0.5
        self.CloudMinSpacing = -1
        self.CloudMaxSpacing = -1

    @property
    def plotGeomInfo(self):
        """Plot geometry information."""
        id = 0
        if self.volume_indexes:
            id += 1
        if self.surfaces_indexes:
            id += 1
        if self.cutplane_indexes:
            id += 1
        if self.line_indexes:
            id += 1
        info = [id]
        if self.volume_indexes:
            info.append("Volume")
            info.append("ObjList")
            info.append(len(self.volume_indexes))
            for index in self.volume_indexes:
                info.append(str(index))
        if self.surfaces_indexes:
            info.append("Surface")
            info.append("FacesList")
            info.append(len(self.surfaces_indexes))
            for index in self.surfaces_indexes:
                info.append(str(index))
        if self.cutplane_indexes:
            info.append("Surface")
            info.append("CutPlane")
            info.append(len(self.cutplane_indexes))
            for index in self.cutplane_indexes:
                info.append(str(index))
        if self.line_indexes:
            info.append("Line")
            info.append(len(self.line_indexes))
            for index in self.line_indexes:
                info.append(str(index))
        return info

    @property
    def intrinsicVar(self):
        """Intrinsic variable.

        Returns
        -------
        list or dict
            List or dictionary of the variables for the field plot.
        """
        var = ""
        if type(self.intrinsincList) is list:
            l = 0
            while l < len(self.intrinsincList):
                val = self.intrinsincList[l + 1]
                if ":=" in self.intrinsincList[l] and type(self.intrinsincList[l + 1]) is list:
                    val = self.intrinsincList[l + 1][0]
                ll = self.intrinsincList[l].split(":=")
                var += ll[0] + "='" + str(val) + "' "
                l += 2
        else:
            for a in self.intrinsincList:
                var += a + "='" + str(self.intrinsincList[a]) + "' "
        return var

    @property
    def plotsettings(self):
        """Plot settings.

        Returns
        -------
        list
            List of plot settings.
        """
        if self.surfaces_indexes:
            arg = [
                "NAME:PlotOnSurfaceSettings",
                "Filled:=",
                self.Filled,
                "IsoValType:=",
                self.IsoVal,
                "SmoothShade:=",
                self.SmoothShade,
                "AddGrid:=",
                self.AddGrid,
                "MapTransparency:=",
                self.MapTransparency,
                "Refinement:=",
                self.Refinement,
                "Transparency:=",
                self.Transparency,
                "SmoothingLevel:=",
                self.SmoothingLevel,
                [
                    "NAME:Arrow3DSpacingSettings",
                    "ArrowUniform:=",
                    self.ArrowUniform,
                    "ArrowSpacing:=",
                    self.ArrowSpacing,
                    "MinArrowSpacing:=",
                    self.MinArrowSpacing,
                    "MaxArrowSpacing:=",
                    self.MaxArrowSpacing,
                ],
                "GridColor:=",
                self.GridColor,
            ]
        else:
            arg = [
                "NAME:PlotOnVolumeSettings",
                "PlotIsoSurface:=",
                self.PlotIsoSurface,
                "PointSize:=",
                self.PointSize,
                "Refinement:=",
                self.Refinement,
                "CloudSpacing:=",
                self.CloudSpacing,
                "CloudMinSpacing:=",
                self.CloudMinSpacing,
                "CloudMaxSpacing:=",
                self.CloudMaxSpacing,
                [
                    "NAME:Arrow3DSpacingSettings",
                    "ArrowUniform:=",
                    self.ArrowUniform,
                    "ArrowSpacing:=",
                    self.ArrowSpacing,
                    "MinArrowSpacing:=",
                    self.MinArrowSpacing,
                    "MaxArrowSpacing:=",
                    self.MaxArrowSpacing,
                ],
            ]
        return arg

    @property
    def surfacePlotInstruction(self):
        """Surface plot settings.

        Returns
        -------
        list
            List of surface plot settings.

        """
        return [
            "NAME:" + self.name,
            "SolutionName:=",
            self.solutionName,
            "QuantityName:=",
            self.quantityName,
            "PlotFolder:=",
            self.plotFolder,
            "UserSpecifyName:=",
            1,
            "UserSpecifyFolder:=",
            1,
            "StreamlinePlot:=",
            False,
            "AdjacentSidePlot:=",
            False,
            "FullModelPlot:=",
            False,
            "IntrinsicVar:=",
            self.intrinsicVar,
            "PlotGeomInfo:=",
            self.plotGeomInfo,
            "FilterBoxes:=",
            [0],
            self.plotsettings,
            "EnableGaussianSmoothing:=",
            False,
        ]

    @property
    def field_plot_settings(self):
        """Field Plot Settings.

        Returns
        -------
        list
            Field Plot Settings.
        """
        return [
            "NAME:FieldsPlotItemSettings",
            [
                "NAME:PlotOnSurfaceSettings",
                "Filled:=",
                self.Filled,
                "IsoValType:=",
                self.IsoVal,
                "AddGrid:=",
                self.AddGrid,
                "MapTransparency:=",
                self.MapTransparency,
                "Refinement:=",
                self.Refinement,
                "Transparency:=",
                self.Transparency,
                "SmoothingLevel:=",
                self.SmoothingLevel,
                "ShadingType:=",
                self.SmoothShade,
                [
                    "NAME:Arrow3DSpacingSettings",
                    "ArrowUniform:=",
                    self.ArrowUniform,
                    "ArrowSpacing:=",
                    self.ArrowSpacing,
                    "MinArrowSpacing:=",
                    self.MinArrowSpacing,
                    "MaxArrowSpacing:=",
                    self.MaxArrowSpacing,
                ],
                "GridColor:=",
                self.GridColor,
            ],
        ]

    @pyaedt_function_handler()
    def create(self):
        """Create a field plot.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        """

        self.oField.CreateFieldPlot(self.surfacePlotInstruction, "Field")
        return True

    @pyaedt_function_handler()
    def update(self):
        """Update the field plot.

        .. note::
           This method works on any plot created inside PyAEDT.
           For Plot already existing in AEDT Design it may produce incorrect results.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.
        """
        self.oField.ModifyFieldPlot(self.name, self.surfacePlotInstruction)

    @pyaedt_function_handler()
    def update_field_plot_settings(self):
        """Modify the field plot settings.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.
        """
        self.oField.SetFieldPlotSettings(self.name, ["NAME:FieldsPlotItemSettings", self.plotsettings])
        return True

    @pyaedt_function_handler()
    def delete(self):
        """Delete the field plot."""
        self.oField.DeleteFieldPlot([self.name])
        self._postprocessor.field_plots.pop(self.name, None)

    @pyaedt_function_handler()
    def change_plot_scale(self, minimum_value, maximum_value, is_log=False, is_db=False):
        """Change Field Plot Scale.

        Parameters
        ----------
        minimum_value : str, float
            Minimum value of the scale.
        maximum_value : str, float
            Maximum value of the scale.
        is_log : bool, optional
            Set to ``True`` if Log Scale is setup.
        is_db : bool, optional
            Set to ``True`` if dB Scale is setup.

        Returns
        -------
        bool
            ``True`` if successful.

        References
        ----------

        >>> oModule.SetPlotFolderSettings
        """
        args = ["NAME:FieldsPlotSettings", "Real Time mode:=", True]
        args += [
            [
                "NAME:ColorMaPSettings",
                "ColorMapType:=",
                "Spectrum",
                "SpectrumType:=",
                "Rainbow",
                "UniformColor:=",
                [127, 255, 255],
                "RampColor:=",
                [255, 127, 127],
            ]
        ]
        args += [
            [
                "NAME:Scale3DSettings",
                "minvalue:=",
                minimum_value,
                "maxvalue:=",
                maximum_value,
                "log:=",
                not is_log,
                "dB:=",
                is_db,
                "ScaleType:=",
                1,
            ]
        ]
        self.oField.SetPlotFolderSettings(self.plotFolder, args)
        return True

    @pyaedt_function_handler()
    def export_image(self, full_path=None, width=1920, height=1080, orientation="isometric", display_wireframe=True):
        """Export the active plot to an image file.

        .. note::
           There are some limitations on HFSS 3D Layout plots.

        full_path : str, optional
            Path for saving the image file. PNG and GIF formats are supported.
            The default is ``None`` which export file in working_directory.
        width : int, optional
            Plot Width.
        height : int, optional
            Plot height.
        orientation : str, optional
            View of the exported plot. Options are ``isometric``,
            ``top``, ``bottom``, ``right``, ``left``, ``front``,
            ``back``, and any custom orientation.
        display_wireframe : bool, optional
            Set to ``True`` if the objects has to be put in wireframe mode.

        Returns
        -------
        str
            Full path to exported file if successful.

        References
        ----------

        >>> oModule.ExportPlotImageToFile
        >>> oModule.ExportModelImageToFile
        >>> oModule.ExportPlotImageWithViewToFile
        """
        self.oField.UpdateQuantityFieldsPlots(self.plotFolder)
        if not full_path:
            full_path = os.path.join(self._postprocessor._app.working_directory, self.name + ".png")
        status = self._postprocessor.export_field_jpg(
            full_path,
            self.name,
            self.plotFolder,
            orientation=orientation,
            width=width,
            height=height,
            display_wireframe=display_wireframe,
        )
        if status:
            return full_path
        else:
            return False

    @pyaedt_function_handler()
    def export_image_from_aedtplt(
        self, export_path=None, view="isometric", plot_mesh=False, scale_min=None, scale_max=None
    ):
        """Save an image of the active plot using PyVista.

        .. note::
            This method only works if the CPython with PyVista module is installed.

        Parameters
        ----------
        export_path : str, optional
            Path where image will be saved.
            The default is ``None`` which export file in working_directory.
        view : str, optional
            View of the exported plot. Options are ``isometric``,
            ``top``, ``front``, ``left``, and ``all``.
        plot_mesh : bool, optional
            Plot mesh.
        scale_min : float, optional
            Scale output min.
        scale_max : float, optional
            Scale output max.

        Returns
        -------
        str
            Full path to exported file if successful.

        References
        ----------

        >>> oModule.UpdateAllFieldsPlots
        >>> oModule.UpdateQuantityFieldsPlots
        >>> oModule.ExportFieldPlot
        """
        if not export_path:
            export_path = self._postprocessor._app.working_directory
        if sys.version_info.major > 2:
            return self._postprocessor.plot_field_from_fieldplot(
                self.name,
                project_path=export_path,
                meshplot=plot_mesh,
                imageformat="jpg",
                view=view,
                plot_label=self.quantityName,
                show=False,
                scale_min=scale_min,
                scale_max=scale_max,
            )
        else:
            self._postprocessor.logger.info("This method wors only on CPython with PyVista")
            return False


class PostProcessorCommon(object):
    """Manages the main AEDT postprocessing functions.

    This class is inherited in the caller application and is accessible through the post variable( eg. ``hfss.post`` or
    ``q3d.post``).

    .. note::
       Some functionalities are available only when AEDT is running in
       the graphical mode.

    Parameters
    ----------
    app : :class:`pyaedt.application.Analsis3D.FieldAnalysis3D`
        Inherited parent object. The parent object must provide the members
        ``_modeler``, ``_desktop``, ``_odesign``, and ``logger``.

    Examples
    --------
    >>> from pyaedt import Q3d
    >>> q3d = Q3d()
    >>> q3d = q.post.get_solution_data(expression="C(Bar1,Bar1)", domain="Original")
    """

    def __init__(self, app):
        self._app = app
        self.oeditor = self.modeler.oeditor
        self._scratch = self._app.working_directory
        self.plots = self._get_plot_inputs()
        self.reports_by_category = Reports(self, self._app.design_type)

    @pyaedt_function_handler()
    def _get_plot_inputs(self):
        names = self._app.get_oo_name(self.oreportsetup)
        plots = []
        if names:
            for name in names:
                obj = self._app.get_oo_object(self.oreportsetup, name)
                if is_ironpython:
                    report_type = obj.Get_ReportType()
                else:
                    report_type = obj.Get_ReportType
                if report_type in TEMPLATES_BY_NAME:
                    report = TEMPLATES_BY_NAME[report_type]
                else:
                    report = rt.Standard
                plots.append(report(self, report_type, None))
                plots[-1]._plot_name = name
                plots[-1]._is_created = True
                if is_ironpython:
                    plots[-1].report_type = obj.Get_DisplayType()
                else:
                    plots[-1].report_type = obj.Get_DisplayType
        return plots

    @property
    def oreportsetup(self):
        """Report setup.

        Returns
        -------
        :attr:`pyaedt.modules.PostProcessor.PostProcessor.oreportsetup`

        References
        ----------

        >>> oDesign.GetModule("ReportSetup")
        """
        return self._app.oreportsetup

    @property
    def logger(self):
        """Logger."""
        return self._app.logger

    @property
    def _desktop(self):
        """Desktop."""
        return self._app._desktop

    @property
    def _odesign(self):
        """Design."""
        return self._app._odesign

    @property
    def _oproject(self):
        """Project."""
        return self._app._oproject

    @property
    def modeler(self):
        """Modeler."""
        return self._app._modeler

    @property
    def post_solution_type(self):
        """Design solution type.

        Returns
        -------
        type
            Design solution type.
        """
        return self._app.solution_type

    @property
    def all_report_names(self):
        """List of all report names.

        Returns
        -------
        list

        References
        ----------

        >>> oModule.GetAllReportNames()
        """
        return list(self.oreportsetup.GetAllReportNames())

    @pyaedt_function_handler()
    def copy_report_data(self, PlotName):
        """Copy report data as static data.

        Parameters
        ----------
        PlotName : str
            Name of the report.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        References
        ----------

        >>> oModule.CopyReportsData
        >>> oModule.PasteReports
        """
        self.oreportsetup.CopyReportsData([PlotName])
        self.oreportsetup.PasteReports()
        return True

    @pyaedt_function_handler()
    def delete_report(self, PlotName):
        """Delete a field plot report.

        Parameters
        ----------
        PlotName : str
            Name of the field plot report.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        References
        ----------

        >>> oModule.DeleteReports
        """
        self.oreportsetup.DeleteReports([PlotName])
        return True

    @pyaedt_function_handler()
    def rename_report(self, PlotName, newname):
        """Rename a plot.

        Parameters
        ----------
        PlotName : str
            Name of the plot.
        newname : str
            New name of the plot.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        References
        ----------

        >>> oModule.RenameReport
        """
        self.oreportsetup.RenameReport(PlotName, newname)
        return True

    @pyaedt_function_handler()
    def get_report_data(
        self, expression="dB(S(1,1))", setup_sweep_name="", domain="Sweep", families_dict=None, report_input_type=None
    ):
        """Generate report data.
        This method returns the data object and the arrays ``solData`` and
        ``FreqVals``.

        .. deprecated:: 0.4.41
           Use :func:`get_solution_data` method instead.

        Parameters
        ----------
        expression : str or list
            One or more formulas to add to the report. The default is
            ``"dB(S(1,1))"``.
        setup_sweep_name : str, optional
            Name of the setup for computing the report. The
            default is ``""``, in which case the nominal sweep is
            used.
        domain : str or list, optional
            Context type. The options are ``"Sweep"`` or
            ``"Time"``. The default is ``"Sweep".``
        families_dict : dict, optional
            Dictionary of all families including the primary
            sweep. The default is ``{"Freq": ["All"]}``.
        report_input_type :  str
            Type of input data for the report.

        Returns
        -------
        pyaedt.modules.PostProcessor.SolutionData

        References
        ----------

        >>> oModule.GetSolutionDataPerVariation

        Examples
        --------
        Generate a report with the default sweep and default variation.

        >>> hfss = HFSS()
        >>> hfss.post.get_report_data("S(1,1)")

        >>> m3d = Maxwell3D()
        >>> m3d.post.get_report_data("SurfaceLoss")   # Eddy Current examples
        >>> m3d.post.get_report_data("Wind(LoadA,LaodA)")    # TransientAnalsysis

        """
        warnings.warn("`get_report_data` is deprecated. Use `get_solution_data` property instead.", DeprecationWarning)
        if self.post_solution_type in ["HFSS3DLayout", "NexximLNA", "NexximTransient", "TR", "AC", "DC"]:
            if domain == "Sweep":
                did = 3
            else:
                did = 1
            ctxt = [
                "NAME:Context",
                "SimValueContext:=",
                [did, 0, 2, 0, False, False, -1, 1, 0, 1, 1, "", 0, 0, "IDIID", False, "1"],
            ]
        elif isinstance(domain, list):
            ctxt = domain
        else:
            ctxt = ["Domain:=", domain]
        if self.post_solution_type in ["TR", "AC", "DC"]:
            ctxt[2] = ctxt[2][:-3]
            setup_sweep_name = self.post_solution_type
        if not isinstance(expression, list):
            expression = [expression]
        if not setup_sweep_name:
            setup_sweep_name = self._app.nominal_sweep

        if not report_input_type:
            report_input_type = self._app.design_solutions.report_type

        if families_dict is None:
            if domain == "Time":
                families_dict = {"Time": ["All"]}
            else:
                families_dict = {"Freq": ["All"]}

        solution_data = self.get_solution_data_per_variation(
            report_input_type, setup_sweep_name, ctxt, families_dict, expression
        )

        if not solution_data:
            warnings.warn("No Data Available. Check inputs")
            return False
        return solution_data

    @pyaedt_function_handler()
    def create_rectangular_plot(
        self,
        expression="dB(S(1,1))",
        setup_sweep_name="",
        families_dict={"Freq": ["All"]},
        primary_sweep_variable="Freq",
        context=None,
        plotname=None,
        report_category=None,
        plot_type="Rectangular Plot",
    ):
        """Create a 2D rectangular plot in AEDT.

        .. deprecated:: 0.4.41
            Method deprecated. use `create_report` instead.

        Parameters
        ----------
        expression : str or list, optional
            One or more formulas to add to the report. The default is value = ``"dB(S(1,1))"``.
        setup_sweep_name : str, optional
            Setup name with the sweep. The default is ``""``.
        families_dict : dict, optional
            Dictionary of all families including the primary sweep. The default is ``{"Freq": ["All"]}``.
        primary_sweep_variable : str, optional
            Name of the primary sweep. The default is ``"Freq"``.
        context : str, optional
            The default is ``None``.
        plotname : str, optional
            Name of the plot. The default is ``None``.
        report_category : str, optional
            Type of the Report to be created. If `None` default data Report will be used
        plot_type : str, optional
            The format of Data Visualization. Default is ``Rectangular Plot``
        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        References
        ----------

        >>> oModule.CreateReport
        """
        warnings.warn(
            "`create_rectangular_plot` is deprecated. Use `create_report` property instead.", DeprecationWarning
        )

        ctxt = []
        if not setup_sweep_name:
            setup_sweep_name = self._app.nominal_sweep
        if self.post_solution_type in ["HFSS3DLayout", "NexximLNA", "NexximTransient", "TR", "AC", "DC"]:
            if "Freq" == primary_sweep_variable or "Freq" in list(families_dict.keys()):
                did = 3
            else:
                did = 1
            ctxt = [
                "NAME:Context",
                "SimValueContext:=",
                [did, 0, 2, 0, False, False, -1, 1, 0, 1, 1, "", 0, 0, "IDIID", False, "1"],
            ]
        elif context:
            if type(context) is list:
                ctxt = context
            else:
                ctxt = ["Context:=", context]
        if self.post_solution_type in ["TR", "AC", "DC"]:
            ctxt[2] = ctxt[2][:-3]
            setup_sweep_name = self.post_solution_type
        if not isinstance(expression, list):
            expression = [expression]
        if not setup_sweep_name:
            setup_sweep_name = self._app.nominal_sweep
        if not report_category and not self._app.design_solutions.report_type:
            self.logger.info("Solution not supported")
            return False
        if not report_category:
            modal_data = self._app.design_solutions.report_type
        else:
            modal_data = report_category
        if not plotname:
            plotname = generate_unique_name("Plot")
        families_input = []
        families_input.append(primary_sweep_variable + ":=")
        if not primary_sweep_variable in families_dict:
            families_input.append(["All"])
        elif isinstance(families_dict[primary_sweep_variable], list):
            families_input.append(families_dict[primary_sweep_variable])
        else:
            families_input.append([families_dict[primary_sweep_variable]])
        for el in families_dict:
            if el == primary_sweep_variable:
                continue
            families_input.append(el + ":=")
            if isinstance(families_dict[el], list):
                families_input.append(families_dict[el])
            else:
                families_input.append([families_dict[el]])
        self.oreportsetup.CreateReport(
            plotname,
            modal_data,
            plot_type,
            setup_sweep_name,
            ctxt,
            families_input,
            ["X Component:=", primary_sweep_variable, "Y Component:=", expression],
        )
        self.logger.info("Report %s correctly created.", plotname)
        return True

    @pyaedt_function_handler()
    def get_solution_data_per_variation(
        self, soltype="Far Fields", setup_sweep_name="", ctxt=None, sweeps=None, expression=""
    ):
        """Retrieve solution data for each variation.

        Parameters
        ----------
        soltype : str, optional
            Type of the solution. For example, ``"Far Fields"`` or ``"Modal Solution Data"``. The default
            is ``"Far Fields"``.
        setup_sweep_name : str, optional
            Name of the setup for computing the report. The default is ``""``,
            in which case ``"nominal adaptive"`` is used.
        ctxt : list, optional
            List of context variables. The default is ``None``.
        sweeps : dict, optional
            Dictionary of variables and values. The default is ``None``,
            in which case this list is used:
            ``{'Theta': 'All', 'Phi': 'All', 'Freq': 'All'}``.
        expression : str or list, optional
            One or more traces to include. The default is ``""``.

        Returns
        -------
        pyaedt.modules.PostProcessor.SolutionData


        References
        ----------

        >>> oModule.GetSolutionDataPerVariation
        """
        if sweeps is None:
            sweeps = {"Theta": "All", "Phi": "All", "Freq": "All"}
        if not ctxt:
            ctxt = []
        if not isinstance(expression, list):
            expression = [expression]
        if not setup_sweep_name:
            setup_sweep_name = self._app.nominal_adaptive
        sweep_list = _convert_dict_to_report_sel(sweeps)

        data = list(
            self.oreportsetup.GetSolutionDataPerVariation(soltype, setup_sweep_name, ctxt, sweep_list, expression)
        )
        self.logger.info("Solution Data Correctly Loaded.")
        return SolutionData(data)

    @pyaedt_function_handler()
    def steal_focus_oneditor(self):
        """Remove the selection of an object that would prevent the image from exporting correctly.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        References
        ----------

        >>> oDesktop.RestoreWindow
        """
        self._desktop.RestoreWindow()
        param = ["NAME:SphereParameters", "XCenter:=", "0mm", "YCenter:=", "0mm", "ZCenter:=", "0mm", "Radius:=", "1mm"]
        attr = ["NAME:Attributes", "Name:=", "DUMMYSPHERE1", "Flags:=", "NonModel#"]
        self.oeditor.CreateSphere(param, attr)
        self.oeditor.Delete(["NAME:Selections", "Selections:=", "DUMMYSPHERE1"])
        return True

    @pyaedt_function_handler()
    def export_report_to_file(self, output_dir, plot_name, extension, unique_file=False):
        """Export the 2D Plot data to a file.

        This method leaves the data in the plot (as data) as a reference
        for the Plot after the loops.

        Parameters
        ----------
        output_dir : str
            Path to the directory of exported report
        plot_name : str
            Name of the plot to export.
        extension : str
            Extension of export , one of
                * (CSV) .csv
                * (Tab delimited) .tab
                * (Post processor format) .txt
                * (Ensight XY data) .exy
                * (Anosft Plot Data) .dat
                * (Ansoft Report Data Files) .rdat
        unique_file : bool
            If set to True, generates unique file in output_dit

        Returns
        -------
        str
            path of exported file

        References
        ----------

        >>> oModule.ExportReportDataToFile
        >>> oModule.ExportToFile
        """
        npath = os.path.normpath(output_dir)

        if "." not in extension:
            extension = "." + extension

        supported_ext = [".csv", ".tab", ".txt", ".exy", ".dat", ".rdat"]
        if extension not in supported_ext:
            msg = "Extension {} is not supported. Use one of {}".format(extension, ", ".join(supported_ext))
            raise ValueError(msg)

        file_path = os.path.join(npath, plot_name + extension)
        if unique_file:
            while os.path.exists(file_path):
                file_name = generate_unique_name(plot_name)
                file_path = os.path.join(npath, file_name + extension)

        if extension == ".rdat":
            self.oreportsetup.ExportReportDataToFile(plot_name, file_path)
        else:
            self.oreportsetup.ExportToFile(plot_name, file_path)

        return file_path

    @pyaedt_function_handler()
    def export_report_to_csv(self, project_dir, plot_name):
        """Export the 2D Plot data to a CSV file.

        This method leaves the data in the plot (as data) as a reference
        for the Plot after the loops.

        Parameters
        ----------
        project_dir : str
            Path to the project directory. The csv file will be plot_name.csv.
        plot_name : str
            Name of the plot to export.

        Returns
        -------
        str
            path of exported file

        References
        ----------

        >>> oModule.ExportReportDataToFile
        >>> oModule.ExportToFile
        """
        return self.export_report_to_file(project_dir, plot_name, extension=".csv")

    @pyaedt_function_handler()
    def export_report_to_jpg(self, project_dir, plot_name):
        """Export the SParameter plot to a JPG file.

        Parameters
        ----------
        project_dir : str
            Path to the project directory.
        plot_name : str
            Name of the plot to export.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        References
        ----------

        >>> oModule.ExportImageToFile
        """
        # path
        npath = os.path.normpath(project_dir)
        file_name = os.path.join(npath, plot_name + ".jpg")  # name of the image file
        self.oreportsetup.ExportImageToFile(plot_name, file_name, 0, 0)
        return True

    @pyaedt_function_handler()
    def _get_report_inputs(
        self,
        expressions,
        setup_sweep_name=None,
        domain="Sweep",
        variations=None,
        primary_sweep_variable=None,
        secondary_sweep_variable=None,
        report_category=None,
        plot_type="Rectangular Plot",
        context=None,
        subdesign_id=None,
        polyline_points=0,
        plotname=None,
        only_get_method=False,
    ):
        ctxt = []
        if not setup_sweep_name:
            setup_sweep_name = self._app.nominal_sweep
        elif setup_sweep_name not in self._app.existing_analysis_sweeps:
            self.logger.error("Sweep not Available.")
            return False
        families_input = OrderedDict({})
        did = 3
        if domain == "Sweep" and not primary_sweep_variable:
            primary_sweep_variable = "Freq"
        elif not primary_sweep_variable:
            primary_sweep_variable = "Time"
            did = 1
        if not variations or primary_sweep_variable not in variations:
            families_input[primary_sweep_variable] = ["All"]
        elif isinstance(variations[primary_sweep_variable], list):
            families_input[primary_sweep_variable] = variations[primary_sweep_variable]
        else:
            families_input[primary_sweep_variable] = [variations[primary_sweep_variable]]
        if not variations:
            variations = self._app.available_variations.nominal_w_values_dict
        for el in list(variations.keys()):
            if el == primary_sweep_variable:
                continue
            if isinstance(variations[el], list):
                families_input[el] = variations[el]
            else:
                families_input[el] = [variations[el]]
        if only_get_method and domain == "Sweep":
            if "Phi" not in families_input:
                families_input["Phi"] = ["All"]
            if "Theta" not in families_input:
                families_input["Theta"] = ["All"]

        if self.post_solution_type in ["TR", "AC", "DC"]:
            ctxt = [
                "NAME:Context",
                "SimValueContext:=",
                [did, 0, 2, 0, False, False, -1, 1, 0, 1, 1, "", 0, 0],
            ]
            setup_sweep_name = self.post_solution_type
        elif self.post_solution_type in ["HFSS3DLayout"]:
            if context == "Differential Pairs":
                ctxt = [
                    "NAME:Context",
                    "SimValueContext:=",
                    [
                        did,
                        0,
                        2,
                        0,
                        False,
                        False,
                        -1,
                        1,
                        0,
                        1,
                        1,
                        "",
                        0,
                        0,
                        "EnsDiffPairKey",
                        False,
                        "1",
                        "IDIID",
                        False,
                        "1",
                    ],
                ]
            else:
                ctxt = [
                    "NAME:Context",
                    "SimValueContext:=",
                    [did, 0, 2, 0, False, False, -1, 1, 0, 1, 1, "", 0, 0, "IDIID", False, "1"],
                ]
        elif self.post_solution_type in ["NexximLNA", "NexximTransient"]:
            ctxt = ["NAME:Context", "SimValueContext:=", [did, 0, 2, 0, False, False, -1, 1, 0, 1, 1, "", 0, 0]]
            if subdesign_id:
                ctxt_temp = ["NUMLEVELS", False, "1", "SUBDESIGNID", False, str(subdesign_id)]
                for el in ctxt_temp:
                    ctxt[2].append(el)
            if context == "Differential Pairs":
                ctxt_temp = ["USE_DIFF_PAIRS", False, "1"]
                for el in ctxt_temp:
                    ctxt[2].append(el)
        elif context == "Differential Pairs":
            ctxt = ["Diff:=", "Differential Pairs", "Domain:=", domain]
        elif self.post_solution_type in ["Q3D Extractor", "2D Extractor"]:
            if not context:
                ctxt = ["Context:=", "Original"]
            else:
                ctxt = ["Context:=", context]
        elif context:
            ctxt = ["Context:=", context]
            if context in self.modeler.line_names:
                ctxt.append("PointCount:=")
                ctxt.append(polyline_points)

        if not isinstance(expressions, list):
            expressions = [expressions]

        if not report_category and not self._app.design_solutions.report_type:
            self.logger.error("Solution not supported")
            return False
        if not report_category:
            modal_data = self._app.design_solutions.report_type
        else:
            modal_data = report_category
        if not plotname:
            plotname = generate_unique_name("Plot")

        arg = ["X Component:=", primary_sweep_variable, "Y Component:=", expressions]
        if plot_type in ["3D Polar Plot", "3D Spherical Plot"]:
            if not primary_sweep_variable:
                primary_sweep_variable = "Phi"
            if not secondary_sweep_variable:
                secondary_sweep_variable = "Theta"
            arg = [
                "Phi Component:=",
                primary_sweep_variable,
                "Theta Component:=",
                secondary_sweep_variable,
                "Mag Component:=",
                expressions,
            ]
        elif plot_type == "Radiation Pattern":
            if not primary_sweep_variable:
                primary_sweep_variable = "Phi"
            arg = ["Ang Component:=", primary_sweep_variable, "Mag Component:=", expressions]
        elif plot_type in ["Smith Chart", "Polar Plot"]:
            arg = ["Polar Component:=", expressions]
        elif plot_type == "Rectangular Contour Plot":
            arg = [
                "X Component:=",
                primary_sweep_variable,
                "Y Component:=",
                secondary_sweep_variable,
                "Z Component:=",
                expressions,
            ]
        return [plotname, modal_data, plot_type, setup_sweep_name, ctxt, families_input, arg]

    @pyaedt_function_handler()
    def create_report(
        self,
        expressions,
        setup_sweep_name=None,
        domain="Sweep",
        variations=None,
        primary_sweep_variable=None,
        secondary_sweep_variable=None,
        report_category=None,
        plot_type="Rectangular Plot",
        context=None,
        subdesign_id=None,
        polyline_points=1001,
        plotname=None,
    ):
        """Create a report in AEDT. It can be a 2D plot, 3D plot, polar plots or data tables.

        Parameters
        ----------
        expressions : str or list, optional
            One or more formulas to add to the report. Example is value = ``"dB(S(1,1))"``.
        setup_sweep_name : str, optional
            Setup name with the sweep. The default is ``""``.
        domain : str, optional
            Plot Domain. Options are "Sweep" and "Time".
        variations : dict, optional
            Dictionary of all families including the primary sweep. The default is ``{"Freq": ["All"]}``.
        primary_sweep_variable : str, optional
            Name of the primary sweep. The default is ``"Freq"``.
        secondary_sweep_variable : str, optional
            Name of the secondary sweep variable in 3D Plots.
        report_category : str, optional
            Category of the Report to be created. If `None` default data Report will be used.
            The Report Category can be one of the types available for creating a report depend on the simulation setup.
            For example for a Far Field Plot in HFSS the UI shows the report category as "Create Far Fields Report".
            The report category will be in this case "Far Fields".
            Depending on the setup different categories are available.
            If `None` default category will be used (the first item in the Results drop down menu in AEDT).
        plot_type : str, optional
            The format of Data Visualization. Default is ``Rectangular Plot``.
        context : str, optional
            The default is ``None``. It can be `None`, `"Differential Pairs"` or
            Reduce Matrix Name for Q2d/Q3d solution or Infinite Sphere name for Far Fields Plot.
        plotname : str, optional
            Name of the plot. The default is ``None``.
        polyline_points : int, optional,
            Number of points on which create the report for plots on polylines.
        subdesign_id : int, optional
            Specify a subdesign ID to export a Touchstone file of this subdesign. Valid for Circuit Only.
            The default value is ``None``.
        context : str, optional

        Returns
        -------
        :class:`pyaedt.modules.report_templates.Standard`
            ``True`` when successful, ``False`` when failed.


        References
        ----------

        >>> oModule.CreateReport

        Examples
        --------
        >>> from pyaedt import Hfss
        >>> aedtapp = Hfss()
        >>> aedtapp.post.create_report("dB(S(1,1))")

        >>> variations = aedtapp.available_variations.nominal_w_values_dict
        >>> variations["Theta"] = ["All"]
        >>> variations["Phi"] = ["All"]
        >>> variations["Freq"] = ["30GHz"]
        >>> aedtapp.post.create_report(
        ...    "db(GainTotal)",
        ...    aedtapp.nominal_adaptive,
        ...    variations=variations,
        ...    primary_sweep_variable="Phi",
        ...    secondary_sweep_variable="Theta",
        ...    plot_type="3D Polar Plot",
        ...    context="3D",
        ...    report_category="Far Fields",
        ...)

        >>> aedtapp.post.create_report(
        ...    "S(1,1)",
        ...    aedtapp.nominal_sweep,
        ...    variations=variations,
        ...    plot_type="Smith Chart",
        ...)

        >>> from pyaedt import Maxwell2d
        >>> maxwell_2d = Maxwell2d()
        >>> maxwell_2d.post.create_report(
        ...     "InputCurrent(PHA)", domain="Time", primary_sweep_variable="Time", plotname="Winding Plot 1"
        ... )
        """
        if domain == "Spectral":
            report_category = "Spectral"
        elif not report_category and not self._app.design_solutions.report_type:
            self.logger.error("Solution not supported")
            return False
        elif not report_category:
            report_category = self._app.design_solutions.report_type
        if report_category in TEMPLATES_BY_NAME:
            report_class = TEMPLATES_BY_NAME[report_category]
        elif "Fields" in report_category:
            report_class = TEMPLATES_BY_NAME["Fields"]
        else:
            report_class = TEMPLATES_BY_NAME["Standard"]
        if not setup_sweep_name:
            setup_sweep_name = self._app.nominal_sweep
        report = report_class(self, report_category, setup_sweep_name)
        report.expressions = expressions
        report.domain = domain
        report.primary_sweep = primary_sweep_variable
        report.secondary_sweep = secondary_sweep_variable
        if variations:
            report.variations = variations
        report.report_type = plot_type
        report.sub_design_id = subdesign_id
        report.point_number = polyline_points
        if context == "Differential Pairs":
            report.differential_pairs = True
        elif self._app.design_type in ["Q3D Extractor", "2D Extractor"] and context:
            report.matrix = context
        elif report_category == "Far Fields":
            if not context and self._app._field_setups:
                report.far_field_sphere = self._app.field_setups[0].name
            else:
                report.far_field_sphere = context
        elif report_category == "Near Fields":
            report.near_field = context
        elif context:
            if context in self.modeler.line_names:
                report.polyline = context

        result = report.create(plotname)
        if result:
            return report
        return False
        # out = self._get_report_inputs(
        #     expressions=expressions,
        #     setup_sweep_name=setup_sweep_name,
        #     domain=domain,
        #     variations=variations,
        #     primary_sweep_variable=primary_sweep_variable,
        #     secondary_sweep_variable=secondary_sweep_variable,
        #     report_category=report_category,
        #     plot_type=plot_type,
        #     context=context,
        #     subdesign_id=subdesign_id,
        #     polyline_points=polyline_points,
        #     plotname=plotname,
        # )
        # if not out:
        #     return False
        # self.oreportsetup.CreateReport(
        #     out[0],
        #     out[1],
        #     out[2],
        #     out[3],
        #     out[4],
        #     _convert_dict_to_report_sel(out[5]),
        #     out[6],
        # )
        # return True

    @pyaedt_function_handler()
    def get_solution_data(
        self,
        expressions,
        setup_sweep_name=None,
        domain="Sweep",
        variations=None,
        primary_sweep_variable=None,
        report_category=None,
        context=None,
        subdesign_id=None,
        polyline_points=1001,
    ):
        """Get SolutionData of a report in AEDT. It can be a 2D plot, 3D solution data class.

        Parameters
        ----------
        expressions : str or list, optional
            One or more formulas to add to the report. Example is value = ``"dB(S(1,1))"``.
        setup_sweep_name : str, optional
            Setup name with the sweep. The default is ``""``.
        domain : str, optional
            Plot Domain. Options are "Sweep" and "Time".
        variations : dict, optional
            Dictionary of all families including the primary sweep. The default is ``{"Freq": ["All"]}``.
        primary_sweep_variable : str, optional
            Name of the primary sweep. The default is ``"Freq"``.
        report_category : str, optional
            Category of the Report to be created. If `None` default data Report will be used.
            The Report Category can be one of the types available for creating a report depend on the simulation setup.
            For example for a Far Field Plot in HFSS the UI shows the report category as "Create Far Fields Report".
            The report category will be in this case "Far Fields".
            Depending on the setup different categories are available.
            If `None` default category will be used (the first item in the Results drop down menu in AEDT).
        context : str, optional
            The default is ``None``. It can be `None`, `"Differential Pairs"` or
            Reduce Matrix Name for Q2d/Q3d solution or Infinite Sphere name for Far Fields Plot.
        subdesign_id : int, optional
            Specify a subdesign ID to export a Touchstone file of this subdesign. Valid for Circuit Only.
            The default value is ``None``.
        polyline_points : int, optional,
            Number of points on which create the report for plots on polylines.


        Returns
        -------
        :class:`pyaedt.modules.PostProcessor.SolutionData`
            `Solution Data object.


        References
        ----------

        >>> oModule.GetSolutionDataPerVariation

        Examples
        --------
        >>> from pyaedt import Hfss
        >>> aedtapp = Hfss()
        >>> aedtapp.post.create_report("dB(S(1,1))")

        >>> variations = aedtapp.available_variations.nominal_w_values_dict
        >>> variations["Theta"] = ["All"]
        >>> variations["Phi"] = ["All"]
        >>> variations["Freq"] = ["30GHz"]
        >>> data1 = aedtapp.post.get_solution_data(
        ...    "GainTotal",
        ...    aedtapp.nominal_adaptive,
        ...    variations=variations,
        ...    primary_sweep_variable="Phi",
        ...    secondary_sweep_variable="Theta",
        ...    context="3D",
        ...    report_category="Far Fields",
        ...)

        >>> data2 =aedtapp.post.get_solution_data(
        ...    "S(1,1)",
        ...    aedtapp.nominal_sweep,
        ...    variations=variations,
        ...)
        >>> data2.plot()

        >>> from pyaedt import Maxwell2d
        >>> maxwell_2d = Maxwell2d()
        >>> data3 = maxwell_2d.post.get_solution_data(
        ...     "InputCurrent(PHA)", domain="Time", primary_sweep_variable="Time",
        ... )
        >>> data3.plot("InputCurrent(PHA)")

        """
        if domain == "Spectral":
            report_category = "Spectral"
        if not report_category and not self._app.design_solutions.report_type:
            self.logger.error("Solution not supported")
            return False
        elif not report_category:
            report_category = self._app.design_solutions.report_type
        if report_category in TEMPLATES_BY_NAME:
            report_class = TEMPLATES_BY_NAME[report_category]
        elif "Fields" in report_category:
            report_class = TEMPLATES_BY_NAME["Fields"]
        else:
            report_class = TEMPLATES_BY_NAME["Standard"]
        if not setup_sweep_name:
            setup_sweep_name = self._app.nominal_sweep
        report = report_class(self, report_category, setup_sweep_name)
        report.expressions = expressions
        report.domain = domain
        report.primary_sweep = primary_sweep_variable
        if variations:
            report.variations = variations
        report.sub_design_id = subdesign_id
        report.point_number = polyline_points
        if context == "Differential Pairs":
            report.differential_pairs = True
        elif self._app.design_type in ["Q3D Extractor", "2D Extractor"] and context:
            report.matrix = context
        elif report_category == "Far Fields":
            if not context and self._app.field_setups:
                report.far_field_sphere = self._app.field_setups[0].name
            else:
                report.far_field_sphere = context
        elif report_category == "Near Fields":
            report.near_field = context
        elif context:
            if context in self.modeler.line_names:
                report.polyline = context

        return report.get_solution_data()

        # out = self._get_report_inputs(
        #     expressions=expressions,
        #     setup_sweep_name=setup_sweep_name,
        #     domain=domain,
        #     variations=variations,
        #     primary_sweep_variable=primary_sweep_variable,
        #     report_category=report_category,
        #     context=context,
        #     subdesign_id=subdesign_id,
        #     polyline_points=polyline_points,
        #     only_get_method=True,
        # )
        #
        # solution_data = self.get_solution_data_per_variation(out[1], out[3], out[4], out[5], expressions)
        # if primary_sweep_variable:
        #     solution_data.primary_sweep = primary_sweep_variable
        # if not solution_data:
        #     warnings.warn("No Data Available. Check inputs")
        #     return False
        # return solution_data


class PostProcessor(PostProcessorCommon, object):
    """Manages the main AEDT postprocessing functions.

    The inherited `AEDTConfig` class contains all `_desktop`
    hierarchical calls needed for the class inititialization data
    `_desktop` and the design types ``"HFSS"``, ``"Icepak"``, and
    ``"HFSS3DLayout"``.

    .. note::
       Some functionalities are available only when AEDT is running in
       the graphical mode.

    Parameters
    ----------
    app : :class:`pyaedt.application.Analsis3D.FieldAnalysis3D`
        Inherited parent object. The parent object must provide the members
        ``_modeler``, ``_desktop``, ``_odesign``, and ``logger``.

    Examples
    --------
    Basic usage demonstrated with an HFSS, Maxwell, or any other design:

    >>> from pyaedt import Hfss
    >>> aedtapp = Hfss()
    >>> post = aedtapp.post
    """

    def __init__(self, app):
        self._app = app
        self._post_osolution = self._app.osolution
        self.field_plots = self._get_fields_plot()
        PostProcessorCommon.__init__(self, app)

    @property
    def _primitives(self):
        """Primitives.

        Returns
        -------
        pyaedt.modeler.Primitives
            Primitives object.

        """
        return self._app._modeler

    @property
    def model_units(self):
        """Model units.

        Returns
        -------
        str
           Model units, such as ``"mm"``.
        """
        return _retry_ntimes(10, self.oeditor.GetModelUnits)

    @property
    def post_osolution(self):
        """Solution.

        Returns
        -------
        type
            Solution module.
        """
        return self._post_osolution

    @property
    def ofieldsreporter(self):
        """Fields reporter.

        Returns
        -------
        :attr:`pyaedt.modules.PostProcessor.PostProcessor.ofieldsreporter`

        References
        ----------

        >>> oDesign.GetModule("FieldsReporter")
        """
        return self._app.ofieldsreporter

    @property
    def report_types(self):
        """Report types.

        References
        ----------

        >>> oModule.GetAvailableReportTypes
        """
        return list(self.oreportsetup.GetAvailableReportTypes())

    @pyaedt_function_handler()
    def display_types(self, report_type):
        """Retrieve display types for a report type.

        Parameters
        ----------
        report_type : str
            Type of the report.

        Returns
        -------
        :attr:`pyaedt.modules.PostProcessor.PostProcessor.report_types`

        References
        ----------

        >>> oModule.GetAvailableDisplayTypes
        """
        return self.oreportsetup.GetAvailableDisplayTypes(report_type)

    @pyaedt_function_handler()
    def _get_base_name(self, setup):
        setups_data = self._app.design_properties["FieldsReporter"]["FieldsPlotManagerID"]
        base_name = ""
        if "SimDataExtractors" in self._app.design_properties["SolutionManager"]:
            sim_data = self._app.design_properties["SolutionManager"]["SimDataExtractors"]
        else:
            sim_data = self._app.design_properties["SolutionManager"]
        if "SimSetup" in sim_data:
            if isinstance(sim_data["SimSetup"], list):
                for solution in sim_data["SimSetup"]:
                    base_name = solution["Name"]
                    for sol in solution["Solution"]:
                        if sol["ID"] == setups_data[setup]["SolutionId"]:
                            base_name += " : " + sol["Name"]
                            return base_name
            else:
                base_name = sim_data["SimSetup"]["Name"]
                if isinstance(sim_data["SimSetup"]["Solution"], list):
                    for sol in sim_data["SimSetup"]["Solution"]:
                        if sol["ID"] == setups_data[setup]["SolutionId"]:
                            base_name += " : " + sol["Name"]
                            return base_name
                else:
                    sol = sim_data["SimSetup"]["Solution"]
                    if sol["ID"] == setups_data[setup]["SolutionId"]:
                        base_name += " : " + sol["Name"]
                        return base_name

        return ""

    @pyaedt_function_handler()
    def _get_intrinsic(self, setup):
        setups_data = self._app.design_properties["FieldsReporter"]["FieldsPlotManagerID"]
        intrinsics = [i.split("=") for i in setups_data[setup]["IntrinsicVar"].split(" ")]
        intr_dict = {}
        if intrinsics:
            for intr in intrinsics:
                if isinstance(intr, list) and len(intr) == 2:
                    intr_dict[intr[0]] = intr[1].replace("\\", "").replace("'", "")
        return intr_dict

    @pyaedt_function_handler()
    def _get_volume_objects(self, list_objs):
        if self._app.solution_type not in ["HFSS3DLayout", "HFSS 3D Layout Design"]:
            obj_list = []
            editor = self._app._odesign.SetActiveEditor("3D Modeler")
            for obj in list_objs:
                obj_list.append(editor.GetObjectNameByID(int(obj)))
        if obj_list:
            return obj_list
        else:
            return list_objs

    @pyaedt_function_handler()
    def _get_surface_objects(self, list_objs):
        faces = [int(i) for i in list_objs]
        if self._app.solution_type not in ["HFSS3DLayout", "HFSS 3D Layout Design"]:
            planes = self._get_cs_plane_ids()
            objs = []
            for face in faces:
                if face in list(planes.keys()):
                    objs.append(planes[face])
            if objs:
                return "CutPlane", objs
        return "FacesList", faces

    @pyaedt_function_handler()
    def _get_cs_plane_ids(self):
        name2refid = {-4: "Global:XY", -3: "Global:YZ", -2: "Global:XZ"}
        if self._app.design_properties and "ModelSetup" in self._app.design_properties:
            cs = self._app.design_properties["ModelSetup"]["GeometryCore"]["GeometryOperations"]["CoordinateSystems"]
            for ds in cs:
                try:
                    if isinstance(cs[ds], (OrderedDict, dict)):
                        name = cs[ds]["Attributes"]["Name"]
                        cs_id = cs[ds]["XYPlaneID"]
                        name2refid[cs_id] = name + ":XY"
                        name2refid[cs_id + 1] = name + ":YZ"
                        name2refid[cs_id + 2] = name + ":XZ"
                    elif type(cs[ds]) is list:
                        for el in cs[ds]:
                            cs_id = el["XYPlaneID"]
                            name = el["Attributes"]["Name"]
                            name2refid[cs_id] = name + ":XY"
                            name2refid[cs_id + 1] = name + ":YZ"
                            name2refid[cs_id + 2] = name + ":XZ"
                except:
                    pass
        return name2refid

    @pyaedt_function_handler()
    def _get_fields_plot(self):
        plots = {}
        if (
            self._app.design_properties
            and "FieldsReporter" in self._app.design_properties
            and "FieldsPlotManagerID" in self._app.design_properties["FieldsReporter"]
        ):
            setups_data = self._app.design_properties["FieldsReporter"]["FieldsPlotManagerID"]
            for setup in setups_data:
                try:
                    if isinstance(setups_data[setup], (OrderedDict, dict)) and "PlotDefinition" in setup:
                        plot_name = setups_data[setup]["PlotName"]
                        plots[plot_name] = FieldPlot(self)
                        plots[plot_name].solutionName = self._get_base_name(setup)
                        plots[plot_name].quantityName = self.ofieldsreporter.GetFieldPlotQuantityName(
                            setups_data[setup]["PlotName"]
                        )
                        plots[plot_name].intrinsincList = self._get_intrinsic(setup)
                        list_objs = setups_data[setup]["FieldPlotGeometry"][1:]
                        while list_objs:
                            id = list_objs[0]
                            num_objects = list_objs[2]
                            if id == 64:
                                plots[plot_name].volume_indexes = self._get_volume_objects(
                                    list_objs[3 : num_objects + 3]
                                )
                            elif id == 128:
                                out, faces = self._get_surface_objects(list_objs[3 : num_objects + 3])
                                if out == "CutPlane":
                                    plots[plot_name].cutplane_indexes = faces
                                else:
                                    plots[plot_name].surfaces_indexes = faces
                            elif id == 256:
                                plots[plot_name].line_indexes = self._get_volume_objects(list_objs[3 : num_objects + 3])
                            list_objs = list_objs[num_objects + 3 :]
                        plots[plot_name].name = setups_data[setup]["PlotName"]
                        plots[plot_name].plotFolder = setups_data[setup]["PlotFolder"]
                        surf_setts = setups_data[setup]["PlotOnSurfaceSettings"]
                        plots[plot_name].Filled = surf_setts["Filled"]
                        plots[plot_name].IsoVal = surf_setts["IsoValType"]
                        plots[plot_name].AddGrid = surf_setts["AddGrid"]
                        plots[plot_name].MapTransparency = surf_setts["MapTransparency"]
                        plots[plot_name].Refinement = surf_setts["Refinement"]
                        plots[plot_name].Transparency = surf_setts["Transparency"]
                        plots[plot_name].SmoothingLevel = surf_setts["SmoothingLevel"]
                        arrow_setts = surf_setts["Arrow3DSpacingSettings"]
                        plots[plot_name].ArrowUniform = arrow_setts["ArrowUniform"]
                        plots[plot_name].ArrowSpacing = arrow_setts["ArrowSpacing"]
                        plots[plot_name].MinArrowSpacing = arrow_setts["MinArrowSpacing"]
                        plots[plot_name].MaxArrowSpacing = arrow_setts["MaxArrowSpacing"]
                        plots[plot_name].GridColor = surf_setts["GridColor"]
                except:
                    pass
        return plots

    # TODO: define a fields calculator module and make robust !!
    @pyaedt_function_handler()
    def volumetric_loss(self, object_name):
        """Use the field calculator to create a variable for volumetric losses.

        Parameters
        ----------
        object_name : str
            Name of the object to compute volumetric losses on.

        Returns
        -------
        str
            Name of the variable created.

        References
        ----------

        >>> oModule.EnterQty
        >>> oModule.EnterVol
        >>> oModule.CalcOp
        >>> oModule.AddNamedExpression
        """
        oModule = self.ofieldsreporter
        oModule.EnterQty("OhmicLoss")
        oModule.EnterVol(object_name)
        oModule.CalcOp("Integrate")
        name = "P_{}".format(object_name)  # Need to check for uniqueness !
        oModule.AddNamedExpression(name, "Fields")
        return name

    @pyaedt_function_handler()
    def change_field_property(self, plotname, propertyname, propertyval):
        """Modify a field plot property.

        Parameters
        ----------
        plotname : str
            Name of the field plot.
        propertyname : str
            Name of the property.
        propertyval :
            Value for the property.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        References
        ----------

        >>> oDesign.ChangeProperty
        """
        self._odesign.ChangeProperty(
            [
                "NAME:AllTabs",
                [
                    "NAME:FieldsPostProcessorTab",
                    ["NAME:PropServers", "FieldsReporter:" + plotname],
                    ["NAME:ChangedProps", ["NAME:" + propertyname, "Value:=", propertyval]],
                ],
            ]
        )

    @pyaedt_function_handler()
    def get_scalar_field_value(
        self,
        quantity_name,
        scalar_function="Maximum",
        solution=None,
        variation_dict=None,
        isvector=False,
        intrinsics=None,
        phase=None,
    ):
        """Use the field calculator to Compute Scalar of a Field.

        Parameters
        ----------
        quantity_name : str
            Name of the quantity to export. For example, ``"Temp"``.
        solution : str, optional
            Name of the solution in the format ``"solution : sweep"``. The default is ``None``.
        variation_dict : dict, optional
            Dictionary of all variation variables with their values.
            The default is ``None``.
        isvector : bool, optional
            Whether the quantity is a vector. The  default is ``False``.
        intrinsics : str, optional
            This parameter is mandatory for a frequency field
            calculation. The default is ``None``.
        phase : str, optional
            Field phase. The default is ``None``.

        Returns
        -------
        float
            ``True`` when successful, ``False`` when failed.

        References
        ----------

        >>> oModule.EnterQty
        >>> oModule.CopyNamedExprToStack
        >>> oModule.CalcOp
        >>> oModule.EnterQty
        >>> oModule.EnterVol
        >>> oModule.CalculatorWrite
        """
        self.logger.info("Exporting {} field. Be patient".format(quantity_name))
        if not solution:
            solution = self._app.existing_analysis_sweeps[0]
        self.ofieldsreporter.CalcStack("clear")
        if isvector:
            try:
                self.ofieldsreporter.EnterQty(quantity_name)
            except:
                self.ofieldsreporter.CopyNamedExprToStack(quantity_name)
            self.ofieldsreporter.CalcOp("Smooth")
            self.ofieldsreporter.EnterScalar(0)
            self.ofieldsreporter.CalcOp("AtPhase")
            self.ofieldsreporter.CalcOp("Mag")
        else:
            try:
                self.ofieldsreporter.EnterQty(quantity_name)
            except:
                self.logger.info("Quantity {} not present. Trying to get it from Stack".format(quantity_name))
                self.ofieldsreporter.CopyNamedExprToStack(quantity_name)
        obj_list = "AllObjects"
        if scalar_function:
            self.ofieldsreporter.EnterVol(obj_list)
            self.ofieldsreporter.CalcOp(scalar_function)
        if not variation_dict:
            variation_dict = self._app.available_variations.nominal_w_values
        if intrinsics:
            if "Transient" in solution:
                variation_dict.append("Time:=")
                variation_dict.append(intrinsics)
            else:
                variation_dict.append("Freq:=")
                variation_dict.append(intrinsics)
                variation_dict.append("Phase:=")
                if phase:
                    variation_dict.append(phase)
                else:
                    variation_dict.append("0deg")
        file_name = os.path.join(self._app.working_directory, generate_unique_name("temp_fld") + ".fld")
        self.ofieldsreporter.CalculatorWrite(file_name, ["Solution:=", solution], variation_dict)
        value = None
        if os.path.exists(file_name):
            with open(file_name, "r") as f:
                lines = f.readlines()
                lines = [line.strip() for line in lines]
                value = lines[-1]
            os.remove(file_name)
        self.ofieldsreporter.CalcStack("clear")
        return float(value)

    @pyaedt_function_handler()
    def export_field_file_on_grid(
        self,
        quantity_name,
        solution=None,
        variation_dict=None,
        filename=None,
        gridtype="Cartesian",
        grid_center=[0, 0, 0],
        grid_start=[0, 0, 0],
        grid_stop=[0, 0, 0],
        grid_step=[0, 0, 0],
        isvector=False,
        intrinsics=None,
        phase=None,
    ):
        """Use the field calculator to create a field file on a grid based on a solution and variation.

        Parameters
        ----------
        quantity_name : str
            Name of the quantity to export. For example, ``"Temp"``.
        solution : str, optional
            Name of the solution in the format ``"solution : sweep"``. The default is ``None``.
        variation_dict : dict, optional
            Dictionary of all variation variables with their values.
            The default is ``None``.
        filename : str, optional
            Full path and name to save the file to.
            The default is ``None`` which export file in working_directory.
        gridtype : str, optional
            Type of the grid to export. The default is ``"Cartesian"``.
        grid_center : list, optional
            The ``[x, y, z]`` coordinates for the center of the grid.
            The default is ``[0, 0, 0]``. This parameter is disabled if ``gridtype=
            "Cartesian"``.
        grid_start : list, optional
            The ``[x, y, z]`` coordinates for the starting point of the grid.
            The default is ``[0, 0, 0]``.
        grid_stop : list, optional
            The ``[x, y, z]`` coordinates for the stopping point of the grid.
            The default is ``[0, 0, 0]``.
        grid_step : list, optional
            The ``[x, y, z]`` coordinates for the step size of the grid.
            The default is ``[0, 0, 0]``.
        isvector : bool, optional
            Whether the quantity is a vector. The  default is ``False``.
        intrinsics : str, optional
            This parameter is mandatory for a frequency field
            calculation. The default is ``None``.
        phase : str, optional
            Field phase. The default is ``None``.

        Returns
        -------
        str
            Field file path when succeeded.

        References
        ----------

        >>> oModule.EnterQty
        >>> oModule.CopyNamedExprToStack
        >>> oModule.CalcOp
        >>> oModule.EnterQty
        >>> oModule.EnterVol
        >>> oModule.ExportOnGrid
        """
        self.logger.info("Exporting %s field. Be patient", quantity_name)
        if not solution:
            solution = self._app.existing_analysis_sweeps[0]
        if not filename:
            filename = os.path.join(
                self._app.working_directory, "{}_{}.fld".format(quantity_name, solution.replace(" : ", "_"))
            )
        elif os.path.isdir(filename):
            filename = os.path.join(filename, "{}_{}.fld".format(quantity_name, solution.replace(" : ", "_")))
        self.ofieldsreporter.CalcStack("clear")
        try:
            self.ofieldsreporter.EnterQty(quantity_name)
        except:
            self.ofieldsreporter.CopyNamedExprToStack(quantity_name)
        if isvector:
            self.ofieldsreporter.CalcOp("Smooth")
            if phase:
                self.ofieldsreporter.EnterScalar(0)
                self.ofieldsreporter.CalcOp("AtPhase")
                self.ofieldsreporter.CalcOp("Mag")
        units = self.modeler.model_units
        ang_units = "deg"
        if gridtype == "Cartesian":
            grid_center = ["0mm", "0mm", "0mm"]
            grid_start_wu = [str(i) + units for i in grid_start]
            grid_stop_wu = [str(i) + units for i in grid_stop]
            grid_step_wu = [str(i) + units for i in grid_step]
        elif gridtype == "Cylindrical":
            grid_center = [str(i) + units for i in grid_center]
            grid_start_wu = [str(grid_start[0]) + units, str(grid_start[1]) + ang_units, str(grid_start[2]) + units]
            grid_stop_wu = [str(grid_stop[0]) + units, str(grid_stop[1]) + ang_units, str(grid_stop[2]) + units]
            grid_step_wu = [str(grid_step[0]) + units, str(grid_step[1]) + ang_units, str(grid_step[2]) + units]
        elif gridtype == "Spherical":
            grid_center = [str(i) + units for i in grid_center]
            grid_start_wu = [str(grid_start[0]) + units, str(grid_start[1]) + ang_units, str(grid_start[2]) + ang_units]
            grid_stop_wu = [str(grid_stop[0]) + units, str(grid_stop[1]) + ang_units, str(grid_stop[2]) + ang_units]
            grid_step_wu = [str(grid_step[0]) + units, str(grid_step[1]) + ang_units, str(grid_step[2]) + ang_units]
        else:
            self.logger.error("Error in the type of the grid.")
            return False
        if not variation_dict:
            variation_dict = self._app.available_variations.nominal_w_values
        if intrinsics:
            if "Transient" in solution:
                variation_dict.append("Time:=")
                variation_dict.append(intrinsics)
            else:
                variation_dict.append("Freq:=")
                variation_dict.append(intrinsics)
                variation_dict.append("Phase:=")
                if phase:
                    variation_dict.append(phase)
                else:
                    variation_dict.append("0deg")

        self.ofieldsreporter.ExportOnGrid(
            filename,
            grid_start_wu,
            grid_stop_wu,
            grid_step_wu,
            solution,
            variation_dict,
            True,
            gridtype,
            grid_center,
            False,
        )
        if os.path.exists(filename):
            return filename
        return False  # pragma: no cover

    @pyaedt_function_handler()
    def export_field_file(
        self,
        quantity_name,
        solution=None,
        variation_dict=None,
        filename=None,
        obj_list="AllObjects",
        obj_type="Vol",
        intrinsics=None,
        phase=None,
        sample_points_file=None,
        sample_points_lists=None,
        export_with_sample_points=True,
    ):
        """Use the field calculator to create a field file based on a solution and variation.

        Parameters
        ----------
        quantity_name :
            Name of the quantity to export. For example, ``"Temp"``.
        solution : str, optional
            Name of the solution in the format ``"solution: sweep"``.
            The default is ``None``.
        variation_dict : dict, optional
            Dictionary of all variation variables with their values.
            The default is ``None``.
        filename : str, optional
            Full path and name to save the file to.
            The default is ``None`` which export file in working_directory.
        obj_list : str, optional
            List of objects to export. The default is ``"AllObjects"``.
        obj_type : str, optional
            Type of objects to export. Options are ``"Vol"`` for volume and
            ``"Surf"`` for surface. The default is ``"Vol"``.
        intrinsics : str, optional
            This parameter is mandatory for a frequency or transient field
            calculation. The default is ``None``.
        phase : str, optional
            Field phase. The default is ``None``.
        sample_points_file : str, optional
            Name of the file with sample points. The default is ``None``.
        sample_points_lists : list, optional
            List of the sample points. The default is ``None``.
        export_with_sample_points : bool, optional
            Whether to include the sample points in the file to export.
            The default is ``True``.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        References
        ----------

        >>> oModule.EnterQty
        >>> oModule.CopyNamedExprToStack
        >>> oModule.CalcOp
        >>> oModule.EnterQty
        >>> oModule.EnterVol
        >>> oModule.CalculatorWrite
        >>> oModule.ExportToFile
        """
        self.logger.info("Exporting %s field. Be patient", quantity_name)
        if not solution:
            solution = self._app.existing_analysis_sweeps[0]
        if not filename:
            appendix = ""
            ext = ".fld"
            filename = os.path.join(self._app.working_directory, solution.replace(" : ", "_") + appendix + ext)
        else:
            filename = filename.replace("//", "/").replace("\\", "/")
        self.ofieldsreporter.CalcStack("clear")
        try:
            self.ofieldsreporter.EnterQty(quantity_name)
        except:
            self.ofieldsreporter.CopyNamedExprToStack(quantity_name)
        if not variation_dict:
            if not sample_points_file and not sample_points_lists:
                if obj_type == "Vol":
                    self.ofieldsreporter.EnterVol(obj_list)
                elif obj_type == "Surf":
                    self.ofieldsreporter.EnterSurf(obj_list)
                else:
                    self.logger.error("No correct choice.")
                    return False
                self.ofieldsreporter.CalcOp("Value")
                variation_dict = self._app.available_variations.nominal_w_values
            else:
                variations = self._app.available_variations.nominal_w_values_dict
                variation_dict = []
                for el, value in variations.items():
                    variation_dict.append(el + ":=")
                    variation_dict.append(value)
        if intrinsics:
            if "Transient" in solution:
                variation_dict.append("Time:=")
                variation_dict.append(intrinsics)
            else:
                variation_dict.append("Freq:=")
                variation_dict.append(intrinsics)
                variation_dict.append("Phase:=")
                if phase:
                    variation_dict.append(phase)
                else:
                    variation_dict.append("0deg")
        if not sample_points_file and not sample_points_lists:

            _retry_ntimes(10, self.ofieldsreporter.CalculatorWrite, filename, ["Solution:=", solution], variation_dict)
        elif sample_points_file:

            _retry_ntimes(
                10,
                self.ofieldsreporter.ExportToFile,
                filename,
                sample_points_file,
                solution,
                variation_dict,
                export_with_sample_points,
            )
        else:
            sample_points_file = os.path.join(self._app.working_directory, "temp_points.pts")
            with open(sample_points_file, "w") as f:
                for point in sample_points_lists:
                    f.write(" ".join([str(i) for i in point]) + "\n")
            _retry_ntimes(
                10,
                self.ofieldsreporter.ExportToFile,
                filename,
                sample_points_file,
                solution,
                variation_dict,
                export_with_sample_points,
            )

        if os.path.exists(filename):
            return filename
        return False  # pragma: no cover

    @pyaedt_function_handler()
    def export_field_plot(self, plotname, filepath, filename="", file_format="aedtplt"):
        """Export a field plot.

        Parameters
        ----------
        plotname : str
            Name of the plot.

        filepath : str
            Path for saving the file.

        filename : str, optional
            Name of the file. The default is ``""``.

        file_format : str, optional
            Name of the file extension. The default is ``"aedtplt"``. Option is ``"case"``.

        Returns
        -------
        str
            File Path when succeeded.

        References
        ----------

        >>> oModule.ExportFieldPlot
        """
        if not filename:
            filename = plotname
        self.ofieldsreporter.ExportFieldPlot(plotname, False, os.path.join(filepath, filename + "." + file_format))
        return os.path.join(filepath, filename + "." + file_format)

    @pyaedt_function_handler()
    def change_field_plot_scale(self, plot_name, minimum_value, maximum_value, is_log=False, is_db=False):
        """Change Field Plot Scale.

        Parameters
        ----------
        plot_name : str
            Name of the Plot Folder to update.
        minimum_value : str, float
            Minimum value of the scale.
        maximum_value : str, float
            Maximum value of the scale.
        is_log : bool, optional
            Set to ``True`` if Log Scale is setup.
        is_db : bool, optional
            Set to ``True`` if dB Scale is setup.

        Returns
        -------
        bool
            ``True`` if successful.

        References
        ----------

        >>> oModule.SetPlotFolderSettings
        """
        args = ["NAME:FieldsPlotSettings", "Real Time mode:=", True]
        args += [
            [
                "NAME:ColorMaPSettings",
                "ColorMapType:=",
                "Spectrum",
                "SpectrumType:=",
                "Rainbow",
                "UniformColor:=",
                [127, 255, 255],
                "RampColor:=",
                [255, 127, 127],
            ]
        ]
        args += [
            [
                "NAME:Scale3DSettings",
                "minvalue:=",
                minimum_value,
                "maxvalue:=",
                maximum_value,
                "log:=",
                not is_log,
                "dB:=",
                is_db,
                "ScaleType:=",
                1,
            ]
        ]
        self.ofieldsreporter.SetPlotFolderSettings(plot_name, args)
        return True

    @pyaedt_function_handler()
    def _create_fieldplot(self, objlist, quantityName, setup_name, intrinsincList, listtype, plot_name=None):
        if isinstance(objlist, (str, int)):
            objlist = [objlist]
        if not setup_name:
            setup_name = self._app.existing_analysis_sweeps[0]
        self._desktop.CloseAllWindows()
        try:
            self._app._modeler.fit_all()
        except:
            pass
        self._desktop.TileWindows(0)
        self._oproject.SetActiveDesign(self._app.design_name)

        char_set = string.ascii_uppercase + string.digits
        if not plot_name:
            plot_name = quantityName + "_" + "".join(random.sample(char_set, 6))
        if listtype == "CutPlane":
            plot = FieldPlot(
                self,
                cutplanelist=objlist,
                solutionName=setup_name,
                quantityName=quantityName,
                intrinsincList=intrinsincList,
            )
        elif listtype == "FacesList":
            plot = FieldPlot(
                self,
                surfacelist=objlist,
                solutionName=setup_name,
                quantityName=quantityName,
                intrinsincList=intrinsincList,
            )
        elif listtype == "ObjList":
            plot = FieldPlot(
                self, objlist=objlist, solutionName=setup_name, quantityName=quantityName, intrinsincList=intrinsincList
            )
        elif listtype == "Line":
            plot = FieldPlot(
                self,
                linelist=objlist,
                solutionName=setup_name,
                quantityName=quantityName,
                intrinsincList=intrinsincList,
            )
        plot.name = plot_name
        plot.plotFolder = plot_name

        plt = plot.create()
        if "Maxwell" in self._app.design_type and self.post_solution_type == "Transient":
            self.ofieldsreporter.SetPlotsViewSolutionContext([plot_name], setup_name, "Time:" + intrinsincList["Time"])
        if plt:
            self.field_plots[plot_name] = plot
            return plot
        else:
            return False

    @pyaedt_function_handler()
    def create_fieldplot_line(self, objlist, quantityName, setup_name=None, intrinsincDict={}, plot_name=None):
        """Create a field plot of line.

        Parameters
        ----------
        objlist : list
            List of polyline to plot.
        quantityName : str
            Name of the quantity to plot.
        setup_name : str, optional
            Name of the setup in the format ``"setupName : sweepName"``. The default
            is ``None``.
        intrinsincDict : dict, optional
            Dictionary containing all intrinsic variables. The default
            is ``{}``.
        plot_name : str, optional
            Name of the fieldplot to create.

        Returns
        -------
        type
            Plot object.

        References
        ----------

        >>> oModule.CreateFieldPlot
        """
        if plot_name and plot_name in list(self.field_plots.keys()):
            self.logger.info("Plot {} exists. returning the object.".format(plot_name))
            return self.field_plots[plot_name]
        return self._create_fieldplot(objlist, quantityName, setup_name, intrinsincDict, "Line", plot_name)

    @pyaedt_function_handler()
    def create_fieldplot_surface(self, objlist, quantityName, setup_name=None, intrinsincDict={}, plot_name=None):
        """Create a field plot of surfaces.

        Parameters
        ----------
        objlist : list
            List of surfaces to plot.
        quantityName : str
            Name of the quantity to plot.
        setup_name : str, optional
            Name of the setup in the format ``"setupName : sweepName"``. The default
            is ``None``.
        intrinsincDict : dict, optional
            Dictionary containing all intrinsic variables. The default
            is ``{}``.
        plot_name : str, optional
            Name of the fieldplot to create.

        Returns
        -------
        :class:``pyaedt.modules.PostProcessor.FieldPlot``
            Plot object.

        References
        ----------

        >>> oModule.CreateFieldPlot
        """
        if plot_name and plot_name in list(self.field_plots.keys()):
            self.logger.info("Plot {} exists. returning the object.".format(plot_name))
            return self.field_plots[plot_name]
        return self._create_fieldplot(objlist, quantityName, setup_name, intrinsincDict, "FacesList", plot_name)

    @pyaedt_function_handler()
    def create_fieldplot_cutplane(self, objlist, quantityName, setup_name=None, intrinsincDict={}, plot_name=None):
        """Create a field plot of cut planes.

        Parameters
        ----------
        objlist : list
            List of cut planes to plot.
        quantityName : str
            Name of the quantity to plot.
        setup_name : str, optional
            Name of the setup in the format
            ``"setupName : sweepName"``. The default is ``None``,
            in which case ``"nominal, lastadaptive"`` is used.
        intrinsincDict : dict, optional
            Dictionary containing all intrinsic variables.
            The default is ``{}``.
        plot_name : str, optional
            Name of the fieldplot to create.

        Returns
        -------
        :class:``pyaedt.modules.PostProcessor.FieldPlot``
            Plot object.

        References
        ----------

        >>> oModule.CreateFieldPlot
        """
        if plot_name and plot_name in list(self.field_plots.keys()):
            self.logger.info("Plot {} exists. returning the object.".format(plot_name))
            return self.field_plots[plot_name]
        return self._create_fieldplot(objlist, quantityName, setup_name, intrinsincDict, "CutPlane", plot_name)

    @pyaedt_function_handler()
    def create_fieldplot_volume(self, objlist, quantityName, setup_name=None, intrinsincDict={}, plot_name=None):
        """Create a field plot of volumes.

        Parameters
        ----------
        objlist : list
            List of volumes to plot.
        quantityName :
            Name of the quantity to plot.
        setup_name : str, optional
            Name of the setup in the format
            ``"setupName : sweepName"``. The default is ``None``,
            in which case ``"nominal, lastadaptive"`` is used.
        intrinsincDict : dict, optional
            Dictionary containing all intrinsic variables. The default
            is ``{}``.
        plot_name : str, optional
            Name of the fieldplot to create.

        Returns
        -------
        :class:``pyaedt.modules.PostProcessor.FieldPlot``
            Plot object

        References
        ----------

        >>> oModule.CreateFieldPlot
        """
        if plot_name and plot_name in list(self.field_plots.keys()):
            self.logger.info("Plot {} exists. returning the object.".format(plot_name))
            return self.field_plots[plot_name]
        return self._create_fieldplot(objlist, quantityName, setup_name, intrinsincDict, "ObjList", plot_name)

    @pyaedt_function_handler()
    def export_field_jpg(
        self, fileName, plotName, foldername, orientation="isometric", width=1920, height=1080, display_wireframe=True
    ):
        """Export a field plot and coordinate system to a JPG file.

        Parameters
        ----------
        fileName : str
            Full path and name to save the JPG file to.
        plotName : str
            Name of the plot.
        foldername : str
            Name of the folder plot.
        orientation : str
            Name of the orientation to apply.
        width : int
            Plot Width.
        height : int
            Plot Height.
        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        References
        ----------

        >>> oModule.ExportPlotImageToFile
        >>> oModule.ExportModelImageToFile
        """
        if self.post_solution_type not in ["HFSS3DLayout", "HFSS 3D Layout Design"]:
            wireframes = []
            if display_wireframe:
                names = self._primitives.object_names
                for el in names:
                    if not self._primitives[el].display_wireframe:
                        wireframes.append(el)
                        self._primitives[el].display_wireframe = True
            if self._app._aedt_version < "2021.2":
                bound = self.modeler.get_model_bounding_box()
                center = [
                    (float(bound[0]) + float(bound[3])) / 2,
                    (float(bound[1]) + float(bound[4])) / 2,
                    (float(bound[2]) + float(bound[5])) / 2,
                ]
                view = orientation_to_view.get(orientation, "iso")
                cs = self.modeler.create_coordinate_system(origin=center, mode="view", view=view)
                self.ofieldsreporter.ExportPlotImageToFile(fileName, foldername, plotName, cs.name)
                cs.delete()
            else:

                self.export_model_picture(
                    full_name=fileName, width=width, height=height, orientation=orientation, field_selections=plotName
                )
                # self.ofieldsreporter.ExportPlotImageWithViewToFile(
                #     fileName, foldername, plotName, width, height, orientation
                # )

            for solid in wireframes:
                self._primitives[solid].display_wireframe = False
        else:
            self.ofieldsreporter.ExportPlotImageWithViewToFile(
                fileName, foldername, plotName, width, height, orientation
            )
        # self.oeditor.ExportImage(fileName, 1920, 1080)
        return True

    @pyaedt_function_handler()
    def export_field_image_with_view(self, plotName, foldername, exportFilePath, view="isometric", wireframe=True):
        """Export a field plot image with a view.

        .. deprecated:: 0.5.0
           Use :func:`export_field_jpg` method instead.

        .. note::
           For AEDT 2019 R3, this method works only on the ISO view due to a bug in the API.
           This method works properly in 2021 R1.

        Parameters
        ----------
        plotName : str
            Name of the plot.
        exportFilePath :
            Path for exporting the image file.
        view : str, optional
            View to export. Options are ``"isometric"``, ``"top"``, ``"bottom"``, ``"right"``, ``"left"`` and any
            custom orientation.
            The default is ``"isometric"``.
        wireframe : bool, optional
            Whether to put the objects in the wireframe mode. The default is ``True``.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        References
        ----------

        >>> oModule.ExportPlotImageToFile
        >>> oModule.ExportModelImageToFile
        """
        warnings.warn(
            "`export_field_image_with_view` is deprecated. Use `export_field_jpg` property instead.", DeprecationWarning
        )

        return self.export_field_jpg(
            exportFilePath, plotName, foldername, orientation=view, display_wireframe=wireframe
        )

    @pyaedt_function_handler()
    def delete_field_plot(self, name):
        """Delete a field plot.

        Parameters
        ----------
        name : str
            Name of the field plot.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        References
        ----------

        >>> oModule.DeleteFieldPlot
        """
        self.ofieldsreporter.DeleteFieldPlot([name])
        self.field_plots.pop(name, None)
        return True

    @pyaedt_function_handler()
    def export_model_picture(
        self,
        full_name=None,
        show_axis=True,
        show_grid=True,
        show_ruler=True,
        show_region="Default",
        selections=None,
        field_selections=None,
        orientation="isometric",
        width=0,
        height=0,
    ):
        """Export a snapshot of the model to a JPG file.

        .. note::
           This method works only when AEDT is running in the graphical mode.

        Parameters
        ----------
        full_name : str, optional
            Full Path for exporting the image file. The default is ``None``, in which case working_dir will be used.
        show_axis : bool, optional
            Whether to show the axes. The default is ``True``.
        show_grid : bool, optional
            Whether to show the grid. The default is ``True``.
        show_ruler : bool, optional
            Whether to show the ruler. The default is ``True``.
        show_region : bool, optional
            Whether to show the region or not. The default is ``Default``.
        selections : list, optional
            Whether to export image of a selection or not. Default is `None`.
        field_selections : str, list, optional
            List of Fields plots to add to the image. Default is `None`. `"all"` for all field plots.
        orientation : str, optional
            Picture orientation. Orientation can be one of `"top"`, `"bottom"`, `"right"`, `"left"`,
            `"front"`, `"back"`, `"trimetric"`, `"dimetric"`, `"isometric"`, or a custom
            orientation that you added to the Orientation List.
        width : int, optional
            Export image picture width size in pixels. Default is 0 which takes the desktop size.
        height : int, optional
            Export image picture height size in pixels. Default is 0 which takes the desktop size.

        Returns
        -------
        str
            File path of the generated JPG file.

        References
        ----------

        >>> oEditor.ExportModelImageToFile
        """
        # Set up arguments list for createReport function
        if selections:
            selections = self.modeler.convert_to_selections(selections, False)
        else:
            selections = ""
        if not full_name:
            full_name = os.path.join(self._app.working_directory, generate_unique_name(self._app.design_name) + ".jpg")

        # open the 3D modeler and remove the selection on other objects
        if self._app.design_type not in ["HFSS 3D Layout Design", "Circuit Design", "Maxwell Circuit", "Twin Builder"]:
            self.oeditor.ShowWindow()
            self.steal_focus_oneditor()
        self.modeler.fit_all()
        # export the image
        if field_selections:
            if isinstance(field_selections, str):
                if field_selections.lower() == "all":
                    field_selections = [""]
                else:
                    field_selections = [field_selections]

        else:
            field_selections = ["none"]
        arg = [
            "NAME:SaveImageParams",
            "ShowAxis:=",
            str(show_axis),
            "ShowGrid:=",
            str(show_grid),
            "ShowRuler:=",
            str(show_ruler),
            "ShowRegion:=",
            str(show_region),
            "Selections:=",
            selections,
            "FieldPlotSelections:=",
            ",".join(field_selections),
            "Orientation:=",
            orientation,
        ]
        if self._app.design_type in ["HFSS 3D Layout Design", "Circuit Design", "Maxwell Circuit", "Twin Builder"]:
            if width == 0:
                width = 1920
            if height == 0:
                height = 1080
            self.oeditor.ExportImage(full_name, width, height)
        else:
            self.oeditor.ExportModelImageToFile(full_name, width, height, arg)
        return full_name

    @pyaedt_function_handler()
    def get_far_field_data(
        self, expression="GainTotal", setup_sweep_name="", domain="Infinite Sphere1", families_dict=None
    ):
        """Generate far field data using ``GetSolutionDataPerVariation``.

        This method returns the data ``solData``, ``ThetaVals``,
        ``PhiVals``, ``ScanPhiVals``, ``ScanThetaVals``, and
        ``FreqVals``.

        Parameters
        ----------
        expression : str or list, optional
            One or more formulas to add to the report. The default is ``"GainTotal"``.
        setup_sweep_name : str, optional
            Name of the setup for computing the report. The default is ``""``,
            in which case the nominal sweep is used.
        domain : str, optional
            Context type (sweep or time). The default is ``"Infinite Sphere1"``.
        families_dict : dict, optional
            Dictionary of variables and values. The default is ``{"Freq": ["All"]}``.

        Returns
        -------
        :class:`pyaedt.modules.PostProcessor.SolutionData`

        References
        ----------

        >>> oModule.GetSolutionDataPerVariation
        """
        if type(expression) is not list:
            expression = [expression]
        if not setup_sweep_name:
            setup_sweep_name = self._app.nominal_adaptive
        if families_dict is None:
            families_dict = {"Theta": ["All"], "Phi": ["All"], "Freq": ["All"]}
        solution_data = self.get_solution_data_per_variation(
            "Far Fields", setup_sweep_name, ["Context:=", domain], families_dict, expression
        )
        if not solution_data:
            print("No Data Available. Check inputs")
            return False
        return solution_data

    @pyaedt_function_handler()
    def export_model_obj(self, obj_list=None, export_path=None, export_as_single_objects=False, air_objects=False):
        """Export the model.

        Parameters
        ----------
        obj_list : list, optional
            List of objects to export. Export every model object except 3D ones, vacuum and air objects.
        export_path : str, optional
            Full path of the exported obj file.
        export_as_single_objects : bool, optional
            Define if the model will be exported as single obj or list of objs for each object.
        air_objects : bool, optional
            Define if air and vacuum objects will be exported.

        Returns
        -------
        list
            Files obj path.
        """

        assert self._app._aedt_version >= "2021.2", self.logger.error("Object is supported from AEDT 2021 R2.")
        if not export_path:
            export_path = self._app.working_directory
        if not obj_list:
            self._app.modeler.refresh_all_ids()
            obj_list = self._app.modeler.object_names
            if not air_objects:
                obj_list = [
                    i
                    for i in obj_list
                    if not self._app.modeler[i].is3d
                    or (
                        self._app.modeler[i].material_name.lower() != "vacuum"
                        and self._app.modeler[i].material_name.lower() != "air"
                    )
                ]
        if export_as_single_objects:
            files_exported = []
            for el in obj_list:
                fname = os.path.join(export_path, "{}.obj".format(el))
                self._app.modeler.oeditor.ExportModelMeshToFile(fname, [el])
                if not self._app.modeler[el].display_wireframe:
                    transp = 0.6
                    if self._app.modeler[el].transparency:
                        transp = self._app.modeler[el].transparency
                    files_exported.append([fname, self._app.modeler[el].color, 1 - transp])
                else:
                    files_exported.append([fname, self._app.modeler[el].color, 0.05])
            return files_exported
        else:
            fname = os.path.join(export_path, "Model_AllObjs_AllMats.obj")
            self._app.modeler.oeditor.ExportModelMeshToFile(fname, obj_list)
            return [[fname, "grey", 0.6]]

    @pyaedt_function_handler()
    def export_mesh_obj(self, setup_name=None, intrinsic_dict={}):
        """Export the mesh.

        Parameters
        ----------
        setup_name : str, optional
            Name of the setup. The default is ``None``.
        intrinsic_dict : dict, optipnal.
            Intrinsic dictionary that is needed for the export.
            The default is ``{}``.

        Returns
        -------

        """
        project_path = self._app.working_directory

        if not setup_name:
            setup_name = self._app.nominal_adaptive
        face_lists = []
        obj_list = self._app.modeler.object_names
        for el in obj_list:
            obj_id = self._app.modeler.get_obj_id(el)
            if not self._app.modeler.objects[obj_id].is3d or (
                self._app.modeler.objects[obj_id].material_name != "vacuum"
                and self._app.modeler.objects[obj_id].material_name != "air"
            ):
                face_lists += self._app.modeler.get_object_faces(obj_id)
        plot = self.create_fieldplot_surface(face_lists, "Mesh", setup_name, intrinsic_dict)
        if plot:
            file_to_add = self.export_field_plot(plot.name, project_path)
            plot.delete()
            return file_to_add
        return None


class CircuitPostProcessor(PostProcessorCommon, object):
    """Manages the main AEDT Nexxim postprocessing functions.


    .. note::
       Some functionalities are available only when AEDT is running in the graphical mode.

    Parameters
    ----------
    app : :class:`pyaedt.application.AnalysisNexxim.FieldAnalysisCircuit`
        Inherited parent object. The parent object must provide the members
        `_modeler`, `_desktop`, `_odesign`, and `logger`.

    """

    def __init__(self, app):
        PostProcessorCommon.__init__(self, app)

    def create_ami_initial_response_plot(
        self,
        setupname,
        ami_name,
        variation_list_w_value,
        plot_type="Rectangular Plot",
        plot_initial_response=True,
        plot_intermediate_response=False,
        plot_final_response=False,
        plotname=None,
    ):
        """Create an AMI initial response plot.


        Parameters
        ----------
        setupname : str
            Name of the setup
        ami_name : str
            AMI Probe name to use
        variation_list_w_value : list
            list of variations with relative values
        plot_type : str, Default ``"Rectangular Plot"``
            String containing the report type. Default is ``"Rectangular Plot"``. It can be ``"Data Table"``,
            ``"Rectangular Stacked Plot"``or any of the other valid AEDT Report types.
        plot_initial_response : bool, optional
            Set either to plot the initial input response.  Default is ``True``.
        plot_intermediate_response : bool, optional
            Set whether to plot the intermediate input response.  Default is ``False``.
        plot_final_response : bool, optional
            Set whether to plot the final input response.  Default is ``False``.
        plotname : str, optional
            The plot name.  Default is a unique name.

        Returns
        -------
        str
            Name of the plot.
        """
        if not plotname:
            plotname = generate_unique_name("AMIAnalysis")
        variations = ["__InitialTime:=", ["All"]]
        i = 0
        for a in variation_list_w_value:
            if (i % 2) == 0:
                if ":=" in a:
                    variations.append(a)
                else:
                    variations.append(a + ":=")
            else:
                if isinstance(a, list):
                    variations.append(a)
                else:
                    variations.append([a])
            i += 1
        ycomponents = []
        if plot_initial_response:
            ycomponents.append("InitialImpulseResponse<{}.int_ami_rx>".format(ami_name))
        if plot_intermediate_response:
            ycomponents.append("IntermediateImpulseResponse<{}.int_ami_rx>".format(ami_name))
        if plot_final_response:
            ycomponents.append("FinalImpulseResponse<{}.int_ami_rx>".format(ami_name))
        self.oreportsetup.CreateReport(
            plotname,
            "Standard",
            plot_type,
            setupname,
            [
                "NAME:Context",
                "SimValueContext:=",
                [
                    55824,
                    0,
                    2,
                    0,
                    False,
                    False,
                    -1,
                    1,
                    0,
                    1,
                    1,
                    "",
                    0,
                    0,
                    "NUMLEVELS",
                    False,
                    "1",
                    "PCID",
                    False,
                    "-1",
                    "PID",
                    False,
                    "1",
                    "SCID",
                    False,
                    "-1",
                    "SID",
                    False,
                    "0",
                ],
            ],
            variations,
            ["X Component:=", "__InitialTime", "Y Component:=", ycomponents],
        )
        return plotname

    def create_ami_statistical_eye_plot(
        self, setupname, ami_name, variation_list_w_value, ami_plot_type="InitialEye", plotname=None
    ):
        """Create an AMI statistical eye plot.

        Parameters
        ----------
        setupname : str
            Name of the setup.
        probe_id : str
            AMI Probe Name to use
        variation_list_w_value : list
            List of variations with relative values.
        plot_type : str, optional
            String containing the report type. Default is ``"Rectangular Plot"``. It can be ``"Data Table"``,
            ``"Rectangular Stacked Plot"``, or any other valid AEDT report types.
        ami_plot_type : str, optional
            String containing the report AMI type. Default is ``"InitialEye"``. It can be ``"EyeAfterSource"``,
            ``"EyeAfterChannel"`` or ``"EyeAfterProbe"``.
        plotname : str, optional
            The name of the plot.  Defaults to a unique name starting with ``"Plot"``.

        Returns
        -------
        str
           The name of the plot.

        References
        ----------

        >>> oModule.CreateReport
        """
        if not plotname:
            plotname = generate_unique_name("AMYAanalysis")
        variations = [
            "__UnitInterval:=",
            ["All"],
            "__Amplitude:=",
            ["All"],
        ]
        i = 0
        for a in variation_list_w_value:
            if (i % 2) == 0:
                if ":=" in a:
                    variations.append(a)
                else:
                    variations.append(a + ":=")
            else:
                if isinstance(a, list):
                    variations.append(a)
                else:
                    variations.append([a])
            i += 1
        ycomponents = []
        if ami_plot_type == "InitialEye" or ami_plot_type == "EyeAfterSource":
            ibs_type = "tx"
        else:
            ibs_type = "rx"
        ycomponents.append("{}<{}.int_ami_{}>".format(ami_plot_type, ami_name, ibs_type))

        ami_id = "0"
        if ami_plot_type == "EyeAfterSource":
            ami_id = "1"
        elif ami_plot_type == "EyeAfterChannel":
            ami_id = "2"
        elif ami_plot_type == "EyeAfterProbe":
            ami_id = "3"
        self.oreportsetup.CreateReport(
            plotname,
            "Statistical Eye",
            "Statistical Eye Plot",
            setupname,
            [
                "NAME:Context",
                "SimValueContext:=",
                [
                    55819,
                    0,
                    2,
                    0,
                    False,
                    False,
                    -1,
                    1,
                    0,
                    1,
                    1,
                    "",
                    0,
                    0,
                    "NUMLEVELS",
                    False,
                    "1",
                    "QTID",
                    False,
                    ami_id,
                    "SCID",
                    False,
                    "-1",
                    "SID",
                    False,
                    "0",
                ],
            ],
            variations,
            ["X Component:=", "__UnitInterval", "Y Component:=", "__Amplitude", "Eye Diagram Component:=", ycomponents],
        )
        return plotname

    def create_statistical_eye_plot(
        self, setupname, probe_names, variation_list_w_value, ami_plot_type="InitialEye", plotname=None
    ):
        """Create a statistical QuickEye, VerifEye, and/or Statistical Eye plot.

        Parameters
        ----------
        setupname : str
            Name of the setup
        probe_names : str or list
            Name of the probe to plot in the EYE diagram.
        variation_list_w_value : list
            List of variations with relative values.
        plotname : str, optional
            The name of the plot.

        Returns
        -------
        str
            The name of the plot.

        References
        ----------

        >>> oModule.CreateReport
        """
        if not plotname:
            plotname = generate_unique_name("AMIAanalysis")
        variations = [
            "__UnitInterval:=",
            ["All"],
            "__Amplitude:=",
            ["All"],
        ]
        i = 0
        for a in variation_list_w_value:
            if (i % 2) == 0:
                if ":=" in a:
                    variations.append(a)
                else:
                    variations.append(a + ":=")
            else:
                if isinstance(a, list):
                    variations.append(a)
                else:
                    variations.append([a])
            i += 1
        if isinstance(probe_names, list):
            ycomponents = probe_names
        else:
            ycomponents = [probe_names]

        self.oreportsetup.CreateReport(
            plotname,
            "Statistical Eye",
            "Statistical Eye Plot",
            setupname,
            [
                "NAME:Context",
                "SimValueContext:=",
                [
                    55819,
                    0,
                    2,
                    0,
                    False,
                    False,
                    -1,
                    1,
                    0,
                    1,
                    1,
                    "",
                    0,
                    0,
                    "NUMLEVELS",
                    False,
                    "1",
                    "QTID",
                    False,
                    "1",
                    "SCID",
                    False,
                    "-1",
                    "SID",
                    False,
                    "0",
                ],
            ],
            variations,
            ["X Component:=", "__UnitInterval", "Y Component:=", "__Amplitude", "Eye Diagram Component:=", ycomponents],
        )
        return plotname
