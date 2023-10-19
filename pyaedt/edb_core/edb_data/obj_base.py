class ObjBase(object):
    """Manages EDB functionalities for a base object."""

    def __init__(self, pedb, model):
        self._pedb = pedb
        self._edb_object = model

    @property
    def is_null(self):
        """Flag indicating if this object is null."""
        return self._edb_object.IsNull()

    @property
    def type(self):
        """Get type."""
        return self._edb_object.GetType()
