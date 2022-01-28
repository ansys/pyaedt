from pyaedt.modeler.Circuit import ModelerMaxwellCircuit
from pyaedt.application.Analysis import Analysis


class AnalysisMaxwellCircuit(Analysis):
    """Class for Maxwell Circuit (MaxwellCircuit)

    Maxwell Circuit Editor has no setup, solution, analysis or postprocessor
    It is automatically initialized by Application call (Maxwell Circuit).
    Refer to Application function for inputs definition

    Parameters
    ----------
    projectname : str, optional
        Name of the project to select or the full path to the project
        or AEDTZ archive to open.  The default is ``None``, in which
        case an attempt is made to get an active project. If no
        projects are present, an empty project is created.
    designname : str, optional
        Name of the design to select. The default is ``None``, in
        which case an attempt is made to get an active design. If no
        designs are present, an empty design is created.
    specified_version : str, optional
        Version of AEDT to use. The default is ``None``. If ``None``,
        the active setup is used or the latest installed version is
        used.
    NG : bool, optional
        Whether to launch AEDT in the non-graphical mode. The default
        is ``False``, in which case AEDT is launched in the graphical mode.
    new_desktop_session : bool, optional
        Whether to launch an instance of AEDT in a new thread, even if
        another instance of the ``specified_version`` is active on the
        machine.  The default is ``True``.
    close_on_exit : bool, optional
        Whether to release AEDT on exit. The default is ``True``.
    student_version : bool, optional
        Whether open AEDT Student Version. The default is ``False``.

    """

    def __init__(
        self,
        application,
        projectname,
        designname,
        specified_version=None,
        non_graphical=False,
        new_desktop_session=False,
        close_on_exit=False,
        student_version=False,
    ):

        Analysis.__init__(
            self,
            application,
            projectname,
            designname,
            None,
            None,
            specified_version,
            non_graphical,
            new_desktop_session,
            close_on_exit,
            student_version,
        )
        self.solution_type = None
        self._modeler = ModelerMaxwellCircuit(self)

    @property
    def modeler(self):
        """Design oModeler."""
        return self._modeler
