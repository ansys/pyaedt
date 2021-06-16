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
    from System import Convert, String
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
        """ """
        return self.parent.edb

    @property
    def messenger(self):
        """ """
        return self.parent.messenger

    def __init__(self,parent):
        self.parent = parent
        self._primitives = {}
        self.init_primitives()


    @property
    def builder(self):
        """ """
        return self.parent.builder

    @property
    def edb(self):
        """ """
        return self.parent.edb

    @property
    def edb_value(self):
        """ """
        return self.parent.edb_value

    @property
    def edbutils(self):
        """ """
        return self.parent.edbutils

    @property
    def active_layout(self):
        """ """
        return self.parent.active_layout

    @property
    def cell(self):
        """ """
        return self.parent.cell

    @property
    def db(self):
        """ """
        return self.parent.db

    @property
    def layers(self):
        """ """
        return self.parent.core_stackup.stackup_layers.layers

    @aedt_exception_handler
    def init_primitives(self):
        for lay in self.layers:
            self._primitives[lay] = self.get_polygons_by_layer(lay)

    @property
    def polygons(self):
        """:return: list of polygons"""
        layoutInstance = self.active_layout.GetLayoutInstance()
        layoutObjectInstances = layoutInstance.GetAllLayoutObjInstances()
        objs = [el.GetLayoutObj() for el in layoutObjectInstances.Items if el.GetLayoutObj().GetType().Name == "Polygon"]
        return objs

    @aedt_exception_handler
    def get_polygons_by_layer(self, layer_name, net_list=None):
        """
        return

        :param layer_name: str layer name
        :param net_list: list of net name
        :return: list of Primitive object
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
        
        :examples:

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
        
        :examples:

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
