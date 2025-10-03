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
from difflib import SequenceMatcher
from functools import total_ordering
import inspect
from pathlib import Path
import re
from types import MappingProxyType
from typing import List
from typing import Optional
from typing import Union
import warnings

try:
    import pandas as pd
except ImportError:  # pragma: no cover
    pd = None
    warnings.warn(
        "The Pandas module is required to run some functionalities of PostProcess.\nInstall with \n\npip install pandas"
    )

from ansys.aedt.core.aedt_logger import pyaedt_logger as logging
from ansys.aedt.core.base import PyAedtBase
from ansys.aedt.core.generic.general_methods import pyaedt_function_handler
from ansys.aedt.core.generic.numbers_utils import Quantity
from ansys.aedt.core.modeler.cad.elements_3d import BinaryTreeNode


def string_to_time(time_string: str) -> timedelta:
    """
    Convert a string to a :class:`datetime.timedelta` object.

    Parameters
    ----------
    time_string : str
        Time string in the format "hh:mm:ss"

    Returns
    -------
    :class:`datetime.timedelta`

    Examples
    --------
    >>> time_object = string_to_time("01:02:03")
    """
    h, m, s = None, None, None
    h, m, s = map(int, time_string.split(":"))
    if h or m or s:
        return timedelta(hours=h, minutes=m, seconds=s)
    else:
        return timedelta(seconds=0)


def format_timedelta(time_delta: Optional[Union[str, timedelta]]) -> str:
    """Format :class:`datetime.timedelta` for tables.

    Parameters
    ----------
    time_delta : :class:`datetime.timedelta` or str
        Timedelta to be formatted. Non-timedelta values are converted to `str` unchanged.

    Returns
    -------
    str
    ``"DD days HH:MM:SS"`` if days are present, otherwise ``"HH:MM:SS"``.
    """
    if not isinstance(time_delta, timedelta):
        return str(time_delta)

    total_seconds = int(time_delta.total_seconds())
    days, rem = divmod(total_seconds, 86400)
    hours, rem = divmod(rem, 3600)
    minutes, seconds = divmod(rem, 60)

    if days:
        days_info = f"{days} day{'s' if days > 1 else ''}"
        return f"{days_info} {hours:02}:{minutes:02}:{seconds:02}"
    return f"{hours:02}:{minutes:02}:{seconds:02}"


def _find_common_string(s1, s2):
    match = SequenceMatcher(None, s1, s2).find_longest_match(0, len(s1), 0, len(s2))
    return s1[match.a : match.b + match.size]


def merge_dict(d1: dict, d2: dict) -> dict:
    """Recursively merge two dictionaries using type-aware rules.

    The merge follows these rules when a key exists in both:

    - Identical values: keep that value.
    - Both `dict`: merge recursively with the same algorithm.
    - Both `list`: concatenate and return a sorted list.
    - Both `str`: concatenate separated by a newline.
    - Different or otherwise incompatible types: preserve the value from
    ``d1`` under the original key and store the value from ``d2``
    under ``"<key>_2"``.

    Keys that exist in only one dictionary are copied as-is.
    Keys are ordered using a natural sort that extracts a trailing integer.

    Parameters
    ----------
    d1 : dict
    d2 : dict

    Returns
    -------
    dict
    Merged dictionary.

    """

    def sort_key(k: str):
        parts = k.split()
        try:
            # try parsing the last token as an integer
            num = int(parts[-1])
            # if successful, sort by everything before the number (joined) and then the number
            return " ".join(parts[:-1]), num
        except ValueError:
            # fallback: just sort by the whole string lexicographically
            return k, float("inf")

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


