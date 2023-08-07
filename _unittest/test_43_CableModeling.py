import os

from _unittest.conftest import config
from _unittest.conftest import local_path
import pytest

from pyaedt.generic.DataHandlers import json_to_dict
from pyaedt.modules.CableModeling import Cable

if config["desktopVersion"] > "2022.2":
    project_name = "cable_modeling_231"
else:
    project_name = "cable_modeling"

test_subfloder = "T43"


@pytest.fixture(scope="class")
def aedtapp(add_app):
    app = add_app(project_name=project_name, design_name="HFSSDesign1", subfolder=test_subfloder)
    return app


@pytest.fixture(scope="class", autouse=True)
def dict_in(local_scratch):
    dict_in_tmp = json_to_dict(
        os.path.join(
            local_path,
            "example_models",
            test_subfloder,
            "cable_modeling_json_files",
            "set_cable_properties.json",
        )
    )
    return dict_in_tmp


@pytest.mark.skipif(config["desktopVersion"] > "2022.2", reason="AEDT Crashes")
class TestClass:
    @pytest.fixture(autouse=True)
    def init(self, aedtapp, dict_in, local_scratch):
        self.aedtapp = aedtapp
        self.dict_in = dict_in
        self.local_scratch = local_scratch

    def test_01_working_dir(self):
        Cable(self.aedtapp, self.dict_in)
        assert os.path.exists(self.aedtapp.toolkit_directory)
        assert os.path.exists(os.path.join(self.aedtapp.toolkit_directory, "export_cable_library_as_json_test.json"))

    def test_02_invalid_cable_type(self):
        self.dict_in["Add_Cable"] = "True"
        self.dict_in["Cable_prop"]["CableType"] = ""
        assert not Cable(self.aedtapp, self.dict_in).create_cable()

    def test_03_create_cables_bundle_check_definitions(self):
        # Create 1st Cable bundle - Jacket Type = Insulation
        self.dict_in["Add_Cable"] = "True"
        self.dict_in["Cable_prop"]["CableType"] = "bundle"
        self.dict_in["Cable_prop"]["IsJacketTypeInsulation"] = "True"
        self.dict_in["CableManager"]["Definitions"]["CableBundle"]["BundleParams"]["InsulationJacketParams"][
            "InsThickness"
        ] = "3.66mm"
        self.dict_in["CableManager"]["Definitions"]["CableBundle"]["BundleParams"]["InsulationJacketParams"][
            "JacketMaterial"
        ] = "pec"
        self.dict_in["CableManager"]["Definitions"]["CableBundle"]["BundleParams"]["InsulationJacketParams"][
            "InnerDiameter"
        ] = "2.88mm"
        self.dict_in["CableManager"]["Definitions"]["CableBundle"]["BundleAttribs"]["Name"] = "bundle_cable_insulation"
        assert Cable(self.aedtapp, self.dict_in).create_cable()
        cable = Cable(self.aedtapp)
        assert len(cable.cable_definitions) == 1
        assert list(cable.cable_definitions.keys())[0] == "CableBundle"
        assert cable.cable_definitions["CableBundle"]["BundleAttribs"]["Name"] == "bundle_cable_insulation"
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
        self.dict_in["CableManager"]["Definitions"]["CableBundle"]["BundleParams"]["InsulationJacketParams"][
            "JacketMaterial"
        ] = "alu"
        assert not Cable(self.aedtapp, self.dict_in).create_cable()
        self.dict_in["CableManager"]["Definitions"]["CableBundle"]["BundleParams"]["InsulationJacketParams"][
            "JacketMaterial"
        ] = ""
        # assert not Cable(self.aedtapp, self.dict_in).create_cable()
        # Create 2nd Cable bundle - Jacket Type = No Jacket
        self.dict_in["Cable_prop"]["IsJacketTypeInsulation"] = "False"
        self.dict_in["Cable_prop"]["IsJacketTypeNoJacket"] = "True"
        self.dict_in["CableManager"]["Definitions"]["CableBundle"]["BundleAttribs"]["Name"] = "Bundle_Cable_NoJacket"
        self.dict_in["CableManager"]["Definitions"]["CableBundle"]["BundleParams"]["VirtualJacketParams"][
            "JacketMaterial"
        ] = "copper"
        assert Cable(self.aedtapp, self.dict_in).create_cable()
        cable = Cable(self.aedtapp)
        assert len(cable.cable_definitions["CableBundle"]) == 2
        assert type(cable.cable_definitions["CableBundle"]) is list
        assert cable.cable_definitions["CableBundle"][1]["BundleAttribs"]["Name"] == "Bundle_Cable_NoJacket"
        assert cable.cable_definitions["CableBundle"][1]["BundleParams"].get("VirtualJacketParams")
        assert (
            cable.cable_definitions["CableBundle"][1]["BundleParams"]["VirtualJacketParams"]["JacketMaterial"] == "None"
        )
        assert (
            cable.cable_definitions["CableBundle"][1]["BundleParams"]["VirtualJacketParams"]["InnerDiameter"] == "2.5mm"
        )
        self.dict_in["CableManager"]["Definitions"]["CableBundle"]["BundleParams"]["VirtualJacketParams"][
            "JacketMaterial"
        ] = ""
        self.dict_in["CableManager"]["Definitions"]["CableBundle"]["BundleAttribs"]["Name"] = "Bundle_Cable_NoJacket_1"
        # Create 3rd Cable bundle - Jacket Type = No Jacket
        assert Cable(self.aedtapp, self.dict_in).create_cable()
        cable = Cable(self.aedtapp)
        assert (
            cable.cable_definitions["CableBundle"][2]["BundleParams"]["VirtualJacketParams"]["JacketMaterial"] == "None"
        )
        assert cable.cable_definitions["CableBundle"][2]["BundleAttribs"]["Name"] == "Bundle_Cable_NoJacket_1"
        self.dict_in["Cable_prop"]["IsJacketTypeNoJacket"] = "False"
        self.dict_in["Cable_prop"]["IsJacketTypeBraidShield"] = "True"
        self.dict_in["CableManager"]["Definitions"]["CableBundle"]["BundleParams"]["BraidShieldJacketParams"][
            "JacketMaterial"
        ] = "pec"
        self.dict_in["CableManager"]["Definitions"]["CableBundle"]["BundleParams"]["BraidShieldJacketParams"][
            "InnerDiameter"
        ] = "6mm"
        self.dict_in["CableManager"]["Definitions"]["CableBundle"]["BundleParams"]["BraidShieldJacketParams"][
            "NumCarriers"
        ] = "36"
        self.dict_in["CableManager"]["Definitions"]["CableBundle"]["BundleParams"]["BraidShieldJacketParams"][
            "NumWiresInCarrier"
        ] = "52"
        self.dict_in["CableManager"]["Definitions"]["CableBundle"]["BundleParams"]["BraidShieldJacketParams"][
            "WireDiameter"
        ] = "0.242424mm"
        self.dict_in["CableManager"]["Definitions"]["CableBundle"]["BundleParams"]["BraidShieldJacketParams"][
            "WeaveAngle"
        ] = "33deg"
        self.dict_in["CableManager"]["Definitions"]["CableBundle"]["BundleAttribs"]["Name"] = "Bundle_Cable_Shielding"
        # Create 4th Cable bundle - Jacket Type = Shielding
        assert Cable(self.aedtapp, self.dict_in).create_cable()
        cable = Cable(self.aedtapp)
        assert len(cable.cable_definitions["CableBundle"]) == 4
        assert type(cable.cable_definitions["CableBundle"]) is list
        assert cable.cable_definitions["CableBundle"][3]["BundleAttribs"]["Name"] == "Bundle_Cable_Shielding"
        assert cable.cable_definitions["CableBundle"][3]["BundleParams"].get("BraidShieldJacketParams")
        assert (
            cable.cable_definitions["CableBundle"][3]["BundleParams"]["BraidShieldJacketParams"]["JacketMaterial"]
            == "pec"
        )
        assert (
            cable.cable_definitions["CableBundle"][3]["BundleParams"]["BraidShieldJacketParams"]["InnerDiameter"]
            == "6mm"
        )
        assert (
            cable.cable_definitions["CableBundle"][3]["BundleParams"]["BraidShieldJacketParams"]["NumCarriers"] == "36"
        )
        assert (
            cable.cable_definitions["CableBundle"][3]["BundleParams"]["BraidShieldJacketParams"]["NumWiresInCarrier"]
            == "52"
        )
        assert (
            cable.cable_definitions["CableBundle"][3]["BundleParams"]["BraidShieldJacketParams"]["WireDiameter"]
            == "0.242424mm"
        )
        assert (
            cable.cable_definitions["CableBundle"][3]["BundleParams"]["BraidShieldJacketParams"]["WeaveAngle"]
            == "33deg"
        )
        self.dict_in["CableManager"]["Definitions"]["CableBundle"]["BundleParams"]["BraidShieldJacketParams"][
            "InnerDiameter"
        ] = ""
        # assert not Cable(self.aedtapp, self.dict_in).create_cable()
        self.dict_in["CableManager"]["Definitions"]["CableBundle"]["BundleParams"]["BraidShieldJacketParams"][
            "JacketMaterial"
        ] = "alu"
        # assert not Cable(self.aedtapp, self.dict_in).create_cable()
        self.dict_in["Cable_prop"]["IsJacketTypeNoJacket"] = "True"
        # assert not Cable(self.aedtapp, self.dict_in).create_cable()
        # for cable harness
        self.dict_in["Cable_prop"]["IsJacketTypeBraidShield"] = "False"
        self.dict_in["Cable_prop"]["IsJacketTypeNoJacket"] = "False"
        self.dict_in["Cable_prop"]["IsJacketTypeInsulation"] = "True"
        self.dict_in["CableManager"]["Definitions"]["CableBundle"]["BundleAttribs"]["Name"] = "bundle1"
        assert Cable(self.aedtapp, self.dict_in).create_cable()

    def test_04_update_cables_bundle_check_definitions(self):
        # Update 1st cable bundle - Jacket type = Insulation
        self.dict_in["Cable_prop"]["IsJacketTypeNoJacket"] = "False"
        self.dict_in["Cable_prop"]["IsJacketTypeBraidShield"] = "False"
        self.dict_in["Cable_prop"]["IsJacketTypeInsulation"] = "True"
        self.dict_in["CableManager"]["Definitions"]["CableBundle"]["BundleAttribs"]["Name"] = "bundle_cable_insulation"
        self.dict_in["Update_Cable"] = "True"
        self.dict_in["Cable_prop"]["UpdatedName"] = "New_updated_name_cable_bundle_insulation"
        self.dict_in["CableManager"]["Definitions"]["CableBundle"]["BundleParams"]["InsulationJacketParams"][
            "JacketMaterial"
        ] = "pec"
        assert Cable(self.aedtapp, self.dict_in).update_cable_properties()
        cable = Cable(self.aedtapp)
        assert cable.cable_definitions["CableBundle"][0]["BundleParams"].get("InsulationJacketParams")
        assert (
            cable.cable_definitions["CableBundle"][0]["BundleParams"]["InsulationJacketParams"]["InsThickness"]
            == "3.66mm"
        )
        assert (
            cable.cable_definitions["CableBundle"][0]["BundleParams"]["InsulationJacketParams"]["JacketMaterial"]
            == "pec"
        )
        assert (
            cable.cable_definitions["CableBundle"][0]["BundleParams"]["InsulationJacketParams"]["InnerDiameter"]
            == "2.88mm"
        )
        assert (
            cable.cable_definitions["CableBundle"][0]["BundleAttribs"]["Name"]
            == "New_updated_name_cable_bundle_insulation"
        )
        # Update 1st cable bundle - Jacket type = Insulation
        self.dict_in["CableManager"]["Definitions"]["CableBundle"]["BundleParams"]["InsulationJacketParams"][
            "InsThickness"
        ] = "5mm"
        self.dict_in["CableManager"]["Definitions"]["CableBundle"]["BundleParams"]["InsulationJacketParams"][
            "JacketMaterial"
        ] = "pec"
        self.dict_in["CableManager"]["Definitions"]["CableBundle"]["BundleParams"]["InsulationJacketParams"][
            "InnerDiameter"
        ] = "3mm"
        self.dict_in["CableManager"]["Definitions"]["CableBundle"]["BundleAttribs"][
            "Name"
        ] = "New_updated_name_cable_bundle_insulation"
        self.dict_in["Cable_prop"]["UpdatedName"] = "New_updated_name_cable_bundle_insulation_1"
        assert Cable(self.aedtapp, self.dict_in).update_cable_properties()
        cable = Cable(self.aedtapp)
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
        # Update 1st cable bundle - Jacket type = Insulation
        self.dict_in["CableManager"]["Definitions"]["CableBundle"]["BundleParams"]["InsulationJacketParams"][
            "JacketMaterial"
        ] = "alu"
        assert not Cable(self.aedtapp, self.dict_in).update_cable_properties()
        # Update 3rd cable bundle - Jacket type = No Jacket
        self.dict_in["Cable_prop"]["IsJacketTypeNoJacket"] = "True"
        self.dict_in["Cable_prop"]["IsJacketTypeBraidShield"] = "False"
        self.dict_in["Cable_prop"]["IsJacketTypeInsulation"] = "False"
        self.dict_in["Update_Cable"] = "True"
        self.dict_in["CableManager"]["Definitions"]["CableBundle"]["BundleAttribs"]["Name"] = "Bundle_Cable_NoJacket_1"
        self.dict_in["Cable_prop"]["UpdatedName"] = "New_updated_name_cable_bundle_no_jacket"
        assert Cable(self.aedtapp, self.dict_in).update_cable_properties()
        cable = Cable(self.aedtapp)
        assert (
            cable.cable_definitions["CableBundle"][2]["BundleParams"]["VirtualJacketParams"]["JacketMaterial"] == "None"
        )
        assert (
            cable.cable_definitions["CableBundle"][2]["BundleParams"]["VirtualJacketParams"]["InnerDiameter"] == "2.5mm"
        )
        self.dict_in["Cable_prop"]["UpdatedName"] = ""
        assert not Cable(self.aedtapp, self.dict_in).update_cable_properties()
        # Update 4th cable bundle - Jacket type = Shielding - Name
        self.dict_in["Cable_prop"]["IsJacketTypeNoJacket"] = "False"
        self.dict_in["Cable_prop"]["IsJacketTypeBraidShield"] = "True"
        self.dict_in["Cable_prop"]["IsJacketTypeInsulation"] = "False"
        self.dict_in["Update_Cable"] = "True"
        self.dict_in["CableManager"]["Definitions"]["CableBundle"]["BundleAttribs"]["Name"] = "Bundle_Cable_Shielding"
        self.dict_in["Cable_prop"]["UpdatedName"] = "New_updated_name_cable_bundle_shielding"
        Cable(self.aedtapp, self.dict_in).update_shielding()
        cable = Cable(self.aedtapp, self.dict_in)
        assert (
            cable.cable_definitions["CableBundle"][3]["BundleAttribs"]["Name"]
            == "New_updated_name_cable_bundle_shielding"
        )
        assert cable.cable_definitions["CableBundle"][3]["BundleParams"].get("BraidShieldJacketParams")
        assert (
            cable.cable_definitions["CableBundle"][3]["BundleParams"]["BraidShieldJacketParams"]["JacketMaterial"]
            == "copper"
        )
        assert (
            cable.cable_definitions["CableBundle"][3]["BundleParams"]["BraidShieldJacketParams"]["InnerDiameter"]
            == "2.5mm"
        )
        assert (
            cable.cable_definitions["CableBundle"][3]["BundleParams"]["BraidShieldJacketParams"]["NumCarriers"] == "2"
        )
        assert (
            cable.cable_definitions["CableBundle"][3]["BundleParams"]["BraidShieldJacketParams"]["NumWiresInCarrier"]
            == "5"
        )
        assert (
            cable.cable_definitions["CableBundle"][3]["BundleParams"]["BraidShieldJacketParams"]["WireDiameter"]
            == "0.1mm"
        )
        assert (
            cable.cable_definitions["CableBundle"][3]["BundleParams"]["BraidShieldJacketParams"]["WeaveAngle"]
            == "30deg"
        )
        # Update 4th cable bundle - Jacket type = Shielding - Properties
        self.dict_in["CableManager"]["Definitions"]["CableBundle"]["BundleParams"]["BraidShieldJacketParams"][
            "JacketMaterial"
        ] = "pec"
        self.dict_in["CableManager"]["Definitions"]["CableBundle"]["BundleParams"]["BraidShieldJacketParams"][
            "InnerDiameter"
        ] = "10mm"
        self.dict_in["CableManager"]["Definitions"]["CableBundle"]["BundleParams"]["BraidShieldJacketParams"][
            "NumCarriers"
        ] = "22"
        self.dict_in["CableManager"]["Definitions"]["CableBundle"]["BundleParams"]["BraidShieldJacketParams"][
            "NumWiresInCarrier"
        ] = "23"
        self.dict_in["CableManager"]["Definitions"]["CableBundle"]["BundleParams"]["BraidShieldJacketParams"][
            "WireDiameter"
        ] = "0.212mm"
        self.dict_in["CableManager"]["Definitions"]["CableBundle"]["BundleParams"]["BraidShieldJacketParams"][
            "WeaveAngle"
        ] = "35deg"
        self.dict_in["CableManager"]["Definitions"]["CableBundle"]["BundleAttribs"][
            "Name"
        ] = "New_updated_name_cable_bundle_shielding"
        self.dict_in["Cable_prop"]["UpdatedName"] = "New_updated_name_cable_bundle_shielding_1"
        assert Cable(self.aedtapp, self.dict_in).update_shielding()
        cable = Cable(self.aedtapp, self.dict_in)
        assert (
            cable.cable_definitions["CableBundle"][3]["BundleParams"]["BraidShieldJacketParams"]["JacketMaterial"]
            == "pec"
        )
        assert (
            cable.cable_definitions["CableBundle"][3]["BundleParams"]["BraidShieldJacketParams"]["InnerDiameter"]
            == "10mm"
        )
        assert (
            cable.cable_definitions["CableBundle"][3]["BundleParams"]["BraidShieldJacketParams"]["NumCarriers"] == "22"
        )
        assert (
            cable.cable_definitions["CableBundle"][3]["BundleParams"]["BraidShieldJacketParams"]["NumWiresInCarrier"]
            == "23"
        )
        assert (
            cable.cable_definitions["CableBundle"][3]["BundleParams"]["BraidShieldJacketParams"]["WireDiameter"]
            == "0.212mm"
        )
        assert (
            cable.cable_definitions["CableBundle"][3]["BundleParams"]["BraidShieldJacketParams"]["WeaveAngle"]
            == "35deg"
        )
        self.dict_in["CableManager"]["Definitions"]["CableBundle"]["BundleParams"]["BraidShieldJacketParams"][
            "JacketMaterial"
        ] = "alu"
        assert not Cable(self.aedtapp, self.dict_in).update_shielding()

    def test_05_create_cables_straight_wire_check_definitions(self):
        # Create 1st straight wire cable
        self.dict_in["Add_Cable"] = "True"
        self.dict_in["Cable_prop"]["CableType"] = "straight wire"
        self.dict_in["Update_Cable"] = "False"
        self.dict_in["CableManager"]["Definitions"]["StWireCable"]["StWireParams"]["WireStandard"] = "ISO"
        self.dict_in["CableManager"]["Definitions"]["StWireCable"]["StWireParams"]["WireGauge"] = "2.5"
        self.dict_in["CableManager"]["Definitions"]["StWireCable"]["StWireParams"]["CondDiameter"] = "10mm"
        self.dict_in["CableManager"]["Definitions"]["StWireCable"]["StWireParams"]["CondMaterial"] = "pec"
        self.dict_in["CableManager"]["Definitions"]["StWireCable"]["StWireParams"]["InsThickness"] = "0.9mm"
        self.dict_in["CableManager"]["Definitions"]["StWireCable"]["StWireParams"]["InsMaterial"] = "copper"
        self.dict_in["CableManager"]["Definitions"]["StWireCable"]["StWireParams"]["InsType"] = "Thin Wall"
        self.dict_in["CableManager"]["Definitions"]["StWireCable"]["StWireAttribs"]["Name"] = "straight_wire_cable"
        assert Cable(self.aedtapp, self.dict_in).create_cable()
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
        # for cable harness
        self.dict_in["CableManager"]["Definitions"]["StWireCable"]["StWireAttribs"]["Name"] = "stwire1"
        assert Cable(self.aedtapp, self.dict_in).create_cable()
        self.dict_in["CableManager"]["Definitions"]["StWireCable"]["StWireAttribs"]["Name"] = "stwire2"
        assert Cable(self.aedtapp, self.dict_in).create_cable()
        self.dict_in["CableManager"]["Definitions"]["StWireCable"]["StWireAttribs"]["Name"] = "stwire3"
        assert Cable(self.aedtapp, self.dict_in).create_cable()

    @pytest.mark.skip(reason="Unable to update if it's not done before manually.")
    def test_06_update_cables_straight_wire_check_definitions(self):
        self.dict_in["Update_Cable"] = "True"
        self.dict_in["Cable_prop"]["UpdatedName"] = "New_updated_name_cable_straight_wire"
        self.dict_in["CableManager"]["Definitions"]["StWireCable"]["StWireParams"]["WireStandard"] = "ISO"
        self.dict_in["CableManager"]["Definitions"]["StWireCable"]["StWireParams"]["WireGauge"] = "0.13"
        self.dict_in["CableManager"]["Definitions"]["StWireCable"]["StWireParams"]["CondDiameter"] = "0.5mm"
        self.dict_in["CableManager"]["Definitions"]["StWireCable"]["StWireParams"]["CondMaterial"] = "pec"
        self.dict_in["CableManager"]["Definitions"]["StWireCable"]["StWireParams"]["InsThickness"] = "0.25mm"
        self.dict_in["CableManager"]["Definitions"]["StWireCable"]["StWireParams"]["InsMaterial"] = "copper"
        self.dict_in["CableManager"]["Definitions"]["StWireCable"]["StWireParams"]["InsType"] = "Thin Wall"
        self.dict_in["CableManager"]["Definitions"]["StWireCable"]["StWireAttribs"]["Name"] = "straight_wire_cable"
        assert Cable(self.aedtapp, self.dict_in).update_cable_properties()
        cable = Cable(self.aedtapp)
        assert cable.cable_definitions["StWireCable"]
        assert cable.cable_definitions["StWireCable"]["StWireAttribs"]["Name"] == "New_updated_name_cable_straight_wire"
        assert cable.cable_definitions["StWireCable"]["StWireParams"]["WireStandard"] == "ISO"
        assert cable.cable_definitions["StWireCable"]["StWireParams"]["WireGauge"] == "0.13"
        assert cable.cable_definitions["StWireCable"]["StWireParams"]["CondDiameter"] == "0.5mm"
        assert cable.cable_definitions["StWireCable"]["StWireParams"]["CondMaterial"] == "pec"
        assert cable.cable_definitions["StWireCable"]["StWireParams"]["InsThickness"] == "0.25mm"
        assert cable.cable_definitions["StWireCable"]["StWireParams"]["InsMaterial"] == "copper"
        assert cable.cable_definitions["StWireCable"]["StWireParams"]["InsType"] == "Thin Wall"

    def test_07_create_cables_twisted_pair_check_definitions(self):
        self.dict_in["Add_Cable"] = "True"
        self.dict_in["Cable_prop"]["CableType"] = "twisted pair"
        self.dict_in["Update_Cable"] = "False"
        self.dict_in["CableManager"]["Definitions"]["TwistedPairCable"]["TwistedPairParams"][
            "StraightWireCableID"
        ] = 1025
        self.dict_in["CableManager"]["Definitions"]["TwistedPairCable"]["TwistedPairParams"][
            "IsLayLengthSpecified"
        ] = "False"
        self.dict_in["CableManager"]["Definitions"]["TwistedPairCable"]["TwistedPairParams"]["LayLength"] = "34mm"
        self.dict_in["CableManager"]["Definitions"]["TwistedPairCable"]["TwistedPairParams"]["TurnsPerMeter"] = "99"
        self.dict_in["CableManager"]["Definitions"]["TwistedPairCable"]["TwistedPairAttribs"][
            "Name"
        ] = "twisted_pair_cable"
        assert Cable(self.aedtapp, self.dict_in).create_cable()
        cable = Cable(self.aedtapp)
        assert cable.cable_definitions["TwistedPairCable"]
        assert cable.cable_definitions["TwistedPairCable"]["TwistedPairAttribs"]["Name"] == "twisted_pair_cable"
        assert cable.cable_definitions["TwistedPairCable"]["TwistedPairParams"]
        assert cable.cable_definitions["TwistedPairCable"]["TwistedPairParams"]["StraightWireCableID"] == 1025
        assert not cable.cable_definitions["TwistedPairCable"]["TwistedPairParams"]["IsLayLengthSpecified"]
        assert cable.cable_definitions["TwistedPairCable"]["TwistedPairParams"]["LayLength"] == "0mm"
        assert cable.cable_definitions["TwistedPairCable"]["TwistedPairParams"]["TurnsPerMeter"] == "99"
        self.dict_in["CableManager"]["Definitions"]["TwistedPairCable"]["TwistedPairParams"][
            "IsLayLengthSpecified"
        ] = {}
        assert not Cable(self.aedtapp, self.dict_in).create_cable()
        self.dict_in["CableManager"]["Definitions"]["TwistedPairCable"]["TwistedPairAttribs"][
            "Name"
        ] = "twisted_pair_cable_1"
        self.dict_in["CableManager"]["Definitions"]["TwistedPairCable"]["TwistedPairParams"][
            "IsLayLengthSpecified"
        ] = "True"
        self.dict_in["CableManager"]["Definitions"]["TwistedPairCable"]["TwistedPairParams"]["LayLength"] = "34mm"
        assert Cable(self.aedtapp, self.dict_in).create_cable()
        cable = Cable(self.aedtapp, self.dict_in)
        assert cable.cable_definitions["TwistedPairCable"][1]["TwistedPairAttribs"]["Name"] == "twisted_pair_cable_1"
        assert cable.cable_definitions["TwistedPairCable"][1]["TwistedPairParams"]["IsLayLengthSpecified"]
        assert cable.cable_definitions["TwistedPairCable"][1]["TwistedPairParams"]["LayLength"] == "34mm"

    def test_08_update_cables_twisted_pair_check_definitions(self):
        self.dict_in["Update_Cable"] = "True"
        self.dict_in["Cable_prop"]["UpdatedName"] = "New_updated_name_cable_twisted_pair"
        self.dict_in["CableManager"]["Definitions"]["TwistedPairCable"]["TwistedPairParams"][
            "StraightWireCableID"
        ] = 1025
        self.dict_in["CableManager"]["Definitions"]["TwistedPairCable"]["TwistedPairParams"][
            "IsLayLengthSpecified"
        ] = "True"
        self.dict_in["CableManager"]["Definitions"]["TwistedPairCable"]["TwistedPairParams"]["LayLength"] = "47mm"
        self.dict_in["CableManager"]["Definitions"]["TwistedPairCable"]["TwistedPairParams"]["TurnsPerMeter"] = "97"
        self.dict_in["CableManager"]["Definitions"]["TwistedPairCable"]["TwistedPairAttribs"][
            "Name"
        ] = "twisted_pair_cable_1"
        assert Cable(self.aedtapp, self.dict_in).update_cable_properties()
        cable = Cable(self.aedtapp)
        assert (
            cable.cable_definitions["TwistedPairCable"][1]["TwistedPairAttribs"]["Name"]
            == "New_updated_name_cable_twisted_pair"
        )
        assert cable.cable_definitions["TwistedPairCable"][1]["TwistedPairParams"]["StraightWireCableID"] == 1025
        assert cable.cable_definitions["TwistedPairCable"][1]["TwistedPairParams"]["IsLayLengthSpecified"]
        assert cable.cable_definitions["TwistedPairCable"][1]["TwistedPairParams"]["LayLength"] == "47mm"
        assert cable.cable_definitions["TwistedPairCable"][1]["TwistedPairParams"]["TurnsPerMeter"] == "97"

    def test_09_add_cables_to_bundle(self):
        self.dict_in["Add_Cable"] = "False"
        self.dict_in["Update_Cable"] = "False"
        self.dict_in["Add_CablesToBundle"] = "True"
        self.dict_in["CablesToBundle_prop"]["CablesToAdd"] = "straight_wire_cable"
        self.dict_in["CablesToBundle_prop"]["BundleCable"] = "New_updated_name_cable_bundle_insulation_1"
        self.dict_in["CablesToBundle_prop"]["NumberOfCableToAdd"] = 3
        assert Cable(self.aedtapp, self.dict_in).add_cable_to_bundle()
        cable = Cable(self.aedtapp, self.dict_in)
        assert cable.cable_definitions["CableBundle"][0]["Instances"]["StWireInstance"]
        assert len(cable.cable_definitions["CableBundle"][0]["Instances"]["StWireInstance"]) == 3
        self.dict_in["CablesToBundle_prop"]["NumberOfCableToAdd"] = ""
        assert Cable(self.aedtapp, self.dict_in).add_cable_to_bundle()
        cable = Cable(self.aedtapp, self.dict_in)
        assert len(cable.cable_definitions["CableBundle"][0]["Instances"]["StWireInstance"]) == 5
        self.dict_in["CablesToBundle_prop"]["BundleCable"] = "New_updated_name_cable_bundle_insulation_"
        assert not Cable(self.aedtapp, self.dict_in).add_cable_to_bundle()
        # for cable harness
        self.dict_in["CablesToBundle_prop"]["CablesToAdd"] = ["stwire1", "stwire2", "stwire3"]
        self.dict_in["CablesToBundle_prop"]["BundleCable"] = "bundle1"
        self.dict_in["CablesToBundle_prop"]["NumberOfCableToAdd"] = 3
        assert Cable(self.aedtapp, self.dict_in).add_cable_to_bundle()

    def test_10_remove_cables(self):
        self.dict_in["Add_Cable"] = "False"
        self.dict_in["Update_Cable"] = "False"
        self.dict_in["Add_CablesToBundle"] = "False"
        self.dict_in["Remove_Cable"] = "True"
        self.dict_in["Cable_prop"]["CablesToRemove"] = "New_updated_name_cable_bundle_no_jacket"
        assert Cable(self.aedtapp, self.dict_in).remove_cables()
        self.dict_in["Cable_prop"]["CablesToRemove"] = ["abc", "cd"]
        assert not Cable(self.aedtapp, self.dict_in).remove_cables()

    def test_11_add_clock_source(self):
        self.dict_in["Add_Cable"] = "False"
        self.dict_in["Update_Cable"] = "False"
        self.dict_in["Add_CablesToBundle"] = "False"
        self.dict_in["Remove_Cable"] = "False"
        self.dict_in["Add_Source"] = "True"
        self.dict_in["Source_prop"]["AddClockSource"] = "True"
        self.dict_in["CableManager"]["TDSources"]["ClockSourceDef"]["ClockSignalParams"]["Period"] = "40us"
        self.dict_in["CableManager"]["TDSources"]["ClockSourceDef"]["ClockSignalParams"]["LowPulseVal"] = "0.1V"
        self.dict_in["CableManager"]["TDSources"]["ClockSourceDef"]["ClockSignalParams"]["HighPulseVal"] = "2V"
        self.dict_in["CableManager"]["TDSources"]["ClockSourceDef"]["ClockSignalParams"]["Risetime"] = "5us"
        self.dict_in["CableManager"]["TDSources"]["ClockSourceDef"]["ClockSignalParams"]["Falltime"] = "10us"
        self.dict_in["CableManager"]["TDSources"]["ClockSourceDef"]["ClockSignalParams"]["PulseWidth"] = "23us"
        self.dict_in["CableManager"]["TDSources"]["ClockSourceDef"]["TDSourceAttribs"]["Name"] = "clock_test_1"
        assert Cable(self.aedtapp, self.dict_in).create_clock_source()
        cable = Cable(self.aedtapp)
        assert len(cable.clock_source_definitions) == 3
        assert cable.clock_source_definitions[2]["ClockSignalParams"]["Period"] == "40us"
        assert cable.clock_source_definitions[2]["ClockSignalParams"]["LowPulseVal"] == "0.1V"
        assert cable.clock_source_definitions[2]["ClockSignalParams"]["HighPulseVal"] == "2V"
        assert cable.clock_source_definitions[2]["ClockSignalParams"]["Risetime"] == "5us"
        assert cable.clock_source_definitions[2]["ClockSignalParams"]["Falltime"] == "10us"
        assert cable.clock_source_definitions[2]["ClockSignalParams"]["PulseWidth"] == "23us"
        assert cable.clock_source_definitions[2]["TDSourceAttribs"]["Name"] == "clock_test_1"
        self.dict_in["CableManager"]["TDSources"]["ClockSourceDef"]["TDSourceAttribs"]["Name"] = ""
        assert Cable(self.aedtapp, self.dict_in).create_clock_source()
        self.dict_in["CableManager"]["TDSources"]["ClockSourceDef"]["ClockSignalParams"]["Period"] = "40u"
        assert not Cable(self.aedtapp, self.dict_in).create_clock_source()
        self.dict_in["CableManager"]["TDSources"]["ClockSourceDef"]["ClockSignalParams"]["LowPulseVal"] == "0.1voltage"
        assert not Cable(self.aedtapp, self.dict_in).create_clock_source()
        self.dict_in["CableManager"]["TDSources"]["ClockSourceDef"]["ClockSignalParams"]["HighPulseVal"] = "2voltage"
        assert not Cable(self.aedtapp, self.dict_in).create_clock_source()
        self.dict_in["CableManager"]["TDSources"]["ClockSourceDef"]["ClockSignalParams"]["Risetime"] = "5u"
        assert not Cable(self.aedtapp, self.dict_in).create_clock_source()
        self.dict_in["CableManager"]["TDSources"]["ClockSourceDef"]["ClockSignalParams"]["Falltime"] = "10u"
        assert not Cable(self.aedtapp, self.dict_in).create_clock_source()
        self.dict_in["CableManager"]["TDSources"]["ClockSourceDef"]["ClockSignalParams"]["PulseWidth"] = "23u"
        assert not Cable(self.aedtapp, self.dict_in).create_clock_source()

    def test_12_update_clock_source(self):
        self.dict_in["Add_Source"] = "False"
        self.dict_in["Update_Source"] = "True"
        self.dict_in["Source_prop"]["UpdateClockSource"] = "True"
        self.dict_in["Source_prop"]["UpdatedSourceName"] = "update_clock_test_1"
        self.dict_in["CableManager"]["TDSources"]["ClockSourceDef"]["TDSourceAttribs"]["Name"] = "clock_test_1"
        self.dict_in["CableManager"]["TDSources"]["ClockSourceDef"]["ClockSignalParams"]["Period"] = "45us"
        self.dict_in["CableManager"]["TDSources"]["ClockSourceDef"]["ClockSignalParams"]["LowPulseVal"] = "0.3V"
        self.dict_in["CableManager"]["TDSources"]["ClockSourceDef"]["ClockSignalParams"]["HighPulseVal"] = "3V"
        self.dict_in["CableManager"]["TDSources"]["ClockSourceDef"]["ClockSignalParams"]["Risetime"] = "4us"
        self.dict_in["CableManager"]["TDSources"]["ClockSourceDef"]["ClockSignalParams"]["Falltime"] = "15us"
        self.dict_in["CableManager"]["TDSources"]["ClockSourceDef"]["ClockSignalParams"]["PulseWidth"] = "26us"
        assert Cable(self.aedtapp, self.dict_in).update_clock_source()
        cable = Cable(self.aedtapp)
        assert cable.clock_source_definitions[2]["TDSourceAttribs"]["Name"] == "update_clock_test_1"
        assert cable.clock_source_definitions[2]["ClockSignalParams"]["Period"] == "45us"
        assert cable.clock_source_definitions[2]["ClockSignalParams"]["LowPulseVal"] == "0.3V"
        assert cable.clock_source_definitions[2]["ClockSignalParams"]["HighPulseVal"] == "3V"
        assert cable.clock_source_definitions[2]["ClockSignalParams"]["Risetime"] == "4us"
        assert cable.clock_source_definitions[2]["ClockSignalParams"]["Falltime"] == "15us"
        assert cable.clock_source_definitions[2]["ClockSignalParams"]["PulseWidth"] == "26us"
        self.dict_in["Add_Source"] = "True"
        self.dict_in["Update_Source"] = "True"
        assert not Cable(self.aedtapp, self.dict_in).update_clock_source()
        self.dict_in["Source_prop"]["AddClockSource"] = "True"
        self.dict_in["Source_prop"]["UpdateClockSource"] = "True"
        assert not Cable(self.aedtapp, self.dict_in).update_clock_source()
        self.dict_in["CableManager"]["TDSources"]["ClockSourceDef"]["TDSourceAttribs"]["Name"] = ""
        assert not Cable(self.aedtapp, self.dict_in).update_clock_source()

    def test_13_add_pwl_source(self):
        self.dict_in["Add_Cable"] = "False"
        self.dict_in["Update_Cable"] = "False"
        self.dict_in["Add_CablesToBundle"] = "False"
        self.dict_in["Remove_Cable"] = "False"
        self.dict_in["Add_Source"] = "True"
        self.dict_in["Update_Source"] = "False"
        self.dict_in["Source_prop"]["AddClockSource"] = "False"
        self.dict_in["Source_prop"]["AddPwlSource"] = "True"
        self.dict_in["CableManager"]["TDSources"]["PWLSourceDef"]["PWLSignalParams"]["SignalValues"] = [
            "0V",
            "0.5V",
            "0V",
            "3V",
            "4V",
            "0V",
        ]
        self.dict_in["CableManager"]["TDSources"]["PWLSourceDef"]["PWLSignalParams"]["TimeValues"] = [
            "0ns",
            "1ns",
            "2ns",
            "3ns",
            "4ns",
            "5ns",
        ]
        self.dict_in["CableManager"]["TDSources"]["PWLSourceDef"]["TDSourceAttribs"]["Name"] = "pwl4"
        assert Cable(self.aedtapp, self.dict_in).create_pwl_source()
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
        self.dict_in["CableManager"]["TDSources"]["PWLSourceDef"]["PWLSignalParams"]["SignalValues"] = [
            "0V",
            "0.5V",
            "0V",
            "3V",
            "4V",
            "1V",
        ]
        assert not Cable(self.aedtapp, self.dict_in).create_pwl_source()
        self.dict_in["CableManager"]["TDSources"]["PWLSourceDef"]["TDSourceAttribs"] = {}
        assert not Cable(self.aedtapp, self.dict_in).create_pwl_source()
        self.dict_in["Add_Source"] = "False"
        self.dict_in["Update_Source"] = "True"
        self.dict_in["Source_prop"]["AddClockSource"] = "False"
        self.dict_in["Source_prop"]["AddPwlSource"] = "False"
        self.dict_in["Source_prop"]["UpdateClockSource"] = "False"
        self.dict_in["Source_prop"]["UpdatePwlSource"] = "True"
        self.dict_in["Source_prop"]["UpdatedSourceName"] = "update_pwl_source"
        self.dict_in["CableManager"]["TDSources"]["PWLSourceDef"]["PWLSignalParams"]["SignalValues"] = [
            "0V",
            "0.5V",
            "0V",
            "3V",
            "4V",
            "9V",
            "0V",
        ]
        self.dict_in["CableManager"]["TDSources"]["PWLSourceDef"]["PWLSignalParams"]["TimeValues"] = [
            "0ns",
            "1ns",
            "2ns",
            "3ns",
            "4ns",
            "5ns",
            "6ns",
        ]
        self.dict_in["CableManager"]["TDSources"]["PWLSourceDef"]["TDSourceAttribs"]["Name"] = "pwl1"
        self.dict_in["Source_prop"]["UpdatedSourceName"] = "updated_pwl1"
        assert Cable(self.aedtapp, self.dict_in).update_pwl_source()
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
        assert cable.pwl_source_definitions[0]["TDSourceAttribs"]["Name"] == "updated_pwl1"
        self.dict_in["Add_Source"] = "True"
        self.dict_in["Update_Source"] = "False"
        self.dict_in["Source_prop"]["AddClockSource"] = "False"
        self.dict_in["Source_prop"]["AddPwlSource"] = "True"
        self.dict_in["Source_prop"]["AddPwlSourceFromFile"] = os.path.join(
            local_path, "example_models", "T43", "cable_modeling_json_files", "import_pwl.pwl"
        )
        self.dict_in["Source_prop"]["UpdateClockSource"] = "False"
        self.dict_in["Source_prop"]["UpdatePwlSource"] = "False"
        assert Cable(self.aedtapp, self.dict_in).create_pwl_source_from_file()
        self.dict_in["Source_prop"]["AddPwlSourceFromFile"] = os.path.join(
            local_path, "example_models", "T43", "cable_modeling_json_files", "import_pwl.doc"
        )
        assert Cable(self.aedtapp, self.dict_in).create_pwl_source_from_file()
        self.dict_in["Source_prop"]["AddPwlSourceFromFile"] = os.path.join(
            local_path, "example_models", "T43", "cable_modeling_json_files", "import_pwl.txt"
        )
        assert not Cable(self.aedtapp, self.dict_in).create_pwl_source_from_file()

    def test_14_remove_source(self):
        self.dict_in["Add_Cable"] = "False"
        self.dict_in["Update_Cable"] = "False"
        self.dict_in["Add_CablesToBundle"] = "False"
        self.dict_in["Remove_Cable"] = "False"
        self.dict_in["Add_Source"] = "False"
        self.dict_in["Update_Source"] = "False"
        self.dict_in["Remove_Source"] = "True"
        self.dict_in["Source_prop"]["AddClockSource"] = "False"
        self.dict_in["Source_prop"]["AddPwlSource"] = "False"
        self.dict_in["Source_prop"]["SourcesToRemove"] = "update_clock_test_1"
        assert Cable(self.aedtapp, self.dict_in).remove_source()
        cable = Cable(self.aedtapp)
        assert len(cable.clock_source_definitions) == 3
        self.dict_in["Source_prop"]["SourcesToRemove"] = "non_existing_source"
        assert not Cable(self.aedtapp, self.dict_in).remove_source()

    def test_15_add_cable_harness(self):
        self.dict_in["Add_Cable"] = "False"
        self.dict_in["Update_Cable"] = "False"
        self.dict_in["Add_CablesToBundle"] = "False"
        self.dict_in["Remove_Cable"] = "False"
        self.dict_in["Add_Source"] = "False"
        self.dict_in["Update_Source"] = "False"
        self.dict_in["Remove_Source"] = "False"
        self.dict_in["Add_CableHarness"] = "True"
        self.dict_in["CableHarness_prop"]["Name"] = "cable_harness_test"
        self.dict_in["CableHarness_prop"]["Bundle"] = "bundle1"
        self.dict_in["CableHarness_prop"]["TwistAngleAlongRoute"] = "20deg"
        self.dict_in["CableHarness_prop"]["Polyline"] = "polyline1"
        self.dict_in["CableHarness_prop"]["AutoOrient"] = "False"
        self.dict_in["CableHarness_prop"]["XAxis"] = "Undefined"
        self.dict_in["CableHarness_prop"]["XAxisOrigin"] = ["0mm", "0mm", "0mm"]
        self.dict_in["CableHarness_prop"]["XAxisEnd"] = ["0mm", "0mm", "0mm"]
        self.dict_in["CableHarness_prop"]["ReverseYAxisDirection"] = "True"
        assert Cable(self.aedtapp, self.dict_in).create_cable_harness()
        self.dict_in["CableHarness_prop"]["Bundle"] = "New_updated_name_cable_bundle_insulation_1"
        self.dict_in["CableHarness_prop"]["CableTerminationsToInclude"][0]["CableName"] = "straight_wire_cable"
        self.dict_in["CableHarness_prop"]["CableTerminationsToInclude"][1]["CableName"] = "straight_wire_cable1"
        self.dict_in["CableHarness_prop"]["CableTerminationsToInclude"][2]["CableName"] = "straight_wire_cable2"
        self.dict_in["CableHarness_prop"]["Name"] = "cable_harness_test_1"
        assert Cable(self.aedtapp, self.dict_in).create_cable_harness()
        self.dict_in["CableHarness_prop"]["Name"] = ""
        assert Cable(self.aedtapp, self.dict_in).create_cable_harness()
        self.dict_in["CableHarness_prop"]["XAxis"] = "NewVector"
        self.dict_in["CableHarness_prop"]["XAxisOrigin"] = ["1mm", "2mm", "3mm"]
        self.dict_in["CableHarness_prop"]["XAxisEnd"] = ["4mm", "5mm", "6mm"]
        assert Cable(self.aedtapp, self.dict_in).create_cable_harness()
        self.dict_in["CableHarness_prop"]["Bundle"] = "non_existing_bundle"
        assert not Cable(self.aedtapp, self.dict_in).create_cable_harness()
        self.dict_in["CableHarness_prop"]["Bundle"] = "bundle1"
        self.dict_in["CableHarness_prop"]["Name"] = ""
        self.dict_in["CableHarness_prop"]["TwistAngleAlongRoute"] = "20de"
        assert not Cable(self.aedtapp, self.dict_in).create_cable_harness()
        self.dict_in["CableHarness_prop"]["TwistAngleAlongRoute"] = "20deg"
        self.dict_in["CableHarness_prop"]["Polyline"] = "polyline2"
        assert not Cable(self.aedtapp, self.dict_in).create_cable_harness()
        self.dict_in["CableHarness_prop"]["Polyline"] = "polyline1"
        self.dict_in["CableHarness_prop"]["XAxis"] = "Invalid"
        assert not Cable(self.aedtapp, self.dict_in).create_cable_harness()
        self.dict_in["CableHarness_prop"]["XAxis"] = "Undefined"
        self.dict_in["CableHarness_prop"]["XAxisOrigin"] = ["0k", "0mm", "0mm"]
        assert not Cable(self.aedtapp, self.dict_in).create_cable_harness()
        self.dict_in["CableHarness_prop"]["XAxisOrigin"] = ["0mm", "0mm", "0mm"]
        self.dict_in["CableHarness_prop"]["AutoOrient"] = ""
        assert not Cable(self.aedtapp, self.dict_in).create_cable_harness()
        self.dict_in["CableHarness_prop"]["AutoOrient"] = "True"
        self.dict_in["CableHarness_prop"]["ReverseYAxisDirection"] = ""
        assert not Cable(self.aedtapp, self.dict_in).create_cable_harness()
        self.dict_in["CableHarness_prop"]["ReverseYAxisDirection"] = "True"
        self.dict_in["CableHarness_prop"]["CableTerminationsToInclude"][0]["Assignment"] = "invalid_assignment"
        assert not Cable(self.aedtapp, self.dict_in).create_cable_harness()
        self.dict_in["CableHarness_prop"]["CableTerminationsToInclude"][0]["Assignment"] = "Reference"
        self.dict_in["CableHarness_prop"]["CableTerminationsToInclude"][0]["Impedance"] = "50o"
        assert not Cable(self.aedtapp, self.dict_in).create_cable_harness()
        self.dict_in["CableHarness_prop"]["CableTerminationsToInclude"][0]["Impedance"] = "50ohm"
        self.dict_in["CableHarness_prop"]["CableTerminationsToInclude"][1]["Source"]["Type"] = "invalid"
        assert not Cable(self.aedtapp, self.dict_in).create_cable_harness()
        self.dict_in["CableHarness_prop"]["CableTerminationsToInclude"][1]["Source"]["Type"] = "impedance"
        self.dict_in["CableHarness_prop"]["CableTerminationsToInclude"] = {}
        assert not Cable(self.aedtapp, self.dict_in).create_cable_harness()

    def test_16_empty_json(self):
        self.dict_in = {}
        assert not Cable(self.aedtapp, self.dict_in).create_cable()

    def test_17_json_file_path(self):
        assert Cable(
            self.aedtapp,
            os.path.join(
                local_path,
                "example_models",
                test_subfloder,
                "cable_modeling_json_files",
                "set_cable_properties.json",
            ),
        ).create_cable()
