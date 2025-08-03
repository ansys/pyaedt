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

from collections.abc import Mapping
from datetime import datetime
from datetime import timedelta
from functools import total_ordering
import re
from types import MappingProxyType

from ansys.aedt.core.aedt_logger import pyaedt_logger as logging
from ansys.aedt.core.generic.general_methods import pyaedt_function_handler
from ansys.aedt.core.generic.numbers import Quantity
from ansys.aedt.core.modules.variation import Variation


def string_to_time(time_string):
    h, m, s = map(int, time_string.split(":"))
    return timedelta(hours=h, minutes=m, seconds=s)


def parse_profile_key(self, profile_key):
    """Split the profile key.

    Split the profile key into the setup name
    and variation.

    Parameters
    ----------
    profile_key : str
        String of the format "SetupName - variation". For example
        "MySetup - l_dipole='10.1cm' wire_rad='1mm'".

    Returns
    -------
    setup_name : string
    variation : Variation (dict-like)

    """
    if "-" in profile_key:
        setup, variation_string = profile_key.split("-")
        setup_name = setup.strip()
        variation = Variation(variation_string)
        return setup_name, variation
    else:
        return profile_key, None  # HFSS 3DLayout doesn't use the variation in the setup name.


@pyaedt_function_handler()
def _select_group(sim_groups):
    if len(sim_groups) > 1:
        # Find the group with the longest elapsed time.
        this_group = max(sim_groups, key=lambda g: g.elapsed_time)
    else:
        this_group = sim_groups[0]
    return this_group


@total_ordering
class MemoryGB(object):
    """Class to represent memory in Gigabytes."""

    convert_mem = {"G": 1.0, "M": 0.001, "KB": 1e-6, "K": 1e-6}

    @pyaedt_function_handler()
    def __init__(self, memory_value):
        if isinstance(memory_value, (int, float)):
            self._memory_str = f"{memory_value} G"
        elif isinstance(memory_value, MemoryGB):
            self._memory_str = str(memory_value)
        elif isinstance(memory_value, str):
            self._memory_str = memory_value
        else:
            raise TypeError("Invalid value for memory.")

    @pyaedt_function_handler()
    def __call__(self):
        return self.value

    @property
    def value(self):
        num, suffix = self._memory_str.split()
        return float(num) * self.convert_mem[suffix]

    @pyaedt_function_handler()
    def __str__(self):
        return self._memory_str

    @pyaedt_function_handler()
    def __add__(self, other):
        if isinstance(other, MemoryGB):
            # Sum values in GB, create new instance with "G" suffix
            total = self.value + other.value
            return MemoryGB(f"{total} G")
        return NotImplemented

    @pyaedt_function_handler()
    def __radd__(self, other):
        # Allows sum() and other left-hand operations
        if other == 0:
            return self
        elif isinstance(other, MemoryGB):
            return self.__add__(other)
        return NotImplemented

    @pyaedt_function_handler()
    def __repr__(self):
        return self._memory_str

    @pyaedt_function_handler()
    def __eq__(self, other):
        if isinstance(other, MemoryGB):
            return self.value == other.value
        return NotImplemented

    @pyaedt_function_handler()
    def __lt__(self, other):
        if isinstance(other, MemoryGB):
            return self.value < other.value
        return NotImplemented

    @pyaedt_function_handler()
    def __float__(self):
        return self.value


# Map AEDT Profile step names to attribute names and
# types.
PROFILE_PROP_METHODS = MappingProxyType(
    {
        "Cpu time": string_to_time,
        "Real time": string_to_time,
        "Memory": MemoryGB,
        "Disk": MemoryGB,
        "Tetrahedra": int,
        "Nodes": int,  # Icepak only
        "Faces": int,  # Icepak only
        "Cells": int,  # Icepak only
    }
)

attr_mapping = {
    "_name": "Name",
    "_cpu_time": "Cpu time",
    "_real_time": "Real time",
    "_memory": "Memory",
    "_disk_space": "Disk",
    "_num_tets": "Tetrahedra",
    "_type": "Type",
    "_nodes": "Nodes",  # Icepak only
    "_faces": "Faces",  # Icepak only
    "_cells": "Cells",  # Icepak only
    "_info": "Info",
}


