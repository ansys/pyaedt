"""
This module contains these classes: ``EdbLayout`` and ''Shape``.
"""

import warnings
from .general import *
from ..generic.general_methods import get_filename_without_extension, generate_unique_name
import math
try:
    import clr
    from System import Convert, String, Tuple
    from System import Double, Array
    from System.Collections.Generic import List
except ImportError:
    warnings.warn('This module requires pythonnet.')


class EdbLayout(object):
    """EdbLayout class."""

    def __init__(self, parent):
        self._prims = []
        self._parent = parent
        self._primitives_by_layer = {}
        #self.update_primitives()

    @property
    def _edb(self):
        return self._parent.edb

    @property
    def _messenger(self):
        """ """
        return self._parent._messenger

    @property
    def _builder(self):
        return self._parent.builder

    @property
    def _edb_value(self):
        return self._parent.edb_value

    @property
    def _edbutils(self):
        return self._parent.edbutils

    @property
    def _active_layout(self):
        return self._parent.active_layout

    @property
    def _cell(self):
        return self._parent.active_cell

    @property
    def db(self):
        return self._parent.db

    @property
    def layers(self):
        """Dictionary of layers.

        Returns
        -------
        dict
            Dictionary of layers.
        """
        return self._parent.core_stackup.stackup_layers.layers

    @aedt_exception_handler
    def update_primitives(self):
        """
        Update a primitives list from the EDB database.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.
        """
        layoutInstance = self._active_layout.GetLayoutInstance()
        layoutObjectInstances = layoutInstance.GetAllLayoutObjInstances()
        for el in layoutObjectInstances.Items:
            self._prims.append(el.GetLayoutObj())
        for lay in self.layers:
            self._primitives_by_layer[lay] = self.get_polygons_by_layer(lay)
        print("Primitives Updated")
        return True

    @property
    def primitives(self):
        """List of primitives.

        Returns
        -------
        list
            List of primitives.
        """
        if not self._prims:
            self.update_primitives()
        return self._prims

    @property
    def polygons_by_layer(self):
        """Dictionary of primitives with layer names as keys.

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
        """List of rectangles.

        Returns
        -------
        list
            List of rectangles.

        """
        prims = []
        for el in self.primitives:
            if "Rectangle" in el.ToString():
                prims.append(el)
        return prims

    @property
    def circles(self):
        """List of circles.

        Returns
        -------
        list
            List of circles.

        """
        prims = []
        for el in self.primitives:
            if "Circle" in el.ToString():
                prims.append(el)
        return prims

    @property
    def paths(self):
        """List of paths.

        Returns
        -------
        list
            List of paths.
        """
        prims = []
        for el in self.primitives:
            if "Path" in el.ToString():
                prims.append(el)
        return prims

    @property
    def bondwires(self):
        """List of bondwires.

        Returns
        -------
        list
            List of bondwires.
        """
        prims = []
        for el in self.primitives:
            if "Bondwire" in el.ToString():
                prims.append(el)
        return prims

    @property
    def polygons(self):
        """List of polygons.

        Returns
        -------
        list
            List of polygons.
        """
        prims = []
        for el in self.primitives:
            if "Polygon" in el.ToString():
                prims.append(el)
        return prims

    @aedt_exception_handler
    def get_polygons_by_layer(self, layer_name, net_list=None):
        """Retrieve polygons by a layer.
        
        Parameters
        ----------
        layer_name: str
            Name of the layer.
        net_list : list, optional
            List of net names.
        
        Returns
        -------
        list
            List of primitive objects.
        """
        objinst=[]
        for el in self.polygons:
            if el.GetLayer().GetName() == layer_name:
                if net_list and el.GetNet().GetName() in net_list:
                    objinst.append(el)
                else:
                    objinst.append(el)
        return objinst

    @aedt_exception_handler
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
            bbox = polygon.GetPolygonData().GetBBox()
            bounding =[bbox.Item1.X.ToDouble(), bbox.Item1.Y.ToDouble(), bbox.Item2.X.ToDouble(), bbox.Item2.Y.ToDouble()]
        except:
            pass
        return bounding

    @aedt_exception_handler
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
        i=0
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

    @aedt_exception_handler
    def parametrize_polygon(self, polygon,selection_polygon, offset_name="offsetx", origin=None):
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
        # bounding = self.get_polygon_bounding_box(polygon)
        # bounding2 =self.get_polygon_bounding_box(selection_polygon)
        # center = [(bounding[0] + bounding[2]) / 2, (bounding[1] + bounding[3]) / 2]
        # center2 = [(bounding2[0] + bounding2[2]) / 2, (bounding2[1] + bounding2[3]) / 2]

        if not origin:
            origin = [center[0] + float(x1)*10000, center[1] + float(y1)*10000]

        var_server = self._cell.GetVariableServer()
        var_server.AddVariable(offset_name,self._edb_value(0.0), True)
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
                            self._edb.Utility.Value(point.X.ToString() + '{}*{}'.format(xcoeff, offset_name), var_server),
                            self._edb.Utility.Value(point.Y.ToString() + '{}*{}'.format(ycoeff, offset_name), var_server))
                        poligon_data.SetPoint(i, new_points)
                    prev_point = point
                    i += 1
                else:
                    continue_iterate = False
            except:
                continue_iterate = False
        polygon.SetPolygonData(poligon_data)
        return True

    @aedt_exception_handler
    def create_path(self, path_list, layer_name, width=1, net_name="", start_cap_style="Round", end_cap_style="Round",
                    corner_style="Round"):
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
            Style of the corner. Options are ``"Round"`` and 
            ``"Flat"``. The default is ``"Round"``.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.
        """
        net = self._parent.core_nets.find_or_create_net(net_name)
        if start_cap_style.lower() == "round":
            start_cap_style = 0
        elif start_cap_style.lower() == "extended":
            start_cap_style = 2
        else:
            start_cap_style = 1
        if end_cap_style.lower() == "round":
            end_cap_style = 0
        elif end_cap_style.lower() == "extended":
            end_cap_style = 2
        else:
            end_cap_style = 1
        if corner_style.lower() == "round":
            corner_style = 0
        else:
            corner_style = 1
        pointlists = [self._edb.Geometry.PointData(self._edb_value(i[0]), self._edb_value(i[1])) for i in path_list.points]
        polygonData =  self._edb.Geometry.PolygonData(convert_py_list_to_net_list(pointlists), False)
        polygon = self._edb.Cell.Primitive.Path.Create(
            self._active_layout,
            layer_name,
            net,
            self._edb_value(width),
            start_cap_style,
            end_cap_style,
            corner_style,
            polygonData)
        if polygon.IsNull():
            self._messenger.add_error_message('Null path created')
            return False
        else:
            self.update_primitives()
            return True

    @aedt_exception_handler
    def create_polygon(self, main_shape,  layer_name, voids=[], net_name=""):
        """Create a new polygon based on a list of points and voids.

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
        bool
            ``True`` when successful, ``False`` when failed.
        """
        net = self._parent.core_nets.find_or_create_net(net_name)
        polygonData = self.shape_to_polygon_data(main_shape)
        if polygonData is None or polygonData.IsNull():
            self._messenger.add_error_message('Failed to create main shape polygon data')
            return False
        for void in voids:
            voidPolygonData = self.shape_to_polygon_data(void)
            if voidPolygonData is None or voidPolygonData.IsNull():
                self._messenger.add_error_message('Failed to create void polygon data')
                return False
            polygonData.AddHole(voidPolygonData)
        polygon = self._edb.Cell.Primitive.Polygon.Create(
            self._active_layout,
            layer_name,
            net,
            polygonData)
        if polygon.IsNull():
            self._messenger.add_error_message('Null polygon created')
            return False
        else:
            self.update_primitives()
            return True

    def shape_to_polygon_data(self, shape):
        """Convert a shape to polygon data.

        Parameters
        ----------
        shape : str
            Type of the shape to convert. Options are ``"rectangle"`` and ``"polygon"``.
        """
        if shape.type == 'polygon':
            return self._createPolygonDataFromPolygon(shape)
        elif shape.type == 'rectangle':
            return self._createPolygonDataFromRectangle(shape)
        else:
            self._messenger.add_error_message('Unsupported shape type {} when creating a polygon primitive.'.format(shape.type))
            return None

    def _createPolygonDataFromPolygon(self, shape):
        points = shape.points
        if not self._validatePoint(points[0]):
            self._messenger.add_error_message('Error validating point.')
            return None
        arcs = []
        for i in range(1, len(points)):
            startPoint = points[i - 1]
            endPoint = points[i]
            if not self._validatePoint(endPoint):
                return None
            startPoint = [self._edb_value(i) for i in startPoint]
            endPoint = [self._edb_value(i) for i in endPoint]
            if len(endPoint) == 2:
                arc = self._edb.Geometry.ArcData(
                    self._edb.Geometry.PointData(startPoint[0], startPoint[1]),
                    self._edb.Geometry.PointData(endPoint[0], endPoint[1]))
                arcs.append(arc)
            elif len(endPoint) == 5:
                rotationDirection = self._edb.Geometry.RotationDirection.Colinear
                if endPoint[2].ToString() == 'cw':
                    rotationDirection = self._edb.Geometry.RotationDirection.CW
                elif endPoint[2].ToString() == 'ccw':
                    rotationDirection = self._edb.Geometry.RotationDirection.CCW
                else:
                    self._messenger.add_error_message('Invalid rotation direction {} is specified.'.format(endPoint[2]))
                    return None
                arc = self._edb.Geometry.ArcData(
                    self._edb.Geometry.PointData(startPoint[0], startPoint[1]),
                    self._edb.Geometry.PointData(endPoint[0], endPoint[1]),
                    rotationDirection,
                    self._edb.Geometry.PointData(endPoint[3], endPoint[4]))
                arcs.append(arc)
        return self._edb.Geometry.PolygonData.CreateFromArcs(convert_py_list_to_net_list(arcs), True)

    def _validatePoint(self, point, allowArcs=True):
        if len(point) == 2:
            if not isinstance(point[0], (int,float)):
                self._messenger.add_error_message('Point X value must be a float.')
                return False
            if not isinstance(point[1], (int,float)):
                self._messenger.add_error_message('Point Y value must be a float.')
                return False
            return True
        elif len(point) == 5:
            if not allowArcs:
                self._messenger.add_error_message('Arc found but arcs are not allowed in _validatePoint.')
                return False
            if not isinstance(point[0], (int,float)):
                self._messenger.add_error_message('Point X value must be a float.')
                return False
            if not isinstance(point[1], (int,float)):
                self._messenger.add_error_message('Point Y value must be a float.')
                return False
            if not isinstance(point[2], str) or point[2] not in ['cw', 'ccw']:
                self._messenger.add_error_message('Invalid rotation direction {} is specified.')
                return False
            if not isinstance(point[3], (int,float)):
                self._messenger.add_error_message('Arc center point X value must be a float.')
                return False
            if not isinstance(point[4], (int,float)):
                self._messenger.add_error_message('Arc center point Y value must be a float.')
                return False
            return True
        else:
            self._messenger.add_error_message('Arc point descriptor has incorrect number of elements ({})'.format(len(point)))
            return False

    def _createPolygonDataFromRectangle(self, shape):
        if not self._validatePoint(shape.pointA, False) or not self._validatePoint(shape.pointB, False):
            return None
        pointA = self._edb.Geometry.PointData(self._edb_value(shape.pointA[0]),self._edb_value(shape.pointA[1]))
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
        def __init__(self, type='unknown', pointA=None, pointB=None, centerPoint=None, radius=None, points=None,
                         properties={}):
                self.type = type
                self.pointA = pointA
                self.pointB = pointB
                self.centerPoint = centerPoint
                self.radius = radius
                self.points = points
                self.properties = properties
