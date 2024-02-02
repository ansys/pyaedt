Getting started
===============

.. grid:: 2

   .. grid-item-card:: About PyAnsys and AEDT
            :link: About
            :link-type: doc
            :margin: 2 2 0 0
            
            Learn more about PyAnsys and AEDT.

   .. grid-item-card:: Installation
            :link: Installation
            :link-type: doc
            :margin: 2 2 0 0

            Learn how to install PyAEDT from PyPi or Conda.

   .. grid-item-card:: User guide
            :link: ../User_guide/index
            :link-type: doc
            :margin: 2 2 0 0

            This section provides in-depth information on PyAEDT key concepts.

   .. grid-item-card:: Client-Server
            :link: ClientServer
            :link-type: doc
            :margin: 2 2 0 0

            Launch PyAEDT on a client machine and control Electronics Desktop
            on a remote server.

   .. grid-item-card:: Versions and interfaces
            :link: versioning
            :link-type: doc
            :margin: 2 2 0 0

            Discover the compatibility between PyAEDT and Ansys AEDT versions.

   .. grid-item-card:: Troubleshooting
            :link: Troubleshooting
            :link-type: doc
            :margin: 2 2 0 0

            Any questions? Refer to Q&A before submitting an issue.


What is PyAEDT?
---------------
PyAEDT is a Python library that interacts directly with the API for
Ansys Electronics Desktop (AEDT) to make scripting simpler. The architecture
for PyAEDT can be reused for all AEDT 3D products (HFSS, Icepak, Maxwell 3D,
and Q3D Extractor), 2D tools, and Ansys Mechanical. PyAEDT also provides
support for Circuit tools like Nexxim and system simulation tools like
Twin Builder. Finally, PyAEDT provides scripting capabilities in Ansys layout
tools like HFSS 3D Layout and EDB. The PyAEDT class and method structures
simplify operation while reusing information as much as possible across
the API.

To run PyAEDT, you must have a licensed copy of Ansys Electronics
Desktop (AEDT) installed.

The Ansys Electronics Desktop (AEDT) is a platform that enables true electronics system design.
`AEDT <https://www.ansys.com/products/electronics>`_ provides access to the Ansys gold-standard
electro-magnetics simulation solutions such as Ansys HFSS,
Ansys Maxwell, Ansys Q3D Extractor, Ansys Siwave, and Ansys Icepak using electrical CAD (ECAD) and
Mechanical CAD (MCAD) workflows.
In addition, it includes direct links to the complete Ansys portfolio of thermal, fluid,
and Mechanical solvers for comprehensive multiphysics analysis.
Tight integration among these solutions provides unprecedented ease of use for setup and
faster resolution of complex simulations for design and optimization.

.. image:: ../Resources/aedt_3.png
  :width: 800
  :alt: AEDT Applications
  :target: https://www.ansys.com/products/electronics

For more information, see `Ansys Electronics <https://www.ansys.com/products/electronics>`_
on the Ansys website.

PyAEDT cheat sheets
-------------------

PyAEDT cheat sheets introduce the basics that you need to use PyAEDT.
These one-page references providing syntax rules and commands
for using PyAEDT API and EDB API:

**PyAEDT cheat sheet:** `PyAEDT API <https://cheatsheets.docs.pyansys.com/pyaedt_API_cheat_sheet.pdf>`_

**EDB cheat sheet:** `EDB API <https://cheatsheets.docs.pyansys.com/pyedb_API_cheat_sheet.pdf>`_


Get help
--------

**Development issues:** For PyAEDT development-related matters, see the
`PyAEDT Issues <https://github.com/ansys/PyAEDT/issues>`_ page.
You can create issues to report bugs and request new features.

**User questions:** The best way to get help is to post your question on the `PyAEDT Discussions
<https://github.com/ansys/pyaedt/discussions>`_ page or the `Discussions <https://discuss.ansys.com/>`_
page on the Ansys Developer portal. You can post questions, share ideas, and get community feedback.


License
-------
PyAEDT is licensed under the MIT license.

PyAEDT makes no commercial claim over Ansys whatsoever. This library extends the
functionality of AEDT by adding a Python interface to AEDT without changing the
core behavior or license of the original software. The use of PyAEDT requires a
legally licensed local copy of AEDT.

To get a copy of AEDT, see the `Ansys Electronics <https://www.ansys.com/products/electronics>`_
page on the Ansys website.



.. toctree::
   :hidden:
   :maxdepth: 2

   Installation
   Troubleshooting
   ../User_guide/index
   ClientServer
   versioning
   Contributing
   About

