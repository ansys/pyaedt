"""
Maxwell 2d: Magnet DC Analysis
------------------------------
This example shows how you can use PyAEDT to create a Maxwell DC Analysis,
compute mass center and move Coordinate Systems.
"""

#################################################################################
# Import packages
from math import sqrt as mysqrt
import os
import csv
import tempfile

from pyaedt import Maxwell2d
from pyaedt import examples
from pyaedt.generic.general_methods import generate_unique_name

# initialization: version, path project and design nameand type
desktopVersion = "2022.1"

sName = "MySetupAuto"
sType = "TransientXY"
pName = "Example_inline"
tmpfold = tempfile.gettempdir()
pathName = os.path.join(tmpfold, generate_unique_name("Example"))
dName = "NissanLeaf_Sinusoidal_inline"

# initialization: parameters
geom_params = {  # geometry
    "DiaGap": "132mm",
    "DiaStatorYoke": "198mm",
    "DiaStatorInner": "132mm",
    "DiaRotorLam": "130mm",
    "DiaShaft": "44.45mm",
    "DiaOuter": "198mm",
    "Airgap": "1mm",
    "SlotNumber": "48",
    "SlotType": "3"
}
wind_params = {  # winding definitions
    "Layers": "1",
    "ParallelPaths": "2",
    "R_Phase": "7.5mOhm",
    "WdgExt_F": "5mm",
    "SpanExt": "30mm",
    "SegAngle": "0.25",
    "CoilPitch": "5",  # coil pitch in slots
    "Coil_SetBack": "3.605732823mm",
    "SlotWidth": "2.814mm",  # RMxprt Bs0
    "Coil_Edge_Short": "3.769235435mm",
    "Coil_Edge_Long": "15.37828521mm"
}
mod_params = {  # modelling parameters
    "NumPoles": "8",
    "Model_Length": "80mm",
    "SymmetryFactor": "8",
    "Magnetic_Axial_Length": "150mm",
    "Stator_Lam_Length": "0mm",
    "StatorSkewAngle": "0deg",
    "NumTorquePointsPerCycle": "30",
    "mapping_angle": "0.125*4deg",
    "num_m": "16",
    "Section_Angle": "360deg/SymmetryFactor"
}
oper_params = {  # operating point
    "InitialPositionMD": "180deg/4",
    "IPeak": "480A",
    "MachineRPM": "3000rpm",
    "ElectricFrequency": "MachineRPM/60rpm*NumPoles/2*1Hz",
    "ElectricPeriod": "1Hz/ElectricFrequency",
    "BandTicksinModel": "360deg/NumPoles/mapping_angle",
    "TimeStep": "ElectricPeriod/(2*BandTicksinModel)",
    "StopTime": "2*ElectricPeriod",
    "Theta_i": "135deg"
}
output_vars = {  # output variables
    "Current_A": "InputCurrent(Phase_A)",
    "Current_B": "InputCurrent(Phase_B)",
    "Current_C": "InputCurrent(Phase_C)",
    "Flux_A": "FluxLinkage(Phase_A)",
    "Flux_B": "FluxLinkage(Phase_B)",
    "Flux_C": "FluxLinkage(Phase_C)",
    "pos": "(Moving1.Position -InitialPositionMD) *NumPoles/2",
    "cos0": "cos(pos)",
    "cos1": "cos(pos-2*PI/3)",
    "cos2": "cos(pos-4*PI/3)",
    "sin0": "sin(pos)",
    "sin1": "sin(pos-2*PI/3)",
    "sin2": "sin(pos-4*PI/3)",
    "Flux_d": "2/3*(Flux_A*cos0+Flux_B*cos1+Flux_C*cos2)",
    "Flux_q": "-2/3*(Flux_A*sin0+Flux_B*sin1+Flux_C*sin2)",
    "I_d": "2/3*(Current_A*cos0 + Current_B*cos1 + Current_C*cos2)",
    "I_q": "-2/3*(Current_A*sin0 + Current_B*sin1 + Current_C*sin2)",
    "Irms": "sqrt(I_d^2+I_q^2)/sqrt(2)",
    "ArmatureOhmicLoss_DC": "Irms^2*R_phase",
    "Lad": "L(Phase_A,Phase_A)*cos0 + L(Phase_A,Phase_B)*cos1 + L(Phase_A,Phase_C)*cos2",
    "Laq": "L(Phase_A,Phase_A)*sin0 + L(Phase_A,Phase_B)*sin1 + L(Phase_A,Phase_C)*sin2",
    "Lbd": "L(Phase_B,Phase_A)*cos0 + L(Phase_B,Phase_B)*cos1 + L(Phase_B,Phase_C)*cos2",
    "Lbq": "L(Phase_B,Phase_A)*sin0 + L(Phase_B,Phase_B)*sin1 + L(Phase_B,Phase_C)*sin2",
    "Lcd": "L(Phase_C,Phase_A)*cos0 + L(Phase_C,Phase_B)*cos1 + L(Phase_C,Phase_C)*cos2",
    "Lcq": "L(Phase_C,Phase_A)*sin0 + L(Phase_C,Phase_B)*sin1 + L(Phase_C,Phase_C)*sin2",
    "L_d": "(Lad*cos0 + Lbd*cos1 + Lcd*cos2) * 2/3",
    "L_q": "(Laq*sin0 + Lbq*sin1 + Lcq*sin2) * 2/3",
    "OutputPower": "Moving1.Speed*Moving1.Torque",
    "Ui_A": "InducedVoltage(Phase_A)",
    "Ui_B": "InducedVoltage(Phase_B)",
    "Ui_C": "InducedVoltage(Phase_C)",
    "Ui_d": "2/3*(Ui_A*cos0 + Ui_B*cos1 + Ui_C*cos2)",
    "Ui_q": "-2/3*(Ui_A*sin0 + Ui_B*sin1 + Ui_C*sin2)",
    "U_A": "Ui_A+R_Phase*Current_A",
    "U_B": "Ui_B+R_Phase*Current_B",
    "U_C": "Ui_C+R_Phase*Current_C",
    "U_d": "2/3*(U_A*cos0 + U_B*cos1 + U_C*cos2)",
    "U_q": "-2/3*(U_A*sin0 + U_B*sin1 + U_C*sin2)"
}
post_params = {  # reports
    "Moving1.Torque": "TorquePlots"
}
post_params_multiplot = {  # reports
    ("U_A", "U_B", "U_C", "Ui_A", "Ui_B", "Ui_C"): "PhaseVoltages",
    ("CoreLoss", "SolidLoss", "ArmatureOhmicLoss_DC"): "Losses",
    ("InputCurrent(Phase_A)", "InputCurrent(Phase_B)", "InputCurrent(Phase_C)"): "PhaseCurrents",
    ("FluxLinkage(Phase_A)", "FluxLinkage(Phase_B)", "FluxLinkage(Phase_C)"): "PhaseFluxes",
    ("I_d", "I_q"): "Currents_dq",
    ("Flux_d", "Flux_q"): "Fluxes_dq",
    ("Ui_d", "Ui_q"): "InducedVoltages_dq",
    ("U_d", "U_q"): "Voltages_dq",
    ("L(Phase_A,Phase_A)", "L(Phase_B,Phase_B)", "L(Phase_C,Phase_C)", "L(Phase_A,Phase_B)", "L(Phase_A,Phase_C)",
     "L(Phase_B,Phase_C)"): "PhaseInductances",
    ("L_d", "L_q"): "Inductances_dq",
    ("CoreLoss", "CoreLoss(Stator)", "CoreLoss(Rotor)"): "CoreLosses",
    ("EddyCurrentLoss", "EddyCurrentLoss(Stator)", "EddyCurrentLoss(Rotor)"): "EddyCurrentLosses (Core)",
    ("ExcessLoss", "ExcessLoss(Stator)", "ExcessLoss(Rotor)"): "ExcessLosses (Core)",
    ("HysteresisLoss", "HysteresisLoss(Stator)", "HysteresisLoss(Rotor)"): "HysteresisLosses (Core)",
    ("SolidLoss", "SolidLoss(IPM1)", "SolidLoss(IPM1_1)", "SolidLoss(OPM1)", "SolidLoss(OPM1_1)"): "SolidLoss"
}

