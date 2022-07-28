# -*- coding: utf-8 -*-
"""
This module provides methods and data structures for managing all properties of
objects (points, lines, sheeets, and solids) within the AEDT 3D Layout Modeler.

"""
from __future__ import absolute_import  # noreorder

import re

from pyaedt import _retry_ntimes
from pyaedt import pyaedt_function_handler
from pyaedt.modeler.GeometryOperators import GeometryOperators
from pyaedt.modeler.Object3d import clamp
from pyaedt.modeler.Object3d import rgb_color_codes


class Objec3DLayout(object):
    """Manages properties of objects in HFSS 3D Layout.

    Parameters
    -----------
    primitives : :class:`pyaedt.modeler.Model3DLayout.Modeler3dLayout`
    """

    def __init__(self, primitives, prim_type=None):
        self._primitives = primitives
        self.m_Editor = self._primitives.oeditor
        self._n = 10
        self.prim_type = prim_type
        self._points = []

    @property
    def object_units(self):
        """Object units.

        Returns
        -------
        str
        """
        return self._primitives.model_units

    @pyaedt_function_handler()
    def change_property(self, property_val, names_list=None):
        """Modify a property.

        Parameters
        ----------
        property_val : list

        names_list : list, optional
             The default is ``None``.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        References
        ----------

        >>> oEditor.ChangeProperty
        """
        vChangedProps = ["NAME:ChangedProps", property_val]
        if names_list:  # pragma: no cover
            vPropServers = ["NAME:PropServers"]
            for el in names_list:
                vPropServers.append(el)
        else:
            vPropServers = ["NAME:PropServers", self.name]
        vGeo3dlayout = ["NAME:BaseElementTab", vPropServers, vChangedProps]
        vOut = ["NAME:AllTabs", vGeo3dlayout]

        self.m_Editor.ChangeProperty(vOut)
        return True

    @pyaedt_function_handler()
    def set_property_value(self, property_name, property_value):
        """Set a property value.

        Parameters
        ----------
        property_name : str
            Name of the property.
        property_value :
            Value of the property.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        References
        ----------

        >>> oEditor.ChangeProperty
        """
        vProp = ["NAME:" + property_name, "Value:=", property_value]
        return self.change_property(vProp)

    @property
    def angle(self):
        """Get/Set the circle radius.

        Returns
        -------
        str
            placement layer.

        References
        ----------

        >>> oEditor.GetPropertyValue
        """
        if self.prim_type in ["component", "pin", "via"]:
            return _retry_ntimes(self._n, self.m_Editor.GetPropertyValue, "BaseElementTab", self.name, "Angle")

    @angle.setter
    def angle(self, value):
        if self.prim_type in ["component", "pin", "via"]:
            vMaterial = ["NAME:Angle", "Value:=", value]
            self.change_property(vMaterial)

    @property
    def net_name(self):
        """Get/Set the net name.

        Returns
        -------
        str
            Name of the net.

        References
        ----------

        >>> oEditor.GetPropertyValue
        """
        if self.prim_type not in ["component"]:
            return _retry_ntimes(self._n, self.m_Editor.GetPropertyValue, "BaseElementTab", self.name, "Net")

    @net_name.setter
    def net_name(self, netname=""):
        if self.prim_type not in ["component"]:
            vMaterial = ["NAME:Net", "Value:=", netname]
            self.change_property(vMaterial)

    @property
    def placement_layer(self):
        """Get/Set the placement layer of the object.

        Returns
        -------
        str
            placement layer.

        References
        ----------

        >>> oEditor.GetPropertyValue
        """
        if self.prim_type not in ["pin", "via"]:
            return _retry_ntimes(self._n, self.m_Editor.GetPropertyValue, "BaseElementTab", self.name, "PlacementLayer")

    @placement_layer.setter
    def placement_layer(self, layer_name):
        if self.prim_type not in ["pin", "via"]:
            vMaterial = ["NAME:PlacementLayer", "Value:=", layer_name]
            self.change_property(vMaterial)

    @property
    def location(self):
        """Retrieve/Set the component location.

        Returns
        -------
        list
           List of ``(x, y)`` coordinates for the component location.

        References
        ----------

        >>> oEditor.GetPropertyValue
        """
        if self.prim_type in ["component", "pin", "via"]:
            location = _retry_ntimes(
                self._n, self.m_Editor.GetPropertyValue, "BaseElementTab", self.name, "Location"
            ).split(",")
            locs = []
            for i in location:
                try:
                    locs.append(float(i))
                except ValueError:  # pragma: no cover
                    locs.append(i)
            return locs
        else:
            return None

    @location.setter
    def location(self, position):
        if self.prim_type in ["component", "pin", "via"]:
            props = ["NAME:Location", "X:=", str(position[0]), "Y:=", str(position[0])]
            self.change_property(props)

    @property
    def lock_position(self):
        """Get/Set the lock position.

        Parameters
        ----------
        lock_position : bool, optional
            The default value is ``True``.

        Returns
        -------
        type

        References
        ----------

        >>> oEditor.ChangeProperty
        """
        return (
            True
            if _retry_ntimes(self._n, self.m_Editor.GetPropertyValue, "BaseElementTab", self.name, "LockPosition")
            in [True, "true"]
            else False
        )

    @lock_position.setter
    def lock_position(self, lock_position=True):
        vMaterial = ["NAME:LockPosition", "Value:=", lock_position]
        self.change_property(vMaterial)


