# -*- coding: utf-8 -*-
from __future__ import absolute_import

import math
from collections import OrderedDict

from pyaedt import _retry_ntimes
from pyaedt import pyaedt_function_handler
from pyaedt import settings
from pyaedt.application.Variables import decompose_variable_value
from pyaedt.generic.constants import AEDT_UNITS
from pyaedt.generic.constants import MILS2METER
from pyaedt.generic.general_methods import _arg2dict
from pyaedt.generic.general_methods import _dim_arg
from pyaedt.modeler.cad.elements3d import _dict2arg


class CircuitPins(object):
    """Class that manages circuit component pins."""

    def __init__(self, circuit_comp, pinname):
        self._circuit_comp = circuit_comp
        self.name = pinname
        self.m_Editor = circuit_comp.m_Editor

    @property
    def location(self):
        """Pin Position in [x,y] format.

        References
        ----------

        >>> oPadstackManager.GetComponentPinLocation
        """
        if "Port" in self._circuit_comp.composed_name:
            pos1 = _retry_ntimes(
                30,
                self.m_Editor.GetPropertyValue,
                "BaseElementTab",
                self._circuit_comp.composed_name,
                "Component Location",
            )
            if isinstance(pos1, str):
                pos1 = pos1.split(", ")
                pos1 = [float(i.strip()[:-3]) * 0.0000254 for i in pos1]
                if "GPort" in self._circuit_comp.composed_name:
                    pos1[1] += 0.00254
                return pos1
            return []
        return [
            _retry_ntimes(30, self.m_Editor.GetComponentPinLocation, self._circuit_comp.composed_name, self.name, True),
            _retry_ntimes(
                30, self.m_Editor.GetComponentPinLocation, self._circuit_comp.composed_name, self.name, False
            ),
        ]

    @property
    def net(self):
        """Get pin net."""
        if "PagePort@" in self.name:
            return self._circuit_comp.name.split("@")[1]
        for net in self._circuit_comp._circuit_components.nets:
            conns = self.m_Editor.GetNetConnections(net)
            for conn in conns:
                if conn.endswith(self.name) and (
                    ";{};".format(self._circuit_comp.id) in conn or ";{} ".format(self._circuit_comp.id) in conn
                ):
                    return net
        return ""

    @pyaedt_function_handler()
    def connect_to_component(self, component_pin, page_name=None):
        """Connect schematic components.

        Parameters
        ----------
        component_pin : :class:`pyaedt.modeler.PrimitivesNexxim.CircuitPins`
           Component Pin to attach
        name : str, optional
            page port name.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        References
        ----------

        >>> oPadstackManager.CreatePagePort
        """
        if not isinstance(component_pin, list):
            component_pin = [component_pin]
        comp_angle = self._circuit_comp.angle * math.pi / 180
        if len(self._circuit_comp.pins) == 2:
            comp_angle += math.pi / 2
        if page_name is None:
            page_name = "{}_{}".format(
                self._circuit_comp.composed_name.replace("CompInst@", "").replace(";", "_"), self.name
            )

        if "Port" in self._circuit_comp.composed_name:
            try:
                page_name = self._circuit_comp.name.split("@")[1].replace(";", "_")
            except:
                pass
        else:
            for cmp in component_pin:
                if "Port" in cmp._circuit_comp.composed_name:
                    try:
                        page_name = cmp._circuit_comp.name.split("@")[1].replace(";", "_")
                        break
                    except:
                        continue
        try:
            x_loc = AEDT_UNITS["Length"][decompose_variable_value(self._circuit_comp.location[0])[1]] * float(
                decompose_variable_value(self._circuit_comp.location[1])[0]
            )
        except:
            x_loc = float(self._circuit_comp.location[0])
        if self.location[0] < x_loc:
            angle = comp_angle
        else:
            angle = math.pi + comp_angle
        ret1 = self._circuit_comp._circuit_components.create_page_port(page_name, self.location, angle=angle)
        for cmp in component_pin:
            try:
                x_loc = AEDT_UNITS["Length"][decompose_variable_value(cmp._circuit_comp.location[0])[1]] * float(
                    decompose_variable_value(cmp._circuit_comp.location[0])[0]
                )
            except:
                x_loc = float(self._circuit_comp.location[0])
            comp_pin_angle = cmp._circuit_comp.angle * math.pi / 180
            if len(cmp._circuit_comp.pins) == 2:
                comp_pin_angle += math.pi / 2
            if cmp.location[0] < x_loc:
                angle = comp_pin_angle
            else:
                angle = math.pi + comp_pin_angle
            ret2 = self._circuit_comp._circuit_components.create_page_port(
                page_name, location=cmp.location, angle=angle
            )
        if ret1 and ret2:
            return True
        else:
            return False


