# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 - 2026 Synopsys, Inc. and ANSYS, Inc. All rights reserved.
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

from __future__ import annotations

import sys

if sys.version_info >= (3, 13):
    from warnings import deprecated
else:
    from typing_extensions import deprecated

import copy
from difflib import SequenceMatcher
import os
from typing import TYPE_CHECKING
from typing import Any
import warnings

from ansys.aedt.core.application import _get_obj_data
from ansys.aedt.core.application import _has_get_obj_data
from ansys.aedt.core.base import PyAedtBase
from ansys.aedt.core.generic.constants import unit_converter
from ansys.aedt.core.generic.data_handlers import _dict2arg
from ansys.aedt.core.generic.general_methods import pyaedt_function_handler
from ansys.aedt.core.generic.numbers_utils import Quantity
from ansys.aedt.core.generic.props import Props as SweepProps
from ansys.aedt.core.internal.load_aedt_file import load_entire_aedt_file
from ansys.aedt.core.modeler.cad.elements_3d import BinaryTreeNode
from ansys.aedt.core.modules.setup_templates import Sweep3DLayout
from ansys.aedt.core.modules.setup_templates import SweepEddyCurrent
from ansys.aedt.core.modules.setup_templates import SweepHfss3D
from ansys.aedt.core.modules.setup_templates import SweepQ3D
from ansys.aedt.core.modules.setup_templates import SweepRaptorX
from ansys.aedt.core.modules.setup_templates import SweepSiwave

if TYPE_CHECKING:
    from ansys.aedt.core.modules.solve_setup import Setup3DLayout


@pyaedt_function_handler()
def identify_setup(props: dict) -> bool:
    """Identify if a setup's properties is based on a time or frequency domain.

    Parameters
    ----------
    props : dict
        Dictionary of the properties.

    Returns
    -------
    bool
        `True` if domain is a time. `False` if the domain is for a frequency and sweeps.

    Examples
    --------
    >>> from ansys.aedt.core.modules.solve_sweeps import identify_setup
    >>> identify_setup(props={"Name": "Value"})

    """
    keys = [
        "Transient",
        "TimeStep",
        "Data/InitialStep",
        "TransientData",
        "QuickEyeAnalysis",
        "VerifEyeAnalysis",
        "AMIAnalysis",
        "HSPICETransientData",
        "SystemFDAnalysis",
        "Start Time:=",
    ]
    for key in keys:
        if "/" in key:
            if key.split("/")[0] in props and key.split("/")[1] in props[key.split("/")[0]]:
                return True
        elif key in props:
            return True
    return False


class SweepCommon(BinaryTreeNode, PyAedtBase):
    """Provide sweep common."""

    def __repr__(self) -> str:
        return f"{self.setup_name} : {self.name}"

    def __str__(self) -> str:
        return f"{self.setup_name} : {self.name}"

    def __init__(self, setup: Setup3DLayout, name: str) -> None:
        self._setup: Setup3DLayout = setup
        self._app: Any = self._setup._app

        self._name = name

        self.__sweep_type = None

        self._has_getobject = _has_get_obj_data(self._child_object)

    @pyaedt_function_handler()
    def _initialize_tree_node(self) -> bool:
        if self._child_object:
            BinaryTreeNode.__init__(self, self._name, self._child_object, False, app=self._app)
            return True
        return False

    @property
    def _child_object(self) -> Any | None:
        """Object-oriented properties.

        Returns
        -------
        AEDT object if any or None

        """
        child_object = None
        if self._setup.child_object:
            child_object = self._app.get_oo_object(self._setup.child_object, self._name)
        return child_object

    @property
    def name(self) -> str:
        """Name of the sweep.

        Returns
        -------
        str
           Name of the sweep.

        Examples
        --------
        >>> from ansys.aedt.core import Hfss
        >>> hfss = Hfss()
        >>> s = hfss.create_setup()
        >>> sweep = s.add_sweep()
        >>> sweep.name

        """
        child_object = self._child_object
        if child_object is not None and "Sweep" in dir(child_object):
            self._name = child_object.Sweep
        return self._name

    @name.setter
    def name(self, name: str) -> None:
        setup_names = self._app.setup_names
        if name in setup_names:
            raise ValueError(f"Name {name} already assigned in the design.")
        if self._child_object is not None:
            self._child_object.Name = str(name)
            object.__setattr__(self, "_name", name)
            object.__setattr__(self, "_tree_node_initialized", False)
            object.__setattr__(self, "_props", None)
            object.__setattr__(self, "_children_loaded", False)

    @property
    def sweep_type(self) -> str | None:
        """Sweet type.

        Returns
        -------
        str
           Name of the sweep.

        Examples
        --------
        >>> from ansys.aedt.core import Hfss3dLayout
        >>> hfss = Hfss3dLayout()
        >>> s = hfss.create_setup()
        >>> s.sweep_type

        """
        if not self.__sweep_type:
            self.__sweep_type = self.child_object.Type if "Type" in dir(self.child_object) else None
        return self.__sweep_type

    @property
    def setup_name(self) -> str:
        """Setup name."""
        return self._setup.name


