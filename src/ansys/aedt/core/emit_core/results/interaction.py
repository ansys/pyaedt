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
        error = self._check_interaction_validity()
        if error:
            raise RuntimeError(f"Cannot get worst case instance: {error}")
        
        if result_type == ResultType.POWER_AT_RX:
            warnings.warn("Worst case instances are not available for Power At Rx.")
            return None
        
        # Call GetWorstInstance to get the channel indexes for the worst case
        self.emit_project.results.current_revision._load_revision()
        worst_indexes = self.emit_project._emit_com_module.GetWorstInstance(
            self.emit_project.results.current_revision.results_index,
            result_type.value,
            self.domain.receiver_name,
            self.domain.receiver_band_name,
            self.domain.receiver_channel_frequency,
            self.domain.interferer_names,
            self.domain.interferer_band_names,
            self.domain.interferer_channel_frequencies,
        )
        
        if not worst_indexes or len(worst_indexes) == 0:
            warnings.warn("No worst case instance found.")
            return None
        
        # Create a new domain with the worst case channel indexes
        # The indexes represent specific channel frequencies
        worst_domain = InteractionDomain(self.emit_project)
        
        # Get the band nodes to map indexes to frequencies
        rx_band_node = self.current_revision.get_band_node(self.domain.receiver_band_name)
        tx_band_nodes = [self.current_revision.get_band_node(name) for name in self.domain.interferer_band_names]
        
        if rx_band_node and len(worst_indexes) >= 2:
            # For 1-to-1: [tx_channel_idx, rx_channel_idx]
            tx_channel_idx = worst_indexes[0]
            rx_channel_idx = worst_indexes[1] if len(worst_indexes) > 1 else -1
            
            # Get the actual frequencies from the channel indexes
            rx_freqs = rx_band_node.get_active_frequencies(is_rx=True, units="Hz")
            if rx_channel_idx >= 0 and rx_channel_idx < len(rx_freqs):
                rx_freq = rx_freqs[rx_channel_idx]
            else:
                rx_freq = -1
            
            worst_domain.set_receiver(self.domain.receiver_name, self.domain.receiver_band_name, rx_freq, "Hz")
            
            # Set interferer with worst channel
            if tx_band_nodes and tx_band_nodes[0] and tx_channel_idx >= 0:
                tx_freqs = tx_band_nodes[0].get_active_frequencies(is_rx=False, units="Hz")
                if tx_channel_idx < len(tx_freqs):
                    tx_freq = tx_freqs[tx_channel_idx]
                    worst_domain.set_interferer(
                        self.domain.interferer_names[0],
                        self.domain.interferer_band_names[0],
                        tx_freq,
                        "Hz"
                    )
        
        # Now get the instance data for the worst case domain
        return self.get_instance(worst_domain)
    

    # def get_worst_instance(self, result_type: ResultType) -> InteractionInstance:
    #     """Get the worst instance for this interaction.

    #     Parameters
    #     ----------
    #     result_type : ResultType
    #         The interaction instance to get the worst case instance for.
    #     result_type : ResultType
    #         The result type to get the worst case instance for.

    #     Returns
    #     -------
    #     InteractionInstance
    #         The worst case instance for this interaction.

    #     Raises
    #     ------
    #     RuntimeError
    #         If the worst case instance cannot be retrieved.
    #     """
    #     status = self.emit_project._emit_com_module.CheckInstanceValidity()
    #     if status != "":
    #         raise RuntimeError(status)

    #     # Can't compute worst instance for Power at RX
    #     if result_type == ResultType.POWER_AT_RX:
    #         err_msg = "Worst case instances are not available for Power At Rx."
    #         warnings.warn(err_msg)
    #         return None

    #     complete = self.emit_project._emit_com_module.IsComplete()
    #     if not complete:
    #         warnings.warn("The result is not available. The interaction is not fully analyzed.")
    #         return None

    #     sim = self.current_revision.get_simulation()
    #     status = sim.is_domain_valid(self.domain)
    #     if status != "":
    #         warnings.warn(status)
    #         warnings.warn("The interaction domain is not valid. Cannot retrieve worst case instance.")
    #         return None

    #     count = self.emit_project._emit_com_module.GetInstanceCount(result_type.value)
    #     if count == 0:
    #         warnings.warn("The instance domain is empty.")
    #         return None

    #     rx_radio_node = self.current_revision.get_radio_node(self.domain.receiver_name)
    #     rx_band_node = self.current_revision.get_band_node(self.domain.receiver_band_name) if self.domain.receiver_band_name else None
    #     tx_radio_nodes = [self.current_revision.get_radio_node(name) for name in self.domain.interferer_names]
    #     tx_band_nodes = [self.current_revision.get_band_node(name) for name in self.domain.interferer_band_names]

    #     rx_node = rx_band_node if rx_band_node else rx_radio_node
        
    #     rx_channel_index = next((rx_node.get_active_frequencies(is_rx=True).index(freq) for freq in [self.domain.receiver_channel_frequency] if freq >= 0), -1)
    #     tx_channel_indexes = next((tx_band.get_active_frequencies(is_rx=False).index(freq) for tx_band in tx_band_nodes for freq in self.domain.interferer_channel_frequencies if freq >= 0 and freq in tx_band.get_active_frequencies(is_rx=False)), -1)

    #     is_desense = (result_type == ResultType.DESENSE or result_type == ResultType.SENSITIVITY)
        
    #     if (len(tx_radio_nodes) == 1):
    #         tx_node = None
    #         if len(tx_band_nodes) > 0 and tx_band_nodes[0]:
    #             tx_node = tx_band_nodes[0]
    #         else:
    #             tx_node = tx_radio_nodes[0]
    #         tx_channel_index = -1
    #         if(len(tx_channel_indexes) > 0):
    #             tx_channel_index = tx_channel_indexes[0]
    #     # TODO: Complete worst instance implementation - needs new COM API
    #     # Need to add GetWorstInstance COM method that returns:
    #     # - encoded_emi, encoded_desense, largest_emi_interferer_type
    #     # Then create InteractionInstance with that data:
    #     #   worst_instance = InteractionInstance(self.emit_project, worst_domain)
    #     #   worst_instance.encoded_emi = <from COM>
    #     #   worst_instance.encoded_desense = <from COM>
    #     #   worst_instance.largest_emi_interferer_type = <from COM>
    #     #   return worst_instance
    #     raise NotImplementedError("get_worst_instance requires new COM API: GetWorstInstance")

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
        # Call HasValidAvailability via COM
        self.emit_project.results.current_revision._load_revision()
        has_valid = self.emit_project._emit_com_module.HasValidAvailability(
            self.emit_project.results.current_revision.results_index,
            domain.receiver_name,
            domain.receiver_band_name,
            domain.receiver_channel_frequency,
            domain.interferer_names,
            domain.interferer_band_names,
            domain.interferer_channel_frequencies,
        )
        return bool(has_valid)

    def get_availability(self, domain: InteractionDomain) -> float:
        """Get the availability of this interaction.
        
        Parameters
        ----------
        domain : InteractionDomain
            The interaction domain to get availability for.
            
        Returns
        -------
        float
            The availability value for this interaction. Returns -1 if not valid.
            
        Raises
        ------
        RuntimeError
            If the domain is invalid or availability cannot be calculated.
        """
        # First check if availability is valid for this domain
        if not self.has_valid_availability(domain):
            warning = self.get_availability_warning(domain)
            raise RuntimeError(f"Availability is not valid for this domain: {warning}")
        
        # Call GetAvailability via COM
        self.emit_project.results.current_revision._load_revision()
        availability = self.emit_project._emit_com_module.GetAvailability(
            self.emit_project.results.current_revision.results_index,
            domain.receiver_name,
            domain.receiver_band_name,
            domain.receiver_channel_frequency,
            domain.interferer_names,
            domain.interferer_band_names,
            domain.interferer_channel_frequencies,
        )
        return float(availability)

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
        # Call GetAvailabilityWarning via COM
        self.emit_project.results.current_revision._load_revision()
        warning = self.emit_project._emit_com_module.GetAvailabilityWarning(
            self.emit_project.results.current_revision.results_index,
            domain.receiver_name,
            domain.receiver_band_name,
            domain.receiver_channel_frequency,
            domain.interferer_names,
            domain.interferer_band_names,
            domain.interferer_channel_frequencies,
        )
        return str(warning)

    def get_instance(self, domain: InteractionDomain) -> InteractionInstance:
        """Get the instance at the specified index for this interaction."""
        # Validate the domain can return a single instance
        if not domain.is_single_instance():
            raise RuntimeError("The instance domain must be fully defined.")
        
        sim = self.current_revision.get_simulation()
        status = sim.is_domain_valid(domain)
        if status != "":
            raise RuntimeError(status)

        # Call GetInstance to get the encoded result values
        self.emit_project.results.current_revision._load_revision()
        instance_values = self.emit_project._emit_com_module.GetInstance(
            self.emit_project.results.current_revision.results_index,
            ResultType.EMI.value,  # Get EMI results
            domain.receiver_name,
            domain.receiver_band_name,
            domain.receiver_channel_frequency,
            domain.interferer_names,
            domain.interferer_band_names,
            domain.interferer_channel_frequencies,
        )
        
        # Create InteractionInstance and populate with values
        instance = InteractionInstance(self.emit_project, domain)
        
        if instance_values and len(instance_values) > 0:
            # The COM method returns encoded values (dB * 100)
            instance.encoded_emi = instance_values[0] if len(instance_values) > 0 else -32768
            
            # Also get desense values
            desense_values = self.emit_project._emit_com_module.GetInstance(
                self.emit_project.results.current_revision.results_index,
                ResultType.DESENSE.value,  # Get Desense results
                domain.receiver_name,
                domain.receiver_band_name,
                domain.receiver_channel_frequency,
                domain.interferer_names,
                domain.interferer_band_names,
                domain.interferer_channel_frequencies,
            )
            
            if desense_values and len(desense_values) > 0:
                instance.encoded_desense = desense_values[0]
        
        return instance

    def results_exist(self) -> bool:
        """Check if this interaction analysis is complete.
        
        Returns
        -------
        bool
            True if the interaction has been fully analyzed, False otherwise.
        """
        return self.emit_project._emit_com_module.GetResultsExist()

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
        is_complete = self._check_results_exist()
        
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

    def _check_interaction_validity(self) -> str:
        """Check if this interaction is valid.
        
        Returns
        -------
        str
            Empty string if valid, error message otherwise.
        """
        is_complete = self._check_results_exist()
        
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
        
        return error_message

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
        results_exist = bool(results_exist)
        return results_exist
