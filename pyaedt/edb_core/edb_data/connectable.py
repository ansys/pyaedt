from pyaedt import pyaedt_function_handler
from pyaedt.edb_core.general import Primitives
from pyaedt.edb_core.general import LayoutObjType


class LayoutObjInstance:
    """Manages EDB functionalities for the layout object instance."""

    def __init__(self, pedb, edb_object):
        self._pedb = pedb
        self._edb_object = edb_object

    @pyaedt_function_handler
    def get_connected_objects(self):
        """Get connected objects.

        Returns
        -------
        list[:class:`pyaedt.edb_core.edb_data.padstacks_data.EDBPadstackInstance`,
        :class:`pyaedt.edb_core.edb_data.padstacks_data.EDBPadstackInstance`,
        :class:`pyaedt.edb_core.edb_data.padstacks_data.EdbPath`,
        :class:`pyaedt.edb_core.edb_data.padstacks_data.EdbRectangle`,
        :class:`pyaedt.edb_core.edb_data.padstacks_data.EdbCircle`,
        :class:`pyaedt.edb_core.edb_data.padstacks_data.EdbPolygon`,
            ]
        """
        temp = []
        for i in list([loi.GetLayoutObj() for loi in self._pedb.layout_instance.GetConnectedObjects(self._edb_object).Items]):
            obj_type = i.GetObjType().ToString()
            if obj_type == LayoutObjType.PadstackInstance.name:
                from pyaedt.edb_core.edb_data.padstacks_data import EDBPadstackInstance
                temp.append(EDBPadstackInstance(i, self._pedb))
            elif obj_type == LayoutObjType.Primitive.name:
                prim_type = i.GetPrimitiveType().ToString()
                if prim_type == Primitives.Path.name:
                    from pyaedt.edb_core.edb_data.primitives_data import EdbPath
                    temp.append(EdbPath(i, self._pedb))
                elif prim_type == Primitives.Rectangle.name:
                    from pyaedt.edb_core.edb_data.primitives_data import EdbRectangle
                    temp.append(EdbRectangle(i, self._pedb))
                elif prim_type == Primitives.Circle.name:
                    from pyaedt.edb_core.edb_data.primitives_data import EdbCircle
                    temp.append(EdbCircle(i, self._pedb))
                elif prim_type == Primitives.Polygon.name:
                    from pyaedt.edb_core.edb_data.primitives_data import EdbPolygon
                    temp.append(EdbPolygon(i, self._pedb))
                else:
                    continue
            else:
                continue
        return temp


class LayoutObj(object):
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
    def _layout_obj_instance(self):
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
        return self._edb_object.GetObjType().ToString()

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
