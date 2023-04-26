"""
HFSS: Cable Modeling
--------------------
This example shows how you can use PyAEDT to use all the cable modeling features available in HFSS.
Cable Modeling requires a pre-defined JSON file with all the cables and cable harness properties to set.
In this example the properties are explicitly set but the user can also set them manually inside the file, save it
and instantiate the Cable class to access all the available methods.
"""

###############################################################################
# Perform required imports
# ~~~~~~~~~~~~~~~~~~~~~~~~
# Perform required imports.

import os
import pyaedt
from pyaedt.modules.CableModeling import Cable

# Set local temporary folder to export the cable library into.
# set_cable_properties.json is the required json file to work with the Cable class.
# Its structure must never change except for the properties values.
temp_folder = pyaedt.generate_unique_folder_name()
project_path = pyaedt.downloads.download_file("cable_modeling", "cable_modeling.aedt", temp_folder)
json_path = pyaedt.downloads.download_file("cable_modeling", "set_cable_properties.json", temp_folder)

###############################################################################
# Launch AEDT
# ~~~~~~~~~~~
# Launch AEDT 2023 R1 in graphical mode. This example uses SI units.

desktopVersion = "2023.1"

###############################################################################
# Set non-graphical mode
# ~~~~~~~~~~~~~~~~~~~~~~
# Set non-graphical mode. ``"PYAEDT_NON_GRAPHICAL"`` is needed to generate
# documentation only.
# You can set ``non_graphical`` either to ``True`` or ``False``.

non_graphical = False

###############################################################################
# Launch AEDT
# ~~~~~~~~~~~
# Launch AEDT 2023 R1 in graphical mode.

d = pyaedt.launch_desktop(desktopVersion, non_graphical=non_graphical, new_desktop_session=True)

###############################################################################
# Launch HFSS
# ~~~~~~~~~~~
# Launch HFSS 2023 R1 in graphical mode.

hfss = pyaedt.Hfss(projectname=project_path, non_graphical=non_graphical)
hfss.modeler.model_units = "mm"

###############################################################################
# New instance of Cable modeling class
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# New instance of Cable modeling class which requires as input
# the aedt app and the json file path containing all the cable properties.

cable = Cable(hfss, json_path)

###############################################################################
# Create cable bundle
# ~~~~~~~~~~~~~~~~~~~
# Properties for cable bundle are updated (user can change them manually
# in json file).
# A cable bundle with insulation jacket type is created.

cable_props = pyaedt.data_handler.json_to_dict(json_path)

cable_props["Add_Cable"] = "True"
cable_props["Cable_prop"]["CableType"] = "bundle"
cable_props["Cable_prop"]["IsJacketTypeInsulation"] = "True"
cable_props["CableManager"]["Definitions"]["CableBundle"]["BundleParams"]["InsulationJacketParams"][
            "InsThickness"
        ] = "3.66mm"
cable_props["CableManager"]["Definitions"]["CableBundle"]["BundleParams"]["InsulationJacketParams"][
            "JacketMaterial"
        ] = "pec"
cable_props["CableManager"]["Definitions"]["CableBundle"]["BundleParams"]["InsulationJacketParams"][
            "InnerDiameter"
        ] = "2.88mm"
cable_props["CableManager"]["Definitions"]["CableBundle"]["BundleAttribs"]["Name"] = "Bundle_Cable_Insulation"

cable = Cable(hfss, cable_props)
cable.create_cable()

###############################################################################
# Create cable bundle
# ~~~~~~~~~~~~~~~~~~~
# A cable bundle with no jacket type is created.

cable_props["Cable_prop"]["IsJacketTypeInsulation"] = "False"
cable_props["Cable_prop"]["IsJacketTypeNoJacket"] = "True"
cable_props["CableManager"]["Definitions"]["CableBundle"]["BundleAttribs"]["Name"] = "Bundle_Cable_NoJacket"

