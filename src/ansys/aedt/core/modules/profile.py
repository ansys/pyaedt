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
from datetime import datetime, timedelta

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
        setup, variation_string = profile_key.split('-')
        setup_name = setup.strip()
        variation = Variation(variation_string)
        return setup_name, variation
    else:
        return profile_key, None  # HFSS 3DLayout doesn't use the variation in the setup name.

def _select_group(sim_groups):
    if len(sim_groups) > 0:
        # Find the group with the max number of adaptive passes.
        this_group = max(sim_groups, key=lambda g: len(g.adaptive_pass))
    else:
        this_group =  sim_groups[0]
    return this_group

class MemoryGB(object):
    """Class to represent memory in Gigabytes."""

    convert_mem = {"G": 1.0, "M": 0.001, "KB": 1E-6}

    def __init__(self, memory_string):
        self._memory_str = memory_string

    def __call__(self):
        return self.value

    @property
    def value(self):
        num, suffix = self._memory_str.split()
        return num * self.convert_mem[suffix]

    def __str__(self):
        return self._memory_str

    def __add__(self, other):
        if isinstance(other, MemoryGB):
            # Sum values in GB, create new instance with "G" suffix
            total = self.value + other.value
            return MemoryGB(f"{total} G")
        return NotImplemented

    def __radd__(self, other):
        # Allows sum() and other left-hand operations
        if other == 0:
            return self
        elif isinstance(other, MemoryGB):
            return self.__add__(other)
        return NotImplemented

    def __repr__(self):
        return self._memory_str

class ProfileStep(object):

    def __init__(self, data):  # data is the dict with the profile step data

        self._data = data
        self._cpu_time = dict()
        self._real_time = dict()
        self._memory = dict()
        self._disk_space = dict()
        self._num_tets = dict()

    @property
    def process_steps(self):
        return list(self._cpu_time.keys())  # Return all keys.

    @property
    def cpu_time(self):
        return sum(self._cpu_time.values())

    @property
    def real_time(self):
        return sum(self._real_time.values())

    @property
    def max_memory(self):
        return max(self._memory.values())

    def _get_time(self, key, name_string):
        return string_to_time(self._data.children[key].properties[name_string])

    def _get_memory(self, key, name_string):
        return MemoryGB(self._data.children[key].properties[name_string])

    def _get_prop(self, key, name_string):
        return self._data.children[key].properties[name_string]

class InitialMesh(ProfileStep):
    """Information about the initial mesh generation."""

    _type = None

    def __init__(self, data):
        super().__init__(data)

        self._elapsed_time = string_to_time(data.properties["Elapsed Time"])

        self._cpu_time["mesh"] = self._get_time("Mesh", "Cpu time")
        self._real_time["mesh"] = self._get_time("Mesh","Real time")
        self._memory["mesh"] = self._get_memory("Mesh", "Memory")
        self._type = self._get_prop("Mesh", "Type")
        self._num_tets["mesh"] = self._get_prop("Mesh", "Tetrahedra")

        self._cpu_time["post"] = self._get_time("Post", "Cpu time")
        self._real_time["post"] = self._get_time("Post", "Real time")
        self._memory["post"] = self._get_memory("Post", "Memory")
        self._num_tets["post"] = self._get_prop("Post", "Tetrahedra")

        self._cpu_time["lambda_refine"] = self._get_time("Lambda Refine", "Cpu time")
        self._real_time["lambda_refine"] = self._get_time("Lambda Refine", "Real time")
        self._memory["lambda_refine"] = self._get_memory("Lambda Refine", "Memory")
        self._num_tets["lambda_refine"] = self._get_prop("Lambda Refine", "Tetrahedra")

        self._cpu_time["manual_refine"] = self._get_time("Manual Refine", "Cpu time")
        self._real_time["manual_refine"] = self._get_time("Manual Refine", "Real time")
        self._memory["manual_refine"] = self._get_memory("Manual Refine", "Memory")
        self._num_tets["manual_refine"] = self._get_prop("Manual Refine", "Tetrahedra")

        self._cpu_time["sim_setup"] = self._get_time("Simulation Setup", "Cpu time")
        self._real_time["sim_setup"] = self._get_time("Simulation Setup", "Real time")
        self._memory["sim_setup"] = self._get_memory("Simulation Setup", "Memory")
        self._num_tets["sim_setup"] = self._get_prop("Simulation Setup", "Tetrahedra")
        self._disk_space["sim_setup"] = self._get_prop("Simulation Setup", "Disk")

        self._cpu_time["port_adapt"] = self._get_time("Port Adapt", "Cpu time")
        self._real_time["port_adapt"] = self._get_time("Port Adapt", "Real time")
        self._memory["port_adapt"] = self._get_memory("Port Adapt", "Memory")
        self._num_tets["port_adapt"] = self._get_prop("Port Adapt", "Tetrahedra")
        self._disk_space["port_adapt"] = self._get_prop("Port Adapt", "Disk")


        self._cpu_time["port_refine"] = self._get_time("Port Refine", "Cpu time")
        self._real_time["port_refine"] = self._get_time("Port Refine", "Real time")
        self._memory["port_refine"] = self._get_memory("Port Refine", "Memory")
        self._num_tets["port_refine"] = self._get_prop("Port Refine", "Tetrahedra")

