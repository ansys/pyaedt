PyAEDT documentation  |version|
===============================

**Useful links**:
`Installation <https://aedt.docs.pyansys.com/version/stable/Getting_started/Installation.html>`_ |
`Source Repository <https://github.com/ansys/pyaedt>`_ |
`Issues <https://github.com/ansys/pyaedt/issues>`_

PyAEDT is a Python library that interacts directly with the Ansys Electronics Desktop (AEDT) API,
enabling straightforward and efficient automation in your workflow.

.. grid:: 2

   .. grid-item-card::
            :img-top: _static/assets/index_getting_started.png

            Getting started
            ^^^^^^^^^^^^^^^

            New to PyAEDT? This section provides the information that you need to get started with PyAEDT.

            +++

            .. button-link:: Getting_started/index.html
               :color: secondary
               :expand:
               :outline:
               :click-parent:

                  Getting started

   .. grid-item-card::
            :img-top: _static/assets/index_user_guide.png

            User guide
            ^^^^^^^^^^

            This section provides in-depth information on PyAEDT key concepts.

            +++
            .. button-link:: User_guide/index.html
               :color: secondary
               :expand:
               :outline:
               :click-parent:

                  User guide



.. grid:: 2

   .. grid-item-card::
            :img-top: _static/assets/index_api.png

            AEDT API reference
            ^^^^^^^^^^^^^^^^^^

            The PyAEDT API reference contains descriptions of the functions and modules included in PyAEDT.
            It describes how the methods work and the parameter that can be used.

            +++
            .. button-link:: API/index.html
               :color: secondary
               :expand:
               :outline:
               :click-parent:

                  AEDT API reference

   .. grid-item-card::
            :img-top: _static/assets/index_api.png

            EDB API reference
            ^^^^^^^^^^^^^^^^^

            The PyAEDT EDB API reference contains descriptions of the functions and modules included in PyAEDT.
            It describes how the methods work and the parameter that can be used.

            +++
            .. button-link:: EDBAPI/index.html
               :color: secondary
               :expand:
               :outline:
               :click-parent:

                  EDB API reference

.. jinja:: main_toctree

    .. grid:: 2

           {% if run_examples %}
           .. grid-item-card::
                    :img-top: _static/assets/index_examples.png

                    Examples
                    ^^^^^^^^

                    Explore examples that show how to use PyAEDT to
                    perform different types of simulations.

                    +++
                    .. button-link:: examples/index.html
                       :color: secondary
                       :expand:
                       :outline:
                       :click-parent:

                          Examples
           {% endif %}

        .. grid-item-card::
                :img-top: _static/assets/index_contribute.png

                Contribute
                ^^^^^^^^^^
                Learn how to contribute to the PyAEDT codebase
                or documentation.

                +++
                .. button-link:: Getting_started/Contributing.html
                   :color: secondary
                   :expand:
                   :outline:
                   :click-parent:

                      Contribute

Indices and tables
==================
* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`


.. jinja:: main_toctree

    .. toctree::
       :hidden:

       Getting_started/index
       User_guide/index
       API/index
       EDBAPI/index
       {% if run_examples %}
       examples/index
       {% endif %}


