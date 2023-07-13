class EdbDesignOptions:
    def __init__(self, active_cell):
        self._active_cell = active_cell

    @property
    def suppress_pads(self):
        """Whether to suppress non-functional pads.

        Returns
        -------
        bool
            ``True`` if suppress non-functional pads is on, ``False`` otherwise.

        """
        return self._active_cell.GetSuppressPads()

    @suppress_pads.setter
    def suppress_pads(self, value):
        self._active_cell.SetSuppressPads(value)

    @property
    def antipads_always_on(self):
        """Whether to always turn on antipad.

        Returns
        -------
        bool
            ``True`` if antipad is always on, ``False`` otherwise.

        """
        return self._active_cell.GetAntiPadsAlwaysOn()

    @antipads_always_on.setter
    def antipads_always_on(self, value):
        self._active_cell.SetAntiPadsAlwaysOn(value)