class SweepHFSS(SweepCommon):
    """Initializes, creates, and updates sweeps in HFSS.

    Parameters
    ----------
    setup : :class 'from ansys.aedt.core.modules.solve_setup.Setup'
        Setup to use for the analysis.
    name : str
        Name of the sweep.
    sweep_type : str, optional
        Type of the sweep. Options are ``"Fast"``, ``"Interpolating"``,
        and ``"Discrete"``. The default is ``"Interpolating"``.
    props : dict, optional
        Dictionary of the properties. The default is ``None``, in which case
        the default properties are retrieved.

    Examples
    --------
    >>> hfss = Hfss(
    ...     version=version,
    ...     project=proj,
    ...     design=gtemDesign,
    ...     solution_type=solutiontype,
    ...     name=name,
    ...     new_desktop=False,
    ...     close_on_exit=False,
    ... )
    >>> hfss_setup = hfss.setups[0]
    >>> hfss_sweep = SweepHFSS(hfss_setup, "Sweep", sweep_type="Interpolating", props=None)

    """

    def __init__(self, setup, name: str, sweep_type: str = "Interpolating", props=None) -> None:
        self._app = setup
        self.setup_name = setup.name
        self.name = name
        self.props = copy.deepcopy(SweepHfss3D)
        if props:
            if "RangeStep" in props.keys():  # LinearCount is the default sweep type. Change it if RangeStep is passed.
                if "RangeCount" in props.keys():
                    self._app._app.logger.info(
                        "Inconsistent arguments 'RangeCount' and 'RangeStep' passed to 'SweepHFSS',"
                    )
                    self._app._app.logger.info("Default remains 'LinearCount' sweep type.")
                else:
                    self.props["RangeType"] = "LinearStep"
            for key, value in props.items():
                if key in self.props.keys():
                    self.props[key] = value
                else:
                    error_message = f"Parameter '{key}' is invalid and will be ignored."
                    self._app._app.logger.warning(error_message)

        if SequenceMatcher(None, sweep_type.lower(), "interpolating").ratio() > 0.8:
            sweep_type = "Interpolating"
        elif SequenceMatcher(None, sweep_type.lower(), "discrete").ratio() > 0.8:
            sweep_type = "Discrete"
        elif SequenceMatcher(None, sweep_type.lower(), "fast").ratio() > 0.8:
            sweep_type = "Fast"
        else:
            warnings.warn("Invalid sweep type. `Interpolating` will be set as the default.")
            sweep_type = "Interpolating"
        self.props["Type"] = sweep_type

    @property
    def is_solved(self) -> bool:
        """Verify if solutions are available for the sweep.

        Returns
        -------
        bool
            `True` if solutions are available.

        Examples
        --------
        >>> from ansys.aedt.core.modules.solve_sweeps import SweepHFSS
        >>> obj = SweepHFSS()
        >>> obj.is_solved

        """
        sol = self._app._app.post.reports_by_category.standard(setup=f"{self.setup_name} : {self.name}")
        if identify_setup(self.props):
            sol.domain = "Time"
        return True if sol.get_solution_data() else False

    @property
    def frequencies(self) -> list[float]:
        """List of all frequencies of the active sweep.

        To see values, the project must be saved and solved.

        Returns
        -------
        list of float
            Frequency points.

        Examples
        --------
        >>> from ansys.aedt.core.modules.solve_sweeps import SweepHFSS
        >>> obj = SweepHFSS()
        >>> obj.frequencies

        """
        sol = self._app._app.post.reports_by_category.standard(setup=f"{self.setup_name} : {self.name}")
        soldata = sol.get_solution_data()
        if soldata and "Freq" in soldata.intrinsics:
            return [Quantity(i, soldata.units_sweeps["Freq"]) for i in soldata.intrinsics["Freq"]]
        return []

    @property
    def basis_frequencies(self) -> list[float]:
        """List of all frequencies that have fields available.

        To see values, the project must be saved and solved.

        Returns
        -------
        list of float
            Frequency points.

        Examples
        --------
        >>> from ansys.aedt.core.modules.solve_sweeps import SweepHFSS
        >>> obj = SweepHFSS()
        >>> obj.basis_frequencies

        """
        solutions_file = os.path.join(self._app._app.results_directory, f"{self._app._app.design_name}.asol")
        fr = []
        if os.path.exists(solutions_file):
            solutions = load_entire_aedt_file(solutions_file)
            for k, v in solutions.items():
                if "SolutionBlock" in k and "SolutionName" in v and v["SolutionName"] == self.name and "Fields" in v:
                    try:
                        new_list = [float(i) for i in v["Fields"]["IDDblMap"][1::2]]

                        new_list.sort()
                        new_list = unit_converter(
                            values=new_list,
                            unit_system="Freq",
                            input_units="Hz",
                            output_units=self._app._app.units.frequency,
                        )
                        fr.append(new_list)
                    except (KeyError, NameError, IndexError):
                        pass

        count = 0
        for el in self._app._app.setups:
            if el.name == self.setup_name:
                for sweep in el.sweeps:
                    if sweep.name == self.name:
                        return fr[count] if len(fr) >= count + 1 else []
            else:
                for sweep in el.sweeps:
                    if sweep.name == self.name:
                        count += 1
        return []

    @pyaedt_function_handler()
    def add_subrange(
        self,
        range_type: str,
        start: float,
        end: float = None,
        count: float = None,
        unit: str = "GHz",
        save_single_fields: bool = False,
        clear: bool = False,
    ) -> bool:
        """Add a range to the sweep.

        Parameters
        ----------
        range_type : str
            Type of the range. Options are ``"LinearCount"``,
            ``"LinearStep"``, ``"LogScale"``, and ``"SinglePoints"``.
        start : float
            Starting frequency.
        end : float, optional
            Stopping frequency. The default value is ``None``. A value is required for
            ``range_type="LinearCount"|"LinearStep"|"LogScale"``.
        count : int or float, optional
            Frequency count or frequency step. The default is ``None``. A value is required for
            ``range_type="LinearCount"|"LinearStep"|"LogScale"``.
        unit : str, optional
            Unit of the frequency. For example, ``"MHz`` or ``"GHz"``. The default is ``"GHz"``.
        save_single_fields : bool, optional
            Whether to save the fields of the single point. The default is ``False``.
            This parameter is used only for ``range_type="SinglePoints"``.
        clear : bool, optional
            Whether to suppress all other subranges except the current one under creation.
            The default value is ``False``.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        Examples
        --------
        Create a setup in an HFSS design and add multiple sweep ranges.

        >>> setup = hfss.create_setup(name="MySetup")
        >>> sweep = setup.add_sweep()
        >>> sweep.change_type("Interpolating")
        >>> sweep.change_range("LinearStep", 1.1, 2.1, 0.4, "GHz")
        >>> sweep.add_subrange("LinearCount", 1, 1.5, 5, "MHz")
        >>> sweep.add_subrange("LogScale", 1, 3, 10, "GHz")

        """
        if range_type == "LinearCount" or range_type == "LinearStep" or range_type == "LogScale":
            if not end or not count:
                raise AttributeError("Parameters 'end' and 'count' must be present.")

        if clear:
            self.props["RangeType"] = range_type
            self.props["RangeStart"] = str(start) + unit
            if range_type == "LinearCount":
                self.props["RangeEnd"] = str(end) + unit
                self.props["RangeCount"] = count
            elif range_type == "LinearStep":
                self.props["RangeEnd"] = str(end) + unit
                self.props["RangeStep"] = str(count) + unit
            elif range_type == "LogScale":
                self.props["RangeEnd"] = str(end) + unit
                self.props["RangeSamples"] = count
            elif range_type == "SinglePoints":
                self.props["RangeEnd"] = str(start) + unit
                self.props["SaveSingleField"] = save_single_fields
            self.props["SweepRanges"] = {"Subrange": []}
            return self.update()

        interval = {"RangeType": range_type, "RangeStart": str(start) + unit}
        if range_type == "LinearCount":
            interval["RangeEnd"] = str(end) + unit
            interval["RangeCount"] = count
        elif range_type == "LinearStep":
            interval["RangeEnd"] = str(end) + unit
            interval["RangeStep"] = str(count) + unit
        elif range_type == "LogScale":
            interval["RangeEnd"] = str(end) + unit
            interval["RangeCount"] = self.props["RangeCount"]
            interval["RangeSamples"] = count
        elif range_type == "SinglePoints":
            interval["RangeEnd"] = str(start) + unit
            interval["SaveSingleField"] = save_single_fields
        if not self.props.get("SweepRanges", None):
            self.props["SweepRanges"] = {"Subrange": []}

        if not isinstance(self.props["SweepRanges"]["Subrange"], list):
            self.props["SweepRanges"]["Subrange"] = [self.props["SweepRanges"]["Subrange"]]
        self.props["SweepRanges"]["Subrange"].append(interval)

        return self.update()

    @pyaedt_function_handler()
    def create(self) -> bool:
        """Create a sweep.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        Examples
        --------
        >>> from ansys.aedt.core.modules.solve_sweeps import SweepHFSS
        >>> obj = SweepHFSS()
        >>> obj.create()

        """
        self._app.oanalysis.InsertFrequencySweep(self.setup_name, self._get_args())
        return True

    @pyaedt_function_handler()
    def update(self) -> bool:
        """Update a sweep.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        Examples
        --------
        >>> from ansys.aedt.core.modules.solve_sweeps import SweepHFSS
        >>> obj = SweepHFSS()
        >>> obj.update()

        """
        self._app.oanalysis.EditFrequencySweep(self.setup_name, self.name, self._get_args())

        return True

    @pyaedt_function_handler()
    def _get_args(self, props=None):
        """Get arguments.

        Parameters
        ----------
        props : dict, optional
             Dictionary of the properties. The default is ``None``, in which
             case the default properties are retrieved.

        Returns
        -------
        dict
            Dictionary of the properties.

        """
        if props is None:
            props = self.props
        arg = ["NAME:" + self.name]
        _dict2arg(props, arg)
        return arg


