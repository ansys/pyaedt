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
import inspect
from pathlib import Path
import re
from types import MappingProxyType

import pandas as pd

from ansys.aedt.core.aedt_logger import pyaedt_logger as logging
from ansys.aedt.core.generic.general_methods import pyaedt_function_handler
from ansys.aedt.core.generic.numbers import Quantity


def string_to_time(time_string):
    h, m, s = map(int, time_string.split(":"))
    return timedelta(hours=h, minutes=m, seconds=s)


def merge_dict(d1, d2):
    """Merge two dictionaries."""

    def sort_key(k: str):
        parts = k.split()
        try:
            # try parsing the last token as an integer
            num = int(parts[-1])
            # if successful, sort by everything before the number (joined) and then the number
            return (" ".join(parts[:-1]), num)
        except ValueError:
            # fallback: just sort by the whole string lexicographically
            return (k, float("inf"))

    merged = {}

    # Union of all keys
    keys_union = d1.keys() | d2.keys()
    all_keys = sorted(keys_union, key=sort_key)

    for key in all_keys:
        if key in d1 and key in d2:
            if d1[key] == d2[key]:
                merged[key] = d1[key]
            elif isinstance(d1[key], dict) and isinstance(d2[key], dict):
                merged[key] = merge_dict(d1[key], d2[key])
            elif isinstance(d1[key], list) and isinstance(d2[key], list):
                merged[key] = sorted(d1[key] + d2[key])
            elif isinstance(d1[key], str) and isinstance(d2[key], str):
                merged[key] = d1[key] + "\n" + d2[key]
            else:
                merged[key] = d1[key]
                merged[key + "_2"] = d2[key]
        elif key in d1:
            merged[key] = d1[key]
        else:
            merged[key] = d2[key]
    return merged


@pyaedt_function_handler()
def _select_group(sim_groups):
    this_group = sim_groups[0]
    for g in sim_groups[1:]:
        this_group = this_group + g  # Merge simulation groups.
    return this_group


@total_ordering
class MemoryGB(object):
    """Class to represent memory in Gigabytes."""

    _convert_mem = {"TB": 1000.0, "G": 1.0, "M": 0.001, "KB": 1e-6, "K": 1e-6, "Bytes": 1e-9}

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
        return float(num) * self._convert_mem[suffix]

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


# Map AEDT names to attribute names and operators that convert the
# data of the property to the correct type.
PROFILE_PROP_MAPPING = MappingProxyType(
    {
        "Cpu time": ("_cpu_time", string_to_time),
        "Real time": ("_real_time", string_to_time),
        "Elapsed Time": ("elapsed_time", string_to_time),
        "Memory": ("_memory", MemoryGB),
        "Disk": ("_disk_space", MemoryGB),
        "Product": ("_product_str", str),
        "Frequency": ("freq", Quantity),
        "Name": ("name", str),
        "Max Mag. Delta S": ("delta_s_max", float),
        "Tetrahedra": ("num_tets", int),
        "Info": ("info", str),
        "OS": ("os", str),
        "Solution Basis Order": ("basis_order", str),
        "Executing From": ("engine", Path),
        "Host": ("host_name", str),
        "Status": ("status", str),
        "Processor": ("num_cores", int),
        # Note: Two different keys may be used to denote the start time for a process,
        # "Time" and "Start Time".  When "Time" and "Elapsed Time" are specified, then
        # the "stop_time" attribute can be calculated.
        "Start Time": ("start_time", lambda t: datetime.strptime(t, "%m/%d/%Y %H:%M:%S")),
        "Time": ("start_time", lambda t: datetime.strptime(t, "%m/%d/%Y %H:%M:%S")),
        "Stop Time": ("stop_time", lambda t: datetime.strptime(t, "%m/%d/%Y %H:%M:%S")),
        "Nodes": ("nodes", int),  # Icepak only
        "Faces": ("faces", int),  # Icepak only
        "Cells": ("cells", int),  # Icepak only
    }
)


