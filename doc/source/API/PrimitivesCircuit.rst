Modeler and components Circuit
==============================

This section lists the core AEDT Modeler modules:

* Modeler
* Primitives
* Objects

They are accessible through the ``modeler`` module and ``modeler.objects`` property:

.. code:: python


    from pyaedt import TwinBuilder
    app = TwinBuilder(specified_version="2023.1",
               non_graphical=False, new_desktop_session=True,
               close_on_exit=True, student_version=False)

    # This call returns the Modeler class
    modeler = app.modeler

    ...


Modeler
~~~~~~~

The ``Modeler`` module contains all properties and methods needed to edit a
modeler, including all primitives methods and properties:

* ``ModelerNexxim`` for Circuit
* ``ModelerTwinBuilder`` for Twin Builder
* ``ModelerEmit`` for EMIT


.. currentmodule:: pyaedt.modeler

.. autosummary::
   :toctree: _autosummary
   :nosignatures:

   schematic.ModelerNexxim
   schematic.ModelerTwinBuilder
   schematic.ModelerEmit
   schematic.ModelerMaxwellCircuit


Schematic in Circuit
~~~~~~~~~~~~~~~~~~~~
The following classes define the object properties for Circuit components.
They contain all getters and setters to simplify object manipulation.

.. currentmodule:: pyaedt.modeler.circuits.PrimitivesNexxim

.. autosummary::
   :toctree: _autosummary
   :nosignatures:

   NexximComponents

.. code:: python

    from pyaedt import Circuit
    app = Circuit(specified_version="2023.1",
               non_graphical=False, new_desktop_session=True,
               close_on_exit=True, student_version=False)

    # This call returns a Schematic object
    schematic = modeler.schematic

    # This call returns an Object3d object
    my_res = schematic.create_resistor("R1", 50)


Objects in Circuit
~~~~~~~~~~~~~~~~~~
The following classes define the object properties for Circuit.
They contain all getters and setters to simplify object manipulation.

.. currentmodule:: pyaedt.modeler.circuits

.. autosummary::
   :toctree: _autosummary
   :nosignatures:

   object3dcircuit.CircuitComponent
   object3dcircuit.CircuitPins
   object3dcircuit.Wire

.. code:: python

    from pyaedt import Circuit
    app = Circuit(specified_version="2023.1",
               non_graphical=False, new_desktop_session=True,
               close_on_exit=True, student_version=False)

    # This call returns the Modeler class
    modeler = app.modeler

    # This call returns a Schematic object
    schematic = modeler.schematic

    # This call returns an Object3d object
    my_res = schematic.create_resistor("R1", 50)

    # Getter and setter
    my_res.location
    my_res.parameters["R"]=100

    ...

Schematic in EMIT
~~~~~~~~~~~~~~~~~
The following classes define the object properties for EMIT components.
They contain all getters and setters to simplify object manipulation.

.. currentmodule:: pyaedt.modeler.circuits.PrimitivesEmit

.. autosummary::
   :toctree: _autosummary
   :nosignatures:

   EmitComponents


Schematic in Twin Builder
~~~~~~~~~~~~~~~~~~~~~~~~~
The following classes define the object properties for Twin Builder components.
They contain all getters and setters to simplify object manipulation.

.. currentmodule:: pyaedt.modeler.circuits.PrimitivesTwinBuilder

.. autosummary::
   :toctree: _autosummary
   :nosignatures:

   TwinBuilderComponents

.. code:: python

    from pyaedt import TwinBuilder
    app = TwinBuilder(specified_version="2023.1",
               non_graphical=False, new_desktop_session=True,
               close_on_exit=True, student_version=False)

    # This call returns the Modeler class
    modeler = app.modeler

    # This call returns a Schematic object
    schematic = modeler.schematic

    # This call returns an Object3d object
    my_res = schematic.create_resistor("R1", 50)

    # Getter and setter
    my_res.location
    my_res.parameters["R"]=100

    ...


Schematic in Maxwell Circuit
~~~~~~~~~~~~~~~~~~~~~~~~~~~~
The following classes define the object properties for Maxwell Circuit components.
They contain all getters and setters to simplify object manipulation.

.. currentmodule:: pyaedt.modeler.circuits.PrimitivesMaxwellCircuit

.. autosummary::
   :toctree: _autosummary
   :nosignatures:

   MaxwellCircuitComponents