class ModelInfoRlc(object):
    def __init__(self, component, name):
        self._comp = component
        self._name = name

    @property
    def rlc_model_type(self):
        props = _retry_ntimes(self._comp._n, self._comp.m_Editor.GetComponentInfo, self._name)
        model = ""
        for p in props:
            if "ComponentProp=" in p:
                model = p
                break
        s = r".+rlc\(r='(.+?)', re=(.+?), l='(.+?)', le=(.+?), c='(.+?)', ce=(.+?), p=(.+?), lyr=(.+?)"
        m = re.search(s, model)
        vals = []
        if m:
            for i in range(1, 9):
                if m.group(i) == "false":
                    vals.append(False)
                elif m.group(i) == "true":
                    vals.append(True)
                else:
                    vals.append(m.group(i))
        return vals

    @property
    def res(self):
        if self.rlc_model_type:
            return self.rlc_model_type[0]

    @property
    def cap(self):
        if self.rlc_model_type:
            return self.rlc_model_type[4]

    @property
    def ind(self):
        if self.rlc_model_type:
            return self.rlc_model_type[2]

    @property
    def is_parallel(self):
        if self.rlc_model_type:
            return self.rlc_model_type[6]


class Components3DLayout(Objec3DLayout, object):
    """Contains components in HFSS 3D Layout."""

    def __init__(self, primitives, name="", edb_object=None):
        Objec3DLayout.__init__(self, primitives, "component")
        self.name = name
        self.edb_object = edb_object

    @property
    def part(self):
        """Retrieve the component part.

        Returns
        -------
        type
            Component part.

        References
        ----------

        >>> oEditor.GetPropertyValue
        """
        return _retry_ntimes(self._n, self.m_Editor.GetPropertyValue, "BaseElementTab", self.name, "Part")

    @property
    def part_type(self):
        """Retrieve the component part type.

        Returns
        -------
        type
            Component part type.

        References
        ----------

        >>> oEditor.GetPropertyValue
        """
        return _retry_ntimes(self._n, self.m_Editor.GetPropertyValue, "BaseElementTab", self.name, "Part Type")

    @property
    def _part_type_id(self):
        parts = {"Other": 0, "Resistor": 1, "Inductor": 2, "Capacitor": 3, "IC": 4, "IO": 5}
        if self.part_type in parts:
            return parts[self.part_type]
        return -1

    @pyaedt_function_handler
    def enabled(self, status=True):
        """Enable or Disable the RLC Component.

        Parameters
        ----------
        status : bool, optional
            Set the RLC Component to Enable or Disable state.

        Returns
        -------
        bool
            `True` if succeeded.
        """
        if self._part_type_id in [0, 4, 5]:
            return False
        args = [
            "NAME:Model Info",
            ["NAME:Model", "RLCProp:=", ["CompPropEnabled:=", status], "CompType:=", self._part_type_id],
        ]
        return self.change_property(args)

    @property
    def pins(self):
        """Component pins.

        Returns
        -------
        List of str
        """
        return list(self.m_Editor.GetComponentPins(self.name))

    @property
    def model(self):
        """RLC model if available.

        Returns
        -------
        :class:`pyaedt.modeler.object3dlayout.ModelInfoRlc`
        """
        if self._part_type_id in [1, 2, 3]:
            return ModelInfoRlc(self, self.name)


