# ===========================================================================
# Description:
#   This python library will extract EMIT response like EMI, Rx_Power,
#   Sensitivity and Desense. The first function will extract this data
#   for all channel combinations between a single Transmit and Receive band.
#
# Authors: Bryan Kaylor, Jason Bommer, Eldon Staggs
#
# Revision History:
#   12/05/2024[Eldon]: Initial creation of EMI extraction for band to band interaction
#
# ===========================================================================
import pyaedt
from ansys.aedt.core.emit_core.emit_constants import TxRxMode, ResultType


def get_radios(project, version):
    # Launch the EMIT design of interest
    #
    #project = r'D:\Designs\Electronics_Desktop_2025\EMIT\AH-64 Apache Cosite.aedt'
    desktop = pyaedt.Desktop(specified_version=version, new_desktop=True)

    # Link to the results from the latest simulation
    #
    emit = pyaedt.Emit(project=project)
    revision = emit.results.analyze()
    domain = emit.results.interaction_domain()

    # Extract and return the Transmit / Receive radio lists
    #
    aggressors = revision.get_interferer_names()
    victims = revision.get_receiver_names()

    return aggressors, victims, domain, revision


def tx_rx_response(aggressor, victim, aggressor_band, victim_band, domain, revision):
    # For the given bands, extract all of the channels for each
    #
    aggressor_frequencies = revision.get_active_frequencies(aggressor, aggressor_band, TxRxMode.TX)
    victim_frequencies    = revision.get_active_frequencies(victim,    victim_band,    TxRxMode.RX)

    # I believe that this is for tying to where all of the results will reside?
    domain.set_receiver(victim, victim_band)
    domain.set_interferer(aggressor, aggressor_band)

    # Checkout the license once for EMIT for all of the data extraction iterations
    #
    interaction = revision.run(domain)
    with revision.get_license_session():

        emi=[]
        rx_power=[]
        desense=[]
        sensitivity=[]

        for aggressor_frequency in aggressor_frequencies:

            emi_line=[]
            rx_power_line=[]
            desense_line=[]
            sensitivity_line=[]
            domain.set_interferer(aggressor, aggressor_band, aggressor_frequency)

            for victim_frequency in victim_frequencies:

                #print(f'aggressor_frequency = {aggressor_frequency} victim_frequency = {victim_frequency}')
                domain.set_receiver(victim, victim_band, victim_frequency)

                instance = interaction.get_instance(domain)

                if instance.has_valid_values():
                    emi_line.append(instance.get_value(ResultType.EMI))  # dB
                    rx_power_line.append(instance.get_value(ResultType.POWER_AT_RX)) # dBM
                    desense_line.append(instance.get_value(ResultType.DESENSE))
                    sensitivity_line.append(instance.get_value(ResultType.SENSITIVITY))
                else:
                    warning = instance.get_result_warning()
                    print(f'No valid values: {warning}')

            emi.append(emi_line)
            rx_power.append(rx_power_line)
            desense.append(desense_line)
            sensitivity.append(sensitivity_line)

    return emi, rx_power, desense, sensitivity
