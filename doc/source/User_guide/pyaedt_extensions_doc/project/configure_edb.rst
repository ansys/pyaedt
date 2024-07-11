Configure layout EDB
====================

Single configuration file to set up layout for any kind of PCB & package analysis.


The following image shows the extension user interface:

.. image:: ../../../_static/extensions/configure_edb.png
  :width: 800
  :alt: Configure Layout UI


The available arguments are: ``aedb_path``, ``configuration_path``.
User can pass as an argument a configuration file (a json formatted file or a toml file), or a folder containing more
than N configuration files. In such case the script creates N new aedb projects, each one with corresponding
setting file applied.


.. image:: ../../../_static/extensions/configure_edb_way_of_work.png
  :width: 800
  :alt: Principle of working of Layout UI


A brief description of which options are defined in the configuration file:

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
