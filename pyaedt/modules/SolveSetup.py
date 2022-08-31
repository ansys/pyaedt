"""
This module contains these classes: `Setup`, `Setup3DLayout`, and `SetupCircuit`.

This module provides all functionalities for creating and editing setups in AEDT.
It is based on templates to allow for easy creation and modification of setup properties.

"""
from __future__ import absolute_import  # noreorder

import os.path
import warnings
from collections import OrderedDict

from pyaedt.generic.DataHandlers import _dict2arg
from pyaedt.generic.DataHandlers import _tuple2dict
from pyaedt.generic.general_methods import PropsManager
from pyaedt.generic.general_methods import generate_unique_name
from pyaedt.generic.general_methods import pyaedt_function_handler
from pyaedt.modules.SetupTemplates import SetupKeys
from pyaedt.modules.SetupTemplates import SetupProps
from pyaedt.modules.SetupTemplates import SweepHFSS
from pyaedt.modules.SetupTemplates import SweepHFSS3DLayout
from pyaedt.modules.SetupTemplates import SweepQ3D


class CommonSetup(PropsManager, object):
    def __init__(self, app, solutiontype, setupname="MySetupAuto", isnewsetup=True):
        self.auto_update = False
        self._app = None
        self.p_app = app
        if solutiontype is None:
            self.setuptype = self.p_app.design_solutions.default_setup
        elif isinstance(solutiontype, int):
            self.setuptype = solutiontype
        elif solutiontype in SetupKeys.SetupNames:
            self.setuptype = SetupKeys.SetupNames.index(solutiontype)
        else:
            self.setuptype = self.p_app.design_solutions._solution_options[solutiontype]["default_setup"]
        self._setupname = setupname
        self.props = {}
        self.sweeps = []
        self._init_props(isnewsetup)
        self.auto_update = True

    def __repr__(self):
        return "SetupName " + self.name + " with " + str(len(self.sweeps)) + " Sweeps"

    @pyaedt_function_handler()
    def _init_props(self, isnewsetup=False):
        if isnewsetup:
            setup_template = SetupKeys.SetupTemplates[self.setuptype]
            for t in setup_template:
                _tuple2dict(t, self.props)
            self.props = SetupProps(self, self.props)
        else:
            try:
                setups_data = self.p_app.design_properties["AnalysisSetup"]["SolveSetups"]
                if self.name in setups_data:
                    setup_data = setups_data[self.name]
                    if "Sweeps" in setup_data and self.setuptype not in [
                        0,
                        7,
                    ]:  # 0 and 7 represent setup HFSSDrivenAuto
                        if self.setuptype <= 4:
                            app = setup_data["Sweeps"]
                            app.pop("NextUniqueID", None)
                            app.pop("MoveBackForward", None)
                            app.pop("MoveBackwards", None)
                            for el in app:
                                if isinstance(app[el], (OrderedDict, dict)):
                                    self.sweeps.append(SweepHFSS(self, self.name, el, props=app[el]))

                        else:
                            app = setup_data["Sweeps"]
                            for el in app:
                                if isinstance(app[el], (OrderedDict, dict)):
                                    self.sweeps.append(SweepQ3D(self, self.name, el, props=app[el]))
                        setup_data.pop("Sweeps", None)
                    self.props = SetupProps(self, OrderedDict(setup_data))
            except:
                self.props = SetupProps(self, OrderedDict())

    @property
    def is_solved(self):
        """Verify if solutions are available for given setup.

        Returns
        -------
        bool
            `True` if solutions are available.
        """
        if self.p_app.design_solutions.default_adaptive:
            sol = self.p_app.post.reports_by_category.standard(
                setup_name="{} : {}".format(self.name, self.p_app.design_solutions.default_adaptive)
            )
        else:
            sol = self.p_app.post.reports_by_category.standard(setup_name=self.name)

        return True if sol.get_solution_data() else False

    @property
    def p_app(self):
        """Parent."""
        return self._app

    @p_app.setter
    def p_app(self, value):
        self._app = value

    @property
    def omodule(self):
        """Analysis module."""
        return self._app.oanalysis

    @property
    def name(self):
        """Name."""
        return self._setupname

    @name.setter
    def name(self, name):
        self._setupname = name
        self.props["Name"] = name


