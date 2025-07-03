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


import os
from pathlib import Path
import platform
import re


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
    if version:
        version_folder = "v" + version.replace(".", "")
        version_suffix = version.replace(".", "")
    else:
        version_folder = None
        version_suffix = None
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

    # Build a map of version suffix → path
    for key in os.environ:
        match = pattern.fullmatch(key)
        if match:
            suffix = match.group(1)  # e.g., "251"
            version_map[suffix] = os.environ[key]

    if version is None:
        # Return the highest version (sorted numerically)
        latest_suffix = max(version_map.keys(), key=lambda s: int(s))
        return Path(version_map[latest_suffix]) / exe_name

    # Convert version like "25.1" → "251"
    desired_suffix = version.replace(".", "")
    return Path(version_map.get(desired_suffix)) / exe_name


class JobSettings(dict):
    """
    A dictionary-like class to help manage HPC job submission settings.

    This class provides an interface to create and modify
    an ``*.areg`` configuration file to specify HPC job submission settings. The
    solve setup `*.areg`` file can be exported or imported from the "Submit Job"
    user-interface via the Export and Import buttons.

    A class instance is instantiated with no input. The following key value pairs
    are defined upon instantiation and can be modified.

    Parameters
    ----------
    version : str
        Version of Ansys Electronics Desktop. For example `"23.2"` or `"24.1"`. If no
        value is passed, the version will be retrieved from the
        local `$PATH`. If the installation folder is not defined in the `$PATH`,
        Ansys-specific
        environment variables `ANSYSEM_ROOT241`, `ANSYSEM_ROOT251`, will be queried. The
        newest installed version will be used.

    Attributes
    ----------
    data : str
        The text version of the job settings. This text will be written to the ``*.areg`` file
        with the ``write()`` method.

    Keys
    ----
    monitor : bool
        Open the monitor GUI after job submission. Default is ``True``
    wait_for_license: bool
        Wait for an available license before submitting the job.
        Default is ``True``.
    use_ppe: bool
        Use the "Pro/Premium/Enterprise" licence type. This is the default
        license for HPC since version 2023.1. Default is ``True``.
    ng_solve: bool
        Run the solve in non-graphical mode. This is a new feature in
        2025.1. Default setting is ``True``
    product_full_path :  str or Path
        The path for the AEDT executable used for job submission. The default value will be
        set by searching for the most recently installed version of Ansys Electronics Desktop
        via the environment variable `"ANSYSEM_ROOT???"` Where "???" signifies the version number
        like "241" or "252".
        This can be overridden manually. For example,
        ``job_settings["product_full_path"] = "/opt/software/ansys_inc/v252/AnsysEM/ansysedt.exe"``
    num_tasks :  int
        Number of tasks for the submission. The default value is ``1`.
    cores_per_task :  int
        Number of cores assigned to each task. The default value is ``4``.
    max_tasks_per_node : int
        The maximum number of tasks allowed to run on a single node. The default
        value is ``0`` which causes this parameter to be ignored.
    ram_limit :  int
        The fraction of available RAM to be used by the simulation. The default value is ``90``.
    num_gpu :  int
        Number of GPUs to be used for the simulation. The default value is ``0``.
    num_nodes :  int
        Number of nodes for distribution of the HPC jobs. The default value is ``1``
    num_cores :  int
        Total number of compute cores to be used by the job. The default value is ``2``
    job_name : str
        Name to be assigned to the HPC job when it is launched.
        The default value is ``"AEDT Simulation"``.
    ram_per_core : float
        Total RAM in GB to be used per core for the simulation job. The default is ``2.0``.
    exclusive : bool
        A flag that specifies whether nodes will be reserved for exclusive
        use by the HPC job. The default is ``False``.
    custom_submission_string : str
        A custom submission string that is passed to the scheduler. For example with LSF:
        - "-n 4 -R "span[hosts=1] -J job_name -o output.log -e error.log" will be inserted
          between ``"bsub"`` and the AEDT executable (``"ansysedt.exe"``). Default is ""

    Methods
    -------
    save(filename='Job_Settings.areg')
        Write the job submission configuration to a file.

    Examples
    --------
    >>> job_settings = JobSettings()
    >>> job_settings["num_cores"] = 64
    >>> job_settings["num_tasks"] = 4
    >>> job_settings_fn = "/home/my_home/hpc/JobSettings.areg"
    >>> job_settings.save(job_settings_fn)
    >>> hfss.submit_job(setting_file=job_settings_fn)

    or

    >>> job_settings = JobSettings()
    >>> job_settings.update({"num_cores": 64, "num_tasks": 4, "job_name": "HFSS Test"})
    >>> job_settings["num_tasks"] = 4
    >>> job_settings_fn = "/home/my_home/hpc/JobSettings.areg"
    >>> hfss.submit_job(setting_file=job_settings.save(job_settings_fn))
    """

    _JOB_TEMPLATE = Path(__file__).resolve().parent.parent / "misc" / "Job_Settings_Template.txt"

    _job_defaults = {
        "monitor": True,
        "wait_for_license": True,
        "use_ppe": True,
        "ng_solve": False,
        "product_full_path": None,
        "num_tasks": 1,
        "cores_per_task": 4,
        "max_tasks_per_node": 0,
        "ram_limit": 90,
        "num_gpu": 0,
        "num_nodes": 1,
        "num_cores": 2,
        "job_name": "AEDT Simulation",
        "ram_per_core": 2.0,  # RAM per core in GB
        "exclusive": False,  # Reserve the entire node.
        "custom_submission_string": "",  # Allow custom submission string.
    }

    _job_defaults_read_only = {
        "use_custom_submission_string": False,
        "fix_job_name": False,
    }

    def __init__(self, version=None):
        super().__init__()
        self._template_path = self._JOB_TEMPLATE
        self._template_text = self._load_template()
        self.update(self._job_defaults)
        self.update(self._job_defaults_read_only)
        self["product_full_path"] = path_string(get_aedt_exe(version))
        self.data = self._render_template()

    def _load_template(self) -> str:
        with self._template_path.open("r", encoding="utf-8") as f:
            return f.read()

    def _render_template(self) -> str:
        pattern = re.compile(r"\{\{(\w+)\}\}")

        def replacer(match):
            key = match.group(1)
            value = self.get(key, match.group(0))
            if isinstance(value, bool):  # Boolean need to be lower case.
                return str(value).lower()
            elif value is None:  # Return an empty string if None
                return ""
            return str(value)  # Keep {{key}} if not found

        return pattern.sub(replacer, self._template_text)

    def __setitem__(self, key, value):
        if key in self._job_defaults_read_only.keys():
            settings.logger.warning(f"Key {key} is read-only and will not be changed.")
            return
        elif key == "num_tasks":
            if self["cores_per_task"] == 0 and self["num_cores"] > 0:
                self["cores_per_task"] = value // self["num_cores"]
                if self["cores_per_task"] == 0:
                    self["cores_per_task"] = 1
            else:
                self["cores_per_task"] = 1
            self.update({"num_cores": self["cores_per_task"] * value})
        super().__setitem__(key, value)
        self.data = self._render_template()

    def __getitem__(self, key):
        if key == "use_custom_submission_string":  # True if the string has been changed.
            return bool(self.get("custom_submission_string", ""))
        elif key == "fix_job_name":
            return bool(self._job_defaults["job_name"] == self["job_name"])
        return super().__getitem__(key)

    def save(self, filename: str = "Job_Settings.areg"):
        path = Path(filename)
        if not path.suffix:
            path = path.with_suffix(".areg")
        with path.open("w", encoding="utf-8") as f:
            f.write(self.data)
        return filename
