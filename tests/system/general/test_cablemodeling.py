# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 - 2026 ANSYS, Inc. and/or its affiliates.
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

from pathlib import Path
import shutil

import pytest

from ansys.aedt.core.generic.file_utils import read_json
from ansys.aedt.core.modules.cable_modeling import Cable
from tests import TESTS_GENERAL_PATH
from tests.conftest import DESKTOP_VERSION

PROJECT_NAME = "cable_modeling_231"

TEST_SUBFOLDER = "T43"
CABLE_PROPERTIES = (
    TESTS_GENERAL_PATH / "example_models" / TEST_SUBFOLDER / "cable_modeling_json_files" / "set_cable_properties.json"
)

pytestmark = pytest.mark.skipif(DESKTOP_VERSION > "2022.2", reason="AEDT Crashes")


@pytest.fixture
def aedt_app(add_app_example):
    app = add_app_example(project=PROJECT_NAME, design="HFSSDesign1", subfolder=TEST_SUBFOLDER)
    yield app
    app.close_project(save=False)


def test_working_dir(aedt_app, test_tmp_dir) -> None:
    file = shutil.copy2(CABLE_PROPERTIES, test_tmp_dir / "set_cable_properties.json")
    data = read_json(file)
    Cable(aedt_app, data)
    assert (Path(aedt_app.toolkit_directory) / "export_cable_library_as_json_test.json").is_file()


def test_invalid_cable_type(aedt_app, test_tmp_dir) -> None:
    file = shutil.copy2(CABLE_PROPERTIES, test_tmp_dir / "set_cable_properties.json")
    data = read_json(file)
    data["Add_Cable"] = "True"
    data["Cable_prop"]["CableType"] = ""
    assert not Cable(aedt_app, data).create_cable()


def test_create_cables_bundle_check_definitions(aedt_app, test_tmp_dir) -> None:
    file = shutil.copy2(CABLE_PROPERTIES, test_tmp_dir / "set_cable_properties.json")
    data = read_json(file)

    # Create 1st Cable bundle - Jacket Type = Insulation
    data["Add_Cable"] = "True"
    data["Cable_prop"]["CableType"] = "bundle"
    data["Cable_prop"]["IsJacketTypeInsulation"] = "True"
    data["CableManager"]["Definitions"]["CableBundle"]["BundleParams"]["InsulationJacketParams"]["InsThickness"] = (
        "3.66mm"
    )
    data["CableManager"]["Definitions"]["CableBundle"]["BundleParams"]["InsulationJacketParams"]["JacketMaterial"] = (
        "pec"
    )
    data["CableManager"]["Definitions"]["CableBundle"]["BundleParams"]["InsulationJacketParams"]["InnerDiameter"] = (
        "2.88mm"
    )
    data["CableManager"]["Definitions"]["CableBundle"]["BundleAttribs"]["Name"] = "bundle_cable_insulation"
    assert Cable(aedt_app, data).create_cable()
    cable = Cable(aedt_app)
    assert len(cable.cable_definitions) == 1
    assert list(cable.cable_definitions.keys())[0] == "CableBundle"
    assert cable.cable_definitions["CableBundle"]["BundleAttribs"]["Name"] == "bundle_cable_insulation"
    assert cable.cable_definitions["CableBundle"]["BundleParams"].get("InsulationJacketParams")
    assert cable.cable_definitions["CableBundle"]["BundleParams"]["InsulationJacketParams"]["InsThickness"] == "3.66mm"
    assert cable.cable_definitions["CableBundle"]["BundleParams"]["InsulationJacketParams"]["JacketMaterial"] == "pec"
    assert cable.cable_definitions["CableBundle"]["BundleParams"]["InsulationJacketParams"]["InnerDiameter"] == "2.88mm"
    data["CableManager"]["Definitions"]["CableBundle"]["BundleParams"]["InsulationJacketParams"]["JacketMaterial"] = (
        "alu"
    )
    assert not Cable(aedt_app, data).create_cable()
    data["CableManager"]["Definitions"]["CableBundle"]["BundleParams"]["InsulationJacketParams"]["JacketMaterial"] = ""
    # assert not Cable(aedt_app, data).create_cable()
    # Create 2nd Cable bundle - Jacket Type = No Jacket
    data["Cable_prop"]["IsJacketTypeInsulation"] = "False"
    data["Cable_prop"]["IsJacketTypeNoJacket"] = "True"
    data["CableManager"]["Definitions"]["CableBundle"]["BundleAttribs"]["Name"] = "Bundle_Cable_NoJacket"
    data["CableManager"]["Definitions"]["CableBundle"]["BundleParams"]["VirtualJacketParams"]["JacketMaterial"] = (
        "copper"
    )
    assert Cable(aedt_app, data).create_cable()
    cable = Cable(aedt_app)
    assert len(cable.cable_definitions["CableBundle"]) == 2
    assert isinstance(cable.cable_definitions["CableBundle"], list)
    assert cable.cable_definitions["CableBundle"][1]["BundleAttribs"]["Name"] == "Bundle_Cable_NoJacket"
    assert cable.cable_definitions["CableBundle"][1]["BundleParams"].get("VirtualJacketParams")
    assert cable.cable_definitions["CableBundle"][1]["BundleParams"]["VirtualJacketParams"]["JacketMaterial"] == "None"
    assert cable.cable_definitions["CableBundle"][1]["BundleParams"]["VirtualJacketParams"]["InnerDiameter"] == "2.5mm"
    data["CableManager"]["Definitions"]["CableBundle"]["BundleParams"]["VirtualJacketParams"]["JacketMaterial"] = ""
    data["CableManager"]["Definitions"]["CableBundle"]["BundleAttribs"]["Name"] = "Bundle_Cable_NoJacket_1"
    # Create 3rd Cable bundle - Jacket Type = No Jacket
    assert Cable(aedt_app, data).create_cable()
    cable = Cable(aedt_app)
    assert cable.cable_definitions["CableBundle"][2]["BundleParams"]["VirtualJacketParams"]["JacketMaterial"] == "None"
    assert cable.cable_definitions["CableBundle"][2]["BundleAttribs"]["Name"] == "Bundle_Cable_NoJacket_1"
    data["Cable_prop"]["IsJacketTypeNoJacket"] = "False"
    data["Cable_prop"]["IsJacketTypeBraidShield"] = "True"
    data["CableManager"]["Definitions"]["CableBundle"]["BundleParams"]["BraidShieldJacketParams"]["JacketMaterial"] = (
        "pec"
    )
    data["CableManager"]["Definitions"]["CableBundle"]["BundleParams"]["BraidShieldJacketParams"]["InnerDiameter"] = (
        "6mm"
    )
    data["CableManager"]["Definitions"]["CableBundle"]["BundleParams"]["BraidShieldJacketParams"]["NumCarriers"] = "36"
    data["CableManager"]["Definitions"]["CableBundle"]["BundleParams"]["BraidShieldJacketParams"][
        "NumWiresInCarrier"
    ] = "52"
    data["CableManager"]["Definitions"]["CableBundle"]["BundleParams"]["BraidShieldJacketParams"]["WireDiameter"] = (
        "0.242424mm"
    )
    data["CableManager"]["Definitions"]["CableBundle"]["BundleParams"]["BraidShieldJacketParams"]["WeaveAngle"] = (
        "33deg"
    )
    data["CableManager"]["Definitions"]["CableBundle"]["BundleAttribs"]["Name"] = "Bundle_Cable_Shielding"
    # Create 4th Cable bundle - Jacket Type = Shielding
    assert Cable(aedt_app, data).create_cable()
    cable = Cable(aedt_app)
    assert len(cable.cable_definitions["CableBundle"]) == 4
    assert isinstance(cable.cable_definitions["CableBundle"], list)
    assert cable.cable_definitions["CableBundle"][3]["BundleAttribs"]["Name"] == "Bundle_Cable_Shielding"
    assert cable.cable_definitions["CableBundle"][3]["BundleParams"].get("BraidShieldJacketParams")
    assert (
        cable.cable_definitions["CableBundle"][3]["BundleParams"]["BraidShieldJacketParams"]["JacketMaterial"] == "pec"
    )
    assert (
        cable.cable_definitions["CableBundle"][3]["BundleParams"]["BraidShieldJacketParams"]["InnerDiameter"] == "6mm"
    )
    assert cable.cable_definitions["CableBundle"][3]["BundleParams"]["BraidShieldJacketParams"]["NumCarriers"] == "36"
    assert (
        cable.cable_definitions["CableBundle"][3]["BundleParams"]["BraidShieldJacketParams"]["NumWiresInCarrier"]
        == "52"
    )
    assert (
        cable.cable_definitions["CableBundle"][3]["BundleParams"]["BraidShieldJacketParams"]["WireDiameter"]
        == "0.242424mm"
    )
    assert cable.cable_definitions["CableBundle"][3]["BundleParams"]["BraidShieldJacketParams"]["WeaveAngle"] == "33deg"
    data["CableManager"]["Definitions"]["CableBundle"]["BundleParams"]["BraidShieldJacketParams"]["InnerDiameter"] = ""
    # assert not Cable(aedt_app, data).create_cable()
    data["CableManager"]["Definitions"]["CableBundle"]["BundleParams"]["BraidShieldJacketParams"]["JacketMaterial"] = (
        "alu"
    )
    # assert not Cable(aedt_app, data).create_cable()
    data["Cable_prop"]["IsJacketTypeNoJacket"] = "True"
    # assert not Cable(aedt_app, data).create_cable()
    # for cable harness
    data["Cable_prop"]["IsJacketTypeBraidShield"] = "False"
    data["Cable_prop"]["IsJacketTypeNoJacket"] = "False"
    data["Cable_prop"]["IsJacketTypeInsulation"] = "True"
    data["CableManager"]["Definitions"]["CableBundle"]["BundleAttribs"]["Name"] = "bundle1"
    assert Cable(aedt_app, data).create_cable()


