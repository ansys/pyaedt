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
import pyaedt
from pyaedt import Emit
from pyaedt.emit import Interaction_Domain
from pyaedt.emit import Revision
from pyaedt.emit import Result
from pyaedt.modeler.circuits.PrimitivesEmit import EmitComponent

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

# Import required modules
import plotly.graph_objects as go

###############################################################################
# Set non-graphical mode
# ~~~~~~~~~~~~~~~~~~~~~~
# Set non-graphical mode. ``"PYAEDT_NON_GRAPHICAL"``` is needed to generate
# documentation only.
# You can set ``non_graphical`` either to ``True`` or ``False``.
# The ``NewThread`` Boolean variable defines whether to create a new instance
# of AEDT or try to connect to existing instance of it if one is available.

non_graphical = os.getenv("PYAEDT_NON_GRAPHICAL", "False").lower() in ("true", "1", "t")
NewThread = False
desktop_version = "2023.2"

###############################################################################
# Launch AEDT with EMIT
# ~~~~~~~~~~~~~~~~~~~~~
# Launch AEDT with EMIT. The ``Desktop`` class initializes AEDT and starts it
# on the specified version and in the specified graphical mode.

d = pyaedt.launch_desktop(desktop_version, non_graphical, NewThread)
emitapp = Emit(pyaedt.generate_unique_project_name())

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
# Create and connect EMIT components
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Set up the scenario with radios connected to antennas

def addAndConnectRadio(radio_name, schematic_name=""):
    """Adds a radio from the EMIT library and connects
    it to an antenna
    Returns: 
        instance of the radio
    Argments:
        radio_name - string name of the EMIT library radio
            to add
        schematic_name - name that appears in the schematic
    """
    rad = emitapp.modeler.components.create_component(radio_name, schematic_name)
    ant = emitapp.modeler.components.create_component("Antenna")
    if rad and ant:
        ant.move_and_connect_to(rad)
    return rad

# Add 3 systems to the project
bluetooth = addAndConnectRadio("Bluetooth Low Energy (LE)", "Bluetooth")
gps = addAndConnectRadio("GPS Receiver", "GPS")
wifi = addAndConnectRadio("WiFi - 802.11-2012", "WiFi")

###############################################################################
# Configure the radios
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Enable the HR-DSSS bands for the WiFi Radio and set the power level
# for all Transmit bands to -20 dBm
def setBandPowerLevel(band, power):
    """Set the power of the fundamental for the given band
    Arguments:
        band: the Band being configured
        power: the peak amplitude of the fundamental [dBm]
    """
    prop_list = { "FundamentalAmplitude": power}
    for child in band.children:
        if child.props["Type"] == "TxSpectralProfNode":
            child._set_prop_value(prop_list)
            return # only one Tx Spectral Profile per Band
        
bands = wifi.bands()
for band in bands:
    if "HR-DSSS" in band.node_name:
        if "Ch 1-13" in band.node_name:
            band.enabled=True
            setBandPowerLevel(band, "-20")

# Reduce the Bluetooth tranmit power
bands = bluetooth.bands()
for band in bands:
    setBandPowerLevel(band, "-20")

# Configure the first Rx Band in the GPS Rx to have 0 dBm Susc
def setProtectionBand(radio):
    """Sets susceptibility of the Rx Band to 0 dBm
    for all frequencies
    Arguments:
        radio: the radio to be modified
    """
    bands = radio.bands()
    prop_list = {
                "InBandSensitivity": "0",
                "SnrAtSensitivity": "0",
                "RxMaxAttenuation": "0"
                }
    for band in bands:
        for child in band.children:
            if child.props["Type"] == "RxSusceptibilityProfNode":
                child._set_prop_value(prop_list)
                break # only one Rx Spectral Profile per Band

def getRadioNode(radio_name):
    """Returns the radio node that matches the
    given radio name
    Arguments:
        radio_name: string name of the radio
    Returns: instance of the radio
    """
    if gps.name == radio_name:
        radio = gps
    elif bluetooth.name == radio_name:
        radio = bluetooth
    else:
        radio = wifi
    return radio
