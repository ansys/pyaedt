# ------------------------------------------------------------------------------
#
# This Example shows how to create a setup in different tools
#
#
# -------------------------------------------------------------------------------
from pyaedt import Desktop
from pyaedt import Hfss
from pyaedt import Maxwell2d, Maxwell3d
from pyaedt import Icepak
from pyaedt import Q3d
from pyaedt import Circuit

with Desktop("2021.1"):
    q3d = Q3d()
    setup = q3d.create_setup("MyFirstQ3DSetup")
    hfss = Hfss()
    hfss.modeler.model_units = "cm"
    hfss["rad"] = "3mm"
    hfss["$h"] = "20mm"
    hfss.solution_type = hfss.SolutionTypes.Hfss.DrivenModal
    setup1 = hfss.create_setup("mysetup", hfss.SimulationSetupTypes.HFSSDrivenAuto)
    m2d = Maxwell2d()
    m2d.solution_type = m2d.SolutionTypes.Maxwell2d.TransientXY
    setup2 = m2d.create_setup()
    setup2.props['StopTime'] = "1ns"
    setup2.update()
    m3d = Maxwell3d()
    m3d.solution_type = m3d.SolutionTypes.Maxwell3d.Transient
    setup2 = m3d.create_setup()
    setup2.props['StopTime'] = "1ns"
    setup2.update()
    ipk = Icepak()
    ipk.solution_type = ipk.SolutionTypes.Icepak.SteadyTemperatureOnly
    setup3 = ipk.create_setup()
    setup3.props["Convergence Criteria - Max Iterations"] = 3
    setup3.update()
    ipk.solution_type = ipk.SolutionTypes.Icepak.SteadyTemperatureAndFlow
    cir = Circuit()
    setup4 = cir.create_setup("mysetup", hfss.SimulationSetupTypes.NexximDC)
    setup5 = cir.create_setup("mysetup2", hfss.SimulationSetupTypes.NexximLNA)
    pass

print("Done")
