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

from __future__ import annotations

from dataclasses import dataclass
from enum import IntEnum
import json
import logging
import os
from pathlib import Path
import platform
import re
from typing import Optional
from typing import Union

import tomli
import tomli_w

DEFAULT_AUTO_HPC = False
"""Default setting for Auto HPC."""
DEFAULT_CLUSTER_NAME = "ClusterName"
"""Default cluster name for the job submission."""
DEFAULT_CUSTOM_SUBMISSION_STRING = ""
"""Default custom submission string for the job submission."""
DEFAULT_JOB_NAME = "AEDT Simulation"
"""Default job name for the job submission."""
DEFAULT_NB_CORES = 4
"""Default number of cores for the job submission."""
DEFAULT_NB_GPUS = 0
"""Default number of GPUs for the job submission."""
DEFAULT_NB_NODES = 1
"""Default number of nodes for the job submission."""
DEFAULT_NB_TASKS = 4
"""Default number of tasks for the job submission."""
DEFAULT_RAM_LIMIT = 100
"""Default fraction of available RAM to be used for the job submission."""
DEFAULT_RAM_PER_CORE = 2.0
"""Default RAM in GB to be used per core for the job submission."""
JOB_TEMPLATE_PATH = Path(__file__).resolve().parent.parent / "misc" / "Job_Settings_Template.txt"
"""Path to the job settings template file."""


class HPCMethod(IntEnum):
    """Enumeration for HPC settings.

    Values specify the method used for HPC distribution in
     the ``"Job_Settings.areg"`` file.

    Attributes
    ----------
    USE_TASKS_AND_CORES:
        Use tasks and cores for HPC submission.
    USE_RAM_CONSTRAINED:
        Use constrained RAM for HPC submission.
    USE_NODES_AND_CORES:
        Specify only number of nodes and cores.
    USE_AUTO_HPC:
        Use Auto HPC.
    """

    USE_TASKS_AND_CORES = 1
    USE_RAM_CONSTRAINED = 2
    USE_NODES_AND_CORES = 3
    USE_AUTO_HPC = 4


def path_string(path: Path):
    """Convert the path to a string.

    If the path has whitespace and the OS is Windows, the path will be
    enclosed in double quotes.
    """

    path_str = str(path)
    if platform.system() == "Windows" and " " in path_str:
        return f'"{path_str}"'  # wrap in double quotes
    return path_str


def get_aedt_exe(version=None):
    """Retrieve the full path to the Ansys AEDT executable.

    Parameters
    ----------
    version : str
        Version of Ansys Electronics Desktop. For example ``"25.2"``.
        The default will be the newest currently installed version of
        AEDT.

    Returns
    -------
    Full path to the Ansys AEDT executable.
    """

    exe_name = "ansysedt.exe"
    #  Check in the current path.
    version_folder = None
    if version:
        version_folder = "v" + version.replace(".", "")
    matched_paths = []
    if "PATH" in os.environ.keys():
        for path_str in os.environ["PATH"].split(os.pathsep):
            path = Path(path_str).resolve()
            parts = path.parts

            # Check for the default installation folder "AnsysEM"
            for i in range(len(parts) - 1):
                if parts[i] == "AnsysEM":
                    if version_folder:
                        if parts[i + 1] == version_folder:
                            matched_paths.append(str(path))
                            return Path(path) / exe_name
                    else:
                        matched_paths.append(str(path))
                        return Path(path) / exe_name

    pattern = re.compile(r"ANSYSEM_ROOT(\d{3})")  # Match e.g., ANSYSEM_ROOT251
    version_map = {}

    # Build a map of version suffix -> path
    for key in os.environ:
        match = pattern.fullmatch(key)
        if match:
            suffix = match.group(1)  # e.g., "251"
            version_map[suffix] = os.environ[key]

    if version is None:
        # Return the highest version (sorted numerically)
        latest_suffix = max(version_map.keys(), key=lambda s: int(s))
        return Path(version_map[latest_suffix]) / exe_name

    # Convert version like "25.1" -> "251"
    desired_suffix = version.replace(".", "")
    return Path(version_map.get(desired_suffix)) / exe_name


