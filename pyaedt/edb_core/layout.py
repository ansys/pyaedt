"""
Components Class
-------------------

This class manages Edb Components and related methods


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

class Primitive(object):

    def __init__(self,parent, id):
        self.parent = parent
        self.id = id
        self.poly = []
        self.paths = []

class EdbLayout(object):
    """HFSS 3DLayout object"""
    @property
    def edb(self):
        return self.parent.edb

    @property
    def messenger(self):
        """ """
        return self.parent.messenger

    def __init__(self,parent):
        self._prims = []
        self.parent = parent
        self._primitives_by_layer = {}
        self.update_primitives()


    @property
    def builder(self):
        return self.parent.builder


    @property
    def edb_value(self):
        return self.parent.edb_value

    @property
    def edbutils(self):
        return self.parent.edbutils

    @property
    def active_layout(self):
        return self.parent.active_layout

    @property
    def cell(self):
        return self.parent.cell

    @property
    def db(self):
        return self.parent.db

    @property
    def layers(self):
        """

        Returns
        -------
        dict
            Dictionary of Layers
        """
        return self.parent.core_stackup.stackup_layers.layers

    @aedt_exception_handler
    def update_primitives(self):
        """
        Update Primitives list from Edb Database

        Returns
        -------
        bool
            ``True`` if succeeded
        """

        layoutInstance = self.active_layout.GetLayoutInstance()
        layoutObjectInstances = layoutInstance.GetAllLayoutObjInstances()
        for el in layoutObjectInstances.Items:
            self._prims.append(el.GetLayoutObj())
        for lay in self.layers:
            self._primitives_by_layer[lay] = self.get_polygons_by_layer(lay)
        return True

    @property
    def primitives(self):
        """

        Returns
        -------
        list
            list of all primitives

        """
        if not self._prims:
            self.update_primitives()
        return self._prims

    @property
    def polygons_by_layer(self):
        """

        Returns
        -------
        dict
            Dictionary of primitives with Layer Name as keys

        """
        if not self._primitives_by_layer:
            self.update_primitives()
        return self._primitives_by_layer

    @property
    def rectangles(self):
        """

        Returns
        -------
        list
            list of all rectangles

        """
        prims = []
        for el in self.primitives:
            if "Rectangle" in el.ToString():
                prims.append(el)
        return prims

    @property
    def circles(self):
        """

        Returns
        -------
        list
            list of all circles

        """
        prims = []
        for el in self.primitives:
            if "Circle" in el.ToString():
                prims.append(el)
        return prims

    @property
    def paths(self):
        """

        Returns
        -------
        list
            list of all paths

        """
        prims = []
        for el in self.primitives:
            if "Path" in el.ToString():
                prims.append(el)
        return prims

    @property
    def bondwires(self):
        """

        Returns
        -------
        list
            list of all bondwires

        """
        prims = []
        for el in self.primitives:
            if "Bondwire" in el.ToString():
                prims.append(el)
        return prims

    @property
    def polygons(self):
        """

        Returns
        -------
        list
            list of all polygons

        """
        prims = []
        for el in self.primitives:
            if "Polygon" in el.ToString():
                prims.append(el)
        return prims

    @aedt_exception_handler
    def get_polygons_by_layer(self, layer_name, net_list=None):
        """

        Parameters
        ----------
        layer_name : str
            layer name
        net_list : list
            List of net names

        Returns
        -------
        list
            list of Primitive object
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
        """Return the polygon bounding box
        

        Parameters
        ----------
        polygon :
            edb_core polygon

        Returns
        -------
        list
            bounding box [-x,-y,+x,+y]

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
        """Return Polygon Points list. for Arcs, 1 point will be returned
        
        Parameters
        ----------
        polygon :
            edb_core polygon

        Returns
        -------
        type
            list of list of double

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
        """Parametrize pieces of polygon based on another polygon.

        Parameters
        ----------
        polygon : Polygon
            Polygon to parametrize.
        selection_polygon : Polygon
            Polygon to use as filter.
        offset_name : str, optional
            Name of the variable to create.  Defaults to ``"offsetx"``.
        origin : list, optional
            List of x and y origin. Default is ``[0, 0]``. It impacts the vector 
            computation and is needed to determine expansion direction. If 
            ``None``, it will be computed from the polygon's center.

        Returns
        -------
        bool
            Returns ``True`` when successful.
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

        var_server = self.parent.active_cell.GetVariableServer()
        var_server.AddVariable(offset_name,self.edb_value(0.0), True)
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

                        new_points = self.edb.Geometry.PointData(
                            self.edb.Utility.Value(point.X.ToString() + '{}*{}'.format(xcoeff, offset_name), var_server),
                            self.edb.Utility.Value(point.Y.ToString() + '{}*{}'.format(ycoeff, offset_name), var_server))
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
        Create a path based on a list of points

        Parameters
        ----------
        path_list : Shape
            list of points
        layer_name : str
            name of the layer on which path will be created
        width : float
            path width
        net_name : str
            net name
        start_cap_style : str
            Start Cap file. "Round", "Extended", "Flat"
        end_cap_style : str
            End Cap file. "Round", "Extended", "Flat"
        corner_style : str
            Corner Style: "Round" or "Flat"

        Returns
        -------
        bool
        """
        net = self.parent.core_nets.find_or_create_net(net_name)
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
        pointlists = [self.edb.Geometry.PointData(self.edb_value(i[0]), self.edb_value(i[1])) for i in path_list.points]
        polygonData =  self.edb.Geometry.PolygonData(convert_py_list_to_net_list(pointlists), False)
        polygon = self.edb.Cell.Primitive.Path.Create(
            self.active_layout,
            layer_name,
            net,
            self.edb_value(width),
            start_cap_style,
            end_cap_style,
            corner_style,
            polygonData)
        if polygon.IsNull():
            self.messenger.add_error_message('Null path created')
            return False
        else:
            self.update_primitives()
            return True

    @aedt_exception_handler
    def create_polygon(self, main_shape,  layer_name, voids=[], net_name=""):
        """
        Create a new polygon based on list of points and voids

        Parameters
        ----------
        main_shape : Shape
            shape main object
        layer_name : str
            layer on which polygon will be created
        voids : list
            list of Shape object for voids
        net_name : str
            name of the net

        Returns
        -------
        bool
        """
        net = self.parent.core_nets.find_or_create_net(net_name)
        polygonData = self.shape_to_polygon_data(main_shape)
        if polygonData is None or polygonData.IsNull():
            self.messenger.add_error_message('Failed to create main shape polygon data')
            return False
        for void in voids:
            voidPolygonData = self.shape_to_polygon_data(void)
            if voidPolygonData is None or voidPolygonData.IsNull():
                self.messenger.add_error_message('Failed to create void polygon data')
                return False
            polygonData.AddHole(voidPolygonData)
        polygon = self.edb.Cell.Primitive.Polygon.Create(
            self.active_layout,
            layer_name,
            net,
            polygonData)
        if polygon.IsNull():
            self.messenger.add_error_message('Null polygon created')
            return False
        else:
            self.update_primitives()
            return True

    def shape_to_polygon_data(self, shape):
        if shape.type == 'polygon':
            return self._createPolygonDataFromPolygon(shape)
        elif shape.type == 'rectangle':
            return self._createPolygonDataFromRectangle(shape)
        else:
            self.messenger.add_error_message('Unsupported shape type {} when creating polygon primitive'.format(shape.type))
            return None

    def _createPolygonDataFromPolygon(self, shape):
        points = shape.points
        if not self._validatePoint(points[0]):
            self.messenger.add_error_message('Error validating point')
            return None
        arcs = []
        for i in range(1, len(points)):
            startPoint = points[i - 1]
            endPoint = points[i]
            if not self._validatePoint(endPoint):
                return None
            startPoint = [self.edb_value(i) for i in startPoint]
            endPoint = [self.edb_value(i) for i in endPoint]
            if len(endPoint) == 2:
                arc = self.edb.Geometry.ArcData(
                    self.edb.Geometry.PointData(startPoint[0], startPoint[1]),
                    self.edb.Geometry.PointData(endPoint[0], endPoint[1]))
                arcs.append(arc)
            elif len(endPoint) == 5:
                rotationDirection = self.edb.Geometry.RotationDirection.Colinear
                if endPoint[2].ToString() == 'cw':
                    rotationDirection = self.edb.Geometry.RotationDirection.CW
                elif endPoint[2].ToString() == 'ccw':
                    rotationDirection = self.edb.Geometry.RotationDirection.CCW
                else:
                    self.messenger.add_error_message('Invalid rotation direction {} specified'.format(endPoint[2]))
                    return None
                arc = self.edb.Geometry.ArcData(
                    self.edb.Geometry.PointData(startPoint[0], startPoint[1]),
                    self.edb.Geometry.PointData(endPoint[0], endPoint[1]),
                    rotationDirection,
                    self.edb.Geometry.PointData(endPoint[3], endPoint[4]))
                arcs.append(arc)
        return self.edb.Geometry.PolygonData.CreateFromArcs(convert_py_list_to_net_list(arcs), True)

    def _validatePoint(self, point, allowArcs=True):
        if len(point) == 2:
            if not isinstance(point[0], (int,float)):
                self.messenger.add_error_message('Point X value must be a float')
                return False
            if not isinstance(point[1], (int,float)):
                self.messenger.add_error_message('Point Y value must be a float')
                return False
            return True
        elif len(point) == 5:
            if not allowArcs:
                self.messenger.add_error_message('Arc found but arcs not allowed in _validatePoint')
                return False
            if not isinstance(point[0], (int,float)):
                self.messenger.add_error_message('Point X value must be a float')
                return False
            if not isinstance(point[1], (int,float)):
                self.messenger.add_error_message('Point Y value must be a float')
                return False
            if not isinstance(point[2], str) or point[2] not in ['cw', 'ccw']:
                self.messenger.add_error_message('Invalid rotation direction')
                return False
            if not isinstance(point[3], (int,float)):
                self.messenger.add_error_message('Arc center point X value must be a float')
                return False
            if not isinstance(point[4], (int,float)):
                self.messenger.add_error_message('Arc center point Y value must be a float')
                return False
            return True
        else:
            self.messenger.add_error_message('Arc point descriptor has incorrect number of elements ({})'.format(len(point)))
            return False

    def _createPolygonDataFromRectangle(self, shape):
        if not self._validatePoint(shape.pointA, False) or not self._validatePoint(shape.pointB, False):
            return None
        pointA = self.edb.Geometry.PointData(self.edb_value(shape.pointA[0]),self.edb_value(shape.pointA[1]))
        pointB = self.edb.Geometry.PointData(self.edb_value(shape.pointB[0]), self.edb_value(shape.pointB[1]))
        points = Tuple[self.edb.Geometry.PointData, self.edb.Geometry.PointData](pointA, pointB)
        return self.edb.Geometry.PolygonData.CreateFromBBox(points)

    class Shape(object):
        def __init__(self, type='unknown', pointA=None, pointB=None, centerPoint=None, radius=None, points=None,
                     properties={}):
            """Shape constructor

            Keyword Arguments:
            type -- type of shape ('circle' or 'rectangle' or 'polygon')
            pointA -- lower-left corner of 'rectangle' type shape
            pointB -- upper-right corner of 'rectangle' type shape
            centerPoint -- center point of 'circle' type shape
            radius -- radius of 'circle' type shape
            points -- list of point data lists for 'polygon' type shape
            properties -- dictionary of properties associated with the shape
            """
            self.type = type
            self.pointA = pointA
            self.pointB = pointB
            self.centerPoint = centerPoint
            self.radius = radius
            self.points = points
            self.properties = properties