def test_update_cables_bundle_check_definitions(aedt_app, test_tmp_dir) -> None:
    file = shutil.copy2(CABLE_PROPERTIES, test_tmp_dir / "set_cable_properties.json")
    data = read_json(file)

    # Update 1st cable bundle - Jacket type = Insulation
    data["Cable_prop"]["IsJacketTypeNoJacket"] = "False"
    data["Cable_prop"]["IsJacketTypeBraidShield"] = "False"
    data["Cable_prop"]["IsJacketTypeInsulation"] = "True"
    data["CableManager"]["Definitions"]["CableBundle"]["BundleAttribs"]["Name"] = "bundle_cable_insulation"
    data["Update_Cable"] = "True"
    data["Cable_prop"]["UpdatedName"] = "New_updated_name_cable_bundle_insulation"
    data["CableManager"]["Definitions"]["CableBundle"]["BundleParams"]["InsulationJacketParams"]["JacketMaterial"] = (
        "pec"
    )

    assert Cable(aedt_app, data).update_cable_properties()
    cable = Cable(aedt_app)
    assert cable.cable_definitions["CableBundle"][0]["BundleParams"].get("InsulationJacketParams")
    assert (
        cable.cable_definitions["CableBundle"][0]["BundleParams"]["InsulationJacketParams"]["InsThickness"] == "3.66mm"
    )
    assert (
        cable.cable_definitions["CableBundle"][0]["BundleParams"]["InsulationJacketParams"]["JacketMaterial"] == "pec"
    )
    assert (
        cable.cable_definitions["CableBundle"][0]["BundleParams"]["InsulationJacketParams"]["InnerDiameter"] == "2.88mm"
    )
    assert (
        cable.cable_definitions["CableBundle"][0]["BundleAttribs"]["Name"] == "New_updated_name_cable_bundle_insulation"
    )
    # Update 1st cable bundle - Jacket type = Insulation
    data["CableManager"]["Definitions"]["CableBundle"]["BundleParams"]["InsulationJacketParams"]["InsThickness"] = "5mm"
    data["CableManager"]["Definitions"]["CableBundle"]["BundleParams"]["InsulationJacketParams"]["JacketMaterial"] = (
        "pec"
    )
    data["CableManager"]["Definitions"]["CableBundle"]["BundleParams"]["InsulationJacketParams"]["InnerDiameter"] = (
        "3mm"
    )
    data["CableManager"]["Definitions"]["CableBundle"]["BundleAttribs"]["Name"] = (
        "New_updated_name_cable_bundle_insulation"
    )
    data["Cable_prop"]["UpdatedName"] = "New_updated_name_cable_bundle_insulation_1"
    assert Cable(aedt_app, data).update_cable_properties()
    cable = Cable(aedt_app)
    assert cable.cable_definitions["CableBundle"][0]["BundleParams"]["InsulationJacketParams"]["InsThickness"] == "5mm"
    assert (
        cable.cable_definitions["CableBundle"][0]["BundleParams"]["InsulationJacketParams"]["JacketMaterial"] == "pec"
    )
    assert cable.cable_definitions["CableBundle"][0]["BundleParams"]["InsulationJacketParams"]["InnerDiameter"] == "3mm"
    # Update 1st cable bundle - Jacket type = Insulation
    data["CableManager"]["Definitions"]["CableBundle"]["BundleParams"]["InsulationJacketParams"]["JacketMaterial"] = (
        "alu"
    )
    assert not Cable(aedt_app, data).update_cable_properties()
    # Update 3rd cable bundle - Jacket type = No Jacket
    data["Cable_prop"]["IsJacketTypeNoJacket"] = "True"
    data["Cable_prop"]["IsJacketTypeBraidShield"] = "False"
    data["Cable_prop"]["IsJacketTypeInsulation"] = "False"
    data["Update_Cable"] = "True"
    data["CableManager"]["Definitions"]["CableBundle"]["BundleAttribs"]["Name"] = "Bundle_Cable_NoJacket_1"
    data["Cable_prop"]["UpdatedName"] = "New_updated_name_cable_bundle_no_jacket"
    assert Cable(aedt_app, data).update_cable_properties()
    cable = Cable(aedt_app)
    assert cable.cable_definitions["CableBundle"][2]["BundleParams"]["VirtualJacketParams"]["JacketMaterial"] == "None"
    assert cable.cable_definitions["CableBundle"][2]["BundleParams"]["VirtualJacketParams"]["InnerDiameter"] == "2.5mm"
    data["Cable_prop"]["UpdatedName"] = ""
    assert not Cable(aedt_app, data).update_cable_properties()
    # Update 4th cable bundle - Jacket type = Shielding - Name
    data["Cable_prop"]["IsJacketTypeNoJacket"] = "False"
    data["Cable_prop"]["IsJacketTypeBraidShield"] = "True"
    data["Cable_prop"]["IsJacketTypeInsulation"] = "False"
    data["Update_Cable"] = "True"
    data["CableManager"]["Definitions"]["CableBundle"]["BundleAttribs"]["Name"] = "Bundle_Cable_Shielding"
    data["Cable_prop"]["UpdatedName"] = "New_updated_name_cable_bundle_shielding"
    Cable(aedt_app, data).update_shielding()
    cable = Cable(aedt_app, data)
    assert (
        cable.cable_definitions["CableBundle"][3]["BundleAttribs"]["Name"] == "New_updated_name_cable_bundle_shielding"
    )
    assert cable.cable_definitions["CableBundle"][3]["BundleParams"].get("BraidShieldJacketParams")
    assert (
        cable.cable_definitions["CableBundle"][3]["BundleParams"]["BraidShieldJacketParams"]["JacketMaterial"]
        == "copper"
    )
    assert (
        cable.cable_definitions["CableBundle"][3]["BundleParams"]["BraidShieldJacketParams"]["InnerDiameter"] == "2.5mm"
    )
    assert cable.cable_definitions["CableBundle"][3]["BundleParams"]["BraidShieldJacketParams"]["NumCarriers"] == "2"
    assert (
        cable.cable_definitions["CableBundle"][3]["BundleParams"]["BraidShieldJacketParams"]["NumWiresInCarrier"] == "5"
    )
    assert (
        cable.cable_definitions["CableBundle"][3]["BundleParams"]["BraidShieldJacketParams"]["WireDiameter"] == "0.1mm"
    )
    assert cable.cable_definitions["CableBundle"][3]["BundleParams"]["BraidShieldJacketParams"]["WeaveAngle"] == "30deg"
    # Update 4th cable bundle - Jacket type = Shielding - Properties
    data["CableManager"]["Definitions"]["CableBundle"]["BundleParams"]["BraidShieldJacketParams"]["JacketMaterial"] = (
        "pec"
    )
    data["CableManager"]["Definitions"]["CableBundle"]["BundleParams"]["BraidShieldJacketParams"]["InnerDiameter"] = (
        "10mm"
    )
    data["CableManager"]["Definitions"]["CableBundle"]["BundleParams"]["BraidShieldJacketParams"]["NumCarriers"] = "22"
    data["CableManager"]["Definitions"]["CableBundle"]["BundleParams"]["BraidShieldJacketParams"][
        "NumWiresInCarrier"
    ] = "23"
    data["CableManager"]["Definitions"]["CableBundle"]["BundleParams"]["BraidShieldJacketParams"]["WireDiameter"] = (
        "0.212mm"
    )
    data["CableManager"]["Definitions"]["CableBundle"]["BundleParams"]["BraidShieldJacketParams"]["WeaveAngle"] = (
        "35deg"
    )
    data["CableManager"]["Definitions"]["CableBundle"]["BundleAttribs"]["Name"] = (
        "New_updated_name_cable_bundle_shielding"
    )
    data["Cable_prop"]["UpdatedName"] = "New_updated_name_cable_bundle_shielding_1"
    assert Cable(aedt_app, data).update_shielding()
    cable = Cable(aedt_app, data)
    assert (
        cable.cable_definitions["CableBundle"][3]["BundleParams"]["BraidShieldJacketParams"]["JacketMaterial"] == "pec"
    )
    assert (
        cable.cable_definitions["CableBundle"][3]["BundleParams"]["BraidShieldJacketParams"]["InnerDiameter"] == "10mm"
    )
    assert cable.cable_definitions["CableBundle"][3]["BundleParams"]["BraidShieldJacketParams"]["NumCarriers"] == "22"
    assert (
        cable.cable_definitions["CableBundle"][3]["BundleParams"]["BraidShieldJacketParams"]["NumWiresInCarrier"]
        == "23"
    )
    assert (
        cable.cable_definitions["CableBundle"][3]["BundleParams"]["BraidShieldJacketParams"]["WireDiameter"]
        == "0.212mm"
    )
    assert cable.cable_definitions["CableBundle"][3]["BundleParams"]["BraidShieldJacketParams"]["WeaveAngle"] == "35deg"
    data["CableManager"]["Definitions"]["CableBundle"]["BundleParams"]["BraidShieldJacketParams"]["JacketMaterial"] = (
        "alu"
    )
    assert not Cable(aedt_app, data).update_shielding()