# Cable class has to be reinitialized because json has changed.
# It accepts in input both a json file path and a dictionary.
cable = Cable(hfss, cable_props)
cable.create_cable()

###############################################################################
# Create cable bundle
# ~~~~~~~~~~~~~~~~~~~
# A cable bundle with shielding jacket type is created.

cable_props["Cable_prop"]["IsJacketTypeNoJacket"] = "False"
cable_props["Cable_prop"]["IsJacketTypeBraidShield"] = "True"
cable_props["CableManager"]["Definitions"]["CableBundle"]["BundleParams"]["BraidShieldJacketParams"][
            "JacketMaterial"
        ] = "pec"
cable_props["CableManager"]["Definitions"]["CableBundle"]["BundleParams"]["BraidShieldJacketParams"][
            "InnerDiameter"
        ] = "6mm"
cable_props["CableManager"]["Definitions"]["CableBundle"]["BundleParams"]["BraidShieldJacketParams"][
            "NumCarriers"
        ] = "36"
cable_props["CableManager"]["Definitions"]["CableBundle"]["BundleParams"]["BraidShieldJacketParams"][
            "NumWiresInCarrier"
        ] = "52"
cable_props["CableManager"]["Definitions"]["CableBundle"]["BundleParams"]["BraidShieldJacketParams"][
            "WireDiameter"
        ] = "0.242424mm"
cable_props["CableManager"]["Definitions"]["CableBundle"]["BundleParams"]["BraidShieldJacketParams"][
            "WeaveAngle"
        ] = "33deg"
cable_props["CableManager"]["Definitions"]["CableBundle"]["BundleAttribs"]["Name"] = "Bundle_Cable_Shielding"

cable = Cable(hfss, cable_props)
cable.create_cable()

###############################################################################
# Update cable bundle
# ~~~~~~~~~~~~~~~~~~~
# The first cable bundle (insulation jacket type) is updated.

cable_props["Update_Cable"] = "True"
cable_props["Cable_prop"]["IsJacketTypeNoJacket"] = "False"
cable_props["Cable_prop"]["IsJacketTypeBraidShield"] = "False"
cable_props["Cable_prop"]["IsJacketTypeInsulation"] = "True"
cable_props["CableManager"]["Definitions"]["CableBundle"]["BundleAttribs"]["Name"] = "Bundle_Cable_Insulation"
cable_props["Cable_prop"]["UpdatedName"] = "New_updated_name_cable_bundle_insulation"
cable_props["CableManager"]["Definitions"]["CableBundle"]["BundleParams"]["InsulationJacketParams"][
            "InsThickness"
        ] = "4mm"
cable_props["CableManager"]["Definitions"]["CableBundle"]["BundleParams"]["InsulationJacketParams"][
            "JacketMaterial"
        ] = "pec"
cable_props["CableManager"]["Definitions"]["CableBundle"]["BundleParams"]["InsulationJacketParams"][
            "InnerDiameter"
        ] = "1.2mm"

cable = Cable(hfss, cable_props)
cable.update_cable_properties()

###############################################################################
# Create straight wire cable
# ~~~~~~~~~~~~~~~~~~~~~~~~~~
# Create straight wire cable.

cable_props["Add_Cable"] = "True"
cable_props["Cable_prop"]["CableType"] = "straight wire"
cable_props["Update_Cable"] = "False"
cable_props["CableManager"]["Definitions"]["StWireCable"]["StWireParams"]["WireStandard"] = "ISO"
cable_props["CableManager"]["Definitions"]["StWireCable"]["StWireParams"]["WireGauge"] = "2.5"
cable_props["CableManager"]["Definitions"]["StWireCable"]["StWireParams"]["CondDiameter"] = "10mm"
cable_props["CableManager"]["Definitions"]["StWireCable"]["StWireParams"]["CondMaterial"] = "pec"
cable_props["CableManager"]["Definitions"]["StWireCable"]["StWireParams"]["InsThickness"] = "0.9mm"
cable_props["CableManager"]["Definitions"]["StWireCable"]["StWireParams"]["InsMaterial"] = "copper"
cable_props["CableManager"]["Definitions"]["StWireCable"]["StWireParams"]["InsType"] = "Thin Wall"
cable_props["CableManager"]["Definitions"]["StWireCable"]["StWireAttribs"]["Name"] = "straight_wire_cable"

