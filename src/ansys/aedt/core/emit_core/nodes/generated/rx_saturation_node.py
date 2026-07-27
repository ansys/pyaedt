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
from ansys.aedt.core.internal.checks import min_aedt_version


class RxSaturationNode(EmitNode):
    """Provide rx saturation node."""

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
        >>> radio = app.schematic.create_component("New Radio")
        >>> band = radio.children[0]
        >>> rx_profile = band.children[1]
        >>> rx_saturation = rx_profile.add_rx_saturation()
        >>> rx_saturation.parent

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
        >>> radio = app.schematic.create_component("New Radio")
        >>> band = radio.children[0]
        >>> rx_profile = band.children[1]
        >>> rx_saturation = rx_profile.add_rx_saturation()
        >>> rx_saturation.node_type

        """
        return self._node_type

    @min_aedt_version("2025.2")
    def import_csv_file(self, file_name: str) -> EmitNode:
        """Import a CSV File....

        Examples
        --------
        >>> from ansys.aedt.core import Emit
        >>> app = Emit()
        >>> radio = app.schematic.create_component("New Radio")
        >>> band = radio.children[0]
        >>> rx_profile = band.children[1]
        >>> rx_saturation = rx_profile.add_rx_saturation()
        >>> rx_saturation.import_csv_file("C:\\EMIT\\data.csv")

        """
        return self._import(file_name, "CsvFile")

    @min_aedt_version("2027.1")
    def export_to_csv(self, file_name: str) -> str:
        """Export's the data for this node"""
        return self._export_to_csv(file_name, "", "")

    @min_aedt_version("2027.1")
    def plot(self):
        """Bring up a Cartesian plot for this node"""
        return self._plot("", "")

    @min_aedt_version("2025.2")
    def delete(self) -> None:
        """Delete this node.

        Examples
        --------
        >>> from ansys.aedt.core import Emit
        >>> app = Emit()
        >>> radio = app.schematic.create_component("New Radio")
        >>> band = radio.children[0]
        >>> rx_profile = band.children[1]
        >>> rx_saturation = rx_profile.add_rx_saturation()
        >>> rx_saturation.delete()

        """
        self._delete()

    @property
    @min_aedt_version("2025.2")
    def table_data(self) -> list[tuple]:
        """Rx Saturation Profile Table.
        Table consists of 2 columns.
        Frequency:
            Value should be between 1 and 100e9.
        Amplitude:
            Value should be between -1000 and 1000.

        Examples
        --------
        >>> from ansys.aedt.core import Emit
        >>> app = Emit()
        >>> radio = app.schematic.create_component("New Radio")
        >>> band = radio.children[0]
        >>> rx_profile = band.children[1]
        >>> rx_saturation = rx_profile.add_rx_saturation()
        >>> rx_saturation.table_data = [(2, 25.0)]

        """
        return self._get_table_data()

    @table_data.setter
    @min_aedt_version("2025.2")
    def table_data(self, value: list[tuple]) -> None:
        self._set_table_data(value)

    @property
    @min_aedt_version("2025.2")
    def enabled(self) -> bool:
        """Enabled state for this node.

        Examples
        --------
        >>> from ansys.aedt.core import Emit
        >>> app = Emit()
        >>> radio = app.schematic.create_component("New Radio")
        >>> band = radio.children[0]
        >>> rx_profile = band.children[1]
        >>> rx_saturation = rx_profile.add_rx_saturation()
        >>> rx_saturation.enabled = True

        """
        return self._get_property("Enabled") == "true"

    @enabled.setter
    @min_aedt_version("2025.2")
    def enabled(self, value: bool) -> None:
        self._set_property("Enabled", f"{str(value).lower()}")