class Setup(CommonSetup):
    """Initializes, creates, and updates a 3D setup.

    Parameters
    ----------
    app : :class:`pyaedt.application.Analysis3D.FieldAnalysis3D`
        Inherited app object.
    solutiontype : int, str
        Type of the setup.
    setupname : str, optional
        Name of the setup. The default is ``"MySetupAuto"``.
    isnewsetup : bool, optional
        Whether to create the setup from a template. The default is ``True``.
        If ``False``, access is to the existing setup.

    """

    def __init__(self, app, solutiontype, setupname="MySetupAuto", isnewsetup=True):
        CommonSetup.__init__(self, app, solutiontype, setupname, isnewsetup)

    @pyaedt_function_handler()
    def create(self):
        """Add a new setup based on class settings in AEDT.

        Returns
        -------
        dict
            Dictionary of arguments.

        References
        ----------

        >>> oModule.InsertSetup
        """
        soltype = SetupKeys.SetupNames[self.setuptype]
        arg = ["NAME:" + self.name]
        _dict2arg(self.props, arg)
        self.omodule.InsertSetup(soltype, arg)
        return arg

    @pyaedt_function_handler()
    def update(self, update_dictionary=None):
        """Update the setup based on either the class argument or a dictionary.

        Parameters
        ----------
        update_dictionary : optional
            Dictionary to use to update the setup. The default is ``None``.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        References
        ----------

        >>> oModule.EditSetup
        """
        legacy_update = self.auto_update
        self.auto_update = False
        if update_dictionary:
            for el in update_dictionary:
                self.props[el] = update_dictionary[el]
        self.auto_update = legacy_update
        arg = ["NAME:" + self.name]
        _dict2arg(self.props, arg)

        self.omodule.EditSetup(self.name, arg)
        return True

    @pyaedt_function_handler()
    def delete(self):
        """Delete actual Setup.

        Returns
        -------
        bool
            `True` if setup is deleted. `False` if it failed.
        """

        self.omodule.DeleteSetups([self.name])
        self._app.setups.remove(self)
        return True

    @pyaedt_function_handler()
    def _expression_cache(
        self,
        expression_list,
        report_type_list,
        intrinsics_list,
        isconvergence_list,
        isrelativeconvergence,
        conv_criteria,
    ):
        """Retrieve data from the expression setup cache.

        Parameters
        ----------
        expressions_list : list
            List of formulas to retrieve.
        report_type_list : list
            List of report types for the expressions.
        intrinsics_list : list
            List of intrinsic expressions for the expressions.
        isconvergence_list : list
            List of Boolean values indicating whether the expressions are in
            the convergence criteria.
        isrelativeconvergence : bool

        conv_criteria:

        Returns
        -------
        list
            List of the data.

        """
        if isrelativeconvergence:
            userelative = 1
        else:
            userelative = 0

        list_data = ["NAME:ExpressionCache"]
        if type(expression_list) is list:
            i = 0
            while i < len(expression_list):
                expression = expression_list[i]
                name = expression.replace("(", "_") + "1"
                name = name.replace(")", "_")
                name = name.replace(" ", "_")
                name = name.replace(".", "_")
                name = name.replace("/", "_")
                name = name.replace("*", "_")
                name = name.replace("+", "_")
                name = name.replace("-", "_")
                if type(report_type_list) is list:
                    report_type = report_type_list[i]
                else:
                    report_type = report_type_list
                if type(isconvergence_list) is list:
                    isconvergence = isconvergence_list[i]
                else:
                    isconvergence = isconvergence_list
                if type(intrinsics_list) is list:
                    intrinsics = intrinsics_list[i]
                else:
                    intrinsics = intrinsics_list
                list_data.append(
                    [
                        "NAME:CacheItem",
                        "Title:=",
                        name,
                        "Expression:=",
                        expression,
                        "Intrinsics:=",
                        intrinsics,
                        "IsConvergence:=",
                        isconvergence,
                        "UseRelativeConvergence:=",
                        userelative,
                        "MaxConvergenceDelta:=",
                        conv_criteria,
                        "MaxConvergeValue:=",
                        str(conv_criteria),
                        "ReportType:=",
                        report_type,
                        ["NAME:ExpressionContext"],
                    ]
                )
                i += 1

        else:
            name = expression_list.replace("(", "") + "1"
            name = name.replace(")", "")
            name = name.replace(" ", "")
            name = name.replace(",", "_")
            list_data.append(
                [
                    "NAME:CacheItem",
                    "Title:=",
                    name,
                    "Expression:=",
                    expression_list,
                    "Intrinsics:=",
                    intrinsics_list,
                    "IsConvergence:=",
                    isconvergence_list,
                    "UseRelativeConvergence:=",
                    userelative,
                    "MaxConvergenceDelta:=",
                    conv_criteria,
                    "MaxConvergeValue:=",
                    str(conv_criteria),
                    "ReportType:=",
                    report_type_list,
                    ["NAME:ExpressionContext"],
                ]
            )

        return list_data

    @pyaedt_function_handler()
    def enable_expression_cache(
        self,
        expressions,
        report_type="Fields",
        intrinsics="",
        isconvergence=True,
        isrelativeconvergence=True,
        conv_criteria=1,
    ):
        """Enable an expression cache.

        Parameters
        ----------
        expressions : str or list
            One or more formulas to add to the expression cache.
        report_type : str or list, optional
            Type of the report for the expression. The default is ``Fields``. If a list of expressions
            is supplied, supply a corresponding list of report types.
        intrinsics : str or list, optional
            Intrinsic functions for the expressions. The default is ``""``. If a list of expressions
            is supplied, a corresponding list of intrinsic functions must be supplied.
        isconvergence : bool or str or list, optional
            Whether the expression is in the convergence criteria. The default is ``True``.
            If a list of expressions is supplied, a corresponding list of Boolean values must be
            supplied.
        isrelativeconvergence : bool, optional
            The default is ``True``.
        conv_criteria :
            The default is ``1``.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        References
        ----------

        >>> oModule.EditSetup
        """
        arg = ["NAME:" + self.name]
        _dict2arg(self.props, arg)
        expression_cache = self._expression_cache(
            expressions, report_type, intrinsics, isconvergence, isrelativeconvergence, conv_criteria
        )
        arg.append(expression_cache)
        self.omodule.EditSetup(self.name, arg)
        return True

    @pyaedt_function_handler()
    def add_derivatives(self, derivative_list):
        """Add derivatives to the setup.

        Parameters
        ----------
        derivative_list : list
            List of derivatives.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        References
        ----------

        >>> oModule.EditSetup
        """
        arg = ["NAME:" + self.name]
        _dict2arg(self.props, arg)
        arg.append("VariablesForDerivatives:=")
        arg.append(derivative_list)
        self.omodule.EditSetup(self.name, arg)
        return True

    @pyaedt_function_handler()
    def enable(self, setup_name=None):
        """Enable a setup.

        Parameters
        ----------
        setup_name : str, optional
            Name of the setup. The default is ``None``.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        References
        ----------

        >>> oModule.EditSetup
        """
        if not setup_name:
            setup_name = self.name

        self.omodule.EditSetup(setup_name, ["NAME:" + setup_name, "IsEnabled:=", True])
        return True

    @pyaedt_function_handler()
    def disable(self, setup_name=None):
        """Disable a setup.

        Parameters
        ----------
        setup_name : str, optional
            Name of the setup. The default is ``None``.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        References
        ----------

        >>> oModule.EditSetup
        """
        if not setup_name:
            setup_name = self.name

        self.omodule.EditSetup(setup_name, ["NAME:" + setup_name, "IsEnabled:", False])
        return True

    @pyaedt_function_handler()
    def add_sweep(self, sweepname=None, sweeptype="Interpolating"):
        """Add a sweep to the project.

        Parameters
        ----------
        sweepname : str, optional
            Name of the sweep. The default is ``None``.
        sweeptype : str, optional
            Type of the sweep. The default is ``"Interpolating"``.

        Returns
        -------
        :class:`pyaedt.modules.SetupTemplates.SweepHFSS` or :class:`pyaedt.modules.SetupTemplates.SweepQ3D`
            Sweep object.

        References
        ----------

        >>> oModule.InsertFrequencySweep
        """
        if not sweepname:
            sweepname = generate_unique_name("Sweep")
        if self.setuptype == 7:
            self._app.logger.warning("This method only applies to HFSS and Q3d. Use add_eddy_current_sweep method.")
            return False
        if self.setuptype <= 4:
            sweep_n = SweepHFSS(self, self.name, sweepname, sweeptype)
        else:
            sweep_n = SweepQ3D(self, self.name, sweepname, sweeptype)
        sweep_n.create()
        self.sweeps.append(sweep_n)
        return sweep_n

    @pyaedt_function_handler()
    def add_mesh_link(self, design_name, solution_name, parameters_dict, project_name="This Project*"):
        """Add a mesh link to another design.

        Parameters
        ----------
        design_name : str
            Name of the design.
        solution_name : str
            Name of the solution in the format ``"setupname : solutionname"``.
            Optionally use :attr:`appname.nominal_adaptive` to get the
            nominal adaptive or :attr:`appname.nominal_sweep` to get the
            nominal sweep.
        parameters_dict : dict
            Dictionary of the parameters. Optionally use
            :attr:`appname.available_variations.nominal_w_values_dict`
            to get the nominal values.
        project_name : str, optional
            Name of the project with the design. The default is ``"This Project*"``.
            However, you can supply the full path and name to another project.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        References
        ----------

        >>> oModule.EditSetup
        """
        meshlinks = self.props["MeshLink"]
        meshlinks["ImportMesh"] = True
        meshlinks["Project"] = project_name
        meshlinks["Product"] = "ElectronicsDesktop"
        meshlinks["Design"] = design_name
        meshlinks["Soln"] = solution_name
        meshlinks["Params"] = OrderedDict({})
        for el in parameters_dict:
            if el in list(self._app.available_variations.nominal_w_values_dict.keys()):
                meshlinks["Params"][el] = el
            else:
                meshlinks["Params"][el] = parameters_dict[el]
        meshlinks["ForceSourceToSolve"] = True
        meshlinks["PreservePartnerSoln"] = True
        meshlinks["PathRelativeTo"] = "TargetProject"
        meshlinks["ApplyMeshOp"] = True
        self.update()
        return True

    @pyaedt_function_handler()
    def add_eddy_current_sweep(self, range_type="LinearStep", start=0.1, end=100, count=0.1, units="Hz", clear=True):
        """Create a Maxwell Eddy Current Sweep.

        Parameters
        ----------
        range_type : str
            Type of the subrange. Options are ``"LinearCount"``,
            ``"LinearStep"``, ``"LogScale"`` and ``"SinglePoints"``.
        start : float
            Starting frequency.
        end : float, optional
            Stopping frequency. Required for ``rangetype="LinearCount"|"LinearStep"|"LogScale"``.
        count : int or float, optional
            Frequency count or frequency step. Required for ``rangetype="LinearCount"|"LinearStep"|"LogScale"``.
        units : str, optional
            Unit of the frequency. For example, ``"MHz`` or ``"GHz"``. The default is ``"Hz"``.

        clear : boolean, optional
            If set to ``True``, all other subranges will be suppressed except the current one under creation.
            Default value is ``False``.

        Returns
        -------
        bool
        """

        if self.setuptype != 7:
            self._app.logger.warning("This method only applies to Maxwell Eddy Current Solution.")
            return False
        legacy_update = self.auto_update
        self.auto_update = False
        props = OrderedDict()
        props["RangeType"] = range_type
        props["RangeStart"] = "{}{}".format(start, units)
        if range_type == "LinearStep":
            props["RangeEnd"] = "{}{}".format(end, units)
            props["RangeStep"] = "{}{}".format(count, units)
        elif range_type == "LinearCount":
            props["RangeEnd"] = "{}{}".format(end, units)
            props["RangeCount"] = count
        elif range_type == "LogScale":
            props["RangeEnd"] = "{}{}".format(end, units)
            props["RangeSamples"] = count
        elif range_type == "SinglePoints":
            props["RangeEnd"] = "{}{}".format(start, units)
        if clear:
            self.props["SweepRanges"]["Subrange"] = props
        elif isinstance(self.props["SweepRanges"]["Subrange"], list):
            self.props["SweepRanges"]["Subrange"].append(props)
        else:
            self.props["SweepRanges"]["Subrange"] = [self.props["SweepRanges"]["Subrange"], props]
        self.update()
        self.auto_update = legacy_update
        return True

    @pyaedt_function_handler()
    def enable_adaptive_setup_single(self, freq=None, max_passes=None, max_delta_s=None):
        """Enable HFSS single frequency setup.

        Parameters
        ----------
        freq : float, str, optional
            Frequency at which to set the adaptive convergence.
            The default is ``None`` which will not update the value in setup.
            You can enter a float value in (GHz) or a string.
        max_passes : int, optional
            Maximum number of adaptive passes. The default is ``None`` which will not update the value in setup.
        max_delta_s : float, optional
            Delta S convergence criteria. The default is ``None`` which will not update the value in setup.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.
        """
        if self.setuptype != 1 or self.p_app.solution_type not in ["Modal", "Terminal"]:
            self._app.logger.error("Method applies only to HFSS-driven solutions.")
            return False
        self.auto_update = False
        self.props["SolveType"] = "Single"
        if isinstance(freq, (int, float)):
            freq = "{}GHz".format(freq)
        if freq:
            self.props["Frequency"] = freq
        if max_passes:
            self.props["MaximumPasses"] = max_passes
        if max_delta_s:
            self.props["MaxDeltaS"] = max_delta_s
        self.auto_update = True
        return self.update()

    @pyaedt_function_handler()
    def enable_adaptive_setup_broadband(self, low_frequency, high_frquency, max_passes=6, max_delta_s=0.02):
        """Enable HFSS broadband setup.

        Parameters
        ----------
        low_frequency : float, str
            Lower Frequency at which set the adaptive convergence.
            It can be float (GHz) or str.
        high_frquency : float, str
            Lower Frequency at which set the adaptive convergence. It can be float (GHz) or str.
        max_passes : int, optional
            Maximum number of adaptive passes. The default is ``6``.
        max_delta_s : float, optional
            Delta S Convergence criteria. The default is ``0.02``.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.
        """
        if self.setuptype != 1 or self.p_app.solution_type not in ["Modal", "Terminal"]:
            self._app.logger.error("Method applies only to HFSS-driven solutions.")
            return False
        self.auto_update = False
        self.props["SolveType"] = "BroadBand"
        for el in list(self.props["MultipleAdaptiveFreqsSetup"].keys()):
            del self.props["MultipleAdaptiveFreqsSetup"][el]
        if isinstance(low_frequency, (int, float)):
            low_frequency = "{}GHz".format(low_frequency)
        if isinstance(high_frquency, (int, float)):
            high_frquency = "{}GHz".format(high_frquency)
        self.props["MultipleAdaptiveFreqsSetup"]["Low"] = low_frequency
        self.props["MultipleAdaptiveFreqsSetup"]["High"] = high_frquency
        self.props["MaximumPasses"] = max_passes
        self.props["MaxDeltaS"] = max_delta_s
        self.auto_update = True
        return self.update()

    @pyaedt_function_handler()
    def enable_adaptive_setup_multifrequency(self, frequencies, max_delta_s=0.02):
        """Enable HFSS multi-frequency setup.

        Parameters
        ----------
        frequencies : list
            Frequency at which to set the adaptive convergence. You can enter list entries
            as float values in GHz or as strings.
        max_delta_s : list, float
            Delta S convergence criteria. The default is ``0.02``.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.
        """
        if self.setuptype != 1 or self.p_app.solution_type not in ["Modal", "Terminal"]:
            self._app.logger.error("Method applies only to HFSS-driven solutions.")
            return False
        self.auto_update = False
        self.props["SolveType"] = "MultiFrequency"
        for el in list(self.props["MultipleAdaptiveFreqsSetup"].keys()):
            del self.props["MultipleAdaptiveFreqsSetup"][el]
        i = 0
        for f in frequencies:
            if isinstance(max_delta_s, float):
                if isinstance(f, (int, float)):
                    f = "{}GHz".format(f)
                self.props["MultipleAdaptiveFreqsSetup"][f] = [max_delta_s]
            else:
                if isinstance(f, (int, float)):
                    f = "{}GHz".format(f)
                try:
                    self.props["MultipleAdaptiveFreqsSetup"][f] = [max_delta_s[i]]
                except IndexError:
                    self.props["MultipleAdaptiveFreqsSetup"][f] = [0.02]
            i += 1
        self.auto_update = True
        return self.update()


