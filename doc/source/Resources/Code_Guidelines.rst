Code Guidelines
===============

All contributors must adhere to the following guidelines to: 

#. Prevent against common programming errors
#. Limit program complexity
#. Provide an easily readable, understandable, and maintainable product
#. Establish a consistent style  
#. Implement an objective basis for code review

To ensure program homogeneity and code stability, be sure to follow
the guidelines presented in the subsequent sections. 

General Guidelines
------------------

Reading the Windows Registry
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Never read the Windows registry because doing so is danagerous
and makes it difficult to on different enviornments or operating systems.

Bad practice - Example 1

.. code:: python

   self.sDesktopinstallDirectory = Registry.GetValue("HKEY_LOCAL_MACHINE\Software\Ansoft\ElectronicsDesktop\{}\Desktop".format(self.sDesktopVersion), "InstallationDirectory", '')

Bad practice - Example 2

.. code:: python

    EMInstall = (string)Registry.GetValue(string.Format(@"HKEY_LOCAL_MACHINE\SOFTWARE\Ansoft\ElectronicsDesktop{0}\Desktop", AnsysEmInstall.DesktopVersion), "InstallationDirectory", null);


Hard-Coding Values
~~~~~~~~~~~~~~~~~~
Do not write to the registry hard-coded values that the code is to
use. Instead, use the Configuration service.


Duplicated Code
~~~~~~~~~~~~~~~
Follow the DRY principle, which states that "Every piece of knowledge
must have a single, unambiguous, authoritative representation within a
system".  Attempt to follow this unless it overly complicates code.
For example, the follwing example converts Fahrenheit to Celsius
twice.  This now requires the developer to maintain two seperate lines
that do the same thing:

.. code:: python

   temp = 55
   new_temp = ((temp - 32) * (5 / 9)) + 273.15

   temp2 = 46 
   new_temp_k = ((temp2 - 32) * (5 / 9)) + 273.15

Instead, write a simple method that converts Fahrenheit to Celsius:

.. code:: python

   def fahr_to_kelvin(fahr) 
       """Convert temperature in Fahrenheit to kelvin.

       Parameters:
       -----------
       fahr: int or float
           The temperature in Fahrenheit.
    
       Returns:
       -----------
       kelvin : float
           The temperature in kelvin.
       """
       return ((fahr - 32) * (5 / 9)) + 273.15

Now, you can exectue get the exact same output with:

.. code:: python

   new_temp = fahr_to_kelvin(55)
   new_temp_k = fahr_to_kelvin(46)

This is a trivial example, but the approach can be applied for a
variety of both simple and complex algorthims and workflows.  Another
advantage of this approach is that you can now implement unit testing
for this method.  For example:

.. code:: python

   import numpy as np

   def test_fahr_to_kelvin():
       assert np.isclose(12.7778, fahr_to_kelvin(55))

Now, not only do we only have one line of code to verify, but using a
testing framework such as ``pytest``, we can verify that the method is
correct.


Nested Blocks
~~~~~~~~~~~~~

Avoid deeply nested block structures (conditional blocks, loops, ...)
within one single code block.  For example:

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
will be difficult to debug (and validate with unit testing).  It would
be far better to implement more validation methods, join conditionals,
etc.

For a conditional block, the maximum depth recommended is four. If you
think you need more for the algorithm, create small functions that are
reusable and unit-testable.

Loops
~~~~~
While there is nothing inherently wrong with nested loops, to avoid
certain pitfalls, avoid having loops with more than two levels. In
some cases, you can rely on coding mechanisms to avoid nested loops
like list comprehensions.  For example, rather than:

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


If the loop is too complicated to create a list comprehension for,
consider create small functions and calling those instead.  For
example, extracting all the consonants in a sentence:

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
documented.  Additionally, while it's a trivial example, we could
implement a unit test for ``is_consonant``.

AEDT Specific Coding Guidelines
-------------------------------
These guidelines are specific to PyAEDT.

Logging Errors
~~~~~~~~~~~~~~

PyAEDT automatically has an internal logging tool named ``Messenger``
and a log file that is automatically generated in the project
folder. The following examples demonstrates how the Messenger is used
to write both to the internal logger and log file:

.. code:: python

    self.messenger.add_error_message("This is an error message.")
    self.messenger.add_warning_message("This is a warning message.")
    self.messenger.add_info_message("This is an info message.")

The above messages are written to both AEDT message windows and the
log file.  If you want the message to be written only to the log file,
use:

.. code:: python

    self.logger.error("This is an error message.")
    self.messenger.warning("This is a warning message.")
    self.messenger.info("This is an info message.")


**Exceptions Handling**

AEDTLib uses a specific decorator to handle exceptions caused by methods and 
by AEDT API. The eception handler decorator is @aedt_exception_handler. 
It makes AEDTLib fault tolerant to errors that can happear in any method.
This example shows how to use it:

```
    @aedt_exception_handler
    def my_method(self, var):
        pass
``` 
Every method may return a value of ``True`` in case of success and ``False`` in case of failure. 
When a failure occurs, the error handler returns information about the error in both the
console and log file. Here is an example of an error:

