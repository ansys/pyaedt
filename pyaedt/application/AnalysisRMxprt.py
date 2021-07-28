from ..generic.general_methods import aedt_exception_handler, generate_unique_name
from .Analysis import Analysis
from .Design import design_solutions
from ..modeler.Model2D import ModelerRMxprt


class FieldAnalysisRMxprt(Analysis):
    """Manages RMXprt field analysis setup. (To be implemented.)
        
    This class is automatically initialized by an application call (like HFSS,
    Q3D...). Refer to the application function for inputs definition.

    Parameters
    ----------

    Returns
    -------

    """

    @property
    def solution_type(self):
        """Solution type."""
        return self._solution_type

    @solution_type.setter
    def solution_type(self, soltype):
        sol = design_solutions[self._design_type]
        if not soltype:
            soltype = sol[0]
        elif soltype not in sol:
            soltype = sol[0]
        try:
            self.odesign.SetDesignFlow(self._design_type, soltype)
            self._solution_type = soltype
        except:
            pass

    def __init__(self, application, projectname, designname, solution_type, setup_name=None,
                 specified_version=None, NG=False, AlwaysNew=False, release_on_exit=False, student_version=False):
        Analysis.__init__(self, application, projectname, designname, solution_type, setup_name,
                          specified_version, NG, AlwaysNew, release_on_exit, student_version)
        self._modeler = ModelerRMxprt(self)
        #self._post = PostProcessor(self)

    @property
    def modeler(self):
        """Modeler.
        
        Returns
        -------
        :class:`pyaedt.modules.Modeler`

        """
        return self._modeler

    @aedt_exception_handler
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


    @aedt_exception_handler
    def enable_modelcreation(self, solution_type = None):
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
    # @property
    # def mesh(self):
    #     return self._mesh
    #
    # @property
    # def post(self):
    #     return self._post

    @aedt_exception_handler
    def _check_solution_consistency(self):
        """Check solution consistency."""
        if self._solution_type:
            return self._odesign.GetSolutionType() == self._solution_type
        else:
            return True

    @aedt_exception_handler
    def _check_design_consistency(self):
        """Check design consistency."""
        consistent = False
        destype = self._odesign.GetDesignType()
        if destype == "RMxprt":
            consistent = self._check_solution_consistency()
        return consistent