class SetupCircuit(CommonSetup):
    """Initializes, creates, and updates a circuit setup.

    Parameters
    ----------
    app : :class:`pyaedt.application.AnalysisNexxim.FieldAnalysisCircuit`
        Inherited app object.
    solutiontype : str, int
        Type of the setup.
    setupname : str, optional
        Name of the setup. The default is ``"MySetupAuto"``.
    isnewsetup : bool, optional
      Whether to create the setup from a template. The default is ``True.``
      If ``False``, access is to the existing setup.

    """

    def __init__(self, app, solutiontype, setupname="MySetupAuto", isnewsetup=True):
        CommonSetup.__init__(self, app, solutiontype, setupname, isnewsetup)

    @pyaedt_function_handler()
    def _init_props(self, isnewsetup=False):
        props = {}
        if isnewsetup:
            setup_template = SetupKeys.SetupTemplates[self.setuptype]
            for t in setup_template:
                _tuple2dict(t, props)
            self.props = SetupProps(self, props)
        else:
            self.props = SetupProps(self, OrderedDict())
            try:
                setups_data = self.p_app.design_properties["SimSetups"]["SimSetup"]
                if type(setups_data) is not list:
                    setups_data = [setups_data]
                for setup in setups_data:
                    if self.name == setup["Name"]:
                        setup_data = setup
                        setup_data.pop("Sweeps", None)
                        self.props = SetupProps(self, setup_data)
            except:
                self.props = SetupProps(self, OrderedDict())
        self.props["Name"] = self.name

    @property
    def _odesign(self):
        """Design."""
        return self._app._odesign

    @pyaedt_function_handler()
    def create(self):
        """Add a new setup based on class settings in AEDT.

        Returns
        -------
        dict
            Dictionary of the arguments.

        References
        ----------

        >>> oModule.AddLinearNetworkAnalysis
        >>> oModule.AddDCAnalysis
        >>> oModule.AddTransient
        >>> oModule.AddQuickEyeAnalysis
        >>> oModule.AddVerifEyeAnalysis
        >>> oModule.AddAMIAnalysis
        """
        soltype = SetupKeys.SetupNames[self.setuptype]
        arg = ["NAME:SimSetup"]
        _dict2arg(self.props, arg)
        self._setup(soltype, arg)
        return arg

    @pyaedt_function_handler()
    def _setup(self, soltype, arg, newsetup=True):
        if newsetup:
            if soltype == "NexximLNA":
                self.omodule.AddLinearNetworkAnalysis(arg)
            elif soltype == "NexximDC":
                self.omodule.AddDCAnalysis(arg)
            elif soltype == "NexximTransient":
                self.omodule.AddTransient(arg)
            elif soltype == "NexximQuickEye":
                self.omodule.AddQuickEyeAnalysis(arg)
            elif soltype == "NexximVerifEye":
                self.omodule.AddVerifEyeAnalysis(arg)
            elif soltype == "NexximAMI":
                self.omodule.AddAMIAnalysis(arg)
            else:
                warnings.warn("Solution Not Implemented Yet")
        else:
            if soltype == "NexximLNA":
                self.omodule.EditLinearNetworkAnalysis(self.name, arg)
            elif soltype == "NexximDC":
                self.omodule.EditDCAnalysis(self.name, arg)
            elif soltype == "NexximTransient":
                self.omodule.EditTransient(self.name, arg)
            elif soltype == "NexximQuickEye":
                self.omodule.EditQuickEyeAnalysis(self.name, arg)
            elif soltype == "NexximVerifEye":
                self.omodule.EditVerifEyeAnalysis(self.name, arg)
            elif soltype == "NexximAMI":
                self.omodule.EditAMIAnalysis(self.name, arg)

            else:
                raise NotImplementedError("Solution type '{}' is not implemented yet".format(soltype))
        return True

    @pyaedt_function_handler()
    def update(self, update_dictionary=None):
        """Update the setup based on the class arguments or a dictionary.

        Parameters
        ----------
        update_dictionary : dict, optional
            Dictionary of settings to apply. The default is ``None``.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        References
        ----------

        >>> oModule.EditLinearNetworkAnalysis
        >>> oModule.EditDCAnalysis
        >>> oModule.EditTransient
        >>> oModule.EditQuickEyeAnalysis
        >>> oModule.EditVerifEyeAnalysis
        >>> oModule.EditAMIAnalysis
        """
        legacy_update = self.auto_update
        self.auto_update = False
        if update_dictionary:
            for el in update_dictionary:
                self.props[el] = update_dictionary[el]
        arg = ["NAME:SimSetup"]
        soltype = SetupKeys.SetupNames[self.setuptype]
        _dict2arg(self.props, arg)
        self._setup(soltype, arg, False)
        self.auto_update = legacy_update
        return True

    @pyaedt_function_handler()
    def add_sweep_points(self, sweep_variable="Freq", sweep_points=1, units="GHz", override_existing_sweep=True):
        """Add a linear count sweep to existing Circuit Setup.

        Parameters
        ----------
        sweep_variable : str, optional
            Variable to which the sweep belongs. Default is ``"Freq``.
        sweep_points : float or str or list, optional
            Sweep points to apply linear sweep. It can be a list or single points.
             Points can be float or str. If ``str`` then no units will be applied.
        end_point float or str, optional
            End Point of Linear Count sweep. If ``str`` then no units will be applied.
        units : str, optional
            Sweeps Units. It will be ignored if strings are provided as start_point or end_point
        override_existing_sweep : bool, optional
            Define if existing sweep on the same variable has to be overridden or kept and added to this new sweep.

        Returns
        -------
        bool
            ``True`` is succeeded.

        References
        ----------

        >>> oModule.EditLinearNetworkAnalysis
        >>> oModule.EditDCAnalysis
        >>> oModule.EditTransient
        >>> oModule.EditQuickEyeAnalysis
        >>> oModule.EditVerifEyeAnalysis
        >>> oModule.EditAMIAnalysis
        """
        if isinstance(sweep_points, (int, float)):
            sweep_points = [sweep_points]
        sweeps = []
        for el in sweep_points:

            if isinstance(el, (int, float)):
                sweeps.append(str(el) + units)
            else:
                sweeps.append(el)
        lin_data = " ".join(sweeps)
        return self._add_sweep(sweep_variable, lin_data, override_existing_sweep)

    @pyaedt_function_handler()
    def add_sweep_count(
        self,
        sweep_variable="Freq",
        start_point=1,
        end_point=100,
        count=100,
        units="GHz",
        count_type="Linear",
        override_existing_sweep=True,
    ):
        """Add a step sweep to existing Circuit Setup. It can be ``"Linear"``, ``"Decade"`` or ``"Octave"``.

        Parameters
        ----------
        sweep_variable : str, optional
            Variable to which the sweep belongs. Default is ``"Freq``.
        start_point : float or str, optional
            Start Point of Linear Count sweep. If ``str`` then no units will be applied.
        end_point : float or str, optional
            End Point of Linear Count sweep. If ``str`` then no units will be applied.
        count :  int, optional
            Number of points. Default is ``100``.
        units : str, optional
            Sweeps Units. It will be ignored if strings are provided as start_point or end_point.
        count_type : str, optional
            Count Type. Default is ``"Linear"``. It can be also ``"Decade"`` or ``"Octave"``.
        override_existing_sweep : bool, optional
            Define if existing sweep on the same variable has to be overridden or kept and added to this new sweep.

        Returns
        -------
        bool
            ``True`` is succeeded.

        References
        ----------

        >>> oModule.EditLinearNetworkAnalysis
        >>> oModule.EditDCAnalysis
        >>> oModule.EditTransient
        >>> oModule.EditQuickEyeAnalysis
        >>> oModule.EditVerifEyeAnalysis
        >>> oModule.EditAMIAnalysis
        """
        if isinstance(start_point, (int, float)):
            start_point = str(start_point) + units
        if isinstance(end_point, (int, float)):
            end_point = str(end_point) + units
        lin_in = "LINC"
        if count_type.lower() == "decade":
            lin_in = "DEC"
        elif count_type.lower() == "octave":
            lin_in = "OCT"
        lin_data = "{} {} {} {}".format(lin_in, start_point, end_point, count)
        return self._add_sweep(sweep_variable, lin_data, override_existing_sweep)

    @pyaedt_function_handler()
    def add_sweep_step(
        self,
        sweep_variable="Freq",
        start_point=1,
        end_point=100,
        step_size=1,
        units="GHz",
        override_existing_sweep=True,
    ):
        """Add a linear count sweep to existing Circuit Setup.

        Parameters
        ----------
        sweep_variable : str, optional
            Variable to which the sweep belongs. Default is ``"Freq``.
        start_point : float or str, optional
            Start Point of Linear Count sweep. If ``str`` then no units will be applied.
        end_point : float or str, optional
            End Point of Linear Count sweep. If ``str`` then no units will be applied.
        step_size :  float or str, optional
            Step Size of sweep. If ``str`` then no units will be applied.
        units : str, optional
            Sweeps Units. It will be ignored if strings are provided as start_point or end_point
        override_existing_sweep : bool, optional
            Define if existing sweep on the same variable has to be overridden or kept and added to this new sweep.

        Returns
        -------
        bool
            ``True`` is succeeded.

        References
        ----------

        >>> oModule.EditLinearNetworkAnalysis
        >>> oModule.EditDCAnalysis
        >>> oModule.EditTransient
        >>> oModule.EditQuickEyeAnalysis
        >>> oModule.EditVerifEyeAnalysis
        >>> oModule.EditAMIAnalysis
        """
        if isinstance(start_point, (int, float)):
            start_point = str(start_point) + units
        if isinstance(end_point, (int, float)):
            end_point = str(end_point) + units
        if isinstance(step_size, (int, float)):
            step_size = str(step_size) + units
        linc_data = "LIN {} {} {}".format(start_point, end_point, step_size)
        return self._add_sweep(sweep_variable, linc_data, override_existing_sweep)

    @pyaedt_function_handler()
    def _add_sweep(self, sweep_variable, equation, override_existing_sweep):
        if isinstance(self.props["SweepDefinition"], list):
            for sw in self.props["SweepDefinition"]:
                if sw["Variable"] == sweep_variable:
                    if override_existing_sweep:
                        sw["Data"] = equation
                    else:
                        sw["Data"] += " " + equation
                    return self.update()
        elif self.props["SweepDefinition"]["Variable"] == sweep_variable:
            if override_existing_sweep:
                self.props["SweepDefinition"]["Data"] = equation
            else:
                self.props["SweepDefinition"]["Data"] += " " + equation
            return self.update()
        if isinstance(self.props["SweepDefinition"], (OrderedDict, dict)):
            self.props["SweepDefinition"] = [self.props["SweepDefinition"]]
        prop = OrderedDict({"Variable": sweep_variable, "Data": equation, "OffsetF1": False, "Synchronize": 0})
        self.props["SweepDefinition"].append(prop)
        return self.update()

    @pyaedt_function_handler()
    def _expression_cache(
        self,
        expression_list,
        report_type_list,
        intrinsics_list,
        isconvergence_list,
        isrelativeconvergence,
        conv_criteria,
    ):
        """Retrieve data from the expression setup cache.

        Parameters
        ----------
        expressions_list : list
            List of formulas to retrieve.
        report_type_list : list
            List of report types for the expressions.
        intrinsics_list : list
            List of intrinsic functions for the expressions.
        isconvergence_list : list
            List of Boolean values indicating whether the expressions are in
            the convergence criteria.
        isrelativeconvergence :

        conv_criteria:

        Returns
        -------
        list
            List of the data.

        """

        if isrelativeconvergence:
            userelative = 1
        else:
            userelative = 0

        list_data = ["NAME:ExpressionCache"]
        if type(expression_list) is list:
            i = 0
            while i < len(expression_list):
                expression = expression_list[i]
                name = expression.replace("(", "_") + "1"
                name = name.replace(")", "_")
                name = name.replace(" ", "_")
                if type(report_type_list) is list:
                    report_type = report_type_list[i]
                else:
                    report_type = report_type_list
                if type(isconvergence_list) is list:
                    isconvergence = isconvergence_list[i]
                else:
                    isconvergence = isconvergence_list
                if type(intrinsics_list) is list:
                    intrinsics = intrinsics_list[i]
                else:
                    intrinsics = intrinsics_list
                list_data.append(
                    [
                        "NAME:CacheItem",
                        "Title:=",
                        name,
                        "Expression:=",
                        expression,
                        "Intrinsics:=",
                        intrinsics,
                        "IsConvergence:=",
                        isconvergence,
                        "UseRelativeConvergence:=",
                        1,
                        "MaxConvergenceDelta:=",
                        1,
                        "MaxConvergeValue:=",
                        "0.01",
                        "ReportType:=",
                        report_type,
                        ["NAME:ExpressionContext"],
                    ]
                )
                i += 1

        else:
            name = expression_list.replace("(", "") + "1"
            name = name.replace(")", "")
            name = name.replace(" ", "")
            name = name.replace(",", "_")
            list_data.append(
                [
                    "NAME:CacheItem",
                    "Title:=",
                    name,
                    "Expression:=",
                    expression_list,
                    "Intrinsics:=",
                    intrinsics_list,
                    "IsConvergence:=",
                    isconvergence_list,
                    "UseRelativeConvergence:=",
                    userelative,
                    "MaxConvergenceDelta:=",
                    conv_criteria,
                    "MaxConvergeValue:=",
                    str(conv_criteria),
                    "ReportType:=",
                    report_type_list,
                    ["NAME:ExpressionContext"],
                ]
            )

        return list_data

    @pyaedt_function_handler()
    def enable_expression_cache(
        self,
        expressions,
        report_type="Fields",
        intrinsics="",
        isconvergence=True,
        isrelativeconvergence=True,
        conv_criteria=1,
    ):
        """Enable a setup expression cache.

        Parameters
        ----------
        expressions : str or list
            One or more formulas to add to the expression cache.
        report_type : str or list, optional
            Type of the report for the expression. The default is ``"Fields"``. If a list of expressions
            is supplied, a corresponding list of report types must be supplied.
        intrinsics : str or list, optional
            Intrinsic functions for the expressions. The default is ``""``. If a list of expressions
            is supplied, a corresponding list of intrinsic expressesions must be supplied.
        isconvergence : bool, str, or list, optional
            Whether the expression is in the convergence criteria. The  default is ``True``.
            If a list of expressions is supplied, a corresponding list of Boolean values must be
            supplied.
        isrelativeconvergence : bool, optional
            The default is ``True``.
        conv_criteria
            The default is ``1``.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        References
        ----------

        >>> oModule.EditSetup
        """
        arg = ["Name:SimSetup"]
        _dict2arg(self.props, arg)
        expression_cache = self._expression_cache(
            expressions, report_type, intrinsics, isconvergence, isrelativeconvergence, conv_criteria
        )
        arg.append(expression_cache)
        self.omodule.EditSetup(self.name, arg)
        return True

    @pyaedt_function_handler()
    def add_derivatives(self, derivative_list):
        """Add derivatives to the setup.

        Parameters
        ----------
        derivative_list : list
            List of derivatives.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        References
        ----------

        >>> oModule.EditSetup
        """
        arg = ["Name:SimSetup"]
        _dict2arg(self.props, arg)
        arg.append("VariablesForDerivatives:=")
        arg.append(derivative_list)
        self.omodule.EditSetup(self.name, arg)
        return True

    @pyaedt_function_handler()
    def enable(self, setup_name=None):
        """Enable a setup.

        Parameters
        ----------
        setup_name : str, optional
            Name of the setup. The default is ``None``.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        References
        ----------

        >>> oModule.EditSetup
        """
        if not setup_name:
            setup_name = self.name
        self._odesign.EnableSolutionSetup(setup_name, True)
        return True

    @pyaedt_function_handler()
    def disable(self, setup_name=None):
        """Disable a setup.

        Parameters
        ----------
        setup_name : str, optional
            Name of the setup. The default is ``None``.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        References
        ----------

        >>> oModule.EditSetup
        """
        if not setup_name:
            setup_name = self.name
        self._odesign.EnableSolutionSetup(setup_name, False)
        return True