class ProfileStepSummary(object):
    """Summary information for a single profile step."""

    @pyaedt_function_handler()
    def __init__(self, props):
        if "Name" in props.keys():
            self.name = props["Name"]
        else:
            self.name = None
        if "Cpu time" in props.keys():
            self.cpu_time = string_to_time(props["Cpu time"])
        else:
            self.cpu_time = None
        if "Real time" in props.keys():
            self.real_time = string_to_time(props["Real time"])
        elif "Elapsed Time" in props.keys():
            self.real_time = string_to_time(props["Elapsed Time"])
        elif "Info" in props.keys():  # For frequency sweep use "Elapsed time"
            match = re.search(r"Elapsed time\s*:\s*([\d:]+)", props["Info"])
            self.real_time = string_to_time(match.group(1)) if match else None
        else:
            self.real_time = None
        if "Memory" in props.keys():
            self.memory = MemoryGB(props["Memory"])
        else:
            self.memory = None


class ProfileStep(object):
    @pyaedt_function_handler()
    def __init__(self, data):  # data is the dict with the profile step data
        self._data = data
        self._cpu_time = dict()
        self._real_time = dict()
        self._memory = dict()
        self._disk_space = dict()
        self._num_tets = dict()
        self._nodes = dict()
        self._faces = dict()
        self._cells = dict()
        self._info = dict()

        # Map data from profile steps to class attributes. The mapping is defined
        # in PROFILE_PROP_METHODS which enables calculation for
        # summary properties like ``cpu_time`` and ``max_memory``.

        for step_name in self._data.children.keys():
            for attr_name, attr_value in vars(self).items():  # Assign values to all attributes
                #  If the step_name doesn't exist, None will be returned.
                if attr_name in attr_mapping.keys():
                    value = self._get_prop(step_name, attr_mapping[attr_name])
                    if value is not None:
                        attr_value[step_name] = value

        self._summary = ProfileStepSummary(data.properties)

    @property
    def process_steps(self):
        return list(self._cpu_time.keys())  # Return all keys.

    @property
    def cpu_time(self):
        return sum(self._cpu_time.values(), timedelta(0))  # Initialize the sum with a timedelta instance.

    @property
    def real_time(self):
        return sum(self._real_time.values(), timedelta(0))  # Initialize the sum with a timedelta instance.

    @property
    def max_memory(self):
        if len(self._memory) > 0:
            return max(self._memory.values())
        else:
            return MemoryGB("0 M")

    @pyaedt_function_handler()
    def _get_prop(self, key, name_string):
        if name_string in self._data.children[key].properties.keys() and key in self._data.children.keys():
            if name_string in PROFILE_PROP_METHODS:
                # and   key in self._data.children.keys()
                try:
                    return PROFILE_PROP_METHODS[name_string](self._data.children[key].properties[name_string])
                except ValueError:
                    error_message: str = f"Error parsing {name_string} for {key}"
                    error_message += f"\n{self._data.children[key].properties[name_string]}"
                    logging.error(error_message)
            else:
                # if key in self._data.children.keys():
                return self._data.children[key].properties[name_string]
        else:
            return None


class MeshProcess(ProfileStep):
    """Information about the mesh generation."""

    @pyaedt_function_handler()
    def __init__(self, data):
        super().__init__(data)
        self._elapsed_time = string_to_time(data.properties["Elapsed Time"])

    @property
    def elapsed_time(self):
        return self._elapsed_time