def format_timedelta(td):
    """Present timedelta in a format suitable for a table."""
    if isinstance(td, timedelta):
        total_seconds = int(td.total_seconds())
        if total_seconds < 86400:  # less than 1 day
            h, rem = divmod(total_seconds, 3600)
            m, s = divmod(rem, 60)
            return f"{h:02}:{m:02}:{s:02}"
        else:
            days = td.days
            h, rem = divmod(total_seconds - days * 86400, 3600)
            m, s = divmod(rem, 60)
            return f"{days} day{'s' if days > 1 else ''} {h:02}:{m:02}:{s:02}"
    else:
        return str(td)


def step_name_map(input_name):
    """Map AEDT keys to compact, descriptive names."""
    pattern = [re.compile(r"^Frequency\s*-\s*([\d.]+(?:[TGMk]?Hz))$")]
    for p in pattern:
        match = p.search(input_name)
        if match:
            return match.group(1)
        else:
            return input_name


# Specify operation for keys having common values.
# Use the following for attributes when calling the __add__() method.
merge_operator = {
    "start_time": min,
    "end_time": max,
    "stop_time": max,
    "host_name": lambda x, y: x + "\n" + y,  # concatenate strings
    "elapsed_time": lambda a, b: a + b,  # Add timedelta instances
    "max_memory": max,
    "frequency_sweep": merge_dict,
    "transient_step": merge_dict,
    "_cpu_time": max,
    "_real_time": max,
    "info": lambda x, y: x + "\n" + y,
    "_memory": max,
    "steps": merge_dict,
}
attr_mapping = {
    "_name": "Name",
    "_cpu_time": "Cpu time",
    "_real_time": "Real time",
    "elapsed_time": "Elapsed Time",
    "start_time": "Start Time",
    "stop_time": "Stop Time",
    "host_name": "Host",
    "product": "Product",
    "num_cores": "Processor",
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
    __timedelta_props = ["elapsed_time", "cpu_time", "real_time"]

    @pyaedt_function_handler()
    def __init__(self, data):  # data is the dict with the profile step data
        for key, value in data.properties.items():
            if key in PROFILE_PROP_MAPPING:
                setattr(self, PROFILE_PROP_MAPPING[key][0], PROFILE_PROP_MAPPING[key][1](value))
        if len(data.children) > 0:
            self.steps = dict()
            for step_name, step_data in data.children.items():
                name = self._clean_key_name(step_name)  # Clean up key names.
                self.steps[name] = ProfileStep(step_data)

        # Depending on how data is presented in the profile, the end time for
        # the step may have to be calculated. The "_stop_time" property is only
        # temporary.
        if not hasattr(self, "stop_time"):
            if hasattr(self, "start_time") and hasattr(self, "elapsed_time"):
                setattr(self, "stop_time", self.start_time + self.elapsed_time)

    @property
    def process_steps(self):
        if hasattr(self, "steps"):
            return list(self.steps.keys())
        else:
            return None

    @property
    def cpu_time(self):
        if hasattr(self, "_cpu_time"):
            this_time = self._cpu_time
        else:
            this_time = timedelta(0)
            for v in self.steps.values():
                this_time += v.cpu_time
        return this_time

    @property
    def real_time(self):
        if hasattr(self, "_real_time"):
            this_time = self._real_time
        else:
            this_time = timedelta(0)
            for v in self.steps.values():
                this_time += v.real_time
        return this_time

    @staticmethod
    def _clean_key_name(long_key_name):
        return long_key_name.replace("Group", "").strip().replace("Time - ", "").strip()

    @property
    def max_memory(self):
        if hasattr(self, "_memory"):
            mem = self._memory
        else:
            mem = MemoryGB("0 G")
        mem_list = [mem]
        if hasattr(self, "steps"):
            for v in self.steps.values():
                mem_list.append(v.max_memory)
        return max(mem_list)

    @pyaedt_function_handler()
    def table(self, columns=("elapsed_time", "real_time", "cpu_time", "max_memory")):
        """Return a summary of profile step metrics.

        Parameters
        ----------
        columns : list of str
            Defines the columns to be included in the returned table.

            Valid names are:

            * ``"elapsed_time"`` - Default
            * ``"real_time"`` - Default
            * ``"cpu_time"`` - Default
            * ``"max_memory"`` - Default
            * ``"start_time"``
            * ``"end_time"``
            * ``"num_tets"``
            * ``"nodes"`` - Icepak only
            * ``"faces"`` - Icepak only
            * ``"cells"`` - Icepak only

        Names are case-sensitive. Depending on the solution profile step, some
        properties are not available, in which case the value ``"NA"`` will be
        returned in the table.

        Returns
        -------
        Pandas DataFrame
            Table of profile process step information for
            the specified property values.
        """
        data = {"Step": []}  # Contains the data for the Pandas DataFrame.

        for step_name, step_data in self.steps.items():
            name = step_name_map(step_name)  # Replace key with a more meaningful name.
            data["Step"].append(name)
            for prop in columns:
                if hasattr(step_data, prop):
                    value = getattr(step_data, prop)
                else:
                    value = "NA"
                if prop in data:
                    data[prop].append(value)
                else:
                    data[prop] = [value]

        table_out = pd.DataFrame(data)

        # Update formatting of timedelta props
        for p in self.__timedelta_props:
            if p in table_out:
                table_out[p] = table_out[p].apply(format_timedelta)

        return table_out

    @pyaedt_function_handler()
    def _validate_table_properties(self, props_in=None):
        #   exclude = ["steps", "frequency_basis", "frequencies", "process_steps"]
        props = []
        exclude = ["steps", "frequency_basis", "frequencies", "process_steps", "table"]
        step_keys = list(self.steps.keys())
        for name in dir(self.steps[step_keys[0]]):
            if name.startswith("_") or name in exclude:
                continue  # Skip private attributes
            try:
                value = getattr(self.steps[step_keys[0]], name)
                # Optionally skip methods or callables
                if not isinstance(value, (dict, list, pd.DataFrame)):
                    props.append(name)
            except Exception:
                # Skip unreadable or dynamically broken attributes
                continue
        return props

    def __add__(self, other):
        # Instantiate result
        result = self.__class__.__new__(self.__class__)
        result.__dict__ = {}
        for key, value in self.__dict__.items():
            new_val = None
            if key in self.__dict__ and key in other.__dict__:
                if key in merge_operator:
                    new_val = merge_operator[key](value, other.__dict__[key])
                elif value == other.__dict__[key]:
                    new_val = value
                else:
                    try:
                        new_val = value + other.__dict__[key]
                    except TypeError:
                        new_val = value
            elif key in other.__dict__:
                new_val = other.__dict__[key]
            setattr(result, key, new_val)
        return result


class TransientProfile(ProfileStep):
    """Profile data for the frequency sweep."""

    _SELECT_TRANSIENT = re.compile(r"(\d+(?:\.\d+)?s)")  # Matches a time-step name like "0.01s"

    @pyaedt_function_handler()
    def __init__(self, data):
        super().__init__(data)
        self._time_step_keys = []
        for sim_key in self.steps.keys():
            match = self._SELECT_TRANSIENT.match(sim_key)
            if match:
                self._time_step_keys.append(match.group(1))

    @property
    def time_steps(self):
        return sorted([float(t.replace("s", "")) for t in self._time_step_keys])

    def time_step_keys(self, max_time):
        return_val = []
        for k in self._time_step_keys:
            if float(k.replace("s", "")) <= max_time:
                return_val.append(k)
        return return_val

    @property
    def max_time(self):
        if hasattr(self, "time_steps"):
            if len(self.time_steps) > 0:
                return max(self.time_steps)
            else:
                return 0.0
        else:
            return None


class FrequencySweepProfile(ProfileStep):
    """Profile data for the frequency sweep."""

    _SELECT_FREQ = re.compile(r"Frequency - (.*?) Group")

    @pyaedt_function_handler()
    def __init__(self, data, sweep_name=None):
        super().__init__(data)
        self._create_summary(data.properties)
        if sweep_name:
            self.sweep_name = sweep_name
        else:
            self.sweep_name = None
        self._frequencies = []
        freq_pattern = re.compile(r"(\d+(?:\.\d+)?\s*(?:T|G|M|k)?Hz)")
        # self._q3d_adapt = []  # Q3D profile data is not available in the native API
        elapsed_time_pattern = re.compile(r"Elapsed time\s*:\s*(\d{2}:\d{2}:\d{2})")
        for key, value in data.children.items():
            if "Frequency -" in key:
                match_freq = freq_pattern.search(key)
                if match_freq:
                    freq_key = match_freq.group(1)
                    self._frequencies.append(Quantity(freq_key))

                    # Get the elapsed time for the frequency sweep group calculation.
                    # Remove the "Group" text from the key for self.steps if it exists.
                    name = key.replace("Group", "").strip()
                    time_match = elapsed_time_pattern.search(self.steps[name].info)  # Get elapsed time
                    if time_match:
                        self.steps[name].elapsed_time = string_to_time(time_match.group(1))

    @pyaedt_function_handler()
    def _create_summary(self, data):
        if "Info" in data.keys():
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

        # Start time
        if "Time" in data.keys():
            self.start_time = datetime.strptime(data["Time"], "%d/%m/%Y %H:%M:%S")

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


class AdaptivePass(ProfileStep):
    """Information for a single adaptive pass."""

    @pyaedt_function_handler()
    def __init__(self, data):
        super().__init__(data)
        if "Frequency" in data.properties.keys():
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

    # The following attributes are of type dict. When two SimulationProfile
    # instances are combined, the dictionary attributes are merged by including
    # all unique keys.
    dict_attributes = (
        "frequency_sweep",
        "transient_step",
    )

    @pyaedt_function_handler()
    def __init__(self, sim_group_data):  # , setup_type: str
        for name in self.dict_attributes:
            setattr(self, name, dict())
        self._update_props_from_dict(sim_group_data.properties)
        self.adaptive_pass = None
        self.mesh_process = None
        self.validation_time = None
        self.validation_memory = None
        self.solve = None
        self.initialize_solver = None

        if "Adaptive Meshing Group" in sim_group_data.children.keys():
            self.adaptive_pass = ProfileStep(sim_group_data.children["Adaptive Meshing Group"])
        mesh_process_name = get_mesh_process_name(sim_group_data)
        if mesh_process_name:
            self.mesh_process = ProfileStep(sim_group_data.children[mesh_process_name])
        if "HFSS" in sim_group_data.properties["Product"]:
            if "Design Validation" in sim_group_data.children.keys():
                info = sim_group_data.children["Design Validation"].properties["Info"].split(",")
                time_str = info[0].split(":")[-3:]
                time_str = ":".join([x.strip() for x in time_str])
                memory_str = info[1].strip().split(":")[-1].strip()
                self.validation_time = string_to_time(time_str)
                self.validation_memory = MemoryGB(memory_str)
            if "Frequency Sweep Group" in sim_group_data.children:
                for name, data in sim_group_data.children["Frequency Sweep Group"].children.items():
                    sweep_key = name.replace("Group", "").strip()
                    self.frequency_sweep[sweep_key] = FrequencySweepProfile(data, sweep_key)

        if "Maxwell" in sim_group_data.properties["Product"] or "Icepak" in sim_group_data.properties["Product"]:
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
            self.transient_step = TransientProfile(sim_group_data.children["Transient Solution Group"])
        if "Solver Initialization" in sim_group_data.children.keys():
            self.initialize_solver = ProfileStepSummary(sim_group_data.children["Solver Initialization"].properties)
        if "Populate Solver Input" in sim_group_data.children.keys():
            self.populate_solver_input = ProfileStepSummary(sim_group_data.children["Populate Solver Input"].properties)
        if "Solve" in sim_group_data.children.keys():
            self.solve = ProfileStepSummary(sim_group_data.children["Solve"].properties)

        # Some solution setups do not provide "Status" but the solution has run successfully.
        if not hasattr(self, "status"):
            if hasattr(self, "adaptive_pass") or hasattr(self, "frequency_sweep") or hasattr(self, "transient_step"):
                setattr(self, "status", "completed")

    @pyaedt_function_handler()
    def __add__(self, other):
        """Combine two simulation profiles."""
        # Instantiate result
        result = self.__class__.__new__(self.__class__)
        result.__dict__ = {}

        def is_empty(val):
            return val is None or val == {} or val == []

        for key in set(self.__dict__) | set(other.__dict__):  # Iterate through all keys.
            val_self = getattr(self, key, None)
            val_other = getattr(other, key, None)
            if val_self == val_other:
                setattr(result, key, val_self)
            elif (
                key in self.__dict__ and not is_empty(val_self) and key in other.__dict__ and not is_empty(val_other)
            ):  # key exists in both instances.
                if key in merge_operator:
                    new_val = merge_operator[key](val_self, val_other)
                else:
                    try:
                        new_val = val_self + val_other  # Use "+" to combine values.
                    except TypeError:
                        new_val = val_self
                        frame = inspect.currentframe()
                        info = inspect.getframeinfo(frame)
                        message = f"File: {info.filename}, Line: {info.lineno}\n"
                        message += f"Cannot merge values for key {key} in SimulationProfile."
                        logging.warning(message)
                setattr(result, key, new_val)
            elif key in other.__dict__ and not is_empty(val_other):
                setattr(result, key, val_other)
            elif key in self.__dict__:
                setattr(result, key, val_self)
            elif key in other.__dict__:
                setattr(result, key, val_other)
        return result

    @pyaedt_function_handler()
    def _update_props_from_dict(self, props_dict):
        """Use the PROFILE_PROP_MAPPING to map dictionary items to attributes."""
        for key, value in props_dict.items():
            if key in PROFILE_PROP_MAPPING:
                setattr(self, PROFILE_PROP_MAPPING[key][0], PROFILE_PROP_MAPPING[key][1](value))

    @property
    def product(self):
        if not hasattr(self, "_product"):
            self._product = self._product_str.split()[0]
        return self._product

    @product.setter
    def product(self, value):
        self._product = str(value)

    @property
    def product_version(self):
        return self._product_str.split()[-1]

    @pyaedt_function_handler()
    def cpu_time(self, num_passes=None, max_time=None):
        """Total CPU time for adaptive refinement or transient simulations.

           The total CPU time is the sum of execution time for
           all solution process steps and cores. By default, all adaptive passes (for
           adaptive refinement) or all time steps (for transient simulation)
           are included in the return value.
           "CPU time" represents the time required for a process if it were run on
           a single core. The benefit of multi-core processing can be estimated by the ratio
           between the ``real_time`` and the ``cpu_time``.

        Parameters
        ----------
        num_passes : int, optional
            Only valid when adaptive refinement is used.
            Number of passes to include in the time calculation. If nothing
            is passed, then all passes will be used.

        max_time : float, optional
            Maximum time step value in seconds to be considered for the calculation
            of the compute time.
            For example, if
            the total simulated transient time is 100 ms, then
            passing ``max_time=0.05`` will include
            only time steps up to 500 ms. If nothing is passed,
            then all time steps will be considered.

        Returns
        -------
        datetime.timedelta
            Total simulation time for adaptive refinement or transient simulation.
        """
        return self._time_calc("cpu_time", num_passes, max_time)

    @pyaedt_function_handler()
    def real_time(self, num_passes=None, max_time=None):
        """Total real time for adaptive refinement or transient simulations.

           The total real time is calculated as the sum of execution time from
           all solution process steps. By default, all adaptive passes (for
           adaptive refinement) or all time steps are included in the result.
           In contrast to "CPU time", the "Real time" represents the actual
           compute time for processes when they are distributed among multiple
           cores.

        Parameters
        ----------
        num_passes : int, optional
        Only valid when adaptive refinement is used.
        Number of passes to include in the time calculation. If nothing
        is passed, then all passes will be used.

        max_time : float
        Maximum time step value in seconds to be considered for the sum of compute time.
        For example, if
        the total simulated transient time is 100 ms, then ``max_time=0.05`` will include
        only time steps up to 500 ms. If nothing is passed, then all time steps will be used.

        Returns
        -------
        datetime.timedelta
        Total simulation time for adaptive refinement or transient simulation,
        excluding pre-processing and mesh generation.


        """
        return self._time_calc("real_time", num_passes, max_time)

    @pyaedt_function_handler()
    def _time_calc(self, attr_name, num_passes, max_time):
        """Calculate the total time for the simulation.

        Total time excluding meshing and validation.
        """
        num_passes = self._check_num_passes(num_passes)
        if not max_time:
            if hasattr(self, "transient_step"):
                max_time = self.max_time  # Transient simulation
        elif max_time > self.max_time:
            max_time = self.max_time
        total_time = timedelta(0)

        if num_passes:
            pass_names = [s for s in self.adaptive_pass.process_steps if "Adaptive Pass" in s]
            for pass_name in pass_names[:num_passes]:
                total_time += getattr(self.adaptive_pass.steps[pass_name], attr_name)
        elif max_time:
            time_keys = self.time_keys(max_time)
            time_step_values = [getattr(self.transient_step.steps[k], attr_name) for k in time_keys]
            total_time += sum(time_step_values, timedelta(0))
        return total_time

    @property
    def num_adaptive_passes(self):
        if self.adaptive_pass:
            return sum("Adaptive Pass" in s for s in self.adaptive_pass.process_steps)
        else:
            return 0

    @property
    def is_transient(self):
        return bool(self.transient_step)

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
        if self.is_transient:
            mem += [m.max_memory for m in self.transient_step.steps.values()]
        if hasattr(self, "mesh_process"):  # Mesh generation
            if self.mesh_process:
                mem.append(self.mesh_process.max_memory)
        if self.adaptive_pass:  # Adaptive passes
            pass_names = [s for s in self.adaptive_pass.process_steps if "Adaptive Pass" in s]
            for pass_name in pass_names[:num_passes]:
                mem.append(self.adaptive_pass.steps[pass_name].max_memory)

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
        if hasattr(self, "elapsed_time"):
            repr_str += f"Elapsed time: {str(self.elapsed_time)}"
        return repr_str

    @pyaedt_function_handler()
    def __repr__(self):
        repr_str = f"Instance of {self.__class__.__name__}\n"
        if hasattr(self, "_product_str"):
            repr_str += f"{self.product}, version: {self.product_version}\n"
        return repr_str

    @property
    def max_time(self):
        """Maximum time in a transient simulation."""
        if self.is_transient:
            if len(self.transient_step.time_steps) > 0:
                return max(self.transient_step.time_steps)
            else:
                return None
        else:
            return None

    @property
    def time_steps(self):
        """Return a list of time steps."""
        if self.transient_step:
            return self.transient_step.time_steps
        else:
            return None

    @pyaedt_function_handler()
    def time_keys(self, max_time):
        """Return keys for all time steps less than ``max_time``"""
        return self.transient_step.time_step_keys(max_time)


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
            profile_data = SimulationProfile(process_group)
            if profile_data.status:
                groups.append(profile_data)
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
        if hasattr(self, "_profile_data"):
            try:
                return len(self._profile_data)
            except Exception as e:
                logging.warning(f"Error parsing profile: {e}")
                return 0
        else:
            try:
                return len(self._profile_dict)
            except Exception as e:
                logging.warning(f"Error parsing profile: {e}")
                return 0

    # @pyaedt_function_handler()
    # def __repr__(self):
    #    repr_str = f"{self.__class__.__name__} of length {len(self)}:\n"
    #     for key, value in self.items():
    #         try:
    #             repr_str += f"  {key}: {value}\n"
    #         except Exception as e:
    #             logging.error(f"Error parsing profile: {e}")
    #    return str(repr_str)

    @pyaedt_function_handler()
    def keys(self):
        if len(self._profile_data) > 0:
            return self._profile_data.keys()
        else:
            return self._profile_dict.keys()
