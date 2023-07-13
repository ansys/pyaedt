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