class FrequencySweepProfile(object):
    """Profile data for the frequency sweep."""

    _SELECT_FREQ = re.compile(r"Frequency - (.*?) Group")

    @pyaedt_function_handler()
    def __init__(self, data):
        self._frequencies = []
        self._data = data.children
        self._create_summary(data.properties)
        self._frequency_steps = dict()
        self._data_transfer_steps = []
        self._dc_conduction = []
        self._adaptive_refine = []
        self._dc_rl_meshing = []
        # self._q3d_adapt = []  # Q3D profile data is not available in the native API
        for freq in self.frequencies:
            key = str(freq)  # the key is an AEDT Quantity typ.
            if key in self._frequency_steps:  # TODO: Add logic to handle SBR+ Frequency sweep.
                self._frequency_steps[key] = ProfileStep(self._data[self._freq_key(key)])
        for key, value in self._data.items():
            if "Data Transfer" in key:
                self._data_transfer_steps.append(ProfileStepSummary(value.properties))
            elif "DC Conduction Solve" in key:
                self._dc_conduction.append(ProfileStepSummary(value.properties))
            elif "Adaptive Refine" in key:
                self._adaptive_refine.append(ProfileStepSummary(value.properties))
            elif "DC-RL Meshing" in key:
                self._dc_rl_meshing.append(ProfileStepSummary(value.properties))

    @pyaedt_function_handler()
    def _create_summary(self, data):
        self._elapsed_time = string_to_time(data["Elapsed Time"])
        self._start_time = datetime.strptime(data["Time"], "%d/%m/%Y %H:%M:%S")
        sweep_info = data["Info"]

        # 1. Sweep type
        sweep_type_match = re.search(r"^(\w+)\s+HFSS Frequency Sweep", sweep_info)
        self.sweep_type = sweep_type_match.group(1) if sweep_type_match else None

        # 2. Frequencies used
        frequency_match = re.findall(r"\s*([\d.]+[TGMk]?Hz)", sweep_info)
        self.frequency_basis = [Quantity(f) for f in frequency_match]
        self.frequency_basis.sort()

        # 3. Interpolating sweep fitting
        if self.sweep_type == "Interpolating":
            passivity_matches = re.findall(r"Passivity Error\s*=\s*([\d.]+)", sweep_info)
            self.passivity_error = float(passivity_matches[-1]) if passivity_matches else None
            self.converged = "sweep converged" in sweep_info.lower()
            s_matrix_errors = re.findall(r"S Matrix Error\s*=\s*([\d.]+)%", sweep_info)
            self.s_matrix_error = float(s_matrix_errors[-1]) * 0.01 if s_matrix_errors else None

    @property
    def frequencies(self):
        if self._frequencies:
            return self._frequencies
        else:
            for key in self._data.keys():
                select_freq_str = self._SELECT_FREQ.match(key)
                if select_freq_str:
                    self._frequencies.append(Quantity(select_freq_str.group(1)))
                    self._frequencies.sort()
            if self._frequencies:
                return self._frequencies
            else:  # For SBR+
                self._frequencies = self.frequency_basis
                return self._frequencies

    @pyaedt_function_handler()
    def _freq_key(self, freq_str):
        return f"Frequency - {freq_str} Group"

    @pyaedt_function_handler()
    def keys(self):
        return [str(f) for f in self.frequencies]

    @pyaedt_function_handler()
    def __getitem__(self, key):
        """Return the profile step for a given frequency.

        Parameters
        ----------
        key : str
            Frequency value as a string, including units. Use the ``keys()`` method
            to determine all solved frequencies.

        Returns
        -------
        ProfileStep : Profile step for the given frequency.
        """

        if Quantity(key) in self.frequencies:
            return self._frequency_steps[key]
        else:
            raise KeyError(f"Frequency {key} not found in frequency sweep.")

    @property
    def elapsed_time(self):
        return self._elapsed_time

    @property
    def max_memory(self):
        all_memories = [f.max_memory for f in self._frequency_steps.values()]
        if len(all_memories) > 0:
            return max([f.max_memory for f in self._frequency_steps.values()])
        else:
            return None


class AdaptivePass(ProfileStep):
    """Information for a single adaptive pass."""

    @pyaedt_function_handler()
    def __init__(self, data):
        super().__init__(data)
        self._adapt_frequency = Quantity(data.properties["Frequency"])

    @property
    def adapt_frequency(self):
        return self._adapt_frequency


@pyaedt_function_handler()
def get_mesh_process_name(sim_group_data):
    mesh_process_names = ["Initial Meshing Group", "Meshing Process Group"]
    for name in mesh_process_names:
        if name in sim_group_data.children.keys():
            return name
    return None


