Substrate
=========
This section describes the Circuit substrate modules, which provide classes and methods
to manage substrate data blocks in Circuit designs.

A substrate data block defines the physical and electrical properties of a transmission-line
substrate (microstrip, stripline, CPW, ...) and is referenced by distributed circuit
elements inside an AEDT Circuit design.

SubstrateManager
~~~~~~~~~~~~~~~~

The :class:`SubstrateManager` is the main entry point, accessible through
:attr:`ansys.aedt.core.Circuit.substrate`. Use it to add, query, and delete substrate
data blocks in the active Circuit design.

.. currentmodule:: ansys.aedt.core.modules.substrate_circuit

.. autosummary::
   :toctree: _autosummary
   :nosignatures:

   SubstrateManager


.. code:: python

    from ansys.aedt.core import Circuit

    app = Circuit(
        version="2026.1",
        non_graphical=False,
    )

    # Add a microstrip substrate
    sub = app.substrate.add_microstrip("10mil", 4.4, 0.02, "25mm", name="MySub")

    # List all substrate names in the design
    print(app.substrate.names)

    # Modify a property and push it to AEDT
    sub.permittivity = 3.5

    # Delete the substrate
    app.substrate.delete("MySub")


SubstrateDataBlock
~~~~~~~~~~~~~~~~~~

The :class:`SubstrateDataBlock` represents a single substrate definition. Each instance
exposes read and write properties for the substrate geometry and material parameters
(height, permittivity, loss tangent, conductor thickness, ...) as well as a
:meth:`~SubstrateDataBlock.update` method to push changes back to AEDT.

.. currentmodule:: ansys.aedt.core.modules.substrate_circuit

.. autosummary::
   :toctree: _autosummary
   :nosignatures:

   SubstrateDataBlock