class SweepHFSS3DLayout(SweepCommon):
    """Initializes, creates, and updates sweeps in HFSS 3D Layout.

    Parameters
    ----------
    setup : :class 'from ansys.aedt.core.modules.solve_setup.Setup'
        Setup to use for the analysis.
    name : str
        Name of the sweep.
    props : dict, optional
        Dictionary of the properties. The default is ``None``, in which
        case the default properties are retrieved.

    Examples
    --------
    >>> from ansys.aedt.core.modules.solve_sweeps import SweepHFSS3DLayout
    >>> obj = SweepHFSS3DLayout()

    """

    def __init__(self, setup, name: str, props=None) -> None:
        super().__init__(setup=setup, name=name)

        self._legacy_props = {}

        if props:
            self._legacy_props = SweepProps(self, props)

    @property
    def props(self) -> SweepProps:
        """Properties of the mesh operation.

        Returns
        -------
        :class:`ansys.aedt.core.generic.props.Props`

        Examples
        --------
        >>> from ansys.aedt.core import Hfss3dLayout
        >>> hfss = Hfss3dLayout()
        >>> setup = hfss.create_setup()
        >>> sweep = setup.add_sweep()
        >>> sweep.props

        """
        if self._legacy_props and not self._has_getobject:
            return SweepProps(self, self._legacy_props)

        if self._has_getobject:
            props = _get_obj_data(self._child_object) or {}
        else:
            design_property_data = self._app.design_properties["Setup"]["Data"]
            setup_name = self._setup.name
            if (
                setup_name in design_property_data
                and "Data" in design_property_data[setup_name]
                and self._name in design_property_data[setup_name]["Data"]
            ):
                props = design_property_data[setup_name]["Data"][self._name]
                if "Frequencies" in props:
                    del props["Frequencies"]
                if "DataId" in props:
                    del props["DataId"]
            else:
                setup_type = self._setup.setuptype
                if setup_type in [40, 41]:
                    props = copy.deepcopy(SweepSiwave)
                elif setup_type == 62:
                    props = copy.deepcopy(SweepRaptorX)
                else:
                    props = copy.deepcopy(Sweep3DLayout)

        self._legacy_props = props

        return SweepProps(self, self._legacy_props)

    @props.setter
    def props(self, value: dict) -> None:
        # Merge with existing props to support partial updates
        current_props = dict(self.props) if self._legacy_props else {}
        current_props.update(value)

        props = SweepProps(self, current_props)

        self.update(props)

    @property
    @deprecated("Convert to string the object instead.")
    def combined_name(self) -> str:
        """Compute the name : sweep_name string.

        Returns
        -------
        str

        Examples
        --------
        >>> from ansys.aedt.core import Hfss3dLayout
        >>> hfss = Hfss3dLayout()
        >>> setup = hfss.create_setup()
        >>> sweep = setup.add_sweep()
        >>> sweep.combined_name

        """
        return str(self)

    @property
    def is_solved(self) -> bool:
        """Verify if solutions are available for the sweep.

        Returns
        -------
        bool
            `True` if solutions are available.

        Examples
        --------
        >>> from ansys.aedt.core import Hfss3dLayout
        >>> hfss = Hfss3dLayout()
        >>> setup = hfss.create_setup()
        >>> sweep = setup.add_sweep()
        >>> sweep.is_solved

        """
        combined_name = str(self)
        expressions = [i for i in self._app.post.available_report_quantities(solution=combined_name)]
        sol = self._app.post.reports_by_category.standard(expressions=expressions[0], setup=combined_name)
        if identify_setup(dict(self.props)):
            sol.domain = "Time"
        return True if sol.get_solution_data() else False

    @pyaedt_function_handler()
    def change_type(self, sweep_type: str) -> bool:
        """Change the type of the sweep.

        Parameters
        ----------
        sweep_type : str
            Type of the sweep. Options are ``"Interpolating"`` and ``"Discrete"``.
            The default is ``"Interpolating"``.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        Examples
        --------
        >>> from ansys.aedt.core.modules.solve_sweeps import SweepHFSS3DLayout
        >>> obj = SweepHFSS3DLayout()
        >>> obj.change_type(sweep_type=1)

        """
        if sweep_type == "Interpolating":
            self.props["FastSweep"] = True
        elif sweep_type == "Discrete":
            self.props["FastSweep"] = False
        else:
            raise AttributeError("Allowed sweep type options are 'Interpolating' and 'Discrete'.")
        return self.update()

    @pyaedt_function_handler()
    def set_save_fields(self, save_fields: bool, save_rad_fields: bool = False) -> bool:
        """Choose whether to save fields.

        Parameters
        ----------
        save_fields : bool
            Whether to save the fields.
        save_rad_fields : bool, optional
            Whether to save the radiating fields. The default is ``False``.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        Examples
        --------
        >>> from ansys.aedt.core.modules.solve_sweeps import SweepHFSS3DLayout
        >>> obj = SweepHFSS3DLayout()
        >>> obj.set_save_fields(save_fields=True)

        """
        self.props["GenerateSurfaceCurrent"] = save_fields
        self.props["SaveRadFieldsOnly"] = save_rad_fields
        return self.update()

    @pyaedt_function_handler()
    def add_subrange(
        self, range_type: str, start: float, end: float = None, count: float = None, unit: str = "GHz"
    ) -> bool:
        """Add a subrange to the sweep.

        Parameters
        ----------
        range_type : str
            Type of the subrange. Options are ``"LinearCount"``, ``"SinglePoint"``,
            ``"LinearStep"``, and ``"LogScale"``.
        start : float
            Starting frequency.
        end : float, optional
            Stopping frequency. The default is ``None``. A value is
            required for these subranges: ``"LinearCount"``, ``"LinearStep"``, and ``"LogScale"``.
        count : int or float, optional
            Frequency count or frequency step. The default is ``None``.
            A value is required for these subranges: ``"LinearCount"``, ``"LinearStep"``,
            and ``"LogScale"``.
        unit : str
            Unit of the frequency. For example, ``"MHz`` or ``"GHz"``. The default is ``"GHz"``.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        Examples
        --------
        >>> from ansys.aedt.core.modules.solve_sweeps import SweepHFSS3DLayout
        >>> obj = SweepHFSS3DLayout()
        >>> obj.add_subrange(range_type=1, start=[0, 0, 0])

        """
        try:
            if range_type == "SinglePoint" and self.props["FreqSweepType"] == "kInterpolating":
                raise AttributeError("'SinglePoint is allowed only when sweep_type is 'Discrete'.'")
            if range_type == "LinearCount" or range_type == "LinearStep" or range_type == "LogScale":
                if not end or not count:
                    raise AttributeError("Parameters 'end' and 'count' must be present.")

            if range_type == "LinearCount":
                sweep_range = " LINC " + str(start) + unit + " " + str(end) + unit + " " + str(count)
            elif range_type == "LinearStep":
                sweep_range = " LIN " + str(start) + unit + " " + str(end) + unit + " " + str(count) + unit
            elif range_type == "LogScale":
                sweep_range = " DEC " + str(start) + unit + " " + str(end) + unit + " " + str(count)
            elif range_type == "SinglePoint":
                sweep_range = " " + str(start) + unit
            else:
                raise AttributeError(
                    'Allowed range_type are "LinearCount", "SinglePoint", "LinearStep", and "LogScale".'
                )
            self.props["Sweeps"]["Data"] += sweep_range
            return self.update()
        except Exception:
            return False

    @pyaedt_function_handler()
    def change_range(
        self, range_type: str, start: float, end: float = None, count: float = None, unit: str = "GHz"
    ) -> bool:
        """Change the range of the sweep.

        Parameters
        ----------
        range_type : str
            Type of the subrange. Options are ``"LinearCount"``, ``"SinglePoint"``,
            ``"LinearStep"``, and ``"LogScale"``.
        start : float
            Starting frequency.
        end : float, optional
            Stopping frequency. The default is ``None``.  A value is required
            for these subranges: ``"LinearCount"``, ``"LinearStep"``, and ``"LogScale"``.
        count : int or float, optional
            Frequency count or frequency step. The default is ``None``.
            A value is required for these subranges: ``"LinearCount"``,
            ``"LinearStep"``, and ``"LogScale"``.
        unit : str, optional
            Unit of the frequency. For example, ``"MHz`` or ``"GHz"``. The default is ``"GHz"``.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        Examples
        --------
        >>> from ansys.aedt.core.modules.solve_sweeps import SweepHFSS3DLayout
        >>> obj = SweepHFSS3DLayout()
        >>> obj.change_range(range_type=1, start=[0, 0, 0])

        """
        if range_type == "LinearCount":
            sweep_range = "LINC " + str(start) + unit + " " + str(end) + unit + " " + str(count)
        elif range_type == "LinearStep":
            sweep_range = "LIN " + str(start) + unit + " " + str(end) + unit + " " + str(count) + unit
        elif range_type == "LogScale":
            sweep_range = "DEC " + str(start) + unit + " " + str(end) + unit + " " + str(count)
        elif range_type == "SinglePoint":
            sweep_range = str(start) + unit
        else:
            raise AttributeError('Allowed range_type are "LinearCount", "SinglePoint", "LinearStep", and "LogScale".')
        self.props["Sweeps"]["Data"] = sweep_range
        return self.update()

    @pyaedt_function_handler()
    def create(self) -> bool:
        """Create a sweep.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        Examples
        --------
        >>> from ansys.aedt.core.modules.solve_sweeps import SweepHFSS3DLayout
        >>> obj = SweepHFSS3DLayout()
        >>> obj.create()

        """
        self._app.oanalysis.AddSweep(self.setup_name, self._get_args())
        return True

    @pyaedt_function_handler()
    def update(self, props: dict | None = None) -> bool:
        """Update the sweep.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        Examples
        --------
        >>> from ansys.aedt.core.modules.solve_sweeps import SweepHFSS3DLayout
        >>> obj = SweepHFSS3DLayout()
        >>> obj.update()

        """
        if props is None:
            props = dict(self.props)
        self._app.oanalysis.EditSweep(self._setup.name, self.name, self._get_args(props))
        self._legacy_props = dict(props)
        return True

    @pyaedt_function_handler()
    def _get_args(self, props=None):
        """Retrieve properties.

        Parameters
        ----------
        props : dict
             Dictionary of the properties. The default is ``None``, in which case
             the default properties are retrieved.

        Returns
        -------
        dict
            Dictionary of the properties.

        """
        if props is None:
            props = dict(self.props)
        arg = ["NAME:" + self.name]
        _dict2arg(props, arg)
        return arg


