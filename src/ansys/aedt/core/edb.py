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

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING
from typing import Any

from ansys.aedt.core.generic.settings import settings

if TYPE_CHECKING:
    from pyedb.dotnet.edb import Edb as EdbDotnet
    from pyedb.grpc.edb import Edb as EdbGrpc

log = settings.logger


# lazy imports
def Edb(
    edbpath: str | Path | None = None,
    cellname: str | None = None,
    isreadonly: bool = False,
    edbversion: str | None = None,
    isaedtowned: bool = False,
    oproject: Any = None,
    student_version: bool = False,
    use_ppe: bool = False,
    technology_file: str | Path | None = None,
) -> EdbDotnet | EdbGrpc:
    """Provides the EDB application interface.

    This module inherits all objects that belong to EDB.

    Parameters
    ----------
    edbpath : str or :class:`pathlib.Path`, optional
        Full path to the ``aedb`` folder. The variable can also contain
        the path to a layout to import. Allowed formats are BRD,
        XML (IPC2581), GDS, and DXF. The default is ``None``.
        For GDS import, the Ansys control file (also XML) should have the same
        name as the GDS file. Only the file extension differs.
    cellname : str, optional
        Name of the cell to select. The default is ``None``.
    isreadonly : bool, optional
        Whether to open EDB in read-only mode when it is
        owned by HFSS 3D Layout. The default is ``False``.
    edbversion : str, optional
        Version of EDB to use. The default is ``None``, in which case
        the active version or latest installed version is used.
    isaedtowned : bool, optional
        Whether to launch EDB from HFSS 3D Layout. The
        default is ``False``.
    oproject : Any, optional
        Reference to the AEDT project object. The default is ``None``.
    student_version : bool, optional
        Whether to open the AEDT student version. The default is ``False``.
    use_ppe : bool, optional
        Whether to use PPE license. The default is ``False``.
    technology_file : str or :class:`pathlib.Path`, optional
        Full path to technology file to be converted to XML before importing.
        Supported by GDS format only. The default is ``None``.

    Returns
    -------
    :class:`pyedb.dotnet.edb.Edb` or :class:`pyedb.grpc.edb.Edb`
        EDB application object.

    Examples
    --------
    Create an ``Edb`` object and a new EDB cell.

    >>> from ansys.aedt.core import Edb
    >>> app = Edb()

    Add a new variable named "s1" to the ``Edb`` instance.

    >>> app["s1"] = "0.25 mm"
    >>> app["s1"].tofloat
    0.00025
    >>> app["s1"].tostring
    '0.25mm'

    Add a new parameter with description.

    >>> app["s2"] = ["20um", "Spacing between traces"]
    >>> app["s2"].value
    1.9999999999999998e-05
    >>> app["s2"].description
    'Spacing between traces'

    Create an ``Edb`` object and open the specified project.

    >>> app = Edb("myfile.aedb")

    Create an ``Edb`` object from GDS and control files.
    The XML control file resides in the same directory as the GDS file (myfile.xml).

    >>> app = Edb("/path/to/file/myfile.gds")

    """
    # Use EDB legacy (default choice)
    from pyedb import Edb

    return Edb(
        edbpath=edbpath,
        cellname=cellname,
        isreadonly=isreadonly,
        edbversion=edbversion,
        isaedtowned=isaedtowned,
        oproject=oproject,
        student_version=student_version,
        use_ppe=use_ppe,
        technology_file=technology_file,
    )


def Siwave(
    specified_version: str | None = None,
) -> Any:
    """Siwave application interface.

    Parameters
    ----------
    specified_version : str, optional
        Version of Siwave to use. The default is ``None``, in which case
        the active version or latest installed version is used.

    Returns
    -------
    Any
        Siwave application object.

    Examples
    --------
    Create a Siwave object with the default version.

    >>> from ansys.aedt.core import Siwave
    >>> siwave = Siwave()

    Create a Siwave object with a specific version.

    >>> siwave = Siwave(specified_version="2025.2")

    """
    from pyedb.siwave import Siwave as app

    return app(
        specified_version=specified_version,
    )
