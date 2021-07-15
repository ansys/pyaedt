# -*- coding: utf-8 -*-
"""This module contains the `Circuit` class."""

from __future__ import absolute_import
import math
from .application.AnalysisNexxim import FieldAnalysisCircuit
from .desktop import exception_to_desktop
from .generic.general_methods import generate_unique_name, aedt_exception_handler
import re
import os

RKM_MAPS = {
    # Resistors
    'L': 'm',
    'R': '',
    'E': '',
    'k': 'k',
    'K': 'k',
    'M': 'M',
    'G': 'G',
    'T': 'T',
    # Capacitors/Inductors
    'F': '',
    'H': '',
    'h': '',
    'm': 'm',
    'u': 'μ',
    'μ': 'μ',
    'U': 'μ',
    'n': 'n',
    'N': 'n',
    'p': 'p',
    'P': 'p',
    'mF': 'm',
    'uF': 'μ',
    'μF': 'μ',
    'UF': 'μ',
    'nF': 'n',
    'NF': 'n',
    'pF': 'p',
    'PF': 'p',
    'mH': 'm',
    'uH': 'μ',
    'μH': 'μ',
    'UH': 'μ',
    'nH': 'n',
    'NH': 'n',
    'pH': 'p',
    'PH': 'p',
}

AEDT_MAPS = {
    'μ': 'u'
}


def from_rkm(code):
    """Convert an RKM code string to a string with a decimal point.

    Parameters
    ----------
    code : str
        RKM code string.

    Returns
    -------
    str
        String with a decimal point and R value.

    Examples
    --------
    >>> from pyaedt.circuit import from_rkm
    >>> from_rkm('R47')
    '0.47'

    >>> from_rkm('4R7')
    '4.7'

    >>> from_rkm('470R')
    '470'

    >>> from_rkm('4K7')
    '4.7k'

    >>> from_rkm('47K')
    '47k'

    >>> from_rkm('47K3')
    '47.3k'

    >>> from_rkm('470K')
    '470k'

    >>> from_rkm('4M7')
    '4.7M'

    """

    # Matches RKM codes that start with a digit.
    # fd_pattern = r'([0-9]+)([LREkKMGTFmuµUnNpP]+)([0-9]*)'
    fd_pattern = r'([0-9]+)([{}]+)([0-9]*)'.format(''.join(RKM_MAPS.keys()), )
    # matches rkm codes that end with a digit
    # ld_pattern = r'([0-9]*)([LREkKMGTFmuµUnNpP]+)([0-9]+)'
    ld_pattern = r'([0-9]*)([{}]+)([0-9]+)'.format(''.join(RKM_MAPS.keys()))

    fd_regex = re.compile(fd_pattern, re.I)
    ld_regex = re.compile(ld_pattern, re.I)

    for regex in [fd_regex, ld_regex]:
        m = regex.match(code)
        if m:
            fd, base, ld = m.groups()
            ps = RKM_MAPS[base]

            if ld:
                return_str = ''.join([fd, '.', ld, ps])
            else:
                return_str = ''.join([fd, ps])
            return return_str
    return code


def to_aedt(code):
    """

    Parameters
    ----------
    code : str
        

    Returns
    -------
    str
    """
    pattern = r'([{}]{})'.format(''.join(AEDT_MAPS.keys()), '{1}')
    regex = re.compile(pattern, re.I)
    return_code = regex.sub(lambda m: AEDT_MAPS.get(m.group(), m.group()), code)
    return return_code


def from_rkm_to_aedt(code):
    """

    Parameters
    ----------
    code : str
        

    Returns
    -------
    str
    """
    return to_aedt(from_rkm(code))


