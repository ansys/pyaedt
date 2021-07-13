from ..generic.general_methods import aedt_exception_handler, generate_unique_name
from .Analysis import Analysis
from .Design import solutions_settings, Design
from ..modeler.Circuit import ModelerEmit
from ..modules.PostProcessor import PostProcessor
from ..modules.SetupTemplates import SetupKeys
from ..modules.SolveSetup import SetupCircuit


class FieldAnalysisEmit(Design):
    """FieldAnaysisEmit class.

    The class is for setting up an EMIT analysis in AEDT.
    It is automatically initialized by an application call (like for HFSS,
    Q3D, and other tools). Refer to the Application function for input definitions.

    
    """

    @property
    def solution_type(self):
        """Solution type.
          
        Parameters
        ----------
        soltype :
            SolutionType object.
        """
        return self._solution_type

    @solution_type.setter
    def solution_type(self, soltype):
        """ """

        if soltype:
            self._solution_type = "EMIT"
        else:
            self._solution_type = "EMIT"

    @property
    def existing_analysis_setups(self):
        """Existing analysis setups."""
        return []

    @property
    def setup_names(self):
        """Setup names."""
        return []


    def __init__(self, application, projectname, designname, solution_type, setup_name=None,
                 specified_version=None, NG=False, AlwaysNew=True, release_on_exit=True, student_version=False):
        self.solution_type = solution_type
        Design.__init__(self, application, projectname, designname, solution_type,
                        specified_version, NG, AlwaysNew, release_on_exit, student_version)
        self._modeler = ModelerEmit(self)
        self._post = PostProcessor(self)

    @property
    def modeler(self):
        """Modeler.
        
        Returns
        -------
        type
            Design oModeler
        """
        return self._modeler

    @property
    def oanalysis(self):
        """Analysis object.
        
        Returns
        -------
        type: 
           Design module ``"SimSetup"``
        """
        return None
