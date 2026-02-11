# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 - 2026 ANSYS, Inc. and/or its affiliates.
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
import json
import logging
import re
from unittest.mock import patch

import pytest

from ansys.aedt.core.generic.scheduler import DEFAULT_CLUSTER_NAME
from ansys.aedt.core.generic.scheduler import DEFAULT_CUSTOM_SUBMISSION_STRING
from ansys.aedt.core.generic.scheduler import DEFAULT_JOB_NAME
from ansys.aedt.core.generic.scheduler import DEFAULT_MAX_TASKS_PER_NODE
from ansys.aedt.core.generic.scheduler import DEFAULT_NUM_CORES
from ansys.aedt.core.generic.scheduler import DEFAULT_NUM_GPUS
from ansys.aedt.core.generic.scheduler import DEFAULT_NUM_NODES
from ansys.aedt.core.generic.scheduler import DEFAULT_NUM_TASKS
from ansys.aedt.core.generic.scheduler import DEFAULT_RAM_LIMIT
from ansys.aedt.core.generic.scheduler import DEFAULT_RAM_PER_CORE
from ansys.aedt.core.generic.scheduler import HPCMethod
from ansys.aedt.core.generic.scheduler import JobConfigurationData
from ansys.aedt.core.generic.scheduler import _ResourcesConfiguration

MOCK_AEDT_EXE = "aedt_path.exe"


@patch("ansys.aedt.core.generic.scheduler.get_aedt_exe", return_value=MOCK_AEDT_EXE)
def test_job_configuration_data_default_values(mock_get_exe) -> None:
    """Test the default values of JobConfigurationData."""
    data = JobConfigurationData()

    assert not data.auto_hpc
    assert DEFAULT_CLUSTER_NAME == data.cluster_name
    assert DEFAULT_NUM_CORES * DEFAULT_NUM_TASKS == data.cores_per_task
    assert DEFAULT_CUSTOM_SUBMISSION_STRING == data.custom_submission_string
    assert not data.exclusive
    assert data.job_name == DEFAULT_JOB_NAME
    assert data.max_tasks_per_node is None
    assert data.monitor
    assert not data.ng_solve
    assert DEFAULT_NUM_CORES == data.num_cores
    assert data.num_gpus is None
    assert DEFAULT_NUM_NODES == data.num_nodes
    assert DEFAULT_NUM_TASKS == data.num_tasks
    assert MOCK_AEDT_EXE == data.product_full_path
    assert DEFAULT_RAM_LIMIT == data.ram_limit
    assert DEFAULT_RAM_PER_CORE == data.ram_per_core
    assert data.shared_directory_linux is None
    assert data.shared_directory_windows is None
    assert data.use_ppe
    assert data.wait_for_license


@patch("ansys.aedt.core.generic.scheduler.get_aedt_exe", return_value=MOCK_AEDT_EXE)
def test_job_configuration_data_custom_properties(mock_get_exe) -> None:
    """Test custom properties of JobConfigurationData."""
    data = JobConfigurationData()

    assert not data.use_custom_submission_string
    assert data.fix_job_name

    data.custom_submission_string = "Dummy custom submission string"
    data.job_name = "Dummy job name"

    assert data.use_custom_submission_string
    assert not data.fix_job_name


@patch("ansys.aedt.core.generic.scheduler.get_aedt_exe", return_value=MOCK_AEDT_EXE)
def test_job_configuration_data_execution_configuration_properties(mock_get_exe) -> None:
    """Test execution configuration properties of JobConfigurationData."""
    data = JobConfigurationData()

    data.auto_hpc = False
    data.cluster_name = "DummyCustomCluster"
    data.custom_submission_string = "Dummy custom submission string"
    data.job_name = "Dummy job name"
    data.monitor = True
    data.ng_solve = False
    data.product_full_path = "Dummy product path"
    data.shared_directory_linux = "/dummy/linux/path"
    data.shared_directory_windows = "C:\\dummy\\windows\\path"
    data.use_ppe = True
    data.wait_for_license = True

    assert not data.auto_hpc
    assert data.cluster_name == "DummyCustomCluster"
    assert data.custom_submission_string == "Dummy custom submission string"
    assert data.job_name == "Dummy job name"
    assert data.monitor
    assert not data.ng_solve
    assert data.product_full_path == "Dummy product path"
    assert data.shared_directory_linux == "/dummy/linux/path"
    assert data.shared_directory_windows == "C:\\dummy\\windows\\path"
    assert data.use_ppe
    assert data.wait_for_license


