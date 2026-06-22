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


class Isolator(EmitNode):
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
        >>> isolator = app.schematic.create_component("Isolator", name="Isolator1")
        >>> isolator.node_type
        """
        return self._node_type

    @min_aedt_version("2025.2")
    def duplicate(self, new_name: str = "") -> EmitNode:
        """Duplicate this node

        Examples
        --------
        >>> from ansys.aedt.core import Emit
        >>> app = Emit()
        >>> isolator = app.schematic.create_component("Isolator", name="Isolator1")
        >>> isolator_copy = isolator.duplicate("IsolatorCopy")
        """
        return self._duplicate(new_name)

    @min_aedt_version("2025.2")
    def delete(self) -> None:
        """Delete this node

        Examples
        --------
        >>> from ansys.aedt.core import Emit
        >>> app = Emit()
        >>> isolator = app.schematic.create_component("Isolator", name="Isolator1")
        >>> isolator.delete()
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
        >>> isolator = app.schematic.create_component("Isolator", name="Isolator1")
        >>> isolator.filename = "C:\\Temp\\isolator.s2p"
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
        >>> isolator = app.schematic.create_component("Isolator", name="Isolator1")
        >>> isolator.noise_temperature = 290.0
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
        >>> isolator = app.schematic.create_component("Isolator", name="Isolator1")
        >>> isolator.notes = "Updated for the link budget study"
        """
        val = self._get_property("Notes")
        return val

    @notes.setter
    @min_aedt_version("2025.2")
    def notes(self, value: str) -> None:
        self._set_property("Notes", f"{value}")

    class IsolatorTypeOption(Enum):
        BY_FILE = "ByFile"
        PARAMETRIC = "Parametric"

    @property
    @min_aedt_version("2025.2")
    def isolator_type(self) -> IsolatorTypeOption:
        """Isolator Type.

        Type of isolator model to use. Options include: By File (measured or
        simulated) or Parametric.


        Examples
        --------
        >>> from ansys.aedt.core import Emit
        >>> app = Emit()
        >>> isolator = app.schematic.create_component("Isolator", name="Isolator1")
        >>> isolator.isolator_type = isolator.IsolatorTypeOption.PARAMETRIC
        """
        val = self._get_property("Isolator Type")
        val = self.IsolatorTypeOption[val.upper()]
        return val

    @isolator_type.setter
    @min_aedt_version("2025.2")
    def isolator_type(self, value: IsolatorTypeOption) -> None:
        self._set_property("Isolator Type", f"{value.value}")

    @property
    @min_aedt_version("2025.2")
    def insertion_loss(self) -> float:
        """Isolator in-band loss in forward direction.

        Value should be between 0 and 100.


        Examples
        --------
        >>> from ansys.aedt.core import Emit
        >>> app = Emit()
        >>> isolator = app.schematic.create_component("Isolator", name="Isolator1")
        >>> isolator.insertion_loss = 1.2
        """
        val = self._get_property("Insertion Loss")
        return float(val)

    @insertion_loss.setter
    @min_aedt_version("2025.2")
    def insertion_loss(self, value: float) -> None:
        self._set_property("Insertion Loss", f"{value}")

    @property
    @min_aedt_version("2025.2")
    def finite_reverse_isolation(self) -> bool:
        """Finite Reverse Isolation.

        Use a finite reverse isolation. If disabled, the  isolator model is
        ideal (infinite reverse isolation).

        Value should be 'true' or 'false'.


        Examples
        --------
        >>> from ansys.aedt.core import Emit
        >>> app = Emit()
        >>> isolator = app.schematic.create_component("Isolator", name="Isolator1")
        >>> isolator.finite_reverse_isolation = True
        """
        val = self._get_property("Finite Reverse Isolation")
        return val == "true"

    @finite_reverse_isolation.setter
    @min_aedt_version("2025.2")
    def finite_reverse_isolation(self, value: bool) -> None:
        self._set_property("Finite Reverse Isolation", f"{str(value).lower()}")

    @property
    @min_aedt_version("2025.2")
    def reverse_isolation(self) -> float:
        """Isolator reverse isolation (i.e., loss in the reverse direction).

        Value should be between 0 and 100.


        Examples
        --------
        >>> from ansys.aedt.core import Emit
        >>> app = Emit()
        >>> isolator = app.schematic.create_component("Isolator", name="Isolator1")
        >>> isolator.reverse_isolation = 35.0
        """
        val = self._get_property("Reverse Isolation")
        return float(val)

    @reverse_isolation.setter
    @min_aedt_version("2025.2")
    def reverse_isolation(self, value: float) -> None:
        self._set_property("Reverse Isolation", f"{value}")

    @property
    @min_aedt_version("2025.2")
    def finite_bandwidth(self) -> bool:
        """Finite Bandwidth.

        Use a finite bandwidth. If disabled, the  isolator model is ideal
        (infinite bandwidth).

        Value should be 'true' or 'false'.


        Examples
        --------
        >>> from ansys.aedt.core import Emit
        >>> app = Emit()
        >>> isolator = app.schematic.create_component("Isolator", name="Isolator1")
        >>> isolator.finite_bandwidth = True
        """
        val = self._get_property("Finite Bandwidth")
        return val == "true"

    @finite_bandwidth.setter
    @min_aedt_version("2025.2")
    def finite_bandwidth(self, value: bool) -> None:
        self._set_property("Finite Bandwidth", f"{str(value).lower()}")

    @property
    @min_aedt_version("2025.2")
    def out_of_band_attenuation(self) -> float:
        """Out-of-band loss (attenuation).

        Value should be between 0 and 200.


        Examples
        --------
        >>> from ansys.aedt.core import Emit
        >>> app = Emit()
        >>> isolator = app.schematic.create_component("Isolator", name="Isolator1")
        >>> isolator.out_of_band_attenuation = 60.0
        """
        val = self._get_property("Out-of-band Attenuation")
        return float(val)

    @out_of_band_attenuation.setter
    @min_aedt_version("2025.2")
    def out_of_band_attenuation(self, value: float) -> None:
        self._set_property("Out-of-band Attenuation", f"{value}")

    @property
    @min_aedt_version("2025.2")
    def lower_stop_band(self) -> float:
        """Lower stop band frequency.

        Value should be between 1 and 100e9.


        Examples
        --------
        >>> from ansys.aedt.core import Emit
        >>> app = Emit()
        >>> isolator = app.schematic.create_component("Isolator", name="Isolator1")
        >>> isolator.lower_stop_band = "1.8GHz"
        """
        val = self._get_property("Lower Stop Band")
        val = self._convert_from_internal_units(float(val), "Freq")
        return float(val)

    @lower_stop_band.setter
    @min_aedt_version("2025.2")
    def lower_stop_band(self, value: float | str) -> None:
        value = self._convert_to_internal_units(value, "Freq")
        self._set_property("Lower Stop Band", f"{value}")

    @property
    @min_aedt_version("2025.2")
    def lower_cutoff(self) -> float:
        """Lower cutoff frequency.

        Value should be between 1 and 100e9.


        Examples
        --------
        >>> from ansys.aedt.core import Emit
        >>> app = Emit()
        >>> isolator = app.schematic.create_component("Isolator", name="Isolator1")
        >>> isolator.lower_cutoff = "2.0GHz"
        """
        val = self._get_property("Lower Cutoff")
        val = self._convert_from_internal_units(float(val), "Freq")
        return float(val)

    @lower_cutoff.setter
    @min_aedt_version("2025.2")
    def lower_cutoff(self, value: float | str) -> None:
        value = self._convert_to_internal_units(value, "Freq")
        self._set_property("Lower Cutoff", f"{value}")

    @property
    @min_aedt_version("2025.2")
    def higher_cutoff(self) -> float:
        """Higher cutoff frequency.

        Value should be between 1 and 100e9.


        Examples
        --------
        >>> from ansys.aedt.core import Emit
        >>> app = Emit()
        >>> isolator = app.schematic.create_component("Isolator", name="Isolator1")
        >>> isolator.higher_cutoff = "2.2GHz"
        """
        val = self._get_property("Higher Cutoff")
        val = self._convert_from_internal_units(float(val), "Freq")
        return float(val)

    @higher_cutoff.setter
    @min_aedt_version("2025.2")
    def higher_cutoff(self, value: float | str) -> None:
        value = self._convert_to_internal_units(value, "Freq")
        self._set_property("Higher Cutoff", f"{value}")

    @property
    @min_aedt_version("2025.2")
    def higher_stop_band(self) -> float:
        """Higher stop band frequency.

        Value should be between 1 and 100e9.


        Examples
        --------
        >>> from ansys.aedt.core import Emit
        >>> app = Emit()
        >>> isolator = app.schematic.create_component("Isolator", name="Isolator1")
        >>> isolator.higher_stop_band = "2.4GHz"
        """
        val = self._get_property("Higher Stop Band")
        val = self._convert_from_internal_units(float(val), "Freq")
        return float(val)

    @higher_stop_band.setter
    @min_aedt_version("2025.2")
    def higher_stop_band(self, value: float | str) -> None:
        value = self._convert_to_internal_units(value, "Freq")
        self._set_property("Higher Stop Band", f"{value}")

    @property
    @min_aedt_version("2025.2")
    def warnings(self) -> str:
        """Warning(s) for this node.

        Examples
        --------
        >>> from ansys.aedt.core import Emit
        >>> app = Emit()
        >>> isolator = app.schematic.create_component("Isolator", name="Isolator1")
        >>> isolator.warnings
        """
        val = self._get_property("Warnings")
        return val
