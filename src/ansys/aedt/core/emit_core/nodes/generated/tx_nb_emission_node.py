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


class TxNbEmissionNode(EmitNode):
    """Provide tx nb emission node."""

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
        >>> tx_spec = radio.children[0].children[0]
        >>> nb_mask = tx_spec.add_narrowband_emissions_mask()
        >>> nb_mask.parent

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
        >>> tx_spec = radio.children[0].children[0]
        >>> nb_mask = tx_spec.add_narrowband_emissions_mask()
        >>> nb_mask.node_type

        """
        return self._node_type

    @min_aedt_version("2025.2")
    def import_csv_file(self, file_name: str) -> EmitNode:
        """
        Import a CSV File...

        Examples
        --------
        >>> from ansys.aedt.core import Emit
        >>> app = Emit()
        >>> radio = app.schematic.create_component("New Radio")
        >>> tx_spec = radio.children[0].children[0]
        >>> nb_mask = tx_spec.add_narrowband_emissions_mask()
        >>> nb_mask.import_csv_file("C:\\Temp\\tx_nb_emission.csv")

        """
        return self._import(file_name, "Csv")

    @min_aedt_version("2025.2")
    def delete(self) -> None:
        """Delete this node.

        Examples
        --------
        >>> from ansys.aedt.core import Emit
        >>> app = Emit()
        >>> radio = app.schematic.create_component("New Radio")
        >>> tx_spec = radio.children[0].children[0]
        >>> nb_mask = tx_spec.add_narrowband_emissions_mask()
        >>> nb_mask.delete()

        """
        self._delete()

    @property
    @min_aedt_version("2025.2")
    def table_data(self) -> list[tuple]:
        """
        Tx Emissions Profile Table.
        Table consists of 2 columns.
        Bandwidth or Frequency:
            Value should be between 1 and 100e9.
        Attenuation or Power:
            Value should be between -1000 and 1000.

        Examples
        --------
        >>> from ansys.aedt.core import Emit
        >>> app = Emit()
        >>> radio = app.schematic.create_component("New Radio")
        >>> tx_spec = radio.children[0].children[0]
        >>> nb_mask = tx_spec.add_narrowband_emissions_mask()
        >>> nb_mask.table_data = [("1 MHz", "-40 dB"), ("5 MHz", "-55 dB")]

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
        >>> radio = app.schematic.create_component("New Radio")
        >>> tx_spec = radio.children[0].children[0]
        >>> nb_mask = tx_spec.add_narrowband_emissions_mask()
        >>> nb_mask.enabled = True

        """
        return self._get_property("Enabled") == "true"

    @enabled.setter
    @min_aedt_version("2025.2")
    def enabled(self, value: bool) -> None:
        self._set_property("Enabled", f"{str(value).lower()}")

    class NarrowbandBehaviorOption(Enum):
        ABSOLUTE_FREQS_AND_POWER = "Absolute"
        RELATIVE_FREQS_AND_ATTENUATION = "RelativeBandwidth"

    @property
    @min_aedt_version("2025.2")
    def narrowband_behavior(self) -> NarrowbandBehaviorOption:
        """
        Specifies the behavior of the parametric narrowband emissions mask.

        Examples
        --------
        >>> from ansys.aedt.core import Emit
        >>> app = Emit()
        >>> radio = app.schematic.create_component("New Radio")
        >>> tx_spec = radio.children[0].children[0]
        >>> nb_mask = tx_spec.add_narrowband_emissions_mask()
        >>> nb_mask.narrowband_behavior = nb_mask.NarrowbandBehaviorOption.RELATIVE_FREQS_AND_ATTENUATION

        """
        val = self._get_property("Narrowband Behavior")
        val = self.NarrowbandBehaviorOption[val.upper()]
        return val

    @narrowband_behavior.setter
    @min_aedt_version("2025.2")
    def narrowband_behavior(self, value: NarrowbandBehaviorOption) -> None:
        self._set_property("Narrowband Behavior", f"{value.value}")

    @property
    @min_aedt_version("2025.2")
    def measurement_frequency(self) -> float:
        """
        Measurement frequency for the absolute freq/amp pairs.

        Examples
        --------
        >>> from ansys.aedt.core import Emit
        >>> app = Emit()
        >>> radio = app.schematic.create_component("New Radio")
        >>> tx_spec = radio.children[0].children[0]
        >>> nb_mask = tx_spec.add_narrowband_emissions_mask()
        >>> nb_mask.measurement_frequency = "2.45 GHz"

        """
        val = self._get_property("Measurement Frequency")
        val = self._convert_from_internal_units(float(val), "Freq")
        return float(val)

    @measurement_frequency.setter
    @min_aedt_version("2025.2")
    def measurement_frequency(self, value: float | str) -> None:
        value = self._convert_to_internal_units(value, "Freq")
        self._set_property("Measurement Frequency", f"{value}")
