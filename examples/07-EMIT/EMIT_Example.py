"""
EMIT: antenna
---------------------
This example shows how you can use PyAEDT to create a project in EMIT for
the simulation of an antenna.
"""
###############################################################################
# Perform required inputs
# ~~~~~~~~~~~~~~~~~~~~~~~
# Perform required imports.

import os
import pyaedt

###############################################################################
# Set non-graphical mode
# ~~~~~~~~~~~~~~~~~~~~~~
# Set non-graphical mode. ``"PYAEDT_NON_GRAPHICAL"`` is needed to generate
# documentation only.
# You can set ``non_graphical`` either to ``True`` or ``False``.
# The ``NewThread`` Boolean variable defines whether to create a new instance
# of AEDT or try to connect to existing instance of it if one is available.

non_graphical = False
NewThread = False
desktop_version = "2022.2"


###############################################################################
# Launch AEDT with EMIT
# ~~~~~~~~~~~~~~~~~~~~~
# Launch AEDT with EMIT. The ``Desktop`` class initializes AEDT and starts it
# on the specified version and in the specified graphical mode.

d = pyaedt.launch_desktop(desktop_version, non_graphical, NewThread)
aedtapp = pyaedt.Emit(pyaedt.generate_unique_project_name())


###############################################################################
# Create and connect EMIT components
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Create three radios and connect an antenna to each one.

rad1 = aedtapp.modeler.components.create_component("New Radio")
ant1 = aedtapp.modeler.components.create_component("Antenna")
if rad1 and ant1:
    ant1.move_and_connect_to(rad1)

# Convenience method to create a radio and antenna connected together
rad2, ant2 = aedtapp.modeler.components.create_radio_antenna("GPS Receiver")
rad3, ant3 = aedtapp.modeler.components.create_radio_antenna("Bluetooth Low Energy (LE)", "Bluetooth")

###############################################################################
# Define coupling among RF systems
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Define the coupling among the RF systems. This portion of the EMIT API is not
# yet implemented.


###############################################################################
# Run EMIT simulation
# ~~~~~~~~~~~~~~~~~~~
# Run the EMIT simulation. 
#
# This part of the example requires Ansys AEDT 2023 R2. 
# Uncomment it and run on correct version.

# rev = aedtapp.analyze()
# modeRx = aedtapp.tx_rx_mode().rx
# modeTx = aedtapp.tx_rx_mode().tx
# modeEmi = aedtapp.result_type().emi
# rx_bands = aedtapp.results.get_band_names(rad2.name, modeRx) 
# tx_bands = aedtapp.results.get_band_names(rad3.name, modeTx) 
# domain = aedtapp.interaction_domain()
# domain.set_receiver(rad2.name, rx_bands[0], -1)
# domain.set_interferers([rad3.name],[tx_bands[0]],[-1])
# interaction = rev.run(domain)
# worst = interaction.get_worst_instance(modeEmi)
# if worst.has_valid_values():
#     emi = worst.get_value(modeEmi)
#     print("Worst case interference is: {} dB".format(emi))

###############################################################################
# Save project and close AEDT
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~
# After the simulation completes, you can close AEDT or release it using the
# :func:`pyaedt.Desktop.force_close_desktop` method.
# All methods provide for saving the project before closing.

aedtapp.save_project()
aedtapp.release_desktop(close_projects=True, close_desktop=True)
