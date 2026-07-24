from ansys.aedt.core import Hfss
import math

# -------------------------------------------------------------
# 1. Launch HFSS
# -------------------------------------------------------------
hfss = Hfss(
    project="DiffStripline_Weaved",
    design="Stripline_Weaved",
    solution_type="DrivenTerminal",
    new_desktop=True,
    non_graphical=False,
)
hfss.modeler.model_units = "mm"

# -------------------------------------------------------------
# 2. Design variables
#    100 Ω differential stripline:
#    W ≈ 0.11 mm,  S ≈ 0.15 mm  for 250 µm sub + 35 µm copper
# -------------------------------------------------------------
hfss["W"]  = "0.11mm"    # trace width  (tune for exact 100 Ω diff)
hfss["S"]  = "0.15mm"    # edge-to-edge gap
hfss["t"]  = "0.035mm"   # copper thickness
hfss["H"]  = "0.25mm"    # single dielectric thickness (top + bottom)

hfss["Ltot"]   = "10mm"
hfss["Pitch"]  = "W + S"
hfss["BoardW"] = "Ltot + 2mm"
hfss["BoardY"] = "4mm"

# -------------------------------------------------------------
# 3. Materials
# -------------------------------------------------------------
if "resin336" not in hfss.materials.material_keys:
    r = hfss.materials.add_material("resin336")
    r.permittivity = 3.36
    r.dielectric_loss_tangent = 0.004

# -------------------------------------------------------------
# 4. Stackup  (Z = 0 at bottom of bottom ground plane)
#
#   z5 ──── top GND (35 µm)         z = 2*H + 3*t  ..  2*H + 2*t
#   z4 ──── top substrate (250 µm)  z =   H + 2*t  ..  2*H + 2*t
#   z3 ──── signal traces (35 µm)   z =   H + t    ..  H   + 2*t
#   z2 ──── bot substrate (250 µm)  z =   t        ..  H   + t
#   z1 ──── bot GND (35 µm)         z =   0        ..  t
# -------------------------------------------------------------
H   = 0.25   # mm
t   = 0.035  # mm

z1_bot = 0.0
z2_bot = t
z3_bot = t + H
z4_bot = t + H + t
z5_bot = t + H + t + H

gnd_bot = hfss.modeler.create_box(
    origin=["-1mm", "-BoardY/2", f"{z1_bot}mm"],
    sizes=["BoardW", "BoardY", "t"],
    name="GND_Bot", material="copper",
)

sub_bot = hfss.modeler.create_box(
    origin=["-1mm", "-BoardY/2", f"{z2_bot}mm"],
    sizes=["BoardW", "BoardY", "H"],
    name="Sub_Bot", material="resin336",
)

sub_top = hfss.modeler.create_box(
    origin=["-1mm", "-BoardY/2", f"{z4_bot}mm"],
    sizes=["BoardW", "BoardY", "H"],
    name="Sub_Top", material="resin336",
)

gnd_top = hfss.modeler.create_box(
    origin=["-1mm", "-BoardY/2", f"{z5_bot}mm"],
    sizes=["BoardW", "BoardY", "t"],
    name="GND_Top", material="copper",
)

hfss.assign_finite_conductivity(gnd_bot.name, material="copper")
hfss.assign_finite_conductivity(gnd_top.name, material="copper")

# -------------------------------------------------------------
# 5. Signal traces — centred vertically in dielectric stack
#    z_trace_centre = t + H + t/2
# -------------------------------------------------------------
z_trace = f"{t + H + t / 2}mm"   # centre of trace layer

pointsP = [["-1mm", "Pitch/2",  z_trace], ["Ltot+1mm", "Pitch/2",  z_trace]]
pointsN = [["-1mm", "-Pitch/2", z_trace], ["Ltot+1mm", "-Pitch/2", z_trace]]

