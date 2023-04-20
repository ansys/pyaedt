from pyaedt.application.Analysis import Analysis
from pyaedt.generic.general_methods import pyaedt_function_handler


class FieldAnalysisRMxprt(Analysis):
    """Manages RMXprt field analysis setup. (To be implemented.)

    This class is automatically initialized by an application call (like HFSS,
    Q3D...). Refer to the application function for inputs definition.

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
        solution_type,
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
        Analysis.__init__(
            self,
            application,
            projectname,
            designname,
            solution_type,
            setup_name,
            specified_version,
            non_graphical,
            new_desktop_session,
            close_on_exit,
            student_version,
            machine,
            port,
            aedt_process_id,
        )

        self._modeler = None
        self._post = None

    @property
    def post(self):
        """Post Object.

        Returns
        -------
        :class:`pyaedt.modules.PostProcessor.CircuitPostProcessor`
        """
        if self._post is None:  # pragma: no cover
            from pyaedt.modules.PostProcessor import CircuitPostProcessor

            self._post = CircuitPostProcessor(self)
        return self._post

    @property
    def modeler(self):
        """Modeler.

        Returns
        -------
        :class:`pyaedt.modules.modeler2d.ModelerRMxprt`

        """
        if self._modeler is None:
            from pyaedt.modeler.modeler2d import ModelerRMxprt

            self._modeler = ModelerRMxprt(self)

        return self._modeler

    @pyaedt_function_handler()
    def disable_modelcreation(self, solution_type=None):
        """Enable the RMxprt solution.

        Parameters
        ----------
        solution_type :
            Type of the solution. The default is ``None``.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        """
        self._design_type = "RMxprtSolution"
        self.solution_type = solution_type
        return True

    @pyaedt_function_handler()
    def enable_modelcreation(self, solution_type=None):
        """Enable model creation for the Maxwell model wizard.

        Parameters
        ----------
        solution_type : str
            Type of the solution. The default is ``None``.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        """
        self._design_type = "ModelCreation"
        self.solution_type = solution_type
        return True

    @pyaedt_function_handler()
    def set_material_threshold(self, conductivity=100000, permeability=100):
        """Set material threshold.

        Parameters
        ----------
        conductivity : float, optional
            Conductivity threshold.
            The default value is 100000.
        permeability : float, optional
            Permeability threshold.
            The default value is 100.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.
        """
        try:
            self.odesign.SetThreshold(conductivity, permeability)
            return True
        except:
            return False

    @pyaedt_function_handler()
    def _check_solution_consistency(self):
        """Check solution consistency."""
        if self.design_solutions:
            return self._odesign.GetSolutionType() == self.design_solutions._solution_type
        else:
            return True

    @pyaedt_function_handler()
    def _check_design_consistency(self):
        """Check design consistency."""
        consistent = False
        destype = self._odesign.GetDesignType()
        if destype == "RMxprt":
            consistent = self._check_solution_consistency()
        return consistent
