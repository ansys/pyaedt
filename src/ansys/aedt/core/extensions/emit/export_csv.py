def export_csv(csv_file, emi, rx_power, desense, sensitivity, aggressor, aggressor_band, aggressor_frequencies, victim, victim_band, victim_frequencies):

    pivot_results = "Agressor_Radio,Aggressor_Band,Aggressor_Channel,Victim_Radio,Victim_Band,Victim_Channel,EMI,RX_Power,Desense,Sensitivity \n"

    for aggressor_index in range(len(aggressor_frequencies)):

        aggressor_frequency = aggressor_frequencies[aggressor_index]
        for victim_index in range(len(victim_frequencies)):

            victim_frequency    = victim_frequencies[victim_index]

            pivot_results += f'{aggressor},{aggressor_band},{aggressor_frequency},{victim},{victim_band},{victim_frequency},{emi[aggressor_index][victim_index]},{rx_power[aggressor_index][victim_index]},{desense[aggressor_index][victim_index]},{sensitivity[aggressor_index][victim_index]}\n'

    print(pivot_results)
    with open(csv_file, 'w') as file:
        file.write(pivot_results)

    return

