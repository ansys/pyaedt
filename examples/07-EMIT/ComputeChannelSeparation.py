"""
EMIT: Compute required channel separation
-----------------------------------------
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
import subprocess
import pyaedt
from pyaedt import Emit
import pyaedt.emit_core.EmitConstants as econsts

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
plt.ion() # Enables interactive mode so plots show immediately
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

if desktop_version <= "2023.1":
    print("Warning: this example requires AEDT 2023.2 or later.")
    sys.exit()

d = pyaedt.launch_desktop(desktop_version, non_graphical, NewThread)
emitapp = Emit(pyaedt.generate_unique_project_name())

###############################################################################
# Create and connect EMIT components
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Set up the scenario with radios connected to antennas.

bluetooth, blue_ant = emitapp.modeler.components.create_radio_antenna("Bluetooth Low Energy (LE)", "Bluetooth")
gps, gps_ant = emitapp.modeler.components.create_radio_antenna("GPS Receiver", "GPS")
wifi, wifi_ant = emitapp.modeler.components.create_radio_antenna("WiFi - 802.11-2012", "WiFi")

###############################################################################
# Configure the radios
# ~~~~~~~~~~~~~~~~~~~~
# Enable the HR-DSSS bands for the wifi radio and set the power level
# for all transmit bands to simulate coupling.

wifi_sampling = wifi.get_sampling()
wifi_sampling.set_channel_sampling(percentage=25)
for band in wifi.bands():
    if "HR-DSSS" in band.node_name:
        band.enabled=True
        band.set_band_power_level(-50)

# Reduce the bluetooth transmit power
blue_sampling = bluetooth.get_sampling()
blue_sampling.set_channel_sampling(percentage=50)
for band in bluetooth.bands():
    band.set_band_power_level(-50)
    
###############################################################################
# Load the results set
# ~~~~~~~~~~~~~~~~~~~~
# Create a results revision and load it for analysis.

rev = emitapp.results.analyze()
modeRx = econsts.tx_rx_mode().rx
modeTx = econsts.tx_rx_mode().tx
modeEmi = econsts.result_type().emi
tx_interferer = econsts.interferer_type().transmitters

def get_rx_bands(rx_radio):
    """Return a list of all Rx bands in a given radio.
    Returns:
        List of ("Rx Radio Name", "Rx Band Name") tuples.
    """
    bands = rev.get_band_names(rx_radio, modeRx)
    return [(rx_radio, band) for band in bands]

def overlapping_tx_bands(rx_band):
    """Return a list of all Tx bands overlapping a given Rx band.
    Returns:
       List of ("Tx Radio Name", "Tx Band Name") tuples.
    Argments:
       rx_band: Rx band, given as a tuple ("Rx Radio Name", "Rx Band Name").
    """
    overlapping = []
    rx_frequencies = rev.get_active_frequencies(
        rx_band[0], rx_band[1], modeRx
    )
    if len(rx_frequencies) < 1:
        return overlapping
    rx_start = min(rx_frequencies)
    rx_stop = max(rx_frequencies)
    for tx_radio in rev.get_interferer_names(tx_interferer):
        if tx_radio == rx_band[0]:
            # skip self interaction
            continue        
        for tx_band in rev.get_band_names(tx_radio, modeTx):
            tx_frequencies = rev.get_active_frequencies(
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
for rx_radio in rev.get_receiver_names():
    print("Potential in-band issues for Rx Radio: {}".format(rx_radio))
    for rx_band in get_rx_bands(rx_radio):
        tx_bands = overlapping_tx_bands(rx_band)
        if len(tx_bands) < 1:
            print('    Rx Band "{}" has no overlapping Tx bands'.format(rx_band[1]))
            continue
        print(
            '    Rx band "{}" has the following overlapping Tx bands:'.format(rx_band[1])
        )
        for tx_band in tx_bands:
            overlapping.append((rx_band, tx_band))
            print('        {}'.format(tx_band))

###############################################################################
# Print a list of overlapping bands
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Prints a list of overlapping receivers and bands.
print(overlapping[0][0])

###############################################################################
# Analyze the results
# ~~~~~~~~~~~~~~~~~~~
# Consider any EMI margin of 0dB or greater an interference issue.

verbose = False    
threshold = 0. 

def minimum_tx_channel_separation(rx_band, tx_band, emi_threshold):
    """Return the minimum separation the Tx must be operated at for interference-free
    operation of the Rx.
    Returns:
        Separation in MHz.
    Arguments:
        rx_band: Rx band, given as a tuple: ("Rx Radio Name", "Rx Band Name").
        tx_band: Tx band, given as a tuple: ("Tx Radio Name", "Tx Band Name").
        emi_threshold: Tx channel separation to be determined such that the EMI
        margin is not at or above this level.
    """

    domain = emitapp.results.interaction_domain()
    domain.set_receiver(rx_band[0], rx_band[1])
    domain.set_interferer(tx_band[0], tx_band[1])

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
    # Freqs are used to set the domain, so they need to be in Hz
    rx_frequencies = rev.get_active_frequencies(
        rx_band[0], rx_band[1], modeRx, "Hz"
    )
    rx_channel_count = len(rx_frequencies)
    tx_frequencies = rev.get_active_frequencies(
        tx_band[0], tx_band[1], modeTx, "Hz"
    )
    tx_channel_count = len(tx_frequencies)
    chpair = domain
    offset_by_rx_freq = {}
    for rx_frequency in rx_frequencies:
        required_offset = 0.0
        chpair.set_receiver(rx_band[0], rx_band[1], rx_frequency)
        for tx_frequency in tx_frequencies:
            chpair.set_interferer(tx_band[0], tx_band[1], tx_frequency)
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
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# For each overlapping transmit/receive band combination, plot the required
# separation for each channel.
num=1 # Current figure number
for rx_band, tx_band in tqdm(overlapping[1:]):
    tx_frequencies = rev.get_active_frequencies(tx_band[0], tx_band[1], modeTx)
    rx_frequencies = rev.get_active_frequencies(rx_band[0], rx_band[1], modeRx)
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
    """Remove duplicate values from a list.
    Returns:
        List with duplicate values removed.
        a_list: List of tuples.
    """
    ret = []
    for a in a_list:
        if a not in ret:
            ret.append(a)
    return ret

def show_separation_table(separation_results, title='In-band Separation (MHz)'):
    """Create a scenario matrix-like table to display the maximum
    channel separate required for each transmit/receive band combination.
    Arguments: 
        separation_results: Tuple of {Rx_Band, Tx_Band, max_channel_separation}.
        title: Title of the table.
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
# Show results for bluetooth receiver
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Show the minimum required channel separation for the Bluetooth receiver.
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