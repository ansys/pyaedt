from pyaedt.application.Analysis import Analysis
from pyaedt.generic.general_methods import pyaedt_function_handler
from pyaedt.modeler.schematic import ModelerTwinBuilder
from pyaedt.modules.PostProcessor import CircuitPostProcessor
from pyaedt.modules.SolveSetup import SetupCircuit
from pyaedt.modules.SolveSweeps import SetupKeys


class AnalysisTwinBuilder(Analysis):
    """Provides the Twin Builder Analysis Setup (TwinBuilder).
    It is automatically initialized by Application call (Twin Builder).
    Refer to Application function for inputs definition

    Parameters
    ----------

    Returns
    -------

    """

    @property
    def existing_analysis_setups(self):
        """Get all analysis solution setups.

        References
        ----------

        >>> oModule.GetAllSolutionSetups"""
        setups = list(self.oanalysis.GetAllSolutionSetups())
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
        self._modeler = ModelerTwinBuilder(self)
        self._post = CircuitPostProcessor(self)

    @property
    def existing_analysis_sweeps(self):
        """Get all existing analysis setups.

        Returns
        -------
        list of str
            List of all analysis setups in the design.

        """
        return self.existing_analysis_setups

    @property
    def modeler(self):
        """Design oModeler."""
        return self._modeler

    @pyaedt_function_handler()
    def create_setup(self, setupname="MySetupAuto", setuptype=None, **kwargs):
        """Create a setup.

        Parameters
        ----------
        setupname : str, optional
            Name of the setup. The default is ``"MySetupAuto"``.
        setuptype : str
            Type of the setup. The default is ``None``, in which case the default
            type is applied.
        **kwargs : dict, optional
            Extra arguments to set up the circuit.
            Available keys depend on the setup chosen.
            For more information, see
            :doc:`../SetupTemplatesCircuit`.

        Returns
        -------
        :class:`pyaedt.modules.SolveSetup.SetupCircuit`
            Setup object.
        """
        if setuptype is None:
            setuptype = self.design_solutions.default_setup
        elif setuptype in SetupKeys.SetupNames:
            setuptype = SetupKeys.SetupNames.index(setuptype)
        name = self.generate_unique_setup_name(setupname)
        setup = SetupCircuit(self, setuptype, name)
        setup.create()
        setup.auto_update = False

        if "props" in kwargs:
            for el in kwargs["props"]:
                setup.props[el] = kwargs["props"][el]
        for arg_name, arg_value in kwargs.items():
            if arg_name == "props":
                continue
            if setup[arg_name] is not None:
                setup[arg_name] = arg_value
        setup.auto_update = True
        setup.update()
        self.setups.append(setup)
        return setup