##########################################################
# Set Non Graphical Mode.
# Default is False

non_graphical = os.getenv("PYAEDT_NON_GRAPHICAL", "False").lower() in ("true", "1", "t")

#launch Maxwell 2D
M2D = Maxwell2d(specified_version="2022.1", designname=dName, solution_type=sType, new_desktop_session=False, non_graphical=non_graphical)
mod2D = M2D.modeler
mod2D.delete()
mod2D.model_units = "mm"

# define design variables from the created dictionaries of paramters
for k, v in geom_params.items():
    M2D[k] = v
for k, v in wind_params.items():
    M2D[k] = v
for k, v in mod_params.items():
    M2D[k] = v
for k, v in oper_params.items():
    M2D[k] = v

# create materials
################################
filename_PM, filename_lam = examples.download_leaf()

mat_coils = M2D.materials.add_material("Copper (Annealed)_65C")
mat_coils.update()
mat_coils.conductivity = "49288048.9198"
mat_coils.permeability = "1"

mat_PM = M2D.materials.add_material("Arnold_Magnetics_N30UH_80C_new")
mat_PM.update()
mat_PM.conductivity = "555555.5556"
mat_PM.set_magnetic_coercitivity(7500, 1, 0, 0)
mat_PM.mass_density = "7500"
BH_List_PM = []
with open(filename_PM) as f:
    reader = csv.reader(f, delimiter='\t')
    next(reader)
    for row in reader:
        BH_List_PM.append([float(row[0]), float(row[1])])
mat_PM.permeability.set_non_linear(BH_List_PM)

mat_lam = M2D.materials.add_material("30DH_20C_smooth")
mat_lam.update()
mat_lam.conductivity = "1694915.25424"
kh = 71.7180985413
kc = 0.25092214579
ke = 12.1625774023
kdc = 0.001
eq_depth = 0.001
mat_lam.set_electrical_steel_coreloss(kh, kc, ke, kdc, eq_depth)
mat_lam.mass_density = "7650"
BH_List_lam = []
with open(filename_lam) as f:
    reader = csv.reader(f, delimiter='\t')
    next(reader)
    for row in reader:
        BH_List_lam.append([float(row[0]), float(row[1])])
mat_lam.permeability.set_non_linear(BH_List_lam)

# GEOMETRY
###############################
# create stator
udp_par_list_stator = [["DiaGap", "DiaGap"], ["DiaYoke", "DiaStatorYoke"], ["Length", "Stator_Lam_Length"],
                       ["Skew", "StatorSkewAngle"], ["Slots", "SlotNumber"], ["SlotType", "SlotType"],
                       ["Hs0", "1.2mm"], ["Hs01", "0mm"], ["Hs1", "0.4834227384999mm"],
                       ["Hs2", "17.287669825502mm"],
                       ["Bs0", "2.814mm"], ["Bs1", "4.71154109036mm"], ["Bs2", "6.9777285790998mm"], ["Rs", "2mm"],
                       ["FilletType", "1"], ["HalfSlot", "0"], ["VentHoles", "0"], ["HoleDiaIn", "0mm"],
                       ["HoleDiaOut", "0mm"],
                       ["HoleLocIn", "0mm"], ["HoleLocOut", "0mm"], ["VentDucts", "0"], ["DuctWidth", "0mm"],
                       ["DuctPitch", "0mm"],
                       ["SegAngle", "0deg"], ["LenRegion", "Model_Length"], ["InfoCore", "0"]]

