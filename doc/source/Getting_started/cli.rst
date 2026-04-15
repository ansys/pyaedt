Command line interface
======================

PyAEDT provides a command line interface (CLI) for starting AEDT sessions, working with open
projects, running scripts, exporting data, and opening documentation directly from a terminal.

Get started
-----------

To see the available commands, run:

.. code-block:: bash

    pyaedt --help

All commands can be run with ``--json`` to output results in JSON format for easy parsing in scripts.

.. code-block:: console

    $ pyaedt --json version
    {"status": "ok", "data": {"version": "1.0.dev0"}}

    $ pyaedt version
    PyAEDT version: 1.0.dev0


Main commands
-------------

The CLI is organized into these top-level commands:

* ``version`` - Display the installed PyAEDT version
* ``aedt-versions`` - List AEDT versions installed on the machine
* ``session`` - Start, list, stop, or attach to AEDT sessions
* ``project`` - List, open, create, save, and close AEDT projects
* ``script`` - Run a Python script inside AEDT
* ``export`` - Export screenshots or design configuration data
* ``panels`` - Install PyAEDT panels into AEDT
* ``doc`` - Open PyAEDT documentation and related resources
* ``test-config`` - Create, inspect, or update ``tests/local_config.json``


Version commands
----------------

Use the ``version`` commands to check the installed PyAEDT version or AEDT versions on the machine.

**PyAEDT version**

.. code-block:: bash

    pyaedt version

**AEDT installed version**

.. code-block:: bash

    pyaedt aedt-versions


Session commands
----------------

Use the ``session`` group to manage running AEDT instances.

**Start a session**

.. code-block:: bash

    pyaedt session start
    pyaedt session start --version 2026.1
    pyaedt session start --non-graphical
    pyaedt session start --port 50051
    pyaedt session start -v 2026.1 -ng --port 50051

By default, ``session start`` uses AEDT ``2026.1`` and port ``50051``.
Use ``--port 0`` to let AEDT choose an available port automatically.

**List running sessions**

.. code-block:: bash

    pyaedt session list

This shows the PID, detected AEDT version, and port for each running session.

**Attach to a running session**

.. code-block:: bash

    pyaedt session attach
    pyaedt session attach --port 50051
    pyaedt session attach --port 50051 --project MyProject --design MyDesign

If ``--port`` is omitted, PyAEDT shows an interactive list of running sessions.
When available, IPython is used for the interactive console.

**Stop sessions**

.. code-block:: bash

    pyaedt session stop --port 50051
    pyaedt session stop --all


Project commands
----------------

Use the ``project`` group to work with projects in an already running AEDT gRPC session.
These commands require ``--port``.

**List open projects and designs**

.. code-block:: bash

    pyaedt project list --port 50051

**Open a project**

.. code-block:: bash

    pyaedt project open my_project.aedt --port 50051

**Create a project**

.. code-block:: bash

    pyaedt project create --port 50051 --project DemoProject

**Create a design in a project**

.. code-block:: bash

    pyaedt project create --port 50051 --project DemoProject --design Filter1 --type Hfss

Supported design types include ``Hfss``, ``Maxwell2d``, ``Maxwell3d``, ``Q3d``, ``Q2d``,
``Icepak``, ``Circuit``, ``TwinBuilder``, ``Mechanical``, ``Emit``, ``Rmxprt``,
``Hfss3dLayout``, and ``MaxwellCircuit``.

**Save the active project**

.. code-block:: bash

    pyaedt project save --port 50051
    pyaedt project save --port 50051 --path saved_copy.aedt

**Close a project**

.. code-block:: bash

    pyaedt project close --port 50051
    pyaedt project close --port 50051 --project DemoProject


Script and export commands
--------------------------

Use ``script`` to execute Python inside AEDT and ``export`` to extract files from the active design.

**Run a script**

.. code-block:: bash

    pyaedt script run my_script.py --port 50051

The script runs with an attached Desktop object available as ``desktop``.

**Export a screenshot**

.. code-block:: bash

    pyaedt export screenshot --port 50051 --path screenshot.jpg
    pyaedt export screenshot --port 50051 --project DemoProject --design Filter1

**Export design configuration**

.. code-block:: bash

    pyaedt export config --port 50051
    pyaedt export config --port 50051 --output config.json
    pyaedt export config --port 50051 --project DemoProject --design Filter1

If ``--output`` is omitted, the exported JSON is printed to the terminal.


Test configuration
------------------

Use ``test-config`` to manage the local test configuration stored in
``tests/local_config.json``.

.. code-block:: bash

    pyaedt test-config
    pyaedt test-config --show

Running ``pyaedt test-config`` starts an interactive configuration flow.


Panels management
-----------------

Use ``panels add`` to install PyAEDT panels into AEDT.

.. code-block:: bash

    pyaedt panels add --personal-lib "C:\\Users\\username\\AppData\\Roaming\\Ansoft\\PersonalLib"
    pyaedt panels add --personal-lib "C:\\Users\\username\\AppData\\Roaming\\Ansoft\\PersonalLib" --reset
    pyaedt panels add --personal-lib "C:\\Users\\username\\AppData\\Roaming\\Ansoft\\PersonalLib" --light

Useful options:

* ``--reset`` - Remove the existing ``Toolkits`` directory before installing
* ``--light`` - Install only the light panel set (PyAEDT Console and Run Script)
* ``--skip-version-manager`` - Skip the Version Manager panel
* ``--skip-extension-manager`` - Skip the Extension Manager panel


Documentation shortcuts
-----------------------

Use the ``doc`` group to open online documentation and project resources:

.. code-block:: bash

    pyaedt doc
    pyaedt doc getting-started
    pyaedt doc installation
    pyaedt doc user-guide
    pyaedt doc api
    pyaedt doc examples
    pyaedt doc github
    pyaedt doc issues
    pyaedt doc changelog
    pyaedt doc changelog 0.22.0
    pyaedt doc search hfss mesh

If no subcommand is provided, ``pyaedt doc`` opens the documentation home page.


Common workflows
----------------

**Start AEDT, inspect projects, and stop it**

.. code-block:: bash

    pyaedt session start --version 2026.1 --port 50051
    pyaedt session list
    pyaedt project list --port 50051
    pyaedt session stop --port 50051

**Run a script against a running session**

.. code-block:: bash

    pyaedt session start --non-graphical --port 50051
    pyaedt script run my_script.py --port 50051
    pyaedt session stop --port 50051

**Export design data**

.. code-block:: bash

    pyaedt export screenshot --port 50051 --project DemoProject --design Filter1
    pyaedt export config --port 50051 --project DemoProject --design Filter1 --output filter1.json


Requirements
------------

If the ``pyaedt`` command is not available, install PyAEDT with CLI dependencies:

.. code-block:: bash

    pip install pyaedt[all]

The interactive attach console uses IPython when it is installed.


Get help
--------

Use ``--help`` on any command group or command to see the available options:

.. code-block:: bash

    pyaedt --help
    pyaedt session --help
    pyaedt project --help
    pyaedt script run --help
    pyaedt export --help
    pyaedt panels add --help
    pyaedt doc --help
    pyaedt test-config --help
