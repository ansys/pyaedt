"""
Q2D: Cable parameter identification
---------------------------------------------------
This example shows how you can use PyAEDT to perform these tasks:

 - Create a Q2D design using the Modeler primitives and importing part of the geometry.
 - Set up the entire simulation.
 - Link the solution to a Simplorer design.

 For cable information, see `4 Core Armoured Power Cable <https://www.luxingcable.com/low-voltage-cables/4-core-armoured-power-cable.html>`_

"""
#################################################################################
# Perform required imports
# ~~~~~~~~~~~~~~~~~~~~~~~~

import pyaedt
import math

#################################################################################
# Initialize core strand dimensions and positions
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Initialize cable sizing - radii in mm

c_strand_radius = 2.575
cable_n_cores = 4
core_n_strands = 6
core_xlpe_ins_thickness = 0.5
core_xy_coord = math.ceil(3 * c_strand_radius + 2 * core_xlpe_ins_thickness)

#################################################################################
# Initialize filling and sheet dimensions
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Initialize radii of further structures incrementally adding thicknesses

filling_radius = 1.4142 * (core_xy_coord + 3 * c_strand_radius + core_xlpe_ins_thickness + 0.5)
inner_sheet_radius = filling_radius + 0.75
armour_thickness = 3
armour_radius = inner_sheet_radius + armour_thickness
outer_sheet_radius = armour_radius + 2

#################################################################################
# Initialize armature strand dimensions
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Initialize radii

armour_centre_pos = inner_sheet_radius + armour_thickness / 2.0
arm_strand_rad = armour_thickness / 2.0 - 0.2
n_arm_strands = 30

#################################################################################
# Initialize dictionaries
# ~~~~~~~~~~~~~~~~~~~~~~~
# Initialize dictionaries that contain all the definitions for the design
# variables and output variables.

core_params = {
    "n_cores": str(cable_n_cores),
    "n_strands_core": str(core_n_strands),
    "c_strand_radius": str(c_strand_radius) + 'mm',
    "c_strand_xy_coord": str(core_xy_coord) + 'mm'
}
outer_params = {
    "filling_radius": str(filling_radius) + 'mm',
    "inner_sheet_radius": str(inner_sheet_radius) + 'mm',
    "armour_radius": str(armour_radius) + 'mm',
    "outer_sheet_radius": str(outer_sheet_radius) + 'mm'
}
arm_params = {
    "armour_centre_pos": str(armour_centre_pos) + 'mm',
    "arm_strand_rad": str(arm_strand_rad) + 'mm',
    "n_arm_strands": str(n_arm_strands)
}

#################################################################################
# Initialize Q2D
# ~~~~~~~~~~~~~~
# Initialize Q2D, providing the version, path to the project, and the design
# name and type.

desktopVersion = "2023.2"
project_name = 'Q2D_ArmouredCableExample'
q2d_design_name = '2D_Extractor_Cable'
sName = "MySetupAuto"
swName = "sweep1"
twinb_design_name = 'CableSystem'
Q2D_DS = pyaedt.Q2d(projectname=project_name, designname=q2d_design_name, specified_version=desktopVersion)

##########################################################
# Define variables from dictionaries
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Define design variables from the created dictionaries.

for k, v in core_params.items():
    Q2D_DS[k] = v
for k, v in outer_params.items():
    Q2D_DS[k] = v
for k, v in arm_params.items():
    Q2D_DS[k] = v

##########################################################
# Create object to access 2D modeler
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Create the object ``mod2D`` to access the 2D modeler easily.

mod2D = Q2D_DS.modeler
mod2D.delete()
mod2D.model_units = "mm"

#################################################################################
# Initialize required material properties
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Cable insulators require specific materials not included in the Sys Library
# Plastic, PE (cross-linked, wire, and cable grade)

mat_pe_cable_grade = Q2D_DS.materials.add_material("plastic_pe_cable_grade")
mat_pe_cable_grade.update()
mat_pe_cable_grade.conductivity = "1.40573e-16"
mat_pe_cable_grade.permittivity = "2.09762"
mat_pe_cable_grade.dielectric_loss_tangent = "0.000264575"
# Plastic, PP (10% carbon fiber)
mat_pp = Q2D_DS.materials.add_material("plastic_pp_carbon_fiber")
mat_pp.update()
mat_pp.conductivity = "0.0003161"

#####################################################################################
# Create geometry for core strands, filling, and XLPE insulation
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

mod2D.create_coordinate_system(['c_strand_xy_coord', 'c_strand_xy_coord', '0mm'], name='CS_c_strand_1')
mod2D.set_working_coordinate_system('CS_c_strand_1')
c1_id = mod2D.create_circle(['0mm', '0mm', '0mm'], 'c_strand_radius', name='c_strand_1', matname='copper')
c2_id = c1_id.duplicate_along_line(vector=['0mm', '2.0*c_strand_radius', '0mm'], nclones=2)
mod2D.duplicate_around_axis(c2_id, cs_axis="Z", angle=360 / core_n_strands, nclones=6)
c_unite_name = mod2D.unite(Q2D_DS.get_all_conductors_names())

