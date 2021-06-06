"""
Components Class
-------------------

This class manages Edb Components and related methods


"""
import warnings
from .general import *
from ..generic.general_methods import get_filename_without_extension, generate_unique_name


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

    def get_polygon_bounding_box(self, polygon):
        """Return the polygon bounding box
        
        :examples:

        Parameters
        ----------
        polygon :
            edb_core polygon

        Returns
        -------
        type
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