def load_template(template_path: Path) -> str:
    """Load the job settings template from a file."""
    with template_path.open("r", encoding="utf-8") as f:
        return f.read()


def render_template(data: JobConfigurationData, template_path: Path) -> str:
    """Render the job settings template with the provided data."""
    pattern = re.compile(r"\{\{(\w+)\}\}")

    def replacer(match):
        key = match.group(1)
        if not hasattr(data, key):
            raise AttributeError(f"Missing attribute '{key}' in JobConfigurationData for template replacement")
        value = getattr(data, key)
        if key in ("windows_value", "linux_value"):
            if value is None:
                return "0:"
            return f"1: '{value}'"
        if isinstance(value, bool):  # Boolean need to be lower case.
            return str(value).lower()
        elif value is None:  # Return an empty string if None
            return ""
        elif isinstance(value, HPCMethod):
            return str(value.value)
        return str(value)

    return pattern.sub(replacer, load_template(template_path))


class ResourcesConfiguration:
    """Configuration for resources used in the job submission."""

    def __init__(
        self,
        cores_per_task: Optional[int],
        exclusive: bool,
        nb_cores: int,
        nb_gpus: Optional[int],
        nb_nodes: int,
        nb_tasks: int,
        max_tasks_per_node: Optional[int],
        ram_limit: int,
        ram_per_core: float,
    ):
        """Configuration for resources used in the job submission."""
        self.__cores_per_task = self.__validate_optional_positive_int("cores_per_task", cores_per_task)
        self.__exclusive = exclusive
        self.__nb_cores = self.__validate_positive_int("nb_cores", nb_cores)
        self.__nb_gpus = self.__validate_optional_positive_int("nb_gpus", nb_gpus, strict=False)
        self.__nb_nodes = self.__validate_positive_int("nb_nodes", nb_nodes)
        self.__nb_tasks = self.__validate_positive_int("nb_tasks", nb_tasks)
        self.__max_tasks_per_node = self.__validate_optional_positive_int(
            "max_tasks_per_node", max_tasks_per_node, strict=False
        )
        self.__ram_limit = self.__validate_positive_int("ram_limit", ram_limit)
        self.__ram_per_core = self.__validate_positive_float("ram_per_core", ram_per_core)

    def __validate_positive_int(self, name, value, strict=True):
        """Validate that the value is an integer > 0 (strict) or >= 0 (non-strict)."""
        if not isinstance(value, int):
            raise ValueError(f"{name} must be an integer, got {type(value).__name__}.")

        if strict and value <= 0:
            raise ValueError(f"{name} must be a positive integer (> 0), got {value}.")
        elif not strict and value < 0:
            raise ValueError(f"{name} must be a non-negative integer (>= 0), got {value}.")

        return value

    def __validate_positive_float(self, name, value):
        """Validate that the value is a foat greater than zero."""
        if not isinstance(value, float):
            raise ValueError(f"{name} must be a float, got {type(value).__name__}.")

        if value <= 0:
            raise ValueError(f"{name} must be a positive float (> 0), got {value}.")

        return value

    def __validate_optional_positive_int(self, name, value, strict=True):
        """Validate that the value is either None or a valid integer.

        If strict is True, the value must be > 0; otherwise, it can be >= 0.
        """
        if value is None:
            return None
        return self.__validate_positive_int(name, value, strict=strict)

    @property
    def cores_per_task(self) -> Optional[int]:
        return self.__cores_per_task

    @cores_per_task.setter
    def cores_per_task(self, value: Optional[int]):
        self.__cores_per_task = self.__validate_optional_positive_int("cores_per_task", value)

    @property
    def exclusive(self) -> bool:
        return self.__exclusive

    @exclusive.setter
    def exclusive(self, value: bool):
        if not isinstance(value, bool):
            raise ValueError(f"exclusive must be a boolean, got {type(value).__name__}.")
        self.__exclusive = value

    @property
    def nb_cores(self) -> int:
        return self.__nb_cores

    @nb_cores.setter
    def nb_cores(self, value: int):
        self.__nb_cores = self.__validate_positive_int("nb_cores", value)

    @property
    def nb_gpus(self) -> Optional[int]:
        return self.__nb_gpus

    @nb_gpus.setter
    def nb_gpus(self, value: Optional[int]):
        self.__nb_gpus = self.__validate_optional_positive_int("nb_gpus", value, strict=False)

    @property
    def nb_nodes(self) -> int:
        return self.__nb_nodes

    @nb_nodes.setter
    def nb_nodes(self, value: int):
        self.__nb_nodes = self.__validate_positive_int("nb_nodes", value)

    @property
    def nb_tasks(self) -> int:
        return self.__nb_tasks

    @nb_tasks.setter
    def nb_tasks(self, value: int):
        self.__nb_tasks = self.__validate_positive_int("nb_tasks", value)

    @property
    def max_tasks_per_node(self) -> Optional[int]:
        return self.__max_tasks_per_node

    @max_tasks_per_node.setter
    def max_tasks_per_node(self, value: Optional[int]):
        self.__max_tasks_per_node = self.__validate_optional_positive_int("max_tasks_per_node", value, strict=False)

    @property
    def ram_limit(self) -> int:
        return self.__ram_limit

    @ram_limit.setter
    def ram_limit(self, value: int):
        self.__ram_limit = self.__validate_positive_int("ram_limit", value)

    @property
    def ram_per_core(self) -> float:
        return self.__ram_per_core

    @ram_per_core.setter
    def ram_per_core(self, value: float):
        self.__ram_per_core = self.__validate_positive_float(value)

    def check_consistency(self):
        """Check the consistency of the resource configuration."""
        if self.__max_tasks_per_node is not None:
            if self.__nb_tasks > self.__max_tasks_per_node:
                raise ValueError(
                    f"Number of tasks ({self.__nb_tasks}) exceeds max tasks per node ({self.__max_tasks_per_node})."
                )
            if self.__nb_tasks // self.__nb_nodes > self.__max_tasks_per_node:
                raise ValueError(
                    f"Tasks per node ({self.__nb_tasks // self.__nb_nodes}) exceeds max tasks per node "
                    f"({self.__max_tasks_per_node})."
                )
        if self.__cores_per_task is not None:
            if self.__nb_cores % self.__cores_per_task != 0:
                raise ValueError(
                    f"Number of cores ({self.__nb_cores}) is not a multiple of cores per task "
                    f"({self.__cores_per_task})."
                )
            if self.__nb_tasks * self.__cores_per_task != self.__nb_cores:
                raise ValueError(
                    f"Number of tasks ({self.__nb_tasks}) * cores per task ({self.__cores_per_task}) "
                    f"does not equal number of cores ({self.__nb_cores})."
                )

    def align_dependent_attributes(self):
        """Align dependent attributes based on the current configuration."""
        if self.__cores_per_task is None:
            logging.info("Cores per task is not set. Setting it based on the number of cores and tasks.")
            self.__cores_per_task = self.__nb_cores // self.__nb_tasks
        if self.__nb_gpus is None:
            logging.info("Number of GPUs is not set. Setting it to 0.")
            self.__nb_gpus = 0
        if self.__max_tasks_per_node is None:
            logging.info("Max tasks per node is not set. Setting it to 0 (no limit).")
            self.__max_tasks_per_node = 0

    def to_dict(self) -> dict:
        return {
            "cores_per_task": self.__cores_per_task,
            "exclusive": self.__exclusive,
            "nb_cores": self.__nb_cores,
            "nb_gpus": self.__nb_gpus,
            "nb_nodes": self.__nb_nodes,
            "nb_tasks": self.__nb_tasks,
            "max_tasks_per_node": self.__max_tasks_per_node,
            "ram_limit": self.__ram_limit,
            "ram_per_core": self.__ram_per_core,
        }

    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            cores_per_task=data.get("cores_per_task"),
            exclusive=data["exclusive"],
            nb_cores=data["nb_cores"],
            nb_gpus=data.get("nb_gpus"),
            nb_nodes=data["nb_nodes"],
            nb_tasks=data["nb_tasks"],
            max_tasks_per_node=data.get("max_tasks_per_node"),
            ram_limit=data["ram_limit"],
            ram_per_core=data["ram_per_core"],
        )


