import os
from pyaedt import Hfss

hfss = Hfss(specified_version="2022.2", designname="Array_Simple")
from pyaedt.generic.DataHandlers import json_to_dict

local_path = r'C:\ansysdev\git\repos\pyaedt\_unittest'
dict_in = json_to_dict(os.path.join(local_path, "example_models", "array_simple.json"))
dict_in["Circ_Patch_5GHz1"] = os.path.join(local_path, "example_models", "Circ_Patch_5GHz.a3dcomp")
dict_in["cells"][(3, 3)] = {"name": "Circ_Patch_5GHz1"}
hfss.add_3d_component_array_from_json(dict_in)
setup = hfss.create_setup()
setup.props["Frequency"] = "3.5GHz"
setup.props["MaximumPasses"] = 3
hfss.analyze_nominal()

ffdata = hfss.get_antenna_ffd_solution_data(sphere_name="Infinite Sphere1", setup_name=hfss.nominal_adaptive,
                                            frequencies=[3.5e9])

ffdata.plot_farfield_contour(qty_str='RealizedGain', convert_to_db=True,
                             title='Contur at {}Hz'.format(ffdata.frequency))

ffdata.plot_2d_cut(primary_sweep='theta', secondary_sweep_value=[-180, -75, 75],
                   qty_str='RealizedGain',
                   title='Azimuth at {}Hz'.format(ffdata.frequency),
                   convert_to_db=True)

ffdata.plot_2d_cut(primary_sweep="phi", secondary_sweep_value=30,
                   qty_str='RealizedGain',
                   title='Elevation',
                   convert_to_db=True)

ffdata.polar_plot_3d(qty_str='RealizedGain',
                     convert_to_db=True)

ffdata.polar_plot_3d_pyvista(qty_str='RealizedGain',
                             convert_to_db=True)
hfss.release_desktop(False, False)
