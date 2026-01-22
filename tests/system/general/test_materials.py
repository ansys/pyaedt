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

import builtins
import logging
from pathlib import Path
from unittest.mock import mock_open

from mock import patch
import pytest

from ansys.aedt.core import Icepak
from ansys.aedt.core import Maxwell3d
from ansys.aedt.core.hfss import Hfss
from ansys.aedt.core.modules.material import MatProperties
from ansys.aedt.core.modules.material import SurfMatProperties
from tests import TESTS_GENERAL_PATH
from tests.conftest import USE_GRPC

TEST_SUBFOLDER = "T03"

MISSING_RGB_MATERIALS = b"""
{
    "materials": {
        "copper_5540": {
            "AttachedData": {
                "MatAppearanceData": {
                    "property_data": "appearance_data"
                }
            },
            "permeability": "0.999991",
            "conductivity": "58000000"
        }
    }
}
"""


@pytest.fixture
def aedt_app(add_app):
    app = add_app(application=Hfss)
    yield app
    app.close_project(app.project_name, save=False)


@pytest.fixture
def m3d_app(add_app):
    app = add_app(application=Maxwell3d)
    yield app
    app.close_project(app.project_name, save=False)


@pytest.fixture
def icepak_app(add_app):
    app = add_app(application=Icepak)
    yield app
    app.close_project(app.project_name, save=False)


@pytest.fixture
def maxwell_app(add_app):
    app = add_app(application=Maxwell3d)
    yield app
    app.close_project(app.project_name, save=False)


def test_vacuum(aedt_app):
    assert "vacuum" in list(aedt_app.materials.material_keys.keys())


def test_create_material(aedt_app):
    mat1 = aedt_app.materials.add_material("new_copper2")
    assert mat1
    mat1.conductivity = 59000000000
    assert mat1.conductivity.value == 59000000000
    mat1.permeability.value = MatProperties.get_defaultvalue(aedtname="permeability")
    assert mat1.permeability.value == MatProperties.get_defaultvalue(aedtname="permeability")
    mat1.permeability.value = [[0, 0], [30, 40], [50, 60]]
    assert mat1.permeability.type == "nonlinear"
    mat1.permittivity.value = 5
    assert mat1.permittivity.value == 5
    mat1.dielectric_loss_tangent.value = 0.1
    assert mat1.dielectric_loss_tangent.value == 0.1
    mat1.magnetic_loss_tangent.value = 0.2
    assert mat1.magnetic_loss_tangent.value == 0.2
    mat1.mass_density.value = 100
    assert mat1.mass_density.value == 100
    mat1.youngs_modulus.value = 1000
    assert mat1.youngs_modulus.value == 1000
    mat1.poissons_ratio.value = [1, 2, 3]
    assert mat1.poissons_ratio.value == [1, 2, 3]
    assert mat1.poissons_ratio.type == "anisotropic"
    mat1.thermal_conductivity.value = 5
    assert mat1.thermal_conductivity.value == 5
    mat1.thermal_conductivity = [1, 2, 3, 4, 5, 6, 7, 8, 9]
    assert mat1.thermal_conductivity.type == "tensor"
    mat1.diffusivity.value = MatProperties.get_defaultvalue(aedtname="diffusivity")

    assert mat1.diffusivity.value == MatProperties.get_defaultvalue(aedtname="diffusivity")

    assert "Electromagnetic" in mat1.physics_type
    mat1.molecular_mass.value = MatProperties.get_defaultvalue(aedtname="molecular_mass")
    mat1.specific_heat.value = MatProperties.get_defaultvalue(aedtname="specific_heat")
    mat1.thermal_expansion_coefficient.value = 100

    assert mat1.coordinate_system == "Cartesian"
    assert mat1.name == "new_copper2"
    assert mat1.molecular_mass.value == MatProperties.get_defaultvalue(aedtname="molecular_mass")
    assert mat1.specific_heat.value == MatProperties.get_defaultvalue(aedtname="specific_heat")
    assert mat1.thermal_expansion_coefficient.value == 100
    assert aedt_app.change_validation_settings()
    assert aedt_app.change_validation_settings(ignore_unclassified=True, skip_intersections=True)

    assert mat1.set_magnetic_coercivity(1, 2, 3, 4)
    assert mat1.get_magnetic_coercivity() == ("1A_per_meter", "2", "3", "4")
    mat1.coordinate_system = "Cylindrical"
    assert mat1.coordinate_system == "Cylindrical"
    mat1.magnetic_coercivity = [2, 1, 0, 1]

    assert mat1.get_magnetic_coercivity() == ("2A_per_meter", "1", "0", "1")
    mat1.magnetic_coercivity.value = ["1", "2", "3", "4"]
    assert mat1.get_magnetic_coercivity() == ("1A_per_meter", "2", "3", "4")
    assert mat1.magnetic_coercivity.evaluated_value == [1.0, 2.0, 3.0, 4.0]

    assert mat1.set_electrical_steel_coreloss(1, 2, 3, 4, 0.002)
    assert mat1.get_curve_coreloss_type() == "Electrical Steel"
    assert mat1.get_curve_coreloss_values()["core_loss_equiv_cut_depth"] == 0.002
    assert mat1.set_hysteresis_coreloss(1, 2, 3, 4, 0.002)
    assert mat1.get_curve_coreloss_type() == "Hysteresis Model"
    assert mat1.set_bp_curve_coreloss([[0, 0], [10, 10], [20, 20]])
    assert mat1.get_curve_coreloss_type() == "B-P Curve"
    assert mat1.set_power_ferrite_coreloss()
    assert mat1.get_curve_coreloss_type() == "Power Ferrite"
    assert isinstance(mat1.material_appearance, list)

    mat1.material_appearance = [11, 22, 0, 0.5]
    assert mat1.material_appearance == [11, 22, 0, 0.5]
    mat1.material_appearance = ["11", "22", "10", "0.5"]
    assert mat1.material_appearance == [11, 22, 10, 0.5]
    with pytest.raises(ValueError):
        mat1.material_appearance = [11, 22, 300, 0.5]
    with pytest.raises(ValueError):
        mat1.material_appearance = [11, 22, 100, 1.5]
    with pytest.raises(ValueError):
        mat1.material_appearance = [11, -22, 0, 0.5]
    with pytest.raises(ValueError):
        mat1.material_appearance = [11, 22, 0, -1]
    with pytest.raises(ValueError):
        mat1.material_appearance = [11, 22]


