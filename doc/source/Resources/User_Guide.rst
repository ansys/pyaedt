User Guide
----------

PyAEDT works both inside AEDT and as a standalone application.
It automatically detects whether it is running in an IronPython or CPython
environment and initializes AEDT accordingly. PyAEDT also provides
advanced error management.

You can start AEDT in non-graphical from Python:

.. code:: python

    Launch AEDT 2021 R1 in non-graphical mode

    from pyaedt import Desktop, Circuit
    with Desktop(specified_version="2021.1", non_graphical=True, new_desktop_session=True, close_on_exit=True,
                 student_version=False):
        circuit = Circuit()
        ...
        # Any error here will be caught by Desktop.
        ...

    # Desktop is automatically closed here.


The previous code launches AEDT and initializes a new Circuit design.

.. image:: ./aedt_first_page.png
  :width: 800
  :alt: Electronics Desktop Launched


You can obtain the same result with:

.. code:: python

    # Launch the latest installed version of AEDT in graphical mode.

    from pyaedt import Circuit
    with Circuit(specified_version="2021.1", non_graphical=False) as circuit:
        ...
        # Any error here will be caught by Desktop.
        ...

    # Desktop is automatically released here.


Variables
~~~~~~~~~
PyAEDT provides a simplified interface for getting and setting variables inside a project or a design.
You simply need to initialize a variable as a dictionary key. If you use ``$`` as the prefix 
for the variable name, a project-wide variable is created.

.. code:: python

    from pyaedt import Hfss
    with Hfss as hfss:
         hfss["dim"] = "1mm"   # design variable
         hfss["$dim"] = "1mm"  # project variable


.. image:: ./aedt_variables.png
  :width: 800
  :alt: Variable Management


With Variable Manager, you can create advanced equations and manage them through PyAEDT.

While you can set or get the variable value using the application setter and getter, you can
access the ``variable_manager`` object for a more comprehensive set of functions:

.. code:: python

        >>> hfss["$PrjVar1"] = "2*pi"
        >>> hfss["$PrjVar2"] = "100Hz"
        >>> hfss["$PrjVar3"] = "34 * $PrjVar1/$PrjVar2"
        >>> hfss["$PrjVar3"]
        2.13628300444106
        >>> hfss["$PrjVar3"].value
        2.13628300444106
        hfss.variable_manager["$PrjVar3"].expression
        '34 * $PrjVar1/$PrjVar2'


.. image:: ./variables_advanced.png
  :width: 600
  :alt: Variable Management


Modeler
~~~~~~~
Object-oriented programming is used to create and manage objects in the AEDT 3D and 2D Modelers. 
You can create an object and change properties using getters and setters.

.. code:: python

    Create a box, assign variables, and assign materials.

    from pyaedt.hfss import Hfss
    with Hfss as hfss:
         box = hfss.modeler.create_box([0, 0, 0], [10, "dim", 10],
                                       "mybox", "aluminum")
         print(box.faces)
         box.material_name = "copper"
         box.color = "Red"



.. image:: ./aedt_box.png
  :width: 800
  :alt: Modeler Object

Once an object is created or is present in the design (from a loaded project), you can
simply get the related object using getters. A getter works either with an object ID or
object name. The object returned has all features even if it has not been created in PyAEDT.

This example shows how easily you can go deeper into edges and vertices of faces or 3D objects:

.. code:: python

     box = hfss.modeler["mybox2"]
     for face in box.faces:
        print(face.center)
        for edge in face:
            print(edge.midpoint)
            for vertice in edge.vertices:
                print(edge.position)
     for vertice in box.vertices:
        print(edge.position)


All objects support executing any modeler operation, such as union or subtraction:

.. code:: python


     box = hfss.modeler["mybox2"]
     cyl = hfss.modeler["mycyl"]
     box.unit(cyl)


.. image:: ./objects_operations.gif
  :width: 800
  :alt: Object Modeler Operations


Mesh
~~~~
Mesh operations are very important in engineering simulation. PyAEDT is able to read all mesh
operations already present in a design, edit them, and create new ones. All mesh operations
are listed in the mesh object.

.. code:: python


    from pyaedt import Maxwell3d
    m3d = Maxwell3d()
    all_mesh_ops = m3d.mesh.meshoperations
    my_mesh_op = all_mesh_ops[0]
    # all properties are in props dictionary.
    my_mesh_op.props["my_prop"] = "my_value"
    my_mesh_op.update()


.. image:: ./Mesh_Operations.png
  :width: 800
  :alt: Mesh object List


