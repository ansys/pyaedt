EMIT design
===========
This section describes the classes used for building and querying EMIT designs through the ``emit_core`` module.
The module provides tools for constructing RF system schematics, defining coupling between antennas, and
analyzing electromagnetic interference.


Node tree overview
~~~~~~~~~~~~~~~~~~
An EMIT design organizes its data into three main trees. Each tree is rooted at a
well-known node class and contains typed child nodes that the user can create,
inspect, and modify through the PyAEDT API.

.. code-block:: text

   EMIT Design
   │
   ├── Scene (EmitSceneNode)
   │   ├── Antenna / Emitter (AntennaNode)
   │   │   └── AntennaPassband  [0..*]
   │   ├── SceneGroupNode  [0..*]
   │   │   └── (any Scene child: Antenna, CAD, nested Group)
   │   └── CADNode  [0..*]
   │
   ├── Coupling Data (CouplingsNode)
   │   ├── TouchstoneCouplingNode       [0..*]
   │   ├── CustomCouplingNode           [0..*]
   │   ├── ErcegCouplingNode            [0..*]
   │   ├── FiveGChannelModel            [0..*]
   │   ├── HataCouplingNode             [0..*]
   │   ├── IndoorPropagationCouplingNode[0..*]
   │   ├── LogDistanceCouplingNode      [0..*]
   │   ├── PropagationLossCouplingNode  [0..*]
   │   ├── WalfischCouplingNode         [0..*]
   │   ├── TwoRayPathLossCouplingNode   [0..*]
   │   └── CouplingLinkNode             [0..*]
   │       └── SolutionCouplingNode
   │           └── SolutionsNode
   │
   └── Components (via EmitSchematic)
       ├── Amplifier
       ├── Cable
       ├── Circulator
       ├── Filter
       ├── Isolator
       ├── Multiplexer
       │   └── MultiplexerBand  [2..*]  (one per port minus one)
       ├── PowerDivider
       ├── RadioNode
       │   ├── SamplingNode  [1]
       │   ├── BandFolder  [0..*]
       │   │   └── Band  [0..*]
       │   └── Band  [0..*]
       │       ├── TxSpectralProfNode  [1]
       │       │   ├── TxSpurNode          [0..1]
       │       │   ├── TxNbEmissionNode    [0..1]
       │       │   ├── TxBbEmissionNode    [0..1]
       │       │   └── TxHarmonicNode      [0..1]
       │       ├── RxSusceptibilityProfNode  [1]
       │       │   ├── RxMixerProductNode  [0..1]
       │       │   ├── RxSaturationNode    [0..1]
       │       │   ├── RxSelectivityNode   [0..1]
       │       │   └── RxSpurNode          [0..1]
       │       ├── TxMeasNode  [0..*]
       │       └── RxMeasNode  [0..*]
       ├── Terminator
       └── TR_Switch


Scene
~~~~~
The scene tree organizes the physical layout of an EMIT design: antennas, emitters,
3-D geometry (CAD), and grouping nodes.

* ``EmitSceneNode`` is the root of the scene tree. It is obtained from a
  ``Revision`` after analysis.
* ``AntennaNode`` defines the position, orientation, and 3-D radiation pattern of
  an antenna or emitter. Antennas may contain ``AntennaPassband`` children that add
  frequency-dependent behavior to parametric antenna models.
* ``SceneGroupNode`` groups antennas, CAD nodes, or other groups so they can be
  repositioned and reoriented together. Any node type that can be a child of the
  scene can also be a child of a group.
* ``CADNode`` represents imported 3-D platform geometry.

They are accessible through:

.. currentmodule:: ansys.aedt.core.emit_core.nodes.generated

.. autosummary::
   :toctree: _autosummary
   :nosignatures:

   emit_scene_node.EmitSceneNode
   antenna_node.AntennaNode
   antenna_passband.AntennaPassband
   scene_group_node.SceneGroupNode
   cad_node.CADNode


Coupling data
~~~~~~~~~~~~~
The coupling data tree organizes the coupling models that connect pairs of antennas
in the design. The ``CouplingsNode`` can have any number of children, and their
**order matters**: children lower in the tree have higher priority. When an
antenna pair is covered by overlapping coupling definitions, the highest-priority
(lowest in tree) coupling is used.

* ``CouplingLinkNode`` provides a link to an HFSS design. It has a
  ``SolutionCouplingNode`` child and a ``SolutionsNode`` grandchild.

All other coupling children are standalone propagation or data-driven models.

They are accessible through:

.. currentmodule:: ansys.aedt.core.emit_core.nodes.generated

