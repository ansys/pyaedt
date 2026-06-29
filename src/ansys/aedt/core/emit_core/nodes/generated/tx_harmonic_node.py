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

from enum import Enum

from ansys.aedt.core.emit_core.nodes.emit_node import EmitNode
from ansys.aedt.core.internal.checks import min_aedt_version


class TxHarmonicNode(EmitNode):
    """Provide tx harmonic node."""

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
        >>> emitter, antenna = app.schematic.create_radio_antenna("Bluetooth")
        >>> band = emitter.get_radio().add_band()
        >>> tx_profile = band.children[0]
        >>> tx_harmonics = tx_profile.add_custom_tx_harmonics()
        >>> tx_harmonics.parent

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
        >>> emitter, antenna = app.schematic.create_radio_antenna("Bluetooth")
        >>> band = emitter.get_radio().add_band()
        >>> tx_profile = band.children[0]
        >>> tx_harmonics = tx_profile.add_custom_tx_harmonics()
        >>> tx_harmonics.node_type

        """
        return self._node_type

    @min_aedt_version("2025.2")
    def import_csv_file(self, file_name: str) -> EmitNode:
        """Import a CSV File.

        Parameters
        ----------
        file_name : str
            File name.

        Examples
        --------
        >>> from ansys.aedt.core import Emit
        >>> app = Emit()
        >>> emitter, antenna = app.schematic.create_radio_antenna("Bluetooth")
        >>> band = emitter.get_radio().add_band()
        >>> tx_profile = band.children[0]
        >>> tx_harmonics = tx_profile.add_custom_tx_harmonics()
        >>> tx_harmonics.import_csv_file("C:\\Measurements\\tx_harmonics.csv")

        """
        return self._import(file_name, "Csv")

    @min_aedt_version("2025.2")
    def delete(self) -> None:
        """
        Delete this node

        Examples
        --------
        >>> from ansys.aedt.core import Emit
        >>> app = Emit()
        >>> emitter, antenna = app.schematic.create_radio_antenna("Bluetooth")
        >>> band = emitter.get_radio().add_band()
        >>> tx_profile = band.children[0]
        >>> tx_harmonics = tx_profile.add_custom_tx_harmonics()
        >>> tx_harmonics.delete()

        """
        self._delete()

    @property
    @min_aedt_version("2025.2")
    def table_data(self) -> list[tuple]:
        """Edit Harmonics Table.

        Table consists of 2 columns:
        Harmonic:
            Value should be between 2 and 1000.
        Power (Relative or Absolute):
            Value should be between -1000 and 1000.

        Examples
        --------
        >>> from ansys.aedt.core import Emit
        >>> app = Emit()
        >>> emitter, antenna = app.schematic.create_radio_antenna("Bluetooth")
        >>> band = emitter.get_radio().add_band()
        >>> tx_profile = band.children[0]
        >>> tx_harmonics = tx_profile.add_custom_tx_harmonics()
        >>> tx_harmonics.table_data = [(2, -35.0), (3, -45.0)]
        >>> tx_harmonics.table_data

        """
        return self._get_table_data()

    @table_data.setter
    @min_aedt_version("2025.2")
    def table_data(self, value: list[tuple]) -> None:
        self._set_table_data(value)

    @property
    @min_aedt_version("2025.2")
    def enabled(self) -> bool:
        """
        Enabled state for this node.

        Examples
        --------
        >>> from ansys.aedt.core import Emit
        >>> app = Emit()
        >>> emitter, antenna = app.schematic.create_radio_antenna("Bluetooth")
        >>> band = emitter.get_radio().add_band()
        >>> tx_profile = band.children[0]
        >>> tx_harmonics = tx_profile.add_custom_tx_harmonics()
        >>> tx_harmonics.enabled = False
        >>> tx_harmonics.enabled

        """
        return self._get_property("Enabled") == "true"

    @enabled.setter
    @min_aedt_version("2025.2")
    def enabled(self, value: bool) -> None:
        self._set_property("Enabled", f"{str(value).lower()}")

    class HarmonicTableUnitsOption(Enum):
        ABSOLUTE = "Absolute"
        RELATIVE = "Relative"

    @property
    @min_aedt_version("2025.2")
    def harmonic_table_units(self) -> HarmonicTableUnitsOption:
        """
        Specifies the units for the Harmonics.

        Examples
        --------
        >>> from ansys.aedt.core import Emit
        >>> app = Emit()
        >>> emitter, antenna = app.schematic.create_radio_antenna("Bluetooth")
        >>> band = emitter.get_radio().add_band()
        >>> tx_profile = band.children[0]
        >>> tx_harmonics = tx_profile.add_custom_tx_harmonics()
        >>> tx_harmonics.harmonic_table_units = tx_harmonics.HarmonicTableUnitsOption.RELATIVE
        >>> tx_harmonics.harmonic_table_units

        """
        val = self._get_property("Harmonic Table Units")
        val = self.HarmonicTableUnitsOption[val.upper()]
        return val

    @harmonic_table_units.setter
    @min_aedt_version("2025.2")
    def harmonic_table_units(self, value: HarmonicTableUnitsOption) -> None:
        self._set_property("Harmonic Table Units", f"{value.value}")