@total_ordering
class MemoryGB(PyAedtBase):
    """Represent memory with conversion to *gigabytes* and arithmetic.

    Parameters
    ----------
    memory_value : float, int, str, or :class:`MemoryGB`
        Memory value. If numeric, assumes gigabytes (``"G"``). If ``str``, expects formats like ``"1 G"``, ``"500 M"``,
        ``"1024 KB"``, or ``"1 TB"``.

    """

    _convert_mem = {"TB": 1000.0, "G": 1.0, "M": 0.001, "MB": 0.001, "KB": 1e-6, "K": 1e-6, "Bytes": 1e-9}

    @pyaedt_function_handler()
    def __init__(self, memory_value: Optional[Union[int, float, str]] = None):
        """Initialize the instance."""
        if isinstance(memory_value, (int, float)):
            self._memory_str = f"{memory_value} G"
        elif isinstance(memory_value, MemoryGB):
            self._memory_str = str(memory_value)
        elif isinstance(memory_value, str):
            self._memory_str = memory_value
        else:
            raise TypeError("Invalid value for memory.")

    @pyaedt_function_handler()
    def __call__(self) -> float:
        """Return the numeric value in gigabytes.

        Returns
        -------
        float
        """
        return self.value

    @property
    def value(self) -> float:
        """Value expressed in gigabytes.

        Returns
        -------
        float
        """
        num, suffix = self._memory_str.split()
        return float(num) * self._convert_mem[suffix]

    @pyaedt_function_handler()
    def __str__(self) -> str:
        """Return the canonical memory string.

        Returns
        -------
        str
        """
        return self._memory_str

    @pyaedt_function_handler()
    def __add__(self, new_memory):
        """Add two :class:`MemoryGB` values.

        Parameters
        ----------
        new_memory : :class:`MemoryGB`

        Returns
        -------
        :class:`MemoryGB`
        """
        if isinstance(new_memory, MemoryGB):
            # Sum values in GB, create new instance with "G" suffix
            total = self.value + new_memory.value
            return MemoryGB(f"{total} G")
        return NotImplemented

    @pyaedt_function_handler()
    def __radd__(self, new_memory):
        """Right-addition to support :func:`sum` and similar.

        When ``new_memory`` is ``0``, return ``self``.
        """
        # Allows sum() and other left-hand operations
        if new_memory == 0:
            return self
        elif isinstance(new_memory, MemoryGB):
            return self.__add__(new_memory)
        return NotImplemented

    @pyaedt_function_handler()
    def __repr__(self):
        """Unambiguous string representation."""
        return self._memory_str

    @pyaedt_function_handler()
    def __eq__(self, new_memory):
        """Equality by comparing values in gigabytes."""
        if isinstance(new_memory, MemoryGB):
            return self.value == new_memory.value
        return NotImplemented

    @pyaedt_function_handler()
    def __lt__(self, new_memory):
        """Ordering by comparing values in gigabytes."""
        if isinstance(new_memory, MemoryGB):
            return self.value < new_memory.value
        return NotImplemented

    @pyaedt_function_handler()
    def __float__(self):
        """Coerce to ``float`` (gigabytes)."""
        return self.value


# Map AEDT names to attribute names and operators that convert the
# data of the property to the correct type.
PROFILE_PROP_MAPPING = MappingProxyType(
    {
        "Cpu time": ("_cpu_time", string_to_time),
        "Real time": ("_real_time", string_to_time),
        "Elapsed Time": ("elapsed_time", string_to_time),
        "Elapsed time": ("elapsed_time", string_to_time),
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
        "Residual": ("residual", float),  # Icepak steady-state only
    }
)


def step_name_map(input_name: str) -> str:
    """Map verbose AEDT step labels to compact names.

    Currently, recognizes labels like ``"Frequency - <value>Hz"`` and
    reduces them to ``"<value>Hz"``. Falls back to the original string if
    no match is found.

    Parameters
    ----------
    input_name : str
    Original AEDT step label.

    Returns
    -------
    str

    """
    pattern = [re.compile(r"^Frequency\s*-\s*([\d.]+(?:[TGMk]?Hz))$")]
    for p in pattern:
        match = p.search(input_name)
        if match:
            return match.group(1)
        else:
            return input_name


