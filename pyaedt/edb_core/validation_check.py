# from pyaedt import Edb


class ValidationCheck(object):
    def __init__(self, pedb):
        self._pedb = pedb
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

    def dc_shorts(self):
        # self.connected_primitives = self._get_connected_primitives()
        pass

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
