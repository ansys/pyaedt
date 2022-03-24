from __future__ import absolute_import  # noreorder

from pyaedt.application.AnalysisEmit import FieldAnalysisEmit


class Emit(FieldAnalysisEmit, object):
    """Provides the Emit application interface.

    .. note::
       This object creates only a skeleton for an empty design.
       It has very limited functionalities, and no methods
       are implemented yet.

    Parameters
    ----------
    projectname : str, optional
        Name of the project to select or the full path to the project
        or AEDTZ archive to open.  The default is ``None``. If
        ``None``, try to get an active project and, if no projects are
        present, create an empty project.
    designname : str, optional
        Name of the design to select. The default is ``None``. If
        ``None``, try to get an active design and, if no designs are
        present, create an empty design.
    solution_type : str, optional
        Solution type to apply to the design. The default is ``None``, in which
        case the default type is applied.
    setup_name : str, optional
       Name of the setup to use as the nominal. The default is
       ``None``, in which case the active setup is used or nothing is
       used.
    specified_version : str, optional
        Version of AEDT to use. The default is ``None``, in which case
        the active setup is used or the latest installed version is
        used.
    non_graphical : bool, optional
        Whether to launch AEDT in non-graphical mode. The default
        is ``False``, in which case AEDT is launched in graphical mode.
        This parameter is ignored when a script is launched within AEDT.
    new_desktop_session : bool, optional
        Whether to launch an instance of AEDT in a new thread, even if
        another instance of the ``specified_version`` is active on the
        machine.  The default is ``True``.
    close_on_exit : bool, optional
        Whether to release AEDT on exit. The default is ``True``.
    student_version : bool, optional
        Whether to open the AEDT student version. The default is ``False``.

    Examples
    --------
    Create an instance of Emit and connect to an existing Emit
    design or create a new Emit design if one does not exist.

    >>> from pyaedt import Emit
    >>> app = Emit()

    Create a instance of Emit and link to a project named
    ``"projectname"``. If this project does not exist, create one with
    this name.

    >>> app = Emit(projectname)

    Create an instance of Emit and link to a design named
    ``"designname"`` in a project named ``"projectname"``.

    >>> app = Emit(projectname,designame)

    Create an instance of Emit and open the specified project,
    which is named ``Myfile.aedt``.

    >>> app = Emit("myfile.aedt")


    """

    def __init__(
        self,
        projectname=None,
        designname=None,
        solution_type=None,
        setup_name=None,
        specified_version=None,
        non_graphical=False,
        new_desktop_session=True,
        close_on_exit=True,
        student_version=False,
    ):
        """Constructor."""
        FieldAnalysisEmit.__init__(
            self,
            "EMIT",
            projectname,
            designname,
            solution_type,
            setup_name,
            specified_version,
            non_graphical,
            new_desktop_session,
            close_on_exit,
            student_version,
        )

    def __enter__(self):
        return self
