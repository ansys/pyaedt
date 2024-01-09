Choke file
==========

The choke configuration file allows to synthesize a choke from a JSON file.

This file can be created using the following command:

.. code:: python

    from pyaedt import Hfss

    hfss = Hfss()
    choke_file1 =  "choke_example.json"
    choke = hfss.modeler.create_choke(choke_file1)
    hfss.release_desktop()

The main file skeleton is shown below.

:download:`Choke example <../../Resources/choke_example.json>`