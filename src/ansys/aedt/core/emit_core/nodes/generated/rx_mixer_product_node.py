# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 - 2025 ANSYS, Inc. and/or its affiliates.
# SPDX-FileCopyrightText: 2021 - 2025 ANSYS, Inc. and /or its affiliates.
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


class RxMixerProductNode(EmitNode):
    def __init__(self, emit_obj, result_id, node_id):
        self._is_component = False
        EmitNode.__init__(self, emit_obj, result_id, node_id)

    @property
    def parent(self):
        """The parent of this emit node."""
        return self._parent

    @property
    def node_type(self) -> str:
        """The type of this emit node."""
        return self._node_type

    def import_csv_file(self, file_name):
        """Import a CSV File..."""
        return self._import(file_name, "Csv")

    def delete(self):
        """Delete this node"""
        self._delete()

    @property
    def table_data(self):
        """Edit Mixer Products Table.
        Table consists of 3 columns.
        RF Harmonic Order:
            Value should be between -100 and 100.
        LO Harmonic Order:
            Value should be between 1 and 100.
        Power (Relative or Absolute):
            Value should be between -1000 and 1000.
        """
        return self._get_table_data()

    @table_data.setter
    def table_data(self, value):
        self._set_table_data(value)

    @property
    def enabled(self) -> bool:
        """Enabled state for this node."""
        return self._get_property("Enabled")

    @enabled.setter
    def enabled(self, value: bool):
        self._set_property("Enabled", f"{str(value).lower()}")

    class MixerProductTaperOption(Enum):
        CONSTANT = "Constant"
        MIL_STD_461G = "MIL-STD-461G"
        DUFF_MODEL = "Duff Model"

    @property
    def mixer_product_taper(self) -> MixerProductTaperOption:
        """Taper for setting amplitude of mixer products."""
        val = self._get_property("Mixer Product Taper")
        val = self.MixerProductTaperOption[val.upper()]
        return val

    @mixer_product_taper.setter
    def mixer_product_taper(self, value: MixerProductTaperOption):
        self._set_property("Mixer Product Taper", f"{value.value}")

    @property
    def mixer_product_susceptibility(self) -> float:
        """Mixer product amplitudes (relative to the in-band susceptibility).

        Value should be between -200 and 200.
        """
        val = self._get_property("Mixer Product Susceptibility")
        return float(val)

    @mixer_product_susceptibility.setter
    def mixer_product_susceptibility(self, value: float):
        self._set_property("Mixer Product Susceptibility", f"{value}")

    @property
    def spurious_rejection(self) -> float:
        """Mixer product amplitudes (relative to the in-band susceptibility).

        Value should be between -200 and 200.
        """
        val = self._get_property("Spurious Rejection")
        return float(val)

    @spurious_rejection.setter
    def spurious_rejection(self, value: float):
        self._set_property("Spurious Rejection", f"{value}")

    @property
    def minimum_tuning_frequency(self) -> float:
        """Minimum tuning frequency of Rx's local oscillator.

        Value should be between 1 and 100e9.
        """
        val = self._get_property("Minimum Tuning Frequency")
        val = self._convert_from_internal_units(float(val), "Freq")
        return float(val)

    @minimum_tuning_frequency.setter
    def minimum_tuning_frequency(self, value: float | str):
        value = self._convert_to_internal_units(value, "Freq")
        self._set_property("Minimum Tuning Frequency", f"{value}")

    @property
    def maximum_tuning_frequency(self) -> float:
        """Maximum tuning frequency of Rx's local oscillator.

        Value should be between 1 and 100e9.
        """
        val = self._get_property("Maximum Tuning Frequency")
        val = self._convert_from_internal_units(float(val), "Freq")
        return float(val)

    @maximum_tuning_frequency.setter
    def maximum_tuning_frequency(self, value: float | str):
        value = self._convert_to_internal_units(value, "Freq")
        self._set_property("Maximum Tuning Frequency", f"{value}")

    @property
    def mixer_product_slope(self) -> float:
        """Mixer Product Slope.

        Rate of decrease for amplitude of Rx's local oscillator harmonics
        (dB/decade).

        Value should be between 0 and 100.
        """
        val = self._get_property("Mixer Product Slope")
        return float(val)

    @mixer_product_slope.setter
    def mixer_product_slope(self, value: float):
        self._set_property("Mixer Product Slope", f"{value}")

    @property
    def mixer_product_intercept(self) -> float:
        """Mixer product intercept (dBc).

        Value should be between 0 and 100.
        """
        val = self._get_property("Mixer Product Intercept")
        return float(val)

    @mixer_product_intercept.setter
    def mixer_product_intercept(self, value: float):
        self._set_property("Mixer Product Intercept", f"{value}")

    @property
    def bandwidth_80_db(self) -> float:
        """Bandwidth 80 dB.

        Bandwidth where Rx's susceptibility envelope is 80 dB above in-band
        susceptibility level.

        Value should be greater than 1.
        """
        val = self._get_property("Bandwidth 80 dB")
        val = self._convert_from_internal_units(float(val), "Freq")
        return float(val)

    @bandwidth_80_db.setter
    def bandwidth_80_db(self, value: float | str):
        value = self._convert_to_internal_units(value, "Freq")
        self._set_property("Bandwidth 80 dB", f"{value}")

    @property
    def image_rejection(self) -> float:
        """Image frequency amplitude (relative to the in-band susceptibility).

        Value should be between -200 and 200.
        """
        val = self._get_property("Image Rejection")
        return float(val)

    @image_rejection.setter
    def image_rejection(self, value: float):
        self._set_property("Image Rejection", f"{value}")

    @property
    def maximum_rf_harmonic_order(self) -> int:
        """Maximum order of RF frequency.

        Value should be between 1 and 100.
        """
        val = self._get_property("Maximum RF Harmonic Order")
        return int(val)

    @maximum_rf_harmonic_order.setter
    def maximum_rf_harmonic_order(self, value: int):
        self._set_property("Maximum RF Harmonic Order", f"{value}")

    @property
    def maximum_lo_harmonic_order(self) -> int:
        """Maximum order of the LO frequency.

        Value should be between 1 and 100.
        """
        val = self._get_property("Maximum LO Harmonic Order")
        return int(val)

    @maximum_lo_harmonic_order.setter
    def maximum_lo_harmonic_order(self, value: int):
        self._set_property("Maximum LO Harmonic Order", f"{value}")

    class MixingModeOption(Enum):
        LO_ABOVE_TUNED_RF_FREQUENCY = "LO Above Tuned (RF) Frequency"
        LO_BELOW_TUNED_RF_FREQUENCY = "LO Below Tuned (RF) Frequency"
        LO_ABOVEBELOW_TUNED_RF_FREQUENCY = "LO Above/Below Tuned (RF) Frequency"

    @property
    def mixing_mode(self) -> MixingModeOption:
        """Specifies whether the IF frequency is > or < RF channel frequency."""
        val = self._get_property("Mixing Mode")
        val = self.MixingModeOption[val.upper()]
        return val

    @mixing_mode.setter
    def mixing_mode(self, value: MixingModeOption):
        self._set_property("Mixing Mode", f"{value.value}")

    @property
    def first_if_frequency(self):
        """Intermediate frequency for Rx's 1st conversion stage.

        Value should be a mathematical expression.
        """
        val = self._get_property("First IF Frequency")
        return val

    @first_if_frequency.setter
    def first_if_frequency(self, value):
        self._set_property("First IF Frequency", f"{value}")

    @property
    def rf_transition_frequency(self) -> float:
        """RF Frequency Transition point."""
        val = self._get_property("RF Transition Frequency")
        val = self._convert_from_internal_units(float(val), "Freq")
        return float(val)

    @rf_transition_frequency.setter
    def rf_transition_frequency(self, value: float | str):
        value = self._convert_to_internal_units(value, "Freq")
        self._set_property("RF Transition Frequency", f"{value}")

    class UseHighLOOption(Enum):
        ABOVE_TRANSITION_FREQUENCY = "Above Transition Frequency"
        BELOW_TRANSITION_FREQUENCY = "Below Transition Frequency"

    @property
    def use_high_lo(self) -> UseHighLOOption:
        """Use High LO above/below the transition frequency."""
        val = self._get_property("Use High LO")
        val = self.UseHighLOOption[val.upper()]
        return val

    @use_high_lo.setter
    def use_high_lo(self, value: UseHighLOOption):
        self._set_property("Use High LO", f"{value.value}")

    class MixerProductTableUnitsOption(Enum):
        ABSOLUTE = "Absolute"
        RELATIVE = "Relative"

    @property
    def mixer_product_table_units(self) -> MixerProductTableUnitsOption:
        """Specifies the units for the Mixer Products."""
        val = self._get_property("Mixer Product Table Units")
        val = self.MixerProductTableUnitsOption[val.upper()]
        return val

    @mixer_product_table_units.setter
    def mixer_product_table_units(self, value: MixerProductTableUnitsOption):
        self._set_property("Mixer Product Table Units", f"{value.value}")
