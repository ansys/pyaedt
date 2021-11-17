"""
This module .
"""

from pyaedt import aedt_exception_handler
from pyaedt.edb_core.layout import EdbLayout
from pyaedt.edb_core.padstack import EdbPadstacks

class Trace(object):
    """
    Manage EDB trace
    """
    def __init__(self, width="0.0", point_list=None, layer="", net_name=""):
        if point_list is None:
            point_list = [[0.0, 0.0], [1e-3, 0.0]]
        self.point_list = point_list
        self.width = width
        self.layer = layer
        self.net_name = net_name
        self.layout_core = EdbLayout(self)

    @aedt_exception_handler
    def place_line(self):

        path = self.layout_core.Shape("polygon", points=self.point_list)
        edb_path = self.layout_core.create_path(path, self.layer, self.width, self.net_name, start_cap_style="Flat",
                                                   end_cap_style="Flat")
        return edb_path

class via_def(object):
    def __init__(self, name="via_def", hole_diam="", pad_diam="", anti_pad_diam="", start_layer="top",
                 stop_layer="bottom", antipad_shape="Circle", x_size="", y_size="", corner_rad=""):
        self.name = name
        self.hole_diam = hole_diam
        self.pad_diam = pad_diam
        self.anti_pad_diam = anti_pad_diam
        self.start_layer = start_layer
        self.stop_layer = stop_layer
        self.anti_pad_shape = antipad_shape
        self.x_size = x_size
        self.y_size = y_size
        self.corner_rad = corner_rad
        self.padstack_core = EdbPadstacks(self)

    def add_via_def_to_edb(self):
        self.padstack_core.create_padstack(padstackname=self.name, holediam=self.hole_diam,
                                          paddiam=self.pad_diam,
                                          antipaddiam=self.anti_pad_diam,
                                          startlayer=self.start_layer,
                                          endlayer=self.stop_layer,
                                          antipad_shape=self.anti_pad_shape,
                                          x_size=self.x_size,
                                          y_size=self.y_size,
                                          corner_radius=self.corner_rad)

class via_instance(object):
    def __init__(self, pos_x="", pos_y="", rotation=0.0, net_name=""):
        self.pos_x = pos_x
        self.pos_y = pos_y
        self.rotation = rotation
        self.pos = [self.pos_x, self.pos_y]
        self.net_name = net_name
        self.padstack_core = EdbPadstacks(self)

    def place_via(self, viadef=via_def()):
        edb_padstanck_inst = self.padstack_core.place_padstack(
            position=self.pos, definition_name=viadef.name, net_name=self.net_name, via_name="", rotation=self.rotation,
            fromlayer=viadef.start_layer, tolayer=viadef.stop_layer)
        return  edb_padstanck_inst

class rectangle(object):
    def __init__(self, lower_left_corner=[], upper_right_corner=[], voids=None):
        self.lower_left_corner = lower_left_corner
        self.upper_right_corner = upper_right_corner
        self.voids = voids
        self.padstack_core = EdbPadstacks(self)
        self.layout_core = EdbLayout(self)

    def place_rectangle(self, layer_name="top", net_name=""):
        pts = [[self.lower_left_corner[0], self.lower_left_corner[1]],
               [self.upper_right_corner[0], self.lower_left_corner[1]],
               [self.upper_right_corner[0], self.upper_right_corner[1]],
               [self.lower_left_corner[0], self.upper_right_corner[1]]
               ]
        shape = self.layout_core.Shape("polygon", points=pts)
        if self.voids:
            shape_void = [self.layout_core.Shape("polygon", points=self.voids)]
        else:
            shape_void = []
        poly = self.layout_core.create_polygon(main_shape=shape, layer_name=layer_name, 
                                               voids=shape_void, net_name=net_name)
        return poly
