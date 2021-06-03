from ..generic.general_methods import aedt_exception_handler, generate_unique_name
from .Analysis import Analysis
from .Design import design_solutions
from ..modeler.Model2D import ModelerRMxprt


class FieldAnalysisRMxprt(Analysis):
    """**AEDT_RMxprtAnalysis**
    
    
    To BE Implemented
    Class for RMXpert Field Analysis Setup
    
    It is automatically initialized by Application call (like HFSS,
    Q3D...). Refer to Application function for inputs definition

    Parameters
    ----------

    Returns
    -------

    """

    @property
    def solution_type(self):
        """ """
        return self._solution_type

    @solution_type.setter
    def solution_type(self, soltype):
        """

        Parameters
        ----------
        soltype :
            SolutionType object

        Returns
        -------

        """

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

    def __init__(self, application, projectname, designname, solution_type, setup_name=None):
        Analysis.__init__(self, application, projectname, designname, solution_type, setup_name)
        self._modeler = ModelerRMxprt(self)
        #self._post = PostProcessor(self)

    @property
    def modeler(self):
        """ """
        return self._modeler

    @aedt_exception_handler
    def disable_modelcreation(self, solution_type=None):
        """It Enables RMxprtSolution

        Parameters
        ----------
        solution_type :
            solutionType (Default value = None)

        Returns
        -------
        type
            Bool

        """
        self._design_type = "RMxprtSolution"
        self.solution_type = solution_type
        return True


    @aedt_exception_handler
    def enable_modelcreation(self, solution_type = None):
        """It Enables ModelCreation  for Maxwell Model Wizard

        Parameters
        ----------
        solution_type :
            solutionType (Default value = None)

        Returns
        -------
        type
            Bool

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
        """ """
        if self._solution_type:
            return self._odesign.GetSolutionType() == self._solution_type
        else:
            return True

    @aedt_exception_handler
    def _check_design_consistency(self):
        """ """
        consistent = False
        destype = self._odesign.GetDesignType()
        if destype == "RMxprt":
            consistent = self._check_solution_consistency()
        return consistent
