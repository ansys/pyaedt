# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 - 2026 ANSYS, Inc. and/or its affiliates.
# SPDX-License-Identifier: MIT
#
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.


from ansys.aedt.core.generic.settings import settings
from ansys.aedt.core.internal.aedt_versions import aedt_versions

log = settings.logger


# lazy imports
def Edb(
    edbpath=None,
    cellname=None,
    isreadonly=False,
    version=None,
    isaedtowned=False,
    oproject=None,
    student_version=False,
    use_ppe=False,
    technology_file=None,
):
    """Provides the EDB application interface.

    This module inherits all objects that belong to EDB.

    Parameters
    ----------
    edbpath : str, optional
        Full path to the ``aedb`` folder. The variable can also contain
        the path to a layout to import. Allowed formats are BRD,
        XML (IPC2581), GDS, and DXF. The default is ``None``.
        For GDS import, the Ansys control file (also XML) should have the same
        name as the GDS file. Only the file extension differs.
    cellname : str, optional
        Name of the cell to select. The default is ``None``.
    isreadonly : bool, optional
        Whether to open EBD in read-only mode when it is
        owned by HFSS 3D Layout. The default is ``False``.
    version : str, optional
        Version of EDB to use. The default is ``"2021.2"``.
    isaedtowned : bool, optional
        Whether to launch EDB from HFSS 3D Layout. The
        default is ``False``.
    oproject : optional
        Reference to the AEDT project object.
    student_version : bool, optional
        Whether to open the AEDT student version. The default is ``False.``
    technology_file : str, optional
        Full path to technology file to be converted to xml before importing or xml. Supported by GDS format only.

    Returns
    -------
    :class:`pyedb.dotnet.edb.Edb`, :class:`pyedb.grpc.edb.Edb`

    Examples
    --------
    Create an ``Edb`` object and a new EDB cell.

    >>> from pyedb import Edb
    >>> app = Edb()

    Add a new variable named "s1" to the ``Edb`` instance.

    >>> app["s1"] = "0.25 mm"
    >>> app["s1"].tofloat
    >>> 0.00025
    >>> app["s1"].tostring
    >>> "0.25mm"

    or add a new parameter with description:

    >>> app["s2"] = ["20um", "Spacing between traces"]
    >>> app["s2"].value
    >>> 1.9999999999999998e-05
    >>> app["s2"].description
    >>> "Spacing between traces"


    Create an ``Edb`` object and open the specified project.

    >>> app = Edb("myfile.aedb")

    Create an ``Edb`` object from GDS and control files.
    The XML control file resides in the same directory as the GDS file: (myfile.xml).

    >>> app = Edb("/path/to/file/myfile.gds")

    """
    from pyedb import Edb

    if not settings.aedt_version:  # pragma: no cover
        settings.aedt_version = aedt_versions.current_version

    if settings.pyedb_use_grpc is None and settings.aedt_version > "2025.2":  # pragma: no cover
        settings.logger.info("No EDB gRPC setting provided. Enabling gRPC for EDB.")
        settings.pyedb_use_grpc = True

    use_grpc = True if settings.pyedb_use_grpc and settings.aedt_version > "2025.2" else False  # pragma: no cover
    grpc_enabled = "Grpc enabled" if use_grpc else "Dotnet enabled"  # pragma: no cover
    settings.logger.info(f"Loading EDB with {grpc_enabled}.")

    return Edb(
        edbpath=str(edbpath),
        cellname=cellname,
        isreadonly=isreadonly,
        version=version,
        isaedtowned=isaedtowned,
        oproject=oproject,
        student_version=student_version,
        use_ppe=use_ppe,
        technology_file=technology_file,
        grpc=use_grpc,
    )


def Siwave(
    specified_version=None,
):
    """Siwave Class."""
    from pyedb.siwave import Siwave as app

    return app(
        specified_version=specified_version,
    )
