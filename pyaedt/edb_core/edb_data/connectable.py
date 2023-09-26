from pyaedt import pyaedt_function_handler

class LayoutObj(object):
    """Manages EDB functionalities for the layout object."""

    def __getattr__(self, key):
        try:
            return super().__getattribute__(key)
        except AttributeError:
            try:
                return getattr(self._edb_object, key)
            except AttributeError:
                raise AttributeError("Attribute not present")

    def __init__(self, pedb, edb_object):
        self._pedb = pedb
        self._edb_object = edb_object

    @property
    def _edb(self):
        """EDB object.

        Returns
        -------
        Ansys.Ansoft.Edb
        """
        return self._pedb.edb_api

    @property
    def _layout(self):
        """Return Ansys.Ansoft.Edb.Cell.Layout object."""
        return self._pedb.active_layout

    @property
    def _edb_properties(self):
        p = self._edb_object.GetProductSolverOption(self._edb.edb_api.ProductId.Designer, "HFSS")
        return p

    @_edb_properties.setter
    def _edb_properties(self, value):
        self._edb_object.SetProductSolverOption(self._edb.edb_api.ProductId.Designer, "HFSS", value)

    @property
    def is_null(self):
        """Determine if this object is null."""
        return self._edb_object.IsNull()

    @property
    def id(self):
        """Primitive ID.

        Returns
        -------
        int
        """
        return self._edb_object.GetId()

    @pyaedt_function_handler()
    def delete(self):
        """Delete this primitive."""
        self._edb_object.Delete()
        return True

class Connectable(LayoutObj):
    """Manages EDB functionalities for a connectable object."""

    def __init__(self, pedb, edb_object):
        super().__init__(pedb, edb_object)

    @property
    def net(self):
        """Net Object.

        Returns
        -------
        :class:`pyaedt.edb_core.edb_data.nets_data.EDBNetsData`
        """
        from pyaedt.edb_core.edb_data.nets_data import EDBNetsData
        return EDBNetsData(self._edb_object.GetNet(), self._pedb)

    @property
    def component(self):
        """Component connected to this object.

        Returns
        -------
        :class:`pyaedt.edb_core.edb_data.nets_data.EDBComponent`
        """
        from pyaedt.edb_core.edb_data.components_data import EDBComponent

        edb_comp = self._edb_object.GetComponent()
        if edb_comp.IsNull():
            return None
        else:
            return EDBComponent(self._pedb, edb_comp)
