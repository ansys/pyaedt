"""
This module contains these classes: `CouplingsEmit`.

This module provides the capability to interact with EMIT Analysis & Results windows.
"""
import warnings


class CouplingsEmit(object):
    """Provides for interaction with the EMIT Coupling folder

    This class is accessible through the EMIT application results variable
    object( eg. ``emit.couplings``).

    Parameters
    ----------
    app :
        Inherited parent object.

    Examples
    --------
    >>> from pyaedt import Emit
    >>> app = Emit()
    >>> my_couplings = app.couplings
    """

    def __init__(self, app):
        self._app = app

    # Properties derived from internal parent data
    @property
    def _desktop(self):
        """Desktop."""
        return self._app._desktop

    @property
    def logger(self):
        """Logger."""
        return self._app.logger

    @property
    def _odesign(self):
        """Design."""
        return self._app._odesign

    @property
    def projdir(self):
        """Project directory."""
        return self._app.project_path

    @property
    def coupling_names(self):
        """List of existing link names."""
        return self._odesign.GetLinkNames()

    def add_link(self, new_coupling_name):
        """add a new link if it's not already there"""
        if new_coupling_name not in self._odesign.GetLinkNames():
            self._odesign.AddLink(new_coupling_name)

    def update_link(self, coupling_name):
        """update the link if it's a valid link"""
        if coupling_name in self._odesign.GetLinkNames():
            self._odesign.UpdateLink(coupling_name)

    @property
    def linkable_design_names(self):
        """list the available link names"""
        desktop_version = self._desktop.GetVersion()[0:6]
        if desktop_version >= "2022.2":
            return self._odesign.GetAvailableLinkNames()
        else:
            warnings.warn("The function linkable_design_names() requires AEDT 2022 R2 or newer.")
            return []
        
    @property
    def cad_nodes(self):
        """list the cad nodes"""
        coupling_node_name = 'CouplingNodeTree@EMIT'
        cad_node_list = {}
        for coupling in self._odesign.GetComponentNodeNames(coupling_node_name):
            properties_list = self._odesign.GetComponentNodeProperties(coupling_node_name, coupling)
            props = dict(p.split("=") for p in properties_list)
            if (props["Type"] == "CADNode"): 
                # cad_node_list.append(coupling)
                cad_node_list[coupling] = props
        return cad_node_list

    @property
    def antenna_pattern_nodes(self):
        """list the antenna pattern nodes"""
        radios_node_name = 'NODE-*-RF Systems-*-RF System-*-Radios'
        antenna_patterns_list = {}
        for radio in self._odesign.GetComponentNodeNames(radios_node_name):
            properties_list = self._odesign.GetComponentNodeProperties(radios_node_name, radio)
            props = dict(p.split("=") for p in properties_list)
            # TODO(bkaylor): Is this Type check necessary?
            if (props["Type"] == "RadioNode"): 
                # TODO(bkaylor): How to access the Antenna Pattern from the radio node?
                antenna_patterns_list[radio] = props
        return antenna_patterns_list