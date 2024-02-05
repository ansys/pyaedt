# # EMIT: HFSS to EMIT coupling
#
# <img src="_static/emit_hfss.png" width="60"> This example 
# demonstrates how link an HFSS design
# to EMIT and model RF interference among various components.
#
# > **Note:** This example uses the ``Cell Phone RFI Desense``
# > project that is available with the AEDT installation in the 
# > folder ``\Examples\EMIT\``

# ## Perform required imports
#
# Perform required imports.

import os
import pyaedt
import tempfile
from pyaedt.emit_core.emit_constants import TxRxMode, ResultType
import shutil

# ## Set non-graphical mode
#
# Set non-graphical mode. 
# You can set ``non_graphical`` either to ``True`` or ``False``.
# The Boolean parameter ``new_thread`` defines whether to create a new instance
# of AEDT or try to connect to an existing instance of it.

non_graphical = False
NewThread = True
desktop_version = "2023.2"

# ## Launch AEDT with EMIT
#
# Launch AEDT with EMIT. The ``Desktop`` class initializes AEDT and starts it
# on the specified version and in the specified graphical mode.
# A temporary working directory is created using ``tempfile``.

d = pyaedt.launch_desktop(desktop_version, non_graphical, NewThread)
temp_dir = tempfile.TemporaryDirectory(suffix=".ansys")

# ## Copy Example Files
#
# Copy the ``Cell Phone RFT Defense`` example data from the
# installed examples folder to the temporary working
# directory.
#
# > **Note:** The HFSS design from the installed example
# > used to model the RF environment
# > has been pre-solved. Hence, the results folder is copied and
# > the RF interference between transcievers is calculated in EMIT using
# > results from the linked HFSS design.
#
# The following lambda functions help create file and folder
# names when copying data from the Examples folder. 

file_name = lambda s: s + ".aedt"
results_name = lambda s: s + ".aedtresults"
pdf_name = lambda s: s + " Example.pdf"

# Build the names of the source files for this example.

example = "Cell Phone RFI Desense"
example_dir = os.path.join(d.install_path, "Examples\\EMIT")
example_project = os.path.join(example_dir, file_name(example))
example_results_folder = os.path.join(example_dir, results_name(example))
example_pdf = os.path.join(example_dir, pdf_name(example))

# Copy the files to the temporary working directory.

project_name = shutil.copyfile(example_project, 
                               os.path.join(temp_dir.name, file_name(example)))
results_folder = shutil.copytree(example_results_folder,
                                 os.path.join(temp_dir.name, results_name(example)))
project_pdf = shutil.copyfile(example_pdf, 
                              os.path.join(temp_dir.name, pdf_name(example)))

# Open the project in the working directory.

aedtapp = pyaedt.Emit(project_name)

# ## Create and connect EMIT components
#
# Create two radios with antennas connected to each one.

rad1, ant1 = aedtapp.modeler.components.create_radio_antenna("Bluetooth Low Energy (LE)")
rad2, ant2 = aedtapp.modeler.components.create_radio_antenna("Bluetooth Low Energy (LE)")

# ## Define coupling among RF systems
#
# Define coupling among the RF systems.

for link in aedtapp.couplings.linkable_design_names:
    aedtapp.couplings.add_link(link)
    print("linked \"" + link + "\".")

for link in aedtapp.couplings.coupling_names:
    aedtapp.couplings.update_link(link)
    print("linked \"" + link + "\".")

# ## Calculate RF Interference
#
# Run the EMIT simulation. This portion of the EMIT API is not yet implemented.
#
# This part of the example requires Ansys AEDT 2023 R2. 

if desktop_version > "2023.1":
    rev = aedtapp.results.analyze()
    rx_bands = rev.get_band_names(rad1.name, TxRxMode.RX) 
    tx_bands = rev.get_band_names(rad2.name, TxRxMode.TX) 
    domain = aedtapp.results.interaction_domain()
    domain.set_receiver(rad1.name, rx_bands[0], -1)
    domain.set_interferer(rad2.name,tx_bands[0])
    interaction = rev.run(domain)
    worst = interaction.get_worst_instance(ResultType.EMI)
    if worst.has_valid_values():
        emi = worst.get_value(ResultType.EMI)
        print("Worst case interference is: {} dB".format(emi))

# ## Save and Close the Project
#
# After the simulation completes, you can close AEDT or release it using the
# `pyaedt.Desktop.force_close_desktop` method.
# All methods provide for saving the project before closing.

aedtapp.save_project()
aedtapp.release_desktop(close_projects=True, close_desktop=True)

temp_dir.cleanup()  # Remove temporary project files.
