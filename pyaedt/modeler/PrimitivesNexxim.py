from ..generic.general_methods import aedt_exception_handler
from .PrimitivesCircuit import CircuitComponents


class NexximComponents(CircuitComponents):
    """Class for management of all CircuitComponents for Nexxim"""
    @property
    def design_libray(self):
        return "Nexxim Circuit Elements"

    @property
    def tab_name(self):
        return "PassedParameterTab"

    @aedt_exception_handler
    def __getitem__(self, partname):
        """
        :param partname: if integer try to get the object id. if string, trying to get object Name
        :return: part object details
        """
        if type(partname) is int:
            return self.components[partname]
        for el in self.components:
            if self.components[el].name == partname or self.components[el].composed_name == partname or el == partname:
                return self.components[el]

        return None

    def __init__(self, parent, modeler):
        CircuitComponents.__init__(self, parent, modeler)
        self._parent = parent
        self.modeler = modeler
        self._currentId = 0
        pass

    @aedt_exception_handler
    def create_3dlayout_subcircuit(self, sourcename):
        """Create a new subcircuit

        Parameters
        ----------
        sourcename :
            name of the source design

        Returns
        -------
        type
            el, composed_name if succeeded or False

        """
        self._parent._oproject.CopyDesign(sourcename)
        self.oeditor.PasteDesign(0, ["NAME:Attributes", "Page:=", 1, "X:=", 0, "Y:=", 0, "Angle:=", 0, "Flip:=", False])
        self.refresh_all_ids()
        for el in self.components:
            if sourcename in self.components[el].composed_name:
                return el, self.components[el].composed_name
        return False

    @aedt_exception_handler
    def create_field_model(self, design_name, solution_name, pin_names, model_type="hfss", posx=0, posy=1):
        """Create Field Model

        Parameters
        ----------
        design_name :
            param solution_name:
        pin_names :
            param model_type:
        posx :
            param posy: (Default value = 0)
        solution_name :
            
        model_type :
             (Default value = "hfss")
        posy :
             (Default value = 1)

        Returns
        -------

        """
        id = self.create_unique_id()
        component_name = design_name + "_" + str(id)
        arg = ["NAME: " +component_name ,"Name:="	, component_name,
               "ModTime:="		, 1589868932,
               "Library:="		, "",
               "LibLocation:="		, "Project",
               "ModelType:="		, model_type,
               "Description:="		, "",
               "ImageFile:="		, "",
               "SymbolPinConfiguration:=", 0,
               [
                   "NAME:PortInfoBlk"
               ],
               [
                   "NAME:PortOrderBlk"
               ],
               "DesignName:="		, design_name,
               "SolutionName:="	, solution_name,
               "NewToOldMap:="		, [],
               "OldToNewMap:="		, [],
               "PinNames:="		, pin_names,
               [
                   "NAME:DesignerCustomization",
                   "DCOption:="		, 0,
                   "InterpOption:="	, 0,
                   "ExtrapOption:="	, 1,
                   "Convolution:="		, 0,
                   "Passivity:="		, 0,
                   "Reciprocal:="		, False,
                   "ModelOption:="		, "",
                   "DataType:="		, 1
               ],
               [
                   "NAME:NexximCustomization",
                   "DCOption:="		, 3,
                   "InterpOption:="	, 1,
                   "ExtrapOption:="	, 3,
                   "Convolution:="		, 0,
                   "Passivity:="		, 0,
                   "Reciprocal:="		, False,
                   "ModelOption:="		, "",
                   "DataType:="		, 2
               ],
               [
                   "NAME:HSpiceCustomization",
                   "DCOption:="		, 1,
                   "InterpOption:="	, 2,
                   "ExtrapOption:="	, 3,
                   "Convolution:="		, 0,
                   "Passivity:="		, 0,
                   "Reciprocal:="		, False,
                   "ModelOption:="		, "",
                   "DataType:="		, 3
               ],
               "NoiseModelOption:="	, "External",
               "WB_SystemID:="		, design_name,
               "IsWBModel:="		, False,
               "filename:="		, "",
               "numberofports:="	, len(pin_names),
               "Simulate:="		, False,
               "CloseProject:="	, False,
               "SaveProject:="		, True,
               "InterpY:="		, True,
               "InterpAlg:="		, "auto",
               "IgnoreDepVars:="	, False,
               "Renormalize:="		, False,
               "RenormImpedance:="	, 50
               ]
        self.o_model_manager.Add(arg)
        arg = [
            "NAME:" + component_name,
            "Info:=",
            ["Type:=", 8, "NumTerminals:=", len(pin_names), "DataSource:=", "", "ModifiedOn:=", 1589868933,
             "Manufacturer:=", "",
             "Symbol:=", "", "ModelNames:=", "", "Footprint:=", "", "Description:=", "", "InfoTopic:=", "",
             "InfoHelpFile:=", "", "IconFile:=", "", "Library:=", "", "OriginalLocation:=", "Project",
             "IEEE:=", "", "Author:=", "", "OriginalAuthor:=", "", "CreationDate:=", 1589868933, "ExampleFile:=",
             "", "HiddenComponent:=", 0, "CircuitEnv:=", 0, "GroupID:=", 0],
            "CircuitEnv:="	, 0,
            "Refbase:="		, "S",
            "NumParts:="		, 1,
            "ModSinceLib:="		, False]
        id = 2
        for pn in pin_names:
            arg.append("Terminal:=")
            arg.append([pn ,pn, "A", False, id, 1, "", "Electrical", "0"])
            id += 1
        arg.append(["NAME:Properties", "TextProp:=", ["Owner", "RD", "", model_type.upper()]])
        arg.append("CompExtID:="), arg.append(5)
        arg.append(["NAME:Parameters", "TextProp:="	, ["ModelName" ,"RD", "", "FieldSolver"],
                    "MenuProp:=", ["CoSimulator", "SD", "", "Default", 0],
                    "ButtonProp:=", ["CosimDefinition", "SD", "", "Edit", "Edit", 40501, "ButtonPropClientData:=", []]])
        arg.append(["NAME:CosimDefinitions",
                    ["NAME:CosimDefinition", "CosimulatorType:=", 103, "CosimDefName:=", "Default", "IsDefinition:=",
                     True, "Connect:=", True,
                     "ModelDefinitionName:=", component_name, "ShowRefPin2:=", 2, "LenPropName:=", ""],
                    "DefaultCosim:=", "Default"])

        self.o_component_manager.Add(arg)
        self._parent.odesign.AddCompInstance(component_name)
        self.refresh_all_ids()
        for el in self.components:
            if component_name in self.components[el].composed_name:
                return el, self.components[el].composed_name
        return False

    @aedt_exception_handler
    def create_resistor(self, compname=None, value=50, xpos=0, ypos=0,angle=0, use_instance_id_netlist=False):
        """Create a new Resistor

        Parameters
        ----------
        compname :
            name (Default value = None)
        value :
            value (Default value = 50)
        xpos :
            x pos (Default value = 0)
        ypos :
            y pos (Default value = 0)
        angle :
            angle (Default value = 0)
        use_instance_id_netlist :
            bool (Default value = False)

        Returns
        -------
        type
            id, name

        """
        cmpid, cmpname = self.create_component(compname, xpos=xpos, ypos=ypos, angle=angle, use_instance_id_netlist=use_instance_id_netlist)

        self.components[cmpid].set_property("R", value)
        return cmpid, cmpname

    @aedt_exception_handler
    def create_inductor(self, compname=None,value=50, xpos=0, ypos=0,angle=0, use_instance_id_netlist=False):
        """Create a new Inductor

        Parameters
        ----------
        compname :
            name (Default value = None)
        value :
            value (Default value = 50)
        xpos :
            x pos (Default value = 0)
        ypos :
            y pos (Default value = 0)
        angle :
            angle (Default value = 0)
        use_instance_id_netlist :
            bool (Default value = False)

        Returns
        -------
        type
            id, name

        """
        cmpid, cmpname = self.create_component(compname, component_library="Inductors", component_name="IND_", xpos=xpos, ypos=ypos,
                                         angle=angle, use_instance_id_netlist=use_instance_id_netlist)

        self.components[cmpid].set_property("L", value)

        return cmpid, cmpname

    @aedt_exception_handler
    def create_capacitor(self, compname=None,value=50, xpos=0, ypos=0, angle=0, use_instance_id_netlist=False):
        """Create a new Capacitor

        Parameters
        ----------
        compname :
            name (Default value = None)
        value :
            value (Default value = 50)
        xpos :
            x pos (Default value = 0)
        ypos :
            y pos (Default value = 0)
        angle :
            angle (Default value = 0)
        use_instance_id_netlist :
            bool (Default value = False)

        Returns
        -------
        type
            id, name

        """
        cmpid, cmpname = self.create_component(compname,component_library="Capacitors", component_name="CAP_", xpos=xpos, ypos=ypos,
                                         angle=angle, use_instance_id_netlist=use_instance_id_netlist)

        self.components[cmpid].set_property("C", value)
        return cmpid, cmpname

    @aedt_exception_handler
    def create_voltage_dc(self, compname=None, value=1, xpos=0, ypos=0, angle=0, use_instance_id_netlist=False):
        """Create a new Voltage DC Source

        Parameters
        ----------
        compname :
            name (Default value = None)
        value :
            value (Default value = 1)
        xpos :
            x pos (Default value = 0)
        ypos :
            y pos (Default value = 0)
        angle :
            angle (Default value = 0)
        use_instance_id_netlist :
            bool (Default value = False)

        Returns
        -------
        type
            id, name

        """
        cmpid, cmpname = self.create_component(compname,component_library="Independent Sources", component_name="V_DC", xpos=xpos, ypos=ypos,
                                         angle=angle, use_instance_id_netlist=use_instance_id_netlist)

        self.components[cmpid].set_property("DC", value)
        return cmpid, cmpname

    @aedt_exception_handler
    def create_current_pulse(self, compname=None, value_lists=[], xpos=0, ypos=0, angle=0, use_instance_id_netlist=False):
        """Create a new Current Pulse

        Parameters
        ----------
        compname :
            name (Default value = None)
        value :
            value
        xpos :
            x pos (Default value = 0)
        ypos :
            y pos (Default value = 0)
        angle :
            angle (Default value = 0)
        use_instance_id_netlist :
            bool (Default value = False)
        value_lists :
             (Default value = [])

        Returns
        -------
        type
            id, name

        """
        cmpid, cmpname = self.create_component(compname,component_library="Independent Sources", component_name="I_PULSE", xpos=xpos, ypos=ypos,
                                         angle=angle, use_instance_id_netlist=use_instance_id_netlist)

        if len(value_lists) > 0:
            self.components[cmpid].set_property("I1", value_lists[0])
        if len(value_lists) > 1:
            self.components[cmpid].set_property("I2", value_lists[1])
        if len(value_lists) > 2:
            self.components[cmpid].set_property("TD", value_lists[2])
        if len(value_lists) > 3:
            self.components[cmpid].set_property("TR", value_lists[3])
        if len(value_lists) > 4:
            self.components[cmpid].set_property("TF", value_lists[4])
        if len(value_lists) > 5:
            self.components[cmpid].set_property("PW", value_lists[5])
        if len(value_lists) > 6:
            self.components[cmpid].set_property("PER", value_lists[6])


        return cmpid, cmpname

    @aedt_exception_handler
    def create_voltage_pulse(self, compname=None, value_lists=[], xpos=0, ypos=0, angle=0, use_instance_id_netlist=False):
        """Create a new Voltage Pulse

        Parameters
        ----------
        compname :
            name (Default value = None)
        value :
            value
        xpos :
            x pos (Default value = 0)
        ypos :
            y pos (Default value = 0)
        angle :
            angle (Default value = 0)
        use_instance_id_netlist :
            bool (Default value = False)
        value_lists :
             (Default value = [])

        Returns
        -------
        type
            id, name

        """
        cmpid, cmpname = self.create_component(compname,component_library="Independent Sources", component_name="V_PULSE", xpos=xpos, ypos=ypos,
                                         angle=angle, use_instance_id_netlist=use_instance_id_netlist)

        if len(value_lists) > 0:
            self.components[cmpid].set_property("V1", value_lists[0])
        if len(value_lists) > 1:
            self.components[cmpid].set_property("V2", value_lists[1])
        if len(value_lists) > 2:
            self.components[cmpid].set_property("TD", value_lists[2])
        if len(value_lists) > 3:
            self.components[cmpid].set_property("TR", value_lists[3])
        if len(value_lists) > 4:
            self.components[cmpid].set_property("TF", value_lists[4])
        if len(value_lists) > 5:
            self.components[cmpid].set_property("PW", value_lists[5])
        if len(value_lists) > 6:
            self.components[cmpid].set_property("PER", value_lists[6])


        return cmpid, cmpname


    @aedt_exception_handler
    def create_current_dc(self, compname=None, value=1, xpos=0, ypos=0, angle=0, use_instance_id_netlist=False):
        """Create a new Current DC Source

        Parameters
        ----------
        compname :
            name (Default value = None)
        value :
            value (Default value = 1)
        xpos :
            x pos (Default value = 0)
        ypos :
            y pos (Default value = 0)
        angle :
            angle (Default value = 0)
        use_instance_id_netlist :
            bool (Default value = False)

        Returns
        -------
        type
            id, name

        """
        cmpid, cmpname = self.create_component(compname,component_library="Independent Sources", component_name="I_DC", xpos=xpos, ypos=ypos,
                                         angle=angle, use_instance_id_netlist=use_instance_id_netlist)

        self.components[cmpid].set_property("DC", value)
        return cmpid, cmpname

    def create_coupling_inductors(self, compname, l1, l2, value=1, xpos=0, ypos=0, angle=0, use_instance_id_netlist=False):
        """Create a new Coupling Inductor

        Parameters
        ----------
        compname :
            name
        value :
            value (Default value = 1)
        xpos :
            x pos (Default value = 0)
        ypos :
            y pos (Default value = 0)
        angle :
            angle (Default value = 0)
        use_instance_id_netlist :
            bool (Default value = False)
        l1 :
            
        l2 :
            

        Returns
        -------
        type
            id, name

        """
        cmpid, cmpname = self.create_component(compname,component_library="Inductors", component_name="K_IND", xpos=xpos, ypos=ypos,
                                         angle=angle, use_instance_id_netlist=use_instance_id_netlist)

        self.components[cmpid].set_property("Inductor1", l1)
        self.components[cmpid].set_property("Inductor2", l2)
        self.components[cmpid].set_property("CouplingFactor", value)
        return cmpid, cmpname

    @aedt_exception_handler
    def create_diode(self, compname=None,model_name="required", xpos=0, ypos=0, angle=0, use_instance_id_netlist=False):
        """Create a new Diode

        Parameters
        ----------
        compname :
            name (Default value = None)
        value :
            value
        xpos :
            x pos (Default value = 0)
        ypos :
            y pos (Default value = 0)
        angle :
            angle (Default value = 0)
        use_instance_id_netlist :
            bool (Default value = False)
        model_name :
             (Default value = "required")

        Returns
        -------
        type
            id, name

        """
        cmpid, cmpname = self.create_component(compname,component_library="Diodes", component_name="DIODE_Level1", xpos=xpos, ypos=ypos,
                                         angle=angle, use_instance_id_netlist=use_instance_id_netlist)

        self.components[cmpid].set_property("MOD", model_name)
        return cmpid, cmpname

    @aedt_exception_handler
    def create_npn(self, compname=None, value=None, xpos=0, ypos=0, angle=0, use_instance_id_netlist=False):
        """Create a new Transistor NPN

        Parameters
        ----------
        compname :
            name (Default value = None)
        value :
            value (Default value = None)
        xpos :
            x pos (Default value = 0)
        ypos :
            y pos (Default value = 0)
        angle :
            angle (Default value = 0)
        use_instance_id_netlist :
            bool (Default value = False)

        Returns
        -------
        type
            id, name

        """

        id, name = self.create_component(compname,component_library="BJTs", component_name="Level01_NPN", xpos=xpos, ypos=ypos,
                                         angle=angle, use_instance_id_netlist=use_instance_id_netlist)
        if value:
            self.components[id].set_property("MOD", value)
        return id, name

    @aedt_exception_handler
    def create_pnp(self, compname=None,value=50, xpos=0, ypos=0, angle=0, use_instance_id_netlist=False):
        """Create a new Transistor PNP

        Parameters
        ----------
        compname :
            name (Default value = None)
        value :
            value (Default value = 50)
        xpos :
            x pos (Default value = 0)
        ypos :
            y pos (Default value = 0)
        angle :
            angle (Default value = 0)
        use_instance_id_netlist :
            bool (Default value = False)

        Returns
        -------
        type
            id, name

        """
        id, name = self.create_component(compname, component_library="BJTs", component_name="Level01_PNP", xpos=xpos, ypos=ypos,
                                         angle=angle, use_instance_id_netlist=use_instance_id_netlist)
        if value:
            self.components[id].set_property( "MOD", value)

        return id, name

    @aedt_exception_handler
    def create_new_component_from_symbol(self,symbol_name, pin_lists, Refbase = "U", parameter_list=[], parameter_value=[]):
        """Create a new Component from symbol

        Parameters
        ----------
        symbol_name :
            symbol name
        pin_lists :
            list of pins name
        Refbase :
            reference base (Default value = "U")
        parameter_list :
            list of parameters (Default value = [])
        parameter_value :
            list of parameters values (Default value = [])

        Returns
        -------
        type
            true

        """
        arg = ["NAME:" + symbol_name, "Info:=",
               ["Type:=", 0, "NumTerminals:=", len(pin_lists), "DataSource:=", "", "ModifiedOn:=", 1591858313, "Manufacturer:=", "",
                "Symbol:=", symbol_name, "ModelNames:=", "", "Footprint:=", "",
                "Description:=", "", "InfoTopic:=", "", "InfoHelpFile:=", "", "IconFile:=", "", "Library:=", "",
                "OriginalLocation:=", "Project", "IEEE:=", "", "Author:=", "", "OriginalAuthor:=", "",
                "CreationDate:=", 1591858278, "ExampleFile:=", "", "HiddenComponent:=", 0, "CircuitEnv:=", 0,
                "GroupID:=", 0], "CircuitEnv:=", 0, "Refbase:=", Refbase, "NumParts:=", 1, "ModSinceLib:=", True]

        for pin in pin_lists:
            arg.append("Terminal:=")
            arg.append([pin, pin, "A", False, 0, 1, "", "Electrical", "0"])
        arg.append("CompExtID:=")
        arg.append(1)
        arg2 = ["NAME:Parameters"]
        for el, val in zip(parameter_list, parameter_value):
            if type(val) is str:
                arg2.append("TextValueProp:=")
                arg2.append([el, "D", "", val])
            else:
                arg2.append("ValueProp:=")
                arg2.append([el, "D", "", val, False, ""])
        arg2.append("ButtonProp:=")
        arg2.append(["CosimDefinition", "D", "", "Edit", "Edit", 40501, "ButtonPropClientData:=", []])
        arg2.append("MenuProp:=")
        arg2.append(["CoSimulator", "D", "", "DefaultNetlist", 0])

        arg.append(arg2)
        spicesintax = Refbase + "@ID "
        id = 0
        while id < len(pin_lists):
            spicesintax += "%" + str(id) + " "
            id += 1
        for el, val in zip(parameter_list, parameter_value):
            if "MOD" in el:
                spicesintax += "@{} ".format(el)
            else:
                spicesintax += "{}=@{} ".format(el,val)

        arg3 = [
            "NAME:CosimDefinitions",
            [
                "NAME:CosimDefinition",
                "CosimulatorType:=", 4,
                "CosimDefName:=", "DefaultNetlist",
                "IsDefinition:=", True,
                "Connect:="	, True,
                "Data:="		, [					"Nexxim Circuit:="	, spicesintax],
                "GRef:="		, [					"Nexxim Circuit:="	, ""]
            ],
            "DefaultCosim:="	, "DefaultNetlist"
        ]
        arg.append(arg3)
        self.o_component_manager.Add(arg)
        return True

    @aedt_exception_handler
    def update_object_properties(self, o):
        """

        Parameters
        ----------
        o :
            object

        Returns
        -------
        type
            object with properties

        """
        name = o.composed_name
        proparray = self.oeditor.GetProperties("PassedParameterTab", name)
        for j in proparray:
            propval = self.oeditor.GetPropertyValue("PassedParameterTab", name, j)
            o._add_property(j, propval)
        return o

    @aedt_exception_handler
    def get_comp_custom_settings(self, toolNum ,dc = 0, interp=0, extrap=1, conv=0, passivity=0, reciprocal="False", opt="", data_type=1):
        """

        Parameters
        ----------
        toolNum :
            param dc:
        interp :
            param extrap: (Default value = 0)
        conv :
            param passivity: (Default value = 0)
        reciprocal :
            param opt: (Default value = "False")
        data_type :
            return: (Default value = 1)
        dc :
             (Default value = 0)
        extrap :
             (Default value = 1)
        passivity :
             (Default value = 0)
        opt :
             (Default value = "")

        Returns
        -------

        """
        if toolNum == 1:
            custom = "NAME:DesignerCustomization"
        elif toolNum == 2:
            custom = "NAME:NexximCustomization"
        else:
            custom = "NAME:HSpiceCustomization"

        res = [custom,
               "DCOption:="		, dc,
               "InterpOption:="	, interp,
               "ExtrapOption:="	, extrap,
               "Convolution:="		, conv,
               "Passivity:="		, passivity,
               "Reciprocal:="		, reciprocal,
               "ModelOption:="		, opt,
               "DataType:="		, data_type]

        return res

    @aedt_exception_handler
    def add_subcircuit_hfss_link(self, compName, pin_names, source_project_path, source_project_name, source_design_name, solution_name = "Setup1 : Sweep"):
        """

        Parameters
        ----------
        compName :
            param pin_names:
        source_project_path :
            param source_project_name:
        source_design_name :
            param solution_name:
        pin_names :
            
        source_project_name :
            
        solution_name :
             (Default value = "Setup1 : Sweep")

        Returns
        -------

        """
        designer_customization = self.get_comp_custom_settings(1, 0, 0, 1, 0, 0, "False", "", 1)
        nexxim_customization = self.get_comp_custom_settings(2, 3, 1, 3, 0, 0, "False", "", 2)
        hspice_customization = self.get_comp_custom_settings(3, 1, 2, 3, 0, 0, "False", "", 3)

        compInfo = ["NAME:"+str(compName),
                    "Name:=", compName,
                    "ModTime:=", 1591855779,
                    "Library:=", "",
                    "LibLocation:=", "Project",
                    "ModelType:=", "hfss",
                    "Description:=", "",
                    "ImageFile:=", "",
                    "SymbolPinConfiguration:=", 0,
                    ["NAME:PortInfoBlk"],
                    ["NAME:PortOrderBlk"],
                    "DesignName:=", source_design_name,
                    "SolutionName:=", solution_name,
                    "NewToOldMap:=", [],
                    "OldToNewMap:=", [],
                    "PinNames:=", pin_names,
                    designer_customization,
                    nexxim_customization,
                    hspice_customization,
                    "NoiseModelOption:=", "External",
                    "WB_SystemID:=", "",
                    "IsWBModel:=", False,
                    "filename:=", source_project_path,
                    "numberofports:=", len(pin_names),
                    "Simulate:=", False,
                    "CloseProject:=", False,
                    "SaveProject:=", True,
                    "InterpY:=", True,
                    "InterpAlg:=", "auto",
                    "IgnoreDepVars:=", False,
                    "Renormalize:=", False,
                    "RenormImpedance:=", 50]

        self.o_model_manager.Add(compInfo)

        info = ["Type:=", 8, "NumTerminals:=", len(pin_names), "DataSource:=", "", "ModifiedOn:=", 1591855894, "Manufacturer:=", "",
                "Symbol:=", "", "ModelNames:=", "", "Footprint:=", "", "Description:=", "", "InfoTopic:=", "",
                "InfoHelpFile:=", "",	"IconFile:=", "hfss.bmp", "Library:=", "",	"OriginalLocation:=", "Project",
                "IEEE:=", "", "Author:=", "", "OriginalAuthor:=", "",	"CreationDate:=", 1591855894, "ExampleFile:=", "",
                "HiddenComponent:=", 0, "CircuitEnv:=", 0, "GroupID:=", 0]



        compInfo2 = ["NAME:"+str(compName),
                     "Info:=", info,
                     "CircuitEnv:=", 0,
                     "Refbase:=", "S",
                     "NumParts:=", 1,
                     "ModSinceLib:=", False]

        id = 0
        for pin in pin_names:
            compInfo2.append("Terminal:=")
            compInfo2.append([pin ,pin, "A", False, id, 1, "", "Electrical", "0"])
            id += 1

        compInfo2.append(["NAME:Properties","TextProp:=", ["Owner" ,"RD" ,"" ,"HFSS"]])
        compInfo2.append("CompExtID:=")
        compInfo2.append(5)
        compInfo2.append(["NAME:Parameters",
                          "TextProp:=", ["ModelName" ,"RD" ,"" ,"FieldSolver"],
                          "MenuProp:=", ["CoSimulator" ,"SD" ,"" ,"Default" ,0],
                          "ButtonProp:=", ["CosimDefinition" ,"SD" ,"" ,"Edit" ,"Edit" ,40501, "ButtonPropClientData:=", []]])
        compInfo2.append(["NAME:CosimDefinitions",
                          ["NAME:CosimDefinition",
                           "CosimulatorType:=", 103,
                           "CosimDefName:=", "Default",
                           "IsDefinition:=", True,
                           "Connect:=", True,
                           "ModelDefinitionName:=", compName,
                           "ShowRefPin2:=", 2,
                           "LenPropName:=", ""],
                          "DefaultCosim:=", "Default"])

        self.o_component_manager.Add(compInfo2)
        self._parent.odesign.AddCompInstance(compName)
        self.refresh_all_ids()
        for el in self.components:
            item = compName
            item2 = self.components[el].composed_name
            if compName in self.components[el].composed_name:
                return el, self.components[el].composed_name
        return False

    @aedt_exception_handler
    def set_sim_option_on_hfss_subcircuit(self, component):
        """

        Parameters
        ----------
        component :
            CompInst@Galileo_cutout3;87;1

        Returns
        -------

        """
        complist = component.split(";")
        complist2 = complist[0].split("@")
        arg = ["NAME:AllTabs"]
        arg1 = ["NAME:Model"]
        arg2 = ["NAME:PropServers", "Component@"+str(complist2[1])]
        arg3 = ["NAME:ChangedProps",["NAME:Simulation option", "Value:=", "Simulate missing solutions"]]

        arg1.append(arg2)
        arg1.append(arg3)
        arg.append(arg1)

        self._parent._oproject.ChangeProperty(arg)

        argo = ["NAME:AllTabs", ["NAME:Component", ["NAME:PropServers", str(component)]]]

        self.oeditor.ChangeProperty(argo)

        pass

    @aedt_exception_handler
    def refresh_dynamic_link(self, component_name):
        """

        Parameters
        ----------
        component_name :
            

        Returns
        -------

        """
        self.o_component_manager.UpdateDynamicLink(component_name)

    @aedt_exception_handler
    def push_excitations(self, instance_name,thevenin_calculation = False):
        """

        Parameters
        ----------
        instance_name :
            
        thevenin_calculation :
             (Default value = False)

        Returns
        -------

        """
        arg = ["NAME:options",
               "CalcThevenin:=", thevenin_calculation,
               "Sol:=", "LinearFrequency"]

        self.oeditor.PushExcitation(instance_name, arg)
        pass

    @aedt_exception_handler
    def assign_sin_excitation2ports(self, ports, settings):
        """

        Parameters
        ----------
        ports :
            List of circuit ports for excitation assignation
        settings :
            List of parameters values used in voltage sinusoidal excitation creation:
        settings :
            0]: AC magnitude for small-signal analysis
        settings :
            1]: AC phase for small-signal analysis
        settings :
            2]: DC voltage
        settings :
            3]: Voltage offset from zero
        settings :
            4]: Voltage amplitude
        settings :
            5]: Frequency
        settings :
            6]: Delay to start of sine wave
        settings :
            7]: Damping factor
        settings :
            8]: Phase Delay
        settings :
            9]: Frequency to use for harmonic balance analysis

        Returns
        -------

        """
        id = self.create_unique_id()

        arg1 = ["NAME:NexximSources",
                ["NAME:NexximSources",
                 ["NAME:Data",
                  ["NAME:VoltageSinusoidal"+str(id),
                   "DataId:=", "Source"+str(id),
                   "Type:=", 1,
                   "Output:=", 0,
                   "NumPins:=", 2,
                   "Netlist:=", "V@ID %0 %1 *DC(DC=@DC) SIN(?VO(@VO) ?VA(@VA) ?FREQ(@FREQ) ?TD(@TD) ?ALPHA(@ALPHA) ?THETA(@THETA)) *TONE(TONE=@TONE) *ACMAG(AC @ACMAG @ACPHASE)",
                   "CompName:=", "Nexxim Circuit Elements\\Independent Sources:V_SIN",
                   "FDSFileName:=", "",
                   ["NAME:Properties",
                    "TextProp:=", ["LabelID","HD","Property string for netlist ID","V@ID"],
                    "ValueProp:=", ["ACMAG","D","AC magnitude for small-signal analysis (Volts)",settings[0],0],
                    "ValuePropNU:=", ["ACPHASE","D","AC phase for small-signal analysis",settings[1],0,"deg"],
                    "ValueProp:=", ["DC","D","DC voltage (Volts)",settings[2],0],
                    "ValueProp:=", ["VO","OD","Voltage offset from zero (Volts)",settings[3],0],
                    "ValueProp:=", ["VA","OD","Voltage amplitude (Volts)",settings[4],0],
                    "ValueProp:=", ["FREQ","OD","Frequency (Hz)",settings[5],0],
                    "ValueProp:=", ["TD","D","Delay to start of sine wave (seconds)",settings[6],0],
                    "ValueProp:=", ["ALPHA","D","Damping factor (1/seconds)",settings[7],0],
                    "ValuePropNU:=", ["THETA","D","Phase delay",settings[8],0,"deg"],
                    "ValueProp:=", ["TONE","D","Frequency (Hz) to use for harmonic balance analysis, should be a submultiple of (or equal to) the driving frequency and should also be included in the HB analysis setup",settings[9],0],
                    "TextProp:=", ["ModelName","SHD","","V_SIN"],
                    "MenuProp:=", ["CoSimulator","D","","DefaultNetlist",0],
                    "ButtonProp:=", ["CosimDefinition","D","","","Edit",40501, "ButtonPropClientData:=", [] ] ] ] ] ] ]

        arg2 = ["NAME:ComponentConfigurationData"]

        arg3 = ["NAME:ComponentConfigurationData", ["NAME:EnabledPorts", "VoltageSinusoidal"+str(id)+":=", ports],
                ["NAME:EnabledMultipleComponents", "VoltageSinusoidal"+str(id)+":=", [] ] ]

        for prt in ports:
            arg_temp = []
            arg_temp = ["NAME:EnabledAnalyses", ["NAME:"+str(prt), str(prt)+":=", [] ], ["NAME:VoltageSinusoidal"+str(id), str(prt)+":=", [] ] ]
            arg3.append(arg_temp)

        arg2.append(arg3)

        self._parent.odesign.UpdateSources(arg1,arg2)

        pass