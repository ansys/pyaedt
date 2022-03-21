"""
Optimetrics Setup
-----------------
This example shows how you can use PyAEDT to create a project in HFSS and create all optimetrics setups.
"""

from pyaedt import Hfss
from pyaedt import Desktop
import os

###############################################################################
# Launch AEDT in Non-Graphical Mode
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# You can change the Boolean parameter ``NonGraphical`` to ``False`` to launch
# AEDT in graphical mode.

NG = False
#d = Desktop("2022.1", non_graphical=NG, new_desktop_session=True)

###############################################################################
# Initialize the `Hfss` Object and Create the Needed Design Variables
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# In this example, HFSS is to have two design variables, ``w1`` and ``w2``.

hfss = Hfss(specified_version="2021.2", new_desktop_session=True, non_graphical=NG)
hfss["w1"] = "1mm"
hfss["w2"] = "100mm"

###############################################################################
# Create a Waveguide with Sheets on It
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# This method creates one of the standard waveguide structures and parametrizes it.
# You can also create rectangles of waveguide openings and assign ports later.

wg1, p1, p2 = hfss.modeler.create_waveguide(
    [0, 0, 0],
    hfss.AXIS.Y,
    "WG17",
    wg_thickness="w1",
    wg_length="w2",
    create_sheets_on_openings=True,
)

model = hfss.plot(show=False)

model.show_grid = False
model.plot(os.path.join(hfss.working_directory, "Image.jpg"))

###############################################################################
# Create Wave Ports on the Sheets
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# This example creates two wave ports on the sheets.

hfss.create_wave_port_from_sheet(p1, axisdir=hfss.AxisDir.ZPos, portname="1")
hfss.create_wave_port_from_sheet(p2, axisdir=hfss.AxisDir.ZPos, portname="2")

###############################################################################
# Create a Setup and a Frequency Sweep
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# This example creates a setup and a frequency sweep to use as the base for
# Optimetrics setups.

setup = hfss.create_setup()
hfss.create_linear_step_sweep(
    setupname=setup.name, unit="GHz", freqstart=1, freqstop=5, step_size=0.1, sweepname="Sweep1", save_fields=True
)

###############################################################################
# Optimetrics Parametrics Setup
# -----------------------------
# Simple Parametrics Analysis with Output Calculations
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# This example creates a simple parametrics analysis with output calculations.

sweep = hfss.parametrics.add({"w2": "LIN 90mm 200mm 5mm"})
sweep.add_variation("w1", "LIN 0.1mm 2mm 0.1mm")
sweep.add_calculation(calculation="dB(S(1,1))", calculation_value="2.5GHz", reporttype="Modal Solution Data")
sweep.add_calculation(calculation="dB(S(1,1))", calculation_value="2.6GHz", reporttype="Modal Solution Data")

###############################################################################
# Optimetrics Sensitivity Setup
# -----------------------------
# Sensitivity Analysis with Output Calculations
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# This example creates a sensitivity analysis with output calculations.

sweep2 = hfss.optimizations.add(calculation="dB(S(1,1))", intrinsics={"Freq":"2.5GHz"}, optim_type="Sensitivity")
sweep2.add_calculation(calculation="dB(S(1,1))", calculation_value="2.6GHz")

###############################################################################
# Optimetrics Optimization Setup
# ------------------------------
# Optimization Based on Goals and Calculations
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# This example creates an optimization based on goals and calculations.

sweep3 = hfss.optimizations.add(calculation="dB(S(1,1))", intrinsics={"Freq":"2.5GHz"})
sweep3.add_goal(calculation="dB(S(1,1))", calculation_value="2.6GHz")
sweep3.add_goal(calculation="dB(S(1,1))", calculation_value="2.6GHz", calculation_type="rd", calculation_stop="5GHz")
sweep3.add_goal(
    calculation="dB(S(1,1))",
    calculation_value="2.6GHz",
    calculation_type="rd",
    calculation_stop="5GHz",
    condition="Maximize",
)

###############################################################################
# Optimetrics DesignXplorer (DX) Setup
# ------------------------------------
# DX Optimization Based on a Goal and a Calculation
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# This example creates a DX optimization based on a goal and a calculation.

sweep4 = hfss.optimizations.add(calculation="dB(S(1,1))", intrinsics={"Freq": "2.5GHz"}, optim_type="DesignExplorer")
sweep4.add_goal(calculation="dB(S(1,1))", calculation_value="2.6GHz")

###############################################################################
# Optimetrics DOE (Design of Experiments) Setup
# ---------------------------------------------
# DOE Based on a Goal and a Calculation
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# This example creates a DOE based on a goal and a calculation.

sweep5 = hfss.optimizations.add(calculation="dB(S(1,1))", intrinsics={"Freq": "2.6GHz"}, optim_type="DXDOE")
sweep5.add_goal(calculation="dB(S(1,1))", calculation_value="2.6GHz")
sweep5.add_calculation(calculation="dB(S(1,1))", calculation_value="2.5GHz")

###############################################################################
# Optimetrics ODOE (Design of Experiments) Setup
# ---------------------------------------------
# DOE Based on a Goal and a Calculation
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# This example creates a DOE based on a goal and a calculation.

region = hfss.modeler.create_region()
hfss.assign_radiation_boundary_to_objects(region)
hfss.insert_infinite_sphere(name="Infinite_1")
sweep6 = hfss.optimizations.add(calculation="RealizedGainTotal", solution=hfss.nominal_adaptive,
                                intrinsics={"Freq": "5GHz", "Theta": "0deg", "Phi": "0deg"}, context="Infinite_1")

###############################################################################
# Close AEDT
# ----------
# After the simulaton is completed, you can close AEDT or release it using the
# :func:`pyaedt.Desktop.release_desktop` method.
# All methods provide for saving the project before exiting.

if os.name != "posix":
    d.release_desktop()
