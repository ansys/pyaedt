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
from tests.conftest import config

test_subfolder = "T03"

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


@pytest.fixture()
def aedtapp(add_app):
    app = add_app(application=Hfss)
    yield app
    app.close_project(app.project_name)


@pytest.fixture()
def icepakapp(add_app):
    app = add_app(application=Icepak)
    yield app
    app.close_project(app.project_name)


@pytest.fixture()
def maxwellapp(add_app):
    app = add_app(application=Maxwell3d)
    yield app
    app.close_project(app.project_name)


def test_vacuum(aedtapp):
    assert "vacuum" in list(aedtapp.materials.material_keys.keys())


def test_create_material(aedtapp):
    mat1 = aedtapp.materials.add_material("new_copper2")
    assert mat1
    mat1.conductivity = 59000000000
    assert mat1.conductivity.value == 59000000000
    mat1.permeability.value = MatProperties.get_defaultvalue(aedtname="permeability")
    assert mat1.permeability.value == MatProperties.get_defaultvalue(aedtname="permeability")
    mat1.permeability.value = [[0, 0], [30, 40], [50, 60]]
    mat1.permeability.type == "nonlinear"
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
    assert aedtapp.change_validation_settings()
    assert aedtapp.change_validation_settings(ignore_unclassified=True, skip_intersections=True)

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


def test_create_modifiers(aedtapp):
    aedtapp.materials.add_material("new_copper")
    assert aedtapp.materials["new_copper"].mass_density.add_thermal_modifier_free_form(
        "if(Temp > 1000cel, 1, if(Temp < -273.15cel, 1, 1))"
    )
    assert aedtapp.materials["new_copper"].mass_density.add_thermal_modifier_closed_form()
    assert aedtapp.materials["new_copper"].mass_density.add_thermal_modifier_closed_form(auto_calc=False)
    assert aedtapp.materials["new_copper"].permittivity.add_thermal_modifier_closed_form()
    assert aedtapp.materials["new_copper"].permeability.add_thermal_modifier_closed_form(auto_calc=False)
    assert aedtapp.materials["new_copper"].permittivity.add_thermal_modifier_closed_form(auto_calc=False)
    filename = Path(TESTS_GENERAL_PATH) / "example_models" / test_subfolder / "ds_1d.tab"
    ds1 = aedtapp.import_dataset1d(filename)
    assert aedtapp.materials["new_copper"].permittivity.add_thermal_modifier_dataset(ds1.name)

    assert aedtapp.materials["new_copper"].mass_density.add_spatial_modifier_free_form(
        "if(X > 1mm, 1, if(X < 1mm, 2, 1))"
    )
    assert aedtapp.materials["new_copper"].mass_density.add_spatial_modifier_free_form(
        "if(X > 1mm, 1, if(X < 1mm, 3, 1))"
    )
    exp = aedtapp.materials["new_copper"].mass_density.spatialmodifier = "X+1"
    assert exp == "X+1"
    exp = aedtapp.materials["new_copper"].mass_density.spatialmodifier = ["Y+1"]
    assert exp == ["Y+1"]
    filename = Path(TESTS_GENERAL_PATH) / "example_models" / test_subfolder / "ds_3d.tab"
    ds2 = aedtapp.import_dataset3d(str(filename))
    assert aedtapp.materials["new_copper"].permeability.add_spatial_modifier_dataset(ds2.name)
    mat1 = aedtapp.materials.add_material("new_mat")
    mat1.mass_density.value == MatProperties.get_defaultvalue(aedtname="mass_density")
    mat1.permittivity.value == MatProperties.get_defaultvalue(aedtname="permittivity")
    assert aedtapp.materials["new_mat"].mass_density.add_spatial_modifier_free_form("if(X > 1mm, 1, if(X < 1mm, 3, 1))")
    assert aedtapp.materials["new_mat"].mass_density.add_thermal_modifier_free_form(
        "if(Temp > 1000cel, 1, if(Temp < -273.15cel, 1, 1))"
    )
    assert aedtapp.materials["new_mat"].permittivity.add_thermal_modifier_free_form("X^2")
    mat1 = aedtapp.materials.add_material("new_mat2")
    mat1.mass_density.value == MatProperties.get_defaultvalue(aedtname="mass_density")
    assert aedtapp.materials["new_mat2"].mass_density.add_spatial_modifier_free_form(
        "if(X > 1mm, 1, if(X < 1mm, 3, 1))"
    )
    assert aedtapp.materials["new_mat2"].mass_density.add_thermal_modifier_closed_form()
    mat1 = aedtapp.materials.add_material("new_mat3")
    mat1.mass_density.value == MatProperties.get_defaultvalue(aedtname="mass_density")
    assert aedtapp.materials["new_mat3"].mass_density.add_thermal_modifier_closed_form()


