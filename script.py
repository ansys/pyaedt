#---------Script start----------
import os
#os.environ["ANSYSEMSV_ROOT252"] = "C:\\Program Files\\ANSYS Inc\\ANSYS Student\\v252\\AnsysEM"

from ansys.aedt.core import Desktop
d = Desktop()

#import ansys.aedt.core as pyaedt

#"""User Inputs"""
#project_path = r"D:\Folder1...\HFSS_3D_Layout_Project.aedt" # Enter complete path to the HFSS 3D Layout Project
#design_name = "HFSS3DLayoutDesign1" # Enter the name of the Design in the Project
#hfss_setup_name = "Setup1"
#output_hfss = r"D:\Folder1...\HFSS_Classic_Project.aedt" # Enter complete path to the output HFSS Classic Project
#version = "2025.2" # Specify the AEDT version, error found in both 2024.2 and 2025.2 versions

#""" tool process"""
#h3d = pyaedt.Hfss3dLayout(project=project_path, design=design_name, version=version, new_desktop=True)
#setup = h3d.get_setup(hfss_setup_name)
#setup.export_to_hfss(output_hfss, keep_net_name=True, unite=True)
#h3d.save_project()
#h3d.release_desktop(False, False)
#------------Script End--------