def test_create_modifiers(aedt_app):
    aedt_app.materials.add_material("new_copper")
    assert aedt_app.materials["new_copper"].mass_density.add_thermal_modifier_free_form(
        "if(Temp > 1000cel, 1, if(Temp < -273.15cel, 1, 1))"
    )
    assert aedt_app.materials["new_copper"].mass_density.add_thermal_modifier_closed_form()
    assert aedt_app.materials["new_copper"].mass_density.add_thermal_modifier_closed_form(auto_calc=False)
    assert aedt_app.materials["new_copper"].permittivity.add_thermal_modifier_closed_form()
    assert aedt_app.materials["new_copper"].permeability.add_thermal_modifier_closed_form(auto_calc=False)
    assert aedt_app.materials["new_copper"].permittivity.add_thermal_modifier_closed_form(auto_calc=False)
    filename = Path(TESTS_GENERAL_PATH) / "example_models" / TEST_SUBFOLDER / "ds_1d.tab"
    ds1 = aedt_app.import_dataset1d(filename)
    assert aedt_app.materials["new_copper"].permittivity.add_thermal_modifier_dataset(ds1.name)

    assert aedt_app.materials["new_copper"].mass_density.add_spatial_modifier_free_form(
        "if(X > 1mm, 1, if(X < 1mm, 2, 1))"
    )
    assert aedt_app.materials["new_copper"].mass_density.add_spatial_modifier_free_form(
        "if(X > 1mm, 1, if(X < 1mm, 3, 1))"
    )
    exp = aedt_app.materials["new_copper"].mass_density.spatialmodifier = "X+1"
    assert exp == "X+1"
    exp = aedt_app.materials["new_copper"].mass_density.spatialmodifier = ["Y+1"]
    assert exp == ["Y+1"]
    filename = Path(TESTS_GENERAL_PATH) / "example_models" / TEST_SUBFOLDER / "ds_3d.tab"
    ds2 = aedt_app.import_dataset3d(str(filename))
    assert aedt_app.materials["new_copper"].permeability.add_spatial_modifier_dataset(ds2.name)
    mat1 = aedt_app.materials.add_material("new_mat")
    assert mat1.mass_density.value == MatProperties.get_defaultvalue(aedtname="mass_density")
    assert mat1.permittivity.value == MatProperties.get_defaultvalue(aedtname="permittivity")
    assert aedt_app.materials["new_mat"].mass_density.add_spatial_modifier_free_form(
        "if(X > 1mm, 1, if(X < 1mm, 3, 1))"
    )
    assert aedt_app.materials["new_mat"].mass_density.add_thermal_modifier_free_form(
        "if(Temp > 1000cel, 1, if(Temp < -273.15cel, 1, 1))"
    )
    assert aedt_app.materials["new_mat"].permittivity.add_thermal_modifier_free_form("X^2")
    mat1 = aedt_app.materials.add_material("new_mat2")
    assert mat1.mass_density.value == MatProperties.get_defaultvalue(aedtname="mass_density")
    assert aedt_app.materials["new_mat2"].mass_density.add_spatial_modifier_free_form(
        "if(X > 1mm, 1, if(X < 1mm, 3, 1))"
    )
    assert aedt_app.materials["new_mat2"].mass_density.add_thermal_modifier_closed_form()
    mat1 = aedt_app.materials.add_material("new_mat3")
    assert mat1.mass_density.value == MatProperties.get_defaultvalue(aedtname="mass_density")
    assert aedt_app.materials["new_mat3"].mass_density.add_thermal_modifier_closed_form()


