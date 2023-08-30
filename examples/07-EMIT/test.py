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
#
# sphinx_gallery_thumbnail_path = "Resources/emit_simple_cosite.png"

import pyaedt
#from EmitApiPython import EmitApi, FilterProps, AntennaProps, RadioProps
from EmitApiPython import *
from pyaedt.emit_core.emit_constants import TxRxMode, ResultType


###############################################################################
# Set non-graphical mode
# ~~~~~~~~~~~~~~~~~~~~~~
# Set non-graphical mode. 
# You can set ``non_graphical`` either to ``True`` or ``False``.
# The ``NewThread`` Boolean variable defines whether to create a new instance
# of AEDT or try to connect to existing instance of it if one is available.

non_graphical = True
NewThread = True
desktop_version = "2023.2"

###############################################################################
# Launch AEDT with EMIT
# ~~~~~~~~~~~~~~~~~~~~~
# Launch AEDT with EMIT. The ``Desktop`` class initializes AEDT and starts it
# on the specified version and in the specified graphical mode.

d = pyaedt.launch_desktop(desktop_version, non_graphical, NewThread)
emitapp = pyaedt.Emit(pyaedt.generate_unique_project_name())

radio = emitapp.modeler.components.create_component("New Radio")
bn = radio.get_prop_nodes({"Type": "Band"})[0]
band_props = bn.props
bn._set_prop_value({"BitRate": "25e3"})

api = emitapp.get_api()

# create system 1
rad1 = api.create_radio("Rad1")
# r1p1 = rad1.get_antenna_side_ports()
# ant1 = api.create_antenna(rad1.get_name(), "Ant1")
# a1p1 = ant1.get_radio_side_ports()
#
# # create system 2
# rad2 = api.create_radio("Rad2")
# r2p1 = rad1.get_antenna_side_ports()
# ant2 = api.create_antenna(rad2.get_name(), "Ant2")
# a2p1 = ant2.get_radio_side_ports()

# connect the systems
# api.connect(rad1.get_name(), r1p1, ant1.get_name(), a1p1)
# api.connect(rad2.get_name(), r2p1, ant2.get_name(), a2p1)
name = rad1.get_property(RadioProps.name)
ct = rad1.get_property(RadioProps.comp_type)
ap = rad1.get_property(RadioProps.antenna_side_ports)
rp = rad1.get_property(RadioProps.radio_side_ports)

ant = api.create_antenna("Rad1", "ant")
subType = ant.get_property(AntennaProps.sub_type)

filt = api.create_filter("Rad1", "new")
subType = filt.get_property(FilterProps.sub_type)
insLoss = filt.get_property(FilterProps.insertion_loss)
filt.set_property(FilterProps.sub_type, "LowPass")
subType = filt.get_property(FilterProps.sub_type)

# run the simulation
eng = api.get_engine()
dom = emitapp.results.interaction_domain()
inst = eng.get_instance_count(dom)
print("Total Instances = {}".format(inst))
interaction = eng.run(dom)
worst = interaction.get_worst_instance(ResultType.EMI)
print("Worst EMI = {}".format(worst))


emitapp.release_desktop(close_projects=True, close_desktop=True)