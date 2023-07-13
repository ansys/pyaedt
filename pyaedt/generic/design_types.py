import re
import sys


# lazy imports
def Circuit(
    projectname=None,
    designname=None,
    solution_type=None,
    setup_name=None,
    specified_version=None,
    non_graphical=False,
    new_desktop_session=False,
    close_on_exit=False,
    student_version=False,
    machine="",
    port=0,
    aedt_process_id=None,
):
    """Circuit Class.

    Returns
    -------
    :class:`pyaedt.circuit.Circuit`
    """
    from pyaedt.circuit import Circuit as app

    return app(
        projectname=projectname,
        designname=designname,
        solution_type=solution_type,
        setup_name=setup_name,
        specified_version=specified_version,
        non_graphical=non_graphical,
        new_desktop_session=new_desktop_session,
        close_on_exit=close_on_exit,
        student_version=student_version,
        machine=machine,
        port=port,
        aedt_process_id=aedt_process_id,
    )


def Hfss(
    projectname=None,
    designname=None,
    solution_type=None,
    setup_name=None,
    specified_version=None,
    non_graphical=False,
    new_desktop_session=False,
    close_on_exit=False,
    student_version=False,
    machine="",
    port=0,
    aedt_process_id=None,
):
    """Return an instance of the Hfss Class.

    Returns
    -------
    :class:`pyaedt.hfss.Hfss`
    """
    from pyaedt.hfss import Hfss as app

    return app(
        projectname=projectname,
        designname=designname,
        solution_type=solution_type,
        setup_name=setup_name,
        specified_version=specified_version,
        non_graphical=non_graphical,
        new_desktop_session=new_desktop_session,
        close_on_exit=close_on_exit,
        student_version=student_version,
        machine=machine,
        port=port,
        aedt_process_id=aedt_process_id,
    )


def Icepak(
    projectname=None,
    designname=None,
    solution_type=None,
    setup_name=None,
    specified_version=None,
    non_graphical=False,
    new_desktop_session=False,
    close_on_exit=False,
    student_version=False,
    machine="",
    port=0,
    aedt_process_id=None,
):
    """Icepak Class.

    Returns
    -------
    :class:`pyaedt.icepak.Icepak`"""
    from pyaedt.icepak import Icepak as app

    return app(
        projectname=projectname,
        designname=designname,
        solution_type=solution_type,
        setup_name=setup_name,
        specified_version=specified_version,
        non_graphical=non_graphical,
        new_desktop_session=new_desktop_session,
        close_on_exit=close_on_exit,
        student_version=student_version,
        machine=machine,
        port=port,
        aedt_process_id=aedt_process_id,
    )


def Emit(
    projectname=None,
    designname=None,
    solution_type=None,
    setup_name=None,
    specified_version=None,
    non_graphical=False,
    new_desktop_session=False,
    close_on_exit=False,
    student_version=False,
    machine="",
    port=0,
    aedt_process_id=None,
):
    """Emit Class.

    Returns
    -------
    :class:`pyaedt.emit.Emit`"""
    from pyaedt.emit import Emit as app

    return app(
        projectname=projectname,
        designname=designname,
        solution_type=solution_type,
        setup_name=setup_name,
        specified_version=specified_version,
        non_graphical=non_graphical,
        new_desktop_session=new_desktop_session,
        close_on_exit=close_on_exit,
        student_version=student_version,
        machine=machine,
        port=port,
        aedt_process_id=aedt_process_id,
    )


def Hfss3dLayout(
    projectname=None,
    designname=None,
    solution_type=None,
    setup_name=None,
    specified_version=None,
    non_graphical=False,
    new_desktop_session=False,
    close_on_exit=False,
    student_version=False,
    machine="",
    port=0,
    aedt_process_id=None,
):
    """Hfss3dLayout Class.

    Returns
    -------
    :class:`pyaedt.hfss3dlayout.Hfss3dLayout`"""
    from pyaedt.hfss3dlayout import Hfss3dLayout as app

    return app(
        projectname=projectname,
        designname=designname,
        solution_type=solution_type,
        setup_name=setup_name,
        specified_version=specified_version,
        non_graphical=non_graphical,
        new_desktop_session=new_desktop_session,
        close_on_exit=close_on_exit,
        student_version=student_version,
        machine=machine,
        port=port,
        aedt_process_id=aedt_process_id,
    )


