Code Guidelines
========================================================

Introduction

This document is build by developers to help the developers to :

1. Prevent against common programming errors
1. Limit the program complexity
1. Provide an easily readable, understandable and maintainable
1. Establish a consistent style
1. Establish an objective basis of code review

The recommendations inside this documents can be divided in two parts, those concerning the style and which guarantee the homogeneity within the program, and those which guarantee the stability of the code. 

All of them are important and must be follow by all contributors.

Cross-cutting coding languages rules
- Windows Registry: Reading the registry

Never Do That (really Dangerous if the code could be used in different OS)

```    
    ...
    self.sDesktopinstallDirectory = Registry.GetValue("HKEY_LOCAL_MACHINE\Software\Ansoft\ElectronicsDesktop\{}\Desktop".format(self.sDesktopVersion), "InstallationDirectory", '')
    ...
```

// Not recommended

```
    EMInstall = (string)Registry.GetValue(string.Format(@"HKEY_LOCAL_MACHINE\SOFTWARE\Ansoft\ElectronicsDesktop{0}\Desktop", AnsysEmInstall.DesktopVersion), "InstallationDirectory", null);
```

Writing on the registry
Hard coded values
In order to provide some values in the code, it is recommended to use the Configuration Service.


Duplicated code
To be documented more

**File/Folder management service**

To be documented more

**Nested blocks**

It is often a bad idea to nest block structures too deeply (conditional blocks, loops, ...).

**Conditional blocks**

The maximum depth combination recommended is 4. 

If you think you need more for the algorithm, one must create small function reusable and unit testable.

**Loops**
There's nothing inherently wrong or necessarily even bad about nested loops.

However, to avoid certain pitfalls, it is recommended not more than 2 levels of loops. In some case one can rely on coding mechanism to avoid nested loop. Otherwise, it is recommended to create small functions.


**Logging errors**

AEDTLib automatically has an internal logging tool named messenger, as well as log file automatically generated in project folder.
Developer can decide to use both like in example below.

```
    self.messenger.add_error_message("This is an error message")
    self.messenger.add_warning_message("This is a warning message")
    self.messenger.add_info_message("This is an info message")

``` 

the above message will be plot in log file and in AEDT Message windows
if message has to be put on log file only then user has to use
```
    self.logger.error("This is an error message")
    self.messenger.warning("This is a warning message")
    self.messenger.info("This is an info message")

``` 

**Exceptions handling**

AEDTLib uses a specific decorator to handle exceptions caused by methods and by AEDT API.
the decorator is @aedt_exception_handler and can be used like in following example

```
    @aedt_exception_handler
    def my_method(self, var):
        pass
``` 
Every methods may return a value or True in case of success and False in case an exceptions in rised.
When an error occurs the handler returns info about the error itself both in log file and in console. An example of the error is the following:

```
    ---------------------------------------------------------------------------------------
    AEDTLib Error on Method create_box:  General or AEDT Error. Please Check again
    Arguments Provided: 
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

The exception handler decorator makes AEDTLib Fault Tolerant to errors that can happear in any method.



Python coding guidelines
=========================

Code structure
--------------------

**Imports**

Imports must always be put at the top of the file, just after any module comments and docstrings, and before module globals and constants.

Never Do That(really Dangerous)

```
    def compute_logBase8(x):
    import math
    return math.log(8, x)
```

Recommended

```
    import math

    def compute_logBase8(x):
    return math.log(8, x)
```

For a better readability, it is recommended to group the imports following the order below:

1. Standard library
2. Related third party imports
3. Local application/library specific imports

Not recommended

```
    from System import Uri
    import sys
    import subprocess
    from MyPackage import MyModule
    import math

    def compute_logBase8(x):
    return math.log(8, x)
```

Recommended

```
    import sys
    import subprocess
    import math
    from System import Uri
    from MyPackage import MyModule
    
    def compute_logBase8(x):
    return math.log(8, x)
```

It is recommended to put imports in separate line unless they are related to modules from the same package.

Not recommended

```    
    import sys, math
    from MyPackage import MyModule1
    from MyPackage import MyModule2
    
    def compute_logBase8(x):
    return math.log(8, x)
```

Recommended
 
```    
    import sys
    import math
    from MyPackage import MyModule1, MyModule2
    
    def compute_logBase8(x):
    return math.log(8, x)
```

In most cases, it is recommended to avoid WildCard import. 

It can bring confusion on which names are present in the namespaces.

Not recommended
    from MyPackage.MyModule import *

Recommended
    from MyPackage.MyModule import MyClass

**Indentation**

Proper and consistent indentation is important in producing easy to read and maintainable code. In python, use 4 spaces per indentation level and avoid tabs. Indentation should be used to:

- Emphasize the body of a control statement such as a loop or a select statement.
- Emphasize the body of a conditional statement.
- Emphasize a new scope block.
- Blank lines / Wrapping lines
- Put two blank lines before and after all function and class definition.

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

**Maximum line length**

It is considered good practice to keep the lengths of source code lines at or below 79 characters and 72 for the docstrings and comments. Lines longer than this may not be displayed properly on some terminals and tools.

**Naming conventions**

The naming of classes, methods, functions, constants, etc. are very important for producing a easy maintainable code. One must never overlook this aspect. Regardless the programming language, a developer must follow these global rules to choose the right name:

1. Choose descriptive and unambiguous names.
1. Make meaningful distinction.
1. Use pronounceable names.
1. Use searchable names.
1. Replace magic numbers with named constants.
1. Avoid encodings. Don't append prefixes or type information.


**Names to avoid**

Never use the characters 'l' (lowercase letter el), 'O' (uppercase letter oh), or 'I' (uppercase letter eye) as single character variable names. In some fonts, these characters are indistinguishable from the numerals one and zero.

**Package and module naming**

To create a module, use a short, lowercase word or words to name it. Separate words with underscores to improve readability.

```
    module.py, my_module.py