def test_duplicate_material(aedt_app):
    aedt_app.materials.add_material("copper")
    assert aedt_app.materials.duplicate_material("copper", "copper2")
    assert not aedt_app.materials.duplicate_material("nonexistent_copper", "copper2")


def test_delete_material(aedt_app):
    aedt_app.materials.add_material("copper")
    assert aedt_app.materials.remove_material("copper")
    assert not aedt_app.materials.remove_material("copper2")


def test_surface_material(icepak_app):
    mat2 = icepak_app.materials.add_surface_material("Steel")
    mat2.emissivity.value = SurfMatProperties.get_defaultvalue(aedtname="surface_emissivity")
    mat2.surface_diffuse_absorptance.value = SurfMatProperties.get_defaultvalue(aedtname="surface_diffuse_absorptance")
    mat2.surface_roughness.value = SurfMatProperties.get_defaultvalue(aedtname="surface_roughness")

    assert mat2.emissivity.value == SurfMatProperties.get_defaultvalue(aedtname="surface_emissivity")
    assert mat2.coordinate_system
    assert mat2.surface_diffuse_absorptance.value == SurfMatProperties.get_defaultvalue(
        aedtname="surface_diffuse_absorptance"
    )
    assert mat2.surface_roughness.value == SurfMatProperties.get_defaultvalue(aedtname="surface_roughness")
    assert icepak_app.materials.duplicate_surface_material("Steel", "Steel2")
    assert not icepak_app.materials.duplicate_surface_material("Steel4", "Steel2")
    assert icepak_app.materials.duplicate_surface_material("Steel")


def test_export_materials(aedt_app, test_tmp_dir):
    assert aedt_app.materials.export_materials_to_file(test_tmp_dir / "materials.json")
    assert (test_tmp_dir / "materials.json").exists()


def test_import_materials(aedt_app):
    assert aedt_app.materials.import_materials_from_file(
        Path(TESTS_GENERAL_PATH) / "example_models" / TEST_SUBFOLDER / "mats.json"
    )
    assert "$copper_ds1" in aedt_app.project_datasets.keys()
    assert "copper_5540" in aedt_app.materials.material_keys.keys()
    assert "al-extruded1" in aedt_app.materials.material_keys.keys()
    assert aedt_app.materials["al-extruded1"].thermal_conductivity.thermalmodifier

    assert not aedt_app.materials.import_materials_from_file()
    assert not aedt_app.materials.import_materials_from_file("mat.invented")
    assert not aedt_app.materials.import_materials_from_file(
        Path(TESTS_GENERAL_PATH) / "example_models" / TEST_SUBFOLDER / "mats.csv"
    )

    assert aedt_app.materials.import_materials_from_file(
        Path(TESTS_GENERAL_PATH) / "example_models" / TEST_SUBFOLDER / "material_sample.amat"
    )
    assert aedt_app.materials.import_materials_from_file(
        Path(TESTS_GENERAL_PATH) / "example_models" / TEST_SUBFOLDER / "iron_pyaedt.amat"
    )


def test_import_materials_from_excel(aedt_app):
    mats = aedt_app.materials.import_materials_from_excel(
        Path(TESTS_GENERAL_PATH) / "example_models" / TEST_SUBFOLDER / "mats.xlsx"
    )
    assert len(mats) == 2
    assert mats[0].conductivity.value == 5700000
    assert mats[0].permittivity.value == 0.5
    assert mats[0].name == "aluminum_2"
    mats = aedt_app.materials.import_materials_from_excel(
        Path(TESTS_GENERAL_PATH) / "example_models" / TEST_SUBFOLDER / "mats.csv"
    )
    assert len(mats) == 2


