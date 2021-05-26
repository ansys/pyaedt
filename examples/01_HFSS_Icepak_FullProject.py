"""
# ------------------------------------------------------------------------------
#
# This Example shows how to create a full project from scratch in HFSS and Icepak (linked to HFSS). the project creates
# a setup, solves it and create post processing output. It includes a lot of commands to show pyaedt Capabilities
#
# -------------------------------------------------------------------------------
"""

import os
import sys
import pathlib
import glob
from pyaedt import Hfss
from pyaedt import Icepak
from pyaedt import Desktop
from pyaedt.generic.general_methods import generate_unique_name
sys.path.append(r'..\DLLs\PDFReport')
import clr
clr.AddReference("AnsysReport")
from pyaedt.application.DataHandlers import create_table_for_csharp
import AnsysReport

try:
    import numpy as np
    import matplotlib.pyplot as plt
    import math
    advanced = True
except ImportError:
    print("For advanced PostProcessing please install numpy and matplotlib")
    advanced = False

# local_path = os.path.dirname(os.path.realpath(__file__))
local_path = "../../examples/pyaedt/"
module_path = pathlib.Path(local_path)
root_path = module_path.parent
desktopVersion = "2021.1"
project_dir = os.path.join(os.environ['TEMP'], generate_unique_name('Example', n=16))
if not os.path.exists(project_dir):
    os.makedirs(project_dir)
