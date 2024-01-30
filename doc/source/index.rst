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

       User_guide/index
       {% if run_examples %}
       examples/index
       {% endif %}


