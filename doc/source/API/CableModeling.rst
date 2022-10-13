Cable modeling
==============
The ``Cable Modeling`` module includes several methods to work
with the Cable Modeling HFSS Beta feature:


* ``create_cable`` to create all available types of cables: bundle, straight wire and twisted pair.
* ``update_cable_properties`` to update all cables properties for all cable types.
* ``update_shielding`` to update only the shielding jacket type for bundle cable.
* ``remove_cables`` to remove cables.
* ``add_cable_to_bundle`` to add a cable or a list of cables to a bundle.
* ``create_clock_source`` to create a clock source.
* ``update_clock_source`` to update a clock source.
* ``remove_source`` to remove a source.
* ``remove_all_sources`` to remove all sources.
* ``create_pwl_source`` to create a pwl source.
* ``create_pwl_source_from_file`` to create a pwl source from file.
* ``update_pwl_source`` to update a pwl source.
* ``create_cable_harness`` to create a cable harness.

They are accessible through:

.. currentmodule:: pyaedt.modules

.. autosummary::
   :toctree: _autosummary
   :nosignatures:

   CableModeling.Cable

Cable bundle creation example:

.. code:: python

    from pyaedt import Hfss
    from pyaedt.generic.DataHandlers import json_to_dict
    from pyaedt.modules.CableModeling import Cable

    hfss = Hfss(projectname=project_path, specified_version="2022.1",
                 non_graphical=False, new_desktop_session=True,
                 close_on_exit=True, student_version=False)
    # This call returns a dictionary out of the JSON file
    cable_props = json_to_dict(json_path)
    # This example shows how to manually change from script the cable properties
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
    # This call returns the Cable class
    cable = Cable(hfss, cable_props)
    # This call creates the cable bundle
    cable.create_cable()

Clock source creation example:

.. code:: python

    from pyaedt import Hfss
    from pyaedt.generic.DataHandlers import json_to_dict
    from pyaedt.modules.CableModeling import Cable

    hfss = Hfss(projectname=project_path, specified_version="2022.1",
                 non_graphical=False, new_desktop_session=True,
                 close_on_exit=True, student_version=False)
    # This call returns a dictionary out of the JSON file
    cable_props = json_to_dict(json_path)
    # This example shows how to manually change from script the clock source properties
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
    # This call returns the Cable class
    cable = Cable(hfss, cable_props)
    # This call creates the clock source
    cable.create_clock_source()

Cable harness creation example:

.. code:: python

    from pyaedt import Hfss
    from pyaedt.generic.DataHandlers import json_to_dict
    from pyaedt.modules.CableModeling import Cable

    hfss = Hfss(projectname=project_path, specified_version="2022.1",
                 non_graphical=False, new_desktop_session=True,
                 close_on_exit=True, student_version=False)
    # This call returns a dictionary out of the JSON file
    cable_props = json_to_dict(json_path)
    # This example shows how to manually change from script the cable harness properties
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
    # This call returns the Cable class
    cable = Cable(hfss, cable_props)
    # This call creates the cable harness
    cable.create_cable_harness()