ReadMe
=======

PyAedt is intended to consolidate and extend all existing functionalities around AEDT-based scripting to allow re-use of existing code, sharing of best-practice and  increase collaboration collaboration.
PyAedt is run under [MIT License](LICENSE.md).

This tool has actually been tested on HFSS, Icepak and Maxwell 3D, EDB, Q3D.

Useful Links:
- [PyAedt Documentation](Documentation/index.html)

- [Coding Guidelines](doc/source/Resources/Code_Guidelines.md)

- [Installation Guidelines](Installation.md)

- [PEP 8 ](https://www.python.org/dev/peps/pep-0008/)

- [Clean Code - R. C. Martin ](https://www.amazon.com/Robert-Martin-Clean-Code-Collection-ebook/dp/B00666M59G)

**What is PyAedt**

PyAedt uses an architecture that can be reused for all 3D tools (Maxwell, Q3D, HFSS, Icepak), and in future for all other desktop tools.
    
![Overview](Resources/Items.png)

Its classes and methods structures allows to simplify operation for end-user while reusing as much as possible of the information across the API.
Main advantages:

Automatic initialization of all the AEDT Objects (from desktop to every single objects like editor, boundaries, etc…)
- Error Management
- Variable Management
- Compatibility with Ironpython and CPython
- Compatibility on Windows and Linux (Ironpython only). This requires further intensive tests 
- Simplification of complex API syntax thanks to Data Objects and PEP8 compatibility
- Sharing of new codes across FES team with TFS
- User can reuse most of the code across different solvers
- Docstrings on functions for better understanding and tool usage
- Unit Test of code to increase quality across different AEDT Version

**Usage Workflow**

User has to:
1. Initialize Desktop Class with version of AEDT to be used.
2. initialize application to use within AEDT

**Desktop.py - Connect to Desktop from Python IDE**

- Works inside Electronics Desktop and as a Standalone Application
- Automatically detect if it is Ironpython or CPython and initialize accordingly the Desktop
- Advanced Error Management 

Examples of usage:

- Explicit Desktop Declaration and error management

```
    from pyaedt import Desktop
    from pyaedt import Circuit    
    with Desktop("2020.1", NG=True):
        print("AEDT 2020R1 in Non-Graphicalmode will be launched)
        circuit = Circuit()
        ...
        print("any error here will be catched by Desktop=
        ...
    print("here Desktop is automatically release")
```    

- Implicit Desktop Declaration and error management


```
    from pyaedt import Circuit    
    with Circuit as circuit:
        print("Latest version of Desktop in Graphical mode will be launched")
        ...
        print("any error here will be catched by Desktop")
        ...
    print("here Desktop is automatically release")
```


**Application Classes and Inheritance**

An application class inherits both a Design and an Analysis class

- Example


```
    from pyaedt import Desktop
    from pyaedt import Circuit
    
    with Desktop("2020.1", NG=True):
        AEDT 2020R1 in Non-Graphicalmode will be launched
        circuit = Circuit()
        circuit.save_project("C:/Temp/My_projectname.aedt") # this function is from Design.py
```       


**Variable Class**

Variables can be created by simply assinging properties 
If String contains "$" then it will be stored as Project Variable

- Example

```
    hfss["a"]= "1mm" # local variable
    hfss["$a"]= "1mm" # project variable
```    