def test_non_linear_materials(maxwell_app, test_tmp_dir):
    mat1 = maxwell_app.materials.add_material("myMat")
    mat1.permeability = [[0, 0], [1, 12], [10, 30]]
    mat1.permeability.set_non_linear(x_unit="Oe", y_unit="gauss")
    mat1.permittivity = [[0, 0], [2, 12], [10, 30]]
    mat1.conductivity.value = [[0, 0], [3, 12], [10, 30]]
    maxwell_app.materials.export_materials_to_file(test_tmp_dir / "non_linear.json")
    (test_tmp_dir / "non_linear.json").exists()
    maxwell_app.materials.remove_material("myMat")
    maxwell_app.materials.import_materials_from_file(test_tmp_dir / "non_linear.json")
    assert maxwell_app.materials["myMat"].permeability.value == [[0, 0], [1, 12], [10, 30]]
    assert maxwell_app.materials["myMat"].permittivity.value == [[0, 0], [2, 12], [10, 30]]
    assert maxwell_app.materials["myMat"].conductivity.value == [[0, 0], [3, 12], [10, 30]]
    assert maxwell_app.materials["myMat"].permeability.type == "nonlinear"
    assert maxwell_app.materials["myMat"].conductivity.type == "nonlinear"
    assert maxwell_app.materials["myMat"].permittivity.type == "nonlinear"
    assert maxwell_app.materials["myMat"].permeability.bunit == "tesla"
    assert maxwell_app.materials["myMat"].permeability.hunit == "A_per_meter"
    mat2 = maxwell_app.materials.add_material("myMat2")
    assert not mat2.is_used
    assert maxwell_app.modeler.create_box([0, 0, 0], [10, 10, 10], material="myMat2")
    assert maxwell_app.materials.material_keys["mymat2"].is_used


def test_add_material_sweep(aedt_app):
    material_name = "sweep_material"
    assert aedt_app.materials.add_material_sweep(["copper", "aluminum", "FR4_epoxy"], material_name)
    assert material_name in list(aedt_app.materials.material_keys.keys())
    properties_to_check = [
        "permittivity",
        "permeability",
        "conductivity",
        "dielectric_loss_tangent",
        "thermal_conductivity",
        "mass_density",
        "specific_heat",
        "thermal_expansion_coefficient",
        "youngs_modulus",
        "poissons_ratio",
    ]
    # check if the variables are correctly created
    assert "$ID" + material_name in aedt_app.variable_manager.variable_names
    for prop in properties_to_check:
        var_name = "$" + material_name + "_" + prop
        assert var_name in aedt_app.variable_manager.variable_names
    # check if the material properties are correct
    for prop in properties_to_check:
        var_name = "$" + material_name + "_" + prop
        mat_prop = getattr(aedt_app.materials[material_name], prop).value
        assert mat_prop == var_name + "[$ID" + material_name + "]"


def test_material_case(aedt_app):
    assert aedt_app.materials["Aluminum"] == aedt_app.materials["aluminum"]
    assert aedt_app.materials["Aluminum"].name == "aluminum"
    assert aedt_app.materials.add_material("AluMinum") == aedt_app.materials["aluminum"]


def test_material_model(aedt_app):
    mat = aedt_app.materials.add_material("ds_material")
    aedt_app["$dk"] = 3
    aedt_app["$df"] = 0.01
    assert mat.set_djordjevic_sarkar_model(dk="$dk", df="$df")


@pytest.mark.skipif(not USE_GRPC, reason="Not running in COM mode")
def test_get_materials_in_project(aedt_app):
    used_materials = aedt_app.materials.get_used_project_material_names()
    assert isinstance(used_materials, list)
    for m in [mat for mat in aedt_app.materials if mat.is_used]:
        assert m.name in used_materials


