# standard imports
import os
import gc
try:
    import pytest
except ImportError:
    import _unittest_ironpython.conf_unittest as pytest

# Setup paths for module imports
from _unittest.conftest import local_path, scratch_path, desktop_version, new_thread, non_graphical

# Import required modules
from pyaedt import Hfss, Icepak
from pyaedt.generic.filesystem import Scratch

from pyaedt.modules.Material import MatProperties, SurfMatProperties

class TestClass:

    def setup_class(self):
        with Scratch(scratch_path) as self.local_scratch:
            self.aedtapp = Hfss(specified_version=desktop_version,
                                AlwaysNew=new_thread, NG=non_graphical)

    def teardown_class(self):
        assert self.aedtapp.close_project(self.aedtapp.project_name)
        self.local_scratch.remove()
        gc.collect()

    def test_vaacum(self):
        assert "vacuum" in list(self.aedtapp.materials.material_keys.keys())

    def test_create_material(self):
        mat1 = self.aedtapp.materials.add_material("new_copper2")
        assert mat1
        mat1.conductivity = 59000000000
        assert mat1.conductivity.value == 59000000000
        mat1.permeability.value = MatProperties.get_defaultvalue(aedtname="permeability")
        assert mat1.permeability.value == MatProperties.get_defaultvalue(aedtname="permeability")
        mat1.permittivity.value = MatProperties.get_defaultvalue(aedtname="permittivity")
        assert mat1.permittivity.value == MatProperties.get_defaultvalue(aedtname="permittivity")
        mat1.dielectric_loss_tangent.value = MatProperties.get_defaultvalue(
            aedtname="dielectric_loss_tangent")
        assert mat1.dielectric_loss_tangent.value == MatProperties.get_defaultvalue(
            aedtname="dielectric_loss_tangent")
        mat1.magnetic_loss_tangent.value = MatProperties.get_defaultvalue(
            aedtname="magnetic_loss_tangent")
        assert mat1.magnetic_loss_tangent.value == MatProperties.get_defaultvalue(
            aedtname="magnetic_loss_tangent")
        mat1.mass_density.value = MatProperties.get_defaultvalue(aedtname="mass_density")
        assert mat1.mass_density.value == MatProperties.get_defaultvalue(aedtname="mass_density")
        mat1.youngs_modulus.value = MatProperties.get_defaultvalue(aedtname="youngs_modulus")
        assert mat1.youngs_modulus.value == MatProperties.get_defaultvalue(
            aedtname="youngs_modulus")
        mat1.poissons_ratio.value = MatProperties.get_defaultvalue(aedtname="poissons_ratio")
        assert mat1.poissons_ratio.value == MatProperties.get_defaultvalue(
            aedtname="poissons_ratio")
        mat1.thermal_conductivity.value = MatProperties.get_defaultvalue(
            aedtname="thermal_conductivity")
        assert mat1.thermal_conductivity.value == MatProperties.get_defaultvalue(
            aedtname="thermal_conductivity")
        mat1.diffusivity.value = MatProperties.get_defaultvalue(aedtname="diffusivity")

        assert mat1.diffusivity.value == MatProperties.get_defaultvalue(aedtname="diffusivity")

        assert "Electromagnetic" in mat1.physics_type
        mat1.core_loss_kc.value = MatProperties.get_defaultvalue(aedtname="core_loss_kc")
        mat1.core_loss_kh.value = MatProperties.get_defaultvalue(aedtname="core_loss_kh")
        mat1.core_loss_ke.value = MatProperties.get_defaultvalue(aedtname="core_loss_ke")
        mat1.molecular_mass.value = MatProperties.get_defaultvalue(aedtname="molecular_mass")
        mat1.specific_heat.value = MatProperties.get_defaultvalue(aedtname="specific_heat")
        mat1.thermal_expansion_coefficient.value = MatProperties.get_defaultvalue(
            aedtname="thermal_expansion_coefficient")

        assert mat1.core_loss_kc.value == MatProperties.get_defaultvalue(aedtname="core_loss_kc")
        assert mat1.core_loss_kh.value == MatProperties.get_defaultvalue(aedtname="core_loss_kh")
        assert mat1.core_loss_ke.value == MatProperties.get_defaultvalue(aedtname="core_loss_ke")
        assert mat1.coordinate_system == "Cartesian"
        assert mat1.name == "new_copper2"
        assert mat1.molecular_mass.value == MatProperties.get_defaultvalue(
            aedtname="molecular_mass")
        assert mat1.specific_heat.value == MatProperties.get_defaultvalue(aedtname="specific_heat")
        assert mat1.thermal_expansion_coefficient.value == MatProperties.get_defaultvalue(
            aedtname="thermal_expansion_coefficient")
        assert self.aedtapp.change_validation_settings()
        assert self.aedtapp.change_validation_settings(
            ignore_unclassified=True, skip_intersections=True)

        assert mat1.material_appearance == [128, 128, 128]
        mat1.material_appearance = [11, 22, 0]
        assert mat1.material_appearance == [11, 22, 0]
        mat1.material_appearance = ['11', '22', '10']
        assert mat1.material_appearance == [11, 22, 10]
        with pytest.raises(ValueError):
            mat1.material_appearance = [11, 22, 300]
        with pytest.raises(ValueError):
            mat1.material_appearance = [11, -22, 0]
        with pytest.raises(ValueError):
            mat1.material_appearance = [11, 22]

    def test_create_thermal_modifier(self):
        assert self.aedtapp.materials["new_copper2"].mass_density.add_thermal_modifier_free_form(
            "if(Temp > 1000cel, 1, if(Temp < -273.15cel, 1, 1))")
        assert self.aedtapp.materials["new_copper2"].permittivity.add_thermal_modifier_closed_form()
        assert self.aedtapp.materials["new_copper2"].permeability.add_thermal_modifier_closed_form(
            auto_calc=False)
        assert self.aedtapp.materials["new_copper2"].permittivity.add_thermal_modifier_closed_form(
            auto_calc=True)

    def test_duplicate_material(self):
        assert self.aedtapp.materials.duplicate_material("new_copper2", "copper3")
        assert not self.aedtapp.materials.duplicate_material("new_copper3", "copper3")

    def test_delete_material(self):
        assert self.aedtapp.materials.remove_material("copper3")
        assert not self.aedtapp.materials.remove_material("copper4")

    def test_surface_material(self):
        ipk = Icepak()
        mat2 = ipk.materials.add_surface_material("Steel")
        mat2.emissivity.value = SurfMatProperties.get_defaultvalue(aedtname="surface_emissivity")
        mat2.surface_diffuse_absorptance.value = SurfMatProperties.get_defaultvalue(
            aedtname="surface_diffuse_absorptance")
        mat2.surface_roughness.value = SurfMatProperties.get_defaultvalue(
            aedtname="surface_roughness")

        assert mat2.emissivity.value == SurfMatProperties.get_defaultvalue(
            aedtname="surface_emissivity")
        assert mat2.coordinate_system
        assert mat2.surface_diffuse_absorptance.value == SurfMatProperties.get_defaultvalue(
            aedtname="surface_diffuse_absorptance")
        assert mat2.surface_roughness.value == SurfMatProperties.get_defaultvalue(
            aedtname="surface_roughness")
        assert ipk.materials.duplicate_surface_material("Steel", "Steel2")
        assert not ipk.materials.duplicate_surface_material("Steel4", "Steel2")

    def test_export_materials(self):
        assert self.aedtapp.materials.export_materials_to_file(
            os.path.join(self.local_scratch.path, "materials.json"))
        assert os.path.exists(os.path.join(self.local_scratch.path, "materials.json"))

    def test_import_materials(self):
        assert self.aedtapp.materials.import_materials_from_file(
            os.path.join(local_path, 'example_models', 'mats.json'))
        assert "$copper_ds1" in self.aedtapp.project_datasets.keys()
        assert "copper_5540" in self.aedtapp.materials.material_keys.keys()
        assert "al-extruded1" in self.aedtapp.materials.material_keys.keys()
        assert self.aedtapp.materials["al-extruded1"].thermal_conductivity.thermalmodifier

    def test_add_material_sweep(self):
        assert self.aedtapp.materials.add_material_sweep(["copper3", "new_copper"], "sweep_copper")
        assert "sweep_copper" in list(self.aedtapp.materials.material_keys.keys())
