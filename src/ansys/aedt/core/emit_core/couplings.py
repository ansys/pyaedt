# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 - 2025 ANSYS, Inc. and/or its affiliates.
# SPDX-License-Identifier: MIT
#
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

"""This module contains these classes: `CouplingsEmit`.

This module provides for interacting with EMIT Analysis and Results windows.
"""

from ansys.aedt.core.internal.checks import min_aedt_version


class CouplingsEmit(object):
    """Provides for interaction with the EMIT ```coupling`` folder.

    This class is accessible through the results variable
    object (``emit.couplings``) for the EMIT app.

    Parameters
    ----------
    app :
        Inherited parent object.

    Examples
    --------
    >>> from ansys.aedt.core import Emit
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
        """List of existing link names.

        Parameters
        ----------
        None

        Returns
        -------
        coupling_names : list str
            List of all existing linked couplings.

        Examples
        --------
        >>> app = Emit()
        >>> my_couplings = app.couplings
        >>> coupling_names = my_couplings.coupling_names
        """
        return self._odesign.GetLinkNames()

    def add_link(self, new_coupling_name):
        """Add a new link if it's not already there.

        Parameters
        ----------
        new_coupling_name : str
            Name of the design to link. The design must be
            within the same project as the EMIT design.

        Returns
        -------
        None

        Examples
        --------
        >>> app = Emit()
        >>> app.couplings.add_link("HFSS_Design")
        """
        if new_coupling_name not in self._odesign.GetLinkNames():
            self._odesign.AddLink(new_coupling_name)

    def delete_link(self, coupling_link_name):
        """Delete a link from the EMIT design.

        Parameters
        ----------
        coupling_link_name : str
            Name of the link to delete.

        Returns
        -------
        None

        Examples
        --------
        >>> app = Emit()
        >>> app.couplings.delete_link("HFSS_Design")
        """
        self._odesign.DeleteLink(coupling_link_name)

    def update_link(self, coupling_name):
        """Update the link if it's a valid link.

        Check if anything in the linked design has changed and retrieve updated data if it has.

        Parameters
        ----------
        coupling_name : str
            Name of the linked design.

        Returns
        -------
        None

        Examples
        --------
        >>> app = Emit()
        >>> app.update_link("HFSS_Design")
        """
        if coupling_name in self._odesign.GetLinkNames():
            self._odesign.UpdateLink(coupling_name)

    @property
    @min_aedt_version("2022.2")
    def linkable_design_names(self):
        """List the available link names.

        This property is only available in AEDT version 2022.2 or higher.

        Parameters
        ----------
        None

        Returns
        -------
        linkable_design_names : list str
            List of all existing, non-EMIT designs in the active project.
            If a design is already linked, it is excluded from the list.

        Examples
        --------
        >>> app = Emit("Apache with multiple links")
        >>> links = app.couplings.linkable_design_names
        """
        return self._odesign.GetAvailableLinkNames()

    @property
    def cad_nodes(self):
        """Dictionary of the CAD nodes.

        Parameters
        ----------
        None

        Returns
        -------
        cad_nodes : dict
            A dict containing all of the CAD nodes with their
            properties for the given design.

        Examples
        --------
        >>> app = Emit()
        >>> cad_nodes = app.couplings.cad_nodes
        """
        coupling_node_name = "CouplingNodeTree@EMIT"
        cad_node_list = {}
        for coupling in self._odesign.GetComponentNodeNames(coupling_node_name):
            properties_list = self._odesign.GetComponentNodeProperties(coupling_node_name, coupling)
            props = dict(p.split("=") for p in properties_list)
            if props["Type"] == "CADNode":
                cad_node_list[coupling] = props
        return cad_node_list

    @property
    def antenna_nodes(self):
        """Dictionary of the antenna nodes.

        Parameters
        ----------
        None

        Returns
        -------
        antenna_nodes : dict
            A dictionary containing all of the antenna nodes with their
            properties for the given design.

        Examples
        --------
        >>> app = Emit()
        >>> antenna_nodes = app.couplings.antenna_nodes
        """
        antenna_nodes_list = self._app.modeler.components.get_antennas()
        # osch = self._odesign.SetActiveEditor("SchematicEditor")
        # comps = osch.GetAllComponents()

        # coupling_node_name = "CouplingNodeTree@EMIT"
        # antenna_nodes_list = {}
        # for coupling in self._odesign.GetComponentNodeNames(coupling_node_name):
        #     properties_list = self._odesign.GetComponentNodeProperties(coupling_node_name, coupling)
        #     props = dict(p.split("=") for p in properties_list)
        #     if props["Type"] == "AntennaNode":
        #         antenna_nodes_list[coupling] = props
        return antenna_nodes_list
