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

For a practical demonstration, refer to the provided example in the following link:
`Choke example <https://aedt.docs.pyansys.com/version/stable/examples/02-HFSS/HFSS_Choke.html#sphx-glr-examples-02-hfss-hfss-choke-py>`_