class Nets3DLayout(object):
    """Contains Nets in HFSS 3D Layout."""

    def __init__(self, primitives, name=""):
        self._primitives = primitives
        self.m_Editor = self._primitives.oeditor
        self._n = 10
        self.name = name

    @property
    def components(self):
        """Components that belongs to the Nets.

        Returns
        -------
        :class:`pyaedt.modeler.object3dlayout.Components3DLayout`
        """
        comps = {}
        for c in self.m_Editor.FilterObjectList("Type", "component", self.m_Editor.FindObjects("Net", self.name)):
            comps[c] = self._primitives.components[c]
        return comps


class Pins3DLayout(Objec3DLayout, object):
    """Contains the pins in HFSS 3D Layout."""

    def __init__(self, primitives, name="", component_name=None, is_pin=True):
        Objec3DLayout.__init__(self, primitives, "pin" if is_pin else "via")
        self.componentname = "-".join(name.split("-")[:-1]) if not component_name else component_name
        self.name = name
        self.is_pin = is_pin

    @property
    def start_layer(self):
        """Retrieve the starting layer of the pin.

        Returns
        -------
        str
            Name of the starting layer of the pin.

        References
        ----------

        >>> oEditor.GetPropertyValue
        """
        return _retry_ntimes(self._n, self.m_Editor.GetPropertyValue, "BaseElementTab", self.name, "Start Layer")

    @property
    def stop_layer(self):
        """Retrieve the starting layer of the pin.

        Returns
        -------
        str
            Name of the stopping layer of the pin.

        References
        ----------

        >>> oEditor.GetPropertyValue
        """
        return _retry_ntimes(self._n, self.m_Editor.GetPropertyValue, "BaseElementTab", self.name, "Stop Layer")

    @property
    def holediam(self):
        """Retrieve the hole diameter of the pin.

        Returns
        --------
        float
           Hole diameter of the pin.

        References
        ----------

        >>> oEditor.GetPropertyValue
        """
        return _retry_ntimes(self._n, self.m_Editor.GetPropertyValue, "BaseElementTab", self.name, "HoleDiameter")