def test_create_cables_straight_wire_check_definitions(aedt_app, test_tmp_dir) -> None:
    file = shutil.copy2(CABLE_PROPERTIES, test_tmp_dir / "set_cable_properties.json")
    data = read_json(file)

    # Create 1st straight wire cable
    data["Add_Cable"] = "True"
    data["Cable_prop"]["CableType"] = "straight wire"
    data["Update_Cable"] = "False"
    data["CableManager"]["Definitions"]["StWireCable"]["StWireParams"]["WireStandard"] = "ISO"
    data["CableManager"]["Definitions"]["StWireCable"]["StWireParams"]["WireGauge"] = "2.5"
    data["CableManager"]["Definitions"]["StWireCable"]["StWireParams"]["CondDiameter"] = "10mm"
    data["CableManager"]["Definitions"]["StWireCable"]["StWireParams"]["CondMaterial"] = "pec"
    data["CableManager"]["Definitions"]["StWireCable"]["StWireParams"]["InsThickness"] = "0.9mm"
    data["CableManager"]["Definitions"]["StWireCable"]["StWireParams"]["InsMaterial"] = "copper"
    data["CableManager"]["Definitions"]["StWireCable"]["StWireParams"]["InsType"] = "Thin Wall"
    data["CableManager"]["Definitions"]["StWireCable"]["StWireAttribs"]["Name"] = "straight_wire_cable"
    assert Cable(aedt_app, data).create_cable()
    cable = Cable(aedt_app)
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
    data["CableManager"]["Definitions"]["StWireCable"]["StWireAttribs"]["Name"] = "stwire1"
    assert Cable(aedt_app, data).create_cable()
    data["CableManager"]["Definitions"]["StWireCable"]["StWireAttribs"]["Name"] = "stwire2"
    assert Cable(aedt_app, data).create_cable()
    data["CableManager"]["Definitions"]["StWireCable"]["StWireAttribs"]["Name"] = "stwire3"
    assert Cable(aedt_app, data).create_cable()


