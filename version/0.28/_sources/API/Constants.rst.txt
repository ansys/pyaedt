Constants
==========
This section lists constants that are commonly used in PyAEDT.


Example of constants usage:

.. code:: python

    from ansys.aedt.core import constants

    ipk = Icepak()
    # Use of Axis constant
    cylinder = ipk.modeler.create_cylinder(constants.Axis.X, [0, 0, 0], 10, 3)
    # Use of PLANE Constant
    ipk.modeler.split(cylinder, constants.Plane.YZ, sides="Both")
    ...
    ipk.release_desktop()


.. automodule:: ansys.aedt.core.generic.constants
   :members:
