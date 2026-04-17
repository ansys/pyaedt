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
from typing import TYPE_CHECKING

from ansys.aedt.core.emit_core.emit_constants import ResultType
from ansys.aedt.core.emit_core.nodes.generated.band import Band
from ansys.aedt.core.emit_core.nodes.generated.radio_node import RadioNode
from ansys.aedt.core.emit_core.results.interaction_domain import InteractionDomain
from ansys.aedt.core.emit_core.results.interaction_instance import InteractionInstance

if TYPE_CHECKING:
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

    def get_worst_instance(self, result_type: ResultType) -> InteractionInstance:
        """Get the worst instance for this interaction.

        Parameters
        ----------
        result_type : ResultType
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

        sim = self.current_revision.get_simulation()
        status = sim.is_domain_valid(self.domain)
        if status != "":
            warnings.warn(status)
            warnings.warn("The interaction domain is not valid. Cannot retrieve worst case instance.")
            return None

        count = self.emit_project._emit_com_module.GetInstanceCount(result_type.value)
        if count == 0:
            warnings.warn("The instance domain is empty.")
            return None

        rx_radio_node = self.current_revision.get_radio_node(self.domain.receiver_name)
        rx_band_node = self.current_revision.get_band_node(self.domain.receiver_band_name) if self.domain.receiver_band_name else None
        tx_radio_nodes = [self.current_revision.get_radio_node(name) for name in self.domain.interferer_names]
        tx_band_nodes = [self.current_revision.get_band_node(name) for name in self.domain.interferer_band_names]

        rx_node = rx_band_node if rx_band_node else rx_radio_node
        
        rx_channel_index = next((rx_node.get_active_frequencies(is_rx=True).index(freq) for freq in [self.domain.receiver_channel_frequency] if freq >= 0), -1)
        tx_channel_indexes = next((tx_band.get_active_frequencies(is_rx=False).index(freq) for tx_band in tx_band_nodes for freq in self.domain.interferer_channel_frequencies if freq >= 0 and freq in tx_band.get_active_frequencies(is_rx=False)), -1)

        is_desense = (result_type == ResultType.DESENSE or result_type == ResultType.SENSITIVITY)
        
        if (len(tx_radio_nodes) == 1):
            tx_node = None
            if len(tx_band_nodes) > 0 and tx_band_nodes[0]:
                tx_node = tx_band_nodes[0]
            else:
                tx_node = tx_radio_nodes[0]
            tx_channel_index = -1
            if(len(tx_channel_indexes) > 0):
                tx_channel_index = tx_channel_indexes[0]
        # TODO: Complete worst instance implementation - needs new COM API
        # Need to add GetWorstInstance COM method that returns:
        # - encoded_emi, encoded_desense, largest_emi_interferer_type
        # Then create InteractionInstance with that data:
        #   worst_instance = InteractionInstance(self.emit_project, worst_domain)
        #   worst_instance.encoded_emi = <from COM>
        #   worst_instance.encoded_desense = <from COM>
        #   worst_instance.largest_emi_interferer_type = <from COM>
        #   return worst_instance
        raise NotImplementedError("get_worst_instance requires new COM API: GetWorstInstance")

    def has_valid_availability(self, domain: InteractionDomain) -> bool:
        """Check if this interaction has valid availability.
        
        Parameters
        ----------
        domain : InteractionDomain
            The interaction domain to check availability for.
            
        Returns
        -------
        bool
            True if the interaction has valid availability, False otherwise.
        """
        # Check if there's any warning - if no warning, availability is valid
        try:
            warning = self.get_availability_warning(domain)
            return warning == ""
        except RuntimeError:
            # If there's an error checking the warning, availability is not valid
            return False

    def get_availability(self, domain: InteractionDomain) -> float:
        """Get the availability of this interaction.
        
        Parameters
        ----------
        domain : InteractionDomain
            The interaction domain to get availability for.
            
        Returns
        -------
        float
            The availability value for this interaction.
            
        Raises
        ------
        RuntimeError
            If the domain is invalid or availability cannot be calculated.
        NotImplementedError
            Until the COM API is implemented.
        """
        # First check if availability is valid for this domain
        if not self.has_valid_availability(domain):
            warning = self.get_availability_warning(domain)
            raise RuntimeError(f"Availability is not valid for this domain: {warning}")
        
        # TODO: Needs new COM API method: GetAvailability(resultIndex, domain_params)
        # Should call:
        # return self.emit_project._emit_com_module.GetAvailability(
        #     self.emit_project.results.current_revision.results_index,
        #     domain.receiver_name,
        #     domain.receiver_band_name,
        #     domain.receiver_channel_frequency,
        #     domain.interferer_names,
        #     domain.interferer_band_names,
        #     domain.interferer_channel_frequencies
        # )
        raise NotImplementedError("get_availability requires new COM API: GetAvailability")

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
        sim = self.current_revision.get_simulation()
        status = sim.is_domain_valid(domain)
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

        # Get channel indices - check if specific channels are defined
        rx_channel_index = -1
        tx_channel_index = -1

        # Get the active frequencies for the bands
        rx_band_freqs = rx_band_node.get_active_frequencies(is_rx=True)
        tx_band_freqs = tx_band_node.get_active_frequencies(is_rx=False)

        # Check if specific channel frequencies are defined in the domain
        if domain.receiver_channel_frequency >= 0 and domain.receiver_channel_frequency in rx_band_freqs:
            rx_channel_index = rx_band_freqs.index(domain.receiver_channel_frequency)
        
        if (domain.interferer_channel_frequencies and 
            len(domain.interferer_channel_frequencies) > 0 and
            domain.interferer_channel_frequencies[0] >= 0 and
            domain.interferer_channel_frequencies[0] in tx_band_freqs):
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
            return "Error in configuration."

        # No warnings
        return ""

    def get_instance(self, domain: InteractionDomain) -> InteractionInstance:
        """Get the instance at the specified index for this interaction."""
        status = self.emit_project._emit_com_module.CheckInstanceValidity()
        if status != "":
            raise RuntimeError(status)

        sim = self.current_revision.get_simulation()
        status = sim.is_domain_valid(domain)
        if status != "":
            raise RuntimeError(status)

        if not domain.is_single_instance():
            raise RuntimeError("The instance domain must be fully defined.")

        complete = self.emit_project._emit_com_module.IsComplete()
        if not complete:
            raise RuntimeError("The result is not available. The interaction is not fully analyzed.")

        # TODO: Complete get_instance implementation - needs new COM API
        # Need to add GetInstance COM method that returns:
        # - encoded_emi, encoded_desense, largest_emi_interferer_type for the specific domain
        # Then create InteractionInstance with that data:
        #   instance = InteractionInstance(self.emit_project, domain)
        #   instance.encoded_emi = <from COM>
        #   instance.encoded_desense = <from COM>
        #   instance.largest_emi_interferer_type = <from COM>
        #   return instance
        raise NotImplementedError("get_instance requires new COM API: GetInstance")

    def is_complete(self) -> bool:
        """Check if this interaction analysis is complete.
        
        Returns
        -------
        bool
            True if the interaction has been fully analyzed, False otherwise.
        """
        return self.emit_project._emit_com_module.IsComplete()

    def get_domain(self) -> InteractionDomain:
        """Get the interaction domain for this interaction.
        
        Returns
        -------
        InteractionDomain
            The interaction domain.
        """
        return self.domain

    def check_validity(self) -> None:
        """Check if this interaction is still valid.
        
        Raises
        ------
        RuntimeError
            If the interaction is no longer valid.
        """
        is_complete = self.is_complete()
        
        # Call the COM API to check interaction validity using domain
        self.emit_project.results.current_revision._load_revision()
        error_message = self.emit_project._emit_com_module.CheckInteractionValidity(
            self.emit_project.results.current_revision.results_index,
            is_complete,
            self.domain.receiver_name,
            self.domain.receiver_band_name,
            self.domain.receiver_channel_frequency,
            self.domain.interferer_names,
            self.domain.interferer_band_names,
            self.domain.interferer_channel_frequencies,
        )
        
        if error_message:
            raise RuntimeError(f"Interaction is not valid: {error_message}")

    def check_valid_radio_analysis(self, rx_radio_node: RadioNode, tx_radio_node: RadioNode) -> str:
        """Check if the radio pair is valid for analysis.
        
        Parameters
        ----------
        rx_radio_node : RadioNode
            The receiver radio node.
        tx_radio_node : RadioNode
            The transmitter radio node.
            
        Returns
        -------
        str
            Empty string if valid, error message otherwise.
        """
        # Check that both radio nodes exist
        if rx_radio_node is None:
            return "Receiver radio node is None."
        if tx_radio_node is None:
            return "Transmitter radio node is None."
        
        # Check that both radios are enabled
        if not hasattr(rx_radio_node, 'enabled') or not rx_radio_node.enabled:
            return "Receiver radio is not enabled."
        if not hasattr(tx_radio_node, 'enabled') or not tx_radio_node.enabled:
            return "Transmitter radio is not enabled."
        
        # Additional validation can be added here based on radio types
        # For now, basic validation passes
        return ""

    def _check_results_exist(self, domain: InteractionDomain = None) -> bool:
        """Check if simulation results exist for the given domain.
        
        Parameters
        ----------
        domain : InteractionDomain, optional
            The domain to check. If None, uses self.domain.
            
        Returns
        -------
        bool
            True if results exist for the domain, False otherwise.
        """
        # Use the provided domain or default to self.domain
        check_domain = domain if domain is not None else self.domain
            
        self.emit_project.results.current_revision._load_revision()
        results_exist = self.emit_project._emit_com_module.GetResultsExist(
            self.emit_project.results.current_revision.results_index,
            check_domain.receiver_name,
            check_domain.receiver_band_name,
            check_domain.receiver_channel_frequency,
            check_domain.interferer_names,
            check_domain.interferer_band_names,
            check_domain.interferer_channel_frequencies,
        )
        
        return results_exist
