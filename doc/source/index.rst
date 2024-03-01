PyAEDT documentation  |version|
===============================

**Useful links**:
`Installation <https://aedt.docs.pyansys.com/version/stable/Getting_started/Installation.html>`_ |
`Source Repository <https://github.com/ansys/pyaedt>`_ |
`Issues <https://github.com/ansys/pyaedt/issues>`_

PyAEDT is a Python library that interacts directly with the Ansys Electronics Desktop (AEDT) API,
enabling straightforward and efficient automation in your workflow.


.. grid:: 2

    .. grid-item-card:: Getting started :fa:`person-running`
        :link: Getting_started/index
        :link-type: doc

        New to PyAEDT? This section provides the information that you need to get started with PyAEDT.

    .. grid-item-card:: User guide :fa:`book-open-reader`
        :link: User_guide/index
        :link-type: doc

        This section provides in-depth information on PyAEDT key concepts.

.. grid:: 2

    .. grid-item-card::  AEDT API reference :fa:`book-bookmark`
        :link: API/index
        :link-type: doc

        This section contains descriptions of the functions and modules included in PyAEDT.
        It describes how the methods work and the parameter that can be used.

    .. grid-item-card::  EDB API reference :fa:`book-bookmark`
        :link: https://edb.docs.pyansys.com/version/stable/
        :link-type: url

        Contains descriptions of the functions and modules included in PyEDB.
        It describes how the methods work and the parameter that can be used.

.. jinja:: main_toctree

   .. grid:: 2

      {% if run_examples %}
      .. grid-item-card:: Examples :fa:`scroll`
         :link: examples/index
         :link-type: doc

         Explore examples that show how to use PyAEDT to perform different types of simulations.
      
      {% endif %}

      .. grid-item-card:: Contribute :fa:`people-group`
         :link: Getting_started/Contributing
         :link-type: doc

         Learn how to contribute to the PyAEDT codebase or documentation.

.. jinja:: main_toctree

    .. toctree::
       :hidden:

       Getting_started/index
       User_guide/index
       API/index
       {% if run_examples %}
       examples/index
       {% endif %}