.. autosummary::
   :toctree: _autosummary
   :nosignatures:

   couplings_node.CouplingsNode
   touchstone_coupling_node.TouchstoneCouplingNode
   custom_coupling_node.CustomCouplingNode
   erceg_coupling_node.ErcegCouplingNode
   five_g_channel_model.FiveGChannelModel
   hata_coupling_node.HataCouplingNode
   indoor_propagation_coupling_node.IndoorPropagationCouplingNode
   log_distance_coupling_node.LogDistanceCouplingNode
   propagation_loss_coupling_node.PropagationLossCouplingNode
   walfisch_coupling_node.WalfischCouplingNode
   two_ray_path_loss_coupling_node.TwoRayPathLossCouplingNode
   coupling_link_node.CouplingLinkNode
   solution_coupling_node.SolutionCouplingNode
   solutions_node.SolutionsNode


Components
~~~~~~~~~~
Components form the RF signal chain in an EMIT schematic. Although they are stored
internally under an RF System Group node, that node is hidden from users.
Components appear at the top level of the ``EmitSchematic`` and are created
through its ``create_component`` method.

Most components are leaf nodes, but two can have children:

* ``Multiplexer`` has 2 or more ``MultiplexerBand`` children
  (``num_ports - 1``).
* ``RadioNode`` contains a rich subtree:

  - Exactly one ``SamplingNode``.
  - Zero or more ``Band`` nodes (directly or inside ``BandFolder`` nodes).
  - Each ``Band`` has exactly one ``TxSpectralProfNode`` and one
    ``RxSusceptibilityProfNode``, plus optional measurement nodes.
  - ``TxSpectralProfNode`` may have up to one each of ``TxSpurNode``,
    ``TxNbEmissionNode``, ``TxBbEmissionNode``, and ``TxHarmonicNode``.
  - ``RxSusceptibilityProfNode`` may have up to one each of
    ``RxMixerProductNode``, ``RxSaturationNode``, ``RxSelectivityNode``,
    and ``RxSpurNode``.

They are accessible through:

.. currentmodule:: ansys.aedt.core.emit_core.nodes.generated

.. autosummary::
   :toctree: _autosummary
   :nosignatures:

   amplifier.Amplifier
   cable.Cable
   circulator.Circulator
   filter.Filter
   isolator.Isolator
   multiplexer.Multiplexer
   multiplexer_band.MultiplexerBand
   power_divider.PowerDivider
   radio_node.RadioNode
   terminator.Terminator
   tr_switch.TR_Switch
   band.Band
   band_folder.BandFolder
   waveform.Waveform
   sampling_node.SamplingNode
   tx_spectral_prof_node.TxSpectralProfNode
   tx_spectral_prof_emitter_node.TxSpectralProfEmitterNode
   tx_spur_node.TxSpurNode
   tx_nb_emission_node.TxNbEmissionNode
   tx_bb_emission_node.TxBbEmissionNode
   tx_harmonic_node.TxHarmonicNode
   rx_susceptibility_prof_node.RxSusceptibilityProfNode
   rx_mixer_product_node.RxMixerProductNode
   rx_saturation_node.RxSaturationNode
   rx_selectivity_node.RxSelectivityNode
   rx_spur_node.RxSpurNode
   tx_meas_node.TxMeasNode
   rx_meas_node.RxMeasNode


Results and analysis
~~~~~~~~~~~~~~~~~~~~
After building the schematic and coupling definitions, results are obtained by
analyzing a ``Revision``. The results module provides classes for querying
interference metrics, interaction details, and result plots.

They are accessible through:

.. currentmodule:: ansys.aedt.core.emit_core.results

.. autosummary::
   :toctree: _autosummary
   :nosignatures:

   revision.Revision
   interaction.Interaction
   interaction_domain.InteractionDomain

.. currentmodule:: ansys.aedt.core.emit_core.nodes.generated

.. autosummary::
   :toctree: _autosummary
   :nosignatures:

   result_plot_node.ResultPlotNode
   emi_plot_marker_node.EmiPlotMarkerNode


Schematic
~~~~~~~~~
The ``EmitSchematic`` class provides methods for creating and connecting RF
components in the EMIT design.

.. currentmodule:: ansys.aedt.core.emit_core

.. autosummary::
   :toctree: _autosummary
   :nosignatures:

   emit_schematic.EmitSchematic


Base node
~~~~~~~~~
All generated node classes inherit from ``EmitNode``, which provides common
tree-navigation methods (``parent``, ``children``), property access, and
serialization utilities.

.. currentmodule:: ansys.aedt.core.emit_core.nodes

.. autosummary::
   :toctree: _autosummary
   :nosignatures:

   emit_node.EmitNode


``EMIT Design`` example:

.. code:: python

    from ansys.aedt.core import Emit

    app = Emit()

    # Create an emitter (radio + antenna pair)
    emitter, antenna = app.schematic.create_radio_antenna("Bluetooth")

    # Access the radio and add a band
    radio = emitter.get_radio()
    band = radio.add_band()

    # Add an amplifier to the signal chain
    amp = app.schematic.create_component("Amplifier")
    amp.gain = 30.0

    # Analyze and inspect results
    rev = app.results.analyze()
    scene = rev.get_scene_node()
    couplings = rev.get_coupling_data_node()
