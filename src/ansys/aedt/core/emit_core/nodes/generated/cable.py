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


class Cable(EmitNode):
    """Provide cable."""

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
        >>> cable = app.schematic.create_component("Cable", name="Cable1")
        >>> cable.node_type
        """
        return self._node_type

    @min_aedt_version("2025.2")
    def duplicate(self, new_name: str = "") -> EmitNode:
        """Duplicate this node

        Examples
        --------
        >>> from ansys.aedt.core import Emit
        >>> app = Emit()
        >>> cable = app.schematic.create_component("Cable", name="Cable1")
        >>> cable_copy = cable.duplicate("CableCopy")
        """
        return self._duplicate(new_name)

    @min_aedt_version("2025.2")
    def delete(self) -> None:
        """Delete this node

        Examples
        --------
        >>> from ansys.aedt.core import Emit
        >>> app = Emit()
        >>> cable = app.schematic.create_component("Cable", name="Cable1")
        >>> cable.delete()
        """
        self._delete()

    @property
    @min_aedt_version("2025.2")
    def filename(self) -> str:
        """Name of file defining the outboard component.

        Value should be a full file path.

        Examples
        --------
        >>> from ansys.aedt.core import Emit
        >>> app = Emit()
        >>> cable = app.schematic.create_component("Cable", name="Cable1")
        >>> cable.filename = "C:\\Temp\\cable.s2p"
        >>> cable.filename
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
        >>> cable = app.schematic.create_component("Cable", name="Cable1")
        >>> cable.noise_temperature = 290.0
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
        >>> cable = app.schematic.create_component("Cable", name="Cable1")
        >>> cable.notes = "Route between modules"
        """
        val = self._get_property("Notes")
        return val

    @notes.setter
    @min_aedt_version("2025.2")
    def notes(self, value: str) -> None:
        self._set_property("Notes", f"{value}")

    class CableTypeOption(Enum):
        BY_FILE = "ByFile"
        CONSTANT_LOSS = "Constant"
        COAXIAL_CABLE = "Coaxial"

    @property
    @min_aedt_version("2025.2")
    def cable_type(self) -> CableTypeOption:
        """Cable Type.

        Type of cable to use. Options include: By File (measured or simulated),
        Constant Loss, or Coaxial Cable.

        Examples
        --------
        >>> from ansys.aedt.core import Emit
        >>> app = Emit()
        >>> cable = app.schematic.create_component("Cable", name="Cable1")
        >>> cable.cable_type = cable.CableTypeOption.CONSTANT_LOSS
        """
        val = self._get_property("Cable Type")
        val = self.CableTypeOption[val.upper()]
        return val

    @cable_type.setter
    @min_aedt_version("2025.2")
    def cable_type(self, value: CableTypeOption) -> None:
        self._set_property("Cable Type", f"{value.value}")

    @property
    @min_aedt_version("2025.2")
    def length(self) -> float:
        """Length of cable.

        Value should be between 0 and 500.

        Examples
        --------
        >>> from ansys.aedt.core import Emit
        >>> app = Emit()
        >>> cable = app.schematic.create_component("Cable", name="Cable1")
        >>> cable.length = "5 m"
        """
        val = self._get_property("Length")
        val = self._convert_from_internal_units(float(val), "Length")
        return float(val)

    @length.setter
    @min_aedt_version("2025.2")
    def length(self, value: float | str) -> None:
        value = self._convert_to_internal_units(value, "Length")
        self._set_property("Length", f"{value}")

    @property
    @min_aedt_version("2025.2")
    def loss_per_length(self) -> float:
        """Cable loss per unit length (dB/meter).

        Value should be between 0 and 20.

        Examples
        --------
        >>> from ansys.aedt.core import Emit
        >>> app = Emit()
        >>> cable = app.schematic.create_component("Cable", name="Cable1")
        >>> cable.loss_per_length = 0.25
        """
        val = self._get_property("Loss Per Length")
        return float(val)

    @loss_per_length.setter
    @min_aedt_version("2025.2")
    def loss_per_length(self, value: float) -> None:
        self._set_property("Loss Per Length", f"{value}")

    @property
    @min_aedt_version("2025.2")
    def measurement_length(self) -> float:
        """Length of the cable used for the measurements.

        Value should be between 0 and 500.

        Examples
        --------
        >>> from ansys.aedt.core import Emit
        >>> app = Emit()
        >>> cable = app.schematic.create_component("Cable", name="Cable1")
        >>> cable.measurement_length = "2 m"
        """
        val = self._get_property("Measurement Length")
        val = self._convert_from_internal_units(float(val), "Length")
        return float(val)

    @measurement_length.setter
    @min_aedt_version("2025.2")
    def measurement_length(self, value: float | str) -> None:
        value = self._convert_to_internal_units(value, "Length")
        self._set_property("Measurement Length", f"{value}")

    @property
    @min_aedt_version("2025.2")
    def resistive_loss_constant(self) -> float:
        """Coaxial cable resistive loss constant.

        Value should be between 0 and 2.

        Examples
        --------
        >>> from ansys.aedt.core import Emit
        >>> app = Emit()
        >>> cable = app.schematic.create_component("Cable", name="Cable1")
        >>> cable.resistive_loss_constant = 0.1
        """
        val = self._get_property("Resistive Loss Constant")
        return float(val)

    @resistive_loss_constant.setter
    @min_aedt_version("2025.2")
    def resistive_loss_constant(self, value: float) -> None:
        self._set_property("Resistive Loss Constant", f"{value}")

    @property
    @min_aedt_version("2025.2")
    def dielectric_loss_constant(self) -> float:
        """Coaxial cable dielectric loss constant.

        Value should be between 0 and 1.

        Examples
        --------
        >>> from ansys.aedt.core import Emit
        >>> app = Emit()
        >>> cable = app.schematic.create_component("Cable", name="Cable1")
        >>> cable.dielectric_loss_constant = 0.01
        """
        val = self._get_property("Dielectric Loss Constant")
        return float(val)

    @dielectric_loss_constant.setter
    @min_aedt_version("2025.2")
    def dielectric_loss_constant(self, value: float) -> None:
        self._set_property("Dielectric Loss Constant", f"{value}")

    @property
    @min_aedt_version("2025.2")
    def warnings(self) -> str:
        """Warning(s) for this node.

        Examples
        --------
        >>> from ansys.aedt.core import Emit
        >>> app = Emit()
        >>> cable = app.schematic.create_component("Cable", name="Cable1")
        >>> cable.warnings
        """
        val = self._get_property("Warnings")
        return val
