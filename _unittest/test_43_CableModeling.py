import os

from _unittest.conftest import BasisTest
from _unittest.conftest import is_ironpython
from _unittest.conftest import local_path
from pyaedt.modules.CableModeling import Cable

try:
    import pytest  # noqa: F401
except ImportError:
    import _unittest_ironpython.conf_unittest as pytest

# Input Data and version for the test
project_name = "cable_modeling"


class TestClass(BasisTest, object):
    def setup_class(self):
        BasisTest.my_setup(self)
        self.aedtapp = BasisTest.add_app(self, project_name=project_name, design_name="HFSSDesign1")

    def teardown_class(self):
        BasisTest.my_teardown(self)

    def test_01_create_cables_bundle_check_definitions(self):
        cable_file1 = os.path.join(
            local_path, "example_models", "cable_modeling_json_files", "set_bundle_cable_properties_insulation.json"
        )
        cable_file2 = os.path.join(
            local_path, "example_models", "cable_modeling_json_files", "set_bundle_cable_properties_no_jacket.json"
        )
        cable_file3 = os.path.join(
            local_path, "example_models", "cable_modeling_json_files", "set_bundle_cable_properties_shielding.json"
        )
        cable = Cable(self.aedtapp, cable_file1)
        cable.create_cable()
        cable2 = Cable(self.aedtapp, cable_file2)
        assert len(cable2.cable_definitions) == 1
        assert list(cable2.cable_definitions.keys())[0] == "CableBundle"
        assert cable2.cable_definitions["CableBundle"]["BundleAttribs"]["Name"] == "Bundle_Cable_Insulation"
        assert cable2.cable_definitions["CableBundle"]["BundleParams"].get("InsulationJacketParams")
        assert (
            cable2.cable_definitions["CableBundle"]["BundleParams"]["InsulationJacketParams"]["InsThickness"]
            == "3.66mm"
        )
        assert (
            cable2.cable_definitions["CableBundle"]["BundleParams"]["InsulationJacketParams"]["JacketMaterial"] == "pec"
        )
        assert (
            cable2.cable_definitions["CableBundle"]["BundleParams"]["InsulationJacketParams"]["InnerDiameter"]
            == "2.88mm"
        )
        cable2.create_cable()
        cable3 = Cable(self.aedtapp, cable_file3)
        assert len(cable3.cable_definitions["CableBundle"]) == 2
        assert type(cable3.cable_definitions["CableBundle"]) is list
        assert cable3.cable_definitions["CableBundle"][1]["BundleAttribs"]["Name"] == "Bundle_Cable_NoJacket"
        assert cable3.cable_definitions["CableBundle"][1]["BundleParams"].get("VirtualJacketParams")
        assert (
            cable3.cable_definitions["CableBundle"][1]["BundleParams"]["VirtualJacketParams"]["JacketMaterial"]
            == "None"
        )
        assert (
            cable3.cable_definitions["CableBundle"][1]["BundleParams"]["VirtualJacketParams"]["InnerDiameter"]
            == "2.5mm"
        )
        cable3.create_cable()
        cable4 = Cable(self.aedtapp)
        assert len(cable4.cable_definitions["CableBundle"]) == 3
        assert type(cable4.cable_definitions["CableBundle"]) is list
        assert cable4.cable_definitions["CableBundle"][2]["BundleAttribs"]["Name"] == "Bundle_Cable_Shielding"
        assert cable4.cable_definitions["CableBundle"][2]["BundleParams"].get("BraidShieldJacketParams")
        assert (
            cable4.cable_definitions["CableBundle"][2]["BundleParams"]["BraidShieldJacketParams"]["JacketMaterial"]
            == "pec"
        )
        assert (
            cable4.cable_definitions["CableBundle"][2]["BundleParams"]["BraidShieldJacketParams"]["InnerDiameter"]
            == "6mm"
        )
        assert (
            cable4.cable_definitions["CableBundle"][2]["BundleParams"]["BraidShieldJacketParams"]["NumCarriers"] == "36"
        )
        assert (
            cable4.cable_definitions["CableBundle"][2]["BundleParams"]["BraidShieldJacketParams"]["NumWiresInCarrier"]
            == "52"
        )
        assert (
            cable4.cable_definitions["CableBundle"][2]["BundleParams"]["BraidShieldJacketParams"]["WireDiameter"]
            == "0.242424mm"
        )
        assert (
            cable4.cable_definitions["CableBundle"][2]["BundleParams"]["BraidShieldJacketParams"]["WeaveAngle"]
            == "33deg"
        )

    def test_02_create_cables_straight_wire_check_definitions(self):
        cable_file1 = os.path.join(
            local_path, "example_models", "cable_modeling_json_files", "set_straight_wire_cable_properties.json"
        )
        cable = Cable(self.aedtapp, cable_file1)
        cable.create_cable()
        cable2 = Cable(self.aedtapp)
        assert cable2.cable_definitions["StWireCable"]
        assert cable2.cable_definitions["StWireCable"]["StWireAttribs"]["Name"] == "straight_wire_cable"
        assert cable2.cable_definitions["StWireCable"]["StWireParams"]["WireStandard"] == "ISO"
        assert cable2.cable_definitions["StWireCable"]["StWireParams"]["WireGauge"] == "2.5"
        assert cable2.cable_definitions["StWireCable"]["StWireParams"]["CondDiameter"] == "10mm"
        assert cable2.cable_definitions["StWireCable"]["StWireParams"]["CondMaterial"] == "pec"
        assert cable2.cable_definitions["StWireCable"]["StWireParams"]["InsThickness"] == "0.9mm"
        assert cable2.cable_definitions["StWireCable"]["StWireParams"]["InsMaterial"] == "copper"
        assert cable2.cable_definitions["StWireCable"]["StWireParams"]["InsType"] == "Thin Wall"

    def test_03_create_cables_twisted_pair_check_definitions(self):
        cable_file1 = os.path.join(
            local_path, "example_models", "cable_modeling_json_files", "set_twisted_pair_cable_properties.json"
        )
        cable = Cable(self.aedtapp, cable_file1)
        cable.create_cable()
        cable2 = Cable(self.aedtapp)
        assert cable2.cable_definitions["TwistedPairCable"]
        assert cable2.cable_definitions["TwistedPairCable"]["TwistedPairAttribs"]["Name"] == "twisted_pair_cable"
        assert cable2.cable_definitions["TwistedPairCable"]["TwistedPairParams"]
        assert cable2.cable_definitions["TwistedPairCable"]["TwistedPairParams"]["StraightWireCableID"] == 1020
        assert not cable2.cable_definitions["TwistedPairCable"]["TwistedPairParams"]["IsLayLengthSpecified"]
        assert cable2.cable_definitions["TwistedPairCable"]["TwistedPairParams"]["LayLength"] == "0mm"
        assert cable2.cable_definitions["TwistedPairCable"]["TwistedPairParams"]["TurnsPerMeter"] == "99"
        assert type(cable2.cable_definitions["TwistedPairCable"]["Instances"]["StWireInstance"]) is list
        assert len(cable2.cable_definitions["TwistedPairCable"]["Instances"]["StWireInstance"]) == 2

    def test_04_create_cables_missing_properties(self):
        cable_file1 = os.path.join(
            local_path,
            "example_models",
            "cable_modeling_json_files",
            "set_bundle_cable_missing_properties_insulation.json",
        )
        cable_file2 = os.path.join(
            local_path,
            "example_models",
            "cable_modeling_json_files",
            "set_bundle_cable_missing_properties_shielding.json",
        )
        cable_file3 = os.path.join(
            local_path,
            "example_models",
            "cable_modeling_json_files",
            "set_bundle_cable_missing_properties_no_jacket.json",
        )
        cable = Cable(self.aedtapp, cable_file1)
        cable.create_cable()
        cable2 = Cable(self.aedtapp, cable_file2)
        assert len(cable2.cable_definitions["CableBundle"]) == 4
        assert list(cable2.cable_definitions.keys())[0] == "CableBundle"
        assert (
            cable2.cable_definitions["CableBundle"][3]["BundleAttribs"]["Name"]
            == "Bundle_Cable_Insulation_Default_Properties"
        )
        assert cable2.cable_definitions["CableBundle"][3]["BundleParams"].get("InsulationJacketParams")
        assert (
            cable2.cable_definitions["CableBundle"][3]["BundleParams"]["InsulationJacketParams"]["InsThickness"]
            == "0.25mm"
        )
        assert (
            cable2.cable_definitions["CableBundle"][3]["BundleParams"]["InsulationJacketParams"]["JacketMaterial"]
            == "PVC plastic"
        )
        assert (
            cable2.cable_definitions["CableBundle"][3]["BundleParams"]["InsulationJacketParams"]["InnerDiameter"]
            == "2.5mm"
        )
        cable2.create_cable()
        cable3 = Cable(self.aedtapp, cable_file3)
        assert len(cable3.cable_definitions["CableBundle"]) == 5
        assert type(cable3.cable_definitions["CableBundle"]) is list
        assert (
            cable3.cable_definitions["CableBundle"][4]["BundleAttribs"]["Name"]
            == "Bundle_Cable_Shielding_Default_Properties"
        )
        assert cable3.cable_definitions["CableBundle"][4]["BundleParams"].get("BraidShieldJacketParams")
        assert (
            cable3.cable_definitions["CableBundle"][4]["BundleParams"]["BraidShieldJacketParams"]["JacketMaterial"]
            == "copper"
        )
        assert (
            cable3.cable_definitions["CableBundle"][4]["BundleParams"]["BraidShieldJacketParams"]["InnerDiameter"]
            == "2.5mm"
        )
        assert (
            cable3.cable_definitions["CableBundle"][4]["BundleParams"]["BraidShieldJacketParams"]["NumCarriers"] == "2"
        )
        assert (
            cable3.cable_definitions["CableBundle"][4]["BundleParams"]["BraidShieldJacketParams"]["NumWiresInCarrier"]
            == "5"
        )
        assert (
            cable3.cable_definitions["CableBundle"][4]["BundleParams"]["BraidShieldJacketParams"]["WireDiameter"]
            == "0.1mm"
        )
        assert (
            cable3.cable_definitions["CableBundle"][4]["BundleParams"]["BraidShieldJacketParams"]["WeaveAngle"]
            == "30deg"
        )
        cable3.create_cable()
        cable4 = Cable(self.aedtapp)
        assert len(cable4.cable_definitions["CableBundle"]) == 6
        assert type(cable4.cable_definitions["CableBundle"]) is list
        assert cable4.cable_definitions["CableBundle"][5]["BundleParams"].get("VirtualJacketParams")
        assert (
            cable4.cable_definitions["CableBundle"][5]["BundleParams"]["VirtualJacketParams"]["JacketMaterial"]
            == "None"
        )
        assert (
            cable4.cable_definitions["CableBundle"][5]["BundleParams"]["VirtualJacketParams"]["InnerDiameter"]
            == "2.5mm"
        )

    def test_05_jacket_types(self):
        cable_file1 = os.path.join(
            local_path, "example_models", "cable_modeling_json_files", "set_bundle_cable_jacket_types_exception.json"
        )
        if not is_ironpython:
            with pytest.raises(ValueError):
                Cable(self.aedtapp, cable_file1)

    def test_06_invalid_cable_type(self):
        cable_file1 = os.path.join(
            local_path, "example_models", "cable_modeling_json_files", "invalid_cable_types.json"
        )
        if not is_ironpython:
            with pytest.raises(ValueError):
                Cable(self.aedtapp, cable_file1)

    def test_07_invalid_cable_bundle_material_insulation(self):
        cable_file1 = os.path.join(
            local_path,
            "example_models",
            "cable_modeling_json_files",
            "set_bundle_cable_invalid_material_insulation.json",
        )
        if not is_ironpython:
            with pytest.raises(ValueError):
                Cable(self.aedtapp, cable_file1)

    def test_08_invalid_cable_bundle_material_shielding(self):
        cable_file1 = os.path.join(
            local_path,
            "example_models",
            "cable_modeling_json_files",
            "set_bundle_cable_invalid_material_shielding.json",
        )
        if not is_ironpython:
            with pytest.raises(ValueError):
                Cable(self.aedtapp, cable_file1)
