from pyaedt.application.Design import Design
from pyaedt.emit_core.Couplings import CouplingsEmit
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
        machine="",
        port=0,
        aedt_process_id=None,
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
            machine=machine,
            port=machine,
            aedt_process_id=aedt_process_id,
        )
        self.solution_type = solution_type
        self._modeler = ModelerEmit(self)
        self._couplings = CouplingsEmit(self)

    @property
    def modeler(self):
        """Modeler.

        Returns
        -------
        pyaedt.modeler.Circuit.ModelerEmit
            Design oModeler
        """
        return self._modeler

    @property
    def couplings(self):
        """Emit Couplings.

        Returns
        -------
        pyaedt.emit_core.Couplings.CouplingsEmit
            Couplings within the EMIT Design
        """
        return self._couplings
