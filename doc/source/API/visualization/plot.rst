Graphics operations
===================

You can use PyAEDT for postprocessing of AEDT results to display graphics object and plot data.


.. note::
   Some capabilities of the ``plot`` module require Python 3 and
   installations of the `numpy <https://numpy.org/doc/stable/>`_,
   `matplotlib <https://matplotlib.org/>`_, and `pyvista <https://docs.pyvista.org/>`_
   packages.

There have three main categories:

* **3D Plot**
* **Post-processing**
* **PDF**


3D Plot
~~~~~~~

HERE PYVISTA INFO

.. currentmodule:: ansys.aedt.core.visualization.plot.pyvista

.. autosummary::
   :toctree: _autosummary
   :nosignatures:

   ModelPlotter
   FieldClass
   ObjClass


2D Plot
~~~~~~~

HERE MATPLOTLIB INFO


.. currentmodule:: ansys.aedt.core.visualization.plot.matplotlib

.. autosummary::
   :toctree: _autosummary
   :nosignatures:

   plot_polar_chart
   plot_3d_chart
   plot_2d_chart
   plot_contour
   is_notebook
   update_plot_settings


PDF
~~~

.. currentmodule:: ansys.aedt.core.visualization.plot.pdf

.. autosummary::
   :toctree: _autosummary
   :nosignatures:

   AnsysReport