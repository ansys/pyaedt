"""
EMIT: Computes required channel separation
---------------------------
This example shows how you can use PyAEDT to open an AEDT project with
an EMIT design, and analyze the results to determine the required channel
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

# Check to see which python libraries have been installed
reqs = subprocess.check_output([sys.executable, '-m', 'pip', 'freeze'])
installed_packages = [r.decode().split('==')[0] for r in reqs.split()]

# Install required packages if they are not installed
def install(package): 
    subprocess.check_call([sys.executable, '-m', 'pip', 'install', package])

# Install any missing libraries
required_packages = ['tk', 'plotly', 'tqdm', 'matplotlib', 'numpy']
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
# Select the results file to load
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Select the result file to use for this analysis. The results do not
# need to be solved.
Tk().withdraw() # we don't want a full GUI, so keep the root window from appearing
filename = askdirectory() # show an "open" dialog box and return the path
api.load_project(filename)
engine = api.get_engine()

def get_rx_bands(rx_radio):
    """Return a list of all Rx bands in a given radio.
    Returns:
        List of ("Rx Radio Name", "Rx Band Name") tuples.
    """
    bands = api.get_band_names(rx_radio, EmitApiPython.tx_rx_mode.rx)
    return [(rx_radio, band) for band in bands]

def overlapping_tx_bands(rx_band):
    """Return a list of all Tx Bands overlapping a given Rx band
    Returns:
       List of ("Tx Radio Name", "Tx Band Name") tuples
    Argments:
       rx_band - The Rx band, given as a tuple: ("Rx Radio Name", "Rx Band Name").
    """
    overlapping = []
    rx_frequencies = api.get_active_frequencies(
        rx_band[0], rx_band[1], EmitApiPython.tx_rx_mode.rx
    )
    if len(rx_frequencies) < 1:
        return overlapping
    rx_start = min(rx_frequencies)
    rx_stop = max(rx_frequencies)
    for tx_radio in api.get_radio_names(EmitApiPython.tx_rx_mode.tx):
        for tx_band in api.get_band_names(tx_radio, EmitApiPython.tx_rx_mode.tx):
            tx_frequencies = api.get_active_frequencies(
                tx_radio, tx_band, EmitApiPython.tx_rx_mode.tx
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
for rx_radio in api.get_radio_names(EmitApiPython.tx_rx_mode.rx):
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


def abbreviate(band, skip_radio=False):
    """Return an abbreviated name for the band and receiver
    Returns:
       List of ("Abbreviated Radio Name", "Abbreviated Band Name") tuples
    Argments:
       band - The Rx band, given as a tuple: ("Rx Radio Name", "Rx Band Name")
       skip_radio - if True, only returns the abbreviated band name.
    """
    radio_abbreviations = {'RF System RX - ARC-210-RT-1851A(C)':'RX1', 'RF System RX 2 - ARC-210-RT-1851A(C)':'RX2', 'RF System TX - ARC-210-RT-1851A(C)':'TX1'}
    band_abbreviations = {'Air Traffic Control':'ATC', 'Close Air Support':'CAS', 'Maritime':'MT', 'Military-Homeland Defense':'MHD', 'Land Mobile':'LM', ' - ':'-'}
    abbrev_radio = radio_abbreviations[band[0]]
    abbrev_band = band[1]
    for long, short in band_abbreviations.items():
        abbrev_band = abbrev_band.replace(long, short)
    if skip_radio:
        return abbrev_band
    else:
        return '{} / {}'.format(abbrev_radio, abbrev_band)

###############################################################################
# Print a list of overlapping bands
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Prints a list of overlapping receivers and bands
print(abbreviate(overlapping[0][0]))
print(abbreviate(overlapping[0][0], skip_radio=True))

###############################################################################
# Perform required imports
# ~~~~~~~~~~~~~~~~~~~~~~~~
# Perform required imports.
from tqdm.notebook import tqdm
    
from matplotlib import pyplot as plt
plt.ion() # enables interactive mode so plots show immediately
plt.show()
import numpy as np

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
    domain = EmitApiPython.InteractionDomain()

    domain.set_receiver(rx_band[0], rx_band[1], 0.0)
    radTx = []
    bandTx = []
    chanTx = []
    radTx.append(tx_band[0])
    bandTx.append(tx_band[1])
    chanTx.append(0.0)
    domain.set_interferers(radTx, bandTx, chanTx)
    interaction = engine.run(domain)
    worst = interaction.get_worst_instance(EmitApiPython.result_type.emi)
    # If the worst case for the band-pair is below the EMI limit, then
    # there are no interference issues and no offset is required.
    if worst.has_valid_values():
        emi = worst.get_value(EmitApiPython.result_type.emi)
        if emi < emi_threshold:
            return 0.0
    # Assess each Rx channel and see how close the Tx can be tuned while
    # keeping the EMI below the threshold.
    rx_frequencies = api.get_active_frequencies(
        rx_band[0], rx_band[1], EmitApiPython.tx_rx_mode.rx
    )
    rx_channel_count = len(rx_frequencies)
    tx_frequencies = api.get_active_frequencies(
        tx_band[0], tx_band[1], EmitApiPython.tx_rx_mode.tx
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
            chpair_result = interaction.get_instance(chpair)
            if chpair_result.has_valid_values():
                emi = chpair_result.get_value(EmitApiPython.result_type.emi)
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
for rx_band, tx_band in tqdm(overlapping[2:]):
    tx_frequencies = api.get_active_frequencies(tx_band[0], tx_band[1], EmitApiPython.tx_rx_mode.tx)
    rx_frequencies = api.get_active_frequencies(rx_band[0], rx_band[1], EmitApiPython.tx_rx_mode.rx)
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
    plt.title('Separation for {} and {}'.format(abbreviate(rx_band), abbreviate(tx_band)))
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
    rx_bands_abbrev = [abbreviate(r, skip_radio=True) for r in rx_bands]
    tx_bands = remove_duplicates([tx_band for rx_band, tx_band, sep in separation_results])
    tx_bands_abbrev = [abbreviate(t, skip_radio=True) for t in tx_bands]
    
    header_values = ['<b>Tx / Rx</b>']
    header_values.extend(rx_bands_abbrev)

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
        
    values = [tx_bands_abbrev]
    values.extend(rows)
    
    val_colors = [['white' for _ in tx_bands]]
    val_colors.extend(colors)
    
    fig = go.Figure(data=[go.Table(
        header=dict(
            values=header_values,
            line_color='darkslategray',
            fill_color='white',
            align=['left','center'],
            font=dict(color='darkslategray',size=16)
        ),
        cells=dict(
            values=values,
            line_color='darkslategray',
            #fill_color='white',
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
    
rx2_results = [x for x in separation_results if 'RX 2 -' in x[0][0]]

# Create a table
show_separation_table(rx2_results, title='Separation for RX 2 and TX 1 (MHz)')

# Need this to ensure plots don't close
input("Press [enter] to continue.")