print('project_dir: ' + project_dir)
NonGraphical = False
NewThread = True
with Desktop(desktopVersion, NonGraphical, NewThread):
    aedtapp = Hfss()
    material_database = os.path.join(root_path, 'pyaedt', 'misc', 'amat.xml')
    aedtapp.materials.load_from_file(material_database)
    newmat = aedtapp.materials.creatematerial("my_material")
    newmat.set_property_value(newmat.PropName.Conductivity, 650000000)
    dataset = newmat.create_thermal_modifier([[22, 1], [80, 0.8]])
    newmat.set_property_therm_modifier(newmat.PropName.Conductivity, dataset)
    newmat.update()
    aedtapp["$height"] = "10mm"
    aedtapp["height"] = "10mm"
    aedtapp["height"] = "5mm"
    project_name = "Test_Exercise01"
    project_file = os.path.join(project_dir, project_name + ".aedt")
    aedtapp.save_project(project_file)
    udp = aedtapp.modeler.Position(0, 0, 0)
    coax_dimension = 200
    aedtapp["dim"] = "2mm"
    id1 = aedtapp.modeler.primitives.create_cylinder(aedtapp.CoordinateSystemPlane.XYPlane, udp, 3, coax_dimension,
                                                     0, "inner")
    id2 = aedtapp.modeler.primitives.create_cylinder(aedtapp.CoordinateSystemPlane.XYPlane, udp, 8, coax_dimension,
                                                     0, matname="teflon_based")
    id3 = aedtapp.modeler.primitives.create_cylinder(aedtapp.CoordinateSystemPlane.XYPlane, udp, 10, coax_dimension,
                                                     0, "outer")
    aedtapp["dim"] = "5mm"
    aedtapp["$dim"] = "5mm"
    aedtapp.modeler.subtract(id3, id2, True)
    aedtapp.modeler.subtract(id2, id1, True)
    aedtapp.assignmaterial([id1, id3], "Copper")
    aedtapp.get_all_conductors_names()
    aedtapp.get_all_dielectrics_names()
    aedtapp.mesh.assign_initial_mesh_from_slider(6)
    aedtapp.mesh.assign_model_resolution(
        [aedtapp.modeler.primitives.get_obj_name(id1), aedtapp.modeler.primitives.get_obj_name(id3)], None)
    aedtapp.mesh.assign_length_mesh(aedtapp.modeler.primitives.get_object_faces(id2), False, 1, 2000)
    aedtapp.modeler.subtract([id3], [id2], True)
    id4 = aedtapp.modeler.primitives.create_circle(aedtapp.CoordinateSystemPlane.YZPlane, udp, 10, 0)
    pos2 = aedtapp.modeler.Position(coax_dimension, 0, 0)
    id5 = aedtapp.modeler.primitives.create_circle(aedtapp.CoordinateSystemPlane.YZPlane, pos2, 10, 0)
    list_ports = [aedtapp.modeler.primitives.get_obj_name(id4), aedtapp.modeler.primitives.get_obj_name(id5)]
    portnames = aedtapp.create_wave_port_from_sheets(list_ports, 0)
    aedtapp.set_active_design(aedtapp.design_name)
    setup = aedtapp.create_setup("MySetup")
    setup.props["Frequency"] = "1GHz"
    setup.props["BasisOrder"] = 2
    setup.props["MaximumPasses"] = 1
    setup.update()
    sweepname = aedtapp.create_frequency_sweep("MySetup", "GHz", 0.8, 1.2)
    aedtapp.modeler.fit_all()
    ipkapp = Icepak()
    ipkapp.copy_solid_bodies_from(aedtapp)
    surfaceobj = aedtapp.get_all_conductors_names()
    ipkapp.assign_em_losses(aedtapp.design_name, "MySetup", "LastAdaptive", "1GHz", surfaceobj)
    ipkapp.edit_design_settings(aedtapp.GravityDirection.ZNeg)
    setup_ipk = ipkapp.create_setup("SetupIPK")
    setup_ipk.props["Convergence Criteria - Max Iterations"] = 3
    setup_ipk.update()
    airbox = ipkapp.modeler.primitives.get_obj_id("Region")
    ipkapp.modeler.primitives[airbox].display_wireframe(True)
    airfaces = ipkapp.modeler.primitives.get_object_faces(airbox)
    ipkapp.assign_openings(airfaces)
    ipkapp.modeler.edit_region_dimensions([])
    aedtapp.save_project()
    aedtapp.close_project(project_name)
    aedtapp.load_project(project_file)
    ipkapp = Icepak()
    ipkapp.modeler.fit_all()
    setup1 = ipkapp.analyze_setup("SetupIPK")
    aedtapp.save_project()
    aedtapp.modeler.fit_all()
    aedtapp.analyze_setup("MySetup")

    #Generating images and Field Plots

    cutlist = ["Global:XY", "Global:XZ", "Global:YZ"]
    vollist = [aedtapp.modeler.primitives.get_obj_name(id2)]
    setup_name = "MySetup : LastAdaptive"
    quantity_name = "ComplexMag_E"
    quantity_name2 = "ComplexMag_H"
    surflist = aedtapp.modeler.primitives.get_object_faces(id1)
    intrinsic = {"Freq": "1GHz", "Phase": "0deg"}
    plot1 = aedtapp.post.create_fieldplot_cutplane(cutlist, quantity_name, setup_name, intrinsic)
    plot1.IsoVal = "Tone"
    plot1.modify_folder()
    results_folder = os.path.join(aedtapp.project_path,"Coaxial_Results")
    if not os.path.exists(results_folder):
        os.mkdir(results_folder)
    aedtapp.post.export_field_image_with_View(plot1.name, os.path.join(results_folder, "prova1.jpg"))
    plot2 = aedtapp.post.create_fieldplot_volume(vollist, quantity_name2, setup_name, intrinsic)
    aedtapp.post.export_field_image_with_View(plot2.name, os.path.join(results_folder, "prova2.jpg"))
    plot3 = aedtapp.post.create_fieldplot_surface(surflist, quantity_name, setup_name, intrinsic)
    aedtapp.post.export_field_image_with_View(plot3.name, os.path.join(results_folder, "prova3.jpg"))
    aedtapp.create_scattering("Scattering1")
    aedtapp.create_scattering("Scattering2", variations=aedtapp.available_variations.nominal_w_values)
    aedtapp.post.export_report_to_jpg(results_folder, "Scattering1")
    quantity_name = "Temperature"
    setup_name = ipkapp.existing_analysis_sweeps[0]
    intrinsic = ""
    surflist = ipkapp.modeler.primitives.get_object_faces("inner")
    plot5 = ipkapp.post.create_fieldplot_surface(surflist, "SurfTemperature")
    ipkapp.post.export_field_image_with_View(plot5.name, os.path.join(results_folder, "SurfXZ.jpg"), view="XZ")
    ipkapp.post.export_field_image_with_View(plot5.name, os.path.join(results_folder, "SurfXY.jpg"), view="YZ")
    plot4 = ipkapp.post.create_fieldplot_cutplane(cutlist, quantity_name)
    ipkapp.post.export_field_image_with_View(plot4.name, os.path.join(results_folder, "FaceIso.jpg"))
    ipkapp.post.export_field_image_with_View(plot4.name, os.path.join(results_folder, "FaceXZ.jpg"), view="XZ")
    ipkapp.post.export_field_image_with_View(plot4.name, os.path.join(results_folder, "FaceXY.jpg"), view="XY")
    ipkapp.post.export_field_image_with_View(plot4.name, os.path.join(results_folder, "FaceYZ.jpg"), view="YZ")
    ipkapp.post.export_field_file_on_grid("Temp", setup_name, ipkapp.available_variations.nominal_w_values,
                                          os.path.join(project_dir, "Temp.fld"), grid_stop=[10,10,10], grid_step=[1,1,1])
    aedtapp.save_project()

    if advanced:
        trace_names = []
        for el in portnames:
            for el2 in portnames:
                trace_names.append('S(' + el + ',' + el2 + ')')
        cxt = ['Domain:=', 'Sweep']
        families = ['Freq:=', ['All']]
        my_data = aedtapp.post.get_report_data(trace_names)
        freq_data = np.array(my_data.sweeps["Freq"])

        comp = []
        fig, ax = plt.subplots(figsize=(20, 10))

        ax.set(xlabel='Frequency (Ghz)', ylabel='SParameters(dB)', title='Scattering Chart')
        ax.grid()
        for el in trace_names:
            mag_data = np.array(my_data.data_db(el))
            ax.plot(freq_data, mag_data)
        #plt.show()

    aedtapp.close_project(aedtapp.project_name)

    #Generating PDF Report

    report = AnsysReport.CreatePdfReport()

    report.Specs.ModelName = "Coaxial"
    report.Specs.Revision = "Rev1"

    report.Specs.AnsysVersion = "2021R1"
    report.Specs.ProjectName = "My Coaxial"
    report.AddAnsysHeader()
    report.AddFirstPage()
    section2 = report.CreateNewSection()

    report.AddChapter("Simulation Results")
    testo = "The project name is " + report.Specs.ProjectName + "."
    report.AddText(testo)
    imagefiles = glob.glob(results_folder + "/*.jpg")
    for img in imagefiles:
        report.AddImageWithCaption(img, img, 13)

    report.AddChapter("Project Variables")

    my_table = [["$dim", "$height"], ["5mm", "10mm"]]

    mytable = create_table_for_csharp(my_table, True)
    report.AddTableFromList("Project Variables", mytable, True, True)

    report.AddTableOfContent()
    filename=report.SavePDF(results_folder)
    os.startfile(os.path.join(results_folder,filename))


print("loaded")
