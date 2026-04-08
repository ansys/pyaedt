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

import warnings

from ansys.aedt.core.emit_core.emit_constants import ResultType
from ansys.aedt.core.emit_core.nodes.generated.band import Band
from ansys.aedt.core.emit_core.nodes.generated.radio_node import RadioNode
from ansys.aedt.core.emit_core.results.interaction_domain import InteractionDomain
from ansys.aedt.core.emit_core.results.interaction_instance import InteractionInstance
from ansys.aedt.core.emit_core.results.simulation import Simulation


class Interaction:
    def __init__(self, emit_obj, domain):
        self.emit_project = emit_obj
        self.odesktop = self.emit_project.odesktop
        self.domain = domain

    @property
    def current_revision(self):
        """Current active Revision. Always reflects the active revision from the project."""
        return self.emit_project.results.current_revision

    def get_worst_instance(self, intstance: InteractionInstance, result_type: ResultType) -> InteractionInstance:
        """Get the worst instance for this interaction.

        Parameters
        ----------
        intstance : InteractionInstance
            The interaction instance to get the worst case instance for.
        result_type : ResultType
            The result type to get the worst case instance for.

        Returns
        -------
        InteractionInstance
            The worst case instance for this interaction.

        Raises
        ------
        RuntimeError
            If the worst case instance cannot be retrieved.
        """
        status = self.emit_project._emit_com_module.CheckInstanceValidity()
        if status != "":
            raise RuntimeError(status)

        # Can't compute worst instance for Power at RX
        if result_type == ResultType.POWER_AT_RX:
            err_msg = "Worst case instances are not available for Power At Rx."
            warnings.warn(err_msg)
            return None

        complete = self.emit_project._emit_com_module.IsComplete()
        if not complete:
            warnings.warn("The result is not available. The interaction is not fully analyzed.")
            return None

        if Simulation.is_domain_valid(self.domain) != "":
            warnings.warn("The interaction domain is not valid. Cannot retrieve worst case instance.")
            return None

        count = self.emit_project._emit_com_module.GetInstanceCount(result_type.value)
        if count == 0:
            warnings.warn("The instance domain is empty.")
            return None

        rx_node: Band = self.current_revision.get_band_node(self.domain.receiver_band_name)
        if rx_node is None:
            rx_node: RadioNode = self.current_revision.get_radio_node(self.domain.receiver_band_name)

    def has_valid_availability(self) -> bool:
        """Check if this interaction has valid availability."""
        return self._emit_com.HasValidAvailability()

    def get_availability(self) -> float:
        """Get the availability of this interaction."""
        return self._emit_com.GetAvailability()

    def get_availability_warning(self, domain: InteractionDomain) -> str:
        """
        Get the availability warning for this interaction.

        Parameters
        ----------
        domain : InteractionDomain
            The interaction domain to check availability for.

        Returns
        -------
        str
            The availability warning message, or empty string if no warning.

        Raises
        ------
        RuntimeError
            If the document is invalid or domain validation fails.
        """
        # Check if emit document is valid
        if self.emit_project is None:
            raise RuntimeError("Invalid document.")

        # Check domain validity
        status = Simulation.is_domain_valid(domain)
        if status != "":
            raise RuntimeError(status)

        # Get nodes from interaction domain
        try:
            rx_radio_node = self.current_revision.get_radio_node(domain.receiver_name)
            rx_band_node = (
                self.current_revision.get_band_node(domain.receiver_band_name) if domain.receiver_band_name else None
            )

            tx_radio_nodes = []
            tx_band_nodes = []

            for interferer_name in domain.interferer_names:
                tx_radio = self.current_revision.get_radio_node(interferer_name)
                if tx_radio:
                    tx_radio_nodes.append(tx_radio)

            for interferer_band_name in domain.interferer_band_names:
                tx_band = self.current_revision.get_band_node(interferer_band_name)
                if tx_band:
                    tx_band_nodes.append(tx_band)

        except Exception as e:
            raise RuntimeError(f"Error retrieving nodes from domain: {str(e)}")

        # Check for multiple TX bands (not supported for availability)
        if len(tx_band_nodes) > 1:
            return "Availability only defined for 1 to 1 runs."

        # Check if no TX bands defined
        if len(tx_band_nodes) == 0:
            return "Availability only defined for bands and channels."

        tx_band_node = tx_band_nodes[0]

        # Check if RX or TX band nodes are None
        if rx_band_node is None or tx_band_node is None:
            return "Availability only defined for bands and channels."

        # Get channel indices (simplified - would need actual implementation)
        rx_channel_index = -1
        tx_channel_index = -1

        rx_band_freqs = rx_band_node.get_active_frequencies(is_rx=True).index(domain.receiver_channel_frequency)
        tx_band_freqs = (
            tx_band_node.get_active_frequencies(is_rx=False).index(domain.interferer_channel_frequencies[0])
            if domain.interferer_channel_frequencies
            else -1
        )

        if rx_band_freqs.index(domain.receiver_channel_frequency) != -1:
            rx_channel_index = rx_band_freqs.index(domain.receiver_channel_frequency)
        if tx_band_freqs.index(domain.interferer_channel_frequencies[0]) != -1:
            tx_channel_index = tx_band_freqs.index(domain.interferer_channel_frequencies[0])

        # Check for single channel pairs
        if rx_channel_index != -1 and tx_channel_index != -1:
            return "Availability undefined for single channel pairs."

        # Check for self-interaction at channel level
        if rx_band_node == tx_band_node and (rx_channel_index != -1 or tx_channel_index != -1):
            return "Self-interaction availability only at band level."

        # Check for single channel case
        if tx_channel_index != -1 and hasattr(rx_band_node, "num_channels") and rx_band_node.num_channels == 1:
            return "Only one channel pair exists, availability undefined."

        # Check if radio pair is enabled in simulation
        if not rx_radio_node.enabled or not tx_radio_nodes[0].enabled:
            return "Radio pair disabled."

        # check for validradioanalysis
        if self.check_valid_radio_analysis(rx_radio_node, tx_radio_nodes[0]) != "":
            return "Error in radio analysis."

        # No warnings
        return ""

    def get_instance(self, domain: InteractionDomain) -> InteractionInstance:
        """Get the instance at the specified index for this interaction."""
        status = self.emit_project._emit_com_module.CheckInstanceValidity()
        if status != "":
            raise RuntimeError(status)

        status = Simulation.is_domain_valid(domain)
        if status != "":
            raise RuntimeError(status)

        if not domain.is_single_instance():
            raise RuntimeError("The instance domain must be fully defined.")

        complete = self.emit_project._emit_com_module.IsComplete()
        if not complete:
            raise RuntimeError("The result is not available. The interaction is not fully analyzed.")

    def check_valid_radio_analysis(self, rx_radio_node: RadioNode, tx_radio_node: RadioNode) -> str:
        """Check if the radio pair is valid for analysis."""
        # This is a placeholder implementation
        if rx_radio_node.properties.get("Type") == "Wi-Fi" and tx_radio_node.properties.get("Type") == "Wi-Fi":
            return ""
