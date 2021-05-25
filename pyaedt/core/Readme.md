ReadMe
=======

AEDTLIb is intended to consolidate and extend all existing functionalities around AEDT-based scripting to allow re-use of existing code, sharing of best-practice and  increase collaboration collaboration.
AEDTLib is run under [MIT License](LICENSE.md).

This tool has actually been tested on HFSS, Icepak and Maxwell 3D, EDB, Q3D.

Useful Links:
- [AEDTLib Documentation](Documentation/index.html)

- [Coding Guidelines](../../Doc/Sphinx_AEDTLib/Resources/Code_Guidelines.md)

- [Installation Guidelines](Installation.md)

- [PEP 8 ](https://www.python.org/dev/peps/pep-0008/)

- [Clean Code - R. C. Martin ](https://www.amazon.com/Robert-Martin-Clean-Code-Collection-ebook/dp/B00666M59G)


**Getting Started Examples:**

- [JupyterLab HFSS Full Example](../examples/HFSS_Icepak_fullEXample.ipynb): It is a Jupyter lab file that shows how user can launch AEDTLib from Jupyter lab. 
It requires Juputer Lab to be installed on your machine. It can be launched with the following command: 

    *"jupyter lab pathtoAEDTLibRoot/Documentation/Examples/HFSS_Icepak_fullEXample.ipynb"* and jupyter server will be launched and the notebook will be loaded

- [JupyterLab PostProcessing Example](../examples/far_field_test.ipynb): It is a Jupyter lab file that shows how user can use matplotly to postprocess data from AEDT in Non-Graphical mode. 
It requires Juputer Lab to be installed on your machine. It can be launched with the following command: 

    *"jupyter lab pathtoAEDTLibRoot/Documentation/Examples/far_field_test.ipynb"* and jupyter server will be launched and the notebook will be loaded

- [HFSS Example](../examples/01_HFSS_Icepak_FullProject.py): Includes HFSS and Icepak Analysis

- [Maxwell 3D Example](../examples/02_Maxwell_Icepak_App_Example.py): It includes Maxwell and Icepak Analysis

- [Solution Setup Example](../examples/13_Solution_Setup_Example.py): It includes example to create automatically a Simulation Setup in different tools

- [Icepak Example](../examples/AEDTLib/Icepak_Example.py): It includes example to create mesh regions and edit it

- [Q3D Example](../examples/03_Q3D_Example.py)Q3D_Example.py: It includes an example of creating Q3D Project

- [EDB Example](../examples/08A_EDB_From3DLayout_Example.py): It includes an example of using Edb API from AEDTLib within 3DLayout (read ONLY)

- [EDB Standalone Example](../examples/08B_EDB_Standalone_example.py): It includes an example of using Edb API ouside aedt (read/write)

- [HFSS 3D Layout Example](../examples/08C_HFSS_3DLayout_example.py): It includes an example of using HFSS3DLayout

- [Dipole Example](../examples/05_Dipole_Example.py): It includes an example of using HFSS 

- [Circuit Example](../examples/06_Circuit_Example.py): A Simple RLC Example

- [Netlist Example](../examples/09_Import_Netlist.py): A Simple HSPICE Netlist Import Example

- [Geometry Creation Example](../examples/10_Geometry_Creation_Package.py): A Simple Package Creation Example

- [Ansys Report Example](../examples/11_Ansys_Report.py): An example on how to create pdf reports

- [HeatSink Example](../examples/11_Ansys_Report.py): An example on how to create a fully parametrized HeatSink

Why the need a structured API

Recording and reusing script is a very fast approach for simple operations in Desktop UI. But:
1. Code recorded is very dirty
2. Code reusability is very low
3. Complex Coding are demanded to few people across the Globe

**What is AEDTLib**

AEDTLib uses an architecture that can be reused for all 3D tools (Maxwell, Q3D, HFSS, Icepak), and in future for all other desktop tools.
    
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
    from pyaedt.core.Destkop import Desktop
    from pyaedt.core.Circuit import Circuit    
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
    from pyaedt.core.Circuit import Circuit    
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
    from pyaedt.core.Destkop import Desktop
    from pyaedt.core.Circuit import Circuit
    
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



