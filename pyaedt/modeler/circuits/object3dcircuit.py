# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 - 2024 ANSYS, Inc. and/or its affiliates.
# SPDX-License-Identifier: MIT
#
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

from __future__ import absolute_import

from collections import OrderedDict
import math
import time

from pyaedt.application.Variables import decompose_variable_value
from pyaedt.generic.constants import AEDT_UNITS
from pyaedt.generic.general_methods import _arg2dict
from pyaedt.generic.general_methods import _dim_arg
from pyaedt.generic.general_methods import pyaedt_function_handler
from pyaedt.modeler.cad.elements3d import _dict2arg
from pyaedt.modeler.geometry_operators import GeometryOperators as go


class CircuitPins(object):
    """Manages circuit component pins."""

    def __init__(self, circuit_comp, pinname):
        self._circuit_comp = circuit_comp
        self.name = pinname
        self._oeditor = circuit_comp._oeditor

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
            pos1 = self._oeditor.GetPropertyValue(
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
                self._oeditor.GetComponentPinLocation(self._circuit_comp.composed_name, self.name, True)
                / AEDT_UNITS["Length"][self.units],
                8,
            ),
            round(
                self._oeditor.GetComponentPinLocation(self._circuit_comp.composed_name, self.name, False)
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
            conns = self._oeditor.GetNetConnections(net)
            for conn in conns:
                if conn.endswith(self.name) and (
                    ";{};".format(self._circuit_comp.id) in conn or ";{} ".format(self._circuit_comp.id) in conn
                ):
                    return net
        return ""

    @property
    def angle(self):
        """Pin angle."""
        props = list(self._oeditor.GetComponentPinInfo(self._circuit_comp.composed_name, self.name))
        for i in props:
            if "Angle=" in i:
                return round(float(i[6:]))
        return 0.0

    @staticmethod
    def _is_inside_point(plist, pa, pb):
        for p in plist:
            if pa < p < pb or pa > p > pb:
                return True
        return False

    def _add_point(
        self,
        pins,
        points,
        delta,
        target,
    ):
        inside = False
        pa = points[-1] + [0]
        pb = target + [0]
        for pin in pins:
            if go.is_between_points(pin, pa, pb):
                inside = True
        if not inside:
            points.append(target)
        elif pa[0] == pb[0]:
            deltax = target[0] + delta
            points.append([deltax, points[-1][1]])
            points.append([deltax, target[1]])
        else:
            deltay = target[1] + delta
            points.append([points[-1][0], deltay])
            points.append([target[0], deltay])

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

    @pyaedt_function_handler(component_pin="assignment")
    def connect_to_component(
        self, assignment, page_name=None, use_wire=False, wire_name="", clearance_units=1, page_port_angle=None
    ):
        """Connect schematic components.

        Parameters
        ----------
        assignment : :class:`pyaedt.modeler.circuits.PrimitivesNexxim.CircuitPins`
           Component pin to attach.
        page_name : str, optional
            Page port name. The default value is ``None``, in which case
            a name is automatically generated.
        use_wire : bool, optional
            Whether to use wires or a page port to connect the pins.
            The default is ``False``, in which case a page port is used. Note
            that if wires are used but not well placed, shorts can result.
        wire_name : str, optional
            Wire name used only when ``user_wire=True``. The default is ``""``.
        clearance_units : int, optional
            Number of snap units (100mil each) around the object to overcome pins and wires.
        page_port_angle : int, optional
            Page port angle on the source pin. The default is ``None``, in which case
            the angle is automatically computed.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        References
        ----------

        >>> oPadstackManager.CreatePagePort
        """
        tol = 1e-8
        if not isinstance(assignment, list):
            assignment = [assignment]
        if use_wire:
            direction = (180 + self.angle + self._circuit_comp.angle) * math.pi / 180
            points = [self.location]
            cangles = [self._circuit_comp.angle]
            negative = 0.0 >= direction >= (math.pi)
            for cpin in assignment:
                prev = [i for i in points[-1]]
                act = [i for i in cpin.location]
                pins_x = [i.location[0] for i in self._circuit_comp.pins if i.name != self.name]
                pins_x += [i.location[0] for i in cpin._circuit_comp.pins if i.name != cpin.name]
                pins_y = [i.location[1] for i in self._circuit_comp.pins if i.name != self.name]
                pins_y += [i.location[1] for i in cpin._circuit_comp.pins if i.name != cpin.name]
                pins = [[i, j, 0] for i, j in zip(pins_x, pins_y)]
                delta, _ = self._get_deltas([0, 0], move_y=False, positive=not negative, units=clearance_units)
                if abs(points[-1][0] - cpin.location[0]) < tol:
                    dx = round((prev[0] + act[0]) / 2, -2)

                    self._add_point(pins, points, delta, act)
                    if points[-1][0] != act[0] and points[-1][1] != act[1]:
                        points.append([points[-1][0], act[1]])
                        points.append(act)
                    if points[-1][0] != act[0] or points[-1][1] != act[1]:
                        points.append(act)

                elif abs(points[-1][1] - cpin.location[1]) < tol:
                    dy = round((prev[1] + act[1]) / 2, -2)
                    self._add_point(pins, points, delta, act)
                    if points[-1][0] != act[0] and points[-1][1] != act[1]:
                        points.append([act[0], points[-1][1]])
                        points.append(act)
                    if points[-1][0] != act[0] or points[-1][1] != act[1]:
                        points.append(act)

                elif cangles[-1] in [0.0, 180.0]:
                    dx = round((prev[0] + act[0]) / 2, -2)
                    p2 = act[1]

                    self._add_point(
                        pins,
                        points,
                        delta,
                        [prev[0], p2],
                    )
                    p2 = points[-1][1]

                    self._add_point(pins, points, delta, [dx, p2])
                    if points[-1][0] != dx:
                        dx = points[-1][0]

                    if p2 == act[1]:
                        self._add_point(pins, points, delta, [act[0], p2])
                    else:
                        points.append([act[0], p2])
                    if points[-1][0] != act[0] or points[-1][1] != act[1]:
                        points.append(act)

                else:
                    dy = round((prev[1] + act[1]) / 2, -2)
                    p1 = act[0]
                    self._add_point(pins, points, delta, [p1, prev[1]])
                    p1 = points[-1][0]

                    self._add_point(
                        pins,
                        points,
                        delta,
                        [act[0], dy],
                    )
                    if points[-1][1] != dy:
                        dy = points[-1][0]

                    if p1 == act[0]:
                        self._add_point(pins, points, delta, [p1, act[1]])
                    else:
                        points.append([p1, act[1]])
                    if points[-1][0] != act[0] or points[-1][1] != act[1]:
                        points.append(act)

                cangles.append(cpin._circuit_comp.angle)
            self._circuit_comp._circuit_components.create_wire(points, name=wire_name)
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
            except Exception:
                pass
        else:
            for cmp in assignment:
                if "Port" in cmp._circuit_comp.composed_name:
                    try:
                        page_name = cmp._circuit_comp.name.split("@")[1].replace(";", "_")
                        break
                    except Exception:
                        continue
        try:
            x_loc = AEDT_UNITS["Length"][decompose_variable_value(self._circuit_comp.location[0])[1]] * float(
                decompose_variable_value(self._circuit_comp.location[1])[0]
            )
        except Exception:
            x_loc = float(self._circuit_comp.location[0])
        if page_port_angle is not None:
            angle = page_port_angle * math.pi / 180
        elif self.location[0] < x_loc:
            angle = comp_angle
        else:
            angle = math.pi + comp_angle
        ret1 = self._circuit_comp._circuit_components.create_page_port(page_name, self.location, angle=angle)
        for cmp in assignment:
            try:
                x_loc = AEDT_UNITS["Length"][decompose_variable_value(cmp._circuit_comp.location[0])[1]] * float(
                    decompose_variable_value(cmp._circuit_comp.location[0])[0]
                )
            except Exception:
                x_loc = float(cmp._circuit_comp.location[0])
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
            return True, ret1, ret2
        else:
            return False


class ComponentParameters(dict):
    """Manages component parameters."""

    def __setitem__(self, key, value):
        if not isinstance(value, (int, float)):
            try:
                self._component._oeditor.ChangeProperty(
                    [
                        "NAME:AllTabs",
                        [
                            "NAME:" + self._tab,
                            ["NAME:PropServers", self._component.composed_name],
                            [
                                "NAME:ChangedProps",
                                ["NAME:" + key, "ButtonText:=", str(value), "ExtraText:=", str(value)],
                            ],
                        ],
                    ]
                )
                if (
                    self._component._oeditor.GetPropertyValue("PassedParameterTab", self._component.composed_name, key)
                    != value
                ):
                    try:
                        self._component._oeditor.SetPropertyValue(
                            self._tab, self._component.composed_name, key, str(value)
                        )
                        dict.__setitem__(self, key, value)
                    except Exception:
                        self._component._circuit_components.logger.warning(
                            "Property %s has not been edited.Check if readonly", key
                        )
                dict.__setitem__(self, key, value)
            except Exception:
                self._component._circuit_components.logger.warning(
                    "Property %s has not been edited. Check if read-only.", key
                )
        else:
            try:
                self._component._oeditor.SetPropertyValue(self._tab, self._component.composed_name, key, str(value))
                dict.__setitem__(self, key, value)
            except Exception:
                self._component._circuit_components.logger.warning(
                    "Property %s has not been edited.Check if readonly", key
                )

    def __init__(self, component, tab, *args, **kw):
        dict.__init__(self, *args, **kw)
        self._component = component
        self._tab = tab


class ModelParameters(object):
    """Manages model parameters."""

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
        except Exception:
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
            self._oeditor = custom_editor
        else:
            self._oeditor = self._circuit_components.oeditor
        self._modelName = None
        self.status = "Active"
        self.component = None
        self.id = 0
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

    @pyaedt_function_handler()
    def delete(self):
        """Delete the component.

        Returns
        -------
        bool
        """
        self._oeditor.Delete(["NAME:Selections", "Selections:=", [self.composed_name]])
        for k, v in self._circuit_components.components.items():
            if v.name == self.name:
                del self._circuit_components.components[k]
                break
        return True

    @property
    def refdes(self):
        """Reference designator."""
        try:
            return self._oeditor.GetPropertyValue("Component", self.composed_name, "RefDes")
        except Exception:
            return ""

    @property
    def units(self):
        """Length units."""
        return self._circuit_components.schematic_units

    @property
    def _property_data(self):
        """Property Data List."""
        try:
            return list(self._circuit_components.o_component_manager.GetData(self.name.split("@")[1]))
        except Exception:
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
        if self._circuit_components._app.design_type == "Circuit Design" or self.name in [
            "CompInst@FML_INIT",
            "CompInst@Measurement",
        ]:
            tabs = ["PassedParameterTab"]
        elif self._circuit_components._app.design_type == "Maxwell Circuit":
            tabs = ["PassedParameterTab"]
        else:
            tabs = ["Quantities", "PassedParameterTab"]
        proparray = {}
        for tab in tabs:
            try:
                proparray[tab] = self._oeditor.GetProperties(tab, self.composed_name)
            except Exception:
                proparray[tab] = []

        for tab, props in proparray.items():
            for j in props:
                propval = self._oeditor.GetPropertyValue(tab, self.composed_name, j)
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
        proparray = self._oeditor.GetProperties(tab, self.composed_name)

        for j in proparray:
            propval = self._oeditor.GetPropertyValue(tab, self.composed_name, j)
            _component_info[j] = propval
        self._component_info = ComponentParameters(self, tab, _component_info)
        return self._component_info

    @property
    def bounding_box(self):
        """Component bounding box."""
        comp_info = self._oeditor.GetComponentInfo(self.composed_name)
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
            pins = list(self._oeditor.GetComponentPins(self.composed_name))
            if "Port@" in self.composed_name and pins == []:
                self._pins.append(CircuitPins(self, self.composed_name))
                return self._pins
            elif not pins:
                return []
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
            loc = self._oeditor.GetPropertyValue("BaseElementTab", self.composed_name, "Component Location")
            loc = [loc.split(",")[0].strip(), loc.split(",")[1].strip()]
            loc = [decompose_variable_value(i) for i in loc]

            self._location = [
                round(i[0] * AEDT_UNITS["Length"][i[1]] / AEDT_UNITS["Length"][self.units], 10) for i in loc
            ]
        except Exception:
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
        comp_info = self._oeditor.GetComponentInfo(self.composed_name)
        self._angle = 0.0
        if comp_info:
            for info in comp_info:
                if "Angle=" in info:
                    self._angle = float(info[6:])
                    break
        else:
            self._angle = float(
                self._oeditor.GetPropertyValue("BaseElementTab", self.composed_name, "Component Angle").replace(
                    "deg", ""
                )
            )
        return self._angle

    @angle.setter
    def angle(self, angle=None):
        """Set the part angle."""
        from pyaedt.generic.settings import settings

        if isinstance(angle, (float, int)):
            angle = int(angle)
            if angle not in [0, 90, 180, 270]:  # pragma: no cover
                self._circuit_components._app.logger.error("Supported angle values are 0,90,180,270.")
        self._angle = 0 if angle is None else angle
        if settings.aedt_version > "2023.2":  # pragma: no cover
            angle = _dim_arg(self._angle, "deg")
            vMaterial = ["NAME:Component Angle", "Value:=", angle]
            self.change_property(vMaterial)
        elif not self._circuit_components._app.desktop_class.is_grpc_api:
            if not angle:
                angle = str(self._angle) + "°"
            else:
                angle = _dim_arg(angle, "°")
            vMaterial = ["NAME:Component Angle", "Value:=", angle]
            self.change_property(vMaterial)
        else:
            self._circuit_components._app.logger.warning(
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
                self._oeditor.GetPropertyValue("BaseElementTab", self.composed_name, "Component Mirror") == "true"
            )
        except Exception:
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

    @pyaedt_function_handler(symbol_color="color")
    def set_use_symbol_color(self, color=None):
        """Set symbol color usage.

        Parameters
        ----------
        color : bool, optional
            The default is ``None``.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        References
        ----------

        >>> oEditor.ChangeProperty
        """
        if not color:
            color = self.usesymbolcolor
        vMaterial = ["NAME:Use Symbol Color", "Value:=", color]
        self.change_property(vMaterial)
        return True

    @pyaedt_function_handler(R="red", G="green", B="blue")
    def set_color(self, red=255, green=128, blue=0):
        """Set symbol color.

        Parameters
        ----------
        red : int, optional
            Red color value. The default is ``255``.
        green : int, optional
            Green color value. The default is ``128``.
        blue : int, optional
            Blue color value. The default is ``0``

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        References
        ----------

        >>> oEditor.ChangeProperty
        """
        vMaterial = ["NAME:Component Color", "R:=", red, "G:=", green, "B:=", blue]
        self.change_property(vMaterial)
        return True

    @pyaedt_function_handler(property_name="name", property_value="value")
    def set_property(self, name, value):
        """Set a part property.

        Parameters
        ----------
        name : str
            Name of the property.
        value :
            Value for the property.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        References
        ----------

        >>> oEditor.ChangeProperty
        """
        if isinstance(name, list):
            for p, v in zip(name, value):
                v_prop = ["NAME:" + p, "Value:=", v]
                self.change_property(v_prop)
                if self.__dict__.get("_parameters", None) and p in self.__dict__["_parameters"]:
                    self.__dict__["_parameters"][p] = v
                else:
                    self.__dict__[p] = v
        else:
            v_prop = ["NAME:" + name, "Value:=", value]
            self.change_property(v_prop)
            if self.__dict__.get("_parameters", None) and name in self.__dict__["_parameters"]:
                self.__dict__["_parameters"][name] = value
            elif self.__dict__.get("_component_info", None) and name in self.__dict__.get("_component_info", None):
                self.__dict__["_component_info"][name] = value
            else:
                self.__dict__[name] = value
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

    @pyaedt_function_handler(vPropChange="property", names_list="names")
    def change_property(self, property_name, names=None):
        """Modify a property.

        Parameters
        ----------
        property_name : list
            Property value in AEDT syntax.
        names : list, optional
             The default is ``None``.

        Returns
        -------
        bool

        References
        ----------

        >>> oEditor.GetPropertyValue
        >>> oEditor.ChangeProperty
        """
        vChangedProps = ["NAME:ChangedProps", property_name]
        if names:
            vPropServers = ["NAME:PropServers"]
            for el in names:
                vPropServers.append(el)
        else:
            vPropServers = ["NAME:PropServers", self.composed_name]
        tabname = None
        if property_name[0][5:] in self._oeditor.GetProperties(self.tabname, self.composed_name):
            tabname = self.tabname
        elif property_name[0][5:] in self._oeditor.GetProperties("PassedParameterTab", self.composed_name):
            tabname = "PassedParameterTab"
        elif property_name[0][5:] in self._oeditor.GetProperties("BaseElementTab", self.composed_name):
            tabname = "BaseElementTab"
        if tabname:
            vGeo3dlayout = ["NAME:" + tabname, vPropServers, vChangedProps]
            vOut = ["NAME:AllTabs", vGeo3dlayout]
            if "NAME:Component Location" in str(vChangedProps) and "PagePort" not in self.composed_name:
                self._oeditor.ChangeProperty(vOut)
            return self._oeditor.ChangeProperty(vOut)
        return False

    @pyaedt_function_handler()
    def enforce_touchstone_model_passive(self):
        """Enforce touchstone model passive.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        References
        ----------

        >>> oModelManager.EditWithComps
        """
        props = self.model_data.props
        passive = OrderedDict(
            [
                ("DCOption", -1),
                ("InterpOption", 1),
                ("ExtrapOption", 3),
                ("Convolution", 0),
                ("Passivity", 6),
                ("Reciprocal", False),
                ("ModelOption", ""),
                ("DataType", 2),
            ]
        )
        props["NexximCustomization"] = passive
        props["ModTime"] = int(time.time())
        self.model_data.props = props
        return self.model_data.update()


class Wire(object):
    """Creates and manipulates a wire."""

    def __init__(self, modeler, composed_name=None):
        self.composed_name = composed_name
        self._app = modeler._app
        self._modeler = modeler
        self.name = ""
        self.id = 0
        self._points_in_segment = {}

    @property
    def points_in_segment(self):
        """Points in segment."""
        if not self.composed_name:
            return {}
        for segment in self._app.oeditor.GetWireSegments(self.composed_name):
            key = segment.split(" ")[3]
            point1 = [float(x) for x in segment.split(" ")[1].split(",")]
            point2 = [float(x) for x in segment.split(" ")[2].split(",")]
            if key in self._points_in_segment:
                self._points_in_segment[key].extend([point1, point2])
            else:
                self._points_in_segment[key] = [point1, point2]
        return self._points_in_segment

    @property
    def _oeditor(self):
        return self._modeler.oeditor

    @property
    def logger(self):
        """Logger."""
        return self._app.logger

    @property
    def wires(self):
        """List of all schematic wires in the design."""
        wire_names = []
        for wire in self._oeditor.GetAllElements():
            if "Wire" in wire:
                wire_names.append(wire)
        return wire_names

    @pyaedt_function_handler(wire_name="name")
    def display_wire_properties(self, name="", property_to_display="NetName", visibility="Name", location="Top"):
        """
        Display wire properties.

        Parameters
        ----------
        name : str, optional
            Wire name to display.
            Default value is ``""``.
        property_to_display : str, optional
            Property to display. Choices are: ``"NetName"``, ``"PinCount"``, ``"AlignMicrowavePorts"``,
            ``"SchematicID"``, ``"Segment0"``.
            Default value is ``"NetName"``.
        visibility : str, optional
            Visibility type. Choices are ``"Name"``, ``"Value"``, ``"Both"``, ``"Evaluated Value"``,
            ``"Evaluated Both"``.
            Default value is ``"Name"``.
        location : str, optional
            Wire name location. Choices are ``"Left"``, ``"Top"``, ``"Right"``, ``"Bottom"``, ``"Center"``.
            Default value is ``"Top"``.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.
        """
        try:
            if name:
                wire_exists = False
                for wire in self.wires:
                    if name == wire.split("@")[1].split(";")[0]:
                        wire_id = wire.split("@")[1].split(";")[1].split(":")[0]
                        wire_exists = True
                        break
                    else:
                        continue
                if not wire_exists:
                    raise ValueError("Invalid wire name provided.")
                composed_name = "Wire@{};{};{}".format(name, wire_id, 1)
            else:
                composed_name = self.composed_name
            self._oeditor.ChangeProperty(
                [
                    "NAME:AllTabs",
                    [
                        "NAME:PropDisplayPropTab",
                        ["NAME:PropServers", composed_name],
                        [
                            "NAME:NewProps",
                            ["NAME:" + property_to_display, "Format:=", visibility, "Location:=", location],
                        ],
                    ],
                ]
            )
            return True
        except ValueError as e:
            self.logger.error(str(e))
            return False
