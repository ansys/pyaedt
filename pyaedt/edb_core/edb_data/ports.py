import re

from pyaedt.edb_core.edb_data.nets_data import EDBNetsData
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
        temp = re.search(r"'Horizontal Extent Factor'='.*?'", self._edb_properties)
        if temp:
            txt = temp.group()
            return float(txt.split("=")[1].replace("'", ""))
        else:  # pragma: no cover
            return None

    @horizontal_extent_factor.setter
    def horizontal_extent_factor(self, value):
        new_arg = r"'Horizontal Extent Factor'='{}'".format(value)
        if self.horizontal_extent_factor:
            p = re.sub(r"'Horizontal Extent Factor'='.*?'", new_arg, self._edb_properties)
        else:
            match = re.search(r"(.*\))$", self._edb_properties)
            p = match.group(1)[:-1] + ", " + new_arg + ")"
        self._edb_properties = p

    @property
    def vertical_extent_factor(self):
        """Vertical extent factor."""
        temp = re.search(r"'Vertical Extent Factor'='.*?'", self._edb_properties)
        if temp:
            txt = temp.group()
            return float(txt.split("=")[1].replace("'", ""))
        return None  # pragma: no cover

    @vertical_extent_factor.setter
    def vertical_extent_factor(self, value):
        new_arg = r"'Vertical Extent Factor'='{}'".format(value)
        if self.vertical_extent_factor:
            p = re.sub(r"'Vertical Extent Factor'='.*?'", new_arg, self._edb_properties)
        else:
            match = re.search(r"(.*\))$", self._edb_properties)
            p = match.group(1)[:-1] + ", " + new_arg + ")"
        self._edb_properties = p

    @property
    def radial_extent_factor(self):
        """Radial extent factor."""
        temp = re.search(r"'Radial Extent Factor'='.*?'", self._edb_properties)
        if temp:
            txt = temp.group()
            return float(txt.split("=")[1].replace("'", ""))
        return None  # pragma: no cover

    @radial_extent_factor.setter
    def radial_extent_factor(self, value):
        new_arg = r"'Radial Extent Factor'='{}'".format(value)
        if self.radial_extent_factor:
            p = re.sub(r"'Radial Extent Factor'='.*?'", new_arg, self._edb_properties)
        else:
            match = re.search(r"(.*\))$", self._edb_properties)
            p = match.group(1)[:-1] + ", " + new_arg + ")"
        self._edb_properties = p

    @property
    def pec_launch_width(self):
        """Launch width for the printed electronic component (PEC)."""
        temp = re.search(r"'PEC Launch Width'='.*?'", self._edb_properties)
        if temp:
            txt = temp.group()
            return txt.split("=")[1].replace("'", "")
        else:  # pragma: no cover
            return None

    @pec_launch_width.setter
    def pec_launch_width(self, value):
        new_arg = r"'PEC Launch Width'='{}'".format(value)
        if self.pec_launch_width:
            p = re.sub(r"'PEC Launch Width'='.*?'", new_arg, self._edb_properties)
        else:
            match = re.search(r"(.*\))$", self._edb_properties)
            p = match.group(1)[:-1] + ", " + new_arg + ")"
        self._edb_properties = p

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
        return self._edb_bundle_terminal.GetName()

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


class ExcitationDifferential(ExcitationBundle):
    """Manages differential excitation properties."""

    def __init__(self, pedb, edb_boundle_terminal):
        ExcitationBundle.__init__(self, pedb, edb_boundle_terminal)

    @property
    def net_name(self):
        """Net name.

        Returns
        -------
        str
             Name of the net.
        """
        return self._edb_bundle_terminal.GetNet().GetName()

    @property
    def net(self):
        """Net object.

        Returns
        -------
        :class:`pyaedt.edb_core.edb_data.nets_data.EDBNetsData`
        """
        return EDBNetsData(self._edb_bundle_terminal.GetNet(), self._pedb)
