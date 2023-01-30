# -*- coding: utf-8 -*-
from __future__ import absolute_import

import math
from collections import OrderedDict

from pyaedt import _retry_ntimes
from pyaedt import pyaedt_function_handler
from pyaedt import settings
from pyaedt.application.Variables import decompose_variable_value
from pyaedt.generic.constants import AEDT_UNITS
from pyaedt.generic.general_methods import _arg2dict
from pyaedt.generic.general_methods import _dim_arg
from pyaedt.modeler.cad.elements3d import _dict2arg


class CircuitPins(object):
    """Manages circuit component pins."""

    def __init__(self, circuit_comp, pinname):
        self._circuit_comp = circuit_comp
        self.name = pinname
        self.m_Editor = circuit_comp.m_Editor

    @property
    def units(self):
        """Length units."""
        return self._circuit_comp.units

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
                pos1 = [round(i / AEDT_UNITS["Length"][self.units], 8) for i in pos1]
                return pos1
            return []
        return [
            round(
                _retry_ntimes(
                    30, self.m_Editor.GetComponentPinLocation, self._circuit_comp.composed_name, self.name, True
                )
                / AEDT_UNITS["Length"][self.units],
                8,
            ),
            round(
                _retry_ntimes(
                    30, self.m_Editor.GetComponentPinLocation, self._circuit_comp.composed_name, self.name, False
                )
                / AEDT_UNITS["Length"][self.units],
                8,
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

    @property
    def angle(self):
        """Pin angle."""
        props = list(self.m_Editor.GetComponentPinInfo(self._circuit_comp.composed_name, self.name))
        for i in props:
            if "Angle=" in i:
                return round(float(i[6:]))
        return 0.0

    def _is_inside_point(self, plist, pa, pb):
        for p in plist:
            if pa <= p <= pb or pa >= p >= pb:
                return True
        return False

    def _add_point(self, pins, points, deltax, deltay, target, orient=0):

        if (orient == 0 and not self._is_inside_point(pins, points[-1][1], target[1])) or (
            orient == 1 and not self._is_inside_point(pins, points[-1][0], target[0])
        ):
            points.append(target)
        elif orient == 0:
            points.append([deltax, points[-1][1]])
            points.append([deltax, deltay])
        else:
            points.append([points[-1][0], deltay])
            points.append([deltax, deltay])

    def _get_deltas(self, point, move_x=True, move_y=True, positive=True, units=1):
        if positive:
            delta = +units * 0.00254 / AEDT_UNITS["Length"][self._circuit_comp._circuit_components.schematic_units]
        else:
            delta = -units * 0.00254 / AEDT_UNITS["Length"][self._circuit_comp._circuit_components.schematic_units]
        if move_x:
            deltax = point[0] + delta
        else:
            deltax = point[0]
        if move_y:
            deltay = point[1] + delta
        else:
            deltay = point[1]
        return deltax, deltay

    @pyaedt_function_handler()
    def connect_to_component(self, component_pin, page_name=None, use_wire=False, clearance_units=1):
        """Connect schematic components.

        Parameters
        ----------
        component_pin : :class:`pyaedt.modeler.circuits.PrimitivesNexxim.CircuitPins`
           Component pin to attach.
        page_name : str, optional
            Page port name. The default value is ``None``, in which case
            a name is automatically generated.
        use_wire : bool, optional
            Whether to use wires or a page port to connect the pins.
            The default is ``False``, in which case a page port is used. Note
            that if wires are used but not well placed, shorts can result.
        clearance_units : int, optional
            Number of snap units (100mil each) around the object to overcome pins and wires.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        References
        ----------

        >>> oPadstackManager.CreatePagePort
        """
        tol = 1e-8
        if not isinstance(component_pin, list):
            component_pin = [component_pin]
        if use_wire:
            direction = (180 + self.angle + self._circuit_comp.angle) * math.pi / 180
            points = [self.location]
            cangles = [self._circuit_comp.angle]
            dir = 0.0 >= direction >= (math.pi)
            for cpin in component_pin:
                prev = [i for i in points[-1]]
                act = [i for i in cpin.location]
                pins_x = [i.location[0] for i in self._circuit_comp.pins if i.name != self.name]
                pins_x += [i.location[0] for i in cpin._circuit_comp.pins if i.name != cpin.name]
                pins_y = [i.location[1] for i in self._circuit_comp.pins if i.name != self.name]
                pins_y += [i.location[1] for i in cpin._circuit_comp.pins if i.name != cpin.name]

                if abs(points[-1][0] - cpin.location[0]) < tol:
                    dx = round((prev[0] + act[0]) / 2, -2)

                    deltax, deltay = self._get_deltas(
                        [dx, prev[1]], move_y=False, positive=not dir, units=clearance_units
                    )

                    self._add_point(pins_y, points, deltax, deltay, act)
                    if points[-1][0] != act[0] and points[-1][1] != act[1]:
                        points.append([points[-1][0], act[1]])
                        points.append(act)

                    if points[-1][0] != act[0] or points[-1][1] != act[1]:
                        points.append(act)

                elif abs(points[-1][1] - cpin.location[1]) < tol:
                    dy = round((prev[1] + act[1]) / 2, -2)

                    deltax, deltay = self._get_deltas(
                        [prev[0], dy], move_x=False, positive=not dir, units=clearance_units
                    )

                    self._add_point(pins_x, points, deltax, deltay, act, 1)
                    if points[-1][0] != act[0] and points[-1][1] != act[1]:
                        points.append([act[0], points[-1][1]])
                        points.append(act)
                    if points[-1][0] != act[0] or points[-1][1] != act[1]:
                        points.append(act)

                elif cangles[-1] in [0.0, 180.0]:
                    dx = round((prev[0] + act[0]) / 2, -2)
                    p2 = act[1]
                    deltax, deltay = self._get_deltas(
                        [prev[0], p2], move_x=False, positive=True if p2 - prev[1] > 0 else False, units=clearance_units
                    )
                    self._add_point(
                        pins_y,
                        points,
                        deltax,
                        deltay,
                        [prev[0], p2],
                    )
                    p2 = points[-1][1]

                    deltax, deltay = self._get_deltas(
                        [dx, p2], move_y=False, positive=True if dx - prev[0] > 0 else False, units=clearance_units
                    )
                    self._add_point(pins_x, points, deltax, deltay, [dx, p2], 1)
                    if points[-1][0] != dx:
                        dx = points[-1][0]
                    deltax, deltay = self._get_deltas(
                        act, move_y=False, positive=True if act[0] - dx > 0 else False, units=clearance_units
                    )
                    if p2 == act[1]:
                        self._add_point(pins_x, points, deltax, deltay, [act[0], p2], 1)
                    else:
                        points.append([act[0], p2])
                    if points[-1][0] != act[0] or points[-1][1] != act[1]:
                        points.append(act)

                else:

                    dy = round((prev[1] + act[1]) / 2, -2)
                    p1 = act[0]

                    deltax, deltay = self._get_deltas(
                        [p1, prev[1]], move_y=False, positive=True if p1 - prev[0] > 0 else False, units=clearance_units
                    )
                    self._add_point(pins_y, points, deltax, deltay, [p1, prev[1]], 1)
                    p1 = points[-1][0]

                    deltax, deltay = self._get_deltas(
                        [p1, dy], move_x=False, positive=True if dy - prev[1] > 0 else False, units=clearance_units
                    )
                    self._add_point(pins_x, points, deltax, deltay, [act[0], dy], 1)
                    if points[-1][1] != dy:
                        dy = points[-1][0]
                    deltax, deltay = self._get_deltas(
                        act, move_x=False, positive=True if act[1] - dy > 0 else False, units=clearance_units
                    )
                    if p1 == act[0]:
                        self._add_point(pins_x, points, deltax, deltay, [p1, act[1]], 1)
                    else:
                        points.append([p1, act[1]])
                    if points[-1][0] != act[0] or points[-1][1] != act[1]:
                        points.append(act)

                cangles.append(cpin._circuit_comp.angle)
            self._circuit_comp._circuit_components.create_wire(points)
            return True
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

    def __init__(self, circuit_components, tabname="PassedParameterTab", custom_editor=None):
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
        self.tabname = tabname
        self.InstanceName = None
        self._pins = None
        self._parameters = {}
        self._component_info = {}
        self._model_data = {}

    @property
    def units(self):
        """Length units."""
        return self._circuit_components.schematic_units

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
        try:
            proparray = self.m_Editor.GetProperties(tab, self.composed_name)
        except:
            proparray = []

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
    def bounding_box(self):
        """Component bounding box."""
        comp_info = self.m_Editor.GetComponentInfo(self.composed_name)
        if not comp_info:
            if len(self.pins) == 1:
                return [
                    self.pins[0].location[0] - 0.00254 / AEDT_UNITS["Length"][self._circuit_components.schematic_units],
                    self.pins[0].location[-1]
                    + 0.00254 / AEDT_UNITS["Length"][self._circuit_components.schematic_units],
                    self.pins[0].location[0] + 0.00254 / AEDT_UNITS["Length"][self._circuit_components.schematic_units],
                    self.pins[0].location[1] + 0.00254 / AEDT_UNITS["Length"][self._circuit_components.schematic_units],
                ]
            return [0, 0, 0, 0]
        i = 0
        for cp in comp_info:
            if "BBoxLLx" in cp:
                break
            i += 1
        bounding_box = [
            float(comp_info[i][8:]),
            float(comp_info[i + 1][8:]),
            float(comp_info[i + 2][8:]),
            float(comp_info[i + 3][8:]),
        ]
        return [i / AEDT_UNITS["Length"][self._circuit_components.schematic_units] for i in bounding_box]

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
        self._location = []
        try:
            loc = _retry_ntimes(
                10, self.m_Editor.GetPropertyValue, "BaseElementTab", self.composed_name, "Component Location"
            )
            loc = [loc.split(",")[0].strip(), loc.split(",")[1].strip()]
            loc = [decompose_variable_value(i) for i in loc]

            self._location = [
                round(i[0] * AEDT_UNITS["Length"][i[1]] / AEDT_UNITS["Length"][self.units], 10) for i in loc
            ]
        except:
            self._location = []
        return self._location

    @location.setter
    def location(self, location_xy):
        """Set the part location.

        Parameters
        ----------
        location_xy : list
            List of x and y coordinates. If float values are provided, the default units are used.
        """
        x, y = [
            int(i / AEDT_UNITS["Length"]["mil"]) for i in self._circuit_components._convert_point_to_meter(location_xy)
        ]
        x_location = _dim_arg(x, "mil")
        y_location = _dim_arg(y, "mil")

        vMaterial = ["NAME:Component Location", "X:=", x_location, "Y:=", y_location]
        self.change_property(vMaterial)

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

    @pyaedt_function_handler()
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
        if vPropChange[0][5:] in _retry_ntimes(10, self.m_Editor.GetProperties, self.tabname, self.composed_name):
            tabname = self.tabname
        elif vPropChange[0][5:] in _retry_ntimes(
            10, self.m_Editor.GetProperties, "PassedParameterTab", self.composed_name
        ):
            tabname = "PassedParameterTab"
        elif vPropChange[0][5:] in _retry_ntimes(10, self.m_Editor.GetProperties, "BaseElementTab", self.composed_name):
            tabname = "BaseElementTab"
        if tabname:
            vGeo3dlayout = ["NAME:" + tabname, vPropServers, vChangedProps]
            vOut = ["NAME:AllTabs", vGeo3dlayout]
            if "NAME:Component Location" in str(vChangedProps) and "PagePort" not in self.composed_name:
                _retry_ntimes(10, self.m_Editor.ChangeProperty, vOut)
            return _retry_ntimes(10, self.m_Editor.ChangeProperty, vOut)
        return False
