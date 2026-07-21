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


class Multiplexer(EmitNode):
    """Provide multiplexer."""

    def __init__(self, emit_obj, result_id, node_id) -> None:
        EmitNode.__init__(self, emit_obj, result_id, node_id)
        self._is_component = True

    @property
    @min_aedt_version("2025.2")
    def node_type(self) -> str:
        """The type of this emit node.

        Examples
        --------
        >>> from ansys.aedt.core import Emit
        >>> app = Emit()
        >>> mux = app.schematic.create_component("Multiplexer")
        >>> mux.node_type

        """
        return self._node_type

    @min_aedt_version("2025.2")
    def add_multiplexer_pass_band(self) -> EmitNode:
        """Add a New Multiplexer Band to this Multiplexer

        Examples
        --------
        >>> from ansys.aedt.core import Emit
        >>> app = Emit()
        >>> mux = app.schematic.create_component("Multiplexer")
        >>> multiplexer_pass_band = mux.add_multiplexer_pass_band()

        """
        return self._add_child_node("Multiplexer Pass Band")

    @min_aedt_version("2027.1")
    def export_to_csv(self, file_name: str = "", ports: str = "1|2") -> str:
        """Export's the data for this node

        Parameters
        ----------
        file_name: str[optional]
            full path to the file to export to.
        ports: str
            the ports to export the data for.
            Default orientation port names: 1|2|3

        Returns
        -------
        csv_data: str
            stringified data for the node returned if file_name not specified"""
        keys = "SelectedInputPort|SelectedOutputPort"
        vals = f"{ports}"
        return self._export_to_csv(file_name, keys, vals)

    @min_aedt_version("2027.1")
    def plot(self, ports: str = "1|2"):
        """Bring up a Cartesian plot for this node

        Parameters
        ----------
        ports: str
            the ports to export the data for.
            Default orientation port names: 1|2|3"""
        keys = "SelectedInputPort|SelectedOutputPort"
        vals = f"{ports}"
        return self._plot(keys, vals)

    @min_aedt_version("2025.2")
    def duplicate(self, new_name: str = "") -> EmitNode:
        """Duplicate this node.

        Examples
        --------
        >>> from ansys.aedt.core import Emit
        >>> app = Emit()
        >>> mux = app.schematic.create_component("Multiplexer")
        >>> mux_copy = mux.duplicate("mux_copy")

        """
        return self._duplicate(new_name)

    @min_aedt_version("2025.2")
    def delete(self) -> None:
        """Delete this node.

        Examples
        --------
        >>> from ansys.aedt.core import Emit
        >>> app = Emit()
        >>> mux = app.schematic.create_component("Multiplexer")
        >>> mux.delete()

        """
        self._delete()

    @property
    @min_aedt_version("2025.2")
    def filename(self) -> str:
        """Name of file defining the multiplexer.

        Value should be a full file path.

        Examples
        --------
        >>> from ansys.aedt.core import Emit
        >>> app = Emit()
        >>> mux = app.schematic.create_component("Multiplexer")
        >>> mux.filename = "example_value"

        """
        val = self._get_property("Filename")
        return val

    @filename.setter
    @min_aedt_version("2025.2")
    def filename(self, value: str) -> None:
        self._set_property("Filename", f"{value}")

    @property
    @min_aedt_version("2025.2")
    def noise_temperature(self) -> float:
        """System Noise temperature (K) of the component.

        Value should be between 0 and 1000.

        Examples
        --------
        >>> from ansys.aedt.core import Emit
        >>> app = Emit()
        >>> mux = app.schematic.create_component("Multiplexer")
        >>> mux.noise_temperature = 290.0

        """
        val = self._get_property("Noise Temperature")
        return float(val)

    @noise_temperature.setter
    @min_aedt_version("2025.2")
    def noise_temperature(self, value: float) -> None:
        self._set_property("Noise Temperature", f"{value}")

    @property
    @min_aedt_version("2025.2")
    def notes(self) -> str:
        """Expand to view/edit notes stored with the project.

        Examples
        --------
        >>> from ansys.aedt.core import Emit
        >>> app = Emit()
        >>> mux = app.schematic.create_component("Multiplexer")
        >>> mux.notes = "example_value"

        """
        val = self._get_property("Notes")
        return val

    @notes.setter
    @min_aedt_version("2025.2")
    def notes(self, value: str) -> None:
        self._set_property("Notes", f"{value}")

    class MultiplexerTypeOption(Enum):
        BY_PASS_BAND = "Parametric"  # nosec
        BY_FILE = "ByFile"

    @property
    @min_aedt_version("2025.2")
    def multiplexer_type(self) -> MultiplexerTypeOption:
        """Multiplexer Type.

        Type of multiplexer model. Options include: By File (one measured or
        simulated file for the device) or By Pass Band (parametric or file-based
        definition for each pass band).

        Examples
        --------
        >>> from ansys.aedt.core import Emit
        >>> app = Emit()
        >>> mux = app.schematic.create_component("Multiplexer")
        >>> mux.multiplexer_type = Multiplexer.MultiplexerTypeOption.BY_PASS_BAND

        """
        val = self._get_property("Multiplexer Type")
        val = self.MultiplexerTypeOption[val.upper()]
        return val

    @multiplexer_type.setter
    @min_aedt_version("2025.2")
    def multiplexer_type(self, value: MultiplexerTypeOption) -> None:
        self._set_property("Multiplexer Type", f"{value.value}")

    @property
    @min_aedt_version("2025.2")
    def ports(self) -> list[str]:
        """Assigns the child port nodes to the multiplexers ports.

        Examples
        --------
        >>> from ansys.aedt.core import Emit
        >>> app = Emit()
        >>> mux = app.schematic.create_component("Multiplexer")
        >>> mux.ports

        """
        val = self._get_property("Ports")
        return val

    @ports.setter
    @min_aedt_version("2025.2")
    def ports(self, value: list[str] | str) -> None:
        if isinstance(value, (list, tuple)):
            value = "|".join(value)
        self._set_property("Ports", f"{value}")

    @property
    @min_aedt_version("2025.2")
    def warnings(self) -> str:
        """Warning(s) for this node.

        Examples
        --------
        >>> from ansys.aedt.core import Emit
        >>> app = Emit()
        >>> mux = app.schematic.create_component("Multiplexer")
        >>> mux.warnings

        """
        val = self._get_property("Warnings")
        return val
