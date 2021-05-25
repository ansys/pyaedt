#Demo Dipole
import os

from pyaedt.core import Desktop
from pyaedt.core import Hfss
from pyaedt.core.generic.general_methods import generate_unique_name

project_dir = os.path.join(os.environ['TEMP'], generate_unique_name('Example', n=16))
if not os.path.exists(project_dir):
    os.makedirs(project_dir)
print('project_dir: ' + project_dir)
project_name = "Test_Exercise05"
project_file = os.path.join(project_dir, project_name + ".aedt")

with Desktop("2021.1"):
    hfss = Hfss()
    hfss['l_dipole'] = "13.5cm"
    # compfile = os.path.join(hfss.desktop_install_dir, "syslib", "3DComponents", "HFSS", "Antennas", "Dipole", "Dipole_Antenna_DM.a3dcomp")
    # geometryparams={"dipole_length":"l_dipole", "port_gap":"0.225cm", "wire_rad":"0.225cm"}
    compfile = hfss.components3d['Dipole_Antenna_DM']
    geometryparams = hfss.get_components3d_vars('Dipole_Antenna_DM')
    geometryparams['dipole_length'] = "l_dipole"
    hfss.modeler.primitives.insert_3d_component(compfile, geometryparams)
    hfss.create_open_region(Frequency="1GHz")
    setup = hfss.create_setup("MySetup", hfss.SimulationSetupTypes.HFSSDrivenAuto)
    setup.props["Type"] = "Interpolating"

    setup.update()
    setup.add_sweep("Sweep1")
    hfss.save_project(project_file)
    hfss.analyze_setup("MySetup")
    hfss.create_scattering("MyScattering")
