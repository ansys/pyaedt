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

from ..EmitNode import EmitNode


class TxSpectralProfNode(EmitNode):
    def __init__(self, emit_obj, result_id, node_id):
        self._is_component = False
        EmitNode.__init__(self, emit_obj, result_id, node_id)

    @property
    def parent(self):
        """The parent of this emit node."""
        return self._parent

    @property
    def enabled(self) -> bool:
        """Enabled state for this node."""
        return self._oRevisionData.GetEmitNodeProperties(self._result_id, self._node_id, "enabled")

    @enabled.setter
    def enabled(self, value: bool):
        self._oRevisionData.SetEmitNodeProperties(self._result_id, self._node_id, [f"enabled= + {value}"])

    class SpectrumTypeOption(Enum):
        NARROWBAND__BROADBAND = "Narrowband & Broadband"  # eslint-disable-line no-eval
        BROADBAND_ONLY = "Broadband Only"  # eslint-disable-line no-eval

    @property
    def spectrum_type(self) -> SpectrumTypeOption:
        """Spectrum Type
        Specifies EMI Margins to calculate

        """
        val = self._get_property("Spectrum Type")
        val = self.SpectrumTypeOption[val.upper()]
        return val  # type: ignore

    @spectrum_type.setter
    def spectrum_type(self, value: SpectrumTypeOption):
        self._oRevisionData.SetEmitNodeProperties(self._result_id, self._node_id, [f"Spectrum Type={value.value}"])

    class TxPowerOption(Enum):
        PEAK_POWER = "Peak Power"  # eslint-disable-line no-eval
        AVERAGE_POWER = "Average Power"  # eslint-disable-line no-eval

    @property
    def tx_power(self) -> TxPowerOption:
        """Tx Power
        Method used to specify the power

        """
        val = self._get_property("Tx Power")
        val = self.TxPowerOption[val.upper()]
        return val  # type: ignore

    @tx_power.setter
    def tx_power(self, value: TxPowerOption):
        self._oRevisionData.SetEmitNodeProperties(self._result_id, self._node_id, [f"Tx Power={value.value}"])

    @property
    def peak_power(self) -> float:
        """Peak Power
        Tx's carrier frequency peak power

        Value should be between -1000 and 1000.
        """
        val = self._get_property("Peak Power")
        val = self._convert_from_internal_units(float(val), "Power")
        return val  # type: ignore

    @peak_power.setter
    def peak_power(self, value: float | str):
        value = self._convert_to_internal_units(value, "Power")
        self._oRevisionData.SetEmitNodeProperties(self._result_id, self._node_id, [f"Peak Power={value}"])

    @property
    def average_power(self) -> float:
        """Average Power
        Tx's fundamental level specified by average power

        Value should be between -1000 and 1000.
        """
        val = self._get_property("Average Power")
        val = self._convert_from_internal_units(float(val), "Power")
        return val  # type: ignore

    @average_power.setter
    def average_power(self, value: float | str):
        value = self._convert_to_internal_units(value, "Power")
        self._oRevisionData.SetEmitNodeProperties(self._result_id, self._node_id, [f"Average Power={value}"])

    @property
    def include_phase_noise(self) -> bool:
        """Include Phase Noise
        Include oscillator phase noise in Tx spectral profile

        Value should be 'true' or 'false'.
        """
        val = self._get_property("Include Phase Noise")
        val = val == "true"
        return val  # type: ignore

    @include_phase_noise.setter
    def include_phase_noise(self, value: bool):
        self._oRevisionData.SetEmitNodeProperties(self._result_id, self._node_id, [f"Include Phase Noise={value}"])

    @property
    def tx_broadband_noise(self) -> float:
        """Tx Broadband Noise
        Transmitters broadband noise level

        Value should be less than 1000.
        """
        val = self._get_property("Tx Broadband Noise")
        return val  # type: ignore

    @tx_broadband_noise.setter
    def tx_broadband_noise(self, value: float):
        self._oRevisionData.SetEmitNodeProperties(self._result_id, self._node_id, [f"Tx Broadband Noise={value}"])

    class HarmonicTaperOption(Enum):
        CONSTANT = "Constant"  # eslint-disable-line no-eval
        MIL_STD_461G = "MIL-STD-461G"  # eslint-disable-line no-eval
        MIL_STD_461G_NAVY = "MIL-STD-461G Navy"  # eslint-disable-line no-eval
        DUFF_MODEL = "Duff Model"  # eslint-disable-line no-eval

    @property
    def harmonic_taper(self) -> HarmonicTaperOption:
        """Harmonic Taper
        Taper type used to set amplitude of harmonics

        """
        val = self._get_property("Harmonic Taper")
        val = self.HarmonicTaperOption[val.upper()]
        return val  # type: ignore

    @harmonic_taper.setter
    def harmonic_taper(self, value: HarmonicTaperOption):
        self._oRevisionData.SetEmitNodeProperties(self._result_id, self._node_id, [f"Harmonic Taper={value.value}"])

    @property
    def harmonic_amplitude(self) -> float:
        """Harmonic Amplitude
        Amplitude (relative to the carrier power) of harmonics

        Value should be between -1000 and 0.
        """
        val = self._get_property("Harmonic Amplitude")
        return val  # type: ignore

    @harmonic_amplitude.setter
    def harmonic_amplitude(self, value: float):
        self._oRevisionData.SetEmitNodeProperties(self._result_id, self._node_id, [f"Harmonic Amplitude={value}"])

    @property
    def harmonic_slope(self) -> float:
        """Harmonic Slope
        Rate of decrease for harmonics' amplitudes (dB/decade)

        Value should be between -1000 and 0.
        """
        val = self._get_property("Harmonic Slope")
        return val  # type: ignore

    @harmonic_slope.setter
    def harmonic_slope(self, value: float):
        self._oRevisionData.SetEmitNodeProperties(self._result_id, self._node_id, [f"Harmonic Slope={value}"])

    @property
    def harmonic_intercept(self) -> float:
        """Harmonic Intercept
        Amplitude intercept at the fundamental (dBc)

        Value should be between -1000 and 0.
        """
        val = self._get_property("Harmonic Intercept")
        return val  # type: ignore

    @harmonic_intercept.setter
    def harmonic_intercept(self, value: float):
        self._oRevisionData.SetEmitNodeProperties(self._result_id, self._node_id, [f"Harmonic Intercept={value}"])

    @property
    def enable_harmonic_bw_expansion(self) -> bool:
        """Enable Harmonic BW Expansion
        If (True), bandwidth of harmonics increases proportional to the harmonic
         number

        Value should be 'true' or 'false'.
        """
        val = self._get_property("Enable Harmonic BW Expansion")
        val = val == "true"
        return val  # type: ignore

    @enable_harmonic_bw_expansion.setter
    def enable_harmonic_bw_expansion(self, value: bool):
        self._oRevisionData.SetEmitNodeProperties(
            self._result_id, self._node_id, [f"Enable Harmonic BW Expansion={value}"]
        )

    @property
    def number_of_harmonics(self) -> int:
        """Number of Harmonics
        Maximum number of harmonics modeled

        Value should be between 1 and 1000.
        """
        val = self._get_property("Number of Harmonics")
        return val  # type: ignore

    @number_of_harmonics.setter
    def number_of_harmonics(self, value: int):
        self._oRevisionData.SetEmitNodeProperties(self._result_id, self._node_id, [f"Number of Harmonics={value}"])

    @property
    def second_harmonic_level(self) -> float:
        """Second Harmonic Level
        Amplitude (relative to the carrier power) of the 2nd harmonic

        Value should be between -1000 and 0.
        """
        val = self._get_property("Second Harmonic Level")
        return val  # type: ignore

    @second_harmonic_level.setter
    def second_harmonic_level(self, value: float):
        self._oRevisionData.SetEmitNodeProperties(self._result_id, self._node_id, [f"Second Harmonic Level={value}"])

    @property
    def third_harmonic_level(self) -> float:
        """Third Harmonic Level
        Amplitude (relative to the carrier power) of the 3rd harmonic

        Value should be between -1000 and 0.
        """
        val = self._get_property("Third Harmonic Level")
        return val  # type: ignore

    @third_harmonic_level.setter
    def third_harmonic_level(self, value: float):
        self._oRevisionData.SetEmitNodeProperties(self._result_id, self._node_id, [f"Third Harmonic Level={value}"])

    @property
    def other_harmonic_levels(self) -> float:
        """Other Harmonic Levels
        Amplitude (relative to the carrier power) of the higher order harmonics

        Value should be between -1000 and 0.
        """
        val = self._get_property("Other Harmonic Levels")
        return val  # type: ignore

    @other_harmonic_levels.setter
    def other_harmonic_levels(self, value: float):
        self._oRevisionData.SetEmitNodeProperties(self._result_id, self._node_id, [f"Other Harmonic Levels={value}"])

    @property
    def perform_tx_intermod_analysis(self) -> bool:
        """Perform Tx Intermod Analysis
        Performs a non-linear intermod analysis for the Tx

        Value should be 'true' or 'false'.
        """
        val = self._get_property("Perform Tx Intermod Analysis")
        val = val == "true"
        return val  # type: ignore

    @perform_tx_intermod_analysis.setter
    def perform_tx_intermod_analysis(self, value: bool):
        self._oRevisionData.SetEmitNodeProperties(
            self._result_id, self._node_id, [f"Perform Tx Intermod Analysis={value}"]
        )

    @property
    def internal_amp_gain(self) -> float:
        """Internal Amp Gain
        Internal Tx Amplifier's Gain

        Value should be between -1000 and 1000.
        """
        val = self._get_property("Internal Amp Gain")
        return val  # type: ignore

    @internal_amp_gain.setter
    def internal_amp_gain(self, value: float):
        self._oRevisionData.SetEmitNodeProperties(self._result_id, self._node_id, [f"Internal Amp Gain={value}"])

    @property
    def noise_figure(self) -> float:
        """Noise Figure
        Internal Tx Amplifier's noise figure

        Value should be between 0 and 50.
        """
        val = self._get_property("Noise Figure")
        return val  # type: ignore

    @noise_figure.setter
    def noise_figure(self, value: float):
        self._oRevisionData.SetEmitNodeProperties(self._result_id, self._node_id, [f"Noise Figure={value}"])

    @property
    def amplifier_saturation_level(self) -> float:
        """Amplifier Saturation Level
        Internal Tx Amplifier's Saturation Level

        Value should be between -200 and 200.
        """
        val = self._get_property("Amplifier Saturation Level")
        val = self._convert_from_internal_units(float(val), "Power")
        return val  # type: ignore

    @amplifier_saturation_level.setter
    def amplifier_saturation_level(self, value: float | str):
        value = self._convert_to_internal_units(value, "Power")
        self._oRevisionData.SetEmitNodeProperties(
            self._result_id, self._node_id, [f"Amplifier Saturation Level={value}"]
        )

    @property
    def p1_db_point_ref_input_(self) -> float:
        """P1-dB Point, Ref. Input
        Internal Tx Amplifier's 1 dB Compression Point - total power > P1dB
         saturates the internal Tx amplifier

        Value should be between -200 and 200.
        """
        val = self._get_property("P1-dB Point, Ref. Input ")
        val = self._convert_from_internal_units(float(val), "Power")
        return val  # type: ignore

    @p1_db_point_ref_input_.setter
    def p1_db_point_ref_input_(self, value: float | str):
        value = self._convert_to_internal_units(value, "Power")
        self._oRevisionData.SetEmitNodeProperties(self._result_id, self._node_id, [f"P1-dB Point, Ref. Input ={value}"])

    @property
    def ip3_ref_input(self) -> float:
        """IP3, Ref. Input
        Internal Tx Amplifier's 3rd order intercept point

        Value should be between -200 and 200.
        """
        val = self._get_property("IP3, Ref. Input")
        val = self._convert_from_internal_units(float(val), "Power")
        return val  # type: ignore

    @ip3_ref_input.setter
    def ip3_ref_input(self, value: float | str):
        value = self._convert_to_internal_units(value, "Power")
        self._oRevisionData.SetEmitNodeProperties(self._result_id, self._node_id, [f"IP3, Ref. Input={value}"])

    @property
    def reverse_isolation(self) -> float:
        """Reverse Isolation
        Internal Tx Amplifier's Reverse Isolation

        Value should be between -200 and 200.
        """
        val = self._get_property("Reverse Isolation")
        return val  # type: ignore

    @reverse_isolation.setter
    def reverse_isolation(self, value: float):
        self._oRevisionData.SetEmitNodeProperties(self._result_id, self._node_id, [f"Reverse Isolation={value}"])

    @property
    def max_intermod_order(self) -> int:
        """Max Intermod Order
        Internal Tx Amplifier's maximum intermod order to compute

        Value should be between 3 and 20.
        """
        val = self._get_property("Max Intermod Order")
        return val  # type: ignore

    @max_intermod_order.setter
    def max_intermod_order(self, value: int):
        self._oRevisionData.SetEmitNodeProperties(self._result_id, self._node_id, [f"Max Intermod Order={value}"])
