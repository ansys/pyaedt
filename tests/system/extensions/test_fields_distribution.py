# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 - 2025 ANSYS, Inc. and/or its affiliates.
# SPDX-License-Identifier: MIT
#
#
# Permission is hereby granted, free of charge, to any person obtaining a
# copy of this software and associated documentation files (the "Software"),
# to deal in the Software without restriction, including without limitation
# the rights to use, copy, modify, merge, publish, distribute, sublicense,
# and/or sell copies of the Software, and to permit persons to whom the
# Software is furnished to do so, subject to the following conditions:
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

from pathlib import Path
import shutil

import pytest

import ansys.aedt.core
from tests import TESTS_EXTENSIONS_PATH

# Test project constants
FIELDS_DISTRIBUTION = "transformer_loss_distribution"
TEST_SUBFOLDER = "T45"


def test_fields_distribution_basic_export(add_app_example, test_tmp_dir):
    """Test basic fields distribution export functionality."""
    from ansys.aedt.core.extensions.maxwell3d.fields_distribution import FieldsDistributionExtensionData
    from ansys.aedt.core.extensions.maxwell3d.fields_distribution import main

    file_path = test_tmp_dir / "loss_distribution_points.csv"

    aedtapp = add_app_example(
        application=ansys.aedt.core.Maxwell2d,
        subfolder=TEST_SUBFOLDER,
        project=FIELDS_DISTRIBUTION,
    )

    data = FieldsDistributionExtensionData(
        points_file="",
        export_file=str(file_path),
        export_option="Ohmic_loss",
        objects_list=["hv_terminal"],
        solution_option="Setup1 : LastAdaptive",
    )
    data.is_test = True

    assert main(data)
    assert file_path.is_file()
    aedtapp.close_project(aedtapp.project_name, save=False)


def test_fields_distribution_with_points_file(add_app_example, test_tmp_dir):
    """Test fields distribution export with custom points file."""
    from ansys.aedt.core.extensions.maxwell3d.fields_distribution import FieldsDistributionExtensionData
    from ansys.aedt.core.extensions.maxwell3d.fields_distribution import main

    file_path = test_tmp_dir / "loss_distribution_points.csv"
    points_file_original = Path(TESTS_EXTENSIONS_PATH) / "example_models" / TEST_SUBFOLDER / "hv_terminal.pts"
    points_file = shutil.copy2(points_file_original, test_tmp_dir / "hv_terminal.pts")

    aedtapp = add_app_example(
        application=ansys.aedt.core.Maxwell2d,
        subfolder=TEST_SUBFOLDER,
        project=FIELDS_DISTRIBUTION,
    )

    data = FieldsDistributionExtensionData(
        points_file=str(points_file),
        export_file=str(file_path),
        export_option="Ohmic_loss",
        objects_list=["hv_terminal"],
        solution_option="Setup1 : LastAdaptive",
    )
    data.is_test = True

    assert main(data)
    assert file_path.is_file()
    aedtapp.close_project(aedtapp.project_name, save=False)


def test_fields_distribution_multiple_objects(add_app_example, test_tmp_dir):
    """Test fields distribution export with multiple objects."""
    from ansys.aedt.core.extensions.maxwell3d.fields_distribution import FieldsDistributionExtensionData
    from ansys.aedt.core.extensions.maxwell3d.fields_distribution import main

    file_path = test_tmp_dir / "loss_distribution_points.csv"

    aedtapp = add_app_example(
        application=ansys.aedt.core.Maxwell2d,
        subfolder=TEST_SUBFOLDER,
        project=FIELDS_DISTRIBUTION,
    )

    data = FieldsDistributionExtensionData(
        points_file="",
        export_file=str(file_path),
        export_option="Ohmic_loss",
        objects_list=["hv_terminal", "lv_turn1"],
        solution_option="Setup1 : LastAdaptive",
    )
    data.is_test = True

    assert main(data)
    assert file_path.is_file()
    aedtapp.close_project(aedtapp.project_name, save=False)


def test_fields_distribution_all_objects(add_app_example, test_tmp_dir):
    """Test fields distribution export with all objects."""
    from ansys.aedt.core.extensions.maxwell3d.fields_distribution import FieldsDistributionExtensionData
    from ansys.aedt.core.extensions.maxwell3d.fields_distribution import main

    file_path = test_tmp_dir / "loss_distribution_points.csv"

    aedtapp = add_app_example(
        application=ansys.aedt.core.Maxwell2d,
        subfolder=TEST_SUBFOLDER,
        project=FIELDS_DISTRIBUTION,
    )

    data = FieldsDistributionExtensionData(
        points_file="",
        export_file=str(file_path),
        export_option="Ohmic_loss",
        objects_list=[],
        solution_option="Setup1 : LastAdaptive",
    )
    data.is_test = True

    assert main(data)
    assert file_path.is_file()
    aedtapp.close_project(aedtapp.project_name, save=False)


