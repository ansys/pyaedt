"""
Circuit: Touchstone file management
-----------------------------------
This example shows how to use objects in a Touchstone file without opening AEDT.

To provide the advanced postprocessing features needed for this example, Matplotlib and NumPy
must be installed on your machine.

This example runs only on Windows using CPython.
"""
###############################################################################
# Perform required imports
# ~~~~~~~~~~~~~~~~~~~~~~~~
# Perform required imports and set the local path to the path for PyAEDT.

# sphinx_gallery_thumbnail_path = 'Resources/nde.png'
import os
import pathlib
import sys

# Set local path to path for PyAEDT
local_path = os.path.abspath("")
module_path = pathlib.Path(local_path)
root_path = module_path.parent
root_path2 = root_path.parent
root_path3 = root_path2.parent
path1 = os.path.join(root_path2)
path2 = os.path.join(root_path3)
sys.path.append(path1)
sys.path.append(path2)
from pyaedt import examples

example_path = examples.download_touchstone()

###############################################################################
# Import Matplotlib and Touchstone file
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Import Matplotlib and the Touchstone file.

import matplotlib.pyplot as plt
import numpy as np
from pyaedt.generic.TouchstoneParser import (
    read_touchstone,
    get_return_losses,
    get_insertion_losses_from_prefix,
    get_fext_xtalk_from_prefix,
    get_next_xtalk,
    get_worst_curve_from_solution_data,
)

###############################################################################
# Read Touchstone file
# ~~~~~~~~~~~~~~~~~~~~
# Read the Touchstone file.

data = read_touchstone(example_path)

###############################################################################
# Get curve names
# ~~~~~~~~~~~~~~~
# Get the curve names. The following code shows how to get lists of the return losses,
# insertion losses, fext, and next based on a few inputs and port names.

rl_list = get_return_losses(data.ports)
il_list = get_insertion_losses_from_prefix(data.ports, "U1", "U7")
fext_list = get_fext_xtalk_from_prefix(data.ports, "U1", "U7")
next_list = get_next_xtalk(data.ports, "U1")


###############################################################################
# Get curve worst cases
# ~~~~~~~~~~~~~~~~~~~~~
# Get curve worst cases.

worst_rl, global_mean = get_worst_curve_from_solution_data(
    data, freq_min=1, freq_max=20, worst_is_higher=True, curve_list=rl_list
)
worst_il, mean2 = get_worst_curve_from_solution_data(
    data, freq_min=1, freq_max=20, worst_is_higher=False, curve_list=il_list
)
worst_fext, mean3 = get_worst_curve_from_solution_data(
    data, freq_min=1, freq_max=20, worst_is_higher=True, curve_list=fext_list
)
worst_next, mean4 = get_worst_curve_from_solution_data(
    data, freq_min=1, freq_max=20, worst_is_higher=True, curve_list=next_list
)

###############################################################################
# Plot curves using Matplotlib
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Plot the curves using Matplotlib.

fig, ax = plt.subplots(figsize=(20, 10))
ax.set(xlabel="Frequency (Hz)", ylabel="Return Loss (dB)", title="Return Loss")
ax.grid()
mag_data = 20 * np.log10(np.array(data.solutions_data_mag[worst_rl]))
freq_data = np.array([i * 1e9 for i in data.sweeps["Freq"]])
ax.plot(freq_data, mag_data, label=worst_rl)
mag_data2 = 20 * np.log10(np.array(data.solutions_data_mag[worst_il]))
ax.plot(freq_data, mag_data2, label=worst_il)
mag_data3 = 20 * np.log10(np.array(data.solutions_data_mag[worst_fext]))
ax.plot(freq_data, mag_data3, label=worst_fext)
mag_data4 = 20 * np.log10(np.array(data.solutions_data_mag[worst_next]))
ax.plot(freq_data, mag_data4, label=worst_next)
ax.legend(
    ["Worst RL = " + worst_rl, "Worst IL = " + worst_il, "Worst FEXT = " + worst_fext, "Worst NEXT = " + worst_next]
)
plt.show()