```
    ---------------------------------------------------------------------------------------
    AEDTLib error on method create_box:  General or AEDT error. Check again
    the arguments provided: 
        position = [0, 0, 0] 
        dimensions_list = [0, 10, 10] 
        name = None 
        matname = None 
    ---------------------------------------------------------------------------------------
    
    (-2147352567, 'Exception occurred.', (0, None, None, None, 0, -2147024381), None)
      File "C:\GIT\repos\AnsysAutomation\AEDTLib\Primitives.py", line 1930, in create_box
        o.name = self.oeditor.CreateBox(vArg1, vArg2)
    
    ************************************************************
    Method Docstring: 
    
    Create a Box
    
            :param position: ApplicationName.modeler.Position(x,y,z) object
            :param dimensions_list: list of dimensions of X, Y, Z
            :param name: box name. Optional, if nothing default name will be assigned
            :param matname: material name. Optional, if nothing default material will be assigned
            :return: Box ID
            
    ************************************************************

``` 

Python Coding Guidelines
========================

Imports
-------

Imports must always be placed at the top of the file, just after any module comments and docstrings and before module globals and constants.

Never do this:

```
    def compute_logBase8(x):
    import math
    return math.log(8, x)
```

Recommended:

```
    import math

    def compute_logBase8(x):
    return math.log(8, x)
```

For better readability, you should group the imports following this order:

1. Standard library
2. Related third-party imports
3. Local application/library-specific imports

Not recommended:

```
    from System import Uri
    import sys
    import subprocess
    from MyPackage import MyModule
    import math

    def compute_logBase8(x):
    return math.log(8, x)
```

Recommended:

```
    import sys
    import subprocess
    import math
    from System import Uri
    from MyPackage import MyModule
    
    def compute_logBase8(x):
    return math.log(8, x)
```

You shoulod place imports in separate lines unless they are related to modules from the same package.

Not recommended:

```    
    import sys, math
    from MyPackage import MyModule1
    from MyPackage import MyModule2
    
    def compute_logBase8(x):
    return math.log(8, x)
```

Recommended:
 
```    
    import sys
    import math
    from MyPackage import MyModule1, MyModule2
    
    def compute_logBase8(x):
    return math.log(8, x)
```

You should generally avoid using wild cards in imports because it 
can cause confusion on which names are present in the namespaces.

Not recommended:

``` 
    from MyPackage.MyModule import *
```     

Recommended:

``` 
    from MyPackage.MyModule import MyClass
``` 

Indentation
-----------

Proper and consistent indentation is important in producing easy-to-read 
and maintainable code. In Python, use four spaces per indentation level 
and avoid tabs. Indentation should be used to:

- Emphasize the body of a control statement such as a loop or a select statement.
- Emphasize the body of a conditional statement.
- Emphasize a new scope block.
- Add blank lines or wrapping lines.
- Add two blank lines before and after all function and class definitions.

```
    class MyFirstClass:
    pass
    
    class MySecondClass:
    pass
    
    def top_level_function():
    return None
    Inside a class, put a single line before any method definition.
    
    class MyClass:
    def first_method(self):
    return None
    
    def second_method(self):
        return None
```
        
To structure well the code inside a function, use a blank line to separate the logical sections.

Maximum Line Length
-------------------

For source code lines, best practice is to keep the length at or below 79 characters.
For docstrings and comments, best pratice is to keep the lenght at or below 72 characters.

Lines longer than this may not display properly on some terminals and tools.

Naming Conventions
------------------

To produce code that is easy to maintain, naming of classes, methods, functions, constants, 
and more is critical. Regardless of the programming language, you must follow these global 
rules to determine the right name:

1. Choose descriptive and unambiguous names.
1. Make meaningful distinctions.
1. Use pronounceable names.
1. Use searchable names.
1. Replace magic numbers with named constants.
1. Avoid encodings. Do not append prefixes or type information.


**Names to Avoid**

Never use the characters 'l' (lowercase letter el), 'O' (uppercase letter oh), or 'I' 
(uppercase letter ie) as single-character variable names. In some fonts, these characters 
are indistinguishable from the numerals one and zero.

**Package and Module Naming**

To create a module, use a short, lowercase word or words to name it. Separate words 
with underscores to improve readability.

```
    module.py, my_module.py
```

For a package, use a short, lowercase word or words. Do not separate words 
with underscores.

```
    package, mypackage
```

**Class Naming**

To name a class, use the CapWords or camel case convention. It means that you must 
start each word with a capital letter. Do not separate words with underscores.

Not recommended:

```
    class myclass():
    def init(self): # Our ctor method
    
    class my_class():
    def init(self): # Our ctor method
```

Recommended:

```
    class MyClass():
    def init(self): # Our ctor method
```

**Function and Method Naming**

For a method name, use a lowercase word or words. Separate words with 
underscores to improve readability.

```
    class MyClass():
    def init(self): # ctor()
    
    def my_class_method():
    my_function
```

**Variable Naming**

