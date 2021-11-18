Constants
==========
This section lists all the useful constants used in pyaedt.


Example of constants usage:

.. code:: python

    from pyaedt import constants
    ipk = Icepak()
    # Use of AXIS Constant
    cyl = ipk.modeler.primitives.create_cylinder(constants.AXIS.X, [0,0,0],10,3)
    # Use of PLANE Constant
    ipk.modeler.split(cyl, constants.PLANE.YZ, sides="Both")
    ...
    ipk.release_desktop()


.. automodule:: pyaedt.generic.constants
   :members:
