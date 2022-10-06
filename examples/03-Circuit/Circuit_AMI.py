"""
Circuit: AMI PostProcessing
----------------------------------
This example shows how you can use PyAEDT to perform advanced postprocessing of AMI simulations.
"""

###############################################################################
# Perform required imports
# ~~~~~~~~~~~~~~~~~~~~~~~~
# Perform required imports and set the local path to the path for PyAEDT.

# sphinx_gallery_thumbnail_path = 'Resources/spectrum_plot.png'
import os
from matplotlib import pyplot as plt
import numpy as np

import pyaedt
from pyaedt import examples
from pyaedt import generate_unique_folder_name

# Set local path to path for PyAEDT
temp_folder = generate_unique_folder_name()
project_path = examples.download_file("ami", "ami_usb.aedtz", temp_folder)

###############################################################################
# Import main classes
# ~~~~~~~~~~~~~~~~~~~
# Import the main classes that are needed: :class:`pyaedt.Desktop` and :class:`pyaedt.Circuit`.

from pyaedt import Circuit
from pyaedt import constants
from pyaedt import settings

###############################################################################
# Launch AEDT
# ~~~~~~~~~~~
# Launch AEDT 2022 R2 in graphical mode. This example uses SI units.

desktopVersion = "2022.2"

##########################################################
# Set non-graphical mode
# ~~~~~~~~~~~~~~~~~~~~~~
# Set non-graphical mode. ``"PYAEDT_NON_GRAPHICAL"``` is needed to generate
# documentation only.
# You can set ``non_graphical`` either to ``True`` or ``False``.
# The Boolean parameter ``new_thread`` defines whether to create a new instance
# of AEDT or try to connect to an existing instance of it.

non_graphical = os.getenv("PYAEDT_NON_GRAPHICAL", "False").lower() in ("true", "1", "t")
NewThread = True

###############################################################################
# Launch AEDT with Circuit and enable pandas as the output format
# ~~~~~~~~~~~~~~~~~~~~~~~~
# All outputs obtained with the method `get_solution_data` will have pandas format.
# Launch AEDT with Circuit. The :class:`pyaedt.Desktop` class initializes AEDT
# and starts the specified version in the specified mode.

settings.enable_pandas_output = True
cir = Circuit(projectname=os.path.join(project_path), non_graphical=non_graphical,
              specified_version=desktopVersion, new_desktop_session=NewThread)

###############################################################################
# Solve AMI setup
# ~~~~~~~~~~~~~~~~~~~~~
# Solve the transient setup.

cir.analyze_setup("AMIAnalysis")

###############################################################################
# Create AMI report
# ~~~~~~~~~~~~~
# Create a report that plots solution data.

plot_name = "WaveAfterSource<b_output4_42.int_ami_tx>"
cir.solution_type = "NexximAMI"
original_data = cir.post.get_solution_data(expressions=plot_name,
                                           setup_sweep_name="AMIAnalysis", domain="Time",
                                           variations=cir.available_variations.nominal)
original_data_value = original_data.full_matrix_real_imag[0]
original_data_sweep = original_data.primary_sweep_values
print(original_data_value)

###############################################################################
# Plot data
# ~~~~~~~~~
# Create a plot based on solution data.
fig = original_data.plot()

###############################################################################
# Sample WaveAfterSource waveform using receiver clock
# ~~~~~~~~~~~~~
# Extract waveform at specific clock time plus half unit interval.

probe_name = "b_input_43"
source_name = "b_output4_42"
plot_type = "WaveAfterSource"
setup_name = "AMIAnalysis"
ignore_bits = 100
unit_interval = 0.1e-9
sample_waveform = cir.post.sample_ami_waveform(setupname=setup_name, probe_name=probe_name, source_name=source_name,
                                               variation_list_w_value=cir.available_variations.nominal,
                                               unit_interval=unit_interval, ignore_bits=ignore_bits,
                                               plot_type=None)

###############################################################################
# Plot waveform and samples
# ~~~~~~~~~
# Create the plot from a start time to stop time in seconds.

tstop = 55e-9
tstart = 50e-9
scale_time = constants.unit_converter(1, unit_system="Time", input_units="s",
                                 output_units=original_data.units_sweeps["Time"])
scale_data = constants.unit_converter(1, unit_system="Voltage", input_units="V",
                                 output_units=original_data.units_data[plot_name])

tstop_ns = scale_time * tstop
tstart_ns = scale_time * tstart

for time in original_data_value[plot_name].index:
    if tstart_ns <= time[0]:
        start_index_original_data = time[0]
        break
for time in original_data_value[plot_name][start_index_original_data:].index:
    if time[0] >= tstop_ns:
        stop_index_original_data = time[0]
        break
for time in sample_waveform[0].time:
    if tstart <= time:
        start_index_waveform = sample_waveform[0].time.index[sample_waveform[1].time == time].tolist()[0]
        break
for time in sample_waveform[0].time:
    if time >= tstop:
        stop_index_waveform = sample_waveform[0].time.index[sample_waveform[1].time == time].tolist()[0]
        break

original_data_zoom = original_data_value[start_index_original_data:stop_index_original_data]
sampled_data_zoom = sample_waveform[1].voltage[start_index_waveform:stop_index_waveform] * scale_data
sampled_time_zoom = sample_waveform[1].time[start_index_waveform:stop_index_waveform] * scale_time

fig, ax = plt.subplots()
ax.plot(sampled_time_zoom, sampled_data_zoom, "r*")
ax.plot(np.array(list(original_data_zoom.index.values)), original_data_zoom.values, color='blue')
ax.set_title('WaveAfterSource')
ax.set_xlabel(original_data.units_sweeps["Time"])
ax.set_ylabel(original_data.units_data[plot_name])
plt.show()

###############################################################################
# Plot Slicer Scatter
# ~~~~~~~~~
# Create the plot from a start time to stop time in seconds.

fig, ax2 = plt.subplots()
ax2.plot(sample_waveform[1].time, sample_waveform[1].voltage, "r*")
ax2.set_title('Slicer Scatter: WaveAfterSource')
ax2.set_xlabel("s")
ax2.set_ylabel("V")
plt.show()

fig, ax3 = plt.subplots()
ax3.set_title('Slicer Scatter: WaveAfterChannel')
ax3.plot(sample_waveform[2].time, sample_waveform[2].voltage, "r*")
ax3.set_xlabel("s")
ax3.set_ylabel("V")
plt.show()

###############################################################################
# Plot Scatter Histogram
# ~~~~~~~~~
# Create the plot from a start time to stop time in seconds.

fig, ax4 = plt.subplots()
ax4.set_title('Slicer Histogram: WaveAfterSource')
ax4.hist(sample_waveform[1].voltage, orientation='horizontal')
ax4.set_ylabel("V")
ax4.grid()
plt.show()

fig, ax5 = plt.subplots()
ax5.set_title('Slicer Histogram: WaveAfterChannel')
ax5.hist(sample_waveform[2].voltage, orientation='horizontal')
ax5.set_ylabel("V")
ax5.grid()
plt.show()

###############################################################################
# Save project and close AEDT
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Save the project and close AEDT.

cir.save_project()
print("Project Saved in {}".format(cir.project_path))
cir.release_desktop()
