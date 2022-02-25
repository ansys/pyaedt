# Setup paths for module imports
from _unittest.conftest import local_path, BasisTest

# Import required modules
from pyaedt.generic.LoadAEDTFile import load_entire_aedt_file
import base64
import filecmp
import os
import sys


def _write_jpg(design_info, scratch):
    """writes the jpg Image64 property of the design info
    to a temporary file and returns the filename"""
    filename = os.path.join(scratch, design_info["DesignName"] + ".jpg")
    image_data_str = design_info["Image64"]
    with open(filename, "wb") as f:
        if sys.version_info.major == 2:
            bytes = bytes(image_data_str).decode("base64")
        else:
            bytes = base64.decodebytes(image_data_str.encode("ascii"))
        f.write(bytes)
    return filename


class TestClass(BasisTest):
    def setup_class(self):
        BasisTest.my_setup(self)
        hfss_file = os.path.join(local_path, "example_models", "Coax_HFSS.aedt")
        self.project_dict = load_entire_aedt_file(hfss_file)
        aedt_file = os.path.join(local_path, "example_models", "Coordinate_System.aedt")
        self.test_project = self.local_scratch.copyfile(aedt_file)
        aedt_file = os.path.join(local_path, "example_models", "Coordinate_System1.aedt")
        self.test_project1 = self.local_scratch.copyfile(aedt_file)
        aedt_file = os.path.join(local_path, "example_models", "Coordinate_System2.aedt")
        self.test_project2 = self.local_scratch.copyfile(aedt_file)
        aedt_file = os.path.join(local_path, "example_models", "Coordinate_System3.aedt")
        self.test_project3 = self.local_scratch.copyfile(aedt_file)

    def teardown_class(self):
        BasisTest.my_teardown(self)

    def test_01_check_top_level_keys(self):
        assert list(self.project_dict.keys()) == ["AnsoftProject", "AllReferencedFilesForProject", "ProjectPreview"]

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
        assert ["Cassegrain_Hybrid", "feeder", "Cassegrain_"] == design_names
        jpg_file = _write_jpg(self.design_info[0], self.local_scratch.path)
        assert filecmp.cmp(jpg_file, os.path.join(local_path, "example_models", "Cassegrain_Hybrid.jpg"))

    def test_05_check_can_load_aedt_file_with_multiple_coord_systems(self):
        # implicitly this will test to make sure no exception is thrown by load_entire_aedt_file
        assert load_entire_aedt_file(self.test_project)

    def test_06_check_coordinate_system_retrival(self):
        self.aedtapp.load_project(self.test_project, close_active_proj=True)
        cs = self.aedtapp.modeler.coordinate_systems
        assert cs
        self.aedtapp.load_project(self.test_project1, close_active_proj=True)
        cs = self.aedtapp.modeler.coordinate_systems
        assert cs
        self.aedtapp.load_project(self.test_project2, close_active_proj=True)
        cs = self.aedtapp.modeler.coordinate_systems
        assert cs
        self.aedtapp.load_project(self.test_project3, close_active_proj=True)
        cs = self.aedtapp.modeler.coordinate_systems
        assert cs
