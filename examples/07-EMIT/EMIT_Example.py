# # EMIT: Antenna
#
# This example shows how to create a project in EMIT for
# the simulation of an antenna using HFSS.
#
# <img src="_static/emit_simple_cosite.png" width="400">

# ## Perform required inputs
#
# Perform required imports.

import os
import pyaedt
import tempfile
from pyaedt.emit_core.emit_constants import TxRxMode, ResultType


# ## Set non-graphical mode
#
# Set non-graphical mode. 
# You can set ``non_graphical`` either to ``True`` or ``False``.
# The ``NewThread`` Boolean variable defines whether to create a new instance
# of AEDT or try to connect to existing instance of it if one is available.

non_graphical = False
NewThread = True
desktop_version = "2023.2"


# ## Launch AEDT with EMIT
#
# Launch AEDT with EMIT. The ``launch_desktop()`` method initializes AEDT
# using the specified version. The 2nd argument can be set to ``True`` to
# run AEDT in non-graphical mode.

temp_dir = tempfile.TemporaryDirectory(suffix=".ansys")
d = pyaedt.launch_desktop(desktop_version, non_graphical, NewThread)
aedtapp = pyaedt.Emit(os.path.join(temp_dir.name, "antenna_cosite"))


# ## Create and connect EMIT components
#
# Create three radios and connect an antenna to each one.

rad1 = aedtapp.modeler.components.create_component("New Radio")
ant1 = aedtapp.modeler.components.create_component("Antenna")
if rad1 and ant1:
    ant1.move_and_connect_to(rad1)

# ## Place Antenna Radio Pairs
#
# The method ``create_radio_antenna()`` places radio/antenna pair. The first 
# argument is the type of radio. The 2nd argumnt is the name that
# will be assigned to the radio.

rad2, ant2 = aedtapp.modeler.components.create_radio_antenna("GPS Receiver")
rad3, ant3 = aedtapp.modeler.components.create_radio_antenna("Bluetooth Low Energy (LE)", "Bluetooth")

# ## Define the RF Environment
#
# The next step in this workflow is to specify the RF coupling among antennas. 
# This functionality yet to be implemented in the API, but can be entered from the UI.
#
# <img src="_static/coupling.png" width="500">


# ## Run EMIT simulation
#
# Run the EMIT simulation. 
#
# This part of the example requires Ansys AEDT 2023 R2. 

if desktop_version > "2023.1" and os.getenv("PYAEDT_DOC_GENERATION", "False") != "1":
    rev = aedtapp.results.analyze()
    rx_bands = rev.get_band_names(rad2.name, TxRxMode.RX) 
    tx_bands = rev.get_band_names(rad3.name, TxRxMode.TX) 
    domain = aedtapp.results.interaction_domain()
    domain.set_receiver(rad2.name, rx_bands[0], -1)
    domain.set_interferer(rad3.name,tx_bands[0])
    interaction = rev.run(domain)
    worst = interaction.get_worst_instance(ResultType.EMI)
    if worst.has_valid_values():
        emi = worst.get_value(ResultType.EMI)
        print("Worst case interference is: {} dB".format(emi))

# ## Save project and close AEDT
#
# After the simulation completes, you can close AEDT or release it using the
# `pyaedt.Desktop.force_close_desktop` method.
# All methods provide for saving the project before closing.

aedtapp.save_project()
aedtapp.release_desktop(close_projects=True, close_desktop=True)

# Clean up the temporary directory and remove the project files located
# in ``temp_dir.name``.

temp_dir.cleanup()
