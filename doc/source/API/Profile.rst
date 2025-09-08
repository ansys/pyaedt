Profile
=======

Why profiles matter
-------------------

Running a simulation in AEDT produces a **solver profile**: a detailed log
containing time spent, memory used, mesh/adaptation passes, and frequencies or
transient steps solved.

These profiles are extremely useful because they allow you to:

* **Measure performance** — How long did the solve take? How much memory was used?
* **Identify bottlenecks** — Which step (meshing, adaptive passes, sweeps) consumed the most resources?
* **Compare runs** — Are results consistent across variations or after restarts?
* **Automate reporting** — Generate tables and plots directly from profile data.

Without programmatic access, this information remains buried in text logs or GUI panels.
PyAEDT makes it accessible, structured, and easy to analyze in Python.

Capabilities
------------

PyAEDT provides four main levels of interaction with solver profiles:

* **Parsing** — turn raw profile trees into Python objects.
* **Aggregation** — merge interrupted runs or multiple groups into one coherent profile.
* **Reporting** — generate tabular or graphical summaries of solver metrics.
* **Introspection** — drill down into adaptive passes, frequency sweeps, and transient steps.

Simulation profile
~~~~~~~~~~~~~~~~~~

Central class that encapsulates all profile data from a single simulation run.

- Tracks product name, version, status.
- Contains adaptive passes, frequency sweeps, transient steps, and validation.
- Provides methods to compute total CPU time, real time, and peak memory.

.. currentmodule:: ansys.aedt.core.generic.profiles

.. autosummary::
   :toctree: _autosummary
   :nosignatures:

   SimulationProfile

.. code:: python

    from ansys.aedt.core import Hfss
    profiles = Profiles(raw_profile_dict)
    sim = next(iter(profiles.values()))
    print("Product:", sim.product, sim.product_version)
    print("CPU time:", sim.cpu_time())
    print("Real time:", sim.real_time())
    print("Max memory:", sim.max_memory())

