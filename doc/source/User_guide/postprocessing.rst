Postprocessing
==============
Postprocessing is essential in simulation. PyAEDT can read all solutions and plot results in AEDT or
outside it using the `pyvista <https://www.pyvista.org/>`_ and `matplotlib <https://matplotlib.org/>`_
packages:

.. code:: python


    from pyaedt import Hfss
    hfss = Hfss()
    hfss.analyze_nominal()
    cutlist = ["Global:XY"]
    setup_name = self.aedtapp.existing_analysis_sweeps[0]
    quantity_name = "ComplexMag_E"
    intrinsic = {"Freq": "5GHz", "Phase": "180deg"}

    # create a field plot
    plot1 = hfss.post.create_fieldplot_cutplane(cutlist, quantity_name, setup_name, intrinsic)

    # create a 3d far field
    new_report = hfss.post.reports_by_category.far_field("db(RealizedGainTotal)", hfss.nominal_adaptive)

    # create a rectangular plot
    report = hfss.post.reports_by_category.modal_solution("dB(S(1,1))")
    report.create()

    solutions = report.get_solution_data()


.. image:: ../Resources/field_plot.png
  :width: 800
  :alt: Post Processing features
