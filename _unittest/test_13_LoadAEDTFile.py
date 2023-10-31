import base64
import filecmp
import os
import sys

from _unittest.conftest import config
from _unittest.conftest import local_path
import pytest

from pyaedt.generic.LoadAEDTFile import load_entire_aedt_file
from pyaedt.generic.LoadAEDTFile import load_keyword_in_aedt_file

test_subfolder = "T13"
if config["desktopVersion"] > "2022.2":
    test_project_name = "Coax_HFSS_t13_231"
    cs_name = "Coordinate_System_231"
    cs1_name = "Coordinate_System1_231"
    cs2_name = "Coordinate_System2_231"
    cs3_name = "Coordinate_System3_231"
    image_f = "Coax_HFSS_v231.jpg"
else:
    test_project_name = "Coax_HFSS_t13"
    cs_name = "Coordinate_System"
    cs1_name = "Coordinate_System1"
    cs2_name = "Coordinate_System2"
    cs3_name = "Coordinate_System3"
    image_f = "Coax_HFSS.jpg"


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


@pytest.fixture(scope="class")
def coax(add_app):
    app = add_app(project_name=test_project_name, subfolder=test_subfolder)
    return app


@pytest.fixture(scope="class")
def cs(add_app):
    app = add_app(project_name=cs_name, subfolder=test_subfolder)
    return app


@pytest.fixture(scope="class")
def cs1(add_app):
    app = add_app(project_name=cs1_name, subfolder=test_subfolder)
    return app


@pytest.fixture(scope="class")
def cs2(add_app):
    app = add_app(project_name=cs2_name, subfolder=test_subfolder)
    return app


@pytest.fixture(scope="class")
def cs3(add_app):
    app = add_app(project_name=cs3_name, subfolder=test_subfolder)
    return app


@pytest.fixture(scope="class")
def mat1(add_app):
    app = add_app(project_name="Add_material")
    return app


@pytest.fixture(scope="class")
def project_dict(add_app):
    hfss_file = os.path.join(local_path, "example_models", test_subfolder, test_project_name + ".aedt")
    return load_entire_aedt_file(hfss_file)


@pytest.fixture(scope="class")
def project_sub_key(add_app):
    hfss_file = os.path.join(local_path, "example_models", test_subfolder, test_project_name + ".aedt")
    return load_keyword_in_aedt_file(hfss_file, "AnsoftProject")