fill_id = mod2D.create_circle(['0mm', '0mm', '0mm'], '3*c_strand_radius', name='c_strand_fill',
                              matname='plastic_pp_carbon_fiber')
fill_id.color = (255, 255, 0)
xlpe_id = mod2D.create_circle(['0mm', '0mm', '0mm'], '3*c_strand_radius+' + str(core_xlpe_ins_thickness) + 'mm',
                              name='c_strand_xlpe',
                              matname='plastic_pe_cable_grade')
xlpe_id.color = (0, 128, 128)

mod2D.set_working_coordinate_system('Global')
all_obj_names = Q2D_DS.get_all_conductors_names() + Q2D_DS.get_all_dielectrics_names()
mod2D.duplicate_around_axis(all_obj_names, cs_axis="Z", angle=360 / cable_n_cores, nclones=4)
cond_names = Q2D_DS.get_all_conductors_names()

#####################################################################################
# Create geometry for filling object
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

filling_id = mod2D.create_circle(['0mm', '0mm', '0mm'], 'filling_radius', name='Filling',
                                 matname='plastic_pp_carbon_fiber')
filling_id.color = (255, 255, 180)

#####################################################################################
# Create geometry for inner sheet object
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

inner_sheet_id = mod2D.create_circle(['0mm', '0mm', '0mm'], 'inner_sheet_radius', name='InnerSheet',
                                     matname='PVC plastic')
inner_sheet_id.color = (0, 0, 0)

#####################################################################################
# Create geometry for armature fill
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

arm_fill_id = mod2D.create_circle(['0mm', '0mm', '0mm'], 'armour_radius', name='ArmourFilling',
                                  matname='plastic_pp_carbon_fiber')
arm_fill_id.color = (255, 255, 255)

#####################################################################################
# Create geometry for outer sheet
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

outer_sheet_id = mod2D.create_circle(['0mm', '0mm', '0mm'], 'outer_sheet_radius', name='OuterSheet',
                                     matname='PVC plastic')
outer_sheet_id.color = (0, 0, 0)

#####################################################################################
# Create geometry for armature steel strands
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

arm_strand_1_id = mod2D.create_circle(['0mm', 'armour_centre_pos', '0mm'], '1.1mm', name='arm_strand_1',
                                      matname='steel_stainless')
arm_strand_1_id.color = (128, 128, 64)
arm_strand_1_id.duplicate_around_axis('Z', '360deg/n_arm_strands', nclones='n_arm_strands')
arm_strand_names = mod2D.get_objects_w_string('arm_strand')

#####################################################################################
# Create region
# ~~~~~~~~~~~~~

oeditor = Q2D_DS.odesign.SetActiveEditor("3D Modeler")
oeditor.CreateRegion(
    [
        "NAME:RegionParameters",
        "+XPaddingType:=", "Percentage Offset",
        "+XPadding:=", "500",
        "-XPaddingType:=", "Percentage Offset",
        "-XPadding:=", "500",
        "+YPaddingType:=", "Percentage Offset",
        "+YPadding:=", "500",
        "-YPaddingType:=", "Percentage Offset",
        "-YPadding:=", "500",
        "+ZPaddingType:=", "Percentage Offset",
        "+ZPadding:=", "0",
        "-ZPaddingType:=", "Percentage Offset",
        "-ZPadding:="	, "0",
		[
			"NAME:BoxForVirtualObjects",
			[
				"NAME:LowPoint",
				1,
				1,
				1
			],
			[
				"NAME:HighPoint",
				-1,
				-1,
				-1
			]
		]
	],
	[
		"NAME:Attributes",
		"Name:="		, "Region",
		"Flags:="		, "Wireframe#",
		"Color:="		, "(143 175 143)",
		"Transparency:="	, 0,
		"PartCoordinateSystem:=", "Global",
		"UDMId:="		, "",
		"MaterialValue:="	, "\"vacuum\"",
		"SurfaceMaterialValue:=", "\"\"",
		"SolveInside:="		, False,
		"ShellElement:="	, False,
		"ShellElementThickness:=", "nan ",
		"ReferenceTemperature:=", "nan ",
		"IsMaterialEditable:="	, True,
		"UseMaterialAppearance:=", False,
		"IsLightweight:="	, False
	])

##########################################################
# Assign conductors and reference ground
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

obj = [Q2D_DS.modeler.get_object_from_name(i) for i in cond_names]
[Q2D_DS.assign_single_conductor(name ='C1 ' +str(obj.index(i) + 1), target_objects=i, conductor_type='SignalLine') for i
 in obj]
obj = [Q2D_DS.modeler.get_object_from_name(i) for i in arm_strand_names]
Q2D_DS.assign_single_conductor(name="gnd", target_objects=obj, conductor_type="ReferenceGround")
mod2D.fit_all()

##########################################################
# Assign design settings
# ~~~~~~~~~~~~~~~~~~~~~~

