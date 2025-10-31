<!-- -->
<a name="readme-top"></a>
<!--
*** PyAEDT README
-->

[![PyAEDT logo](https://raw.githubusercontent.com/ansys/pyaedt/main/doc/source/_static/logo.png)](https://aedt.docs.pyansys.com)

<p style="text-align: center;">
    <br> English | <a href="README_CN.md">中文</a>
</p>

[![PyAnsys](https://img.shields.io/badge/Py-Ansys-ffc107.svg?logo=data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAIAAACQkWg2AAABDklEQVQ4jWNgoDfg5mD8vE7q/3bpVyskbW0sMRUwofHD7Dh5OBkZGBgW7/3W2tZpa2tLQEOyOzeEsfumlK2tbVpaGj4N6jIs1lpsDAwMJ278sveMY2BgCA0NFRISwqkhyQ1q/Nyd3zg4OBgYGNjZ2ePi4rB5loGBhZnhxTLJ/9ulv26Q4uVk1NXV/f///////69du4Zdg78lx//t0v+3S88rFISInD59GqIH2esIJ8G9O2/XVwhjzpw5EAam1xkkBJn/bJX+v1365hxxuCAfH9+3b9/+////48cPuNehNsS7cDEzMTAwMMzb+Q2u4dOnT2vWrMHu9ZtzxP9vl/69RVpCkBlZ3N7enoDXBwEAAA+YYitOilMVAAAAAElFTkSuQmCC)](https://docs.pyansys.com/)
[![pypi](https://img.shields.io/pypi/v/pyaedt.svg?logo=python&logoColor=white)](https://pypi.org/project/pyaedt/)
[![PyPIact](https://static.pepy.tech/badge/pyaedt/month)](https://www.pepy.tech/projects/pyaedt)
[![PythonVersion](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![GH-CI](https://github.com/ansys/pyaedt/actions/workflows/ci_cd.yml/badge.svg)](https://github.com/ansys/pyaedt/actions/workflows/ci_cd.yml)
[![codecov](https://codecov.io/gh/ansys/pyaedt/branch/main/graph/badge.svg)](https://codecov.io/gh/ansys/pyaedt)
[![MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/blog/license/mit)
[![black](https://img.shields.io/badge/code%20style-black-000000.svg?style=flat)](https://github.com/psf/black)
[![Anaconda](https://anaconda.org/conda-forge/pyaedt/badges/version.svg)](https://anaconda.org/conda-forge/pyaedt)
[![pre-commit](https://results.pre-commit.ci/badge/github/ansys/pyaedt/main.svg)](https://results.pre-commit.ci/latest/github/ansys/pyaedt/main)
[![deep-wiki](https://deepwiki.com/badge.svg)](https://deepwiki.com/ansys/pyaedt)

## What is PyAEDT?

PyAEDT is a Python library that interacts directly with the API for
Ansys Electronics Desktop (AEDT) to make scripting simpler. The architecture
for PyAEDT can be reused for all AEDT 3D products (HFSS, Icepak, Maxwell 3D,
and Q3D Extractor), 2D tools, and Ansys Mechanical inside AEDT. PyAEDT also provides
support for circuit tools like Nexxim and system simulation tools like
Twin Builder. Finally, PyAEDT provides scripting capabilities in Ansys layout
tools like HFSS 3D Layout. The Ansys Electronics Database 
([EDB](https://edb.docs.pyansys.com/version/stable/)) is included
with PyAEDT as a dependency and is recommended for any automated manipulation and 
setup of layout data for PCBs, electronic packages, and integrated circuits. 

The PyAEDT class and method structures
simplify operation while reusing information as much as possible across
the API.

## Install on CPython from PyPI

You can install PyAEDT on CPython 3.8 through 3.12 from PyPI with this command:


```sh
  pip install pyaedt
```

Install PyAEDT with all extra packages (matplotlib, numpy, pandas, pyvista, ...):

```sh
  pip install pyaedt[all]
```

> **Note:**
The [all] installation target includes `fpdf2` for PDF export functionality, which is
under license LGPL v3. For license-sensitive environments, install PyAEDT without [all]
and add dependencies individually.

You can also install PyAEDT from Conda-Forge with this command:

```sh
  conda install -c conda-forge pyaedt
```
PyAEDT remains compatible with IronPython and can be still used in the AEDT Framework.

## PyAEDT compatibility requirements

PyAEDT has different compatibility requirements based on its version. Below is an overview of the compatibility matrix between PyAEDT, Python versions, and AEDT releases:

- PyAEDT Version ≤ 0.8.11:
  - Python Compatibility:
    - Compatible with IronPython (Python 2.7).
    - Compatible with Python 3.7 and versions up to Python 3.11.
  - AEDT Compatibility:
    - All tests were conducted using AEDT 2024 R1.
-  0.9.0 <= PyAEDT Version < 0.18.0:
  - Python Compatibility:
    - Dropped support for python 3.7 and below.
    - Compatible with Python 3.8 and versions up to Python 3.12.
  - AEDT Compatibility:
    - Version 0.9.x has been tested using AEDT 2024 R1.
    - From versions 0.10.0 to 0.13.3, all tests have been performed with AEDT 2024 R2.
    - Starting from version 0.14.0, all tests are performed with AEDT 2025 R1.
- PyAEDT Version ≥ 0.18.0:
  - Python Compatibility:
    - Dropped support for Python 3.8 and 3.9.
    - Compatible with Python 3.10 and versions up to Python 3.13.
  - AEDT Compatibility:
    - All tests were conducted using AEDT 2025 R1.


## About PyAnsys

PyAEDT is part of the larger [PyAnsys](https://docs.pyansys.com "PyAnsys") effort to facilitate the use of Ansys technologies directly from Python.

PyAEDT is intended to consolidate and extend all existing
functionalities around scripting for AEDT to allow reuse of existing code,
sharing of best practices, and increased collaboration.

## About AEDT

[AEDT](https://www.ansys.com/products/electronics) is a platform that enables true
electronics system design. AEDT provides access to the Ansys gold-standard
electro-magnetics simulation solutions, such as Ansys HFSS, Ansys Maxwell,
Ansys Q3D Extractor, Ansys SIwave, and Ansys Icepak using electrical CAD (ECAD) and
Mechanical CAD (MCAD) workflows.

In addition, AEDT includes direct links to the complete Ansys portfolio of thermal, fluid,
and mechanical solvers for comprehensive multiphysics analysis.
Tight integration among these solutions provides unprecedented ease of use for setup and
faster resolution of complex simulations for design and optimization.

<p align="center">
  <img width="100%" src="https://images.ansys.com/is/image/ansys/ansys-electronics-technology-collage?wid=941&op_usm=0.9,1.0,20,0&fit=constrain,0" title="AEDT Applications" herf="https://www.ansys.com/products/electronics"
  />
</p>

`PyAEDT` is licensed under the [MIT License](https://github.com/ansys/pyaedt/blob/main/LICENSE)

PyAEDT includes functionality for interacting with the following AEDT tools and Ansys products:

  - HFSS and HFSS 3D Layout
  - Icepak
  - Maxwell 2D, Maxwell 3D, and RMXprt
  - 2D Extractor and Q3D Extractor
  - Mechanical
  - Nexxim
  - EDB
  - Twin Builder
  - EMIT

## Documentation and issues

Documentation for the latest stable release of PyAEDT is hosted at
[PyAEDT documentation](https://aedt.docs.pyansys.com/version/stable/).

In the upper right corner of the documentation's title bar, there is an option
for switching from viewing the documentation for the latest stable release
to viewing the documentation for the development version or previously
released versions.

You can also view or download PyAEDT cheat sheets, which are one-page references
providing syntax rules and commands for using the PyAEDT API and PyEDB API:

- [View](https://cheatsheets.docs.pyansys.com/pyaedt_API_cheat_sheet.png) or
  [download](https://cheatsheets.docs.pyansys.com/pyaedt_API_cheat_sheet.pdf) the
  PyAEDT API cheat sheet.

- [View](https://cheatsheets.docs.pyansys.com/pyedb_API_cheat_sheet.png) or
  [download](https://cheatsheets.docs.pyansys.com/pyedb_API_cheat_sheet.pdf) the
  PyEDB API cheat sheet.


On the [PyAEDT Issues](https://github.com/ansys/PyAEDT/issues) page, you can
create issues to report bugs and request new features. On the
[PyAEDT Discussions](https://github.com/ansys/pyaedt/discussions) page or the
[Discussions](https://discuss.ansys.com/) page on the Ansys Developer portal,
you can post questions, share ideas, and get community feedback.

To reach the project support team, email [pyansys.core@ansys.com](mailto:pyansys.core@ansys.com).

## Dependencies

To run PyAEDT, you must have a local licenced copy of AEDT.
PyAEDT supports AEDT versions 2022 R1 or newer.

## Contributing

For comprehensive information on contributing to the PyAnsys project, see the [PyAnsys developer's guide](https://dev.docs.pyansys.com). 


Note that PyAEDT uses semantic naming for pull requests (PR). This convention 
greatly simplifies the review process by providing meaningful
information in the PR title. The
following 
[prefixes](https://github.com/ansys/actions/blob/main/commit-style/action.yml)
should be used for pull request name:

- "BUILD"
- "CHORE"
- "CI"
- "DOCS"
- "FEAT"
- "FIX"
- "PERF"
- "REFACTOR"
- "REVERT"
- "STYLE"
- "TEST"


## Student version

PyAEDT supports AEDT Student versions 2022 R1 and later. For more information, see the
[Ansys Electronics Desktop Student - Free Software Download](https://www.ansys.com/academic/students/ansys-electronics-desktop-student)
page on the Ansys website.

## Why PyAEDT?

A quick and easy approach for automating a simple operation in the AEDT UI is to record and reuse a script. However, disadvantages of this approach are:

  - Recorded code is dirty and difficult to read and understand.
  - Recorded scripts are difficult to reuse and adapt.
  - Complex coding is required by many global users of AEDT.

The main advantages of PyAEDT are:

  - Automatic initialization of all AEDT objects, such as desktop objects like the editor and boundaries
  - Error management
  - Log management
  - Variable management
  - Compatibility with IronPython and CPython
  - Simplification of complex API syntax using data objects while maintaining PEP8 compliance.
  - Code reusability across different solvers
  - Clear documentation on functions and API
  - Unit tests of code to increase quality across different AEDT versions

## Example workflow

 1. Initialize the ``Desktop`` class with the version of AEDT to use.
 2. Initialize the application to use within AEDT.

## Connect to AEDT from Python IDE

PyAEDT works both inside AEDT and as a standalone application. This Python library
automatically detects whether it is running in an IronPython or CPython environment
and initializes AEDT accordingly. PyAEDT also provides advanced error management.
Usage examples follow.

## Explicit AEDT declaration and error management

``` python
    # Launch AEDT 2022 R2 in non-graphical mode

    from ansys.aedt.core import Desktop, Circuit
    with Desktop(specified_version="2022.2",
                 non_graphical=False, new_desktop_session=True,
                 close_on_exit=True, student_version=False):
        circuit = Circuit()
        ...
        # Any error here will be caught by Desktop.
        ...

    # Desktop is automatically released here.
```

## Implicit AEDT declaration and error management

``` python
    # Launch the latest installed version of AEDT in graphical mode

    from ansys.aedt.core import Circuit
    with Circuit(specified_version="2022.2",
                 non_graphical=False) as circuit:
        ...
        # Any error here will be caught by Desktop.
        ...

    # Desktop is automatically released here.
```

## Remote application call

You can make a remote application call on a CPython server
or any Windows client machine.

On a CPython Server:

``` python
    # Launch PyAEDT remote server on CPython

    from ansys.aedt.core.common_rpc import pyaedt_service_manager
    pyaedt_service_manager()
```

On any Windows client machine:

``` python
    from ansys.aedt.core.common_rpc import create_session
    cl1 = create_session("server_name")
    cl1.aedt(port=50000, non_graphical=False)
    hfss = Hfss(machine="server_name", port=50000)
    # your code here
```

## Variables

``` python
    from ansys.aedt.core.HFSS import HFSS
    with HFSS as hfss:
         hfss["dim"] = "1mm"   # design variable
         hfss["$dim"] = "1mm"  # project variable
```

## Modeler

``` python
    # Create a box, assign variables, and assign materials.

    from ansys.aedt.core.hfss import Hfss
    with Hfss as hfss:
         hfss.modeler.create_box([0, 0, 0], [10, "dim", 10],
                                 "mybox", "aluminum")
```

## License

PyAEDT is licensed under the MIT license.

PyAEDT provides an optional PDF export feature via the class `AnsysReport`.
It requires the [fpdf2](https://github.com/py-pdf/fpdf2)
library, which is licensed under the
[GNU Lesser General Public License v3.0 (LGPLv3)](https://www.gnu.org/licenses/lgpl-3.0.en.html#license-text).

PyAEDT makes no commercial claim over Ansys whatsoever. This library extends the
functionality of AEDT by adding a Python interface to AEDT without changing the
core behavior or license of the original software. The use of PyAEDT requires a
legally licensed local copy of AEDT.

To get a copy of AEDT, see the [Ansys Electronics](https://www.ansys.com/products/electronics)
page on the Ansys website.

<p style="text-align: right;"> <a href="#readme-top">back to top</a> </p>

## Indices and tables

-  [Index](https://aedt.docs.pyansys.com/version/stable/genindex.html)
-  [Module Index](https://aedt.docs.pyansys.com/version/stable/py-modindex.html)
-  [Search Page](https://aedt.docs.pyansys.com/version/stable/search.html)