@dataclass
class ExecutionConfiguration:
    """Configuration for the execution of the job."""

    auto_hpc: bool = DEFAULT_AUTO_HPC
    cluster_name: str = DEFAULT_CLUSTER_NAME
    custom_submission_string: str = DEFAULT_CUSTOM_SUBMISSION_STRING
    job_name: str = DEFAULT_JOB_NAME
    monitor: bool = True
    ng_solve: bool = False
    product_full_path: Optional[str] = None
    shared_directory_linux: Optional[str] = None
    shared_directory_windows: Optional[str] = None
    use_ppe: bool = True
    wait_for_license: bool = True


class JobConfigurationData:
    def __init__(
        self,
        aedt_version: Optional[str] = None,
        auto_hpc: bool = DEFAULT_AUTO_HPC,
        cluster_name: str = DEFAULT_CLUSTER_NAME,
        cores_per_task: Optional[int] = None,
        custom_submission_string: str = DEFAULT_CUSTOM_SUBMISSION_STRING,
        exclusive: bool = False,
        job_name: str = DEFAULT_JOB_NAME,
        max_tasks_per_node: Optional[int] = None,
        monitor: bool = True,
        ng_solve: bool = False,
        nb_cores: int = DEFAULT_NB_CORES,
        nb_gpus: Optional[int] = None,
        nb_nodes: int = DEFAULT_NB_NODES,
        nb_tasks: int = DEFAULT_NB_TASKS,
        product_full_path: Optional[str] = None,
        ram_limit: int = DEFAULT_RAM_LIMIT,
        ram_per_core: float = DEFAULT_RAM_PER_CORE,
        shared_directory_linux: Optional[str] = None,
        shared_directory_windows: Optional[str] = None,
        use_ppe: bool = True,
        wait_for_license: bool = True,
    ):
        """Configuration data for HPC job submission.

        Keys
        ----
        aedt_version : Optional[str]
            Initialization-only variable to specify AEDT version, used internally to
            compute ``product_full_path`` if not provided explicitly.
        auto_hpc : bool
            Set to true if Auto HPC should be used. With Auto HPC Electronics Desktop
            will specify the number of cores and tasks based on the best estimate of
            available resources. Attributes ``nb_cores`` and ``nb_tasks`` will be
            ignored. Default is ``DEFAULT_AUTO_HPC``.
        cluster_name : str
            Name of the cluster to be used for the job submission.
            Default is ``DEFAULT_CLUSTER_NAME``.
        cores_per_task : int
            Number of cores assigned to each task. Default is ``4``.
        custom_submission_string : str
            A custom submission string passed to the scheduler. For example with LSF:
            - "-n 4 -R \"span[hosts=1] -J job_name -o output.log -e error.log\"" will be inserted
            between ``"bsub"`` and the AEDT executable (``"ansysedt.exe"``).
            Default is ``DEFAULT_CUSTOM_SUBMISSION_STRING`` (usually empty).
        exclusive : bool
            Specifies whether nodes will be reserved for exclusive
            use by the HPC job. Default is ``False``.
        job_name : str
            Name to be assigned to the HPC job when it is launched.
            Default is ``DEFAULT_JOB_NAME``.
        max_tasks_per_node : int
            The maximum number of tasks allowed to run on a single node. Default
            is ``0``, which causes this parameter to be ignored.
        monitor : bool
            Open the monitor GUI after job submission. Default is ``True``.
        ng_solve : bool
            Run the solve in non-graphical mode. This is a new feature in
            2025.1. Default setting is ``False``.
        nb_cores : int
            Total number of compute cores to be used by the job. Default is the constant
            ``DEFAULT_NUM_CORES``.
        nb_gpus : int
            Number of GPUs to be used for the simulation. Default is ``0``.
        nb_nodes : int
            Number of nodes for distribution of the HPC jobs. Default is the constant
            ``DEFAULT_NUM_NODES``.
        nb_tasks : int
            Number of tasks for the submission. Default is ``1``.
        product_full_path : str or Path
            The path for the AEDT executable used for job submission. The default value will be
            set by searching for the most recently installed version of Ansys Electronics Desktop
            via the environment variable `"ANSYSEM_ROOT???"` where "???" signifies the version number
            like "241" or "252".
        ram_limit : int
            The fraction of available RAM to be used by the simulation. Default is ``100``.
        ram_per_core : float
            Total RAM in GB to be used per core for the simulation job. Default is ``2.0``.
        shared_directory_linux : str or Path
            The path to the shared directory on Linux systems. This is used for
            transferring files between the local machine and the HPC cluster.
            Default is ``None``.
        shared_directory_windows : str or Path
            The path to the shared directory on Windows systems. This is used for
            transferring files between the local machine and the HPC cluster.
            Default is ``None``.
        use_ppe : bool
            Use the "Pro/Premium/Enterprise" licence type. This is the default
            license for HPC since version 2023.1. Default is ``True``.
        wait_for_license : bool
            Wait for an available license before submitting the job.
            Default is ``True``.
        """
        self.__resources_conf: ResourcesConfiguration = ResourcesConfiguration(
            cores_per_task=cores_per_task,
            exclusive=exclusive,
            nb_cores=nb_cores,
            nb_gpus=nb_gpus,
            nb_nodes=nb_nodes,
            nb_tasks=nb_tasks,
            max_tasks_per_node=max_tasks_per_node,
            ram_limit=ram_limit,
            ram_per_core=ram_per_core,
        )
        self.__execution_conf: ExecutionConfiguration = ExecutionConfiguration(
            auto_hpc=auto_hpc,
            cluster_name=cluster_name,
            custom_submission_string=custom_submission_string,
            job_name=job_name,
            monitor=monitor,
            ng_solve=ng_solve,
            product_full_path=product_full_path or path_string(get_aedt_exe(aedt_version)),
            shared_directory_linux=shared_directory_linux,
            shared_directory_windows=shared_directory_windows,
            use_ppe=use_ppe,
            wait_for_license=wait_for_license,
        )

        self.__hpc_method: HPCMethod = HPCMethod.USE_NODES_AND_CORES
        self.__update_hpc_method()

    # === Custom properties ===

    @property
    def use_custom_submission_string(self) -> bool:
        """Check if a custom submission string is provided."""
        return bool(self.custom_submission_string)

    @property
    def fix_job_name(self) -> bool:
        """Check if the job name is set to the default value."""
        return self.job_name == DEFAULT_JOB_NAME

    # === ResourcesConfiguration properties ===

    @property
    def cores_per_task(self) -> Optional[int]:
        return self.__resources_conf.cores_per_task

    @cores_per_task.setter
    def cores_per_task(self, value: Optional[int]):
        self.__resources_conf.cores_per_task = value

    @property
    def exclusive(self) -> bool:
        return self.__resources_conf.exclusive

    @exclusive.setter
    def exclusive(self, value: bool):
        self.__resources_conf.exclusive = value

    @property
    def nb_cores(self) -> int:
        return self.__resources_conf.nb_cores

    @nb_cores.setter
    def nb_cores(self, value: int):
        self.__resources_conf.nb_cores = value

    @property
    def nb_gpus(self) -> Optional[int]:
        return self.__resources_conf.nb_gpus

    @nb_gpus.setter
    def nb_gpus(self, value: Optional[int]):
        self.__resources_conf.nb_gpus = value

    @property
    def nb_nodes(self) -> int:
        return self.__resources_conf.nb_nodes

    @nb_nodes.setter
    def nb_nodes(self, value: int):
        self.__resources_conf.nb_nodes = value

    @property
    def nb_tasks(self) -> int:
        return self.__resources_conf.nb_tasks

    @nb_tasks.setter
    def nb_tasks(self, value: int):
        self.__resources_conf.nb_tasks = value
        self.__update_hpc_method()

    @property
    def max_tasks_per_node(self) -> Optional[int]:
        return self.__resources_conf.max_tasks_per_node

    @max_tasks_per_node.setter
    def max_tasks_per_node(self, value: Optional[int]):
        self.__resources_conf.max_tasks_per_node = value

    @property
    def ram_limit(self) -> int:
        return self.__resources_conf.ram_limit

    @ram_limit.setter
    def ram_limit(self, value: int):
        self.__resources_conf.ram_limit = value

    @property
    def ram_per_core(self) -> float:
        return self.__resources_conf.ram_per_core

    @ram_per_core.setter
    def ram_per_core(self, value: float):
        self.__resources_conf.ram_per_core = value

    # === ExecutionConfiguration properties ===

    @property
    def auto_hpc(self) -> bool:
        return self.__execution_conf.auto_hpc

    @auto_hpc.setter
    def auto_hpc(self, value: bool):
        self.__execution_conf.auto_hpc = value
        self.__update_hpc_method()

    @property
    def cluster_name(self) -> str:
        return self.__execution_conf.cluster_name

    @cluster_name.setter
    def cluster_name(self, value: str):
        self.__execution_conf.cluster_name = value

    @property
    def custom_submission_string(self) -> str:
        return self.__execution_conf.custom_submission_string

    @custom_submission_string.setter
    def custom_submission_string(self, value: str):
        self.__execution_conf.custom_submission_string = value

    @property
    def job_name(self) -> str:
        return self.__execution_conf.job_name

    @job_name.setter
    def job_name(self, value: str):
        self.__execution_conf.job_name = value

    @property
    def monitor(self) -> bool:
        return self.__execution_conf.monitor

    @monitor.setter
    def monitor(self, value: bool):
        self.__execution_conf.monitor = value

    @property
    def ng_solve(self) -> bool:
        return self.__execution_conf.ng_solve

    @ng_solve.setter
    def ng_solve(self, value: bool):
        self.__execution_conf.ng_solve = value

    @property
    def product_full_path(self) -> Optional[str]:
        return self.__execution_conf.product_full_path

    @product_full_path.setter
    def product_full_path(self, value: Optional[str]):
        self.__execution_conf.product_full_path = value

    @property
    def shared_directory_linux(self) -> Optional[str]:
        return self.__execution_conf.shared_directory_linux

    @shared_directory_linux.setter
    def shared_directory_linux(self, value: Optional[str]):
        self.__execution_conf.shared_directory_linux = value

    @property
    def shared_directory_windows(self) -> Optional[str]:
        return self.__execution_conf.shared_directory_windows

    @shared_directory_windows.setter
    def shared_directory_windows(self, value: Optional[str]):
        self.__execution_conf.shared_directory_windows = value

    @property
    def use_ppe(self) -> bool:
        return self.__execution_conf.use_ppe

    @use_ppe.setter
    def use_ppe(self, value: bool):
        self.__execution_conf.use_ppe = value

    @property
    def wait_for_license(self) -> bool:
        return self.__execution_conf.wait_for_license

    @wait_for_license.setter
    def wait_for_license(self, value: bool):
        self.__execution_conf.wait_for_license = value

    # === Public methods ===

    @classmethod
    def from_dict(cls, data: dict) -> JobConfigurationData:
        """Create a JobConfigurationData instance from a dictionary."""
        return cls(
            aedt_version=data.get("aedt_version"),
            auto_hpc=data.get("auto_hpc", False),
            cluster_name=data.get("cluster_name", DEFAULT_CLUSTER_NAME),
            cores_per_task=data.get("cores_per_task"),
            custom_submission_string=data.get("custom_submission_string", DEFAULT_CUSTOM_SUBMISSION_STRING),
            exclusive=data.get("exclusive", False),
            job_name=data.get("job_name", DEFAULT_JOB_NAME),
            max_tasks_per_node=data.get("max_tasks_per_node"),
            monitor=data.get("monitor", True),
            ng_solve=data.get("ng_solve", False),
            nb_cores=data.get("nb_cores", DEFAULT_NB_CORES),
            nb_gpus=data.get("nb_gpus"),
            nb_nodes=data.get("nb_nodes", DEFAULT_NB_NODES),
            nb_tasks=data.get("nb_tasks", DEFAULT_NB_TASKS),
            product_full_path=data.get("product_full_path"),
            ram_limit=data.get("ram_limit", DEFAULT_RAM_LIMIT),
            ram_per_core=data.get("ram_per_core", DEFAULT_RAM_PER_CORE),
            shared_directory_linux=data.get("shared_directory_linux"),
            shared_directory_windows=data.get("shared_directory_windows"),
            use_ppe=data.get("use_ppe", True),
            wait_for_license=data.get("wait_for_license", True),
        )

    def to_dict(self) -> dict:
        """Convert the JobConfigurationData to a dictionary."""
        return {
            "auto_hpc": self.auto_hpc,
            "cluster_name": self.cluster_name,
            "cores_per_task": self.cores_per_task,
            "custom_submission_string": self.custom_submission_string,
            "exclusive": self.exclusive,
            "job_name": self.job_name,
            "max_tasks_per_node": self.max_tasks_per_node,
            "monitor": self.monitor,
            "ng_solve": self.ng_solve,
            "nb_cores": self.nb_cores,
            "nb_gpus": self.nb_gpus,
            "nb_nodes": self.nb_nodes,
            "nb_tasks": self.nb_tasks,
            "product_full_path": self.product_full_path,
            "ram_limit": self.ram_limit,
            "ram_per_core": self.ram_per_core,
            "shared_directory_linux": self.shared_directory_linux,
            "shared_directory_windows": self.shared_directory_windows,
            "use_ppe": self.use_ppe,
            "wait_for_license": self.wait_for_license,
        }

    def to_json(self, path: Union[str, Path]):
        with open(path, "w") as f:
            json.dump(self.to_dict(), f, indent=4)

    @classmethod
    def from_json(cls, path: Union[str, Path]) -> JobConfigurationData:
        with open(path, "r") as f:
            data = json.load(f)
        return cls.from_dict(data)

    def to_toml(self, path: Union[str, Path]):
        with open(path, "w") as f:
            tomli_w.dump(self.to_dict(), f)

    @classmethod
    def from_toml(cls, path: Union[str, Path]) -> JobConfigurationData:
        with open(path, "r") as f:
            data = tomli.load(f)
        return cls.from_dict(data)

    def save_areg(self, file_path: str = "Job_Settings.areg") -> Path:
        """Save the job settings to an AREG file."""
        # Check if inconsistencies in resources configuration exist
        self.__resources_conf.check_consistency()
        self.__resources_conf.align_dependent_attributes()

        path = Path(file_path)
        if not path.suffix:
            path = path.with_suffix(".areg")

        with path.open("w", encoding="utf-8") as f:
            f.write(render_template(self, JOB_TEMPLATE_PATH))
        return path

    # === Private methods ===

    def __update_hpc_method(self):
        """Update the HPC method based on the current settings."""
        if self.auto_hpc:
            logging.debug("Using Auto HPC method for job submission.")
            self.__hpc_method = HPCMethod.USE_AUTO_HPC
        elif self.nb_tasks > 1:
            logging.debug("Using tasks and cores for HPC job submission.")
            self.__hpc_method = HPCMethod.USE_TASKS_AND_CORES
        else:
            logging.debug("Using nodes and cores for HPC job submission.")
            self.__hpc_method = HPCMethod.USE_NODES_AND_CORES


if __name__ == "__main__":
    data = JobConfigurationData(
        nb_cores=4,
        nb_tasks=8,
        custom_submission_string="this is the custom submission string",
        job_name="happy job",
    )
    for key, value in data.to_dict().items():
        print(f"{key} = {value}")
    data.save_areg("test_job_settings.areg")
