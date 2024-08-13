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

import pyaedt
import pyaedt.filtersolutions_core.attributes
from pyaedt.filtersolutions_core.attributes import FilterType, FilterClass, FilterImplementation
from pyaedt.filtersolutions_core.ideal_response import FrequencyResponseColumn
#import matplotlib.pyplot as plt
from pyaedt.filtersolutions_core.export_to_aedt import ExportFormat,PartLibraries
from pyaedt.filtersolutions_core.optimization_goals_table import OptimizationGoalParameter


###############################################################################
# Create the lumped design
# ~~~~~~~~~~~~~~~~~~~~~~~~
# Create a lumped element filter design and assign the class, type, frequency, and order.
design = pyaedt.FilterSolutions(version="2025.1", implementation_type= FilterImplementation.LUMPED)
design.export_to_aedt.part_libraries = PartLibraries.MODELITHICS
print(design.export_to_aedt.part_libraries)
design.export_to_aedt.load_modelithics_models()

print(design.export_to_aedt.modelithics_resistor_list_count)
design.export_to_aedt.modelithics_resistor_add_family("AVX -> RES_AVX_0402_001 UBR0402")
design.export_to_aedt.modelithics_resistor_add_family("Vishay -> RES_VIS_0603_001 D11")
print(design.export_to_aedt.modelithics_resistor_family_list_count)
design.export_to_aedt.modelithics_inductor_selection = "AVX -> IND_AVX_0201_101 Accu-L"
design.export_to_aedt.modelithics_inductor_add_family("AVX -> IND_AVX_0402_101 AccuL")
design.export_to_aedt.modelithics_inductor_add_family("Wurth -> IND_WTH_0603_003 WE-KI")
design.export_to_aedt.modelithics_inductor_remove_family("Wurth -> IND_WTH_0603_003 WE-KI")
print(design.export_to_aedt.modelithics_inductor_selection)
for i in range(design.export_to_aedt.modelithics_inductor_family_list_count):
    print(design.export_to_aedt.modelithics_inductor_family_list(i))
print(design.export_to_aedt.modelithics_inductor_family_list_count)
#design.export_to_aedt.interconnect_geometry_optimization_enabled = False
#design.export_to_aedt.modelithics_inductor_add_family("jj")
#print(design.export_to_aedt.modelithics_inductor_family_list()) 
#.export_to_aedt.overwrite_design_to_aedt(ExportFormat.DIRECT)

exit()

design.attributes.pass_band_center_frequency = "2G"  
#design.export_to_aedt.open_aedt_export()
#design.optimization_goals_table.set_design_goals()
design.export_to_aedt.schematic_name = "my_schematic"
print(design.export_to_aedt.schematic_name)
design.export_to_aedt.simulate_after_export_enabled = True
#design.export_to_aedt.overwrite_design_to_aedt(ExportFormat.DIRECT)
design.optimization_goals_table.adjust_goal_frequency("150 MHz")
print(design.optimization_goals_table.row(0)[OptimizationGoalParameter.LOWER_FREQUENCY.value])

print(design.optimization_goals_table.row_count)
design.optimization_goals_table.append_row("100 MHz", "2 GHz", "-3", ">", "dB(S(Port2,Port2))", "1", "Y")
#design.optimization_goals_table.save_goals(design, "c:\\goals.csv")
design.optimization_goals_table.clear_goal_entries()
design.optimization_goals_table.load_goals("c:\\goals.csv")

for row_index in range(design.optimization_goals_table.row_count):
    print(design.optimization_goals_table.row(row_index))
design.export_to_aedt.include_output_return_loss_s22_enabled = True
print(design.export_to_aedt.include_output_return_loss_s22_enabled)
design.export_to_aedt.part_libraries = PartLibraries.MODELITHICS
design.export_to_aedt.interconnect_geometry_optimization_enabled = False
print(design.export_to_aedt.modelithics_inductor_list_count)
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
