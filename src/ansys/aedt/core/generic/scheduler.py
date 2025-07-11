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

from enum import IntEnum
import logging
import os
from pathlib import Path
import platform
import re
from typing import Optional
import warnings

DEFAULT_JOB_NAME = "AEDT Simulation"
"""Default job name for the job submission."""
DEFAULT_CUSTOM_SUBMISSION_STRING = ""
"""Default custom submission string for the job submission."""
DEFAULT_NUM_CORES = 2
"""Default number of cores for the job submission."""
DEFAULT_NUM_NODES = 1
"""Default number of nodes for the job submission."""
DEFAULT_AUTO_HPC = False
"""Default setting for Auto HPC."""
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
        if isinstance(value, bool):  # Boolean need to be lower case.
            return str(value).lower()
        elif value is None:  # Return an empty string if None
            return ""
        elif isinstance(value, HPCMethod):
            return str(value.value)
        return str(value)

    return pattern.sub(replacer, load_template(template_path))


class JobConfigurationData:
    def __init__(
        self,
        aedt_version: Optional[str] = None,
        auto_hpc: bool = False,
        cores_per_task: int = 4,
        custom_submission_string: str = DEFAULT_CUSTOM_SUBMISSION_STRING,
        exclusive: bool = False,
        job_name: str = DEFAULT_JOB_NAME,
        max_tasks_per_node: int = 0,
        monitor: bool = True,
        ng_solve: bool = False,
        num_cores: int = DEFAULT_NUM_CORES,
        num_gpu: int = 0,
        num_nodes: int = DEFAULT_NUM_NODES,
        num_tasks: int = 1,
        product_full_path: Optional[str] = None,
        ram_limit: int = 100,
        ram_per_core: float = 2.0,
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
            available resources. Attributes ``num_cores`` and ``num_tasks`` will be
            ignored. Default is ``DEFAULT_AUTO_HPC``.
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
        num_cores : int
            Total number of compute cores to be used by the job. Default is the constant
            ``DEFAULT_NUM_CORES``.
        num_gpu : int
            Number of GPUs to be used for the simulation. Default is ``0``.
        num_nodes : int
            Number of nodes for distribution of the HPC jobs. Default is the constant
            ``DEFAULT_NUM_NODES``.
        num_tasks : int
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
        use_ppe : bool
            Use the "Pro/Premium/Enterprise" licence type. This is the default
            license for HPC since version 2023.1. Default is ``True``.
        wait_for_license : bool
            Wait for an available license before submitting the job.
            Default is ``True``.
        """

        # Initialization for dependent attributes must avoid using the native __settattr__()
        object.__setattr__(self, "num_tasks", num_tasks)
        object.__setattr__(self, "num_cores", num_cores)

        self.num_nodes = num_nodes
        self.auto_hpc = auto_hpc
        self.cores_per_task = cores_per_task
        self.custom_submission_string = custom_submission_string
        self.exclusive = exclusive
        self.job_name = job_name
        self.max_tasks_per_node = max_tasks_per_node
        self.monitor = monitor
        self.ng_solve = ng_solve
        self.num_gpu = num_gpu
        self.product_full_path = product_full_path or path_string(get_aedt_exe(aedt_version))
        self.ram_limit = ram_limit
        self.ram_per_core = ram_per_core
        self.use_ppe = use_ppe
        self.wait_for_license = wait_for_license

        self.__hpc_method = HPCMethod.USE_NODES_AND_CORES
        self.__update_hpc_method()

    @property
    def use_custom_submission_string(self) -> bool:
        """Check if a custom submission string is provided."""
        return bool(self.custom_submission_string)

    @property
    def fix_job_name(self) -> bool:
        """Check if the job name is set to the default value."""
        return self.job_name == DEFAULT_JOB_NAME

    def __repr__(self):
        """Return a string representation of the job configuration data."""
        visible = self.to_dict()
        return f"JobConfigurationData({visible})"

    def __setattr__(self, name, value):
        """Set an attribute of the job configuration data."""
        INT_FIELDS = {
            "num_tasks",
            "cores_per_task",
            "max_tasks_per_node",
            "ram_limit",
            "num_gpu",
            "num_nodes",
            "num_cores",
        }
        if name in INT_FIELDS and isinstance(value, int):
            if value < 0:
                raise ValueError(f"{name} must be greater or equal to zero.")

        # If num_tasks is being set, update cores_per_task based on the current
        # value of num_cores.
        if name == "num_tasks":
            num_cores = self.cores_per_task * value
            if self.num_cores != num_cores:
                if self.num_cores > 0:
                    self.cores_per_task = self.num_cores // value
                    if self.cores_per_task == 0:
                        self.cores_per_task = 1
                self.num_cores = self.cores_per_task * value

        # If num_cores is being set, make sure it is consistent with other settings.
        elif name == "num_cores":
            if self.num_tasks > 1:
                if value < self.num_tasks:
                    warning_message = "num_cores unchanged. The number of cores must be an integer\n"
                    warning_message += f"multiple of the number of tasks.{self.num_tasks}."
                    logging.warning(warning_message)
                    return
                elif value > self.num_tasks:
                    self.cores_per_task = value // self.num_tasks
                    if value % self.num_tasks > 0:
                        warning_message = "The number of cores must be an integer multiple of the\n"
                        warning_message += "number of tasks. num_tasks is set to "
                        warning_message += f"{self.cores_per_task * self.num_tasks}."
                        logging.warning(warning_message)
                        self.num_cores = self.cores_per_task * self.num_tasks
                        return
        object.__setattr__(self, name, value)
        if name in ("num_tasks", "auto_hpc", "num_cores"):
            self.__update_hpc_method()

    def save_areg(self, file_path: str = "Job_Settings.areg") -> Path:
        """Save the job settings to an AREG file."""
        path = Path(file_path)
        if not path.suffix:
            path = path.with_suffix(".areg")

        with path.open("w", encoding="utf-8") as f:
            f.write(render_template(self, JOB_TEMPLATE_PATH))
        return path

    def to_dict(self) -> dict:
        """Export public attributes as a dictionary."""
        return {key: value for key, value in self.__dict__.items() if not key.startswith("_")}

    def __update_hpc_method(self):
        """Update the HPC method based on the current settings."""
        try:
            if self.auto_hpc:
                self.__hpc_method = HPCMethod.USE_AUTO_HPC
                return
            elif self.num_tasks > 1:
                self.__hpc_method = HPCMethod.USE_TASKS_AND_CORES
                if self.cores_per_task == 0 and self.num_cores > 0:
                    new_cores_per_task = max(self.num_cores // self.num_tasks, 1)
                    warnings.warn(f"Settings cores per task to {new_cores_per_task}.")
                    self.cores_per_task = new_cores_per_task
            else:
                self.__hpc_method = HPCMethod.USE_NODES_AND_CORES
        except AttributeError:
            # If the attribute is not set, we cannot update it.
            # This can happen if the object is not fully initialized.
            pass


if __name__ == "__main__":
    data = JobConfigurationData(
        num_cores=4,
        num_tasks=8,
        custom_submission_string="this is the custom submission string",
        job_name="happy job",
    )
    for key, value in data.to_dict().items():
        print(f"{key} = {value}")
    data.save_areg("test_job_settings.areg")
