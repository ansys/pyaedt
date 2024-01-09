Project Configuration file
==========================

The project configuration file is the most comprehensive format that allows to apply a set of variables, materials,
setup, mesh and boundaries to a new project or save an existing one.
This file can be created using the following command:

.. code:: python

    from pyaedt import Icepak
    ipk = Icepak()
    filename = "test"
    ipk.export_3d_model(file_name=filename,
                        file_path=ipk.working_directory,
                        file_format=".step",
                        object_list=[],
                        removed_objects=[])
    conf_file = ipk.configurations.export_config()


The command is often combined with the ``export_3d_model`` method which allows to export the geometry
to a 3D cad format.
In the same way the file can be imported using the following command:


.. code:: python

    app.modeler.import_3d_cad(file_path)
    out = app.configurations.import_config(conf_file)

The main file skeleton is shown below.
Few example files can be found at:

:download:`Icepak Example <../../Resources/icepak_project_example.json>`

:download:`HFSS 3D Layout Example <../../Resources/hfss3dlayout_project_example.json>`

.. code-block:: json

    {
        "general": {
            "pyaedt_version": "0.8.dev0",
            "model_units": "mm",
            "design_name": "IcepakDesign1",
            "date": "09/01/2024 08:22:17",
            "object_mapping": {
                # object_id: [
                #     object_name,
                #    object_center
                # ],
                "12": [
                    "Region",
                    [
                        80.0,
                        14.243,
                        -55.0
                    ]
                ]
            },
            "output_variables": {},
            "variables": {},
            "postprocessing_variables": {}
        },
        "setups": {
            # Setup Name : {Setup Properties}
            "MySetupAuto": {
                "Enabled": true,
                "Flow Regime": "Turbulent",
                "Include Temperature": true,
            }
        },
        "boundaries": {
            # Boundary Name : {Boundary Properties}
            "CPU": {
                "Objects": [
                    "CPU"
                ],
                "Block Type": "Solid",
                "Use External Conditions": false,
                "Total Power": "25W",
                "BoundType": "Block"
            },
        },
        "mesh": {
            "Settings": {
                # mesh_properties,
                "MeshMethod": "MesherHD",
                "UserSpecifiedSettings": true,
                "ComputeGap": true,
                "MaxElementSizeX": "16mm",
                "MaxElementSizeY": "3.5mm",
                "MaxElementSizeZ": "11mm",
                # ....
            }
        },
        "materials": {
            # Material Name : {Material Properties}
            "Al-Extruded": {
                "CoordinateSystemType": "Cartesian",
                "BulkOrSurfaceType": 1,
                "PhysicsTypes": {
                    "set": [
                        "Thermal"
                    ]
                },
                "AttachedData": {
                    "MatAppearanceData": {
                        "property_data": "appearance_data",
                        "Red": 232,
                        "Green": 235,
                        "Blue": 235
                    }
                },
                "thermal_conductivity": "205",
                "mass_density": "2800",
                "specific_heat": "900",
                "thermal_material_type": {
                    "property_type": "ChoiceProperty",
                    "Choice": "Solid"
                },
                "clarity_type": {
                    "property_type": "ChoiceProperty",
                    "Choice": "Opaque"
                }
            },
        },
        "objects": {
            # Object Name: {object properties}
            "Region": {
                "SurfaceMaterial": "",
                "Material": "air",
                "SolveInside": true,
                "Model": true,
                "Group": "",
                "Transparency": 0.0,
                "Color": [
                    255,
                    0,
                    0
                ],
                "CoordinateSystem": "Global"
            },

        },
        "datasets": [
            # Dataset Name : {Dataset Properties}
        ],
        "monitors": [
            # Monitor Name : {Monitor Properties}
    ],
        "native components": {
            # Component Name : {Component Properties}

    }
    }



