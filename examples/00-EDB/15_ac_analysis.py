# # EDB: Network Analysis in SIwave
#
# This example shows how to use PyAEDT to set up SYZ analysis on a 
# [serdes](https://en.wikipedia.org/wiki/SerDes) channel.
# The signal input is applied differetially. The positive net is _"PCIe_Gen4_TX3_CAP_P"_.
# The negative net is _"PCIe_Gen4_TX3_CAP_N"_. In this example, ports are placed on the
# driver and
# receiver components.

# ### Perform required imports
#
# Perform required imports, which includes importing a section.

import time
import pyaedt
import tempfile

# ### Download file
#
# Download the AEDB file and copy it in the temporary folder.

temp_dir = tempfile.TemporaryDirectory(suffix=".ansys")
edb_full_path = pyaedt.downloads.download_file('edb/ANSYS-HSD_V1.aedb', destination=temp_dir.name)
time.sleep(5)

print(edb_full_path)

# ### Configure EDB
#
# Creat an instance of the `pyaedt.Edb` class.

edbapp = pyaedt.Edb(edbpath=edb_full_path, edbversion="2023.2")

# ### Generate extended nets
#
# An extended net is a connection between two nets that are connected
# through a passive component such as a resistor or capacitor.

all_nets = edbapp.extended_nets.auto_identify_signal(resistor_below=10, 
                                          inductor_below=1, 
                                          capacitor_above=1e-9)

# Review the properties of extended nets.

# +
diff_p = edbapp.nets["PCIe_Gen4_TX3_CAP_P"]
diff_n = edbapp.nets["PCIe_Gen4_TX3_CAP_N"]

nets_p = list(diff_p.extended_net.nets.keys())
nets_n = list(diff_n.extended_net.nets.keys())

comp_p = list(diff_p.extended_net.components.keys())
comp_n = list(diff_n.extended_net.components.keys())

rlc_p = list(diff_p.extended_net.rlc.keys())
rlc_n = list(diff_n.extended_net.rlc.keys())

print(comp_p, rlc_p, comp_n, rlc_n, sep="\n")
# -

# Prepare input data for port creation.

ports = []
for net_name, net_obj in diff_p.extended_net.nets.items():
    for comp_name, comp_obj in net_obj.components.items():
        if comp_obj.type not in ["Resistor", "Capacitor", "Inductor"]:
            ports.append({"port_name": "{}_{}".format(comp_name, net_name),
                          "comp_name":comp_name,
                          "net_name":net_name})

for net_name, net_obj in diff_n.extended_net.nets.items():
    for comp_name, comp_obj in net_obj.components.items():
        if comp_obj.type not in ["Resistor", "Capacitor", "Inductor"]:
            ports.append({"port_name": "{}_{}".format(comp_name, net_name),
                          "comp_name":comp_name,
                          "net_name":net_name})

print(*ports, sep="\n")

# ### Create ports
#
# Solder balls are generated automatically. The default port type is coax port.

for d in ports:
    port_name = d["port_name"]
    comp_name = d["comp_name"]
    net_name = d["net_name"]
    edbapp.components.create_port_on_component(component=comp_name,
                                               net_list=net_name,
                                               port_name=port_name
                                               )

# ### Cutout
#
# Retain only relevant parts of the layout.

nets = []
nets.extend(nets_p)
nets.extend(nets_n)
edbapp.cutout(signal_list=nets, reference_list=["GND"], extent_type="Bounding")

# Set up the model for network analysis in SIwave.

setup = edbapp.create_siwave_syz_setup("setup1")
setup.add_frequency_sweep(frequency_sweep=[
                               ["linear count", "0", "1kHz", 1],
                               ["log scale", "1kHz", "0.1GHz", 10],
                               ["linear scale", "0.1GHz", "10GHz", "0.1GHz"],
                               ])

# Save and close the EDB.

edbapp.save()
edbapp.close_edb()

# ### Launch Hfss3dLayout
#
# The HFSS 3D Layout user inteface in AEDT is used to import the EDB and
# run the analysis. AEDT 3D Layout can be used to view the model 
# if it is launched in graphical mode.

h3d = pyaedt.Hfss3dLayout(edb_full_path, 
                          specified_version="2023.2",
                          non_graphical=False,  # Set to true for non-graphical mode.
                          new_desktop_session=True)

# Define the differential pair.

h3d.set_differential_pair(positive_terminal="U1_PCIe_Gen4_TX3_CAP_P", 
                          negative_terminal="U1_PCIe_Gen4_TX3_CAP_N", 
                          diff_name="PAIR_U1")
h3d.set_differential_pair(positive_terminal="X1_PCIe_Gen4_TX3_P", 
                          negative_terminal="X1_PCIe_Gen4_TX3_N", 
                          diff_name="PAIR_X1")

# Solve and plot the results.

h3d.analyze(num_cores=4)

# Visualze the results.

h3d.post.create_report("dB(S(PAIR_U1,PAIR_U1))", context="Differential Pairs")

# Close AEDT.

h3d.save_project()
print("Project is saved to {}".format(h3d.project_path))
h3d.release_desktop(True, True)

# The following cell cleans up the temporary directory and removes all project data.

temp_dir.cleanup()
