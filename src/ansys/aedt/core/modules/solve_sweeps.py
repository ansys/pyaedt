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

from ansys.aedt.core.internal.errors import AEDTRuntimeError

if sys.version_info >= (3, 13):
    from warnings import deprecated
else:
    from typing_extensions import deprecated

import copy
from difflib import SequenceMatcher
from pathlib import Path
from typing import TYPE_CHECKING
from typing import Any

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
from ansys.aedt.core.modules.setup_templates import SweepSiwave

if TYPE_CHECKING:
    from ansys.aedt.core.modules.solve_setup import Setup3DLayout
    from ansys.aedt.core.modules.solve_setup import SetupHFSS
    from ansys.aedt.core.modules.solve_setup import SetupQ3D


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


@pyaedt_function_handler()
def get_sweep_type(sweep_type: str) -> str:
    """Convert sweep type to AEDT sweep type accepted key.

    Parameters
    ----------
    sweep_type : str
        Sweep type.

    Returns
    -------
    str
        AEDT sweep type accepted key.

    Examples
    --------
    >>> from ansys.aedt.core.modules.solve_sweeps import get_sweep_type
    >>> get_sweep_type("interpolating")

    """
    if SequenceMatcher(None, sweep_type.lower(), "interpolating").ratio() > 0.8:
        sweep_type = "kInterpolating"
    elif SequenceMatcher(None, sweep_type.lower(), "discrete").ratio() > 0.8:
        sweep_type = "kDiscrete"
    elif SequenceMatcher(None, sweep_type.lower(), "fast").ratio() > 0.8:
        sweep_type = "kBroadbandFast"
    else:
        sweep_type = "kInterpolating"

    return sweep_type


class SweepCommon(BinaryTreeNode, PyAedtBase):
    """Common base class for sweeps.

    Parameters
    ----------
    setup : Setup3DLayout, SetupHFSS, or SetupQ3D
        Setup that owns the sweep.
    name : str
        Name of the sweep.

    Examples
    --------
    >>> from ansys.aedt.core import Hfss
    >>> hfss = Hfss()
    >>> s = hfss.create_setup()
    >>> sweep = s.add_sweep()

    """

    def __getitem__(self, key: str) -> Any:
        """Return a sweep property by key."""
        return self.props[key]

    def __setitem__(self, key: str, value: Any) -> None:
        """Set a sweep property by key."""
        self.props[key] = value

    def __repr__(self) -> str:
        return f"{self.setup_name} : {self.name}"

    def __str__(self) -> str:
        return f"{self.setup_name} : {self.name}"

    def __init__(self, setup: Setup3DLayout | SetupHFSS | SetupQ3D, name: str) -> None:
        self._setup: Setup3DLayout | SetupHFSS | SetupQ3D = setup
        self._app: Any = self._setup._app

        self._name = name

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
            cc_names = self._app.get_oo_name(self._setup.child_object)
            if self._name in cc_names:
                child_object = self._app.get_oo_object(self._setup.child_object, self._name)
        return child_object

    @property
    def name(self) -> str:
        """Name of the sweep.

        Returns
        -------
        str
            Sweep type.

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
        sweep_names = self._setup.sweep_names
        if name in sweep_names:
            raise ValueError(f"Name {name} already assigned in the design.")

        self._app.oanalysis.RenameSweep(self.setup_name, self.name, str(name))

        # Reset object
        self.__child_object = None
        object.__setattr__(self, "_name", name)
        object.__setattr__(self, "_tree_node_initialized", False)
        object.__setattr__(self, "_props", None)
        object.__setattr__(self, "_children_loaded", False)

    @property
    def sweep_type(self) -> str | None:
        """Sweep type.

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
        sweep_type = self.child_object.Type if "Type" in dir(self.child_object) else None
        return sweep_type

    @sweep_type.setter
    def sweep_type(self, sweep_type):
        if "FreqSweepType" in self.props:
            sweep_type = get_sweep_type(sweep_type)
            self.props["FreqSweepType"] = sweep_type
        elif "Type" in self.props:
            self.props["Type"] = sweep_type

    @property
    def setup_name(self) -> str:
        """Setup name."""
        return self._setup.name

    @property
    def props(self) -> SweepProps:
        """Properties of the sweep, implemented by concrete sweep classes."""
        raise NotImplementedError


