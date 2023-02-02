"""
HFSS: Inductive Iris waveguide filter
----------------------------------------
This example shows how to build and analyze a 4-pole
X-Band waveguide filter using inductive irises.

Note that this example uses the Python package SymPy to
evaluate expressions.
"""
###############################################################################
# Perform required imports
# ~~~~~~~~~~~~~~~~~~~~~~~~
# Perform required imports. Note the dependence on
# SymPy is used to evaluate expressions. SymPy is not
# a default requirement in PyAedt and is only compatible
# with CPython > 3.6.

# sphinx_gallery_thumbnail_path = 'Resources/wgf.png'
import os
import tempfile
import pyaedt
from pyaedt import general_methods

###############################################################################
# Launch AEDT
# ~~~~~~~~~~~
#


###############################################################################
# Define values for the waveguide iris filter.
# ~~~~~~~~~~~~~~~~~~~~~~

wgparams = {'l': [0.7428, 0.82188],
            'w': [0.50013, 0.3642, 0.3458],
            'a': 0.4,
            'b': 0.9,
            't': 0.15,
            'units': 'in'}

non_graphical = os.getenv("PYAEDT_NON_GRAPHICAL", "False").lower() in ("true", "1", "t")
new_thread = True

# project_name = pyaedt.generate_unique_project_name(project_name="wgf")

project_folder = tempfile.gettempdir()
project_name = project_folder + "\\" + general_methods.generate_unique_name("wgf", n=2)

# Connect to an existing instance if it exits.
hfss = pyaedt.Hfss(projectname=project_name + '.aedt',
                   specified_version="2022.2",
                   designname="filter",
                   non_graphical=non_graphical,
                   close_on_exit=True)

# hfss.settings.enable_debug_methods_argument_logger = False  # Only for debugging.

var_mapping = dict()  # Used by parse_expr to parse expressions.

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

if len(wgparams['l']) % 2 == 0:
    zstart = "-t/2"  # Even number of cavities, odd number of irises.
    is_even = True
else:
    zstart = "l1/2 - t/2"  # Odd number of cavities, even number of irises.
    is_even = False

###############################################################################
# Draw the parametric waveguide filter.
# ~~~~~~~~~~~~~~~~~~~~~~
# Define a function that places a single iris given the longitudinal (z) position,
# thickness and an integer, n, defining which iris is being placed.  Numbering
# will go from the largest value (interior of the filter) to 1, which is the first
# iris nearest the waveguide ports.
def place_iris(zpos, dz, n):
    w_str = "w" + str(n)  # Iris width parameter as a string.
    this_name = "iris_a_"+str(n)  # Iris object name
    iris = []  # Return a list of the two iris objects.
    if this_name in hfss.modeler.object_names:
        this_name = this_name.replace("a", "c")
    iris.append(hfss.modeler.primitives.create_box(['-b/2', '-a/2', zpos], ['(b - ' + w_str + ')/2', 'a',  dz],
                                                     name=this_name , matname="silver"))
    iris.append(iris[0].mirror([0, 0, 0], [1, 0, 0], duplicate=True))
    return iris

###############################################################################
# Place irises from inner (highest integer) to outer, 1
# ~~~~~~~~~~~~~~~~~~~~~~

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

###############################################################################
# Draw the full waveguide with ports.
# ~~~~~~~~~~~~~~~~~~~~~~
# parse_expr() is used to determine the numerical position
# of the integration line endpoints on the waveguide port.


var_mapping['port_extension'] = 1.5 * wgparams['l'][0]  # Used to evaluate expression with parse_expr()
hfss['port_extension'] = str(var_mapping['port_extension']) + wgparams['units']
hfss["wg_z_start"] = "-(" + zpos + ") - port_extension"
hfss["wg_length"]  = "2*(" + zpos + " + port_extension )"
wg_z_start = hfss.variable_manager["wg_z_start"]
wg_length = hfss.variable_manager["wg_length"]
hfss["u_start"] = "-a/2"
hfss["u_end"]  = "a/2"
# wg_z_start = "-(" + zpos + ") - port_extension"  # Add port length.
# wg_length = "2*(" + zpos + " + port_extension )"
hfss.modeler.create_box(["-b/2", "-a/2", "wg_z_start"], ["b", "a", "wg_length"],
                        name="waveguide", matname="vacuum")

###############################################################################
# Use parse_expr() to evaluate the numerical Cartesian coordinates
# needed to specify start and end points of the integration line
# on the port surfaces.
# ~~~~~~~~~~~~~~~~~~~~~~
wg_z = [wg_z_start.evaluated_value, hfss.value_with_units(wg_z_start.numeric_value + wg_length.numeric_value, "in")]

count = 0
ports = []
for n, z in enumerate(wg_z):
    face_id = hfss.modeler.get_faceid_from_position([0, 0, z], obj_name="waveguide")
    u_start = [0, hfss.variable_manager["u_start"].evaluated_value,  z]
    u_end = [0, hfss.variable_manager["u_end"].evaluated_value, z]

    ports.append(hfss.create_wave_port(face_id, u_start, u_end, portname="P" + str(n + 1), renorm=False))

#  See pyaedt.modules.SetupTemplates.SetupKeys.SetupNames
#  for allowed values for setuptype.
setup = hfss.create_setup("Setup1", setuptype="HFSSDriven",
                           MultipleAdaptiveFreqsSetup=['9.8GHz', '10.2GHz'],
                           MaximumPasses=5)

setup.create_frequency_sweep(
    unit="GHz",
    sweepname="Sweep1",
    freqstart=9.5,
    freqstop=10.5,
    sweep_type="Interpolating",
    )

setup.analyze(num_tasks=2)  # Each frequency point will be solved simultaneously.


#  The following commands fetch solution data from HFSS for plotting directly
#  from the Python interpreter. Caution: The syntax for expressions must be identical to that used
#  in HFSS:

traces_to_plot = hfss.get_traces_for_plot(second_element_filter="P1*")
report = hfss.post.create_report(traces_to_plot)  # Creates a report in HFSS
solution = report.get_solution_data()
plt = solution.plot(solution.expressions)  # Matplotlib axes object.

hfss.release_desktop(close_desktop=False, close_projects=False)
