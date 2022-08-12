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
       matname = None
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
Best practice is to keep the length at or below 120 characters for code, docstrings,
and comments. Lines longer than this might not display properly on some terminals
and tools or might be difficult to follow.
