Project configuration file
==========================

The project configuration file is the most comprehensive format that allows to apply a set of variables, materials,
setup, mesh, and boundaries to a new project or save an existing one.
This code creates the JSON file:

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
    ipk.release_desktop()


This code imports the project configuration from the JSON file:


.. code:: python

    app.modeler.import_3d_cad(file_path)
    out = app.configurations.import_config(conf_file)

File structure examples:

:download:`Icepak Example <../../Resources/icepak_project_example.json>`

:download:`HFSS 3D Layout Example <../../Resources/hfss3dlayout_project_example.json>`

.. code-block::

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

For a practical demonstration, see the
`Project configuration file example <https://aedt.docs.pyansys.com/version/stable/examples/01-Modeling-Setup/Configurations.html#sphx-glr-examples-01-modeling-setup-configurations-py>`_
