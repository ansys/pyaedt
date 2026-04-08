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
from ansys.aedt.core.emit_core.results.simulation import Simulation


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

    def get_results_warning(self) -> str:
        """Get the results warning for this interaction."""
        status = self.emit_project._emit_com_module.CheckInteractionInstanceValidity()
        if status != "":
            raise RuntimeError(status)
        if not self.has_valid_values():
            return self.emit_project._emit_com_module.GetResultsWarning(self._encoded_emi)

    def has_valid_values(self) -> bool:
        """
        Check if this interaction instance has valid values.

        Returns
        -------
        bool
            True if the interaction instance has valid values, False otherwise.

        Raises
        ------
        RuntimeError
            If the interaction instance is invalid.
        """
        status = self.emit_project._emit_com_module.CheckInstanceValidity()
        if status != "":
            raise RuntimeError(status)

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
        ValueError
            If the result type is invalid or values cannot be computed.
        """
        # Check validity first
        status = self.emit_project._emit_com_module.CheckInteractionInstanceValidity()
        if status != "":
            raise RuntimeError(status)

        # Get encoded result based on type
        if result_type == ResultType.EMI:
            if self.encoded_emi == 30201:
                raise RuntimeError("EMI value not available.")
            encoded_result = self.encoded_emi
        else:
            if self.encoded_desense == 30201:
                raise RuntimeError("Desense and sensitivity values not available.")
            encoded_result = self.encoded_desense

        # Check for out-of-range encoded results (except for PowerAtRx)
        if encoded_result > 30000 or encoded_result < -30000:
            # Try to get a more specific error message from the simulation
            self.emit_project._emit_com_module.GetResultsWarning(encoded_result)
            error_msg = f"Unable to evaluate value: {encoded_result}."
            raise RuntimeError(error_msg)

        if result_type == ResultType.EMI or result_type == ResultType.DESENSE:
            val = encoded_result / 100.0
        elif result_type == ResultType.SENSITIVITY:
            status = status = Simulation.is_domain_valid(self.domain)
            if status != "":
                raise RuntimeError(status)
            val = encoded_result / 100.0  # desense
            rx_band: Band = self.current_revision.get_band_node(self.domain.receiver_band_name)
            if rx_band is None:
                raise RuntimeError(f"Could not find the band {self.domain.receiver_band_name} for the receiver.")
            rx_sus_prof: RxSusceptibilityProfNode = next(
                (child for child in rx_band.children if child.node_type == "RxSusceptibilityProfNode"), None
            )
            # I THINK THIS IS THE RIGHT PROPERTY BUT DOUBLE CHECK
            val = rx_sus_prof.receiver_sensitivity + max(val, 0)
        elif result_type == ResultType.POWER_AT_RX:
            status = Simulation.is_domain_valid(self.domain)
            if status != "":
                raise RuntimeError(status)
            # Detailed results max unfiltered power at RX
            self.detailed_results = self.emit_project._emit_com_module.GetDetailedResults()
            val = self.detailed_results.max_unfiltered_power_at_rx

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
        """
        if not self.has_valid_values():
            raise ValueError("An EMI value is not available so the largest EMI problem type is undefined.")

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
            text = f"Error: category {self.largest_emi_interferer_type} not found!"
        return text