class Geometries3DLayout(Objec3DLayout, object):
    """Contains geometries in HFSS 3D Layout."""

    def __init__(self, primitives, name, prim_type="poly", is_void=False):
        Objec3DLayout.__init__(self, primitives, prim_type)
        self.name = name
        self.is_void = is_void

    @property
    def is_closed(self):
        """Either if the Geometry is closed or not.

        Returns
        -------
        bool
        """
        return True

    @property
    def points(self):
        """Provide the polygon points. For Lines it returns the center line.

        Returns
        -------
        List of :class:`pyaedt.modeler.object3dlayout.Points3dLayout`
        """
        if self._points:
            return self._points
        self._points = []
        obj = self.m_Editor.GetPolygon(self.name)
        for oo in obj.GetPoints():
            self._points.append(Points3dLayout(self._primitives, oo))
        return self._points

    @property
    def edges(self):
        """Edges list.

        Returns
        -------
        List
        """
        info = self.m_Editor.GetPolygonInfo(self.name)
        points = []
        for i in info:
            if i == "Poly:=":
                for k in info[info.index(i) + 1]:
                    if k == "pt:=":
                        source = info[info.index(i) + 1]
                        points = source[source.index(k) + 1][2:]
                        break
        xpoints = list(points[1::4])
        ypoints = list(points[3::4])
        if self.prim_type not in ["rect", "line"]:
            xt, yt = GeometryOperators.orient_polygon(xpoints, ypoints, clockwise=False)
        else:
            xt, yt = xpoints, ypoints
        edges = []
        p1 = None
        p2 = None
        for x, y in zip(xt, yt):
            if y < 1e100:
                if not p1:
                    p1 = [x, y]
                elif not p2:
                    p2 = [x, y]
                    edges.append([p1, p2])
                    p1 = p2
                else:
                    edges.append([p1, [x, y]])
                    p1 = [x, y]
        if self.prim_type == "rect":
            edges = [edges[2], edges[3], edges[0], edges[1]]
        return edges

    @pyaedt_function_handler()
    def edge_by_point(self, point):
        """Return the closest edge to specified point.

        Parameters
        ----------
        point : list
            List of [x,y] values.

        Returns
        -------
        int
            Edge id.
        """
        index_i = 0
        v_dist = None
        edge_id = None
        for edge in self.edges:
            v = GeometryOperators.v_norm(GeometryOperators.distance_vector(point, edge[0], edge[1]))
            if not v_dist or v < v_dist:
                v_dist = v
                edge_id = index_i
            index_i += 1
        return edge_id

    @property
    def bottom_edge_x(self):
        """Compute the lower edge in the layout on x direction.

        Returns
        -------
        int
            Edge number.
        """
        result = [(edge[0][0] + edge[1][0]) for edge in self.edges]
        return result.index(min(result))

    @property
    def top_edge_x(self):
        """Compute the upper edge in the layout on x direction.

        Returns
        -------
        int
            Edge number.
        """
        result = [(edge[0][0] + edge[1][0]) for edge in self.edges]
        return result.index(max(result))

    @property
    def bottom_edge_y(self):
        """Compute the lower edge in the layout on y direction.

        Returns
        -------
        int
            Edge number.
        """
        result = [(edge[0][1] + edge[1][1]) for edge in self.edges]
        return result.index(min(result))

    @property
    def top_edge_y(self):
        """Compute the upper edge in the layout on y direction.

        Returns
        -------
        int
            Edge number.
        """
        result = [(edge[0][1] + edge[1][1]) for edge in self.edges]
        return result.index(max(result))

    @pyaedt_function_handler()
    def get_property_value(self, propertyname):
        """Retrieve a property value.

        Parameters
        ----------
        propertyname : str
            Name of the property

        Returns
        -------
        type
            Value of the property.

        References
        ----------

        >>> oEditor.GetPropertyValue
        """
        return _retry_ntimes(self._n, self.m_Editor.GetPropertyValue, "BaseElementTab", self.name, propertyname)

    @property
    def negative(self):
        """Get/Set the negative.

        Parameters
        ----------
        negative : bool, optional
            The default is ``False``.
        Returns
        -------
        type

        References
        ----------

        >>> oEditor.ChangeProperty
        """
        if self.is_void:
            return False
        return (
            True
            if _retry_ntimes(self._n, self.m_Editor.GetPropertyValue, "BaseElementTab", self.name, "Negative")
            in [True, "true"]
            else False
        )

    @negative.setter
    def negative(self, negative=False):
        if not self.is_void:
            vMaterial = ["NAME:Negative", "Value:=", negative]
            self.change_property(vMaterial)

    @property
    def net_name(self):
        """Get/Set the net name.

        Returns
        -------
        str
            Name of the net.

        References
        ----------

        >>> oEditor.GetPropertyValue
        """
        if self.is_void:
            return None
        if self.prim_type not in ["component"]:
            return _retry_ntimes(self._n, self.m_Editor.GetPropertyValue, "BaseElementTab", self.name, "Net")

    @net_name.setter
    def net_name(self, netname=""):
        if not self.is_void and self.prim_type not in ["component"]:
            vMaterial = ["NAME:Net", "Value:=", netname]
            self.change_property(vMaterial)


