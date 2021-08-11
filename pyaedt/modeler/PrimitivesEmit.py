import random
from collections import defaultdict

from ..generic.general_methods import aedt_exception_handler, retry_ntimes

class EmitComponents(object):
    """EmitComponents class. 
    
     This is the class for managing all EMIT components.
     """

    @property
    def oeditor(self):
        """ """
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
    def __getitem__(self, compname):
        """
        Parameters
        ----------
        partname : str
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

    @aedt_exception_handler
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

        """
        # Pass an empty string to allow name to be automatically assigned.
        if name is None:
            name = ""
        # Pass an emptry string to use syslib EMIT library.
        if library is None:
            library = ""
        new_comp_name = self.oeditor.CreateComponent(name, component_type, library)
        o = EmitComponent(self.oeditor, self.odesign)
        o.name = new_comp_name
        o_update = self.update_object_properties(o)
        self.components[new_comp_name] = o_update
        return o_update

    def _get_node_props(self, comp_name, node_name):
        prop_list = self.odesign.GetComponentNodeProperties(comp_name, node_name)
        props = dict(p.split('=') for p in prop_list)
        return props
    def _get_node_type(self, comp_name, node_name):
        return self._get_node_props(comp_name, node_name)['Type']
    def _get_comp_type(self, comp_name):
        nodes = self.odesign.GetComponentNodeNames(comp_name)
        root_node = nodes[0]
        return self._get_node_type(comp_name, root_node)


    @aedt_exception_handler
    def refresh_all_ids(self):
        """Refresh all IDs and return the number of components."""
        all_comps = self.oeditor.GetAllComponents()
        for comp_name in all_comps:
            if not self.get_obj_id(comp_name):
                comp_type = self._get_comp_type(comp_name)
                if comp_type == 'RadioNode':
                    o = EmitRadioComponent(self.oeditor, self.odesign)
                else:
                    o = EmitComponent(self.oeditor, self.odesign)
                o.name = comp_name
                o_update = self.update_object_properties(o)
                self.components[comp_name] = o_update
        return len(self.components)


    @aedt_exception_handler
    def get_obj_id(self, objname):
        """

        Parameters
        ----------
        objname : str
            Name of the object.

        Returns
        -------
        EmitComponent
            The component when successful, None when failed.
        """
        for el in self.components:
            if self.components[el].name == objname:
                return el
        return None

    @aedt_exception_handler
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
        comp_type = o.root_prop_node.props['Type']
        o._add_property('Type', comp_type)
        return o

    @aedt_exception_handler
    def get_pins(self, partid):
        """

        Parameters
        ----------
        partid : int or str
            ID or full name of the component.

        Returns
        -------
        type
            Object with properties.

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
            ID of the component.
        pinname :
            Name of the pin.

        Returns
        -------
        List
            List of axis values ``[x, y]``.

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
        Value : str
            
        sUnits :
            The default is ``None``.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        """
        if type(Value) is str:
            val = Value
        else:
            if sUnits is None:
                sUnits = self.model_units
            val = "{0}{1}".format(Value, sUnits)

        return val