cable = Cable(hfss, cable_props)
cable.create_cable()

# Create 3 straight wire cables for late to create the cable harness.

cable_props["CableManager"]["Definitions"]["StWireCable"]["StWireAttribs"]["Name"] = "stwire1"
cable = Cable(hfss, cable_props)
cable.create_cable()
cable_props["CableManager"]["Definitions"]["StWireCable"]["StWireAttribs"]["Name"] = "stwire2"
cable = Cable(hfss, cable_props)
cable.create_cable()
cable_props["CableManager"]["Definitions"]["StWireCable"]["StWireAttribs"]["Name"] = "stwire3"
cable = Cable(hfss, cable_props)
cable.create_cable()

###############################################################################
# Create twisted pair cable
# ~~~~~~~~~~~~~~~~~~~~~~~~~
# Create twisted pair cable.

cable_props["Add_Cable"] = "True"
cable_props["Cable_prop"]["CableType"] = "twisted pair"
cable_props["Update_Cable"] = "False"
cable_props["CableManager"]["Definitions"]["TwistedPairCable"]["TwistedPairParams"][
            "StraightWireCableID"
        ] = 1023
cable_props["CableManager"]["Definitions"]["TwistedPairCable"]["TwistedPairParams"][
            "IsLayLengthSpecified"
        ] = "False"
cable_props["CableManager"]["Definitions"]["TwistedPairCable"]["TwistedPairParams"]["LayLength"] = "34mm"
cable_props["CableManager"]["Definitions"]["TwistedPairCable"]["TwistedPairParams"]["TurnsPerMeter"] = "99"
cable_props["CableManager"]["Definitions"]["TwistedPairCable"]["TwistedPairAttribs"][
            "Name"
        ] = "twisted_pair_cable"

cable = Cable(hfss, cable_props)
cable.create_cable()

###############################################################################
# Add cables to bundle
# ~~~~~~~~~~~~~~~~~~~~
# Add straight wire cables to bundle.

cable_props["Add_Cable"] = "False"
cable_props["Update_Cable"] = "False"
cable_props["Add_CablesToBundle"] = "True"
cable_props["CablesToBundle_prop"]["CablesToAdd"] = "straight_wire_cable"
cable_props["CablesToBundle_prop"]["BundleCable"] = "New_updated_name_cable_bundle_insulation"
cable_props["CablesToBundle_prop"]["NumberOfCableToAdd"] = 3

cable = Cable(hfss, cable_props)
cable.add_cable_to_bundle()

###############################################################################
# Remove a cable or a list of cables
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Remove a cable or a list of cables.

cable_props["Add_Cable"] = "False"
cable_props["Update_Cable"] = "False"
cable_props["Add_CablesToBundle"] = "False"
cable_props["Remove_Cable"] = "True"
cable_props["Cable_prop"]["CablesToRemove"] = "Bundle_Cable_Shielding"

cable = Cable(hfss, cable_props)
cable.remove_cables()

###############################################################################
# Create clock sources
# ~~~~~~~~~~~~~~~~~~~~
# Create and update a clock source.

