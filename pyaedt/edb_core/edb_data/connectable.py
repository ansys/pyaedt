from pyaedt import pyaedt_function_handler
from pyaedt.edb_core.edb_data.obj_base import ObjBase


class LayoutObjInstance:
    """Manages EDB functionalities for the layout object instance."""

    def __init__(self, pedb, edb_object):
        self._pedb = pedb
        self._edb_object = edb_object


class LayoutObj(ObjBase):
    """Manages EDB functionalities for the layout object."""

    def __getattr__(self, key):  # pragma: no cover
        try:
            return super().__getattribute__(key)
        except AttributeError:
            try:
                return getattr(self._edb_object, key)
            except AttributeError:
                raise AttributeError("Attribute not present")

    def __init__(self, pedb, edb_object):
        super().__init__(pedb, edb_object)

    @property
    def _edb(self):
        """EDB object.

        Returns
        -------
        Ansys.Ansoft.Edb
        """
        return self._pedb.edb_api

    @property
    def _layout_obj_instance(self):
        """Returns :class:`pyaedt.edb_core.edb_data.connectable.LayoutObjInstance`."""
        obj = self._pedb.layout_instance.GetLayoutObjInstance(self._edb_object, None)
        return LayoutObjInstance(self._pedb, obj)

    @property
    def _edb_properties(self):
        p = self._edb_object.GetProductSolverOption(self._edb.edb_api.ProductId.Designer, "HFSS")
        return p

    @_edb_properties.setter
    def _edb_properties(self, value):
        self._edb_object.SetProductSolverOption(self._edb.edb_api.ProductId.Designer, "HFSS", value)

    @property
    def _obj_type(self):
        """Returns LayoutObjType."""
        return self._edb_object.GetObjType().ToString()

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

    @net.setter
    def net(self, value):
        """Set net."""
        net = self._pedb.nets[value]
        self._edb_object.SetNet(net.net_object)

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
