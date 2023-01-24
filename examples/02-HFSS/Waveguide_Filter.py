"""
HFSS: Inductive Iris waveguide filter
----------------------------------------
This example shows how to create a simple waveguide filter.
"""
###############################################################################
# Perform required imports
# ~~~~~~~~~~~~~~~~~~~~~~~~
# Perform required imports.

# sphinx_gallery_thumbnail_path = 'Resources/circuit.png'

import pyaedt
from pyaedt import general_methods
from sympy.parsing.sympy_parser import parse_expr
import os

###############################################################################
# Launch AEDT
# ~~~~~~~~~~~
#


###############################################################################
# Define values for the waveguide iris filter.
# ~~~~~~~~~~~~~~~~~~~~~~

# hfss.settings.enable_debug_methods_argument_logger = False  # Only for debugging.
wgparams = {'l': [0.7428, 0.82188],
            'w': [0.50013, 0.3642, 0.3458],
            'a': 0.4,
            'b': 0.9,
            't': 0.15,
            'units': 'in'}

non_graphical = False
new_thread = False
project_folder = r'C:\Ansoft\Projects\Examples\HFSS\Filters\Eplane WG Filter\test'
project_name = project_folder + "\\" + general_methods.generate_unique_name("wgf", n=2)

# Connect to an existing instance if it exits.
hfss = pyaedt.Hfss(projectname=project_name + '.aedt',
                   specified_version="2022.2",
                   designname="filter",
                   non_graphical=non_graphical,
                   close_on_exit=True)
var_mapping = dict()  # Used to parse expressions.

###############################################################################
# Initialize design parameters in HFSS.
# ~~~~~~~~~~~~~~~~~~~~~~
hfss.modeler.model_units = "in"  # Set to inches
for key in wgparams:
    if type(wgparams[key]) in [int, float]:
        hfss[key] = str(wgparams[key]) + wgparams['units']
        var_mapping[key] = wgparams[key]  # Used for expression parsing
    elif type(wgparams[key]) == list:
        count = 1
        for v in wgparams[key]:
            this_key = key + str(count)
            hfss[this_key] = str(v) + wgparams['units']
            var_mapping[this_key] = v  # Used to parse expressions and generate numerical values.
            count += 1
    else:
        pass

if len(wgparams['l']) % 2 == 0:
    zstart = "-t/2"  # Even number of cavities, odd number of irises.
    is_even = True
else:
    zstart = "l1/2 - t/2"  # Odd number of cavities, even number of irises.
    is_even = False


# Define a function to place a single iris given the longitudinal (z) position, thickness and an iterator, n.
def place_iris(zpos, dz, n):
    w_str = "w" + str(n)  # Iris width as a string.
    this_name = "iris_a_"+str(n)
    iris = []
    if this_name in hfss.modeler.object_names:
        this_name = this_name.replace("a", "c")
    iris.append(hfss.modeler.primitives.create_box(['-b/2', '-a/2', zpos], ['(b - ' + w_str + ')/2', 'a',  dz],
                                                     name=this_name , matname="silver"))
    iris.append(iris[0].mirror([0, 0, 0], [1, 0, 0], duplicate=True))
    return iris


for count in reversed(range(1, len(wgparams['w']) + 1)):
    if count < len(wgparams['w']):  # Update zpos
        zpos = zpos + "".join([" + l" + str(count) + " + "])[:-3]
        iris = place_iris(zpos, "t", count)
        iris = place_iris("-(" + zpos + ")", "-t", count)

    else:  # Place first iris
        zpos = zstart
        iris = place_iris(zpos, "t", count)
        if not is_even:
            iris = place_iris("-(" + zpos + ")", "-t", count)


var_mapping['port_extension'] = 1.5 * wgparams['l'][0]  # Used to evaluate expression with parse_expr()
hfss['port_extension'] = str(var_mapping['port_extension']) + wgparams['units']
wg_z_start = "-(" + zpos + ") - port_extension"  # Add port length.
wg_length = "2*(" + zpos + " + port_extension )"
hfss.modeler.create_box(["-b/2", "-a/2", wg_z_start], ["b", "a", wg_length],
                        name="waveguide", matname="vacuum")

# hfss.create_wave_port_from_sheet()

###############################################################################
# Use parse_expr() to evaluate the numerical values of the integration line
# and a point on the port surface.
# ~~~~~~~~~~~~~~~~~~~~~~
wg_z = [str(parse_expr(wg_z_start, var_mapping)) + wgparams['units'],
        str(parse_expr(wg_z_start + "+" + wg_length, var_mapping)) + wgparams['units']]
count = 0
ports = []
for n, z in enumerate(wg_z):
    face_id = hfss.modeler.get_faceid_from_position([0, 0, z], obj_name="waveguide")
    u_start = [0, str(parse_expr('-a/2', var_mapping)) + wgparams['units'],  z]
    u_end = [0, str(parse_expr('a/2', var_mapping)) + wgparams['units'], z]
    ports.append(hfss.create_wave_port(face_id, u_start, u_end, portname="P" + str(n + 1), renorm=False))

#  See pyaedt.modules.SetupTemplates.SetupKeys.SetupNames
#  for allowed values for type

setup = hfss.insert_setup(name="Setup1", setup_type="HFSSDriven",
                          Frequency="10GHz", MaximumPasses=15)

hfss.create_linear_count_sweep(
    setupname=setup.name,
    unit="GHz",
    freqstart=9.5,
    freqstop=10.5,
    num_of_freq_points=251,
    sweepname="sweep1",
    sweep_type="Interpolating",
    interpolation_tol=0.5,
    interpolation_max_solutions=255,
    save_fields=False,
)

hfss.release_desktop(close_desktop=False, close_projects=False)