class Circuit(FieldAnalysisCircuit, object):
    """Circuit application interface.

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
        ``None``, which applies the default type.
    setup_name : str, optional
        Name of the setup to use as the nominal. The default is
        ``None``, in which case the active setup is used or
        nothing is used.
    specified_version: str, optional
        Version of AEDT to use. The default is ``None``, in which case
        the active version or latest installed version is  used.
    NG : bool, optional
        Whether to run AEDT in the non-graphical mode. The default
        is``False``, which launches AEDT in the graphical mode.
    AlwaysNew : bool, optional
        Whether to launch an instance of AEDT in a new thread, even if
        another instance of the ``specified_version`` is active on the
        machine.  The default is ``True``.
    release_on_exit : bool, optional
        Whether to release AEDT on exit.
    student_version : bool, optional
        Whether open AEDT Student Version. The default is ``False``.

    Examples
    --------
    Create an instance of `Circuit` and connect to an existing HFSS
    design or create a new HFSS design if one does not exist.

    >>> from pyaedt import Circuit
    >>> aedtapp = Circuit()

    Create an instance of `Circuit` and link to a project named
    ``projectname``. If this project does not exist, create one with
    this name.

    >>> aedtapp = Circuit(projectname)

    Create an instance of `Circuit` and link to a design named
    ``designname`` in a project named ``projectname``.

    >>> aedtapp = Circuit(projectname,designame)

    Create an instance of `Circuit` and open the specified project,
    which is ``myfie.aedt``.

    >>> aedtapp = Circuit("myfile.aedt")

    Create an instance of `Circuit` using the 2021 R1 version and
    open the specified project, which is ``myfie.aedt``.

    >>> aedtapp = Circuit(specified_version="2021.1", projectname="myfile.aedt")

    Create an instance of ``Circuit`` using the 2021 R2 student version and open
    the specified project, which is named ``"myfile.aedt"``.

    >>> hfss = Circuit(specified_version="2021.2", projectname="myfile.aedt", student_version=True)

    Examples
    --------
    Create an instance of ``Circuit`` and connect to an existing HFSS
    design or create a new HFSS design if one does not exist.

    >>> from pyaedt import Circuit
    >>> aedtapp = Circuit()

    Create an instance of ``Circuit`` and link to a project named
    ``projectname``. If this project does not exist, create one with
    this name.

    >>> aedtapp = Circuit(projectname)

    Create an instance of ``Circuit`` and link to a design named
    ``designname`` in a project named ``projectname``.

    >>> aedtapp = Circuit(projectname,designame)

    Create an instance of ``Circuit`` and open the specified project,
    which is ``myfie.aedt``.

    >>> aedtapp = Circuit("myfile.aedt")

    Create an instance of ``Circuit`` using the 2021 R1 version and
    open the specified project, which is ``myfie.aedt``.

    >>> aedtapp = Circuit(specified_version="2021.1", projectname="myfile.aedt")

    """

    def __init__(self, projectname=None, designname=None, solution_type=None, setup_name=None,
                 specified_version=None, NG=False, AlwaysNew=False, release_on_exit=False, student_version=False):
        FieldAnalysisCircuit.__init__(self, "Circuit Design", projectname, designname, solution_type, setup_name,
                                      specified_version, NG, AlwaysNew, release_on_exit, student_version)

    def __enter__(self):
        return self

    def __exit__(self, ex_type, ex_value, ex_traceback):
        if ex_type:
            exception_to_desktop(self, ex_value, ex_traceback)

    @property
    def onetwork_data_explorer(self):
        return self._desktop.GetTool("NdExplorer")

    @aedt_exception_handler
    def _get_number_from_string(self, stringval):
        value = stringval[stringval.find("=") + 1:].strip().replace("{", "").replace("}", "").replace(",", ".")
        try:
            float(value)
            return value
        except:
            return from_rkm_to_aedt(value)

    @aedt_exception_handler
    def create_schematic_from_netlist(self, file_to_import):
        """Create a circuit schematic from an HSpice netlist.

        Supported currently:
        
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
        with open(file_to_import, 'rb') as f:
            for line in f:
                line = line.decode('utf-8')
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
            self.modeler.components.create_symbol("Models_Netlist", [])
            self.modeler.components.create_new_component_from_symbol("Models_Netlist", [], "")
            self.modeler.components.create_component(None, component_library=None, component_name="Models_Netlist",
                                                     xpos=xpos, ypos=0, global_netlist_list=model)
            self.modeler.components.disable_data_netlist(component_name="Models_Netlist")
            xpos += 0.0254
        counter = 0
        with open(file_to_import, 'rb') as f:
            for line in f:
                line = line.decode('utf-8')
                mycomp = None
                fields = line.split(" ")
                name = fields[0].replace(".", "")

                if fields[0][0] == "R":
                    if "{" in fields[3][0]:
                        value = fields[3].strip()[1:-1]
                    elif '/' in fields[3] and '"' not in fields[3][0] and "'" not in fields[3][0] and "{" not in \
                            fields[3][0]:
                        value = self._get_number_from_string(fields[3].split('/')[0])
                    else:
                        value = self._get_number_from_string(fields[3])
                    mycomp, mycompname = self.modeler.components.create_resistor(name, value, xpos, ypos,
                                                                                 use_instance_id_netlist=use_instance)
                elif fields[0][0] == "L":
                    if len(fields) > 4 and "=" not in fields[4]:
                        try:
                            float(fields[4])
                        except:
                            self._messenger.add_warning_message(
                                "Component {} Not Imported. Check it and manually import".format(name))
                            continue
                    if "{" in fields[3][0]:
                        value = fields[3].strip()[1:-1]
                    elif '/' in fields[3] and '"' not in fields[3][0] and "'" not in fields[3][0]:
                        value = self._get_number_from_string(fields[3].split('/')[0])
                    else:
                        value = self._get_number_from_string(fields[3])
                    mycomp, mycompname = self.modeler.components.create_inductor(name, value, xpos, ypos,
                                                                                 use_instance_id_netlist=use_instance)
                elif fields[0][0] == "C":
                    if "{" in fields[3][0]:
                        value = fields[3].strip()[1:-1]
                    elif '/' in fields[3] and '"' not in fields[3][0] and "'" not in fields[3][0]:
                        value = self._get_number_from_string(fields[3].split('/')[0])
                    else:
                        value = self._get_number_from_string(fields[3])
                    mycomp, mycompname = self.modeler.components.create_capacitor(name, value, xpos, ypos,
                                                                                  use_instance_id_netlist=use_instance)
                elif fields[0][0] == "Q" or fields[0][0] == "U":
                    if len(fields) == 4 and fields[0][0] == "Q":
                        value = fields[3].strip()
                        mycomp, mycompname = self.modeler.components.create_npn(fields[0], value, xpos, ypos,
                                                                                use_instance_id_netlist=use_instance)
                    else:
                        numpins = len(fields) - 2
                        i = 1
                        pins = []
                        while i <= numpins:
                            pins.append("Pin" + str(i))
                            i += 1
                        parameter = fields[len(fields) - 1][:-1].strip()
                        if "=" in parameter:
                            parameter_list = [parameter[:parameter.find("=") - 1]]
                            parameter_value = [parameter[parameter.find("=") + 1:]]
                        else:
                            parameter_list = ["MOD"]
                            parameter_value = [parameter]
                        self.modeler.components.create_symbol(parameter, pins)
                        already_exist = False
                        for el in self.modeler.components.components:
                            if self.modeler.components.components[el].name == parameter:
                                already_exist = True
                        if not already_exist:
                            self.modeler.components.create_new_component_from_symbol(parameter, pins, fields[0][0],
                                                                                     parameter_list, parameter_value)
                        mycomp, mycompname = self.modeler.components.create_component(fields[0], component_library=None,
                                                                                      component_name=parameter,
                                                                                      xpos=xpos, ypos=ypos,
                                                                                      use_instance_id_netlist=use_instance)
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
                        parameter_list = [parameter[:parameter.find("=") - 1]]
                        parameter_value = [parameter[parameter.find("=") + 1:]]
                    else:
                        parameter_list = ["MOD"]
                        parameter_value = [parameter]
                    self.modeler.components.create_symbol(parameter, pins)
                    already_exist = False
                    for el in self.modeler.components.components:
                        if self.modeler.components.components[el].name == parameter:
                            already_exist = True
                    if not already_exist:
                        self.modeler.components.create_new_component_from_symbol(parameter, pins, fields[0][0],
                                                                                 parameter_list, parameter_value)
                    mycomp, mycompname = self.modeler.components.create_component(fields[0], component_library=None,
                                                                                  component_name=parameter,
                                                                                  xpos=xpos, ypos=ypos,
                                                                                  use_instance_id_netlist=use_instance)
                    value = None
                elif fields[0][0] == "D":
                    value = self._get_number_from_string(fields[3])
                    mycomp, mycompname = self.modeler.components.create_diode(name, value, xpos, ypos,
                                                                              use_instance_id_netlist=use_instance)
                elif fields[0][0] == "V":
                    if "PULSE" not in line:
                        value = self._get_number_from_string(fields[3])
                        mycomp, mycompname = self.modeler.components.create_voltage_dc(name, value, xpos, ypos,
                                                                                       use_instance_id_netlist=use_instance)
                    else:
                        value = line[line.index("PULSE") + 6:line.index(")") - 1].split(" ")
                        value = [i.replace("{", "").replace("}", "") for i in value]
                        fields[1], fields[2] = fields[2], fields[1]
                        mycomp, mycompname = self.modeler.components.create_voltage_pulse(name, value, xpos, ypos,
                                                                                          use_instance_id_netlist=use_instance)
                elif fields[0][0] == "K":
                    value = self._get_number_from_string(fields[3])
                    mycomp, mycompname = self.modeler.components.create_coupling_inductors(name, fields[1], fields[2],
                                                                                           value, xpos, ypos,
                                                                                           use_instance_id_netlist=use_instance)
                elif fields[0][0] == "I":
                    if "PULSE" not in line:
                        value = self._get_number_from_string(fields[3])
                        mycomp, mycompname = self.modeler.components.create_current_dc(name, value, xpos, ypos,
                                                                                       use_instance_id_netlist=use_instance)
                    else:
                        value = line[line.index("PULSE") + 6:line.index(")") - 1].split(" ")
                        value = [i.replace("{", "").replace("}", "") for i in value]
                        mycomp, mycompname = self.modeler.components.create_current_pulse(name, value, xpos, ypos,
                                                                                          use_instance_id_netlist=use_instance)
                if mycomp:
                    pins = self.modeler.components.get_pins(mycomp)
                    id = 1
                    for pin in pins:
                        pos = self.modeler.components.get_pin_location(mycomp, pin)
                        if pos[0] < xpos:
                            angle = 6.28318530717959
                        else:
                            angle = 3.14159265358979
                        self.modeler.components.create_page_port(fields[id], pos[0], pos[1], angle)
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
        return True

    @aedt_exception_handler
    def create_schematic_from_mentor_netlist(self, file_to_import):
        """Create a circuit schematic from a Mentor net list.
        
        Supported currently:
        
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
        my_netlist = []
        with open(file_to_import, 'r') as f:
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
                mycomp, mycompname = self.modeler.components.create_resistor(name, value, xpos, ypos,
                                                                             use_instance_id_netlist=use_instance)
            elif "inductor:COIL." in comptype:
                mycomp, mycompname = self.modeler.components.create_inductor(name, value, xpos, ypos,
                                                                             use_instance_id_netlist=use_instance)
            elif "capacitor:CAP." in comptype:
                mycomp, mycompname = self.modeler.components.create_capacitor(name, value, xpos, ypos,
                                                                              use_instance_id_netlist=use_instance)
            elif "transistor:NPN" in comptype:
                mycomp, mycompname = self.modeler.components.create_npn(name, value, xpos, ypos,
                                                                        use_instance_id_netlist=use_instance)
            elif "transistor:PNP" in comptype:
                mycomp, mycompname = self.modeler.components.create_pnp(name, value, xpos, ypos,
                                                                        use_instance_id_netlist=use_instance)
            elif "diode:" in comptype:
                mycomp, mycompname = self.modeler.components.create_diode(name, value, xpos, ypos,
                                                                          use_instance_id_netlist=use_instance)

            if mycomp:
                pins = self.modeler.components.get_pins(mycomp)
                id = 1
                for pin in pins:
                    pos = self.modeler.components.get_pin_location(mycomp, pin)
                    if pos[0] < xpos:
                        angle = 6.28318530717959
                    else:
                        angle = 3.14159265358979
                    netname = None
                    for net in nets:
                        net = [i.strip() for i in net]
                        if (name + "-" + str(id)) in net:
                            fullnetname = net[2]
                            netnames = fullnetname.split("/")
                            netname = netnames[len(netnames) - 1].replace(",", "_").replace("'", "").replace("$",
                                                                                                             "").strip()
                    if not netname:
                        prop = props[name]
                        if "Pin:" in prop and id in prop:
                            netname = prop[-1]
                            netname = netname.replace("$", "")

                    if netname:
                        self.modeler.components.create_page_port(netname, pos[0], pos[1], angle)
                    else:
                        self._messenger.add_info_message("Page Port Not Created", "Global")
                    id += 1
                ypos += delta
                if ypos > delta * (column_number):
                    xpos += delta
                    ypos = 0

        for el in nets:
            netname = el[2][1:-1]
            netname = netname.replace("$", "")
            if "GND" in netname.upper():
                self.modeler.components.create_gnd(xpos, ypos)
                page_pos = ypos + 0.00254
                id, name = self.modeler.components.create_page_port(netname, xpos, ypos, 6.28318530717959)
                mod1 = self.modeler.components[id]
                mod1.set_location(str(xpos) + "meter", str(page_pos) + "meter")
                ypos += delta
                if ypos > delta * column_number:
                    xpos += delta
                    ypos = 0

        return True

    @aedt_exception_handler
    def retrieve_mentor_comp(self, refid):
        """Retrieve the type of the Mentor net list component for a given reference ID.

        Parameters
        ----------
        refid : str
            Reference ID.

        Returns
        -------
        str
            Type of Mentor net list comoponet.
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
    def get_source_pin_names(self, source_design_name, source_project_name=None, source_project_path=None,
                             port_selector=3):
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
             Type of the port. Options are ``1``, ``2``, or ``3``, corresponding respectively to ``"Wave Port"``, ``"Terminal"``, or ``"Circuit Port"``.
             The default is ``3``, which is a circuit port.

        Returns
        -------
        list
            List of pin names.
        """

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
        """
        if filename[-2:] == "ts":
            with open(filename, "r") as f:
                lines = f.readlines()
                for i in lines:
                    if "[Number of Ports]" in i:
                        ports = int(i[i.find("]") + 1:])
                portnames = [i.split(" = ")[1].strip() for i in lines if "! Port" in i[:9]]
                if not portnames:
                    portnames = ["Port{}".format(i + 1) for i in range(ports)]
        else:
            re_filename = re.compile(r"\.s(?P<ports>\d+)+p", re.I)
            m = re_filename.search(filename)
            ports = int(m.group('ports'))
            portnames = None
            with open(filename, "r") as f:
                lines = f.readlines()
                portnames = [i.split(" = ")[1].strip() for i in lines if "Port[" in i]
            if not portnames:
                portnames = ["Port{}".format(i + 1) for i in range(ports)]
        arg = ["NAME:NPortData", "Description:=", "", "ImageFile:=", "",
               "SymbolPinConfiguration:=", 0, ["NAME:PortInfoBlk"], ["NAME:PortOrderBlk"],
               "filename:=", filename, "numberofports:=", ports, "sssfilename:=", "",
               "sssmodel:=", False, "PortNames:=", portnames,
               "domain:=", "frequency", "datamode:=", "Link", "devicename:=", "",
               "SolutionName:=", solution_name, "displayformat:=", "MagnitudePhase", "datatype:=", "SMatrix",
               ["NAME:DesignerCustomization",
                "DCOption:=", 0, "InterpOption:=", 0, "ExtrapOption:=", 1,
                "Convolution:=", 0, "Passivity:=", 0, "Reciprocal:=", False,
                "ModelOption:=", "", "DataType:=", 1],
               ["NAME:NexximCustomization", "DCOption:=", 3, "InterpOption:=", 1,
                "ExtrapOption:=", 3, "Convolution:=", 0, "Passivity:=", 0,
                "Reciprocal:=", False, "ModelOption:=", "", "DataType:=", 2],
               ["NAME:HSpiceCustomization", "DCOption:=", 1, "InterpOption:=", 2,
                "ExtrapOption:=", 3, "Convolution:=", 0, "Passivity:=", 0,
                "Reciprocal:=", False, "ModelOption:=", "", "DataType:=", 3],
               "NoiseModelOption:=", "External"]
        self.odesign.ImportData(arg, "", True)
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
             Full path to the output file. The default is ``None``.
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
        """

        # Normalize the save path
        if not filename:
            appendix = ""
            for v, vv in zip(variation, variations_value):
                appendix += "_" + v + vv.replace("\'", "")
            ext = ".S" + str(self.oboundary.GetNumExcitations()) + "p"
            filename = os.path.join(self.project_path, solutionname + "_" + sweepname + appendix + ext)
        else:
            filename = filename.replace("//", "/").replace("\\", "/")
        print("Exporting Touchstone " + filename)
        DesignVariations = ""
        i = 0
        for el in variation:
            DesignVariations += str(variation[i]) + "=\'" + str(variations_value[i].replace("\'", "")) + "\' "
            i += 1
            # DesignVariations = "$AmbientTemp=\'22cel\' $PowerIn=\'100\'"
        # array containing "SetupName:SolutionName" pairs (note that setup and solution are separated by a colon)
        SolutionSelectionArray = [solutionname + ":" + sweepname]
        # 2=tab delimited spreadsheet (.tab), 3= touchstone (.sNp), 4= CitiFile (.cit),
        # 7=Matlab (.m), 8=Terminal Z0 spreadsheet
        FileFormat = 3
        OutFile = filename  # full path of output file
        FreqsArray = ["all"]  # array containin the frequencies to export, use ["all"] for all frequencies
        DoRenorm = True  # perform renormalization before export
        RenormImped = 50  # Real impedance value in ohm, for renormalization
        DataType = "S"  # Type: "S", "Y", or "Z" matrix to export
        Pass = -1  # The pass to export. -1 = export all passes.
        ComplexFormat = 0  # 0=Magnitude/Phase, 1=Real/Immaginary, 2=dB/Phase
        DigitsPrecision = 15  # Touchstone number of digits precision
        IncludeGammaImpedance = True  # Include Gamma and Impedance in comments
        NonStandardExtensions = False  # Support for non-standard Touchstone extensions

        self.odesign.ExportNetworkData(DesignVariations, SolutionSelectionArray, FileFormat,
                                         OutFile, FreqsArray, DoRenorm, RenormImped, DataType, Pass,
                                         ComplexFormat, DigitsPrecision, False, IncludeGammaImpedance,
                                         NonStandardExtensions)
        return True

    @aedt_exception_handler
    def export_fullwave_spice(self, designname=None, setupname=None, is_solution_file=False, filename=None,
                              passivity=False, causality=False, renormalize=False, impedance=50, error=0.5,
                              poles=10000):
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
        is_solution_file: bool, optional
            Whether it is an imported solution file. The default is ``False``. 
        filename: str, optional
            Full path and name for exporting the HSpice file. The default is ``None``.
        passivity: bool, optional
            Whether to compute the passivity. The default is ``False``.
        causality: bool, optional
            Whether to compute the causality. The default is ``False``.
        renormalize: bool, optional
            Whether to renormalize the S-matrix to a specific port impedance.
            The default is ``False``.
        impedance: float, optional
            Impedance value if ``renormalize=True``. The default is ``50``.
        error: float, optional
            Fitting error. The default is ``0.05``.
        poles: int, optional
            Number of fitting poles. The default is ``10000``.

        Returns
        -------
        str
            File name if the export is successful.
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
        self.onetwork_data_explorer.ExportFullWaveSpice(designname, is_solution_file, setupname, "",
                                                        [],
                                                        ["NAME:SpiceData", "SpiceType:=", "HSpice",
                                                         "EnforcePassivity:=", passivity, "EnforceCausality:=",
                                                         causality,
                                                         "UseCommonGround:=", True,
                                                         "ShowGammaComments:=", True,
                                                         "Renormalize:=", renormalize,
                                                         "RenormImpedance:=", impedance,
                                                         "FittingError:=", error,
                                                         "MaxPoles:=", poles,
                                                         "PassivityType:=", "IteratedFittingOfPV",
                                                         "ColumnFittingType:=", "Matrix",
                                                         "SSFittingType:=", "FastFit",
                                                         "RelativeErrorToleranc:=", False,
                                                         "EnsureAccurateZfit:=", True,
                                                         "TouchstoneFormat:=", "MA",
                                                         "TouchstoneUnits:=", "GHz",
                                                         "TouchStonePrecision:=", 15,
                                                         "SubcircuitName:=", "",
                                                         "SYZDataInAutoMode:=", False,
                                                         "ExportDirectory:=", os.path.dirname(filename) + "\\",
                                                         "ExportSpiceFileName:=", os.path.basename(filename),
                                                         "FullwaveSpiceFileName:=",
                                                         os.path.basename(filename), "UseMultipleCores:=",
                                                         True, "NumberOfCores:=", 20])
        return filename

    @aedt_exception_handler
    def create_touchstone_report(self, plot_name, curvenames, solution_name=None, variation_dict=None):
        """Create a Touchstone plot.

        Parameters
        ----------
        plot_name : str
            Name of the plot.
        curvenames : str
            List of the curves to plot.
        solution_name : str, optional
            Name of the solution. The default value is ``None``.
        variation_dict : dict, optional
            Dictionary of variation names. The default value is ``None``.

        Returns
        -------
        bool
           ``True`` when successful, ``False`` when failed.

        """
        if not solution_name:
            solution_name = self.nominal_sweep
        variations = ["Freq:=", ["All"]]
        if variation_dict:
            for el in variation_dict:
                variations.append(el + ":=")
                variations.append([variation_dict[el]])
        self.post.oreportsetup.CreateReport(plot_name, "Standard", "Rectangular Plot", solution_name,
                                            ["NAME:Context", "SimValueContext:=",
                                             [3, 0, 2, 0, False, False, -1, 1, 0, 1, 1, "", 0, 0]], variations,
                                            ["X Component:=", "Freq", "Y Component:=", curvenames])
        return True
