Constants
==========
This section lists constants that are commonly used in PyAEDT.


Example of constants usage:

.. code:: python

    from pyaedt import constants
    ipk = Icepak()
    # Use of AXIS Constant
    cylinder = ipk.modeler.create_cylinder(constants.AXIS.X, [0,0,0],10,3)
    # Use of PLANE Constant
    ipk.modeler.split(cylinder, constants.PLANE.YZ, sides="Both")
    ...
    ipk.release_desktop()


.. automodule:: pyaedt.generic.constants
   :members:
