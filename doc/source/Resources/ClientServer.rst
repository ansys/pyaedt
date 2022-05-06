Client/Server
-------------

You can launh PyAEDT on a remote machine if these conditions are met:

#. PyAEDT is installed on client and server machines. (There is no need to have AEDT
   installed on the the client machine.)
#. The same Python version is used on the client and server. (CPython 3.6+ or
   IronPython is embedded in the AEDT installation.)

Windows Server
~~~~~~~~~~~~~~

Here is an usage example for a Windows server:

.. code:: python

    # Launch the latest installed version of AEDT in graphical mode.

    from pyaedt.common_rpc import launch_server
    launch_server()



Linux and Windows Clients
~~~~~~~~~~~~~~~~~~~~~~~~~

Here is an usage example for the client side:

.. code:: python

    # Launch the latest installed version of AEDT in graphical mode.

    from pyaedt.common_rpc import client
    my_client = client("full_name_of_server", port=18000)
    circuit = my_client.root.circuit(specified_version="2022.1", non_graphical=True)
    ...
    # code like locally
    ...


Linux Server
~~~~~~~~~~~~

To bypass current IronPython limits, you can launch PyAEDT on a Linux machine:

#. Using ``pip``, install PyAEDT 0.4.23 or later on a Linux machine.
#. Launch CPython and run PyAEDT on the same machine.

   .. code:: python

      # Launch the latest installed version of PyAEDT in non-graphical mode.

      from pyaedt.common_rpc import launch_ironpython_server
      client = launch_ironpython_server(ansysem_path="/path/to/ansys/executable/folder", non_graphical=True, port=18000)
      hfss = client.root.hfss()
      # put your code here

#. Launch CPython Server on a machine and connect to the server from anaother machinee.

   .. code:: python

      # Launch the latest installed version of PyAEDT in non-graphical mode.

      from pyaedt.common_rpc import launch_ironpython_server
      launch_ironpython_server(ansysem_path="/path/to/ansys/executable/folder",
                               launch_client=False,
                               non_graphical=True,
                               port=18000)
      # connect to the port 18000 from the client machine

#. If the method returns a list or dictionary, use this method to work around an
   issue with CPython handling:

   .. code:: python

      box1 = hfss.modeler.create_box([0,0,0],[1,1,1])
      # convert_remote_object method convert remote ironpython list to local cpython.
      faces = client.convert_remote_object(box1.faces)



.. image:: ./IronPython2Cpython.png
  :width: 800
  :alt: Electronics Desktop Launched