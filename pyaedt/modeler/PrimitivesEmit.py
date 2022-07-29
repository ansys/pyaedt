from collections import defaultdict

from ..generic.general_methods import pyaedt_function_handler


class EmitComponents(object):
    """EmitComponents class.

    This is the class for managing all EMIT components.
    """

    @property
    def oeditor(self):
        """Oeditor Module."""
        return self.modeler.oeditor

    @property
    def odesign(self):
        """ """
        return self._parent.odesign

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
        """Aedt Model Manager"""
        return self.modeler.o_model_manager

    @property
    def o_definition_manager(self):
        """Aedt Definition Manager.

        References
        ----------

        >>> oDefinitionManager = oProject.GetDefinitionManager()
        """
        return self._parent._oproject.GetDefinitionManager()

    @property
    def o_symbol_manager(self):
        """AEDT Simbol Manager.

        References
        ----------

        >>> oSymbolManager = oDefinitionManager.GetManager("Symbol")
        """
        return self._parent.o_symbol_manager

    @property
    def o_component_manager(self):
        """AEDT Component Manager.

        References
        ----------

        >>> oComponentManager = oDefinitionManager.GetManager("Component")
        """
        return self._parent.o_component_manager

    @property
    def design_type(self):
        """ """
        return self._parent.design_type

    @pyaedt_function_handler()
    def __getitem__(self, compname):
        """
        Parameters
        ----------
        compname : str
           Name of the component.

        Returns
        -------
        EmitComponent
            The Component or ``None`` if a component with the given name is not
            found.
        """
        if compname in self.components:
            return self.components[compname]

        return None

    def __len__(self):
        return len(self.components)

    def __iter__(self):
        return self.components.keys().__iter__()

    def __init__(self, parent, modeler):
        self._parent = parent
        self.modeler = modeler
        self._currentId = 0
        self.components = defaultdict(EmitComponent)
        pass

    @pyaedt_function_handler()
    def create_component(self, component_type, name=None, library=None):
        """Create a new component from a library.

        Parameters
        ----------
        component_type : str
            Type of component to create. For example, "Antenna"
        name : str, optional
            Name to assign to the new component. If ``None``, then an instance
            name is assigned automatically. The default is ``None.``
        library : str, optional
            Name of the component library. If ``None``, the syslib is used. The
            default is ``None``.

        Returns
        -------
        EmitComponent
            The newly created component.

        References
        ----------

        >>> oEditor.CreateComponent
        """
        # Pass an empty string to allow name to be automatically assigned.
        if name is None:
            name = ""
        # Pass an empty string to use syslib EMIT library.
        if library is None:
            library = ""
        new_comp_name = self.oeditor.CreateComponent(name, component_type, library)
        o = EmitComponent.create(self, new_comp_name)
        o.name = new_comp_name
        o_update = self.update_object_properties(o)
        self.components[new_comp_name] = o_update
        return o_update

    @pyaedt_function_handler()
    def refresh_all_ids(self):
        """Refresh all IDs and return the number of components."""
        all_comps = self.oeditor.GetAllComponents()
        for comp_name in all_comps:
            if not self.get_obj_id(comp_name):
                o = EmitComponent.create(self, comp_name)
                o_update = self.update_object_properties(o)
                self.components[comp_name] = o_update
        return len(self.components)

    @pyaedt_function_handler()
    def get_obj_id(self, object_name):
        """

        Parameters
        ----------
        object_name : str
            Name of the object.

        Returns
        -------
        EmitComponent
            The component when successful, None when failed.
        """
        for el in self.components:
            if self.components[el].name == object_name:
                return el
        return None

    @pyaedt_function_handler()
    def update_object_properties(self, o):
        """Update the properties of an EMIT component.

        Parameters
        ----------
        o :
            Object (component) to update.

        Returns
        -------
        type
            Object with properties.

        """
        o.update_property_tree()
        comp_type = o.root_prop_node.props["Type"]
        o._add_property("Type", comp_type)
        return o