stator_id = mod2D.create_udp(udp_dll_name="RMxprt/VentSlotCore.dll",
                             udp_parameters_list=udp_par_list_stator, upd_library='syslib',
                             name='my_stator', udp_type='Solid')  # name not taken
M2D.assign_material(stator_id, "30DH_20C_smooth")
stator_id.name = "Stator"
stator_id.color = (0, 0, 255)  # rgb
stator_id.solve_inside = True  # to be reassigned: M2D.assign material puts False if not dielectric
###############################
# create permanent magnets

def find_elements(lst1, lst2):
    return [lst1[i] for i in lst2]


def find_n_largest(input_len_list, n_largest_edges):
    tmp = list(input_len_list)
    copied = list(input_len_list)
    copied.sort()  # sort list so that largest elements are on the far right
    index_list = []
    for n in range(1, n_largest_edges + 1):  # get index of the Nth largest element
        index_list.append(tmp.index(copied[-n]))
        tmp[tmp.index(copied[-n])] = 0  # index can only get the first occurrence, that solves the problem
    return index_list


def create_cs_magnets(pm_id, cs_name, point_direction):
    pm_face_id = mod2D.get_object_faces(pm_id.name)[0]  # works with name only
    pm_edges = mod2D.get_object_edges(pm_id.name)
    edge_len_list = list(
        map(mod2D.get_edge_length, pm_edges))  # apply method get_edge_length to all elements of list pm_edges
    index_2_longest = find_n_largest(edge_len_list, 2)  # find the 2 longest edges
    longest_edge_list = find_elements(pm_edges, index_2_longest)
    edge_center_list = list(map(mod2D.get_edge_midpoint,
                                longest_edge_list))  # apply method get_edge_midpoint to all elements of list longest_edge_list

    rad = lambda x: mysqrt(x[0] * x[0] + x[1] * x[1] + x[2] * x[2])
    index_largest_r = find_n_largest(list(map(rad, edge_center_list)), 2)
    longest_edge_list2 = [longest_edge_list[i] for i in index_largest_r]  # reorder: outer first element of the list
    if point_direction == 'outer':
        my_axis_pos = longest_edge_list2[0]
    elif point_direction == 'inner':
        my_axis_pos = longest_edge_list2[1]

    mod2D.create_face_coordinate_system(face=pm_face_id, origin=pm_face_id, axis_position=my_axis_pos,
                                        axis="X", name=cs_name)
    pm_id.part_coordinate_system = cs_name
    mod2D.set_working_coordinate_system('Global')
# create permanent magnets
IM1_points = [[56.70957112, 3.104886585, 0], [40.25081875, 16.67243502, 0], [38.59701538, 14.66621111, 0],
              [55.05576774, 1.098662669, 0]]
OM1_points = [[54.37758185, 22.52393189, 0], [59.69688156, 9.68200639, 0], [63.26490432, 11.15992981, 0],
              [57.94560461, 24.00185531, 0]]
IPM1_id = mod2D.create_polyline(position_list=IM1_points, cover_surface=True, name="PM_I1",
                                matname="Arnold_Magnetics_N30UH_80C_new")
IPM1_id.color = (0, 128, 64)
OPM1_id = mod2D.create_polyline(position_list=OM1_points, cover_surface=True, name="PM_O1",
                                matname="Arnold_Magnetics_N30UH_80C_new")
OPM1_id.color = (0, 128, 64)
# create coordinate systems for magnets in the face center
create_cs_magnets(IPM1_id, 'CS_' + IPM1_id.name, 'outer')
create_cs_magnets(OPM1_id, 'CS_' + OPM1_id.name, 'outer')
mod2D.duplicate_and_mirror([IPM1_id, OPM1_id], position=[0, 0, 0],
                           vector=["cos((360deg/SymmetryFactor/2)+90deg)",
                                   "sin((360deg/SymmetryFactor/2)+90deg)", 0],
                           is_3d_comp=True)
