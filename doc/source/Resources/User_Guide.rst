User Guide
----------

PyAEDT works both inside AEDT and as a standalone application.
It automatically detects whether it is running in an IronPython or CPython
environment and initializes AEDT accordingly. PyAEDT also provides
advanced error management.

AEDT can be started from Python in the non-graphical mode using AEDT.

.. code:: python

    Launch AEDT 2021 R1 in Non-Graphical mode

    from pyaedt import Desktop, Circuit
    with Desktop(specified_version="2021.1", non_graphical=True, new_desktop_session=True, close_on_exit=True,
                 student_version=False):
        circuit = Circuit()
        ...
        # Any error here will be caught by Desktop.
        ...

    # Desktop is automatically closed here.


The previous command launches AEDT and initializes a new Circuit design.

.. image:: ./aedt_first_page.png
  :width: 800
  :alt: Electronics Desktop Launched


The same result can be obtained with the following code:

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


Variable Manager allows user to create advanced equations and manage them through PyAEDT.

The Variable value can be set or get using application setter and getter but user can access
more comprehensive set of functions by accessing directly the variable_manager object.

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
         box = hfss.modeler.primitives.create_box([0, 0, 0], [10, "dim", 10],
                                                  "mybox", "aluminum")
         print(box.faces)
         box.material_name = "copper"
         box.color = "Red"



.. image:: ./aedt_box.png
  :width: 800
  :alt: Modeler Object

Once an object is created or is present in the design (from a loaded project), user can
simply get the related object using getters. Getter works either with object id or object name.
Object returned has all features even if it has not been created in PyAEDT.
Next example shows how easily user can go deeper into edges and vertices of faces or 3d objects.

.. code:: python


     box = hfss.modeler.primitives["mybox2"]
     for face in box.faces:
        print(face.center)
        for edge in face:
            print(edge.midpoint)
            for vertice in edge.vertices:
                print(edge.position)
     for vertice in box.vertices:
        print(edge.position)


All objects allow to execute any modeler operations like union or subtraction.


.. code:: python


     box = hfss.modeler.primitives["mybox2"]
     cyl = hfss.modeler.primitives["mycyl"]
     box.unit(cyl)


.. image:: ./objects_operations.gif
  :width: 800
  :alt: Object Modeler Operations


Mesh
~~~~
Mesh operations are very important in Engineering Simulation. PyAEDT is able to read all mesh
operations already present in a design, edit them and create new ones.
All mesh operations are listed into mesh object.

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
Setup, Optimetrics and Sweeps are the last operations before running analysis.
PyAEDT is able to read all setups, sweeps and optimetrics already present in a design,
edit them and create new ones.
All setup operations are listed into setups list.

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
Optimetrics allows user to setup parametric analysis, sensitivity analysis, optimization and DOE.
PyAEDT is able to read all optimetrics setup already present in a design and create new ones.

.. code:: python


    from pyaedt import Maxwell3d
    m3d = Maxwell3d()
    m3d.opti_parametric.add_parametric_setup("Rload", "LIN 0.1 1 0.1")


.. image:: ./Optimetrics_Parametric.png
  :width: 800
  :alt: Optimetrics Creation




Client/Server
~~~~~~~~~~~~~

Pyaedt can also be launched on a remote machine. To do that, the following conditions are needed:

1. Pyaedt has to be installed on Client and Server machines
2. No need to have AEDT installed on client machine
3. Same Python version has to be used on client and server (CPython 3.6+ or IronPython embedded in AEDT Installation)

Here one example of usage on Windows Server or Linux Server (IronPython):

.. code:: python

    # Launch the latest installed version of AEDT in graphical mode.

    from pyaedt.common_rpc import launch_server
    # ansysem_path and non_graphical are needed only for Linux Ironpython Server
    launch_server(ansysem_path="/path/to/ansys/executable/folder", non_graphical=True)

On Client Side:

.. code:: python

    # Launch the latest installed version of AEDT in graphical mode.

    from pyaedt.common_rpc import client
    my_client = client("full_name_of_server")
    circuit = my_client.root.circuit(specified_version="2021.2", non_graphical=True)
    ...
    # code like locally
    ...


Here one example of usage on Linux Server (CPython):

.. code:: python

    # Launch the latest installed version of AEDT in graphical mode.

    from pyaedt.common_rpc import launch_server
    launch_server()

On Client Side:

.. code:: python

    # Launch the latest installed version of AEDT in graphical mode.

    from pyaedt.common_rpc import client
    my_client = client("full_name_of_server")
    example_script = ["from pyaedt import Circuit", "circuit="Circuit()", "circuit.save_project(\"project_name\")"]
    ansysem = "/path/to/AnsysEMxxx/Linux64"
    my_client.root.run_script(example_script, ansysem_path=ansysem)
    my_client.root.run_script(example_script, aedt_version="2021.2") #if ANSYSEM_ROOTxxx env variable is present


As an alternative, the user can upload the script to run to the server and run it.

.. code:: python

    # Launch the latest installed version of AEDT in graphical mode.

    from pyaedt.common_rpc import client, upload
    my_client = client("full_name_of_server")
    local_script ="path/to/my/local/pyaedt/script.py"
    remote_script ="path/to/my/remote/pyaedt/script.py"
    upload(local_script, remote_script, "servername")
    ansysem = "/path/to/AnsysEMxxx/Linux64"
    my_client.root.run_script(remote_script, ansysem_path=ansysem)