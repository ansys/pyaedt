.. _assembly-config-file:

Choke file
==========

The configuration file allows you to assemble 3D components, 3D layout components in HFSS 3D.

The code loads the configuration file and creates an assembled design in HFSS 3D:

.. code:: python

    from ansys.aedt.core.extensions.hfss.mcad_assembly import run

    run(config_data="assembly_config.json")

File structure example:

:download:`Choke example <../../Resources/assembly_config.json>`

This code creates a configure file and create an assembled design in HFSS 3D:

.. code:: python

    import json
    from pathlib import Path


    from ansys.aedt.core.extensions.hfss.mcad_assembly import Arrange
    from ansys.aedt.core.extensions.hfss.mcad_assembly import MCADAssemblyBackend
    from ansys.aedt.core.extensions.hfss.mcad_assembly import run

    CUR_DIR = Path(__file__).parent


    def create_config() -> MCADAssemblyBackend:

        top_assembly = MCADAssemblyBackend()
        top_assembly.add_mcad_component_model(
            name="case", path="mcad_assembly/Chassi.a3dcomp"
        )
        top_assembly.add_mcad_component_model(
            name="cable", path="mcad_assembly/Cable.a3dcomp"
        )
        top_assembly.add_mcad_component_model(
            name="clamp_monitor", path="mcad_assembly/BCI_MONITORING_CLAMP.a3dcomp"
        )
        top_assembly.add_mcad_component_model(
            name="cap0402", path="mcad_assembly/Capacitor_HFSS.a3dcomp"
        )
        top_assembly.add_ecad_component_model(
            name="pcb", path="mcad_assembly/DCDC-Converter-App_main.aedb"
        )

        cs = top_assembly.add_coordinate_system(name="GLOBAL_2")
        cs.origin = ["100mm", "0mm", "0mm"]
        cs = top_assembly.add_coordinate_system(name="CS_CLAMP")
        cs.origin = ["-130mm", "80mm", "12mm"]
        cs.reference_coordinate_system = "GLOBAL_2"

        sub_comp = top_assembly.add_sub_mcad_component(name="case", model="case")
        sub_comp.target_coordinate_system = "GLOBAL_2"
        sub_comp.reference_coordinate_system = "GLOBAL_2"

        sub_comp_ = sub_comp.add_sub_ecad_component(name="pcb", model="pcb")
        sub_comp_.target_coordinate_system = "Guiding_Pin"
        sub_comp_.layout_coordinate_systems = [
            "CABLE1_via_65",
            "CABLE2_via_65",
            "H0_via_65",
        ]
        sub_comp_.reference_coordinate_system = "H0_via_65"
        sub_comp_.arranges = [Arrange(operation="rotate", axis="X", angle="0deg")]

        sub_comp__ = sub_comp_.add_sub_mcad_component(name="cable_a", model="cable")
        sub_comp__.use_pin_mapping = True
        sub_comp__.placement_pin_mapping.reference_designator = "CABLE1"
        sub_comp__.placement_pin_mapping.pin_1_loc = (0, 0, 0)

        sub_comp__ = sub_comp_.add_sub_mcad_component(name="cable_b", model="cable")
        sub_comp__.use_pin_mapping = True
        sub_comp__.placement_pin_mapping.reference_designator = "CABLE2"
        sub_comp__.placement_pin_mapping.pin_1_loc = (0, 0, 0)

        sub_comp__ = sub_comp_.add_sub_mcad_component(name="cap_c4", model="cap0402")
        sub_comp__.use_pin_mapping = True
        sub_comp__.placement_pin_mapping.reference_designator = "C2"
        sub_comp__.placement_pin_mapping.pin_1_loc = (0, 0, 0)
        sub_comp__.placement_pin_mapping.pin_2_loc = (0.7375e-3, 0, 0)

        sub_comp__ = sub_comp_.add_sub_mcad_component(name="cap_c4", model="cap0402")
        sub_comp__.use_pin_mapping = True
        sub_comp__.placement_pin_mapping.reference_designator = "C3"
        sub_comp__.placement_pin_mapping.pin_1_loc = (0, 0, 0)
        sub_comp__.placement_pin_mapping.pin_2_loc = (0.7375e-3, 0, 0)

        sub_comp__ = sub_comp_.add_sub_mcad_component(name="cap_c4", model="cap0402")
        sub_comp__.use_pin_mapping = True
        sub_comp__.placement_pin_mapping.reference_designator = "C4"
        sub_comp__.placement_pin_mapping.pin_1_loc = (0, 0, 0)
        sub_comp__.placement_pin_mapping.pin_2_loc = (0.7375e-3, 0, 0)

        sub_comp__ = sub_comp_.add_sub_mcad_component(name="cap_r7", model="cap0402")
        sub_comp__.use_pin_mapping = True
        sub_comp__.placement_pin_mapping.reference_designator = "R7"
        sub_comp__.placement_pin_mapping.pin_1_loc = (0, 0, 0)
        sub_comp__.placement_pin_mapping.pin_2_loc = (0.7375e-3, 0, 0)

        sub_comp = top_assembly.add_sub_mcad_component(
            name="clamp_monitor", model="clamp_monitor"
        )
        sub_comp.target_coordinate_system = "CS_CLAMP"

        return top_assembly


    if __name__ == "__main__":
        config = create_config()

        output_path = CUR_DIR / "assembly_config.json"
        with output_path.open("w", encoding="utf-8") as f:
            json.dump(config.model_dump(exclude_none=True), f, indent=4)

        print(f"Saved JSON config to: {output_path}")

        run(config_data=output_path, model_dir=str(CUR_DIR))
