Configure layout
================

------------
Introduction
------------

This extension provides the capability of

- Apply simulation configuration to HFSS 3D Layout design.
- Export simulation configuration as text files from activated HFSS 3D Layout design.

The simulation configuration file is a text file in json or toml format. It contains information like layer stackup,
materials, components, HFSS/SIwave setups, etc. This configure file can be used to set up PCB for DCIR, signal
integrity as well as power integrity analysis.

.. image:: ../../../_static/extensions/configure_edb_way_of_work.png
  :width: 800
  :alt: Principle of working of Layout UI

--------------------------------------------------------------------------
A brief description of which options are defined in the configuration file
--------------------------------------------------------------------------


.. image:: ../../../_static/extensions/edb_config_setup.png
  :width: 800
  :alt: Setup defined by a configuration file

As depicted above, these options are importing a stackup, defining components and solderballs / bumps on them,
doing a cutout (much faster and easier than the UI one),
creating coaxial ports with an appropriate PEC backing, as well as, automatically creating distributed circuit ports (or current / voltage sources) on a component,
with the negative terminal of each being its nearest pin of the reference net. Moreover, a variety of simulation setups are supported, namely HFSS, SIwave SYZ, SIwave DC,
as well as, mesh operations that is length based. Last but not least, exporting a configuration file from the active design is also supported, hence the user can get the
configuration setup and re-use it with or without modifications as many times as possible.

The value of this format and toolkit, lies in the fact that it is totally reusable, it is really user-friendly, even with users that are not familiar with scripting.
It supports most of the options that the UI also supports (not only the ones explained above, but many additional), and it has the advantage of obtaining the initial
configuration file from the design, by using its export property.

----------
How to use
----------

.. image:: ../../../_static/extensions/configure_layout_ui.png
  :width: 800
  :alt: Configure Layout UI

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Apply configuration to project
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

1, Activate ``Load`` tab in GUI.

2, Click ``Generate Template`` and choose a directory to save the templates. A toml and a json files are exported.

3, Modify the template files for your application.

4, Click ``Load Configuration`` and browse to the toml file.

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Export configuration files from the active design
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

1, Activate ``Export`` tab in GUI.

2, Click ``Export`` and choose a directory to save the configuration files.

~~~~~~~~~
Resources
~~~~~~~~~

1, EDB Configuration `User Guide`_ for details

.. _User Guide: https://examples.aedt.docs.pyansys.com/version/dev/examples/00_edb/use_configuration/index.html

2, `Webinar Automating Signal and Power Integrity workflow with PyAEDT`_

.. _Webinar Automating Signal and Power Integrity workflow with PyAEDT: https://www.ansys.com/webinars/automating-signal-power-integrity-workflow-pyaedt?campaignID=7013g000000Y8uOAAS&utm_campaign=product&utm_content=digital_electronics_oktopost-Ansys+Electronics_oktopost-%25campaign_n&utm_medium=social-organic&utm_source=LinkedIn