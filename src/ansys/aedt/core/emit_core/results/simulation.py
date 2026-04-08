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

from ansys.aedt.core.emit_core.emit_constants import EmiCategoryFilter
from ansys.aedt.core.emit_core.emit_constants import InterfererType
from ansys.aedt.core.emit_core.emit_constants import ResultType
from ansys.aedt.core.emit_core.emit_constants import TxRxMode
from ansys.aedt.core.emit_core.nodes.generated import Band
from ansys.aedt.core.emit_core.nodes.generated import RadioNode
from ansys.aedt.core.emit_core.results.interaction import Interaction
from ansys.aedt.core.emit_core.results.interaction_domain import InteractionDomain
from ansys.aedt.core.generic.general_methods import pyaedt_function_handler
from ansys.aedt.core.internal.checks import min_aedt_version


class Simulation:
    """
    Provides the ``Simulation`` object for running EMIT analyses.

    The Simulation object contains methods for running interference analyses,
    getting interactions, and managing simulation parameters.

    Parameters
    ----------
    revision :
        ``Revision`` object that this simulation is associated with.

    Examples
    --------
    Get a ``Simulation`` instance from a revision.

    >>> aedtapp = Emit()
    >>> rev = aedtapp.results.current_revision
    >>> sim = rev.get_simulation()
    >>> domain = InteractionDomain(aedtapp)
    >>> sim.run(domain)
    """

    def __init__(self, revision):
        self._revision = revision
        """Parent Revision object."""

        self.aedt_version = revision.aedt_version
        """AEDT version."""

        self.odesktop = revision.odesktop
        """Desktop object."""

        self.emit_project = revision.emit_project
        """Emit project instance."""

        self.results_index = revision.results_index
        """Revision results index."""

    @pyaedt_function_handler()
    @min_aedt_version("2025.2")
    def get_interaction(self, domain: InteractionDomain):
        """
        Create a new interaction for a domain.

        Parameters
        ----------
        domain : class:`Emit.InteractionDomain`
            ``InteractionDomain`` object for constraining the analysis parameters.

        Returns
        -------
        interaction:class: `Interaction`
            Interaction object.

        Examples
        --------
        >>> domain = InteractionDomain(aedtapp)
        >>> sim = rev.get_simulation()
        >>> sim.get_interaction(domain)

        """
        # TODO: update when Domain methods are added to API
        self._revision._load_revision()
        engine = self._revision.emit_project._emit_api.get_engine()
        if domain.interferer_names and engine.max_simultaneous_interferers != len(domain.interferer_names):
            raise ValueError("The max_simultaneous_interferers must equal the number of interferers in the domain.")
        interaction = engine.get_interaction(domain)
        return interaction

    @pyaedt_function_handler()
    @min_aedt_version("2023.2")
    def run(self, domain: InteractionDomain):
        """
        Load the revision and then analyze along the given domain.

        Parameters
        ----------
        domain :
            ``InteractionDomain`` object for constraining the analysis parameters.

        Returns
        -------
        interaction:class: `Interaction`
            Interaction object.

        Examples
        --------
        >>> domain = InteractionDomain(aedtapp)
        >>> sim = rev.get_simulation()
        >>> sim.run(domain)

        """
        if domain.receiver_channel_frequency > 0:
            raise ValueError("The domain must not have channels specified.")
        if len(domain.interferer_channel_frequencies) != 0:
            for freq in domain.interferer_channel_frequencies:
                if freq > 0:
                    raise ValueError("The domain must not have channels specified.")
        self._revision._load_revision()
        if self._revision.emit_project._aedt_version < "2024.1":
            if len(domain.interferer_names) == 1:
                engine = self._revision.emit_project._emit_api.get_engine()
                engine.max_simultaneous_interferers = 1
            if len(domain.interferer_names) > 1:
                raise ValueError("Multiple interferers cannot be specified prior to AEDT version 2024 R1.")
        if self._revision.emit_project._aedt_version > "2025.1":
            # check for disconnected systems and add a warning
            disconnected_radios = self._revision._get_disconnected_radios()
            if len(disconnected_radios) > 0:
                err_msg = (
                    "Some radios are part of a system with unconnected ports or errors "
                    "and will not be included in the EMIT analysis: " + ", ".join(disconnected_radios)
                )
                warnings.warn(err_msg)
        if self._revision.emit_project._aedt_version < "2027.1":
            engine = self._revision.emit_project._emit_api.get_engine()
            interaction = engine.run(domain)
        else:
            interaction: Interaction = self.emit_project._emit_com_module.RunEmitDomain(
                self._revision.results_index,
                domain.receiver_name,
                domain.receiver_band_name,
                domain.receiver_channel_frequency,
                domain.interferer_names,
                domain.interferer_band_names,
                domain.interferer_channel_frequencies,
            )
            interaction.domain = domain
        # save the project and revision
        self._revision.emit_project.save_project()
        return interaction

    @pyaedt_function_handler()
    @min_aedt_version("2027.1")
    def is_domain_valid(self, domain: InteractionDomain) -> str:
        """
        Return ``True`` if the given domain is valid for the current revision.

        Parameters
        ----------
        domain :
            ``InteractionDomain`` object for constraining the analysis parameters.

        Examples
        --------
        >>> domain = InteractionDomain(aedtapp)
        >>> sim = aedtapp.results.current_revision.get_simulation()
        >>> sim.is_domain_valid(domain)
        True
        """
        self._revision._load_revision()
        valid = self.emit_project._emit_com_module.CheckDomainValidity(
            self._revision.results_index,
            domain.receiver_name,
            domain.receiver_band_name,
            domain.receiver_channel_frequency,
            domain.interferer_names,
            domain.interferer_band_names,
            domain.interferer_channel_frequencies,
        )
        return valid

    @pyaedt_function_handler()
    @min_aedt_version("2025.2")
    def get_instance_count(self, domain: InteractionDomain):
        """
        Return the number of instances in the domain for the current revision.

        Parameters
        ----------
        domain :
            ``InteractionDomain`` object for constraining the analysis parameters.

        Returns
        -------
        count : int
            Number of instances in the domain for the current revision.

        Examples
        --------
        >>> domain = InteractionDomain(aedtapp)
        >>> sim = aedtapp.results.current_revision.get_simulation()
        >>> num_instances = sim.get_instance_count(domain)
        """
        self._revision._load_revision()
        engine = self._revision.emit_project._emit_api.get_engine()
        return engine.get_instance_count(domain)

    @property
    @min_aedt_version("2027.1")
    def n_to_1_limit(self) -> int:
        """
        Maximum number of interference combinations to run per receiver for N to 1.

        Returns
        -------
        max_instances : int
            Maximum number of interference combinations to run per receiver for N to 1.
        - A value of ``0`` disables N to 1 entirely.
        - A value of  ``-1`` allows unlimited N to 1. (N is set to the maximum.)

        Examples
        --------
        >>> sim = aedtapp.results.current_revision.get_simulation()
        >>> sim.n_to_1_limit = 2**20
        >>> sim.n_to_1_limit
        1048576
        """
        if self._revision.revision_loaded:
            engine = self._revision.emit_project._emit_api.get_engine()
            max_instances = engine.n_to_1_limit
        else:  # pragma: no cover
            max_instances = None
        return max_instances

    @n_to_1_limit.setter
    @min_aedt_version("2025.2")
    def n_to_1_limit(self, max_instances: int):
        if self._revision.revision_loaded:
            engine = self._revision.emit_project._emit_api.get_engine()
            engine.n_to_1_limit = max_instances

    @min_aedt_version("2025.2")
    def get_emi_category_filter_enabled(self, category: EmiCategoryFilter) -> bool:
        """Get whether the EMI category filter is enabled.

        Parameters
        ----------
        category : :class:`EmiCategoryFilter`
            EMI category filter.

        Returns
        -------
        bool
            ``True`` when the EMI category filter is enabled, ``False`` otherwise.
        """
        engine = self._revision.emit_project._emit_api.get_engine()
        return engine.get_emi_category_filter_enabled(category)

    @min_aedt_version("2025.2")
    def set_emi_category_filter_enabled(self, category: EmiCategoryFilter, enabled: bool):
        """Set whether the EMI category filter is enabled.

        Parameters
        ----------
        category : :class:`EmiCategoryFilter`
            EMI category filter.
        enabled : bool
            Whether to enable the EMI category filter.
        """
        engine = self._revision.emit_project._emit_api.get_engine()
        engine.set_emi_category_filter_enabled(category, enabled)

    @pyaedt_function_handler()
    @min_aedt_version("2025.2")
    def enable_n_to_1(self, enabled: bool):
        """Enables unlimited N to 1 analysis, which runs all combinations of interferers for each receiver.

        Parameters
        ----------
        enabled : bool
            Whether to enable unlimited N to 1 analysis.
        """
        if enabled:
            self.n_to_1_limit = -1  # allow unlimited N to 1
        else:
            self.n_to_1_limit = 0  # disable N to 1

    @pyaedt_function_handler
    @min_aedt_version("2024.2")
    def get_license_session(self):
        """Get a license session.

        A license session can be started with checkout(), and ended with check in().
        The `with` keyword can also be used, where checkout() is called on enter, and check in() is called on exit.

        Avoids having to wait for license check in and checkout when doing many runs.

        Examples
        --------
        sim = revision.get_simulation()
        with sim.get_license_session():
            domain = InteractionDomain(aedtapp)
            sim.run(domain)
        """
        engine = self._revision.emit_project._emit_api.get_engine()
        return engine.license_session()

    @pyaedt_function_handler()
    @min_aedt_version("2023.2")
    def interference_type_classification(
        self,
        domain: InteractionDomain,
        interferer_type: InterfererType = InterfererType.TRANSMITTERS,
        use_filter: bool = False,
        filter_list: list[str] = None,
    ):  # pragma: no cover
        """Classify interference type as according to inband/inband,
        out of band/in band, inband/out of band, and out of band/out of band.

        Parameters
        ----------
            domain :
                ``InteractionDomain`` object for constraining the analysis parameters.
            interferer_type : TxRxMode, optional
                Specifies whether to analyze all interferers, radios only, or emitters only.
            use_filter : bool, optional
                Whether filtering is being used. The default is ``False``.
            filter_list : list[str], optional
                List of filter values selected by the user via the GUI if filtering is in use.

        Returns
        -------
            power_matrix : list
                List of worst case interference power at Rx.
            all_colors : list
                Color classification of interference types.

        Examples
        --------
        >>> sim = rev.get_simulation()
        >>> interference_results = sim.interference_type_classification(domain)
        """
        power_matrix = []
        all_colors = []

        # Get project results and radios
        mode_rx = TxRxMode.RX
        mode_tx = TxRxMode.TX
        rx_radios = self._revision.get_all_radio_nodes(tx_rx_mode=mode_rx)
        if interferer_type == InterfererType.TRANSMITTERS:
            tx_radios = self._revision.get_all_radio_nodes(tx_rx_mode=mode_tx)
        elif interferer_type == InterfererType.TRANSMITTERS_AND_EMITTERS:
            tx_radios = self._revision.get_all_radio_nodes(tx_rx_mode=mode_tx, include_emitters=True)
        else:
            tx_radios = self._revision.get_all_emitter_radios()

        if tx_radios is None:
            raise ValueError("No interferers defined in the analysis.")
        if rx_radios is None:
            raise ValueError("No receivers defined in the analysis.")

        for tx_radio in tx_radios:
            rx_powers = []
            rx_colors = []
            for rx_radio in rx_radios:
                rx_radio: RadioNode
                # powerAtRx is the same for all Rx bands, so just use first one
                if tx_radio == rx_radio:
                    # skip self-interaction
                    rx_powers.append("N/A")
                    rx_colors.append("white")
                    continue

                max_power = -200
                rx_band_nodes = self._revision.get_all_band_nodes(radio=rx_radio, enabled_only=True, tx_rx_mode=mode_rx)
                tx_band_nodes = self._revision.get_all_band_nodes(radio=tx_radio, enabled_only=True, tx_rx_mode=mode_tx)

                for rx_band in rx_band_nodes:
                    # Find the highest power level at the Rx input due to each Tx Radio.
                    # Can look at any Rx freq since susceptibility won't impact
                    # powerAtRx, but need to look at all tx channels since coupling
                    # can change over a transmitter's bandwidth
                    rx_band: Band
                    rx_freq = rx_band.get_active_frequencies(is_rx=True, units="Hz")[0]

                    rx_start_freq = rx_band.start_frequency
                    rx_stop_freq = rx_band.stop_frequency
                    rx_channel_bandwidth = rx_band.channel_bandwidth

                    for tx_band in tx_band_nodes:
                        tx_band: Band
                        domain.set_receiver(rx_radio.name, rx_band.name)
                        domain.set_interferer(tx_radio.name, tx_band.name)
                        interaction = self.run(domain)
                        # check for valid interaction, this would catch any disabled radio pairs
                        if not interaction.is_valid():
                            continue

                        domain.set_receiver(rx_radio.name, rx_band.name, rx_freq, "Hz")
                        tx_freqs = tx_band.get_active_frequencies(is_rx=False, units="Hz")
                        for tx_freq in tx_freqs:
                            domain.set_interferer(tx_radio.name, tx_band.name, tx_freq, "Hz")
                            instance = interaction.get_instance(domain)
                            if not instance.has_valid_values():
                                # check for saturation somewhere in the chain
                                # set power=200 to flag it as strong interference
                                if instance.get_result_warning() == "An amplifier was saturated.":
                                    max_power = 200
                                else:
                                    # other warnings (e.g. no path from Tx to Rx,
                                    # no power received, error in configuration, etc.)
                                    # should just be skipped
                                    continue
                            else:
                                tx_prob = instance.get_largest_emi_problem_type().replace(" ", "").split(":")[1]
                                power = instance.get_value(ResultType.EMI)
                            if (
                                rx_start_freq - rx_channel_bandwidth / 2
                                <= tx_freq
                                <= rx_stop_freq + rx_channel_bandwidth / 2
                            ):
                                rx_prob = "In-band"
                            else:
                                rx_prob = "Out-of-band"
                            prob_filter_val = tx_prob + ":" + rx_prob

                            # Check if problem type is in filtered list of problem types to analyze
                            if use_filter:
                                in_filters = any(prob_filter_val in sublist for sublist in filter_list)
                            else:
                                in_filters = True

                            # Save the worst case interference values
                            if power > max_power and in_filters:
                                max_power = power
                                largest_rx_prob = rx_prob
                                prob = instance.get_largest_emi_problem_type()
                                largest_tx_prob = prob.replace(" ", "").split(":")

                if max_power > -200:
                    rx_powers.append(max_power)

                    if largest_tx_prob[-1] == "TxFundamental" and largest_rx_prob == "In-band":
                        rx_colors.append("red")
                    elif largest_tx_prob[-1] != "TxFundamental" and largest_rx_prob == "In-band":
                        rx_colors.append("orange")
                    elif largest_tx_prob[-1] == "TxFundamental" and not (largest_rx_prob == "In-band"):
                        rx_colors.append("yellow")
                    elif largest_tx_prob[-1] != "TxFundamental" and not (largest_rx_prob == "In-band"):
                        rx_colors.append("green")
                else:
                    rx_powers.append("<= -200")
                    rx_colors.append("white")

            all_colors.append(rx_colors)
            power_matrix.append(rx_powers)

        return all_colors, power_matrix

    @pyaedt_function_handler()
    @min_aedt_version("2023.2")
    def protection_level_classification(
        self,
        domain,
        interferer_type: InterfererType = InterfererType.TRANSMITTERS,
        global_protection_level: bool = True,
        global_levels: list = None,
        protection_levels: dict = None,
        use_filter: bool = False,
        filter_list: list[str] = None,
    ):  # pragma: no cover
        """
        Classify worst-case power at each Rx radio according to interference type.

        Options for interference type are `inband/inband, out of band/in band,
        inband/out of band, and out of band/out of band.

        Parameters
        ----------
            domain :
                ``InteractionDomain`` object for constraining the analysis parameters.
            interferer_type : TxRxMode, optional
                Specifies whether to analyze all interferers, radios only, or emitters only.
            global_protection_level : bool, optional
                Whether to use the same protection levels for all radios. The default is ``True``.
            global_levels : list, optional
                List of protection levels to use for all radios.
            protection_levels : dict, optional
                Dictionary of protection levels for each Rx radio.
            use_filter : bool, optional
                Whether to use filtering. The default is ``False``.
            filter_list : list, optional
                List of filter values selected by the user via the GUI if filtering is in use.

        Returns
        -------
            power_matrix : list
                Worst case interference according to power at each Rx radio.
            all_colors : list
                Color classification of protection level.

        Examples
        --------
        >>> sim = rev.get_simulation()
        >>> protection_results = sim.protection_level_classification(domain)
        """
        power_matrix = []
        all_colors = []

        # Get project results and radios
        mode_rx = TxRxMode.RX
        mode_tx = TxRxMode.TX
        mode_power = ResultType.POWER_AT_RX
        rx_radios = self._revision.get_all_radio_nodes(tx_rx_mode=mode_rx)
        if interferer_type == InterfererType.TRANSMITTERS:
            tx_radios = self._revision.get_all_radio_nodes(tx_rx_mode=mode_tx)
        elif interferer_type == InterfererType.TRANSMITTERS_AND_EMITTERS:
            tx_radios = self._revision.get_all_radio_nodes(tx_rx_mode=mode_tx, include_emitters=True)
        else:
            tx_radios = self._revision.get_all_emitter_radios()

        if tx_radios is None:
            raise ValueError("No interferers defined in the analysis.")
        if rx_radios is None:
            raise ValueError("No receivers defined in the analysis.")

        if global_protection_level and global_levels is None:
            damage_threshold = 30
            overload_threshold = 4
            intermod_threshold = -20
        elif global_protection_level:
            damage_threshold = global_levels[0]
            overload_threshold = global_levels[1]
            intermod_threshold = global_levels[2]

        for tx_radio in tx_radios:
            rx_powers = []
            rx_colors = []
            for rx_radio in rx_radios:
                # powerAtRx is the same for all Rx bands, so just
                # use the first one
                if not global_protection_level:
                    damage_threshold = protection_levels[rx_radio.name][0]
                    overload_threshold = protection_levels[rx_radio.name][1]
                    intermod_threshold = protection_levels[rx_radio.name][2]

                if tx_radio == rx_radio:
                    # skip self-interaction
                    rx_powers.append("N/A")
                    rx_colors.append("white")
                    continue

                max_power = -200

                rx_band = self._revision.get_all_band_nodes(radio=rx_radio, enabled_only=True, tx_rx_mode=mode_rx)[0]
                tx_band_nodes = self._revision.get_all_band_nodes(radio=tx_radio, enabled_only=True, tx_rx_mode=mode_tx)

                for tx_band in tx_band_nodes:
                    # Find the highest power level at the Rx input due to each Tx Radio.
                    # Can look at any Rx freq since susceptibility won't impact
                    # powerAtRx, but need to look at all tx channels since coupling
                    # can change over a transmitter's bandwidth
                    rx_freq = rx_band.get_active_frequencies(is_rx=True, units="Hz")[0]
                    domain.set_receiver(rx_radio.name, rx_band.name)
                    domain.set_interferer(tx_radio.name, tx_band.name)
                    interaction = self.run(domain)
                    # check for valid interaction, this would catch any disabled radio pairs
                    if not interaction.is_valid():
                        continue
                    domain.set_receiver(rx_radio.name, rx_band.name, rx_freq, "Hz")
                    tx_freqs = tx_band.get_active_frequencies(is_rx=False, units="Hz")

                    power_list = []

                    for tx_freq in tx_freqs:
                        domain.set_interferer(tx_radio.name, tx_band.name, tx_freq, "Hz")
                        instance = interaction.get_instance(domain)
                        if not instance.has_valid_values():
                            # check for saturation somewhere in the chain
                            # set power=200 to flag it as "damage threshold"
                            if instance.get_result_warning() == "An amplifier was saturated.":
                                max_power = 200
                            else:
                                # other warnings (e.g. no path from Tx to Rx,
                                # no power received, error in configuration, etc.)
                                # should just be skipped
                                continue
                        else:
                            power = instance.get_value(mode_power)

                        if power > damage_threshold:
                            classification = "damage"
                        elif power > overload_threshold:
                            classification = "overload"
                        elif power > intermod_threshold:
                            classification = "intermodulation"
                        else:
                            classification = "desensitization"

                        power_list.append(power)

                        if use_filter:
                            filtering = classification in filter_list
                        else:
                            filtering = True

                        if power > max_power and filtering:
                            max_power = power

                # If the worst case for the band-pair is below the power thresholds, then
                # there are no interference issues and no offset is required.
                if max_power > -200:
                    rx_powers.append(max_power)
                    if max_power > damage_threshold:
                        rx_colors.append("red")
                    elif max_power > overload_threshold:
                        rx_colors.append("orange")
                    elif max_power > intermod_threshold:
                        rx_colors.append("yellow")
                    else:
                        rx_colors.append("green")
                else:
                    rx_powers.append("< -200")
                    rx_colors.append("white")

            all_colors.append(rx_colors)
            power_matrix.append(rx_powers)

        return all_colors, power_matrix
