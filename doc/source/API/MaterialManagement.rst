Material and Stackup
====================
This section lists material and stackup modules.
Those classes cannot be used directly and can be accessed through Application.
Example:


.. currentmodule:: pyaedt.modules

.. autosummary::
   :toctree: _autosummary
   :nosignatures:

   MaterialLib.Materials
   Material.MatProperties
   Material.SurfMatProperties
   Material.MatProperty
   Material.Material
   Material.SurfaceMaterial
   LayerStackup.Layers
   LayerStackup.Layer

.. code:: python

    from pyaedt import Hfss
    app = Hfss(specified_version="2022.1",
                 non_graphical=False, new_desktop_session=True,
                 close_on_exit=True, student_version=False)

    # this call return the Materials Class
    my_materials = app.materials
    # this call return the Material Class
    copper = my_materials["copper"]
    # this property is from MatProperty Class
    copper.conductivity
    ...