"""
EMIT: Compute required channel separation
-------------------------------------------
This example shows how you can use PyAEDT to open an AEDT project with
an EMIT design and analyze the results to determine the required channel
separation for overlapping bands. 
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
required_packages = ['plotly', 'tqdm', 'matplotlib', 'numpy']
for package in required_packages:
    if package not in installed_packages:
        install(package)

# Import required modules
import plotly.graph_objects as go
from tqdm.notebook import tqdm
    
from matplotlib import pyplot as plt
plt.ion() # enables interactive mode so plots show immediately
plt.show()
import numpy as np

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
# Create and connect EMIT components
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Set up the scenario with radios connected to antennas

def addAndConnectRadio(radio_name, schematic_name=""):
    """Add a radio from the EMIT library and connect
    it to an antenna.
    Returns: 
        Instance of the radio.
    Argments:
        radio_name - String name of the EMIT library radio
            to add.
        schematic_name - Name that appears in the schematic.
    """
    rad = emitapp.modeler.components.create_component(radio_name, schematic_name)
    ant = emitapp.modeler.components.create_component("Antenna")
    if rad and ant:
        ant.move_and_connect_to(rad)
    return rad

# Add three systems to the project
bluetooth = addAndConnectRadio("Bluetooth Low Energy (LE)", "Bluetooth")
gps = addAndConnectRadio("GPS Receiver", "GPS")
wifi = addAndConnectRadio("WiFi - 802.11-2012", "WiFi")

###############################################################################
# Configure the radios
# ~~~~~~~~~~~~~~~~~~~~
# Enable the HR-DSSS bands for the wifi radio and set the power level
# for all transmit bands to simulate coupling.
def setBandPowerLevel(band, power):
    """Set the power of the fundamental for the given band.
    Arguments:
        band: Band being configured.
        power: Peak amplitude of the fundamental [dBm].
    """
    prop_list = { "FundamentalAmplitude": power}
    for child in band.children:
        if child.props["Type"] == "TxSpectralProfNode":
            child._set_prop_value(prop_list)
            return # only one Tx Spectral Profile per Band
        
def setChannelSampling(radio, percentage):
    """Set the channel sampling for the radio.
    Arguments:
        radio: Radio to modify.
        percentage: Percentage of channels to sample for the analysis.
    """
    sampling = radio.get_prop_nodes({"Type": "SamplingNode"})[0]
    sampling._set_prop_value({
            "SpecifyPercentage": "true", 
            "PercentageChannels": "{}".format(percentage)
            })
        
# Enable the HR-DSSS wifi band, reduce
# its transmit power, and reduce its sampling
setChannelSampling(wifi, 50)
for band in wifi.bands():
    if "HR-DSSS" in band.node_name:
        band.enabled=True
        setBandPowerLevel(band, "-50")

# Reduce the bluetooth transmit power
setChannelSampling(bluetooth, 50)
for band in bluetooth.bands():
    setBandPowerLevel(band, "-50")
    
###############################################################################
# Load the results set
# ~~~~~~~~~~~~~~~~~~~~
# Create a results revision and load it for analysis

rev = emitapp.analyze()
emitapp._load_revision(rev.path)
modeRx = emitapp.tx_rx_mode().rx
modeTx = emitapp.tx_rx_mode().tx
modeEmi = emitapp.result_type().emi

def get_rx_bands(rx_radio):
    """Return a list of all Rx bands in a given radio.
    Returns:
        List of ("Rx Radio Name", "Rx Band Name") tuples.
    """
    bands = emitapp.results.get_band_names(rx_radio, modeRx)
    return [(rx_radio, band) for band in bands]

def overlapping_tx_bands(rx_band):
    """Return a list of all Tx bands overlapping a given Rx band.
    Returns:
       List of ("Tx Radio Name", "Tx Band Name") tuples.
    Argments:
       rx_band - The Rx band, given as a tuple: ("Rx Radio Name", "Rx Band Name").
    """
    overlapping = []
    rx_frequencies = emitapp.results.get_active_frequencies(
        rx_band[0], rx_band[1], modeRx
    )
    if len(rx_frequencies) < 1:
        return overlapping
    rx_start = min(rx_frequencies)
    rx_stop = max(rx_frequencies)
    for tx_radio in emitapp.results.get_radio_names(modeTx):
        if tx_radio == rx_band[0]:
            # skip self interaction
            continue        
        for tx_band in emitapp.results.get_band_names(tx_radio, modeTx):
            tx_frequencies = emitapp.results.get_active_frequencies(
                tx_radio, tx_band, modeTx
            )
            tx_start = min(tx_frequencies)
            tx_stop = max(tx_frequencies)

            def fuzzy_in_range(val, range_start, range_stop):
                return (
                    (val >= range_start and val <= range_stop)
                    or abs(val - range_start) < 1.0
                    or abs(val - range_stop) < 1.0
                )

            if (
                fuzzy_in_range(tx_start, rx_start, rx_stop)
                or fuzzy_in_range(tx_stop, rx_start, rx_stop)
                or fuzzy_in_range(rx_start, tx_start, tx_stop)
                or fuzzy_in_range(rx_stop, tx_start, tx_stop)
            ):
                overlapping.append((tx_radio, tx_band))
    return overlapping

###############################################################################
# Iterate over all the receivers
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Iterates over each of the receivers in the project and finds any transmit
# bands that contain overlapping channel frequencies.
overlapping = []
for rx_radio in emitapp.results.get_radio_names(modeRx):
    print("Potential in-band issues for Rx Radio: {}".format(rx_radio))
    for rx_band in get_rx_bands(rx_radio):
        tx_bands = overlapping_tx_bands(rx_band)
        if len(tx_bands) < 1:
            print('    Rx Band "{}" has no overlapping Tx Bands'.format(rx_band[1]))
            continue
        print(
            '    Rx Band "{}" has the following overlapping Tx Bands:'.format(rx_band[1])
        )
        for tx_band in tx_bands:
            overlapping.append((rx_band, tx_band))
            print('        {}'.format(tx_band))

###############################################################################
# Print a list of overlapping bands
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Prints a list of overlapping receivers and bands
print(overlapping[0][0])

###############################################################################
# Analyze the results
# ~~~~~~~~~~~~~~~~~~~~~~~~  
# Consider any EMI margin of 0dB or greater an interference issue    
verbose = False    
threshold = 0. 

def minimum_tx_channel_separation(rx_band, tx_band, emi_threshold):
    """Return the minimum separation that the Tx must be operated for interference-free
    operation of the Rx.
    Returns:
        The separation in MHz.
    Arguments:
        rx_band - The Rx band, given as a tuple: ("Rx Radio Name", "Rx Band Name").
        tx_band - The Tx band, given as a tuple: ("Tx Radio Name", "Tx Band Name").
        emi_threshold - Tx channel separation will be determined such that the EMI
        margin will not be at or above this level.
    """
    domain = Interaction_Domain()

    domain.set_receiver(rx_band[0], rx_band[1], 0.0)
    radTx = []
    bandTx = []
    chanTx = []
    radTx.append(tx_band[0])
    bandTx.append(tx_band[1])
    chanTx.append(0.0)
    domain.set_interferers(radTx, bandTx, chanTx)
    
    interaction = rev.run(domain)
    worst = interaction.get_worst_instance(modeEmi)
    # If the worst case for the band-pair is below the EMI limit, then
    # there are no interference issues and no offset is required.
    if worst.has_valid_values():
        emi = worst.get_value(modeEmi)
        if emi < emi_threshold:
            return 0.0
    # Assess each Rx channel and see how close the Tx can be tuned while
    # keeping the EMI below the threshold.
    rx_frequencies = emitapp.results.get_active_frequencies(
        rx_band[0], rx_band[1], modeRx
    )
    rx_channel_count = len(rx_frequencies)
    tx_frequencies = emitapp.results.get_active_frequencies(
        tx_band[0], tx_band[1], modeTx
    )
    tx_channel_count = len(tx_frequencies)
    chpair = domain
    offset_by_rx_freq = {}
    for rx_frequency in rx_frequencies:
        required_offset = 0.0
        chpair.set_receiver(rx_band[0], rx_band[1], rx_frequency)
        for tx_frequency in tx_frequencies:
            chanTx = []
            chanTx.append(tx_frequency)
            chpair.set_interferers(radTx, bandTx, chanTx)
            chpair_interaction = rev.run(chpair)
            chpair_result = chpair_interaction.get_worst_instance(modeEmi)
            if chpair_result.has_valid_values():
                emi = chpair_result.get_value(modeEmi)
            else:
                emi = 300.0
            if emi >= emi_threshold:
                current_offset = abs(tx_frequency - rx_frequency)
                if current_offset > required_offset and verbose:
                    print(
                        "Interference between Tx {} and Rx {} is {}".format(
                            tx_frequency, rx_frequency, emi
                        )
                    )
                required_offset = max(required_offset, current_offset)
        offset_by_rx_freq[rx_frequency / 1.e6] = required_offset / 1.e6
    return offset_by_rx_freq

separation_results = []


###############################################################################
# Plot the channel separation data
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# For each overlapping transmit/receive band combination, plot the required
# separation for each channel.
num=1 # current figure number
for rx_band, tx_band in tqdm(overlapping[1:]):
    tx_frequencies = emitapp.results.get_active_frequencies(tx_band[0], tx_band[1], modeTx)
    rx_frequencies = emitapp.results.get_active_frequencies(rx_band[0], rx_band[1], modeRx)
    print('Rx:')
    print('    Radio:', rx_band[0])
    print('    Band:', rx_band[1])
    print('    Channels: {} [{}, {}]'.format(len(rx_frequencies), min(rx_frequencies), max(rx_frequencies)))
    print('Tx:')
    print('    Radio:', tx_band[0])
    print('    Band:', tx_band[1])
    print('    Channels: {} [{}, {}]'.format(len(tx_frequencies), min(tx_frequencies), max(tx_frequencies)))
    channel_pairs = len(tx_frequencies)*len(rx_frequencies)
    print('Channel pairs: ', channel_pairs)

    if (channel_pairs > 10000):
        print('--- Skipping large band pair ---')
        continue
    
    separation = minimum_tx_channel_separation(rx_band, tx_band, threshold)
   
    rx_separation_pairs = sorted(separation.items())
    x, y = zip(*rx_separation_pairs)
    plt.figure(num)
    num=num+1
    plt.plot(x, y, 'bo')
    plt.xlabel('Rx Channel (MHz)')
    plt.ylabel('Tx Separation (MHz)')
    plt.title('Separation for {} and {}'.format(rx_band, tx_band))
    plt.grid()
    plt.draw()
    plt.pause(0.001) # needed to allow GUI events to occur
    separation_results.append((rx_band, tx_band, max(y)))

def remove_duplicates(a_list):
    """Removes duplicate values from a list
    Returns:
        A list with duplicate values removed
    Arguments: 
        a_list - list of tuples
    """
    ret = []
    for a in a_list:
        if a not in ret:
            ret.append(a)
    return ret

def show_separation_table(separation_results, title='In-band Separation (MHz)'):
    """Creates a scenario matrix like table to display the maximum
    channel separate required for each transmit/receive band combination.
    Arguments: 
        separation_results - tuple of {Rx_Band, Tx_Band, max_channel_separation}
        title - title of the table
    """
    rx_bands = remove_duplicates([rx_band for rx_band, tx_band, sep in separation_results])
    tx_bands = remove_duplicates([tx_band for rx_band, tx_band, sep in separation_results])
    
    header_values = ['<b>Tx / Rx</b>']
    header_values.extend(rx_bands)

    def get_separation(rx_band, tx_band):
        for rxb, txb, sep in separation_results:
            if txb==tx_band and rxb==rx_band:
                return sep
        return 'N/A'
    
    rows = []
    colors = []
    for tx_band in tx_bands:
        row = []
        color = []
        for rx_band in rx_bands:
            sep = get_separation(rx_band, tx_band)
            row.append(sep)
            if isinstance(sep, float):
                if sep <= 1.:
                    color.append('yellow')
                elif sep > 1.:
                    color.append('orange')
                else:
                    color.append('white')
            else:
                color.append('white')
        rows.append(row)
        colors.append(color)
        
    values = [tx_bands]
    values.extend(rows)
    
    val_colors = [['white' for _ in tx_bands]]
    val_colors.extend(colors)
    
    fig = go.Figure(data=[go.Table(
        header=dict(
            values=header_values,
            line_color='darkslategray',
            fill_color='grey',
            align=['left','center'],
            font=dict(color='darkslategray',size=16)
        ),
        cells=dict(
            values=values,
            line_color='darkslategray',
            fill_color=val_colors,
            align = ['left', 'center'],
            font = dict(
                color = ['darkslategray','black'],
                size = 15)
        )
    )])
    fig.update_layout(
        title=dict(
            text=title,
            font=dict(color='darkslategray',size=20),
            x = 0.5
        ),
        width = 800
        )
    fig.show()
    
###############################################################################
# Show results for Bluetooth receiver
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Minimum required channel separation for Bluetooth receiver
rx2_results = [x for x in separation_results if 'Bluetooth' in x[1][0]]

# Create a table
show_separation_table(rx2_results, title='Separation for Bluetooth and WiFi (MHz)')

# Need this to ensure plots don't close
input("Press [enter] to continue.")

###############################################################################
# Save project and close AEDT
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~
# After the simulation completes, you can close AEDT or release it using the
# :func:`pyaedt.Desktop.force_close_desktop` method.
# All methods provide for saving the project before closing.

emitapp.save_project()
emitapp.release_desktop(close_projects=True, close_desktop=True)