class Terminal(object):
    """Terminal Manager."""

    def __init__(self, pedb, pterminal):
        self._pedb = pedb
        self._ptermimal = pterminal

    @property
    def name(self):
        """Terminal name.

        Returns
        -------
        str
        """
        return self._ptermimal.GetName()

    @property
    def id(self):
        """Terminal id.

        Returns
        -------
        id
        """
        return self._ptermimal.GetId()

    @property
    def net_name(self):
        """Terminal net name.

        Returns
        -------
        str
        """
        return self._ptermimal.GetNet().GetName()

    @property
    def net(self):
        """Terminal net class.

        Returns
        -------
        :class:`pyaedt.edb_core.EDB_Data.EDBNets` class.

        """
        if self.net_name:
            return self._pedb.core_nets.nets[self.net_name]

    @property
    def pingroup(self):
        """Pingroup net class.

        Returns
        -------
        :class:`pyaedt.edb_core.pingroups.PinGroup` class.

        """
        if self._ptermimal.GetPinGroup():
            return self._pedb.core_padstack.pingroups[self._ptermimal.GetPinGroup().GetName()]

    @property
    def pins(self):
        """Terminal pins list class.

        Returns
        -------
        list of :class:`pyaedt.edb_core.EDB_Data.EDBPadstackInstance` class.

        """
        pins = []
        if self.pingroup:
            pins = self.pingroup.GetPins()
        return [self._pedb.pins[pin.GetId()] for pin in pins]

    @property
    def is_circuit(self):
        """Check if terminal is circuit port or not.

        Returns
        -------
        bool
        """
        return self._ptermimal.GetIsCircuitPort()

    @property
    def impedance(self):
        """Terminal port impedance.

        Returns
        -------
        float
        """
        return self._ptermimal.GetImpedance().ToDouble()

    @property
    def is_auto_port(self):
        """Check if is auto port or not.

        Returns
        -------
        bool
        """
        return self._ptermimal.GetIsAutoPort()

    @property
    def amplitude(self):
        """Terminal amplitude.

        Returns
        -------
        float
        """
        return self._ptermimal.GetSourceAmplitude().ToDouble()

    @property
    def phase(self):
        """Terminal phase.

        Returns
        -------
        float
        """
        return self._ptermimal.GetSourcePhase().ToDouble()


class PinGroup(object):
    """Pingroup object management."""

    def __init__(self, pedb, pgroup):
        self._pedb = pedb
        self._pingroup = pgroup

    @property
    def name(self):
        """Pingroup name.

        Returns
        -------
        str
        """
        return self._pingroup.GetName()

    @property
    def id(self):
        """Pingroup Id.

        Returns
        -------
        int
        """
        return self._pingroup.GetId()

    @property
    def net_name(self):
        """Pingroup net name.

        Returns
        -------
        str
        """
        return self._pingroup.GetNet().GetName()

    @property
    def net(self):
        """Pingroup net class.

        Returns
        -------
        :class:`pyaedt.edb_core.EDB_Data.EDBNets` class.

        """
        if self.net_name:
            return self._pedb.core_nets.nets[self.net_name]

    @property
    def pins(self):
        """Pingroup pins list class.

        Returns
        -------
        list of :class:`pyaedt.edb_core.EDB_Data.EDBPadstackInstance` class.

        """
        pins = self._pingroup.GetPins()
        return [self._pedb.pins[pin.GetId()] for pin in pins]