class TestClass:
    @pytest.fixture(autouse=True)
    def init(self, project_dict, project_sub_key, test_project_file, local_scratch):
        self.project_dict = project_dict
        self.project_sub_key = project_sub_key
        self.multiple_cs_project = test_project_file(cs3_name, subfolder=test_subfolder)
        self.local_scratch = local_scratch

    def test_01_check_top_level_keys(self):
        assert "AnsoftProject" in list(self.project_dict.keys())
        assert "AllReferencedFilesForProject" in list(self.project_dict.keys())
        assert "ProjectPreview" in list(self.project_dict.keys())
        assert ["AnsoftProject"] == list(self.project_sub_key.keys())
        assert self.project_dict["AnsoftProject"] == self.project_sub_key["AnsoftProject"]

    def test_02_check_design_info(self):
        design_info = self.project_dict["ProjectPreview"]["DesignInfo"]
        # there is one design in this aedt file, so DesignInfo will be a dict
        assert isinstance(design_info, dict)
        assert design_info["Factory"] == "HFSS"
        assert design_info["DesignName"] == "HFSSDesign"
        assert design_info["IsSolved"] == False
        jpg_file = _write_jpg(design_info, self.local_scratch.path)
        assert filecmp.cmp(jpg_file, os.path.join(local_path, "example_models", test_subfolder, image_f))

    def test_03_check_can_load_aedt_file_with_binary_content(self):
        aedt_file = os.path.join(local_path, "example_models", test_subfolder, "assembly.aedt")
        # implicitly this will test to make sure no exception is thrown by load_entire_aedt_file
        self.project_dict = load_entire_aedt_file(aedt_file)

    def test_04_check_design_type_names_jpg(self):
        # there are multiple designs in this aedt file, so DesignInfo will be a list
        aedt_file = os.path.join(local_path, "example_models", test_subfolder, "Cassegrain.aedt")
        self.project_dict2 = load_entire_aedt_file(aedt_file)
        self.design_info = self.project_dict2["ProjectPreview"]["DesignInfo"]
        assert isinstance(self.design_info, list)
        design_names = [design["DesignName"] for design in self.design_info]
        assert ["feeder", "Cassegrain_reflectors"] == design_names

    def test_05_check_can_load_aedt_file_with_multiple_coord_systems(self):
        # implicitly this will test to make sure no exception is thrown by load_entire_aedt_file
        assert load_entire_aedt_file(self.multiple_cs_project)

    @pytest.mark.parametrize(
        "cs_app",
        ["cs", "cs1", "cs2", "cs3"],
    )
    def test_06_check_coordinate_system_retrival(self, cs_app, request):
        cs_fixt = request.getfixturevalue(cs_app)
        coordinate_systems = cs_fixt.modeler.coordinate_systems
        assert coordinate_systems

    def test_07_load_material_file(self):
        mat_file = os.path.join(local_path, "example_models", test_subfolder, "material_sample.amat")
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

    def test_08_add_material_from_amat(self, mat1):
        mat_file = os.path.join(local_path, "example_models", test_subfolder, "material_sample.amat")
        dd = load_entire_aedt_file(mat_file)
        newmat = mat1.materials.add_material("foe_mat", props=dd["mat_example_1"])
        assert newmat.conductivity.value == "1100000"
        assert newmat.thermal_conductivity.value == "13.8"
        assert newmat.mass_density.value == "8055"
        assert newmat.specific_heat.value == "480"
        assert newmat.youngs_modulus.value == "195000000000"
        assert newmat.poissons_ratio.value == "0.3"
        assert newmat.thermal_expansion_coefficient.value == "1.08e-05"

    def test_09_3dcomponents_array(self):
        array_file = os.path.join(local_path, "example_models", test_subfolder, "phased_array.aedt")
        dd = load_entire_aedt_file(array_file)
        dd_array = dd["AnsoftProject"]["HFSSModel"]["ArrayDefinition"]["ArrayObject"]
        cells = [
            [3, 4, 4, 4, 4, 4, 4, 3],
            [4, 2, 2, 2, 2, 2, 2, 4],
            [4, 2, 1, 1, 1, 1, 2, 4],
            [4, 2, 1, 1, 1, 1, 2, 4],
            [4, 2, 1, 3, 1, 1, 2, 4],
            [4, 2, 1, 1, 1, 1, 2, 4],
            [4, 2, 2, 2, 2, 2, 2, 4],
        ]
        active = [
            [True, True, True, True, True, True, False, False],
            [True, True, True, True, True, True, True, False],
            [True, True, False, False, False, False, True, False],
            [False, True, False, False, False, False, True, False],
            [False, True, True, True, True, True, True, False],
            [False, False, False, True, True, True, False, False],
            [False, False, False, False, False, False, False, False],
        ]
        rotation = [
            [90, 0, 0, 0, 0, 0, 0, 90],
            [270, 0, 0, 0, 0, 0, 0, 90],
            [0, 0, 0, 0, 0, 0, 0, 90],
            [270, 0, 0, 0, 0, 0, 0, 90],
            [270, 0, 0, 0, 0, 0, 0, 90],
            [270, 0, 0, 0, 0, 0, 0, 90],
            [270, 0, 0, 0, 0, 0, 0, 90],
        ]
        onecell = {5: [3, 5], 84: [3, 2], 190: [1, 1], 258: [4, 1]}
        assert dd_array["Cells"]["rows"] == 7
        assert dd_array["Cells"]["columns"] == 8
        assert dd_array["Cells"]["matrix"] == cells
        assert dd_array["Active"]["rows"] == 7
        assert dd_array["Active"]["columns"] == 8
        assert dd_array["Active"]["matrix"] == active
        assert dd_array["Rotation"]["rows"] == 7
        assert dd_array["Rotation"]["columns"] == 8
        assert dd_array["Rotation"]["matrix"] == rotation
        assert dd_array["PostProcessingCells"] == onecell
