# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 - 2026 Synopsys, Inc. and ANSYS, Inc. All rights reserved.
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

from ansys.aedt.core.emit_core.nodes.emit_node import EmitNode
from ansys.aedt.core.emit_core.nodes.generated import AntennaNode
from ansys.aedt.core.internal.checks import min_aedt_version


class CouplingLinkNode(EmitNode):
    """Provide coupling link node."""

    def __init__(self, emit_obj, result_id, node_id) -> None:
        EmitNode.__init__(self, emit_obj, result_id, node_id)
        self._is_component = False

    @property
    @min_aedt_version("2025.2")
    def parent(self) -> EmitNode:
        """The parent of this emit node.

        Examples
        --------
        >>> from ansys.aedt.core import Emit
        >>> app = Emit()
        >>> rev = app.results.get_revision()
        >>> cpl = rev.get_coupling_data_node()
        >>> link = cpl.children[0]
        >>> link.parent

        """
        return self._parent

    @property
    @min_aedt_version("2025.2")
    def node_type(self) -> str:
        """The type of this emit node.

        Examples
        --------
        >>> from ansys.aedt.core import Emit
        >>> app = Emit()
        >>> rev = app.results.get_revision()
        >>> cpl = rev.get_coupling_data_node()
        >>> link = cpl.children[0]
        >>> link.node_type

        """
        return self._node_type

    @min_aedt_version("2027.1")
    def export_to_csv(
        self, file_name: str, antennas: tuple[AntennaNode, AntennaNode] | None = None, ports: str = ""
    ) -> str:
        """Export's the data for this node

        Parameters
        ----------
        file_name: str[optional]
            full path to the file to export to.
        antennas: tuple(AntennaNode, AntennaNode), optional
            tuple of antenna nodes to pull the selected Tx and Rx antenna names from for the export.
            If not specified, will use the names specified by the ports parameter.
        ports: str, optional
            the ports to export the data for.

        Returns
        -------
        csv_data: str
            stringified data for the node returned if file_name not specified
        """
        if antennas is not None and all(isinstance(x, AntennaNode) for x in antennas):
            a1, a2 = antennas
            vals = f"{a1.name}|{a2.name}"
        else:
            vals = f"{ports}"
        return self._export_to_csv(file_name, "SelectedRxAntenna|SelectedTxAntenna", vals)

    @min_aedt_version("2027.1")
    def plot(self, antennas: tuple[AntennaNode, AntennaNode] | None = None, ports: str = ""):
        """Bring up a Cartesian plot for this node

        Parameters
        ----------
        antennas: tuple(AntennaNode, AntennaNode), optional
            tuple of antenna nodes to pull the selected Tx and Rx antenna names from for the export.
            If not specified, will use the names specified by the ports parameter.
        ports: str, optional
            the ports to export the data for.
        """
        if antennas is not None and all(isinstance(x, AntennaNode) for x in antennas):
            a1, a2 = antennas
            vals = f"{a1.name}|{a2.name}"
        else:
            vals = f"{ports}"
        return self._plot("SelectedRxAntenna|SelectedTxAntenna", vals)

    @property
    @min_aedt_version("2025.2")
    def enabled(self) -> bool:
        """Enable/Disable coupling link.

        Value should be 'true' or 'false'.

        Examples
        --------
        >>> from ansys.aedt.core import Emit
        >>> app = Emit()
        >>> rev = app.results.get_revision()
        >>> cpl = rev.get_coupling_data_node()
        >>> link = cpl.children[0]
        >>> link.enabled = True

        """
        val = self._get_property("Enabled")
        return val == "true"

    @enabled.setter
    @min_aedt_version("2025.2")
    def enabled(self, value: bool) -> None:
        self._set_property("Enabled", f"{str(value).lower()}")

    @property
    @min_aedt_version("2025.2")
    def ports(self) -> list[str]:
        """Maps each port in the link to an antenna in the project.

        Examples
        --------
        >>> from ansys.aedt.core import Emit
        >>> app = Emit()
        >>> rev = app.results.get_revision()
        >>> cpl = rev.get_coupling_data_node()
        >>> link = cpl.children[0]
        >>> link.ports

        """
        val = self._get_property("Ports")
        return val

    @ports.setter
    @min_aedt_version("2025.2")
    def ports(self, value: list[str] | list[EmitNode] | str) -> None:
        if isinstance(value, (list, tuple)):
            if all(isinstance(v, EmitNode) for v in value):
                value = "|".join(self._full_node_name(v.name) for v in value)
            else:
                value = "|".join(self._full_node_name(v) for v in value)
        else:
            parts = value.split("|")
            value = "|".join(self._full_node_name(p) for p in parts)
        self._set_property("Ports", f"{value}")