def test_get_coreloss_coefficients(aedt_app):
    aedt_app.materials.add_material("mat_test")
    # Test points_list_at_freq
    coeff = aedt_app.materials["mat_test"].get_core_loss_coefficients(
        points_at_frequency={60: [[0, 0], [1, 3.5], [2, 7.4]]}
    )
    assert isinstance(coeff, list)
    assert len(coeff) == 3
    assert all(isinstance(c, float) for c in coeff)
    coeff = aedt_app.materials["mat_test"].get_core_loss_coefficients(
        points_at_frequency={"60Hz": [[0, 0], [1, 3.5], [2, 7.4]]}
    )
    assert isinstance(coeff, list)
    assert len(coeff) == 3
    assert all(isinstance(c, float) for c in coeff)
    coeff = aedt_app.materials["mat_test"].get_core_loss_coefficients(
        points_at_frequency={"0.06kHz": [[0, 0], [1, 3.5], [2, 7.4]]}
    )
    assert isinstance(coeff, list)
    assert len(coeff) == 3
    assert all(isinstance(c, float) for c in coeff)
    with pytest.raises(TypeError):
        aedt_app.materials["mat_test"].get_core_loss_coefficients(points_at_frequency=[[0, 0], [1, 3.5], [2, 7.4]])
    coeff = aedt_app.materials["mat_test"].get_core_loss_coefficients(
        points_at_frequency={
            60: [[0, 0], [1, 3.5], [2, 7.4]],
            100: [[0, 0], [1, 8], [2, 9]],
            150: [[0, 0], [1, 10], [2, 19]],
        }
    )
    assert isinstance(coeff, list)
    assert len(coeff) == 3
    assert all(isinstance(c, float) for c in coeff)
    # Test thickness
    coeff = aedt_app.materials["mat_test"].get_core_loss_coefficients(
        points_at_frequency={60: [[0, 0], [1, 3.5], [2, 7.4]]}, thickness="0.6mm"
    )
    assert isinstance(coeff, list)
    assert len(coeff) == 3
    assert all(isinstance(c, float) for c in coeff)
    with pytest.raises(TypeError):
        aedt_app.materials["mat_test"].get_core_loss_coefficients(
            points_at_frequency={60: [[0, 0], [1, 3.5], [2, 7.4]]}, thickness="invalid"
        )
    with pytest.raises(TypeError):
        aedt_app.materials["mat_test"].get_core_loss_coefficients(
            points_at_frequency={60: [[0, 0], [1, 3.5], [2, 7.4]]}, thickness=50
        )