class EmitComponent(object):
    """A component in the EMIT schematic."""

    # Dictionary of subclass types. Register each subclass types with
    # class decorator and use EmitComponent.create to create the correct
    # object type.
    subclasses = {}

    @classmethod
    def register_subclass(cls, root_node_type):
        def decorator(subclass):
            cls.subclasses[root_node_type] = subclass
            return subclass

        return decorator

    @classmethod
    def create(cls, components, component_name):
        nodes = components.odesign.GetComponentNodeNames(component_name)
        root_node = nodes[0]
        prop_list = components.odesign.GetComponentNodeProperties(component_name, root_node)
        props = dict(p.split("=") for p in prop_list)
        root_node_type = props["Type"]
        if root_node_type.endswith("Node"):
            root_node_type = root_node_type[: -len("Node")]
        if root_node_type not in cls.subclasses:
            return EmitComponent(components, component_name)
        return cls.subclasses[root_node_type](components, component_name)

    def __init__(self, components, component_name):
        self.name = component_name
        self.components = components
        self.oeditor = components.oeditor
        self.odesign = components.odesign
        self.root_prop_node = None

    @property
    def composed_name(self):
        """Component name. Needed for compatibility."""
        return self.name

    @pyaedt_function_handler()
    def move_and_connect_to(self, component):
        """Move and connect this component to another component.

        Parameters
        ----------
        component : EmitComponent or str
            The component or name of component to move this component to
            and connect. For example, "Radio1"

        Returns
        -------
        None

        """
        if isinstance(component, EmitComponent):
            self.oeditor.PlaceComponent(self.name, component.name)
        else:
            self.oeditor.PlaceComponent(self.name, component)

    @pyaedt_function_handler()
    def port_names(self):
        """Get the names of the component's ports.
        Returns
        -------
        List
            List of port names.

        References
        ----------

        >>> oEditor.GetComponentPorts
        """
        return self.oeditor.GetComponentPorts(self.name)

    @pyaedt_function_handler()
    def port_connection(self, port_name):
        """Get the name component and port connected to the given port.

        Parameters
        ----------
        port_name : str
            The name of the port to interrogate for connection information.

        Returns
        -------
        str
            Connected component name. Returns None if no connection at given
            port.
        str
            Port name on connected component. Returns None if no connection
            at given port.

        References
        ----------

        >>> oEditor.GetWireAtPort
        >>> oEditor.GetWireConnections
        """
        wire_name = self.oeditor.GetWireAtPort(self.name, port_name)
        wire_connections = self.oeditor.GetWireConnections(wire_name)
        # One end of the wire will be this componenent. The other end will be
        # the other component. Return component and port names for the other
        # end.
        for wc_comp_name, wc_port_name in wire_connections:
            if wc_comp_name != self.name:
                return wc_comp_name, wc_port_name
        return None, None

    @pyaedt_function_handler()
    def update_property_tree(self):
        """Update the nodes (property groups) for this component.

        Returns
        -------
        EmitComponentPropNode
            The root node of the updated property tree.

        References
        ----------

        >>> oDesign.GetComponentNodeNames
        """
        node_names = sorted(self.odesign.GetComponentNodeNames(self.name))
        root_node_name = node_names[0]
        nodes = {}
        for node_name in node_names:
            new_node = EmitComponentPropNode(self.oeditor, self.odesign, self, node_name)
            parent_name = node_name.rpartition("-*-")[0]
            if parent_name in nodes:
                parent_node = nodes[parent_name]
                parent_node.children.append(new_node)
                new_node.parent = parent_node
            nodes[node_name] = new_node
        self.root_prop_node = nodes[root_node_name]
        return self.root_prop_node

    @pyaedt_function_handler()
    def get_node_properties(self, node=None):
        """Return the properties of the given node (property group).

        Parameters
        ----------
        node : str
            The name of the node (property group) whose properties will
            be returned. If node is None, the root node properties will be
            returned. (Default value = None)

        Returns
        -------
        dict
            Dictionary of property names (keys) and property values.

        References
        ----------

        >>> oDesign.GetComponentNodeNames
        >>> oDesign.GetComponentNodeProperties
        """
        nodes = sorted(self.odesign.GetComponentNodeNames(self.name))
        root_node = nodes[0]
        node_name = root_node
        if node is not None:
            node_name = root_node + "-*-" + "-*-".join(node.split("/")[1:])
        props_list = self.odesign.GetComponentNodeProperties(self.name, node_name)
        props = dict(p.split("=") for p in props_list)
        return props

    @pyaedt_function_handler()
    def set_property(self, property_name, property_value):
        """Set part property

        Parameters
        ----------
        property_name :
            property name
        property_value :
            property value

        Returns
        -------
        bool

        References
        ----------

        >>> oEditor.ChangeProperty
        """
        if type(property_name) is list:
            for p, v in zip(property_name, property_value):
                v_prop = ["NAME:" + p, "Value:=", v]
                self.change_property(v_prop)
                self.__dict__[p] = v
        else:
            v_prop = ["NAME:" + property_name, "Value:=", property_value]
            self.change_property(v_prop)
            self.__dict__[property_name] = property_value
        return True

    @pyaedt_function_handler()
    def _add_property(self, property_name, property_value):
        """Add a property or update existing property value.

        Parameters
        ----------
        property_name : Name of property.

        property_value : Value to assign to property.


        Returns
        -------
        True.
        """
        self.__dict__[property_name] = property_value
        return True

    def get_prop_nodes(self, property_filter=None):
        """Get all property nodes that match a set of key,value pairs.

        Args:
            property_filter (dict, optional): Only return nodes with all
            the property name, value pairs of this dict. Defaults to ``None``
            which returns all nodes.

        Returns:
            list: All matching nodes (EmitComponentPropNode).
        """
        if property_filter == None:
            property_filter = {}

        filtered_nodes = []
        nodes_to_expand = [self.root_prop_node]
        while nodes_to_expand:
            node = nodes_to_expand.pop()
            nodes_to_expand.extend(node.children)
            # <= checks if subset; {} is subset of all dicts
            if property_filter.items() <= node.props.items():
                filtered_nodes.append(node)
        return filtered_nodes

    @pyaedt_function_handler()
    def get_connected_components(self):
        """Get all EMIT components that are connected (directly or indirectly) to this component.

        Args:
            None

        Returns:
            List containing all EMIT components that are connected to this component.
        """
        component_names = []
        to_search = [self.name]
        while to_search:
            cursor = self.components[to_search.pop()]
            ports = cursor.port_names()

            for port in ports:
                connection_name, _ = cursor.port_connection(port)
                if connection_name not in component_names and connection_name not in to_search:
                    to_search.append(connection_name)

            component_names.append(cursor.name)

        components = map(lambda component_name: self.components[component_name], component_names)
        return list(components)

    @pyaedt_function_handler()
    def get_type(self):
        """
        Args:

        Returns:
            Type property of self.
        """
        properties = self.get_node_properties()

        return properties["Type"]


