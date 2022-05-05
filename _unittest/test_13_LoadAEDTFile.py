# Setup paths for module imports
import base64
import filecmp
import os
import sys

from _unittest.conftest import BasisTest
from _unittest.conftest import local_path
from pyaedt.generic.LoadAEDTFile import load_entire_aedt_file


def _write_jpg(design_info, scratch):
    """writes the jpg Image64 property of the design info
    to a temporary file and returns the filename"""
    filename = os.path.join(scratch, design_info["DesignName"] + ".jpg")
    image_data_str = design_info["Image64"]
    with open(filename, "wb") as f:
        if sys.version_info.major == 2:
            bs = bytes(image_data_str).decode("base64")
        else:
            bs = base64.decodebytes(image_data_str.encode("ascii"))
        f.write(bs)
    return filename


class TestClass(BasisTest, object):
    def setup_class(self):
        BasisTest.my_setup(self)
        self.coax = BasisTest.add_app(self, "Coax_HFSS")
        self.cs = BasisTest.add_app(self, "Coordinate_System")
        self.cs1 = BasisTest.add_app(self, "Coordinate_System1")
        self.cs2 = BasisTest.add_app(self, "Coordinate_System2")
        self.cs3 = BasisTest.add_app(self, "Coordinate_System3")
        self.multiple_cs_project = self.test_project
        self.mat1 = BasisTest.add_app(self, "Add_material")
        hfss_file = os.path.join(local_path, "example_models", "Coax_HFSS.aedt")
        self.project_dict = load_entire_aedt_file(hfss_file)

    def teardown_class(self):
        BasisTest.my_teardown(self)

    def test_01_check_top_level_keys(self):
        assert "AnsoftProject" in list(self.project_dict.keys())
        assert "AllReferencedFilesForProject" in list(self.project_dict.keys())
        assert "ProjectPreview" in list(self.project_dict.keys())

    def test_02_check_design_info(self):
        design_info = self.project_dict["ProjectPreview"]["DesignInfo"]
        # there is one design in this aedt file, so DesignInfo will be a dict
        assert isinstance(design_info, dict)
        assert design_info["Factory"] == "HFSS"
        assert design_info["DesignName"] == "HFSSDesign"
        assert design_info["IsSolved"] == False
        jpg_file = _write_jpg(design_info, self.local_scratch.path)
        assert filecmp.cmp(jpg_file, os.path.join(local_path, "example_models", "Coax_HFSS.jpg"))

    def test_03_check_can_load_aedt_file_with_binary_content(self):
        aedt_file = os.path.join(local_path, "example_models", "assembly.aedt")
        # implicitly this will test to make sure no exception is thrown by load_entire_aedt_file
        self.project_dict = load_entire_aedt_file(aedt_file)

    def test_04_check_design_type_names_jpg(self):
        # there are multiple designs in this aedt file, so DesignInfo will be a list
        aedt_file = os.path.join(local_path, "example_models", "Cassegrain.aedt")
        self.project_dict2 = load_entire_aedt_file(aedt_file)
        self.design_info = self.project_dict2["ProjectPreview"]["DesignInfo"]
        assert isinstance(self.design_info, list)
        design_names = [design["DesignName"] for design in self.design_info]
        assert ["feeder", "Cassegrain_reflectors"] == design_names

    def test_05_check_can_load_aedt_file_with_multiple_coord_systems(self):
        # implicitly this will test to make sure no exception is thrown by load_entire_aedt_file
        assert load_entire_aedt_file(self.multiple_cs_project)

    def test_06_check_coordinate_system_retrival(self):
        cs = self.cs.modeler.coordinate_systems
        assert cs
        cs = self.cs1.modeler.coordinate_systems
        assert cs
        cs = self.cs2.modeler.coordinate_systems
        assert cs
        cs = self.cs3.modeler.coordinate_systems
        assert cs

    def test_07_load_material_file(self):
        mat_file = os.path.join(local_path, "example_models", "material_sample.amat")
        dd = load_entire_aedt_file(mat_file)
        assert dd["vacuum"]
        assert dd["vacuum"]["AttachedData"]["MatAppearanceData"]["Red"] == 230
        assert dd["pec"]
        assert dd["pec"]["conductivity"] == "1e+30"
        assert dd["mat_example_1"]
        assert dd["mat_example_1"]["AttachedData"]["MatAppearanceData"]["Green"] == 154
        assert dd["mat_example_1"]["youngs_modulus"] == "195000000000"
        assert dd["mat_example_1"]["poissons_ratio"] == "0.3"
        assert dd["mat_example_1"]["thermal_expansion_coefficient"] == "1.08e-05"
        assert dd["mat_example_2"]
        assert dd["mat_example_2"]["AttachedData"]["MatAppearanceData"]["Blue"] == 123
        assert dd["mat_example_2"]["conductivity"] == "16700000"
        assert dd["mat_example_2"]["thermal_conductivity"] == "115.5"
        assert dd["mat_example_2"]["mass_density"] == "7140"
        assert dd["mat_example_2"]["specific_heat"] == "389"

    def test_08_add_material_from_amat(self):
        mat_file = os.path.join(local_path, "example_models", "material_sample.amat")
        dd = load_entire_aedt_file(mat_file)
        newmat = self.mat1.materials.add_material("foe_mat", props=dd["mat_example_1"])
        assert newmat.conductivity.value == "1100000"
        assert newmat.thermal_conductivity.value == "13.8"
        assert newmat.mass_density.value == "8055"
        assert newmat.specific_heat.value == "480"
        assert newmat.youngs_modulus.value == "195000000000"
        assert newmat.poissons_ratio.value == "0.3"
        assert newmat.thermal_expansion_coefficient.value == "1.08e-05"
