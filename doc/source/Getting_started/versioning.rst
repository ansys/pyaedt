.. _versions_and_interfaces:

=======================
Versions and interfaces
=======================

The PyAEDT project attempts to maintain compatibility with legacy
versions of AEDT while allowing for support of faster and better
interfaces with the latest versions of AEDT.

There are two interfaces PyAEDT can use to connect to AEDT.
You can see a table with the AEDT version and the supported interfaces
in `Table of supported versions <table_versions_>`_


gRPC interface
==============

This is the default and preferred interface to connect to AEDT.
Ansys 2022 R2 and later support the latest gRPC interface, allowing
for remote management of MAPDL with rapid streaming of mesh, results,
and files from the MAPDL service.


Legacy interfaces
=================

COM interface
--------------

AnsysEM supports the legacy COM interface, enabled with the settings option.

This interface works only on Windows and uses .NET COM objects.


.. code:: python


    from pyaedt import settings

    settings.use_grpc_api = False



Compatibility between AEDT and interfaces
=========================================

The following table shows the supported versions of Ansys EDT and the recommended interface for each one of them in PyAEDT.


**Table of supported versions**

.. _table_versions:

+---------------------------+------------------------+-----------------------------------------------+
| Ansys Version             | Recommended interface  | Support                                       |
|                           |                        +-----------------------+-----------------------+
|                           |                        | gRPC                  | COM                   |
+===========================+========================+=======================+=======================+
| AnsysEM 2024 R1           | gRPC                   |        YES            |        NO*            |
+---------------------------+------------------------+-----------------------+-----------------------+
| AnsysEM 2023 R2           | gRPC                   |        YES            |        YES*           |
+---------------------------+------------------------+-----------------------+-----------------------+
| AnsysEM 2023 R1           | gRPC                   |        YES            |        YES*           |
+---------------------------+------------------------+-----------------------+-----------------------+
| AnsysEM 2022 R2           | gRPC                   |        YES*           |        YES            |
+---------------------------+------------------------+-----------------------+-----------------------+
| AnsysEM 2022 R1           | gRPC                   |        NO             |        YES            |
+---------------------------+------------------------+-----------------------+-----------------------+
| AnsysEM 2021 R2           | gRPC                   |        NO            |         YES            |
+---------------------------+------------------------+-----------------------+-----------------------+

Where:

* YES means that the interface is supported and recommended.
* YES* means that the interface is supported, but not recommended. Their support might be dropped in the future.
* NO means that the interface is not supported.
* NO* means that the interface is still supported but it is deprecated.
