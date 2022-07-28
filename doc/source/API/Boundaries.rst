Boundary objects
================
This section lists classes for creating and editing
boundaries in the 3D tools. These objects are returned by
app methods and can be used to edit or delete a boundary condition.


.. currentmodule:: pyaedt.modules.Boundary

.. autosummary::
   :toctree: _autosummary
   :nosignatures:

   NativeComponentObject
   BoundaryObject
   FarFieldSetup
   Matrix

Example without ``Native Component Object``:

.. code:: python

    from pyaedt import Icepak
    ipk = Icepak()
    component_name = "RadioBoard1"
    native_comp = self.aedtapp.create_ipk_3dcomponent_pcb(
        component_name, link_data, solution_freq, resolution, custom_x_resolution=400, custom_y_resolution=500
    )
     # native_comp is a NativeComponentObject
    ...
    ipk.release_desktop()

