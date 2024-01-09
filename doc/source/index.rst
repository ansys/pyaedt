PyAEDT documentation  |version|
===============================

PyAEDT is a Python library that interacts directly with the API for
Ansys Electronics Desktop (AEDT) to make scripting simpler.

In the upper right corner of the documentation's title bar, there is an option
for switching from viewing the documentation for the latest stable release
to viewing the documentation for the development version or previously
released versions.

You can also view or download PyAEDT cheat sheets, which are one-page references
providing syntax rules and commands for using the PyAEDT API and PyEDB API:

- `View PyAEDT cheat sheet <https://cheatsheets.docs.pyansys.com/pyaedt_API_cheat_sheet.png>`_ or
  `download PyAEDT cheat sheet <https://cheatsheets.docs.pyansys.com/pyaedt_API_cheat_sheet.pdf>`_ the
  PyAEDT API cheat sheet.

- `View EDB cheat sheet <https://cheatsheets.docs.pyansys.com/pyedb_API_cheat_sheet.png>`_ or
  `download EDB cheat sheet  <https://cheatsheets.docs.pyansys.com/pyedb_API_cheat_sheet.pdf>`_ the
  PyAEDT API cheat sheet.


On the `PyAEDT Issues <https://github.com/ansys/PyAEDT/issues>`_ page, you can
create issues to report bugs and request new features. On the `PyAEDT Discussions
<https://github.com/ansys/pyaedt/discussions>`_ page or the `Discussions <https://discuss.ansys.com/>`_
page on the Ansys Developer portal, you can post questions, share ideas, and get community feedback.


.. grid:: 2

   .. grid-item-card::
            :img-top: _static/assets/index_getting_started.png

            Getting started
            ^^^^^^^^^^^^^^^

            Learn how to run install PyAEDT, to launch Electronics Desktop and
            install link button in AEDT.

            +++

            .. button-link:: Getting_started/index.html
               :color: secondary
               :expand:
               :outline:
               :click-parent:

                  Getting started

   .. grid-item-card::
            :img-top: _static/assets/index_user_guide.png

            Tutorial
            ^^^^^^^^

            Understand key concepts and approaches for primitives,
            modeler, mesh, setup and post-processing.

            +++
            .. button-link:: User_guide/index.html
               :color: secondary
               :expand:
               :outline:
               :click-parent:

                  Tutorial



.. grid:: 2

   .. grid-item-card::
            :img-top: _static/assets/index_api.png

            AEDT API reference
            ^^^^^^^^^^^^^^^^^^

            Understand PyAEDT API endpoints, their capabilities,
            and how to interact with them programmatically.

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

            Understand PyAEDT EDB API endpoints, their capabilities,
            and how to interact with them programmatically.

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


