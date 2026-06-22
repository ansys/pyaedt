Kernel conversion
=================

Conversion of the kernel from ACIS (2022R2 and previous versions),
to Parasolid (2023R1 and following versions) is becoming accessible to the customer,
with the use of a simple script.

This script is compatible with AEDT files, as well as A3DCOMP files (including encrypted 3DComponents).

.. warning::

   This extension requires **AEDT 2022 R2** to be installed on the same machine alongside
   the current AEDT release. AEDT 2022 R2 is launched automatically as a second, non-graphical
   desktop to read project files that still use the legacy ACIS kernel. If this version is not
   found, the extension raises an error listing all currently installed AEDT versions so you
   know exactly what is missing.

   If you need to use a different legacy version as the input kernel (for example because your
   files were created with a specific intermediate release), you can override the default by
   setting the ``PYAEDT_KERNEL_AEDT_VERSION`` environment variable before launching the
   extension:

   .. code-block:: bash

      # Windows - Command Prompt (cmd)
      set PYAEDT_KERNEL_AEDT_VERSION=2022.2

      # Linux
      export PYAEDT_KERNEL_AEDT_VERSION=2022.2

   The value must match one of the version strings returned by the AEDT version discovery (for
   example ``2022.2``, ``2023.1``).

The following image shows the extension user interface:

.. image:: ../../../_static/extensions/kernel_convert_ui.png
  :width: 800
  :alt: Kernel Convert UI

The Browse file or folder input points to a path which is either an A3DCOMP file,
an AEDT file, or a folder containing a variety of files of both types
(this way the user is capable to convert the kernel of a component library with one launch of the script)

.. warning::

   For encrypted 3D components the enable editing should be always on (with the corresponding
   password that is given as an input). When pointing to a library, in order for
   all the 3DComponents to be converted, they must have the same Application and Solution type,
   given as an input in the last two entries of the UI, as well as same password, in order for the
   conversion to be successful for all files.

Last but not least, for every file in the folder, a new file is generated in the path provided, that contains the
design converted to the latest version, and its name indicating the initial file version (for example test_aedt_2025.2)
Furthermore, for every conversion, a CSV file is created, with a name pointing to the converted design name,
containing any violations that occurred during the conversion, and that need **manual** fixing by the user.

The following image show, the initial test_aedt and test_a3dcomp files, the corresponding CSV files and
the generated 2025R1 version (with the Parasolid Kernel) files.

.. image:: ../../../_static/extensions/converted_files.png
  :width: 800
  :alt: Generated Files During Kernel Conversion

You can launch the extension user interface from the terminal, you can find the script in the PyAEDT installation:

.. code::

   python.exe path/to/pyaedt/extensions/common/kernel_converter.py

Finally, this code shows how you can run the extension directly from a Python script:

.. code:: python

    from ansys.aedt.core.extensions.common.kernel_converter import main

    main(
        test_args={
            "password": "my_pwd",
            "application": "HFSS",
            "solution": "Modal",
            "file_path": "C:\my_path\file_containing_projects",
        }
    )
