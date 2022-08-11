.. _contributing_aedt:

============
Contributing
============
Overall guidance on contributing to a PyAnsys repository appears in
`Contributing <https://dev.docs.pyansys.com/overview/contributing.html>`_
in the *PyAnsys Developer's Guide*. Ensure that you are thoroughly familiar
with it, paying particular attention to `Guidelines and Best Practices
<https://dev.docs.pyansys.com/guidelines/index.html>`_, before attempting
to contribute to PyAEDT.
 
The following contribution information is specific to PyAEDT.

Clone the repository
--------------------
To clone and install the latest version of PyAEDT in
development mode, run:

.. code::

    git clone https://github.com/pyansys/pyaedt
    cd pyaedt
    pip install -e .

Post issues
--------------
Use the `PyAEDT Issues <https://github.com/pyansys/pyaedt/issues>`_
page to submit questions, report bugs, and request new features.

To reach the support team, email `pyansys.support@ansys.com <pyansys.support@ansys.com>`_.

View PyAEDT documentation
-------------------------
Documentation for the latest stable release of PyAEDT is hosted at
`PyAEDT Documentation <https://aedtdocs.pyansys.com>`_.  

Documentation for the latest development version, which tracks the
``main`` branch, is hosted at  `Development PyAEDT Documentation <https://dev.aedtdocs.pyansys.com/>`_.
This version is automatically kept up to date via GitHub actions.

Adhere to code style
--------------------
PyAEDT is compliant with `PyAnsys code style
<https://dev.docs.pyansys.com/coding_style/index.html>`_. It uses the tool
`pre-commit <https://pre-commit.com/>`_ to check the code style. You can install
and activate this tool with:

.. code:: bash

  pip install pre-commit
  pre-commit run --all-files

You can also install this as a pre-commit hook with:

.. code:: bash

  pre-commit install

This way, it's not possible for you to push code that fails the style checks.
For example::

  $ pre-commit install
  $ git commit -am "Add my cool feature."
  black....................................................................Passed
  isort....................................................................Passed
  flake8...................................................................Passed
  codespell................................................................Passed
