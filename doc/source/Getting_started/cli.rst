Command line interface
======================

PyAEDT provides a command line interface (CLI) to help you manage AEDT processes and test configurations
from your terminal. The CLI offers simple commands to start, stop, and monitor AEDT sessions without
writing any Python code.

Get started
-----------

To use the CLI, open your terminal and type:

.. code-block:: bash

    pyaedt --help

This displays all available commands and options.


Main Commands
-------------

The PyAEDT CLI provides these main commands:

* ``version`` - Display the installed PyAEDT version
* ``processes`` - List all running AEDT processes
* ``start`` - Start a new AEDT session
* ``stop`` - Stop running AEDT processes
* ``config`` - Manage test configuration settings
* ``doc`` - Quick access to PyAEDT documentation


Display version
~~~~~~~~~~~~~~~

Check which version of PyAEDT you have installed:

.. code-block:: bash

    pyaedt version

This shows the current PyAEDT version number.


List running processes
~~~~~~~~~~~~~~~~~~~~~~

View all AEDT processes currently running on your system:

.. code-block:: bash

    pyaedt processes

This command displays useful information for each process:

* Process ID (PID)
* Process name
* Command line arguments
* Port number (if available)


Start AEDT
~~~~~~~~~~

Launch a new AEDT session directly from the command line:

.. code-block:: bash

    pyaedt start

This starts AEDT with default settings (latest AEDT version released, graphical mode).

You can customize the startup with these options:

**Set AEDT Version**

.. code-block:: bash

    pyaedt start --version 2025.2
    pyaedt start -v 2025.2

**Non-Graphical Mode**

Run AEDT without the user interface (useful for automation):

.. code-block:: bash

    pyaedt start --non-graphical
    pyaedt start -ng

**Specify Port**

Set a specific port for the AEDT connection:

.. code-block:: bash

    pyaedt start --port 50051
    pyaedt start -p 50051

**Student Version**

Start the AEDT Student edition:

.. code-block:: bash

    pyaedt start --student

**Combine Options**

You can use multiple options together:

.. code-block:: bash

    pyaedt start -v 2025.2 -ng -p 50051


Stop AEDT
~~~~~~~~~

Stop running AEDT processes using different methods:

**Stop by Process ID**

.. code-block:: bash

    pyaedt stop --pid 12345

Stop multiple processes:

.. code-block:: bash

    pyaedt stop --pid 12345 --pid 67890

**Stop by Port**

.. code-block:: bash

    pyaedt stop --port 50051

**Stop All AEDT Processes**

.. code-block:: bash

    pyaedt stop --all
    pyaedt stop -a


Test configuration management
------------------------------

The ``config test`` command helps you create and modify the test configuration file
used when running PyAEDT tests. This is useful for developers and contributors.

Launch the interactive configuration tool:

.. code-block:: bash

    pyaedt config test

This starts a guided setup that walks you through all configuration options and saves
the configuration to ``tests/local_config.json``.

To see your configuration without making changes:

.. code-block:: bash

    pyaedt config test --show
    pyaedt config test -s

You can also set individual values directly. For example:

.. code-block:: bash

    pyaedt config test desktop-version 2025.2
    pyaedt config test non-graphical true
    pyaedt config test use-grpc true

For a complete description of all configuration parameters and their usage, see the
:ref:`Local testing parameters <contributing_aedt>` section in the Contributing guide.


Documentation access
--------------------

The ``doc`` command provides quick access to PyAEDT documentation and resources directly
from the command line. This opens the documentation in your default web browser.

**Open Documentation Sections**

Access different parts of the documentation:

.. code-block:: bash

    pyaedt doc home              # Open documentation home page
    pyaedt doc getting-started   # Open getting started guide
    pyaedt doc installation      # Open installation guide
    pyaedt doc user-guide        # Open user guide
    pyaedt doc api               # Open API reference
    pyaedt doc examples          # Open examples gallery

**Access Development Resources**

.. code-block:: bash

    pyaedt doc github            # Open PyAEDT GitHub repository
    pyaedt doc issues            # Open GitHub issues page
    pyaedt doc changelog         # Open latest changelog
    pyaedt doc changelog 0.9.0   # Open specific version changelog

**Search Documentation**

Search the documentation with keywords:

.. code-block:: bash

    pyaedt doc search hfss        # Search for "hfss"
    pyaedt doc search circuit     # Search for "circuit"
    pyaedt doc search aedt mesh   # Search for "aedt mesh"

The search command accepts one or more keywords and opens the documentation search page
with your query.


Practical examples
------------------

Here are some common workflows using the CLI:

**Start AEDT and Check Status**

.. code-block:: bash

    # Start AEDT
    pyaedt start -v 2025.2

    # Check it's running
    pyaedt processes

    # Stop when done
    pyaedt stop --all

**Automation Script**

.. code-block:: bash

    # Start AEDT in non-graphical mode on a specific port
    pyaedt start -ng -p 50051

    # Your automation code runs here
    python my_script.py

    # Clean up
    pyaedt stop --port 50051

**Configure Tests**

.. code-block:: bash

    # Use interactive mode
    pyaedt config test

    # Or set values directly
    pyaedt config test desktop-version 2025.2

**Quick Documentation Access**

.. code-block:: bash

    # Open API reference
    pyaedt doc api

    # Search for specific topics
    pyaedt doc search maxwell 3d

    # Open GitHub repository
    pyaedt doc github

**Emergency Cleanup**

If AEDT processes are stuck:

.. code-block:: bash

    # See what's running
    pyaedt processes

    # Stop everything
    pyaedt stop --all


Troubleshooting
---------------

**Command Not Found**

If ``pyaedt`` command is not recognized, ensure PyAEDT is installed with CLI support:

.. code-block:: bash

    pip install pyaedt[all]

**Cannot Stop Process**

If you get "Access denied" errors:

* You can only stop processes owned by your user
* Some processes may require administrator privileges
* Try closing AEDT normally from the application first

**AEDT Won't Start**

Common issues when starting AEDT:

* Verify AEDT is installed and in your system PATH
* Check the version number is correct (for example, 2025.1, 2025.2)
* Ensure license server is available

**Configuration Not Found**

The test configuration is created in the ``tests`` folder relative to the PyAEDT installation.
If you're not in a development environment, you may need to navigate to the correct directory first.


Get help
--------

For detailed help on any command:

.. code-block:: bash

    pyaedt --help
    pyaedt start --help
    pyaedt stop --help
    pyaedt config test --help
    pyaedt doc --help

For more information, visit the PyAEDT documentation or GitHub repository.