```

For a package use a short, lowercase word or words. Do not separate words with underscores.

```
    package, mypackage
```

**Class naming**

To name a class use the CapWords convention. it means one must start each word with a capital letter. Do not separate words with underscores. This style is also called camel case.

Not recommended

```
    class myclass():
    def init(self): # Our ctor method
    
    class my_class():
    def init(self): # Our ctor method
```

Recommended

```
    class MyClass():
    def init(self): # Our ctor method
```

**Function and method naming**

For a method name, use a lowercase word or words. Separate words with underscores to improve readability.

```
    class MyClass():
    def init(self): # ctor()
    
    def my_class_method():
    my_function
```

**Variable naming**

Use a lowercase single letter, word, or words to name a variable. Separate words with underscores to improve readability.

```
    my_variable=5
```

**Constants naming**
For constant, use an up
percase single letter, word, or words. Separate words with underscores to improve readability.

```    
    CONSTANT=4
    MY_CONSTANT=8
    MY_LONG_CONSTANT=1000
```

**Comments**

Since AEDTLib is about multiples physics domains, many times the one who interact with the code has not the same background that the one who produces it. That is why it is very important for this program to produce a commented and documented source code. Comments that contradict the code are worse than no comments. Always make a priority of keeping the comments up-to-date when the code changes! Regardless the coding languages the following recommendations are always correct:

Always try to explain yourself in code.
1. Don't be redundant.
1. Don't add obvious noise.
1. Don't use closing brace comments.
1. Don't comment out code. Just remove.
1. Use as explanation of intent.
1. Use as clarification of code.
1. Use as warning of consequences.
1. Comments should be complete sentences. The first word should be capitalized, unless it is an identifier that begins with a lower case letter. Then, one should use two spaces after a sentence-ending period in multi- sentence comments, except after the final sentence.

**Inline comments**

Inline comments should be used sparingly.

An inline comment is a comment on the same line as a statement. Inline comments should be separated by at least two spaces from the statement. They should start with a # and a single space.

```
    x = 5 # This is an inline comment
```

Inline comments are unnecessary and in fact distracting if they state the obvious. Don't do this:

```
    x = x + 1 # Increment x
```

Use better naming conventions instead of inline comments to give the meaning.

To avoid

```
    x = 'John Smith' # Student Name
```

To do

```
    user_name = 'John Smith'
```
    
**Documentation strings**

A docstring is a string literal that occurs as the first statement in a module, function, class, or method definition. Such a docstring becomes the doc special attribute of that object.

Write docstrings for all public modules, functions, classes, and methods. Docstrings are not necessary for non-public methods, but you should have a comment that describes what the method does. This comment should appear after the def line.

To create a docstrings surround the comments with three double quotes on either side, as in """This is a docstring""". For a multiline docstring put the """ that ends on a line by itself and for one-line docstrings, keep the """ on the same line

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

**Block comments**

Block comments generally apply to some (or all) code that follows them, and are indented to the same level as that code. Each line of a block comment starts with a # and a single space (unless it is indented text inside the comment).

Paragraphs inside a block comment are separated by a line containing a single #. Indent block comments to the same level as the code they describe.

```
    for i in range(0, 10):
    print(i, '\n')
```

**Programming Recommendations**

In this section, you’ll see some of the suggestions PEP 8 provides to remove that ambiguity and preserve consistency.

Don’t compare boolean values to True or False using the equivalence operator.

```
    my_bool = 6 > 5
```

Not recommended

```
    if my_bool == True:
         return '6 is bigger than 5'
```

Recommended

```
    if my_bool:
    return '6 is bigger than 5'
```

Use the fact that empty sequences are falsy in if statements. 
In Python any empty list, string, or tuple is falsy.

Not recommended

```
    my_list = []
    if not len(my_list):
    print('List is empty!')
```

Recommended

```
    my_list = []
    if not my_list:
    print('List is empty!')
```

Use is not rather than not ... is in if statements.

Recommended
 
```    
    if x is not None:
    return 'x exists!'
```

Not recommended

```    
    if not x is None:
    return 'x exists!'
```

Don’t use if x: when you mean if x is not None:.

Not Recommended

```
    if arg:
```

Recommended

```
    if arg is not None:
```
    
Use .startswith() and .endswith() instead of slicing.

Not recommended

```    
    if word[:3] == 'cat':
    print('The word starts with "cat"')
```

Not recommended

```
    if file_name[-3:] == 'jpg':
    print('The file is a JPEG')
```

Recommended

```    
    if word.startswith('cat'):
    print('The word starts with "cat"')
```

Recommended

```    
    if file_name.endswith('jpg'):
    print('The file is a JPEG')
```

References

- [PEP 8 ](https://www.python.org/dev/peps/pep-0008/)

- [Clean Code - R. C. Martin ](https://www.amazon.com/Robert-Martin-Clean-Code-Collection-ebook/dp/B00666M59G)