class Setup3DLayout(CommonSetup):
    """Initializes, creates, and updates a 3D Layout setup.

    Parameters
    ----------
    app : :class:`pyaedt.application.Analysis3DLayout.FieldAnalysis3DLayout`
        Inherited app object.
    solutiontype : int or str
        Type of the setup.
    setupname : str, optional
        Name of the setup. The default is ``"MySetupAuto"``.
    isnewsetup : bool, optional
        Whether to create the setup from a template. The default is ``True.``
        If ``False``, access is to the existing setup.

    """

    def __init__(self, app, solutiontype, setupname="MySetupAuto", isnewsetup=True):
        CommonSetup.__init__(self, app, solutiontype, setupname, isnewsetup)

    @pyaedt_function_handler()
    def _init_props(self, isnewsetup=False):
        if isnewsetup:
            setup_template = SetupKeys.SetupTemplates[self.setuptype]
            for t in setup_template:
                _tuple2dict(t, self.props)
            self.props = SetupProps(self, self.props)
        else:
            try:
                setups_data = self._app.design_properties["Setup"]["Data"]
                if self.name in setups_data:
                    setup_data = setups_data[self.name]
                    if "Data" in setup_data:  # 0 and 7 represent setup HFSSDrivenAuto
                        app = setup_data["Data"]
                        for el in app:
                            if isinstance(app[el], (OrderedDict, dict)):
                                self.sweeps.append(SweepHFSS3DLayout(self, self.name, el, props=app[el]))

                    self.props = SetupProps(self, OrderedDict(setup_data))
            except:
                self.props = SetupProps(self, OrderedDict())

    @property
    def is_solved(self):
        """Verify if solutions are available for a given setup.

        Returns
        -------
        bool
            `True` if solutions are available.
        """
        if self.props.get("SolveSetupType", "HFSS") == "HFSS":
            sol = self._app.post.reports_by_category.standard(setup_name="{} : Last Adaptive".format(self.name))
        else:
            sol = self._app.post.reports_by_category.standard(setup_name=self.name)

        return True if sol.get_solution_data() else False

    @property
    def solver_type(self):
        """Setup type.

        Returns
        -------
        type
            Setup type.
        """

        if "SolveSetupType" in self.props:
            return self.props["SolveSetupType"]
        else:
            return None

    @pyaedt_function_handler()
    def create(self):
        """Add a new setup based on class settings in AEDT.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        References
        ----------

        >>> oModule.Add
        """
        arg = ["NAME:" + self.name]
        _dict2arg(self.props, arg)
        self.omodule.Add(arg)
        return True

    @pyaedt_function_handler()
    def update(self, update_dictionary=None):
        """Update the setup based on the class arguments or a dictionary.

        Parameters
        ----------
        update_dictionary : dict, optional
            Dictionary of settings to apply.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        References
        ----------

        >>> oModule.Edit
        """
        if update_dictionary:
            for el in update_dictionary:
                self.props._setitem_without_update(el, update_dictionary[el])
        arg = ["NAME:" + self.name]
        _dict2arg(self.props, arg)
        self.omodule.Edit(self.name, arg)
        return True

    @pyaedt_function_handler()
    def enable(self):
        """Enable a setup.

        Parameters
        ----------
        setup_name : str, optional
            Name of the setup.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        References
        ----------

        >>> oModule.Edit
        """
        self.props["Properties"]["Enable"] = "true"
        self.update()
        return True

    @pyaedt_function_handler()
    def disable(self):
        """Disable a setup.

        Parameters
        ----------
        setup_name : str, optional
            Name of the setup.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        References
        ----------

        >>> oModule.Edit
        """
        self.props["Properties"]["Enable"] = "false"
        self.update()
        return True

    @pyaedt_function_handler()
    def export_to_hfss(self, file_fullname):
        """Export the project to a file.

        Parameters
        ----------
        file_fullname : str
            Full path and file name for exporting the project.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        References
        ----------

        >>> oModule.ExportToHfss
        """

        file_fullname = file_fullname
        if not os.path.isdir(os.path.dirname(file_fullname)):
            return False
        file_fullname = os.path.splitext(file_fullname)[0] + ".aedt"
        self.omodule.ExportToHfss(self.name, file_fullname)
        return True

    @pyaedt_function_handler()
    def add_sweep(self, sweepname=None, sweeptype="Interpolating"):
        """Add a frequency sweep.

        Parameters
        ----------
        sweepname : str, optional
            Name of the sweep. The default is ``None``.
        sweeptype : str, optional
            Type of the sweep. Options are ``"Interpolating"`` and ``"Discrete"``.
            The default is ``"Interpolating"``.

        Returns
        -------
        :class:`pyaedt.modules.SetupTemplates.SweepHFSS3DLayout`
            Sweep object.

        References
        ----------

        >>> oModule.AddSweep
        """
        if not sweepname:
            sweepname = generate_unique_name("Sweep")
        sweep_n = SweepHFSS3DLayout(self, self.name, sweepname, sweeptype)
        if sweep_n.create():
            self.sweeps.append(sweep_n)
            return sweep_n
        return False


