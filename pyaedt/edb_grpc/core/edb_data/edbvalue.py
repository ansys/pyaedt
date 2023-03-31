class EdbValue:
    """Class defining Edb Value properties."""

    def __init__(self, edb_obj):
        self._edb_obj = edb_obj

    @property
    def value(self):
        """Variable Value Object.

        Returns
        -------
        Edb Object
        """
        return self._edb_obj

    @property
    def name(self):
        """Variable name.

        Returns
        -------
        str
        """
        return self._edb_obj.GetName()

    @property
    def tofloat(self):
        """Returns the float number of the variable.

        Returns
        -------
        float
        """
        return self._edb_obj.ToDouble()

    @property
    def tostring(self):
        """Returns the string of the variable.

        Returns
        -------
        str
        """
        return self._edb_obj.ToString()

    def __str__(self):
        """Another way to return the string for the value."""
        return self.tostring

    def __repr__(self):
        """Another way to return the string for the value."""
        return "<Instance of pyaedt.edb_grpc.core.edb_data.EdbValue = " + self.tostring + ">"
