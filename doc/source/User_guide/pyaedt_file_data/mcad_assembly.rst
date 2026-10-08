Configuration file for MCAD assembly
====================================

Example 1, assembly RLC components on a PCB in HFSS 3D
-----------------------------------------------------------------------

.. code:: python

    from pathlib import Path
    from ansys.aedt.core import Hfss
    from ansys.aedt.core.modeler.advanced_cad.mcad_assembly import run
    from ansys.aedt.core.modeler.advanced_cad.mcad_assembly import MCADAssembly

    # Resolve paths relative to this script so the example can be moved as a folder.
    CUR_DIR = Path(__file__).resolve().parent

    # Build the top-level ECAD/MCAD assembly definition.
    top_assembly = MCADAssembly()
    # Register the PCB database that will be used as the ECAD source.
    top_assembly.add_ecad_component_model(name="LimeSDR", path=str(CUR_DIR / "models/edb/LimeSDR-USB_1v4s_analog.aedb"))
    # Register the mechanical component that will be placed on the PCB.
    top_assembly.add_mcad_component_model(name="cap0402", path=str(CUR_DIR / "models/a3d_library/CAP0402_100nF_26R1.a3dcomp"))

    # Add the board instance to the assembly using the registered ECAD model.
    pcb = top_assembly.add_sub_ecad_component(name="pcb", model="LimeSDR")

    # Add a child MCAD component under the PCB so it can be positioned from layout data.
    cap = pcb.add_sub_mcad_component(name="cap", model="cap0402")
    # Enable placement by pin mapping instead of free-space coordinates.
    cap.use_pin_mapping = True
    # Use reference designator MN20 on the PCB to drive the component placement.
    cap.placement_pin_mapping.reference_designator = "MN20"
    # Define the local origin and pin-1 direction used to orient the 3D component.
    cap.placement_pin_mapping.pin_1_loc = [0.0, 0.0, 0.0]
    cap.placement_pin_mapping.pin_1_loc = [0.7375e-3, 0, 0]

    # Launch HFSS/AEDT, execute the assembly import workflow, then leave AEDT open.
    hfss = Hfss(version="2026.1")
    run(config_data=top_assembly.model_dump(), version="2026.1")
    hfss.release_desktop(close_desktop=False, close_projects=False)

Example 2, assembly RLC components on a PCB from the library in HFSS 3D
-----------------------------------------------------------------------

.. image:: ../../../_static/extensions/mcad_assembly_4.png
   :alt:  MCAD Assembly Example
   :width: 800

.. code:: python

    from pathlib import Path
    from ansys.aedt.core import Hfss
    from ansys.aedt.core.modeler.advanced_cad.mcad_assembly import run
    from ansys.aedt.core.modeler.advanced_cad.mcad_assembly import MCADAssembly


    CUR_DIR = Path(__file__).resolve().parent

    top_assembly = MCADAssembly()
    top_assembly.add_ecad_component_model(name="LimeSDR", path=str(CUR_DIR / "models/edb/LimeSDR-USB_1v4s_analog.aedb"))

    pcb = top_assembly.add_sub_ecad_component(name="pcb", model="LimeSDR")

    pcb.add_sub_mcad_component_from_library(library_path=str(CUR_DIR / "models/a3d_library"))
    pcb.assembly_all_from_library = True

    hfss = Hfss(version="2026.1")
    run(config_data=top_assembly.model_dump(), version="2026.1")
    hfss.release_desktop(close_desktop=False, close_projects=False)

Example 3, assemble a PCB into a chassis
----------------------------------------

.. image:: ../../../_static/extensions/mcad_assembly_3.png
   :alt:  MCAD Assembly Example
   :width: 800

.. code:: python

    import json
    from pathlib import Path

    from ansys.aedt.core import Hfss
    from ansys.aedt.core.modeler.advanced_cad.mcad_assembly import run
    from ansys.aedt.core.modeler.advanced_cad.mcad_assembly import MCADAssembly

    CUR_DIR = Path(__file__).parent

    # Initial the configuration class
    config = MCADAssembly()


    # Add chassis model path
    config.add_mcad_component_model(
        name="chassis", path= str(CUR_DIR / "models/Chassi.a3dcomp")
    )

    # Add layout component path
    config.add_ecad_component_model(
        name="pcb", path= str(CUR_DIR / "models/DCDC-Converter-App_main.aedbcomp")
    )

    # Add a coordinate system to place the chassis.
    cs = config.add_coordinate_system(name="GLOBAL_2")
    cs.origin = ["100mm", "0mm", "0mm"]

    # Place the chassis into HFSS 3D modeler
    box = config.add_sub_mcad_component(name="box", model="chassis")
    box.target_coordinate_system = "GLOBAL_2"
    box.reference_coordinate_system = "GLOBAL_2"

    # Assemble PCB into the chassis
    pcb = box.add_sub_ecad_component(name="pcb", model="pcb")
    pcb.target_coordinate_system = "Guiding_Pin"
    # Include guiding hole padstack instance when inserting the PCB
    pcb.layout_coordinate_systems = ["H0_via_65"]
    pcb.reference_coordinate_system = "H0_via_65"

    # Save configuration as a JSON file. Optional.
    output_path = CUR_DIR / "assembly_config.json"
    with output_path.open("w", encoding="utf-8") as f:
        json.dump(config.model_dump(exclude_none=True), f, indent=4)

    # Do the assembly
    hfss = Hfss(version="2026.1")
    run(config_data=output_path, model_dir=str(CUR_DIR))
    hfss.release_desktop(close_desktop=False, close_projects=False)


Resources
---------
- `MCAD Assembly Extension Examples <https://github.com/ansys-internal/pyaedt-extension-examples/tree/main/HFSS/MCAD%20Assembly>`_.(Ask Ansys support for more information)
- The example board is from https://github.com/myriadrf/LimeSDR-USB