@patch("ansys.aedt.core.generic.scheduler.get_aedt_exe", return_value=MOCK_AEDT_EXE)
def test_job_configuration_data_check_failure(mock_get_exe) -> None:
    """Test that check method raises ValueError for invalid configurations."""
    data = JobConfigurationData()

    int_strict_attributes = ["num_cores", "num_nodes", "num_tasks", "ram_limit"]
    int_non_strict_attributes = ["num_gpus", "max_tasks_per_node"]
    float_attributes = ["ram_per_core"]
    wrong_int_value = -1
    wrong_float_value = -1.0

    for attr in int_strict_attributes:
        with pytest.raises(ValueError, match=re.escape(f"{attr} must be an integer, got float.")):
            setattr(data, attr, -1.0)
        with pytest.raises(
            ValueError, match=re.escape(f"{attr} must be a positive integer (> 0), got {wrong_int_value}.")
        ):
            setattr(data, attr, -1)

    for attr in int_non_strict_attributes:
        with pytest.raises(
            ValueError, match=re.escape(f"{attr} must be a non-negative integer (>= 0), got {wrong_int_value}.")
        ):
            setattr(data, attr, -1)

    for attr in float_attributes:
        with pytest.raises(ValueError, match=re.escape(f"{attr} must be a float, got int.")):
            setattr(data, attr, -1)
        with pytest.raises(
            ValueError, match=re.escape(f"{attr} must be a positive float (> 0), got {wrong_float_value}.")
        ):
            setattr(data, attr, -1.0)


@patch("ansys.aedt.core.generic.scheduler.get_aedt_exe", return_value=MOCK_AEDT_EXE)
def test_job_configuration_data_check_none_assign_success(mock_get_exe) -> None:
    """Test that optional attributes can be assigned None without raising errors."""
    data = JobConfigurationData()

    optional_attributes = ["num_gpus", "max_tasks_per_node"]
    for attr in optional_attributes:
        setattr(data, attr, None)
        assert getattr(data, attr) is None, f"Expected {attr} to be None after assignment."


@patch("ansys.aedt.core.generic.scheduler.get_aedt_exe", return_value=MOCK_AEDT_EXE)
def test_job_configuration_data_check_consistency_failure(mock_get_exe) -> None:
    """Test that check_consistency raises ValueError for inconsistent configurations."""
    data = JobConfigurationData(num_tasks=4, max_tasks_per_node=3)
    with pytest.raises(ValueError, match=re.escape("Tasks per node (4) exceeds max tasks per node (3).")):
        data._JobConfigurationData__resources_conf.check_consistency()

    data = JobConfigurationData(num_tasks=4, num_cores=2)
    with pytest.raises(
        ValueError, match=re.escape("Number of cores (2) must be greater than or equal to the number of tasks (4).")
    ):
        data._JobConfigurationData__resources_conf.check_consistency()


@patch("ansys.aedt.core.generic.scheduler.get_aedt_exe", return_value=MOCK_AEDT_EXE)
def test_job_configuration_data_align_dependent_attributes(mock_get_exe, caplog) -> None:
    """Test that align_dependent_attributes sets default values and logs warnings."""
    caplog.set_level(logging.INFO)

    data = JobConfigurationData(num_tasks=4, num_cores=2)
    data._JobConfigurationData__resources_conf.align_dependent_attributes()

    assert f"Number of GPUs is not set. Setting it to {DEFAULT_NUM_GPUS}." in caplog.text
    assert f"Max tasks per node is not set. Setting it to {DEFAULT_MAX_TASKS_PER_NODE} (no limit)." in caplog.text