@pytest.mark.skip(reason="Unable to update if it's not done before manually.")
def test_update_cables_straight_wire_check_definitions(aedt_app, test_tmp_dir) -> None:
    file = shutil.copy2(CABLE_PROPERTIES, test_tmp_dir / "set_cable_properties.json")
    data = read_json(file)

    data["Update_Cable"] = "True"
    data["Cable_prop"]["UpdatedName"] = "New_updated_name_cable_straight_wire"
    data["CableManager"]["Definitions"]["StWireCable"]["StWireParams"]["WireStandard"] = "ISO"
    data["CableManager"]["Definitions"]["StWireCable"]["StWireParams"]["WireGauge"] = "0.13"
    data["CableManager"]["Definitions"]["StWireCable"]["StWireParams"]["CondDiameter"] = "0.5mm"
    data["CableManager"]["Definitions"]["StWireCable"]["StWireParams"]["CondMaterial"] = "pec"
    data["CableManager"]["Definitions"]["StWireCable"]["StWireParams"]["InsThickness"] = "0.25mm"
    data["CableManager"]["Definitions"]["StWireCable"]["StWireParams"]["InsMaterial"] = "copper"
    data["CableManager"]["Definitions"]["StWireCable"]["StWireParams"]["InsType"] = "Thin Wall"
    data["CableManager"]["Definitions"]["StWireCable"]["StWireAttribs"]["Name"] = "straight_wire_cable"
    assert Cable(aedt_app, data).update_cable_properties()
    cable = Cable(aedt_app)
    assert cable.cable_definitions["StWireCable"]
    assert cable.cable_definitions["StWireCable"]["StWireAttribs"]["Name"] == "New_updated_name_cable_straight_wire"
    assert cable.cable_definitions["StWireCable"]["StWireParams"]["WireStandard"] == "ISO"
    assert cable.cable_definitions["StWireCable"]["StWireParams"]["WireGauge"] == "0.13"
    assert cable.cable_definitions["StWireCable"]["StWireParams"]["CondDiameter"] == "0.5mm"
    assert cable.cable_definitions["StWireCable"]["StWireParams"]["CondMaterial"] == "pec"
    assert cable.cable_definitions["StWireCable"]["StWireParams"]["InsThickness"] == "0.25mm"
    assert cable.cable_definitions["StWireCable"]["StWireParams"]["InsMaterial"] == "copper"
    assert cable.cable_definitions["StWireCable"]["StWireParams"]["InsType"] == "Thin Wall"


