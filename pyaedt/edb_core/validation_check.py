# from pyaedt import Edb


class ValidationCheck(object):
    def __init__(self, pedb):
        self._pedb = pedb
        self._primitives_dict = {}
        self._padstack_instances_dict = {}
        self._primitives_rtreee = {}
        self._padstack_instances_rtree = {}

    @property
    def _layout(self):
        """Get layout.

        Returns
        -------
        :class:` :class:`pyaedt.edb_core.dotnet.layout.LayoutDotNet`
        """
        return self._pedb.layout

    @property
    def _logger(self):
        """EDB logger."""
        return self._pedb.logger

    def _init_primitives(self):
        for net_name, net in self._pedb.nets.nets.items():
            self._primitives_dict[net_name] = net.primitives
        for net_name, prim_list in self._primitives_dict.items():
            self._primitives_rtreee[net_name] = self._pedb._edb.Geometry.RTree()
            for prim in prim_list:
                if prim.type == "Path":
                    edb_obj = prim.convert_to_polygon()
                    rtree_obj = self._pedb._edb.Geometry.RTreeObj(edb_obj.polygon_data.edb_api, prim)
                    try:
                        self._primitives_rtreee[net_name].Insert(rtree_obj)
                    except:
                        pass
                elif prim.type == "Polygon":
                    rtree_obj = self._pedb._edb.Geometry.RTreeObj(prim.polygon_data.edb_api, prim)
                    try:
                        self._primitives_rtreee[net_name].Insert(rtree_obj)
                    except:
                        pass
        for padstck in list(self._pedb.padstacks.padstack_instances.values()):
            if padstck.net_name in self._padstack_instances_dict:
                self._padstack_instances_dict[padstck.net_name].append(padstck)
            else:
                self._padstack_instances_dict[padstck.net_name] = [padstck]
        for net_name, padstack_instance_list in self._padstack_instances_dict.items():
            self._padstack_instances_rtree[net_name] = self._pedb._edb.Geometry.RTree()
            for padstack_inst in padstack_instance_list:
                shape = self._pedb.modeler.Shape("polygon", points=padstack_inst.bounding_box)
                bb_box = self._pedb.modeler.shape_to_polygon_data(shape)
                rtree_obj = self._pedb._edb.Geometry.RTreeObj(bb_box, padstack_inst)
                try:
                    self._padstack_instances_rtree[net_name].Insert(rtree_obj)
                except:
                    pass

    def _polygon_dc_sorts(self):
        self._init_primitives()
        dc_shorts = []
        for net_name, primitive_rtree in self._primitives_rtreee.items():
            net_extent = primitive_rtree.GetExtent()
            for net_checked, primitive_rtree2 in self._primitives_rtreee.items():
                if not net_checked == net_name:
                    intersection = primitive_rtree2.Find(net_extent, False)
                    if intersection:
                        for prim_tree_obj1 in list(primitive_rtree.Items):
                            for prim_tree_obj2 in list(primitive_rtree2.Items):
                                poly1 = prim_tree_obj1.get_Obj()
                                poly2 = prim_tree_obj2.get_Obj()
                                if poly1.layer_name == poly2.layer_name:
                                    if poly1.intersect(poly2):
                                        dc_shorts.append((poly1, poly2))
            # for net_checked,
        return dc_shorts

    def _poly_disjoint(self):
        disjoint_polys = {}
        for net_name, primitives_rtree in self._primitives_rtreee.items():
            connected_geometry_sets = list(primitives_rtree.GetConnectedGeometrySets())
            if len(connected_geometry_sets) > 2:
                disjoint_polys[net_name] = [list(poly) for poly in connected_geometry_sets[1:]]
        return disjoint_polys
