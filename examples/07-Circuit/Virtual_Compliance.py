"""
Circuit: PCIE virtual compliance
--------------------------------
This example shows how to generate a compliance report in PyAEDT using
the ``VirtualCompliance`` class.
"""

###############################################################################
# Perform required imports
# ~~~~~~~~~~~~~~~~~~~~~~~~
# Perform required imports and set paths.

import os.path
import pyaedt
from pyaedt.generic.compliance import VirtualCompliance

##########################################################
# Set AEDT version
# ~~~~~~~~~~~~~~~~
# Set AEDT version.

aedt_version = "2024.1"

###############################################################################
# Set non-graphical mode
# ~~~~~~~~~~~~~~~~~~~~~~
# Set non-graphical mode.
# You can set ``non_graphical`` either to ``True`` or ``False``.
# The Boolean parameter ``new_thread`` defines whether to create a new instance
# of AEDT or try to connect to an existing instance of it.

non_graphical = True
new_thread = True

###############################################################################
# Download example files
# ~~~~~~~~~~~~~~~~~~~~~~
# Download the project and files needed to run the example.
workdir = pyaedt.downloads.download_file('pcie_compliance')

projectdir = os.path.join(workdir, "project")

###############################################################################
# Launch AEDT
# ~~~~~~~~~~~
# Launch AEDT.

d = pyaedt.Desktop(aedt_version, new_desktop_session=new_thread, non_graphical=non_graphical)

###############################################################################
# Open and solve layout
# ~~~~~~~~~~~~~~~~~~~~~
# Open the HFSS 3D Layout project and analyze it using the SIwave solver.
# Before solving, this code ensures that the model is solved from DC to 70GHz and that
# causality and passivity are enforced.

h3d = pyaedt.Hfss3dLayout(os.path.join(projectdir, "PCIE_GEN5_only_layout.aedtz"), specified_version=241)
h3d.remove_all_unused_definitions()
h3d.edit_cosim_options(simulate_missing_solution=False)
h3d.setups[0].sweeps[0].props["EnforcePassivity"] = True
h3d.setups[0].sweeps[0].props["Sweeps"]["Data"] = 'LIN 0MHz 70GHz 0.1GHz'
h3d.setups[0].sweeps[0].props["EnforceCausality"] = True
h3d.setups[0].sweeps[0].update()
h3d.analyze()
touchstone_path = h3d.export_touchstone()

###############################################################################
# Create LNA project
# ~~~~~~~~~~~~~~~~~~
# Use the LNA setup to retrieve Touchstone files
# and generate frequency domain reports.

cir = pyaedt.Circuit(projectname=h3d.project_name, designname="Touchstone")

###############################################################################
# Add dynamic link object
# ~~~~~~~~~~~~~~~~~~~~~~~
# Add the layout project as a dynamic link object
# so that if modifications are made, the circuit
# is always linked to the updated version of the results.

sub = cir.modeler.components.add_subcircuit_3dlayout("main_cutout")

###############################################################################
# Add ports and differential pairs
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Add a port for each layout port and rename it for circuit compatibility.
# Then, create differential pairs, which are useful for generating differential S-parameters.

ports = []
for pin in sub.pins:
    ports.append(cir.modeler.components.create_interface_port(name=pin.name.replace(".", "_"), location=pin.location))

for pin in ports:
    pin_name = pin.name.split("_")
    if pin_name[-1] == "P":
        component = pin_name[0]
        suffix = pin_name[-2] if "X" in pin_name[-2] else pin_name[-3]
        for neg_pin in ports:
            neg_pin_name = neg_pin.name.split("_")
            suffix_neg = neg_pin_name[-2] if "X" in neg_pin_name[-2] else neg_pin_name[-3]
            if neg_pin_name[0] == component and suffix_neg == suffix and neg_pin.name[-1] == "N":
                cir.set_differential_pair(
                    positive_terminal=pin.name,
                    negative_terminal=neg_pin.name,
                    common_name=f"COMMON_{component}_{suffix}",
                    diff_name=f"{component}_{suffix}",
                    common_ref_z=25,
                    diff_ref_z=100,
                    active=True,
                )
                break

###############################################################################
# Create setup, analyze, and plot
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Create a setup and then analyze and plot the data.

setup1 = cir.create_setup()
setup1.props["SweepDefinition"]["Data"] = "LINC 0GHz 70GHz 1001"

cir.analyze()

###############################################################################
# Create TDR project
# ~~~~~~~~~~~~~~~~~~
# Create a TDR project to compute transient simulation and retrieve
# the TDR measurement on a differential pair.
# The original circuit schematic is duplicated and modified to achieve this target.

cir.duplicate_design("TDR")
cir.set_active_design("TDR")

###############################################################################
# Replace ports with TDR probe
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Delete the ports on the selected differential pair.
# Place and connect a differential TDR probe to the pins of the layout object.

cir.modeler.components.delete_component("X1_A2_PCIe_Gen4_RX0_P")
cir.modeler.components.delete_component("IPort@X1_A3_PCIe_Gen4_RX0_N")
sub = cir.modeler.components.get_component("main_cutout1")

dif_end = cir.modeler.components.components_catalog["TDR_Differential_Ended"]

new_tdr_comp = dif_end.place("Tdr_probe", [-0.05, 0.01], angle=-90)
p_pin = [i for i in sub.pins if i.name.replace(".", "_") == "X1_A2_PCIe_Gen4_RX0_P"][0]
n_pin = [i for i in sub.pins if i.name.replace(".", "_") == "X1_A3_PCIe_Gen4_RX0_N"][0]
new_tdr_comp.pins[0].connect_to_component(p_pin)
new_tdr_comp.pins[1].connect_to_component(n_pin)
new_tdr_comp.parameters["Pulse_repetition"] = "2ms"
new_tdr_comp.parameters["Rise_time"] = "35ps"

