"""
SBR+: HFSS to SBR+ time animation
---------------------------------
This example shows how you can use PyAEDT to create an SBR+ time animation
and save it to a GIF file. This example works only on CPython.
"""

###############################################################################
# Import packages
# ~~~~~~~~~~~~~~~
# Import the packages.

import os
from pyaedt import Hfss, examples

##########################################################
# Set non-graphical mode
# ~~~~~~~~~~~~~~~~~~~~~~
# Set non-graphical mode. The default is ``False``.

non_graphical = os.getenv("PYAEDT_NON_GRAPHICAL", "False").lower() in ("true", "1", "t")


##########################################################
# Launch AEDT and load project
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Launch AEDT and load the project.

project_file = examples.download_sbr_time()

hfss = Hfss(project_file, specified_version="2022.2", non_graphical=non_graphical, new_desktop_session=True)

hfss.analyze_nominal()

###############################################################################
# Get solution data
# ~~~~~~~~~~~~~~~~~
# Get solution data. After simulation is performed, you can load solutions
# in ``solution_data``.

solution_data = hfss.post.get_solution_data(expressions=["NearEX", "NearEY", "NearEZ"],
                                            variations={"_u": ["All"], "_v": ["All"], "Freq": ["All"]},
                                            context="Near_Field",
                                            report_category="Near Fields")

###############################################################################
# Compute IFFT
# ~~~~~~~~~~~~
# Compute IFFT (Inverse Fast Fourier Transform).

t_matrix = solution_data.ifft("NearE", window=True)


###############################################################################
# Export IFFT to CSV files
# ~~~~~~~~~~~~~~~~~~~~~~~~
# Export the IFFT to CSV files.

frames_list_file = solution_data.ifft_to_file(coord_system_center=[-0.15, 0, 0], db_val=True,
                                              csv_dir=os.path.join(hfss.working_directory, "csv"))

###############################################################################
# Plot scene
# ~~~~~~~~~~
# Plot the scene to create the time plot animation.

hfss.post.plot_scene(frames_list_file, os.path.join(hfss.working_directory, "animation.gif"), norm_index=15, dy_rng=35,
                     show=False)


hfss.release_desktop()


