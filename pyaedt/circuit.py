# -*- coding: utf-8 -*-
"""This module contains the `Circuit` class."""

from __future__ import absolute_import

import math
import os
import re

from pyaedt.application.AnalysisNexxim import FieldAnalysisCircuit
from pyaedt.generic.DataHandlers import from_rkm_to_aedt
from pyaedt.generic.general_methods import aedt_exception_handler


class Circuit(FieldAnalysisCircuit, object):
    """Provides the Circuit application interface.

    Parameters
    ----------
    projectname : str, optional
        Name of the project to select or the full path to the project
        or AEDTZ archive to open.  The default is ``None``, in which
        case an attempt is made to get an active project. If no
        projects are present, an empty project is created.
    designname : str, optional
        Name of the design to select. The default is ``None``, in
        which case an attempt is made to get an active design. If no
        designs are present, an empty design is created.
    solution_type : str, optional
        Solution type to apply to the design. The default is
        ``None``, in which case the default type is applied.
    setup_name : str, optional
        Name of the setup to use as the nominal. The default is
        ``None``, in which case the active setup is used or
        nothing is used.
    specified_version : str, optional
        Version of AEDT to use. The default is ``None``, in which case
        the active version or latest installed version is  used.
        This parameter is ignored when Script is launched within AEDT.
    NG : bool, optional
        Whether to run AEDT in the non-graphical mode. The default
        is``False``, in which case AEDT is launched in the graphical mode.
        This parameter is ignored when Script is launched within AEDT.
    new_desktop_session : bool, optional
        Whether to launch an instance of AEDT in a new thread, even if
        another instance of the ``specified_version`` is active on the
        machine.  The default is ``True``. This parameter is ignored when Script is launched within AEDT.
    close_on_exit : bool, optional
        Whether to release AEDT on exit.
    student_version : bool, optional
        Whether to open the AEDT student version. The default is ``False``.
        This parameter is ignored when Script is launched within AEDT.

    Examples
    --------
    Create an instance of Circuit and connect to an existing HFSS
    design or create a new HFSS design if one does not exist.

    >>> from pyaedt import Circuit
    >>> aedtapp = Circuit()

    Create an instance of Circuit and link to a project named
    ``"projectname"``. If this project does not exist, create one with
    this name.

    >>> aedtapp = Circuit(projectname)

    Create an instance of Circuit and link to a design named
    ``"designname"`` in a project named ``"projectname"``.

    >>> aedtapp = Circuit(projectname,designame)

    Create an instance of Circuit and open the specified project,
    which is ``"myfie.aedt"``.

    >>> aedtapp = Circuit("myfile.aedt")

    Create an instance of Circuit using the 2021 R1 version and
    open the specified project, which is ``"myfile.aedt"``.

    >>> aedtapp = Circuit(specified_version="2021.2", projectname="myfile.aedt")

    Create an instance of Circuit using the 2021 R2 student version and open
    the specified project, which is named ``"myfile.aedt"``.

    >>> hfss = Circuit(specified_version="2021.2", projectname="myfile.aedt", student_version=True)

    """

    def __init__(
        self,
        projectname=None,
        designname=None,
        solution_type=None,
        setup_name=None,
        specified_version=None,
        non_graphical=False,
        new_desktop_session=False,
        close_on_exit=False,
        student_version=False,
    ):
        FieldAnalysisCircuit.__init__(
            self,
            "Circuit Design",
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

        self.onetwork_data_explorer = self._desktop.GetTool("NdExplorer")

    def __enter__(self):
        return self

    def _get_number_from_string(self, stringval):
        value = stringval[stringval.find("=") + 1 :].strip().replace("{", "").replace("}", "").replace(",", ".")
        try:
            float(value)
            return value
        except:
            return from_rkm_to_aedt(value)

    @aedt_exception_handler
    def create_schematic_from_netlist(self, file_to_import):
        """Create a circuit schematic from an HSpice net list.

        Supported currently are:

        * R
        * L
        * C
        * Diodes
        * Bjts
        * Discrete components with syntax ``Uxxx net1 net2 ... netn modname``

        Parameters
        ----------
        file_to_import : str
            Full path to the HSpice file to import.

        Returns
        -------
        bool
             ``True`` when successful, ``False`` when failed.

        """
        xpos = 0
        ypos = 0
        delta = 0.0508
        use_instance = True
        model = []
        self._desktop.CloseAllWindows()
        autosave = False
        if self._desktop.GetAutoSaveEnabled() == 1:
            self._desktop.EnableAutoSave(False)
            autosave = True
        with open(file_to_import, "rb") as f:
            for line in f:
                line = line.decode("utf-8")
                if ".param" in line[:7].lower():
                    try:
                        ppar = line[7:].split("=")[0]
                        pval = line[7:].split("=")[1]
                        self[ppar] = pval
                        xpos = 0.0254
                    except:
                        pass
                elif ".model" in line[:7].lower() or ".lib" in line[:4].lower():
                    model.append(line)
        if model:
            self.modeler.schematic.create_symbol("Models_Netlist", [])
            self.modeler.schematic.create_new_component_from_symbol("Models_Netlist", [], "")
            self.modeler.schematic.create_component(
                None,
                component_library=None,
                component_name="Models_Netlist",
                location=[xpos, 0],
                global_netlist_list=model,
            )
            self.modeler.schematic.disable_data_netlist(component_name="Models_Netlist")
            xpos += 0.0254
        counter = 0
        with open(file_to_import, "rb") as f:
            for line in f:
                line = line.decode("utf-8")
                mycomp = None
                fields = line.split(" ")
                name = fields[0].replace(".", "")

                if fields[0][0] == "R":
                    if "{" in fields[3][0]:
                        value = fields[3].strip()[1:-1]
                    elif (
                        "/" in fields[3]
                        and '"' not in fields[3][0]
                        and "'" not in fields[3][0]
                        and "{" not in fields[3][0]
                    ):
                        value = self._get_number_from_string(fields[3].split("/")[0])
                    else:
                        value = self._get_number_from_string(fields[3])
                    mycomp = self.modeler.schematic.create_resistor(
                        name, value, [xpos, ypos], use_instance_id_netlist=use_instance
                    )
                elif fields[0][0] == "L":
                    if len(fields) > 4 and "=" not in fields[4]:
                        try:
                            float(fields[4])
                        except:
                            self.logger.warning("Component {} Not Imported. Check it and manually import".format(name))
                            continue
                    if "{" in fields[3][0]:
                        value = fields[3].strip()[1:-1]
                    elif "/" in fields[3] and '"' not in fields[3][0] and "'" not in fields[3][0]:
                        value = self._get_number_from_string(fields[3].split("/")[0])
                    else:
                        value = self._get_number_from_string(fields[3])
                    mycomp = self.modeler.schematic.create_inductor(
                        name, value, [xpos, ypos], use_instance_id_netlist=use_instance
                    )
                elif fields[0][0] == "C":
                    if "{" in fields[3][0]:
                        value = fields[3].strip()[1:-1]
                    elif "/" in fields[3] and '"' not in fields[3][0] and "'" not in fields[3][0]:
                        value = self._get_number_from_string(fields[3].split("/")[0])
                    else:
                        value = self._get_number_from_string(fields[3])
                    mycomp = self.modeler.schematic.create_capacitor(
                        name, value, [xpos, ypos], use_instance_id_netlist=use_instance
                    )
                elif fields[0][0] == "Q" or fields[0][0] == "U":
                    if len(fields) == 4 and fields[0][0] == "Q":
                        value = fields[3].strip()
                        mycomp = self.modeler.schematic.create_npn(
                            fields[0], value, [xpos, ypos], use_instance_id_netlist=use_instance
                        )
                    else:
                        numpins = len(fields) - 2
                        i = 1
                        pins = []
                        while i <= numpins:
                            pins.append("Pin" + str(i))
                            i += 1
                        parameter = fields[len(fields) - 1][:-1].strip()
                        if "=" in parameter:
                            parameter_list = [parameter[: parameter.find("=") - 1]]
                            parameter_value = [parameter[parameter.find("=") + 1 :]]
                        else:
                            parameter_list = ["MOD"]
                            parameter_value = [parameter]
                        self.modeler.schematic.create_symbol(parameter, pins)
                        already_exist = False
                        for el in self.modeler.schematic.components:
                            if self.modeler.schematic.components[el].name == parameter:
                                already_exist = True
                        if not already_exist:
                            self.modeler.schematic.create_new_component_from_symbol(
                                parameter, pins, fields[0][0], parameter_list, parameter_value
                            )
                        mycomp = self.modeler.schematic.create_component(
                            fields[0],
                            component_library=None,
                            component_name=parameter,
                            location=[xpos, ypos],
                            use_instance_id_netlist=use_instance,
                        )
                        value = None
                elif fields[0][0] == "J":
                    numpins = len(fields) - 1
                    i = 1
                    pins = []
                    while i <= numpins:
                        pins.append("Pin" + str(i))
                        i += 1
                    parameter = fields[len(fields) - 1][:-1].strip()
                    if "=" in parameter:
                        parameter_list = [parameter[: parameter.find("=") - 1]]
                        parameter_value = [parameter[parameter.find("=") + 1 :]]
                    else:
                        parameter_list = ["MOD"]
                        parameter_value = [parameter]
                    self.modeler.schematic.create_symbol(parameter, pins)
                    already_exist = False
                    for el in self.modeler.schematic.components:
                        if self.modeler.schematic.components[el].name == parameter:
                            already_exist = True
                    if not already_exist:
                        self.modeler.schematic.create_new_component_from_symbol(
                            parameter, pins, fields[0][0], parameter_list, parameter_value
                        )
                    mycomp = self.modeler.schematic.create_component(
                        fields[0],
                        component_library=None,
                        component_name=parameter,
                        location=[xpos, ypos],
                        use_instance_id_netlist=use_instance,
                    )
                    value = None
                elif fields[0][0] == "D":
                    value = self._get_number_from_string(fields[3])
                    mycomp = self.modeler.schematic.create_diode(
                        name, value, [xpos, ypos], use_instance_id_netlist=use_instance
                    )
                elif fields[0][0] == "V":
                    if "PULSE" not in line:
                        value = self._get_number_from_string(fields[3])
                        mycomp = self.modeler.schematic.create_voltage_dc(
                            name, value, [xpos, ypos], use_instance_id_netlist=use_instance
                        )
                    else:
                        value = line[line.index("PULSE") + 6 : line.index(")") - 1].split(" ")
                        value = [i.replace("{", "").replace("}", "") for i in value]
                        fields[1], fields[2] = fields[2], fields[1]
                        mycomp = self.modeler.schematic.create_voltage_pulse(
                            name, value, [xpos, ypos], use_instance_id_netlist=use_instance
                        )
                elif fields[0][0] == "K":
                    value = self._get_number_from_string(fields[3])
                    mycomp = self.modeler.schematic.create_coupling_inductors(
                        name, fields[1], fields[2], value, [xpos, ypos], use_instance_id_netlist=use_instance
                    )
                elif fields[0][0] == "I":
                    if "PULSE" not in line:
                        value = self._get_number_from_string(fields[3])
                        mycomp = self.modeler.schematic.create_current_dc(
                            name, value, [xpos, ypos], use_instance_id_netlist=use_instance
                        )
                    else:
                        value = line[line.index("PULSE") + 6 : line.index(")") - 1].split(" ")
                        value = [i.replace("{", "").replace("}", "") for i in value]
                        mycomp = self.modeler.schematic.create_current_pulse(
                            name, value, [xpos, ypos], use_instance_id_netlist=use_instance
                        )
                if mycomp:
                    id = 1
                    for pin in mycomp.pins:
                        pos = pin.location
                        if pos[0] < xpos:
                            angle = 0.0
                        else:
                            angle = math.pi
                        self.modeler.schematic.create_page_port(fields[id], [pos[0], pos[1]], angle)
                        id += 1
                    ypos += delta
                    if ypos > 0.254:
                        xpos += delta
                        ypos = 0
                    counter += 1
                    if counter > 59:
                        self.modeler.oeditor.CreatePage("<Page Title>")
                        counter = 0
        if autosave:
            self._desktop.EnableAutoSave(True)
        self.logger.info("Netlist correctly imported into %s", self.design_name)
        return True

    @aedt_exception_handler
    def create_schematic_from_mentor_netlist(self, file_to_import):
        """Create a circuit schematic from a Mentor net list.

        Supported currently are:

        * R
        * L
        * C
        * Diodes
        * Bjts
        * Discrete components with syntax ``Uxxx net1 net2get_source_pin_names ... netn modname``

        Parameters
        ----------
        file_to_import : str
            Full path to the HSpice file to import.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        """
        xpos = 0
        ypos = 0
        delta = 0.0508
        use_instance = True
        my_netlist = []
        with open(file_to_import, "r") as f:
            for line in f:
                my_netlist.append(line.split(" "))
        nets = [i for i in my_netlist if i[0] == "NET"]
        comps = [i for i in my_netlist if i[0] == "COMP:"]
        props = {}
        for el in my_netlist:
            if el[0] == "COMP:":
                n = el[2].strip()
                n = n[1:-1]
                props[n] = []
                i = my_netlist.index(el) + 1
                finished = False
                while not finished and i < len(my_netlist):
                    if my_netlist[i][0] == "Property:":
                        props[n].append(my_netlist[i][1])
                    elif "Pin:" in my_netlist[i]:
                        props[n].append(my_netlist[i])
                    else:
                        finished = True
                    i += 1

        column_number = int(math.sqrt(len(comps)))
        for el in comps:
            name = el[2].strip()  # Remove carriage return.
            name = name[1:-1]  # Remove quotes.
            if len(el) > 3:
                comptype = el[3]
            else:
                comptype = self.retrieve_mentor_comp(el[2])
            value = "required"
            for prop in props[name]:
                if "Value=" in prop:
                    value = prop.split("=")[1].replace(",", ".").strip()

            mycomp = None
            if "resistor:RES." in comptype:
                mycomp = self.modeler.schematic.create_resistor(
                    name, value, [xpos, ypos], use_instance_id_netlist=use_instance
                )
            elif "inductor:COIL." in comptype:
                mycomp = self.modeler.schematic.create_inductor(
                    name, value, [xpos, ypos], use_instance_id_netlist=use_instance
                )
            elif "capacitor:CAP." in comptype:
                mycomp = self.modeler.schematic.create_capacitor(
                    name, value, [xpos, ypos], use_instance_id_netlist=use_instance
                )
            elif "transistor:NPN" in comptype:
                mycomp = self.modeler.schematic.create_npn(
                    name, value, [xpos, ypos], use_instance_id_netlist=use_instance
                )
            elif "transistor:PNP" in comptype:
                mycomp = self.modeler.schematic.create_pnp(
                    name, value, [xpos, ypos], use_instance_id_netlist=use_instance
                )
            elif "diode:" in comptype:
                mycomp = self.modeler.schematic.create_diode(
                    name, value, [xpos, ypos], use_instance_id_netlist=use_instance
                )

            if mycomp:
                id = 1
                for pin in mycomp.pins:
                    pos = pin.location
                    if pos[0] < xpos:
                        angle = 0.0
                    else:
                        angle = math.pi
                    netname = None
                    for net in nets:
                        net = [i.strip() for i in net]
                        if (name + "-" + str(id)) in net:
                            fullnetname = net[2]
                            netnames = fullnetname.split("/")
                            netname = (
                                netnames[len(netnames) - 1].replace(",", "_").replace("'", "").replace("$", "").strip()
                            )
                    if not netname:
                        prop = props[name]
                        if "Pin:" in prop and id in prop:
                            netname = prop[-1]
                            netname = netname.replace("$", "")

                    if netname:
                        self.modeler.schematic.create_page_port(netname, [pos[0], pos[1]], angle)
                    else:
                        self.logger.info("Page Port Not Created")
                    id += 1
                ypos += delta
                if ypos > delta * (column_number):
                    xpos += delta
                    ypos = 0

        for el in nets:
            netname = el[2][1:-1]
            netname = netname.replace("$", "")
            if "GND" in netname.upper():
                self.modeler.schematic.create_gnd([xpos, ypos])
                page_pos = ypos + 0.00254
                mod1 = self.modeler.schematic.create_page_port(netname, [xpos, ypos], 0.0)
                mod1.location = [str(xpos) + "meter", str(page_pos) + "meter"]
                ypos += delta
                if ypos > delta * column_number:
                    xpos += delta
                    ypos = 0

        self.logger.info("Netlist correctly imported into %s", self.design_name)
        return True

    @aedt_exception_handler
    def retrieve_mentor_comp(self, refid):
        """Retrieve the type of the Mentor net list component for a given reference ID.

        Parameters
        ----------
        refid : int
            Reference ID.

        Returns
        -------
        str
            Type of the Mentor net list component.

        """
        if refid[1] == "R":
            return "resistor:RES."
        elif refid[1] == "C":
            return "capacitor:CAP."
        elif refid[1] == "L":
            return "inductor:COIL."
        elif refid[1] == "D":
            return "diode"
        elif refid[1] == "Q":
            return "transistor:NPN"
        else:
            return ""

    @aedt_exception_handler
    def get_source_pin_names(
        self, source_design_name, source_project_name=None, source_project_path=None, port_selector=3
    ):
        """List the pin names.

        Parameters
        ----------
        source_design_name : str
            Name of the source design.
        source_project_name :str, optional
            Name of the source project. The default is ``None``.
        source_project_path : str, optional
            Path to the source project if different than the existing path. The default is ``None``.
        port_selector : int, optional
             Type of the port. Options are ``1``, ``2``, or ``3``, corresponding respectively to ``"Wave Port"``,
             ``"Terminal"``, or ``"Circuit Port"``.
             The default is ``3``, which is a circuit port.

        Returns
        -------
        list
            List of pin names.

        References
        ----------

        >>> oModule.GetExcitationsOfType
        """
        if source_project_name and self.project_name != source_project_name and not source_project_path:
            raise AttributeError(
                "If source project is different than the current one, " "``source_project_path`` must be also provided."
            )
        if source_project_path and not source_project_name:
            raise AttributeError(
                "When ``source_project_path`` is specified, " "``source_project_name`` must be also provided."
            )
        if not source_project_name or self.project_name == source_project_name:
            oSrcProject = self._desktop.GetActiveProject()
        else:
            self._desktop.OpenProject(source_project_path)
            oSrcProject = self._desktop.SetActiveProject(source_project_name)
        oDesign = oSrcProject.SetActiveDesign(source_design_name)
        oModule = oDesign.GetModule("BoundarySetup")
        port = None
        if port_selector == 1:
            port = "Wave Port"
        elif port_selector == 2:
            port = "Terminal"
        elif port_selector == 3:
            port = "Circuit Port"
        if not port:
            return False
        pins = list(oModule.GetExcitationsOfType(port))
        self.logger.info("%s Excitations Pins found.", len(pins))
        return pins

    @aedt_exception_handler
    def import_touchstone_solution(self, filename, solution_name="Imported_Data"):
        """Import a Touchstone file as the solution.

        Parameters
        ----------
        filename : str
            Name of the Touchstone file.
        solution_name : str, optional
            Name of the solution. The default is ``"Imported_Data"``.

        Returns
        -------
        list
            List of ports.

        References
        ----------

        >>> oDesign.ImportData
        """
        if filename[-2:] == "ts":
            with open(filename, "r") as f:
                lines = f.readlines()
                for i in lines:
                    if "[Number of Ports]" in i:
                        ports = int(i[i.find("]") + 1 :])
                portnames = [i.split(" = ")[1].strip() for i in lines if "! Port" in i[:9]]
                if not portnames:
                    portnames = ["Port{}".format(i + 1) for i in range(ports)]
        else:
            re_filename = re.compile(r"\.s(?P<ports>\d+)+p", re.I)
            m = re_filename.search(filename)
            ports = int(m.group("ports"))
            portnames = None
            with open(filename, "r") as f:
                lines = f.readlines()
                portnames = [i.split(" = ")[1].strip() for i in lines if "Port[" in i]
            if not portnames:
                portnames = ["Port{}".format(i + 1) for i in range(ports)]
        arg = [
            "NAME:NPortData",
            "Description:=",
            "",
            "ImageFile:=",
            "",
            "SymbolPinConfiguration:=",
            0,
            ["NAME:PortInfoBlk"],
            ["NAME:PortOrderBlk"],
            "filename:=",
            filename,
            "numberofports:=",
            ports,
            "sssfilename:=",
            "",
            "sssmodel:=",
            False,
            "PortNames:=",
            portnames,
            "domain:=",
            "frequency",
            "datamode:=",
            "Link",
            "devicename:=",
            "",
            "SolutionName:=",
            solution_name,
            "displayformat:=",
            "MagnitudePhase",
            "datatype:=",
            "SMatrix",
            [
                "NAME:DesignerCustomization",
                "DCOption:=",
                0,
                "InterpOption:=",
                0,
                "ExtrapOption:=",
                1,
                "Convolution:=",
                0,
                "Passivity:=",
                0,
                "Reciprocal:=",
                False,
                "ModelOption:=",
                "",
                "DataType:=",
                1,
            ],
            [
                "NAME:NexximCustomization",
                "DCOption:=",
                3,
                "InterpOption:=",
                1,
                "ExtrapOption:=",
                3,
                "Convolution:=",
                0,
                "Passivity:=",
                0,
                "Reciprocal:=",
                False,
                "ModelOption:=",
                "",
                "DataType:=",
                2,
            ],
            [
                "NAME:HSpiceCustomization",
                "DCOption:=",
                1,
                "InterpOption:=",
                2,
                "ExtrapOption:=",
                3,
                "Convolution:=",
                0,
                "Passivity:=",
                0,
                "Reciprocal:=",
                False,
                "ModelOption:=",
                "",
                "DataType:=",
                3,
            ],
            "NoiseModelOption:=",
            "External",
        ]
        self.odesign.ImportData(arg, "", True)
        self.logger.info("Touchstone correctly imported into %s", self.design_name)
        return portnames

    @aedt_exception_handler
    def export_touchstone(self, solutionname, sweepname, filename=None, variation=[], variations_value=[]):
        """Export the Touchstone file to a local folder.

        Parameters
        ----------
        solutionname : str
             Name of the solution that has been solved.
        sweepname : str
             Name of the sweep that has been solved.
        filename : str, optional
             Full path and name for the Touchstone file. The default is ``None``.
        variation : list, optional
             List of all parameter variations. For example, ``["$AmbientTemp", "$PowerIn"]``.
             The default is ``[]``.
        variations_value : list, optional
             List of all parameter variation values. For example, ``["22cel", "100"]``.
             The default is ``[]``.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        References
        ----------

        >>> oDesign.ExportNetworkData
        """
        # Normalize the save path
        if not filename:
            appendix = ""
            for v, vv in zip(variation, variations_value):
                appendix += "_" + v + vv.replace("'", "")
            ext = ".S" + str(self.oboundary.GetNumExcitations()) + "p"
            filename = os.path.join(self.project_path, solutionname + "_" + sweepname + appendix + ext)
        else:
            filename = filename.replace("//", "/").replace("\\", "/")
        self.logger.info("Exporting Touchstone " + filename)
        DesignVariations = ""
        i = 0
        for el in variation:
            DesignVariations += str(variation[i]) + "='" + str(variations_value[i].replace("'", "")) + "' "
            i += 1
            # DesignVariations = "$AmbientTemp=\'22cel\' $PowerIn=\'100\'"
        # array containing "SetupName:SolutionName" pairs (note that setup and solution are separated by a colon)
        SolutionSelectionArray = [solutionname + ":" + sweepname]
        # 2=tab delimited spreadsheet (.tab), 3= touchstone (.sNp), 4= CitiFile (.cit),
        # 7=Matlab (.m), 8=Terminal Z0 spreadsheet
        FileFormat = 3
        OutFile = filename  # full path of output file
        # array containin the frequencies to export, use ["all"] for all frequencies
        FreqsArray = ["all"]
        DoRenorm = True  # perform renormalization before export
        RenormImped = 50  # Real impedance value in ohm, for renormalization
        DataType = "S"  # Type: "S", "Y", or "Z" matrix to export
        Pass = -1  # The pass to export. -1 = export all passes.
        ComplexFormat = 0  # 0=Magnitude/Phase, 1=Real/Immaginary, 2=dB/Phase
        DigitsPrecision = 15  # Touchstone number of digits precision
        IncludeGammaImpedance = True  # Include Gamma and Impedance in comments
        NonStandardExtensions = False  # Support for non-standard Touchstone extensions

        self.odesign.ExportNetworkData(
            DesignVariations,
            SolutionSelectionArray,
            FileFormat,
            OutFile,
            FreqsArray,
            DoRenorm,
            RenormImped,
            DataType,
            Pass,
            ComplexFormat,
            DigitsPrecision,
            False,
            IncludeGammaImpedance,
            NonStandardExtensions,
        )
        self.logger.info("Touchstone correctly exported to %s", filename)
        return True

    @aedt_exception_handler
    def export_fullwave_spice(
        self,
        designname=None,
        setupname=None,
        is_solution_file=False,
        filename=None,
        passivity=False,
        causality=False,
        renormalize=False,
        impedance=50,
        error=0.5,
        poles=10000,
    ):
        """
        Export a full wave HSpice file using NDE.

        .. warning::
          This method doesn't work.

        Parameters
        ----------
        designname : str, optional
            Name of the design or the full path to the solution file if it is an imported file.
            The default is ``None``.
        setupname : str, optional
            Name of the setup if it is a design. The default is ``None``.
        is_solution_file : bool, optional
            Whether it is an imported solution file. The default is ``False``.
        filename : str, optional
            Full path and name for exporting the HSpice file. The default is ``None``.
        passivity : bool, optional
            Whether to compute the passivity. The default is ``False``.
        causality : bool, optional
            Whether to compute the causality. The default is ``False``.
        renormalize : bool, optional
            Whether to renormalize the S-matrix to a specific port impedance.
            The default is ``False``.
        impedance : float, optional
            Impedance value if ``renormalize=True``. The default is ``50``.
        error : float, optional
            Fitting error. The default is ``0.5``.
        poles : int, optional
            Number of fitting poles. The default is ``10000``.

        Returns
        -------
        str
            Name of the HSpice file if the export is successful.

        References
        ----------

        >>> oDesign.ExportFullWaveSpice
        """
        if not designname:
            designname = self.design_name
        if not filename:
            filename = os.path.join(self.project_path, self.design_name + ".sp")
        if is_solution_file:
            setupname = designname
            designname = ""
        else:
            if not setupname:
                setupname = self.nominal_sweep
        self.onetwork_data_explorer.ExportFullWaveSpice(
            designname,
            is_solution_file,
            setupname,
            "",
            [],
            [
                "NAME:SpiceData",
                "SpiceType:=",
                "HSpice",
                "EnforcePassivity:=",
                passivity,
                "EnforceCausality:=",
                causality,
                "UseCommonGround:=",
                True,
                "ShowGammaComments:=",
                True,
                "Renormalize:=",
                renormalize,
                "RenormImpedance:=",
                impedance,
                "FittingError:=",
                error,
                "MaxPoles:=",
                poles,
                "PassivityType:=",
                "IteratedFittingOfPV",
                "ColumnFittingType:=",
                "Matrix",
                "SSFittingType:=",
                "FastFit",
                "RelativeErrorToleranc:=",
                False,
                "EnsureAccurateZfit:=",
                True,
                "TouchstoneFormat:=",
                "MA",
                "TouchstoneUnits:=",
                "GHz",
                "TouchStonePrecision:=",
                15,
                "SubcircuitName:=",
                "",
                "SYZDataInAutoMode:=",
                False,
                "ExportDirectory:=",
                os.path.dirname(filename) + "\\",
                "ExportSpiceFileName:=",
                os.path.basename(filename),
                "FullwaveSpiceFileName:=",
                os.path.basename(filename),
                "UseMultipleCores:=",
                True,
                "NumberOfCores:=",
                20,
            ],
        )
        self.logger.info("FullWaveSpice correctly exported to %s", filename)

        return filename

    @aedt_exception_handler
    def create_touchstone_report(
        self,
        plot_name,
        curvenames,
        solution_name=None,
        variation_dict=None,
        subdesign_id=None,
    ):
        """
        Create a Touchstone plot.

        Parameters
        ----------
        plot_name : str
            Name of the plot.
        curvenames : list
            List of names for the curves to plot.
        solution_name : str, optional
            Name of the solution. The default value is ``None``.
        variation_dict : dict, optional
            Dictionary of variation names. The default value is ``None``.
        subdesign_id : int, optional
            Specify a SubDesign ID to export a touchstone of this Subdesign. The default value is ``None``.

        Returns
        -------
        bool
           ``True`` when successful, ``False`` when failed.

        References
        ----------

        >>> oModule.CreateReport
        """
        if not solution_name:
            solution_name = self.nominal_sweep
        variations = {"Freq": ["All"]}
        if variation_dict:
            for el in variation_dict:
                variations[el] = [variation_dict[el]]
        ctxt = ["NAME:Context", "SimValueContext:=", [3, 0, 2, 0, False, False, -1, 1, 0, 1, 1, "", 0, 0]]
        if subdesign_id:
            ctxt_temp = ["NUMLEVELS", False, "0", "SUBDESIGNID", False, str(subdesign_id)]
            for el in ctxt_temp:
                ctxt[2].append(el)

        return self.post.create_rectangular_plot(
            curvenames, solution_name, variations, plotname=plot_name, context=ctxt
        )

    @aedt_exception_handler
    def get_touchstone_data(self, curvenames, solution_name=None, variation_dict=None):
        """Return Touchstone Data plot.

        Parameters
        ----------
        curvenames : list
            List of the curves to plot.
        solution_name : str, optional
            Name of the solution. The default value is ``None``.
        variation_dict : dict, optional
            Dictionary of variation names. The default value is ``None``.

        Returns
        -------
        :class:`pyaedt.modules.PostProcessor.SolutionData`
           Class containing all Requested Data

        References
        ----------

        >>> oModule.GetSolutionDataPerVariation
        """
        if not solution_name:
            solution_name = self.nominal_sweep
        variations = {"Freq": ["All"]}
        if variation_dict:
            for el in variation_dict:
                variations[el] = [variation_dict[el]]
        ctxt = ["NAME:Context", "SimValueContext:=", [3, 0, 2, 0, False, False, -1, 1, 0, 1, 1, "", 0, 0]]
        return self.post.get_solution_data_per_variation("Standard", solution_name, ctxt, variations, curvenames)

    @aedt_exception_handler
    def push_excitations(self, instance_name, thevenin_calculation=False, setup_name="LinearFrequency"):
        """Push excitations.

        Parameters
        ----------
        instance_name : str
            Name of the instance.
        thevenin_calculation : bool, optional
            Whether to perform the Thevenin equivalent calculation. The default is ``False``.
        setup_name : str
            Name of the solution setup to push.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        References
        ----------

        >>> oEditor.PushExcitations
        """
        arg = ["NAME:options", "CalcThevenin:=", thevenin_calculation, "Sol:=", setup_name]

        self.modeler.oeditor.PushExcitations(instance_name, arg)
        return True

    @aedt_exception_handler
    def assign_voltage_sinusoidal_excitation_to_ports(self, ports, settings):
        """Assign a voltage sinusoidal excitation to circuit ports.

        Parameters
        ----------
        ports : list
            List of circuit ports to assign to the sinusoidal excitation.
        settings : list
            List of parameter values to use in voltage sinusoidal excitation creation.
            All settings must be provided as strings.
            An empty string (``""``) sets the parameter to its default.

            Values are given in this order:

            * 0: AC magnitude for small-signal analysis. For example ``"33V"``. Default = "nan V".
            * 1: AC phase for small-signal analysis. For example ``"44deg"``. Default = "0deg".
            * 2: DC voltage. For example ``"1V"``. Default = "0V"
            * 3: Voltage offset from zero. For example ``"1V"``. Default = "0V".
            * 4: Voltage amplitude. For example ``"3V"``. Default = "0V".
            * 5: Frequency. For example ``"15GHz"``. Default = "1GHz".
            * 6: Delay to start of sine wave. For example ``"16s"``. Default = "0s".
            * 7: Damping factor (1/seconds). For example ``"2"``. Default = "0".
            * 8: Phase delay. For example ``"18deg"``. Default = "0deg".
            * 9: Frequency to use for harmonic balance analysis. For example ``"20Hz"``. Default = "0Hz".

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        References
        ----------

        >>> oDesign.UpdateSources
        """
        # setting the defaults if no value is provided
        defaults = ["nan V", "0deg", "0V", "0V", "0V", "1GHz", "0s", "0", "0deg", "0Hz"]
        for i in range(len(settings)):
            if settings[i] == "":
                settings[i] = defaults[i]

        id = self.modeler.schematic.create_unique_id()

        arg1 = [
            "NAME:NexximSources",
            [
                "NAME:NexximSources",
                [
                    "NAME:Data",
                    [
                        "NAME:VoltageSinusoidal" + str(id),
                        "DataId:=",
                        "Source" + str(id),
                        "Type:=",
                        1,
                        "Output:=",
                        0,
                        "NumPins:=",
                        2,
                        "Netlist:=",
                        (
                            "V@ID %0 %1 *DC(DC=@DC) SIN(?VO(@VO) ?VA(@VA) ?FREQ(@FREQ) ?TD(@TD) ?ALPHA(@ALPHA) "
                            "?THETA(@THETA)) *TONE(TONE=@TONE) *ACMAG(AC @ACMAG @ACPHASE)"
                        ),
                        "CompName:=",
                        "Nexxim Circuit Elements\\Independent Sources:V_SIN",
                        "FDSFileName:=",
                        "",
                        [
                            "NAME:Properties",
                            "TextProp:=",
                            ["LabelID", "HD", "Property string for netlist ID", "V@ID"],
                            "ValueProp:=",
                            ["ACMAG", "OD", "AC magnitude for small-signal analysis (Volts)", settings[0], 0],
                            "ValuePropNU:=",
                            ["ACPHASE", "OD", "AC phase for small-signal analysis", settings[1], 0, "deg"],
                            "ValueProp:=",
                            ["DC", "OD", "DC voltage (Volts)", settings[2], 0],
                            "ValueProp:=",
                            ["VO", "OD", "Voltage offset from zero (Volts)", settings[3], 0],
                            "ValueProp:=",
                            ["VA", "OD", "Voltage amplitude (Volts)", settings[4], 0],
                            "ValueProp:=",
                            ["FREQ", "OD", "Frequency (Hz)", settings[5], 0],
                            "ValueProp:=",
                            ["TD", "OD", "Delay to start of sine wave (seconds)", settings[6], 0],
                            "ValueProp:=",
                            ["ALPHA", "OD", "Damping factor (1/seconds)", settings[7], 0],
                            "ValuePropNU:=",
                            ["THETA", "OD", "Phase delay", settings[8], 0, "deg"],
                            "ValueProp:=",
                            [
                                "TONE",
                                "OD",
                                (
                                    "Frequency (Hz) to use for harmonic balance analysis, should be a submultiple of "
                                    "(or equal to) the driving frequency and should also be included in the "
                                    "HB analysis setup"
                                ),
                                settings[9],
                                0,
                            ],
                            "TextProp:=",
                            ["ModelName", "SHD", "", "V_SIN"],
                            "MenuProp:=",
                            ["CoSimulator", "D", "", "DefaultNetlist", 0],
                            "ButtonProp:=",
                            ["CosimDefinition", "D", "", "", "Edit", 40501, "ButtonPropClientData:=", []],
                        ],
                    ],
                ],
            ],
        ]

        arg2 = ["NAME:ComponentConfigurationData"]

        arg3 = ["NAME:ComponentConfigurationData", ["NAME:EnabledPorts", "VoltageSinusoidal" + str(id) + ":=", ports]]

        arg2.append(arg3)

        self.odesign.UpdateSources(arg1, arg2)
        self.logger.info("Voltage Source updated correctly.")
        return True

    @aedt_exception_handler
    def assign_current_sinusoidal_excitation_to_ports(self, ports, settings):
        """Assign a current sinusoidal excitation to circuit ports.

        Parameters
        ----------
        ports : list
            List of circuit ports to assign to the sinusoidal excitation.
        settings : list
            List of parameter values to use in voltage sinusoidal excitation creation.
            All settings must be provided as strings.
            An empty string (``""``) sets the parameter to its default.

            Values are given in this order:

            * 0: AC magnitude for small-signal analysis. For example ``"33A"``. Default = "nan A".
            * 1: AC phase for small-signal analysis. For example ``"44deg"``. Default = "0deg".
            * 2: DC voltage. For example ``"1A"``. Default = "0A"
            * 3: Current offset from zero. For example ``"1A"``. Default = "0A".
            * 4: Current amplitude. For example ``"3A"``. Default = "0A".
            * 5: Frequency. For example ``"15GHz"``. Default = "1GHz".
            * 6: Delay to start of sine wave. For example ``"16s"``. Default = "0s".
            * 7: Damping factor (1/seconds). For example ``"2"``. Default = "0".
            * 8: Phase delay. For example ``"18deg"``. Default = "0deg".
            * 9: Multiplier for simulating multiple parallel current sources. For example ``"4"``. Default = "1".
            * 10: Frequency to use for harmonic balance analysis. For example ``"20Hz"``. Default = "0Hz".

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        References
        ----------

        >>> oDesign.UpdateSources
        """
        # setting the defaults if no value is provided
        defaults = ["nan A", "0deg", "0A", "0A", "0A", "1GHz", "0s", "0", "0deg", "1", "0Hz"]
        for i in range(len(settings)):
            if settings[i] == "":
                settings[i] = defaults[i]

        id = self.modeler.schematic.create_unique_id()

        arg1 = [
            "NAME:NexximSources",
            [
                "NAME:NexximSources",
                [
                    "NAME:Data",
                    [
                        "NAME:CurrentSinusoidal" + str(id),
                        "DataId:=",
                        "Source" + str(id),
                        "Type:=",
                        1,
                        "Output:=",
                        1,
                        "NumPins:=",
                        2,
                        "Netlist:=",
                        (
                            "I@ID %0 %1 *DC(DC=@DC) SIN(?VO(@VO) ?VA(@VA) ?FREQ(@FREQ) ?TD(@TD) ?ALPHA(@ALPHA) "
                            "?THETA(@THETA) *M(M=@M)) *TONE(TONE=@TONE) *ACMAG(AC @ACMAG @ACPHASE)"
                        ),
                        "CompName:=",
                        "Nexxim Circuit Elements\\Independent Sources:I_SIN",
                        "FDSFileName:=",
                        "",
                        [
                            "NAME:Properties",
                            "TextProp:=",
                            ["LabelID", "HD", "Property string for netlist ID", "I@ID"],
                            "ValueProp:=",
                            ["ACMAG", "OD", "AC magnitude for small-signal analysis (Amps)", settings[0], 0],
                            "ValuePropNU:=",
                            ["ACPHASE", "OD", "AC phase for small-signal analysis", settings[1], 0, "deg"],
                            "ValueProp:=",
                            ["DC", "OD", "DC current (Amps)", settings[2], 0],
                            "ValueProp:=",
                            ["VO", "OD", "Current offset (Amps)", settings[3], 0],
                            "ValueProp:=",
                            ["VA", "OD", "Current amplitude (Amps)", settings[4], 0],
                            "ValueProp:=",
                            ["FREQ", "OD", "Frequency (Hz)", settings[5], 0],
                            "ValueProp:=",
                            ["TD", "OD", "Delay to start of sine wave (seconds)", settings[6], 0],
                            "ValueProp:=",
                            ["ALPHA", "OD", "Damping factor (1/seconds)", settings[7], 0],
                            "ValuePropNU:=",
                            ["THETA", "OD", "Phase delay", settings[8], 0, "deg"],
                            "ValueProp:=",
                            ["M", "OD", "Multiplier for simulating multiple parallel current sources", settings[9], 0],
                            "ValueProp:=",
                            [
                                "TONE",
                                "OD",
                                "Frequency (Hz) to use for harmonic balance analysis, should be a submultiple of "
                                "(or equal to) the driving frequency and should also be included in the "
                                "HB analysis setup",
                                settings[10],
                                0,
                            ],
                            "TextProp:=",
                            ["ModelName", "SHD", "", "I_SIN"],
                            "MenuProp:=",
                            ["CoSimulator", "D", "", "DefaultNetlist", 0],
                            "ButtonProp:=",
                            ["CosimDefinition", "D", "", "", "Edit", 40501, "ButtonPropClientData:=", []],
                        ],
                    ],
                ],
            ],
        ]

        arg2 = ["NAME:ComponentConfigurationData"]

        arg3 = ["NAME:ComponentConfigurationData", ["NAME:EnabledPorts", "CurrentSinusoidal" + str(id) + ":=", ports]]

        arg2.append(arg3)

        self.odesign.UpdateSources(arg1, arg2)
        self.logger.info("Current Source updated correctly.")

        return True

    @aedt_exception_handler
    def assign_power_sinusoidal_excitation_to_ports(self, ports, settings):
        """Assign a power sinusoidal excitation to circuit ports.

        Parameters
        ----------
        ports : list
            List of circuit ports to assign to the sinusoidal excitation.
        settings : list
            List of parameter values to use in power sinusoidal excitation creation.
            All settings must be provided as strings.
            An empty string (``""``) sets the parameter to its default.

            Values are given in this order:

            * 0: AC magnitude for small-signal analysis. For example ``"33V"``. Default = "nan V".
            * 1: AC phase for small-signal analysis. For example ``"44deg"``. Default = "0deg".
            * 2: DC voltage. For example ``"1V"``. Default = "0V"
            * 3: Power offset from zero watts. For example ``"1W"``. Default = "0W".
            * 4: Available power of the source above VO. For example ``"3W"``. Default = "0W".
            * 5: Frequency. For example ``"15GHz"``. Default = "1GHz".
            * 6: Delay to start of sine wave. For example ``"16s"``. Default = "0s".
            * 7: Damping factor (1/seconds). For example ``"2"``. Default = "0".
            * 8: Phase delay. For example ``"18deg"``. Default = "0deg".
            * 9: Frequency to use for harmonic balance analysis. For example ``"20Hz"``. Default = "0Hz".

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        References
        ----------

        >>> oDesign.UpdateSources
        """
        # setting the defaults if no value is provided
        defaults = ["nan V", "0deg", "0V", "0W", "0W", "1GHz", "0s", "0", "0deg", "0Hz"]
        for i in range(len(settings)):
            if settings[i] == "":
                settings[i] = defaults[i]

        id = self.modeler.schematic.create_unique_id()

        arg1 = [
            "NAME:NexximSources",
            [
                "NAME:NexximSources",
                [
                    "NAME:Data",
                    [
                        "NAME:PowerSinusoidal" + str(id),
                        "DataId:=",
                        "Source" + str(id),
                        "Type:=",
                        1,
                        "Output:=",
                        2,
                        "NumPins:=",
                        2,
                        "Netlist:=",
                        (
                            "V@ID %0 %1 *DC(DC=@DC) POWER SIN(?VO(@VO) ?POWER(@POWER) ?FREQ(@FREQ) ?TD(@TD) "
                            "?ALPHA(@ALPHA) ?THETA(@THETA)) *TONE(TONE=@TONE) *ACMAG(AC @ACMAG @ACPHASE)"
                        ),
                        "CompName:=",
                        "Nexxim Circuit Elements\\Independent Sources:P_SIN",
                        "FDSFileName:=",
                        "",
                        [
                            "NAME:Properties",
                            "TextProp:=",
                            ["LabelID", "HD", "Property string for netlist ID", "V@ID"],
                            "ValueProp:=",
                            ["ACMAG", "OD", "AC magnitude for small-signal analysis (Volts)", settings[0], 0],
                            "ValuePropNU:=",
                            ["ACPHASE", "OD", "AC phase for small-signal analysis", settings[1], 0, "deg"],
                            "ValueProp:=",
                            ["DC", "OD", "DC voltage (Volts)", settings[2], 0],
                            "ValuePropNU:=",
                            ["VO", "OD", "Power offset from zero watts", settings[3], 0, "W"],
                            "ValueProp:=",
                            ["POWER", "OD", "Available power of the source above VO", settings[4], 0],
                            "ValueProp:=",
                            ["FREQ", "OD", "Frequency (Hz)", settings[5], 0],
                            "ValueProp:=",
                            ["TD", "OD", "Delay to start of sine wave (seconds)", settings[6], 0],
                            "ValueProp:=",
                            ["ALPHA", "OD", "Damping factor (1/seconds)", settings[7], 0],
                            "ValuePropNU:=",
                            ["THETA", "OD", "Phase delay", settings[8], 0, "deg"],
                            "ValueProp:=",
                            [
                                "TONE",
                                "OD",
                                (
                                    "Frequency (Hz) to use for harmonic balance analysis, should be a submultiple of "
                                    "(or equal to) the driving frequency and should also be included in the "
                                    "HB analysis setup"
                                ),
                                settings[9],
                                0,
                            ],
                            "TextProp:=",
                            ["ModelName", "SHD", "", "P_SIN"],
                            "ButtonProp:=",
                            ["CosimDefinition", "D", "", "Edit", "Edit", 40501, "ButtonPropClientData:=", []],
                            "MenuProp:=",
                            ["CoSimulator", "D", "", "DefaultNetlist", 0],
                        ],
                    ],
                ],
            ],
        ]

        arg2 = ["NAME:ComponentConfigurationData"]

        arg3 = ["NAME:ComponentConfigurationData", ["NAME:EnabledPorts", "PowerSinusoidal" + str(id) + ":=", ports]]

        arg2.append(arg3)

        self.odesign.UpdateSources(arg1, arg2)
        self.logger.info("Power Source updated correctly.")

        return True
