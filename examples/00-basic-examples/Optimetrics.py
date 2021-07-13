"""

Optimetrics Example Analysis
--------------------------------------------
This tutorial shows how you can use PyAedt to create a project in HFSS and create all optimetrics setup
"""
# sphinx_gallery_thumbnail_path = 'Resources/optimetrics.png'

from pyaedt import Hfss
from pyaedt import Desktop
import os
###################################
# Starting Desktop in Non-Graphical mode. User can change boolean to run in graphical mode

NG = False
d =Desktop("2021.1", NG=NG)

###################################
# Initialize Hfss object and creates needed design variables. Hfss will have 2 design variables w1 and w2

hfss = Hfss()
hfss["w1"] = "1mm"
hfss["w2"] = "100mm"

###################################
# Create waveguide and sheets on it. This method creates one of the standard waveguides structure and parametrize it.
# User may also create rectangles of WG openings to assign ports later

wg1, p1, p2= hfss.modeler.create_waveguide([0,0,0],hfss.CoordinateSystemAxis.YAxis,"WG17",wg_thickness="w1",wg_length="w2", create_sheets_on_openings=True)

###################################
# Create Wave ports on sheets

hfss.create_wave_port_from_sheet(p1, axisdir=hfss.AxisDir.ZPos, portname="1")
hfss.create_wave_port_from_sheet(p2, axisdir=hfss.AxisDir.ZPos, portname="2")

###################################
# Here we create a setup and a frequency sweep that will be used as base for Optimetrics setups

setup = hfss.create_setup()
hfss.create_linear_step_sweep(setupname=setup.name, unit='GHz', freqstart=1, freqstop=5, step_size=0.1,
                                                   sweepname="Sweep1", save_fields=True)
###################################
# Optimetrics Parametrics Setup
# ---------------------------------
# Simple parametrics analysis with output calculations


sweep = hfss.opti_parametric.add_parametric_setup("w2", "LIN 90mm 200mm 5mm")
sweep.add_variation("w1", "LIN 0.1mm 2mm 0.1mm")
sweep.add_calculation(calculation="dB(S(1,1))", calculation_value="2.5GHz", reporttype="Modal Solution Data")
sweep.add_calculation(calculation="dB(S(1,1))", calculation_value="2.6GHz", reporttype="Modal Solution Data")

###################################
# Optimetrics Sensitivity Setup
# ---------------------------------
# Sensitivity analysis with output calculations

sweep2 = hfss.opti_sensitivity.add_sensitivity(calculation="dB(S(1,1))", calculation_value="2.5GHz")
sweep2.add_calculation(calculation="dB(S(1,1))", calculation_value="2.6GHz")

###################################
# Optimetrics Optimization Setup
# ---------------------------------
# Optimization based on a goal and cal calculation

sweep3 = hfss.opti_optimization.add_optimization(calculation="dB(S(1,1))", calculation_value="2.5GHz")
sweep3.add_goal(calculation="dB(S(1,1))", calculation_value="2.6GHz")
sweep3.add_goal(calculation="dB(S(1,1))", calculation_value="2.6GHz", calculation_type="rd", calculation_stop="5GHz")
sweep3.add_goal(calculation="dB(S(1,1))", calculation_value="2.6GHz", calculation_type="rd", calculation_stop="5GHz",condition="Maximize")

###################################
# Optimetrics DX Setup
# ---------------------------------
# DX based on a goal and cal calculation

sweep4 = hfss.opti_designxplorer.add_dx_setup(variables_to_include=["w1"])
sweep4.add_goal(calculation="dB(S(1,1))", calculation_value="2.6GHz")

###################################
# Optimetrics DOE Setup
# ---------------------------------
# DOE based on a goal and cal calculation


sweep5 = hfss.opti_doe.add_doe(calculation="dB(S(1,1))", calculation_value="2.6GHz")
sweep5.add_goal(calculation="dB(S(1,1))", calculation_value="2.6GHz")
sweep5.add_calculation(calculation="dB(S(1,1))", calculation_value="2.5GHz")


###################################
# Close Desktop
# ---------------------------------
if os.name != "posix":
    d.force_close_desktop()


