"""
EMIT: Computes receiver protection levels
---------------------------
This example shows how you can use PyAEDT to open an AEDT project with
an EMIT design, and analyze the results to determine if the received 
power at the input to each receiver exceeds the specified protection
levels. 
"""
###############################################################################
# Perform required imports
# ~~~~~~~~~~~~~~~~~~~~~~~~
# Perform required imports.
import os
import sys
import time
import subprocess

# Check to see which python libraries have been installed
reqs = subprocess.check_output([sys.executable, '-m', 'pip', 'freeze'])
installed_packages = [r.decode().split('==')[0] for r in reqs.split()]

# Install required packages if they are not installed
def install(package): 
    subprocess.check_call([sys.executable, '-m', 'pip', 'install', package])

# Install any missing libraries
required_packages = ['tk', 'plotly']
for package in required_packages:
    if package not in installed_packages:
        install(package)

# Import required modules
from tkinter import Tk
from tkinter.filedialog import askdirectory
import plotly.graph_objects as go

sys.path.append("D:\\AnsysDev\\workspace3\\build_output\\64Release\\Delcross")
# Get AnsysEM installation directory
install_dir = os.getenv("ANSYSEM_ROOT231")
emit_dir = os.path.join(install_dir, "Delcross")
sys.path.append(emit_dir)
import EmitApiPython

# load the API and print the version and copyright info
api = EmitApiPython.EmitApi()

###############################################################################
# Specify the protection levels
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# The protection levels are specified in dBm
# If the damage threshold is exceeded, permanent damage to the receiver front
# end may occur.
# Exceeding the overload threshold severely densensitizes the receiver.
# Exceeding the intermod threshold may drive the victim receiver into non-
# linear operation where it operates as a mixer. 
# Exceeding the desense threshold reduces the signal-to-noise ratio and can 
# reduce the maximum range, maximum bandwidth, and/or the overall link quality.
header_color = 'grey'
damage_threshold = 30
overload_threshold = -4
intermod_threshold = -30
desense_threshold = -104

###############################################################################
# Select the results file to load
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Select the result file to use for this analysis. The results do not
# need to be solved.
Tk().withdraw() # we don't want a full GUI, so keep the root window from appearing
filename = askdirectory() # show an "open" dialog box and return the path
api.load_project(filename)

###############################################################################
# Generate a legend
# ~~~~~~~~~~~~~~~~~
# Defines the thresholds and colors used to display the results of 
# the protection level analysis.
def create_legend_table():    
    """Creates a table showing the defined protection levels"""
    protectionLevels = ['>{} dBm'.format(damage_threshold), '>{} dBm'.format(overload_threshold),
        '>{} dBm'.format(intermod_threshold), '>{} dBm'.format(desense_threshold)]
    fig = go.Figure(data=[go.Table(
        header=dict(
            values=['<b>Interference</b>','<b>Power Level Threshold</b>'],
            line_color='darkslategray',
            fill_color=header_color,
            align=['left','center'],
            font=dict(color='white',size=16)
        ),
        cells=dict(
            values=[['Damage','Overload','Intermodulation','Clear'], protectionLevels],
            line_color='darkslategray',
            fill_color=['white',['red','orange','yellow','green']],
            align = ['left', 'center'],
            font = dict(
                color = ['darkslategray','black'],
                size = 15)
        )
    )])
    fig.update_layout(
        title=dict(
            text='Protection Levels (dBm)',
            font=dict(color='darkslategray',size=20),
            x = 0.5
        ),
        width = 600
        )
    fig.show()

###############################################################################
# Create a scenario matrix view
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Creates a scenario matrix view with the transmitters defined across the top
# and receivers down the left-most column. The power at the input to each
# receiver is shown in each cell of the matrix and color-coded based on the
# protection level thresholds defined.
def create_scenario_view(emis, colors, tx_radios, rx_radios):
    """Creates a Scenario Matrix like table with the higher received
    power for each Tx-Rx radio combination. The colors
    used for the Scenario Matrix view are based on the highest 
    protection level that the received power exceeds."""
    fig = go.Figure(data=[go.Table(
        header=dict(
            values=['<b>Tx/Rx</b>','<b>{}</b>'.format(tx_radios[0])],
            line_color='darkslategray',
            fill_color=header_color,
            align=['left','center'],
            font=dict(color='white',size=16)
        ),
        cells=dict(
            values=[
                rx_radios,
                emis],
            line_color='darkslategray',
            fill_color=['white',colors],
            align = ['left', 'center'],
            font = dict(
                color = ['darkslategray','black'],
                size = 15)
        )
    )])
    fig.update_layout(
        title=dict(
            text='Protection Levels (dBm)',
            font=dict(color='darkslategray',size=20),
            x = 0.5
        ),
        width = 600
        )

    fig.show()

###############################################################################
# Get all the radios in the project
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Generates lists of all the transmitters and receivers in the project.
rx_radios = api.get_radio_names(EmitApiPython.tx_rx_mode.rx)
tx_radios = api.get_radio_names(EmitApiPython.tx_rx_mode.tx)
engine = api.get_engine()
domain = EmitApiPython.InteractionDomain()

###############################################################################
# Iterate over all the radios
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Iterates over all the transmitters and receivers and computes the power
# at the input to each receiver due to each of the transmitters. Computes
# which, if any, protection levels are exceeded by these power levels.
all_rx_emis=[]
all_colors=[]
for rx_radio in rx_radios:
    for tx_radio in tx_radios:
        print("Power Thresholds for {tx} vs {rx}".format(tx=tx_radio,rx=rx_radio))
        for rx_band in api.get_band_names(rx_radio, EmitApiPython.tx_rx_mode.rx): 
            if "Protection Band" not in rx_band:
                # skip 'normal' Rx bands
                continue
            # find the highest power level at the Rx input due
            # to each Tx Radio
            domain.rx_radio_name = rx_radio
            domain.rx_band_name = rx_band
            domain.tx_radio_name = tx_radio
            interaction = engine.run(domain)
            worst = interaction.get_worst_instance(EmitApiPython.result_type.emi)

            # If the worst case for the band-pair is below the EMI limit, then
            # there are no interference issues and no offset is required.
            emi = worst.get_value(EmitApiPython.result_type.emi)
            all_rx_emis.append(emi)
            if (emi > damage_threshold):
                all_colors.append('red')
                print("{} may damage {}".format(tx_radio, rx_radio))
            elif (emi > overload_threshold):
                all_colors.append('orange')
                print("{} may overload {}".format(tx_radio, rx_radio))
            elif (emi > intermod_threshold):
                all_colors.append('yellow')
                print("{} may cause intermodulation in {}".format(tx_radio, rx_radio))
            else:
                all_colors.append('green')
                print("{} may cause desensitization in {}".format(tx_radio, rx_radio))

# create a Scenario Matrix like view for the Protection Levels
create_scenario_view(all_rx_emis, all_colors, tx_radios, rx_radios)

# create a legend for the Protection Levels
create_legend_table()
