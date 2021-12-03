from pyaedt.generic.general_methods import aedt_exception_handler
from pyaedt.modeler.Circuit import ModelerSimplorer
from pyaedt.modules.SolveSetup import SetupCircuit
from pyaedt.application.Analysis import Analysis
from pyaedt.application.Design import solutions_settings
from pyaedt.modules.PostProcessor import CircuitPostProcessor


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
        """Solution Type."""
        return self._solution_type

    @solution_type.setter
    def solution_type(self, soltype):
        if soltype:
            self._solution_type = solutions_settings[soltype]
        else:
            self._solution_type = "TR"

    @property
    def existing_analysis_setups(self):
        """Existing analysis setups.

        References
        ----------

        >>> oModule.GetAllSolutionSetups"""
        setups = self.oanalysis.GetAllSolutionSetups()
        return setups

    @property
    def setup_names(self):
        """Setup names.

        References
        ----------

        >>> oModule.GetAllSolutionSetups"""
        return list(self.oanalysis.GetAllSolutionSetups())

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
        )
        self.solution_type = solution_type
        self._modeler = ModelerSimplorer(self)
        self._post = CircuitPostProcessor(self)

    @property
    def modeler(self):
        """Design oModeler."""
        return self._modeler

    @aedt_exception_handler
    def create_setup(self, setupname="MySetupAuto", setuptype=None, props={}):
        """Create a new setup.

        Parameters
        ----------
        setupname : str, optional
            Name of the new setup.  Default is ``"MySetupAuto"``.
        setuptype : str
            Setup type. If ``None``, default type will be applied.
        props : dict
            Dictionary of properties with values.

        Returns
        -------
        pyaedt.modules.SolveSetup.SetupCircuit
            Setup object
        """
        if setuptype is None:
            setuptype = self.solution_type
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
