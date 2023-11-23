class ObjBase(object):
    """Manages EDB functionalities for a base object."""

    def __init__(self, pedb, edb_object):
        self._pedb = pedb
        self._edb_object = edb_object

    @property
    def is_null(self):
        """Flag indicating if this object is null."""
        return self._edb_object.IsNull()

    @property
    def type(self):
        """Get type."""
        try:
            return self._edb_object.GetType()
        except AttributeError:  # pragma: no cover
            return None
