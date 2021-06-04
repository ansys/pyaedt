# -*- coding: utf-8 -*-
"""
Circuit Class
-------------
This class contains the link to Circuit object. It includes all
inherited classes and modules needed to create and edit circuit designs.

"""
from __future__ import absolute_import
import math
from .application.AnalysisNexxim import FieldAnalysisCircuit
from .desktop import exception_to_desktop
from .generic.general_methods import generate_unique_name, aedt_exception_handler
import re

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
    """Convert a RKM code string to a string with decimal point.

    Parameters
    ----------
    code : str
        RKM code string.

    Returns
    -------
    str
        String with decimal point and R value.

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

    # matches rkm codes that start with a digit
    # fd_pattern = r'([0-9]+)([LREkKMGTFmuµUnNpP]+)([0-9]*)'
    fd_pattern = r'([0-9]+)([{}]+)([0-9]*)'.format(''.join(RKM_MAPS.keys()),)
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
    """Circuit Object

    Parameters
    ----------
    projectname : str, optional
        Name of the project to be selected or full path to the project
        to be opened or to the AEDTZ archive. If ``None``, try to get
        active project and, if nothing present to create an empty one.
    designname : str, optional
        Name of the design to be selected. if ``None``, try to get
        active design and, if nothing present to create an empty one.
    solution_type : str, optional
        Solution type to be applied to design. If ``None``, the default is used.
    setup_name : str, optional
        Setup_name to be used as nominal. If ``None`` active setup is
        used or nothing.

    """

    def __init__(self, projectname=None, designname=None, solution_type=None, setup_name=None):
        FieldAnalysisCircuit.__init__(self, "Circuit Design", projectname, designname, solution_type, setup_name)

    def __enter__(self):
        return self

    def __exit__(self, ex_type, ex_value, ex_traceback):
        if ex_type:
            exception_to_desktop(self, ex_value, ex_traceback)

    @aedt_exception_handler
    def _get_number_from_string(self, stringval):
        value = stringval[stringval.find("=") + 1:].strip().replace("{", "").replace("}", "").replace(",",".")
        return from_rkm_to_aedt(value)


    @aedt_exception_handler
    def create_schematic_from_netlist(self, file_to_import):
        """Create a Circuit Schematic from a spice netlist.

        Supported in this moment:
        -R, L, C, Diodes, Bjts
        -Discrete components with syntax Uxxx net1 net2 ... netn modname

        Parameters
        ----------
        file_to_import : str
            full path to spice file

        Returns
        -------
        bool
            True if completed
        """
        xpos = 0
        ypos = 0
        delta = 0.0508
        use_instance = True
        model =[]
        self._desktop.CloseAllWindows()
        autosave=False
        if self._desktop.GetAutoSaveEnabled() == 1:
            self._desktop.EnableAutoSave(False)
            autosave=True
        with open(file_to_import, 'rb') as f:
            for line in f:
                line=line.decode('utf-8')
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
            xpos +=0.0254
        counter =  0
        with open(file_to_import, 'rb') as f:
            for line in f:
                line=line.decode('utf-8')
                mycomp = None
                fields = line.split(" ")
                name = fields[0].replace(".","")

                if fields[0][0] == "R":
                    if  "{" in fields[3][0]:
                        value =  fields[3].strip()[1:-1]
                    elif '/' in fields[3] and '"' not in fields[3][0] and "'" not in fields[3][0] and "{" not in fields[3][0]:
                        value = self._get_number_from_string(fields[3].split('/')[0])
                    else:
                        value = self._get_number_from_string(fields[3])
                    mycomp, mycompname = self.modeler.components.create_resistor(name, value, xpos, ypos,
                                                                                 use_instance_id_netlist=use_instance)
                elif fields[0][0] == "L":
                    if len(fields)>4 and  "=" not in fields[4]:
                        try:
                            float(fields[4])
                        except:
                            self._messenger.add_warning_message("Component {} Not Imported. Check it and manually import".format(name))
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
                    if  "{" in fields[3][0]:
                        value =  fields[3].strip()[1:-1]
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
                        already_exist=False
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
                        value = line[line.index("PULSE")+6:line.index(")")-1].split(" ")
                        value = [i.replace("{", "").replace("}","") for i in value]
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
                        value = line[line.index("PULSE")+6:line.index(")")-1].split(" ")
                        value = [i.replace("{", "").replace("}","") for i in value]
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
                    counter+=1
                    if counter>59:
                        self.modeler.oeditor.CreatePage("<Page Title>")
                        counter =0
        if autosave:
            self._desktop.EnableAutoSave(True)
        return True

    @aedt_exception_handler
    def create_schematic_from_mentor_netlist(self, file_to_import):
        """Create a Circuit Schematic from a Mentor netlist.
        Supported in this moment:
        -R, L, C, Diodes, Bjts
        -Discrete components with syntax Uxxx net1 net2 ... netn modname

        Parameters
        ----------
        file_to_import : str
            Full path to spice file.

        Returns
        -------
        bool
            ``True`` if successful.
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
                while not finished and i<len(my_netlist):
                    if my_netlist[i][0] == "Property:":
                        props[n].append(my_netlist[i][1])
                    elif "Pin:" in my_netlist[i]:
                        props[n].append(my_netlist[i])
                    else:
                        finished = True
                    i += 1

        column_number = int(math.sqrt(len(comps)))
        for el in comps:
            name = el[2].strip()   #Remove carriage return
            name = name[1:-1]      #remove quotes
            if len(el) > 3:
                comptype = el[3]
            else:
                comptype = self.retrieve_mentor_comp(el[2])
            value = "required"
            for prop in props[name]:
                if "Value=" in prop:
                    value = prop.split("=")[1].replace(",",".").strip()

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
                        if (name+"-"+str(id)) in net:
                            fullnetname = net[2]
                            netnames = fullnetname.split("/")
                            netname = netnames[len(netnames)-1].replace(",","_").replace("'","").replace("$","").strip()
                    if not netname:
                        prop = props[name]
                        if "Pin:" in prop and id in prop:
                            netname = prop[-1]
                            netname = netname.replace("$", "")

                    if netname:
                        self.modeler.components.create_page_port(netname, pos[0], pos[1], angle)
                    else:
                        print("notFound")
                    id += 1
                ypos += delta
                if ypos > delta * (column_number):
                    xpos += delta
                    ypos = 0

        for el in nets:
            netname = el[2][1:-1]
            netname = netname.replace("$","")
            if "GND" in netname.upper():
                self.modeler.components.create_gnd(xpos, ypos)
                page_pos = ypos+0.00254
                id, name = self.modeler.components.create_page_port(netname, xpos, ypos, 6.28318530717959)
                mod1 = self.modeler.components[id]
                mod1.set_location(str(xpos)+"meter", str(page_pos)+"meter")
                ypos += delta
                if ypos > delta * column_number:
                    xpos += delta
                    ypos = 0

        return True

    @aedt_exception_handler
    def retrieve_mentor_comp(self, refid):
        """Identifies from the reference ID which type of component is (from Mentor Netlist)

        Parameters
        ----------
        refid : str
            Reference ID.

        Returns
        -------
        str
            refid Nexxim Type
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
    def get_source_pin_names(self, source_design_name, source_project_name=None, source_project_path=None, port_selector=3):
        """Port_selector:
        - 1 Wave Port
        - 2 Terminal
        - 3 Circuit Port

        Parameters
        ----------
        source_project_name :str
            source project name
        source_design_name : str
            source design name
        source_project_path : str
            source project path if different than existsting one
        port_selector : int
             1 - Wave Port, 2  - Terminal, 3 - Circuit
             (Default value = 3)

        Returns
        -------
        list
            pin lists
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
    def import_touchsthone_solution(self, filename, solution_name="Imported_Data"):
        """ Import Touchstone file as solution

        Parameters
        ----------
        filename : str
            sNp/ts filename
        solution_name : str
                solution name
        Returns
        -------
        list
            list of ports
        """
        if filename[-2:] == "ts":
            with open(filename, "r") as f:
                lines = f.readlines()
                for i in lines:
                    if "[Number of Ports]" in  i:
                        ports = int(i[i.find("]")+1:])
                portnames = [i.split(" = ")[1].strip() for i in lines if "! Port" in i[:9]]
                if not portnames:
                    portnames = ["Port{}".format(i + 1) for i in range(ports)]
        else:
            re_filename = re.compile(r"\.s(?P<ports>\d+)+p", re.I)
            m = re_filename.search(filename)
            ports = int(m.group('ports'))
            portnames = None
            with open(filename,"r") as f:
                lines = f.readlines()
                portnames = [i.split(" = ")[1].strip() for i in lines if "Port[" in i]
            if not portnames:
                portnames = ["Port{}".format(i+1) for i in range(ports)]
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

    # @aedt_exception_handler
    # def export_fullwave_spice(self, designname=None, setupname=None, is_solution_file=False, filename=None,
    #                           passivity=False, causality=False, renormalize=False, impedance=50, error=0.5,
    #                           poles=10000):
    #     """
    #     This method doesn't work actually
    #     Export Full Wave Spice using NDE
    #
    #     Parameters
    #     ----------
    #     designname : str
    #             name of the design or the solution file full path if it is an imported file
    #     setupname : str
    #             name of setup if is a design
    #     is_solution_file: bool
    #             True if it is an imported solution
    #     filename: str
    #             full path to exported sp file
    #     passivity: bool
    #     causality: bool
    #     renormalize: bool
    #     impedance: float
    #         impedance in case of renormalization
    #     error: float
    #         fitting error
    #     poles: int
    #         fitting poles
    #
    #     Returns
    #     -------
    #     str
    #         filename if the export if successful
    #     """
    #     if not designname:
    #         designname = self.design_name
    #     if not filename:
    #         filename = os.path.join(self.project_path, self.design_name + ".sp")
    #     if is_solution_file:
    #         setupname = designname
    #         designname = ""
    #     else:
    #         if not setupname:
    #             setupname=self.nominal_sweep
    #     self.onetwork_data_explorer.ExportFullWaveSpice(designname, is_solution_file, setupname, "",
    #                                                     ["NAME:Frequencies"],
    #                                                     ["NAME:SpiceData", "SpiceType:=", "HSpice",
    #                                                      "EnforcePassivity:=", passivity, "EnforceCausality:=",
    #                                                      causality,
    #                                                      "UseCommonGround:=", True,
    #                                                      "ShowGammaComments:=", True,
    #                                                      "Renormalize:=", renormalize,
    #                                                      "RenormImpedance:=", impedance,
    #                                                      "FittingError:=", error,
    #                                                      "MaxPoles:=", poles,
    #                                                      "PassivityType:=", "IteratedFittingOfPV",
    #                                                      "ColumnFittingType:=", "Matrix",
    #                                                      "SSFittingType:=", "FastFit",
    #                                                      "RelativeErrorToleranc:=", False,
    #                                                      "EnsureAccurateZfit:=", True,
    #                                                      "TouchstoneFormat:=", "MA",
    #                                                      "TouchstoneUnits:=", "GHz",
    #                                                      "TouchStonePrecision:=", 15,
    #                                                      "SubcircuitName:=", "",
    #                                                      "SYZDataInAutoMode:=", False,
    #                                                      "ExportDirectory:=", os.path.dirname(filename)+"\\",
    #                                                      "ExportSpiceFileName:=", os.path.basename(filename),
    #                                                      "FullwaveSpiceFileName:=", os.path.basename(filename)[:-2]+"sss"])
    #     return filename

    @aedt_exception_handler
    def create_touchstone_report(self,plot_name, curvenames, solution_name=None, variation_dict=None):
        """Create a touchstone plot

        Parameters
        ----------
        plot_name : str
            name of the plot
        curvenames : str
            list of curves to plot
        solution_name : str
            name of solution (Default value = None)
        variation_dict : dict
            name of variations (Default value = None)

        Returns
        -------
        bool
            Boolean

        """
        if not solution_name:
            solution_name = self.nominal_sweep
        variations = ["Freq:=", ["All"]]
        if variation_dict:
            for el in variation_dict:
                variations.append(el +":=")
                variations.append([variation_dict[el]])
        self.post.oreportsetup.CreateReport(plot_name, "Standard", "Rectangular Plot", solution_name,
                             ["NAME:Context", "SimValueContext:=",
                              [3, 0, 2, 0, False, False, -1, 1, 0, 1, 1, "", 0, 0]], variations,
                             ["X Component:=", "Freq", "Y Component:=", curvenames])
        return True