traceP = hfss.modeler.create_polyline(
    points=pointsP, name="TraceP", material="copper",
    xsection_type="Rectangle", xsection_width="W", xsection_height="t",
)
traceN = hfss.modeler.create_polyline(
    points=pointsN, name="TraceN", material="copper",
    xsection_type="Rectangle", xsection_width="W", xsection_height="t",
)

# -------------------------------------------------------------
# 6. Woven glass fill — one weave per substrate layer
# -------------------------------------------------------------
yarn_names_bot = hfss.modeler.define_weave(sub_bot, weave_style="7628", name_prefix="BotWeave",weave_rotate_deg=10)
#yarn_names_top = hfss.modeler.define_weave(sub_top, weave_style="1067", name_prefix="TopWeave")

print(f"[Weave] bot yarns: {len(yarn_names_bot)},  top yarns: {len(yarn_names_top)}")

# -------------------------------------------------------------
# 7. Wave ports — full stackup height (bot GND → top GND)
# -------------------------------------------------------------
port_h  = f"{z5_bot + t}mm"          # total board height
port_z0 = f"{z1_bot}mm"

port1 = hfss.modeler.create_rectangle(
    orientation="YZ",
    origin=["-1mm", "-2*Pitch", port_z0],
    sizes=["4*Pitch", port_h],
    name="Port1_sheet",
)
hfss.wave_port(
    assignment=port1.name, name="P1",
    reference=[gnd_bot.name, gnd_top.name],
    terminals_rename=True,
)

port2 = hfss.modeler.create_rectangle(
    orientation="YZ",
    origin=["Ltot+1mm", "-2*Pitch", port_z0],
    sizes=["4*Pitch", port_h],
    name="Port2_sheet",
)
hfss.wave_port(
    assignment=port2.name, name="P2",
    reference=[gnd_bot.name, gnd_top.name],
    terminals_rename=True,
)

# -------------------------------------------------------------
# 8. Differential pair definition
# -------------------------------------------------------------
hfss.set_differential_pair(
    assignment="P1_T1", reference="P1_T2",
    differential_mode="P1_diff", common_mode="P1_cmn",
    differential_reference=100, common_reference=25, active=True,
)
hfss.set_differential_pair(
    assignment="P2_T1", reference="P2_T2",
    differential_mode="P2_diff", common_mode="P2_cmn",
    differential_reference=100, common_reference=25, active=True,
)

# -------------------------------------------------------------
# 9. Airbox (minimal — GND planes shield most fields)
# -------------------------------------------------------------
airbox = hfss.modeler.create_box(
    origin=["-2mm", "-BoardY/2 - 1mm", f"{z1_bot - 0.5}mm"],
    sizes=["BoardW + 2mm", "BoardY + 2mm", f"{z5_bot + t + 1.0}mm"],
    name="Airbox", material="air",
)
hfss.assign_radiation_boundary_to_objects(airbox.name)

# -------------------------------------------------------------
# 10. Solution setup
# -------------------------------------------------------------
setup = hfss.create_setup(name="Setup1")
setup.props["Frequency"]     = "50GHz"
setup.props["MaximumPasses"] = 12
setup.props["MaxDeltaS"]     = 0.02
setup.props["BasisOrder"]    = 1
setup.props["SetTrianglesForWavePort"] = True
setup.props["MinTrianglesForWavePort"] = 500
setup.props["MaxTrianglesForWavePort"] = 2000
setup.update()
setup.create_frequency_sweep(
    unit="GHz", name="Sweep1",
    start_frequency=10, stop_frequency=50, num_of_freq_points=501,
    sweep_type="Interpolating",
)

# -------------------------------------------------------------
# 11. Fit + save
# -------------------------------------------------------------
hfss.modeler.fit_all()
hfss.save_project()

print("Done.")
total_h = z5_bot + t
print(f"  Total board thickness : {total_h:.3f} mm  ({total_h*1000:.1f} µm)")
print(f"  Trace Z centre        : {t + H + t/2:.4f} mm")
print(f"  Weave bot             : {len(yarn_names_bot)} yarns")
print(f"  Weave top             : {len(yarn_names_top)} yarns")