def test_fields_distribution_surface_ac_force_density(add_app_example, test_tmp_dir):
    """Test fields distribution export with SurfaceAcForceDensity option."""
    from ansys.aedt.core.extensions.maxwell3d.fields_distribution import FieldsDistributionExtensionData
    from ansys.aedt.core.extensions.maxwell3d.fields_distribution import main

    file_path = test_tmp_dir / "surface_ac_force_density.csv"

    aedtapp = add_app_example(
        application=ansys.aedt.core.Maxwell2d,
        subfolder=TEST_SUBFOLDER,
        project=FIELDS_DISTRIBUTION,
    )

    data = FieldsDistributionExtensionData(
        points_file="",
        export_file=str(file_path),
        export_option="SurfaceAcForceDensity",
        objects_list=["hv_terminal"],
        solution_option="Setup1 : LastAdaptive",
    )
    data.is_test = True

    assert main(data)
    assert file_path.is_file()
    aedtapp.close_project(aedtapp.project_name, save=False)


def test_fields_distribution_npy_export(add_app_example, test_tmp_dir):
    """Test fields distribution export to numpy format."""
    from ansys.aedt.core.extensions.maxwell3d.fields_distribution import FieldsDistributionExtensionData
    from ansys.aedt.core.extensions.maxwell3d.fields_distribution import main

    file_path = test_tmp_dir / "loss_distribution.npy"

    aedtapp = add_app_example(
        application=ansys.aedt.core.Maxwell2d,
        subfolder=TEST_SUBFOLDER,
        project=FIELDS_DISTRIBUTION,
    )

    data = FieldsDistributionExtensionData(
        points_file="",
        export_file=str(file_path),
        export_option="SurfaceAcForceDensity",
        objects_list=["hv_terminal"],
        solution_option="Setup1 : LastAdaptive",
    )
    data.is_test = True

    assert main(data)
    assert file_path.is_file()
    aedtapp.close_project(aedtapp.project_name, save=False)


def test_fields_distribution_tab_export(add_app_example, test_tmp_dir):
    """Test fields distribution export to tab-delimited format."""
    from ansys.aedt.core.extensions.maxwell3d.fields_distribution import FieldsDistributionExtensionData
    from ansys.aedt.core.extensions.maxwell3d.fields_distribution import main

    file_path = test_tmp_dir / "loss_distribution.tab"

    aedtapp = add_app_example(
        application=ansys.aedt.core.Maxwell2d,
        subfolder=TEST_SUBFOLDER,
        project=FIELDS_DISTRIBUTION,
    )

    data = FieldsDistributionExtensionData(
        points_file="",
        export_file=str(file_path),
        export_option="Ohmic_loss",
        objects_list=["hv_terminal"],
        solution_option="Setup1 : LastAdaptive",
    )
    data.is_test = True

    assert main(data)
    assert file_path.is_file()
    aedtapp.close_project(aedtapp.project_name, save=False)


def test_fields_distribution_error_no_export_file(add_app_example):
    """Test error handling when no export file is specified."""
    from ansys.aedt.core.extensions.maxwell3d.fields_distribution import FieldsDistributionExtensionData
    from ansys.aedt.core.extensions.maxwell3d.fields_distribution import main
    from ansys.aedt.core.internal.errors import AEDTRuntimeError

    aedtapp = add_app_example(
        application=ansys.aedt.core.Maxwell2d,
        subfolder=TEST_SUBFOLDER,
        project=FIELDS_DISTRIBUTION,
    )

    data = FieldsDistributionExtensionData(
        points_file="",
        export_file="",
        export_option="Ohmic_loss",
        objects_list=["hv_terminal"],
        solution_option="Setup1 : LastAdaptive",
    )
    data.is_test = True

    with pytest.raises(AEDTRuntimeError, match="No export file specified."):
        main(data)

    aedtapp.close_project(aedtapp.project_name, save=False)


