from pyaedt.application.Design import Design
from pyaedt.modeler.Circuit import ModelerEmit


class FieldAnalysisEmit(Design):
    """FieldAnaysisEmit class.

    The class is for setting up an EMIT analysis in AEDT.
    It is automatically initialized by an application call (like for HFSS,
    Q3D, and other tools). Refer to the Application function for input definitions.


    """

    @property
    def existing_analysis_setups(self):
        """Existing analysis setups."""
        return []

    @property
    def setup_names(self):
        """Setup names."""
        return []

    def __init__(
        self,
        application,
        projectname,
        designname,
        solution_type,
        setup_name=None,
        specified_version=None,
        non_graphical=False,
        new_desktop_session=True,
        close_on_exit=True,
        student_version=False,
    ):
        Design.__init__(
            self,
            application,
            projectname,
            designname,
            solution_type,
            specified_version,
            non_graphical,
            new_desktop_session,
            close_on_exit,
            student_version,
        )
        self.solution_type = solution_type
        self.oanalysis = None
        self._modeler = ModelerEmit(self)

    @property
    def modeler(self):
        """Modeler.

        Returns
        -------
        pyaedt.modeler.Circuit.ModelerEmit
            Design oModeler
        """
        return self._modeler
