Graphics operations
===================

PyAEDT enables powerful post-processing of AEDT results,
allowing you to visualize graphics objects and plot data with ease.


.. note::
   Some capabilities of the ``plot`` module require Python 3 and
   installations of the `numpy <https://numpy.org/doc/stable/>`_,
   `matplotlib <https://matplotlib.org/>`_, and `pyvista <https://docs.pyvista.org/>`_
   packages.

There have three main categories:

* **Three-dimensional visualization**
* **Graph visualization**
* **PDF**


Three-dimensional visualization
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

HERE PYVISTA INFO

.. currentmodule:: ansys.aedt.core.visualization.plot.pyvista

.. autosummary::
   :toctree: _autosummary
   :nosignatures:

   ModelPlotter
   FieldClass
   ObjClass


Graph visualization
~~~~~~~~~~~~~~~~~~~

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