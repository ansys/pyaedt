PyAEDT
======

PyAedt consolidates and extends all AEDT-based scripting functionalities to allow reuse of existing code, sharing of best practices, and increased collaboration.
PyAedt runs under the [MIT License](LICENSE.md).

This tool has been tested on HFSS, Icepak, and Maxwell 3D, EDB, and Q3D.

Useful Links:
- [PyAedt Documentation](Documentation/index.html)

- [Coding Guidelines](doc/source/Resources/Code_Guidelines.md)

- [Installation Guidelines](Installation.md)

- [PEP 8 ](https://www.python.org/dev/peps/pep-0008/)

- [Clean Code - R. C. Martin ](https://www.amazon.com/Robert-Martin-Clean-Code-Collection-ebook/dp/B00666M59G)

**What is PyAedt?**

PyAedt uses an architecture that can be reused for all 3D tools (Maxwell, Q3D, HFSS, and Icepak). In the future, this architecture will be used for all other desktop tools.
    
![Overview](Resources/Items.png)

PyAEDT class and method structures simplify operation for end users while reusing as much information as possible across the API.

**Main Advantages**

- Automatic initialization of all AEDT objects (from the desktop to every single object like the editor, boundaries, and so on)
- Error management
- Variable management
- Compatibility with Ironpython and CPython
- Compatibility with Windows and Linux (IronPython only, which requires further testing)
- Simplification of complex API syntax using data objects and PEP8 compatibility
- Reuse of most code across different solvers
- Docstrings on functions for better understanding and tool usage
- Unit tests of code to increase quality across different AEDT versions

**Usage Workflow**

You must:
1. Initialize the ``Desktop`` class with the version of AEDT to use.
2. Initialize the application to use within AEDT.

**Desktop.py - Connect to Desktop from Python IDE**

- Works inside Electronics Desktop and as a standalone application
- Detects automatically if it is Ironpython or CPython and initializes the desktop according
- Provides advanced error management 

Examples of usage:

- Explicit Desktop declaration and error management

```
    from pyaedt import Desktop
    from pyaedt import Circuit    
    with Desktop("2020.1", NG=True):
        print("AEDT 2020R1 in Non-Graphical mode will be launched.")
        circuit = Circuit()
        ...
        print("Any error here will be caught by Desktop."
        ...
    print("Here Desktop is automatically released.")
```    

- Implicit Desktop declaration and error management


```
    from pyaedt import Circuit    
    with Circuit as circuit:
        print("Latest version of Desktop in Graphical mode will be launched.")
        ...
        print("Any error here will be caught by Desktop.")
        ...
    print("Here Desktop is automatically released.")
```


**Application Classes and Inheritance**

An ``Application`` class inherits both a ``Design`` class and an ``Analysis`` class.

- Example


```
    from pyaedt import Desktop
    from pyaedt import Circuit
    
    with Desktop("2020.1", NG=True):
        AEDT 2020R1 in Non-Graphical mode will be launched.
        circuit = Circuit()
        circuit.save_project("C:/Temp/My_projectname.aedt") # this function is from Design.py
```       


**Variable Class**

Variables can be created by simply assinging properties. 
If the string contains "$", it is stored as a project variable.

- Example

```
    hfss["a"]= "1mm" # local variable
    hfss["$a"]= "1mm" # project variable
```    