class SetupHFSS(Setup, object):
    """Initializes, creates, and updates an HFSS setup.

    Parameters
    ----------
    app : :class:`pyaedt.application.Analysis3D.FieldAnalysis3D`
        Inherited app object.
    solutiontype : int, str
        Type of the setup.
    setupname : str, optional
        Name of the setup. The default is ``"MySetupAuto"``.
    isnewsetup : bool, optional
        Whether to create the setup from a template. The default is ``True``.
        If ``False``, access is to the existing setup.

    """

    def __init__(self, app, solutiontype, setupname="MySetupAuto", isnewsetup=True):
        Setup.__init__(self, app, solutiontype, setupname, isnewsetup)

    @pyaedt_function_handler()
    def create_linear_count_sweep(
        self,
        unit,
        freqstart,
        freqstop,
        num_of_freq_points,
        sweepname=None,
        save_fields=True,
        save_rad_fields=False,
        sweep_type="Discrete",
        interpolation_tol=0.5,
        interpolation_max_solutions=250,
    ):
        """Create a sweep with the specified number of points.

        Parameters
        ----------
        unit : str
            Frequency Units.
        freqstart : float
            Starting frequency of the sweep, such as ``1``.
        freqstop : float
            Stopping frequency of the sweep.
        num_of_freq_points : int
            Number of frequency points in the range.
        sweepname : str, optional
            Name of the sweep. The default is ``None``.
        save_fields : bool, optional
            Whether to save the fields. The default is ``True``.
        save_rad_fields : bool, optional
            Whether to save the radiating fields. The default is ``False``.
        sweep_type : str, optional
            Type of the sweep. Options are ``"Fast"``, ``"Interpolating"``,
            and ``"Discrete"``. The default is ``"Discrete"``.
        interpolation_tol : float, optional
            Error tolerance threshold for the interpolation
            process. The default is ``0.5``.
        interpolation_max_solutions : int, optional
            Maximum number of solutions evaluated for the interpolation process.
            The default is ``250``.

        Returns
        -------
        :class:`pyaedt.modules.SetupTemplates.SweepHFSS` or bool
            Sweep object if successful, ``False`` otherwise.

        References
        ----------

        >>> oModule.InsertFrequencySweep

        Examples
        --------

        Create a setup named ``"LinearCountSetup"`` and use it in a linear count sweep
        named ``"LinearCountSweep"``.

        >>> setup = hfss.create_setup("LinearCountSetup")
        >>> linear_count_sweep = hfss.create_linear_count_sweep(setupname="LinearCountSetup",
        ...                                                     sweepname="LinearCountSweep",
        ...                                                     unit="MHz", freqstart=1.1e3,
        ...                                                     freqstop=1200.1, num_of_freq_points=1658)
        >>> type(linear_count_sweep)
        <class 'pyaedt.modules.SetupTemplates.SweepHFSS'>

        """
        if sweep_type not in ["Discrete", "Interpolating", "Fast"]:
            raise AttributeError("Invalid in `sweep_type`. It has to be either 'Discrete', 'Interpolating', or 'Fast'")

        if sweepname is None:
            sweepname = generate_unique_name("Sweep")

        if sweepname in [sweep.name for sweep in self.sweeps]:
            oldname = sweepname
            sweepname = generate_unique_name(oldname)
            self.logger.warning("Sweep %s is already present. Sweep has been renamed in %s.", oldname, sweepname)
        sweepdata = self.add_sweep(sweepname, sweep_type)
        if not sweepdata:
            return False
        sweepdata.props["RangeType"] = "LinearCount"
        sweepdata.props["RangeStart"] = str(freqstart) + unit
        sweepdata.props["RangeEnd"] = str(freqstop) + unit
        sweepdata.props["RangeCount"] = num_of_freq_points
        sweepdata.props["Type"] = sweep_type
        if sweep_type == "Interpolating":
            sweepdata.props["InterpTolerance"] = interpolation_tol
            sweepdata.props["InterpMaxSolns"] = interpolation_max_solutions
            sweepdata.props["InterpMinSolns"] = 0
            sweepdata.props["InterpMinSubranges"] = 1
        sweepdata.props["SaveFields"] = save_fields
        sweepdata.props["SaveRadFields"] = save_rad_fields
        sweepdata.update()
        self.logger.info("Linear count sweep {} has been correctly created".format(sweepname))
        return sweepdata

    @pyaedt_function_handler()
    def create_linear_step_sweep(
        self,
        setupname,
        unit,
        freqstart,
        freqstop,
        step_size,
        sweepname=None,
        save_fields=True,
        save_rad_fields=False,
        sweep_type="Discrete",
    ):
        """Create a Sweep with a specified frequency step.

        References
        ----------

        >>> oModule.InsertFrequencySweep

        Parameters
        ----------
        setupname : str
            Name of the setup.
        unit : str
            Unit of the frequency. For example, ``"MHz`` or ``"GHz"``.
        freqstart : float
            Starting frequency of the sweep.
        freqstop : float
            Stopping frequency of the sweep.
        step_size : float
            Frequency size of the step.
        sweepname : str, optional
            Name of the sweep. The default is ``None``.
        save_fields : bool, optional
            Whether to save the fields. The default is ``True``.
        save_rad_fields : bool, optional
            Whether to save the radiating fields. The default is ``False``.
        sweep_type : str, optional
            Whether to create a ``"Discrete"``,``"Interpolating"`` or ``"Fast"`` sweep.
            The default is ``"Discrete"``.

        Returns
        -------
        :class:`pyaedt.modules.SetupTemplates.SweepHFSS` or bool
            Sweep object if successful, ``False`` otherwise.

        Examples
        --------

        Create a setup named ``"LinearStepSetup"`` and use it in a linear step sweep
        named ``"LinearStepSweep"``.

        >>> setup = hfss.create_setup("LinearStepSetup")
        >>> linear_step_sweep = hfss.create_linear_step_sweep(setupname="LinearStepSetup",
        ...                                                   sweepname="LinearStepSweep",
        ...                                                   unit="MHz", freqstart=1.1e3,
        ...                                                   freqstop=1200.1, step_size=153.8)
        >>> type(linear_step_sweep)
        <class 'pyaedt.modules.SetupTemplates.SweepHFSS'>

        """
        if sweep_type not in ["Discrete", "Interpolating", "Fast"]:
            raise AttributeError("Invalid in `sweep_type`. It has to either 'Discrete', 'Interpolating', or 'Fast'")
        if sweepname is None:
            sweepname = generate_unique_name("Sweep")

        if setupname not in self.setup_names:
            return False
        for s in self.setups:
            if s.name == setupname:
                setupdata = s
                if sweepname in [sweep.name for sweep in setupdata.sweeps]:
                    oldname = sweepname
                    sweepname = generate_unique_name(oldname)
                    self.logger.warning(
                        "Sweep %s is already present. Sweep has been renamed in %s.", oldname, sweepname
                    )
                sweepdata = setupdata.add_sweep(sweepname, sweep_type)
                if not sweepdata:
                    return False
                sweepdata.props["RangeType"] = "LinearStep"
                sweepdata.props["RangeStart"] = str(freqstart) + unit
                sweepdata.props["RangeEnd"] = str(freqstop) + unit
                sweepdata.props["RangeStep"] = str(step_size) + unit
                sweepdata.props["SaveFields"] = save_fields
                sweepdata.props["SaveRadFields"] = save_rad_fields
                sweepdata.props["ExtrapToDC"] = False
                sweepdata.props["Type"] = sweep_type
                if sweep_type == "Interpolating":
                    sweepdata.props["InterpTolerance"] = 0.5
                    sweepdata.props["InterpMaxSolns"] = 250
                    sweepdata.props["InterpMinSolns"] = 0
                    sweepdata.props["InterpMinSubranges"] = 1
                sweepdata.update()
                self.logger.info("Linear step sweep {} has been correctly created".format(sweepname))
                return sweepdata
        return False

    @pyaedt_function_handler()
    def create_single_point_sweep(
        self,
        setupname,
        unit,
        freq,
        sweepname=None,
        save_single_field=True,
        save_fields=False,
        save_rad_fields=False,
    ):
        """Create a Sweep with a single frequency point.

        Parameters
        ----------
        setupname : str
            Name of the setup.
        unit : str
            Unit of the frequency. For example, ``"MHz`` or ``"GHz"``.
        freq : float, list
            Frequency of the single point or list of frequencies to create distinct single points.
        sweepname : str, optional
            Name of the sweep. The default is ``None``.
        save_single_field : bool, list, optional
            Whether to save the fields of the single point. The default is ``True``.
            If a list is specified, the length must be the same as freq length.
        save_fields : bool, optional
            Whether to save the fields for all points and subranges defined in the sweep. The default is ``False``.
        save_rad_fields : bool, optional
            Whether to save only the radiating fields. The default is ``False``.

        Returns
        -------
        :class:`pyaedt.modules.SetupTemplates.SweepHFSS` or bool
            Sweep object if successful, ``False`` otherwise.

        References
        ----------

        >>> oModule.InsertFrequencySweep

        Examples
        --------

        Create a setup named ``"LinearStepSetup"`` and use it in a single point sweep
        named ``"SinglePointSweep"``.

        >>> setup = hfss.create_setup("LinearStepSetup")
        >>> single_point_sweep = hfss.create_single_point_sweep(setupname="LinearStepSetup",
        ...                                                   sweepname="SinglePointSweep",
        ...                                                   unit="MHz", freq=1.1e3)
        >>> type(single_point_sweep)
        <class 'pyaedt.modules.SetupTemplates.SweepHFSS'>

        """
        if sweepname is None:
            sweepname = generate_unique_name("SinglePoint")

        if isinstance(save_single_field, list):
            if not isinstance(freq, list) or len(save_single_field) != len(freq):
                raise AttributeError("The length of save_single_field must be the same as freq length.")

        add_subranges = False
        if isinstance(freq, list):
            if not freq:
                raise AttributeError("Frequency list is empty! Specify at least one frequency point.")
            freq0 = freq.pop(0)
            if freq:
                add_subranges = True
        else:
            freq0 = freq

        if isinstance(save_single_field, list):
            save0 = save_single_field.pop(0)
        else:
            save0 = save_single_field
            if add_subranges:
                save_single_field = [save0] * len(freq)

        if setupname not in self.setup_names:
            return False
        for s in self.setups:
            if s.name == setupname:
                setupdata = s
                if sweepname in [sweep.name for sweep in setupdata.sweeps]:
                    oldname = sweepname
                    sweepname = generate_unique_name(oldname)
                    self.logger.warning(
                        "Sweep %s is already present. Sweep has been renamed in %s.", oldname, sweepname
                    )
                sweepdata = setupdata.add_sweep(sweepname, "Discrete")
                sweepdata.props["RangeType"] = "SinglePoints"
                sweepdata.props["RangeStart"] = str(freq0) + unit
                sweepdata.props["RangeEnd"] = str(freq0) + unit
                sweepdata.props["SaveSingleField"] = save0
                sweepdata.props["SaveFields"] = save_fields
                sweepdata.props["SaveRadFields"] = save_rad_fields
                sweepdata.props["SMatrixOnlySolveMode"] = "Auto"
                if add_subranges:
                    for f, s in zip(freq, save_single_field):
                        sweepdata.add_subrange(rangetype="SinglePoints", start=f, unit=unit, save_single_fields=s)
                sweepdata.update()
                self.logger.info("Single point sweep {} has been correctly created".format(sweepname))
                return sweepdata
        return False