def test_set_core_loss(m3d_app):
    # Testing in time harmonic solver
    m3d_app.solution_type = "AC Magnetic"

    m3d_app.materials.add_material("mat_test")
    # Test points_list_at_freq
    assert m3d_app.materials["mat_test"].set_coreloss_at_frequency(
        points_at_frequency={60: [[0, 0], [1, 3.5], [2, 7.4]]}
    )
    assert m3d_app.materials["mat_test"].set_coreloss_at_frequency(
        points_at_frequency={"60Hz": [[0, 0], [1, 3.5], [2, 7.4]]}
    )
    assert m3d_app.materials["mat_test"].set_coreloss_at_frequency(
        points_at_frequency={"0.06kHz": [[0, 0], [1, 3.5], [2, 7.4]]}
    )
    with pytest.raises(TypeError):
        m3d_app.materials["mat_test"].set_coreloss_at_frequency(points_at_frequency=[[0, 0], [1, 3.5], [2, 7.4]])
    assert m3d_app.materials["mat_test"].set_coreloss_at_frequency(
        points_at_frequency={
            60: [[0, 0], [1, 3.5], [2, 7.4]],
            100: [[0, 0], [1, 8], [2, 9]],
            150: [[0, 0], [1, 10], [2, 19]],
        }
    )
    assert m3d_app.materials["mat_test"].set_coreloss_at_frequency(
        points_at_frequency={
            60: [[0, 0], [1, 3.5], [2, 7.4]],
            100: [[0, 0], [1, 8], [2, 9]],
            150: [[0, 0], [1, 10], [2, 19]],
        },
        core_loss_model_type="Power Ferrite",
    )
    with pytest.raises(ValueError):
        m3d_app.materials["mat_test"].set_coreloss_at_frequency(
            points_at_frequency={80: [[0, 0], [1, 3.5], [2, 7.4]]}, core_loss_model_type="Power Ferrite"
        )
    # Test thickness
    assert m3d_app.materials["mat_test"].set_coreloss_at_frequency(
        points_at_frequency={60: [[0, 0], [1, 3.5], [2, 7.4]]}, thickness="0.6mm"
    )
    with pytest.raises(TypeError):
        m3d_app.materials["mat_test"].set_coreloss_at_frequency(
            points_at_frequency={60: [[0, 0], [1, 3.5], [2, 7.4]]}, thickness="invalid"
        )
    with pytest.raises(TypeError):
        m3d_app.materials["mat_test"].set_coreloss_at_frequency(
            points_at_frequency={60: [[0, 0], [1, 3.5], [2, 7.4]]}, thickness=50
        )

    # Test core loss values are correct and calculated from the correct curves

    # create three bh curves at different frequencies and create a custom material
    bh_multiple_25hz = [
        [0, 0],
        [0.106114, 11.3066],
        [0.126, 19.64],
        [0.15, 29.73],
        [0.176, 46.41],
        [0.19, 69.18],
        [0.23, 100],
    ]
    bh_multiple_50hz = [
        [0, 0],
        [0.084, 17.91],
        [0.10, 30.66],
        [0.12, 50.894],
        [0.1436, 78.22],
        [0.1794, 133.85],
        [0.2125, 229.087],
    ]
    bh_multiple_100hz = [
        [0, 0],
        [0.0611, 19.64],
        [0.0743, 33.11],
        [0.0864, 47.1339],
        [0.1061, 88.4437],
        [0.141, 193.494],
        [0.17469, 353.101],
    ]

    multiple_frequencies = m3d_app.materials.add_material(name="multiple_frequencies")
    multiple_frequencies.conductivity = 2000000
    multiple_frequencies.mass_density = 7850

    multiple_frequencies.set_coreloss_at_frequency(
        points_at_frequency={25: bh_multiple_25hz, 50: bh_multiple_50hz, 100: bh_multiple_100hz}
    )

    # flatten bh curves from list of lists to list as shown in native api
    flattened_bh_multiple_25hz = [item for sublist in bh_multiple_25hz for item in sublist]
    flattened_bh_multiple_50hz = [item for sublist in bh_multiple_50hz for item in sublist]
    flattened_bh_multiple_100hz = [item for sublist in bh_multiple_100hz for item in sublist]
    tol = 1e-4

    assert multiple_frequencies.get_curve_coreloss_type() == "Electrical Steel"
    assert round(float(multiple_frequencies.get_curve_coreloss_values()["core_loss_kh"]) - 67.1481001207547, 4) < tol
    assert round(float(multiple_frequencies.get_curve_coreloss_values()["core_loss_kc"]) - 0.381660804560751, 4) < tol
    assert round(float(multiple_frequencies.get_curve_coreloss_values()["core_loss_ke"]) - 0.0, 4) < tol
    assert round(float(multiple_frequencies.get_curve_coreloss_values()["core_loss_kdc"]) - 0.0, 4) < tol

    # save project before checking project properties
    m3d_app.save_project()
    assert (
        flattened_bh_multiple_25hz
        == m3d_app.project_properties["AnsoftProject"]["Definitions"]["Materials"]["multiple_frequencies"][
            "AttachedData"
        ]["CoreLossMultiCurveData"]["AllCurves"]["OneCurve"][0]["Coordinates"]["Points"]
    )
    assert (
        "25Hz"
        == m3d_app.project_properties["AnsoftProject"]["Definitions"]["Materials"]["multiple_frequencies"][
            "AttachedData"
        ]["CoreLossMultiCurveData"]["AllCurves"]["OneCurve"][0]["Frequency"]
    )

    assert (
        flattened_bh_multiple_50hz
        == m3d_app.project_properties["AnsoftProject"]["Definitions"]["Materials"]["multiple_frequencies"][
            "AttachedData"
        ]["CoreLossMultiCurveData"]["AllCurves"]["OneCurve"][1]["Coordinates"]["Points"]
    )
    assert (
        "50Hz"
        == m3d_app.project_properties["AnsoftProject"]["Definitions"]["Materials"]["multiple_frequencies"][
            "AttachedData"
        ]["CoreLossMultiCurveData"]["AllCurves"]["OneCurve"][1]["Frequency"]
    )

    assert (
        flattened_bh_multiple_100hz
        == m3d_app.project_properties["AnsoftProject"]["Definitions"]["Materials"]["multiple_frequencies"][
            "AttachedData"
        ]["CoreLossMultiCurveData"]["AllCurves"]["OneCurve"][2]["Coordinates"]["Points"]
    )
    assert (
        "100Hz"
        == m3d_app.project_properties["AnsoftProject"]["Definitions"]["Materials"]["multiple_frequencies"][
            "AttachedData"
        ]["CoreLossMultiCurveData"]["AllCurves"]["OneCurve"][2]["Frequency"]
    )

    # create single bh curves at a frequency and create a custom material

    bh_single_60hz = [[0, 0], [1, 3.5], [2, 7.4]]
    single_frequency = m3d_app.materials.add_material(name="single_frequency")
    single_frequency.conductivity = 2000000
    single_frequency.mass_density = 7850
    single_frequency.set_coreloss_at_frequency(points_at_frequency={60: bh_single_60hz})

    # flatten bh curves from list of lists to list as shown in native api
    flattened_bh_single_60hz = [item for sublist in bh_single_60hz for item in sublist]

    assert single_frequency.get_curve_coreloss_type() == "Electrical Steel"
    assert round(float(single_frequency.get_curve_coreloss_values()["core_loss_kh"]) - 0.0, 4) < tol
    assert round(float(single_frequency.get_curve_coreloss_values()["core_loss_kc"]) - 0.0, 4) < tol
    assert round(float(single_frequency.get_curve_coreloss_values()["core_loss_ke"]) - 0.00584064075447473, 4) < tol
    assert round(float(single_frequency.get_curve_coreloss_values()["core_loss_kdc"]) - 0, 4) < tol

    # save project before checking project properties
    m3d_app.save_project()
    assert (
        "60Hz"
        == m3d_app.project_properties["AnsoftProject"]["Definitions"]["Materials"]["single_frequency"]["AttachedData"][
            "CoefficientSetupData"
        ]["Frequency"]
    )
    assert (
        flattened_bh_single_60hz
        == m3d_app.project_properties["AnsoftProject"]["Definitions"]["Materials"]["single_frequency"]["AttachedData"][
            "CoefficientSetupData"
        ]["Coordinates"]["Points"]
    )


