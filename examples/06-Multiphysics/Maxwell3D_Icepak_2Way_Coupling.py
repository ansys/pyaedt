import pyaedt

version = "2023.2"  # AEDT version

maxwell_design_name = "1 Maxwell"
icepak_design_name = "2 Icepak"

m3d = pyaedt.Maxwell3d(
    projectname=pyaedt.generate_unique_project_name(),
    designname=maxwell_design_name,
    solution_type="EddyCurrent",
    specified_version=version,
    non_graphical=False,
)

###############################################################################
# Create geometry in Maxwell
# ~~~~~~~~~~~~~~~~~~~~~~~~~~
# Coil, coil terminal, core, and region

coil = m3d.modeler.create_rectangle(
    csPlane="XZ", position=[70, 0, -11], dimension_list=[11, 110], name="Coil"
)

coil.sweep_around_axis(cs_axis="Z") # todo: what is the correct input?

coil_terminal = m3d.modeler.create_rectangle(
    csPlane="XZ", position=[70, 0, -11], dimension_list=[11, 110], name="Coil_terminal"
)

core = m3d.modeler.create_rectangle(
    csPlane="XZ", position=[45, 0, -18], dimension_list=[7, 160], name="Core"
)
core.sweep_around_axis(cs_axis="Z")  # todo: what is the correct input?

region = m3d.modeler.create_region(pad_percent=[20, 20, 500, 20, 20, 100])

###############################################################################
# Assign materials
# ~~~~~~~~~~~~~~~~~~~~~~~~~~
# Coil --> copper, core --> ferrite, region --> vacuum

m3d.assign_material(region.name, "vacuum")
m3d.assign_material(coil.name, "copper")
m3d.assign_material(core.name, "ferrite")

###############################################################################
# Assign excitation
# ~~~~~~~~~~~~~~~~~~~~~~~~~~
# 10 turns, 50A

m3d.assign_coil(["Coil_terminal"], conductor_number=10, name="Coil_terminal")

m3d.assign_winding(
    is_solid=False,
    current_value=100,
    name="Winding1",
)

m3d.add_winding_coils(windingname="Winding1", coil_names=["Coil_terminal"])

###############################################################################
# Assign mesh operations
# ~~~~~~~~~~~~~~~~~~~~~~~~~~
# Not necessary in eddy current solver, but when assigned, they speed up the simulation

m3d.mesh.assign_length_mesh(
    ["Core"], maxlength=15, meshop_name="Inside_Core", maxel=None
)
m3d.mesh.assign_length_mesh(
    ["Coil"], maxlength=30, meshop_name="Inside_Coil", maxel=None
)

###############################################################################
# Set conductivity temperature coefficient
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Conductivity is now function of temperature

Cu = m3d.materials["copper"]
cu_resistivity_temp_coefficient = 0.00393
Cu.conductivity.add_thermal_modifier_free_form("1.0/(1.0+{}*(Temp-20))".format(cu_resistivity_temp_coefficient))

###############################################################################
# Set object temperature and enable feedback
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Fro 2-way coupling

m3d.modeler.set_objects_temperature(["Coil"])

###############################################################################
# Assign matrix
# ~~~~~~~~~~~~~~~~~~~~~~~~~~
# RL calculation

m3d.assign_matrix(["Winding1"], matrix_name="Matrix1")

###############################################################################
# Create and analyze simulation setup
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Simulation frequency 150kHz

setup = m3d.create_setup(setupname="Setup1")
setup.props["Frequency"] = "150kHz"
m3d.analyze_setup("Setup1")

# todo: how to get the resistance?
#resistance = m3d.post.get_solution_data("Matrix1.R(Winding1,Winding1)").full_matrix_mag_phase[0]
#m3d.logger.design_logger.info("Coil resistance without temperature feedback =  %f", resistance)

###############################################################################
# Icepak design
# ~~~~~~~~~~~~~
# Insert icepak design and copy solid objects from Maxwell, modify region dimensions

# desktop = m3d.desktop_class
# ipk = desktop[[m3d.project_name, icepak_design_name]]

ipk = pyaedt.Icepak(designname=icepak_design_name)
ipk.copy_solid_bodies_from(m3d, no_pec=False)
ipk.modeler.edit_region_dimensions([50, 50, 50, 50, 500, 500])

###############################################################################
# Map coil losses
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Map ohmic losses in coil

ipk.assign_em_losses(
    designname="1 Maxwell",
    setupname=m3d.setups[0].name,
    sweepname="LastAdaptive",
    object_list=["Coil"],
)

###############################################################################
# Boundary conditions
# ~~~~~~~~~~~~~~~~~~~
# Assign opening

ids = [f.id for f in m3d.modeler.objects_by_name["Region"].faces]
ipk.assign_free_opening(ids , boundary_name="Opening1")
face_names = [face.id for face in faces]
ipk.assign_free_opening(face_names, boundary_name="Opening1")

###############################################################################
# Icepak mesh
# ~~~~~~~~~~~~~~~~~~~
# Assign mesh

mesh_region = ipk.mesh.assign_mesh_region(objectlist=["Coil", "Core"])
mesh_region.UserSpecifiedSettings = True
mesh_region.MinGapX = "1mm"
mesh_region.MinGapY = "1mm"
mesh_region.MinGapZ = "1mm"
mesh_region.MaxLevels = "2"
mesh_region.MaxElementSizeX = "10mm"
mesh_region.MaxElementSizeY = "10mm"
mesh_region.MaxElementSizeZ = "10mm"
mesh_region.update()


###############################################################################
# Icepak solution setup
# ~~~~~~~~~~~~~~~~~~~

solution_setup = ipk.create_setup()
solution_setup.props["Convergence Criteria - Max Iterations"] = 200
solution_setup.props["Flow Regime"] = "Turbulent"
solution_setup.props["Turbulent Model Eqn"] = "ZeroEquation"
solution_setup.props["Radiation Model"] = "Discrete Ordinates Model"
solution_setup.props["Include Flow"] = True
solution_setup.props["Include Gravity"] = True
solution_setup.props["Solution Initialization - Z Velocity"] = "0.0005m_per_sec"
solution_setup.props["Convergence Criteria - Flow"] = 0.0005
solution_setup.props["Flow Iteration Per Radiation Iteration"] = "5"

###############################################################################
# Post-processing
# ~~~~~~~~~~~~~~~~~~~
# Plot temperature on the object surfaces

surface_list = []
for name in ["Coil", "Core"]:
    surface_list.extend(ipk.modeler.get_object_faces(name))

ipk.post.create_fieldplot_surface(
    surface_list,
    quantityName="SurfTemperature",
    plot_name="Surface Temperature"
)

###############################################################################
# Add 2-way coupling and solve the project
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

ipk.assign_2way_coupling()
ipk.analyze_setup(name="Setup1")