id_PMs = mod2D.get_objects_w_string("PM", case_sensitive=True)
###############################
# create coils
coil_id = mod2D.create_rectangle(position=['DiaRotorLam/2+Airgap+Coil_SetBack', '-Coil_Edge_Short/2', 0],
                                 dimension_list=['Coil_Edge_Long', 'Coil_Edge_Short', 0],
                                 name='Coil', matname="Copper (Annealed)_65C")
coil_id.color = (255, 128, 0)
M2D.modeler.rotate(objid=coil_id, cs_axis="Z", angle="360deg/SlotNumber/2")
coil_id.duplicate_around_axis(cs_axis="Z", angle="360deg/SlotNumber", nclones='CoilPitch+1',
                              create_new_objects=True)
id_coils = mod2D.get_objects_w_string("Coil", case_sensitive=True)
###############################
# create bands, shaft and region
region_id = mod2D.create_circle(position=[0, 0, 0], radius='DiaOuter/2',
                                num_sides='SegAngle', is_covered=True, name='Region')
shaft_id = mod2D.create_circle(position=[0, 0, 0], radius='DiaShaft/2',
                               num_sides='SegAngle', is_covered=True, name='Shaft')

bandIN_id = mod2D.create_circle(position=[0, 0, 0], radius='(DiaGap - (1.5 * Airgap))/2',
                                num_sides='mapping_angle', is_covered=True, name='RotatingBand_in')
bandMID_id = mod2D.create_circle(position=[0, 0, 0], radius='(DiaGap - (1.0 * Airgap))/2',
                                 num_sides='mapping_angle', is_covered=True, name='RotatingBand_mid')
bandOUT_id = mod2D.create_circle(position=[0, 0, 0], radius='(DiaGap - (0.5 * Airgap))/2',
                                 num_sides='mapping_angle', is_covered=True, name='RotatingBand_out')

M2D.assign_rotate_motion('RotatingBand_mid', coordinate_system="Global", axis="Z", positive_movement=True,
                         start_position="InitialPositionMD", angular_velocity="MachineRPM")

vacuum_obj_id = [shaft_id, region_id, bandIN_id, bandMID_id, bandOUT_id]  # put shaft first
for item in vacuum_obj_id:
    item.color = (128, 255, 255)
###############################
# create rotor
rotor_id = mod2D.create_circle(position=[0, 0, 0], radius='DiaRotorLam/2',
                               num_sides=0, name="Rotor", matname="30DH_20C_smooth")
rotor_id.color = (0, 128, 255)
mod2D.subtract(rotor_id, shaft_id, keepOriginals=True)
void_small_1_id = mod2D.create_circle(position=[62, 0, 0], radius="2.55mm",
                                      num_sides=0, name="void1", matname="vacuum")
M2D.modeler.duplicate_around_axis(void_small_1_id, cs_axis="Z", angle="360deg/SymmetryFactor",
                                  nclones=2, create_new_objects=False)
void_big_1_id = mod2D.create_circle(position=[29.5643, 12.234389332712, 0], radius='9.88mm/2',
                                    num_sides=0, name="void_big", matname="vacuum")
mod2D.subtract(rotor_id, [void_small_1_id, void_big_1_id], keepOriginals=False)

slot_IM1_points = [[37.5302872, 15.54555396, 0], [55.05576774, 1.098662669, 0], [57.33637589, 1.25, 0],
                   [57.28982158, 2.626565019, 0], [40.25081875, 16.67243502, 0]]
slot_OM1_points = [[54.37758185, 22.52393189, 0], [59.69688156, 9.68200639, 0], [63.53825619, 10.5, 0],
                   [57.94560461, 24.00185531, 0]]
slot_IM_id = mod2D.create_polyline(position_list=slot_IM1_points, cover_surface=True, name="slot_IM1",
                                   matname="vacuum")
