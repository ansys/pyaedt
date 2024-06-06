import re
import sys
import time
import warnings

from pyaedt import is_linux
from pyaedt.circuit import Circuit
from pyaedt.desktop import Desktop
from pyaedt.emit import Emit
from pyaedt.generic.settings import settings
from pyaedt.hfss3dlayout import Hfss3dLayout
from pyaedt.hfss import Hfss
from pyaedt.icepak import Icepak
from pyaedt.maxwell import Maxwell2d
from pyaedt.maxwell import Maxwell3d
from pyaedt.maxwellcircuit import MaxwellCircuit
from pyaedt.mechanical import Mechanical
from pyaedt.q3d import Q2d
from pyaedt.q3d import Q3d
from pyaedt.rmxprt import Rmxprt
from pyaedt.twinbuilder import TwinBuilder

if sys.version_info > (3, 7):
    try:
        from pyedb import Edb
        from pyedb import Siwave
    except ImportError:
        warnings.warn("Pyedb package is missed. Please install it.")
Simplorer = TwinBuilder


def launch_desktop(
    specified_version=None,
    non_graphical=False,
    new_desktop_session=True,
    close_on_exit=True,
    student_version=False,
    machine="",
    port=0,
    aedt_process_id=None,
):
    """Initializes AEDT based on the inputs provided.

    Parameters
    ----------
    specified_version : str, int, float, optional
        Version of AEDT to use. The default is ``None``, in which case the
        active setup or latest installed version is used.
    non_graphical : bool, optional
        Whether to launch AEDT in non-graphical mode. The default
        is ``False``, in which case AEDT is launched in graphical mode.
        This parameter is ignored when a script is launched within AEDT.
    new_desktop_session : bool, optional
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
        ``None``. This parameter is only used when ``new_desktop_session = False``.

    Returns
    -------
    :class:`pyaedt.desktop.Desktop`


    Examples
    --------
    Launch AEDT 2021 R1 in non-graphical mode and initialize HFSS.

    >>> import pyaedt
    >>> desktop = pyaedt.launch_desktop("2022.2", non_graphical=True)
    PyAEDT INFO: pyaedt v...
    PyAEDT INFO: Python version ...
    >>> hfss = pyaedt.Hfss(designname="HFSSDesign1")
    PyAEDT INFO: Project...
    PyAEDT INFO: Added design 'HFSSDesign1' of type HFSS.

    Launch AEDT 2021 R1 in graphical mode and initialize HFSS.

    >>> desktop = Desktop("2021.2")
    PyAEDT INFO: pyaedt v...
    PyAEDT INFO: Python version ...
    >>> hfss = pyaedt.Hfss(designname="HFSSDesign1")
    PyAEDT INFO: No project is defined. Project...
    """
    d = Desktop(
        specified_version=specified_version,
        non_graphical=non_graphical,
        new_desktop_session=new_desktop_session,
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
    "2D Extractor": Q2d,
    "Q3D Extractor": Q3d,
    "HFSS": Hfss,
    "Mechanical": Mechanical,
    "Icepak": Icepak,
    "Rmxprt": Rmxprt,
    "HFSS 3D Layout Design": Hfss3dLayout,
    "EMIT": Emit,
    "EDB": Edb,
    "Desktop": Desktop,
    "Siwave": Siwave,
}


def get_pyaedt_app(project_name=None, design_name=None, desktop=None):
    """Gets the PyAEDT object with a given project name and design name.

    Parameters
    ----------
    project_name : str, optional
        Project name.
    design_name : str, optional
        Design name.
    desktop : :class:`pyaedt.desktop.Desktop`, optional
        Desktop class. The default is ``None``.

    Returns
    -------
    :def :`pyaedt.Hfss`
        Any of the Pyaedt App initialized.
    """
    from pyaedt.generic.desktop_sessions import _desktop_sessions

    odesktop = None
    process_id = None
    if desktop:
        odesktop = desktop.odesktop
        process_id = desktop.aedt_process_id
    elif _desktop_sessions and project_name:
        for desktop in list(_desktop_sessions.values()):
            if project_name in list(desktop.project_list()):
                odesktop = desktop.odesktop
                break
    elif _desktop_sessions:
        odesktop = list(_desktop_sessions.values())[-1]
    elif "oDesktop" in dir(sys.modules["__main__"]):  # ironpython
        odesktop = sys.modules["__main__"].oDesktop  # ironpython
    else:
        raise AttributeError("No Desktop Present.")
    if not process_id:
        process_id = odesktop.GetProcessID()
    if project_name and project_name not in odesktop.GetProjectList():
        raise AttributeError("Project  {} doesn't exist in current desktop.".format(project_name))
    if not project_name:
        oProject = odesktop.GetActiveProject()
    else:
        oProject = odesktop.SetActiveProject(project_name)
    if is_linux and settings.aedt_version == "2024.1":
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
        raise AttributeError("Design  {} doesn't exist in current project.".format(design_name))
    if not design_name:
        oDesign = oProject.GetActiveDesign()
    else:
        oDesign = oProject.SetActiveDesign(design_name)
    if is_linux and settings.aedt_version == "2024.1":
        time.sleep(1)
        odesktop.CloseAllWindows()
    if not oDesign:
        raise AttributeError("No design is present.")
    design_type = oDesign.GetDesignType()
    if design_type in list(app_map.keys()):
        version = odesktop.GetVersion().split(".")
        v = ".".join([version[0], version[1]])
        return app_map[design_type](project_name, design_name, specified_version=v, aedt_process_id=process_id)
    return None
