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

from __future__ import annotations

import math
from typing import TYPE_CHECKING

from ansys.aedt.core.emit_core.emit_constants import EMIInterfererType
from ansys.aedt.core.emit_core.emit_constants import ResultType
from ansys.aedt.core.emit_core.nodes.generated.band import Band
from ansys.aedt.core.emit_core.nodes.generated.rx_susceptibility_prof_node import RxSusceptibilityProfNode
from ansys.aedt.core.emit_core.results.interaction_domain import InteractionDomain

if TYPE_CHECKING:
    from ansys.aedt.core.emit_core.results.revision import Revision


class InteractionInstance:
    def __init__(self, emit_obj, domain: InteractionDomain, revision: Revision):
        self.emit_project = emit_obj
        self.odesktop = self.emit_project.odesktop

        self.domain = domain
        self.revision = revision

        # Encoded values are in dB * 100
        # Values <-30000 or >30000 are non-numeric results
        self._encoded_emi = -32768
        self._encoded_desense = -32768
        self._power_at_rx = -200.0  # Power at RX in dBm
        self._largest_emi_interferer_type = -11

    @property
    def power_at_rx(self) -> float:
        """Get the power at RX value in dBm."""
        return self._power_at_rx

    def get_result_warning(self) -> str:
        """Get the result warning for this interaction.

        Returns
        -------
        str
            The warning message if values are invalid, empty string otherwise.
        """
        if not self.has_valid_values():
            # Map encoded values to warning messages (matches SimulationNode::resultMessage)
            if self._encoded_emi == -32768:
                return "Nothing to run."
            elif self._encoded_emi == -32755:
                return "Self-interaction availability only at band level."
            elif self._encoded_emi == -32751:
                return "Channel level results only available for Channel/Band pairs."
            elif self._encoded_emi == -32750:
                return "Not yet run."
            elif self._encoded_emi == -32748:
                return "Unallowable Tx/Rx channel combination."
            elif self._encoded_emi == -32742:
                return "No power received."
            elif self._encoded_emi == -32740:
                return "No path from Tx to Rx."
            elif self._encoded_emi == 30001:
                return "Greater than 300 dB."
            elif self._encoded_emi == -30001:
                return "Less than -300 dB."
            elif self._encoded_emi == 30020:
                return "An amplifier was saturated."
            elif self._encoded_emi == 30100:
                return "Error in configuration."
            elif self._encoded_emi == 30200:
                return "N to 1 results not available in Scenario Details."
            elif self._encoded_emi == -30270:
                return "Radio pair disabled."
            elif self._encoded_emi > 30000 or self._encoded_emi < -30000:
                return f"Invalid encoded value: {self._encoded_emi}"
        return ""

    def has_valid_values(self) -> bool:
        """
        Check if this interaction instance has valid values.

        Returns ``True`` if at least one of the EMI or desense values
        is a valid numeric result.

        Returns
        -------
        bool
            True if at least one result value is valid, False otherwise.
        """
        emi_valid = -30000 <= self._encoded_emi <= 30000
        desense_valid = -30000 <= self._encoded_desense <= 30000
        return emi_valid or desense_valid

    def get_value(self, result_type: ResultType) -> float:
        """
        Get the value of this interaction.

        Parameters
        ----------
        result_type : ResultType
            The type of result to get (EMI, DESENSE, SENSITIVITY, or POWER_AT_RX).

        Returns
        -------
        float
            The value of the interaction, rounded to 2 decimal places.

        Raises
        ------
        RuntimeError
            If the interaction is invalid or values are not available.
        """
        if result_type == ResultType.POWER_AT_RX:
            if self._power_at_rx == -200.0:
                self._fetch_power_at_rx()
            val = self._power_at_rx
        else:
            # Get encoded result based on type
            if result_type == ResultType.EMI:
                if self._encoded_emi == 30201:
                    raise RuntimeError("EMI value not available.")
                encoded_result = self._encoded_emi
            else:
                if self._encoded_desense == 30201:
                    raise RuntimeError("Desense and sensitivity values not available.")
                encoded_result = self._encoded_desense

            # Check for out-of-range encoded results
            if encoded_result > 30000 or encoded_result < -30000:
                warning = self.get_result_warning()
                error_msg = f"Unable to evaluate value: {warning if warning else encoded_result}."
                raise RuntimeError(error_msg)

            if result_type == ResultType.EMI or result_type == ResultType.DESENSE:
                val = encoded_result / 100.0
            elif result_type == ResultType.SENSITIVITY:
                sim = self.revision.get_simulation()
                status = sim.is_domain_valid(self.domain)
                if status != "":
                    raise RuntimeError(status)
                val = encoded_result / 100.0  # desense
                rx_band: Band = self.revision.get_band_node(self.domain.receiver_band_name)
                if rx_band is None:
                    raise RuntimeError(f"Could not find the band {self.domain.receiver_band_name} for the receiver.")
                rx_sus_prof: RxSusceptibilityProfNode = next(
                    (child for child in rx_band.children if child.node_type == "RxSusceptibilityProfNode"), None
                )
                if rx_sus_prof is None:
                    raise RuntimeError(
                        f"Could not find RxSusceptibilityProfNode for band {self.domain.receiver_band_name}."
                    )
                val = rx_sus_prof.min_receive_signal_pwr + max(val, 0)

        # Round to the nearest 2 decimal places
        if val < 0:
            val = math.ceil(val * 100 - 0.5) / 100
        else:
            val = math.floor(val * 100 + 0.5) / 100

        return val

    def get_largest_emi_problem_type(self) -> EMIInterfererType:
        """
        Return the largest EMI problem type for this interaction.

        Returns
        -------
        EMIInterfererType
            The largest EMI problem type for this interaction.
            Example: IN_CHANNEL_TX_FUNDAMENTAL, OUT_OF_CHANNEL_TX_HARMONIC_SPURIOUS, etc.

        Raises
        ------
        RuntimeError
            If the interaction is invalid or values are not available.
        """
        if not (-30000 <= self._encoded_emi <= 30000):
            raise RuntimeError("An EMI value is not available so the largest EMI problem type is undefined.")

        _INTERFERER_TYPE_MAP = {
            0: EMIInterfererType.OUT_OF_CHANNEL_TX_FUNDAMENTAL,
            1: EMIInterfererType.OUT_OF_CHANNEL_TX_HARMONIC_SPURIOUS,
            3: EMIInterfererType.OUT_OF_CHANNEL_TX_INTERMOD,
            7: EMIInterfererType.IN_CHANNEL_TX_FUNDAMENTAL,
            8: EMIInterfererType.IN_CHANNEL_TX_HARMONIC_SPURIOUS,
            10: EMIInterfererType.IN_CHANNEL_TX_INTERMOD,
            14: EMIInterfererType.IN_CHANNEL_BROADBAND,
        }
        result = _INTERFERER_TYPE_MAP.get(self._largest_emi_interferer_type)
        if result is None:
            raise RuntimeError(f"Error: category {self._largest_emi_interferer_type} not found")
        return result

    def get_domain(self) -> InteractionDomain:
        """Get the interaction domain for this instance.

        Returns
        -------
        InteractionDomain
            The interaction domain.
        """
        return self.domain

    def _fetch_power_at_rx(self):
        """GetPowerAtRx COM/gRPC call.

        Mirrors the old C++ InteractionInstancePrivate behavior where
        DetailedResult::run() was called on demand inside getValue(PowerAtRx).
        """
        if len(self.domain.interferer_names) > 1:
            raise RuntimeError("Power at Rx for multiple simultaneous interferers is not available.")
        if not self.domain.is_single_instance():
            raise RuntimeError("Power at Rx requires a fully-specified single-instance domain.")
        try:
            power_at_rx = self.emit_project._emit_com_module.GetPowerAtRx(
                self.revision.results_index,
                self.domain.receiver_name,
                self.domain.receiver_band_name,
                self.domain.receiver_channel_frequency,
                self.domain.interferer_names,
                self.domain.interferer_band_names,
                self.domain.interferer_channel_frequencies,
            )
            self._power_at_rx = float(power_at_rx)
        except Exception as e:
            raise RuntimeError(f"Unable to fetch Power at Rx: {e}") from e

    def check_validity(self) -> None:
        """Check if this interaction instance is still valid.

        Raises
        ------
        RuntimeError
            If the instance is no longer valid.
        """
        # Check if the encoded values are within valid range
        if not self.has_valid_values():
            warning = self.get_result_warning()
            raise RuntimeError(f"InteractionInstance has invalid values: {warning}")