class AdaptivePass(ProfileStep):
    """Information for a single adaptive pass."""

    def __init__(self, data):
        super().__init__(data)
        self._adapt_frequency = data.properties["Frequency"]

        self._cpu_time["setup"] = self._get_time("Simulation Setup", "Cpu time")
        self._real_time["setup"] = self._get_time("Simulation Setup", "Real time")
        self._memory["setup"] = self._get_memory("Simulation Setup", "Memory")
        self._disk_space["setup"] = self._get_memory("Simulation Setup", "Disk")
        self._num_tets["setup"] = self._get_prop("Simulation Setup", "Tetrahedra")

        self._cpu_time["matrix_assembly"] = self._get_time("Matrix Assembly", "Cpu time")
        self._real_time["matrix_assembly"] = self._get_time("Matrix Assembly", "Real time")
        self._memory["matrix_assembly"] = self._get_memory("Matrix Assembly", "Memory")
        self._disk_space["matrix_assembly"] = self._get_memory("Matrix Assembly", "Disk")
        self._num_tets["matrix_assembly"] = self._get_prop("Matrix Assembly", "Tetrahedra")

        self._cpu_time["solve"] = self._get_time("Matrix Solve", "Cpu time")
        self._real_time["solve"] = self._get_time("Matrix Solve", "Real time")
        self._memory["solve"] = self._get_memory("Matrix Solve", "Memory")
        self._cores = self._get_prop("Matrix Solve", "Cores")
        self._matrix_bw = self._get_prop("Matrix Solve", "Matrix bandwidth")
        self._solve_type = self._get_prop("Matrix Solve", "Type")
        self._disk_space["solve"] = self._get_memory("Matrix Solve", "Disk")
        self._matrix_size = self._get_prop("Matrix Solve", "Matrix size")

        self._cpu_time["field_recovery"] = self._get_time("Field Recovery", "Cpu time")
        self._real_time["field_recovery"] = self._get_time("Field Recovery", "Real time")
        self._memory["field_recovery"] = self._get_memory("Field Recovery", "Memory")

        self._cpu_time["data_transfer"] = self._get_time("Data Transfer", "Cpu time")
        self._real_time["data_transfer"] = self._get_time("Data Transfer", "Real time")
        self._memory["data_transfer"] = self._get_memory("Data Transfer", "Memory")

class SimulationProfile(object):
    """Simulation group data

    This class encapsulates all profile data from a single simulation.

    """

    elapsed_time = timedelta(0)
    start_time = None
    stop_time = None
    host_name = None
    num_cores = None
    os = None
    status = None
    adaptive_pass = []

    def __init__(self, sim_group_data):
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
                for pass_name, pass_info in sim_group_data.children["Adaptive Meshing Group"].children.items():
                    self.adaptive_pass.append(AdaptivePass(pass_info))
                #self.initial_mesh = InitialMesh(sim_group_data.children["Initial Meshing Group"])


def extract_profile_data(profile_data):
    """

    Parameters
    ----------
    profile_data : BinaryTreeNode
        The full profile data.

    """
    groups = []
    for group_name, process_group in profile_data.children.items():
        sim_group_data = SimulationProfile(process_group)
        if sim_group_data.status:
            groups.append(sim_group_data)
    return _select_group(groups)  # ProfileData will contain the data from one simulation group.


class Profiles(Mapping):
    """Provide a simple interface to view and parse the solver profiles.

    The Profiles class is iterable. Individual profiles are accessed via the unique
    key comprised of "setup_name - variation".

    Examples
    --------

    """

    def __init__(self, profile_dict):
        self._profile_data = dict()
        if type(profile_dict) is dict:
            self._profile_dict = profile_dict
        else:
            raise TypeError('Profile must be a dictionary.')
        for key, value in profile_dict.items():
            self._profile_data[key] = extract_profile_data(value)

    def __getitem__(self, key):
        if len(self._profile_data) > 0:
            return self._profile_data[key]
        else:
            return self._profile_dict[key]

    def __iter__(self):
        if len(self._profile_data) > 0:
            return iter(self._profile_data)
        else:
            return iter(self._profile_dict)

    def __setitem__(self, key, value):
        raise TypeError(f"{self.__class__.__name__} is read-only and does not support item assignment.")

    def __len__(self):
        if len(self._profile_data) > 0:
            return len(self._profile_data)
        else:
            return len(self._profile_dict)