class Polygons3DLayout(Geometries3DLayout, object):
    """Class for Hfss 3D Layout polygons management."""

    def __init__(self, primitives, name, prim_type="poly", is_void=False):
        Geometries3DLayout.__init__(self, primitives, name, prim_type, is_void)
        self._points = []

    @property
    def is_closed(self):
        """Either if the Geometry is closed or not.

        Returns
        -------
        bool
        """
        obj = self.m_Editor.GetPolygon(self.name)
        return obj.IsClosed()

    @property
    def polygon_voids(self):
        """All Polygon Voids.

        Returns
        -------
        dict
            Dictionary of polygon voids.
        """
        voids = list(self.m_Editor.GetPolygonVoids(self.name))
        pvoids = {}
        for void in voids:
            pvoids[void] = Polygons3DLayout(self._primitives, void, "poly", True)
        return pvoids


class Circle3dLayout(Geometries3DLayout, object):
    """Class for Hfss 3D Layout circles management."""

    def __init__(self, primitives, name, is_void=False):
        Geometries3DLayout.__init__(self, primitives, name, "circle", is_void)

    @property
    def center(self):
        """Get/Set the circle center.

        Returns
        -------
        str
            placement layer.

        References
        ----------

        >>> oEditor.GetPropertyValue
        """
        cent = _retry_ntimes(self._n, self.m_Editor.GetPropertyValue, "BaseElementTab", self.name, "Center")
        if cent:
            return cent.split(",")

    @center.setter
    def center(self, position):
        vMaterial = ["NAME:Center", "Value:=", position]
        self.change_property(vMaterial)

    @property
    def radius(self):
        """Get/Set the circle radius.

        Returns
        -------
        str
            placement layer.

        References
        ----------

        >>> oEditor.GetPropertyValue
        """
        return _retry_ntimes(self._n, self.m_Editor.GetPropertyValue, "BaseElementTab", self.name, "Radius")

    @radius.setter
    def radius(self, value):
        vMaterial = ["NAME:Radius", "Value:=", value]
        self.change_property(vMaterial)


class Rect3dLayout(Geometries3DLayout, object):
    """Class for Hfss 3D Layout rectangles management."""

    def __init__(self, primitives, name, is_void=False):
        Geometries3DLayout.__init__(self, primitives, name, "rect", is_void)

    @property
    def corner_radius(self):
        """Get/Set the circle radius.

        Returns
        -------
        str
            placement layer.

        References
        ----------

        >>> oEditor.GetPropertyValue
        """
        return _retry_ntimes(self._n, self.m_Editor.GetPropertyValue, "BaseElementTab", self.name, "CornerRadius")

    @corner_radius.setter
    def corner_radius(self, value):
        vMaterial = ["NAME:CornerRadius", "Value:=", value]
        self.change_property(vMaterial)

    @property
    def two_point_description(self):
        """Get/Set the circle radius.

        Returns
        -------
        str
            placement layer.

        References
        ----------

        >>> oEditor.GetPropertyValue
        """
        return (
            True
            if _retry_ntimes(self._n, self.m_Editor.GetPropertyValue, "BaseElementTab", self.name, "2 pt Description")
            in [True, "true"]
            else False
        )

    @two_point_description.setter
    def two_point_description(self, value):
        vMaterial = ["NAME:2 pt Description", "Value:=", value]
        self.change_property(vMaterial)

    @property
    def center(self):
        """Get/Set the rectangle center.

        Returns
        -------
        str
            placement layer.

        References
        ----------

        >>> oEditor.GetPropertyValue
        """
        if not self.two_point_description:
            cent = _retry_ntimes(self._n, self.m_Editor.GetPropertyValue, "BaseElementTab", self.name, "Center")
            if cent:
                return cent.split(",")

    @center.setter
    def center(self, value):
        if not self.two_point_description:
            vMaterial = ["NAME:Center", "X:=", value[0], "Y:=", value[1]]
            self.change_property(vMaterial)

    @property
    def width(self):
        """Get/Set the circle radius.

        Returns
        -------
        str
            placement layer.

        References
        ----------

        >>> oEditor.GetPropertyValue
        """
        if not self.two_point_description:
            return _retry_ntimes(self._n, self.m_Editor.GetPropertyValue, "BaseElementTab", self.name, "Width")

    @width.setter
    def width(self, value):
        if not self.two_point_description:
            vMaterial = ["NAME:Width", "Value:=", value]
            self.change_property(vMaterial)

    @property
    def height(self):
        """Get/Set the circle radius.

        Returns
        -------
        str
            placement layer.

        References
        ----------

        >>> oEditor.GetPropertyValue
        """
        if not self.two_point_description:
            return _retry_ntimes(self._n, self.m_Editor.GetPropertyValue, "BaseElementTab", self.name, "Height")

    @height.setter
    def height(self, value):
        if not self.two_point_description:
            vMaterial = ["NAME:Height", "Value:=", value]
            self.change_property(vMaterial)

    @property
    def point_a(self):
        """Get/Set the Point A value if 2Point Description is enabled.

        Returns
        -------
        List
            Point A coordinates.

        References
        ----------

        >>> oEditor.GetPropertyValue
        """
        if self.two_point_description:
            pa = _retry_ntimes(self._n, self.m_Editor.GetPropertyValue, "BaseElementTab", self.name, "Pt A")
            if pa:
                return pa.split(",")

    @point_a.setter
    def point_a(self, value):
        if self.two_point_description:
            vMaterial = ["NAME:Pt A", "X:=", value[0], "Y:=", value[1]]
            self.change_property(vMaterial)

    @property
    def point_b(self):
        """Get/Set the Point A value if 2Point Description is enabled.

        Returns
        -------
        List
            Point B coordinates

        References
        ----------

        >>> oEditor.GetPropertyValue
        """
        if self.two_point_description:
            pa = _retry_ntimes(self._n, self.m_Editor.GetPropertyValue, "BaseElementTab", self.name, "Pt B")
            if pa:
                return pa.split(",")

    @point_b.setter
    def point_b(self, value):
        if self.two_point_description:
            vMaterial = ["NAME:Pt B", "X:=", value[0], "Y:=", value[1]]
            self.change_property(vMaterial)


