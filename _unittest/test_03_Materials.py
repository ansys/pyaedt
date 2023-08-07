# standard imports
import os

from _unittest.conftest import local_path
import pytest

from pyaedt import Icepak
from pyaedt import Maxwell3d

# from pyaedt import is_ironpython
from pyaedt.modules.Material import MatProperties
from pyaedt.modules.Material import SurfMatProperties

# try:
#     import pytest  # noqa: F401
# except ImportError:
#     import _unittest_ironpython.conf_unittest as pytest  # noqa: F401

test_subfolder = "T03"


@pytest.fixture(scope="class")
def aedtapp(add_app):
    app = add_app(project_name="Test03")
    return app


class TestClass:
    @pytest.fixture(autouse=True)
    def init(self, aedtapp, local_scratch):
        self.aedtapp = aedtapp
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
        mat1.permittivity.value = MatProperties.get_defaultvalue(aedtname="permittivity")
        assert mat1.permittivity.value == MatProperties.get_defaultvalue(aedtname="permittivity")
        mat1.dielectric_loss_tangent.value = MatProperties.get_defaultvalue(aedtname="dielectric_loss_tangent")
        assert mat1.dielectric_loss_tangent.value == MatProperties.get_defaultvalue(aedtname="dielectric_loss_tangent")
        mat1.magnetic_loss_tangent.value = MatProperties.get_defaultvalue(aedtname="magnetic_loss_tangent")
        assert mat1.magnetic_loss_tangent.value == MatProperties.get_defaultvalue(aedtname="magnetic_loss_tangent")
        mat1.mass_density.value = MatProperties.get_defaultvalue(aedtname="mass_density")
        assert mat1.mass_density.value == MatProperties.get_defaultvalue(aedtname="mass_density")
        mat1.youngs_modulus.value = MatProperties.get_defaultvalue(aedtname="youngs_modulus")
        assert mat1.youngs_modulus.value == MatProperties.get_defaultvalue(aedtname="youngs_modulus")
        mat1.poissons_ratio.value = MatProperties.get_defaultvalue(aedtname="poissons_ratio")
        assert mat1.poissons_ratio.value == MatProperties.get_defaultvalue(aedtname="poissons_ratio")
        mat1.thermal_conductivity.value = MatProperties.get_defaultvalue(aedtname="thermal_conductivity")
        assert mat1.thermal_conductivity.value == MatProperties.get_defaultvalue(aedtname="thermal_conductivity")
        mat1.diffusivity.value = MatProperties.get_defaultvalue(aedtname="diffusivity")

        assert mat1.diffusivity.value == MatProperties.get_defaultvalue(aedtname="diffusivity")

        assert "Electromagnetic" in mat1.physics_type
        mat1.molecular_mass.value = MatProperties.get_defaultvalue(aedtname="molecular_mass")
        mat1.specific_heat.value = MatProperties.get_defaultvalue(aedtname="specific_heat")
        mat1.thermal_expansion_coefficient.value = MatProperties.get_defaultvalue(
            aedtname="thermal_expansion_coefficient"
        )

        assert mat1.coordinate_system == "Cartesian"
        assert mat1.name == "new_copper2"
        assert mat1.molecular_mass.value == MatProperties.get_defaultvalue(aedtname="molecular_mass")
        assert mat1.specific_heat.value == MatProperties.get_defaultvalue(aedtname="specific_heat")
        assert mat1.thermal_expansion_coefficient.value == MatProperties.get_defaultvalue(
            aedtname="thermal_expansion_coefficient"
        )
        assert self.aedtapp.change_validation_settings()
        assert self.aedtapp.change_validation_settings(ignore_unclassified=True, skip_intersections=True)

        assert mat1.set_magnetic_coercitivity(1, 2, 3, 4)
        assert mat1.get_magnetic_coercitivity() == ("1A_per_meter", "2", "3", "4")
        assert mat1.set_electrical_steel_coreloss(1, 2, 3, 4, 0.002)
        assert mat1.get_curve_coreloss_type() == "Electrical Steel"
        assert mat1.get_curve_coreloss_values()["core_loss_equiv_cut_depth"] == "0.002meter"
        assert mat1.set_hysteresis_coreloss(1, 2, 3, 4, 0.002)
        assert mat1.get_curve_coreloss_type() == "Hysteresis Model"
        assert mat1.set_bp_curve_coreloss([[0, 0], [10, 10], [20, 20]])
        assert mat1.get_curve_coreloss_type() == "B-P Curve"
        assert mat1.set_power_ferrite_coreloss()
        assert mat1.get_curve_coreloss_type() == "Power Ferrite"
        assert isinstance(mat1.material_appearance, list)

        mat1.material_appearance = [11, 22, 0]
        assert mat1.material_appearance == [11, 22, 0]
        mat1.material_appearance = ["11", "22", "10"]
        assert mat1.material_appearance == [11, 22, 10]
        try:
            mat1.material_appearance = [11, 22, 300]
            assert False
        except ValueError:
            assert True
        try:
            mat1.material_appearance = [11, -22, 0]
            assert False
        except ValueError:
            assert True
        try:
            mat1.material_appearance = [11, 22]
            assert False
        except ValueError:
            assert True

    def test_03_create_modifiers(self):
        assert self.aedtapp.materials["new_copper2"].mass_density.add_thermal_modifier_free_form(
            "if(Temp > 1000cel, 1, if(Temp < -273.15cel, 1, 1))"
        )
        assert self.aedtapp.materials["new_copper2"].mass_density.add_thermal_modifier_closed_form()
        assert self.aedtapp.materials["new_copper2"].mass_density.add_thermal_modifier_closed_form(auto_calc=False)
        assert self.aedtapp.materials["new_copper2"].permittivity.add_thermal_modifier_closed_form()
        assert self.aedtapp.materials["new_copper2"].permeability.add_thermal_modifier_closed_form(auto_calc=False)
        assert self.aedtapp.materials["new_copper2"].permittivity.add_thermal_modifier_closed_form(auto_calc=False)
        filename = os.path.join(local_path, "example_models", test_subfolder, "ds_1d.tab")
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
        filename = os.path.join(local_path, "example_models", test_subfolder, "ds_3d.tab")
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
        # ipk = Icepak(specified_version=desktop_version)
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

    def test_07_export_materials(self):
        assert self.aedtapp.materials.export_materials_to_file(os.path.join(self.local_scratch.path, "materials.json"))
        assert os.path.exists(os.path.join(self.local_scratch.path, "materials.json"))

    def test_08_import_materials(self):
        assert self.aedtapp.materials.import_materials_from_file(
            os.path.join(local_path, "example_models", test_subfolder, "mats.json")
        )
        assert "$copper_ds1" in self.aedtapp.project_datasets.keys()
        assert "copper_5540" in self.aedtapp.materials.material_keys.keys()
        assert "al-extruded1" in self.aedtapp.materials.material_keys.keys()
        assert self.aedtapp.materials["al-extruded1"].thermal_conductivity.thermalmodifier

    def test_08B_import_materials_from_excel(self):
        mats = self.aedtapp.materials.import_materials_from_excel(
            os.path.join(local_path, "example_models", test_subfolder, "mats.xlsx")
        )
        assert len(mats) == 2
        assert mats[0].conductivity.value == 5700000
        assert mats[0].permittivity.value == 0.5
        assert mats[0].name == "aluminum_2"
        mats = self.aedtapp.materials.import_materials_from_excel(
            os.path.join(local_path, "example_models", test_subfolder, "mats.csv")
        )
        assert len(mats) == 2

    def test_09_non_linear_materials(self, add_app):
        # app = Maxwell3d(specified_version=desktop_version)
        app = add_app(application=Maxwell3d)
        mat1 = app.materials.add_material("myMat")
        assert mat1.permeability.set_non_linear([[0, 0], [1, 12], [10, 30]])
        assert mat1.permittivity.set_non_linear([[0, 0], [2, 12], [10, 30]])
        assert mat1.conductivity.set_non_linear([[0, 0], [3, 12], [10, 30]])
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
        assert mat2.permeability.set_non_linear([[0, 0], [1, 12], [10, 30]])
        assert app.modeler.create_box([0, 0, 0], [10, 10, 10], matname="myMat2")

    def test_10_add_material_sweep(self):
        assert self.aedtapp.materials.add_material_sweep(["copper", "aluminum"], "sweep_copper")
        assert "sweep_copper" in list(self.aedtapp.materials.material_keys.keys())

    def test_11_material_case(self):
        assert self.aedtapp.materials["Aluminum"] == self.aedtapp.materials["aluminum"]
        assert self.aedtapp.materials["Aluminum"].name == "aluminum"
        assert self.aedtapp.materials.add_material("AluMinum") == self.aedtapp.materials["aluminum"]
