"""

HFSS3DLayout Parametric Via Analysis
--------------------------------------------
This Example shows how to use HFSS3DLayout to create a parametric design, solve it and get results
"""
# sphinx_gallery_thumbnail_path = 'Resources/3dlayout.png'



#########################################
# Import Hfss3d Layout object and initialize it on version 2021.1
#

from pyaedt import Hfss3dLayout
import os
h3d = Hfss3dLayout(specified_version="2021.1", AlwaysNew=False)

#########################################
# Setup of all parametric variables will be used into the layout
#

h3d["viatotrace"]="5mm"
h3d["viatovia"]="10mm"
h3d["w1"]="1mm"
h3d["sp"]="0.5mm"
h3d["len"]="50mm"

#########################################
# Create a stackup
#

h3d.modeler.layers.add_layer("GND","signal",thickness="0", isnegative=True)
h3d.modeler.layers.add_layer("diel","dielectric",thickness="0.2mm",material="FR4_epoxy")
h3d.modeler.layers.add_layer("TOP","signal",thickness="0.035mm", elevation="0.2mm")

#########################################
# Create of signal net and ground planes
#

h3d.modeler.primitives.create_line("TOP", [[0,0],["len",0]],lw="w1", netname="microstrip", name="microstrip")
h3d.modeler.primitives.create_rectangle("TOP",[0,"-w1/2-sp"],["len","-w1/2-sp-20mm"])
h3d.modeler.primitives.create_rectangle("TOP",[0,"w1/2+sp"],["len","w1/2+sp+20mm"])

#########################################
# Create of vias with parametric position
#

h3d.modeler.primitives.create_via(x="viatovia",y="-viatotrace",name="via1")
h3d.modeler.primitives.create_via(x="viatovia",y="viatotrace", name="via2")
h3d.modeler.primitives.create_via(x="2*viatovia",y="-viatotrace")
h3d.modeler.primitives.create_via(x="2*viatovia",y="viatotrace")
h3d.modeler.primitives.create_via(x="3*viatovia",y="-viatotrace")
h3d.modeler.primitives.create_via(x="3*viatovia",y="viatotrace")

#########################################
# Add Circuit Ports to setup
#

h3d.create_edge_port("microstrip", 0)
h3d.create_edge_port("microstrip", 2)

#########################################
# Create setup and sweep
#

setup=h3d.create_setup()
h3d.create_frequency_sweep(setupname=setup.name, unit='GHz', freqstart=3, freqstop=7, num_of_freq_points=1001,
                                                   sweepname="sweep1", sweeptype="interpolating",
                                                   interpolation_tol_percent=1, interpolation_max_solutions=255,
                                                   save_fields=False, use_q3d_for_dc=False)
#########################################
# Solve and plot results
#

h3d.analyse_nominal()
h3d.post.create_rectangular_plot(["db(S(Port1,Port1))","db(S(Port1,Port2))"],families_dict=h3d.available_variations.nominal_w_values_dict)

#########################################
# Close Electronic Desktop
#
if os.name != "posix":
    h3d.close_desktop()
