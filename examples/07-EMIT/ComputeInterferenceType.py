import sys
from pyaedt.emit_core.emit_constants import InterfererType, ResultType, TxRxMode
from pyaedt import Emit
import pyaedt
import os
import pyaedt.generic.constants as consts
import subprocess

# Check to see which Python libraries have been installed
reqs = subprocess.check_output([sys.executable, '-m', 'pip', 'freeze'])
installed_packages = [r.decode().split('==')[0] for r in reqs.split()]

# Install required packages if they are not installed
def install(package):
    subprocess.check_call([sys.executable, '-m', 'pip', 'install', package])

# Install any missing libraries
required_packages = ['plotly']
for package in required_packages:
    if package not in installed_packages:
        install(package)

# Import plotly library (if needed) to displa legend and scenario matrix results
import plotly.graph_objects as go

# Define colors for tables
table_colors = {"out-out":'#7d73ca', "in-out":'#d359a2', "out-in": '#ff6361', "in-in": '#ffa600', "white": '#ffffff'}
header_color = 'grey'

non_graphical = False
new_thread = True
desktop_version = "2023.2"
desktop = pyaedt.launch_desktop(desktop_version, non_graphical=non_graphical, new_desktop_session=new_thread)

path_to_desktop_project = sys.argv[1]
emit_design_name        = sys.argv[2]

emitapp = Emit(non_graphical=False, new_desktop_session=False, projectname=path_to_desktop_project, designname=emit_design_name)

if desktop_version <= "2023.1":
    print("Warning: this example requires AEDT 2023.2 or later.")
    sys.exit()


# Get all the radios in the project
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Get lists of all transmitters and receivers in the project.
rev = emitapp.results.analyze()
modeRx = TxRxMode().RX
modeTx = TxRxMode().TX
mode_power = ResultType().POWER_AT_RX
tx_interferer = InterfererType().TRANSMITTERS
rx_radios = rev.get_receiver_names()
tx_radios = rev.get_interferer_names(tx_interferer)
domain = emitapp.results.interaction_domain()
radios = emitapp.modeler.components.get_radios()

if tx_radios is None or rx_radios is None:
    print("No recievers or transmitters in design.")
    sys.exit()

# Initialize results arrays
power_matrix=[]
all_colors=[]


# Iterate over all the radios
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Iterate over all the transmitters and receivers and compute the power
# at the input to each receiver due to each of the transmitters. Computes
# which, if any, type of interference occured.

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
            rx_colors.append(table_colors['white'])
            continue    

        max_power = -200
        tx_bands = rev.get_band_names(tx_radio, modeTx)
        tx_band_objects = radios[tx_radio].bands()

        for i in range(len(rx_bands)):
            
            rx_freq = rev.get_active_frequencies(rx_radio, rx_bands[i], modeRx)
            rx_start_freq = radios[rx_radio].band_start_frequency(rx_band_objects[i])
            rx_stop_freq = consts.unit_converter(float(rx_band_objects[i].props["StopFrequency"]), "Freq", "Hz", "MHz")
            rx_channel_bandwidth = consts.unit_converter(float(rx_band_objects[i].props["ChannelBandwidth"]), "Freq", "Hz", "MHz")
            
            for j in range(len(tx_bands)):
                domain.set_receiver(rx_radio, rx_bands[i])            
                domain.set_interferer(tx_radio, tx_bands[j])
                interaction = rev.run(domain)
                domain.set_receiver(rx_radio, rx_bands[i], rx_freq[0])
                tx_freqs = rev.get_active_frequencies(tx_radio, tx_bands[j], modeTx)
                for tx_freq in tx_freqs:
                    domain.set_interferer(tx_radio, tx_bands[j], tx_freq)
                    instance = interaction.get_instance(domain)
                    if instance.get_value(mode_power) > max_power:
                        tx_prob = instance.get_largest_problem_type(mode_power)
                        max_power = instance.get_value(mode_power)
                        tx_prob = instance.get_largest_problem_type(mode_power).replace(" ","").split(":")[1]
                        if rx_start_freq-rx_channel_bandwidth/2 <= tx_freq <= rx_stop_freq+rx_channel_bandwidth/2:
                            rx_prob = "In-band"
                        else:
                            rx_prob = 'Out-of-band'

        if max_power > -200:
            rx_powers.append(max_power)
            
            if tx_prob == "TxFundamental" and rx_prob == 'In-band':
                rx_colors.append(table_colors["in-in"])
            elif tx_prob != "TxFundamental" and rx_prob == 'In-band':
                rx_colors.append(table_colors["out-in"])
            elif tx_prob == "TxFundamental" and not(rx_prob == 'In-band'):
                rx_colors.append(table_colors["in-out"])
            elif tx_prob != "TxFundamental" and not(rx_prob == 'In-band'):
                rx_colors.append(table_colors["out-out"])
        else:
            rx_powers.append('<-200')
            rx_colors.append('white')
            
    all_colors.append(rx_colors)
    power_matrix.append(rx_powers)

emitapp.save_project()
emitapp.release_desktop()

def create_scenario_view(emis, colors, tx_radios, rx_radios):
    """Create a scenario matrix-like table with the higher received
    power for each Tx-Rx radio combination. The colors
    used for the scenario matrix view are based on the interference type."""
    fig = go.Figure(data=[go.Table(
        header=dict(
            values=['<b>Tx/Rx</b>','<b>{}</b>'.format(tx_radios[0]),'<b>{}</b>'.format(tx_radios[1])],
            line_color='darkslategray',
            fill_color='grey',
            align=['left','center'],
            font=dict(color='white',size=16)
        ),
        cells=dict(
            values=[
                rx_radios,
                emis[0],
                emis[1]],
            line_color='darkslategray',
            fill_color=['white',colors[0], colors[1]],
            align = ['left', 'center'],
            height = 25,
            font = dict(
                color = ['darkslategray','black'],
                size = 15)
        )
    )])
    fig.update_layout(
        title=dict(
            text='Interference Type Classification',
            font=dict(color='darkslategray',size=20),
            x = 0.5
        ),
        width = 600
        )
    fig.show()

def create_legend_table():    
    """Create a table showing the interference types."""
    classifications = ['In-band/In-band', 'Out-of-band/In-band',
        'In-band/Out-of-band', 'Out-of-band/Out-of-band']
    fig = go.Figure(data=[go.Table(
        header=dict(
            values=['<b>Interference Type (Source/Victim)</b>'],
            line_color='darkslategray',
            fill_color=header_color,
            align=['center'],
            font=dict(color='white',size=16)
        ),
        cells=dict(
            values=[classifications],
            line_color='darkslategray',
            fill_color= [[table_colors['in-in'], table_colors['out-in'], table_colors['in-out'], table_colors['out-out']]],
            align = ['center'],
            height = 25,
            font = dict(
                color = ['darkslategray','black'],
                size = 15)
        )
    )])
    fig.update_layout(
        title=dict(
            text='Interference Type Classification',
            font=dict(color='darkslategray',size=20),
            x = 0.5
        ),
        width = 600
        )
    fig.show()

# Create a scenario view for all the interference types
create_scenario_view(power_matrix, all_colors, tx_radios, rx_radios)

# Create a legend for the interference types
create_legend_table()