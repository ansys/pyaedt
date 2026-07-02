Command line extension launch
=============================
Every extension can also launch the extension user interface from the terminal:

.. code::

   SET PYAEDT_DESKTOP_PORT=50051
   SET PYAEDT_DESKTOP_VERSION=2025.2
   python.exe path/to/pyaedt/extensions/project/import_nastran.py

The available arguments are: ``file_path``, ``planar``, ``lightweight``, and ``decimate``.
You can obtain these arguments from the help with this command:

.. code::

   python.exe path/to/pyaedt/extensions/project/import_nastran.py --help

This code shows how to pass the input file as an argument, which doesn't launch the user interface:

.. code::

   export PYAEDT_DESKTOP_PORT=50051
   export PYAEDT_DESKTOP_VERSION=2025.2
   python.exe path/to/pyaedt/extensions/project/import_nastran.py --file_path="my_file.stl"

Finally, this code shows how you can run the extension directly from a Python script:

.. code:: python

    import ansys.aedt.core
    import os
    from ansys.aedt.core.extensions.project.import_nastran import main

    file_path = "my_file.stl"
    hfss = ansys.aedt.core.Hfss()
    # Specify the AEDT session to connect
    os.environ["PYAEDT_DESKTOP_PORT"] = str(hfss.desktop_class.port)
    os.environ["PYAEDT_DESKTOP_VERSION"] = hfss.desktop_class.aedt_version_id
    # Launch extension
    main(
        {
            "file_path": file_path,
            "lightweight": True,
            "decimate": 0.0,
            "planar": True,
            "is_test": False,
        }
    )