setProtectionBand(bluetooth)            
setProtectionBand(gps)
setProtectionBand(wifi)

bands = gps.bands()
for band in bands:
    for child in band.children:
        if "L2 P(Y)" in band.node_name:
            band.enabled=True
        else:
            band.enabled=False

    
###############################################################################
# Load the results set
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Create a new results revision and load it for analysis

rev = emitapp.analyze()
emitapp._load_revision(rev.path)
modeRx = emitapp.tx_rx_mode().rx
modeTx = emitapp.tx_rx_mode().tx
modeEmi = emitapp.result_type().emi

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
            values=['<b>Tx/Rx</b>','<b>{}</b>'.format(tx_radios[0]),'<b>{}</b>'.format(tx_radios[1])],
            line_color='darkslategray',
            fill_color=header_color,
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

rx_radios = emitapp.results.get_radio_names(modeRx)
tx_radios = emitapp.results.get_radio_names(modeTx)
domain = Interaction_Domain()

###############################################################################
# Iterate over all the radios
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Iterates over all the transmitters and receivers and computes the power
# at the input to each receiver due to each of the transmitters. Computes
# which, if any, protection levels are exceeded by these power levels.
emi_matrix=[]
all_colors=[]
for tx_radio in tx_radios:
    rx_emis = []
    rx_colors = []
    for rx_radio in rx_radios:
        if tx_radio == rx_radio:
            # skip self-interaction
            rx_emis.append('N/A')
            rx_colors.append('green')
            continue
        print("Power Thresholds for {tx} vs {rx}".format(tx=tx_radio,rx=rx_radio))
        for rx_band in emitapp.results.get_band_names(rx_radio, modeRx): 
            # if "L2 P(Y)" not in rx_band:
            #     # skip 'normal' Rx bands
            #     continue
            # check for enabled Bands
            cur_rx_radio = getRadioNode(rx_radio)
            bands = cur_rx_radio.bands()
            for band in bands:
                if rx_band in band.node_name:
                    bandEnabled = band.enabled
                    break
            if not bandEnabled:
                continue
            # get enabled tx band
            cur_tx_radio = getRadioNode(tx_radio)
            bands = cur_tx_radio.bands()
            for band in bands:
                if band.enabled:
                    tx_band = band.node_name
                    break
            for tx_band_shortname in emitapp.results.get_band_names(tx_radio, modeTx): 
                if tx_band_shortname in tx_band:
                    break

            # find the highest power level at the Rx input due
            # to each Tx Radio
            domain.set_receiver(rx_radio, rx_band)
            domain.set_interferers([tx_radio],[tx_band_shortname])
            interaction = rev.run(domain)
            worst = interaction.get_worst_instance(modeEmi)

            # If the worst case for the band-pair is below the EMI limit, then
            # there are no interference issues and no offset is required.
            if worst.has_valid_values():
                emi = worst.get_value(modeEmi)
                rx_emis.append(emi)
                if (emi > damage_threshold):
                    rx_colors.append('red')
                    print("{} may damage {}".format(tx_radio, rx_radio))
                elif (emi > overload_threshold):
                    rx_colors.append('orange')
                    print("{} may overload {}".format(tx_radio, rx_radio))
                elif (emi > intermod_threshold):
                    rx_colors.append('yellow')
                    print("{} may cause intermodulation in {}".format(tx_radio, rx_radio))
                else:
                    rx_colors.append('green')
                    print("{} may cause desensitization in {}".format(tx_radio, rx_radio))
            else:
                rx_emis.append(-200)
                rx_colors.append('red')
    all_colors.append(rx_colors)
    emi_matrix.append(rx_emis)

# create a Scenario Matrix like view for the Protection Levels
create_scenario_view(emi_matrix, all_colors, tx_radios, rx_radios)

# create a legend for the Protection Levels
create_legend_table()

###############################################################################
# Save project and close AEDT
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~
# After the simulation completes, you can close AEDT or release it using the
# :func:`pyaedt.Desktop.force_close_desktop` method.
# All methods provide for saving the project before closing.

emitapp.save_project()
emitapp.release_desktop(close_projects=True, close_desktop=True)