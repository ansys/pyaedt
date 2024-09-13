"""
Design a lumped element filter
------------------------------
This example shows how to use PyAEDT to use the ``FilterSolutions`` module to design and 
visualize the frequency response of a band-pass Butterworth filter. 
"""

###############################################################################
# Perform required imports
# ~~~~~~~~~~~~~~~~~~~~~~~~
# Perform required imports.

import ansys.aedt.core
import ansys.aedt.core.filtersolutions_core.attributes
from ansys.aedt.core.filtersolutions_core.attributes import FilterType, FilterClass, FilterImplementation
from ansys.aedt.core.filtersolutions_core.ideal_response import FrequencyResponseColumn
from ansys.aedt.core.filtersolutions_core.export_to_aedt import PartLibraries, ExportFormat
import matplotlib.pyplot as plt

###############################################################################
# Create the lumped design
# ~~~~~~~~~~~~~~~~~~~~~~~~
# Create a lumped element filter design and assign the class, type, frequency, and order.
design = ansys.aedt.core.FilterSolutions(version="2025.1", implementation_type= FilterImplementation.LUMPED) 
design.attributes.filter_class = FilterClass.BAND_PASS
design.attributes.filter_type = FilterType.BUTTERWORTH
design.attributes.pass_band_center_frequency = "1G"
design.attributes.pass_band_width_frequency = "500M"
design.attributes.filter_order = 5
##############################################################################
# Plot the frequency response of the filter
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Plot the frequency response of the filter without any transmission zeros.

freq, mag_db = design.ideal_response.frequency_response(FrequencyResponseColumn.MAGNITUDE_DB)
plt.plot(freq, mag_db, linewidth=2.0, label="Without Tx Zero")
def format_plot():
    plt.xlabel("Frequency (Hz)")
    plt.ylabel("Magnitude S21 (dB)")
    plt.title("Ideal Frequency Response")
    plt.xscale("log")
    plt.legend()
    plt.grid()
format_plot()
plt.show()

##############################################################################
# Add a transmission zero to the filter design
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Add a transmission zeros that yields nulls separated by 2 times the pass band width (1 GHz).
# Plot the frequency response of the filter with the transmission zero.

design.transmission_zeros_ratio.append_row("2.0")
freq_with_zero, mag_db_with_zero = design.ideal_response.frequency_response(FrequencyResponseColumn.MAGNITUDE_DB)
plt.plot(freq, mag_db, linewidth=2.0, label="Without Tx Zero")
plt.plot(freq_with_zero, mag_db_with_zero, linewidth=2.0, label="With Tx Zero")
format_plot()
plt.show()

##############################################################################
# Generate the netlist for the designed filter
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Generate and print the netlist for the designed filter with the added transmission zero to filter.
netlist = design.topology.circuit_response()
print("Netlist: \n", netlist)
