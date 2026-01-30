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

from pathlib import Path
import shutil

import pytest

from ansys.aedt.core.visualization.plot.pyvista import ModelPlotter
from tests import TESTS_VISUALIZATION_PATH

TEST_SUBFOLDER = "T50"


@pytest.fixture(scope="module", autouse=True)
def desktop():
    """Override the desktop fixture to DO NOT open the Desktop when running this test class"""
    return


@pytest.fixture
def setup_test_data(request, test_tmp_dir):
    # vector field files
    vector_field_path = Path(TESTS_VISUALIZATION_PATH) / "example_models" / TEST_SUBFOLDER / "vector_field"
    vector_dir = test_tmp_dir / "vector_files"
    shutil.copytree(vector_field_path, vector_dir)

    vector_file_fld = vector_dir / "SurfaceAcForceDensity.fld"
    request.cls.field_fld = str(vector_file_fld)

    vector_file_aedtplt = vector_dir / "SurfaceAcForceDensity.aedtplt"
    request.cls.field_aedtplt = str(vector_file_aedtplt)

    case_path = vector_field_path / "case"
    vector_file_case = case_path / "SurfaceAcForceDensity.case"
    request.cls.field_case = str(vector_file_case)

    # scalar field files
    scalar_field_path = Path(TESTS_VISUALIZATION_PATH) / "example_models" / TEST_SUBFOLDER / "scalar_field"
    scalar_dir = test_tmp_dir / "scalar_files"
    shutil.copytree(scalar_field_path, scalar_dir)

    scalar_file_fld = scalar_dir / "Ohmic_Loss.fld"
    request.cls.scalar_fld = str(scalar_file_fld)

    scalar_file_aedtplt = scalar_dir / "Ohmic_Loss.aedtplt"
    request.cls.scalar_aedtplt = str(scalar_file_aedtplt)

    case_path = scalar_field_path / "case"
    scalar_file_case = case_path / "Ohmic_Loss.case"
    request.cls.scalar_case = str(scalar_file_case)

    # cartesian field files
    cartesian_field_path = Path(TESTS_VISUALIZATION_PATH) / "example_models" / TEST_SUBFOLDER
    cartesian_dir = test_tmp_dir / "cartesian_files"
    shutil.copytree(cartesian_field_path, cartesian_dir)

    cartesian_field_file = cartesian_dir / "E_xyz.fld"
    request.cls.cartesian_fld = str(cartesian_field_file)
    yield


@pytest.mark.usefixtures("setup_test_data")
class TestClass:
    def test_add_field_file(self):
        # vector field
        model_pv_vector = ModelPlotter()
        assert not model_pv_vector.fields
        model_pv_vector.add_field_from_file(self.field_fld)
        assert isinstance(model_pv_vector.fields, list)
        assert len(model_pv_vector.fields) == 1
        model_pv_vector.add_field_from_file(self.field_aedtplt)
        assert len(model_pv_vector.fields) == 2
        model_pv_vector.add_field_from_file(self.field_case)
        assert len(model_pv_vector.fields) == 3
        # scalar field
        model_pv_scalar = ModelPlotter()
        assert not model_pv_scalar.fields
        model_pv_scalar.add_field_from_file(self.scalar_fld)
        assert isinstance(model_pv_scalar.fields, list)
        assert len(model_pv_scalar.fields) == 1
        model_pv_scalar.add_field_from_file(self.scalar_aedtplt)
        assert len(model_pv_scalar.fields) == 2
        model_pv_scalar.add_field_from_file(self.scalar_case)
        assert len(model_pv_scalar.fields) == 3

    def test_populate_pyvista_object(self):
        # vector field
        model_pv_vector = ModelPlotter()
        model_pv_vector.add_field_from_file(self.field_fld)
        model_pv_vector.populate_pyvista_object()
        assert model_pv_vector.pv
        assert model_pv_vector.pv.mesh
        assert len(model_pv_vector.pv.mesh.points) == len(model_pv_vector.pv.mesh.active_scalars)
        assert len(model_pv_vector.pv.mesh.points) == len(model_pv_vector.pv.mesh.active_vectors)
        model_pv_vector1 = ModelPlotter()
        model_pv_vector1.add_field_from_file(self.field_aedtplt)
        model_pv_vector1.populate_pyvista_object()
        assert model_pv_vector1.pv
        assert model_pv_vector1.pv.mesh
        assert len(model_pv_vector1.pv.mesh.points) == len(model_pv_vector1.pv.mesh.active_scalars)
        assert len(model_pv_vector1.pv.mesh.points) == len(model_pv_vector1.pv.mesh.active_vectors)
        # scalar field
        model_pv_scalar2 = ModelPlotter()
        model_pv_scalar2.add_field_from_file(self.scalar_fld)
        model_pv_scalar2.range_min = 0.0001
        model_pv_scalar2.range_max = 1
        model_pv_scalar2.populate_pyvista_object()
        assert model_pv_scalar2.pv
        assert model_pv_scalar2.pv.mesh
        assert len(model_pv_scalar2.pv.mesh.points) == len(model_pv_scalar2.pv.mesh.active_scalars)
        assert not model_pv_scalar2.pv.mesh.active_vectors
        model_pv_scalar3 = ModelPlotter()
        model_pv_scalar3.add_field_from_file(self.scalar_aedtplt)
        model_pv_scalar3.convert_fields_in_db = True
        model_pv_scalar3.populate_pyvista_object()
        assert model_pv_scalar3.pv
        assert model_pv_scalar3.pv.mesh
        assert len(model_pv_scalar3.pv.mesh.points) == len(model_pv_scalar3.pv.mesh.active_scalars)
        assert not model_pv_scalar3.pv.mesh.active_vectors
        # cartesian field
        model_pv_scalar4 = ModelPlotter()
        model_pv_scalar4.add_field_from_file(self.cartesian_fld)
        model_pv_scalar4.populate_pyvista_object()
        assert model_pv_scalar4.pv
        assert model_pv_scalar4.pv.mesh
        assert len(model_pv_scalar4.pv.mesh.points) == len(model_pv_scalar4.pv.mesh.active_scalars)
        assert len(model_pv_scalar4.pv.mesh.points) == len(model_pv_scalar4.pv.mesh.active_vectors)

    def test_vector_field_scale(self):
        model_pv_vector = ModelPlotter()
        model_pv_vector.add_field_from_file(self.field_fld)
        model_pv_vector.populate_pyvista_object()
        assert model_pv_vector.vector_field_scale == 1
        model_pv_vector.vector_field_scale = 5
        assert model_pv_vector.vector_field_scale == 5

    @pytest.mark.avoid_ansys_load
    def test_animate(self, test_tmp_dir):
        model_pv_vector = ModelPlotter()
        model_pv_vector.add_frames_from_file([self.field_fld, self.field_fld])
        model_pv_vector.animate(show=False)

        model_pv_vector = ModelPlotter()
        model_pv_vector.gif_file = test_tmp_dir / "field.gif"
        model_pv_vector.add_frames_from_file([self.field_fld, self.field_aedtplt])
        model_pv_vector.animate(show=False)
