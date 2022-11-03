import copy
import warnings
from collections import OrderedDict

from pyaedt.application.Analysis import Analysis
from pyaedt.generic.general_methods import pyaedt_function_handler
from pyaedt.modeler.Circuit import ModelerNexxim
from pyaedt.modeler.Object3d import CircuitComponent
from pyaedt.modules.Boundary import BoundaryProps
from pyaedt.modules.PostProcessor import CircuitPostProcessor
from pyaedt.modules.SolveSetup import SetupCircuit


class FieldAnalysisCircuit(Analysis):
    """FieldCircuitAnalysis class.

    This class is for circuit analysis setup in Nexxim.

    It is automatically initialized by a call from an application,
    such as HFSS or Q3D. See the application function for its
    parameter definitions.

    Parameters
    ----------

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

        self._modeler = ModelerNexxim(self)
        self._post = CircuitPostProcessor(self)
        self._internal_excitations = None

    @pyaedt_function_handler()
    def push_down(self, component_name):
        """Push-down to the child component and reinitialize the Circuit object.

        Parameters
        ----------
        component_name : str or :class:`pyaedt.modeler.Object3d.CircuitComponent`
            Component to initialize.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.
        """
        out_name = ""
        if isinstance(component_name, CircuitComponent):
            out_name = self.design_name + ":" + component_name.component_info["RefDes"]
        elif "U" == component_name[0]:
            out_name = self.design_name + ":" + component_name
        elif ":" not in component_name:
            for v in self.modeler.components.components:
                if component_name == v.composed_name.split(";")[0].split("@")[1]:
                    out_name = self.design_name + ":" + v.component_info["RefDes"]
        else:
            out_name = component_name
        try:
            self.oproject.SetActiveDesign(out_name)
            self.__init__(projectname=self.project_name, designname=out_name)
        except:  # pragma: no cover
            return False
        return True

    @pyaedt_function_handler()
    def pop_up(self):
        """Pop-up to parent Circuit design and reinitialize Circuit object.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.
        """
        try:
            parent_name = self.odesign.GetName().split(";")[1].split("/")[0]
            self.oproject.SetActiveDesign(parent_name)
            self.__init__(projectname=self.project_name, designname=parent_name)
        except:
            return False
        return True

    @property
    def post(self):
        """Postprocessor.

        Returns
        -------
        :class:`pyaedt.modules.PostProcessor.CircuitPostProcessor`
            PostProcessor object.
        """
        return self._post

    @property
    def existing_analysis_sweeps(self):
        """Analysis setups.

        References
        ----------

        >>> oModule.GetAllSolutionSetups"""
        return self.existing_analysis_setups

    @property
    def existing_analysis_setups(self):
        """Analysis setups.

        References
        ----------

        >>> oModule.GetAllSolutionSetups"""
        setups = self.oanalysis.GetAllSolutionSetups()
        return setups

    @property
    def nominal_sweep(self):
        """Nominal sweep."""
        if self.existing_analysis_setups:
            return self.existing_analysis_setups[0]
        else:
            return ""

    @property
    def modeler(self):
        """Modeler object."""
        return self._modeler

    @property
    def setup_names(self):
        """Setup names.

        References
        ----------

        >>> oModule.GetAllSolutionSetups"""
        return self.oanalysis.GetAllSolutionSetups()

    @property
    def source_names(self):
        """Get all source names.

        Returns
        -------
        list
            List of source names.

        References
        ----------

        >>> oDesign.GetChildObject("Excitations").GetChildNames()
        """
        return list(self.odesign.GetChildObject("Excitations").GetChildNames())

    @property
    def sources(self):
        """Get all sources.

        Returns
        -------
        list
            List of sources.

        """
        props = {}
        for source in self.source_names:
            props[source] = Sources(self, source)
        return props

    @property
    def excitations_names(self):
        """Get all excitation names.

        Returns
        -------
        list
            List of excitation names. Excitations with multiple modes will return one
            excitation for each mode.

        References
        ----------

        >>> oModule.GetAllPorts
        """
        ports = [p.replace("IPort@", "").split(";")[0] for p in self.modeler.oeditor.GetAllPorts() if "IPort@" in p]
        return ports

    @property
    def excitations(self):
        """Get all ports.

        Returns
        -------
        list
            List of ports.

        """
        props = {}
        if not self._internal_excitations:
            for port in self.excitations_names:
                props[port] = Excitations(self, port)
            self._internal_excitations = props
        else:
            props = self._internal_excitations
            for port in self.excitations_names:
                if port not in props.keys():
                    index = [i for i, item in enumerate(self.excitations_names) if item not in list(props.keys())][0]
                    if index:
                        props[self.excitations_names[index]] = props[list(props.keys())[index]]
                        del props[list(props.keys())[index]]
        return props

    @property
    def get_excitations_name(self):
        """Excitation names.

        .. deprecated:: 0.4.27
           Use :func:`excitations` property instead.

        Returns
        -------
        type
            BoundarySetup Module object

        References
        ----------

        >>> oEditor.GetAllPorts
        """
        warnings.warn("`get_excitations_name` is deprecated. Use `excitations` property instead.", DeprecationWarning)
        return self.excitations

    @property
    def get_all_sparameter_list(self, excitation_names=[]):
        """List of all S parameters for a list of exctitations.

        Parameters
        ----------
        excitation_names : list, optional
            List of excitations. The default is ``[]``, in which case
            the S parameters for all excitations are to be provided.
            For example, ``["1", "2"]``.

        Returns
        -------
        list of str
            List of strings representing the S parameters of the excitations.
            For example, ``"S(1,1)", "S(1,2)", "S(2,2)"``.

        """
        if not excitation_names:
            excitation_names = self.excitations
        spar = []
        k = 0
        for i in excitation_names:
            k = excitation_names.index(i)
            while k < len(excitation_names):
                spar.append("S({},{})".format(i, excitation_names[k]))
                k += 1
        return spar

    @pyaedt_function_handler()
    def get_all_return_loss_list(self, excitation_names=None, excitation_name_prefix=""):
        """Retrieve a list of all return losses for a list of exctitations.

        Parameters
        ----------
        excitation_names : list, optional
            List of excitations. The default is ``None``, in which case
            the return losses for all excitations are to be provided.
            For example ``["1", "2"]``.
        excitation_name_prefix : string, optional
             Prefix to add to the excitation names. The default is ``""``,

        Returns
        -------
        list of str
            List of strings representing the return losses of the excitations.
            For example ``["S(1, 1)", S(2, 2)]``

        References
        ----------

        >>> oEditor.GetAllPorts
        """
        if excitation_names == None:
            excitation_names = []

        if not excitation_names:
            excitation_names = self.excitations
        if excitation_name_prefix:
            excitation_names = [i for i in excitation_names if excitation_name_prefix.lower() in i.lower()]
        spar = []
        for i in excitation_names:
            spar.append("S({},{})".format(i, i))
        return spar

    @pyaedt_function_handler()
    def get_all_insertion_loss_list(self, trlist=None, reclist=None, tx_prefix="", rx_prefix=""):
        """Retrieve a list of all insertion losses from two lists of excitations (driver and receiver).

        Parameters
        ----------
        trlist : list, optional
            List of drivers. The default is ``[]``. For example, ``["1"]``.
        reclist : list, optional
            List of receivers. The default is ``[]``. The number of drivers equals
            the number of receivers. For example, ``["2"]``.
        tx_prefix : str, optional
            Prefix to add to driver names. For example, ``"DIE"``. The default is ``""``.
        rx_prefix : str, optional
            Prefix to add to receiver names. For example, ``"BGA"``. The default is ``""``.

        Returns
        -------
        list of str
            List of strings representing insertion losses of the excitations.
            For example, ``["S(1,2)"]``.

        References
        ----------

        >>> oEditor.GetAllPorts
        """
        if trlist == None:
            trlist = []
        if reclist == None:
            reclist = []

        spar = []
        if not trlist:
            trlist = [i for i in self.excitations if tx_prefix in i]
        if not reclist:
            reclist = [i for i in self.excitations if rx_prefix in i]
        if len(trlist) != len(reclist):
            self.logger.error("The TX and RX lists should be the same length.")
            return False
        for i, j in zip(trlist, reclist):
            spar.append("S({},{})".format(i, j))
        return spar

    @pyaedt_function_handler()
    def get_next_xtalk_list(self, trlist=[], tx_prefix=""):
        """Retrieve a list of all the near end XTalks from a list of excitations (driver and receiver).

        Parameters
        ----------
        trlist : list, optional
            List of drivers. The default is ``[]``. For example,
            ``["1", "2", "3"]``.
        tx_prefix : str, optional
            Prefix to add to driver names. For example, ``"DIE"``.  The default is ``""``.

        Returns
        -------
        list of str
            List of strings representing near end XTalks of the excitations.
            For example, ``["S(1, 2)", "S(1, 3)", "S(2, 3)"]``.

        References
        ----------

        >>> oEditor.GetAllPorts
        """
        next = []
        if not trlist:
            trlist = [i for i in self.excitations if tx_prefix in i]
        for i in trlist:
            k = trlist.index(i) + 1
            while k < len(trlist):
                next.append("S({},{})".format(i, trlist[k]))
                k += 1
        return next

    @pyaedt_function_handler()
    def get_fext_xtalk_list(self, trlist=None, reclist=None, tx_prefix="", rx_prefix="", skip_same_index_couples=True):
        """Retrieve a list of all the far end XTalks from two lists of exctitations (driver and receiver).

        Parameters
        ----------
        trlist : list, optional
            List of drivers. The default is ``[]``. For example,
            ``["1", "2"]``.
        reclist : list, optional
            List of receiver. The default is ``[]``. For example,
            ``["3", "4"]``.
        tx_prefix : str, optional
            Prefix for driver names. For example, ``"DIE"``.  The default is ``""``.
        rx_prefix : str, optional
            Prefix for receiver names. For examples, ``"BGA"`` The default is ``""``.
        skip_same_index_couples : bool, optional
            Whether to skip driver and receiver couples with the same index position.
            The default is ``True``, in which case the drivers and receivers
            with the same index position are considered insertion losses and
            excluded from the list.

        Returns
        -------
        list of str
            List of strings representing the far end XTalks of the excitations.
            For example, ``["S(1, 4)", "S(2, 3)"]``.

        References
        ----------

        >>> oEditor.GetAllPorts
        """
        if trlist == None:
            trlist = []
        if reclist == None:
            reclist = []

        fext = []
        if not trlist:
            trlist = [i for i in self.excitations if tx_prefix in i]
        if not reclist:
            reclist = [i for i in self.excitations if rx_prefix in i]
        for i in trlist:
            for k in reclist:
                if not skip_same_index_couples or reclist.index(k) != trlist.index(i):
                    fext.append("S({},{})".format(i, k))
        return fext

    @pyaedt_function_handler()
    def get_setup(self, setupname):
        """Retrieve the setup from the current design.

        Parameters
        ----------
        setupname : str
            Name of the setup.

        Returns
        -------
        type
            Setup object.

        """
        setup = SetupCircuit(self, self.solution_type, setupname, isnewsetup=False)
        if setup.props:
            self.analysis_setup = setupname
        return setup

    @pyaedt_function_handler()
    def create_setup(self, setupname="MySetupAuto", setuptype=None, props={}):
        """Create a new setup.

        Parameters
        ----------
        setupname : str, optional
            Name of the new setup. The default is ``"MySetupAuto"``.
        setuptype : str, optional
            Type of the setup. The default is ``None``, in which case
            the default type is applied.
        props : dict, optional
            Dictionary of properties with values. The default is ``{}``.

        Returns
        -------
        SetupCircuit
            Setup object.

        References
        ----------

        >>> oModule.AddLinearNetworkAnalysis
        >>> oModule.AddDCAnalysis
        >>> oModule.AddTransient
        >>> oModule.AddQuickEyeAnalysis
        >>> oModule.AddVerifEyeAnalysis
        >>> oModule.AddAMIAnalysis
        """
        if setuptype is None:
            setuptype = self.solution_type

        name = self.generate_unique_setup_name(setupname)
        setup = SetupCircuit(self, setuptype, name)
        setup.create()
        if props:
            for el in props:
                setup.props._setitem_without_update(el, props[el])
            setup.update()
        self.analysis_setup = name
        self.setups.append(setup)
        return setup

    # @property
    # def mesh(self):
    #     return self._mesh
    #
    # @property
    # def post(self):
    #     return self._post


PowerSinusoidal = [
    "NAME:Name",
    "DataId:=",
    "",
    "Type:=",
    1,
    "Output:=",
    2,
    "NumPins:=",
    2,
    "Netlist:=",
    "",
    "CompName:=",
    "Nexxim Circuit Elements\\Independent Sources:P_SIN",
    "FDSFileName:=",
    "",
    "BtnPropFileName:=",
    "",
    [
        "NAME:Properties",
        "TextProp:=",
        ["LabelID", "HD", "Property string for netlist ID", "V@ID"],
        "ValueProp:=",
        ["ACMAG", "D", "AC magnitude for small-signal analysis (Volts)", "nan V", 0],
        "ValuePropNU:=",
        ["ACPHASE", "D", "AC phase for small-signal analysis", "1deg", 0, "deg", "AdditionalPropInfo:=", ""],
        "ValueProp:=",
        ["DC", "D", "DC voltage (Volts)", "2V", 0],
        "ValuePropNU:=",
        ["VO", "D", "Power offset from zero watts", "0W", 0, "W", "AdditionalPropInfo:=", ""],
        "ValueProp:=",
        ["POWER", "D", "Available power of the source above VO", "0W", 0],
        "ValueProp:=",
        ["FREQ", "D", "Frequency (Hz)", "1GHz", 0],
        "ValueProp:=",
        ["TD", "D", "Delay to start of sine wave (seconds)", "0s", 0],
        "ValueProp:=",
        ["ALPHA", "D", "Damping factor (1/seconds)", "0", 0],
        "ValuePropNU:=",
        ["THETA", "D", "Phase delay", "0deg", 0, "deg", "AdditionalPropInfo:=", ""],
        "ValueProp:=",
        [
            "TONE",
            "D",
            "Frequency (Hz) to use for harmonic balance analysis, should be a "
            "submultiple of (or equal to) the driving frequency and should also be "
            "included in the HB analysis setup",
            "0Hz",
            0,
        ],
        "TextProp:=",
        ["ModelName", "SHD", "", "P_SIN"],
        "ButtonProp:=",
        ["CosimDefinition", "D", "", "Edit", "Edit", 40501, "ButtonPropClientData:=", []],
        "MenuProp:=",
        ["CoSimulator", "D", "", "DefaultNetlist", 0],
    ],
]


class SourceKeys(object):
    """Provides source keys."""

    SourceTemplates = {
        "POWER SIN": PowerSinusoidal,
    }

    SourceNames = [
        "POWER SIN",
    ]


class Sources(object):
    """Manages Sources in Circuit Projects.

    Examples
    --------

    """

    def __init__(self, app, name):
        self._app = app
        self._name = name
        self.props = self.source_props(name)
        self.auto_update = True

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, source_name):
        if source_name not in self._app.source_names:
            if source_name != self._name:
                original_name = self._name
                self._name = source_name
                self.update(original_name)
        else:
            self._logger.warning("Name %s already assigned in the design", source_name)

    @property
    def _logger(self):
        """Logger."""
        return self._app.logger

    @pyaedt_function_handler()
    def source_props(self, source):
        source_aedt_props = self._app.odesign.GetChildObject("Excitations").GetChildObject(source)
        source_prop_dict = {}
        for el in source_aedt_props.GetPropNames():
            if el == "CosimDefinition":
                source_prop_dict[el] = None
            elif el != "Name":
                source_prop_dict[el] = source_aedt_props.GetPropValue(el)
        return BoundaryProps(self, OrderedDict(source_prop_dict))

    @pyaedt_function_handler()
    def _update_command(self, name, source_prop_dict):
        for source_type in SourceKeys.SourceNames:
            if source_type in source_prop_dict["Netlist"]:
                command_template = SourceKeys.SourceTemplates[source_type]
                commands = copy.deepcopy(command_template)
                commands[0] = "NAME:" + name
                commands[10] = source_prop_dict["Netlist"]
                cont = 0
                for command in commands[17:][0]:
                    if (
                        isinstance(command, list)
                        and command[0] in source_prop_dict.keys()
                        and command[0] != "CosimDefinition"
                    ):
                        # command_copy = command.copy()
                        commands[17:][0][cont][3] = source_prop_dict[command[0]]
                    cont += 1

                return commands

    @pyaedt_function_handler()
    def update(self, original_name=None):

        # id = self.modeler.schematic.create_unique_id()
        arg0 = ["NAME:Data"]
        for source in self._app.sources:
            if source == self.name:
                arg0.append(list(self._update_command(source, self.props)))
            elif source != self.name and original_name == source:
                arg0.append(list(self._update_command(self.name, self.props)))
            else:
                arg0.append(list(self._update_command(source, self._app.sources[source].props)))

        arg1 = ["NAME:NexximSources", ["NAME:NexximSources", arg0]]
        arg2 = ["NAME:ComponentConfigurationData"]

        # Check Ports with Sources
        arg3 = ["NAME:EnabledPorts"]
        for source_name in self._app.sources:
            arg3.append(source_name + ":=")
            arg3.append([])

        arg4 = ["NAME:EnabledMultipleComponents"]
        for source_name in self._app.sources:
            arg4.append(source_name + ":=")
            arg4.append([])
        arg5 = ["NAME:EnabledAnalyses"]
        arg6 = ["NAME:ComponentConfigurationData", arg3, arg4, arg5]
        arg2.append(arg6)

        self._app.odesign.UpdateSources(arg1, arg2)
        return True


class Excitations(object):
    """Manages Excitations in Circuit Projects.

    Examples
    --------

    """

    def __init__(self, app, name):
        self._app = app
        self._name = name
        self.props = self.excitation_props(name)
        self.auto_update = True

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, port_name):
        if port_name not in self._app.excitations_names:
            if port_name != self._name:
                # Take previous properties
                self._app.odesign.RenamePort(self._name, port_name)
                self._name = port_name
        else:
            self._logger.warning("Name %s already assigned in the design", port_name)

    @pyaedt_function_handler()
    def excitation_props(self, port):
        excitation_prop_dict = {}
        for comp in self._app.modeler.schematic.components:
            if (
                "PortName" in self._app.modeler.schematic.components[comp].parameters.keys()
                and self._app.modeler.schematic.components[comp].parameters["PortName"] == port
            ):

                excitation_prop_dict["rz"] = None
                excitation_prop_dict["iz"] = None
                excitation_prop_dict["one_port_impedance"] = None
                excitation_prop_dict["TerminationData"] = None
                if "term" in self._app.modeler.schematic.components[comp].parameters:
                    excitation_prop_dict["one_port_impedance"] = self._app.modeler.schematic.components[
                        comp
                    ].parameters["term"]
                    excitation_prop_dict["TerminationData"] = self._app.modeler.schematic.components[comp].parameters[
                        "TerminationData"
                    ]
                else:
                    excitation_prop_dict["rz"] = self._app.modeler.schematic.components[comp].parameters["rz"]
                    excitation_prop_dict["iz"] = self._app.modeler.schematic.components[comp].parameters["iz"]

                excitation_prop_dict["EnabledNoise"] = self._app.modeler.schematic.components[comp].parameters[
                    "EnableNoise"
                ]
                excitation_prop_dict["noisetemp"] = self._app.modeler.schematic.components[comp].parameters["noisetemp"]

                excitation_prop_dict["SymbolType"] = self._app.design_properties["NexximPorts"]["Data"][port][
                    "SymbolType"
                ]

                iport = self._app.design_properties["Circuit"]["IPort"]
                for p in iport:
                    if p["PortName"] == self.name:
                        excitation_prop_dict["RefNode"] = p["Properties"]["TextProp"][3]
                        break

                source_port = []
                enabled_ports = self._app.design_properties["ComponentConfigurationData"]["EnabledPorts"]
                if isinstance(enabled_ports, dict):
                    for source in enabled_ports:
                        if enabled_ports[source] and port in enabled_ports[source]:
                            source_port.append(source)
                excitation_prop_dict["EnabledPorts"] = source_port

                components_port = []
                multiple = self._app.design_properties["ComponentConfigurationData"]["EnabledMultipleComponents"]
                if isinstance(multiple, dict):
                    for source in multiple:
                        if multiple[source] and port in multiple[source]:
                            components_port.append(source)
                excitation_prop_dict["EnabledMultipleComponents"] = components_port

                port_analyses = {}
                enabled_analyses = self._app.design_properties["ComponentConfigurationData"]["EnabledAnalyses"]
                if isinstance(enabled_analyses, dict):
                    for source in enabled_analyses:
                        if enabled_analyses[source] and port in enabled_analyses[source]:
                            port_analyses[source] = enabled_analyses[source][port]
                excitation_prop_dict["EnabledAnalyses"] = port_analyses

                return BoundaryProps(self, OrderedDict(excitation_prop_dict))

        # source_prop_dict = {}
        # for el in source_aedt_props.GetPropNames():
        #     if el == "CosimDefinition":
        #         source_prop_dict[el] = None
        #     elif el != "Name":
        #         source_prop_dict[el] = source_aedt_props.GetPropValue(el)

    @property
    def _logger(self):
        """Logger."""
        return self._app.logger
