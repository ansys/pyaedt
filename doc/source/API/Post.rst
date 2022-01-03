Postprocessing
==============
This section lists modules for creating and editing
plots in the AEDT.
They are accessible through the ``post`` property:

.. code:: python

    from pyaedt import Hfss
    app = Hfss(specified_version="2021.1",
                 non_graphical=False, new_desktop_session=True,
                 close_on_exit=True, student_version=False)

    # this call return the PostProcessor Class
    post = app.post

    # this call return a FieldPlot Object
    plotf = post.create_fieldplot_volume(object_list, quantityname, setup_name, intrinsic_dict)

    # this call return a SolutionData Object
    my_data = post.get_report_data(expression=trace_names)
    ...

.. note::
   The `AdvancedPostProcessing` module requires Python 3 and
   requires `NumPy <https://numpy.org/doc/stable/>`_, `Matplotlib <https://matplotlib.org/>`_, and `PyVista <https://docs.pyvista.org/>`_.

.. note::
   Some functionalities are available only when AEDT is running 
   in graphical mode.


.. currentmodule:: pyaedt.modules

.. autosummary::
   :toctree: _autosummary
   :nosignatures:

   AdvancedPostProcessing.PostProcessor
   PostProcessor.SolutionData
   PostProcessor.FieldPlot