@patch("ansys.aedt.core.generic.scheduler.get_aedt_exe", return_value=MOCK_AEDT_EXE)
def test_resources_configuration_dict_interaction(mock_get_exe) -> None:
    """Test that _ResourcesConfiguration interaction from/to a dictionary."""
    data_dict = {
        "exclusive": False,
        "num_cores": 4,
        "num_gpus": None,
        "num_nodes": 1,
        "num_tasks": 4,
        "max_tasks_per_node": None,
        "ram_limit": 100,
        "ram_per_core": 25.0,
    }

    data = _ResourcesConfiguration.from_dict(data_dict)
    assert isinstance(data, _ResourcesConfiguration)

    res = data.to_dict()
    assert data_dict == res, "The dictionary representation does not match the original data."


@patch("ansys.aedt.core.generic.scheduler.get_aedt_exe", return_value=MOCK_AEDT_EXE)
def test_job_configuration_data_dict_interaction(mock_get_exe) -> None:
    """Test that JobConfigurationData interaction from/to a dictionary."""
    data_dict = {
        "auto_hpc": False,
        "cluster_name": "ClusterName",
        "custom_submission_string": "",
        "exclusive": False,
        "job_name": "AEDT Simulation",
        "max_tasks_per_node": None,
        "monitor": True,
        "ng_solve": False,
        "num_cores": 10,
        "num_gpus": None,
        "num_nodes": 1,
        "num_tasks": 1,
        "product_full_path": "aedt_path.exe",
        "ram_limit": 100,
        "ram_per_core": 2.0,
        "shared_directory_linux": None,
        "shared_directory_windows": None,
        "use_ppe": True,
        "wait_for_license": True,
    }
    data = JobConfigurationData.from_dict(data_dict)
    assert isinstance(data, JobConfigurationData)

    res = data.to_dict()
    assert data_dict == res, "The dictionary representation does not match the original data."


@patch("ansys.aedt.core.generic.scheduler.get_aedt_exe", return_value=MOCK_AEDT_EXE)
def test_job_configuration_data_to_json_and_from_json(mock_get_exe, tmp_path) -> None:
    """Test that JobConfigurationData can be serialized to JSON and deserialized back."""
    data = JobConfigurationData()

    tmp_json_file = tmp_path / "job_config.json"
    data.to_json(tmp_json_file)

    assert tmp_json_file.exists()

    loaded = JobConfigurationData.from_json(tmp_json_file)
    assert isinstance(loaded, JobConfigurationData)
    assert loaded.to_dict() == data.to_dict()

    with open(tmp_json_file, "r") as f:
        json_data = json.load(f)
    assert json_data == data.to_dict()


@patch("ansys.aedt.core.generic.scheduler.get_aedt_exe", return_value="aedt_path.exe")
def test_switch_between_hpc_method_values(mock_get_exe) -> None:
    """Test that switching between HPC methods works correctly on setting attributes."""
    data = JobConfigurationData()
    assert HPCMethod.USE_NODES_AND_CORES == data._JobConfigurationData__hpc_method

    data.num_tasks = 5
    assert HPCMethod.USE_TASKS_AND_CORES == data._JobConfigurationData__hpc_method

    data.num_tasks = 1
    assert HPCMethod.USE_NODES_AND_CORES == data._JobConfigurationData__hpc_method

    data.auto_hpc = True
    assert HPCMethod.USE_AUTO_HPC == data._JobConfigurationData__hpc_method