lumped_length = "100m"
q2d_des_settings = Q2D_DS.design_settings()
q2d_des_settings['LumpedLength'] = lumped_length
Q2D_DS.change_design_settings(q2d_des_settings)

##########################################################
# Insert setup and frequency sweep
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

q2d_setup = Q2D_DS.create_setup(setupname=sName)
q2d_sweep = q2d_setup.add_sweep(sweepname=swName)
q2d_sweep.props["RangeType"] = "LogScale"
q2d_sweep.props["RangeStart"] = "0Hz"
q2d_sweep.props["RangeEnd"] = "3MHz"
q2d_sweep.props["RangeCount"] = 10
q2d_sweep.props["RangeSamples"] = 1
q2d_sweep.update()

##########################################################
# Analyze setup
# ~~~~~~~~~~~~~

Q2D_DS.analyze(setup_name=sName, num_cores=4, num_tasks=2)

###################################################################
# Add a Simplorer/Twin Builder design and the Q3D dynamic component
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

TB_DS = pyaedt.TwinBuilder(designname=twinb_design_name)

###################################################################
# Prepare the lists to call the dynamic component import function
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

exc_list = Q2D_DS.design_excitations
signal_line_list = [item.name for item in exc_list if item.type == 'SignalLine']
num_ports = 2 * signal_line_list.__len__()
port_info_listA = []
port_info_listB = []
for i_var in range(len(signal_line_list)):
    port_info_listA.append("OnePortInfo:=")
    port_info_listB.append("OnePortInfo:=")
    my_listA = [str(signal_line_list[i_var]) + '_' + str(signal_line_list[i_var]) + '_A', -1,
                str(signal_line_list[i_var]) + ':' + str(signal_line_list[i_var]) + '_A']
    my_listB = [str(signal_line_list[i_var]) + '_' + str(signal_line_list[i_var]) + '_B', -1,
                str(signal_line_list[i_var]) + ':' + str(signal_line_list[i_var]) + '_B']
    port_info_listA.append(my_listA)
    port_info_listB.append(my_listB)
port_info_list = ["NAME:PortInfo"]
port_info_list.extend(port_info_listA)
port_info_list.extend(port_info_listB)

des_var_list = Q2D_DS.variable_manager.design_variables
# sort dictionary in alphabetical order
des_var_list_sorted = sorted(des_var_list.keys(), key=lambda x: x.lower())
des_prop_list = ["NAME:Properties"]
for i_var in range(len(des_var_list)):
    my_list = [des_var_list_sorted[i_var],
               str(des_var_list[des_var_list_sorted[0]].numeric_value) + des_var_list[des_var_list_sorted[0]].units]
    des_prop_list.append("paramProp:=")
    des_prop_list.append(my_list)
# last element component depth
des_prop_list.append("paramProp:=")
my_last_list = ["COMPONENT_DEPTH", lumped_length]
des_prop_list.append(my_last_list)

##########################################################
# Add a Q3D dynamic component
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~
#
o_def_manager = TB_DS.oproject.GetDefinitionManager()
dyn_component = o_def_manager.GetManager("Component")
name_comp = "SimpQ3DData1"
dyn_component.AddDynamicNPortData(
    [
        "NAME:ComponentData",
        "ComponentDataType:=", "SimpQ3DData",
        "name:=", name_comp,
        "filename:=", "$PROJECTDIR\\ " + project_name + '.aedt',
        "numberofports:=", num_ports,
        "Is3D:=", False,
        "IsWBLink:=", False,
        "WBSystemId:=", "",
        "CouplingDesignName:=", q2d_design_name,
        "CouplingSolutionName:=", sName + ' : ' + swName,
        "CouplingMatrixName:=", "Original",
        "SaveProject:=", False,
        "CloseProject:=", False,
        "StaticLink:="	, False,
		"CouplingType:="	, "Q2DRLGCTBLink",
		"VariationKey:="	, "",
		"NewToOldMap:="		, [],
		"OldToNewMap:="		, [],
		"ModelText:="		, "",
		"SolvedVariationKey:="	, "",
		"EnforcePassivity:="	, True,
		"MaxNumPoles:="		, "10000",
		"ErrTol:="		, "0.0001",
		"SSZref:="		, "50ohm",
		"IsDepthNeeded:="	, True,
		"Mw2DDepth:="		, lumped_length,
		"IsScaleNeeded:="	, False,
		"MwScale:="		, "1",
		"RefPinStyle:="		, 3,
		"Q3DModelType:="	, 1,
		"SaveDataSSOptions:="	, "",
		des_prop_list,
		port_info_list,
	])

TB_DS.oeditor.CreateComponent(
	[
		"NAME:ComponentProps",
		"Name:="		, name_comp,
		"Id:="			, "6"
	],
	[
		"NAME:Attributes",
		"Page:="		, 1,
		"X:="			, -0.44958,
		"Y:="			, 0.0635,
		"Angle:="		, 0,
		"Flip:="		, False
	])

##########################################################
# Save project and release desktop
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

TB_DS.save_project()
TB_DS.release_desktop(False, False)