def test_duplicate_material(aedtapp):
    aedtapp.materials.add_material("copper")
    assert aedtapp.materials.duplicate_material("copper", "copper2")
    assert not aedtapp.materials.duplicate_material("nonexistent_copper", "copper2")


def test_delete_material(aedtapp):
    aedtapp.materials.add_material("copper")
    assert aedtapp.materials.remove_material("copper")
    assert not aedtapp.materials.remove_material("copper2")


def test_surface_material(icepakapp):
    mat2 = icepakapp.materials.add_surface_material("Steel")
    mat2.emissivity.value = SurfMatProperties.get_defaultvalue(aedtname="surface_emissivity")
    mat2.surface_diffuse_absorptance.value = SurfMatProperties.get_defaultvalue(aedtname="surface_diffuse_absorptance")
    mat2.surface_roughness.value = SurfMatProperties.get_defaultvalue(aedtname="surface_roughness")

    assert mat2.emissivity.value == SurfMatProperties.get_defaultvalue(aedtname="surface_emissivity")
    assert mat2.coordinate_system
    assert mat2.surface_diffuse_absorptance.value == SurfMatProperties.get_defaultvalue(
        aedtname="surface_diffuse_absorptance"
    )
    assert mat2.surface_roughness.value == SurfMatProperties.get_defaultvalue(aedtname="surface_roughness")
    assert icepakapp.materials.duplicate_surface_material("Steel", "Steel2")
    assert not icepakapp.materials.duplicate_surface_material("Steel4", "Steel2")
    assert icepakapp.materials.duplicate_surface_material("Steel")


def test_export_materials(aedtapp, local_scratch):
    assert aedtapp.materials.export_materials_to_file(Path(local_scratch.path) / "materials.json")
    assert (Path(local_scratch.path) / "materials.json").exists()


def test_import_materials(aedtapp):
    assert aedtapp.materials.import_materials_from_file(
        Path(TESTS_GENERAL_PATH) / "example_models" / test_subfolder / "mats.json"
    )
    assert "$copper_ds1" in aedtapp.project_datasets.keys()
    assert "copper_5540" in aedtapp.materials.material_keys.keys()
    assert "al-extruded1" in aedtapp.materials.material_keys.keys()
    assert aedtapp.materials["al-extruded1"].thermal_conductivity.thermalmodifier

    assert not aedtapp.materials.import_materials_from_file()
    assert not aedtapp.materials.import_materials_from_file("mat.invented")
    assert not aedtapp.materials.import_materials_from_file(
        Path(TESTS_GENERAL_PATH) / "example_models" / test_subfolder / "mats.csv"
    )

    assert aedtapp.materials.import_materials_from_file(
        Path(TESTS_GENERAL_PATH) / "example_models" / test_subfolder / "material_sample.amat"
    )
    assert aedtapp.materials.import_materials_from_file(
        Path(TESTS_GENERAL_PATH) / "example_models" / test_subfolder / "iron_pyaedt.amat"
    )


