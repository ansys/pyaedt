from pyaedt.emit_core.emit_constants import InterfererType
from pyaedt.emit_core.emit_constants import ResultType
from pyaedt.emit_core.emit_constants import TxRxMode


def interference_type_classification(emitapp, use_filter=False, filter_list=None):
    """
    Classify interference type as according to inband/inband,
    out of band/in band, inband/out of band, and out of band/out of band.

    Parameters
    ----------
        emitapp : instance of Emit
        use_filter : bool, optional
            Whether filtering is being used. The default is ``False``.
        filter_list : list, optional
            List of filter values selected by the user via the GUI if filtering is in use.

        Returns
        -------
        power_matrix : list
            List of worst case interference power at Rx.
        all_colors : list
            List of color classification of interference types.
    """
    power_matrix = []
    all_colors = []

    # Get project results and radios
    rev = emitapp.results.analyze()
    modeRx = TxRxMode.RX
    modeTx = TxRxMode.TX
    mode_power = ResultType.POWER_AT_RX
    tx_interferer = InterfererType().TRANSMITTERS
    rx_radios = rev.get_receiver_names()
    tx_radios = rev.get_interferer_names(tx_interferer)
    domain = emitapp.results.interaction_domain()
    radios = emitapp.modeler.components.get_radios()

    for tx_radio in tx_radios:
        rx_powers = []
        rx_colors = []
        for rx_radio in rx_radios:
            # powerAtRx is the same for all Rx bands, so just use first one
            rx_bands = rev.get_band_names(rx_radio, modeRx)
            rx_band_objects = radios[rx_radio].bands()
            if tx_radio == rx_radio:
                # skip self-interaction
                rx_powers.append("N/A")
                rx_colors.append("white")
                continue

            max_power = -200
            tx_bands = rev.get_band_names(tx_radio, modeTx)

            for i, rx_band in enumerate(rx_bands):
                # Find the highest power level at the Rx input due to each Tx Radio.
                # Can look at any Rx freq since susceptibility won't impact
                # powerAtRx, but need to look at all tx channels since coupling
                # can change over a transmitter's bandwidth
                rx_freq = rev.get_active_frequencies(rx_radio, rx_band, modeRx)[0]

                # The start and stop frequencies define the Band's extents,
                # while the active frequencies are a subset of the Band's frequencies
                # being used for this specific project as defined in the Radio's Sampling.
                rx_start_freq = radios[rx_radio].band_start_frequency(rx_band_objects[i])
                rx_stop_freq = radios[rx_radio].band_stop_frequency(rx_band_objects[i])
                rx_channel_bandwidth = radios[rx_radio].band_channel_bandwidth(rx_band_objects[i])

                for tx_band in tx_bands:
                    domain.set_receiver(rx_radio, rx_band)
                    domain.set_interferer(tx_radio, tx_band)
                    interaction = rev.run(domain)
                    domain.set_receiver(rx_radio, rx_band, rx_freq)
                    tx_freqs = rev.get_active_frequencies(tx_radio, tx_band, modeTx)
                    for tx_freq in tx_freqs:
                        domain.set_interferer(tx_radio, tx_band, tx_freq)
                        instance = interaction.get_instance(domain)
                        tx_prob = instance.get_largest_problem_type(mode_power).replace(" ", "").split(":")[1]
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
                            in_filters = any(prob_filter_val in sublist for sublist in filter)
                        else:
                            in_filters = True

                        # Save the worst case interference values
                        if instance.get_value(mode_power) > max_power and in_filters:
                            prob = instance.get_largest_problem_type(mode_power)
                            max_power = instance.get_value(mode_power)
                            largest_rx_prob = rx_prob
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


def protection_level_classification(
    emitapp,
    global_protection_level=True,
    global_levels=None,
    protection_levels=None,
    use_filter=False,
    filter_list=None,
):
    """
    Classify worst-case power at each Rx radio according to interference type.

    Options for interference type are `inband/inband, out of band/in band,
    inband/out of band, and out of band/out of band.

    Parameters
    ----------
        emitapp : instance of Emit
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
            List of worst case interference according to power at each Rx radio.
        all_colors : list
            List of color classification of protection level.
    """
    power_matrix = []
    all_colors = []

    # Get project results and radios
    rev = emitapp.results.analyze()
    modeRx = TxRxMode.RX
    modeTx = TxRxMode.TX
    mode_power = ResultType.POWER_AT_RX
    tx_interferer = InterfererType().TRANSMITTERS
    rx_radios = rev.get_receiver_names()
    tx_radios = rev.get_interferer_names(tx_interferer)
    domain = emitapp.results.interaction_domain()

    if global_protection_level:
        damage_threshold = global_levels[0]
        overload_threshold = global_levels[1]
        intermod_threshold = global_levels[2]

    for tx_radio in tx_radios:
        rx_powers = []
        rx_colors = []
        for rx_radio in rx_radios:
            # powerAtRx is the same for all Rx bands, so just
            # use the first one
            if not (global_protection_level):
                damage_threshold = protection_levels[rx_radio][0]
                overload_threshold = protection_levels[rx_radio][1]
                intermod_threshold = protection_levels[rx_radio][2]

            rx_band = rev.get_band_names(rx_radio, modeRx)[0]
            if tx_radio == rx_radio:
                # skip self-interaction
                rx_powers.append("N/A")
                rx_colors.append("white")
                continue

            max_power = -200
            tx_bands = rev.get_band_names(tx_radio, modeTx)

            for tx_band in tx_bands:
                # Find the highest power level at the Rx input due to each Tx Radio.
                # Can look at any Rx freq since susceptibility won't impact
                # powerAtRx, but need to look at all tx channels since coupling
                # can change over a transmitter's bandwidth
                rx_freq = rev.get_active_frequencies(rx_radio, rx_band, modeRx)[0]
                domain.set_receiver(rx_radio, rx_band)
                domain.set_interferer(tx_radio, tx_band)
                interaction = rev.run(domain)
                domain.set_receiver(rx_radio, rx_band, rx_freq)
                tx_freqs = rev.get_active_frequencies(tx_radio, tx_band, modeTx)

                power_list = []

                for tx_freq in tx_freqs:
                    domain.set_interferer(tx_radio, tx_band, tx_freq)
                    instance = interaction.get_instance(domain)
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

                    if instance.get_value(mode_power) > max_power and filtering:
                        max_power = instance.get_value(mode_power)

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
