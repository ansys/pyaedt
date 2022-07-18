Code guidelines
===============

All contributors must adhere to the following guidelines to:

#. Prevent against common programming errors
#. Limit program complexity
#. Provide an easily readable, understandable, and maintainable product
#. Establish a consistent style
#. Implement an objective basis for code review

To ensure program homogeneity and code stability, be sure to follow
the guidelines presented herein.


Python coding guidelines
-------------------------------
The following sections summarize the key points from `PEP8
<https://www.python.org/dev/peps/pep-0008/>`_ and how they apply to
PyAEDT and other PyAnsys modules. PyAnsys libraries will attempt to
be consistent in style and formatting with the "big three" data science
libraries: `numpy <https://numpy.org/>`_, `scipy
<https://www.scipy.org/>`_, and `pandas <https://pandas.pydata.org/>`_.


Imports
-------
Imports should always be placed at the top of the file, just after any
module comments and docstrings and before module globals and
constants.  This reduces the likelihood of an ``ImportError`` that might only
be discovered during runtime.

Avoid this:

.. code:: python

   def compute_logbase8(x):
       import math
       return math.log(8, x)

Instead:

.. code:: python

    import math

    def compute_logbase8(x):
      return math.log(8, x)


For better readability, you should group imports following this order:

#. Standard library imports
#. Related third-party imports
#. Local application/library-specific imports

Not recommended:

.. code:: python

   from System import uri
   import sys
   import subprocess
   from mypackage import mymodule
   import math

   def compute_logbase8(x):
      return math.log(8, x)


Recommended:

.. code:: python

   import sys
   import subprocess
   import math
   from System import uri
   from mypackage import mymodule

   def compute_logbase8(x):
       return math.log(8, x)


You should place imports in separate lines unless they are
modules from the same package.

Not recommended:

.. code:: python

   import sys, math
   from my_package import my_module
   from my_package import my_other_module

   def compute_logbase8(x):
       return math.log(8, x)

Recommended:

.. code:: python

   import sys
   import math
   from my_package import my_module, my_other_module

   def compute_logbase8(x):
       return math.log(8, x)


You should generally avoid using wild cards in imports because doing so
can cause confusion on which names are present in the namespaces.

Avoid:

.. code:: python

    from my_package.mymodule import *

Instead:

.. code:: python

    from my_package.my_module import myclass


Indentation and line breaks
---------------------------
Proper and consistent indentation is important to producing
easy-to-read and maintainable code. In Python, use four spaces per
indentation level and avoid tabs. 

Indentation should be used to:

 - Emphasize the body of a control statement, such as a loop or a select statement.
 - Emphasize the body of a conditional statement.
 - Emphasize a new scope block.

.. code:: python

   class MyFirstClass:
       """MyFirstClass docstring"""

   class MySecondClass:
       """MySecondClass docstring"""

   def top_level_function():
       """Top level function docstring"""
       return

For improved readability, add blank lines or wrapping lines. Two
blank lines should be added before and after all function and class definitions.

Inside a class, use a single line before any method definition.

.. code:: python

   class MyClass:
       """MyClass docstring"""

   def first_method(self):
       """First method docstring"""
       return

   def second_method(self):
       """Second method docstring"""
       return

Use a blank line to separate logical sections. 

Instead of:

.. code::

   if x < y:

       STATEMENTS_A

   else:

       if x > y:

           STATEMENTS_B

       else:

           STATEMENTS_C

   if x > 0 and x < 10:

       print("x is a positive single digit.")

Use:

.. code::

   if x < y:
       STATEMENTS_A
   else:
       if x > y:
           STATEMENTS_B
       else:
           STATEMENTS_C

   if x > 0 and x < 10:
       print("x is a positive single digit.")
   elif x < 0:
       print("x is less than zero.")


This way, it's clear when a "paragraph" of code is complete and 
a new section is starting.


Maximum line length
-------------------
For source code lines, best practice is to keep the length at or below
79 characters.  For docstrings and comments, best practice is to keep
the length at or below 72 characters.

Lines longer than this might not display properly on some terminals and tools 
or might be difficult to follow.  For example, this line is difficult to follow:

.. code:: python

   employee_hours = [schedule.earliest_hour for employee in self.public_employees for schedule in employee.schedules]

The line can be rewritten as:

.. code:: python

   employee_hours = [schedule.earliest_hour for employee in
                     self.public_employees for schedule in employee.schedules]

Alternatively, instead of writing a list comprehension, you can use a
classic loop.


