import os

from pyaedt import Circuit

cir = Circuit(specified_version="2022.1", new_desktop_session=True)
cir.desktop_install_dir
ibis = cir.get_ibis_model_from_file(os.path.join(cir.desktop_install_dir, 'buflib' ,'IBIS', 'u26a_800.ibs'))
ibs = ibis.buffers["DQ_u26a_800"].insert(0, 0)
ibs.parameters["BitPattern"]
tr1 = cir.modeler.components.components_catalog["Ideal Distributed:TRLK_NX"].place("tr1")
tr1.parameters["P"] = "50mm"
res = cir.modeler.components.create_resistor("R1", "1Meg")
gnd1 = cir.modeler.components.create_gnd()
tr1.parameters["P"] = "50mm"
tr1.pins[0].connect_to_component(ibs.pins[0])
tr1.pins[1].connect_to_component(res.pins[0])
res.pins[1].connect_to_component(gnd1.pins[0])
pr1 = cir.modeler.components.components_catalog["Probes:VPROBE"].place("vout")
pr1.parameters["Name"] = "Vout"
pr1.pins[0].connect_to_component(res.pins[0])
trans_setup = cir.create_setup("TransientRun", "NexximTransient")
trans_setup.props["TransientData"] = ["0.01ns", "200ns"]

cir.analyze_setup("TransientRun")
solutions = cir.post.get_solution_data("V(Vout)", domain="Time")
solutions.plot()

from matplotlib import pyplot as plt
import numpy as np

unit_interval = 1
offset = 0.25
tstop = 200
tstart = 0
t_steps = []
i = tstart + offset
while i < tstop:
    i += 2 * unit_interval
    t_steps.append(i)

t = [[i for i in solutions.sweeps["Time"] if k - 2 * unit_interval < i <= k ] for k in
     t_steps]
ys = [[i / 1000 for i, j in zip(solutions.data_real(), solutions.sweeps["Time"]) if
       k - 2 * unit_interval < j <= k ] for k in t_steps]
fig, ax = plt.subplots(sharex=True)
cellst = np.array([])
cellsv = np.array([])
for a, b in zip(t, ys):
    an = np.array(a)
    an = an - an.mean()
    bn = np.array(b)
    cellst = np.append(cellst, an)
    cellsv = np.append(cellsv, bn)
# plt.hist2d(cellst.T,  cellsv.T, (50, 50), cmap="inferno",zorder=10, alpha =0.5)
# plt.colorbar()
plt.plot(cellst.T,  cellsv.T,zorder=0)
plt.show()


new_report = cir.post.templates.standard("V(Vout)")
new_report.domain = "Time"
new_report.create()
new_report.time_start = "20ns"
new_report.time_stop = "100ns"
new_report.create()
sol = new_report.get_solution_data()
sol.plot()

new_eye = cir.post.templates.eye_diagram("V(Vout)")
new_eye.unit_interval = "1e-9s"
new_eye.time_stop = "100ns"
new_eye.create()

cir.post.create_report("V(Vout)", domain="Time")

cir.release_desktop(False, False)
