Command Line Extension Launch
=============================
Every extension can also launch the extension user interface from the terminal:

.. code::

   SET PYAEDT_SCRIPT_PORT=50051
   SET PYAEDT_SCRIPT_VERSION=2024.1
   python.exe path/to/pyaedt/workflows/project/import_nastran.py

The available arguments are: ``file_path``, ``planar``, ``lightweight``, and ``decimate``.
You can obtain these arguments from the help with this command:

.. code::

   python.exe path/to/pyaedt/workflows/project/import_nastran.py --help

This code shows how to pass the input file as an argument, which doesn't launch the user interface:

.. code::

   export PYAEDT_SCRIPT_PORT=50051
   export PYAEDT_SCRIPT_VERSION=2024.1
   python.exe path/to/pyaedt/workflows/project/import_nastran.py --file_path="my_file.stl"

Finally, this code shows how you can run the extension directly from a Python script:

.. code:: python

    import pyaedt
    import os
    from pyaedt.workflows.project.import_nastran import main
    file_path = "my_file.stl"
    hfss = pyaedt.Hfss()
    # Specify the AEDT session to connect
    os.environ["PYAEDT_SCRIPT_PORT"] = str(hfss.desktop_class.port)
    os.environ["PYAEDT_SCRIPT_VERSION"] = hfss.desktop_class.aedt_version_id
    # Launch extension
    main({"file_path": file_path, "lightweight": True, "decimate": 0.0, "planar": True, "is_test": False})