def test_thermalmodifier_and_spatialmodifier(aedt_app):
    assert aedt_app.materials["vacuum"].conductivity.thermalmodifier is None
    assert aedt_app.materials["vacuum"].conductivity.spatialmodifier is None

    aedt_app.materials["vacuum"].conductivity.thermalmodifier = "1"
    assert aedt_app.materials["vacuum"].conductivity.thermalmodifier == "1"
    aedt_app.materials["vacuum"].conductivity.spatialmodifier = "1"
    assert aedt_app.materials["vacuum"].conductivity.spatialmodifier == "1"

    aedt_app.materials["vacuum"].conductivity.thermalmodifier = None
    assert aedt_app.materials["vacuum"].conductivity.thermalmodifier is None
    aedt_app.materials["vacuum"].conductivity.thermalmodifier = "2"
    assert aedt_app.materials["vacuum"].conductivity.thermalmodifier == "2"

    aedt_app.materials["vacuum"].conductivity.spatialmodifier = None
    assert aedt_app.materials["vacuum"].conductivity.spatialmodifier is None
    aedt_app.materials["vacuum"].conductivity.spatialmodifier = "2"
    assert aedt_app.materials["vacuum"].conductivity.spatialmodifier == "2"

    aedt_app.materials["vacuum"].conductivity.thermalmodifier = None
    assert aedt_app.materials["vacuum"].conductivity.thermalmodifier is None
    aedt_app.materials["vacuum"].conductivity.spatialmodifier = None
    assert aedt_app.materials["vacuum"].conductivity.spatialmodifier is None

    aedt_app.materials["vacuum"].conductivity.thermalmodifier = "3"
    assert aedt_app.materials["vacuum"].conductivity.thermalmodifier == "3"
    aedt_app.materials["vacuum"].conductivity.spatialmodifier = "3"
    assert aedt_app.materials["vacuum"].conductivity.spatialmodifier == "3"

    aedt_app.materials["vacuum"].conductivity.thermalmodifier = None
    aedt_app.materials["vacuum"].conductivity.spatialmodifier = None
    aedt_app.materials["vacuum"].conductivity.thermalmodifier = "4"
    assert aedt_app.materials["vacuum"].conductivity.thermalmodifier == "4"
    aedt_app.materials["vacuum"].conductivity.spatialmodifier = "4"
    assert aedt_app.materials["vacuum"].conductivity.spatialmodifier == "4"

    aedt_app.materials["vacuum"].conductivity.thermalmodifier = None
    aedt_app.materials["vacuum"].conductivity.spatialmodifier = None