For a vairable, use a lowercase single letter, word, or words. Separate words 
with underscores to improve readability.

```
    my_variable=5
```

**Constants naming**

For a constant, use an uppercase single letter, word, or words. Separate words 
with underscores to improve readability.

```    
    CONSTANT=4
    MY_CONSTANT=8
    MY_LONG_CONSTANT=1000
```

Comments
--------

Because AEDTLib is about multiple physics domains, many times the person interacting with the code 
does not have the same background as the person who produces it. This is why it is very important 
for this product to produce commented and documented source code. Comments that contradict the code 
are worse than no comments. Always make a priority of keeping comments up-to-date with the code.

Comments should be complete sentences. The first word should be capitalized, unless it is an identifier 
that begins with a lowercase letter. In multi-sentence comments, use two spaces after a sentence-ending 
period, except after the final sentence.

Here are additional guidelinse for using comments:

1. Always try to explain yourself in code.
1. Don't be redundant.
1. Don't add obvious noise.
1. Don't use closing brace comments.
1. Don't comment out code, but rather remove it.
1. Use as explanation of intent.
1. Use to clarify the code.
1. Use to warn of consequences.

**Inline Comments**

Inline comments should be used sparingly.

An inline comment is a comment on the same line as a statement. Inline comments should be separated 
by at least two spaces from the statement. They should start with a # and a single space.

```
    x = 5 # This is an inline comment
```

Inline comments are unnecessary and in fact distracting if they state the obvious. Do not do this:

```
    x = x + 1 # Increment x
```

To provide understanding, use better naming conventions instead of inline comments.

Not recommended:

```
    x = 'John Smith' # Student Name
```

Recommended:

```
    user_name = 'John Smith'
```

**Block Comments**

Block comments generally apply to some (or all) code that follows them and are indented to the same level as this code. 
Each line of a block comment starts with a # and a single space (unless it is indented text inside the comment).

Paragraphs inside a block comment are separated by a line containing a single #. Indent block comments to the same 
level as the code they describe.

```
    for i in range(0, 10):
    print(i, '\n')
```

Documentation strings
---------------------

A docstring is a string literal that occurs as the first statement in a module, function, class, or method definition. 
A docstring becomes the doc special attribute of the object.

Write docstrings for all public modules, functions, classes, and methods. Docstrings are not necessary for non-public 
methods, but you should have a comment that describes what the method does. This comment should appear after the ``def`` line.

To create a docstring, surround the comments with three double quotes on either side. 

For a one-line docstring, keep both 
the starting and ending """ on the same line. For example, """This is a docstring.""". 

For a multiline docstring, put the ending """ on a line by itself: 

```
    def quadratic(a, b, c, x):
    """Solve quadratic equation via the quadratic formula.
    
    A quadratic equation has the following form:
    ax**2 + bx + c = 0
    
    There always two solutions to a quadratic equation: x_1 & x_2.
    
    :param a: a description
    :type a: float
    :param b: b description
    :param c: c description
    :param x: x description
    :return: x1 and x2 description
    
    """
    x_1 = (- b+(b**2-4*a*c)**(1/2)) / (2*a)
    x_2 = (- b-(b**2-4*a*c)**(1/2)) / (2*a)
    
    return x_1, x_2
```

Programming Recommendations
---------------------------

This section provides some of the PEP 8 suggestions for removing ambiguity and preserving consistency.

Don’t compare Boolean values to ``True`` or ``False`` using the equivalence operator:

```
    my_bool = 6 > 5
```

Not recommended:

```
    if my_bool == True:
         return '6 is bigger than 5'
```

Recommended:

```
    if my_bool:
    return '6 is bigger than 5'
```

Use the fact that empty sequences are false in if statements. 

In Python, any empty list, string, or tuple is false.

Not recommended:

```
    my_list = []
    if not len(my_list):
    print('List is empty!')
```

Recommended:

```
    my_list = []
    if not my_list:
    print('List is empty!')
```

In ``if`` statements, use ``is not`` rather than ``not ...``.

Not recommended:

```    
    if not x is None:
    return 'x exists!'
```

Recommended:
 
```    
    if x is not None:
    return 'x exists!'
```
Don’t use ``if x:`` when you mean ``if x is not None:``.

Not Recommended:

```
    if arg:
```

Recommended:

```
    if arg is not None:
```
    
Use ``.startswith()`` and ``.endswith()`` instead of slicing.

Not recommended:

```    
    if word[:3] == 'cat':
    print('The word starts with "cat"')
```

Not recommended:

```
    if file_name[-3:] == 'jpg':
    print('The file is a JPEG')
```

Recommended:

```    
    if word.startswith('cat'):
    print('The word starts with "cat"')
```

Recommended:

```    
    if file_name.endswith('jpg'):
    print('The file is a JPEG')
```

References
----------

- [PEP 8 ](https://www.python.org/dev/peps/pep-0008/)

- [Clean Code - R. C. Martin ](https://www.amazon.com/Robert-Martin-Clean-Code-Collection-ebook/dp/B00666M59G)
