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

"""This module contains the ``TwinBuilder`` class."""

from __future__ import absolute_import  # noreorder

import math
import os.path

from pyaedt.application.AnalysisTwinBuilder import AnalysisTwinBuilder
from pyaedt.application.Variables import Variable
from pyaedt.application.Variables import decompose_variable_value
from pyaedt.generic.general_methods import generate_unique_name
from pyaedt.generic.general_methods import is_number
from pyaedt.generic.general_methods import open_file
from pyaedt.generic.general_methods import pyaedt_function_handler


class TwinBuilder(AnalysisTwinBuilder, object):
    """Provides the Twin Builder application interface.

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
        Version of AEDT to use. The default is ``None``, in which
        case the active setup or latest installed version is
        used.
        Examples of input values are ``232``, ``23.2``,``2023.2``,``"2023.2"``.
    non_graphical : bool, optional
        Whether to launch AEDT in non-graphical mode. The default
        is ``False``, in which case AEDT is launched in graphical mode.
        This parameter is ignored when a script is launched within AEDT.
    new_desktop : bool, optional
        Whether to launch an instance of AEDT in a new thread, even if
        another instance of the ``specified_version`` is active on the
        machine.  The default is ``False``.
    close_on_exit : bool, optional
        Whether to release AEDT on exit. The default is ``False``.
    student_version : bool, optional
        Whether to open the AEDT student version. The default is ``False``.
    machine : str, optional
        Machine name to connect the oDesktop session to. This works only in 2022 R2
        or later. The remote server must be up and running with the command
        `"ansysedt.exe -grpcsrv portnum"`. If the machine is `"localhost"`,
        the server also starts if not present.
    port : int, optional
        Port number on which to start the oDesktop communication on an already existing server.
        This parameter is ignored when creating a new server. It works only in 2022 R2 or later.
        The remote server must be up and running with command `"ansysedt.exe -grpcsrv portnum"`.
    aedt_process_id : int, optional
        Process ID for the instance of AEDT to point PyAEDT at. The default is
        ``None``. This parameter is only used when ``new_desktop = False``.
    remove_lock : bool, optional
        Whether to remove lock to project before opening it or not.
        The default is ``False``, which means to not unlock
        the existing project if needed and raise an exception.

    Examples
    --------
    Create an instance of Twin Builder and connect to an existing
    Maxwell design or create a new Maxwell design if one does not
    exist.

    >>> from pyaedt import TwinBuilder
    >>> app = TwinBuilder()

    Create a instance of Twin Builder and link to a project named
    ``"projectname"``. If this project does not exist, create one with
    this name.

    >>> app = TwinBuilder(projectname)

    Create an instance of Twin Builder and link to a design named
    ``"designname"`` in a project named ``"projectname"``.

    >>> app = TwinBuilder(projectname, designame)

    Create an instance of Twin Builder and open the specified
    project, which is named ``"myfile.aedt"``.

    >>> app = TwinBuilder("myfile.aedt")
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
        """Constructor."""
        AnalysisTwinBuilder.__init__(
            self,
            "Twin Builder",
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

    def _init_from_design(self, *args, **kwargs):
        self.__init__(*args, **kwargs)

    @pyaedt_function_handler(file_to_import="input_file")
    def create_schematic_from_netlist(self, input_file):
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
        input_file : str
            Full path to the HSpice file.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        """
        xpos = 0
        ypos = 0
        delta = 0.0508
        use_instance = True
        with open_file(input_file, "r") as f:
            for line in f:
                mycomp = None
                fields = line.split(" ")
                name = fields[0]
                if fields[0][0] == "R":
                    value = fields[3][fields[3].find("=") + 1 :].strip()
                    mycomp = self.modeler.schematic.create_resistor(
                        name, value, [xpos, ypos], use_instance_id_netlist=use_instance
                    )
                elif fields[0][0] == "L":
                    value = fields[3][fields[3].find("=") + 1 :].strip()
                    mycomp = self.modeler.schematic.create_inductor(
                        name, value, [xpos, ypos], use_instance_id_netlist=use_instance
                    )
                elif fields[0][0] == "C":
                    value = fields[3][fields[3].find("=") + 1 :].strip()
                    mycomp = self.modeler.schematic.create_capacitor(
                        name, value, [xpos, ypos], use_instance_id_netlist=use_instance
                    )
                elif fields[0][0] == "Q":
                    if len(fields) == 4 and fields[0][0] == "Q":
                        value = fields[3].strip()
                        mycomp = self.modeler.schematic.create_npn(
                            fields[0], value, [xpos, ypos], use_instance_id_netlist=use_instance
                        )
                        value = None
                elif fields[0][0] == "D":
                    value = fields[3][fields[3].find("=") + 1 :].strip()
                    mycomp = self.modeler.schematic.create_diode(
                        name, [xpos, ypos], use_instance_id_netlist=use_instance
                    )
                if mycomp:
                    id = 1
                    for pin in mycomp.pins:
                        if pin.name == "CH" or pin.name == fields[0][0]:
                            continue
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
        return True

    @pyaedt_function_handler()
    def set_end_time(self, expression):
        """Set the end time.

        Parameters
        ----------
        expression :


        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        References
        ----------

        >>> oDesign.ChangeProperty
        """
        self.set_sim_setup_parameter("Tend", expression)
        return True

    @pyaedt_function_handler()
    def set_hmin(self, expression):
        """Set hmin.

        Parameters
        ----------
        expression :


        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        References
        ----------

        >>> oDesign.ChangeProperty
        """
        self.set_sim_setup_parameter("Hmin", expression)
        return True

    @pyaedt_function_handler()
    def set_hmax(self, expression):
        """Set hmax.

        Parameters
        ----------
        expression :


        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        References
        ----------

        >>> oDesign.ChangeProperty
        """
        self.set_sim_setup_parameter("Hmax", expression)
        return True

    @pyaedt_function_handler(var_str="variable")
    def set_sim_setup_parameter(self, variable, expression, analysis_name="TR"):
        """Set simulation setup parameters.

        Parameters
        ----------
        variable : string
            Name of the variable.
        expression :

        analysis_name : str, optional
            Name of the analysis. The default is ``"TR"``.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        References
        ----------

        >>> oDesign.ChangeProperty
        """
        if isinstance(expression, Variable):
            value_str = expression.evaluated_value
        # Handle input type int/float, etc (including numeric 0)
        elif is_number(expression):
            value_str = str(expression)
        else:
            value_str = expression

        self._odesign.ChangeProperty(
            [
                "NAME:AllTabs",
                [
                    "NAME:BaseElementTab",
                    ["NAME:PropServers", analysis_name],
                    ["NAME:ChangedProps", ["NAME:" + variable, "Value:=", value_str]],
                ],
            ]
        )
        return True

    @pyaedt_function_handler(setup_name="setup", sweep_name="sweep")
    def add_q3d_dynamic_component(
        self,
        source_project,
        source_design_name,
        setup,
        sweep,
        coupling_matrix_name,
        model_depth="1meter",
        maximum_order=10000,
        error_tolerance=0.005,
        z_ref=50,
        state_space_dynamic_link_type=None,
        component_name=None,
        save_project=True,
    ):
        """Add a Q2D or Q3D dynamic component to a Twin Builder design.

        Parameters
        ----------
        source_project : str
            Source project name or project path.
        source_design_name : str
            Source design name.
        setup : str
            Setup name.
        sweep : str
            Sweep name.
        coupling_matrix_name : str
            Coupling matrix name.
        model_depth : str, optional
            2D model depth specified as value with unit.
            To be provided if design is Q2D.
            The default value is ``1meter``
        maximum_order : float, optional
            The Maximum Order value specifies the highest order state space
            system that you can choose while fitting to represent the system behavior.
            A lower order may lead to less accuracy but faster simulation.
            The default value is ``10000``.
        error_tolerance : float, optional
            Error Tolerance sets the error tolerance for S-Matrix fitting.
            The default value is ``0.005``.
        z_ref : float, optional
            Sets the value of the Z (ref) in ohms.
            The default value is ``50``.
        state_space_dynamic_link_type : str, optional
            Q3D state space dynamic link type.
            Possible options are:
                - ``S`` for S parameters link type.
                - ``RLGC`` for RLGC Parameters link type.
                - ``EQ`` for Equivalent Circuit.
            The default value is ``RLGC``.
        component_name : str, optional
            Component name.
            If not provided a generic name with prefix "SimpQ3DData" will be given.
        save_project : bool, optional
            Save project after use.
            The default value is ``True``.

        Returns
        -------
        :class:`pyaedt.modeler.cad.object3dcircuit.CircuitComponent` or bool
            Circuit component object if successful or ``False`` if fails.

        References
        ----------

        >>> oComponentManager.AddDynamicNPortData

        Examples
        --------

        Create an instance of Twin Builder.

        >>> from pyaedt import TwinBuilder
        >>> tb = TwinBuilder()

        Add a Q2D dynamic link component.

        >>> tb.add_q3d_dynamic_component("Q2D_ArmouredCableExample", "2D_Extractor_Cable", "MySetupAuto", "sweep1",
        ...                              "Original","100mm")
        >>> tb.release_desktop()
        """
        dkp = self.desktop_class
        is_loaded = False
        if os.path.isfile(source_project):
            project_path = source_project
            project_name = os.path.splitext(os.path.basename(source_project))[0]
            if project_name in dkp.project_list():
                app = dkp[[project_name, source_design_name]]
            else:
                app = dkp.load_project(project_path, source_design_name)
                is_loaded = True
        elif source_project in self.project_list:
            project_name = source_project
            project_path = os.path.join(self.project_path, project_name + ".aedt")
            app = dkp[[source_project, source_design_name]]
        else:
            raise ValueError("Invalid project name or path provided.")
        if app is None:  # pragma: no cover
            raise ValueError("Invalid project or design name.")
        setup_name = setup
        setup = [s for s in app.setups if s.name == setup_name]
        if not setup:
            raise ValueError("Invalid setup in selected design.")
        else:
            sweeps = [s for s in app.get_sweeps(setup_name) if s == sweep]
            if sweeps:  # pragma: no cover
                coupling_solution_name = "{} : {}".format(setup_name, sweep)
            else:  # pragma: no cover
                raise ValueError("Invalid sweep name.")
        if not [m for m in app.matrices if m.name == coupling_matrix_name]:
            raise ValueError("Invalid matrix name.")
        if not component_name:
            component_name = generate_unique_name("SimpQ3DData")
        var = app.available_variations.nominal_w_values_dict
        props = ["NAME:Properties"]
        for k, v in var.items():
            props.append("paramProp:=")
            props.append([k, v])
        port_info_list_A = []
        port_info_list_B = []
        # check design_type if Q2D
        if app.design_type == "2D Extractor":
            props.append("paramProp:=")
            props.append(["COMPONENT_DEPTH", model_depth])
            is_3d = False
            is_depth_needed = True
            value, unit = decompose_variable_value(model_depth)
            if not is_number(value) and not unit:
                raise TypeError("Model depth must be provided as a string with value and unit.")
            design_type = "Q2D"
            signal_list = [k for k, v in app.excitation_objects.items() if v.type == "SignalLine"]
            for signal in signal_list:
                port_info_list_A.append("OnePortInfo:=")
                port_info_list_B.append("OnePortInfo:=")
                list_A = [signal + "_" + signal + "_A", -1, signal + ":" + signal + "_A"]
                list_B = [signal + "_" + signal + "_B", -1, signal + ":" + signal + "_B"]
                port_info_list_A.append(list_A)
                port_info_list_B.append(list_B)
        else:
            is_3d = True
            design_type = "Q3D"
            is_depth_needed = False
            for net in app.nets:
                sources = app.net_sources(net)
                sinks = app.net_sinks(net)
                if sources:
                    for source in sources:
                        port_info_list_A.append("OnePortInfo:=")
                        port_info_list_A.append([net + "_" + source, -1, net + ":" + source])
                else:
                    port_info_list_A.append("OnePortInfo:=")
                    port_info_list_A.append([net + "_", -1, net + ":"])
                if sinks:
                    for sink in sinks:
                        port_info_list_B.append("OnePortInfo:=")
                        port_info_list_B.append([net + "_" + sink, -1, net + ":" + sink])
                else:
                    port_info_list_B.append("OnePortInfo:=")
                    port_info_list_B.append([net + "_", -1, net + ":"])
        if port_info_list_A and port_info_list_B:
            port_info_list = ["NAME:PortInfo"]
            port_info_list.extend(port_info_list_A)
            port_info_list.extend(port_info_list_B)
        if not state_space_dynamic_link_type or state_space_dynamic_link_type == "RLGC":
            if dkp.aedt_version_id >= "2024.1":
                state_space_dynamic_link_type = "Q3DRLGCLink"
            else:  # pragma: no cover
                state_space_dynamic_link_type = "{}RLGCTBLink".format(design_type)
            q3d_model_type = 1
            ref_pin_style = 5
            enforce_passivity = False
            maximum_order = ""
        elif state_space_dynamic_link_type == "S":
            state_space_dynamic_link_type = "{}SParamLink".format(design_type)
            q3d_model_type = 1
            ref_pin_style = 3
            enforce_passivity = True
        elif state_space_dynamic_link_type == "EQ":
            state_space_dynamic_link_type = "{}SmlLink".format(design_type)
            q3d_model_type = 0
            ref_pin_style = 3
            enforce_passivity = True
        else:
            raise TypeError("Link type is not valid.")
        self.o_component_manager.AddDynamicNPortData(
            [
                "NAME:ComponentData",
                "ComponentDataType:=",
                "SimpQ3DData",
                "name:=",
                component_name,
                "filename:=",
                project_path,
                "numberofports:=",
                2 * len(app.excitations),
                "Is3D:=",
                is_3d,
                "IsWBLink:=",
                False,
                "WBSystemId:=",
                "",
                "CouplingDesignName:=",
                source_design_name,
                "CouplingSolutionName:=",
                coupling_solution_name,
                "CouplingMatrixName:=",
                coupling_matrix_name,
                "SaveProject:=",
                save_project,
                "CloseProject:=",
                False,
                "StaticLink:=",
                False,
                "CouplingType:=",
                state_space_dynamic_link_type,
                "VariationKey:=",
                "",
                "NewToOldMap:=",
                [],
                "OldToNewMap:=",
                [],
                "ModelText:=",
                "",
                "SolvedVariationKey:=",
                "",
                "EnforcePassivity:=",
                enforce_passivity,
                "MaxNumPoles:=",
                str(maximum_order),
                "ErrTol:=",
                str(error_tolerance),
                "SSZref:=",
                "{}ohm".format(z_ref),
                "IsDepthNeeded:=",
                is_depth_needed,
                "Mw2DDepth:=",
                model_depth,
                "IsScaleNeeded:=",
                False,
                "MwScale:=",
                "1",
                "RefPinStyle:=",
                ref_pin_style,
                "Q3DModelType:=",
                q3d_model_type,
                "SaveDataSSOptions:=",
                "",
                props,
                port_info_list,
            ]
        )

        component = self.modeler.schematic.create_component(component_library="", component_name=component_name)
        if component:
            if is_loaded:
                app.close_project(save=False)
            return component
        else:  # pragma: no cover
            raise ValueError("Error in creating the component.")
