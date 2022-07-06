"""
Circuit: Create Automatic Reports
---------------------------------
# This example shows how to create automatic reports using a json file.
"""
# sphinx_gallery_thumbnail_path = 'Resources/spectrum_plot.png'

import os

###############################################################################
# Import Packages
# ~~~~~~~~~~~~~~~
# Set the local path to the path for PyAEDT.
import shutil
from pyaedt import examples
from pyaedt import generate_unique_name
import tempfile

project_path = examples.download_custom_reports()

tmpfold = tempfile.gettempdir()
temp_folder = os.path.join(tmpfold, generate_unique_name("CustomReport"))


shutil.copytree(project_path, temp_folder)

###############################################################################
# Import the main classes needed: :class:`pyaedt.Desktop` and :class:`pyaedt.Circuit`.

from pyaedt import Circuit
from pyaedt.generic.DataHandlers import json_to_dict

###############################################################################
# Launch AEDT and Circuit
# ~~~~~~~~~~~~~~~~~~~~~~~
# This example launches AEDT 2022R2 in graphical mode.

# This examples uses SI units.

desktopVersion = "2022.2"



##########################################################
# Set Non Graphical Mode.
# Default is False

non_graphical = os.getenv("PYAEDT_NON_GRAPHICAL", "False").lower() in ("true", "1", "t")
NewThread = True

###############################################################################
# Launch AEDT and Circuit
# ~~~~~~~~~~~~~~~~~~~~~~~
# The :class:`pyaedt.Desktop` class initializes AEDT and starts it on a specified version in
# a specified graphical mode. The Boolean parameter ``NewThread`` defines whether
# to create a new instance of AEDT or try to connect to existing instance of it.

cir = Circuit(projectname=os.path.join(temp_folder, 'CISPR25_Radiated_Emissions_Example22R1.aedtz'), non_graphical=non_graphical,
              specified_version=desktopVersion)

###############################################################################
# Spectrum Report
# ~~~~~~~~~~~~~~~
# The json file can be used to create a simple setup or a fully customized one.
# In the following example user can create a simple setup or change the json and customize it.
# In a spectrum report also limitilines and notes can be added. Axes, grid and legend can be edited.
# Custom report can be done, in non graphical mode starting from AEDT 2022.2.

report1 = cir.post.create_report_from_configuration(os.path.join(temp_folder,'Spectrum_CISPR_Basic.json'))

if not non_graphical:
    report1_full = cir.post.create_report_from_configuration(os.path.join(temp_folder,'Spectrum_CISPR_Custom.json'))

###############################################################################
# Transient Report
# ~~~~~~~~~~~~~~~~
# The json file can read and modified before running the script like in the example below where the traces
# are edited before the report is created.
# Custom report can be done, in non graphical mode starting from AEDT 2022.2.

if non_graphical:
    props = json_to_dict(os.path.join(temp_folder, 'Transient_CISPR_Basic.json'))
else:
    props = json_to_dict(os.path.join(temp_folder, 'Transient_CISPR_Custom.json'))

report2 = cir.post.create_report_from_configuration(input_dict=props, solution_name="NexximTransient")
props["expressions"] = {"V(Battery)": {}, "V(U1_VDD)": {}}
props["plot_name"] = "Battery Voltage"
report3 = cir.post.create_report_from_configuration(input_dict=props, solution_name="NexximTransient")

###############################################################################
# Eye Diagram Report
# ~~~~~~~~~~~~~~~~~~
# The json file can contain also the eye mask, plot the eye diagram and fully customize it.
# Custom report can be done, in non graphical mode starting from AEDT 2022.2.

report4 = cir.post.create_report_from_configuration(os.path.join(temp_folder,'EyeDiagram_CISPR_Basic.json'))

if not non_graphical:
    report4_full = cir.post.create_report_from_configuration(os.path.join(temp_folder,'EyeDiagram_CISPR_Custom.json'))

if not non_graphical:
    cir.post.export_report_to_jpg(cir.working_directory, report4.plot_name)

###############################################################################
# Save and close Desktop
# ~~~~~~~~~~~~~~~~~~~~~~
cir.save_project()
print("Project Saved in {}".format(cir.project_path))
cir.release_desktop()