slot_OM_id = mod2D.create_polyline(position_list=slot_OM1_points, cover_surface=True, name="slot_OM1",
                                   matname="vacuum")

M2D.modeler.duplicate_and_mirror([slot_IM_id, slot_OM_id], position=[0, 0, 0],
                                 vector=["cos((360deg/SymmetryFactor/2)+90deg)",
                                         "sin((360deg/SymmetryFactor/2)+90deg)", 0],
                                 is_3d_comp=True)

id_holes = mod2D.get_objects_w_string("slot_", case_sensitive=True)
M2D.modeler.subtract(rotor_id, id_holes, keepOriginals=True)
###############################
# create section
object_list = [stator_id, rotor_id]+ vacuum_obj_id
mod2D.create_coordinate_system(origin=[0, 0, 0],
                               reference_cs="Global",
                               name="Section",
                               mode="axis",
                               x_pointing=["cos(360deg/SymmetryFactor)", "sin(360deg/SymmetryFactor)", 0],
                               y_pointing=["-sin(360deg/SymmetryFactor)", "cos(360deg/SymmetryFactor)", 0])

mod2D.set_working_coordinate_system("Section")
mod2D.split(object_list, "ZX", sides="NegativeOnly")
mod2D.set_working_coordinate_system("Global")
mod2D.split(object_list, "ZX", sides="PositiveOnly")


# SETUP
###############################
# create boundary conditions
pos_1 = "((DiaGap - (1.0 * Airgap))/4)"
id_bc_1 = mod2D.get_edgeid_from_position([pos_1, 0, 0], obj_name='Region')
id_bc_2 = mod2D.get_edgeid_from_position(
    [pos_1 + "*cos((360deg/SymmetryFactor))", pos_1 + "*sin((360deg/SymmetryFactor))", 0],
    obj_name='Region')
M2D.assign_master_slave(master_edge=id_bc_1, slave_edge=id_bc_2,
                        reverse_master=False,
                        reverse_slave=True,
                        same_as_master=False,
                        bound_name="Matching")
pos_2 = "(DiaOuter/2)"
id_bc_az = mod2D.get_edgeid_from_position(
    [pos_2 + "*cos((360deg/SymmetryFactor/2))", pos_2 + "*sin((360deg/SymmetryFactor)/2)", 0],
    obj_name='Region')
M2D.assign_vector_potential(id_bc_az, vectorvalue=0, bound_name="VectorPotentialZero")
###############################
# create windings
###############################
PhA_current = "IPeak * cos(2*pi*ElectricFrequency*time+Theta_i)"
PhB_current = "IPeak * cos(2*pi * ElectricFrequency*time - 120deg+Theta_i)"
PhC_current = "IPeak * cos(2*pi * ElectricFrequency*time - 240deg+Theta_i)"

# Phase_A
M2D.assign_coil(["Coil"], conductor_number=6, polarity="Positive", name="CT_Ph1_P2_C1_Go")
M2D.assign_coil(["Coil_5"], conductor_number=6, polarity="Negative", name="CT_Ph1_P2_C1_Ret")
M2D.assign_winding(coil_terminals=None, winding_type="Current", is_solid=False,
                   current_value=PhA_current, parallel_branches=1, name="Phase_A")
M2D.add_winding_coils("Phase_A", ["CT_Ph1_P2_C1_Go", "CT_Ph1_P2_C1_Ret"])

# Phase_B
M2D.assign_coil("Coil_3", conductor_number=6, polarity="Positive", name="CT_Ph3_P1_C2_Go")
M2D.assign_coil("Coil_4", conductor_number=6, polarity="Positive", name="CT_Ph3_P1_C1_Go")
M2D.assign_winding(coil_terminals=None, winding_type="Current", is_solid=False,
                   current_value=PhB_current, parallel_branches=1,
                   name="Phase_B")