def test_fields_distribution_error_wrong_design_type(add_app, test_tmp_dir):
    """Test error handling when design type is not Maxwell."""
    from ansys.aedt.core.extensions.maxwell3d.fields_distribution import FieldsDistributionExtensionData
    from ansys.aedt.core.extensions.maxwell3d.fields_distribution import main
    from ansys.aedt.core.internal.errors import AEDTRuntimeError

    file_path = test_tmp_dir / "test_export.csv"

    # Use HFSS instead of Maxwell
    aedtapp = add_app(application=ansys.aedt.core.Hfss)

    data = FieldsDistributionExtensionData(
        points_file="",
        export_file=str(file_path),
        export_option="Ohmic_loss",
        objects_list=[],
        solution_option="Setup1 : LastAdaptive",
    )
    data.is_test = True

    with pytest.raises(AEDTRuntimeError, match="Active design is not Maxwell 2D or 3D."):
        main(data)

    aedtapp.close_project(aedtapp.project_name, save=False)


def test_fields_distribution_data_class_initialization():
    """Test FieldsDistributionExtensionData initialization."""
    from ansys.aedt.core.extensions.maxwell3d.fields_distribution import FieldsDistributionExtensionData

    # Test default initialization
    data = FieldsDistributionExtensionData()
    assert data.points_file == ""
    assert data.export_file == ""
    assert data.export_option == "Ohmic loss"
    assert data.objects_list == []
    assert data.solution_option == ""

    # Test custom initialization
    data = FieldsDistributionExtensionData(
        points_file="test.pts",
        export_file="test.csv",
        export_option="SurfaceAcForceDensity",
        objects_list=["obj1", "obj2"],
        solution_option="Setup1 : LastAdaptive",
    )
    assert data.points_file == "test.pts"
    assert data.export_file == "test.csv"
    assert data.export_option == "SurfaceAcForceDensity"
    assert data.objects_list == ["obj1", "obj2"]
    assert data.solution_option == "Setup1 : LastAdaptive"


def test_fields_distribution_file_validation(add_app_example, test_tmp_dir):
    """Test that exported files contain expected data structure."""
    import csv

    import numpy as np

    from ansys.aedt.core.extensions.maxwell3d.fields_distribution import FieldsDistributionExtensionData
    from ansys.aedt.core.extensions.maxwell3d.fields_distribution import main

    aedtapp = add_app_example(
        application=ansys.aedt.core.Maxwell2d,
        subfolder=TEST_SUBFOLDER,
        project=FIELDS_DISTRIBUTION,
    )

    # Test CSV file content
    csv_file_path = test_tmp_dir / "validation_test.csv"
    data = FieldsDistributionExtensionData(
        points_file="",
        export_file=str(csv_file_path),
        export_option="Ohmic_loss",
        objects_list=["hv_terminal"],
        solution_option="Setup1 : LastAdaptive",
    )
    data.is_test = True

    assert main(data)
    assert csv_file_path.is_file()

    # Validate CSV content
    with open(csv_file_path, "r") as f:
        reader = csv.reader(f)
        rows = list(reader)
        assert len(rows) > 0, "CSV file should contain data"

    # Test NPY file content
    npy_file_path = test_tmp_dir / "validation_test.npy"
    data.export_file = str(npy_file_path)

    assert main(data)
    assert npy_file_path.is_file()

    # Validate NPY content
    array_data = np.load(npy_file_path)
    assert array_data.size > 0, "NPY file should contain data"

    aedtapp.close_project(aedtapp.project_name, save=False)


