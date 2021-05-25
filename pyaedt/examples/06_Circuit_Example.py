# ------------------------------------------------------------------------------
#
# This Example shows how to create and solve a Schemati Circuit using pyaedt
#
# -------------------------------------------------------------------------------

from pyaedt.core import Circuit
from pyaedt.core import Desktop


desktopVersion = "2021.1"
NonGraphical = False
NewThread = False

with Desktop(desktopVersion, NonGraphical, NewThread):
    aedtapp = Circuit()
    setup1 = aedtapp.create_setup("MyLNA")
    setup1.SweepDefinition = [('Variable', 'Freq'), ('Data', 'LINC 0GHz 4GHz 10001'), ('OffsetF1', False),
                              ('Synchronize', 0)]
    setup1.update()
    myindid, myind = aedtapp.modeler.components.create_inductor("L1", 1e-9, 0, 0)
    myresid, myres = aedtapp.modeler.components.create_resistor("R1", 50, 0.0254, 0)
    mycapid, mycap = aedtapp.modeler.components.create_capacitor("C1", 1e-12, 0.0400, 0)
    pins_res = aedtapp.modeler.components.get_pins(myres)

    ind1 = aedtapp.modeler.components[myind]
    ind1.set_location(-100, 0)
    res1 = aedtapp.modeler.components[myres]
    res1.set_location(700, 0)
    portid, portname = aedtapp.modeler.components.create_iport("myport", -0.0254, 0)
    gndid, gndname = aedtapp.modeler.components.create_gnd(0.0508, -0.00254)
    aedtapp.modeler.connect_schematic_components(portid, myindid)
    aedtapp.modeler.connect_schematic_components(myindid, myresid, pinnum_second=2)
    aedtapp.modeler.connect_schematic_components(myresid, mycapid, pinnum_first=1)
    aedtapp.modeler.connect_schematic_components(mycapid, gndid)
    setup2 = aedtapp.create_setup("MyTransient", aedtapp.SimulationSetupTypes.NexximTransient)
    setup2.TransientData = ["0.01ns", "200ns"]
    setup2.update()
    setup3 = aedtapp.create_setup("MyDC", aedtapp.SimulationSetupTypes.NexximDC)
    aedtapp.modeler.components.refresh_all_ids()
    aedtapp.analyze_setup("MyLNA")

print("Done")