@patch("ansys.aedt.core.generic.scheduler.get_aedt_exe", return_value="aedt_path.exe")
def test_save_areg_generates_file_with_expected_content(mock_get_exe, tmp_path) -> None:
    """Test that save_areg generates a file with expected content."""
    EXPECTED_CONTENT = r"""$begin 'AddEntries'
	'Desktop/Settings/ProjectOptions/GSDefaults'='$begin \'\'\
\	$begin \'ClusterName\'\
\	\	Monitor=true\
\	\	WaitForLicense=true\
\	\	UsePPELicensing=true\
\	\	EnableWebClient=false\
\	\	SolveUsingNgAEDT=false\
\	\	BatchExtract=false\
\	\	BatchOptions()\
\	\	ProductPath=\'aedt_path.exe\'\
\	\	BatchExtractPath=\'\'\
\	\	UseMultiStep=false\
\	\	UseLSDSO=false\
\	\	$begin \'\'\
\	\	\	Method=3\
\	\	\	$begin \'TasksAndCoresBlock\'\
\	\	\	\	IsExclusive=false\
\	\	\	\	RAMLimit=90\
\	\	\	\	NumTasks=1\
\	\	\	\	NumCoresPerDistributedTask=4\
\	\	\	\	LimitTasksPerNodeEnabled=false\
\	\	\	\	NumMaxTasksPerNode=0\
\	\	\	\	NumGpus=0\
\	\	\	$end \'TasksAndCoresBlock\'\
\	\	\	$begin \'RAMConstrainedBlock\'\
\	\	\	\	IsExclusive=false\
\	\	\	\	RAMLimit=90\
\	\	\	\	NumCores=4\
\	\	\	\	RAMPerCoreCheckbox=false\
\	\	\	\	RAMPerCoreInGB=\'2.0\'\
\	\	\	$end \'RAMConstrainedBlock\'\
\	\	\	$begin \'NodesAndCoresBlock\'\
\	\	\	\	IsExclusive=false\
\	\	\	\	RAMLimit=90\
\	\	\	\	NumNodes=1\
\	\	\	\	NumCores=4\
\	\	\	\	NumGpus=0\
\	\	\	$end \'NodesAndCoresBlock\'\
\	\	\	$begin \'NodeListBlock\'\
\	\	\	\	$begin \'MachineListVec\'\
\	\	\	\	$end \'MachineListVec\'\
\	\	\	$end \'NodeListBlock\'\
\	\	$end \'\'\
\	\	$begin \'JobAttributes\'\
\	\	\	JobName=\'AEDT Simulation\'\
\	\	\	JobPriority=\'\'\
\	\	\	SubmissionOptions=\'\'\
\	\	\	SubmissionOptionsReplace=false\
\	\	\	FixJobName=true\
\	\	$end \'JobAttributes\'\
\	\	$begin \'UniformComputeResources\'\
\	\	$end \'UniformComputeResources\'\
\	\	$begin \'DSOJobDistributionInfo\'\
\	\	\	AllowedDistributionTypes[0:]\
\	\	\	Enable2LevelDistribution=false\
\	\	\	NumL1Engines=2\
\	\	\	UseDefaultsForDistributionTypes=true\
\	\	\	Context()\
\	\	$end \'DSOJobDistributionInfo\'\
\	\	EnvVarNames[1: \'ANSOFT_PASS_DEBUG_ENV_TO_REMOTE_ENGINES\']\
\	\	EnvVarValues[1: \'1\']\
\	\	$begin \'ArchiveOptions\'\
\	\	\	OverwriteFiles=false\
\	\	$end \'ArchiveOptions\'\
\	\	$begin \'SharedDirectories\'\
\	\	\	WindowsPaths[0:]\
\	\	\	LinuxPaths[0:]\
\	\	$end \'SharedDirectories\'\
\	\	$begin \'MultiStepJobSettings\'\
\	\	\	SelectedOption=\'\'\
\	\	$end \'MultiStepJobSettings\'\
\	\	NumVariationsToDistributeInAuto=1\
\	$end \'ClusterName\'\
$end \'\'\
'

$end 'AddEntries'
"""

    data = JobConfigurationData()

    result_path = data.save_areg(tmp_path / "output")

    assert result_path.exists()
    assert ".areg" == result_path.suffix

    content = result_path.read_text(encoding="utf-8")
    assert EXPECTED_CONTENT == content
