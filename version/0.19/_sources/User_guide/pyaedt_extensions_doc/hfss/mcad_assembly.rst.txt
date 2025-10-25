Cad assembly
=============

With this extension, you can assemble 3D components, 3D layout components in HFSS 3D from a predefined configure file.

Below is an example configure file in json format

.. code-block:: python

    {
        "component_models": {
        "case": "E:\\Chassi.a3dcomp",
        },
        "layout_component_models": {
        "pcb": "E:\\DCDC-Converter-App_main.aedbcomp"
        },
        # Create global coordinate system
        "coordinate_system": {
            # Name of the coordinate system
            "CS_1": {
                # Location of the new coordinate system
                "origin": ["100mm", "0mm", "0mm"],
                "reference_cs": "Global"
            },
        },
        # Assembly contains all components to be assembled
        "assembly": {
            # Name of the component
            "case": {
                # Type of the component. Available types are "mcad" for 3D components and "ecad" for 3D layout
                # components.
                "component_type": "mcad",
                # Absolute path to the component file
                "model": "case",
                # Local coordinate system of the component
                "reference_coordinate_system": "Global",
                # Target coordinate system where the component will be placed
                "target_coordinate_system": "CS_1",
                # Operations to be performed on the component.
                # Available operations are "rotate", "move"
                "arranges": [
                    {"operation": "rotate", "axis": "X", "angle": "0deg"},
                    {"operation": "move", "vector": ["0mm", "0mm", "0mm"]}
                ],
                # Child components, if any
                "sub_components": {
                    "pcb": {
                        "component_type": "mcad",
                        "model": "pcb",
                        # Target coordinate system must be defined in its parent component
                        "target_coordinate_system": "CS_CHASSIS",
                    },
                }
            }
        }
    }

----------
How to use
----------

1, Download the example files from `example_files`_ (under construction).

2, Launch AEDT and create a new HFSS 3D design.

3, Launch the extension from the extension manager.

4, Click ``Load Configure File`` and select the ``assembly_config.json`` file. The content of the file is displayed in
the UI.

.. image:: ../../../_static/extensions/mcad_assembly_1.svg
   :alt:  MCAD Assembly
   :width: 800px

6, Click ``Run``. The assembly is created in the design.

.. image:: ../../../_static/extensions/mcad_assembly_2.svg
   :alt:  MCAD Assembly
   :width: 800px

.. _example_files: https://
