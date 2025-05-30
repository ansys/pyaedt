# -*- coding: utf-8 -*-
#
# Copyright(C) 2021 - 2025 ANSYS, Inc. and /or its affiliates.
# SPDX - License - Identifier: MIT
#
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files(the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and /or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions :
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
from ansys.aedt.core.emit_core.nodes.emit_node import EmitNode

class ReadOnlyTxSpectralProfEmitterNode(EmitNode):
    def __init__(self, emit_obj, result_id, node_id):
        self._is_component = False
        EmitNode.__init__(self, emit_obj, result_id, node_id)

    @property
    def parent(self):
        """The parent of this emit node."""
        return self._parent

    @property
    def output_voltage_peak(self) -> float:
        """Output High Voltage Level: maximum voltage of the digital signal."""
        val = self._get_property("Output Voltage Peak")
        val = self._convert_from_internal_units(float(val), "Voltage")
        return float(val)

    @property
    def include_phase_noise(self) -> bool:
        """Include oscillator phase noise in Tx spectral profile.

        Value should be 'true' or 'false'.
        """
        val = self._get_property("Include Phase Noise")
        return (val == true)

    @property
    def tx_broadband_noise(self) -> float:
        """Transmitters broadband noise level.

        Value should be less than 1000.
        """
        val = self._get_property("Tx Broadband Noise")
        return float(val)

    @property
    def perform_tx_intermod_analysis(self) -> bool:
        """Performs a non-linear intermod analysis for the Tx.

        Value should be 'true' or 'false'.
        """
        val = self._get_property("Perform Tx Intermod Analysis")
        return (val == true)

    @property
    def internal_amp_gain(self) -> float:
        """Internal Tx Amplifier's Gain.

        Value should be between -1000 and 1000.
        """
        val = self._get_property("Internal Amp Gain")
        return float(val)

    @property
    def noise_figure(self) -> float:
        """Internal Tx Amplifier's noise figure.

        Value should be between 0 and 50.
        """
        val = self._get_property("Noise Figure")
        return float(val)

    @property
    def amplifier_saturation_level(self) -> float:
        """Internal Tx Amplifier's Saturation Level.

        Value should be between -200 and 200.
        """
        val = self._get_property("Amplifier Saturation Level")
        val = self._convert_from_internal_units(float(val), "Power")
        return float(val)

    @property
    def p1_db_point_ref_input(self) -> float:
        """P1-dB Point, Ref. Input .

        Internal Tx Amplifier's 1 dB Compression Point - total power > P1dB
        saturates the internal Tx amplifier.

        Value should be between -200 and 200.
        """
        val = self._get_property("P1-dB Point, Ref. Input ")
        val = self._convert_from_internal_units(float(val), "Power")
        return float(val)

    @property
    def ip3_ref_input(self) -> float:
        """Internal Tx Amplifier's 3rd order intercept point.

        Value should be between -200 and 200.
        """
        val = self._get_property("IP3, Ref. Input")
        val = self._convert_from_internal_units(float(val), "Power")
        return float(val)

    @property
    def reverse_isolation(self) -> float:
        """Internal Tx Amplifier's Reverse Isolation.

        Value should be between -200 and 200.
        """
        val = self._get_property("Reverse Isolation")
        return float(val)

    @property
    def max_intermod_order(self) -> int:
        """Internal Tx Amplifier's maximum intermod order to compute.

        Value should be between 3 and 20.
        """
        val = self._get_property("Max Intermod Order")
        return int(val)