def test_create_cables_twisted_pair_check_definitions(aedt_app, test_tmp_dir) -> None:
    file = shutil.copy2(CABLE_PROPERTIES, test_tmp_dir / "set_cable_properties.json")
    data = read_json(file)
    Cable(aedt_app, data)

    data["Add_Cable"] = "True"
    data["Cable_prop"]["CableType"] = "twisted pair"
    data["Update_Cable"] = "False"
    data["CableManager"]["Definitions"]["TwistedPairCable"]["TwistedPairParams"]["StraightWireCableID"] = 1025
    data["CableManager"]["Definitions"]["TwistedPairCable"]["TwistedPairParams"]["IsLayLengthSpecified"] = "False"
    data["CableManager"]["Definitions"]["TwistedPairCable"]["TwistedPairParams"]["LayLength"] = "34mm"
    data["CableManager"]["Definitions"]["TwistedPairCable"]["TwistedPairParams"]["TurnsPerMeter"] = "99"
    data["CableManager"]["Definitions"]["TwistedPairCable"]["TwistedPairAttribs"]["Name"] = "twisted_pair_cable"
    assert Cable(aedt_app, data).create_cable()
    cable = Cable(aedt_app)
    assert cable.cable_definitions["TwistedPairCable"]
    assert cable.cable_definitions["TwistedPairCable"]["TwistedPairAttribs"]["Name"] == "twisted_pair_cable"
    assert cable.cable_definitions["TwistedPairCable"]["TwistedPairParams"]
    assert cable.cable_definitions["TwistedPairCable"]["TwistedPairParams"]["StraightWireCableID"] == 1025
    assert not cable.cable_definitions["TwistedPairCable"]["TwistedPairParams"]["IsLayLengthSpecified"]
    assert cable.cable_definitions["TwistedPairCable"]["TwistedPairParams"]["LayLength"] == "0mm"
    assert cable.cable_definitions["TwistedPairCable"]["TwistedPairParams"]["TurnsPerMeter"] == "99"
    data["CableManager"]["Definitions"]["TwistedPairCable"]["TwistedPairParams"]["IsLayLengthSpecified"] = {}
    assert not Cable(aedt_app, data).create_cable()
    data["CableManager"]["Definitions"]["TwistedPairCable"]["TwistedPairAttribs"]["Name"] = "twisted_pair_cable_1"
    data["CableManager"]["Definitions"]["TwistedPairCable"]["TwistedPairParams"]["IsLayLengthSpecified"] = "True"
    data["CableManager"]["Definitions"]["TwistedPairCable"]["TwistedPairParams"]["LayLength"] = "34mm"
    assert Cable(aedt_app, data).create_cable()
    cable = Cable(aedt_app, data)
    assert cable.cable_definitions["TwistedPairCable"][1]["TwistedPairAttribs"]["Name"] == "twisted_pair_cable_1"
    assert cable.cable_definitions["TwistedPairCable"][1]["TwistedPairParams"]["IsLayLengthSpecified"]
    assert cable.cable_definitions["TwistedPairCable"][1]["TwistedPairParams"]["LayLength"] == "34mm"


def test_update_cables_twisted_pair_check_definitions(aedt_app, test_tmp_dir) -> None:
    file = shutil.copy2(CABLE_PROPERTIES, test_tmp_dir / "set_cable_properties.json")
    data = read_json(file)

    data["Update_Cable"] = "True"
    data["Cable_prop"]["UpdatedName"] = "New_updated_name_cable_twisted_pair"
    data["CableManager"]["Definitions"]["TwistedPairCable"]["TwistedPairParams"]["StraightWireCableID"] = 1025
    data["CableManager"]["Definitions"]["TwistedPairCable"]["TwistedPairParams"]["IsLayLengthSpecified"] = "True"
    data["CableManager"]["Definitions"]["TwistedPairCable"]["TwistedPairParams"]["LayLength"] = "47mm"
    data["CableManager"]["Definitions"]["TwistedPairCable"]["TwistedPairParams"]["TurnsPerMeter"] = "97"
    data["CableManager"]["Definitions"]["TwistedPairCable"]["TwistedPairAttribs"]["Name"] = "twisted_pair_cable_1"
    assert Cable(aedt_app, data).update_cable_properties()
    cable = Cable(aedt_app)
    assert (
        cable.cable_definitions["TwistedPairCable"][1]["TwistedPairAttribs"]["Name"]
        == "New_updated_name_cable_twisted_pair"
    )
    assert cable.cable_definitions["TwistedPairCable"][1]["TwistedPairParams"]["StraightWireCableID"] == 1025
    assert cable.cable_definitions["TwistedPairCable"][1]["TwistedPairParams"]["IsLayLengthSpecified"]
    assert cable.cable_definitions["TwistedPairCable"][1]["TwistedPairParams"]["LayLength"] == "47mm"
    assert cable.cable_definitions["TwistedPairCable"][1]["TwistedPairParams"]["TurnsPerMeter"] == "97"


def test_add_cables_to_bundle(aedt_app, test_tmp_dir) -> None:
    file = shutil.copy2(CABLE_PROPERTIES, test_tmp_dir / "set_cable_properties.json")
    data = read_json(file)
    data["Add_Cable"] = "False"
    data["Update_Cable"] = "False"
    data["Add_CablesToBundle"] = "True"
    data["CablesToBundle_prop"]["CablesToAdd"] = "straight_wire_cable"
    data["CablesToBundle_prop"]["BundleCable"] = "New_updated_name_cable_bundle_insulation_1"
    data["CablesToBundle_prop"]["NumberOfCableToAdd"] = 3
    assert Cable(aedt_app, data).add_cable_to_bundle()
    cable = Cable(aedt_app, data)
    assert cable.cable_definitions["CableBundle"][0]["Instances"]["StWireInstance"]
    assert len(cable.cable_definitions["CableBundle"][0]["Instances"]["StWireInstance"]) == 3
    data["CablesToBundle_prop"]["NumberOfCableToAdd"] = ""
    assert Cable(aedt_app, data).add_cable_to_bundle()
    cable = Cable(aedt_app, data)
    assert len(cable.cable_definitions["CableBundle"][0]["Instances"]["StWireInstance"]) == 5
    data["CablesToBundle_prop"]["BundleCable"] = "New_updated_name_cable_bundle_insulation_"
    assert not Cable(aedt_app, data).add_cable_to_bundle()
    # for cable harness
    data["CablesToBundle_prop"]["CablesToAdd"] = ["stwire1", "stwire2", "stwire3"]
    data["CablesToBundle_prop"]["BundleCable"] = "bundle1"
    data["CablesToBundle_prop"]["NumberOfCableToAdd"] = 3
    assert Cable(aedt_app, data).add_cable_to_bundle()