class Line3dLayout(Geometries3DLayout, object):
    """Class for Hfss 3D Layout lines management."""

    def __init__(self, primitives, name, is_void=False):
        Geometries3DLayout.__init__(self, primitives, name, "line", is_void)
        self._points = []

    @property
    def bend_type(self):
        """Get/Set the line bend type.

        Returns
        -------
        str
            Bend Type.

        References
        ----------

        >>> oEditor.GetPropertyValue
        """
        return _retry_ntimes(self._n, self.m_Editor.GetPropertyValue, "BaseElementTab", self.name, "BendType")

    @bend_type.setter
    def bend_type(self, value):
        vMaterial = ["NAME:BendType", "Value:=", value]
        self.change_property(vMaterial)

    @property
    def start_cap_type(self):
        """Get/Set the line start type.

        Returns
        -------
        str
            Start Cap Type.

        References
        ----------

        >>> oEditor.GetPropertyValue
        """
        return _retry_ntimes(self._n, self.m_Editor.GetPropertyValue, "BaseElementTab", self.name, "StartCapType")

    @start_cap_type.setter
    def start_cap_type(self, value):
        vMaterial = ["NAME:StartCap Type", "Value:=", value]
        self.change_property(vMaterial)

    @property
    def end_cap_type(self):
        """Get/Set the line end type.

        Returns
        -------
        str
            End Cap Type.

        References
        ----------

        >>> oEditor.GetPropertyValue
        """
        return _retry_ntimes(self._n, self.m_Editor.GetPropertyValue, "BaseElementTab", self.name, "EndCapType")

    @end_cap_type.setter
    def end_cap_type(self, value):
        vMaterial = ["NAME:EndCap Type", "Value:=", value]
        self.change_property(vMaterial)

    @property
    def width(self):
        """Get/Set the line width.

        Returns
        -------
        str
            Line Width.

        References
        ----------

        >>> oEditor.GetPropertyValue
        """
        return _retry_ntimes(self._n, self.m_Editor.GetPropertyValue, "BaseElementTab", self.name, "LineWidth")

    @width.setter
    def width(self, value):
        vMaterial = ["NAME:LineWidth", "Value:=", value]
        self.change_property(vMaterial)

    @property
    def length(self):
        """Get the line length.

        Returns
        -------
        str
            Line length.

        References
        ----------

        >>> oEditor.GetPropertyValue
        """
        return _retry_ntimes(self._n, self.m_Editor.GetPropertyValue, "BaseElementTab", self.name, "TotalLength")


