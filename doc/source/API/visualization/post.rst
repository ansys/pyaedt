AEDT post-processing
====================

AEDT has some powerful post-processing tools. PyAEDT has classes for manipulating any of these tools.

There are different classes to support all AEDT post-processing solutions. With the following three classes, you can
acces the main AEDT post-processing capabilities:

* ``PostProcessor3D``. Class used by all 3D applications, HFSS, HFSS 3D Layout, Maxwell 3D and 2D, Q3D,
2D Extractor and Mechanical AEDT.
* ``PostProcessorIcepak``. Class used by Icepak, it expands ``PostProcessor3D`` class with additional features.
* ``PostProcessorCircuit``. Schematic post-processing tools, used by Circuit and Twin Builder.

.. note::
   Some functionalities are available only when AEDT is running
   in graphical mode.

.. currentmodule:: ansys.aedt.core.visualization.post.post_common_3d

.. autosummary::
   :toctree: _autosummary
   :nosignatures:

   PostProcessor3D

.. currentmodule:: ansys.aedt.core.visualization.post.post_icepak

.. autosummary::
   :toctree: _autosummary
   :nosignatures:

   PostProcessorIcepak

.. currentmodule:: ansys.aedt.core.visualization.post.post_circuit

.. autosummary::
   :toctree: _autosummary
   :nosignatures:

   PostProcessorCircuit

.. code:: python

    from ansys.aedt.core import Hfss
    app = Hfss(specified_version="2023.1",
                 non_graphical=False, new_desktop_session=True,
                 close_on_exit=True, student_version=False)

    # This call returns the PostProcessor class
    post = app.post

    # This call returns a FieldPlot object
    plotf = post.create_fieldplot_volume(objects, quantity_name, setup_name, intrinsics)

    # This call returns a SolutionData object
    my_data = post.get_solution_data(expressions=trace_names)

    # This call returns a new standard report object and creates one or multiple reports from it.
    standard_report = post.reports_by_category.standard("db(S(1,1))")
    report_standard.create()
    sols = report_standard.get_solution_data()
    ...

User can get the names of the default reports using the following class

.. currentmodule:: ansys.aedt.core.visualization.post.common

.. autosummary::
   :toctree: _autosummary
   :nosignatures:

   Reports

If you need to get the data of any report, you can use this class:

.. currentmodule:: ansys.aedt.core.visualization.post.solution_data

.. autosummary::
   :toctree: _autosummary
   :nosignatures:

   SolutionData