@EmitComponent.register_subclass("Antenna")
class EmitAntennaComponent(EmitComponent):
    """An Antenna component in the EMIT schematic."""

    def __init__(self, components, component_name):
        super(EmitAntennaComponent, self).__init__(components, component_name)

    def get_pattern_filename(self):
        """Get the filename of the antenna pattern defining this antenna.
        Args:

        Returns:
            Filename of the antenna pattern.
        """
        properties = self.get_node_properties()
        return properties["Filename"]

    def get_orientation_rpy(self):
        """Get the RPY orientation of this antenna.

        Args:
            None

        Returns:
            Tuple containing the roll, pitch, and yaw values in degrees defining this orientation.
        """
        properties = self.get_node_properties()

        orientation_string = properties["Orientation"]
        orientation_type = properties["OrientationMode"]

        if orientation_string is None or orientation_type is None:
            return None

        if orientation_type != "rpyDeg":
            # Handle other orientations by fixing up `orientation_string`.
            print("Unhandled orientation type: " + orientation_type)
            return None

        # Build a tuple of the orientation values.
        parts = orientation_string.split()
        orientation = (float(parts[0]), float(parts[1]), float(parts[2]))

        return orientation

    def get_position(self):
        """Get the position of this antenna.

        Args:
            None

        Returns:
            Tuple containing the X, Y, and Z offset values in meters.

        """
        properties = self.get_node_properties()
        position_string = properties["Position"]

        if position_string is None:
            return None

        # Build a tuple of the position
        parts = position_string.split()
        position = (float(parts[0]), float(parts[1]), float(parts[2]))

        return position


@EmitComponent.register_subclass("Radio")
class EmitRadioComponent(EmitComponent):
    """A Radio component in the EMIT schematic."""

    def __init__(self, components, component_name):
        super(EmitRadioComponent, self).__init__(components, component_name)

    def bands(self):
        band_nodes = self.get_prop_nodes({"Type": "Band"})
        return band_nodes

    def band_start_frequency_hz(self, band_node):
        return float(band_node.props["StartFrequency"])

    def band_tx_power_dbm(self, band_node):
        for child in band_node.children:
            if child.props["Type"] == "TxSpectralProfNode":
                return float(child.props["FundamentalAmplitude"])

    def has_tx_channels(self):
        nodes = self.get_prop_nodes({"Type": "TxSpectralProfNode", "Enabled": "true"})
        return len(nodes) > 0

    def has_rx_channels(self):
        nodes = self.get_prop_nodes({"Type": "RxSusceptibilityProfNode", "Enabled": "true"})
        return len(nodes) > 0

    def get_connected_antennas(self):
        components = super().get_connected_components()
        antennas = filter(lambda component: component.get_node_properties()["Type"] == "AntennaNode", components)
        return list(antennas)


class EmitComponentPropNode(object):
    def __init__(self, editor, design, parent_component, node_name):
        self.oeditor = editor
        self.odesign = design
        self.parent_component = parent_component
        self.node_name = node_name
        self.node_name_as_list = node_name.split("-*-")
        self.children = []
        self.parent = None

    @property
    def props(self):
        prop_list = self.odesign.GetComponentNodeProperties(self.parent_component.name, self.node_name)
        props = dict(p.split("=") for p in prop_list)
        return props

    @property
    def enabled(self):
        return self.props["Enabled"] == "true"

    @pyaedt_function_handler()
    def _set_prop_value(self, props={}):
        comp_name = self.parent_component.name
        prop_list = ["NAME:properties"]
        for prop_name, value in props.items():
            prop_list.append("{}:=".format(prop_name))
            if type(value) is not str:
                raise TypeError("Value for key {} is not a string.".format(prop_name))
            prop_list.append(value)
        properties_to_set = [
            ["NAME:node", "fullname:=", self.node_name, prop_list],
            [],  # Property does not get set without this empty list
        ]
        nodes_to_delete = []  # No nodes to delete
        self.odesign.EditComponentNodes(comp_name, properties_to_set, nodes_to_delete)

    @enabled.setter
    def enabled(self, value):
        str_value = "true" if value else "false"
        self._set_prop_value({"Enabled": str_value})