def test_remove_cables(aedt_app, test_tmp_dir) -> None:
    file = shutil.copy2(CABLE_PROPERTIES, test_tmp_dir / "set_cable_properties.json")
    data = read_json(file)

    data["Add_Cable"] = "False"
    data["Update_Cable"] = "False"
    data["Add_CablesToBundle"] = "False"
    data["Remove_Cable"] = "True"
    data["Cable_prop"]["CablesToRemove"] = "New_updated_name_cable_bundle_no_jacket"
    assert Cable(aedt_app, data).remove_cables()
    data["Cable_prop"]["CablesToRemove"] = ["abc", "cd"]
    assert not Cable(aedt_app, data).remove_cables()


def test_add_clock_source(aedt_app, test_tmp_dir) -> None:
    file = shutil.copy2(CABLE_PROPERTIES, test_tmp_dir / "set_cable_properties.json")
    data = read_json(file)

    data["Add_Cable"] = "False"
    data["Update_Cable"] = "False"
    data["Add_CablesToBundle"] = "False"
    data["Remove_Cable"] = "False"
    data["Add_Source"] = "True"
    data["Source_prop"]["AddClockSource"] = "True"
    data["CableManager"]["TDSources"]["ClockSourceDef"]["ClockSignalParams"]["Period"] = "40us"
    data["CableManager"]["TDSources"]["ClockSourceDef"]["ClockSignalParams"]["LowPulseVal"] = "0.1V"
    data["CableManager"]["TDSources"]["ClockSourceDef"]["ClockSignalParams"]["HighPulseVal"] = "2V"
    data["CableManager"]["TDSources"]["ClockSourceDef"]["ClockSignalParams"]["Risetime"] = "5us"
    data["CableManager"]["TDSources"]["ClockSourceDef"]["ClockSignalParams"]["Falltime"] = "10us"
    data["CableManager"]["TDSources"]["ClockSourceDef"]["ClockSignalParams"]["PulseWidth"] = "23us"
    data["CableManager"]["TDSources"]["ClockSourceDef"]["TDSourceAttribs"]["Name"] = "clock_test_1"
    assert Cable(aedt_app, data).create_clock_source()
    cable = Cable(aedt_app)
    assert len(cable.clock_source_definitions) == 3
    assert cable.clock_source_definitions[2]["ClockSignalParams"]["Period"] == "40us"
    assert cable.clock_source_definitions[2]["ClockSignalParams"]["LowPulseVal"] == "0.1V"
    assert cable.clock_source_definitions[2]["ClockSignalParams"]["HighPulseVal"] == "2V"
    assert cable.clock_source_definitions[2]["ClockSignalParams"]["Risetime"] == "5us"
    assert cable.clock_source_definitions[2]["ClockSignalParams"]["Falltime"] == "10us"
    assert cable.clock_source_definitions[2]["ClockSignalParams"]["PulseWidth"] == "23us"
    assert cable.clock_source_definitions[2]["TDSourceAttribs"]["Name"] == "clock_test_1"
    data["CableManager"]["TDSources"]["ClockSourceDef"]["TDSourceAttribs"]["Name"] = ""
    assert Cable(aedt_app, data).create_clock_source()
    data["CableManager"]["TDSources"]["ClockSourceDef"]["ClockSignalParams"]["Period"] = "40u"
    assert not Cable(aedt_app, data).create_clock_source()
    data["CableManager"]["TDSources"]["ClockSourceDef"]["ClockSignalParams"]["LowPulseVal"] = "0.1voltage"
    assert not Cable(aedt_app, data).create_clock_source()
    data["CableManager"]["TDSources"]["ClockSourceDef"]["ClockSignalParams"]["HighPulseVal"] = "2voltage"
    assert not Cable(aedt_app, data).create_clock_source()
    data["CableManager"]["TDSources"]["ClockSourceDef"]["ClockSignalParams"]["Risetime"] = "5u"
    assert not Cable(aedt_app, data).create_clock_source()
    data["CableManager"]["TDSources"]["ClockSourceDef"]["ClockSignalParams"]["Falltime"] = "10u"
    assert not Cable(aedt_app, data).create_clock_source()
    data["CableManager"]["TDSources"]["ClockSourceDef"]["ClockSignalParams"]["PulseWidth"] = "23u"
    assert not Cable(aedt_app, data).create_clock_source()


def test_update_clock_source(aedt_app, test_tmp_dir) -> None:
    file = shutil.copy2(CABLE_PROPERTIES, test_tmp_dir / "set_cable_properties.json")
    data = read_json(file)

    data["Add_Source"] = "False"
    data["Update_Source"] = "True"
    data["Source_prop"]["UpdateClockSource"] = "True"
    data["Source_prop"]["UpdatedSourceName"] = "update_clock_test_1"
    data["CableManager"]["TDSources"]["ClockSourceDef"]["TDSourceAttribs"]["Name"] = "clock_test_1"
    data["CableManager"]["TDSources"]["ClockSourceDef"]["ClockSignalParams"]["Period"] = "45us"
    data["CableManager"]["TDSources"]["ClockSourceDef"]["ClockSignalParams"]["LowPulseVal"] = "0.3V"
    data["CableManager"]["TDSources"]["ClockSourceDef"]["ClockSignalParams"]["HighPulseVal"] = "3V"
    data["CableManager"]["TDSources"]["ClockSourceDef"]["ClockSignalParams"]["Risetime"] = "4us"
    data["CableManager"]["TDSources"]["ClockSourceDef"]["ClockSignalParams"]["Falltime"] = "15us"
    data["CableManager"]["TDSources"]["ClockSourceDef"]["ClockSignalParams"]["PulseWidth"] = "26us"
    assert Cable(aedt_app, data).update_clock_source()
    cable = Cable(aedt_app)
    assert cable.clock_source_definitions[2]["TDSourceAttribs"]["Name"] == "update_clock_test_1"
    assert cable.clock_source_definitions[2]["ClockSignalParams"]["Period"] == "45us"
    assert cable.clock_source_definitions[2]["ClockSignalParams"]["LowPulseVal"] == "0.3V"
    assert cable.clock_source_definitions[2]["ClockSignalParams"]["HighPulseVal"] == "3V"
    assert cable.clock_source_definitions[2]["ClockSignalParams"]["Risetime"] == "4us"
    assert cable.clock_source_definitions[2]["ClockSignalParams"]["Falltime"] == "15us"
    assert cable.clock_source_definitions[2]["ClockSignalParams"]["PulseWidth"] == "26us"
    data["Add_Source"] = "True"
    data["Update_Source"] = "True"
    assert not Cable(aedt_app, data).update_clock_source()
    data["Source_prop"]["AddClockSource"] = "True"
    data["Source_prop"]["UpdateClockSource"] = "True"
    assert not Cable(aedt_app, data).update_clock_source()
    data["CableManager"]["TDSources"]["ClockSourceDef"]["TDSourceAttribs"]["Name"] = ""
    assert not Cable(aedt_app, data).update_clock_source()


