Icepak templates and arguments
===============================

This section lists all setup templates with their default values and keys available in Icepak.
Note that Icepak parameters contain spaces. To use them as arguments of the ``"create_setup"`` method, these
same parameters have to be used without spaces.
You can edit a setup after it is created. Here is an example:

.. code:: python

    from pyaedt import Icepak

    app = Icepak()
    # Any property of this setup can be found on this page.
    setup = app.create_setup(MaxIterations=5)

Available turbulent models are: ``"ZeroEquation"``, ``"TwoEquation"``, ``"EnhancedTwoEquation"``, ``"RNG"``, ``"EnhancedRNG"``, ``"RealizableTwoEquation"``, ``"EnhancedRealizableTwoEquation"``, ``"SpalartAllmaras"``, ``"kOmegaSST"``.

.. pprint:: pyaedt.modules.SetupTemplates.TransientFlowOnly
.. pprint:: pyaedt.modules.SetupTemplates.TransientTemperatureOnly
.. pprint:: pyaedt.modules.SetupTemplates.TransientTemperatureAndFlow
.. pprint:: pyaedt.modules.SetupTemplates.SteadyFlowOnly
.. pprint:: pyaedt.modules.SetupTemplates.SteadyTemperatureOnly
.. pprint:: pyaedt.modules.SetupTemplates.SteadyTemperatureAndFlow
