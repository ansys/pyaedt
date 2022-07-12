"""
EMIT: Hfss Coupling Example
---------------------------
This tutorial shows how you can use PyAEDT to open an AEDT project with
an HFSS design, create an EMIT design in the project, then link the HFSS design
as a coupling link in the EMIT design.
"""
# sphinx_gallery_thumbnail_path = 'Resources/emit.png'
import os
import tempfile

# Import required modules
from pyaedt.generic.filesystem import Scratch

from pyaedt import Emit
from pyaedt import Desktop


###############################################################################
# Initialization Settings
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Change NonGraphical Boolean to False to open AEDT in graphical mode
# With NewThread = False, an existing instance of AEDT will be used, if
# available. This example will use AEDT 2022.2 However this example is supposed to work
# on AEDT 2022R2 and on.

non_graphical = os.getenv("PYAEDT_NON_GRAPHICAL", "False").lower() in ("true", "1", "t")
NewThread = True
desktop_version = "2022.2"
scratch_path = tempfile.gettempdir()

###############################################################################
# Launch AEDT and EMIT Design
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Desktop class initializes AEDT and starts it on specified version and
# specified graphical mode. NewThread Boolean variable defines if a user wants
# to create a new instance of AEDT or try to connect to existing instance of
# it.
d = Desktop(desktop_version, non_graphical, NewThread)

temp_folder = os.path.join(scratch_path, ("EmitHFSSExample"))
if not os.path.exists(temp_folder):
    os.mkdir(temp_folder)

example_name = "Cell Phone RFI Desense"
example_aedt = example_name + ".aedt"
example_lock = example_aedt + ".lock"
example_pdf_file = example_name + " Example.pdf"

example_dir = os.path.join(d.install_path, "Examples\\EMIT")
example_project = os.path.join(example_dir, example_aedt)
example_pdf = os.path.join(example_dir, example_pdf_file)

# If the Cell phone example is not in the install dir, exit from this example.
if not os.path.exists(example_project):
    msg = """
        Cell phone RFT Desense example file is not in the
         Examples/EMIT directory under the EDT installation. You can not run this example.
        """
    print(msg)
    d.release_desktop(True, True)
    exit()

my_project = os.path.join(temp_folder, example_aedt)
my_project_lock = os.path.join(temp_folder, example_lock)
my_project_pdf = os.path.join(temp_folder, example_pdf_file)

if os.path.exists(my_project):
    os.remove(my_project)

if os.path.exists(my_project_lock):
    os.remove(my_project_lock)

with Scratch(scratch_path) as local_scratch:
    local_scratch.copyfile(example_project, my_project)
    if os.path.exists(example_pdf):
        local_scratch.copyfile(example_pdf, my_project_pdf)

aedtapp = Emit(my_project)
###############################################################################

# Create and Connect EMIT Components
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Create 3 radios and connect an antenna to each.
rad1 = aedtapp.modeler.components.create_component("UE - Handheld")
ant1 = aedtapp.modeler.components.create_component("Antenna")
if rad1 and ant1:
    ant1.move_and_connect_to(rad1)

rad2 = aedtapp.modeler.components.create_component("GPS Receiver")
ant2 = aedtapp.modeler.components.create_component("Antenna")
if rad2 and ant2:
    ant2.move_and_connect_to(rad2)

###############################################################################
# Define Coupling Among the RF Systems
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
for link in aedtapp.couplings.linkable_design_names:
    aedtapp.couplings.add_link(link)

for link in aedtapp.couplings.coupling_names:
    aedtapp.couplings.update_link(link)
###############################################################################
# Run the EMIT Simulation
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# This portion of the EMIT API is not yet implemented.


###############################################################################
# Close Desktop
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# After the simulaton is completed user can close the desktop or release it
# (using release_desktop method). All methods give possibility to save projects
# before exit.
aedtapp.save_project()
aedtapp.release_desktop(close_projects=True, close_desktop=True)