cable_props["Add_Cable"] = "False"
cable_props["Update_Cable"] = "False"
cable_props["Add_CablesToBundle"] = "False"
cable_props["Remove_Cable"] = "False"
cable_props["Add_Source"] = "True"
cable_props["Source_prop"]["AddClockSource"] = "True"
cable_props["CableManager"]["TDSources"]["ClockSourceDef"]["ClockSignalParams"]["Period"] = "40us"
cable_props["CableManager"]["TDSources"]["ClockSourceDef"]["ClockSignalParams"]["LowPulseVal"] = "0.1V"
cable_props["CableManager"]["TDSources"]["ClockSourceDef"]["ClockSignalParams"]["HighPulseVal"] = "2V"
cable_props["CableManager"]["TDSources"]["ClockSourceDef"]["ClockSignalParams"]["Risetime"] = "5us"
cable_props["CableManager"]["TDSources"]["ClockSourceDef"]["ClockSignalParams"]["Falltime"] = "10us"
cable_props["CableManager"]["TDSources"]["ClockSourceDef"]["ClockSignalParams"]["PulseWidth"] = "23us"
cable_props["CableManager"]["TDSources"]["ClockSourceDef"]["TDSourceAttribs"]["Name"] = "clock_test_1"

cable = Cable(hfss, cable_props)
cable.create_clock_source()

cable_props["Add_Source"] = "False"
cable_props["Update_Source"] = "True"
cable_props["Source_prop"]["UpdateClockSource"] = "True"
cable_props["Source_prop"]["UpdatedSourceName"] = "update_clock_test_1"
cable_props["CableManager"]["TDSources"]["ClockSourceDef"]["TDSourceAttribs"]["Name"] = "clock_test_1"
cable_props["CableManager"]["TDSources"]["ClockSourceDef"]["ClockSignalParams"]["Period"] = "45us"
cable_props["CableManager"]["TDSources"]["ClockSourceDef"]["ClockSignalParams"]["LowPulseVal"] = "0.3V"
cable_props["CableManager"]["TDSources"]["ClockSourceDef"]["ClockSignalParams"]["HighPulseVal"] = "3V"
cable_props["CableManager"]["TDSources"]["ClockSourceDef"]["ClockSignalParams"]["Risetime"] = "4us"
cable_props["CableManager"]["TDSources"]["ClockSourceDef"]["ClockSignalParams"]["Falltime"] = "15us"
cable_props["CableManager"]["TDSources"]["ClockSourceDef"]["ClockSignalParams"]["PulseWidth"] = "26us"

cable = Cable(hfss, cable_props)
cable.update_clock_source()

###############################################################################
# Create pwl sources
# ~~~~~~~~~~~~~~~~~~
# Create a pwl source.

cable_props["Add_Cable"] = "False"
cable_props["Update_Cable"] = "False"
cable_props["Add_CablesToBundle"] = "False"
cable_props["Remove_Cable"] = "False"
cable_props["Add_Source"] = "True"
cable_props["Update_Source"] = "False"
cable_props["Source_prop"]["AddClockSource"] = "False"
cable_props["Source_prop"]["AddPwlSource"] = "True"
cable_props["CableManager"]["TDSources"]["PWLSourceDef"]["PWLSignalParams"]["SignalValues"] = [
            "0V",
            "0.5V",
            "0V",
            "3V",
            "4V",
            "0V",
        ]
cable_props["CableManager"]["TDSources"]["PWLSourceDef"]["PWLSignalParams"]["TimeValues"] = [
            "0ns",
            "1ns",
            "2ns",
            "3ns",
            "4ns",
            "5ns",
        ]
cable_props["CableManager"]["TDSources"]["PWLSourceDef"]["TDSourceAttribs"]["Name"] = "pwl4"

cable = Cable(hfss, cable_props)
cable.create_pwl_source()

# Update a pwl source.

cable_props["Add_Source"] = "False"
cable_props["Update_Source"] = "True"
cable_props["Source_prop"]["AddClockSource"] = "False"
cable_props["Source_prop"]["AddPwlSource"] = "False"
cable_props["Source_prop"]["UpdateClockSource"] = "False"
cable_props["Source_prop"]["UpdatePwlSource"] = "True"
cable_props["Source_prop"]["UpdatedSourceName"] = "update_pwl_source"
cable_props["CableManager"]["TDSources"]["PWLSourceDef"]["PWLSignalParams"]["SignalValues"] = [
            "0V",
            "0.5V",
            "0V",
            "3V",
            "4V",
            "9V",
            "0V",
        ]