class EmitComponent(object):
    """A component in the EMIT schematic."""

    @property
    def composed_name(self):
        """ """
        if self.id:
            return self.name + ";" +str(self.id) + ";" + str(self.schematic_id)
        else:
            return self.name + ";" + str(self.schematic_id)

    def __init__(self, editor=None, design=None, units="mm", tabname="PassedParameterTab"):
        self.name = None
        self.oeditor = editor
        self.odesign = design
        self.root_prop_node = None
        self.modelName = None
        self.status = "Active"
        self.id = 0
        self.refdes = ""
        self.schematic_id = 0
        self.levels = 0.1
        self.angle = 0
        self.x_location = "0mil"
        self.y_location = "0mil"
        self.mirror = False
        self.usesymbolcolor = True
        self.units = "mm"
        self.tabname = tabname

    @aedt_exception_handler
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

    @aedt_exception_handler
    def port_names(self):
        """Get the names of the component's ports.
        Returns
        -------
        List
            List of port names.
        """
        return self.oeditor.GetComponentPorts(self.name)

    @aedt_exception_handler
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

    @aedt_exception_handler
    def update_property_tree(self):
        """Update the nodes (property groups) for this component.

        Returns
        -------
        EmitComponentPropNode
            The root node of the updated property tree.
        """
        node_names = sorted(self.odesign.GetComponentNodeNames(self.name))
        root_node_name = node_names[0]
        nodes = {}
        for node_name in node_names:
            new_node = EmitComponentPropNode(self.oeditor, self.odesign, self, node_name)
            parent_name = node_name.rpartition('-*-')[0]
            if parent_name in nodes:
                parent_node = nodes[parent_name]
                parent_node.children.append(new_node)
                new_node.parent = parent_node
            nodes[node_name] = new_node
        self.root_prop_node = nodes[root_node_name]
        return self.root_prop_node

    @aedt_exception_handler
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

        """
        nodes = sorted(self.odesign.GetComponentNodeNames(self.name))
        root_node = nodes[0]
        node_name = root_node
        if node is not None:
            node_name = root_node + '-*-' + '-*-'.join(node.split('/')[1:])
        props_list = self.odesign.GetComponentNodeProperties(self.name, node_name)
        props = dict(p.split('=') for p in props_list)
        return props

    @aedt_exception_handler
    def set_location(self, x_location=None, y_location=None):
        """Set part location

        Parameters
        ----------
        x_location :
            x location (Default value = None)
        y_location :
            y location (Default value = None)

        Returns
        -------

        """
        if x_location is None:
            x_location = self.x_location
        else:
            x_location = _dim_arg(x_location,"mil")
        if y_location is None:
            y_location = self.y_location
        else:
            y_location = _dim_arg(y_location,"mil")

        vMaterial = ["NAME:Component Location", "X:=", x_location,"Y:=", y_location]
        self.change_property(vMaterial)

    @aedt_exception_handler
    def set_mirror(self, mirror_value=None):
        """Mirror part

        Parameters
        ----------
        mirror_value :
            mirror angle (Default value = None)

        Returns
        -------

        """
        if not mirror_value:
            mirror_value = self.mirror
        vMaterial = ["NAME:Component Mirror", "Value:=", mirror_value]
        self.change_property(vMaterial)

    @aedt_exception_handler
    def set_use_symbol_color(self, symbol_color=None):
        """Set Symbol Color usage

        Parameters
        ----------
        symbol_color :
            Bool (Default value = None)

        Returns
        -------

        """
        if not symbol_color:
            symbol_color = self.usesymbolcolor
        vMaterial = ["NAME:Use Symbol Color", "Value:=", symbol_color]
        self.change_property(vMaterial)
        return True


    @aedt_exception_handler
    def set_color(self, R=255, G=128, B=0):
        """Set Symbol Color

        Parameters
        ----------
        R :
            red (Default value = 255)
        G :
            Green (Default value = 128)
        B :
            Blue (Default value = 0)

        Returns
        -------

        """
        self.set_mirror(True)
        vMaterial = ["NAME:Component Color", "R:=", R,"G:=", G, "B:=", B]
        self.change_property(vMaterial)
        return True

    @aedt_exception_handler
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

        """
        if type(property_name) is list:
            for p,v in zip(property_name, property_value):
                v_prop = ["NAME:"+p, "Value:=", v]
                self.change_property(v_prop)
                self.__dict__[p] = v
        else:
            v_prop = ["NAME:" + property_name, "Value:=", property_value]
            self.change_property(v_prop)
            self.__dict__[property_name] = property_value
        return True

    @aedt_exception_handler
    def _add_property(self, property_name, property_value):
        """

        Parameters
        ----------
        property_name :

        property_value :


        Returns
        -------

        """
        self.__dict__[property_name] = property_value
        return True

    def change_property(self, vPropChange, names_list=None):
        """

        Parameters
        ----------
        vPropChange :

        names_list :
             (Default value = None)

        Returns
        -------

        """
        vChangedProps = ["NAME:ChangedProps", vPropChange]
        if names_list:
            vPropServers = ["NAME:PropServers"]
            for el in names_list:
                vPropServers.append(el)
        else:
            vPropServers = ["NAME:PropServers", self.composed_name]
        tabname = None
        if vPropChange[0][5:] in list(self.m_Editor.GetProperties(self.tabname, self.composed_name)):
            tabname = self.tabname
        elif vPropChange[0][5:] in list(self.m_Editor.GetProperties("PassedParameterTab", self.composed_name)):
            tabname = "PassedParameterTab"
        elif vPropChange[0][5:] in list(self.m_Editor.GetProperties("BaseElementTab", self.composed_name)):
            tabname = "BaseElementTab"
        if tabname:
            vGeo3dlayout = ["NAME:"+tabname, vPropServers, vChangedProps]
            vOut = ["NAME:AllTabs", vGeo3dlayout]
            return retry_ntimes(10, self.m_Editor.ChangeProperty, vOut)
        return False

    def get_prop_nodes(self, property_filter={}):
        """Get all property nodes that match a set of key,value pairs.

        Args:
            property_filter (dict, optional): Only return nodes with all
            the property name,value pairs of this dict. Defaults to {} 
            which returns all nodes.

        Returns:
            list: All matching nodes (EmitComponentPropNode).
        """
        filtered_nodes = []
        nodes_to_expand = [self.root_prop_node]
        while nodes_to_expand:
            node = nodes_to_expand.pop()
            nodes_to_expand.extend(node.children)
            num_missing_props = sum(1 for prop, value in property_filter.items() if prop not in node.props or node.props[prop] != value)
            # <= checks if subset; {} is subset of all dicts
            if property_filter.items() <= node.props.items(): 
                filtered_nodes.append(node)
        return filtered_nodes

