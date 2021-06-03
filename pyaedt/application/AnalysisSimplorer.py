from ..generic.general_methods import aedt_exception_handler, generate_unique_name
from .Analysis import Analysis
from .Design import solutions_settings
from ..modeler.Circuit import ModelerSimplorer
from ..modules.PostProcessor import PostProcessor
from ..modules.SetupTemplates import SetupKeys
from ..modules.SolveSetup import SetupCircuit


class FieldAnalysisSimplorer(Analysis):
    """**AEDT_CircuitAnalysis**

    Class for Simplorer Analysis Setup (Simplorer)

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
            self._solution_type = solutions_settings[soltype]
        else:
            self._solution_type = "TR"

    @property
    def existing_analysis_setups(self):
        """ """
        setups = self.oanalysis.GetAllSolutionSetups()
        return setups

    @property
    def setup_names(self):
        """ """
        return list(self.oanalysis.GetAllSolutionSetups())


    def __init__(self, application, projectname, designname, solution_type, setup_name=None):
        self.solution_type = solution_type
        Analysis.__init__(self, application, projectname, designname, solution_type, setup_name)
        self._modeler = ModelerSimplorer(self)
        self._post = PostProcessor(self)

    @property
    def modeler(self):
        """:return: Design oModeler"""
        return self._modeler

    @property
    def oanalysis(self):
        """:return: Design Module "SimSetup"
        """
        return self.odesign.GetModule("SimSetup")

    @aedt_exception_handler
    def create_setup(self, setupname="MySetupAuto", setuptype=None, props={}):
        """Create a new Setup.

        Parameters
        ----------
        setupname : str
            optional, name of the new setup (Default value = "MySetupAuto")
        setuptype : str
            optional, setup type. if None, default type will be applied
        props : dict
            optional dictionary of properties with values (Default value = {})

        Returns
        -------
        :class: SetupCircuit
            setup object

        """
        if setuptype is None:
            setuptype = SetupKeys.defaultSetups[self.solution_type]
        name = self.generate_unique_setup_name(setupname)
        setup = SetupCircuit(self, setuptype, name)
        setup.name = name
        setup.create()
        if props:
            for el in props:
                setup.props[el] = props[el]
        setup.update()
        self.analysis_setup = name
        self.setups.append(setup)
        return setup
