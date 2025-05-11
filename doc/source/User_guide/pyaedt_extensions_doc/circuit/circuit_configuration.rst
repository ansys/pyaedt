Circuit Configuration
====================

------------
Introduction
------------

This extension allows to easily:

- Apply simulation configuration to a Circuit design.
- Export simulation configuration as a text file from Circuit, containing all the information in the form of a dictionairy.

The simulation configuration file is a text file in json or toml format. It contains information like component definitions, connections and ports, and more. This configuration file can be used to fully automate the creation of
a circuit design, or to easily make changes on the assembly or any other properties withouth the risk of an error in your design, for example short circuit is a common struggle when manually manipulating the design.

.. image:: ../../../_static/extensions/version_manager.png
  :width: 800
  :alt: Circuit Configuration

----------
Features
----------

- Show Python virtual environment path
- Show Python version
- Show the current PyAEDT and PyEDB versions
- Show the latest PyAEDT and PyEDB release available on PyPI
- Update PyAEDT and PyEDB to the latest version on PyPI
- Install PyAEDT and PyEDB with a branch available on Github
    - By default the main development branch is used
    - Other existing branch names can be provided
- Update PyAEDT and PyEDB from wheelhouse
  - Check compatibility
- Reset and update PyAEDT buttons in AEDT
