# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 - 2025 ANSYS, Inc. and/or its affiliates.
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

import re
import sys
import time

from ansys.aedt.core.circuit import Circuit
from ansys.aedt.core.circuit_netlist import CircuitNetlist
from ansys.aedt.core.desktop import Desktop
from ansys.aedt.core.generic.general_methods import is_linux
from ansys.aedt.core.generic.settings import settings
from ansys.aedt.core.hfss import Hfss
from ansys.aedt.core.hfss3dlayout import Hfss3dLayout
from ansys.aedt.core.icepak import Icepak
from ansys.aedt.core.maxwell import Maxwell2d
from ansys.aedt.core.maxwell import Maxwell3d
from ansys.aedt.core.maxwellcircuit import MaxwellCircuit
from ansys.aedt.core.mechanical import Mechanical
from ansys.aedt.core.q3d import Q2d
from ansys.aedt.core.q3d import Q3d
from ansys.aedt.core.rmxprt import Rmxprt
from ansys.aedt.core.twinbuilder import TwinBuilder

Emit = None
if not ("IronPython" in sys.version or ".NETFramework" in sys.version):  # pragma: no cover
    from ansys.aedt.core.emit import Emit

Simplorer = TwinBuilder


def launch_desktop(
    version=None,
    non_graphical=False,
    new_desktop=True,
    close_on_exit=True,
    student_version=False,
    machine="",
    port=0,
    aedt_process_id=None,
):
    """Initialize AEDT based on the inputs provided.

    Parameters
    ----------
    version : str, int, float, optional
        Version of AEDT to use. The default is ``None``, in which case the
        active setup or latest installed version is used.
    non_graphical : bool, optional
        Whether to launch AEDT in non-graphical mode. The default
        is ``False``, in which case AEDT is launched in graphical mode.
        This parameter is ignored when a script is launched within AEDT.
    new_desktop : bool, optional
        Whether to launch an instance of AEDT in a new thread, even if
        another instance of the ``specified_version`` is active on the machine.
        The default is ``False``.
    close_on_exit : bool, optional
        Whether to close AEDT on exit. The default is ``True``.
    student_version : bool, optional
        Whether to open the AEDT student version. The default is
        ``False``.
    machine : str, optional
        Machine name to connect the oDesktop session to. This parameters works only in 2022 R2
        and later. The remote server must be up and running with the command
        `"ansysedt.exe -grpcsrv portnum"`. If the machine is `"localhost"`, the server also
        starts if not present.
    port : int, optional
        Port number on which to start the oDesktop communication on the already existing server.
        This parameter is ignored when creating a new server. It works only in 2022 R2 and
        later. The remote server must be up and running with the command `"ansysedt.exe -grpcsrv portnum"`.
    aedt_process_id : int, optional
        Process ID for the instance of AEDT to point PyAEDT at. The default is
        ``None``. This parameter is only used when ``new_desktop = False``.

    Returns
    -------
    :class:`ansys.aedt.core.desktop.Desktop`


    Examples
    --------
    Launch AEDT 2025 R1 in non-graphical mode and initialize HFSS.

    >>> import ansys.aedt.core
    >>> desktop = ansys.aedt.core.launch_desktop("2025.2", non_graphical=True)
    PyAEDT INFO: pyaedt v...
    PyAEDT INFO: Python version ...
    >>> hfss = ansys.aedt.core.Hfss(design="HFSSDesign1")
    PyAEDT INFO: Project...
    PyAEDT INFO: Added design 'HFSSDesign1' of type HFSS.

    Launch AEDT 2025 R1 in graphical mode and initialize HFSS.

    >>> desktop = Desktop("2025.2")
    PyAEDT INFO: pyaedt v...
    PyAEDT INFO: Python version ...
    >>> hfss = ansys.aedt.core.Hfss(design="HFSSDesign1")
    PyAEDT INFO: No project is defined. Project...
    """
    d = Desktop(
        version=version,
        non_graphical=non_graphical,
        new_desktop=new_desktop,
        close_on_exit=close_on_exit,
        student_version=student_version,
        machine=machine,
        port=port,
        aedt_process_id=aedt_process_id,
    )
    return d


app_map = {
    "Maxwell 2D": Maxwell2d,
    "Maxwell 3D": Maxwell3d,
    "Maxwell Circuit": MaxwellCircuit,
    "Twin Builder": TwinBuilder,
    "Circuit Design": Circuit,
    "Circuit Netlist": CircuitNetlist,
    "2D Extractor": Q2d,
    "Q3D Extractor": Q3d,
    "HFSS": Hfss,
    "Mechanical": Mechanical,
    "Icepak": Icepak,
    "Rmxprt": Rmxprt,
    "HFSS 3D Layout Design": Hfss3dLayout,
    "EMIT": Emit,
}


def get_pyaedt_app(project_name=None, design_name=None, desktop=None):
    """Get the PyAEDT object with a given project name and design name.

    Parameters
    ----------
    project_name : str, optional
        Project name.
    design_name : str, optional
        Design name.
    desktop : :class:`ansys.aedt.core.desktop.Desktop`, optional
        Desktop class. The default is ``None``.

    Returns
    -------
    :def :`ansys.aedt.core.Hfss`
        Any of the PyAEDT App initialized.
    """
    from ansys.aedt.core.internal.desktop_sessions import _desktop_sessions

    odesktop = None
    process_id = None
    if desktop:
        odesktop = desktop.odesktop
        process_id = desktop.aedt_process_id
    elif _desktop_sessions and project_name:
        for desktop in list(_desktop_sessions.values()):
            if project_name in list(desktop.project_list):
                odesktop = desktop.odesktop
                break
    elif _desktop_sessions:
        odesktop = list(_desktop_sessions.values())[-1].odesktop
    elif "oDesktop" in dir(sys.modules["__main__"]):  # ironpython
        odesktop = sys.modules["__main__"].oDesktop  # ironpython
    else:
        raise AttributeError("No Desktop Present.")
    if not process_id:
        process_id = odesktop.GetProcessID()
    if project_name and project_name not in desktop.project_list:
        raise AttributeError(f"Project {project_name} doesn't exist in current desktop.")
    if not project_name:
        oProject = odesktop.GetActiveProject()
    else:
        oProject = odesktop.SetActiveProject(project_name)
    if is_linux and settings.aedt_version == "2024.1":  # pragma: no cover
        time.sleep(1)
        odesktop.CloseAllWindows()
    if not oProject:
        raise AttributeError("No project is present.")
    design_names = []
    deslist = list(oProject.GetTopDesignList())
    for el in deslist:
        m = re.search(r"[^;]+$", el)
        design_names.append(m.group(0))
    if design_name and design_name not in design_names:
        raise AttributeError(f"Design  {design_name} doesn't exist in current project.")
    if not design_name:
        oDesign = oProject.GetActiveDesign()
    else:
        oDesign = oProject.SetActiveDesign(design_name)
    if is_linux and settings.aedt_version == "2024.1":  # pragma: no cover
        time.sleep(1)
        odesktop.CloseAllWindows()
    if not oDesign:
        raise AttributeError("No design is present.")
    design_type = oDesign.GetDesignType()
    if design_type in list(app_map.keys()):
        version = odesktop.GetVersion().split(".")
        v = ".".join([version[0], version[1]])
        return app_map[design_type](project_name, design_name, version=v, aedt_process_id=process_id)
    return None
