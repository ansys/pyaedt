from pyaedt.edb_core.edb_data.terminals import EdgeTerminal
from pyaedt.edb_core.edb_data.terminals import Terminal


class GapPort(EdgeTerminal):
    """Manages gap port properties.

    Parameters
    ----------
    pedb : pyaedt.edb.Edb
        EDB object from the ``Edblib`` library.
    edb_object : Ansys.Ansoft.Edb.Cell.Terminal.EdgeTerminal
        Edge terminal instance from EDB.

    Examples
    --------
    This example shows how to access the ``GapPort`` class.
    >>> from pyaedt import Edb
    >>> edb = Edb("myaedb.aedb")
    >>> gap_port = edb.ports["gap_port"]
    """

    def __init__(self, pedb, edb_object):
        super().__init__(pedb, edb_object)

    @property
    def magnitude(self):
        """Magnitude."""
        return self._edb_object.GetSourceAmplitude().ToDouble()

    @property
    def phase(self):
        """Phase."""
        return self._edb_object.GetSourcePhase().ToDouble()

    @property
    def renormalize(self):
        """Whether renormalize is active."""
        return self._edb_object.GetPortPostProcessingProp().DoRenormalize

    @property
    def deembed(self):
        """Inductance value of the deembed gap port."""
        return self._edb_object.GetPortPostProcessingProp().DoDeembedGapL

    @property
    def renormalize_z0(self):
        """Renormalize Z0 value (real, imag)."""
        return (
            self._edb_object.GetPortPostProcessingProp().RenormalizionZ0.ToComplex().Item1,
            self._edb_object.GetPortPostProcessingProp().RenormalizionZ0.ToComplex().Item2,
        )


class WavePort(EdgeTerminal):
    """Manages wave port properties.

    Parameters
    ----------
    pedb : pyaedt.edb.Edb
        EDB object from the ``Edblib`` library.
    edb_object : Ansys.Ansoft.Edb.Cell.Terminal.EdgeTerminal
        Edge terminal instance from EDB.

    Examples
    --------
    This example shows how to access the ``WavePort`` class.

    >>> from pyaedt import Edb
    >>> edb = Edb("myaedb.aedb")
    >>> exc = edb.excitations
    >>> print(exc["Port1"].name)
    """

    def __init__(self, pedb, edb_terminal):
        super().__init__(pedb, edb_terminal)

    @property
    def horizontal_extent_factor(self):
        """Horizontal extent factor."""
        return self._hfss_port_property["Horizontal Extent Factor"]

    @horizontal_extent_factor.setter
    def horizontal_extent_factor(self, value):
        p = self._hfss_port_property
        p["Horizontal Extent Factor"] = value
        self._hfss_port_property = p

    @property
    def vertical_extent_factor(self):
        """Vertical extent factor."""
        return self._hfss_port_property["Vertical Extent Factor"]

    @vertical_extent_factor.setter
    def vertical_extent_factor(self, value):
        p = self._hfss_port_property
        p["Vertical Extent Factor"] = value
        self._hfss_port_property = p

    @property
    def radial_extent_factor(self):
        """Radial extent factor."""
        return self._hfss_port_property["Radial Extent Factor"]

    @radial_extent_factor.setter
    def radial_extent_factor(self, value):
        p = self._hfss_port_property
        p["Radial Extent Factor"] = value
        self._hfss_port_property = p

    @property
    def pec_launch_width(self):
        """Launch width for the printed electronic component (PEC)."""
        return self._hfss_port_property["PEC Launch Width"]

    @pec_launch_width.setter
    def pec_launch_width(self, value):
        p = self._hfss_port_property
        p["PEC Launch Width"] = value
        self._hfss_port_property = p

    @property
    def deembed(self):
        """Whether deembed is active."""
        return self._edb_object.GetPortPostProcessingProp().DoDeembed

    @property
    def deembed_length(self):
        """Deembed Length."""
        return self._edb_object.GetPortPostProcessingProp().DeembedLength.ToDouble()


class ExcitationSources(Terminal):
    """Manage sources properties.

    Parameters
    ----------
    pedb : pyaedt.edb.Edb
        Edb object from Edblib.
    edb_terminal : Ansys.Ansoft.Edb.Cell.Terminal.EdgeTerminal
        Edge terminal instance from Edb.



    Examples
    --------
    This example shows how to access this class.
    >>> from pyaedt import Edb
    >>> edb = Edb("myaedb.aedb")
    >>> all_sources = edb.sources
    >>> print(all_sources["VSource1"].name)

    """

    def __init__(self, pedb, edb_terminal):
        Terminal.__init__(self, pedb, edb_terminal)

    @property
    def magnitude(self):
        """Get the magnitude of the source."""
        return self._edb_object.GetSourceAmplitude().ToDouble()

    @magnitude.setter
    def magnitude(self, value):
        self._edb_object.SetSourceAmplitude(self._edb.utility.value(value))

    @property
    def phase(self):
        """Get the phase of the source."""
        return self._edb_object.GetSourcePhase().ToDouble()

    @phase.setter
    def phase(self, value):
        self._edb_object.SetSourcePhase(self._edb.utility.value(value))


class ExcitationProbes(Terminal):
    """Manage probes properties.

    Parameters
    ----------
    pedb : pyaedt.edb.Edb
        Edb object from Edblib.
    edb_terminal : Ansys.Ansoft.Edb.Cell.Terminal.EdgeTerminal
        Edge terminal instance from Edb.


    Examples
    --------
    This example shows how to access this class.
    >>> from pyaedt import Edb
    >>> edb = Edb("myaedb.aedb")
    >>> probes = edb.probes
    >>> print(probes["Probe1"].name)
    """

    def __init__(self, pedb, edb_terminal):
        Terminal.__init__(self, pedb, edb_terminal)


class ExcitationBundle:
    """Manages multi terminal excitation properties."""

    def __init__(self, pedb, edb_bundle_terminal):
        self._pedb = pedb
        self._edb_bundle_terminal = edb_bundle_terminal

    @property
    def name(self):
        """Port Name."""
        return list(self.terminals.values())[0].name

    @property
    def edb(self):  # pragma: no cover
        """Get edb."""
        return self._pedb.edb_api

    @property
    def terminals(self):
        """Get terminals belonging to this excitation."""
        return {i.GetName(): GapPort(self._pedb, i) for i in list(self._edb_bundle_terminal.GetTerminals())}

    @property
    def reference_net_name(self):
        """Reference Name. Not applicable to Differential pairs."""
        return