Naming conventions
------------------
It is important to use concise and descriptive names for classes,
methods, functions, and constants for readable and maintainable
code. Regardless of the programming language, you must follow these
global rules to determine the correct names:

#. Choose descriptive and unambiguous names.
#. Make meaningful distinctions.
#. Use pronounceable names.
#. Use searchable names.
#. Replace magic numbers with named constants.
#. Avoid encodings. Do not append prefixes or type information.


Names to avoid
~~~~~~~~~~~~~~
Do not use the characters ``'l'``, ``'O'`` , or ``'I'`` as
single-character variable names. In some fonts, these characters are
indistinguishable from the numerals one and zero.


Package and module naming
~~~~~~~~~~~~~~~~~~~~~~~~~
Use a short, lowercase word or words for module names. Separate words
with underscores to improve readability.  For example, ``module.py`` or
``my_module.py``.

For a package name, use a short, lowercase word or words.  Avoid
underscores as these will have to be represented as dashes when
installing from PyPi.

.. code::

   pip install package


Class naming
~~~~~~~~~~~~
Use camel case when naming classes.  Do not separate words
with underscores.  For example:

.. code:: python

   class MyClass():
       """Docstring for MyClass"""
       pass


Function and method naming
~~~~~~~~~~~~~~~~~~~~~~~~~~
Use a lowercase word or words for Python functions or methods. Separate
words with underscores to improve readability. 

.. code:: python

   class MyClass():
       """Docstring for MyClass"""

       def __init__(self, value):
           """Constructor.

           Methods with double underscores on either side are called
           "dunder" methods and are special Python methods.

           """
           self._value = value

       def __private_method(self):
           """This method can only be called from ``MyClass``."""
           self._value = 0

       def _protected_method(self):
           """This method should only be called from ``MyClass``.

           Protected methods can be called from inherited classes,
           unlike private methods, which names are "mangled" to avoid
           these methods from being called from inherited classes.

           """
           # note how we can call private methods here
           self.__private_method()

       def public_method(self):
           """This method can be called external to this class."""
           self._value += 2


Variable naming
~~~~~~~~~~~~~~~
Use a lowercase single letter, word, or words when naming
variables. Separate words with underscores to improve readability.

.. code:: python

    my_variable = 5


Constants are variables that are set at the module level and are used
by one or more methods within that module. Use an uppercase word or
words for constants. Separate words with underscores to improve
readability.

.. code:: python

    PI = 3.141592653589793
    CONSTANT = 4
    MY_CONSTANT = 8
    MY_OTHER_CONSTANT = 1000


Comments
--------
Because PyAEDT is about multiple physics domains, the people reading
its source code do not have the same background as the person who
writes it. This is why it is important for this library to have well
commented and documented source code. Comments that contradict the
code are worse than no comments. Always make a priority of keeping
comments up to date with the code.

Comments should be complete sentences. The first word should be
capitalized, unless it is an identifier that begins with a lowercase
letter.

Here are general guidelines for writing comments:

#. Always try to explain yourself in code by making it
   self-documenting with clear variable names.
#. Don't be redundant.
#. Don't add obvious noise.
#. Don't use closing brace comments.
#. Don't comment out code that is unused. Remove it.
#. Use explanations of intent.
#. Clarify the code.
#. Warn of consequences.

Obvious portions of the source code should not be commented. 
For example:

.. code:: python

   # increment the counter
   i += 1

However, important portions of the behavior that are not self-apparent
should include a note from the developer writing it.  Otherwise,
future developers may remove what they see as unnecessary. For example:

.. code:: python

   # Be sure to reset the object's cache prior to exporting, otherwise
   # some portions of the database in memory will not be written.
   obj.update_cache()
   obj.write(filename)


Inline comments
~~~~~~~~~~~~~~~
Inline comments should be used sparingly. An inline comment is a comment 
on the same line as a statement.

Inline comments should be separated by two spaces from the statement. 
For example:

.. code:: python

    x = 5  # This is an inline comment

Inline comments that state the obvious are distracting. Again, avoid:

.. code:: python

    x = x + 1  # Increment x


Focus on writing self-documenting code and using short, but
descriptive variable names.  

Rather than:

.. code:: python

   x = 'John Smith'  # Student Name

Use:

.. code:: python

    user_name = 'John Smith'


Docstrings
----------
A docstring is a string literal that occurs as the first statement in
a module, function, class, or method definition.  A docstring becomes
the doc special attribute of the object.