def test_import_materials_from_excel(aedtapp):
    mats = aedtapp.materials.import_materials_from_excel(
        Path(TESTS_GENERAL_PATH) / "example_models" / test_subfolder / "mats.xlsx"
    )
    assert len(mats) == 2
    assert mats[0].conductivity.value == 5700000
    assert mats[0].permittivity.value == 0.5
    assert mats[0].name == "aluminum_2"
    mats = aedtapp.materials.import_materials_from_excel(
        Path(TESTS_GENERAL_PATH) / "example_models" / test_subfolder / "mats.csv"
    )
    assert len(mats) == 2


def test_non_linear_materials(maxwellapp, local_scratch):
    mat1 = maxwellapp.materials.add_material("myMat")
    mat1.permeability = [[0, 0], [1, 12], [10, 30]]
    mat1.permeability.set_non_linear(x_unit="Oe", y_unit="gauss")
    mat1.permittivity = [[0, 0], [2, 12], [10, 30]]
    mat1.conductivity.value = [[0, 0], [3, 12], [10, 30]]
    maxwellapp.materials.export_materials_to_file(Path(local_scratch.path) / "non_linear.json")
    (Path(local_scratch.path) / "non_linear.json").exists()
    maxwellapp.materials.remove_material("myMat")
    maxwellapp.materials.import_materials_from_file(Path(local_scratch.path) / "non_linear.json")
    assert maxwellapp.materials["myMat"].permeability.value == [[0, 0], [1, 12], [10, 30]]
    assert maxwellapp.materials["myMat"].permittivity.value == [[0, 0], [2, 12], [10, 30]]
    assert maxwellapp.materials["myMat"].conductivity.value == [[0, 0], [3, 12], [10, 30]]
    assert maxwellapp.materials["myMat"].permeability.type == "nonlinear"
    assert maxwellapp.materials["myMat"].conductivity.type == "nonlinear"
    assert maxwellapp.materials["myMat"].permittivity.type == "nonlinear"
    assert maxwellapp.materials["myMat"].permeability.bunit == "tesla"
    assert maxwellapp.materials["myMat"].permeability.hunit == "A_per_meter"
    mat2 = maxwellapp.materials.add_material("myMat2")
    assert not mat2.is_used
    assert maxwellapp.modeler.create_box([0, 0, 0], [10, 10, 10], material="myMat2")
    assert maxwellapp.materials.material_keys["mymat2"].is_used


def test_add_material_sweep(aedtapp):
    material_name = "sweep_material"
    assert aedtapp.materials.add_material_sweep(["copper", "aluminum", "FR4_epoxy"], material_name)
    assert material_name in list(aedtapp.materials.material_keys.keys())
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
    assert "$ID" + material_name in aedtapp.variable_manager.variable_names
    for prop in properties_to_check:
        var_name = "$" + material_name + "_" + prop
        assert var_name in aedtapp.variable_manager.variable_names
    # check if the material properties are correct
    for prop in properties_to_check:
        var_name = "$" + material_name + "_" + prop
        mat_prop = getattr(aedtapp.materials[material_name], prop).value
        assert mat_prop == var_name + "[$ID" + material_name + "]"


def test_material_case(aedtapp):
    assert aedtapp.materials["Aluminum"] == aedtapp.materials["aluminum"]
    assert aedtapp.materials["Aluminum"].name == "aluminum"
    assert aedtapp.materials.add_material("AluMinum") == aedtapp.materials["aluminum"]


def test_material_model(aedtapp):
    mat = aedtapp.materials.add_material("ds_material")
    aedtapp["$dk"] = 3
    aedtapp["$df"] = 0.01
    assert mat.set_djordjevic_sarkar_model(dk="$dk", df="$df")


@pytest.mark.skipif(not config["use_grpc"], reason="Not running in COM mode")
def test_get_materials_in_project(aedtapp):
    used_materials = aedtapp.materials.get_used_project_material_names()
    assert isinstance(used_materials, list)
    for m in [mat for mat in aedtapp.materials if mat.is_used]:
        assert m.name in used_materials


