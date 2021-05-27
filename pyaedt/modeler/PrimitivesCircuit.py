import random
from collections import defaultdict

from ..generic.general_methods import aedt_exception_handler, retry_ntimes
from .Object3d import CircuitComponent

class CircuitComponents(object):
    """Common Class for management of all CircuitComponents for Nexxim and Simplorer"""

    @property
    def oeditor(self):
        """ """
        return self.modeler.oeditor

    @property
    def messenger(self):
        """ """
        return self._parent._messenger

    @property
    def version(self):
        """ """
        return self._parent._aedt_version

    @property
    def design_types(self):
        """ """
        return self._parent._modeler

    @property
    def model_units(self):
        """ """
        return self.modeler.model_units

    @property
    def o_model_manager(self):
        """ """
        return self.modeler.o_model_manager

    @property
    def o_definition_manager(self):
        """ """
        return self._parent._oproject.GetDefinitionManager()

    @property
    def o_symbol_manager(self):
        """ """
        return self.o_definition_manager.GetManager("Symbol")

    @property
    def o_component_manager(self):
        """ """
        return self.o_definition_manager.GetManager("Component")

    @property
    def design_type(self):
        """ """
        return self._parent.design_type

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
        self._parent = parent
        self.modeler = modeler
        self._currentId = 0
        self.components = defaultdict(CircuitComponent)
        pass

    @aedt_exception_handler
    def create_unique_id(self):
        """ """
        id = random.randint(1, 65535)
        while id in self.components:
            id = random.randint(1, 65535)
        return id

    @aedt_exception_handler
    def create_wire(self, points_array):
        """

        Parameters
        ----------
        points_array :
            list of list of points coordinate [[x1,y1], [x2,y2]....]

        Returns
        -------

        """
        pointlist = [str(tuple(i)) for i in points_array]
        self.oeditor.CreateWire(
            [
                "NAME:WireData",
                "Name:=", "",
                "Id:=", random.randint(20000, 23000),
                "Points:=", pointlist
            ],
            [
                "NAME:Attributes",
                "Page:=", 1
            ])
        return True

    @aedt_exception_handler
    def create_iport(self, name, posx=0.1, posy=0.1, angle=0):
        """Create new port

        Parameters
        ----------
        name :
            port name
        posx :
            x position (Default value = 0.1)
        posy :
            y position (Default value = 0.1)
        angle :
            angle rotation (Default value = 0)

        Returns
        -------
        type
            port object,  port_name

        """
        id = self.create_unique_id()
        arg1 = ["NAME:IPortProps", "Name:=", name, "Id:=", id]
        arg2 = ["NAME:Attributes", "Page:=", 1, "X:=", posx, "Y:=", posy, "Angle:=", angle, "Flip:=", False]
        id = self.oeditor.CreateIPort(arg1, arg2)

        id = int(id.split(";")[1])
        self.add_id_to_component(id)
        # return id, self.components[id].composed_name
        for el in self.components:
            if name in self.components[el].composed_name:
                return el, self.components[el].composed_name

    @aedt_exception_handler
    def create_page_port(self, name, posx=0.1, posy=0.1, angle=0):
        """Create new Page port

        Parameters
        ----------
        name :
            port name
        posx :
            x position (Default value = 0.1)
        posy :
            y position (Default value = 0.1)
        angle :
            angle rotation (Default value = 0)

        Returns
        -------
        type
            port id,  port_name

        """
        id = self.create_unique_id()
        id = self.oeditor.CreatePagePort(
            [
                "NAME:PagePortProps",
                "Name:=", name,
                "Id:=", id
            ],
            [
                "NAME:Attributes",
                "Page:=", 1,
                "X:=", posx,
                "Y:=", posy,
                "Angle:=", angle,
                "Flip:=", False
            ])
        id = int(id.split(";")[1])
        # self.refresh_all_ids()
        self.add_id_to_component(id)
        return id, self.components[id].composed_name

    @aedt_exception_handler
    def create_gnd(self, posx, posy):
        """Create GNDt

        Parameters
        ----------
        posx :
            x position
        posy :
            y position

        Returns
        -------
        type
            gnd object,  gnd name

        """
        id = self.create_unique_id()

        name = self.oeditor.CreateGround(
            [
                "NAME:GroundProps",
                "Id:=", id
            ],
            [
                "NAME:Attributes",
                "Page:=", 1,
                "X:=", posx,
                "Y:=", posy,
                "Angle:=", 0,
                "Flip:=", False
            ])
        id = int(name.split(";")[1])
        self.add_id_to_component(id)
        # return id, self.components[id].composed_name
        for el in self.components:
            if name in self.components[el].composed_name:
                return el, self.components[el].composed_name

    @aedt_exception_handler
    def create_model_from_touchstone(self, touchstone_full_path, model_name=None):
        """

        Parameters
        ----------
        touchstone_full_path :
            
        model_name :
             (Default value = None)

        Returns
        -------

        """
        if not model_name:
            model_name = os.path.splitext(os.path.basename(touchstone_full_path))[0]

        num_terminal = int(touchstone_full_path[-2:-1])
        arg = ["NAME:" + model_name, "Name:=", model_name, "ModTime:=", 0, "Library:=", "", "LibLocation:=", "Project",
               "ModelType:=", "nport", "Description:=", "", "ImageFile:=", "", "SymbolPinConfiguration:=", 0,
               ["NAME:PortInfoBlk"], ["NAME:PortOrderBlk"], "filename:=", touchstone_full_path, "numberofports:=",
               num_terminal, "sssfilename:=", "", "sssmodel:=", False, "PortNames:=",
               ["Port" + str(i + 1) for i in range(num_terminal)], "domain:=", "frequency", "datamode:=",
               "Link", "devicename:=", "", "SolutionName:=", "", "displayformat:=", "MagnitudePhase", "datatype:=",
               "SMatrix", ["NAME:DesignerCustomization", "DCOption:=", 0, "InterpOption:=", 0, "ExtrapOption:=", 1,
                           "Convolution:=", 0, "Passivity:=", 0, "Reciprocal:=", False, "ModelOption:=", "",
                           "DataType:=", 1],
               ["NAME:NexximCustomization", "DCOption:=", 3, "InterpOption:=", 1, "ExtrapOption:=", 3, "Convolution:=",
                0, "Passivity:=", 0, "Reciprocal:=", False, "ModelOption:=", "", "DataType:=", 2],
               ["NAME:HSpiceCustomization", "DCOption:=", 1, "InterpOption:=", 2, "ExtrapOption:=", 3, "Convolution:=",
                0, "Passivity:=", 0, "Reciprocal:=", False, "ModelOption:=", "", "DataType:=", 3], "NoiseModelOption:=",
               "External"]
        self.o_model_manager.Add(arg)
        arg = ["NAME:" + model_name, "Info:=",
               ["Type:=", 10, "NumTerminals:=", num_terminal, "DataSource:=", "", "ModifiedOn:=", 1618569625,
                "Manufacturer:=",
                "", "Symbol:=", "", "ModelNames:=", "", "Footprint:=", "", "Description:=", "", "InfoTopic:=", "",
                "InfoHelpFile:=", "", "IconFile:=", "nport.bmp", "Library:=", "", "OriginalLocation:=", "Project",
                "IEEE:=", "", "Author:=", "", "OriginalAuthor:=", "", "CreationDate:=", 1618569625, "ExampleFile:=",
                "", "HiddenComponent:=", 0, "CircuitEnv:=", 0, "GroupID:=", 0],
               "CircuitEnv:=", 0, "Refbase:=", "S", "NumParts:=", 1,
               "ModSinceLib:=", False]
        for i in range(num_terminal):
            arg.append("Terminal:=")
            arg.append(["Port" + str(i + 1), "Port" + str(i + 1), "A", False, i + 6, 1, "", "Electrical", "0"])
        arg.append("CompExtID:=")
        arg.append(num_terminal)
        arg.append(["NAME:Parameters", "MenuProp:=", ["CoSimulator", "SD", "", "Default", 0], "ButtonProp:=",
                    ["CosimDefinition", "SD", "", "Edit", "Edit", 40501, "ButtonPropClientData:=", []]])
        arg.append(["NAME:CosimDefinitions",
                    ["NAME:CosimDefinition", "CosimulatorType:=", 102, "CosimDefName:=", "Default", "IsDefinition:=",
                     True, "Connect:=", True, "ModelDefinitionName:=", model_name, "ShowRefPin2:=", 2, "LenPropName:=",
                     ""], "DefaultCosim:=", "Default"])

        self.o_component_manager.Add(arg)

    @aedt_exception_handler
    def create_component_from_touchstonmodel(self, modelname,xpos=0.1, ypos=0.1, angle=0,):
        """

        Parameters
        ----------
        modelname :
            
        xpos :
             (Default value = 0.1)
        ypos :
             (Default value = 0.1)
        angle :
             (Default value = 0)

        Returns
        -------

        """
        id = self.create_unique_id()
        id = self.oeditor.CreateComponent(["NAME:ComponentProps", "Name:=", modelname, "Id:=", str(id)],
                                ["NAME:Attributes", "Page:=", 1, "X:=", xpos, "Y:=", ypos, "Angle:=", angle, "Flip:=",
                                 False])
        id = int(id.split(";")[1])
        self.add_id_to_component(id)
        return id, self.components[id].composed_name


    @aedt_exception_handler
    def create_component(self, inst_name=None, component_library="Resistors",
                         component_name="RES_", xpos=0.1, ypos=0.1, angle=0, use_instance_id_netlist=False,
                         global_netlist_list=[]):
        """Create new component from Library

        Parameters
        ----------
        inst_name :
            Instance Name (Default value = None)
        component_library :
            Component Library (Default Resistors)
        component_name :
            Component name in library Default RES
        xpos :
            x position (Default value = 0.1)
        ypos :
            y position (Default value = 0.1)
        angle :
            component angle (Default value = 0)
        use_instance_id_netlist :
            bool to enable instance id in netlist (Default value = False)
        global_netlist_list :
             (Default value = [])

        Returns
        -------
        type
            id , composed_name

        """
        id = self.create_unique_id()
        if component_library:
            name = self.design_libray + "\\" + component_library + ":" + component_name
        else:
            name = component_name
        id = self.oeditor.CreateComponent(
            [
                "NAME:ComponentProps",
                "Name:=", name,
                "Id:=", str(id)
            ],
            [
                "NAME:Attributes",
                "Page:=", 1,
                "X:=", xpos,
                "Y:=", ypos,
                "Angle:=", angle,
                "Flip:=", False
            ])
        id = int(id.split(";")[1])
        # self.refresh_all_ids()
        self.add_id_to_component(id)
        if inst_name:
            self.components[id].set_property("InstanceName", inst_name)
        if use_instance_id_netlist:
            self.enable_use_instance_name(component_library, component_name)
        elif global_netlist_list:
            self.enable_global_netlist(component_name, global_netlist_list)
        return id, self.components[id].composed_name

    @aedt_exception_handler
    def disable_data_netlist(self, component_name):
        """Disable Nexxim Global Netlist

        Parameters
        ----------
        component_name :
            Name of Component

        Returns
        -------
        type
            Bool

        """
        name = component_name

        properties = self.o_component_manager.GetData(name)
        if len(properties) > 0:
            nexxim = list(properties[len(properties) - 1][1])
            for el in nexxim:
                if el == "Data:=":
                    nexxim_data = list(nexxim[nexxim.index(el) + 1])
                    nexxim_data[1] = ""
                    nexxim[nexxim.index(el) + 1] = nexxim_data
        self.o_component_manager.Edit(name, ["Name:" + component_name,
                                             ["NAME:CosimDefinitions", nexxim, "DefaultCosim:=", "DefaultNetlist"]])
        return True

    @aedt_exception_handler
    def enable_global_netlist(self, component_name, global_netlist_list=[]):
        """Enable Nexxim Global Netlist

        Parameters
        ----------
        component_name :
            Name of Component
        global_netlist_list :
            List of line to be included (Default value = [])

        Returns
        -------
        type
            Bool

        """
        name = component_name

        properties = self.o_component_manager.GetData(name)
        if len(properties) > 0:
            nexxim = list(properties[len(properties) - 1][1])
            for el in nexxim:
                if el == "GRef:=":
                    nexxim_data = list(nexxim[nexxim.index(el) + 1])
                    nexxim_data[1] = "\n".join(global_netlist_list).replace("\\", "/")
                    nexxim[nexxim.index(el) + 1] = nexxim_data
        retry_ntimes(10, self.o_component_manager.Edit, name, ["Name:" + component_name,
                                             ["NAME:CosimDefinitions", nexxim, "DefaultCosim:=", "DefaultNetlist"]])
        return True

    @aedt_exception_handler
    def create_symbol(self, symbol_name, pin_lists):
        """Create new symbol

        Parameters
        ----------
        symbol_name :
            symbol name
        pin_lists :
            name of pins

        Returns
        -------
        type
            Bool

        """

        numpins = len(pin_lists)
        h = int(numpins / 2)
        x1 = 0
        y2 = 0
        x2 = 0.00508
        y1 = 0.00254 * (h + 3)
        xp = -0.00254
        yp = 0.00254 * (h + 2)
        angle = 0
        self.o_symbol_manager.Add(
            [
                "NAME:" + symbol_name,
                "ModTime:=", 1591858230,
                "Library:=", "",
                "ModSinceLib:=", False,
                "LibLocation:=", "Project",
                "HighestLevel:=", 1,
                "Normalize:=", True,
                "InitialLevels:=", [0, 1],
                [
                    "NAME:Graphics"
                ]
            ])
        arg = ["NAME:" + symbol_name, "ModTime:=", 1591858265, "Library:=", "", "ModSinceLib:=", False, "LibLocation:=",
               "Project", "HighestLevel:=", 1, "Normalize:=", False, "InitialLevels:=", [0, 1]]
        oDefinitionEditor = self._parent._oproject.SetActiveDefinitionEditor("SymbolEditor", symbol_name)

        id = 2
        oDefinitionEditor.CreateRectangle(
            [
                "NAME:RectData",
                "X1:=", x1,
                "Y1:=", y1,
                "X2:=", x2,
                "Y2:=", y2,
                "LineWidth:=", 0,
                "BorderColor:=", 0,
                "Fill:=", 0,
                "Color:=", 0,
                "Id:=", id
            ],
            [
                "NAME:Attributes",
                "Page:=", 1
            ])
        i = 1
        id += 2
        r = numpins - (h * 2)
        for pin in pin_lists:
            oDefinitionEditor.CreatePin(
                [
                    "NAME:PinData",
                    "Name:=", pin,
                    "Id:=", id
                ],
                [
                    "NAME:PinParams",
                    "X:=", xp,
                    "Y:=", yp,
                    "Angle:=", angle,
                    "Flip:=", False
                ])
            arg.append(["NAME:PinDef", "Pin:=",
                        [pin, xp, yp, angle, "N", 0, 0.00254, False, 0, True, "", False, False, pin,
                         True]])
            if i == (h + r):
                yp = 0.00254 * (h + 2)
                xp = 0.00762
                angle = 3.14159265358979
            else:
                yp -= 0.00254
            id += 2
            i += 1

        arg.append(["NAME:Graphics",
                    ["NAME:1", "Rect:=", [0, 0, 0, 0, (x1 + x2) / 2, (y1 + y2) / 2, x2 - x1, y1 - y2, 0, 0, 8192]]])
        self.o_symbol_manager.EditWithComps(symbol_name, arg, [])
        oDefinitionEditor.CloseEditor()
        return True

    @aedt_exception_handler
    def create_new_component_from_symbol(self, symbol_name, pin_lists, Refbase="U", parameter_list=[],
                                         parameter_value=[]):
        """Create new Component from Symbol

        Parameters
        ----------
        symbol_name :
            Symbol Name
        pin_lists :
            Pin Lists
        Refbase :
            Reference Base (Default value = "U")
        parameter_list :
            Parameter Lists (Default value = [])
        parameter_value :
            Parameter Value Lists (Default value = [])

        Returns
        -------

        """
        arg = ["NAME:" + symbol_name, "Info:=",
               ["Type:=", 0, "NumTerminals:=", 5, "DataSource:=", "", "ModifiedOn:=", 1591858313, "Manufacturer:=", "",
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
        while id < (len(pin_lists) - 1):
            spicesintax += "%" + str(id) + " "
            id += 1
        for el in parameter_list:
            spicesintax += "@{} ".format(el)

        arg3 = [
            "NAME:CosimDefinitions",
            [
                "NAME:CosimDefinition",
                "CosimulatorType:=", 4,
                "CosimDefName:=", "DefaultNetlist",
                "IsDefinition:=", True,
                "Connect:=", True,
                "Data:=", ["Nexxim Circuit:=", spicesintax],
                "GRef:=", ["Nexxim Circuit:=", ""]
            ],
            "DefaultCosim:=", "DefaultNetlist"
        ]
        arg.append(arg3)
        self.o_component_manager.Add(arg)
        return True

    @aedt_exception_handler
    def enable_use_instance_name(self, component_library="Resistors",
                                 component_name="RES_"):
        """

        Parameters
        ----------
        component_library :
             (Default value = "Resistors")
        component_name :
             (Default value = "RES_")

        Returns
        -------

        """
        if component_library:
            name = self.design_libray + "\\" + component_library + ":" + component_name
        else:
            name = component_name

        properties = self.o_component_manager.GetData(name)
        if len(properties) > 0:
            nexxim = list(properties[len(properties) - 1][1])
            for el in nexxim:
                if el == "Data:=":
                    nexxim_data = list(nexxim[nexxim.index(el) + 1])
                    netlist = nexxim_data[1]
                    if "@InstanceName" not in netlist[:15]:
                        newnetlist = "@InstanceName" + netlist[4:]
                        nexxim_data[1] = newnetlist
                    nexxim[nexxim.index(el) + 1] = nexxim_data
                elif el == "GRef:=":
                    nexxim_data = list(nexxim[nexxim.index(el) + 1])
                    nexxim[nexxim.index(el) + 1] = nexxim_data
        retry_ntimes(10, self.o_component_manager.Edit, name, ["Name:" + component_name,
                                             ["NAME:CosimDefinitions", nexxim, "DefaultCosim:=", "DefaultNetlist"]])
        return True

    @aedt_exception_handler
    def refresh_all_ids(self):
        """:return: Refresh all Ids and return number of components"""
        obj = self.oeditor.GetAllComponents()
        for el in obj:
            if not self.get_obj_id(el):
                name = el.split(";")
                o = CircuitComponent(self.oeditor, tabname=self.tab_name)
                o.name = name[0]
                o.id = int(name[1])
                o.schematic_id = name[2]
                o_update = self.update_object_properties(o)
                objID = o.id
                self.components[objID] = o_update
        return len(self.components)

    @aedt_exception_handler
    def add_id_to_component(self, id):
        """

        Parameters
        ----------
        id :
            return:

        Returns
        -------

        """
        obj = retry_ntimes(10, self.oeditor.GetAllElements)
        for el in obj:
            name = el.split(";")
            if len(name) > 1 and str(id) == name[1]:
                o = CircuitComponent(self.oeditor, tabname=self.tab_name)
                o.name = name[0]
                if len(name) > 2:
                    o.id = int(name[1])
                    o.schematic_id = int(name[2])
                    objID = o.id
                else:
                    o.schematic_id = int(name[1])
                    objID = o.schematic_id
                o_update = self.update_object_properties(o)

                self.components[objID] = o_update
        return len(self.components)

    @aedt_exception_handler
    def get_obj_id(self, objname):
        """

        Parameters
        ----------
        objname :
            

        Returns
        -------

        """
        for el in self.components:
            if self.components[el].name == objname:
                return el
        return None

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
        proparray = retry_ntimes(10, self.oeditor.GetProperties, "PassedParameterTab", name)
        for j in proparray:
            propval = retry_ntimes(10, self.oeditor.GetPropertyValue, "PassedParameterTab", name, j)
            o._add_property(j, propval)
        return o

    @aedt_exception_handler
    def get_pins(self, partid):
        """

        Parameters
        ----------
        partid :
            component ID (int) or component full name (str)

        Returns
        -------
        type
            object with properties

        """
        if type(partid) is str:
            pins = retry_ntimes(10, self.oeditor.GetComponentPins, partid)
            #pins = self.oeditor.GetComponentPins(partid)
        else:
            pins = retry_ntimes(10, self.oeditor.GetComponentPins, self.components[partid].composed_name)
            #pins = self.oeditor.GetComponentPins(self.components[partid].composed_name)
        return list(pins)

    @aedt_exception_handler
    def get_pin_location(self, partid, pinname):
        """

        Parameters
        ----------
        partid :
            component ID
        pinname :
            Name of the Pin

        Returns
        -------
        type
            x, y] list

        """
        if type(partid) is str:
            x = retry_ntimes(30, self.oeditor.GetComponentPinLocation, partid, pinname, True)
            y = retry_ntimes(30, self.oeditor.GetComponentPinLocation, partid, pinname, False)
        else:
            x = retry_ntimes(30, self.oeditor.GetComponentPinLocation, self.components[partid].composed_name, pinname, True)
            y = retry_ntimes(30, self.oeditor.GetComponentPinLocation, self.components[partid].composed_name, pinname, False)
        return [x, y]

    @aedt_exception_handler
    def arg_with_dim(self, Value, sUnits=None):
        """

        Parameters
        ----------
        Value :
            
        sUnits :
             (Default value = None)

        Returns
        -------

        """
        if type(Value) is str:
            val = Value
        else:
            if sUnits is None:
                sUnits = self.model_units
            val = "{0}{1}".format(Value, sUnits)

        return val