cable_props["CableManager"]["TDSources"]["PWLSourceDef"]["PWLSignalParams"]["TimeValues"] = [
            "0ns",
            "1ns",
            "2ns",
            "3ns",
            "4ns",
            "5ns",
            "6ns",
        ]
cable_props["CableManager"]["TDSources"]["PWLSourceDef"]["TDSourceAttribs"]["Name"] = "pwl1"
cable_props["Source_prop"]["UpdatedSourceName"] = "updated_pwl1"

cable = Cable(hfss, cable_props)
cable.update_pwl_source()

# Create a pwl source from file.

pwl_path = pyaedt.downloads.download_file("cable_modeling", "import_pwl.pwl", temp_folder)

cable_props["Add_Source"] = "True"
cable_props["Update_Source"] = "False"
cable_props["Source_prop"]["AddClockSource"] = "False"
cable_props["Source_prop"]["AddPwlSource"] = "True"
cable_props["Source_prop"]["UpdateClockSource"] = "False"
cable_props["Source_prop"]["UpdatePwlSource"] = "False"
cable_props["Source_prop"]["AddPwlSourceFromFile"] = pwl_path

cable = Cable(hfss, cable_props)
cable.create_pwl_source_from_file()

# Remove clock source.

cable_props["Add_Cable"] = "False"
cable_props["Update_Cable"] = "False"
cable_props["Add_CablesToBundle"] = "False"
cable_props["Remove_Cable"] = "False"
cable_props["Add_Source"] = "False"
cable_props["Update_Source"] = "False"
cable_props["Remove_Source"] = "True"
cable_props["Source_prop"]["AddClockSource"] = "False"
cable_props["Source_prop"]["AddPwlSource"] = "False"
cable_props["Source_prop"]["SourcesToRemove"] = "update_clock_test_1"

cable = Cable(hfss, cable_props)
cable.remove_source()

###############################################################################
# Create cable harness
# ~~~~~~~~~~~~~~~~~~~~
# Create cable harness.

cable_props["Add_Cable"] = "False"
cable_props["Update_Cable"] = "False"
cable_props["Add_CablesToBundle"] = "False"
cable_props["Remove_Cable"] = "False"
cable_props["Add_Source"] = "False"
cable_props["Update_Source"] = "False"
cable_props["Remove_Source"] = "False"
cable_props["Add_CableHarness"] = "True"
cable_props["CableHarness_prop"]["Name"] = "cable_harness_test"
cable_props["CableHarness_prop"]["Bundle"] = "New_updated_name_cable_bundle_insulation"
cable_props["CableHarness_prop"]["TwistAngleAlongRoute"] = "20deg"
cable_props["CableHarness_prop"]["Polyline"] = "Polyline1"
cable_props["CableHarness_prop"]["AutoOrient"] = "False"
cable_props["CableHarness_prop"]["XAxis"] = "Undefined"
cable_props["CableHarness_prop"]["XAxisOrigin"] = ["0mm", "0mm", "0mm"]
cable_props["CableHarness_prop"]["XAxisEnd"] = ["0mm", "0mm", "0mm"]
cable_props["CableHarness_prop"]["ReverseYAxisDirection"] = "True"
cable_props["CableHarness_prop"]["CableTerminationsToInclude"][0]["CableName"] = "straight_wire_cable"
cable_props["CableHarness_prop"]["CableTerminationsToInclude"][1]["CableName"] = "straight_wire_cable1"
cable_props["CableHarness_prop"]["CableTerminationsToInclude"][2]["CableName"] = "straight_wire_cable2"

cable = Cable(hfss, cable_props)
cable.create_cable_harness()

###############################################################################
# Plot model
# ~~~~~~~~~~
# Plot the model.

hfss.plot(show=False, export_path=os.path.join(hfss.working_directory, "Cable.jpg"), plot_air_objects=True)


###############################################################################
# Save project and close AEDT
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Save the project and close AEDT.

hfss.save_project()
hfss.release_desktop()
