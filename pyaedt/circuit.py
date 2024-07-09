# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 - 2024 ANSYS, Inc. and/or its affiliates.
# SPDX-License-Identifier: MIT
#
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

"""This module contains the ``Circuit`` class."""

from __future__ import absolute_import  # noreorder

import io
import math
import os
import re
import shutil
import time

from pyaedt.application.AnalysisNexxim import FieldAnalysisCircuit
from pyaedt.application.analysis_hf import ScatteringMethods
from pyaedt.generic import ibis_reader
from pyaedt.generic.DataHandlers import from_rkm_to_aedt
from pyaedt.generic.constants import unit_converter
from pyaedt.generic.filesystem import search_files
from pyaedt.generic.general_methods import generate_unique_name
from pyaedt.generic.general_methods import is_linux
from pyaedt.generic.general_methods import open_file
from pyaedt.generic.general_methods import pyaedt_function_handler
from pyaedt.generic.settings import settings
from pyaedt.hfss3dlayout import Hfss3dLayout
from pyaedt.modules.Boundary import CurrentSinSource
from pyaedt.modules.Boundary import PowerIQSource
from pyaedt.modules.Boundary import PowerSinSource
from pyaedt.modules.Boundary import Sources
from pyaedt.modules.Boundary import VoltageDCSource
from pyaedt.modules.Boundary import VoltageFrequencyDependentSource
from pyaedt.modules.Boundary import VoltageSinSource
from pyaedt.modules.CircuitTemplates import SourceKeys