Write docstrings for all public modules, functions, classes, and
methods. Docstrings are not necessary for non-public methods, but such
methods should have comments that describe what they do.

To create a docstring, surround the comments with three double quotes
on either side.

For a one-line docstring, keep both the starting and ending ``"""`` on the
same line. For example:

.. code:: python

   """This is a docstring.""".  

For a multi-line docstring, put the ending ``"""`` on a line by itself.

PyAEDT follows the `numpydoc
<https://numpydoc.readthedocs.io/en/latest/format.html>`_
documentation style, which is used by `numpy <https://numpy.org/>`_,
`scipy <https://www.scipy.org/>`_, `pandas
<https://pandas.pydata.org/>`_, and a variety of other Python open
source projects.  For a full description of the code style, reference
`PyAnsys sphinxdocs <https://sphinxdocs.pyansys.com/style.html>`_.


Programming recommendations
---------------------------
This section provides some of the `PEP8
<https://www.python.org/dev/peps/pep-0008/>`_ suggestions for removing
ambiguity and preserving consistency.  They address some common pitfalls 
when writing Python code.


Booleans and comparisons
~~~~~~~~~~~~~~~~~~~~~~~~
Don't compare Boolean values to ``True`` or ``False`` using the
equivalence operator.

Rather than:

.. code:: python

   if my_bool == True:
       return result

Use:

.. code:: python

   if my_bool:
       return result

Knowing that empty sequences are evaluated to ``False``, don't compare the
length of these objects but rather consider how they would evaluate
by using ``bool(<object>)``.

  Avoid:

.. code:: python

   my_list = []
   if not len(my_list):
       raise ValueError('List is empty')

Instead:

.. code:: python

    my_list = []
    if not my_list:
       raise ValueError('List is empty')

In ``if`` statements, use ``is not`` rather than ``not ...``. 

Rather than:

.. code:: python

    if not x is None:
        return x

Use:

.. code:: python

   if x is not None:
       return 'x exists!'

Also, avoid ``if x:`` when you mean ``if x is not None:``.  This is
especially important when parsing arguments.


Handling strings
~~~~~~~~~~~~~~~~
Use ``.startswith()`` and ``.endswith()`` instead of slicing.

Rather than:

.. code:: python

   if word[:3] == 'cat':
       print('The word starts with "cat"')

   if file_name[-3:] == 'jpg':
       print('The file is a JPEG')

Use:

.. code:: python

   if word.startswith('cat'):
       print('The word starts with "cat"')

   if file_name.endswith('jpg'):
       print('The file is a JPEG')


Reading the Windows registry
~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Never read the Windows registry or write to it because this is dangerous and 
makes it difficult to deploy libraries on different environments or operating
systems.

Bad practice - Example 1

.. code:: python

   self.sDesktopinstallDirectory = Registry.GetValue("HKEY_LOCAL_MACHINE\Software\Ansoft\ElectronicsDesktop\{}\Desktop".format(self.sDesktopVersion), "InstallationDirectory", '')

Bad practice - Example 2

.. code:: python

    EMInstall = (string)Registry.GetValue(string.Format(@"HKEY_LOCAL_MACHINE\SOFTWARE\Ansoft\ElectronicsDesktop{0}\Desktop", AnsysEmInstall.DesktopVersion), "InstallationDirectory", null);


Duplicated code
~~~~~~~~~~~~~~~
Follow the DRY principle, which states that "Every piece of knowledge
must have a single, unambiguous, authoritative representation within a
system."  Attempt to follow this unless it overly complicates the code.
For instance, the following example converts Fahrenheit to Kelvin
twice, which now requires the developer to maintain two separate lines
that do the same thing.

.. code:: python

   temp = 55
   new_temp = ((temp - 32) * (5 / 9)) + 273.15

   temp2 = 46
   new_temp_k = ((temp2 - 32) * (5 / 9)) + 273.15

Instead, write a simple method that converts Fahrenheit to Kelvin:

.. code:: python

   def fahr_to_kelvin(fahr)
       """Convert temperature in Fahrenheit to kelvin.

       Parameters:
       -----------
       fahr: int or float
           Temperature in Fahrenheit.

       Returns:
       -----------
       kelvin : float
          Temperature in kelvin.
       """
       return ((fahr - 32) * (5 / 9)) + 273.15

Now, you can execute and get the exact same output with:

.. code:: python

   new_temp = fahr_to_kelvin(55)
   new_temp_k = fahr_to_kelvin(46)

