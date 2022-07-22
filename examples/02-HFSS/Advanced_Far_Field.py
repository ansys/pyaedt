"""
HFSS: advanced far field postprocessing
---------------------------------------
This example shows how to use advanced postprocessing functions to create plots
using Matplotlib without opening the HFSS user interface.
This examples runs only on Windows using CPython.
"""
###############################################################################
# Import packages
# ~~~~~~~~~~~~~~~
# Set the local path to the path for PyAEDT.

import os
import pathlib

local_path = os.path.abspath("")
module_path = pathlib.Path(local_path)
aedt_lib_path = module_path.parent.parent.parent
from pyaedt import examples

project_name = examples.download_antenna_array()


import time


from pyaedt import Desktop
from pyaedt import Hfss
from pyaedt.generic.general_methods import remove_project_lock


##########################################################
# Set non-graphical mode
# Set non-graphical mode. The default is ``False``.

non_graphical = os.getenv("PYAEDT_NON_GRAPHICAL", "False").lower() in ("true", "1", "t")


###############################################################################
# Import all modules for postprocessing
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Import all modules for postprocessing.

import numpy as np
import matplotlib.pyplot as plt

###############################################################################
# Launch AEDT
# ~~~~~~~~~~~
# Launch AEDT 2022 R2 in non-graphical mode.

desktopVersion = "2022.2"
NewThread = False
desktop = Desktop(desktopVersion, non_graphical=non_graphical, new_desktop_session=NewThread)

###############################################################################
# Open HFSS project
# ~~~~~~~~~~~~~~~~~
# Open the HFSS project.

remove_project_lock(project_name)

hfss = Hfss(project_name, "4X4_MultiCell_CA-Array")


###############################################################################
# Solve HFSS project
# ~~~~~~~~~~~~~~~~~~~
# Solves the HFSS project.
# The solution time is computed.

start = time.time()
hfss.analyze_setup("Setup1")
hfss.save_project()
end = time.time() - start
print("Solution Time", end)

#######################################
# Get efields data from solution
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Gets efields data from the solution.

start = time.time()
ff_data = hfss.post.get_efields_data(ff_setup="3D")
end = time.time() - start
print("Postprocessing Time", end)

###############################################################################
# Calculate far field values
# ~~~~~~~~~~~~~~~~~~~~~~~~~~
# Use Matplotlib to read the solution generated in ``ff_data``and process
# the field based on Phi and Theta and generate a plot.

def ff_calc(x=0, y=0, qty="rETotal", dB=True):
    array_size = [4, 4]
    loc_offset = 2  # if array index is not starting at [1,1]
    xphase = float(y)
    yphase = float(x)
    array_shape = (array_size[0], array_size[1])
    weight = np.zeros(array_shape, dtype=complex)
    mag = np.ones(array_shape, dtype="object")
    port_names_arranged = np.chararray(array_shape)
    all_ports = ff_data.keys()
    w_dict = {}
    # calculate weights based off of progressive phase shift
    for m in range(array_shape[0]):
        for n in range(array_shape[1]):
            mag_val = mag[m][n]
            ang = np.radians(xphase * m) + np.radians(yphase * n)
            weight[m][n] = np.sqrt(mag_val) * np.exp(1j * ang)
            current_index_str = "[" + str(m + 1 + loc_offset) + "," + str(n + 1 + loc_offset) + "]"
            port_name = [y for y in all_ports if current_index_str in y]
            w_dict[port_name[0]] = weight[m][n]

    length_of_ff_data = len(ff_data[port_name[0]][2])

    array_shape = (len(w_dict), length_of_ff_data)
    rEtheta_fields = np.zeros(array_shape, dtype=complex)
    rEphi_fields = np.zeros(array_shape, dtype=complex)
    w = np.zeros((1, array_shape[0]), dtype=complex)
    # create port mapping
    for n, port in enumerate(ff_data.keys()):
        re_theta = ff_data[port][2]
        re_phi = ff_data[port][3]
        re_theta = re_theta * w_dict[port]

        w[0][n] = w_dict[port]
        re_phi = re_phi * w_dict[port]

        rEtheta_fields[n] = re_theta
        rEphi_fields[n] = re_phi

        theta_range = ff_data[port][0]
        phi_range = ff_data[port][1]
        theta = [int(np.min(theta_range)), int(np.max(theta_range)), np.size(theta_range)]
        phi = [int(np.min(phi_range)), int(np.max(phi_range)), np.size(phi_range)]
        Ntheta = len(theta_range)
        Nphi = len(phi_range)

    rEtheta_fields = np.dot(w, rEtheta_fields)
    rEtheta_fields = np.reshape(rEtheta_fields, (Ntheta, Nphi))

    rEphi_fields = np.dot(w, rEphi_fields)
    rEphi_fields = np.reshape(rEphi_fields, (Ntheta, Nphi))

    all_qtys = {}
    all_qtys["rEPhi"] = rEphi_fields
    all_qtys["rETheta"] = rEtheta_fields
    all_qtys["rETotal"] = np.sqrt(np.power(np.abs(rEphi_fields), 2) + np.power(np.abs(rEtheta_fields), 2))

    pin = np.sum(w)
    print(str(pin))
    real_gain = 2 * np.pi * np.abs(np.power(all_qtys["rETotal"], 2)) / pin / 377
    all_qtys["RealizedGain"] = real_gain

    if dB:
        if "Gain" in qty:
            qty_to_plot = 10 * np.log10(np.abs(all_qtys[qty]))
        else:
            qty_to_plot = 20 * np.log10(np.abs(all_qtys[qty]))
        qty_str = qty + " (dB)"
    else:
        qty_to_plot = np.abs(all_qtys[qty])
        qty_str = qty + " (mag)"

    plt.figure(figsize=(25, 15))
    plt.title(qty_str)
    plt.xlabel("Theta (degree)")
    plt.ylabel("Phi (degree)")

    plt.imshow(qty_to_plot, cmap="jet")
    plt.colorbar()

    np.max(qty_to_plot)


###############################################################################
# Create plot and interact with it
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Create the plot and interact with it.

ff_calc()

# interact(ff_calc, x=widgets.FloatSlider(value=0, min=-180, max=180, step=1),
#          y=widgets.FloatSlider(value=0, min=-180, max=180, step=1))


vals = hfss.post.get_far_field_data(
    setup_sweep_name=hfss.nominal_sweep, expression="RealizedGainTotal", domain="Elevation"
)

###############################################################################
# Generate polar plot
# ~~~~~~~~~~~~~~~~~~~
# Generate a polar plot.

vals.plot(math_formula="db20", is_polar=True)

###############################################################################
# Generate scalar plot
# ~~~~~~~~~~~~~~~~~~~~
# Generate a scalar plot.

vals.plot(math_formula="db20", is_polar=False)


###############################################################################
# Generate plot using Phi as primary sweep
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Generate the plot using Phi as the primary sweep.

vals3d = hfss.post.get_far_field_data(
    setup_sweep_name=hfss.nominal_sweep, expression="RealizedGainTotal", domain="Infinite Sphere1"
)

vals3d.plot_3d()


#######################################
# Close HFSS project and AEDT
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Close the HFSS project and release AEDT.

# hfss.close_project()
hfss.save_project()
desktop.release_desktop()