# Specify operation for keys having common values.
# Use the following for attributes when calling the __add__() method.
MERGE_OPERATOR = {
    "start_time": min,
    "end_time": max,
    "stop_time": max,
    "host_name": lambda x, y: x + "\n" + y,  # concatenate strings
    "name": _find_common_string,
    # "name": lambda x, y: x + "\n" + y,  # concatenate strings
    "elapsed_time": lambda a, b: a + b,  # Add timedelta instances
    "max_memory": max,
    "frequency_sweeps": merge_dict,
    "transient": merge_dict,
    "_cpu_time": max,
    "_real_time": max,
    "info": lambda x, y: x + "\n" + y,
    "_memory": max,
    "validation_memory": max,
    "steps": merge_dict,
}
ATTR_MAPPING = {
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


class ProfileStepSummary(PyAedtBase):
    """Summary information for a single profile step.

    This light-weight container extracts a small set of common metrics
    (CPU time, real time, memory) from a ``properties`` dictionary.

    Parameters
    ----------
    props : dict
    Properties dictionary as parsed from the solver profile.

    """

    @pyaedt_function_handler()
    def __init__(self, props: dict):
        self.name = props.get("Name", None)
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

    def __add__(self, other):
        self.cpu_time = self.cpu_time + other.cpu_time
        self.real_time = self.real_time + other.real_time
        self.memory = max(self.memory, other.memory)
        return self


class ProfileStep(PyAedtBase):
    """A profile step possibly containing nested sub-steps.

    Parameters
    ----------
    data : class:`ansys.aedt.core.modeler.cad.elements_3d.BinaryTreeNode`
    Node with ``properties`` and ``children`` describing the step.

    """

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

        # A different parser for some profiles is needed
        # because data may be stored in the
        # "info" attribute. Use the regex to extract keywords and values from
        # the Icepak info string. The delimiter in the info string may be
        # either ":" or "="
        elif hasattr(self, "info"):
            key_pattern = "|".join(re.escape(k) for k in PROFILE_PROP_MAPPING)
            pairs = re.findall(rf"(?:(?<=\s)|^)({key_pattern})\s*[:=]\s*([^\s,]+)", self.info)
            for key, value in pairs:
                if key in PROFILE_PROP_MAPPING:
                    if not hasattr(self, PROFILE_PROP_MAPPING[key][0]):
                        setattr(self, PROFILE_PROP_MAPPING[key][0], PROFILE_PROP_MAPPING[key][1](value))

        # Depending on how data is presented in the profile, the end time for
        # the step may have to be calculated. The "_stop_time" property is only
        # temporary.
        if not hasattr(self, "stop_time"):
            if hasattr(self, "start_time") and hasattr(self, "elapsed_time"):
                setattr(self, "stop_time", self.start_time + self.elapsed_time)

    @property
    def process_steps(self) -> Optional[List[str]]:
        """Names of nested process steps, if any.

        Returns
        -------
        list of str or None
        """
        if hasattr(self, "steps"):
            return list(self.steps.keys())
        else:
            return None

    @property
    def cpu_time(self) -> timedelta:
        """CPU time for this step.

        Returns
        -------
        :class:`datetime.timedelta`
        """
        if hasattr(self, "_cpu_time"):
            this_time = self._cpu_time
        else:
            this_time = timedelta(0)
            for v in self.steps.values():
                this_time += v.cpu_time
        return this_time

    @property
    def real_time(self) -> timedelta:
        """Real time for this step.

        Returns
        -------
        :class:`datetime.timedelta`
        """
        if hasattr(self, "_real_time"):
            this_time = self._real_time
        else:
            this_time = timedelta(0)
            for v in self.steps.values():
                this_time += v.real_time
        return this_time

    @staticmethod
    def _clean_key_name(long_key_name: str) -> str:
        """Normalize verbose keys from the profile tree.

        Removes "Group" suffixes and the prefix "Time - ".

        Parameters
        ----------
        long_key_name : str
            Raw key from the profile.

        Returns
        -------
        str
        Cleaned key name.
        """
        return long_key_name.replace("Group", "").strip().replace("Time - ", "").strip()

    @property
    def max_memory(self) -> MemoryGB:
        """Maximum memory over this step and all descendants.

        Returns
        -------
        :class:`MemoryGB`
        """
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
    def table(self, columns: list = None) -> pd.DataFrame:
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
        pandas.DataFrame
            Table of profile process step information for
            the specified property values.
        """
        if columns is None:
            columns = ("elapsed_time", "real_time", "cpu_time", "max_memory")

        data = {"Step": []}  # Contains the data for the Pandas DataFrame.

        if hasattr(self, "steps"):
            for step_name, step_data in self.steps.items():
                name = step_name_map(step_name)  # Replace key with a more meaningful name.
                data["Step"].append(name)
                for prop in columns:
                    if hasattr(step_data, prop):
                        value = getattr(step_data, prop)
                    else:
                        value = "NA"
                    data.setdefault(prop, []).append(value)

            table_out = pd.DataFrame(data)

            # Update formatting of timedelta props
            for p in self.__timedelta_props:
                if p in table_out:
                    table_out[p] = table_out[p].apply(format_timedelta)
        # This is meant to handle Icepak steady-state mesh profile steps which are completely
        # different from all other profile steps. TODO: Improve handling of Icepak mesh profile.
        else:
            for step_name, step_data in self.__dict__.items():
                name = step_name_map(step_name.split("\n")[0])  # Replace key with a more meaningful name.
                data["Step"].append(name)
                for prop in columns:
                    if hasattr(step_data, prop):
                        value = getattr(step_data, prop)
                    else:
                        value = "NA"
                    data.setdefault(prop, []).append(value)
            table_out = pd.DataFrame(data)

        return table_out

    def __add__(self, other):
        """Merge two :class:`ProfileStep` instances.

        The merge combines attributes using :data:`merge_operator` when
        defined; otherwise identical values are kept, or a best-effort
        ``+`` is applied if supported.

        Parameters
        ----------
        new_profile : ProfileStep

        Returns
        -------
        ProfileStep
        New merged instance.
        """
        result = self.__class__.__new__(self.__class__)
        result.__dict__ = {}
        for key in set(self.__dict__) | set(other.__dict__):
            val_self = getattr(self, key, None)
            val_other = getattr(other, key, None)
            if key in self.__dict__ and key in other.__dict__:
                if key in MERGE_OPERATOR:
                    new_val = MERGE_OPERATOR[key](val_self, val_other)
                elif val_self == val_other:
                    new_val = val_self
                else:
                    try:
                        new_val = val_self + val_other
                    except TypeError:
                        new_val = val_self
            elif key in other.__dict__:
                new_val = val_other
            elif key in self.__dict__:
                new_val = val_self
            setattr(result, key, new_val)
        return result


class TransientProfile(ProfileStep):
    """Profile data for a transient solution.

    Parameters
    ----------
    data : class:`ansys.aedt.core.modeler.cad.elements_3d.BinaryTreeNode`
    Node representing the *Transient Solution Group*.

    """

    _SELECT_TRANSIENT = re.compile(r"(\d+(?:\.\d+)?s)")  # Matches a time-step name like "0.01s"

    @pyaedt_function_handler()
    def __init__(self, data):
        super().__init__(data)
        self._time_step_keys = []
        for sim_key in self.steps:
            match = self._SELECT_TRANSIENT.match(sim_key)
            if match:
                self._time_step_keys.append(match.group(1))

    @property
    def time_steps(self) -> List[float]:
        return sorted([float(t.replace("s", "")) for t in self._time_step_keys])

    def time_step_keys(self, max_time: float) -> List[str]:
        """Return time-step labels up to a limit.

        Parameters
        ----------
        max_time : float
        Maximum time step value *inclusive*.

        Returns
        -------
        list of str
        """
        return_val = []
        for k in self._time_step_keys:
            if float(k.replace("s", "")) <= max_time:
                return_val.append(k)
        return return_val

    @property
    def max_time(self) -> Optional[float]:
        """Largest time step in seconds, if any.

        Returns
        -------
        list of float or None
        """
        if hasattr(self, "time_steps"):
            if len(self.time_steps) > 0:
                return max(self.time_steps)
            else:
                return 0.0
        else:
            return None


class FrequencySweepProfile(ProfileStep):
    """Profile data for a frequency sweep.

    Parameters
    ----------
    data : class:`ansys.aedt.core.modeler.cad.elements_3d.BinaryTreeNode`
    sweep_name : str, optional
    """

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
        for key, _ in data.children.items():
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
    def _create_summary(self, data: dict):
        """Parse the sweep summary ``Info`` block and start time.

        Parameters
        ----------
        data : dict
            Properties dictionary of the sweep group.
        """
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
            self.start_time = datetime.strptime(data["Time"], "%m/%d/%Y %H:%M:%S")

    @property
    def frequencies(self) -> List[Quantity]:
        """Frequencies extracted from child groups or summary.

        Returns
        -------
        list or None
        """
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
    def _freq_key(self, freq_str: str) -> str:
        """Build the child group key for a frequency.

        Parameters
        ----------
        freq_str : str
            Frequency string including units.

        Returns
        -------
        str
        """
        return f"Frequency - {freq_str} Group"

    @pyaedt_function_handler()
    def keys(self) -> Optional[List[str]]:
        """Frequency strings for quick iteration.

        Returns
        -------
        list or None
        """
        return [str(f) for f in self.frequencies]

    @pyaedt_function_handler()
    def __getitem__(self, key: str) -> ProfileStep:
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
    def adapt_frequency(self) -> Optional[Quantity]:
        """Frequency used in this adaptive pass."""
        return self._adapt_frequency


@pyaedt_function_handler()
def get_mesh_process_name(group_data: BinaryTreeNode) -> Optional[str]:
    """Return the name of the meshing process group if present.

    Parameters
    ----------
    group_data : class:`ansys.aedt.core.modeler.cad.elements_3d.BinaryTreeNode`
        Simulation group node.

    Returns
    -------
    str or None
    ``"Initial Meshing Group"``, or ``"Meshing Process Group"`` when present, otherwise ``None``.
    """
    mesh_process_names = ["Initial Meshing Group", "Meshing Process Group", "Meshing Process", "Meshing Process 2"]
    names = []
    for name in mesh_process_names:
        if name in group_data.children.keys():
            names.append(name)
    return names if len(names) > 0 else None


def convert_icepak_info(info_str: str) -> tuple:
    """Convert the ``"Info"`` block of the profile ``Summary`` to (timedelta, MemoryGB).

    Parameters
    ----------
    info_str : str
        String containing the Icepak ComEngine profile time and memory.


    Returns
    -------
    time, memory : timedelta, MemoryGB
        Icepak ComEngine profile time and memory.
    """
    pattern = (
        r"Elapsed time\s*:\s*(\d{2}:\d{2}:\d{2})\s*,\s*"
        r"Icepak ComEngine Memory\s*:\s*([\d.]+\s*(?:G|GB|M|MB|K|KB|TB|Bytes))"
    )
    match = re.search(pattern, info_str)
    elapsed, memory = None, None
    if match:
        time_str, mem_str = match.groups()

        # Parse timedelta
        h, m, s = map(int, time_str.split(":"))
        elapsed = timedelta(hours=h, minutes=m, seconds=s)

        # Normalize memory string (add "B")
        if not mem_str.strip().upper().endswith("B"):
            mem_str = mem_str.strip() + "B"

        memory = MemoryGB(mem_str)

    return elapsed, memory


class SimulationProfile(PyAedtBase):
    """Container for all profile data from a single simulation.

    This class parses a *Solution Process Group* and exposes convenience
    accessors for common metrics such as times, memory, passes, sweeps and
    transient steps.

    Parameters
    ----------
    group_data : class:`ansys.aedt.core.modeler.cad.elements_3d.BinaryTreeNode`
    Root node of a solution process group.

    """

    # The following attributes are of type dict. When two SimulationProfile
    # instances are combined, the dictionary attributes are merged by including
    # all unique keys.
    _dict_attributes = (
        "frequency_sweeps",
        "transient",
    )

    @pyaedt_function_handler()
    def __init__(self, group_data: BinaryTreeNode):
        for name in self._dict_attributes:
            setattr(self, name, dict())
        self._update_props_from_dict(group_data.properties)
        self.adaptive_pass = None
        self.mesh_process = None
        self.validation_time = None
        self.validation_memory = None
        self.solve = None
        self.initialize_solver = None
        self.__product = None

        if "Adaptive Meshing Group" in group_data.children.keys():
            self.adaptive_pass = ProfileStep(group_data.children["Adaptive Meshing Group"])
        mesh_process_names = get_mesh_process_name(group_data)
        if mesh_process_names:  # Icepak steady-state can have two mesh-related process steps.
            for name in mesh_process_names:  # TODO: Improve handling of Icepak mesh process step.
                if name in group_data.children.keys():
                    mesh_process = ProfileStep(group_data.children[name])
                    if self.mesh_process:
                        self.mesh_process += mesh_process  # Merge results from the two process steps.
                    else:
                        self.mesh_process = mesh_process

        if "HFSS" in group_data.properties["Product"]:
            if "Design Validation" in group_data.children.keys():
                info = group_data.children["Design Validation"].properties["Info"].split(",")
                time_str = info[0].split(":")[-3:]
                time_str = ":".join([x.strip() for x in time_str])
                memory_str = info[1].strip().split(":")[-1].strip()
                self.validation_time = string_to_time(time_str)
                self.validation_memory = MemoryGB(memory_str)
            if "Frequency Sweep Group" in group_data.children:
                for name, data in group_data.children["Frequency Sweep Group"].children.items():
                    sweep_key = name.replace("Group", "").strip()
                    sweep_key = sweep_key.split("-")[-1].strip()
                    if sweep_key not in self.frequency_sweeps:
                        self.frequency_sweeps[sweep_key] = FrequencySweepProfile(data, sweep_key)

        if "Maxwell" in group_data.properties["Product"] or "Icepak" in group_data.properties["Product"]:
            # Information is stored differently in different products. Icepak steady state uses the
            # "Info" key. Icepak transient and Maxwell transient use "Elapsed Time" and "Memory".
            if "Design Validation" in group_data.children.keys():
                if "Elapsed Time" in group_data.children["Design Validation"].properties:
                    time_str = group_data.children["Design Validation"].properties["Elapsed Time"]
                    self.validation_time = string_to_time(time_str)
                if "Memory" in group_data.children["Design Validation"].properties:
                    memory_str = group_data.children["Design Validation"].properties["Memory"]
                    self.validation_memory = MemoryGB(memory_str)
                if "Info" in group_data.children["Design Validation"].properties:  # TODO: Add test coverage
                    self.validation_time, self.validation_memory = convert_icepak_info(
                        group_data.children["Design Validation"].properties["Info"]
                    )
        if "HPC Group" in group_data.children.keys():
            if "MPI Vendor" in group_data.children["HPC Group"].properties.keys():
                self.mpi_vendor = group_data.children["HPC Group"].properties["MPI Vendor"]
                self.mpi_version = group_data.children["HPC Group"].properties["MPI Version"]
                self.use_mpi = True
        if "Transient Solution Group" in group_data.children:
            self.transient = TransientProfile(group_data.children["Transient Solution Group"])
        if "Solver Initialization" in group_data.children.keys():
            self.initialize_solver = ProfileStepSummary(group_data.children["Solver Initialization"].properties)
        if "Populate Solver Input" in group_data.children.keys():
            self.populate_solver_input = ProfileStepSummary(group_data.children["Populate Solver Input"].properties)
        if "Solve" in group_data.children.keys():
            self.solve = ProfileStepSummary(group_data.children["Solve"].properties)

        # Some solution setups do not provide "Status" but the solution has run successfully.
        if not hasattr(self, "status"):
            if hasattr(self, "adaptive_pass") or hasattr(self, "frequency_sweeps") or hasattr(self, "transient"):
                setattr(self, "status", "completed")

    @pyaedt_function_handler()
    def __add__(self, new_profile):
        """Combine two profiles field-by-field.

        Attributes listed in :data:`merge_operator` use that rule, others
        attempt ``+`` or keep the left value. Empty values (``None``, ``{}``,
        ``[]``) on one side are replaced by the non-empty counterpart.


        Parameters
        ----------
        new_profile : SimulationProfile

        Returns
        -------
        SimulationProfile
        New merge
        """
        # Instantiate result
        result = self.__class__.__new__(self.__class__)
        result.__dict__ = {}

        def is_empty(val):
            return val is None or val == {} or val == []

        for key in set(self.__dict__) | set(new_profile.__dict__):  # Iterate through all keys.
            val_self = getattr(self, key, None)
            val_other = getattr(new_profile, key, None)
            if val_self == val_other:
                setattr(result, key, val_self)
            elif (
                key in self.__dict__
                and not is_empty(val_self)
                and key in new_profile.__dict__
                and not is_empty(val_other)
            ):  # key exists in both instances.
                if key in MERGE_OPERATOR:
                    new_val = MERGE_OPERATOR[key](val_self, val_other)
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
            elif key in new_profile.__dict__ and not is_empty(val_other):
                setattr(result, key, val_other)
            elif key in self.__dict__:
                setattr(result, key, val_self)
            elif key in new_profile.__dict__:
                setattr(result, key, val_other)
        return result

    @pyaedt_function_handler()
    def _update_props_from_dict(self, props_dict: dict):
        """Populate attributes from a properties dict.

        Parameters
        ----------
        props_dict : dict
        Raw properties where keys are AEDT labels.
        """
        for key, value in props_dict.items():
            if key in PROFILE_PROP_MAPPING:
                setattr(self, PROFILE_PROP_MAPPING[key][0], PROFILE_PROP_MAPPING[key][1](value))

    @property
    def product(self) -> Optional[str]:
        """Product name parsed from the ``Product`` field.

        Returns
        -------
        str
        """
        if not self.__product:
            self.__product = self._product_str.split()[0]
        return self.__product

    @product.setter
    def product(self, value):
        self.__product = str(value)

    @property
    def product_version(self) -> str:
        """Product version string parsed from ``Product``.

        Returns
        -------
        str
        """
        return self._product_str.split()[-1]

    @pyaedt_function_handler()
    def cpu_time(self, num_passes: int = None, max_time: float = None) -> timedelta:
        """Total CPU time for adaptive refinement or transient simulations.

           The total CPU time is the sum of execution time for
           all solution process steps and cores. By default, all adaptive passes (for
           adaptive refinement) or all time steps (for transient simulation)
           are included in the return value.
           "CPU time" represents the time required for a process if it were run on
           a single core. The benefit of multicore processing can be estimated by the ratio
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
    def real_time(self, num_passes: int = None, max_time: float = None) -> timedelta:
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
            if hasattr(self, "transient"):
                if self.is_transient:
                    max_time = self.max_time  # Transient simulation
        elif max_time > self.max_time:
            max_time = self.max_time
        total_time = timedelta(0)

        if num_passes:
            pass_names = [s for s in self.adaptive_pass.process_steps if "Pass" in s]
            for pass_name in pass_names[:num_passes]:
                total_time += getattr(self.adaptive_pass.steps[pass_name], attr_name)
        elif max_time:
            time_keys = self.time_keys(max_time)
            time_step_values = [getattr(self.transient.steps[k], attr_name) for k in time_keys]
            total_time += sum(time_step_values, timedelta(0))
        elif hasattr(self, "solve"):  # Steady-state.
            total_time += getattr(self.solve, attr_name)
        return total_time

    @property
    def num_adaptive_passes(self) -> int:
        """Number of adaptive passes available.

        Returns
        -------
        int
        """
        if self.adaptive_pass:
            return sum("Pass" in s for s in self.adaptive_pass.process_steps)
        else:
            return 0

    @property
    def is_transient(self) -> bool:
        """Transient profile is available.

        Returns
        -------
        bool
        """
        return bool(self.transient)

    @property
    def has_frequency_sweep(self) -> bool:
        """Frequency sweep available.

        Returns
        -------
        bool
        """
        if len(self.frequency_sweeps) > 0:
            return True
        else:
            return False

    @pyaedt_function_handler()
    def max_memory(self, num_passes: int = None) -> MemoryGB:
        """Maximum memory used in the solve process.

        Parameters
        ----------
        num_passes : int, optional
            Number of adaptive passes to consider. The default is ``None``.

        Returns
        -------
        :class:`MemoryGB`
        Maximum memory used in the adaptive mesh refinement process.
        """
        num_passes = self._check_num_passes(num_passes)
        mem = []
        if self.is_transient:
            mem += [m.max_memory for m in self.transient.steps.values()]
        if hasattr(self, "mesh_process"):  # Mesh generation
            if self.mesh_process:
                mem.append(self.mesh_process.max_memory)
        if self.adaptive_pass:  # Adaptive passes
            pass_names = [s for s in self.adaptive_pass.process_steps if "Adaptive Pass" in s]
            for pass_name in pass_names[:num_passes]:
                mem.append(self.adaptive_pass.steps[pass_name].max_memory)

        # All other processes
        for _, self_attr in vars(self).items():
            if callable(self_attr):
                continue
            if hasattr(self_attr, "memory"):
                this_mem = getattr(self_attr, "memory")
                if this_mem:
                    mem.append(getattr(self_attr, "memory"))

        return max(mem, default=0)

    @pyaedt_function_handler()
    def _check_num_passes(self, num_passes: int) -> int:
        """Return a valid value for the number of adaptive passes.

        Given an integer, return a valid
        value for the total number of adaptive passes.

        Parameters
        ----------
        num_passes : int
            Number of adaptive passes.

        Returns
        -------
        int
        Valid number of adaptive passes.
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
        """Human-readable representation including elapsed time when present."""
        repr_str = self.__repr__()
        if hasattr(self, "elapsed_time"):
            repr_str += f"Elapsed time: {str(self.elapsed_time)}"
        return repr_str

    @pyaedt_function_handler()
    def __repr__(self):
        """Unambiguous representation including product and version."""
        repr_str = f"Instance of {self.__class__.__name__}\n"
        if hasattr(self, "_product_str"):
            repr_str += f"{self.product}, version: {self.product_version}\n"
        return repr_str

    @property
    def max_time(self) -> Optional[float]:
        """Maximum transient time in seconds.

        Returns
        -------
        float
        """
        if self.is_transient:
            if len(self.transient.time_steps) > 0:
                return max(self.transient.time_steps)
            else:
                return None
        else:
            return None

    @property
    def time_steps(self) -> Optional[List[float]]:
        """List of transient time steps.

        Returns
        -------
        list of float
        """
        if self.transient:
            return self.transient.time_steps
        else:
            return None

    @pyaedt_function_handler()
    def time_keys(self, max_time: float) -> List[str]:
        """Return labels for transient steps not exceeding ``max_time``.

        Parameters
        ----------
        max_time : float
            Time threshold in seconds.

        Returns
        -------
        list of str
        """
        return self.transient.time_step_keys(max_time)


@pyaedt_function_handler()
def _merge_profiles(profiles: List) -> SimulationProfile:
    """Merge a list of :class:`SimulationProfile` into one.

    Parameters
    ----------
    profiles : list of :class:`SimulationProfile`
    Profiles to merge pairwise using ``+``.

    Returns
    -------
    :class:`SimulationProfile`
    Combined profiles
    """
    this_profile = profiles[0]
    for p in profiles[1:]:
        # Merge simulation groups
        this_profile = this_profile + p
    return this_profile


@pyaedt_function_handler()
def _parse_profile_data(profile_data: BinaryTreeNode) -> SimulationProfile:
    """
    Generate the SimulationProfile object from the profile data.

    Parameters
    ----------
    profile_data : BinaryTreeNode
        The raw profile data.

    Returns
    -------
    :class:`pyaedt.modules.SolveSetup.SimulationProfile`
        An instance of the SimulationProfile class.

    """
    profiles = []
    for profile_name, profile_group in profile_data.children.items():  # Loop through "Solution Process Groups".
        try:
            profile = SimulationProfile(profile_group)
            if profile.status:
                profiles.append(profile)
        except Exception as e:
            logging.error(f"Error parsing {profile_name}: {e}")
    return _merge_profiles(profiles)  # Merge "groups" into a single simulation profile.


class Profiles(Mapping, PyAedtBase):
    """Provide an interface to solver profiles.

    The Profiles class is iterable. Individual profiles are accessed via the unique
    key made up of "setup_name - variation". If there are no variations available, the
    unique key is the setup name.

    Examples
    --------
    HFSS 3D Layout
    >>> app = Hfss3DLayout(project="solved_h3d_project")
    >>> profiles = app.setups[0].get_profile()
    >>> key_for_profile = list(profiles.keys())[0]
    >>> print(key_for_profile)
        'HFSS Setup 1'
    >>> profiles[key_for_profile].product
        'HFSS3DLayout'
    >>> print(f"Elapsed time: {profiles[key_for_profile].elapsed_time}")
        Elapsed time: 0:01:39
    >>> print(f"Number of adaptive passes: {profiles[key_for_profile].num_adaptive_passes}")
        Number of adaptive passes: 6
    >>> fsweeps = profiles[key_for_profile].frequency_sweeps
    >>> sweep_name = list(fsweeps.keys())[0]  # Select the first sweep
    >>> print(f"Frequency sweep '{sweep_name}' calculated {len(fsweeps[sweep_name].frequencies)} frequency points.")
        Frequency sweep 'Sweep 1' calculated 74 frequency points. Maxwell 2D (Transient)
    >>> app = Maxwell2d(project="solved_m2d_project")
    >>> profile_name = list(profiles.keys())[0]
    >>> print(f"Profile name: {profile_name}")
        Profile name: Setup1 - fractions='4'
    >>> print(f"Elapsed time: {profiles[profile_name].elapsed_time}")
        Elapsed time: 0:01:24
    >>> print(f"Number of time steps: {len(profiles[profile_name].time_steps)}")
        Number of time steps: 80
    """

    @pyaedt_function_handler()
    def __init__(self, profile_dict):  # Omit setup_type ? setup_type="HFSS 3D Layout"
        self._profile_data = dict()
        if isinstance(profile_dict, dict):
            self._profile_dict = profile_dict
        else:
            raise TypeError("Profile must be a dictionary.")
        try:
            for key, value in profile_dict.items():
                self._profile_data[key] = _parse_profile_data(value)
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
        """Iterate over mapping keys."""
        if len(self._profile_data) > 0:
            return iter(self._profile_data)
        else:
            return iter(self._profile_dict)

    @pyaedt_function_handler()
    def __setitem__(self, key, value):
        raise TypeError(f"{self.__class__.__name__} is read-only and does not support item assignment.")

    @pyaedt_function_handler()
    def __len__(self) -> int:
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

    @pyaedt_function_handler()
    def __repr__(self):
        """Unambiguous representation of the mapping."""
        repr_str = f"{self.__class__.__name__}({dict(self)!r})"
        return str(repr_str)

    @pyaedt_function_handler()
    def keys(self):
        """Expose the keys of the underlying mapping."""
        if len(self._profile_data) > 0:
            return self._profile_data.keys()
        else:
            return self._profile_dict.keys()
