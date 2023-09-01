from pyaedt import pyaedt_function_handler


class LayoutObj(object):

    def __init__(self, pedb, edb_object):
        self._pedb = pedb
        self._edb_object = edb_object

    @pyaedt_function_handler
    def is_null(self):
        """Determine if this object is null."""
        return self._edb_object.IsNull()

    @property
    def _edb(self):
        return self._pedb.edb_api


class Connectable(LayoutObj):

    def __init__(self, pedb, edb_object):
        super().__init__(pedb, edb_object)
