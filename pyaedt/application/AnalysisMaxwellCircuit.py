from pyaedt.modeler.Circuit import ModelerMaxwellCircuit
from pyaedt.application.Analysis import Analysis


class AnalysisMaxwellCircuit(Analysis):
    """Class for Maxwell Circuit (MaxwellCircuit)

    Maxwell Circuit Editor has no setup, solution, analysis or postprocessor
    It is automatically initialized by Application call (Maxwell Circuit).
    Refer to Application function for inputs definition

    Parameters
    ----------

    Returns
    -------

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