class SimulationProfile(object):
    """Simulation group data

    This class encapsulates all profile data from a single simulation.

    """

    @pyaedt_function_handler()
    def __init__(self, sim_group_data):  # , setup_type: str
        self.elapsed_time = timedelta(0)
        self.start_time = None
        self.stop_time = None
        self.host_name = None
        self.num_cores = None
        self.os = None
        self.status = None
        self.mesh_process = None
        self.validation_time = None
        self.validation_memory = None
        self.product = None
        self.adaptive_pass = []
        self.transient_step = {}  # Solution Profile for each transient step.
        self._transient_times = []  # Float of time step values in seconds.
        self.frequency_sweep = {}

        # For Icepak only
        self.solve = None
        self.populate_solver_input = None
        self.initialize_solver = None
        # The time will be the key for the transient steps in a dict.

        if "Elapsed Time" in sim_group_data.properties.keys():
            elapsed_time = string_to_time(sim_group_data.properties["Elapsed Time"])
            if elapsed_time > timedelta(0):  # Only consider simulation groups with time greater than zero
                self.elapsed_time = elapsed_time
                self.start_time = datetime.strptime(sim_group_data.properties["Start Time"], "%m/%d/%Y %H:%M:%S")
                self.stop_time = datetime.strptime(sim_group_data.properties["Stop Time"], "%m/%d/%Y %H:%M:%S")
                self.host_name = sim_group_data.properties["Host"]
                self.num_cores = sim_group_data.properties["Processor"]
                self.os = sim_group_data.properties["OS"]
                self.status = sim_group_data.properties["Status"]
                product_str_list = sim_group_data.properties["Product"].split()
                if len(product_str_list) > 1:
                    self.version = product_str_list[-1]
                    self.product = product_str_list[0]
                else:
                    self.version = None
                    self.product = sim_group_data.properties["Product"]
                # self._product = sim_group_data.properties["Product"]
                self.use_mpi = False
                self.validation = None
                if "Adaptive Meshing Group" in sim_group_data.children.keys():
                    for pass_name, pass_info in sim_group_data.children["Adaptive Meshing Group"].children.items():
                        self.adaptive_pass.append(AdaptivePass(pass_info))
                mesh_process_name = get_mesh_process_name(sim_group_data)
                if mesh_process_name:
                    self.mesh_process = MeshProcess(sim_group_data.children[mesh_process_name])
                if "HFSS" in sim_group_data.properties["Product"]:
                    if "Design Validation" in sim_group_data.children.keys():
                        info = sim_group_data.children["Design Validation"].properties["Info"].split(",")
                        time_str = info[0].split(":")[-3:]
                        time_str = ":".join([x.strip() for x in time_str])
                        memory_str = info[1].strip().split(":")[-1].strip()
                        self.validation_time = string_to_time(time_str)
                        self.validation_memory = MemoryGB(memory_str)
                    if "Frequency Sweep Group" in sim_group_data.children:
                        SWEEP_RE = re.compile(r"Solution - (.*?) Group")
                        for name, data in sim_group_data.children["Frequency Sweep Group"].children.items():
                            match = SWEEP_RE.match(name)
                            if len(match.groups()) > 0:
                                sweep_name = match.group(1)
                                self.frequency_sweep[sweep_name] = FrequencySweepProfile(data)
                if (
                    "Maxwell" in sim_group_data.properties["Product"]
                    or "Icepak" in sim_group_data.properties["Product"]
                ):
                    if "Design Validation" in sim_group_data.children.keys():
                        time_str = sim_group_data.children["Design Validation"].properties["Elapsed Time"]
                        memory_str = sim_group_data.children["Design Validation"].properties["Memory"]
                        self.validation_time = string_to_time(time_str)
                        self.validation_memory = MemoryGB(memory_str)
                if "HPC Group" in sim_group_data.children.keys():
                    if "MPI Vendor" in sim_group_data.children["HPC Group"].properties.keys():
                        self.mpi_vendor = sim_group_data.children["HPC Group"].properties["MPI Vendor"]
                        self.mpi_version = sim_group_data.children["HPC Group"].properties["MPI Version"]
                        self.use_mpi = True
                if "Transient Solution Group" in sim_group_data.children:
                    pattern = re.compile(r"^Time\s*-\s*(\d+(?:\.\d+)?s)$")
                    for sim_key, step_data in sim_group_data.children["Transient Solution Group"].children.items():
                        match = pattern.match(sim_key)
                        if match:
                            self.transient_step[match.group(1)] = ProfileStep(step_data)
                if "Solver Initialization" in sim_group_data.children.keys():
                    self.initialize_solver = ProfileStepSummary(
                        sim_group_data.children["Solver Initialization"].properties
                    )
                if "Populate Solver Input" in sim_group_data.children.keys():
                    self.populate_solver_input = ProfileStepSummary(
                        sim_group_data.children["Populate Solver Input"].properties
                    )
                if "Solve" in sim_group_data.children.keys():
                    self.solve = ProfileStepSummary(sim_group_data.children["Solve"].properties)

    @pyaedt_function_handler()
    def cpu_time(self, num_passes=None, max_time=None):
        """Total CPU time for adaptive refinement or transient simulations.

        Frequency sweep is not included in this calculation. For the frequency sweep
        time use the ``frequency_sweep.elapsed_time`` attribute.

        Parameters
        ----------
        num_passes : int, optional
            Number of adaptive passes (if the solution uses adaptive mesh refinement).
        max_time : float, optional
            Maximum simulation time for a transient simulation in seconds.
        """
        return self._time_calc("cpu_time", num_passes, max_time)

    @pyaedt_function_handler()
    def real_time(self, num_passes=None, max_time=None):
        return self._time_calc("real_time", num_passes, max_time)

    @pyaedt_function_handler()
    def _time_calc(self, attr_name, num_passes, max_time):
        """Calculate the total time for the simulation."""

        num_passes = self._check_num_passes(num_passes)
        if not max_time:
            if len(self.transient_step) > 0:
                max_time = self.max_time  # Transient simulation
        elif max_time > self.max_time:
            max_time = self.max_time
        total_time = timedelta(0)

        if num_passes:
            adapt_times = [getattr(p, attr_name) for p in self.adaptive_pass[:num_passes]]
            total_time += sum(adapt_times, timedelta(0))
        if max_time:
            time_keys = self._get_time_steps(max_time)
            time_steps = {k: getattr(self.transient_step[k], attr_name) for k in time_keys}
            total_time += sum(time_steps.values(), timedelta(0))
        for self_attr_name, self_attr in vars(self).items():
            if callable(self_attr):
                continue
            if hasattr(self_attr, attr_name):
                total_time += getattr(self_attr, attr_name)
        return total_time

    @property
    def num_adaptive_passes(self):
        return len(self.adaptive_pass)

    @property
    def is_transient(self):
        if len(self.transient_step) > 0:
            return True
        else:
            return False

    @property
    def has_frequency_sweep(self):
        if len(self.frequency_sweep) > 0:
            return True
        else:
            return False

    @pyaedt_function_handler()
    def max_memory(self, num_passes=None):
        """Maximum memory used in the solve process.

        Parameters
        ----------
        num_passes : int, optional

        Returns
        -------
        MemoryGB : Maximum memory used in the adaptive mesh
        refinement process.
        """

        num_passes = self._check_num_passes(num_passes)
        mem = []
        mem += [m.max_memory for m in self.transient_step.values()]
        if hasattr(self, "mesh_process"):  # Mesh generation
            if self.mesh_process:
                mem.append(self.mesh_process.max_memory)
        if hasattr(self, "adaptive_pass"):  # Adaptive passes
            pass_iter = 0
            while pass_iter < num_passes:
                mem.append(self.adaptive_pass[pass_iter].max_memory)
                pass_iter += 1

        for self_attr_name, self_attr in vars(self).items():  # All other processes
            if callable(self_attr):
                continue
            if hasattr(self_attr, "memory"):
                this_mem = getattr(self_attr, "memory")
                if this_mem:
                    mem.append(getattr(self_attr, "memory"))

        return max(mem, default=0)

    @pyaedt_function_handler()
    def _check_num_passes(self, num_passes):
        """Return a valid value for the number of adaptive passes.

        Given an integer, return a valid
        value for the total number of adaptive passes.

        Parameters
        ----------
        num_passes : int
            Number of adaptive passes.

        Returns
        -------
        int : Valid number of adaptive passes.
        """

        if num_passes:
            if num_passes > self.num_adaptive_passes:
                return self.num_adaptive_passes
            else:
                return num_passes
        else:
            return self.num_adaptive_passes

    @pyaedt_function_handler()
    def __str__(self):
        repr_str = self.__repr__()
        repr_str += f"Host: {self.host_name}, "
        repr_str += f"Elapsed time: {str(self.elapsed_time)}"
        return repr_str

    @pyaedt_function_handler()
    def __repr__(self):
        return f"{self.product} simulation profile, version: {self.version}\n"

    @property
    def max_time(self):
        """Maximum time in a transient simulation."""
        if isinstance(self.time_steps, list):
            if len(self.time_steps) > 0:
                return max(self.time_steps)
            else:
                return None
        else:
            return None

    @property
    def time_steps(self):
        """Return a list of time steps."""
        if len(self.transient_step) > 0:
            return [float(s[:-1]) for s in self.transient_step.keys()]
        else:
            return [0.0]

    @pyaedt_function_handler()
    def _get_time_steps(self, max_time):
        """Return keys for all time steps less than ``max_time``"""
        if max_time:
            max_time = float(max_time)
            return [s for s in self.transient_step.keys() if float(s[:-1]) <= max_time]
        else:
            return None