def test_add_pwl_source(aedt_app, test_tmp_dir) -> None:
    file = shutil.copy2(CABLE_PROPERTIES, test_tmp_dir / "set_cable_properties.json")
    data = read_json(file)

    data["Add_Cable"] = "False"
    data["Update_Cable"] = "False"
    data["Add_CablesToBundle"] = "False"
    data["Remove_Cable"] = "False"
    data["Add_Source"] = "True"
    data["Update_Source"] = "False"
    data["Source_prop"]["AddClockSource"] = "False"
    data["Source_prop"]["AddPwlSource"] = "True"
    data["CableManager"]["TDSources"]["PWLSourceDef"]["PWLSignalParams"]["SignalValues"] = [
        "0V",
        "0.5V",
        "0V",
        "3V",
        "4V",
        "0V",
    ]
    data["CableManager"]["TDSources"]["PWLSourceDef"]["PWLSignalParams"]["TimeValues"] = [
        "0ns",
        "1ns",
        "2ns",
        "3ns",
        "4ns",
        "5ns",
    ]
    data["CableManager"]["TDSources"]["PWLSourceDef"]["TDSourceAttribs"]["Name"] = "pwl4"
    assert Cable(aedt_app, data).create_pwl_source()
    cable = Cable(aedt_app)
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
    data["CableManager"]["TDSources"]["PWLSourceDef"]["PWLSignalParams"]["SignalValues"] = [
        "0V",
        "0.5V",
        "0V",
        "3V",
        "4V",
        "1V",
    ]
    assert not Cable(aedt_app, data).create_pwl_source()
    data["CableManager"]["TDSources"]["PWLSourceDef"]["TDSourceAttribs"] = {}
    assert not Cable(aedt_app, data).create_pwl_source()
    data["Add_Source"] = "False"
    data["Update_Source"] = "True"
    data["Source_prop"]["AddClockSource"] = "False"
    data["Source_prop"]["AddPwlSource"] = "False"
    data["Source_prop"]["UpdateClockSource"] = "False"
    data["Source_prop"]["UpdatePwlSource"] = "True"
    data["Source_prop"]["UpdatedSourceName"] = "update_pwl_source"
    data["CableManager"]["TDSources"]["PWLSourceDef"]["PWLSignalParams"]["SignalValues"] = [
        "0V",
        "0.5V",
        "0V",
        "3V",
        "4V",
        "9V",
        "0V",
    ]
    data["CableManager"]["TDSources"]["PWLSourceDef"]["PWLSignalParams"]["TimeValues"] = [
        "0ns",
        "1ns",
        "2ns",
        "3ns",
        "4ns",
        "5ns",
        "6ns",
    ]
    data["CableManager"]["TDSources"]["PWLSourceDef"]["TDSourceAttribs"]["Name"] = "pwl1"
    data["Source_prop"]["UpdatedSourceName"] = "updated_pwl1"
    assert Cable(aedt_app, data).update_pwl_source()
    cable = Cable(aedt_app)
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
    data["Add_Source"] = "True"
    data["Update_Source"] = "False"
    data["Source_prop"]["AddClockSource"] = "False"
    data["Source_prop"]["AddPwlSource"] = "True"
    pwl = shutil.copy2(
        TESTS_GENERAL_PATH / "example_models" / TEST_SUBFOLDER / "cable_modeling_json_files" / "import_pwl.pwl",
        test_tmp_dir / "import_pwl.pwl",
    )
    data["Source_prop"]["AddPwlSourceFromFile"] = str(pwl)

    data["Source_prop"]["UpdateClockSource"] = "False"
    data["Source_prop"]["UpdatePwlSource"] = "False"
    assert Cable(aedt_app, data).create_pwl_source_from_file()
    pwl_doc = shutil.copy2(
        TESTS_GENERAL_PATH / "example_models" / TEST_SUBFOLDER / "cable_modeling_json_files" / "import_pwl.doc",
        test_tmp_dir / "import_pwl.doc",
    )
    data["Source_prop"]["AddPwlSourceFromFile"] = str(pwl_doc)
    assert Cable(aedt_app, data).create_pwl_source_from_file()

    pwl_txt = shutil.copy2(
        TESTS_GENERAL_PATH / "example_models" / TEST_SUBFOLDER / "cable_modeling_json_files" / "import_pwl.txt",
        test_tmp_dir / "import_pwl.txt",
    )
    data["Source_prop"]["AddPwlSourceFromFile"] = str(pwl_txt)
    assert not Cable(aedt_app, data).create_pwl_source_from_file()


