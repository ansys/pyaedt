import os

from _unittest.conftest import BasisTest
from _unittest.conftest import config
from _unittest.conftest import local_path
from pyaedt.modules.CableModeling import Cable

try:
    import pytest  # noqa: F401
except ImportError:
    import _unittest_ironpython.conf_unittest as pytest

if config["desktopVersion"] > "2022.2":
    project_name = "cable_modeling_231"
else:
    project_name = "cable_modeling"

test_subfloder = "T43"


class TestClass(BasisTest, object):
    def setup_class(self):
        BasisTest.my_setup(self)
        self.aedtapp = BasisTest.add_app(
            self, project_name=project_name, design_name="HFSSDesign1", subfolder=test_subfloder
        )

    def teardown_class(self):
        BasisTest.my_teardown(self)

    def test_01_create_cables_bundle_check_definitions(self):
        cable_file1 = os.path.join(
            local_path,
            "example_models",
            test_subfloder,
            "cable_modeling_json_files",
            "set_bundle_cable_properties_insulation.json",
        )
        cable_file2 = os.path.join(
            local_path,
            "example_models",
            test_subfloder,
            "cable_modeling_json_files",
            "set_bundle_cable_properties_no_jacket.json",
        )
        cable_file3 = os.path.join(
            local_path,
            "example_models",
            test_subfloder,
            "cable_modeling_json_files",
            "set_bundle_cable_properties_shielding.json",
        )
        Cable(self.aedtapp, cable_file1).create_cable()
        cable = Cable(self.aedtapp, cable_file2)
        assert len(cable.cable_definitions) == 1
        assert list(cable.cable_definitions.keys())[0] == "CableBundle"
        assert cable.cable_definitions["CableBundle"]["BundleAttribs"]["Name"] == "Bundle_Cable_Insulation"
        assert cable.cable_definitions["CableBundle"]["BundleParams"].get("InsulationJacketParams")
        assert (
            cable.cable_definitions["CableBundle"]["BundleParams"]["InsulationJacketParams"]["InsThickness"] == "3.66mm"
        )
        assert (
            cable.cable_definitions["CableBundle"]["BundleParams"]["InsulationJacketParams"]["JacketMaterial"] == "pec"
        )
        assert (
            cable.cable_definitions["CableBundle"]["BundleParams"]["InsulationJacketParams"]["InnerDiameter"]
            == "2.88mm"
        )
        cable.create_cable()
        cable1 = Cable(self.aedtapp, cable_file3)
        assert len(cable1.cable_definitions["CableBundle"]) == 2
        assert type(cable1.cable_definitions["CableBundle"]) is list
        assert cable1.cable_definitions["CableBundle"][1]["BundleAttribs"]["Name"] == "Bundle_Cable_NoJacket"
        assert cable1.cable_definitions["CableBundle"][1]["BundleParams"].get("VirtualJacketParams")
        assert (
            cable1.cable_definitions["CableBundle"][1]["BundleParams"]["VirtualJacketParams"]["JacketMaterial"]
            == "None"
        )
        assert (
            cable1.cable_definitions["CableBundle"][1]["BundleParams"]["VirtualJacketParams"]["InnerDiameter"]
            == "2.5mm"
        )
        cable1.create_cable()
        cable2 = Cable(self.aedtapp)
        assert len(cable2.cable_definitions["CableBundle"]) == 3
        assert type(cable2.cable_definitions["CableBundle"]) is list
        assert cable2.cable_definitions["CableBundle"][2]["BundleAttribs"]["Name"] == "Bundle_Cable_Shielding"
        assert cable2.cable_definitions["CableBundle"][2]["BundleParams"].get("BraidShieldJacketParams")
        assert (
            cable2.cable_definitions["CableBundle"][2]["BundleParams"]["BraidShieldJacketParams"]["JacketMaterial"]
            == "pec"
        )
        assert (
            cable2.cable_definitions["CableBundle"][2]["BundleParams"]["BraidShieldJacketParams"]["InnerDiameter"]
            == "6mm"
        )
        assert (
            cable2.cable_definitions["CableBundle"][2]["BundleParams"]["BraidShieldJacketParams"]["NumCarriers"] == "36"
        )
        assert (
            cable2.cable_definitions["CableBundle"][2]["BundleParams"]["BraidShieldJacketParams"]["NumWiresInCarrier"]
            == "52"
        )
        assert (
            cable2.cable_definitions["CableBundle"][2]["BundleParams"]["BraidShieldJacketParams"]["WireDiameter"]
            == "0.242424mm"
        )
        assert (
            cable2.cable_definitions["CableBundle"][2]["BundleParams"]["BraidShieldJacketParams"]["WeaveAngle"]
            == "33deg"
        )

    def test_02_create_cables_straight_wire_check_definitions(self):
        cable_file1 = os.path.join(
            local_path,
            "example_models",
            test_subfloder,
            "cable_modeling_json_files",
            "set_straight_wire_cable_properties.json",
        )
        Cable(self.aedtapp, cable_file1).create_cable()
        cable = Cable(self.aedtapp)
        assert cable.cable_definitions["StWireCable"]
        assert cable.cable_definitions["StWireCable"]["StWireAttribs"]["Name"] == "straight_wire_cable"
        assert cable.cable_definitions["StWireCable"]["StWireParams"]["WireStandard"] == "ISO"
        assert cable.cable_definitions["StWireCable"]["StWireParams"]["WireGauge"] == "2.5"
        assert cable.cable_definitions["StWireCable"]["StWireParams"]["CondDiameter"] == "10mm"
        assert cable.cable_definitions["StWireCable"]["StWireParams"]["CondMaterial"] == "pec"
        assert cable.cable_definitions["StWireCable"]["StWireParams"]["InsThickness"] == "0.9mm"
        assert cable.cable_definitions["StWireCable"]["StWireParams"]["InsMaterial"] == "copper"
        assert cable.cable_definitions["StWireCable"]["StWireParams"]["InsType"] == "Thin Wall"

    def test_03_create_cables_twisted_pair_check_definitions(self):
        cable_file1 = os.path.join(
            local_path,
            "example_models",
            test_subfloder,
            "cable_modeling_json_files",
            "set_twisted_pair_cable_properties.json",
        )
        Cable(self.aedtapp, cable_file1).create_cable()
        cable = Cable(self.aedtapp)
        assert cable.cable_definitions["TwistedPairCable"]
        assert cable.cable_definitions["TwistedPairCable"]["TwistedPairAttribs"]["Name"] == "twisted_pair_cable"
        assert cable.cable_definitions["TwistedPairCable"]["TwistedPairParams"]
        assert cable.cable_definitions["TwistedPairCable"]["TwistedPairParams"]["StraightWireCableID"] == 1023
        assert not cable.cable_definitions["TwistedPairCable"]["TwistedPairParams"]["IsLayLengthSpecified"]
        assert cable.cable_definitions["TwistedPairCable"]["TwistedPairParams"]["LayLength"] == "0mm"
        assert cable.cable_definitions["TwistedPairCable"]["TwistedPairParams"]["TurnsPerMeter"] == "99"
        assert type(cable.cable_definitions["TwistedPairCable"]["Instances"]["StWireInstance"]) is list
        assert len(cable.cable_definitions["TwistedPairCable"]["Instances"]["StWireInstance"]) == 2
        cable_file1 = os.path.join(
            local_path,
            "example_models",
            test_subfloder,
            "cable_modeling_json_files",
            "set_twisted_pair_cable_properties_laylength.json",
        )
        assert Cable(self.aedtapp, cable_file1).create_cable()

        cable_file1 = os.path.join(
            local_path,
            "example_models",
            test_subfloder,
            "cable_modeling_json_files",
            "set_twisted_pair_cable_properties_invalid.json",
        )
        assert not Cable(self.aedtapp, cable_file1).create_cable()

    def test_04_create_cables_missing_properties(self):
        cable_file1 = os.path.join(
            local_path,
            "example_models",
            test_subfloder,
            "cable_modeling_json_files",
            "set_bundle_cable_missing_properties_insulation.json",
        )
        cable_file2 = os.path.join(
            local_path,
            "example_models",
            test_subfloder,
            "cable_modeling_json_files",
            "set_bundle_cable_missing_properties_shielding.json",
        )
        cable_file3 = os.path.join(
            local_path,
            "example_models",
            test_subfloder,
            "cable_modeling_json_files",
            "set_bundle_cable_missing_properties_no_jacket.json",
        )
        Cable(self.aedtapp, cable_file1).create_cable()
        cable = Cable(self.aedtapp, cable_file2)
        assert len(cable.cable_definitions["CableBundle"]) == 4
        assert (
            cable.cable_definitions["CableBundle"][3]["BundleAttribs"]["Name"]
            == "Bundle_Cable_Insulation_Default_Properties"
        )
        assert cable.cable_definitions["CableBundle"][3]["BundleParams"].get("InsulationJacketParams")
        assert (
            cable.cable_definitions["CableBundle"][3]["BundleParams"]["InsulationJacketParams"]["InsThickness"]
            == "0.25mm"
        )
        assert (
            cable.cable_definitions["CableBundle"][3]["BundleParams"]["InsulationJacketParams"]["JacketMaterial"]
            == "PVC plastic"
        )
        assert (
            cable.cable_definitions["CableBundle"][3]["BundleParams"]["InsulationJacketParams"]["InnerDiameter"]
            == "2.5mm"
        )
        cable.create_cable()
        cable1 = Cable(self.aedtapp, cable_file3)
        assert len(cable1.cable_definitions["CableBundle"]) == 5
        assert type(cable1.cable_definitions["CableBundle"]) is list
        assert (
            cable1.cable_definitions["CableBundle"][4]["BundleAttribs"]["Name"]
            == "Bundle_Cable_Shielding_Default_Properties"
        )
        assert cable1.cable_definitions["CableBundle"][4]["BundleParams"].get("BraidShieldJacketParams")
        assert (
            cable1.cable_definitions["CableBundle"][4]["BundleParams"]["BraidShieldJacketParams"]["JacketMaterial"]
            == "copper"
        )
        assert (
            cable1.cable_definitions["CableBundle"][4]["BundleParams"]["BraidShieldJacketParams"]["InnerDiameter"]
            == "2.5mm"
        )
        assert (
            cable1.cable_definitions["CableBundle"][4]["BundleParams"]["BraidShieldJacketParams"]["NumCarriers"] == "2"
        )
        assert (
            cable1.cable_definitions["CableBundle"][4]["BundleParams"]["BraidShieldJacketParams"]["NumWiresInCarrier"]
            == "5"
        )
        assert (
            cable1.cable_definitions["CableBundle"][4]["BundleParams"]["BraidShieldJacketParams"]["WireDiameter"]
            == "0.1mm"
        )
        assert (
            cable1.cable_definitions["CableBundle"][4]["BundleParams"]["BraidShieldJacketParams"]["WeaveAngle"]
            == "30deg"
        )
        cable1.create_cable()
        cable2 = Cable(self.aedtapp)
        assert len(cable2.cable_definitions["CableBundle"]) == 6
        assert type(cable2.cable_definitions["CableBundle"]) is list
        assert cable2.cable_definitions["CableBundle"][5]["BundleParams"].get("VirtualJacketParams")
        assert (
            cable2.cable_definitions["CableBundle"][5]["BundleParams"]["VirtualJacketParams"]["JacketMaterial"]
            == "None"
        )
        assert (
            cable2.cable_definitions["CableBundle"][5]["BundleParams"]["VirtualJacketParams"]["InnerDiameter"]
            == "2.5mm"
        )

    def test_05_jacket_types(self):
        cable_file1 = os.path.join(
            local_path,
            "example_models",
            test_subfloder,
            "cable_modeling_json_files",
            "set_bundle_cable_jacket_types_exception.json",
        )
        assert not Cable(self.aedtapp, cable_file1).create_cable()

    def test_06_invalid_cable_bundle_material_insulation(self):
        cable_file1 = os.path.join(
            local_path,
            "example_models",
            test_subfloder,
            "cable_modeling_json_files",
            "set_bundle_cable_invalid_material_insulation.json",
        )
        assert not Cable(self.aedtapp, cable_file1).create_cable()

    def test_07_invalid_cable_bundle_material_shielding(self):
        cable_file1 = os.path.join(
            local_path,
            "example_models",
            test_subfloder,
            "cable_modeling_json_files",
            "set_bundle_cable_invalid_material_shielding.json",
        )
        assert not Cable(self.aedtapp, cable_file1).create_cable()

    def test_08_working_dir(self):
        cable_file1 = os.path.join(
            local_path,
            "example_models",
            test_subfloder,
            "cable_modeling_json_files",
            "set_bundle_cable_properties_insulation.json",
        )
        Cable(self.aedtapp, cable_file1)
        assert os.path.exists(self.aedtapp.toolkit_directory)
        assert os.path.exists(os.path.join(self.aedtapp.toolkit_directory, "export_cable_library_as_json_test.json"))
        pass

    def test_09_update_cables_bundle_insulation(self):
        cable_file1 = os.path.join(
            local_path,
            "example_models",
            test_subfloder,
            "cable_modeling_json_files",
            "update_bundle_cable_properties_insulation.json",
        )
        Cable(self.aedtapp, cable_file1).update_cable_properties()
        cable = Cable(self.aedtapp, cable_file1)
        assert (
            cable.cable_definitions["CableBundle"][0]["BundleAttribs"]["Name"]
            == "New_test_updated_name_cable_bundle_insulation"
        )
        assert cable.cable_definitions["CableBundle"][0]["BundleParams"].get("InsulationJacketParams")
        assert (
            cable.cable_definitions["CableBundle"][0]["BundleParams"]["InsulationJacketParams"]["InsThickness"] == "5mm"
        )
        assert (
            cable.cable_definitions["CableBundle"][0]["BundleParams"]["InsulationJacketParams"]["JacketMaterial"]
            == "pec"
        )
        assert (
            cable.cable_definitions["CableBundle"][0]["BundleParams"]["InsulationJacketParams"]["InnerDiameter"]
            == "3mm"
        )

    def test_10_update_cables_bundle_no_jacket(self):
        cable_file1 = os.path.join(
            local_path,
            "example_models",
            test_subfloder,
            "cable_modeling_json_files",
            "update_bundle_cable_properties_no_jacket.json",
        )
        Cable(self.aedtapp, cable_file1).update_cable_properties()
        cable = Cable(self.aedtapp, cable_file1)
        assert (
            cable.cable_definitions["CableBundle"][1]["BundleAttribs"]["Name"]
            == "New_test_updated_name_cable_bundle_no_jacket"
        )
        assert cable.cable_definitions["CableBundle"][1]["BundleParams"].get("VirtualJacketParams")
        assert (
            cable.cable_definitions["CableBundle"][1]["BundleParams"]["VirtualJacketParams"]["JacketMaterial"] == "None"
        )
        assert (
            cable.cable_definitions["CableBundle"][1]["BundleParams"]["VirtualJacketParams"]["InnerDiameter"] == "5mm"
        )

    def test_11_update_cables_bundle_shielding(self):
        cable_file1 = os.path.join(
            local_path,
            "example_models",
            test_subfloder,
            "cable_modeling_json_files",
            "update_bundle_cable_properties_shielding.json",
        )
        Cable(self.aedtapp, cable_file1).update_shielding()
        cable = Cable(self.aedtapp, cable_file1)
        assert (
            cable.cable_definitions["CableBundle"][2]["BundleAttribs"]["Name"]
            == "New_test_updated_name_cable_bundle_shielding"
        )
        assert cable.cable_definitions["CableBundle"][2]["BundleParams"].get("BraidShieldJacketParams")
        assert (
            cable.cable_definitions["CableBundle"][2]["BundleParams"]["BraidShieldJacketParams"]["JacketMaterial"]
            == "pec"
        )
        assert (
            cable.cable_definitions["CableBundle"][2]["BundleParams"]["BraidShieldJacketParams"]["InnerDiameter"]
            == "10mm"
        )
        assert (
            cable.cable_definitions["CableBundle"][2]["BundleParams"]["BraidShieldJacketParams"]["NumCarriers"] == "22"
        )
        assert (
            cable.cable_definitions["CableBundle"][2]["BundleParams"]["BraidShieldJacketParams"]["NumWiresInCarrier"]
            == "23"
        )
        assert (
            cable.cable_definitions["CableBundle"][2]["BundleParams"]["BraidShieldJacketParams"]["WireDiameter"]
            == "0.212mm"
        )
        assert (
            cable.cable_definitions["CableBundle"][2]["BundleParams"]["BraidShieldJacketParams"]["WeaveAngle"]
            == "35deg"
        )

    def test_12_update_invalid_cable_bundle_material_insulation(self):
        cable_file1 = os.path.join(
            local_path,
            "example_models",
            test_subfloder,
            "cable_modeling_json_files",
            "update_bundle_cable_invalid_material_insulation.json",
        )
        assert not Cable(self.aedtapp, cable_file1).update_cable_properties()

    def test_13_update_invalid_cable_bundle_material_shielding(self):
        cable_file1 = os.path.join(
            local_path,
            "example_models",
            test_subfloder,
            "cable_modeling_json_files",
            "update_bundle_cable_invalid_material_shielding.json",
        )
        assert not Cable(self.aedtapp, cable_file1).update_shielding()

    @pytest.mark.skip(reason="Unable to update if it's not done before manually.")
    def test_14_update_cables_straight_wire_definitions(self):
        cable_file1 = os.path.join(
            local_path,
            "example_models",
            test_subfloder,
            "cable_modeling_json_files",
            "update_straight_wire_cable_properties.json",
        )
        assert Cable(self.aedtapp, cable_file1).update_cable_properties()

    def test_15_create_cables_twisted_pair_check_definitions(self):
        cable_file1 = os.path.join(
            local_path,
            "example_models",
            test_subfloder,
            "cable_modeling_json_files",
            "update_twisted_pair_cable_properties.json",
        )
        Cable(self.aedtapp, cable_file1).update_cable_properties()
        cable = Cable(self.aedtapp)
        assert cable.cable_definitions["TwistedPairCable"]
        assert (
            cable.cable_definitions["TwistedPairCable"][0]["TwistedPairAttribs"]["Name"]
            == "updated_name_cable_twisted_pair"
        )
        assert cable.cable_definitions["TwistedPairCable"][0]["TwistedPairParams"]
        assert cable.cable_definitions["TwistedPairCable"][0]["TwistedPairParams"]["StraightWireCableID"] == 1023
        assert not cable.cable_definitions["TwistedPairCable"][0]["TwistedPairParams"]["IsLayLengthSpecified"]
        assert cable.cable_definitions["TwistedPairCable"][0]["TwistedPairParams"]["LayLength"] == "47mm"
        assert cable.cable_definitions["TwistedPairCable"][0]["TwistedPairParams"]["TurnsPerMeter"] == "97"
        assert type(cable.cable_definitions["TwistedPairCable"][0]["Instances"]["StWireInstance"]) is list
        assert len(cable.cable_definitions["TwistedPairCable"][0]["Instances"]["StWireInstance"]) == 2

    def test_16_remove_cables(self):
        cable_file1 = os.path.join(
            local_path, "example_models", test_subfloder, "cable_modeling_json_files", "cables_to_remove.json"
        )
        assert Cable(self.aedtapp, cable_file1).remove_cables()
        cable_file2 = os.path.join(
            local_path, "example_models", test_subfloder, "cable_modeling_json_files", "cables_to_remove_invalid.json"
        )
        assert not Cable(self.aedtapp, cable_file2).remove_cables()

    def test_17_add_cables_to_bundle(self):
        cable_file1 = os.path.join(
            local_path, "example_models", test_subfloder, "cable_modeling_json_files", "add_cables_to_bundle.json"
        )
        assert Cable(self.aedtapp, cable_file1).add_cable_to_bundle()

    def test_17_add_cables_to_bundle_invalid(self):
        cable_file1 = os.path.join(
            local_path,
            "example_models",
            test_subfloder,
            "cable_modeling_json_files",
            "cables_to_remove_add_for_cables_to_add_to_bundle.json",
        )
        Cable(self.aedtapp, cable_file1).remove_cables()
        cable_file2 = os.path.join(
            local_path,
            "example_models",
            test_subfloder,
            "cable_modeling_json_files",
            "add_cables_to_bundle_invalid.json",
        )
        assert not Cable(self.aedtapp, cable_file2).add_cable_to_bundle()

    def test_18_add_clock_source(self):
        cable_file1 = os.path.join(
            local_path,
            "example_models",
            test_subfloder,
            "cable_modeling_json_files",
            "add_clock_source.json",
        )
        assert Cable(self.aedtapp, cable_file1).create_clock_source()
        cable = Cable(self.aedtapp)
        assert len(cable.clock_source_definitions) == 3
        assert cable.clock_source_definitions[2]["ClockSignalParams"]["Period"] == "40us"
        assert cable.clock_source_definitions[2]["ClockSignalParams"]["LowPulseVal"] == "0.1V"
        assert cable.clock_source_definitions[2]["ClockSignalParams"]["HighPulseVal"] == "2V"
        assert cable.clock_source_definitions[2]["ClockSignalParams"]["Risetime"] == "5us"
        assert cable.clock_source_definitions[2]["ClockSignalParams"]["Falltime"] == "10us"
        assert cable.clock_source_definitions[2]["ClockSignalParams"]["PulseWidth"] == "23us"

    def test_18a_add_clock_source_without_name(self):
        cable_file1 = os.path.join(
            local_path,
            "example_models",
            test_subfloder,
            "cable_modeling_json_files",
            "add_clock_source_without_name.json",
        )
        assert Cable(self.aedtapp, cable_file1).create_clock_source()
        cable = Cable(self.aedtapp)
        assert len(cable.clock_source_definitions) == 4
        assert cable.clock_source_definitions[2]["ClockSignalParams"]["Period"] == "40us"
        assert cable.clock_source_definitions[2]["ClockSignalParams"]["LowPulseVal"] == "0.1V"
        assert cable.clock_source_definitions[2]["ClockSignalParams"]["HighPulseVal"] == "2V"
        assert cable.clock_source_definitions[2]["ClockSignalParams"]["Risetime"] == "5us"
        assert cable.clock_source_definitions[2]["ClockSignalParams"]["Falltime"] == "10us"
        assert cable.clock_source_definitions[2]["ClockSignalParams"]["PulseWidth"] == "23us"

    def test_19_add_clock_source_invalid_1(self):
        cable_file1 = os.path.join(
            local_path,
            "example_models",
            test_subfloder,
            "cable_modeling_json_files",
            "invalid_add_clock_source_1.json",
        )
        assert not Cable(self.aedtapp, cable_file1).create_clock_source()

    def test_20_add_clock_source_invalid_2(self):
        cable_file1 = os.path.join(
            local_path,
            "example_models",
            test_subfloder,
            "cable_modeling_json_files",
            "invalid_add_clock_source_2.json",
        )
        assert not Cable(self.aedtapp, cable_file1).create_clock_source()

    def test_21_add_clock_source_invalid_2(self):
        cable_file1 = os.path.join(
            local_path,
            "example_models",
            test_subfloder,
            "cable_modeling_json_files",
            "invalid_add_clock_source_2.json",
        )
        assert not Cable(self.aedtapp, cable_file1).create_clock_source()

    def test_22_add_clock_source_invalid_3(self):
        cable_file1 = os.path.join(
            local_path,
            "example_models",
            test_subfloder,
            "cable_modeling_json_files",
            "invalid_add_clock_source_3.json",
        )
        assert not Cable(self.aedtapp, cable_file1).create_clock_source()

    def test_24_add_clock_source_invalid_4(self):
        cable_file1 = os.path.join(
            local_path,
            "example_models",
            test_subfloder,
            "cable_modeling_json_files",
            "invalid_add_clock_source_4.json",
        )
        assert not Cable(self.aedtapp, cable_file1).create_clock_source()

    def test_24_add_clock_source_invalid_5(self):
        cable_file1 = os.path.join(
            local_path,
            "example_models",
            test_subfloder,
            "cable_modeling_json_files",
            "invalid_add_clock_source_5.json",
        )
        assert not Cable(self.aedtapp, cable_file1).create_clock_source()

    def test_25_add_clock_source_invalid_6(self):
        cable_file1 = os.path.join(
            local_path,
            "example_models",
            test_subfloder,
            "cable_modeling_json_files",
            "invalid_add_clock_source_6.json",
        )
        assert not Cable(self.aedtapp, cable_file1).create_clock_source()

    def test_26_add_clock_source_invalid_7(self):
        cable_file1 = os.path.join(
            local_path,
            "example_models",
            test_subfloder,
            "cable_modeling_json_files",
            "invalid_add_clock_source_7.json",
        )
        assert not Cable(self.aedtapp, cable_file1).create_clock_source()

    def test_27_update_clock_source(self):
        cable_file1 = os.path.join(
            local_path,
            "example_models",
            test_subfloder,
            "cable_modeling_json_files",
            "update_clock_source.json",
        )
        assert Cable(self.aedtapp, cable_file1).update_clock_source()
        cable = Cable(self.aedtapp)
        assert cable.clock_source_definitions[0]["TDSourceAttribs"]["Name"] == "update_clock_test_1"
        assert cable.clock_source_definitions[0]["ClockSignalParams"]["Period"] == "45us"
        assert cable.clock_source_definitions[0]["ClockSignalParams"]["LowPulseVal"] == "0.3V"
        assert cable.clock_source_definitions[0]["ClockSignalParams"]["HighPulseVal"] == "3V"
        assert cable.clock_source_definitions[0]["ClockSignalParams"]["Risetime"] == "4us"
        assert cable.clock_source_definitions[0]["ClockSignalParams"]["Falltime"] == "15us"
        assert cable.clock_source_definitions[0]["ClockSignalParams"]["PulseWidth"] == "26us"

    def test_28_remove_clock_source(self):
        cable_file1 = os.path.join(
            local_path,
            "example_models",
            test_subfloder,
            "cable_modeling_json_files",
            "remove_clock_source.json",
        )
        assert Cable(self.aedtapp, cable_file1).remove_source()
        cable = Cable(self.aedtapp)
        assert len(cable.clock_source_definitions) == 3
        cable_file2 = os.path.join(
            local_path,
            "example_models",
            test_subfloder,
            "cable_modeling_json_files",
            "remove_clock_source_invalid.json",
        )
        assert not Cable(self.aedtapp, cable_file2).remove_source()

    def test_29_add_pwl_source(self):
        cable_file1 = os.path.join(
            local_path,
            "example_models",
            test_subfloder,
            "cable_modeling_json_files",
            "add_pwl_source.json",
        )
        assert Cable(self.aedtapp, cable_file1).create_pwl_source()
        cable = Cable(self.aedtapp)
        assert all(
            [
                a == b
                for a, b in zip(
                    cable.pwl_source_definitions[2]["PWLSignalParams"]["SignalValues"],
                    ["0V", "0.5V", "0V", "3V", "4V", "0V"],
                )
            ]
        )
        assert all(
            [
                a == b
                for a, b in zip(
                    cable.pwl_source_definitions[2]["PWLSignalParams"]["TimeValues"],
                    ["0ns", "1ns", "2ns", "3ns", "4ns", "5ns"],
                )
            ]
        )
        assert cable.pwl_source_definitions[2]["TDSourceAttribs"]["Name"] == "pwl4"

        cable_file1 = os.path.join(
            local_path,
            "example_models",
            test_subfloder,
            "cable_modeling_json_files",
            "add_pwl_source_noname.json",
        )
        assert Cable(self.aedtapp, cable_file1).create_pwl_source()

    def test_30_add_pwl_source_invalid(self):
        cable_file1 = os.path.join(
            local_path,
            "example_models",
            test_subfloder,
            "cable_modeling_json_files",
            "add_pwl_source_invalid.json",
        )
        assert not Cable(self.aedtapp, cable_file1).create_pwl_source()

    def test_31_add_pwl_source_invalid_1(self):
        cable_file1 = os.path.join(
            local_path,
            "example_models",
            test_subfloder,
            "cable_modeling_json_files",
            "add_pwl_source_invalid_1.json",
        )
        assert not Cable(self.aedtapp, cable_file1).create_pwl_source()

    @pytest.mark.skip(reason="Waiting for a valid .pwl file to test.")
    def test_32_add_pwl_source_from_file(self):
        cable_file1 = os.path.join(
            local_path,
            "example_models",
            test_subfloder,
            "cable_modeling_json_files",
            "add_pwl_source_from_file.json",
        )
        assert Cable(self.aedtapp, cable_file1).create_pwl_source_from_file()

    def test_33_update_pwl_source(self):
        cable_file1 = os.path.join(
            local_path,
            "example_models",
            test_subfloder,
            "cable_modeling_json_files",
            "update_pwl_source.json",
        )
        assert Cable(self.aedtapp, cable_file1).update_pwl_source()
        cable = Cable(self.aedtapp)
        assert all(
            [
                a == b
                for a, b in zip(
                    cable.pwl_source_definitions[0]["PWLSignalParams"]["SignalValues"],
                    ["0V", "0.5V", "0V", "3V", "4V", "9V", "0V"],
                )
            ]
        )
        assert all(
            [
                a == b
                for a, b in zip(
                    cable.pwl_source_definitions[0]["PWLSignalParams"]["TimeValues"],
                    ["0ns", "1ns", "2ns", "3ns", "4ns", "5ns", "6ns"],
                )
            ]
        )
        assert cable.pwl_source_definitions[0]["TDSourceAttribs"]["Name"] == "update_pwl_source"

    def test_34_remove_all_sources(self):
        assert Cable(self.aedtapp).remove_all_sources()

    def test_35_create_cables_bundle_check_new_definitions(self):
        cable_file1 = os.path.join(
            local_path,
            "example_models",
            test_subfloder,
            "cable_modeling_json_files",
            "set_bundle_cable_properties_insulation.json",
        )
        assert Cable(self.aedtapp, cable_file1).create_cable()

        cable_file1 = os.path.join(
            local_path,
            "example_models",
            test_subfloder,
            "cable_modeling_json_files",
            "add_pwl_source.json",
        )
        assert Cable(self.aedtapp, cable_file1).create_pwl_source()
        cable = Cable(self.aedtapp)
        assert len(cable.existing_sources_names) == 1
        cable_file1 = os.path.join(
            local_path,
            "example_models",
            test_subfloder,
            "cable_modeling_json_files",
            "add_clock_source.json",
        )
        assert Cable(self.aedtapp, cable_file1).create_clock_source()
        cable = Cable(self.aedtapp)
        assert cable.clock_source_definitions["TDSourceAttribs"]["Name"] == "clock_test_1"