@pyaedt_function_handler()
def extract_profile_data(profile_data):  # setup_type as argument?
    """

    Parameters
    ----------
    profile_data : BinaryTreeNode
        The full profile data.

    """
    groups = []
    for group_name, process_group in profile_data.children.items():  # Loop through "Solution Process Groups".
        try:
            sim_group_data = SimulationProfile(process_group)
            if sim_group_data.status:
                groups.append(sim_group_data)
        except Exception as e:
            logging.error(f"Error parsing {group_name}: {e}")
    return _select_group(groups)  # ProfileData will contain the data from one simulation group.


class Profiles(Mapping):
    """Provide an interface to view and parse the solver profiles.

    The Profiles class is iterable. Individual profiles are accessed via the unique
    key comprised of "setup_name - variation". If there are no variations available, the
    unique key is the setup name.

    Examples
    --------
    >>> app = Hfss(project="solved_project")
    >>> profiles = app.setups[0].get_profile()
    >>> key_for_profile = list(profiles.keys())[0]
    >>> print(key_for_profile)
        'Setup1'
    >>> profiles[key_for_profile].product
        'HFSS3DLayout'
    >>> print(f"Elapsed time: {profiles[key_for_profile].elapsed_time}")
        Elapsed time: 0:01:39
    >>> print(f"Number of adaptive passes: {profiles[key_for_profile].num_adaptive_passes}")
        Number of adaptive passes: 6
    >>> fsweep = profiles[key_for_profile].frequency_sweep
    >>> sweep_name = list(fsweep.keys())[0]
    >>> print(f"Frequency sweep {sweep_name} calculated {len(fsweep)} frequency points.")
    """

    @pyaedt_function_handler()
    def __init__(self, profile_dict):  # Omit setup_type ? setup_type="HFSS 3D Layout"
        self._profile_data = dict()
        if type(profile_dict) is dict:
            self._profile_dict = profile_dict
        else:
            raise TypeError("Profile must be a dictionary.")
        try:
            for key, value in profile_dict.items():
                self._profile_data[key] = extract_profile_data(value)  # setup_type as argument?
        except Exception as e:
            logging.warning(f"Error parsing profile: {e}")
            logging.warning("Use native API profile data instead.")
            self._profile_data = dict()

    @pyaedt_function_handler()
    def __getitem__(self, key):
        if len(self._profile_data) > 0:
            return self._profile_data[key]
        else:
            return self._profile_dict[key]

    @pyaedt_function_handler()
    def __iter__(self):
        if len(self._profile_data) > 0:
            return iter(self._profile_data)
        else:
            return iter(self._profile_dict)

    @pyaedt_function_handler()
    def __setitem__(self, key, value):
        raise TypeError(f"{self.__class__.__name__} is read-only and does not support item assignment.")

    @pyaedt_function_handler()
    def __len__(self):
        if len(self._profile_data) > 0:
            return len(self._profile_data)
        else:
            return len(self._profile_dict)

    @pyaedt_function_handler()
    def __repr__(self):
        repr_str = f"{self.__class__.__name__} of length {len(self)}:\n"
        for key, value in self.items():
            try:
                repr_str += f"  {key}: {value}\n"
            except Exception as e:
                logging.error(f"Error parsing profile: {e}")
        return str(repr_str)

    @pyaedt_function_handler()
    def keys(self):
        if len(self._profile_data) > 0:
            return self._profile_data.keys()
        else:
            return self._profile_dict.keys()