def test_fields_distribution(add_app_example, test_tmp_dir):
    """Test comprehensive fields distribution functionality."""
    from ansys.aedt.core.extensions.maxwell3d.fields_distribution import FieldsDistributionExtensionData
    from ansys.aedt.core.extensions.maxwell3d.fields_distribution import main

    aedtapp = add_app_example(
        application=ansys.aedt.core.Maxwell2d,
        subfolder=TEST_SUBFOLDER,
        project=FIELDS_DISTRIBUTION,
    )

    # Test basic export
    file_path = test_tmp_dir / "loss_distribution.csv"
    data = FieldsDistributionExtensionData(
        points_file="",
        export_file=str(file_path),
        export_option="Ohmic_loss",
        objects_list=["hv_terminal"],
        solution_option="Setup1 : LastAdaptive",
    )
    data.is_test = True

    assert main(data)
    assert file_path.is_file()

    # Test with points file
    points_file_original = TESTS_EXTENSIONS_PATH / "example_models" / TEST_SUBFOLDER / "hv_terminal.pts"
    points_file = shutil.copy2(points_file_original, test_tmp_dir / "hv_terminal.pts")

    data = FieldsDistributionExtensionData(
        points_file=str(points_file),
        export_file=str(file_path),
        export_option="Ohmic_loss",
        objects_list=["hv_terminal"],
        solution_option="Setup1 : LastAdaptive",
    )
    data.is_test = True

    assert main(data)
    assert file_path.is_file()

    # Test with multiple objects
    data = FieldsDistributionExtensionData(
        points_file="",
        export_file=str(file_path),
        export_option="Ohmic_loss",
        objects_list=["hv_terminal", "lv_turn1"],
        solution_option="Setup1 : LastAdaptive",
    )
    data.is_test = True

    assert main(data)
    assert file_path.is_file()

    # Test with empty objects list (all objects)
    data = FieldsDistributionExtensionData(
        points_file="",
        export_file=str(file_path),
        export_option="Ohmic_loss",
        objects_list=[],
        solution_option="Setup1 : LastAdaptive",
    )
    data.is_test = True

    assert main(data)
    assert file_path.is_file()

    # Test SurfaceAcForceDensity option
    data = FieldsDistributionExtensionData(
        points_file="",
        export_file=str(file_path),
        export_option="SurfaceAcForceDensity",
        objects_list=["hv_terminal"],
        solution_option="Setup1 : LastAdaptive",
    )
    data.is_test = True

    assert main(data)
    assert file_path.is_file()

    # Test NPY export
    file_path = test_tmp_dir / "loss_distribution.npy"
    data = FieldsDistributionExtensionData(
        points_file="",
        export_file=str(file_path),
        export_option="SurfaceAcForceDensity",
        objects_list=["hv_terminal"],
        solution_option="Setup1 : LastAdaptive",
    )
    data.is_test = True

    assert main(data)
    assert file_path.is_file()

    aedtapp.close_project(aedtapp.project_name, save=False)


def test_fields_distribution_comprehensive_scenarios(add_app_example, test_tmp_dir):
    """Test comprehensive fields distribution functionality with various scenarios."""
    from ansys.aedt.core.extensions.maxwell3d.fields_distribution import FieldsDistributionExtensionData
    from ansys.aedt.core.extensions.maxwell3d.fields_distribution import main

    file_path = test_tmp_dir / "loss_distribution.csv"

    aedtapp = add_app_example(
        application=ansys.aedt.core.Maxwell2d,
        subfolder=TEST_SUBFOLDER,
        project=FIELDS_DISTRIBUTION,
    )

    # Test basic export
    data = FieldsDistributionExtensionData(
        points_file="",
        export_file=str(file_path),
        export_option="Ohmic_loss",
        objects_list=["hv_terminal"],
        solution_option="Setup1 : LastAdaptive",
    )
    data.is_test = True

    assert main(data)
    assert file_path.is_file()

    # Test with points file
    points_file_original = TESTS_EXTENSIONS_PATH / "example_models" / TEST_SUBFOLDER / "hv_terminal.pts"
    points_file = shutil.copy2(points_file_original, test_tmp_dir / "hv_terminal.pts")

    data = FieldsDistributionExtensionData(
        points_file=str(points_file),
        export_file=str(file_path),
        export_option="Ohmic_loss",
        objects_list=["hv_terminal"],
        solution_option="Setup1 : LastAdaptive",
    )
    data.is_test = True

    assert main(data)
    assert file_path.is_file()

    # Test with multiple objects
    data = FieldsDistributionExtensionData(
        points_file="",
        export_file=str(file_path),
        export_option="Ohmic_loss",
        objects_list=["hv_terminal", "lv_turn1"],
        solution_option="Setup1 : LastAdaptive",
    )
    data.is_test = True

    assert main(data)
    assert file_path.is_file()

    # Test with empty objects list (all objects)
    data = FieldsDistributionExtensionData(
        points_file="",
        export_file=str(file_path),
        export_option="Ohmic_loss",
        objects_list=[],
        solution_option="Setup1 : LastAdaptive",
    )
    data.is_test = True

    assert main(data)
    assert file_path.is_file()

    # Test SurfaceAcForceDensity option
    data = FieldsDistributionExtensionData(
        points_file="",
        export_file=str(file_path),
        export_option="SurfaceAcForceDensity",
        objects_list=["hv_terminal"],
        solution_option="Setup1 : LastAdaptive",
    )
    data.is_test = True

    assert main(data)
    assert file_path.is_file()

    # Test NPY export
    file_path = test_tmp_dir / "loss_distribution.npy"
    data = FieldsDistributionExtensionData(
        points_file="",
        export_file=str(file_path),
        export_option="SurfaceAcForceDensity",
        objects_list=["hv_terminal"],
        solution_option="Setup1 : LastAdaptive",
    )
    data.is_test = True

    assert main(data)
    assert file_path.is_file()

    aedtapp.close_project(aedtapp.project_name, save=False)