M2D.add_winding_coils("Phase_B", ["CT_Ph3_P1_C2_Go", "CT_Ph3_P1_C1_Go"])

# Phase_C
M2D.assign_coil("Coil_1", conductor_number=6, polarity="Negative", name="CT_Ph2_P2_C2_Ret")
M2D.assign_coil("Coil_2", conductor_number=6, polarity="Negative", name="CT_Ph2_P2_C1_Ret")
M2D.assign_winding(coil_terminals=None, winding_type="Current", is_solid=False,
                   current_value=PhC_current, parallel_branches=1,
                   name="Phase_C")
M2D.add_winding_coils("Phase_C", ["CT_Ph2_P2_C2_Ret", "CT_Ph2_P2_C1_Ret"])

# total zero current on PMs
PM_list = id_PMs
for item in PM_list:
    M2D.assign_current(item, amplitude=0, solid=True, name=item + "_I0")
###############################



###############################
# create mesh operations
M2D.mesh.assign_length_mesh(id_coils, isinside=True, maxlength=3, maxel=None, meshop_name="coils")
M2D.mesh.assign_length_mesh(stator_id, isinside=True, maxlength=3, maxel=None, meshop_name="stator")
M2D.mesh.assign_length_mesh(rotor_id, isinside=True, maxlength=3, maxel=None, meshop_name="rotor")
###############################

###############################
#design settings and setup
###############################
# create_eddy_loss_settings
#M2D.eddy_effects_on(eddy_effects_list,activate_eddy_effects=True, activate_displacement_current=False)

# create_core_loss_settings
core_loss_list= ['Rotor', 'Stator']
M2D.set_core_losses(core_loss_list, value=True)

# design settings: inductance matrix, model depth
M2D.change_inductance_computation(compute_transient_inductance=True, incremental_matrix=False)
M2D.model_depth = "Magnetic_Axial_Length"

#create and validate setup
setup = M2D.create_setup(setupname=sName)
setup.props["StopTime"] = "StopTime"
setup.props["TimeStep"] = "TimeStep"
setup.props["SaveFieldsType"] = "None"
setup.props["OutputPerObjectCoreLoss"] = True
setup.props["OutputPerObjectSolidLoss"] = True
setup.props["OutputError"] = True
setup.update()
M2D.validate_simple()
###############################

###############################
#prepare post-processing
###############################
#create_output_variables
for k, v in output_vars.items():
    M2D.create_output_variable(k, v)
#create__reports
for k, v in post_params.items():
    M2D.post.create_report(expressions=k,setup_sweep_name="", domain="Sweep", variations=None,
                           primary_sweep_variable="Time" ,secondary_sweep_variable=None,
                           report_category=None,plot_type="Rectangular Plot",context=None, subdesign_id=None,
                           polyline_points=1001,plotname=v)

for k, v in post_params_multiplot.items():
    M2D.post.create_report(expressions=list(k),setup_sweep_name="", domain="Sweep", variations=None,
                           primary_sweep_variable="Time" ,secondary_sweep_variable=None,
                           report_category=None,plot_type="Rectangular Plot",context=None, subdesign_id=None,
                           polyline_points=1001,plotname=v)
#create flux lines plot on region
faces_reg = mod2D.get_object_faces(object_list[1].name)  # Region
# Maxwell Transient needs time specified in a dictionary
# "IntrinsicVar:="	, "Time=\'0\'",
M2D.post.create_fieldplot_surface(faces_reg, 'Flux_Lines', intrinsincDict={"Time": "0.000"}, plot_name="Flux_Lines")
###############################

###############################
#analyze and save
M2D.analyze_setup(sName, use_auto_settings=False)
M2D.save_project(project_file=pathName + pName + '.aedt', overwrite=True, refresh_obj_ids_after_save=False)
###############################


###############################################
# Close AEDT
# ~~~~~~~~~~
# This command closes AEDT.

M2D.release_desktop()
