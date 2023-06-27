from pyaedt.emit_core.emit_constants import InterfererType, ResultType, TxRxMode
from pyaedt import Emit
import pyaedt
import sys

def interference_classification(emitapp, use_filter, filter):
    """
    Classisify interference type as according to inband/inband, 
    out of band/in band, inband/out of band, and out of band/out of band.

    Parameters
    ----------
        emitapp : instance of Emit
        use_filter : boolean value, True if filtering is being used
        filter : list of filter values if filtering is in use

        Returns
        -------
        power_matrix : list of worst case interference power at Rx
        all_colors : color classification of interterference types
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
                rx_powers.append('N/A')
                rx_colors.append('white')
                continue       

            max_power = -200
            tx_bands = rev.get_band_names(tx_radio, modeTx)
            tx_band_objects = radios[tx_radio].bands()

            for i in range(len(rx_bands)):
                # Find the highest power level at the Rx input due to each Tx Radio.
                # Can look at any Rx freq since susceptibility won't impact
                # powerAtRx, but need to look at all tx channels since coupling
                # can change over a transmitter's bandwidth
                rx_freq = rev.get_active_frequencies(rx_radio, rx_bands[i], modeRx)[0]

                # The start and stop frequencies define the Band's extents, 
                # while the active frequencies are a subset of the Band's frequencies 
                # being used for this specific project as defined in the Radio's Sampling.
                rx_start_freq = radios[rx_radio].band_start_frequency(rx_band_objects[i])
                rx_stop_freq = radios[rx_radio].band_stop_frequency(rx_band_objects[i])
                rx_channel_bandwidth = radios[rx_radio].band_channel_bandwidth(rx_band_objects[i])
                
                for j in range(len(tx_bands)):
                    domain.set_receiver(rx_radio, rx_bands[i])            
                    domain.set_interferer(tx_radio, tx_bands[j])
                    interaction = rev.run(domain)
                    domain.set_receiver(rx_radio, rx_bands[i], rx_freq)
                    tx_freqs = rev.get_active_frequencies(tx_radio, tx_bands[j], modeTx)
                    for tx_freq in tx_freqs:
                        domain.set_interferer(tx_radio, tx_bands[j], tx_freq)
                        instance = interaction.get_instance(domain)
                        tx_prob = instance.get_largest_problem_type(mode_power).replace(" ","").split(":")[1]
                        if rx_start_freq-rx_channel_bandwidth/2 <= tx_freq <= rx_stop_freq+rx_channel_bandwidth/2:
                            rx_prob = "In-band"
                        else:
                            rx_prob = 'Out-of-band'
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
                
                if largest_tx_prob[-1] == "TxFundamental" and largest_rx_prob == 'In-band':
                    rx_colors.append("red")
                elif largest_tx_prob[-1] != "TxFundamental" and largest_rx_prob == 'In-band':
                    rx_colors.append("orange")
                elif largest_tx_prob[-1] == "TxFundamental" and not(largest_rx_prob == 'In-band'):
                    rx_colors.append("yellow")
                elif largest_tx_prob[-1] != "TxFundamental" and not(largest_rx_prob == 'In-band'):
                    rx_colors.append("green")
            else:
                rx_powers.append("<= -200")
                rx_colors.append('white')
                
        all_colors.append(rx_colors)
        power_matrix.append(rx_powers)
    
    return all_colors, power_matrix