class EmitRadioComponent(EmitComponent):
    """A Radio component in the EMIT schematic."""

    def __init__(self, editor=None, design=None, units="mm", tabname="PassedParameterTab"):
        super(EmitRadioComponent, self) .__init__(editor, design, units, tabname)

    def bands(self):
        band_nodes = self.get_prop_nodes({'Type':'Band'})
        return band_nodes

    def band_start_frequency_hz(self, band_node):
        return float(band_node.props['StartFrequency'])

    def band_tx_power_dbm(self, band_node):
        for child in band_node.children:
            if child.props['Type'] == 'TxSpectralProfNode':
                return float(child.props['FundamentalAmplitude'])


    def has_tx_channels(self):
        nodes = self.get_prop_nodes({'Type':'TxSpectralProfNode', 'Enabled':'true'})
        return len(nodes) > 0

    def has_rx_channels(self):
        nodes = self.get_prop_nodes({'Type':'RxSusceptibilityProfNode', 'Enabled':'true'})
        return len(nodes) > 0

class EmitComponentPropNode(object):
    def __init__(self, editor, design, parent_component, node_name):
        self.oeditor = editor
        self.odesign = design
        self.parent_component = parent_component
        self.node_name = node_name
        self.node_name_as_list = node_name.split('-*-')
        self.children = []
        self.parent = None

    @property
    def props(self):
        prop_list = self.odesign.GetComponentNodeProperties(self.parent_component.name, self.node_name)
        props = dict(p.split('=') for p in prop_list)
        return props

    @property
    def enabled(self):
        return self.props['Enabled']=='true'

    @aedt_exception_handler
    def _set_prop_value(self, props={}):
        comp_name = self.parent_component.name
        prop_list = ["NAME:properties"]
        for prop_name, value in props.items():
            prop_list.append('{}:='.format(prop_name))
            if type(value) is not str:
                raise TypeError('Value for key {} is not a string.'.format(prop_name))
            prop_list.append(value)
        properties_to_set = [
                [
                    "NAME:node", 
                    "fullname:=", self.node_name,
                    prop_list
                ],
                [] # Property does not get set without this empty list
            ]
        nodes_to_delete = [] # No nodes to delete
        self.odesign.EditComponentNodes(comp_name, properties_to_set, nodes_to_delete)

    @enabled.setter
    def enabled(self, value):
        str_value = 'true' if value else 'false'
        self._set_prop_value({'Enabled':str_value})
        

