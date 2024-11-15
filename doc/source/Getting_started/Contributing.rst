.. _contributing_aedt:

==========
Contribute
==========
Overall guidance on contributing to a PyAnsys repository appears in
`Contribute <https://dev.docs.pyansys.com/how-to/contributing.html>`_
in the *PyAnsys Developer's Guide*. Ensure that you are thoroughly familiar
with this guide, paying particular attention to `Guidelines and Best Practices
<https://dev.docs.pyansys.com/how-to/index.html>`_, before attempting
to contribute to PyAEDT.
 
The following contribution information is specific to PyAEDT.

Clone the repository
--------------------
To clone and install the latest version of PyAEDT in
development mode, run:

.. code::

    git clone https://github.com/ansys/pyaedt
    cd pyaedt
    python -m pip install --upgrade pip
    pip install -e .

Post issues
-----------
Use the `PyAEDT Issues <https://github.com/ansys/pyaedt/issues>`_
page to submit questions, report bugs, and request new features.

To reach the product support team, email `pyansys.core@ansys.com <pyansys.core@ansys.com>`_.

View PyAEDT documentation
-------------------------
Documentation for the latest stable release of PyAEDT is hosted at
`PyAEDT Documentation <https://aedt.docs.pyansys.com>`_.  

In the upper right corner of the documentation's title bar, there is an option
for switching from viewing the documentation for the latest stable release
to viewing the documentation for the development version or previously
released versions.

Code style
----------
PyAEDT complies with the `PyAnsys code style
<https://dev.docs.pyansys.com/coding-style/index.html>`_.
`pre-commit <https://pre-commit.com/>`_ is applied within the CI/CD to ensure compliance.
The ``pre-commit`` Python package can be installed
and run as follows:

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
  isort (python)...........................................................Passed
  flake8...................................................................Passed
  codespell................................................................Passed
  debug statements (python)................................................Passed
  trim trailing whitespace.................................................Passed
  Validate GitHub Workflows................................................Passed
  blacken-docs.............................................................Passed

Naming conventions
~~~~~~~~~~~~~~~~~~
Consistency of names helps improve readability and
ease of use. Starting with release 0.8 a concerted effort
has been made to
improve consistency of naming and adherence to
:ref:`PEP-8<https://peps.python.org/pep-0008/>`_.

For example, methods used to create or access entities in
AEDT require that a name be passed to the method or function
as an argument.
It is tempting to
include context as part of that variable name. For example, while it is tempting to use
``setupname``
as an argument to :meth:`Hfss.create_setup`_,
the context "setup" is
explicitly defined by the method name. The variable ``name`` provides
a more compact
description of the variable in this context.

In previous PyAEDT versions, you can also find both ``setup_name`` and ``setupname`` used 
for various methods or classes.
Improving naming consistency improves maintainability and readability.

The following table illustrates the recommended conventions:

.. list-table:: Keywords and object names
   :widths: 25 25 50
   :header-rows: 1

   * - Old name
     - New name
     - Example
   * - ``setupname``, ``setup_name``, ``sweepname``
     - ``name``
     - ``Hfss.create_setup()``, ``Hfss.create_linear_step_sweep()``
   * - ``usethickness``
     - ``thickness``
     - ``Hfss.assign_coating()``
   * - ``entities``
     - ``assignment``
     - ``Maxwell.assign_current_density()``
   * - ``entity_list``
     - ``assignment``
     - ``Maxwell.assign_symmetry()``

Take care to use descriptive names for
variables and classes that adhere to PEP-8 and are consistent with conventions already
used in PyAEDT.

Log errors
~~~~~~~~~~
PyAEDT has an internal logging tool named ``Messenger``
and a log file that is automatically generated in the project
folder.

The following examples demonstrate how ``Messenger`` is used to
write both to the internal AEDT message windows and the log file:

.. code:: python

    self.logger.error("This is an error message.")
    self.logger.warning("This is a warning message.")
    self.logger.info("This is an info message.")

These examples demonstrate how to write messages only to the log file:

.. code:: python

    self.logger.error("This is an error message.")
    self.logger.warning("This is a warning message.")
    self.logger.info("This is an info message.")


Handle exceptions
~~~~~~~~~~~~~~~~~
PyAEDT uses a specific decorator, ``@pyaedt_function_handler``,
to handle exceptions caused by methods and by the AEDT API.
This exception handler decorator makes PyAEDT fault tolerant
to errors that can occur in any method.

For example:

.. code:: python

   @pyaedt_function_handler()
   def my_method(self, var):
       pass

Every method can return a value of ``True`` when successful or 
``False`` when failed. When a failure occurs, the error
handler returns information about the error in both the console and
log file.

Here is an example of an error:

.. code::

   ----------------------------------------------------------------------------------
   PyAEDT error on method create_box:  General or AEDT error. Check again
   the arguments provided:
       position = [0, 0, 0]
       dimensions_list = [0, 10, 10]
       name = None
       material = None
   ----------------------------------------------------------------------------------

   (-2147352567, 'Exception occurred.', (0, None, None, None, 0, -2147024381), None)
     File "C:\GIT\repos\AnsysAutomation\PyAEDT\Primitives.py", line 1930, in create_box
       o.name = self.oeditor.createbox(vArg1, vArg2)

   ************************************************************
   Method Docstring:

   Create a box.

   Parameters
   ----------
   ...


Hard-coded values
~~~~~~~~~~~~~~~~~~
Do not write hard-coded values to the registry. Instead, use the Configuration service.

Maximum line length
~~~~~~~~~~~~~~~~~~~
Best practice is to keep the length at or below 120 characters for code,
and comments. Lines longer than this might not display properly on some terminals
and tools or might be difficult to follow.