def Maxwell2d(
    projectname=None,
    designname=None,
    solution_type=None,
    setup_name=None,
    specified_version=None,
    non_graphical=False,
    new_desktop_session=False,
    close_on_exit=False,
    student_version=False,
    machine="",
    port=0,
    aedt_process_id=None,
):
    """Maxwell2d Class.

    Returns
    -------
    :class:`pyaedt.maxwell.Maxwell2d`"""
    from pyaedt.maxwell import Maxwell2d as app

    return app(
        projectname=projectname,
        designname=designname,
        solution_type=solution_type,
        setup_name=setup_name,
        specified_version=specified_version,
        non_graphical=non_graphical,
        new_desktop_session=new_desktop_session,
        close_on_exit=close_on_exit,
        student_version=student_version,
        machine=machine,
        port=port,
        aedt_process_id=aedt_process_id,
    )


def Maxwell3d(
    projectname=None,
    designname=None,
    solution_type=None,
    setup_name=None,
    specified_version=None,
    non_graphical=False,
    new_desktop_session=False,
    close_on_exit=False,
    student_version=False,
    machine="",
    port=0,
    aedt_process_id=None,
):
    """Maxwell3d Class.

    Returns
    -------
    :class:`pyaedt.maxwell.Maxwell3d`"""
    from pyaedt.maxwell import Maxwell3d as app

    return app(
        projectname=projectname,
        designname=designname,
        solution_type=solution_type,
        setup_name=setup_name,
        specified_version=specified_version,
        non_graphical=non_graphical,
        new_desktop_session=new_desktop_session,
        close_on_exit=close_on_exit,
        student_version=student_version,
        machine=machine,
        port=port,
        aedt_process_id=aedt_process_id,
    )


def MaxwellCircuit(
    projectname=None,
    designname=None,
    solution_type=None,
    specified_version=None,
    non_graphical=False,
    new_desktop_session=False,
    close_on_exit=False,
    student_version=False,
    machine="",
    port=0,
    aedt_process_id=None,
):
    """MaxwellCircuit Class.

    Returns
    -------
    :class:`pyaedt.maxwellcircuit.MaxwellCircuit`"""
    from pyaedt.maxwellcircuit import MaxwellCircuit as app

    return app(
        projectname=projectname,
        designname=designname,
        solution_type=solution_type,
        specified_version=specified_version,
        non_graphical=non_graphical,
        new_desktop_session=new_desktop_session,
        close_on_exit=close_on_exit,
        student_version=student_version,
        machine=machine,
        port=port,
        aedt_process_id=aedt_process_id,
    )


def Mechanical(
    projectname=None,
    designname=None,
    solution_type=None,
    setup_name=None,
    specified_version=None,
    non_graphical=False,
    new_desktop_session=False,
    close_on_exit=False,
    student_version=False,
    machine="",
    port=0,
    aedt_process_id=None,
):
    """Mechanical Class.

    Returns
    -------
    :class:`pyaedt.mechanical.Mechanical`"""
    from pyaedt.mechanical import Mechanical as app

    return app(
        projectname=projectname,
        designname=designname,
        solution_type=solution_type,
        setup_name=setup_name,
        specified_version=specified_version,
        non_graphical=non_graphical,
        new_desktop_session=new_desktop_session,
        close_on_exit=close_on_exit,
        student_version=student_version,
        machine=machine,
        port=port,
        aedt_process_id=aedt_process_id,
    )


