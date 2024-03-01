Choke file
==========

The choke configuration file allows you to synthesize a choke from a JSON file.

This code creates the choke geometry:

.. code:: python

    from pyaedt import Hfss

    hfss = Hfss()
    choke_file1 =  "choke_example.json"
    choke = hfss.modeler.create_choke(choke_file1)
    hfss.release_desktop()

File structure example:

:download:`Choke example <../../Resources/choke_example.json>`

For a practical demonstration, see the
`Choke example <https://aedt.docs.pyansys.com/version/stable/examples/02-HFSS/HFSS_Choke.html#sphx-glr-examples-02-hfss-hfss-choke-py>`_.
