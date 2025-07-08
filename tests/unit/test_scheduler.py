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

from unittest.mock import patch
import warnings

import pytest

from ansys.aedt.core.generic.scheduler import DEFAULT_NUM_CORES
from ansys.aedt.core.generic.scheduler import DEFAULT_NUM_NODES
from ansys.aedt.core.generic.scheduler import HPCMethod
from ansys.aedt.core.generic.scheduler import JobConfigurationData


@patch("ansys.aedt.core.generic.scheduler.get_aedt_exe", return_value="aedt_path.exe")
def test_default_values(mock_get_exe):
    """Test the default values of JobConfigurationData."""
    data = JobConfigurationData()
    assert 4 == data.cores_per_task
    assert DEFAULT_NUM_CORES == data.num_cores
    assert 0 == data.num_gpu
    assert 1 == data.num_tasks
    assert DEFAULT_NUM_NODES == data.num_nodes
    assert not data.auto_hpc
    assert HPCMethod.USE_NODES_AND_CORES == data._JobConfigurationData__hpc_method


@patch("ansys.aedt.core.generic.scheduler.get_aedt_exe", return_value="aedt_path.exe")
def test_use_auto_hpc(mock_get_exe):
    """Test that auto HPC sets the method to USE_AUTO_HPC."""
    data = JobConfigurationData(auto_hpc=True)
    assert HPCMethod.USE_AUTO_HPC == data._JobConfigurationData__hpc_method


@patch("ansys.aedt.core.generic.scheduler.get_aedt_exe", return_value="aedt_path.exe")
def test_use_tasks_and_cores_sets_method(mock_get_exe):
    """Test that setting num_tasks and cores_per_task sets the method to USE_TASKS_AND_CORES."""
    data = JobConfigurationData(num_tasks=4)
    assert HPCMethod.USE_TASKS_AND_CORES == data._JobConfigurationData__hpc_method


@patch("ansys.aedt.core.generic.scheduler.get_aedt_exe", return_value="aedt_path.exe")
def test_cores_per_task_auto_adjustment(mock_get_exe):
    """Test that cores_per_task is automatically adjusted when set to 0."""
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        data = JobConfigurationData(num_tasks=4, num_cores=8, cores_per_task=0)
        assert HPCMethod.USE_TASKS_AND_CORES == data._JobConfigurationData__hpc_method
        assert 2 == data.cores_per_task
        assert "Settings cores per task to 2." == str(w[-1].message)


@pytest.mark.parametrize(
    "attribute", ["num_tasks", "num_cores", "cores_per_task", "num_nodes", "max_tasks_per_node", "num_gpu", "ram_limit"]
)
@patch("ansys.aedt.core.generic.scheduler.get_aedt_exe", return_value="aedt_path.exe")
def test_negative_values_raise(mock_get_exe, attribute):
    """Test that negative values for certain fields raise ValueError."""
    with pytest.raises(ValueError, match=f"{attribute} must be greater or equal to zero."):
        JobConfigurationData(**{attribute: -1})


@patch("ansys.aedt.core.generic.scheduler.get_aedt_exe", return_value="aedt_path.exe")
def test_switch_between_hpc_method_values(mock_get_exe):
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
def test_use_custom_submission_string_property(mock_get_exe):
    """Test that custom submission string is used correctly."""
    data = JobConfigurationData(custom_submission_string="this is the custom submission string")
    assert data.use_custom_submission_string

    data.custom_submission_string = ""
    assert not data.use_custom_submission_string


@patch("ansys.aedt.core.generic.scheduler.get_aedt_exe", return_value="aedt_path.exe")
def test_fix_data_name_property(mock_get_exe):
    """Test that fix_data_name property works correctly."""
    data = JobConfigurationData()
    assert data.fix_job_name is True

    data.job_name = "my_data"
    assert data.fix_job_name is False


@patch("ansys.aedt.core.generic.scheduler.get_aedt_exe", return_value="aedt_path.exe")
def test_to_dict_contains_expected_keys(mock_get_exe):
    """Test that the to_dict method contains expected keys."""
    EXPECTED_KEYS = {
        "auto_hpc",
        "cores_per_task",
        "custom_submission_string",
        "exclusive",
        "job_name",
        "max_tasks_per_node",
        "monitor",
        "ng_solve",
        "num_cores",
        "num_gpu",
        "num_nodes",
        "num_tasks",
        "product_full_path",
        "ram_limit",
        "ram_per_core",
        "use_ppe",
        "wait_for_license",
    }
    data = JobConfigurationData()
    data = data.to_dict()

    assert isinstance(data, dict)
    assert EXPECTED_KEYS == set(data.keys())


def test_save_areg_generates_file_with_expected_content(tmp_path):
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
\	\	ProductPath=\'"C:\Program Files\AnsysEM\v251\Win64\ansysedt.exe"\'\
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
\	\	\	\	RAMLimit=100\
\	\	\	\	NumCores=2\
\	\	\	\	RAMPerCoreCheckbox=false\
\	\	\	\	RAMPerCoreInGB=\'2.0\'\
\	\	\	$end \'RAMConstrainedBlock\'\
\	\	\	$begin \'NodesAndCoresBlock\'\
\	\	\	\	IsExclusive=false\
\	\	\	\	RAMLimit=100\
\	\	\	\	NumNodes=1\
\	\	\	\	NumCores=2\
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