class ComponentParameters(dict):
    def __setitem__(self, key, value):
        try:
            self._component.m_Editor.ChangeProperty(
                [
                    "NAME:AllTabs",
                    [
                        "NAME:" + self._tab,
                        ["NAME:PropServers", self._component.composed_name],
                        ["NAME:ChangedProps", ["NAME:" + key, "Value:=", str(value)]],
                    ],
                ]
            )
            dict.__setitem__(self, key, value)
        except:
            self._component._circuit_components.logger.warning("Property %s has not been edited.Check if readonly", key)

    def __init__(self, component, tab, *args, **kw):
        dict.__init__(self, *args, **kw)
        self._component = component
        self._tab = tab


class ModelParameters(object):
    def update(self):
        """Update the model properties.

        Returns
        -------
        bool
        """
        try:
            a = OrderedDict({})
            a[self.name] = self.props
            arg = ["NAME:" + self.name]
            _dict2arg(self.props, arg)
            self._component._circuit_components.o_model_manager.EditWithComps(self.name, arg, [])
            return True
        except:
            self._component._circuit_components.logger.warning("Failed to update model %s ", self.name)
            return False

    def __init__(self, component, name, props):
        self.props = props
        self._component = component
        self.name = name


class CircuitComponent(object):
    """Manages circuit components."""

    @property
    def composed_name(self):
        """Composed names."""
        if self.id:
            return self.name + ";" + str(self.id) + ";" + str(self.schematic_id)
        else:
            return self.name + ";" + str(self.schematic_id)

    def __init__(self, circuit_components, units="mm", tabname="PassedParameterTab", custom_editor=None):
        self.name = ""
        self._circuit_components = circuit_components
        if custom_editor:
            self.m_Editor = custom_editor
        else:
            self.m_Editor = self._circuit_components.oeditor
        self._modelName = None
        self.status = "Active"
        self.component = None
        self.id = 0
        self.refdes = ""
        self.schematic_id = 0
        self.levels = 0.1
        self._angle = None
        self._location = []
        self._mirror = None
        self.usesymbolcolor = True
        self.units = units
        self.tabname = tabname
        self.InstanceName = None
        self._pins = None
        self._parameters = {}
        self._component_info = {}
        self._model_data = {}

    @property
    def _property_data(self):
        """Property Data List."""
        try:
            return list(self._circuit_components.o_component_manager.GetData(self.name.split("@")[1]))
        except:
            return []

    @property
    def model_name(self):
        """Return Model Name if present.

        Returns
        -------
        str
        """
        if self._property_data and "ModelDefName:=" in self._property_data:
            return self._property_data[self._property_data.index("ModelDefName:=") + 1]
        return None

    @property
    def model_data(self):
        """Return the model data if the component has one.

        Returns
        -------
        :class:`pyaedt.modeler.Object3d.ModelParameters`
        """
        """Return the model data if the component has one.
        """
        if self._model_data:
            return self._model_data
        if self.model_name:
            _parameters = OrderedDict({})
            _arg2dict(list(self._circuit_components.o_model_manager.GetData(self.model_name)), _parameters)
            self._model_data = ModelParameters(self, self.model_name, _parameters[self.model_name])
        return self._model_data

    @property
    def parameters(self):
        """Circuit Parameters.

        References
        ----------

        >>> oEditor.GetProperties
        >>> oEditor.GetPropertyValue
        """
        if self._parameters:
            return self._parameters
        _parameters = {}
        if self._circuit_components._app.design_type == "Circuit Design":
            tab = "PassedParameterTab"
        elif self._circuit_components._app.design_type == "Maxwell Circuit":
            tab = "PassedParameterTab"
        else:
            tab = "Quantities"
        proparray = self.m_Editor.GetProperties(tab, self.composed_name)

        for j in proparray:
            propval = _retry_ntimes(10, self.m_Editor.GetPropertyValue, tab, self.composed_name, j)
            _parameters[j] = propval
        self._parameters = ComponentParameters(self, tab, _parameters)
        return self._parameters

    @property
    def component_info(self):
        """Component parameters.

        References
        ----------

        >>> oEditor.GetProperties
        >>> oEditor.GetPropertyValue
        """
        if self._component_info or self._circuit_components._app.design_type != "Circuit Design":
            return self._component_info
        _component_info = {}
        tab = "Component"
        proparray = self.m_Editor.GetProperties(tab, self.composed_name)

        for j in proparray:
            propval = _retry_ntimes(10, self.m_Editor.GetPropertyValue, tab, self.composed_name, j)
            _component_info[j] = propval
        self._component_info = ComponentParameters(self, tab, _component_info)
        return self._component_info

    @property
    def pins(self):
        """Pins of the component.

        Returns
        -------
        list of :class:`pyaedt.modeler.Object3d.CircuitPins`

        """
        if self._pins:
            return self._pins
        self._pins = []

        try:
            pins = _retry_ntimes(10, self.m_Editor.GetComponentPins, self.composed_name)

            if not pins:
                return []
            elif pins is True:
                self._pins.append(CircuitPins(self, self.composed_name))
                return self._pins
            for pin in pins:
                if self._circuit_components._app.design_type != "Twin Builder":
                    self._pins.append(CircuitPins(self, pin))
                elif pin not in list(self.parameters.keys()):
                    self._pins.append(CircuitPins(self, pin))
        except AttributeError:
            self._pins.append(CircuitPins(self, self.composed_name))
        return self._pins

    @property
    def location(self):
        """Get the part location.

        References
        ----------

        >>> oEditor.GetPropertyValue
        >>> oEditor.ChangeProperty
        """
        if self._location:
            return self._location
        try:
            loc = _retry_ntimes(
                10, self.m_Editor.GetPropertyValue, "BaseElementTab", self.composed_name, "Component Location"
            )
            self._location = [loc.split(",")[0].strip(), loc.split(",")[1].strip()]
        except:
            self._location = []
        return self._location

    @location.setter
    def location(self, location_xy):
        """Set the part location.

        Parameters
        ----------
        location_xy : list
            List of x and y coordinates. If float is provided, ``mils`` will be used.
        """
        decomposed = decompose_variable_value(location_xy[0])
        try:
            if decomposed[1] != "":
                x_location = round(AEDT_UNITS["Length"][decomposed[1]] * float(decomposed[0]) * MILS2METER, -2)
            else:
                x_location = round(float(decomposed[0]), -2)

            x_location = _dim_arg(x_location, "mil")

        except:
            x_location = location_xy[0]
        decomposed = decompose_variable_value(location_xy[1])
        try:
            if decomposed[1] != "":
                y_location = round(AEDT_UNITS["Length"][decomposed[1]] * float(decomposed[0]) * MILS2METER, -2)
            else:
                y_location = round(float(decomposed[0]), -2)
            y_location = _dim_arg(y_location, "mil")

        except:
            y_location = location_xy[1]
        vMaterial = ["NAME:Component Location", "X:=", x_location, "Y:=", y_location]
        self.change_property(vMaterial)
        self._location = [x_location, y_location]

    @property
    def angle(self):
        """Get the part angle.

        References
        ----------

        >>> oEditor.GetPropertyValue
        >>> oEditor.ChangeProperty
        """
        if self._angle is not None:
            return self._angle
        self._angle = 0.0
        try:
            self._angle = float(
                _retry_ntimes(
                    10, self.m_Editor.GetPropertyValue, "BaseElementTab", self.composed_name, "Component Angle"
                ).replace("°", "")
            )
        except:
            self._angle = 0.0
        return self._angle

    @angle.setter
    def angle(self, angle=None):
        """Set the part angle."""
        if not settings.use_grpc_api:
            if not angle:
                angle = str(self._angle) + "°"
            else:
                angle = _dim_arg(angle, "°")
            vMaterial = ["NAME:Component Angle", "Value:=", angle]
            self.change_property(vMaterial)
        else:
            self._circuit_components._app.logger.error(
                "Grpc doesn't support angle settings because special characters are not supported."
            )

    @property
    def mirror(self):
        """Get the part mirror.

        References
        ----------

        >>> oEditor.GetPropertyValue
        >>> oEditor.ChangeProperty
        """
        if self._mirror is not None:
            return self._mirror
        try:
            self._mirror = (
                _retry_ntimes(
                    10, self.m_Editor.GetPropertyValue, "BaseElementTab", self.composed_name, "Component Mirror"
                )
                == "true"
            )
        except:
            self._mirror = False
        return self._mirror

    @mirror.setter
    def mirror(self, mirror_value=True):
        """Mirror part.

        Parameters
        ----------
        mirror_value : bool
            Either to mirror the part. The default is ``True``.

        Returns
        -------

        """
        vMaterial = ["NAME:Component Mirror", "Value:=", mirror_value]
        self.change_property(vMaterial)

    @pyaedt_function_handler()
    def set_use_symbol_color(self, symbol_color=None):
        """Set symbol color usage.

        Parameters
        ----------
        symbol_color : bool, optional
            The default is ``None``.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        References
        ----------

        >>> oEditor.ChangeProperty
        """
        if not symbol_color:
            symbol_color = self.usesymbolcolor
        vMaterial = ["NAME:Use Symbol Color", "Value:=", symbol_color]
        self.change_property(vMaterial)
        return True

    @pyaedt_function_handler()
    def set_color(self, R=255, G=128, B=0):
        """Set symbol color.

        Parameters
        ----------
        R : int, optional
            Red color value. The default is ``255``.
        G : int, optional
            Green color value. The default is ``128``.
        B : int, optional
            Blue color value. The default is ``0``

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        References
        ----------

        >>> oEditor.ChangeProperty
        """
        vMaterial = ["NAME:Component Color", "R:=", R, "G:=", G, "B:=", B]
        self.change_property(vMaterial)
        return True

    @pyaedt_function_handler()
    def set_property(self, property_name, property_value):
        """Set a part property.

        Parameters
        ----------
        property_name : str
            Name of the property.
        property_value :
            Value for the property.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

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
        """Add a property.

        Parameters
        ----------
        property_name : str
            Name of the property.
        property_value :
            Value for the property.


        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        """
        self.__dict__[property_name] = property_value
        return True

    def change_property(self, vPropChange, names_list=None):
        """Modify a property.

        Parameters
        ----------
        vPropChange :

        names_list : list, optional
             The default is ``None``.

        Returns
        -------
        bool

        References
        ----------

        >>> oEditor.GetPropertyValue
        >>> oEditor.ChangeProperty
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
            vGeo3dlayout = ["NAME:" + tabname, vPropServers, vChangedProps]
            vOut = ["NAME:AllTabs", vGeo3dlayout]
            return _retry_ntimes(10, self.m_Editor.ChangeProperty, vOut)
        return False