def Q2d(
    projectname=None,
    designname=None,
    solution_type=None,
    setup_name=None,
    specified_version=None,
    non_graphical=False,
    new_desktop_session=False,
    close_on_exit=False,
    student_version=False,
    machine="",
    port=0,
    aedt_process_id=None,
):
    """Q2D Class.

    Returns
    -------
    :class:`pyaedt.q3d.Q2d`"""
    from pyaedt.q3d import Q2d as app

    return app(
        projectname=projectname,
        designname=designname,
        solution_type=solution_type,
        setup_name=setup_name,
        specified_version=specified_version,
        non_graphical=non_graphical,
        new_desktop_session=new_desktop_session,
        close_on_exit=close_on_exit,
        student_version=student_version,
        machine=machine,
        port=port,
        aedt_process_id=aedt_process_id,
    )


def Q3d(
    projectname=None,
    designname=None,
    solution_type=None,
    setup_name=None,
    specified_version=None,
    non_graphical=False,
    new_desktop_session=False,
    close_on_exit=False,
    student_version=False,
    machine="",
    port=0,
    aedt_process_id=None,
):
    """Q3D Class.

    Returns
    -------
    :class:`pyaedt.q3d.Q3d`"""
    from pyaedt.q3d import Q3d as app

    return app(
        projectname=projectname,
        designname=designname,
        solution_type=solution_type,
        setup_name=setup_name,
        specified_version=specified_version,
        non_graphical=non_graphical,
        new_desktop_session=new_desktop_session,
        close_on_exit=close_on_exit,
        student_version=student_version,
        machine=machine,
        port=port,
        aedt_process_id=aedt_process_id,
    )


def Rmxprt(
    projectname=None,
    designname=None,
    solution_type=None,
    setup_name=None,
    specified_version=None,
    non_graphical=False,
    new_desktop_session=False,
    close_on_exit=False,
    student_version=False,
    machine="",
    port=0,
    aedt_process_id=None,
):
    """Rmxprt Class.

    Returns
    -------
    :class:`pyaedt.rmxprt.Rmxprt`"""
    from pyaedt.rmxprt import Rmxprt as app

    return app(
        projectname=projectname,
        designname=designname,
        solution_type=solution_type,
        setup_name=setup_name,
        specified_version=specified_version,
        non_graphical=non_graphical,
        new_desktop_session=new_desktop_session,
        close_on_exit=close_on_exit,
        student_version=student_version,
        machine=machine,
        port=port,
        aedt_process_id=aedt_process_id,
    )


def TwinBuilder(
    projectname=None,
    designname=None,
    solution_type=None,
    setup_name=None,
    specified_version=None,
    non_graphical=False,
    new_desktop_session=False,
    close_on_exit=False,
    student_version=False,
    machine="",
    port=0,
    aedt_process_id=None,
):
    """TwinBuilder Class.

    Returns
    -------
    :class:`pyaedt.twinbuilder.TwinBuilder`"""
    from pyaedt.twinbuilder import TwinBuilder as app

    return app(
        projectname=projectname,
        designname=designname,
        solution_type=solution_type,
        setup_name=setup_name,
        specified_version=specified_version,
        non_graphical=non_graphical,
        new_desktop_session=new_desktop_session,
        close_on_exit=close_on_exit,
        student_version=student_version,
        machine=machine,
        port=port,
        aedt_process_id=aedt_process_id,
    )


def Simplorer(
    projectname=None,
    designname=None,
    solution_type=None,
    setup_name=None,
    specified_version=None,
    non_graphical=False,
    new_desktop_session=False,
    close_on_exit=False,
    student_version=False,
    machine="",
    port=0,
    aedt_process_id=None,
):
    """Simplorer Class.

    Returns
    -------
    :class:`pyaedt.twinbuilder.TwinBuilder`"""
    from pyaedt.twinbuilder import TwinBuilder as app

    return app(
        projectname=projectname,
        designname=designname,
        solution_type=solution_type,
        setup_name=setup_name,
        specified_version=specified_version,
        non_graphical=non_graphical,
        new_desktop_session=new_desktop_session,
        close_on_exit=close_on_exit,
        student_version=student_version,
        machine=machine,
        port=port,
        aedt_process_id=aedt_process_id,
    )