This is a trivial example, but the approach can be applied for a
variety of both simple and complex algorithms and workflows.  Another
advantage of this approach is that you can now implement unit testing
for this method.  For example:

.. code:: python

   import numpy as np

   def test_fahr_to_kelvin():
       assert np.isclose(12.7778, fahr_to_kelvin(55))

Now, not only do you have one line of code to verify, but using a
testing framework such as ``pytest``, you can verify that the method is
correct.


Nested blocks
~~~~~~~~~~~~~

Avoid deeply nested block structures (such as conditional blocks and loops)
within one single code block. For example:

.. code:: python

   def validate_something(self, a, b, c):
       if a > b:
           if a*2 > b:
               if a*3 < b:
                   raise ValueError
           else:
               for i in range(10):
                   c += self.validate_something_else(a, b, c)
                   if c > b:
                       raise ValueError
                   else:
                       d = self.foo(b, c)
                       # recursive
                       e = self.validate_something(a, b, d)


Aside from the lack of comments, this complex nested validation method
is difficult to debug and validate with unit testing. It would
be far better to implement more validation methods and join conditionals.

For a conditional block, the maximum depth recommended is four. If you
think you need more for the algorithm, create small functions that are
reusable and unit-testable.


Loops
~~~~~
While there is nothing inherently wrong with nested loops, to avoid
certain pitfalls, avoid having loops with more than two levels. In
some cases, you can rely on coding mechanisms like list comprehensions 
to avoid nested loops. 

Rather than:

.. code::

   >>> squares = []
   >>> for i in range(10):
   ...    squares.append(i * i)
   >>> squares
   [0, 1, 4, 9, 16, 25, 36, 49, 64, 81]


Implement a list comprehension with:

.. code::

   >>> squares = [i*i for i in range(10)]
   >>> squares
   [0, 1, 4, 9, 16, 25, 36, 49, 64, 81]


If the loop is too complicated for creating a list comprehension,
consider creating small functions and calling these instead.  For
example, extract all consonants in a sentence:

.. code:: python

   >>> sentence = 'This is a sample sentence.'
   >>> vowels = 'aeiou'
   >>> consonants = []
   >>> for letter in sentence:
   ...     if letter.isalpha() and letter.lower() not in vowels:
   ...         consonants.append(letter)
   >>> consonants
   ['T', 'h', 's', 's', 's', 'm', 'p', 'l', 's', 'n', 't', 'n', 'c']


This is better implemented by creating a simple method to return if a
letter is a consonant.

   >>> def is_consonant(letter):
   ...     """Return True when a letter is a consonant."""
   ...     vowels = 'aeiou'
   ...     return letter.isalpha() and letter.lower() not in vowels
   ...
   >>> sentence = 'This is a sample sentence.'
   >>> consonants = [letter for letter in sentence if is_consonant(letter)]
   >>> consonants
   ['T', 'h', 's', 's', 's', 'm', 'p', 'l', 's', 'n', 't', 'n', 'c']

The advantage of the second approach is it is more readable and better
documented.  Additionally, while it's a trivial example, you could
implement a unit test for ``is_consonant``.


PyAEDT-specific guidelines
--------------------------
These coding guidelines are specific to PyAEDT.


Logging errors
~~~~~~~~~~~~~~
PyAEDT has an internal logging tool named ``Messenger``
and a log file that is automatically generated in the project
folder. 

The following examples demonstrate how Messenger is used to 
write both to the internal AEDT message windows and the log file:

.. code:: python

    self.logger.error("This is an error message.")
    self.logger.warning("This is a warning message.")
    self.logger.info("This is an info message.")

These examples demonstrate how to to write messages only to the log file:

.. code:: python

    self.logger.error("This is an error message.")
    self.logger.warning("This is a warning message.")
    self.logger.info("This is an info message.")


Exception handling
~~~~~~~~~~~~~~~~~~
PyAEDT uses a specific decorator,  
``@pyaedt_function_handler``, to handle exceptions caused by
methods and by the AEDT API. This exception handler decorator 
makes PyAEDT fault tolerant to errors that can occur in any method. 
For example:

.. code:: python

   @pyaedt_function_handler()
   def my_method(self, var):
       pass

Every method may return a value of ``True`` in case of success and
``False`` in case of failure.  When a failure occurs, the error
handler returns information about the error in both the console and
log file. Here is an example of an error:

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

   Create a Box

   Parameters
   ----------
   ...


Hard-coding values
~~~~~~~~~~~~~~~~~~
Do not write hard-coded values to the registry. Instead, use the Configuration service.
