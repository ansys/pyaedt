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
        # Validate the interaction before proceeding
        self.validate()

        if result_type == ResultType.POWER_AT_RX:
            warnings.warn("Worst case instances are not available for Power At Rx.")
            return None

        # N-to-1 worst instance cannot be scoped to a specific receiver channel.
        # Catch this before the gRPC call to provide a clearer error message.
        is_n_to_1 = len(self.domain.interferer_names) != 1 or (
            len(self.domain.interferer_names) == 1 and self.domain.interferer_names[0] == ""
        )
        if is_n_to_1 and self.domain.receiver_channel_frequency > 0:
            raise RuntimeError("Unable to retrieve N to 1 worst instance results for a specific receiver channel.")

        self.emit_project.results.current_revision._load_revision()
        result_data = self.emit_project._emit_com_module.GetWorstInstance(
            self.emit_project.results.current_revision.results_index,
            result_type,
            self.domain.receiver_name,
            self.domain.receiver_band_name,
            self.domain.receiver_channel_frequency,
            self.domain.interferer_names,
            self.domain.interferer_band_names,
            self.domain.interferer_channel_frequencies,
        )

        worst_instance = self._data_to_instance(result_data, result_type)
        return worst_instance

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
        warning = self.get_availability_warning(domain)
        if warning:
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
        # GetInstance only supports a single interferer
        if len(domain.interferer_names) > 1:
            raise RuntimeError("Instance data for multiple simultaneous interferers not available.")

        # Validate the domain can return a single instance
        if not domain.is_single_instance():
            raise RuntimeError("The instance domain must be fully defined.")

        # get_instance_count validates the domain (catches bad radio/band names) and
        # returns 0 when the radio pair is disabled at the simulation level.
        if self.get_instance_count(domain) == 0:
            raise RuntimeError("Radio pair disabled.")

        # Fetch instance data. The backend always computes both EMI and desense
        # in a single pass and returns [encodedEmi, encodedDesense, worstEmiIntCat].
        self.emit_project.results.current_revision._load_revision()
        instance_values = self.emit_project._emit_com_module.GetInstance(
            self.emit_project.results.current_revision.results_index,
            domain.receiver_name,
            domain.receiver_band_name,
            domain.receiver_channel_frequency,
            domain.interferer_names,
            domain.interferer_band_names,
            domain.interferer_channel_frequencies,
        )

        # Populate both EMI and desense from the single response array.
        instance = InteractionInstance(self.emit_project, domain)
        if instance_values and len(instance_values) >= 3:
            instance.encoded_emi = int(instance_values[0])
            instance.encoded_desense = int(instance_values[1])
            instance.largest_emi_interferer_type = int(instance_values[2])

        return instance

    def get_instance_count(self, domain: InteractionDomain = None) -> int:
        """Get the number of instances (channel combinations) for this interaction domain.

        Parameters
        ----------
        domain : InteractionDomain, optional
            The interaction domain to count instances for.
            If not provided, uses the interaction's own domain.

        Returns
        -------
        int
            The number of instances in the domain (product of channel counts).

        Raises
        ------
        RuntimeError
            If the domain is invalid.
        """
        if domain is None:
            domain = self.domain

        sim = self.current_revision.get_simulation()
        status = sim.is_domain_valid(domain)
        if status != "":
            raise RuntimeError(status)

        # Call GetInstanceCount to get the count of channel combinations
        self.emit_project.results.current_revision._load_revision()
        count = self.emit_project._emit_com_module.GetInstanceCount(
            self.emit_project.results.current_revision.results_index,
            domain.receiver_name,
            domain.receiver_band_name,
            domain.receiver_channel_frequency,
            domain.interferer_names,
            domain.interferer_band_names,
            domain.interferer_channel_frequencies,
        )

        return int(count)

    def get_domain(self) -> InteractionDomain:
        """Get the interaction domain for this interaction.

        Returns
        -------
        InteractionDomain
            The interaction domain.
        """
        return self.domain

    def is_valid(self) -> bool:
        """Check if this interaction is valid.

        The associated domain must be valid and results must exist for the interaction.

        Returns
        -------
        bool
            True if the interaction is valid, False otherwise.
        """
        return self._check_validity() == ""

    def validate(self) -> None:
        """Validate this interaction, raising an exception if invalid.

        The associated domain must be valid and results must exist for the interaction.

        Raises
        ------
        ValueError
            If the interaction is not valid, with details on why.
        """
        error = self._check_validity()
        if error:
            raise ValueError(error)

    def _check_validity(self) -> str:
        """
        Check if this interaction is valid. The associated domain must
        be valid and results must exist for the interaction.

        Returns
        -------
        str
            Empty string if valid, error message otherwise.
        """
        error = self.current_revision.get_simulation().is_domain_valid(self.domain)
        if error:
            return f"Interaction is not valid. The domain is invalid: {error}"

        if not self._check_results_exist():
            return "Interaction is not valid. The interaction results do not exist."
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

    def _data_to_instance(self, result_data, result_type: ResultType) -> InteractionInstance:
        """Convert the raw result data from GetWorstInstance into an InteractionInstance.

        Parameters
        ----------
        result_data : str
            The raw result data from GetWorstInstance.
        result_type : ResultType
            The type of result (EMI or DESENSE).

        Returns
        -------
        InteractionInstance
            The converted InteractionInstance, or None if no worst case instance was found.
        """
        # The COM method returns a pipe-delimited string:
        # rxRadio|rxBand|rxFreq|tx1Radio|tx1Band|tx1Freq|...|encodedValue|worstIntCat
        # Empty string means no worst instance was found.
        if not result_data:
            warnings.warn("No worst case instance found.")
            return None

        parts = str(result_data).split("|")
        if len(parts) < 5 or not parts[0]:
            warnings.warn("No worst case instance found.")
            return None

        # Last two fields are always encodedValue and worstIntCat
        rx_radio, rx_band, rx_freq_str, *middle_and_tail = parts
        worst_int_cat = int(middle_and_tail.pop())
        encoded_value = int(middle_and_tail.pop())
        tx_parts = middle_and_tail

        worst_domain = InteractionDomain(self.emit_project)
        worst_domain.set_receiver(rx_radio, rx_band, float(rx_freq_str), "Hz")

        # Group tx_parts into (radio, band, freq) triples
        tx_entries = list(zip(*[iter(tx_parts)] * 3))
        if len(tx_entries) == 1:
            tx_radio, tx_band, tx_freq_str = tx_entries[0]
            worst_domain.set_interferer(tx_radio, tx_band, float(tx_freq_str), "Hz")
        elif len(tx_entries) > 1:
            tx_radios, tx_bands, tx_freq_strs = zip(*tx_entries)
            worst_domain.set_interferers(list(tx_radios), list(tx_bands), [float(f) for f in tx_freq_strs], "Hz")

        # For both 1-to-1 and N-to-1, a worst-case instance only carries the requested
        # result type. The other is always 30201 ("not available"), matching old API behavior.
        instance = InteractionInstance(self.emit_project, worst_domain)
        if result_type == ResultType.EMI:
            instance.encoded_emi = encoded_value
            instance.largest_emi_interferer_type = worst_int_cat
            instance.encoded_desense = 30201
        else:
            instance.encoded_desense = encoded_value
            instance.encoded_emi = 30201
        return instance
