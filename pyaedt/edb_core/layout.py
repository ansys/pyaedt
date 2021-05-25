"""
Components Class
-------------------

This class manages Edb Components and related methods

Disclaimer
==========

**Copyright (c) 1986-2021, ANSYS Inc. unauthorised use, distribution or duplication is prohibited**

**This tool release is unofficial and not covered by standard Ansys Support license.**



"""
import clr
import os
import re
from .general import *
from ..generic.general_methods import get_filename_without_extension, generate_unique_name
from System import Convert, String
from System import Double, Array
from System.Collections.Generic import List
import random


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

    def __init__(self, parent):
        self.parent = parent


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

    @property
    def polygons(self):
        """:return: list of polygons"""
        layoutInstance = self.active_layout.GetLayoutInstance()
        layoutObjectInstances = layoutInstance.GetAllLayoutObjInstances()
        objs = [el.GetLayoutObj() for el in layoutObjectInstances.Items if el.GetLayoutObj().GetType().Name == "Path"]
        return objs

    def get_polygons_by_layer(self, layer_name):
        """Return the polygons beloning to a specific layer
        
        :example:

        Parameters
        ----------
        layer_name :
            str layer name

        Returns
        -------
        type
            list of polygons

        >>> poly = edb_core.core_primitives.get_polygons_by_layer("GND")
        """
        objinst=[]
        for el in self.polygons:
            if el.GetLayer().GetName() == layer_name:
                objinst.append(el)
        return objinst

    def get_polygon_bounding_box(self, polygon):
        """Return the polygon bounding box
        
        :example:

        Parameters
        ----------
        polygon :
            edb_core polygon

        Returns
        -------
        type
            bouding box [-x,-y,+x,+y]

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
        
        :example:

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