class SweepMatrix(SweepCommon):
    """Initializes, creates, and updates sweeps in Q3D.

    Parameters
    ----------
    setup : :class 'from ansys.aedt.core.modules.solve_setup.Setup'
        Setup used for the analysis.
    name : str
        Name of the sweep.
    sweep_type : str, optional
        Type of the sweep. Options are ``"Fast"``, ``"Interpolating"``,
        and ``"Discrete"``. The default is ``"Interpolating"``.
    props : dict
        Dictionary of the properties.  The default is ``None``, in which case
        the default properties are retrieved.

    Examples
    --------
    >>> from ansys.aedt.core.modules.solve_sweeps import SweepMatrix
    >>> obj = SweepMatrix()

    """

    def __init__(self, setup, name: str, sweep_type: str = "Interpolating", props=None) -> None:
        self._app = setup  # TODO: Remove sweep_type as an argument as it can be passed in props
        self.setup_name = setup.name
        self.name = name
        self.props = copy.deepcopy(SweepQ3D)
        if props:
            for key, value in props.items():
                if key in self.props:
                    self.props[key] = value
        else:
            self.props["Type"] = sweep_type
            if sweep_type == "Discrete":
                self.props["IsEnabled"] = True
                self.props["RangeType"] = "LinearCount"
                self.props["RangeStart"] = "2.5GHz"
                self.props["RangeStep"] = "1GHz"
                self.props["RangeEnd"] = "7.5GHz"
                self.props["SaveSingleField"] = False
                self.props["RangeSamples"] = 3
                self.props["RangeCount"] = 401
                self.props["SaveFields"] = False
                self.props["SaveRadFields"] = False
                self.props["SweepRanges"] = []
            else:
                self.props["IsEnabled"] = True
                self.props["RangeType"] = "LinearStep"
                self.props["RangeStart"] = "1GHz"
                self.props["RangeStep"] = "1GHz"
                self.props["RangeEnd"] = "20GHz"
                self.props["SaveFields"] = False
                self.props["SaveRadFields"] = False
                self.props["InterpTolerance"] = 0.5
                self.props["InterpMaxSolns"] = 50
                self.props["InterpMinSolns"] = 0
                self.props["InterpMinSubranges"] = 1

    @property
    def is_solved(self) -> bool:
        """Verify if solutions are available for given sweep.

        Returns
        -------
        bool
            `True` if solutions are available.

        Examples
        --------
        >>> from ansys.aedt.core.modules.solve_sweeps import SweepMatrix
        >>> obj = SweepMatrix()
        >>> obj.is_solved

        """
        sol = self._app._app.post.reports_by_category.standard(setup=f"{self.setup_name} : {self.name}")
        return True if sol.get_solution_data() else False

    @property
    def frequencies(self) -> list[float]:
        """List of all frequencies of the active sweep.

        To see values, the project must be saved and solved.

        Returns
        -------
        list of float
            Frequency points.

        Examples
        --------
        >>> from ansys.aedt.core.modules.solve_sweeps import SweepMatrix
        >>> obj = SweepMatrix()
        >>> obj.frequencies

        """
        sol = self._app._app.post.reports_by_category.standard(setup=f"{self.setup_name} : {self.name}")
        soldata = sol.get_solution_data()
        if soldata and "Freq" in soldata.intrinsics:
            return [Quantity(i, soldata.units_sweeps["Freq"]) for i in soldata.intrinsics["Freq"]]
        return []

    @property
    def basis_frequencies(self) -> list[float]:
        """Get the list of all frequencies that have fields available.

        The project has to be saved and solved to see values.

        Returns
        -------
        list of float
            Frequency points.

        Examples
        --------
        >>> from ansys.aedt.core.modules.solve_sweeps import SweepMatrix
        >>> obj = SweepMatrix()
        >>> obj.basis_frequencies

        """
        solutions_file = os.path.join(self._app._app.results_directory, f"{self._app._app.design_name}.asol")
        fr = []
        if os.path.exists(solutions_file):
            solutions = load_entire_aedt_file(solutions_file)
            for k, v in solutions.items():
                if "SolutionBlock" in k and "SolutionName" in v and v["SolutionName"] == self.name and "Fields" in v:
                    try:  # pragma: no cover
                        new_list = [float(i) for i in v["Fields"]["IDDblMap"][1::2]]
                        new_list.sort()
                        new_list = unit_converter(
                            values=new_list,
                            unit_system="Freq",
                            input_units="Hz",
                            output_units=self._app._app.units.frequency,
                        )
                        fr.append(new_list)
                    except (KeyError, NameError, IndexError):
                        pass

        count = 0
        for el in self._app._app.setups:
            if el.name == self.setup_name:
                for sweep in el.sweeps:
                    if sweep.name == self.name:
                        return fr[count] if len(fr) >= count + 1 else []
            else:
                for sweep in el.sweeps:
                    if sweep.name == self.name:
                        count += 1
        return []

    @pyaedt_function_handler()
    def add_subrange(
        self,
        range_type: str,
        start: float,
        end: float = None,
        count: float = None,
        unit: str = "GHz",
        clear: bool = False,
        save_single_fields: bool = False,
    ) -> bool:
        """Add a subrange to the sweep.

        Parameters
        ----------
        range_type : str
            Type of the subrange. Options are ``"LinearCount"``,
            ``"LinearStep"``, and ``"LogScale"``.
        start : float
            Starting frequency.
        end : float
            Stopping frequency. The default is ``None``.
        count : int or float
            Frequency count or frequency step. The default is ``None``.
        unit : str, optional
            Frequency units.
        clear : bool, optional
            Whether to replace the subrange. The default is ``False``, in which case
            subranges are appended.
        save_single_fields : bool, optional
            Whether to save the fields of the single point. The default is ``False``.
            This parameter is used only for ``range_type="SinglePoints"``.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        Examples
        --------
        >>> from ansys.aedt.core import Q3d
        >>> app = Q3d()
        >>> setup = app.create_setup()
        >>> setup.create_single_point_sweep(save_single_field=[True, False, False], freq=[6, 10, 12], unit="GHz")

        """
        if clear:
            self.props["RangeType"] = range_type
            self.props["RangeStart"] = str(start) + unit
            if range_type == "LinearCount":
                self.props["RangeEnd"] = str(end) + unit
                self.props["RangeCount"] = count
            elif range_type == "LinearStep":
                self.props["RangeEnd"] = str(end) + unit
                self.props["RangeStep"] = str(count) + unit
            elif range_type == "LogScale":
                self.props["RangeEnd"] = str(end) + unit
                self.props["RangeSamples"] = count
            self.props["SweepRanges"] = {"Subrange": []}
            return self.update()
        sweep_range = {"RangeType": range_type, "RangeStart": str(start) + unit}
        if range_type == "LinearCount":
            sweep_range["RangeEnd"] = str(end) + unit
            sweep_range["RangeCount"] = count
        elif range_type == "LinearStep":
            sweep_range["RangeEnd"] = str(end) + unit
            sweep_range["RangeStep"] = str(count) + unit
        elif range_type == "LogScale":
            sweep_range["RangeEnd"] = str(end) + unit
            sweep_range["RangeSamples"] = count
        elif range_type == "SinglePoints":
            sweep_range["RangeEnd"] = str(start) + unit
            sweep_range["SaveSingleField"] = save_single_fields

        if not self.props.get("SweepRanges") or not self.props["SweepRanges"].get("Subrange"):
            self.props["SweepRanges"] = {"Subrange": []}
        self.props["SweepRanges"]["Subrange"].append(sweep_range)
        return self.update()

    @pyaedt_function_handler()
    def create(self) -> bool:
        """Create a sweep.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        Examples
        --------
        >>> from ansys.aedt.core.modules.solve_sweeps import SweepMatrix
        >>> obj = SweepMatrix()
        >>> obj.create()

        """
        self._app.oanalysis.InsertSweep(self.setup_name, self._get_args())
        return True

    @pyaedt_function_handler()
    def update(self) -> bool:
        """Update the sweep.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        Examples
        --------
        >>> from ansys.aedt.core.modules.solve_sweeps import SweepMatrix
        >>> obj = SweepMatrix()
        >>> obj.update()

        """
        self._app.oanalysis.EditSweep(self.setup_name, self.name, self._get_args())

        return True

    @pyaedt_function_handler()
    def _get_args(self, props=None):
        """Get properties.

        Parameters
        ----------
        props : dict
             Dictionary of the properties. The default is ``None``, in which case
             the default properties are retrieved.

        Returns
        -------
        dict
            Dictionary of the properties.

        """
        if props is None:
            props = self.props
        arg = ["NAME:" + self.name]
        _dict2arg(props, arg)
        return arg


