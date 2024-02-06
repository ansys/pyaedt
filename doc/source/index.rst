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

       User_guide/index
       {% if run_examples %}
       examples/index
       {% endif %}


