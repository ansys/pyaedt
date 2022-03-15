"""
This module contains these classes: `EdbLayout` and `Shape`.
"""
import math
import os
import warnings

from pyaedt.edb_core.EDB_Data import EDBPrimitives
from pyaedt.edb_core.EDB_Data import SimulationConfiguration
from pyaedt.edb_core.general import convert_py_list_to_net_list
from pyaedt.generic.general_methods import is_ironpython
from pyaedt.generic.general_methods import pyaedt_function_handler

try:
    from System import Tuple
    from System.Collections.Generic import List

except ImportError:
    if os.name != "posix":
        warnings.warn('This module requires the "pythonnet" package.')


class EdbLayout(object):
    """Manages EDB functionalities for layouts.

    Examples
    --------
    >>> from pyaedt import Edb
    >>> edbapp = Edb("myaedbfolder", edbversion="2021.2")
    >>> edb_layout = edbapp.core_primitives
    """

    def __init__(self, p_edb):
        self._prims = []
        self._pedb = p_edb
        self._primitives_by_layer = {}
        # self.update_primitives()

    @property
    def _edb(self):
        return self._pedb.edb

    @property
    def _edb_value(self):
        return self._pedb.edb_value

    @property
    def _logger(self):
        """Logger."""
        return self._pedb.logger

    @property
    def _builder(self):
        return self._pedb.builder

    @property
    def _edbutils(self):
        return self._pedb.edbutils

    @property
    def _active_layout(self):
        return self._pedb.active_layout

    @property
    def _cell(self):
        return self._pedb.active_cell

    @property
    def db(self):
        """Db object."""
        return self._pedb.db

    @property
    def layers(self):
        """Dictionary of layers.

        Returns
        -------
        dict
            Dictionary of layers.
        """
        return self._pedb.core_stackup.stackup_layers.layers

    @pyaedt_function_handler()
    def update_primitives(self):
        """
        Update a primitives list from the EDB database.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.
        """
        if self._active_layout:
            self._prims = []
            self._primitives_by_layer = {}
            layoutInstance = self._active_layout.GetLayoutInstance()
            layoutObjectInstances = layoutInstance.GetAllLayoutObjInstances()
            for el in layoutObjectInstances.Items:
                try:
                    self._prims.append(EDBPrimitives(el.GetLayoutObj(), self._pedb))
                except:
                    continue
            for lay in self.layers:
                self._primitives_by_layer[lay] = self.get_polygons_by_layer(lay)
            self._logger.info("Primitives Updated")
            return True
        return False

    @property
    def primitives(self):
        """Primitives.

        Returns
        -------
        list of :class:`pyaedt.edb_core.EDB_Data.EDBPrimitives`
            List of primitives.
        """
        if not self._prims:
            self.update_primitives()
        return self._prims

    @property
    def polygons_by_layer(self):
        """Primitives with layer names as keys.

        Returns
        -------
        dict
            Dictionary of primitives with layer names as keys.
        """
        if not self._primitives_by_layer:
            self.update_primitives()
        return self._primitives_by_layer

    @property
    def rectangles(self):
        """Rectangles.

        Returns
        -------
        list of :class:`pyaedt.edb_core.EDB_Data.EDBPrimitives`
            List of rectangles.

        """
        return [i for i in self.primitives if i.type == "Rectangle"]

    @property
    def circles(self):
        """Circles.

        Returns
        -------
        list of :class:`pyaedt.edb_core.EDB_Data.EDBPrimitives`
            List of circles.

        """
        return [i for i in self.primitives if i.type == "Circle"]

    @property
    def paths(self):
        """Paths.

        Returns
        -------
        list of :class:`pyaedt.edb_core.EDB_Data.EDBPrimitives`
            List of paths.
        """
        return [i for i in self.primitives if i.type == "Path"]

    @property
    def bondwires(self):
        """Bondwires.

        Returns
        -------
        list of :class:`pyaedt.edb_core.EDB_Data.EDBPrimitives`
            List of bondwires.
        """
        return [i for i in self.primitives if i.type == "Bondwire"]

    @property
    def polygons(self):
        """Polygons.

        Returns
        -------
        list of :class:`pyaedt.edb_core.EDB_Data.EDBPrimitives`
            List of polygons.
        """
        return [i for i in self.primitives if i.type == "Polygon"]

    @pyaedt_function_handler()
    def get_polygons_by_layer(self, layer_name, net_list=None):
        """Retrieve polygons by a layer.

        Parameters
        ----------
        layer_name : str
            Name of the layer.
        net_list : list, optional
            List of net names.

        Returns
        -------
        list
            List of primitive objects.
        """
        objinst = []
        for el in self.polygons:
            if el.GetLayer().GetName() == layer_name:
                if net_list and el.GetNet().GetName() in net_list:
                    objinst.append(el)
                else:
                    objinst.append(el)
        return objinst

    @pyaedt_function_handler()
    def get_polygon_bounding_box(self, polygon):
        """Retrieve a polygon bounding box.

        Parameters
        ----------
        polygon :
            Name of the polygon.

        Returns
        -------
        list
            List of bounding box coordinates in the format ``[-x, -y, +x, +y]``.

        Examples
        --------
        >>> poly = edb_core.core_primitives.get_polygons_by_layer("GND")
        >>> bounding = edb_core.core_primitives.get_polygon_bounding_box(poly[0])
        """
        bounding = []
        try:
            bounding_box = polygon.GetPolygonData().GetBBox()
            bounding = [
                bounding_box.Item1.X.ToDouble(),
                bounding_box.Item1.Y.ToDouble(),
                bounding_box.Item2.X.ToDouble(),
                bounding_box.Item2.Y.ToDouble(),
            ]
        except:
            pass
        return bounding

    @pyaedt_function_handler()
    def get_polygon_points(self, polygon):
        """Retrieve polygon points.

        .. note::
           For arcs, one point is returned.

        Parameters
        ----------
        polygon :
            Name of the polygon.

        Returns
        -------
        list
            List of doubles.

        Examples
        --------

        >>> poly = edb_core.core_primitives.get_polygons_by_layer("GND")
        >>> points  = edb_core.core_primitives.get_polygon_points(poly[0])

        """
        points = []
        i = 0
        continue_iterate = True
        prev_point = None
        while continue_iterate:
            try:
                point = polygon.GetPolygonData().GetPoint(i)
                if prev_point != point:
                    if point.IsArc():
                        points.append([point.X.ToDouble()])
                    else:
                        points.append([point.X.ToDouble(), point.Y.ToDouble()])
                    prev_point = point
                    i += 1
                else:
                    continue_iterate = False
            except:
                continue_iterate = False
        return points

    @pyaedt_function_handler()
    def parametrize_polygon(self, polygon, selection_polygon, offset_name="offsetx", origin=None):
        """Parametrize pieces of a polygon based on another polygon.

        Parameters
        ----------
        polygon :
            Name of the polygon.
        selection_polygon :
            Polygon to use as a filter.
        offset_name : str, optional
            Name of the offset to create.  The default is ``"offsetx"``.
        origin : list, optional
            List of the X and Y origins, which impacts the vector
            computation and is needed to determine expansion direction.
            The default is ``None``, in which case the vector is
            computed from the polygon's center.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.
        """

        def calc_slope(point, origin):
            if point[0] - origin[0] != 0:
                slope = math.atan((point[1] - origin[1]) / (point[0] - origin[0]))
                xcoeff = math.sin(slope)
                ycoeff = math.cos(slope)

            else:
                if point[1] > 0:
                    xcoeff = 0
                    ycoeff = 1
                else:
                    xcoeff = 0
                    ycoeff = -1
            if ycoeff > 0:
                ycoeff = "+" + str(ycoeff)
            else:
                ycoeff = str(ycoeff)
            if xcoeff > 0:
                xcoeff = "+" + str(xcoeff)
            else:
                xcoeff = str(xcoeff)
            return xcoeff, ycoeff

        selection_polygon_data = selection_polygon.GetPolygonData()
        poligon_data = polygon.GetPolygonData()
        bound_center = poligon_data.GetBoundingCircleCenter()
        bound_center2 = selection_polygon_data.GetBoundingCircleCenter()
        center = [bound_center.X.ToDouble(), bound_center.Y.ToDouble()]
        center2 = [bound_center2.X.ToDouble(), bound_center2.Y.ToDouble()]
        x1, y1 = calc_slope(center2, center)

        if not origin:
            origin = [center[0] + float(x1) * 10000, center[1] + float(y1) * 10000]
        result, var_server = self._pedb.add_design_variable(offset_name, 0.0)
        i = 0
        continue_iterate = True
        prev_point = None
        while continue_iterate:
            try:
                point = poligon_data.GetPoint(i)
                if prev_point != point:
                    check_inside = selection_polygon_data.PointInPolygon(point)
                    if check_inside:
                        xcoeff, ycoeff = calc_slope([point.X.ToDouble(), point.X.ToDouble()], origin)

                        new_points = self._edb.Geometry.PointData(
                            self._edb_value(point.X.ToString() + "{}*{}".format(xcoeff, offset_name), var_server),
                            self._edb_value(point.Y.ToString() + "{}*{}".format(ycoeff, offset_name), var_server),
                        )
                        poligon_data.SetPoint(i, new_points)
                    prev_point = point
                    i += 1
                else:
                    continue_iterate = False
            except:
                continue_iterate = False
        polygon.SetPolygonData(poligon_data)
        return True

    @pyaedt_function_handler()
    def create_path(
        self,
        path_list,
        layer_name,
        width=1,
        net_name="",
        start_cap_style="Round",
        end_cap_style="Round",
        corner_style="Round",
    ):
        """
        Create a path based on a list of points.

        Parameters
        ----------
        path_list : list
            List of points.
        layer_name : str
            Name of the layer on which to create the path.
        width : float, optional
            Width of the path. The default is ``1``.
        net_name : str, optional
            Name of the net. The default is ``""``.
        start_cap_style : str, optional
            Style of the cap at its start. Options are ``"Round"``,
            ``"Extended",`` and ``"Flat"``. The default is
            ``"Round"``.
        end_cap_style : str, optional
            Style of the cap at its end. Options are ``"Round"``,
            ``"Extended",`` and ``"Flat"``. The default is
            ``"Round"``.
        corner_style : str, optional
            Style of the corner. Options are ``"Round"``,
            ``"Sharp"`` and ``"Mitered"``. The default is ``"Round"``.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.
        """
        net = self._pedb.core_nets.find_or_create_net(net_name)
        if start_cap_style.lower() == "round":
            start_cap_style = self._edb.Cell.Primitive.PathEndCapStyle.Round
        elif start_cap_style.lower() == "extended":
            start_cap_style = self._edb.Cell.Primitive.PathEndCapStyle.Extended  # pragma: no cover
        else:
            start_cap_style = self._edb.Cell.Primitive.PathEndCapStyle.Flat  # pragma: no cover
        if end_cap_style.lower() == "round":
            end_cap_style = self._edb.Cell.Primitive.PathEndCapStyle.Round  # pragma: no cover
        elif end_cap_style.lower() == "extended":
            end_cap_style = self._edb.Cell.Primitive.PathEndCapStyle.Extended  # pragma: no cover
        else:
            end_cap_style = self._edb.Cell.Primitive.PathEndCapStyle.Flat
        if corner_style.lower() == "round":
            corner_style = self._edb.Cell.Primitive.PathCornerStyle.RoundCorner
        elif corner_style.lower() == "sharp":
            corner_style = self._edb.Cell.Primitive.PathCornerStyle.SharpCorner  # pragma: no cover
        else:
            corner_style = self._edb.Cell.Primitive.PathCornerStyle.MiterCorner  # pragma: no cover

        pointlists = [
            self._edb.Geometry.PointData(self._edb_value(i[0]), self._edb_value(i[1])) for i in path_list.points
        ]
        polygonData = self._edb.Geometry.PolygonData(convert_py_list_to_net_list(pointlists), False)
        polygon = self._edb.Cell.Primitive.Path.Create(
            self._active_layout,
            layer_name,
            net,
            self._edb_value(width),
            start_cap_style,
            end_cap_style,
            corner_style,
            polygonData,
        )
        if polygon.IsNull():
            self._logger.error("Null path created")
            return False
        else:
            if not self._prims:
                self.update_primitives()
            else:
                self._prims.append(EDBPrimitives(polygon, self._pedb))
                if layer_name in self._primitives_by_layer:
                    self._primitives_by_layer[layer_name].append(polygon)
                else:
                    self._primitives_by_layer[layer_name] = [polygon]
        return polygon

    @pyaedt_function_handler()
    def create_polygon(self, main_shape, layer_name, voids=[], net_name=""):
        """Create a polygon based on a list of points and voids.

        Parameters
        ----------
        main_shape :
            Shape of the main object.
        layer_name : str
            Name of the layer on which to create the polygon.
        voids : list, optional
            List of shape objects for voids. The default is``[]``.
        net_name : str, optional
            Name of the net. The default is ``""``.

        Returns
        -------
        bool, :class:`pyaedt.edb_core.EDB_Data.EDBPrimitives`
            Polygon when successful, ``False`` when failed.
        """
        net = self._pedb.core_nets.find_or_create_net(net_name)
        polygonData = self.shape_to_polygon_data(main_shape)
        if polygonData is None or polygonData.IsNull() or polygonData is False:
            self._logger.error("Failed to create main shape polygon data")
            return False
        for void in voids:
            voidPolygonData = self.shape_to_polygon_data(void)
            if voidPolygonData is None or voidPolygonData.IsNull() or polygonData is False:
                self._logger.error("Failed to create void polygon data")
                return False
            polygonData.AddHole(voidPolygonData)
        polygon = self._edb.Cell.Primitive.Polygon.Create(self._active_layout, layer_name, net, polygonData)
        if polygon.IsNull() or polygonData is False:
            self._logger.error("Null polygon created")
            return False
        else:
            if not self._prims:
                self.update_primitives()
            else:
                self._prims.append(EDBPrimitives(polygon, self._pedb))
                if layer_name in list(self._primitives_by_layer.keys()):
                    self._primitives_by_layer[layer_name].append(polygon)
                else:
                    self._primitives_by_layer[layer_name] = [polygon]
            return polygon

    @pyaedt_function_handler()
    def get_primitives(self, net_name=None, layer_name=None, prim_type=None, is_void=False):
        """Get primitives by conditions.

        Parameters
        ----------
        net_name : str, optional
            Set filter on net_name. Default is `None"`.
        layer_name : str, optional
            Set filter on layer_name. Default is `None"`.
        prim_type :  str, optional
            Set filter on primitive type. Default is `None"`.
        is_void : bool
            Set filter on is_void. Default is 'False'
        Returns
        -------
        list
            List of filtered primitives
        """
        prims = []
        for el in self.primitives:
            if not el.type:
                continue
            if net_name:
                if not el.net_name == net_name:
                    continue
            if layer_name:
                if not el.layer_name == layer_name:
                    continue
            if prim_type:
                if not el.type == prim_type:
                    continue
            if not el.is_void == is_void:
                continue
            prims.append(el)
        return prims

    @pyaedt_function_handler()
    def fix_circle_void_for_clipping(self):
        """Fix issues when circle void are clipped due to a bug in EDB.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when no changes were applied.
        """
        for void_circle in self.circles:
            if not void_circle.is_void:
                continue
            if is_ironpython:  # pragma: no cover
                res, center_x, center_y, radius = void_circle.primitive_object.GetParameters()
            else:
                res, center_x, center_y, radius = void_circle.primitive_object.GetParameters(0.0, 0.0, 0.0)
            cloned_circle = self._edb.Cell.Primitive.Circle.Create(
                self._active_layout,
                void_circle.layer_name,
                void_circle.net,
                self._edb_value(center_x),
                self._edb_value(center_y),
                self._edb_value(radius),
            )
            if res:
                cloned_circle.SetIsNegative(True)
                void_circle.Delete()
        self.update_primitives()
        return True

    @pyaedt_function_handler()
    def add_void(self, shape, void_shape):
        """Add a void into a shape.

        Parameters
        ----------
        shape : Polygon
            Shape of the main object.
        void_shape : list, Path
            Shape of the voids.
        """
        flag = False
        if isinstance(void_shape, list):
            for void in void_shape:
                flag = shape.AddVoid(void)
                if not flag:
                    return flag
        else:
            return shape.AddVoid(void_shape)

    @pyaedt_function_handler()
    def shape_to_polygon_data(self, shape):
        """Convert a shape to polygon data.

        Parameters
        ----------
        shape : str
            Type of the shape to convert. Options are ``"rectangle"`` and ``"polygon"``.
        """
        if shape.type == "polygon":
            return self._createPolygonDataFromPolygon(shape)
        elif shape.type == "rectangle":
            return self._createPolygonDataFromRectangle(shape)
        else:
            self._logger.error("Unsupported shape type %s when creating a polygon primitive.", shape.type)
            return None

    @pyaedt_function_handler()
    def _createPolygonDataFromPolygon(self, shape):
        points = shape.points
        if not self._validatePoint(points[0]):
            self._logger.error("Error validating point.")
            return None
        arcs = []
        is_parametric = False
        for i in range(len(points) - 1):
            if i == 0:
                startPoint = points[-1]
                endPoint = points[i]
            else:
                startPoint = points[i - 1]
                endPoint = points[i]

            if not self._validatePoint(endPoint):
                return None
            startPoint = [self._edb_value(i) for i in startPoint]
            endPoint = [self._edb_value(i) for i in endPoint]
            if len(endPoint) == 2:
                is_parametric = (
                    is_parametric
                    or startPoint[0].IsParametric()
                    or startPoint[1].IsParametric()
                    or endPoint[0].IsParametric()
                    or endPoint[1].IsParametric()
                )
                arc = self._edb.Geometry.ArcData(
                    self._edb.Geometry.PointData(
                        self._edb_value(startPoint[0].ToDouble()), self._edb_value(startPoint[1].ToDouble())
                    ),
                    self._edb.Geometry.PointData(
                        self._edb_value(endPoint[0].ToDouble()), self._edb_value(endPoint[1].ToDouble())
                    ),
                )
                arcs.append(arc)
            elif len(endPoint) == 5:
                is_parametric = (
                    is_parametric
                    or startPoint[0].IsParametric()
                    or startPoint[1].IsParametric()
                    or endPoint[0].IsParametric()
                    or endPoint[1].IsParametric()
                    or endPoint[3].IsParametric()
                    or endPoint[4].IsParametric()
                )
                rotationDirection = self._edb.Geometry.RotationDirection.Colinear
                if endPoint[2].ToString() == "cw":
                    rotationDirection = self._edb.Geometry.RotationDirection.CW
                elif endPoint[2].ToString() == "ccw":
                    rotationDirection = self._edb.Geometry.RotationDirection.CCW
                else:
                    self._logger.error("Invalid rotation direction %s is specified.", endPoint[2])
                    return None
                arc = self._edb.Geometry.ArcData(
                    self._edb.Geometry.PointData(
                        self._edb_value(startPoint[0].ToDouble()), self._edb_value(startPoint[1].ToDouble())
                    ),
                    self._edb.Geometry.PointData(
                        self._edb_value(endPoint[0].ToDouble()), self._edb_value(endPoint[1].ToDouble())
                    ),
                    rotationDirection,
                    self._edb.Geometry.PointData(
                        self._edb_value(endPoint[3].ToDouble()), self._edb_value(endPoint[4].ToDouble())
                    ),
                )
                arcs.append(arc)
        polygon = self._edb.Geometry.PolygonData.CreateFromArcs(convert_py_list_to_net_list(arcs), True)
        if not is_parametric:
            return polygon
        else:
            k = 0
            for pt in points:
                point = [self._edb_value(i) for i in pt]
                new_points = self._edb.Geometry.PointData(point[0], point[1])
                if len(point) > 2:
                    k += 1
                polygon.SetPoint(k, new_points)
                k += 1
        return polygon

    @pyaedt_function_handler()
    def _validatePoint(self, point, allowArcs=True):
        if len(point) == 2:
            if not isinstance(point[0], (int, float, str)):
                self._logger.error("Point X value must be a number.")
                return False
            if not isinstance(point[1], (int, float, str)):
                self._logger.error("Point Y value must be a number.")
                return False
            return True
        elif len(point) == 5:
            if not allowArcs:
                self._logger.error("Arc found but arcs are not allowed in _validatePoint.")
                return False
            if not isinstance(point[0], (int, float, str)):
                self._logger.error("Point X value must be a number.")
                return False
            if not isinstance(point[1], (int, float, str)):
                self._logger.error("Point Y value must be a number.")
                return False
            if not isinstance(point[2], str) or point[2] not in ["cw", "ccw"]:
                self._logger.error("Invalid rotation direction {} is specified.")
                return False
            if not isinstance(point[3], (int, float, str)):
                self._logger.error("Arc center point X value must be a number.")
                return False
            if not isinstance(point[4], (int, float, str)):
                self._logger.error("Arc center point Y value must be a number.")
                return False
            return True
        else:
            self._logger.error("Arc point descriptor has incorrect number of elements (%s)", len(point))
            return False

    def _createPolygonDataFromRectangle(self, shape):
        if not self._validatePoint(shape.pointA, False) or not self._validatePoint(shape.pointB, False):
            return None
        pointA = self._edb.Geometry.PointData(self._edb_value(shape.pointA[0]), self._edb_value(shape.pointA[1]))
        pointB = self._edb.Geometry.PointData(self._edb_value(shape.pointB[0]), self._edb_value(shape.pointB[1]))
        points = Tuple[self._edb.Geometry.PointData, self._edb.Geometry.PointData](pointA, pointB)
        return self._edb.Geometry.PolygonData.CreateFromBBox(points)

    class Shape(object):
        """Shape class.

        Parameters
        ----------
        type : str, optional
            Type of the shape. Options are ``"circle"``, ``"rectangle"``, and ``"polygon"``.
            The default is ``"unknown``.
        pointA : optional
            Lower-left corner when ``type="rectangle"``. The default is ``None``.
        pointB : optional
            Upper-right corner when ``type="rectangle"``. The default is ``None``.
        centerPoint : optional
            Center point when ``type="circle"``. The default is ``None``.
        radius : optional
            Radius when ``type="circle"``. The default is ``None``.
        points : list, optional
            List of points when ``type="polygon"``. The default is ``None``.
        properties : dict, optional
            Dictionary of properties associated with the shape. The default is ``{}``.
        """

        def __init__(
            self, type="unknown", pointA=None, pointB=None, centerPoint=None, radius=None, points=None, properties={}
        ):
            self.type = type
            self.pointA = pointA
            self.pointB = pointB
            self.centerPoint = centerPoint
            self.radius = radius
            self.points = points
            self.properties = properties

    @pyaedt_function_handler()
    def parametrize_trace_width(self, nets_name, layers_name=None, parameter_name="trace_width", variable_value=None):
        """Parametrize a Trace on specific layer or all stackup.

        Parameters
        ----------
        nets_name : str, list
            name of the net or list of nets to parametrize.
        layers_name : str, optional
            name of the layer or list of layers to which the net to parametrize has to be included.
        parameter_name : str, optional
            name of the parameter to create.
        variable_value : str, float, optional
            value with units of parameter to create.
            If None, the first trace width of Net will be used as parameter value.

        Returns
        -------
        bool
        """
        if isinstance(nets_name, str):
            nets_name = [nets_name]
        if isinstance(layers_name, str):
            layers_name = [layers_name]
        for net_name in nets_name:
            var_server = False
            for p in self.paths:
                if p.GetNet().GetName() == net_name:
                    if not layers_name:
                        if not var_server:
                            if not variable_value:
                                variable_value = p.GetWidth()
                            result, var_server = self._pedb.add_design_variable(parameter_name, variable_value)
                        p.SetWidth(self._pedb.edb_value(parameter_name))
                    elif p.GetLayer().GetName() in layers_name:
                        if not var_server:
                            if not variable_value:
                                variable_value = p.GetWidth()
                            result, var_server = self._pedb.add_design_variable(parameter_name, variable_value)
                        p.SetWidth(self._pedb.edb_value(parameter_name))
        return True

    @pyaedt_function_handler()
    def unite_polygons_on_layer(self, layer_name=None, delete_padstack_gemometries=False):
        """Try to unite all Polygons on specified layer.

        Parameters
        ----------
        layer_name : str, optional
            Layer Name on which unite objects. If ``None``, all layers will be taken.
        delete_padstack_gemometries : bool, optional
            ``True`` to delete all padstack geometry.

        Returns
        -------
        bool
            ``True`` is successful.
        """
        if isinstance(layer_name, str):
            layer_name = [layer_name]
        if not layer_name:
            layer_name = list(self._pedb.core_stackup.signal_layers.keys())

        for lay in layer_name:
            self._logger.info("Uniting Objects on layer %s.", lay)
            poly_by_nets = {}
            if lay in list(self.polygons_by_layer.keys()):
                for poly in self.polygons_by_layer[lay]:
                    if not poly.GetNet().GetName() in list(poly_by_nets.keys()):
                        if poly.GetNet().GetName():
                            poly_by_nets[poly.GetNet().GetName()] = [poly]
                    else:
                        if poly.GetNet().GetName():
                            poly_by_nets[poly.GetNet().GetName()].append(poly)
            for net in poly_by_nets:
                list_polygon_data = [i.GetPolygonData() for i in poly_by_nets[net]]
                all_voids = [i.Voids for i in poly_by_nets[net]]
                a = self._edb.Geometry.PolygonData.Unite(convert_py_list_to_net_list(list_polygon_data))
                for item in a:
                    for v in all_voids:
                        for void in v:
                            if int(item.GetIntersectionType(void.GetPolygonData())) == 2:
                                item.AddHole(void.GetPolygonData())
                    poly = self._edb.Cell.Primitive.Polygon.Create(
                        self._active_layout, lay, self._pedb.core_nets.nets[net].net_object, item
                    )
                list_to_delete = [i for i in poly_by_nets[net]]
                for v in all_voids:
                    for void in v:
                        for poly in poly_by_nets[net]:
                            if int(void.GetPolygonData().GetIntersectionType(poly.GetPolygonData())) >= 2:
                                try:
                                    id = list_to_delete.index(poly)
                                except ValueError:
                                    id = -1
                                if id >= 0:
                                    list_to_delete.pop(id)

                [i.Delete() for i in list_to_delete]

        if delete_padstack_gemometries:
            self._logger.info("Deleting Padstack Definitions")
            for pad in self._pedb.core_padstack.padstacks:
                p1 = self._pedb.core_padstack.padstacks[pad].edb_padstack.GetData()
                if len(p1.GetLayerNames()) > 1:
                    self._pedb.core_padstack.remove_pads_from_padstack(pad)
        self.update_primitives()
        return True

    @pyaedt_function_handler()
    def setup_coplanar_instances(self, simulation_setup=None):
        # Coplanar circuit port support for intermediate layers for Package merged on Board
        """Iterate coplanar_instances.
        For each component, create a coplanar circuit port at each signalNet pin.
        Use the closest powerNet pin as a reference, regardless of component.
        """
        if not isinstance(simulation_setup, SimulationConfiguration):
            return False
        if not simulation_setup.coplanar_instances:
            return True

        layout = self._cell.GetLayout()
        l_inst = layout.GetLayoutInstance()

        signal_nets, power_nets, port_nets, noport_nets, floating_nets = self._edbutils.NetSetupInfo.GetEdbNets(
            layout, simulation_setup.NetSetup, None
        )  # NetSetup Attribute needs to be addressed in Simulation Configuration
        # success, topLayer, botLayer = edbUtils.HfssUtilities.GetTopBottomSignalLayers(layout)
        # topNm = topLayer.GetName()
        # botNm = botLayer.GetName()

        signal_net_names = list(signal_nets.Select(lambda obj: obj.GetName()))
        # powerNetNames = list(power_nets.Select(lambda obj: obj.GetName()))

        for inst in simulation_setup.coplanar_instances:
            comp = self._edb.Cell.Hierarchy.Component.FindByName(layout, inst)
            if comp.IsNull():
                self._logger.warning("SetupCoplanarInstances: could not find {0}".format(inst))
                continue

            # Get the portLayer based on the component's pin placement
            # cmpIsTop, cmpIsBot = edbUtils.HfssUtilities.GetComponentPlacementByPins(comp, topLayer, botLayer)
            cmp_layer = self._edb.Cell.Hierarchy.Component.GetPlacementLayer(comp)
            # portLayer = botLayer if cmpIsBot else topLayer
            port_layer = cmp_layer
            # portLayerNm = portLayer.GetName()

            # Get the bbox of the comp
            bb = self._edb.Geometry.PolygonData.CreateFromBBox(l_inst.GetLayoutObjInstance(comp, None).GetBBox())
            bb_c = bb.GetBoundingCircleCenter()
            # Expand x5 to create testing polygon...
            bb.Scale(5, bb_c)

            # Find the closest pin in the Ground/Power nets...
            hit = l_inst.FindLayoutObjInstance(bb, port_layer, power_nets)
            # Linux: cast to a list to avoid "ValueError: Type System.Collections.Generic.IEnumerable`1[TSource]
            # contains generic parameters"
            all_hits = list(list(hit.Item1.Items).Concat(list(hit.Item2.Items)))
            hit_pinsts = list(
                all_hits.Where(
                    lambda obj: obj.GetLayoutObj().GetObjType() == self._edb.Cell.LayoutObjType.PadstackInstance
                )
            )
            if not hit_pinsts.Any():
                self._logger.error("SetupCoplanarInstances: could not find a pin in the vicinity of {0}".format(inst))
                continue

            # Iterate each pin in the component that's on the signal nets and create a CircuitPort
            for ii, pin in enumerate(
                list(comp.LayoutObjs).Where(
                    lambda obj: obj.GetObjType() == self._edb.Cell.LayoutObjType.PadstackInstance
                    and obj.GetNet().GetName() in signal_net_names
                )
            ):
                pin_c = l_inst.GetLayoutObjInstance(pin, None).GetCenter()

                ref_pinst = None
                ref_pt = None
                ref_dist = None
                for hhLoi in hit_pinsts:
                    this_c = hhLoi.GetCenter()
                    this_dist = this_c.Distance(pin_c)
                    if ref_pt is None or this_dist < ref_dist:
                        ref_pinst = hhLoi.GetLayoutObj()
                        ref_pt = this_c
                        ref_dist = this_dist

                port_nm = "PORT_{0}_{1}@{2}".format(comp.GetName(), ii, pin.GetNet().GetName())
                self._edbutils.HfssUtilities.CreateCircuitPortFromPoints(
                    port_nm, layout, pin_c, port_layer, pin.GetNet(), ref_pt, port_layer, ref_pinst.GetNet()
                )
        return True

    @pyaedt_function_handler()
    def set_coax_port_attributes(self, simulation_setup=None):
        """1) Rename all ports using the following convention:
                PORT_<component>_<ii_count>@<net>
                For consistency with previous automation, if possible iterate in cfg-file order.

        2) Set coaxial ports with 0.125*sball_diam radial extent factor
        """

        if not isinstance(simulation_setup, SimulationConfiguration):
            return False
        net_names = []
        if simulation_setup.NetSetup:
            net_names = list(
                list(simulation_setup.NetSetup.Where(lambda nn: not nn.IsPwrGnd)).Select(lambda nn: nn.Name)
            )

        cmp_names = (
            simulation_setup.coax_instances
            if simulation_setup.coax_instances
            else [gg.GetName() for gg in self._builder.layout.Groups]
        )
        ii = 0
        for cc in cmp_names:
            cmp = self._edb.Cell.Hierarchy.Component.FindByName(self._builder.layout, cc)
            if cmp.IsNull():
                self._logger.warning("RenamePorts: could not find component {0}".format(cc))
                continue
            terms = list(
                list(cmp.LayoutObjs).Where(lambda obj: obj.GetObjType() == self._edb.Cell.LayoutObjType.Terminal)
            )

            for nn in net_names:
                for tt in list(terms.Where(lambda tt: tt.GetNet().GetName() == nn)):
                    if not tt.SetImpedance("50ohm"):
                        self._logger.warning("Could not set terminal {0} impedance as 5ohm".format(tt.GetName()))
                        continue

                    nparts = tt.GetName().split(".")
                    if nparts[1] == nn:
                        new_name = ".".join(
                            [nparts[0], nparts[2], nparts[1]]
                        )  # rename comp.net.pin --> comp.pin.net (as in ports created in edt GUI)
                        self._logger.info("rename port {0} --> {1}".format(tt.GetName(), new_name))
                        if not tt.SetName(new_name):
                            self._logger.warning("Could not rename terminal {0} as {1}".format(tt.GetName(), new_name))
                            continue
                    ii += 1

            if not simulation_setup.use_default_coax_port_radial_extension:
                radial_factor_multiplier = 0.125
                # Set the Radial Extent Factor
                typ = cmp.GetComponentType()
                if typ in [
                    self._edb.Definition.ComponentType.Other,
                    self._edb.Definition.ComponentType.IC,
                    self._edb.Definition.ComponentType.IO,
                ]:
                    cmp_prop = cmp.GetComponentProperty().Clone()
                    success, diam1, diam2 = cmp_prop.GetSolderBallProperty().GetDiameter()
                    if success and diam1 > 0:
                        radial_factor = "{0}meter".format(radial_factor_multiplier * diam1)
                        for tt in terms:
                            self._builder.SetHfssSolverOption(tt, "Radial Extent Factor", radial_factor)
                            self._builder.SetHfssSolverOption(tt, "Layer Alignment", "Upper")  # ensure this is also set

    @pyaedt_function_handler()
    def trim_component_reference_size(self, simulation_setup=None, trim_to_terminals=False):
        """Trim the common component reference to the minimally acceptable size.
        trimToTerminals: if True, reduce the reference to a box covering only the active terminals (i.e. those with
        ports).
                         if False, reduce the reference to the minimal size needed to cover all pins.
        """

        if not isinstance(simulation_setup, SimulationConfiguration):
            return False

        if not simulation_setup.coax_instances:
            return

        layout = self._cell.GetLayout()
        l_inst = layout.GetLayoutInstance()

        for inst in simulation_setup.coax_instances:
            comp = self._edb.Cell.Hierarchy.Component.FindByName(layout, inst)
            if comp.IsNull():
                continue

            terms_bbox_pts = self._get_terminals_bbox(comp, l_inst, trim_to_terminals)
            if not terms_bbox_pts:
                continue

            terms_bbox = self._edb.Geometry.PolygonData.CreateFromBBox(terms_bbox_pts)

            if trim_to_terminals:
                # Remove any pins that aren't interior to the Terminals bbox
                for pp in list(comp.LayoutObjs).Where(
                    lambda obj: obj.GetObjType() == self._edb.Cell.LayoutObjType.PadstackInstance
                ):
                    loi = l_inst.GetLayoutObjInstance(pp, None)
                    bb_c = loi.GetCenter()
                    if not terms_bbox.PointInPolygon(bb_c):
                        comp.RemoveMember(pp)

            # Set the port property reference size
            cmp_prop = comp.GetComponentProperty().Clone()
            port_prop = cmp_prop.GetPortProperty().Clone()
            port_prop.SetReferenceSizeAuto(False)
            port_prop.SetReferenceSize(
                terms_bbox_pts.Item2.X.ToDouble() - terms_bbox_pts.Item1.X.ToDouble(),
                terms_bbox_pts.Item2.Y.ToDouble() - terms_bbox_pts.Item1.Y.ToDouble(),
            )
            cmp_prop.SetPortProperty(port_prop)
            comp.SetComponentProperty(cmp_prop)

    @pyaedt_function_handler()
    def _get_terminals_bbox(self, comp, l_inst, terminals_only):
        terms_loi = []
        if terminals_only:
            for tt in list(comp.LayoutObjs).Where(
                lambda obj: obj.GetObjType() == self._edb.Cell.LayoutObjType.Terminal
            ):
                success, p_inst, lyr = tt.GetParameters()
                if success:
                    loi = l_inst.GetLayoutObjInstance(p_inst, None)
                    terms_loi.append(loi)
        else:
            for pi in list(comp.LayoutObjs).Where(
                lambda obj: obj.GetObjType() == self._edb.Cell.LayoutObjType.PadstackInstance
            ):
                loi = l_inst.GetLayoutObjInstance(pi, None)
                terms_loi.append(loi)

        if len(terms_loi) == 0:
            return None

        terms_bbox = List[self._edb.Geometry.PolygonData]()
        for loi in terms_loi:
            # Need to account for the coax port dimension
            bb = loi.GetBBox()
            ll = [bb.Item1.X.ToDouble(), bb.Item1.Y.ToDouble()]
            ur = [bb.Item2.X.ToDouble(), bb.Item2.Y.ToDouble()]
            # dim = 0.26 * max(abs(UR[0]-LL[0]), abs(UR[1]-LL[1]))  # 0.25 corresponds to the default 0.5
            # Radial Extent Factor, so set slightly larger to avoid validation errors
            dim = 0.30 * max(abs(ur[0] - ll[0]), abs(ur[1] - ll[1]))  # 0.25 corresponds to the default 0.5
            terms_bbox.Add(self._edb.Geometry.PolygonData(ll[0] - dim, ll[1] - dim, ur[0] + dim, ur[1] + dim))

        return self._edb.Geometry.PolygonData.GetBBoxOfPolygons(terms_bbox)

    @pyaedt_function_handler()
    def get_ports_number(self):
        port_list = []
        for term in self._builder.layout.Terminals:
            if str(term.GetBoundaryType()) == "PortBoundary":
                if "ref" not in term.GetName():
                    port_list.append(term)
        return port_list.Count

    @pyaedt_function_handler()
    def layout_defeaturing(self, simulation_setup=None):
        if not isinstance(simulation_setup, SimulationConfiguration):
            return False
        self._logger.info("Starting Layout Defeaturing")
        polygon_list, voids_list, traces_list, circles = self._collect_prims(self._builder)
        self._logger.info("Number of Polygons Found: {0}".format(str(polygon_list.Count)))
        self._logger.info("Number of Voids Found: {0}".format(str(voids_list.Count)))
        self._logger.info("Number of Traces Found: {0}".format(str(traces_list.Count)))
        self._logger.info("Number of Circles Found: {0}".format(str(circles.Count)))
        polygon_with_voids = self._get_poly_with_voids(polygon_list)
        self._logger.info("Number of Polygons with Voids Found: {0}".format(str(polygon_with_voids.Count)))

        # PadStkList = []
        PadStkInstances = self._builder.layout.PadstackInstances
        # for padstk in PadStkInstances:
        #    PadStkList.append(padstk)

        for Poly in polygon_list:
            # PolyLayout = Poly.GetLayout()
            poly_layer = Poly.GetLayer()
            # PolyLayerId = Poly.GetId()
            # PolyLayerName = PolyLayer.GetName()
            # PolyNet = Poly.GetNet()
            voids_from_current_poly = Poly.Voids

            # defeaturing the current polygon
            # Logger.Info("Defeaturing Polygon {0}".format(str(Poly.GetId())))

            new_poly_data = self._defeature_polygon(simulation_setup, Poly)
            Poly.SetPolygonData(new_poly_data)

            if voids_from_current_poly.Count > 0:
                for void in voids_from_current_poly:
                    # defeaturing voids from the current poylgon
                    void_data = void.GetPolygonData()
                    if void_data.Area() < float(simulation_setup.minimum_void_surface):
                        # print('MinimumVoidSuface:' + str(setup_info.MinimumVoidSuface))
                        # print('Void Area:' + str(VoidData.Area()))
                        void.Delete()
                        self._logger.warning(
                            "Defeaturing Polygon {0}: Deleting Void {1} area is lower than the minimum criteria".format(
                                str(Poly.GetId()), str(void.GetId())
                            )
                        )
                    else:
                        self._logger.info(
                            "Defeaturing Polygon {0}: Void {1}".format(str(Poly.GetId()), str(void.GetId()))
                        )
                        new_void_data = self._defeature_polygon(simulation_setup, void_data)
                        void.SetPolygonData(new_void_data)

    @pyaedt_function_handler()
    def _defeature_polygon(self, setup_info, poly):
        poly_data = poly.GetPolygonData()
        pts_list = []
        pts = poly_data.Points
        defeaturing_step = 1e-6
        if poly_data.Count <= 16:
            # defeaturing skipped for polygons with less than 16 points
            # Logger.Info("Polygon with less than 16 points skipping defeaturing")
            return poly_data

        for pt in pts:
            pts_list.append(pt)
        nb_ini_pts = pts_list.Count
        ind = 0
        minimum_distance = defeaturing_step  # 1e-6
        init_surf = poly_data.Area()
        nb_pts_removed = 0
        surf_dev = 0
        new_poly = None
        # print(setup_info.MaxSufDev)
        while (surf_dev < setup_info.max_suf_dev and pts_list.Count > 16 and minimum_distance < 1000e-6) and float(
            nb_pts_removed
        ) / float(nb_ini_pts) < 0.4:
            pts_list, nb_pts_removed = self._trim_polygon_points(pts, minimum_distance)
            new_poly = self._edb.Geometry.PolygonData(pts_list, True)
            current_surf = new_poly.Area()
            if current_surf == 0:
                surf_dev = 1
            else:
                surf_dev = abs(init_surf - current_surf) / init_surf
                minimum_distance = minimum_distance + defeaturing_step
        self._logger.info(
            "Defeaturing Polygon {0}: Final Surface Deviation = {1} ,  Maximum Distance(um) = {2}, "
            "Number of Points removed = {3}/{4}".format(
                str(poly.GetId()), str(surf_dev), str(minimum_distance * 1e6), str(nb_pts_removed), str(nb_ini_pts)
            )
        )
        return new_poly

    @pyaedt_function_handler()
    def _collect_prims(self, builder):
        circles = []
        poly = []
        voids = []
        traces = []

        for p in builder.layout.Primitives:
            if p.GetPrimitiveType() == self._edb.Cell.Primitive.PrimitiveType.Polygon:
                if not p.GetIsNegative():
                    poly.append(p)
                if p.GetIsNegative():
                    voids.append(p)
            if p.GetPrimitiveType() == self._edb.Cell.Primitive.PrimitiveType.Path:
                traces.append(p)
            if p.GetPrimitiveType() == self._edb.Cell.Primitive.PrimitiveType.Circle:
                circles.append(p)
        return poly, voids, traces, circles

    @pyaedt_function_handler()
    def _get_poly_with_voids(self, list_poly):
        poly_with_voids = []
        for p in list_poly:
            if p.HasVoids():
                poly_with_voids.append(p)
        return poly_with_voids

    @pyaedt_function_handler()
    def _trim_polygon_points(self, points, minimum_distance):
        pts_list = []
        ind = 0

        nb_pts_removed = 0
        for pt in points:
            pts_list.append(pt)
        # NbIniPts = pts_list.Count

        while ind < pts_list.Count - 2:
            pts_list, nb_pts_removed = self._get_point_list_with_minimum_distance(
                pts_list, minimum_distance, ind, nb_pts_removed
            )
            ind = ind + 1

        return pts_list, nb_pts_removed

    @pyaedt_function_handler()
    def _get_point_list_with_minimum_distance(self, pts_list, minimum_distance, ind, nb_pts_removed):
        pt_ind = ind + 1
        while pts_list[ind].Distance(pts_list[pt_ind]) < minimum_distance and pt_ind < pts_list.Count - 2:
            pts_list.RemoveAt(pt_ind)
            nb_pts_removed += 1
            pt_ind += 1

        return pts_list, nb_pts_removed

    @pyaedt_function_handler()
    def setup_net_classes(self, simulation_setup=None):
        if not isinstance(simulation_setup, SimulationConfiguration):
            return False
        layout = self._builder.cell.GetLayout()
        signal_nets, power_nets, port_nets, noport_nets, floating_nets = self._edbutils.NetSetupInfo.GetEdbNets(
            layout, simulation_setup.NetSetup, None
        )

        for obj in layout.Nets:
            obj.SetIsPowerGround(False)

        for obj in power_nets:
            obj.SetIsPowerGround(True)
            self._logger.info("POWER NET: {} pg={}".format(obj.GetName(), obj.IsPowerGround()))
