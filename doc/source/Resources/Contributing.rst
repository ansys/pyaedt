.. _contributing_aedt:

============
Contributing
============
Overall guidance on contributing to a PyAnsys repository appears in the
`Contributing <https://dev.docs.pyansys.com/overview/contributing.html>`_ topic
in the *PyAnsys Developer's Guide*. Ensure that you are thoroughly familiar
with it and all `Guidelines and Best Practices <https://dev.docs.pyansys.com/guidelines/index.html>`_
before attempting to contribute to PyAEDT.
 
The following contribution information is specific to PyAEDT.

Cloning the PyAEDT repository
-----------------------------
Run this code to clone and install the latest version of PyAEDT in development mode:

.. code::

    git clone https://github.com/pyansys/pyaedt
    cd pyaedt
    pip install -e .

Posting issues
--------------
Use the `PyAEDT Issues <https://github.com/pyansys/pyaedt/issues>`_
page to submit questions, report bugs, and request new features.

To reach the project support team, email `pyansys.support@ansys.com <pyansys.support@ansys.com>`_.

Viewing PyAEDT documentation
-----------------------------
Documentation for the latest stable release of PyAEDT is hosted at
`PyAEDT Documentation <https://aedtdocs.pyansys.com>`_.  

Documentation for the latest development version, which tracks the
``main`` branch, is hosted at  `Development PyAEDT Documentation <https://dev.aedtdocs.pyansys.com/>`_.
This version is automatically kept up to date via GitHub actions.

Code style
----------
PyAEDT follows PEP8 standard as outlined in the `PyAnsys Development Guide
<https://dev.docs.pyansys.com>`_ and implements style checking using
`pre-commit <https://pre-commit.com/>`_.

To ensure your code meets minimum code styling standards, run::

  pip install pre-commit
  pre-commit run --all-files

You can also install this as a pre-commit hook by running::

  pre-commit install

This way, it's not possible for you to push code that fails the style checks. For example::

  $ pre-commit install
  $ git commit -am "added my cool feature"
  black....................................................................Passed
  isort....................................................................Passed
  flake8...................................................................Passed
  codespell................................................................Passed
