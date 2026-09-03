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


class CustomCouplingNode(EmitNode):
    """Provide custom coupling node."""

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
        >>> cust = cpl.add_custom_coupling()
        >>> cust.parent

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
        >>> cust = cpl.add_custom_coupling()
        >>> cust.node_type

        """
        return self._node_type

    @min_aedt_version("2025.2")
    def import_csv_file(self, file_name: str) -> EmitNode:
        """Import a CSV File....

        Note: The CSV file should not have any header lines and must contain only numeric values.

        Examples
        --------
        >>> from ansys.aedt.core import Emit
        >>> app = Emit()
        >>> rev = app.results.get_revision()
        >>> cpl = rev.get_coupling_data_node()
        >>> cust = cpl.add_custom_coupling()
        >>> cust.import_csv_file("C:\\EMIT\\data.csv")

        """
        return self._import(file_name, "CsvFile")

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

    @min_aedt_version("2025.2")
    def duplicate(self, new_name: str = "") -> EmitNode:
        """Duplicate this node.

        Examples
        --------
        >>> from ansys.aedt.core import Emit
        >>> app = Emit()
        >>> rev = app.results.get_revision()
        >>> cpl = rev.get_coupling_data_node()
        >>> cust = cpl.add_custom_coupling()
        >>> cust_copy = cust.duplicate("cust_copy")

        """
        return self._duplicate(new_name)

    @min_aedt_version("2025.2")
    def delete(self) -> None:
        """Delete this node.

        Examples
        --------
        >>> from ansys.aedt.core import Emit
        >>> app = Emit()
        >>> rev = app.results.get_revision()
        >>> cpl = rev.get_coupling_data_node()
        >>> cust = cpl.add_custom_coupling()
        >>> cust.delete()

        """
        self._delete()

    @property
    @min_aedt_version("2025.2")
    def table_data(self) -> list[tuple]:
        """Custom Coupling Values Table.
        Table consists of 2 columns.
        Frequency:
            Value should be between 1.0 and 100.0e9.
        Value (dB):
            Value should be between -1000.0 and 0.0.

        Examples
        --------
        >>> from ansys.aedt.core import Emit
        >>> app = Emit()
        >>> rev = app.results.get_revision()
        >>> cpl = rev.get_coupling_data_node()
        >>> cust = cpl.add_custom_coupling()
        >>> cust.table_data = [(2, 25.0)]

        """
        return self._get_table_data()

    @table_data.setter
    @min_aedt_version("2025.2")
    def table_data(self, value: list[tuple]) -> None:
        self._set_table_data(value)

    @property
    @min_aedt_version("2025.2")
    def enabled(self) -> bool:
        """Enable/Disable coupling.

        Value should be 'true' or 'false'.

        Examples
        --------
        >>> from ansys.aedt.core import Emit
        >>> app = Emit()
        >>> rev = app.results.get_revision()
        >>> cpl = rev.get_coupling_data_node()
        >>> cust = cpl.add_custom_coupling()
        >>> cust.enabled = True

        """
        val = self._get_property("Enabled")
        return val == "true"

    @enabled.setter
    @min_aedt_version("2025.2")
    def enabled(self, value: bool) -> None:
        self._set_property("Enabled", f"{str(value).lower()}")

    @property
    @min_aedt_version("2025.2")
    def antenna_a(self) -> EmitNode:
        """First antenna of the pair to apply the coupling values to.

        Examples
        --------
        >>> from ansys.aedt.core import Emit
        >>> app = Emit()
        >>> rev = app.results.get_revision()
        >>> cpl = rev.get_coupling_data_node()
        >>> cust = cpl.add_custom_coupling()
        >>> cust.antenna_a

        """
        val = self._get_property("Antenna A")
        return val

    @antenna_a.setter
    @min_aedt_version("2025.2")
    def antenna_a(self, value: EmitNode) -> None:
        self._set_property("Antenna A", f"{value}")

    @property
    @min_aedt_version("2025.2")
    def antenna_b(self) -> EmitNode:
        """Second antenna of the pair to apply the coupling values to.

        Examples
        --------
        >>> from ansys.aedt.core import Emit
        >>> app = Emit()
        >>> rev = app.results.get_revision()
        >>> cpl = rev.get_coupling_data_node()
        >>> cust = cpl.add_custom_coupling()
        >>> cust.antenna_b

        """
        val = self._get_property("Antenna B")
        return val

    @antenna_b.setter
    @min_aedt_version("2025.2")
    def antenna_b(self, value: EmitNode) -> None:
        self._set_property("Antenna B", f"{value}")
