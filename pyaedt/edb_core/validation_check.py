# from pyaedt import Edb


class ValidationCheck(object):
    def __init__(self, pedb):
        self._pedb = pedb
        self.primitives_dict = {}
        self.padstack_instances_dict = {}
        self.connected_primitives = None

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

    def init_primitives(self):
        for net_name, net in self._pedb.nets.nets.items():
            self.primitives_dict[net_name] = net.primitives
        for padstck in list(self._pedb.padstacks.padstack_instances.values()):
            if padstck.net_name in self.padstack_instances_dict:
                self.padstack_instances_dict[padstck.net_name].append(padstck)
            else:
                self.padstack_instances_dict[padstck.net_name] = [padstck]

    def _get_connected_primitives(self):
        prim_rtree = self._pedb._edb.Geometry.RTree()
        for prim in self._pedb.modeler.primitives:
            if prim.type == "Path":
                edb_obj = prim.convert_to_polygon()
                rtree_obj = self._pedb._edb.Geometry.RTreeObj(edb_obj.polygon_data.edb_api, prim)
                try:
                    prim_rtree.Insert(rtree_obj)
                except:
                    pass
            if prim.type == "Polygon":
                rtree_obj = self._pedb._edb.Geometry.RTreeObj(prim.polygon_data.edb_api, prim)
                try:
                    prim_rtree.Insert(rtree_obj)
                except:
                    pass
        return prim_rtree.GetConnectedGeometrySets()