def test_get_coreloss_coefficients(aedtapp):
    aedtapp.materials.add_material("mat_test")
    # Test points_list_at_freq
    coeff = aedtapp.materials["mat_test"].get_core_loss_coefficients(
        points_at_frequency={60: [[0, 0], [1, 3.5], [2, 7.4]]}
    )
    assert isinstance(coeff, list)
    assert len(coeff) == 3
    assert all(isinstance(c, float) for c in coeff)
    coeff = aedtapp.materials["mat_test"].get_core_loss_coefficients(
        points_at_frequency={"60Hz": [[0, 0], [1, 3.5], [2, 7.4]]}
    )
    assert isinstance(coeff, list)
    assert len(coeff) == 3
    assert all(isinstance(c, float) for c in coeff)
    coeff = aedtapp.materials["mat_test"].get_core_loss_coefficients(
        points_at_frequency={"0.06kHz": [[0, 0], [1, 3.5], [2, 7.4]]}
    )
    assert isinstance(coeff, list)
    assert len(coeff) == 3
    assert all(isinstance(c, float) for c in coeff)
    with pytest.raises(TypeError):
        aedtapp.materials["mat_test"].get_core_loss_coefficients(points_at_frequency=[[0, 0], [1, 3.5], [2, 7.4]])
    coeff = aedtapp.materials["mat_test"].get_core_loss_coefficients(
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
    coeff = aedtapp.materials["mat_test"].get_core_loss_coefficients(
        points_at_frequency={60: [[0, 0], [1, 3.5], [2, 7.4]]}, thickness="0.6mm"
    )
    assert isinstance(coeff, list)
    assert len(coeff) == 3
    assert all(isinstance(c, float) for c in coeff)
    with pytest.raises(TypeError):
        aedtapp.materials["mat_test"].get_core_loss_coefficients(
            points_at_frequency={60: [[0, 0], [1, 3.5], [2, 7.4]]}, thickness="invalid"
        )
    with pytest.raises(TypeError):
        aedtapp.materials["mat_test"].get_core_loss_coefficients(
            points_at_frequency={60: [[0, 0], [1, 3.5], [2, 7.4]]}, thickness=50
        )


def test_set_core_loss(aedtapp):
    aedtapp.materials.add_material("mat_test")
    # Test points_list_at_freq
    assert aedtapp.materials["mat_test"].set_coreloss_at_frequency(
        points_at_frequency={60: [[0, 0], [1, 3.5], [2, 7.4]]}
    )
    assert aedtapp.materials["mat_test"].set_coreloss_at_frequency(
        points_at_frequency={"60Hz": [[0, 0], [1, 3.5], [2, 7.4]]}
    )
    assert aedtapp.materials["mat_test"].set_coreloss_at_frequency(
        points_at_frequency={"0.06kHz": [[0, 0], [1, 3.5], [2, 7.4]]}
    )
    with pytest.raises(TypeError):
        aedtapp.materials["mat_test"].set_coreloss_at_frequency(points_at_frequency=[[0, 0], [1, 3.5], [2, 7.4]])
    assert aedtapp.materials["mat_test"].set_coreloss_at_frequency(
        points_at_frequency={
            60: [[0, 0], [1, 3.5], [2, 7.4]],
            100: [[0, 0], [1, 8], [2, 9]],
            150: [[0, 0], [1, 10], [2, 19]],
        }
    )
    assert aedtapp.materials["mat_test"].set_coreloss_at_frequency(
        points_at_frequency={
            60: [[0, 0], [1, 3.5], [2, 7.4]],
            100: [[0, 0], [1, 8], [2, 9]],
            150: [[0, 0], [1, 10], [2, 19]],
        },
        core_loss_model_type="Power Ferrite",
    )
    with pytest.raises(ValueError):
        aedtapp.materials["mat_test"].set_coreloss_at_frequency(
            points_at_frequency={80: [[0, 0], [1, 3.5], [2, 7.4]]}, core_loss_model_type="Power Ferrite"
        )
    # Test thickness
    assert aedtapp.materials["mat_test"].set_coreloss_at_frequency(
        points_at_frequency={60: [[0, 0], [1, 3.5], [2, 7.4]]}, thickness="0.6mm"
    )
    with pytest.raises(TypeError):
        aedtapp.materials["mat_test"].set_coreloss_at_frequency(
            points_at_frequency={60: [[0, 0], [1, 3.5], [2, 7.4]]}, thickness="invalid"
        )
    with pytest.raises(TypeError):
        aedtapp.materials["mat_test"].set_coreloss_at_frequency(
            points_at_frequency={60: [[0, 0], [1, 3.5], [2, 7.4]]}, thickness=50
        )


def test_thermalmodifier_and_spatialmodifier(aedtapp):
    assert aedtapp.materials["vacuum"].conductivity.thermalmodifier is None
    assert aedtapp.materials["vacuum"].conductivity.spatialmodifier is None

    aedtapp.materials["vacuum"].conductivity.thermalmodifier = "1"
    assert aedtapp.materials["vacuum"].conductivity.thermalmodifier == "1"
    aedtapp.materials["vacuum"].conductivity.spatialmodifier = "1"
    assert aedtapp.materials["vacuum"].conductivity.spatialmodifier == "1"

    aedtapp.materials["vacuum"].conductivity.thermalmodifier = None
    assert aedtapp.materials["vacuum"].conductivity.thermalmodifier is None
    aedtapp.materials["vacuum"].conductivity.thermalmodifier = "2"
    assert aedtapp.materials["vacuum"].conductivity.thermalmodifier == "2"

    aedtapp.materials["vacuum"].conductivity.spatialmodifier = None
    assert aedtapp.materials["vacuum"].conductivity.spatialmodifier is None
    aedtapp.materials["vacuum"].conductivity.spatialmodifier = "2"
    assert aedtapp.materials["vacuum"].conductivity.spatialmodifier == "2"

    aedtapp.materials["vacuum"].conductivity.thermalmodifier = None
    assert aedtapp.materials["vacuum"].conductivity.thermalmodifier is None
    aedtapp.materials["vacuum"].conductivity.spatialmodifier = None
    assert aedtapp.materials["vacuum"].conductivity.spatialmodifier is None

    aedtapp.materials["vacuum"].conductivity.thermalmodifier = "3"
    assert aedtapp.materials["vacuum"].conductivity.thermalmodifier == "3"
    aedtapp.materials["vacuum"].conductivity.spatialmodifier = "3"
    assert aedtapp.materials["vacuum"].conductivity.spatialmodifier == "3"

    aedtapp.materials["vacuum"].conductivity.thermalmodifier = None
    aedtapp.materials["vacuum"].conductivity.spatialmodifier = None
    aedtapp.materials["vacuum"].conductivity.thermalmodifier = "4"
    assert aedtapp.materials["vacuum"].conductivity.thermalmodifier == "4"
    aedtapp.materials["vacuum"].conductivity.spatialmodifier = "4"
    assert aedtapp.materials["vacuum"].conductivity.spatialmodifier == "4"

    aedtapp.materials["vacuum"].conductivity.thermalmodifier = None
    aedtapp.materials["vacuum"].conductivity.spatialmodifier = None


def test_import_materials_from_workbench(aedtapp):
    assert aedtapp.materials.import_materials_from_workbench("not_existing.xml") is False

    imported_mats = aedtapp.materials.import_materials_from_workbench(
        Path(TESTS_GENERAL_PATH) / "example_models" / test_subfolder / "EngineeringData1.xml"
    )
    for m in imported_mats:
        assert m in aedtapp.materials.material_keys.values()
    assert aedtapp.materials.material_keys["new_wb_material_aniso_wb"].permittivity.value == [1, 2, 3]
    assert aedtapp.materials.material_keys["new_wb_material_aniso_wb"].conductivity.value == [
        0.012987012987012988,
        0.011363636363636364,
        0.010101010101010102,
    ]
    assert aedtapp.materials.material_keys["structural_steel_wb"].permeability.value == 10000
    assert aedtapp.materials.material_keys["wb_material_simple_thermal_wb"].conductivity.value == 18
    assert (
        aedtapp.materials.material_keys["wb_material_simple_thermal_wb"].permittivity.thermalmodifier
        == "pwl($TM_WB_MATERIAL_SIMPLE_thermal_wb_permittivity, Temp)"
    )
    assert aedtapp.materials.material_keys["wb_material_simple_wb"].conductivity.value == 3
    assert aedtapp.materials.material_keys["wb_material_simple_wb"].thermal_expansion_coefficient.value == 23

    imported_mats = aedtapp.materials.import_materials_from_workbench(
        Path(TESTS_GENERAL_PATH) / "example_models" / test_subfolder / "EngineeringData2.xml"
    )
    for m in imported_mats:
        assert m in aedtapp.materials.material_keys.values()
    assert aedtapp.materials.material_keys["aluminum_alloy_wb"].conductivity.value == 41152263.3744856
    assert (
        aedtapp.materials.material_keys["aluminum_alloy_wb"].thermal_conductivity.thermalmodifier
        == "pwl($TM_Aluminum_Alloy_wb_thermal_conductivity, Temp)"
    )
    assert aedtapp.materials.material_keys["concrete_wb"].thermal_conductivity.value == 0.72
    assert aedtapp.materials.material_keys["fr_4_wb"].thermal_conductivity.value == [0.38, 0.38, 0.3]
    assert aedtapp.materials.material_keys["silicon_anisotropic_wb"].mass_density.value == 2330
    assert (
        aedtapp.materials.material_keys["silicon_anisotropic_wb"].thermal_expansion_coefficient.thermalmodifier
        == "pwl($TM_Silicon_Anisotropic_wb_thermal_expansion_coefficient, Temp)"
    )

    imported_mats = aedtapp.materials.import_materials_from_workbench(
        Path(TESTS_GENERAL_PATH) / "example_models" / test_subfolder / "EngineeringData3.xml",
        name_suffix="_imp",
    )
    for m in imported_mats:
        assert m in aedtapp.materials.material_keys.values()
    assert (
        aedtapp.materials.material_keys["84zn_12ag_4au_imp"].thermal_conductivity.thermalmodifier
        == "pwl($TM_84Zn_12Ag_4Au_imp_thermal_conductivity, Temp)"
    )
    assert (
        aedtapp.materials.material_keys["84zn_12ag_4au_imp"].mass_density.thermalmodifier
        == "pwl($TM_84Zn_12Ag_4Au_imp_mass_density, Temp)"
    )
    assert (
        aedtapp.materials.material_keys["84zn_12ag_4au_imp"].specific_heat.thermalmodifier
        == "pwl($TM_84Zn_12Ag_4Au_imp_specific_heat, Temp)"
    )
    assert (
        aedtapp.materials.material_keys["84zn_12ag_4au_imp"].youngs_modulus.thermalmodifier
        == "pwl($TM_84Zn_12Ag_4Au_imp_youngs_modulus, Temp)"
    )
    assert (
        aedtapp.materials.material_keys["84zn_12ag_4au_imp"].poissons_ratio.thermalmodifier
        == "pwl($TM_84Zn_12Ag_4Au_imp_poissons_ratio, Temp)"
    )
    assert (
        aedtapp.materials.material_keys["84zn_12ag_4au_imp"].thermal_expansion_coefficient.thermalmodifier
        == "pwl($TM_84Zn_12Ag_4Au_imp_thermal_expansion_coefficient, Temp)"
    )


@patch.object(
    builtins,
    "open",
    new_callable=mock_open,
    read_data=MISSING_RGB_MATERIALS,
)
def test_json_missing_rgb(mock_file, aedtapp, caplog):
    input_path = Path(TESTS_GENERAL_PATH) / "example_models" / test_subfolder / "mats.json"
    with pytest.raises(KeyError):
        aedtapp.materials.import_materials_from_file(input_path)
    assert [
        record
        for record in caplog.records
        if record.levelno == logging.ERROR
        and record.message == (f"Failed to import material 'copper_5540' from {input_path!r}: key error on 'Red'")
    ]