class Points3dLayout(object):
    """Class for Hfss 3D Layout Points management."""

    def __init__(self, primitives, point):
        self._primitives = primitives
        self.point = point

    @property
    def is_arc(self):
        """Either if the Point is an arc or not.

        Returns
        -------
        bool
        """
        return True if self.point.IsArc() != 0 else False

    @property
    def position(self):
        """Points x and y coordinate.

        Returns
        -------
        List
        """
        if self.is_arc:
            return [self.point.GetX()]
        else:
            return [self.point.GetX(), self.point.GetY()]

    @pyaedt_function_handler()
    def move(self, new_position):
        """Move actual point to new location.

        Parameters
        ----------
        new_position : List
            New point location.

        Returns
        -------

        """
        if self.point.Move(self._primitives.m_Editor.Point().Set(new_position[0], new_position[1])):
            return True


class Point(object):
    """Manages point attributes for the AEDT 3D Modeler.

    Parameters
    ----------
    primitives : :class:`pyaedt.modeler.Primitives3D.Primitives3D`
        Inherited parent object.
    name : str
        Name of the point.

    Examples
    --------
    Basic usage demonstrated with an HFSS design:

    >>> from pyaedt import Hfss
    >>> aedtapp = Hfss()
    >>> primitives = aedtapp.modeler

    Create a point, to return an :class:`pyaedt.modeler.Object3d.Point`.

    >>> point = primitives.create_point([30, 30, 0], "my_point", (0, 195, 255))
    >>> my_point = primitives.points_by_name[point.name]
    """

    def __init__(self, primitives, name):
        self._name = name
        self._point_coordinate_system = "Global"
        self._color = None
        self._position = None
        self._primitives = primitives
        self._all_props = None

    @property
    def m_Editor(self):
        """Pointer to the oEditor object in the AEDT API. This property is
        intended primarily for use by FacePrimitive, EdgePrimitive, and
        VertexPrimitive child objects.

        Returns
        -------
        oEditor COM Object

        """
        return self._primitives.oeditor

    @property
    def logger(self):
        """Logger."""
        return self._primitives.logger

    @property
    def name(self):
        """Name of the point as a string value.

        Returns
        -------
        str
           Name of object as a string value.

        References
        ----------

        >>> oEditor.GetPropertyValue
        >>> oEditor.ChangeProperty

        """
        return self._name

    @name.setter
    def name(self, point_name):
        if point_name not in self._primitives.points_by_name.keys:
            if point_name != self._name:
                name_property = []
                name_property.append("NAME:Name")
                name_property.append("Value:=")
                name_property.append(point_name)
                changed_property = ["NAME:ChangedProps", name_property]
                property_servers = ["NAME:PropServers"]
                property_servers.append(self._name)
                point_tab = ["NAME:Geometry3DPointTab", property_servers, changed_property]
                all_tabs = ["NAME:AllTabs", point_tab]
                _retry_ntimes(10, self._primitives.oeditor.ChangeProperty, all_tabs)
                self._name = point_name
                self._primitives.cleanup_objects()
        else:
            self.logger.warning("A point named '%s' already exists.", point_name)

    @property
    def valid_properties(self):
        """Valid properties.

        References
        ----------

        >>> oEditor.GetProperties
        """
        if not self._all_props:
            self._all_props = _retry_ntimes(10, self.m_Editor.GetProperties, "Geometry3DPointTab", self._name)
        return self._all_props

    # Note: We currently cannot get the color property value because
    # when we try to access it, we only get access to the 'edit' button.
    # Following is the line that we would use but it currently returns 'edit'.
    # color = _retry_ntimes(10, self.m_Editor.GetPropertyValue, "Geometry3DPointTab", self._name, "Color")
    def set_color(self, color_value):
        """Set symbol color.

        Parameters
        ----------
        color_value : string
            String exposing the new color of the point in the format of "(001 255 255)".

        References
        ----------

        >>> oEditor.ChangeProperty

        Examples
        --------
        >>> point = self.aedtapp.modeler.create_point([30, 30, 0], "demo_point")
        >>> point.set_color("(143 175 158)")

        """
        color_tuple = None
        if isinstance(color_value, str):
            try:
                color_tuple = rgb_color_codes[color_value]
            except KeyError:
                parse_string = color_value.replace(")", "").replace("(", "").split()
                if len(parse_string) == 3:
                    color_tuple = tuple([int(x) for x in parse_string])
        else:
            try:
                color_tuple = tuple([int(x) for x in color_value])
            except ValueError:
                pass

        if color_tuple:
            try:
                R = clamp(color_tuple[0], 0, 255)
                G = clamp(color_tuple[1], 0, 255)
                B = clamp(color_tuple[2], 0, 255)
                vColor = ["NAME:Color", "R:=", str(R), "G:=", str(G), "B:=", str(B)]
                self._change_property(vColor)
                self._color = (R, G, B)
            except TypeError:
                color_tuple = None
        else:
            msg_text = "Invalid color input {} for object {}.".format(color_value, self._name)
            self._primitives.logger.warning(msg_text)

    @property
    def coordinate_system(self):
        """Coordinate system of the point.

        Returns
        -------
        str
            Name of the point's coordinate system.

        References
        ----------

        >>> oEditor.GetPropertyValue
        >>> oEditor.ChangeProperty

        """
        if self._point_coordinate_system is not None:
            return self._point_coordinate_system
        if "Orientation" in self.valid_properties:
            self._point_coordinate_system = _retry_ntimes(
                10, self.m_Editor.GetPropertyValue, "Geometry3DPointTab", self._name, "Orientation"
            )
            return self._point_coordinate_system

    @coordinate_system.setter
    def coordinate_system(self, new_coordinate_system):

        coordinate_system = ["NAME:Orientation", "Value:=", new_coordinate_system]
        self._change_property(coordinate_system)
        self._point_coordinate_system = new_coordinate_system
        return True

    @pyaedt_function_handler()
    def delete(self):
        """Delete the point.

        References
        ----------

        >>> oEditor.Delete
        """
        arg = ["NAME:Selections", "Selections:=", self._name]
        self.m_Editor.Delete(arg)
        self._primitives.remove_point(self.name)
        self.__dict__ = {}

    @pyaedt_function_handler()
    def _change_property(self, vPropChange):
        return self._primitives._change_point_property(vPropChange, self.name)


