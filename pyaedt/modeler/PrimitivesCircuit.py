import math
import os
import random
import warnings

from pyaedt.generic.constants import AEDT_UNITS
from pyaedt.generic.general_methods import _retry_ntimes
from pyaedt.generic.general_methods import filter_string
from pyaedt.generic.general_methods import generate_unique_name
from pyaedt.generic.general_methods import open_file
from pyaedt.generic.general_methods import pyaedt_function_handler
from pyaedt.generic.general_methods import recursive_glob
from pyaedt.generic.LoadAEDTFile import load_keyword_in_aedt_file
from pyaedt.generic.TouchstoneParser import _parse_ports_name
from pyaedt.modeler.Object3d import CircuitComponent


class CircuitComponents(object):
    """CircutComponents class.

    Manages all circuit components for Nexxim and Twin Builder.

    Examples
    --------

    >>> from pyaedt import Circuit
    >>> aedtapp = Circuit()
    >>> prim = aedtapp.modeler.schematic
    """

    @pyaedt_function_handler()
    def __getitem__(self, partname):
        """Retrieve a part.

        Parameters
        ----------
        partname : int or str
           Part ID or part name.

        Returns
        -------
        type
            Part object details.
        """
        if isinstance(partname, int):
            return self.components[partname]
        for el in self.components:
            if self.components[el].name == partname or self.components[el].composed_name == partname or el == partname:
                return self.components[el]

        return None

    def __init__(self, modeler):
        self._app = modeler._app
        self._modeler = modeler
        self.logger = self._app.logger
        self.o_model_manager = self._modeler.o_model_manager

        self.oeditor = self._modeler.oeditor
        self._currentId = 0
        self.components = {}
        self.refresh_all_ids()
        self.current_position = [0, 0]
        self.increment_mils = [1000, 1000]
        self.limits_mils = 20000
        pass

    @property
    def o_definition_manager(self):
        """Aedt oDefinitionManager.

        References
        ----------

        >>> oDefinitionManager = oProject.GetDefinitionManager()
        """

        return self._app.oproject.GetDefinitionManager()

    @property
    def o_component_manager(self):
        """Component manager object."""
        return self._app.o_component_manager

    @property
    def o_symbol_manager(self):
        """Model manager object."""
        return self._app.o_symbol_manager

    @property
    def version(self):
        """Version."""
        return self._app._aedt_version

    @property
    def design_types(self):
        """Design types."""
        return self._app._modeler

    @property
    def model_units(self):
        """Model units."""
        return self._modeler.model_units

    @property
    def design_type(self):
        """Design type."""
        return self._app.design_type

    @property
    def nets(self):
        """List of all schematic nets."""
        nets_comp = self.oeditor.GetAllNets()
        nets = []
        for net in nets_comp:
            v = net.split(";")
            if v[0].replace("Wire@", "") not in nets:
                nets.append(v[0].replace("Wire@", ""))
        return nets

    @pyaedt_function_handler()
    def _get_location(self, location=None):
        if not location:
            xpos = self.current_position[0]
            ypos = self.current_position[1]
        else:
            xpos = location[0]
            ypos = location[1]
            self.current_position = location
        self.current_position[1] += AEDT_UNITS["Length"]["mil"] * self.increment_mils[1]
        if self.current_position[1] / AEDT_UNITS["Length"]["mil"] > self.limits_mils:
            self.current_position[1] = 0
            self.current_position[0] += AEDT_UNITS["Length"]["mil"] * self.increment_mils[0]
        return xpos, ypos

    @pyaedt_function_handler()
    def create_unique_id(self):
        """Create an unique ID.

        Returns
        -------
        int
            Unique ID in the range of ``[1, 65535]``.

        """
        id = random.randint(1, 65535)
        while id in self.components:
            id = random.randint(1, 65535)
        return id

    @pyaedt_function_handler()
    def create_wire(self, points_array):
        """Create a wire.

        Parameters
        ----------
        points_array : list
            A nested list of point coordinates. For example,
            ``[[x1, y1], [x2, y2], ...]``.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        References
        ----------

        >>> oEditor.CreateWire
        """
        pointlist = [str(tuple(i)) for i in points_array]
        self.oeditor.CreateWire(
            ["NAME:WireData", "Name:=", "", "Id:=", random.randint(20000, 23000), "Points:=", pointlist],
            ["NAME:Attributes", "Page:=", 1],
        )
        return True

    @pyaedt_function_handler()
    def add_pin_iports(self, name, id_num):
        """Add ports on pins.

        Parameters
        ----------
        name : str
            Name of the component.
        id_num : int
            ID of circuit component.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        References
        ----------

        >>> oeditor.AddPinIPorts
        """
        comp_id = "CompInst@" + name + ";" + str(id_num) + ";395"
        arg1 = ["Name:Selections", "Selections:=", [comp_id]]
        self.oeditor.AddPinIPorts(arg1)

        return True

    @pyaedt_function_handler()
    def create_iport(self, name, posx=0.1, posy=0.1, angle=0):
        """Create an interface port.

        .. deprecated:: 0.4.0
           Use :func:`Circuit.modeler.schematic.create_interface_port` instead.
        """
        warnings.warn("`create_iport` is deprecated. Use `create_interface_port` instead.", DeprecationWarning)
        return self.create_interface_port(name, [posx, posy], angle)

    @pyaedt_function_handler()
    def create_interface_port(self, name, location=[], angle=0):
        """Create an interface port.

        Parameters
        ----------
        name : str
            Name of the port.
        location : list, optional
            Position on the X and Y axis. The default is ``None``.
        angle : float, optional
            Angle rotation in degrees. The default is ``0``.

        Returns
        -------
        :class:`pyaedt.modeler.Object3d.CircuitComponent`
            Circuit Component Object.

        References
        ----------

        >>> oEditor.CreateIPort
        """
        if location:
            xpos, ypos = location[0], location[1]
        else:
            xpos, ypos = self._get_location(location)
        id = self.create_unique_id()
        arg1 = ["NAME:IPortProps", "Name:=", name, "Id:=", id]
        arg2 = ["NAME:Attributes", "Page:=", 1, "X:=", xpos, "Y:=", ypos, "Angle:=", angle, "Flip:=", False]
        id = self.oeditor.CreateIPort(arg1, arg2)

        id = int(id.split(";")[1])
        self.add_id_to_component(id)
        # return id, self.components[id].composed_name
        for el in self.components:
            if name in self.components[el].composed_name:
                return self.components[el]
        return False

    @pyaedt_function_handler()
    def create_page_port(self, name, location=[], angle=0):
        """Create a page port.

        Parameters
        ----------
        name : str
            Name of the port.
        location : list, optional
            Position on the X and Y axis. The default is ``None``.
        angle : optional
            Angle rotation in degrees. The default is ``0``.

        Returns
        -------
        :class:`pyaedt.modeler.Object3d.CircuitComponent`
            Circuit Component Object.

        References
        ----------

        >>> oEditor.CreatePagePort
        """
        if location:
            xpos, ypos = location[0], location[1]
        else:
            xpos, ypos = self._get_location(location)

        id = self.create_unique_id()
        id = self.oeditor.CreatePagePort(
            ["NAME:PagePortProps", "Name:=", name, "Id:=", id],
            ["NAME:Attributes", "Page:=", 1, "X:=", xpos, "Y:=", ypos, "Angle:=", angle, "Flip:=", False],
        )
        id = int(id.split(";")[1])
        # self.refresh_all_ids()
        self.add_id_to_component(id)
        return self.components[id]

    @pyaedt_function_handler()
    def create_gnd(self, location=[], angle=0):
        """Create a ground.

        Parameters
        ----------
        location : list, optional
            Position on the X and Y axis. The default is ``None``.
        angle : optional
            Angle rotation in degrees. The default is ``0``.

        Returns
        -------
        :class:`pyaedt.modeler.Object3d.CircuitComponent`
            Circuit Component Object.

        References
        ----------

        >>> oEditor.CreateGround
        """
        xpos, ypos = self._get_location(location)
        id = self.create_unique_id()

        name = self.oeditor.CreateGround(
            ["NAME:GroundProps", "Id:=", id],
            ["NAME:Attributes", "Page:=", 1, "X:=", xpos, "Y:=", ypos, "Angle:=", angle, "Flip:=", False],
        )
        id = int(name.split(";")[1])
        self.add_id_to_component(id)
        # return id, self.components[id].composed_name
        for el in self.components:
            if name in self.components[el].composed_name:
                return self.components[el]

    @pyaedt_function_handler()
    def create_model_from_touchstone(self, touchstone_full_path, model_name=None):
        """Create a model from a Touchstone file.

        Parameters
        ----------
        touchstone_full_path : str
            Full path to the Touchstone file.
        model_name : str, optional
            Name of the model. The default is ``None``.

        Returns
        -------
        str
            Model name when successfully created. ``False`` if something went wrong.

        References
        ----------

        >>> oModelManager.Add
        >>> oComponentManager.Add
        """
        if not model_name:
            model_name = os.path.splitext(os.path.basename(touchstone_full_path))[0]
        if model_name in list(self.o_model_manager.GetNames()):
            model_name = generate_unique_name(model_name, n=2)
        num_terminal = int(os.path.splitext(touchstone_full_path)[1].lower().strip(".sp"))
        with open_file(touchstone_full_path, "r") as f:
            port_names = _parse_ports_name(f)
        image_subcircuit_path = os.path.join(self._modeler._app.desktop_install_dir, "syslib", "Bitmaps", "nport.bmp")

        if not port_names:
            port_names = ["Port" + str(i + 1) for i in range(num_terminal)]
        arg = [
            "NAME:" + model_name,
            "Name:=",
            model_name,
            "ModTime:=",
            0,
            "Library:=",
            "",
            "LibLocation:=",
            "Project",
            "ModelType:=",
            "nport",
            "Description:=",
            "",
            "ImageFile:=",
            image_subcircuit_path,
            "SymbolPinConfiguration:=",
            0,
            ["NAME:PortInfoBlk"],
            ["NAME:PortOrderBlk"],
            "filename:=",
            touchstone_full_path,
            "numberofports:=",
            num_terminal,
            "sssfilename:=",
            "",
            "sssmodel:=",
            False,
            "PortNames:=",
            port_names,
            "domain:=",
            "frequency",
            "datamode:=",
            "Link",
            "devicename:=",
            "",
            "SolutionName:=",
            "",
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
        self.o_model_manager.Add(arg)
        arg = [
            "NAME:" + model_name,
            "Info:=",
            [
                "Type:=",
                10,
                "NumTerminals:=",
                num_terminal,
                "DataSource:=",
                "",
                "ModifiedOn:=",
                1618569625,
                "Manufacturer:=",
                "",
                "Symbol:=",
                "",
                "ModelNames:=",
                "",
                "Footprint:=",
                "",
                "Description:=",
                "",
                "InfoTopic:=",
                "",
                "InfoHelpFile:=",
                "",
                "IconFile:=",
                "nport.bmp",
                "Library:=",
                "",
                "OriginalLocation:=",
                "Project",
                "IEEE:=",
                "",
                "Author:=",
                "",
                "OriginalAuthor:=",
                "",
                "CreationDate:=",
                1618569625,
                "ExampleFile:=",
                "",
                "HiddenComponent:=",
                0,
                "CircuitEnv:=",
                0,
                "GroupID:=",
                0,
            ],
            "CircuitEnv:=",
            0,
            "Refbase:=",
            "S",
            "NumParts:=",
            1,
            "ModSinceLib:=",
            False,
        ]
        for i in range(num_terminal):
            arg.append("Terminal:=")
            arg.append([port_names[i], port_names[i], "A", False, i, 1, "", "Electrical", "0"])
        arg.append("CompExtID:=")
        arg.append(5)
        arg.append(
            [
                "NAME:Parameters",
                "MenuProp:=",
                ["CoSimulator", "SD", "", "Default", 0],
                "ButtonProp:=",
                ["CosimDefinition", "SD", "", "Edit", "Edit", 40501, "ButtonPropClientData:=", []],
            ]
        )
        arg.append(
            [
                "NAME:CosimDefinitions",
                [
                    "NAME:CosimDefinition",
                    "CosimulatorType:=",
                    102,
                    "CosimDefName:=",
                    "Default",
                    "IsDefinition:=",
                    True,
                    "Connect:=",
                    True,
                    "ModelDefinitionName:=",
                    model_name,
                    "ShowRefPin2:=",
                    2,
                    "LenPropName:=",
                    "",
                ],
                "DefaultCosim:=",
                "Default",
            ]
        )

        self.o_component_manager.Add(arg)
        return model_name

    @pyaedt_function_handler()
    def create_component_from_touchstonmodel(
        self,
        model_name,
        location=[],
        angle=0,
    ):
        """Create a component from a Touchstone model.

        .. deprecated:: 0.4.14
           Use :func:`create_touchsthone_component` instead.

        Parameters
        ----------
        model_name : str
            Name of the Touchstone model or full path to touchstone file.
            If full touchstone is provided then, new model will be created.
        location : list of float, optional
            Position on the X  and Y axis.
        angle : float, optional
            Angle rotation in degrees. The default is ``0``.

        Returns
        -------
        :class:`pyaedt.modeler.Object3d.CircuitComponent`
            Circuit Component Object.

        """
        return self.create_touchsthone_component(model_name, location, angle)

    @pyaedt_function_handler()
    def create_touchsthone_component(
        self,
        model_name,
        location=[],
        angle=0,
    ):
        """Create a component from a Touchstone model.

        Parameters
        ----------
        model_name : str
            Name of the Touchstone model or full path to touchstone file.
            If full touchstone is provided then, new model will be created.
        location : list of float, optional
            Position on the X  and Y axis.
        angle : float, optional
            Angle rotation in degrees. The default is ``0``.

        Returns
        -------
        :class:`pyaedt.modeler.Object3d.CircuitComponent`
            Circuit Component Object.

        References
        ----------

        >>> oModelManager.Add
        >>> oComponentManager.Add
        >>> oEditor.CreateComponent
        """
        xpos, ypos = self._get_location(location)
        id = self.create_unique_id()
        if os.path.exists(model_name):
            model_name = self.create_model_from_touchstone(model_name)
        arg1 = ["NAME:ComponentProps", "Name:=", model_name, "Id:=", str(id)]
        arg2 = ["NAME:Attributes", "Page:=", 1, "X:=", xpos, "Y:=", ypos, "Angle:=", angle, "Flip:=", False]
        id = _retry_ntimes(10, self.oeditor.CreateComponent, arg1, arg2)
        id = int(id.split(";")[1])
        self.add_id_to_component(id)
        return self.components[id]

    @pyaedt_function_handler()
    def create_component(
        self,
        inst_name=None,
        component_library="Resistors",
        component_name="RES_",
        location=[],
        angle=0,
        use_instance_id_netlist=False,
        global_netlist_list=[],
    ):
        """Create a component from a library.

        Parameters
        ----------
        inst_name : str, optional
            Name of the instance. The default is ``None.``
        component_library : str, optional
            Name of the component library. The default is ``"Resistors"``.
        component_name : str, optional
            Name of component in the library. The default is ``"RES"``.
        location : list of float, optional
            Position on the X axis and Y axis.
        angle : optional
            Angle rotation in degrees. The default is ``0``.
        use_instance_id_netlist : bool, optional
            Whether to enable the instance ID in the net list.
            The default is ``False``.
        global_netlist_list : list, optional
            The default is``[]``.

        Returns
        -------
        :class:`pyaedt.modeler.Object3d.CircuitComponent`
            Circuit Component Object.

        References
        ----------

        >>> oEditor.CreateComponent
        """
        id = self.create_unique_id()
        if component_library:
            name = self.design_libray + "\\" + component_library + ":" + component_name
        else:
            name = component_name
        arg1 = ["NAME:ComponentProps", "Name:=", name, "Id:=", str(id)]
        xpos, ypos = self._get_location(location)

        arg2 = ["NAME:Attributes", "Page:=", 1, "X:=", xpos, "Y:=", ypos, "Angle:=", angle, "Flip:=", False]
        id = _retry_ntimes(10, self.oeditor.CreateComponent, arg1, arg2)
        id = int(id.split(";")[1])
        # self.refresh_all_ids()
        self.add_id_to_component(id)
        if inst_name:
            self.components[id].set_property("InstanceName", inst_name)
        if use_instance_id_netlist:
            self.enable_use_instance_name(component_library, component_name)
        elif global_netlist_list:
            self.enable_global_netlist(component_name, global_netlist_list)
        return self.components[id]

    @pyaedt_function_handler()
    def disable_data_netlist(self, component_name):
        """Disable the Nexxim global net list.

        Parameters
        ----------
        component_name : str
            Name of the component.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        References
        ----------

        >>> oComponentManager.GetData
        >>> oComponentManager.Edit
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
        self.o_component_manager.Edit(
            name, ["Name:" + component_name, ["NAME:CosimDefinitions", nexxim, "DefaultCosim:=", "DefaultNetlist"]]
        )
        return True

    @pyaedt_function_handler()
    def enable_global_netlist(self, component_name, global_netlist_list=[]):
        """Enable Nexxim global net list.

        Parameters
        ----------
        component_name : str
            Name of the component.
        global_netlist_list : list
            A list of lines to include. The default is ``[]``.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        References
        ----------

        >>> oComponentManager.GetData
        >>> oComponentManager.Edit
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
        _retry_ntimes(
            10,
            self.o_component_manager.Edit,
            name,
            ["Name:" + component_name, ["NAME:CosimDefinitions", nexxim, "DefaultCosim:=", "DefaultNetlist"]],
        )
        return True

    @pyaedt_function_handler()
    def create_symbol(self, symbol_name, pin_lists):
        """Create a symbol.

        Parameters
        ----------
        symbol_name : str
            Name of the symbol.
        pin_lists : list
            List of the pins.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        References
        ----------

        >>> oSymbolManager.Add
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
                "ModTime:=",
                1591858230,
                "Library:=",
                "",
                "ModSinceLib:=",
                False,
                "LibLocation:=",
                "Project",
                "HighestLevel:=",
                1,
                "Normalize:=",
                True,
                "InitialLevels:=",
                [0, 1],
                ["NAME:Graphics"],
            ]
        )
        arg = [
            "NAME:" + symbol_name,
            "ModTime:=",
            1591858265,
            "Library:=",
            "",
            "ModSinceLib:=",
            False,
            "LibLocation:=",
            "Project",
            "HighestLevel:=",
            1,
            "Normalize:=",
            False,
            "InitialLevels:=",
            [0, 1],
        ]
        oDefinitionEditor = self._app._oproject.SetActiveDefinitionEditor("SymbolEditor", symbol_name)
        id = 2
        oDefinitionEditor.CreateRectangle(
            [
                "NAME:RectData",
                "X1:=",
                x1,
                "Y1:=",
                y1,
                "X2:=",
                x2,
                "Y2:=",
                y2,
                "LineWidth:=",
                0,
                "BorderColor:=",
                0,
                "Fill:=",
                0,
                "Color:=",
                0,
                "Id:=",
                id,
            ],
            ["NAME:Attributes", "Page:=", 1],
        )
        i = 1
        id += 2
        r = numpins - (h * 2)
        for pin in pin_lists:
            oDefinitionEditor.CreatePin(
                ["NAME:PinData", "Name:=", pin, "Id:=", id],
                ["NAME:PinParams", "X:=", xp, "Y:=", yp, "Angle:=", angle, "Flip:=", False],
            )
            arg.append(
                [
                    "NAME:PinDef",
                    "Pin:=",
                    [pin, xp, yp, angle, "N", 0, 0.00254, False, 0, True, "", False, False, pin, True],
                ]
            )
            if i == (h + r):
                yp = 0.00254 * (h + 2)
                xp = 0.00762
                angle = math.pi
            else:
                yp -= 0.00254
            id += 2
            i += 1

        arg.append(
            [
                "NAME:Graphics",
                ["NAME:1", "Rect:=", [0, 0, 0, 0, (x1 + x2) / 2, (y1 + y2) / 2, x2 - x1, y1 - y2, 0, 0, 8192]],
            ]
        )
        self.o_symbol_manager.EditWithComps(symbol_name, arg, [])
        oDefinitionEditor.CloseEditor()
        return True

    @pyaedt_function_handler()
    def enable_use_instance_name(self, component_library="Resistors", component_name="RES_"):
        """Enable the use of the instance name.

        Parameters
        ----------
        component_library : str, optional
             Name of the component library. The default is ``"Resistors"``.
        component_name : str, optional
             Name of the component. The default is ``"RES_"``.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        References
        ----------

        >>> oComponentManager.GetData
        >>> oComponentManager.Edit
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
        _retry_ntimes(
            10,
            self.o_component_manager.Edit,
            name,
            ["Name:" + component_name, ["NAME:CosimDefinitions", nexxim, "DefaultCosim:=", "DefaultNetlist"]],
        )
        return True

    @pyaedt_function_handler()
    def refresh_all_ids(self):
        """Refresh all IDs and return the number of components.

        References
        ----------

        >>> oEditor.GetAllElements()"""
        obj = self.oeditor.GetAllElements()
        obj = [i for i in obj if "Wire" not in i[:4]]
        for el in obj:
            if not self.get_obj_id(el):
                name = el.split(";")
                if len(name) > 1:
                    o = CircuitComponent(self, tabname=self.tab_name)
                    o.name = name[0]
                    if len(name) == 2:
                        o.schematic_id = name[1]
                        objID = int(o.schematic_id)
                    else:
                        o.id = int(name[1])
                        o.schematic_id = name[2]
                        objID = o.id
                    self.components[objID] = o
        return len(self.components)

    @pyaedt_function_handler()
    def add_id_to_component(self, id):
        """Add an ID to a component.

        Parameters
        ----------
        id : int
            ID to assign the component.

        Returns
        -------
        int
            Number of components.

        """
        obj = _retry_ntimes(10, self.oeditor.GetAllElements)
        for el in obj:
            name = el.split(";")
            if len(name) > 1 and str(id) == name[1]:
                o = CircuitComponent(self, tabname=self.tab_name)
                o.name = name[0]
                if len(name) > 2:
                    o.id = int(name[1])
                    o.schematic_id = int(name[2])
                    objID = o.id
                else:
                    o.schematic_id = int(name[1])
                    objID = o.schematic_id
                self.components[objID] = o

        return len(self.components)

    @pyaedt_function_handler()
    def get_obj_id(self, objname):
        """Retrieve the ID of an object.

        Parameters
        ----------
        objname : str
            Name of the object.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.
        """
        for el in self.components:
            if self.components[el].name == objname:
                return el
        return None

    @pyaedt_function_handler()
    def get_pins(self, partid):
        """Retrieve one or more pins.

        Parameters
        ----------
        partid : int or str
            One or more IDs or names for the pins to retrieve.

        Returns
        -------
        type
            Pin with properties.

        References
        ----------

        >>> oEditor.GetComponentPins
        """
        if isinstance(partid, CircuitComponent):
            pins = _retry_ntimes(10, self.oeditor.GetComponentPins, partid.composed_name)
        elif isinstance(partid, str):
            pins = _retry_ntimes(10, self.oeditor.GetComponentPins, partid)
            # pins = self.oeditor.GetComponentPins(partid)
        else:
            pins = _retry_ntimes(10, self.oeditor.GetComponentPins, self.components[partid].composed_name)
            # pins = self.oeditor.GetComponentPins(self.components[partid].composed_name)
        return list(pins)

    @pyaedt_function_handler()
    def get_pin_location(self, partid, pinname):
        """Retrieve the location of a pin.

        Parameters
        ----------
        partid : int
            ID of the part.
        pinname :
            Name of the pin.

        Returns
        -------
        List
            List of axis values ``[x, y]``.

        References
        ----------

        >>> oEditor.GetComponentPinLocation
        """
        if isinstance(partid, str):
            x = _retry_ntimes(30, self.oeditor.GetComponentPinLocation, partid, pinname, True)
            y = _retry_ntimes(30, self.oeditor.GetComponentPinLocation, partid, pinname, False)
        else:
            x = _retry_ntimes(
                30, self.oeditor.GetComponentPinLocation, self.components[partid].composed_name, pinname, True
            )
            y = _retry_ntimes(
                30, self.oeditor.GetComponentPinLocation, self.components[partid].composed_name, pinname, False
            )
        return [x, y]

    @pyaedt_function_handler()
    def arg_with_dim(self, Value, sUnits=None):
        """Format an argument with dimensions.

        Parameters
        ----------
        Value : str

        sUnits :
            The default is ``None``.

        Returns
        -------
        type


        """
        if isinstance(Value, str):
            val = Value
        else:
            if sUnits is None:
                sUnits = self.model_units
            val = "{0}{1}".format(Value, sUnits)

        return val

    @pyaedt_function_handler()
    def create_line(self, points_array, color=0, line_width=0):
        """Draw a graphical line.

        Parameters
        ----------
        points_array : list
            A nested list of point coordinates. For example,
            ``[[x1, y1], [x2, y2], ...]``.
        color : string or 3 item list, optional
            Color or the line. The default is ``0``.
        line_width : float, optional
            Width of the line. The default is ``0``.
        Returns
        -------

        >>> oEditor.CreateLine
        """

        pointlist = [str(tuple(i)) for i in points_array]
        id = self.create_unique_id()
        return self.oeditor.CreateLine(
            ["NAME:LineData", "Points:=", pointlist, "LineWidth:=", line_width, "Color:=", color, "Id:=", id],
            ["NAME:Attributes", "Page:=", 1],
        )


class ComponentInfo(object):
    """Class that manage Circuit Catalog info."""

    def __init__(self, name, component_manager, file_name, component_library):
        self._component_manager = component_manager
        self.file_name = file_name
        self.name = name
        self.component_library = component_library
        self._props = None

    @property
    def props(self):
        """Retrieve the component properties."""
        if not self._props:
            self._props = load_keyword_in_aedt_file(self.file_name, self.name)
        return self._props

    @pyaedt_function_handler()
    def place(self, inst_name, location=[], angle=0, use_instance_id_netlist=False):
        """Create a component from a library.

        Parameters
        ----------
        inst_name : str, optional
            Name of the instance. The default is ``None.``
        location : list of float, optional
            Position on the X axis and Y axis.
        angle : optional
            Angle rotation in degrees. The default is ``0``.
        use_instance_id_netlist : bool, optional
            Whether to enable the instance ID in the net list.
            The default is ``False``.

        Returns
        -------
        :class:`pyaedt.modeler.Object3d.CircuitComponent`
            Circuit Component Object.

        References
        ----------

        >>> oEditor.CreateComponent
        """
        return self._component_manager.create_component(
            inst_name=inst_name,
            component_library=self.component_library,
            component_name=self.name,
            location=location,
            angle=angle,
            use_instance_id_netlist=use_instance_id_netlist,
        )


class ComponentCatalog(object):
    """Class that indexes Circuit Sys Catalog."""

    @pyaedt_function_handler()
    def __getitem__(self, compname):
        """Get component from name.

        Parameters
        ----------
        compname : str
            ID or name of the object.

        Returns
        -------
        :class:`pyaedt.modeler.PrimitivesCircuit.ComponentInfo`
            Circuit Component Info.

        """
        items = self.find_components("*" + compname)
        if items and len(items) == 1:
            return self.components[items[0]]
        elif len(items) > 1:
            self._component_manager._logger.warning("Multiple components found.")
            return None
        else:
            self._component_manager._logger.warning("Component not found.")
            return None

    def __init__(self, component_manager):
        self._component_manager = component_manager
        self._app = self._component_manager._app
        self.components = {}
        self._index_components()

    @pyaedt_function_handler()
    def _index_components(self, library_path=None):
        if library_path:
            sys_files = recursive_glob(library_path, "*.aclb")
            root = os.path.normpath(library_path).split(os.path.sep)[-1]
        else:
            sys_files = recursive_glob(os.path.join(self._app.syslib, self._component_manager.design_libray), "*.aclb")
            root = os.path.normpath(self._app.syslib).split(os.path.sep)[-1]
        for file in sys_files:
            comps1 = load_keyword_in_aedt_file(file, "DefInfo")
            comps2 = load_keyword_in_aedt_file(file, "CompInfo")
            comps = comps1.get("DefInfo", {})
            comps.update(comps2.get("CompInfo", {}))
            for compname, comp_value in comps.items():
                root_name, ext = os.path.splitext(os.path.normpath(file))
                full_path = root_name.split(os.path.sep)
                id = full_path.index(root) + 1
                if self._component_manager.design_libray in full_path[id:]:
                    id += 1
                comp_lib = "\\".join(full_path[id:]) + ":" + compname
                self.components[comp_lib] = ComponentInfo(
                    compname, self._component_manager, file, comp_lib.split(":")[0]
                )

    @pyaedt_function_handler()
    def find_components(self, filter_str="*"):
        """Find all components with given filter wildcards.

        Parameters
        ----------
        filter_str : str
            Filter String to search.

        Returns
        list
            List of matching component names.
        """
        c = []
        for el in list(self.components.keys()):
            if filter_string(el, filter_str):
                c.append(el)
        return c
