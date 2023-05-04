"""
HFSS: Eigenmode Filter
--------------------
This example shows how you can use PyAEDT to use eigenmode solver in HFSS.
Eigenmode analysis can be applied to open, radiating structures
using an absorbing boundary condition. This type of analysis can be very helpful
to determine the resonant frequency of an antenna and can be used to refine
the mesh at the resonance, even when the resonant frequence of the antenna is not known.

The challenge posed by this method is to identify and filter the non-physical modes
the result from reflection from boundaries of the main domain.
Since the Eigenmode solver sorts by frequency and does not filter on the
quality factor, these _virtual modes_ will be present when the eigenmode approach is
applied to nominally open structures.
"""

###############################################################################
# Perform required imports
# ~~~~~~~~~~~~~~~~~~~~~~~~
# Perform required imports.

import sys
import os
import pyaedt

# Set local temporary folder to export the cable library into.
# set_cable_properties.json is the required json file to work with the Cable class.
# Its structure must never change except for the properties values.
temp_folder = pyaedt.generate_unique_folder_name()
project_path = pyaedt.downloads.download_file("eigenmode", "emi_PCB_house.aedt", temp_folder)


###############################################################################
# Launch AEDT
# ~~~~~~~~~~~
# Launch AEDT 2023 R1 in graphical mode. This example uses SI units.

desktopVersion = "2023.1"

###############################################################################
# Set non-graphical mode
# ~~~~~~~~~~~~~~~~~~~~~~
# Set non-graphical mode. ``"PYAEDT_NON_GRAPHICAL"`` is needed to generate
# documentation only.
# You can set ``non_graphical`` either to ``True`` or ``False``.

non_graphical = False

###############################################################################
# Launch AEDT
# ~~~~~~~~~~~
# Launch AEDT 2023 R1 in graphical mode.

d = pyaedt.launch_desktop(desktopVersion, non_graphical=non_graphical, new_desktop_session=True)

###############################################################################
# Launch HFSS
# ~~~~~~~~~~~
# Launch HFSS 2023 R1 in graphical mode.

hfss = pyaedt.Hfss(projectname=project_path, non_graphical=non_graphical)

###############################################################################
# New instance of Cable modeling class
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# New instance of Cable modeling class which requires as input
# the aedt app and the json file path containing all the cable properties.



###############################################################################
# Create cable bundle
# ~~~~~~~~~~~~~~~~~~~
# Properties for cable bundle are updated (user can change them manually
# in json file).
# A cable bundle with insulation jacket type is created.

num_modes = 6
fmin = 1.5 # lowest frequesncy of interest
fmax = 2 # highest frequesncy of interest
next_fmin = fmin
setup_nr = 1

limit = 10  # this is the limit for Q-factor, modes with Q less than this will be ignored
resonance = {}

###############################################################################
# Create cable bundle
# ~~~~~~~~~~~~~~~~~~~
# A cable bundle with no jacket type is created.

def find_resonance():
    #setup creation
    next_min_freq = str(next_fmin) + " GHz"
    setup_name = "em_setup" + str(setup_nr)
    setup = hfss.create_setup(setup_name)
    setup.props['MinimumFrequency'] = next_min_freq
    setup.props['NumModes'] = num_modes
    setup.props['ConvergeOnRealFreq'] = True
    setup.props['MaximumPasses'] = 10
    setup.props['MinimumPasses'] = 3
    setup.props['MaxDeltaFreq'] = 5
    #analyzing the eigenmode setup
    hfss.analyze_setup(setup_name, num_cores=8,use_auto_settings=True)
    #getting the Q and real frequency of each mode
    eigen_q = hfss.post.available_report_quantities(quantities_category="Eigen Q")
    eigen_mode =  hfss.post.available_report_quantities()
    data = {}
    cont = 0
    for i in eigen_mode:
        eigen_q_value = hfss.post.get_solution_data(expressions=eigen_q[cont], setup_sweep_name=setup_name+' : LastAdaptive', report_category = "Eigenmode")
        eigen_mode_value = hfss.post.get_solution_data(expressions=eigen_mode[cont], setup_sweep_name=setup_name+' : LastAdaptive', report_category = "Eigenmode")
        data[cont] = [eigen_q_value.data_real()[0], eigen_mode_value.data_real()[0]]
        cont += 1

    print(data)
    return data

###############################################################################
# Create cable bundle
# ~~~~~~~~~~~~~~~~~~~
# A cable bundle with shielding jacket type is created.

while next_fmin < fmax:
    output = find_resonance()
    next_fmin = output[len(output)-1][1]/1e9
    setup_nr +=1
    cont_res = len(resonance)
    for q in output:
        if output[q][0] > limit:
            resonance[cont_res] = output[q]
            cont_res += 1

resonance_frequencies = [f"{resonance[i][1]/1e9:.5} GHz" for i in resonance]
print(str(resonance_frequencies))

###############################################################################
# Update cable bundle
# ~~~~~~~~~~~~~~~~~~~
# The first cable bundle (insulation jacket type) is updated.

###############################################################################
# Save project and close AEDT
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Save the project and close AEDT.

hfss.save_project()
hfss.release_desktop()