def test_remove_source(aedt_app, test_tmp_dir) -> None:
    file = shutil.copy2(CABLE_PROPERTIES, test_tmp_dir / "set_cable_properties.json")
    data = read_json(file)

    data["Add_Cable"] = "False"
    data["Update_Cable"] = "False"
    data["Add_CablesToBundle"] = "False"
    data["Remove_Cable"] = "False"
    data["Add_Source"] = "False"
    data["Update_Source"] = "False"
    data["Remove_Source"] = "True"
    data["Source_prop"]["AddClockSource"] = "False"
    data["Source_prop"]["AddPwlSource"] = "False"
    data["Source_prop"]["SourcesToRemove"] = "update_clock_test_1"
    assert Cable(aedt_app, data).remove_source()
    cable = Cable(aedt_app)
    assert len(cable.clock_source_definitions) == 3
    data["Source_prop"]["SourcesToRemove"] = "non_existing_source"
    assert not Cable(aedt_app, data).remove_source()


def test_add_cable_harness(aedt_app, test_tmp_dir) -> None:
    file = shutil.copy2(CABLE_PROPERTIES, test_tmp_dir / "set_cable_properties.json")
    data = read_json(file)

    data["Add_Cable"] = "False"
    data["Update_Cable"] = "False"
    data["Add_CablesToBundle"] = "False"
    data["Remove_Cable"] = "False"
    data["Add_Source"] = "False"
    data["Update_Source"] = "False"
    data["Remove_Source"] = "False"
    data["Add_CableHarness"] = "True"
    data["CableHarness_prop"]["Name"] = "cable_harness_test"
    data["CableHarness_prop"]["Bundle"] = "bundle1"
    data["CableHarness_prop"]["TwistAngleAlongRoute"] = "20deg"
    data["CableHarness_prop"]["Polyline"] = "polyline1"
    data["CableHarness_prop"]["AutoOrient"] = "False"
    data["CableHarness_prop"]["XAxis"] = "Undefined"
    data["CableHarness_prop"]["XAxisOrigin"] = ["0mm", "0mm", "0mm"]
    data["CableHarness_prop"]["XAxisEnd"] = ["0mm", "0mm", "0mm"]
    data["CableHarness_prop"]["ReverseYAxisDirection"] = "True"
    assert Cable(aedt_app, data).create_cable_harness()
    data["CableHarness_prop"]["Bundle"] = "New_updated_name_cable_bundle_insulation_1"
    data["CableHarness_prop"]["CableTerminationsToInclude"][0]["CableName"] = "straight_wire_cable"
    data["CableHarness_prop"]["CableTerminationsToInclude"][1]["CableName"] = "straight_wire_cable1"
    data["CableHarness_prop"]["CableTerminationsToInclude"][2]["CableName"] = "straight_wire_cable2"
    data["CableHarness_prop"]["Name"] = "cable_harness_test_1"
    assert Cable(aedt_app, data).create_cable_harness()
    data["CableHarness_prop"]["Name"] = ""
    assert Cable(aedt_app, data).create_cable_harness()
    data["CableHarness_prop"]["XAxis"] = "NewVector"
    data["CableHarness_prop"]["XAxisOrigin"] = ["1mm", "2mm", "3mm"]
    data["CableHarness_prop"]["XAxisEnd"] = ["4mm", "5mm", "6mm"]
    assert Cable(aedt_app, data).create_cable_harness()
    data["CableHarness_prop"]["Bundle"] = "non_existing_bundle"
    assert not Cable(aedt_app, data).create_cable_harness()
    data["CableHarness_prop"]["Bundle"] = "bundle1"
    data["CableHarness_prop"]["Name"] = ""
    data["CableHarness_prop"]["TwistAngleAlongRoute"] = "20de"
    assert not Cable(aedt_app, data).create_cable_harness()
    data["CableHarness_prop"]["TwistAngleAlongRoute"] = "20deg"
    data["CableHarness_prop"]["Polyline"] = "polyline2"
    assert not Cable(aedt_app, data).create_cable_harness()
    data["CableHarness_prop"]["Polyline"] = "polyline1"
    data["CableHarness_prop"]["XAxis"] = "Invalid"
    assert not Cable(aedt_app, data).create_cable_harness()
    data["CableHarness_prop"]["XAxis"] = "Undefined"
    data["CableHarness_prop"]["XAxisOrigin"] = ["0k", "0mm", "0mm"]
    assert not Cable(aedt_app, data).create_cable_harness()
    data["CableHarness_prop"]["XAxisOrigin"] = ["0mm", "0mm", "0mm"]
    data["CableHarness_prop"]["AutoOrient"] = ""
    assert not Cable(aedt_app, data).create_cable_harness()
    data["CableHarness_prop"]["AutoOrient"] = "True"
    data["CableHarness_prop"]["ReverseYAxisDirection"] = ""
    assert not Cable(aedt_app, data).create_cable_harness()
    data["CableHarness_prop"]["ReverseYAxisDirection"] = "True"
    data["CableHarness_prop"]["CableTerminationsToInclude"][0]["Assignment"] = "invalid_assignment"
    assert not Cable(aedt_app, data).create_cable_harness()
    data["CableHarness_prop"]["CableTerminationsToInclude"][0]["Assignment"] = "Reference"
    data["CableHarness_prop"]["CableTerminationsToInclude"][0]["Impedance"] = "50o"
    assert not Cable(aedt_app, data).create_cable_harness()
    data["CableHarness_prop"]["CableTerminationsToInclude"][0]["Impedance"] = "50ohm"
    data["CableHarness_prop"]["CableTerminationsToInclude"][1]["Source"]["Type"] = "invalid"
    assert not Cable(aedt_app, data).create_cable_harness()
    data["CableHarness_prop"]["CableTerminationsToInclude"][1]["Source"]["Type"] = "impedance"
    data["CableHarness_prop"]["CableTerminationsToInclude"] = {}
    assert not Cable(aedt_app, data).create_cable_harness()


def test_empty_json(aedt_app) -> None:
    data = {}
    assert not Cable(aedt_app, data).create_cable()


def test_json_file_path(aedt_app, test_tmp_dir) -> None:
    file = shutil.copy2(CABLE_PROPERTIES, test_tmp_dir / "set_cable_properties.json")
    assert Cable(aedt_app, str(file)).create_cable()
