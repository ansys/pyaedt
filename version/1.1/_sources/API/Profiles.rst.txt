Profiles
========

An interface to simulation profiles.

What is a Profile?
~~~~~~~~~~~~~~~~~~

Each simulation *profile* provides
performance metrics for a simulation, including CPU time, real time (wall time),
and peak memory usage.
The ``ansys.aedt.core.modules.profile.Profiles`` class is derived
from :py:class:``collections.abc.Mapping``.
Information for each profile corresponds to a simulation setup and the
parametric variation.

The items in the ``Profiles`` class are instances of the
:class:``ansys.aedt.core.modules.profile.SimulationProfile`` class.

.. currentmodule:: ansys.aedt.core.modules.profile

.. autosummary::
   :toctree: _autosummary
   :nosignatures:

   SimulationProfile

A ``Profiles`` instance can be retrieved from the solution setup. Each
element in the ``Profiles`` instance provides access to the ``SimulationProfile`` instance
for the variation:

.. code-block:: pycon
    >>> from ansys.aedt.core import Hfss
    >>> hfss = Hfss(project="/path/to/solved/OptimTee.aedtz")
    >>> this_setup = hfss.get_setup("Setup1")
    >>> profiles = this_setup.get_profile()
    >>> for key in profiles.keys():
    ...     print(f"Variation: {key.split('-')[-1]}")
    ...
    Variation:  offset='0in'
    Variation:  offset='0.10000000000000001in'
    Variation:  offset='0.20000000000000001in'
    Variation:  offset='0.29999999999999999in'
    Variation:  offset='0.40000000000000002in'
    Variation:  offset='0.5in'
    Variation:  offset='0.59999999999999998in'
    Variation:  offset='0.69999999999999996in'
    Variation:  offset='0.80000000000000004in'
    Variation:  offset='0.90000000000000002in'
    Variation:  offset='1in'

.. note:: Parameter values that define a "variation" may deviate
          from expectations due
          to floating point representation error.
          The correct variation can be obtained using the
          ``.keys()`` method as shown below.

.. code-block:: pycon
    >>> my_profile = profiles[list(profiles.keys())[3]]
    >>> bool(my_profile.adaptive_pass)  # Auto-adaptive mesh refinement used?
    True
    >>> my_profile.num_adaptive_passes  # How many adaptive passes?
    6
    >>> my_profile.real_time()  # Real time for all adaptive passes?
    datetime.timedelta(seconds=7)
    >>> my_profile.real_time(num_passes=5)  # Real time for 5 adaptive passes.
    datetime.timedelta(3)
    >>> my_profile.has_frequency_sweep
    False

Some ``SimulationProfile`` attributes are instances of the ``ProfileStep`` class. A ``ProfileStep``
instance, in turn, may be comprised of additional steps that can be accessed as
a :py:class:`Pandas.dataframe` instance. The ``SimulationProfile`` class allows you to retrieve
summary data from all
steps with the ``real_time``, ``max_memory`` and ``cpu_time`` attributes.

For example

.. code-block:: pycon
    >>> len(my_profile.adaptive_pass.process_steps)  # Number of adaptive passes
    6
    >>> step_name = my_profile.adaptive_pass.process_steps[2]  # Select the 3rd adaptive pass.
    >>> print(step_name)
    "Adaptive Pass 3"
    >>> adapt_data = my_profile.adaptive_pass.steps[
    ...     step_name
    ... ]  # Retrieve the ProfileStep instance
    >>> adapt_table = adapt_data.table(columns=["real_time", "max_memory"])
    >>> print(adapt_table.to_string(index=False))  # Pandas dataframe
    Step                real_time   max_memory
    Adaptive Refine     00:00:02    73.1 M
    Simulation Setup    00:00:01    206 M
    Matrix Assembly     00:00:02    263 M
    Matrix Solve        00:00:05    870 M
    Field Recovery      00:00:02    271 M
    Data Transfer       00:00:01    252 M

The attribute values of a ``SimulationProfile`` instance
depend on the type of simulation. The ``table()`` method
can be used to retrieve a :class:``pandas.DataFrame`` instance summarizing
all simulation steps.

+-------------------------+------------------+-----------------------------+
| Attribute               | Simulation Type  | Description                 |
+=========================+==================+======+======================+
| ''.adaptive_pass.steps[key_name]'' | HFSS | Solution steps during        |
|                                    |      |  adaptive refinement.        |
+------------------------------------+------+------------------------------+
| ``.frequency_sweeps[sweep_name]``  | HFSS |    Frequency sweep |
+------------------------------------+------+------------------------------+
| ``.transient``                 | Maxwell  |    Transient solution steps. |
+--------------------------------+----------+------------------------------+

Some methods and attributes in the ``Profiles`` class are:

* ``elapsed_time`` (Measured elapsed time for the entire simulation.)
* ``real_time()`` (Sum of real time for all process steps.)
* ``max_memory()`` (Peak memory over all processes.)
* ``num_cores`` (Number of compute cores.)
* ``product`` (Which solver was used to generate the profile.)
* ``num_adaptive_passes`` (Number of adaptive passes - only if adaptive refinement is used)
* ``has_frequency_sweep`` (``True`` if a frequency sweep was run.)
* ``is_transient`` (``True`` if the profile is for a transient solution.)
* ``os`` (Operating system)

Main profile classes
~~~~~~~~~~~~~~~~~~~~

The following classes cover simulation-level data, steps, and sweeps.

.. currentmodule:: ansys.aedt.core.modules.profile

.. autosummary::
   :toctree: _autosummary
   :nosignatures:

   Profiles
   SimulationProfile
   ProfileStep
   ProfileStepSummary
   TransientProfile
   FrequencySweepProfile
   AdaptivePass
   MemoryGB

Utilities
~~~~~~~~~

Helper functions for parsing and presentation.

.. currentmodule:: ansys.aedt.core.modules.profile

.. autosummary::
   :toctree: _autosummary
   :nosignatures:

   string_to_time
   format_timedelta
   step_name_map
   merge_dict
   get_mesh_process_name