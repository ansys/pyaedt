Explicit cable harness
======================
This section lists the ``cable_harness`` classes for building a fully explicit three-dimensional
model of a routed, twisted, shielded cable bundle in HFSS. The bundle is described by a
configuration file, from which the conductors, insulation, shields, and jacket are created. The
transfer-impedance boundary conditions, the ports, and the differential pairs are then assigned.

This capability is complementary to :doc:`CableModeling`, which drives the native implicit cable
harness modeler of Ansys Electronics Desktop.

.. currentmodule:: ansys.aedt.core.modeler.advanced_cad.cable_harness

.. autosummary::
   :toctree: _autosummary
   :nosignatures:

   bundle.RoutedCableBundle
   bundle.BuildArtifacts
   configuration.CableBundleConfig
   shield_models.ShieldModel
   shield_models.MeasuredShield
   shield_models.build_shield_model

The following example builds a bundle in an open HFSS design:

.. code:: python

    from ansys.aedt.core import Hfss
    from ansys.aedt.core.modeler.advanced_cad.cable_harness import RoutedCableBundle

    hfss = Hfss(solution_type="Terminal")
    bundle = RoutedCableBundle.from_file("cat6a_sstp_awg25.yaml", hfss)
    artifacts = bundle.build()
    bundle.create_setup()