class ComponentsSubCircuit3DLayout(Objec3DLayout, object):
    """Contains 3d Components in HFSS 3D Layout.

    Parameters
    ----------
    parent :

    name : string, optional
        The default is ``""``.

    """

    def __init__(self, primitives, name=""):
        Objec3DLayout.__init__(self, primitives, "component")
        self.name = name

    @property
    def component_info(self):
        """Retrieve all component info."""
        return self.m_Editor.GetComponentInfo(self.name)

    @property
    def component_name(self):
        """Retrieve the component name."""
        try:
            return self.component_info[0].split("=")[1]
        except IndexError:
            return ""

    @property
    def angle(self):
        """Retrieve/Set the component angle.

        Returns
        -------
        str
            Component angle.

        References
        ----------

        >>> oEditor.GetPropertyValue
        """
        if self.is_3d_placement:
            ang = self.m_Editor.GetPropertyValue("BaseElementTab", self.name, "Rotation Angle")
        else:
            ang = self.m_Editor.GetPropertyValue("BaseElementTab", self.name, "Angle")
        try:
            return float(ang)
        except ValueError:
            return ang

    @angle.setter
    def angle(self, angle_val):
        if isinstance(angle_val, (int, float)):
            angle_val = "{}deg".format(angle_val)

        if not self.is_3d_placement:
            props = ["NAME:Angle", "Value:=", angle_val]
        else:
            props = ["NAME:Rotation Angle", "Value:=", angle_val]
        self.change_property(props)

    @property
    def is_3d_placement(self):
        """Retrieve if the component has 3d placement."""
        if self.m_Editor.GetPropertyValue("BaseElementTab", self.name, "3D Placement") in ["true", "True"]:
            return True
        else:
            return False
