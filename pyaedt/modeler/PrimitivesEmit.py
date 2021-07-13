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
        type
            Component ID.
        str
            Component name.

        """
        # Pass an empty string to allow name to be automatically assigned.
        if name is None:
            name = ""
        # Pass an emptry string to use syslib EMIT library.
        if library is None:
            library = ""
        new_comp_name = self.oeditor.CreateComponent(name, component_type, library)
        o = EmitComponent(self.oeditor)
        o.name = new_comp_name
        o_update = self.update_object_properties(o)
        self.components[new_comp_name] = o_update
        return new_comp_name

    @aedt_exception_handler
    def refresh_all_ids(self):
        """Refresh all IDs and return the number of components."""
        obj = self.oeditor.GetAllComponents()
        for el in obj:
            if not self.get_obj_id(el):
                name = el.split(";")
                o = EmitComponent(self.oeditor, tabname=self.tab_name)
                o.name = name[0]
                o.id = int(name[1])
                o.schematic_id = name[2]
                o_update = self.update_object_properties(o)
                objID = o.id
                self.components[objID] = o_update
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
        bool
            ``True`` when successful, ``False`` when failed.
        """
        for el in self.components:
            if self.components[el].name == objname:
                return el
        return None

    @aedt_exception_handler
    def update_object_properties(self, o):
        """Update the properties of an object.

        Parameters
        ----------
        o :
            Object to update.

        Returns
        -------
        type
            Object with properties.

        """
        # TODO: Handle EMIT component properties here?
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

    def __init__(self, editor=None, units="mm", tabname="PassedParameterTab"):
        self.name = None
        self.m_Editor = editor
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
    def set_angle(self, angle=None):
        """Set part angle

        Parameters
        ----------
        angle :
            angle (Default value = None)

        Returns
        -------

        """
        if not angle:
            angle = str(self.angle) +"°"
        else:
            angle = str(angle) +"°"
        vMaterial = ["NAME:Component Angle", "Value:=", angle]
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