class SweepHFSS(SweepCommon):
    """Initializes, creates, and updates sweeps in HFSS.

    Parameters
    ----------
    setup : :class 'from ansys.aedt.core.modules.solve_setup.SetupHFSS'
        Setup to use for the analysis.
    name : str
        Name of the sweep.
    props : dict, optional
        Dictionary of the properties. The default is ``None``, in which
        case the default properties are retrieved.

    Examples
    --------
    >>> from ansys.aedt.core import Hfss
    >>> hfss = Hfss()
    >>> s = hfss.create_setup()
    >>> sweep = s.add_sweep()

    """

    def __init__(self, setup: SetupHFSS, name: str, props=None) -> None:
        self._legacy_props = copy.deepcopy(props) if props else {}
        super().__init__(setup, name)

    @property
    def props(self) -> SweepProps:
        """Properties of the sweep.

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
            if (
                "AnalysisSetup" in self._app.design_properties
                and "SolveSetups" in self._app.design_properties["AnalysisSetup"]
            ):
                design_property_data = self._app.design_properties["AnalysisSetup"]["SolveSetups"]
                setup_name = self._setup.name
                if (
                    setup_name in design_property_data
                    and "Sweeps" in design_property_data[setup_name]
                    and self._name in design_property_data[setup_name]["Sweeps"]
                ):
                    props = design_property_data[setup_name]["Sweeps"][self._name]
                    if "ID" in props:
                        del props["ID"]
                else:
                    props = copy.deepcopy(SweepHfss3D)
            else:  # pragma: no cover
                props = copy.deepcopy(SweepHfss3D)

        self._legacy_props = props

        return SweepProps(self, self._legacy_props)

    @props.setter
    def props(self, value: dict) -> None:
        # Merge with existing props to support partial updates
        current_props = self.props.to_dict() if self._legacy_props else {}
        current_props.update(value)

        props = SweepProps(self, current_props)

        self.update(props)

    @property
    def is_solved(self) -> bool:
        """Verify if solutions are available for the sweep.

        Returns
        -------
        bool
            `True` if solutions are available.

        Examples
        --------
        >>> from ansys.aedt.core import Hfss
        >>> hfss = Hfss()
        >>> setup = hfss.create_setup()
        >>> sweep = setup.add_sweep()
        >>> sweep.is_solved

        """
        combined_name = str(self)
        sol = self._app.post.reports_by_category.standard(setup=combined_name)
        if identify_setup(self.props.to_dict()):
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
        >>> from ansys.aedt.core import Hfss
        >>> hfss = Hfss()
        >>> setup = hfss.create_setup()
        >>> sweep = setup.add_sweep()
        >>> sweep.frequencies

        """
        combined_name = str(self)
        sol = self._app._app.post.reports_by_category.standard(setup=combined_name)
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
        >>> from ansys.aedt.core import Hfss
        >>> hfss = Hfss()
        >>> setup = hfss.create_setup()
        >>> sweep = setup.add_sweep()
        >>> sweep.frequencies

        """
        solutions_file = Path(self._app.results_directory) / f"{self._app.design_name}.asol"
        fr = []
        if solutions_file.is_file():
            solutions = load_entire_aedt_file(str(solutions_file))
            for k, v in solutions.items():
                if "SolutionBlock" in k and "SolutionName" in v and v["SolutionName"] == self.name and "Fields" in v:
                    try:
                        new_list = [float(i) for i in v["Fields"]["IDDblMap"][1::2]]

                        new_list.sort()
                        new_list = unit_converter(
                            values=new_list,
                            unit_system="Freq",
                            input_units="Hz",
                            output_units=self._app.units.frequency,
                        )
                        fr.append(new_list)
                    except (KeyError, NameError, IndexError):
                        pass

        count = 0
        for setup_name, setup in self._app.setups.items():
            if setup_name == self.setup_name:
                for sweep in setup.sweeps:
                    if sweep == self.name:
                        return fr[count] if len(fr) >= count + 1 else []
            else:
                for sweep in setup.sweeps:
                    if sweep == self.name:
                        count += 1
        return []

    @pyaedt_function_handler()
    def create(self) -> SweepHFSS:
        """Create a sweep.

        Returns
        -------
        :class 'from ansys.aedt.core.modules.solve_sweeps.SweepHFSS'

        Examples
        --------
        >>> from ansys.aedt.core import Hfss3dLayout
        >>> hfss = Hfss3dLayout()
        >>> setup = hfss.create_setup()
        >>> sweep = setup.add_sweep()

        """
        self._app.oanalysis.InsertFrequencySweep(self.setup_name, self._get_args())

        # GetObjData is available for some objects in 2026R1.
        self._has_getobject = _has_get_obj_data(self._child_object)

        return self

    @pyaedt_function_handler()
    def update(self, props: dict | None = None) -> bool:
        """Update the sweep.

        Parameters
        ----------
        props : dict, optional
            New properties to update. The  default is ``None``, in which case it uses the current properties.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        Examples
        --------
        >>> from ansys.aedt.core import Hfss
        >>> hfss = Hfss()
        >>> setup = hfss.create_setup()
        >>> sweep = setup.add_sweep()
        >>> props = dict(sweep.props)
        >>> sweep.update(props)

        """
        if props is None:
            props = self.props.to_dict()

        arg = self._get_args(props=props)

        self._app.oanalysis.EditFrequencySweep(self.setup_name, self.name, arg)

        if not self._has_getobject:
            self._legacy_props = dict(props)

        return True

    @pyaedt_function_handler()
    def delete(self) -> bool:
        """Delete actual Setup.

        Returns
        -------
        bool
            ``True`` if setup is deleted. ``False`` if it failed.

        Examples
        --------
        >>> from ansys.aedt.core import Hfss
        >>> app = Hfss()
        >>> setup = app.create_setup()
        >>> sweep = setup.add_sweep()
        >>> sweep.delete()

        """
        self._app.oanalysis.DeleteSweep(self._setup.name, self.name)
        return True

    @pyaedt_function_handler()
    def add_subrange(
        self,
        range_type: str,
        start: float | int,
        end: float | int | None = None,
        count: float | int | None = None,
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
        start : float or int
            Starting frequency.
        end : float or int, optional
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
        >>> from ansys.aedt.core import Hfss
        >>> hfss = Hfss()
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

        props = self.props.to_dict()

        if clear:
            props["RangeType"] = range_type
            props["RangeStart"] = str(start) + unit
            if range_type == "LinearCount":
                props["RangeEnd"] = str(end) + unit
                props["RangeCount"] = count
            elif range_type == "LinearStep":
                props["RangeEnd"] = str(end) + unit
                props["RangeStep"] = str(count) + unit
            elif range_type == "LogScale":
                props["RangeEnd"] = str(end) + unit
                props["RangeSamples"] = count
            elif range_type == "SinglePoints":
                props["RangeEnd"] = str(start) + unit
                props["SaveSingleField"] = save_single_fields
            props["SweepRanges"] = {"Subrange": []}
            return self.update(props)

        interval = {"RangeType": range_type, "RangeStart": str(start) + unit}
        if range_type == "LinearCount":
            interval["RangeEnd"] = str(end) + unit
            interval["RangeCount"] = count
        elif range_type == "LinearStep":
            interval["RangeEnd"] = str(end) + unit
            interval["RangeStep"] = str(count) + unit
        elif range_type == "LogScale":
            interval["RangeEnd"] = str(end) + unit
            if "RangeCount" in props:
                interval["RangeCount"] = props["RangeCount"]
            else:
                interval["RangeCount"] = count
            interval["RangeSamples"] = count
        elif range_type == "SinglePoints":
            if self.sweep_type == "Discrete":
                interval["RangeEnd"] = str(start) + unit
                interval["SaveSingleField"] = save_single_fields
            else:
                raise AEDTRuntimeError("Sweep type must be Discrete.")

        if not props.get("SweepRanges", None):
            props["SweepRanges"] = {"Subrange": []}

        if not isinstance(props["SweepRanges"]["Subrange"], list):
            props["SweepRanges"]["Subrange"] = [props["SweepRanges"]["Subrange"]]
        props["SweepRanges"]["Subrange"].append(interval)

        return self.update(props)

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
    setup : :class 'from ansys.aedt.core.modules.solve_setup.Setup3DLayout'
        Setup to use for the analysis.
    name : str
        Name of the sweep.
    props : dict, optional
        Dictionary of the properties. The default is ``None``, in which
        case the default properties are retrieved.

    Examples
    --------
    >>> from ansys.aedt.core import Hfss3dLayout
    >>> app = Hfss3dLayout()
    >>> s = app.create_setup()
    >>> sweep = s.add_sweep()

    """

    def __init__(self, setup: Setup3DLayout, name: str, props=None) -> None:
        self._legacy_props = copy.deepcopy(props) if props else {}
        super().__init__(setup, name)

    @property
    def props(self) -> SweepProps:
        """Properties of the sweep.

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
                setup_type = self._setup.solver_type
                if setup_type and "SIwave" in setup_type:
                    props = copy.deepcopy(SweepSiwave)
                else:
                    props = copy.deepcopy(Sweep3DLayout)

        self._legacy_props = props

        return SweepProps(self, self._legacy_props)

    @props.setter
    def props(self, value: dict) -> None:
        # Merge with existing props to support partial updates
        current_props = self.props.to_dict() if self._legacy_props else {}
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
        if not expressions:
            return False
        sol = self._app.post.reports_by_category.standard(expressions=expressions[0], setup=combined_name)
        if identify_setup(self.props.to_dict()):
            sol.domain = "Time"
        return True if sol.get_solution_data() else False

    @pyaedt_function_handler()
    def create(self) -> bool:
        """Create a sweep.

        Returns
        -------
        :class 'from ansys.aedt.core.modules.solve_sweeps.SweepHfss3DLayout'

        Examples
        --------
        >>> from ansys.aedt.core import Hfss3dLayout
        >>> hfss = Hfss3dLayout()
        >>> setup = hfss.create_setup()
        >>> sweep = setup.add_sweep()

        """
        self._app.oanalysis.AddSweep(self.setup_name, self._get_args())

        # GetObjData is available for some objects in 2026R1.
        self._has_getobject = _has_get_obj_data(self._child_object)

        return self

    @pyaedt_function_handler()
    def update(self, props: dict | None = None) -> bool:
        """Update the sweep.

        Parameters
        ----------
        props : dict, optional
            New properties to update. The  default is ``None``, in which case it uses the current properties.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        Examples
        --------
        >>> from ansys.aedt.core import Hfss3dLayout
        >>> hfss = Hfss3dLayout()
        >>> setup = hfss.create_setup()
        >>> sweep = setup.add_sweep()
        >>> props = dict(sweep.props)
        >>> sweep.update(props)

        """
        if props is None:
            props = self.props.to_dict()
        self._app.oanalysis.EditSweep(self._setup.name, self.name, self._get_args(props))

        if not self._has_getobject:
            self._legacy_props = dict(props)

        return True

    @pyaedt_function_handler()
    def delete(self) -> bool:
        """Delete actual Setup.

        Returns
        -------
        bool
            ``True`` if setup is deleted. ``False`` if it failed.

        Examples
        --------
        >>> from ansys.aedt.core import Hfss3dLayout
        >>> app = Hfss3dLayout()
        >>> setup = app.create_setup()
        >>> sweep = setup.add_sweep()
        >>> sweep.delete()

        """
        self._app.oanalysis.DeleteSweep(self._setup.name, self.name)
        return True

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
        >>> from ansys.aedt.core import Hfss3dLayout
        >>> hfss = Hfss3dLayout()
        >>> setup = hfss.create_setup()
        >>> sweep = setup.add_sweep()
        >>> sweep.change_type(sweep_type="Interpolating")

        """
        sweep_type = get_sweep_type(sweep_type)
        props = self.props.to_dict()
        props["FreqSweepType"] = sweep_type
        return self.update(props)

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
        >>> from ansys.aedt.core import Hfss3dLayout
        >>> hfss = Hfss3dLayout()
        >>> setup = hfss.create_setup()
        >>> sweep = setup.add_sweep()
        >>> sweep.set_save_fields(save_fields=True)

        """
        self.props["GenerateSurfaceCurrent"] = save_fields
        self.props["SaveRadFieldsOnly"] = save_rad_fields
        return True

    @pyaedt_function_handler()
    def add_subrange(
        self,
        range_type: str,
        start: float | int,
        end: float | int | None = None,
        count: float | int | None = None,
        unit: str = "GHz",
    ) -> bool:
        """Add a subrange to the sweep.

        Parameters
        ----------
        range_type : str
            Type of the subrange. Options are ``"LinearCount"``, ``"SinglePoint"``,
            ``"LinearStep"``, and ``"LogScale"``.
        start : float or int
            Starting frequency.
        end : float or int, optional
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
        >>> from ansys.aedt.core import Hfss3dLayout
        >>> hfss = Hfss3dLayout()
        >>> setup = hfss.create_setup()
        >>> sweep = setup.add_sweep()
        >>> sweep.add_subrange(range_type="LinearCount", start=1, end=2, count=5)

        """
        props = self.props.to_dict()

        if range_type == "SinglePoint" and props["FreqSweepType"] == "kInterpolating":
            raise AttributeError("'SinglePoint' is allowed only when sweep_type is 'Discrete'.'")

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
            raise AttributeError('Allowed range_type are "LinearCount", "SinglePoint", "LinearStep", and "LogScale".')
        if "Sweeps" in props and "Data" in props["Sweeps"]:
            props["Sweeps"]["Data"] += sweep_range
        return self.update(props)

    @pyaedt_function_handler()
    def change_range(
        self,
        range_type: str,
        start: float | int,
        end: float | int | None = None,
        count: float | int | None = None,
        unit: str = "GHz",
    ) -> bool:
        """Change the range of the sweep.

        Parameters
        ----------
        range_type : str
            Type of the subrange. Options are ``"LinearCount"``, ``"SinglePoint"``,
            ``"LinearStep"``, and ``"LogScale"``.
        start : float or int
            Starting frequency.
        end : float or int, optional
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
        >>> from ansys.aedt.core import Hfss3dLayout
        >>> hfss = Hfss3dLayout()
        >>> setup = hfss.create_setup()
        >>> sweep = setup.add_sweep()
        >>> sweep.change_range(range_type="LinearCount", start=1, end=2, count=5)

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

        props = self.props.to_dict()
        props["Sweeps"]["Data"] = sweep_range
        return self.update(props)

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

        Examples
        --------
        >>> from ansys.aedt.core import Hfss3dLayout
        >>> hfss = Hfss3dLayout()
        >>> setup = hfss.create_setup()
        >>> sweep = setup.add_sweep()
        >>> sweep._get_args()

        """
        if props is None:
            props = self.props.to_dict()
        arg = ["NAME:" + self.name]
        _dict2arg(props, arg)
        return arg


class SweepMatrix(SweepCommon):
    """Create and manage frequency sweeps in Q3D and Q2D.

    Parameters
    ----------
    setup : :class:`ansys.aedt.core.modules.solve_setup.SetupQ3D`
        Setup that owns the sweep.
    name : str
        Name of the sweep.
    props : dict, optional
        Dictionary of the properties. The default is ``None``, in which
        case the default properties are retrieved.

    Examples
    --------
    >>> from ansys.aedt.core import Q3d
    >>> q3d = Q3d()
    >>> setup = q3d.create_setup()
    >>> sweep = setup.add_sweep(name="MySweep")

    """

    def __init__(self, setup: SetupQ3D, name: str, props: dict | None = None) -> None:
        self._legacy_props = copy.deepcopy(props) if props else {}
        super().__init__(setup, name)

    @property
    def props(self) -> SweepProps:
        """Properties of the sweep.

        Returns
        -------
        :class:`ansys.aedt.core.generic.props.Props`
            Sweep properties.

        Examples
        --------
        >>> from ansys.aedt.core import Q3d
        >>> q3d = Q3d()
        >>> setup = q3d.create_setup()
        >>> sweep = setup.add_sweep()
        >>> sweep.props

        """
        if self._legacy_props and not self._has_getobject:
            return SweepProps(self, self._legacy_props)

        if self._has_getobject:
            props = _get_obj_data(self._child_object) or copy.deepcopy(SweepQ3D)
        else:
            design_properties = self._app.design_properties or {}
            setup_data = design_properties.get("AnalysisSetup", {}).get("SolveSetups", {})
            sweep_data = setup_data.get(self._setup.name, {}).get("Sweeps", {}).get(self._name)
            props = copy.deepcopy(sweep_data) if sweep_data else copy.deepcopy(SweepQ3D)
            props.pop("ID", None)

        self._legacy_props = props
        return SweepProps(self, self._legacy_props)

    @props.setter
    def props(self, value: dict) -> None:
        """Update the sweep properties."""
        current_props = self.props.to_dict() if self._legacy_props else {}
        current_props.update(value)
        self.update(current_props)

    @property
    def is_solved(self) -> bool:
        """Check whether solutions are available for the sweep.

        Returns
        -------
        bool
            ``True`` if solutions are available, ``False`` otherwise.

        Examples
        --------
        >>> from ansys.aedt.core import Q3d
        >>> q3d = Q3d()
        >>> sweep = q3d.create_setup().add_sweep()
        >>> sweep.is_solved

        """
        sol = self._app.post.reports_by_category.standard(setup=str(self))
        return bool(sol.get_solution_data())

    @property
    def frequencies(self) -> list[float]:
        """List the frequency points of the sweep.

        The project must be saved and solved for frequency values to be available.

        Returns
        -------
        list of float
            Frequencies, or an empty list when no frequency data is available.

        Examples
        --------
        >>> from ansys.aedt.core import Q3d
        >>> q3d = Q3d()
        >>> sweep = q3d.create_setup().add_sweep()
        >>> sweep.frequencies

        """
        sol = self._app.post.reports_by_category.standard(setup=str(self))
        soldata = sol.get_solution_data()
        if soldata and "Freq" in soldata.intrinsics:
            return [Quantity(i, soldata.units_sweeps["Freq"]) for i in soldata.intrinsics["Freq"]]
        return []

    @pyaedt_function_handler()
    def add_subrange(
        self,
        range_type: str,
        start: float | int,
        end: float | int | None = None,
        count: float | int | None = None,
        unit: str = "GHz",
        clear: bool = False,
        save_single_fields: bool = False,
    ) -> bool:
        """Add a subrange to the sweep.

        Parameters
        ----------
        range_type : str
            Type of the subrange. Options are ``"LinearCount"``, ``"LinearStep"``,
            ``"LogScale"``, and ``"SinglePoints"``.
        start : float or int
            Starting frequency.
        end : float or int, optional
            Stopping frequency. Required for ``"LinearCount"``, ``"LinearStep"``,
            and ``"LogScale"`` ranges.
        count : float or int, optional
            Frequency count, frequency step, or number of samples, depending on
            ``range_type``. Required for ``"LinearCount"``, ``"LinearStep"``,
            and ``"LogScale"`` ranges.
        unit : str, optional
            Frequency unit. The default is ``"GHz"``.
        clear : bool, optional
            Whether to replace existing subranges. The default is ``False``, which
            appends the new subrange.
        save_single_fields : bool, optional
            Whether to save fields for a single point. Used only for
            ``range_type="SinglePoints"``. The default is ``False``.

        Returns
        -------
        bool
            ``True`` if the sweep update succeeds, ``False`` otherwise.

        Examples
        --------
        >>> from ansys.aedt.core import Q3d
        >>> q3d = Q3d()
        >>> setup = q3d.create_setup()
        >>> sweep = setup.add_sweep()
        >>> sweep.add_subrange("LinearCount", 1, 1.5, 5, "GHz")

        """
        if range_type in ("LinearCount", "LinearStep", "LogScale") and (end is None or count is None):
            raise AttributeError("Parameters 'end' and 'count' must be present.")

        props = self.props.to_dict()

        if clear:
            props["RangeType"] = range_type
            props["RangeStart"] = str(start) + unit
            if range_type == "LinearCount":
                props["RangeEnd"] = str(end) + unit
                props["RangeCount"] = count
            elif range_type == "LinearStep":
                props["RangeEnd"] = str(end) + unit
                props["RangeStep"] = str(count) + unit
            elif range_type == "LogScale":
                props["RangeEnd"] = str(end) + unit
                props["RangeSamples"] = count
            elif range_type == "SinglePoints":
                props["RangeEnd"] = str(start) + unit
                props["SaveSingleField"] = save_single_fields
            props["SweepRanges"] = {"Subrange": []}
            return self.update(props)

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

        if not props.get("SweepRanges") or not props["SweepRanges"].get("Subrange"):
            props["SweepRanges"] = {"Subrange": []}

        if (
            "SweepRanges" in props
            and "Subrange" in props["SweepRanges"]
            and not isinstance(props["SweepRanges"]["Subrange"], list)
        ):
            props["SweepRanges"]["Subrange"] = [props["SweepRanges"]["Subrange"]]

        props["SweepRanges"]["Subrange"].append(sweep_range)
        return self.update(props)

    @pyaedt_function_handler()
    def create(self) -> SweepMatrix:
        """Create a sweep.

        Returns
        -------
        :class:`ansys.aedt.core.modules.solve_sweeps.SweepMatrix`
            The created sweep.

        Examples
        --------
        >>> from ansys.aedt.core import Q3d
        >>> q3d = Q3d()
        >>> sweep = q3d.create_setup().add_sweep()
        >>> sweep.create()

        """
        self._app.oanalysis.InsertSweep(self.setup_name, self._get_args())
        self._has_getobject = _has_get_obj_data(self._child_object)
        return self

    @pyaedt_function_handler()
    def update(self, props: dict | SweepProps | None = None) -> bool:
        """Update the sweep.

        Parameters
        ----------
        props : dict, optional
            Properties to apply. If omitted, the current sweep properties are used.

        Returns
        -------
        bool
            ``True`` if the sweep update succeeds, ``False`` otherwise.

        Examples
        --------
        >>> from ansys.aedt.core import Q3d
        >>> q3d = Q3d()
        >>> sweep = q3d.create_setup().add_sweep()
        >>> sweep.update()

        """
        if props is None:
            props = self.props.to_dict()
        elif isinstance(props, SweepProps):
            props = props.to_dict()
        self._app.oanalysis.EditSweep(self.setup_name, self.name, self._get_args(props))
        if not self._has_getobject:
            self._legacy_props = copy.deepcopy(props)
        return True

    @pyaedt_function_handler()
    def delete(self) -> bool:
        """Delete the sweep from the design.

        Returns
        -------
        bool
            ``True`` if the sweep is deleted.

        Examples
        --------
        >>> from ansys.aedt.core import Q3d
        >>> q3d = Q3d()
        >>> sweep = q3d.create_setup().add_sweep()
        >>> sweep.delete()

        """
        self._app.oanalysis.DeleteSweep(self.setup_name, self.name)
        return True

    @pyaedt_function_handler()
    def _get_args(self, props: dict | SweepProps | None = None) -> list[Any]:
        """Convert sweep properties to AEDT arguments.

        Parameters
        ----------
        props : dict, optional
            Properties to convert. If omitted, the current sweep properties are used.

        Returns
        -------
        list
            AEDT argument list for the sweep.

        """
        if props is None:
            props = self.props.to_dict()
        elif isinstance(props, SweepProps):
            props = props.to_dict()
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
