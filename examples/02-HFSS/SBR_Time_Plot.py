"""
HFSS to SBR+ Time Plot
----------------------
This example shows how you can use PyAEDT to create an SBR+ time animation
and save to gif file. This example will work only on CPython.
"""

###############################################################################
# Import Packages
# ~~~~~~~~~~~~~~~
# For this example we will need Hfss package only

import os
from pyaedt import Hfss, examples

project_file = examples.download_sbr_time()

hfss = Hfss(project_file, specified_version="2022.1", non_graphical=True, new_desktop_session=True)

hfss.analyze_nominal()

###############################################################################
# Get Solution Data
# ~~~~~~~~~~~~~~~~~
# After Simulation is performed the solutions can be loaded in solution_data

solution_data = hfss.post.get_solution_data(expressions=["NearEX", "NearEY", "NearEZ"],
                                            variations={"_u": ["All"], "_v": ["All"], "Freq": ["All"]},
                                            context="Near_Field",
                                            report_category="Near Fields")

###############################################################################
# Compute IFFT
# ~~~~~~~~~~~~
# Description
t_matrix = solution_data.ifft("NearE", window=True)


###############################################################################
# Export IFFT to csv files
# ~~~~~~~~~~~~~~~~~~~~~~~~
# Description
frames_list_file = solution_data.ifft_to_file(coord_system_center=[-0.15, 0, 0], db_val=True,
                                              csv_dir=os.path.join(hfss.working_directory, "csv"))

###############################################################################
# Plot the Scene
# ~~~~~~~~~~~~~~
# Description

hfss.post.plot_scene(frames_list_file, os.path.join(hfss.working_directory, "animation.gif"), norm_index=15, dy_rng=35,
                     show=False)


hfss.release_desktop()


