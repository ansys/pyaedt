from ..generic.general_methods import aedt_exception_handler, generate_unique_name
from .Analysis import Analysis
from .Design import solutions_settings, Design
from ..modeler.Circuit import ModelerEmit
from ..modules.PostProcessor import PostProcessor
from ..modules.SetupTemplates import SetupKeys
from ..modules.SolveSetup import SetupCircuit


class FieldAnalysisEmit(Design):
    """**AEDT Emit Analysis**

    Class for Emit Analysis Setup (Emit)

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
        """Solution Type

        Parameters
        ----------
        soltype :
            SolutionType object

        Returns
        -------

        """
        if soltype:
            self._solution_type = "EMIT"
        else:
            self._solution_type = "EMIT"

    @property
    def existing_analysis_setups(self):
        """ """
        return []

    @property
    def setup_names(self):
        """ """
        return []


    def __init__(self, application, projectname, designname, solution_type, setup_name=None,
                 specified_version=None, NG=False, AlwaysNew=True, release_on_exit=True):
        self.solution_type = solution_type
        Design.__init__(self, application, projectname, designname, solution_type,
                        specified_version, NG, AlwaysNew, release_on_exit)
        self._modeler = ModelerEmit(self)
        self._post = PostProcessor(self)

    @property
    def modeler(self):
        """:return: Design oModeler"""
        return self._modeler

    @property
    def oanalysis(self):
        """:return: Design Module "SimSetup"
        """
        return None