class SweepMaxwellEC(SweepCommon):
    """Initializes, creates, and updates sweeps in Maxwell Eddy Current.

    Parameters
    ----------
    setup : :class 'from ansys.aedt.core.modules.solve_setup.Setup'
        Setup used for the analysis.
    name : str
        Name of the sweep.
    sweep_type : str, optional
        Type of the sweep. Options are ``"LinearStep"``, ``"LinearCount"``,
         ``"LogScale"`` and ``"SinglePoints"``. The default is ``"LinearStep"``.
    props : dict
        Dictionary of the properties.  The default is ``None``, in which case
        the default properties are retrieved.

    Examples
    --------
    >>> from ansys.aedt.core.modules.solve_sweeps import SweepMaxwellEC
    >>> obj = SweepMaxwellEC()

    """

    def __init__(self, setup, sweep_type: str = "LinearStep", props=None) -> None:
        self._setup = setup
        self.setup_name = setup.name
        self.props = {}
        if props:
            self.props = props
        else:
            self.props = copy.deepcopy(SweepEddyCurrent)
            self.props["RangeType"] = sweep_type
            if sweep_type == "LinearStep":
                self.props["RangeStep"] = "10Hz"
            elif sweep_type == "LinearCount":
                self.props["RangeCount"] = "10"
            elif sweep_type == "LogScale":
                self.props["RangeSamples"] = "2"
            elif sweep_type == "SinglePoints":
                self.props["RangeEnd"] = self.props["RangeStart"]

    @property
    def name(self) -> str:
        """Setup name.

        Examples
        --------
        >>> from ansys.aedt.core.modules.solve_sweeps import SweepMaxwellEC
        >>> obj = SweepMaxwellEC()
        >>> obj.name

        """
        return self.setup_name

    @property
    def is_solved(self) -> bool:
        """Verify if solutions are available for the sweep.

        Returns
        -------
        bool
            `True` if solutions are available.

        Examples
        --------
        >>> from ansys.aedt.core.modules.solve_sweeps import SweepMaxwellEC
        >>> obj = SweepMaxwellEC()
        >>> obj.is_solved

        """
        expressions = [
            i for i in self._setup._app.post.available_report_quantities(solution=self._setup._app.nominal_sweep)
        ]
        sol = self._setup._app.post.reports_by_category.standard(
            expressions=expressions[0], setup=self._setup._app.nominal_sweep
        )
        if identify_setup(self.props):
            sol.domain = "Time"
        return True if sol.get_solution_data() else False

    @property
    def frequencies(self) -> list[float]:
        """List of all frequencies of the active sweep.

        To see values, the project must be saved and solved.

        Returns
        -------
        list of float
            Frequency points.

        Examples
        --------
        >>> from ansys.aedt.core.modules.solve_sweeps import SweepMaxwellEC
        >>> obj = SweepMaxwellEC()
        >>> obj.frequencies

        """
        expressions = [
            i for i in self._setup._app.post.available_report_quantities(solution=self._setup._app.nominal_sweep)
        ]
        sol = self._setup._app.post.reports_by_category.standard(
            expressions=expressions[0], setup=self._setup._app.nominal_sweep
        )
        soldata = sol.get_solution_data()
        if soldata and "Freq" in soldata.intrinsics:
            return [Quantity(i, soldata.units_sweeps["Freq"]) for i in soldata.intrinsics["Freq"]]
        return []

    @pyaedt_function_handler()
    def create(self, properties: dict = None) -> bool:
        """Create a Maxwell Eddy Current sweep.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        Examples
        --------
        >>> from ansys.aedt.core.modules.solve_sweeps import SweepMaxwellEC
        >>> obj = SweepMaxwellEC()
        >>> obj.create()

        """
        self._app.oanalysis.EditSetup(self.setup_name, self._get_args(properties if properties else self._setup.props))
        return True

    @pyaedt_function_handler()
    def update(self) -> bool:
        """Update a Maxwell Eddy Current sweep.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        Examples
        --------
        >>> from ansys.aedt.core.modules.solve_sweeps import SweepMaxwellEC
        >>> obj = SweepMaxwellEC()
        >>> obj.update()

        """
        self._app.oanalysis.EditSetup(self.setup_name, self._get_args(self._setup.props))
        return True

    @pyaedt_function_handler()
    def delete(self) -> bool:
        """Delete a Maxwell Eddy Current sweep.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        Examples
        --------
        >>> from ansys.aedt.core.modules.solve_sweeps import SweepMaxwellEC
        >>> obj = SweepMaxwellEC()
        >>> obj.delete()

        """
        setup_sweeps = self._setup.props["SweepRanges"]["Subrange"].copy()
        if isinstance(self._setup.props["SweepRanges"]["Subrange"], list):
            for sweep in setup_sweeps:
                if self.props == sweep:
                    self._setup.props["SweepRanges"]["Subrange"].remove(self.props)
                    [self._setup._sweeps.remove(s) for s in self._setup._sweeps if s.props == sweep]
        else:
            pass
        self._setup.update()
        return True

    @pyaedt_function_handler()
    def _get_args(self, props=None):
        """Get arguments.

        Parameters
        ----------
        props : dict, optional
             Dictionary of the properties. The default is ``None``, in which
             case the default properties are retrieved.

        Returns
        -------
        dict
            Dictionary of the properties.

        """
        if props is None:
            props = self.props
        arg = ["NAME:" + self.setup_name]
        _dict2arg(props, arg)
        return arg