###############################################################################
# Create setup, analyze, and plot
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# First, delete the LNA setup. Next, create a
# transient setup and then analyze and plot the data.

cir.delete_setup(cir.setups[0].name)
setup2 = cir.create_setup(setupname="MyTransient", setuptype=cir.SETUPS.NexximTransient)
setup2.props["TransientData"] = ["0.01ns", "10ns"]
cir.oanalysis.AddAnalysisOptions(["NAME:DataBlock", "DataBlockID:=", 8, "Name:=", "Nexxim Options",
                                  ["NAME:ModifiedOptions", "ts_convolution:=", True, ]])
setup2.props["OptionName"] = "Nexxim Options"
tdr_probe_name = f'O(A{new_tdr_comp.id}:zdiff)'
cir.analyze()

###############################################################################
# Create AMI project
# ~~~~~~~~~~~~~~~~~~
# Create an Ibis AMI project to compute an eye diagram simulation and retrieve
# eye mask violations.

cir = pyaedt.Circuit(projectname=h3d.project_name, designname="AMI")
sub = cir.modeler.components.create_touchstone_component(touchstone_path)

###############################################################################
# Replace ports with Ibis models
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Place and connect differential TX and RX Ibis models to the pins of the layout object.

p_pin1 = [i for i in sub.pins if i.name.replace(".", "_") == "U1_AM25_PCIe_Gen4_TX0_CAP_P"][0]
n_pin1 = [i for i in sub.pins if i.name.replace(".", "_") == "U1_AL25_PCIe_Gen4_TX0_CAP_N"][0]
p_pin2 = [i for i in sub.pins if i.name.replace(".", "_") == "X1_B2_PCIe_Gen4_TX0_P"][0]
n_pin2 = [i for i in sub.pins if i.name.replace(".", "_") == "X1_B3_PCIe_Gen4_TX0_N"][0]

ibis = cir.get_ibis_model_from_file(os.path.join(projectdir, "models", "pcieg5_32gt.ibs"), is_ami=True)
tx = ibis.components["Spec_Model"].pins["1p_Spec_Model_pcieg5_32gt_diff"].insert(-0.05, 0.01)
rx = ibis.components["Spec_Model"].pins["2p_Spec_Model_pcieg5_32gt_diff"].insert(0.05, 0.01, 180)

tx_eye_name = tx.parameters["probe_name"]

tx.pins[0].connect_to_component(p_pin1)
tx.pins[1].connect_to_component(n_pin1)
rx.pins[0].connect_to_component(p_pin2)
rx.pins[1].connect_to_component(n_pin2)
tx.parameters["UIorBPSValue"] = "31.25ps"
tx.parameters["BitPattern"] = "random_bit_count=2.5e3 random_seed=1"

###############################################################################
# Create setup, analyze, and plot
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# First delete the LNA setup. Next, create a
# transient setup and then analyze and plot the data.

setup_ami = cir.create_setup("AMI", "NexximAMI")
cir.oanalysis.AddAnalysisOptions(["NAME:DataBlock", "DataBlockID:=", 8, "Name:=", "Nexxim Options",
                                  ["NAME:ModifiedOptions", "ts_convolution:=", True, ]])
setup_ami.props["OptionName"] = "Nexxim Options"

setup_ami.props["DataBlockSize"] = 1000
setup_ami.analyze()
cir.save_project()

###############################################################################
# Create virtual compliance report
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Initialize the ``VirtualCompliance`` class
# and set up the main project information needed to generate the report.

template = os.path.join(workdir, "pcie_gen5_templates", "main.json")

v = VirtualCompliance(cir.desktop_class, str(template))

###############################################################################
# Customize project and design
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Define the path to the project file and the
# design names to be used in each report generation.

v.project_file = cir.project_file
v.reports["insertion losses"].design_name = "Touchstone"
v.reports["return losses"].design_name = "Touchstone"
v.reports["common mode return losses"].design_name = "Touchstone"
v.reports["tdr from circuit"].design_name = "TDR"
v.reports["eye1"].design_name = "AMI"
v.reports["eye3"].design_name = "AMI"
v.parameters["erl"].design_name = "Touchstone"
v.specs_folder = os.path.join(workdir, 'readme_pictures')

###############################################################################
# Define trace names
# ~~~~~~~~~~~~~~~~~~
# Change the trace name with projects and users.
# Reuse the compliance template and update traces accordingly.

v.reports["insertion losses"].traces = [
    "dB(S(U1_RX0,X1_RX0))",
    "dB(S(U1_RX1,X1_RX1))",
    "dB(S(U1_RX3,X1_RX3))"
]

v.reports["eye1"].traces = [tx_eye_name]
v.reports["eye3"].traces = [tx_eye_name]
v.reports["tdr from circuit"].traces = [tdr_probe_name]
v.parameters["erl"].trace_pins = [
    ["X1_A5_PCIe_Gen4_RX1_P", "X1_A6_PCIe_Gen4_RX1_N", "U1_AR25_PCIe_Gen4_RX1_P", "U1_AP25_PCIe_Gen4_RX1_N"],
    [7, 8, 18, 17]]

###############################################################################
# Generate PDF report
# ~~~~~~~~~~~~~~~~~~~~
# Generate the reports and produce a PDF report.

v.create_compliance_report()

d.release_desktop(True, True)