class Circuit(FieldAnalysisCircuit, ScatteringMethods):
    """Provides the Circuit application interface.

    Parameters
    ----------
    project : str, optional
        Name of the project to select or the full path to the project
        or AEDTZ archive to open.  The default is ``None``, in which
        case an attempt is made to get an active project. If no
        projects are present, an empty project is created.
    design : str, optional
        Name of the design to select. The default is ``None``, in
        which case an attempt is made to get an active design. If no
        designs are present, an empty design is created.
    solution_type : str, optional
        Solution type to apply to the design. The default is
        ``None``, in which case the default type is applied.
    setup : str, optional
        Name of the setup to use as the nominal. The default is
        ``None``, in which case the active setup is used or
        nothing is used.
    version : str, int, float, optional
        Version of AEDT to use. The default is ``None``, in which case
        the active version or latest installed version is  used.
        This parameter is ignored when Script is launched within AEDT.
        Examples of input values are ``232``, ``23.2``,``2023.2``,``"2023.2"``.
    non_graphical : bool, optional
        Whether to run AEDT in non-graphical mode. The default
        is ``False``, in which case AEDT is launched in graphical mode.
        This parameter is ignored when a script is launched within AEDT.
    new_desktop : bool, optional
        Whether to launch an instance of AEDT in a new thread, even if
        another instance of the ``specified_version`` is active on the
        machine.  The default is ``False``. This parameter is ignored when
        a script is launched within AEDT.
    close_on_exit : bool, optional
        Whether to release AEDT on exit. The default is ``False``.
    student_version : bool, optional
        Whether to open the AEDT student version. The default is ``False``.
        This parameter is ignored when Script is launched within AEDT.
    machine : str, optional
        Machine name to which connect the oDesktop Session. Works only in 2022 R2
        or later. The remote server must be up and running with the command
        `"ansysedt.exe -grpcsrv portnum"`. If a machine is `"localhost"`, the
        server also starts if not present.
    port : int, optional
        Port number on which to start the oDesktop communication on an already existing server.
        This parameter is ignored when creating a new server. It works only in 2022 R2 or
        later. The remote server must be up and running with the command
        `"ansysedt.exe -grpcsrv portnum"`.
    aedt_process_id : int, optional
        Process ID for the instance of AEDT to point PyAEDT at. The default is
        ``None``. This parameter is only used when ``new_desktop = False``.
    remove_lock : bool, optional
        Whether to remove lock to project before opening it or not.
        The default is ``False``, which means to not unlock
        the existing project if needed and raise an exception.

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

    Create an instance of Circuit using the 2023 R2 version and
    open the specified project, which is ``"myfile.aedt"``.

    >>> aedtapp = Circuit(version=2023.2, project="myfile.aedt")

    Create an instance of Circuit using the 2023 R2 student version and open
    the specified project, which is named ``"myfile.aedt"``.

    >>> hfss = Circuit(version="2023.2", project="myfile.aedt", student_version=True)

    """

    @pyaedt_function_handler(
        designname="design",
        projectname="project",
        specified_version="version",
        setup_name="setup",
        new_desktop_session="new_desktop",
    )
    def __init__(
        self,
        project=None,
        design=None,
        solution_type=None,
        setup=None,
        version=None,
        non_graphical=False,
        new_desktop=False,
        close_on_exit=False,
        student_version=False,
        machine="",
        port=0,
        aedt_process_id=None,
        remove_lock=False,
    ):
        FieldAnalysisCircuit.__init__(
            self,
            "Circuit Design",
            project,
            design,
            solution_type,
            setup,
            version,
            non_graphical,
            new_desktop,
            close_on_exit,
            student_version,
            machine,
            port,
            aedt_process_id,
            remove_lock=remove_lock,
        )
        ScatteringMethods.__init__(self, self)
        self.onetwork_data_explorer = self._desktop.GetTool("NdExplorer")

    def _init_from_design(self, *args, **kwargs):
        self.__init__(*args, **kwargs)

    def _get_number_from_string(self, stringval):
        value = stringval[stringval.find("=") + 1 :].strip().replace("{", "").replace("}", "").replace(",", ".")
        value = value.replace("µ", "u")
        try:
            float(value)
            return value
        except Exception:
            return from_rkm_to_aedt(value)

    @pyaedt_function_handler(file_to_import="input_file")
    def create_schematic_from_netlist(self, input_file):
        """Create a circuit schematic from an HSpice netlist.

        Supported currently are:

        * R
        * L
        * C
        * Diodes
        * Bjts
        * Discrete components with syntax ``Uxxx net1 net2 ... netn modname``

        Parameters
        ----------
        input_file : str
            Full path to the HSpice file to import.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        """
        units = self.modeler.schematic_units
        self.modeler.schematic_units = "meter"
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
        with open_file(input_file, "rb") as f:
            for line in f:
                line = line.decode("utf-8")
                if ".param" in line[:7].lower():
                    try:
                        param_line = " ".join(line[7:].split())
                        param_re = re.split("[ =]", param_line)

                        ppar = param_re[0]
                        pval = param_re[1]
                        self[ppar] = pval
                        xpos = 0.0254
                    except Exception:
                        self.logger.error("Failed to parse line '{}'.".format(line))
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
            self.modeler.schematic.disable_data_netlist(assignment="Models_Netlist")
            xpos += 0.0254
        counter = 0
        with open_file(input_file, "rb") as f:
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
                        except Exception:
                            self.logger.warning(
                                "Component {} was not imported. Check it and manually import".format(name)
                            )
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
                                parameter, pins, refbase=fields[0][0], parameters=parameter_list, values=parameter_value
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
                            parameter, pins, refbase=fields[0][0], parameters=parameter_list, values=parameter_value
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
                elif fields[0][0].lower() == "k":
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
                elif not any(word in line.lower() for word in [".param", ".model", ".lib"]):
                    self.logger.warning("%s could not be imported", line)
                if mycomp:
                    id = 1
                    for pin in mycomp.pins:
                        pos = pin.location
                        if pos[0] < xpos:
                            angle = 0.0
                        else:
                            angle = math.pi
                        if fields[id] == "0":
                            gnd_pos = self.modeler.schematic._convert_point_to_units([0, -0.00254])
                            new_pos = [i + j for i, j in zip(pos, gnd_pos)]
                            self.modeler.schematic.create_gnd([new_pos[0], new_pos[1]])
                        else:
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
        self.modeler.schematic_units = units
        self.logger.info("Netlist was correctly imported into %s", self.design_name)
        return True

    @pyaedt_function_handler(path="input_file")
    def get_ibis_model_from_file(self, input_file, is_ami=False):
        """Create an IBIS model based on the data contained in an IBIS file.

        Parameters
        ----------
        input_file : str
            Path of the IBIS file.
        is_ami : bool, optional
            Whether the file to import is an IBIS AMI file. The
            default is ``False``, in which case it is an IBIS file.

        Returns
        -------
        :class:`pyaedt.generic.ibis_reader.Ibis`
            IBIS object exposing all data from the IBIS file.
        """
        if is_ami:
            reader = ibis_reader.AMIReader(input_file, self)
        else:
            reader = ibis_reader.IbisReader(input_file, self)
        reader.parse_ibis_file()
        return reader.ibis_model

    @pyaedt_function_handler(file_to_import="input_file")
    def create_schematic_from_mentor_netlist(self, input_file):
        """Create a circuit schematic from a Mentor netlist.

        Supported currently are:

        * R
        * L
        * C
        * Diodes
        * Bjts
        * Discrete components with syntax ``Uxxx net1 net2get_source_pin_names ... netn modname``

        Parameters
        ----------
        input_file : str
            Full path to the HSpice file to import.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        """
        units = self.modeler.schematic_units
        self.modeler.schematic_units = "meter"
        xpos = 0
        ypos = 0
        delta = 0.0508
        use_instance = True
        my_netlist = []
        with open_file(input_file, "r") as f:
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
                        self.logger.info("Page port was not created.")
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
                self.modeler.schematic.create_page_port(netname, [xpos, page_pos], 0.0)
                ypos += delta
                if ypos > delta * column_number:
                    xpos += delta
                    ypos = 0

        self.logger.info("Netlist was correctly imported into %s", self.design_name)
        self.modeler.schematic_units = units
        return True

    @pyaedt_function_handler(refid="reference_id")
    def retrieve_mentor_comp(self, reference_id):
        """Retrieve the type of the Mentor netlist component for a given reference ID.

        Parameters
        ----------
        reference_id : list
            Reference ID.

        Returns
        -------
        str
            Type of the Mentor netlist component.

        """
        if reference_id[1] == "R":
            return "resistor:RES."
        elif reference_id[1] == "C":
            return "capacitor:CAP."
        elif reference_id[1] == "L":
            return "inductor:COIL."
        elif reference_id[1] == "D":
            return "diode"
        elif reference_id[1] == "Q":
            return "transistor:NPN"
        else:
            return ""

    @pyaedt_function_handler()
    def get_source_pin_names(
        self, source_design_name, source_project_name=None, source_project_path=None, port_selector=3
    ):
        """Retrieve pin names.

        Parameters
        ----------
        source_design_name : str
            Name of the source design.
        source_project_name : str, optional
            Name of the source project. The default is ``None``.
        source_project_path : str, optional
            Path to the source project if different than the existing path. The default is ``None``.
        port_selector : int, optional
            Type of the port. Options are ``1``, ``2``, and ``3``, corresponding respectively to ``"Wave Port"``,
            ``"Terminal"``, or ``"Circuit Port"``. The default is ``3``, which is a circuit port.

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
                "If the source project is different from the current one, `source_project_path` must also be provided."
            )
        if source_project_path and not source_project_name:
            raise AttributeError(
                "When `source_project_path` is specified, `source_project_name` must also be provided."
            )
        if not source_project_name or self.project_name == source_project_name:
            oSrcProject = self._desktop.GetActiveProject()
        else:
            self._desktop.OpenProject(source_project_path)
            oSrcProject = self._desktop.SetActiveProject(source_project_name)
        oDesign = oSrcProject.SetActiveDesign(source_design_name)
        if is_linux and settings.aedt_version == "2024.1":
            time.sleep(1)
            self._desktop.CloseAllWindows()
        tmp_oModule = oDesign.GetModule("BoundarySetup")
        port = None
        if port_selector == 1:
            port = "Wave Port"
        elif port_selector == 2:
            port = "Terminal"
        elif port_selector == 3:
            port = "Circuit Port"
        if not port:
            return False
        pins = list(tmp_oModule.GetExcitationsOfType(port))
        self.logger.info("%s Excitations Pins found.", len(pins))
        return pins

    @pyaedt_function_handler(filename="input_file", solution_name="solution")
    def import_touchstone_solution(self, input_file, solution="Imported_Data"):
        """Import a Touchstone file as the solution.

        Parameters
        ----------
        input_file : str
            Name of the Touchstone file.
        solution : str, optional
            Name of the solution. The default is ``"Imported_Data"``.

        Returns
        -------
        list
            List of ports.

        References
        ----------

        >>> oDesign.ImportData
        """
        if input_file[-2:] == "ts":
            with open_file(input_file, "r") as f:
                lines = f.readlines()
                for i in lines:
                    if "[Number of Ports]" in i:
                        ports = int(i[i.find("]") + 1 :])
                portnames = [i.split(" = ")[1].strip() for i in lines if "! Port" in i[:9]]
                if not portnames:
                    portnames = ["Port{}".format(i + 1) for i in range(ports)]
        else:
            re_filename = re.compile(r"\.s(?P<ports>\d+)+p", re.I)
            m = re_filename.search(input_file)
            ports = int(m.group("ports"))
            portnames = None
            with open_file(input_file, "r") as f:
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
            input_file,
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
            solution,
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
        self.logger.info("Touchstone file was correctly imported into %s", self.design_name)
        return portnames

    @pyaedt_function_handler(designname="design", setupname="setup")
    def export_fullwave_spice(
        self,
        design=None,
        setup=None,
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
        design : str, optional
            Name of the design or the full path to the solution file if it is an imported file.
            The default is ``None``.
        setup : str, optional
            Name of the setup if it is a design. The default is ``None``.
        is_solution_file : bool, optional
            Whether it is an imported solution file. The default is ``False``.
        filename : str, optional
            Full path and name for exporting the HSpice file.
            The default is ``None``, in which case the file is exported to the working directory.
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
        if not design:
            design = self.design_name
        if not filename:
            filename = os.path.join(self.working_directory, self.design_name + ".sp")
        if is_solution_file:
            setup = design
            design = ""
        else:
            if not setup:
                setup = self.nominal_sweep
        self.onetwork_data_explorer.ExportFullWaveSpice(
            design,
            is_solution_file,
            setup,
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

    @pyaedt_function_handler(
        plot_name="name", curvenames="curves", solution_name="solution", variation_dict="variations"
    )
    def create_touchstone_report(
        self,
        name,
        curves,
        solution=None,
        variations=None,
        differential_pairs=False,
        subdesign_id=None,
    ):
        """
        Create a Touchstone plot.

        Parameters
        ----------
        name : str
            Name of the plot.
        curves : list
            List of names for the curves to plot.
        solution : str, optional
            Name of the solution. The default is ``None``.
        variations : dict, optional
            Dictionary of variation names. The default is ``None``.
        differential_pairs : bool, optional
            Whether the plot is on differential pairs traces. The default is ``False``.
        subdesign_id : int, optional
            Specify a subdesign ID to export a Touchstone file of this subdesign. The default value is ``None``.
        Returns
        -------
        bool
           ``True`` when successful, ``False`` when failed.

        References
        ----------

        >>> oModule.CreateReport
        """
        if not solution:
            solution = self.nominal_sweep
        variations_dict = {"Freq": ["All"]}
        if variations:
            for el in variations:
                variations_dict[el] = [variations[el]]
        dif = None
        if differential_pairs:
            dif = "Differential Pairs"
        return self.post.create_report(
            curves, solution, variations=variations_dict, context=dif, subdesign_id=subdesign_id, plot_name=name
        )

    @pyaedt_function_handler(instance_name="instance", setup_name="setup")
    def push_excitations(self, instance, thevenin_calculation=False, setup="LinearFrequency"):
        """Push excitations for a linear frequency setup.

        Parameters
        ----------
        instance : str
            Name of the instance.
        thevenin_calculation : bool, optional
            Whether to perform the Thevenin equivalent calculation. The default is ``False``.
        setup : str, optional
            Name of the solution setup to push. The default is ``"LinearFrequency"``.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        References
        ----------

        >>> oEditor.PushExcitations
        """
        arg = ["NAME:options", "CalcThevenin:=", thevenin_calculation, "Sol:=", setup]

        self.modeler.oeditor.PushExcitations(instance, arg)
        return True

    @pyaedt_function_handler(instance_name="instance", setup_name="setup")
    def push_time_excitations(
        self,
        instance,
        start=0.0,
        stop=0.0,
        harmonics=100,
        window_type="Rectangular",
        width_percentage=100.0,
        kaiser=0.0,
        correct_coherent_gain=True,
        setup="NexximTransient",
    ):
        """Push excitations for a transient setup.

        Parameters
        ----------
        instance : str
            Name of the instance.
        start : float, optional
            Start time in ``seconds``. The default is ``0.0``.
        stop : float, optional
            Stop time in ``seconds``. The default is ``0.0``.
        harmonics : int, optional
            Maximum number of harmonics. The default is ``100``.
        window_type : str, optional
            Window type. Available windows are: ``Rectangular``, ``Barlett``, ``Blackman``, ``Hamming``,
            ``Hanning``, ``Kaiser``, ``Welch``, ``Weber``, ``Lanzcos``. The default is ``Rectangular``.
        width_percentage : float, optional
            Width percentage. The default is ``100.0``.
        kaiser : float, optional
            Kaiser value. The default is ``0.0``.
        correct_coherent_gain : bool, optional
            Whether to enable the coherent gain correction. The default is ``True``.
        setup : str, optional
            Name of the solution setup to push. The default is ``"LinearFrequency"``.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        References
        ----------

        >>> oEditor.PushExcitations
        """
        arg = [
            "NAME:options",
            "transient:=",
            [
                "start:=",
                start,
                "stop:=",
                stop,
                "maxHarmonics:=",
                harmonics,
                "winType:=",
                window_type,
                "widthPct:=",
                width_percentage,
                "kaiser:=",
                kaiser,
                "correctCoherentGain:=",
                correct_coherent_gain,
            ],
            "Sol:=",
            setup,
        ]
        self.modeler.oeditor.PushExcitations(instance, arg)
        return True

    @pyaedt_function_handler()
    def create_source(self, source_type, name=None):
        """Create a source in Circuit.

        Parameters
        ----------
        source_type : str
            Source type to create. Sources available are:

            * PowerSin.
            * PowerIQ.
            * VoltageFrequencyDependent.
            * VoltageDC.
            * VoltageSin.
            * CurrentSin.

        name : str, optional
            Source name.

        Returns
        -------
        :class:`pyaedt.modules.Boundary.Source`
            Circuit Source Object.

        References
        ----------

        >>> oDesign.UpdateSources
        """
        if not name:
            name = generate_unique_name("Source")
        if name in self.source_names:
            self.logger.warning("Source name is defined in the design.")
            return False
        if source_type not in SourceKeys.SourceNames:
            self.logger.warning("Source type is not correct.")
            return False
        if source_type == "PowerSin":
            new_source = PowerSinSource(self, name, source_type)
        elif source_type == "PowerIQ":
            new_source = PowerIQSource(self, name, source_type)
        elif source_type == "VoltageFrequencyDependent":
            new_source = VoltageFrequencyDependentSource(self, name, source_type)
        elif source_type == "VoltageDC":
            new_source = VoltageDCSource(self, name, source_type)
        elif source_type == "VoltageSin":
            new_source = VoltageSinSource(self, name, source_type)
        elif source_type == "CurrentSin":
            new_source = CurrentSinSource(self, name, source_type)
        else:
            new_source = Sources(self, name, source_type)
        new_source.create()
        if not self._internal_sources:
            self._internal_sources = {name: new_source}
        else:
            self._internal_sources.update({name: new_source})
        return new_source

    @pyaedt_function_handler()
    def assign_voltage_sinusoidal_excitation_to_ports(self, ports):
        """Assign a voltage sinusoidal excitation to circuit ports.

        Parameters
        ----------
        ports : list
            List of circuit ports to assign to the sinusoidal excitation.

        Returns
        -------
        :class:`pyaedt.modules.Boundary.Source`
            Circuit Source Object.

        References
        ----------

        >>> oDesign.UpdateSources
        """

        source_v = self.create_source(source_type="VoltageSin")
        for port in ports:
            self.excitation_objects[port].enabled_sources.append(source_v.name)
            self.excitation_objects[port].update()
        return source_v

    @pyaedt_function_handler()
    def assign_current_sinusoidal_excitation_to_ports(self, ports):
        """Assign a current sinusoidal excitation to circuit ports.

        Parameters
        ----------
        ports : list
            List of circuit ports to assign to the sinusoidal excitation.

        Returns
        -------
        :class:`pyaedt.modules.Boundary.Source`
            Circuit Source Object.

        References
        ----------

        >>> oDesign.UpdateSources
        """
        source_i = self.create_source(source_type="CurrentSin")
        for port in ports:
            self.excitation_objects[port].enabled_sources.append(source_i.name)
            self.excitation_objects[port].update()
        return source_i

    @pyaedt_function_handler()
    def assign_power_sinusoidal_excitation_to_ports(self, ports):
        """Assign a power sinusoidal excitation to circuit ports.

        Parameters
        ----------
        ports : list
            List of circuit ports to assign to the sinusoidal excitation.

        Returns
        -------
        :class:`pyaedt.modules.Boundary.Source`
            Circuit Source Object.

        References
        ----------

        >>> oDesign.UpdateSources
        """
        source_p = self.create_source(source_type="PowerSin")
        for port in ports:
            self.excitation_objects[port].enabled_sources.append(source_p.name)
            self.excitation_objects[port].update()
        return source_p

    @pyaedt_function_handler(filepath="input_file")
    def assign_voltage_frequency_dependent_excitation_to_ports(self, ports, input_file):
        """Assign a frequency dependent excitation to circuit ports from a frequency dependent source (FDS format).

        Parameters
        ----------
        ports : list
            List of circuit ports to assign to the frequency dependent excitation.
        input_file : str
            Path to the frequency dependent file.

        Returns
        -------
        :class:`pyaedt.modules.Boundary.Source`
            Circuit Source Object.

        References
        ----------

        >>> oDesign.UpdateSources
        """
        if not os.path.exists(input_file) or os.path.splitext(input_file)[1] != ".fds":
            self.logger.error("Introduced file is not correct. Check path and format.")
            return False

        if not all(elem in self.excitations for elem in ports):
            self.logger.error("Defined ports do not exist")
            return False

        source_freq = self.create_source(source_type="VoltageFrequencyDependent")
        source_freq.fds_filename = input_file
        for port in ports:
            self.excitation_objects[port].enabled_sources.append(source_freq.name)
            self.excitation_objects[port].update()
        return source_freq

    @pyaedt_function_handler(
        positive_terminal="assignment",
        negative_terminal="reference",
        common_name="common_mode",
        diff_name="differential_mode",
        common_ref="common_reference",
        diff_ref_z="differential_reference",
    )
    def set_differential_pair(
        self,
        assignment,
        reference,
        common_mode=None,
        differential_mode=None,
        common_reference=25,
        differential_reference=100,
        active=True,
    ):
        """Add a differential pair definition.

        Parameters
        ----------
        assignment : str
            Name of the terminal to use as the positive terminal.
        reference : str
            Name of the terminal to use as the negative terminal.
        common_mode : str, optional
            Name for the common mode. The default is ``None``, in which case a unique name is assigned.
        differential_mode : str, optional
            Name for the differential mode. The default is ``None``, in which case a unique name is assigned.
        common_reference : float, optional
            Reference impedance for the common mode. The units are Ohm. The default is ``25``.
        differential_reference : float, optional
            Reference impedance for the differential mode. Units are Ohm. Default is ``100``.
        active : bool, optional
            Whether to set the differential pair as active. The default is ``True``.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        References
        ----------
        >>> oDesign.SetDiffPairs
        """
        if not differential_mode:
            differential_mode = generate_unique_name("Diff")
        if not common_mode:
            common_mode = generate_unique_name("Comm")

        arg1 = [
            "Pos:=",
            assignment,
            "Neg:=",
            reference,
            "On:=",
            active,
            "matched:=",
            False,
            "Dif:=",
            differential_mode,
            "DfZ:=",
            [float(differential_reference), 0],
            "Com:=",
            common_mode,
            "CmZ:=",
            [float(common_reference), 0],
        ]

        arg = ["NAME:DiffPairs"]
        arg.append("Pair:=")
        arg.append(arg1)

        tmpfile1 = os.path.join(self.working_directory, generate_unique_name("tmp"))
        self.odesign.SaveDiffPairsToFile(tmpfile1)
        with open_file(tmpfile1, "r") as fh:
            lines = fh.read().splitlines()

        old_arg = []
        for line in lines:
            data = line.split(",")
            data_arg = [
                "Pos:=",
                data[0],
                "Neg:=",
                data[1],
                "On:=",
                data[2] == "1",
                "matched:=",
                False,
                "Dif:=",
                data[4],
                "DfZ:=",
                [float(data[5]), 0],
                "Com:=",
                data[6],
                "CmZ:=",
                [float(data[7]), 0],
            ]
            old_arg.append(data_arg)

        for arg2 in old_arg:
            arg.append("Pair:=")
            arg.append(arg2)

        try:
            os.remove(tmpfile1)
        except Exception:  # pragma: no cover
            self.logger.warning("ERROR: Cannot remove temp files.")

        try:
            self.odesign.SetDiffPairs(arg)
        except Exception:  # pragma: no cover
            return False
        return True

    @pyaedt_function_handler(filename="input_file")
    def load_diff_pairs_from_file(self, input_file):
        """Load differtential pairs definition from a file.

        You can use the ``save_diff_pairs_to_file()`` method to obtain the file format.
        New definitions are added only if they are compatible with the existing definitions in the project.

        Parameters
        ----------
        input_file : str
            Full qualified name of the file containing the differential pairs definition.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        References
        ----------
        >>> oDesign.LoadDiffPairsFromFile
        """
        if not os.path.isfile(input_file):  # pragma: no cover
            raise ValueError("{}: The specified file could not be found.".format(input_file))

        try:
            new_file = os.path.join(os.path.dirname(input_file), generate_unique_name("temp") + ".txt")
            with open_file(input_file, "r") as file:
                filedata = file.read().splitlines()
            with io.open(new_file, "w", newline="\n") as fh:
                for line in filedata:
                    fh.write(line + "\n")

            self.odesign.LoadDiffPairsFromFile(new_file)
            os.remove(new_file)
        except Exception:  # pragma: no cover
            return False
        return True

    @pyaedt_function_handler(filename="output_file")
    def save_diff_pairs_to_file(self, output_file):
        """Save differential pairs definition to a file.

        If the file that is specified already exists, it is overwritten.

        Parameters
        ----------
        output_file : str
            Full qualified name of the file to save the differential pairs definition to.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        References
        ----------
        >>> oDesign.SaveDiffPairsToFile
        """
        self.odesign.SaveDiffPairsToFile(output_file)

        return os.path.isfile(output_file)

    @pyaedt_function_handler(netlist_file="input_file", datablock_name="name")
    def add_netlist_datablock(self, input_file, name=None):
        """Add a new netlist data block to the circuit schematic.

        Parameters
        ----------
        input_file : str
            Path to the netlist file.
        name : str, optional
            Name of the data block.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.
        """
        if not os.path.exists(input_file):
            self.logger.error("Netlist File doesn't exists")
            return False
        if not name:
            name = generate_unique_name("Inc")

        tmp_oModule = self.odesign.GetModule("DataBlock")
        tmp_oModule.AddNetlistDataBlock(
            ["NAME:DataBlock", "name:=", name, "filename:=", input_file, "filelocation:=", 0]
        )
        return True

    @pyaedt_function_handler(filepath="input_file")
    def browse_log_file(self, input_file=None):
        """Save the most recent log file in a new directory.

        Parameters
        ----------
        input_file : str, optional
            File path to save the new log file to. The default is the ``pyaedt`` folder.

        Returns
        -------
        str
            File Path.
        """
        if input_file and not os.path.exists(os.path.normpath(input_file)):
            self.logger.error("Path does not exist.")
            return None
        elif not input_file:
            input_file = os.path.join(os.path.normpath(self.working_directory), "logfile")
            if not os.path.exists(input_file):
                os.mkdir(input_file)

        results_path = os.path.join(os.path.normpath(self.results_directory), self.design_name)
        results_temp_path = os.path.join(results_path, "temp")

        # Check if .log exist in temp folder
        if os.path.exists(results_temp_path) and search_files(results_temp_path, "*.log"):
            # Check the most recent
            files = search_files(results_temp_path, "*.log")
            latest_file = max(files, key=os.path.getctime)
        elif os.path.exists(results_path) and search_files(results_path, "*.log"):
            # Check the most recent
            files = search_files(results_path, "*.log")
            latest_file = max(files, key=os.path.getctime)
        else:
            self.logger.error("Design not solved")
            return None

        shutil.copy(latest_file, input_file)
        filename = os.path.basename(latest_file)
        return os.path.join(input_file, filename)

    @pyaedt_function_handler()
    def connect_circuit_models_from_multi_zone_cutout(
        self, project_connections, edb_zones_dict, ports=None, schematic_units="mm", model_inc=50
    ):
        """Connect circuit model from a multizone clipped project.

        Parameters
        ----------
        project_connections : dic[str][str]
            Dictionary of project connections returned from the
            ``edb.get_connected_ports_from_multizone_cutout()`` method.
        edb_zones_dict : dict[str][EDB PolygonData]
            Dictionary of zones returned by the ``edb.copy_zones()`` method.
        ports : dict[str][str]
            dictionary return from command edb.cutout_multizone_layout(). These ports are the ones created before
            processing the multizone clipping. Like for instance ports created on components resulting from previous
            automated workflow execution.
        schematic_units : str, optional
            Units for the schematic, such as ``"mm"`` or ``"in"``. The
            default is ``"mm"``.
        model_inc : float, optional
            Distance increment for adding models. The default is ``50``.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        Examples
        --------
        These commands show how to get input arguments described in this method:
        - project_connections
        - edb_zone_dict
        -
        >>> edb = Edb(edb_file)
        >>> edb_zones = edb.copy_zones(r"C:\\Temp\\test")
        >>> defined_ports, project_connections = edb.cutout_multizone_layout(edb_zones, common_reference_net)
        >>> circ = Circuit()
        >>> circ.connect_circuit_models_from_multi_zone_cutout(project_connexions, edb_zones, defined_ports)
        """
        if project_connections and edb_zones_dict:
            self.modeler.schematic_units = schematic_units
            inc = model_inc
            ind = 1
            for edb_file in list(edb_zones_dict.keys()):
                hfss3d_layout_model = self.import_edb_in_circuit(input_dir=edb_file)
                model_position = [ind * inc, 0]
                hfss3d_layout_model.location = model_position
                ind += 1
            for connection in project_connections:
                pin1 = None
                pin2 = None
                model1 = next(
                    cmp for cmp in list(self.modeler.schematic.components.values()) if connection[0][0] in cmp.name
                )
                if model1:
                    try:
                        pin1 = next(pin for pin in model1.pins if pin.name == connection[0][1])
                    except Exception:
                        print("failed to get pin1")
                model2 = next(
                    cmp for cmp in list(self.modeler.schematic.components.values()) if connection[1][0] in cmp.name
                )
                if model2:
                    try:
                        pin2 = next(pin for pin in model2.pins if pin.name == connection[1][1])
                    except Exception:
                        print("failed to get pin2")
                if pin1 and pin2:
                    pin1.connect_to_component(component_pin=pin2, use_wire=False)
            for model_name, ports in ports.items():
                if any(cmp for cmp in list(self.modeler.schematic.components.values()) if model_name in cmp.name):
                    model = next(
                        cmp for cmp in list(self.modeler.schematic.components.values()) if model_name in cmp.name
                    )
                    if model:
                        for port_name in ports:
                            try:
                                model_pin = next(pin for pin in model.pins if pin.name == port_name)
                            except StopIteration:
                                model_pin = None
                            if model_pin:
                                self.modeler.components.create_interface_port(port_name, model_pin.location)
            self.save_project()
            return True
        return False

    @pyaedt_function_handler(edb_path="input_dir")
    def import_edb_in_circuit(self, input_dir):
        """Import an EDB design inside a Circuit project.

        Parameters
        ----------
        input_dir : str
            Path of the EDB file to copy.

        Returns
        -------
            ``Hfss3DLayout`` component instance.
        """
        hfss = Hfss3dLayout(input_dir)
        try:
            hfss.edit_cosim_options(
                simulate_missing_solution=True,
                setup_override_name=hfss.setup_names[0],
                sweep_override_name=hfss.existing_analysis_sweeps[0].split(":")[1].strip(" "),
            )
        except Exception:
            self.logger.error(
                "Failed to setup co-simulation settings, make sure the simulation setup is properly defined"
            )
        active_project = hfss.desktop_class.active_project(hfss.project_name)
        active_project.CopyDesign(hfss.design_name)
        active_project = hfss.desktop_class.active_project(self.project_name)
        active_project.Paste()
        hfss_3d_layout_model = self.modeler.schematic.add_subcircuit_3dlayout(hfss.design_name)
        hfss.close_project(save=False)
        return hfss_3d_layout_model

    @pyaedt_function_handler(touchstone="input_file")
    def create_tdr_schematic_from_snp(
        self,
        input_file,
        probe_pins,
        probe_ref_pins=None,
        termination_pins=None,
        differential=True,
        rise_time=30,
        use_convolution=True,
        analyze=True,
        design_name="LNA",
    ):
        """Create a schematic from a Touchstone file and automatically setup a TDR transient analysis.

        Parameters
        ----------
        input_file : str
            Full path to the sNp file.
        probe_pins : list
            List of pins to attach to the probe components.
        probe_ref_pins : list, optional
            Reference pins to attach to probe components. The default is ``None``.
            This parameter is valid only in differential TDR probes.
        termination_pins : list, optional
            Pins to terminate. The default is ``None``.
        differential : bool, optional
            Whether the buffers are differential. The default is ``True``. If ``False``, the
            pins are single ended.
        rise_time : float, int, optional
            Rise time of the input pulse in picoseconds. The default is ``30``.
        use_convolution : bool, optional
            Whether to use convolution for the Touchstone file. The default is ``True``.
            If ``False``, state-space is used.
        analyze : bool
             Whether to automatically assign differential pairs. The default is ``False``.
        design_name : str, optional
            New schematic name. The default is ``"LNA"``.

        Returns
        -------

        """
        if design_name in self.design_list:
            self.logger.warning("Design already exists. renaming.")
            design_name = generate_unique_name(design_name)
        self.insert_design(design_name)
        if isinstance(input_file, type(Hfss3dLayout)):
            touchstone_path = input_file.export_touchstone()
        else:
            touchstone_path = input_file

        sub = self.modeler.components.create_touchstone_component(touchstone_path)
        center_x = sub.location[0]
        center_y = sub.location[1]
        left = 0
        delta_y = -1 * sub.location[1] - 2000 - 50 * len(probe_pins)
        if differential:
            tdr_probe = self.modeler.components.components_catalog["TDR_Differential_Ended"]
        else:
            tdr_probe = self.modeler.components.components_catalog["TDR_Single_Ended"]
        tdr_probe_names = []
        for i, probe_pin in enumerate(probe_pins):
            pos_y = unit_converter(delta_y - left * 1000, input_units="mil", output_units=self.modeler.schematic_units)
            left += 1
            new_tdr_comp = tdr_probe.place("Tdr_probe", [center_x, center_y + pos_y], angle=-90)
            try:
                if isinstance(probe_pin, int):
                    p_pin = probe_pin
                    if differential:
                        n_pin = probe_ref_pins[i]
                else:
                    p_pin = [k for k in sub.pins if k.name == probe_pin][0]
                    if differential:
                        n_pin = [k for k in sub.pins if k.name == probe_ref_pins[i]][0]
            except IndexError:
                self.logger.error("Failed to retrieve the pins.")
                return False
            for pin in sub.pins:
                if not termination_pins or (pin.name in termination_pins):
                    loc = pin.location
                    loc1 = unit_converter(1500, input_units="mil", output_units=self.modeler.schematic_units)
                    if loc[0] < center_x:
                        p1 = self.modeler.components.create_interface_port(
                            name=pin.name, location=[loc[0] - loc1, loc[1]]
                        )
                    else:
                        p1 = self.modeler.components.create_interface_port(
                            name=pin.name, location=[loc[0] + loc1, loc[1]]
                        )
                    p1.pins[0].connect_to_component(pin, use_wire=True)

            _, first, second = new_tdr_comp.pins[0].connect_to_component(p_pin)
            self.modeler.move(first, [0, 100], "mil")
            if second.pins[0].location[0] > center_x:
                self.modeler.move(second, [1000, 0], "mil")
            else:
                self.modeler.move(second, [-1000, 0], "mil")
            if differential:
                _, first, second = new_tdr_comp.pins[1].connect_to_component(n_pin)
                self.modeler.move(first, [0, -100], "mil")
                if second.pins[0].location[0] > center_x:
                    self.modeler.move(second, [1000, 0], "mil")
                else:
                    self.modeler.move(second, [-1000, 0], "mil")
            new_tdr_comp.parameters["Pulse_repetition"] = "{}ms".format(rise_time * 1e5)
            new_tdr_comp.parameters["Rise_time"] = "{}ps".format(rise_time)
            if differential:
                tdr_probe_names.append("O(A{}:zdiff)".format(new_tdr_comp.id))
            else:
                tdr_probe_names.append("O(A{}:zl)".format(new_tdr_comp.id))

        setup = self.create_setup(name="Transient_TDR", setup_type=self.SETUPS.NexximTransient)
        setup.props["TransientData"] = ["{}ns".format(rise_time / 4), "{}ns".format(rise_time * 1000)]
        if use_convolution:
            self.oanalysis.AddAnalysisOptions(
                [
                    "NAME:DataBlock",
                    "DataBlockID:=",
                    8,
                    "Name:=",
                    "Nexxim Options",
                    [
                        "NAME:ModifiedOptions",
                        "ts_convolution:=",
                        True,
                    ],
                ]
            )
            setup.props["OptionName"] = "Nexxim Options"
        if analyze:
            self.analyze()
            for trace in tdr_probe_names:
                self.post.create_report(trace)
        return True, tdr_probe_names

    @pyaedt_function_handler(touchstone="input_file")
    def create_lna_schematic_from_snp(
        self,
        input_file,
        start_frequency=0,
        stop_frequency=30,
        auto_assign_diff_pairs=False,
        separation=".",
        pattern=None,
        analyze=True,
        design_name="LNA",
    ):
        """Create a schematic from a Touchstone file and automatically set up an LNA analysis.

        This method optionally assigns differential pairs automatically based on name pattern.

        Parameters
        ----------
        input_file : str
            Full path to the sNp file.
        start_frequency : int, float, optional
            Start frequency in GHz of the LNA setup. The default is ``0``.
        stop_frequency  : int, float, optional
            Stop frequency in GHz of the LNA setup. The default is ``30``.
        auto_assign_diff_pairs : bool
            Whether to automatically assign differential pairs. The default is ``False``.
        separation : str, optional
            Character to use to separate port names. The default is ``"."``.
        pattern : list, optional
            Port name pattern. The default is ``["component", "pin", "net"]``.
        analyze : bool
             Whether to automatically assign differential pairs. The default is ``False``.
        design_name : str, optional
            New schematic name. The default is ``"LNA"``.

        Returns
        -------
        (bool, list, list)
            First argument is ``True`` if succeeded.
            Second and third argument are respectively names of the differential and common mode pairs.
        """
        if pattern is None:
            pattern = ["component", "pin", "net"]
        if design_name in self.design_list:
            self.logger.warning("Design already exists. renaming.")
            design_name = generate_unique_name(design_name)
        self.insert_design(design_name)
        if isinstance(input_file, type(Hfss3dLayout)):
            touchstone_path = input_file.export_touchstone()
        else:
            touchstone_path = input_file

        sub = self.modeler.components.create_touchstone_component(touchstone_path)

        ports = []
        center = sub.location[0]
        left = 0
        right = 0
        start = 1500
        for pin in sub.pins:
            loc = pin.location
            if loc[0] < center:
                delta = unit_converter(start + left * 200, input_units="mil", output_units=self.modeler.schematic_units)
                new_loc = [loc[0] - delta, loc[1]]
                left += 1
            else:
                delta = unit_converter(
                    start + right * 200, input_units="mil", output_units=self.modeler.schematic_units
                )
                new_loc = [loc[0] + delta, loc[1]]
                right += 1
            port = self.modeler.components.create_interface_port(name=pin.name, location=new_loc)
            port.pins[0].connect_to_component(assignment=pin, use_wire=True)
            ports.append(port)
        diff_pairs = []
        comm_pairs = []
        if auto_assign_diff_pairs:
            for pin in ports:
                pin_name = pin.name.split(separation)
                if pin_name[-1][-1] == "P":
                    component = pin_name[pattern.index("component")]
                    net = pin_name[pattern.index("net")]
                    for neg_pin in ports:
                        neg_pin_name = neg_pin.name.split(separation)
                        component_neg = neg_pin_name[pattern.index("component")]

                        net_neg = neg_pin_name[pattern.index("net")]

                        if component_neg == component and net_neg != net and net_neg[:-1] == net[:-1]:
                            self.set_differential_pair(
                                assignment=pin.name,
                                reference=neg_pin.name,
                                common_mode="COMMON_{}_{}".format(component, net),
                                differential_mode="{}_{}".format(component, net),
                                common_reference=25,
                                differential_reference=100,
                                active=True,
                            )
                            diff_pairs.append("{}_{}".format(component, net))
                            comm_pairs.append("COMMON_{}_{}".format(component, net))
                            break
        setup1 = self.create_setup()
        setup1.props["SweepDefinition"]["Data"] = "LINC {}GHz {}GHz 1001".format(start_frequency, stop_frequency)
        if analyze:
            self.analyze()
        return True, diff_pairs, comm_pairs

    @pyaedt_function_handler(touchstone="input_file")
    def create_ami_schematic_from_snp(
        self,
        input_file,
        ibis_ami,
        component_name,
        tx_buffer_name,
        rx_buffer_name,
        tx_pins,
        tx_refs,
        rx_pins,
        rx_refs,
        use_ibis_buffer=True,
        differential=True,
        bit_pattern=None,
        unit_interval=None,
        use_convolution=True,
        analyze=False,
        design_name="AMI",
    ):
        """Create a schematic from a Touchstone file and automatically set up an IBIS-AMI analysis.

        Parameters
        ----------
        input_file : str
            Full path to the sNp file.
        ibis_ami : str
            Full path to the IBIS file.
        component_name : str
            Component name in the IBIS file to assign to components.
        tx_buffer_name : str
            Transmission buffer name.
        rx_buffer_name : str
            Receiver buffer name
        tx_pins : list
            Pins to assign the transmitter IBIS.
        tx_refs : list
            Reference pins to assign the transmitter IBIS. This parameter is only used in
            a differential configuration.
        rx_pins : list
            Pins to assign the receiver IBIS.
        rx_refs : list
            Reference pins to assign the receiver IBIS. This parameter is only used
            in a differential configuration.
        use_ibis_buffer : bool, optional
            Whether to use the IBIS buffer. The default is ``True``. If ``False``, pins are used.
        differential : bool, optional
            Whether the buffers are differential. The default is ``True``. If ``False``,
            the buffers are single-ended.
        bit_pattern : str, optional
            IBIS bit pattern.
        unit_interval : str, optional
            Unit interval of the bit pattern.
        use_convolution : bool, optional
            Whether to use convolution for the Touchstone file. The default is
            ``True``. If ``False``, state-space is used.
        analyze : bool
             Whether to automatically assign differential pairs. The default is ``False``.
        design_name : str, optional
            New schematic name. The default is ``"LNA"``.


        Returns
        -------
        (bool, list, list)
            First argument is ``True`` if successful.
            Second and third arguments are respectively the names of the tx and rx mode probes.
        """
        if design_name in self.design_list:
            self.logger.warning("Design already exists. Renaming.")
            design_name = generate_unique_name(design_name)
        self.insert_design(design_name)
        if isinstance(input_file, type(Hfss3dLayout)):
            touchstone_path = input_file.export_touchstone()
        else:
            touchstone_path = input_file

        sub = self.modeler.components.create_touchstone_component(touchstone_path)
        center_x = sub.location[0]
        center_y = sub.location[1]
        left = 0
        delta_y = -1 * sub.location[1] - 2000 - 50 * len(tx_pins)
        ibis = self.get_ibis_model_from_file(ibis_ami, is_ami=True)
        tx_eye_names = []
        rx_eye_names = []
        for j in range(len(tx_pins)):
            pos_x = unit_converter(2000, input_units="mil", output_units=self.modeler.schematic_units)
            pos_y = unit_converter(delta_y - left * 800, input_units="mil", output_units=self.modeler.schematic_units)
            left += 1

            p_pin1 = [i for i in sub.pins if i.name == tx_pins[j]][0]
            p_pin2 = [i for i in sub.pins if i.name == rx_pins[j]][0]
            if differential:
                n_pin1 = [i for i in sub.pins if i.name == tx_refs[j]][0]
                n_pin2 = [i for i in sub.pins if i.name == rx_refs[j]][0]

            if use_ibis_buffer:
                buf = [k for k in ibis.components[component_name].buffer.keys() if k.startswith(tx_buffer_name + "_")]
                if differential:
                    buf = [k for k in buf if k.endswith("diff")]
                tx = ibis.components[component_name].buffer[buf[0]].insert(center_x - pos_x, center_y + pos_y)
                buf = [k for k in ibis.components[component_name].buffer.keys() if k.startswith(rx_buffer_name + "_")]
                if differential:
                    buf = [k for k in buf if k.endswith("diff")]
                rx = ibis.components[component_name].buffer[buf[0]].insert(center_x + pos_x, center_y + pos_y, 180)
            else:
                buf = [k for k in ibis.components[component_name].pins.keys() if k.startswith(tx_buffer_name + "_")]
                if differential:
                    buf = [k for k in buf if k.endswith("diff")]
                tx = ibis.components[component_name].pins[buf[0]].insert(center_x - pos_x, center_y + pos_y)
                buf = [k for k in ibis.components[component_name].pins.keys() if k.startswith(rx_buffer_name + "_")]
                if differential:
                    buf = [k for k in buf if k.endswith("diff")]
                rx = ibis.components[component_name].pins[buf[0]].insert(center_x + pos_x, center_y + pos_y, 180)

            tx_eye_names.append(tx.parameters["probe_name"])
            rx_eye_names.append(rx.parameters["source_name"])
            _, first, second = tx.pins[0].connect_to_component(p_pin1, page_port_angle=180)
            self.modeler.move(first, [0, 100], "mil")
            if second.pins[0].location[0] > center_x:
                self.modeler.move(second, [1000, 0], "mil")
            else:
                self.modeler.move(second, [-1000, 0], "mil")
            _, first, second = rx.pins[0].connect_to_component(p_pin2, page_port_angle=0)
            self.modeler.move(first, [0, -100], "mil")
            if second.pins[0].location[0] > center_x:
                self.modeler.move(second, [1000, 0], "mil")
            else:
                self.modeler.move(second, [-1000, 0], "mil")
            if differential:
                _, first, second = tx.pins[1].connect_to_component(n_pin1, page_port_angle=180)
                self.modeler.move(first, [0, -100], "mil")
                if second.pins[0].location[0] > center_x:
                    self.modeler.move(second, [1000, 0], "mil")
                else:
                    self.modeler.move(second, [-1000, 0], "mil")
                _, first, second = rx.pins[1].connect_to_component(n_pin2, page_port_angle=0)
                self.modeler.move(first, [0, 100], "mil")
                if second.pins[0].location[0] > center_x:
                    self.modeler.move(second, [1000, 0], "mil")
                else:
                    self.modeler.move(second, [-1000, 0], "mil")
            if unit_interval:
                tx.parameters["UIorBPSValue"] = unit_interval
            if bit_pattern:
                tx.parameters["BitPattern"] = "random_bit_count=2.5e3 random_seed=1"

        setup_ami = self.create_setup("AMI", "NexximAMI")
        if use_convolution:
            self.oanalysis.AddAnalysisOptions(
                [
                    "NAME:DataBlock",
                    "DataBlockID:=",
                    8,
                    "Name:=",
                    "Nexxim Options",
                    [
                        "NAME:ModifiedOptions",
                        "ts_convolution:=",
                        True,
                    ],
                ]
            )
            setup_ami.props["OptionName"] = "Nexxim Options"
        if analyze:
            setup_ami.analyze()
        return True, tx_eye_names, rx_eye_names