def test_import_materials_from_workbench(aedt_app):
    assert aedt_app.materials.import_materials_from_workbench("not_existing.xml") is False

    imported_mats = aedt_app.materials.import_materials_from_workbench(
        Path(TESTS_GENERAL_PATH) / "example_models" / TEST_SUBFOLDER / "EngineeringData1.xml"
    )
    for m in imported_mats:
        assert m in aedt_app.materials.material_keys.values()
    assert aedt_app.materials.material_keys["new_wb_material_aniso_wb"].permittivity.value == [1, 2, 3]
    assert aedt_app.materials.material_keys["new_wb_material_aniso_wb"].conductivity.value == [
        0.012987012987012988,
        0.011363636363636364,
        0.010101010101010102,
    ]
    assert aedt_app.materials.material_keys["structural_steel_wb"].permeability.value == 10000
    assert aedt_app.materials.material_keys["wb_material_simple_thermal_wb"].conductivity.value == 18
    assert (
        aedt_app.materials.material_keys["wb_material_simple_thermal_wb"].permittivity.thermalmodifier
        == "pwl($TM_WB_MATERIAL_SIMPLE_thermal_wb_permittivity, Temp)"
    )
    assert aedt_app.materials.material_keys["wb_material_simple_wb"].conductivity.value == 3
    assert aedt_app.materials.material_keys["wb_material_simple_wb"].thermal_expansion_coefficient.value == 23

    imported_mats = aedt_app.materials.import_materials_from_workbench(
        Path(TESTS_GENERAL_PATH) / "example_models" / TEST_SUBFOLDER / "EngineeringData2.xml"
    )
    for m in imported_mats:
        assert m in aedt_app.materials.material_keys.values()
    assert aedt_app.materials.material_keys["aluminum_alloy_wb"].conductivity.value == 41152263.3744856
    assert (
        aedt_app.materials.material_keys["aluminum_alloy_wb"].thermal_conductivity.thermalmodifier
        == "pwl($TM_Aluminum_Alloy_wb_thermal_conductivity, Temp)"
    )
    assert aedt_app.materials.material_keys["concrete_wb"].thermal_conductivity.value == 0.72
    assert aedt_app.materials.material_keys["fr_4_wb"].thermal_conductivity.value == [0.38, 0.38, 0.3]
    assert aedt_app.materials.material_keys["silicon_anisotropic_wb"].mass_density.value == 2330
    assert (
        aedt_app.materials.material_keys["silicon_anisotropic_wb"].thermal_expansion_coefficient.thermalmodifier
        == "pwl($TM_Silicon_Anisotropic_wb_thermal_expansion_coefficient, Temp)"
    )

    imported_mats = aedt_app.materials.import_materials_from_workbench(
        Path(TESTS_GENERAL_PATH) / "example_models" / TEST_SUBFOLDER / "EngineeringData3.xml",
        name_suffix="_imp",
    )
    for m in imported_mats:
        assert m in aedt_app.materials.material_keys.values()
    assert (
        aedt_app.materials.material_keys["84zn_12ag_4au_imp"].thermal_conductivity.thermalmodifier
        == "pwl($TM_84Zn_12Ag_4Au_imp_thermal_conductivity, Temp)"
    )
    assert (
        aedt_app.materials.material_keys["84zn_12ag_4au_imp"].mass_density.thermalmodifier
        == "pwl($TM_84Zn_12Ag_4Au_imp_mass_density, Temp)"
    )
    assert (
        aedt_app.materials.material_keys["84zn_12ag_4au_imp"].specific_heat.thermalmodifier
        == "pwl($TM_84Zn_12Ag_4Au_imp_specific_heat, Temp)"
    )
    assert (
        aedt_app.materials.material_keys["84zn_12ag_4au_imp"].youngs_modulus.thermalmodifier
        == "pwl($TM_84Zn_12Ag_4Au_imp_youngs_modulus, Temp)"
    )
    assert (
        aedt_app.materials.material_keys["84zn_12ag_4au_imp"].poissons_ratio.thermalmodifier
        == "pwl($TM_84Zn_12Ag_4Au_imp_poissons_ratio, Temp)"
    )
    assert (
        aedt_app.materials.material_keys["84zn_12ag_4au_imp"].thermal_expansion_coefficient.thermalmodifier
        == "pwl($TM_84Zn_12Ag_4Au_imp_thermal_expansion_coefficient, Temp)"
    )


@patch.object(
    builtins,
    "open",
    new_callable=mock_open,
    read_data=MISSING_RGB_MATERIALS,
)
def test_json_missing_rgb(mock_file, aedt_app, caplog):
    input_path = Path(TESTS_GENERAL_PATH) / "example_models" / TEST_SUBFOLDER / "mats.json"
    with pytest.raises(KeyError):
        aedt_app.materials.import_materials_from_file(input_path)
    assert [
        record
        for record in caplog.records
        if record.levelno == logging.ERROR
        and record.message == f"Failed to import material 'copper_5540' from {input_path!r}: key error on 'Red'"
    ]
