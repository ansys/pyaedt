from pyaedt import pyaedt_function_handler
from pyaedt.edb_core.edb_data.components_data import EDBComponent
from pyaedt.edb_core.edb_data.nets_data import EDBNetsData


class LayoutObj(object):
    """Manages EDB functionalities for the layout object."""

    def __init__(self, pedb, edb_object):
        self._pedb = pedb
        self._edb_object = edb_object

    @pyaedt_function_handler
    def is_null(self):
        """Determine if this object is null."""
        return self._edb_object.IsNull()

    @property
    def _edb(self):
        """EDB object.

        Returns
        -------
        Ansys.Ansoft.Edb
        """
        return self._pedb.edb_api


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
        return EDBNetsData(self._edb_object.GetNet(), self._pedb)

    @property
    def component(self):
        """Component connected to this object.

        Returns
        -------
        :class:`pyaedt.edb_core.edb_data.nets_data.EDBComponent`
        """

        edb_comp = self._edb_object.GetComponent()
        if edb_comp.IsNull():
            return None
        else:
            return EDBComponent(self._pedb, edb_comp)
