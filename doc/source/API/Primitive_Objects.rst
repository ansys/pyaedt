Primitives
==========

This section lists the core AEDT Modeler primitives that are supported both in 2D and 3D solvers (HFSS, Maxwell,
Icepak, Q3D, and Mechanical):

* Primitives
* Objects

They are accessible through the ``modeler.objects`` property:

.. code:: python

    from ansys.aedt.core import Hfss

    app = Hfss(
        version="2026.1",
        non_graphical=False,
        new_desktop=True,
        close_on_exit=True,
        student_version=False,
    )

    # This call return the Modeler3D class
    modeler = app.modeler

    # This call returns a Primitives3D object
    primitives = modeler

    # This call return an Object3d object
    my_box = primitives.create_box([0, 0, 0], [10, 10, 10])
    my_box = primitives.objects[my_box.id]

    # This call return a FacePrimitive object list
    my_box.faces
    # This call returns an EdgePrimitive object list
    my_box.edges
    my_box.faces[0].edges

    # This call returns a VertexPrimitive object list
    my_box.vertices
    my_box.faces[0].vertices
    my_box.faces[0].edges[0].vertices

    ...



Objects
~~~~~~~

The following classes define objects properties for 3D and 2D Solvers (excluding HFSS 3D Layout).
They contain all getters and setters to simplify object manipulation.



.. currentmodule:: ansys.aedt.core.modeler

.. autosummary::
   :toctree: _autosummary
   :nosignatures:

   cad.object_3d.Object3d
   cad.elements_3d.FacePrimitive
   cad.elements_3d.EdgePrimitive
   cad.elements_3d.VertexPrimitive
   cad.polylines.PolylineSegment
   cad.polylines.Polyline
   cad.component_array.ComponentArray
   cad.components_3d.UserDefinedComponent
   cad.elements_3d.Point
   cad.elements_3d.Plane
   cad.elements_3d.HistoryProps
   cad.elements_3d.BinaryTreeNode


.. code:: python

    from ansys.aedt.core import Hfss

    app = Hfss(
        version="2026.1",
        non_graphical=False,
        new_desktop=True,
        close_on_exit=True,
        student_version=False,
    )

    # This call returns the Modeler3D class
    modeler = app.modeler

    # This call returns a Primitives3D object
    primitives = modeler

    # This call returns an Object3d object
    my_box = primitives.create_box([0, 0, 0], [10, 10, 10])

    # Getter and setter
    my_box.material_name
    my_box.material_name = "copper"

    my_box.faces[0].center

    ...


Coordinate systems and geometry operators
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The module contains all properties and methods needed to edit a
coordinate system and a set of useful geometry operators.
The ``CoordinateSystem`` class is accessible through the ``create_coordinate_system``
method or the ``coordinate_systems`` list. The ``GeometryOperators`` class can be
imported and used because it is made by static methods.


.. currentmodule:: ansys.aedt.core.modeler

.. autosummary::
   :toctree: _autosummary
   :nosignatures:

   cad.modeler.CoordinateSystem
   geometry_operators.GeometryOperators


.. code:: python

    from ansys.aedt.core import Hfss

    app = Hfss(
        version="2026.1",
        non_graphical=False,
        new_desktop=True,
        close_on_exit=True,
        student_version=False,
    )

    # This call returns the CoordinateSystem object list
    cs = app.modeler.coordinate_systems

    # This call returns a CoordinateSystem object
    new_cs = app.modeler.create_coordinate_system()

    ...


Advanced modeler operations
~~~~~~~~~~~~~~~~~~~~~~~~~~~

PyAEDT provides higher-level modeling helpers that implement common CAD patterns and
parameterized workflows. Examples include ``MultiPartComponent`` for 3D component
management, ``Stackup3D`` for parametric stackup creation, and specialized helpers
such as ``Coil`` and ``Weave`` for winding and fiber-weave geometries. These helpers
wrap lower-level modeler primitives to offer reusable, parameter-driven operations;
they live in the ``ansys.aedt.core.modeler.advanced_cad`` package and are typically
instantiated with the application object.

.. currentmodule:: ansys.aedt.core.modeler.advanced_cad

.. autosummary::
   :toctree: _autosummary
   :nosignatures:

   coil.Coil
   weave.Weave
   choke.Choke
   mcad_assembly.MCADAssembly

.. toctree::
    :maxdepth: 2

    MultiPartComponent
    Stackup3D


MCAD Assembly
~~~~~~~~~~~~~

PyAEDT provides utilities to configure and manage multi-part assemblies combining
3D CAD models (MCAD) and PCB layouts (ECAD) in a hierarchical structure. The MCAD
assembly module enables automatic placement of 3D components based on PCB layouts,
coordinate system management, and component library resolution. Use the ``MCADAssembly``
class to define your assembly configuration, then pass it to the ``run()`` function
to build the assembly in HFSS.

.. currentmodule:: ansys.aedt.core.modeler.advanced_cad

.. autosummary::
   :toctree: _autosummary
   :nosignatures:

   mcad_assembly.run
   mcad_assembly.MCADAssembly
   mcad_assembly.MCADComponent
   mcad_assembly.ECADComponent
   mcad_assembly.CoordinateSystem
   mcad_assembly.Arrange
   mcad_assembly.PlacementPinMapping


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
    top_assembly.add_ecad_component_model(
        name="LimeSDR", path=str(CUR_DIR / "models/edb/LimeSDR-USB_1v4s_analog.aedb")
    )
    # Register the mechanical component that will be placed on the PCB.
    top_assembly.add_mcad_component_model(
        name="cap0402", path=str(CUR_DIR / "models/a3d_library/CAP0402_100nF_26R1.a3dcomp")
    )

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
    top_assembly.add_ecad_component_model(
        name="LimeSDR", path=str(CUR_DIR / "models/edb/LimeSDR-USB_1v4s_analog.aedb")
    )

    pcb = top_assembly.add_sub_ecad_component(name="pcb", model="LimeSDR")

    pcb.add_sub_mcad_component_from_library(
        library_path=str(CUR_DIR / "models/a3d_library")
    )
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
        name="chassis", path=str(CUR_DIR / "models/Chassi.a3dcomp")
    )

    # Add layout component path
    config.add_ecad_component_model(
        name="pcb", path=str(CUR_DIR / "models/DCDC-Converter-App_main.aedbcomp")
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