def Desktop(
    specified_version=None,
    non_graphical=False,
    new_desktop_session=True,
    close_on_exit=True,
    student_version=False,
    machine="",
    port=0,
    aedt_process_id=None,
):
    """Desktop Class.

    Returns
    -------
    :class:`pyaedt.desktop.Desktop`"""
    from pyaedt.desktop import Desktop as app

    return app(
        specified_version=specified_version,
        non_graphical=non_graphical,
        new_desktop_session=new_desktop_session,
        close_on_exit=close_on_exit,
        student_version=student_version,
        machine=machine,
        port=port,
        aedt_process_id=aedt_process_id,
    )


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
    specified_version : str, optional
        Version of AEDT to use. The default is ``None``, in which case the
        active setup or latest installed version is used.
    non_graphical : bool, optional
        Whether to launch AEDT in non-graphical mode. The default
        is ``False``, in which case AEDT is launched in graphical mode.
        This parameter is ignored when a script is launched within AEDT.
    new_desktop_session : bool, optional
        Whether to launch an instance of AEDT in a new thread, even if
        another instance of the ``specified_version`` is active on the machine.
        The default is ``True``.
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


def Edb(
    edbpath=None,
    cellname=None,
    isreadonly=False,
    edbversion=None,
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
    edbversion : str, optional
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
    :class:`pyaedt.edb.Edb`

    Examples
    --------
    Create an ``Edb`` object and a new EDB cell.

    >>> from pyaedt import Edb
    >>> app = Edb()

    Add a new variable named "s1" to the ``Edb`` instance.

    >>> app['s1'] = "0.25 mm"
    >>> app['s1'].tofloat
    >>> 0.00025
    >>> app['s1'].tostring
    >>> "0.25mm"

    or add a new parameter with description:

    >>> app['s2'] = ["20um", "Spacing between traces"]
    >>> app['s2'].value
    >>> 1.9999999999999998e-05
    >>> app['s2'].description
    >>> 'Spacing between traces'


    Create an ``Edb`` object and open the specified project.

    >>> app = Edb("myfile.aedb")

    Create an ``Edb`` object from GDS and control files.
    The XML control file resides in the same directory as the GDS file: (myfile.xml).

    >>> app = Edb("/path/to/file/myfile.gds")

    """
    from pyaedt.edb import Edb as app

    return app(
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
    specified_version=None,
):
    """Siwave Class."""
    from pyaedt.siwave import Siwave as app

    return app(
        specified_version=specified_version,
    )


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


def get_pyaedt_app(project_name=None, design_name=None):
    """Returns the Pyaedt Object of specific projec_name and design_name.

    Parameters
    ----------
    project_name
    design_name

    Returns
    -------
    :def :`pyaedt.Hfss`
        Any of the Pyaedt App initialized.
    """
    main = sys.modules["__main__"]
    if "oDesktop" in dir(main):
        if project_name and project_name not in main.oDesktop.GetProjectList():
            raise AttributeError("Project  {} doesn't exist in current Desktop.".format(project_name))
        if not project_name:
            oProject = main.oDesktop.GetActiveProject()
        else:
            oProject = main.oDesktop.SetActiveProject(project_name)
        if not oProject:
            raise AttributeError("No Project Present.")
        design_names = []
        deslist = list(oProject.GetTopDesignList())
        for el in deslist:
            m = re.search(r"[^;]+$", el)
            design_names.append(m.group(0))
        if design_name and design_name not in design_names:
            raise AttributeError("Design  {} doesn't exists in current Project.".format(design_name))
        if not design_name:
            oDesign = oProject.GetActiveDesign()
        else:
            oDesign = oProject.SetActiveDesign(design_name)
        if not oDesign:
            raise AttributeError("No Design Present.")
        design_type = oDesign.GetDesignType()
        if design_type in list(app_map.keys()):
            version = main.oDesktop.GetVersion().split(".")
            v = ".".join([version[0], version[1]])
            return app_map[design_type](project_name, design_name, specified_version=v)
    return None
