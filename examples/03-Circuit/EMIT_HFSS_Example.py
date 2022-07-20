"""
EMIT: HFSS to EMIT coupling
---------------------------
This tutorial shows how you can use PyAEDT to open an AEDT project with
an HFSS design, create an EMIT design in the project, and link the HFSS design
as a coupling link in the EMIT design.
"""
###############################################################################
# Perform required imports
# ~~~~~~~~~~~~~~~~~~~~~~~~
# Perform required imports.

# sphinx_gallery_thumbnail_path = 'Resources/emit.png'
import os
import tempfile

# Import required modules
from pyaedt.generic.filesystem import Scratch

from pyaedt import Emit
from pyaedt import Desktop


###############################################################################
# Specify initialization settings
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Change the ``non_graphical`` Boolean variable to ``False`` to open AEDT in
# graphical mode. With ``NewThread = False``, an existing instance of AEDT
# is used if one is available. The following code uses AEDT 2022 R2.

non_graphical = os.getenv("PYAEDT_NON_GRAPHICAL", "False").lower() in ("true", "1", "t")
NewThread = True
desktop_version = "2022.2"
scratch_path = tempfile.gettempdir()

###############################################################################
# Launch AEDT with EMIT
# ~~~~~~~~~~~~~~~~~~~~~
# Launch AEDT with EMIT. The ``Desktop`` class initializes AEDT and starts it
# on the specified version and in the specified graphical mode. The ``NewThread``
# Boolean variable defines whether to create a new instance of AEDT or try to
# connect to existing instance of it if one is available.

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

# If the ``Cell Phone RFT Defense`` example is not in the installation directory, exit from this example.
if not os.path.exists(example_project):
    msg = """
        Cell phone RFT Desense example file is not in the
         Examples/EMIT directory under the EDT installation. You cannot run this example.
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
# Create and connect EMIT components
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Create three radios and connect an antenna to each one.

rad1 = aedtapp.modeler.components.create_component("UE - Handheld")
ant1 = aedtapp.modeler.components.create_component("Antenna")
if rad1 and ant1:
    ant1.move_and_connect_to(rad1)

rad2 = aedtapp.modeler.components.create_component("GPS Receiver")
ant2 = aedtapp.modeler.components.create_component("Antenna")
if rad2 and ant2:
    ant2.move_and_connect_to(rad2)

###############################################################################
# Define coupling among RF systems
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Define coupling among the RF systems.

for link in aedtapp.couplings.linkable_design_names:
    aedtapp.couplings.add_link(link)

for link in aedtapp.couplings.coupling_names:
    aedtapp.couplings.update_link(link)
###############################################################################
# Run EMIT simulation
# ~~~~~~~~~~~~~~~~~~~
# Run the EMIT simulation. This portion of the EMIT API is not yet implemented.


###############################################################################
# Save project and close AEDT
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~
# After the simulaton completes, you can close AEDT or release it using the
# :func:`pyaedt.Desktop.force_close_desktop` method.
# All methods provide for saving the project before closing.

aedtapp.save_project()
aedtapp.release_desktop(close_projects=True, close_desktop=True)
