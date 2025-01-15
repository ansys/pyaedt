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
import os
from unittest.mock import mock_open

from ansys.aedt.core import Icepak
from ansys.aedt.core import Maxwell3d
from ansys.aedt.core.modules.material import MatProperties
from ansys.aedt.core.modules.material import SurfMatProperties
from mock import patch
import pytest

from tests import TESTS_GENERAL_PATH
from tests.system.general.conftest import config

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


@pytest.fixture(scope="class")
def aedtapp(add_app):
    app = add_app(project_name="Test03")
    return app


@pytest.fixture(scope="class")
def aedtapp2(add_app):
    app = add_app(project_name="Test03", design_name="import_from_wb")
    return app


class TestClass:
    @pytest.fixture(autouse=True)
    def init(self, aedtapp, aedtapp2, local_scratch):
        self.aedtapp = aedtapp
        self.testapp2 = aedtapp2
        self.local_scratch = local_scratch

    def test_01_vaacum(self):
        assert "vacuum" in list(self.aedtapp.materials.material_keys.keys())

    def test_02_create_material(self):
        mat1 = self.aedtapp.materials.add_material("new_copper2")
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
        assert self.aedtapp.change_validation_settings()
        assert self.aedtapp.change_validation_settings(ignore_unclassified=True, skip_intersections=True)

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

    def test_03_create_modifiers(self):
        assert self.aedtapp.materials["new_copper2"].mass_density.add_thermal_modifier_free_form(
            "if(Temp > 1000cel, 1, if(Temp < -273.15cel, 1, 1))"
        )
        assert self.aedtapp.materials["new_copper2"].mass_density.add_thermal_modifier_closed_form()
        assert self.aedtapp.materials["new_copper2"].mass_density.add_thermal_modifier_closed_form(auto_calc=False)
        assert self.aedtapp.materials["new_copper2"].permittivity.add_thermal_modifier_closed_form()
        assert self.aedtapp.materials["new_copper2"].permeability.add_thermal_modifier_closed_form(auto_calc=False)
        assert self.aedtapp.materials["new_copper2"].permittivity.add_thermal_modifier_closed_form(auto_calc=False)
        filename = os.path.join(TESTS_GENERAL_PATH, "example_models", test_subfolder, "ds_1d.tab")
        ds1 = self.aedtapp.import_dataset1d(filename)
        assert self.aedtapp.materials["new_copper2"].permittivity.add_thermal_modifier_dataset(ds1.name)

        assert self.aedtapp.materials["new_copper2"].mass_density.add_spatial_modifier_free_form(
            "if(X > 1mm, 1, if(X < 1mm, 2, 1))"
        )
        assert self.aedtapp.materials["new_copper2"].mass_density.add_spatial_modifier_free_form(
            "if(X > 1mm, 1, if(X < 1mm, 3, 1))"
        )
        exp = self.aedtapp.materials["new_copper2"].mass_density.spatialmodifier = "X+1"
        assert exp == "X+1"
        exp = self.aedtapp.materials["new_copper2"].mass_density.spatialmodifier = ["Y+1"]
        assert exp == ["Y+1"]
        filename = os.path.join(TESTS_GENERAL_PATH, "example_models", test_subfolder, "ds_3d.tab")
        ds2 = self.aedtapp.import_dataset3d(filename)
        assert self.aedtapp.materials["new_copper2"].permeability.add_spatial_modifier_dataset(ds2.name)
        mat1 = self.aedtapp.materials.add_material("new_mat")
        mat1.mass_density.value == MatProperties.get_defaultvalue(aedtname="mass_density")
        mat1.permittivity.value == MatProperties.get_defaultvalue(aedtname="permittivity")
        assert self.aedtapp.materials["new_mat"].mass_density.add_spatial_modifier_free_form(
            "if(X > 1mm, 1, if(X < 1mm, 3, 1))"
        )
        assert self.aedtapp.materials["new_mat"].mass_density.add_thermal_modifier_free_form(
            "if(Temp > 1000cel, 1, if(Temp < -273.15cel, 1, 1))"
        )
        assert self.aedtapp.materials["new_mat"].permittivity.add_thermal_modifier_free_form("X^2")
        mat1 = self.aedtapp.materials.add_material("new_mat2")
        mat1.mass_density.value == MatProperties.get_defaultvalue(aedtname="mass_density")
        assert self.aedtapp.materials["new_mat2"].mass_density.add_spatial_modifier_free_form(
            "if(X > 1mm, 1, if(X < 1mm, 3, 1))"
        )
        assert self.aedtapp.materials["new_mat2"].mass_density.add_thermal_modifier_closed_form()
        mat1 = self.aedtapp.materials.add_material("new_mat3")
        mat1.mass_density.value == MatProperties.get_defaultvalue(aedtname="mass_density")
        assert self.aedtapp.materials["new_mat3"].mass_density.add_thermal_modifier_closed_form()

    def test_04_duplicate_material(self):
        assert self.aedtapp.materials.duplicate_material("new_copper2", "copper3")
        assert not self.aedtapp.materials.duplicate_material("new_copper3", "copper3")

    def test_05_delete_material(self):
        assert self.aedtapp.materials.remove_material("copper3")
        assert not self.aedtapp.materials.remove_material("copper4")

    def test_06_surface_material(self, add_app):
        ipk = add_app(application=Icepak)
        mat2 = ipk.materials.add_surface_material("Steel")
        mat2.emissivity.value = SurfMatProperties.get_defaultvalue(aedtname="surface_emissivity")
        mat2.surface_diffuse_absorptance.value = SurfMatProperties.get_defaultvalue(
            aedtname="surface_diffuse_absorptance"
        )
        mat2.surface_roughness.value = SurfMatProperties.get_defaultvalue(aedtname="surface_roughness")

        assert mat2.emissivity.value == SurfMatProperties.get_defaultvalue(aedtname="surface_emissivity")
        assert mat2.coordinate_system
        assert mat2.surface_diffuse_absorptance.value == SurfMatProperties.get_defaultvalue(
            aedtname="surface_diffuse_absorptance"
        )
        assert mat2.surface_roughness.value == SurfMatProperties.get_defaultvalue(aedtname="surface_roughness")
        assert ipk.materials.duplicate_surface_material("Steel", "Steel2")
        assert not ipk.materials.duplicate_surface_material("Steel4", "Steel2")
        assert ipk.materials.duplicate_surface_material("Steel")

    def test_07_export_materials(self):
        assert self.aedtapp.materials.export_materials_to_file(os.path.join(self.local_scratch.path, "materials.json"))
        assert os.path.exists(os.path.join(self.local_scratch.path, "materials.json"))

    def test_08_import_materials(self):
        assert self.aedtapp.materials.import_materials_from_file(
            os.path.join(TESTS_GENERAL_PATH, "example_models", test_subfolder, "mats.json")
        )
        assert "$copper_ds1" in self.aedtapp.project_datasets.keys()
        assert "copper_5540" in self.aedtapp.materials.material_keys.keys()
        assert "al-extruded1" in self.aedtapp.materials.material_keys.keys()
        assert self.aedtapp.materials["al-extruded1"].thermal_conductivity.thermalmodifier

        assert not self.aedtapp.materials.import_materials_from_file()
        assert not self.aedtapp.materials.import_materials_from_file("mat.invented")
        assert not self.aedtapp.materials.import_materials_from_file(
            os.path.join(TESTS_GENERAL_PATH, "example_models", test_subfolder, "mats.csv")
        )

        assert self.aedtapp.materials.import_materials_from_file(
            os.path.join(TESTS_GENERAL_PATH, "example_models", test_subfolder, "material_sample.amat")
        )
        assert self.aedtapp.materials.import_materials_from_file(
            os.path.join(TESTS_GENERAL_PATH, "example_models", test_subfolder, "iron_pyaedt.amat")
        )
        x = 1

    def test_08B_import_materials_from_excel(self):
        mats = self.aedtapp.materials.import_materials_from_excel(
            os.path.join(TESTS_GENERAL_PATH, "example_models", test_subfolder, "mats.xlsx")
        )
        assert len(mats) == 2
        assert mats[0].conductivity.value == 5700000
        assert mats[0].permittivity.value == 0.5
        assert mats[0].name == "aluminum_2"
        mats = self.aedtapp.materials.import_materials_from_excel(
            os.path.join(TESTS_GENERAL_PATH, "example_models", test_subfolder, "mats.csv")
        )
        assert len(mats) == 2

    def test_09_non_linear_materials(self, add_app):
        app = add_app(application=Maxwell3d, solution_type="Transient")
        mat1 = app.materials.add_material("myMat")
        mat1.permeability = [[0, 0], [1, 12], [10, 30]]
        mat1.permittivity = [[0, 0], [2, 12], [10, 30]]
        mat1.conductivity.value = [[0, 0], [3, 12], [10, 30]]
        app.materials.export_materials_to_file(os.path.join(self.local_scratch.path, "non_linear.json"))
        os.path.exists(os.path.join(self.local_scratch.path, "non_linear.json"))
        app.materials.remove_material("myMat")
        app.materials.import_materials_from_file(os.path.join(self.local_scratch.path, "non_linear.json"))
        assert app.materials["myMat"].permeability.value == [[0, 0], [1, 12], [10, 30]]
        assert app.materials["myMat"].permittivity.value == [[0, 0], [2, 12], [10, 30]]
        assert app.materials["myMat"].conductivity.value == [[0, 0], [3, 12], [10, 30]]
        assert app.materials["myMat"].permeability.type == "nonlinear"
        assert app.materials["myMat"].conductivity.type == "nonlinear"
        assert app.materials["myMat"].permittivity.type == "nonlinear"
        assert app.materials["myMat"].permeability.bunit == "tesla"
        mat2 = app.materials.add_material("myMat2")
        assert not mat2.is_used
        assert app.modeler.create_box([0, 0, 0], [10, 10, 10], material="myMat2")
        assert app.materials.material_keys["mymat2"].is_used

    def test_10_add_material_sweep(self):
        material_name = "sweep_material"
        assert self.aedtapp.materials.add_material_sweep(["copper", "aluminum", "FR4_epoxy"], material_name)
        assert material_name in list(self.aedtapp.materials.material_keys.keys())
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
        assert "$ID" + material_name in self.aedtapp.variable_manager.variable_names
        for prop in properties_to_check:
            var_name = "$" + material_name + "_" + prop
            assert var_name in self.aedtapp.variable_manager.variable_names
        # check if the material properties are correct
        for prop in properties_to_check:
            var_name = "$" + material_name + "_" + prop
            mat_prop = getattr(self.aedtapp.materials[material_name], prop).value
            assert mat_prop == var_name + "[$ID" + material_name + "]"

    def test_11_material_case(self):
        assert self.aedtapp.materials["Aluminum"] == self.aedtapp.materials["aluminum"]
        assert self.aedtapp.materials["Aluminum"].name == "aluminum"
        assert self.aedtapp.materials.add_material("AluMinum") == self.aedtapp.materials["aluminum"]

    def test_12_material_model(self):
        mat = self.aedtapp.materials.add_material("ds_material")
        self.aedtapp["$dk"] = 3
        self.aedtapp["$df"] = 0.01
        assert mat.set_djordjevic_sarkar_model(dk="$dk", df="$df")

    @pytest.mark.skipif(not config["use_grpc"], reason="Not running in COM mode")
    def test_13_get_materials_in_project(self):
        used_materials = self.aedtapp.materials.get_used_project_material_names()
        assert isinstance(used_materials, list)
        for m in [mat for mat in self.aedtapp.materials if mat.is_used]:
            assert m.name in used_materials

    def test_14_get_coreloss_coefficients(self):
        mat = self.aedtapp.materials.add_material("mat_test")
        # Test points_list_at_freq
        coeff = self.aedtapp.materials["mat_test"].get_core_loss_coefficients(
            points_at_frequency={60: [[0, 0], [1, 3.5], [2, 7.4]]}
        )
        assert isinstance(coeff, list)
        assert len(coeff) == 3
        assert all(isinstance(c, float) for c in coeff)
        coeff = self.aedtapp.materials["mat_test"].get_core_loss_coefficients(
            points_at_frequency={"60Hz": [[0, 0], [1, 3.5], [2, 7.4]]}
        )
        assert isinstance(coeff, list)
        assert len(coeff) == 3
        assert all(isinstance(c, float) for c in coeff)
        coeff = self.aedtapp.materials["mat_test"].get_core_loss_coefficients(
            points_at_frequency={"0.06kHz": [[0, 0], [1, 3.5], [2, 7.4]]}
        )
        assert isinstance(coeff, list)
        assert len(coeff) == 3
        assert all(isinstance(c, float) for c in coeff)
        with pytest.raises(TypeError):
            self.aedtapp.materials["mat_test"].get_core_loss_coefficients(
                points_at_frequency=[[0, 0], [1, 3.5], [2, 7.4]]
            )
        coeff = self.aedtapp.materials["mat_test"].get_core_loss_coefficients(
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
        coeff = self.aedtapp.materials["mat_test"].get_core_loss_coefficients(
            points_at_frequency={60: [[0, 0], [1, 3.5], [2, 7.4]]}, thickness="0.6mm"
        )
        assert isinstance(coeff, list)
        assert len(coeff) == 3
        assert all(isinstance(c, float) for c in coeff)
        with pytest.raises(TypeError):
            self.aedtapp.materials["mat_test"].get_core_loss_coefficients(
                points_at_frequency={60: [[0, 0], [1, 3.5], [2, 7.4]]}, thickness="invalid"
            )
        with pytest.raises(TypeError):
            self.aedtapp.materials["mat_test"].get_core_loss_coefficients(
                points_at_frequency={60: [[0, 0], [1, 3.5], [2, 7.4]]}, thickness=50
            )

    def test_14_set_core_loss(self):
        mat = self.aedtapp.materials["mat_test"]
        # Test points_list_at_freq
        assert self.aedtapp.materials["mat_test"].set_coreloss_at_frequency(
            points_at_frequency={60: [[0, 0], [1, 3.5], [2, 7.4]]}
        )
        assert self.aedtapp.materials["mat_test"].set_coreloss_at_frequency(
            points_at_frequency={"60Hz": [[0, 0], [1, 3.5], [2, 7.4]]}
        )
        assert self.aedtapp.materials["mat_test"].set_coreloss_at_frequency(
            points_at_frequency={"0.06kHz": [[0, 0], [1, 3.5], [2, 7.4]]}
        )
        with pytest.raises(TypeError):
            self.aedtapp.materials["mat_test"].set_coreloss_at_frequency(
                points_at_frequency=[[0, 0], [1, 3.5], [2, 7.4]]
            )
        assert self.aedtapp.materials["mat_test"].set_coreloss_at_frequency(
            points_at_frequency={
                60: [[0, 0], [1, 3.5], [2, 7.4]],
                100: [[0, 0], [1, 8], [2, 9]],
                150: [[0, 0], [1, 10], [2, 19]],
            }
        )
        assert self.aedtapp.materials["mat_test"].set_coreloss_at_frequency(
            points_at_frequency={
                60: [[0, 0], [1, 3.5], [2, 7.4]],
                100: [[0, 0], [1, 8], [2, 9]],
                150: [[0, 0], [1, 10], [2, 19]],
            },
            core_loss_model_type="Power Ferrite",
        )
        with pytest.raises(ValueError):
            self.aedtapp.materials["mat_test"].set_coreloss_at_frequency(
                points_at_frequency={80: [[0, 0], [1, 3.5], [2, 7.4]]}, core_loss_model_type="Power Ferrite"
            )
        # Test thickness
        assert self.aedtapp.materials["mat_test"].set_coreloss_at_frequency(
            points_at_frequency={60: [[0, 0], [1, 3.5], [2, 7.4]]}, thickness="0.6mm"
        )
        with pytest.raises(TypeError):
            self.aedtapp.materials["mat_test"].set_coreloss_at_frequency(
                points_at_frequency={60: [[0, 0], [1, 3.5], [2, 7.4]]}, thickness="invalid"
            )
        with pytest.raises(TypeError):
            self.aedtapp.materials["mat_test"].set_coreloss_at_frequency(
                points_at_frequency={60: [[0, 0], [1, 3.5], [2, 7.4]]}, thickness=50
            )

    def test_15_thermalmodifier_and_spatialmodifier(self):
        assert self.aedtapp.materials["vacuum"].conductivity.thermalmodifier is None
        assert self.aedtapp.materials["vacuum"].conductivity.spatialmodifier is None

        self.aedtapp.materials["vacuum"].conductivity.thermalmodifier = "1"
        assert self.aedtapp.materials["vacuum"].conductivity.thermalmodifier == "1"
        self.aedtapp.materials["vacuum"].conductivity.spatialmodifier = "1"
        assert self.aedtapp.materials["vacuum"].conductivity.spatialmodifier == "1"

        self.aedtapp.materials["vacuum"].conductivity.thermalmodifier = None
        assert self.aedtapp.materials["vacuum"].conductivity.thermalmodifier is None
        self.aedtapp.materials["vacuum"].conductivity.thermalmodifier = "2"
        assert self.aedtapp.materials["vacuum"].conductivity.thermalmodifier == "2"

        self.aedtapp.materials["vacuum"].conductivity.spatialmodifier = None
        assert self.aedtapp.materials["vacuum"].conductivity.spatialmodifier is None
        self.aedtapp.materials["vacuum"].conductivity.spatialmodifier = "2"
        assert self.aedtapp.materials["vacuum"].conductivity.spatialmodifier == "2"

        self.aedtapp.materials["vacuum"].conductivity.thermalmodifier = None
        assert self.aedtapp.materials["vacuum"].conductivity.thermalmodifier is None
        self.aedtapp.materials["vacuum"].conductivity.spatialmodifier = None
        assert self.aedtapp.materials["vacuum"].conductivity.spatialmodifier is None

        self.aedtapp.materials["vacuum"].conductivity.thermalmodifier = "3"
        assert self.aedtapp.materials["vacuum"].conductivity.thermalmodifier == "3"
        self.aedtapp.materials["vacuum"].conductivity.spatialmodifier = "3"
        assert self.aedtapp.materials["vacuum"].conductivity.spatialmodifier == "3"

        self.aedtapp.materials["vacuum"].conductivity.thermalmodifier = None
        self.aedtapp.materials["vacuum"].conductivity.spatialmodifier = None
        self.aedtapp.materials["vacuum"].conductivity.thermalmodifier = "4"
        assert self.aedtapp.materials["vacuum"].conductivity.thermalmodifier == "4"
        self.aedtapp.materials["vacuum"].conductivity.spatialmodifier = "4"
        assert self.aedtapp.materials["vacuum"].conductivity.spatialmodifier == "4"

        self.aedtapp.materials["vacuum"].conductivity.thermalmodifier = None
        self.aedtapp.materials["vacuum"].conductivity.spatialmodifier = None

    def test_16_import_materials_from_workbench(self):

        assert self.testapp2.materials.import_materials_from_workbench("not_existing.xml") is False

        imported_mats = self.testapp2.materials.import_materials_from_workbench(
            os.path.join(TESTS_GENERAL_PATH, "example_models", test_subfolder, "EngineeringData1.xml")
        )
        for m in imported_mats:
            assert m in self.testapp2.materials.material_keys.values()
        assert self.testapp2.materials.material_keys["new_wb_material_aniso_wb"].permittivity.value == [1, 2, 3]
        assert self.testapp2.materials.material_keys["new_wb_material_aniso_wb"].conductivity.value == [
            0.012987012987012988,
            0.011363636363636364,
            0.010101010101010102,
        ]
        assert self.testapp2.materials.material_keys["structural_steel_wb"].permeability.value == 10000
        assert self.testapp2.materials.material_keys["wb_material_simple_thermal_wb"].conductivity.value == 18
        assert (
            self.testapp2.materials.material_keys["wb_material_simple_thermal_wb"].permittivity.thermalmodifier
            == "pwl($TM_WB_MATERIAL_SIMPLE_thermal_wb_permittivity, Temp)"
        )
        assert self.testapp2.materials.material_keys["wb_material_simple_wb"].conductivity.value == 3
        assert self.testapp2.materials.material_keys["wb_material_simple_wb"].thermal_expansion_coefficient.value == 23

        imported_mats = self.testapp2.materials.import_materials_from_workbench(
            os.path.join(TESTS_GENERAL_PATH, "example_models", test_subfolder, "EngineeringData2.xml")
        )
        for m in imported_mats:
            assert m in self.testapp2.materials.material_keys.values()
        assert self.testapp2.materials.material_keys["aluminum_alloy_wb"].conductivity.value == 41152263.3744856
        assert (
            self.testapp2.materials.material_keys["aluminum_alloy_wb"].thermal_conductivity.thermalmodifier
            == "pwl($TM_Aluminum_Alloy_wb_thermal_conductivity, Temp)"
        )
        assert self.testapp2.materials.material_keys["concrete_wb"].thermal_conductivity.value == 0.72
        assert self.testapp2.materials.material_keys["fr_4_wb"].thermal_conductivity.value == [0.38, 0.38, 0.3]
        assert self.testapp2.materials.material_keys["silicon_anisotropic_wb"].mass_density.value == 2330
        assert (
            self.testapp2.materials.material_keys[
                "silicon_anisotropic_wb"
            ].thermal_expansion_coefficient.thermalmodifier
            == "pwl($TM_Silicon_Anisotropic_wb_thermal_expansion_coefficient, Temp)"
        )

        imported_mats = self.testapp2.materials.import_materials_from_workbench(
            os.path.join(TESTS_GENERAL_PATH, "example_models", test_subfolder, "EngineeringData3.xml"),
            name_suffix="_imp",
        )
        for m in imported_mats:
            assert m in self.testapp2.materials.material_keys.values()
        assert (
            self.testapp2.materials.material_keys["84zn_12ag_4au_imp"].thermal_conductivity.thermalmodifier
            == "pwl($TM_84Zn_12Ag_4Au_imp_thermal_conductivity, Temp)"
        )
        assert (
            self.testapp2.materials.material_keys["84zn_12ag_4au_imp"].mass_density.thermalmodifier
            == "pwl($TM_84Zn_12Ag_4Au_imp_mass_density, Temp)"
        )
        assert (
            self.testapp2.materials.material_keys["84zn_12ag_4au_imp"].specific_heat.thermalmodifier
            == "pwl($TM_84Zn_12Ag_4Au_imp_specific_heat, Temp)"
        )
        assert (
            self.testapp2.materials.material_keys["84zn_12ag_4au_imp"].youngs_modulus.thermalmodifier
            == "pwl($TM_84Zn_12Ag_4Au_imp_youngs_modulus, Temp)"
        )
        assert (
            self.testapp2.materials.material_keys["84zn_12ag_4au_imp"].poissons_ratio.thermalmodifier
            == "pwl($TM_84Zn_12Ag_4Au_imp_poissons_ratio, Temp)"
        )
        assert (
            self.testapp2.materials.material_keys["84zn_12ag_4au_imp"].thermal_expansion_coefficient.thermalmodifier
            == "pwl($TM_84Zn_12Ag_4Au_imp_thermal_expansion_coefficient, Temp)"
        )

    @patch.object(builtins, "open", new_callable=mock_open, read_data=MISSING_RGB_MATERIALS)
    def test_17_json_missing_rgb(self, _mock_file_open, caplog: pytest.LogCaptureFixture):
        input_path = os.path.join(TESTS_GENERAL_PATH, "example_models", test_subfolder, "mats.json")
        with pytest.raises(KeyError):
            self.aedtapp.materials.import_materials_from_file(input_path)
        assert [
            record
            for record in caplog.records
            if record.levelno == logging.ERROR
            and record.message == f"Failed to import material 'copper_5540' from {input_path!r}: key error on 'Red'"
        ]
