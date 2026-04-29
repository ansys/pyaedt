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

import math

from ansys.aedt.core.emit_core.emit_constants import ResultType
from ansys.aedt.core.emit_core.nodes.generated.band import Band
from ansys.aedt.core.emit_core.nodes.generated.rx_susceptibility_prof_node import RxSusceptibilityProfNode
from ansys.aedt.core.emit_core.results.interaction_domain import InteractionDomain


class InteractionInstance:
    def __init__(self, emit_obj, domain: InteractionDomain):
        self.emit_project = emit_obj
        self.odesktop = self.emit_project.odesktop

        self.interaction_domain = None
        self.detailed_results = None
        self.is_valid = False

        self.domain = domain

        # Encoded values are in dB * 100
        # Values <-30000 or >30000 are non-numeric results
        self._encoded_emi = -32768
        self._encoded_desense = -32768
        self._power_at_rx = -200.0  # Power at RX in dBm

        self._largest_emi_interferer_type = -11

    @property
    def encoded_emi(self) -> float:
        """Get the encoded EMI value in dB * 100."""
        return self._encoded_emi

    @encoded_emi.setter
    def encoded_emi(self, value: float) -> None:
        """Set the encoded EMI value in dB * 100."""
        self._encoded_emi = value

    @property
    def encoded_desense(self) -> float:
        """Get the encoded desense value in dB * 100."""
        return self._encoded_desense

    @encoded_desense.setter
    def encoded_desense(self, value: float) -> None:
        """Set the encoded desense value in dB * 100."""
        self._encoded_desense = value

    @property
    def power_at_rx(self) -> float:
        """Get the power at RX value in dBm."""
        return self._power_at_rx

    @power_at_rx.setter
    def power_at_rx(self, value: float) -> None:
        """Set the power at RX value in dBm."""
        self._power_at_rx = value

    @property
    def largest_emi_interferer_type(self) -> float:
        """Get the largest EMI interferer type."""
        return self._largest_emi_interferer_type

    @largest_emi_interferer_type.setter
    def largest_emi_interferer_type(self, value: float) -> None:
        """Set the largest EMI interferer type."""
        self._largest_emi_interferer_type = value

    @property
    def current_revision(self):
        """Current active Revision. Always reflects the active revision from the project."""
        return self.emit_project.results.current_revision

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
            elif self._encoded_emi == -32760:
                return "Radio pair disabled."
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
            elif self._encoded_emi == 30201:
                return "Result not available."
            elif self._encoded_emi > 30000 or self._encoded_emi < -30000:
                return f"Invalid encoded value: {self._encoded_emi}"
        return ""

    def has_valid_values(self) -> bool:
        """
        Check if this interaction instance has valid values.

        Returns
        -------
        bool
            True if the interaction instance has valid values, False otherwise.
        """
        if self.encoded_emi > 30000 or self.encoded_emi < -30000:
            return False
        else:
            return True

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
                if self.encoded_emi == 30201:
                    raise RuntimeError("EMI value not available.")
                encoded_result = self.encoded_emi
            else:
                if self.encoded_desense == 30201:
                    raise RuntimeError("Desense and sensitivity values not available.")
                encoded_result = self.encoded_desense

            # Check for out-of-range encoded results
            if encoded_result > 30000 or encoded_result < -30000:
                warning = self.get_result_warning()
                error_msg = f"Unable to evaluate value: {warning if warning else encoded_result}."
                raise RuntimeError(error_msg)

            if result_type == ResultType.EMI or result_type == ResultType.DESENSE:
                val = encoded_result / 100.0
            elif result_type == ResultType.SENSITIVITY:
                sim = self.current_revision.get_simulation()
                status = sim.is_domain_valid(self.domain)
                if status != "":
                    raise RuntimeError(status)
                val = encoded_result / 100.0  # desense
                rx_band: Band = self.current_revision.get_band_node(self.domain.receiver_band_name)
                if rx_band is None:
                    raise RuntimeError(f"Could not find the band {self.domain.receiver_band_name} for the receiver.")
                rx_sus_prof: RxSusceptibilityProfNode = next(
                    (child for child in rx_band.children if child.node_type == "RxSusceptibilityProfNode"), None
                )
                if rx_sus_prof is None:
                    raise RuntimeError(
                        f"Could not find RxSusceptibilityProfNode for band {self.domain.receiver_band_name}."
                    )
                val = rx_sus_prof.receiver_sensitivity + max(val, 0)

        # Round to the nearest 2 decimal places
        if val < 0:
            val = math.ceil(val * 100 - 0.5) / 100
        else:
            val = math.floor(val * 100 + 0.5) / 100

        return val

    def get_largest_problem_type(self, result_type: ResultType) -> str:
        """
        Get the largest problem type for this interaction.

        Parameters
        ----------
        result_type : ResultType
            The result type to get the largest problem type for.

        Returns
        -------
        str
            The largest problem type for this interaction.

        Raises
        ------
        ValueError
            If the result_type is not EMI.
        """
        if result_type != ResultType.EMI:
            raise ValueError("The largest problem type is only available for ResultType.EMI.")

        return self.get_largest_emi_problem_type()

    def get_largest_emi_problem_type(self) -> str:
        """
        Return the largest EMI problem type for this interaction.

        Returns
        -------
        text: str
            The largest EMI problem type for this interaction.

        Raises
        ------
        RuntimeError
            If the interaction is invalid or values are not available.
        """
        if not self.has_valid_values():
            raise RuntimeError("An EMI value is not available so the largest EMI problem type is undefined.")

        if self.largest_emi_interferer_type == 0:
            text = "Out-of-Channel: Tx Fundamental"
        elif self.largest_emi_interferer_type == 1:
            text = "Out-of-Channel: Tx Harmonic/Spurious"
        elif self.largest_emi_interferer_type == 3:
            text = "Out-of-Channel: Intermod"
        elif self.largest_emi_interferer_type == 7:
            text = "In-Channel: Tx Fundamental"
        elif self.largest_emi_interferer_type == 8:
            text = "In-Channel: Tx Harmonic/Spurious"
        elif self.largest_emi_interferer_type == 10:
            text = "In-Channel: Tx Intermod"
        elif self.largest_emi_interferer_type == 14:
            text = "In-Channel: Broadband"
        else:
            text = f"Error: category {self.largest_emi_interferer_type} not found"
        return text

    def get_domain(self) -> InteractionDomain:
        """Get the interaction domain for this instance.
        
        Returns
        -------
        InteractionDomain
            The interaction domain.
        """
        return self.domain

    def _fetch_power_at_rx(self):
        """Lazily fetch power at Rx via the GetPowerAtRx COM/gRPC call.

        Mirrors the old C++ InteractionInstancePrivate behavior where
        DetailedResult::run() was called on demand inside getValue(PowerAtRx).
        """
        try:
            power_at_rx = self.emit_project._emit_com_module.GetPowerAtRx(
                self.emit_project.results.current_revision.results_index,
                self.domain.receiver_name,
                self.domain.receiver_band_name,
                self.domain.receiver_channel_frequency,
                self.domain.interferer_names,
                self.domain.interferer_band_names,
                self.domain.interferer_channel_frequencies,
            )
            self._power_at_rx = float(power_at_rx)
        except Exception:
            pass  # stays at -200.0

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
