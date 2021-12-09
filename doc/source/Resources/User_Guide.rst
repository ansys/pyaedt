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
