Configure Layout Edb
====================

Single configuration file to set up layout for any kind of PCB & package analysis.


The following image shows the extension user interface:

.. image:: ../../../_static/extensions/configure_edb.png
  :width: 800
  :alt: Configure Layout UI


User can pass as an argument a configuration file (a json formatted file or a toml file) or a folder containing more
than N configuration files. In such case the script will create N new aedb project, each one with corresponding
settings applied.


.. image:: ../../../_static/extensions/configure_edb_way_of_work.png
  :width: 800
  :alt: Principle of working of Layout UI



The available arguments are: ``aedb_path``, ``configuration_path``.
You can also launch the extension user interface from the terminal an example can be found here.

.. toctree::
   :maxdepth: 2

   ../commandline