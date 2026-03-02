# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 - 2026 ANSYS, Inc. and/or its affiliates.
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


class RxSusceptibilityProfNode(EmitNode):
    def __init__(self, emit_obj, result_id, node_id) -> None:
        EmitNode.__init__(self, emit_obj, result_id, node_id)
        self._is_component = False

    @property
    @min_aedt_version("2025.2")
    def parent(self) -> EmitNode:
        """The parent of this emit node."""
        return self._parent

    @property
    @min_aedt_version("2025.2")
    def node_type(self) -> str:
        """The type of this emit node."""
        return self._node_type

    @min_aedt_version("2025.2")
    def add_rx_saturation(self) -> EmitNode:
        """Add a Saturation Profile"""
        return self._add_child_node("Rx Saturation")

    @min_aedt_version("2025.2")
    def add_rx_selectivity(self) -> EmitNode:
        """Add a Selectivity Profile"""
        return self._add_child_node("Rx Selectivity")

    @min_aedt_version("2025.2")
    def add_mixer_products(self) -> EmitNode:
        """Add a Receiver Mixer Product Node"""
        return self._add_child_node("Mixer Products")

    @min_aedt_version("2025.2")
    def add_spurious_responses(self) -> EmitNode:
        """Add Receiver Spurs"""
        return self._add_child_node("Spurious Responses")

    @property
    @min_aedt_version("2025.2")
    def enabled(self) -> bool:
        """Enabled state for this node."""
        return self._get_property("Enabled") == "true"

    @enabled.setter
    @min_aedt_version("2025.2")
    def enabled(self, value: bool):
        self._set_property("Enabled", f"{str(value).lower()}")

    class SensitivityUnitsOption(Enum):
        DBM = "dBm"
        DBUV = "dBuV"
        MILLIWATTS = "milliwatts"
        MICROVOLTS = "microvolts"

    @property
    @min_aedt_version("2025.2")
    def sensitivity_units(self) -> SensitivityUnitsOption:
        """Units to use for the Rx Sensitivity."""
        val = self._get_property("Sensitivity Units")
        val = self.SensitivityUnitsOption[val.upper()]
        return val

    @sensitivity_units.setter
    @min_aedt_version("2025.2")
    def sensitivity_units(self, value: SensitivityUnitsOption):
        self._set_property("Sensitivity Units", f"{value.value}")

    @property
    @min_aedt_version("2025.2")
    def min_receive_signal_pwr(self) -> float:
        """Received signal power level at the Rx's antenna terminal.

        Value should be between -1000 and 1000.
        """
        val = self._get_property("Min. Receive Signal Pwr")
        return float(val)

    @min_receive_signal_pwr.setter
    @min_aedt_version("2025.2")
    def min_receive_signal_pwr(self, value: float):
        self._set_property("Min. Receive Signal Pwr", f"{value}")

    @property
    @min_aedt_version("2025.2")
    def snr_at_rx_signal_pwr(self) -> float:
        """SNR at Rx Signal Pwr.

        Signal-to-Noise Ratio (dB) at specified received signal power at the
        Rx's antenna terminal.

        Value should be between -1000 and 1000.
        """
        val = self._get_property("SNR at Rx Signal Pwr")
        return float(val)

    @snr_at_rx_signal_pwr.setter
    @min_aedt_version("2025.2")
    def snr_at_rx_signal_pwr(self, value: float):
        self._set_property("SNR at Rx Signal Pwr", f"{value}")

    @property
    @min_aedt_version("2025.2")
    def processing_gain(self) -> float:
        """Rx processing gain (dB) of (optional) despreader.

        Value should be between -1000 and 1000.
        """
        val = self._get_property("Processing Gain")
        return float(val)

    @processing_gain.setter
    @min_aedt_version("2025.2")
    def processing_gain(self, value: float):
        self._set_property("Processing Gain", f"{value}")

    @property
    @min_aedt_version("2025.2")
    def apply_pg_to_narrowband_only(self) -> bool:
        """Apply PG to Narrowband Only.

        Processing gain captures the despreading effect and applies to NB
        signals only (not BB noise) when enabled.

        Value should be 'true' or 'false'.
        """
        val = self._get_property("Apply PG to Narrowband Only")
        return val == "true"

    @apply_pg_to_narrowband_only.setter
    @min_aedt_version("2025.2")
    def apply_pg_to_narrowband_only(self, value: bool):
        self._set_property("Apply PG to Narrowband Only", f"{str(value).lower()}")

    @property
    @min_aedt_version("2025.2")
    def saturation_level(self) -> float:
        """Rx input saturation level.

        Value should be between -1000 and 1000.
        """
        val = self._get_property("Saturation Level")
        val = self._convert_from_internal_units(float(val), "Power")
        return float(val)

    @saturation_level.setter
    @min_aedt_version("2025.2")
    def saturation_level(self, value: float | str):
        value = self._convert_to_internal_units(value, "Power")
        self._set_property("Saturation Level", f"{value}")

    @property
    @min_aedt_version("2025.2")
    def rx_noise_figure(self) -> float:
        """Rx noise figure (dB).

        Value should be between 0 and 1000.
        """
        val = self._get_property("Rx Noise Figure")
        return float(val)

    @rx_noise_figure.setter
    @min_aedt_version("2025.2")
    def rx_noise_figure(self, value: float):
        self._set_property("Rx Noise Figure", f"{value}")

    @property
    @min_aedt_version("2025.2")
    def receiver_sensitivity(self) -> float:
        """Rx minimum sensitivity level (dBm).

        Value should be between -1000 and 1000.
        """
        val = self._get_property("Receiver Sensitivity")
        val = self._convert_from_internal_units(float(val), "Power")
        return float(val)

    @receiver_sensitivity.setter
    @min_aedt_version("2025.2")
    def receiver_sensitivity(self, value: float | str):
        value = self._convert_to_internal_units(value, "Power")
        self._set_property("Receiver Sensitivity", f"{value}")

    @property
    @min_aedt_version("2025.2")
    def snrsinad_at_sensitivity(self) -> float:
        """SNR or SINAD at the specified sensitivity level.

        Value should be between -1000 and 1000.
        """
        val = self._get_property("SNR/SINAD at Sensitivity")
        return float(val)

    @snrsinad_at_sensitivity.setter
    @min_aedt_version("2025.2")
    def snrsinad_at_sensitivity(self, value: float):
        self._set_property("SNR/SINAD at Sensitivity", f"{value}")

    @property
    @min_aedt_version("2025.2")
    def perform_rx_intermod_analysis(self) -> bool:
        """Performs a non-linear intermod analysis for the Rx.

        Value should be 'true' or 'false'.
        """
        val = self._get_property("Perform Rx Intermod Analysis")
        return val == "true"

    @perform_rx_intermod_analysis.setter
    @min_aedt_version("2025.2")
    def perform_rx_intermod_analysis(self, value: bool):
        self._set_property("Perform Rx Intermod Analysis", f"{str(value).lower()}")

    @property
    @min_aedt_version("2025.2")
    def amplifier_saturation_level(self) -> float:
        """Internal Rx Amplifier's Saturation Level.

        Value should be between -200 and 200.
        """
        val = self._get_property("Amplifier Saturation Level")
        val = self._convert_from_internal_units(float(val), "Power")
        return float(val)

    @amplifier_saturation_level.setter
    @min_aedt_version("2025.2")
    def amplifier_saturation_level(self, value: float | str):
        value = self._convert_to_internal_units(value, "Power")
        self._set_property("Amplifier Saturation Level", f"{value}")

    @property
    @min_aedt_version("2025.2")
    def p1_db_point_ref_input(self) -> float:
        """P1-dB Point, Ref. Input.

        Rx's 1 dB Compression Point - total power > P1dB saturates the receiver.

        Value should be between -1000 and 1000.
        """
        val = self._get_property("P1-dB Point, Ref. Input")
        val = self._convert_from_internal_units(float(val), "Power")
        return float(val)

    @p1_db_point_ref_input.setter
    @min_aedt_version("2025.2")
    def p1_db_point_ref_input(self, value: float | str):
        value = self._convert_to_internal_units(value, "Power")
        self._set_property("P1-dB Point, Ref. Input", f"{value}")

    @property
    @min_aedt_version("2025.2")
    def ip3_ref_input(self) -> float:
        """Internal Rx Amplifier's 3rd order intercept point.

        Value should be between -1000 and 1000.
        """
        val = self._get_property("IP3, Ref. Input")
        val = self._convert_from_internal_units(float(val), "Power")
        return float(val)

    @ip3_ref_input.setter
    @min_aedt_version("2025.2")
    def ip3_ref_input(self, value: float | str):
        value = self._convert_to_internal_units(value, "Power")
        self._set_property("IP3, Ref. Input", f"{value}")

    @property
    @min_aedt_version("2025.2")
    def max_intermod_order(self) -> int:
        """Internal Rx Amplifier's maximum intermod order to compute.

        Value should be between 3 and 20.
        """
        val = self._get_property("Max Intermod Order")
        return int(val)

    @max_intermod_order.setter
    @min_aedt_version("2025.2")
    def max_intermod_order(self, value: int):
        self._set_property("Max Intermod Order", f"{value}")