Setup
~~~~~
Setup, optimetrics, and wweeps are the last operations before running analysis.
PyAEDT is able to read all setups, sweeps, and optimetrics already present in a design,
edit them, and create new ones. All setup operations are listed in the setups list.

.. code:: python


    from pyaedt import Maxwell3d
    m3d = Maxwell3d()
    all_setups = m3d.setups
    my_setup = all_setups[0]
    # all properties are in props dictionary.
    my_setup.props['MaximumPasses'] = 10
    my_setup.update()

    new_setup = m3d.create_setup("New_Setup")



.. image:: ./Setups.png
  :width: 800
  :alt: Setup Editing and Creation


Optimization
~~~~~~~~~~~~
Optimetrics allow you to set up parametric analysis, sensitivity analysis, optimization,
and Design of Experients (DOE). PyAEDT is able to read all optimetrics setups already
present in a design and create new ones.

.. code:: python


    from pyaedt import Maxwell3d
    m3d = Maxwell3d()
    m3d.opti_parametric.add_parametric_setup("Rload", "LIN 0.1 1 0.1")


.. image:: ./Optimetrics_Parametric.png
  :width: 800
  :alt: Optimetrics Creation


Client/Server
~~~~~~~~~~~~~
You can launh PyAEDT on a remote machine if these conditions are met:

#. PyAEDT is installed on client and server machines. (There is no need to have AEDT
   installed on the the client machine.)
#. The same Python version is used on the client and server. (CPython 3.6+ or 
   IronPython is embedded in the AEDT installation.)

Here is an usage example for a Windows server or Linux server (IronPython):

.. code:: python

    # Launch the latest installed version of AEDT in graphical mode.

    from pyaedt.common_rpc import launch_server
    # ansysem_path and non_graphical are needed only for Linux Ironpython Server
    launch_server(ansysem_path="/path/to/ansys/executable/folder", non_graphical=True)

Here is an usage example for the client side:

.. code:: python

    # Launch the latest installed version of AEDT in graphical mode.

    from pyaedt.common_rpc import client
    my_client = client("full_name_of_server")
    circuit = my_client.root.circuit(specified_version="2021.2", non_graphical=True)
    ...
    # code like locally
    ...


Here is a usage example for a Linux server (CPython):

.. code:: python

    # Launch the latest installed version of AEDT in graphical mode.

    from pyaedt.common_rpc import launch_server
    launch_server()

Here is a usage example for the client side:

.. code:: python

    # Launch the latest installed version of AEDT in graphical mode.

    from pyaedt.common_rpc import client
    my_client = client("full_name_of_server")
    example_script = ["from pyaedt import Circuit", "circuit="Circuit()", "circuit.save_project(\"project_name\")"]
    ansysem = "/path/to/AnsysEMxxx/Linux64"
    my_client.root.run_script(example_script, ansysem_path=ansysem)
    my_client.root.run_script(example_script, aedt_version="2021.2") #if ANSYSEM_ROOTxxx env variable is present


As an alternative, you can upload the script to the server and run it from there:

.. code:: python

    # Launch the latest installed version of AEDT in graphical mode.

    from pyaedt.common_rpc import client, upload
    my_client = client("full_name_of_server")
    local_script ="path/to/my/local/pyaedt/script.py"
    remote_script ="path/to/my/remote/pyaedt/script.py"
    upload(local_script, remote_script, "servername")
    ansysem = "/path/to/AnsysEMxxx/Linux64"
    my_client.root.run_script(remote_script, ansysem_path=ansysem)


CPython on Linux with Client-Server
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

To bypass current IronPython limits, you can launch PyAEDT on a Linux machine:

#. Using ``pip``, install PyAEDT 0.4.23 or later on a Linux machine.
#. Launch CPython and run PyAEDT.

   .. code:: python

      # Launch the latest installed version of PyAEDT in non-graphical mode.

      from pyaedt.common_rpc import launch_ironpython_server
      client = launch_ironpython_server(ansysem_path="/path/to/ansys/executable/folder", non_graphical=True, port=18000)
      hfss = client.root.hfss()
      # put your code here

#. If the method returns a list or dictionary, use this method to work around an
   issue with CPython handling:

   .. code:: python

      box1 = hfss.modeler.create_box([0,0,0],[1,1,1])
      # convert_remote_object method convert remote ironpython list to local cpython.
      faces = client.convert_remote_object(box1.faces)


.. image:: ./IronPython2Cpython.png
  :width: 800
  :alt: Electronics Desktop Launched