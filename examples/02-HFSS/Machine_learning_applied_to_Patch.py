"""
HFSS: machine learning applied to a patch antenna
---------------------------------------------------------
This example demonstrates the use PyAEDT to apply a
machine learning algorithm in three steps:

#. Generate the database.
#. Create the machine learning algorithm.
#. Implement the model in a PyAEDT method.

While this example provides guidance for all three steps, a
more practical implementation would
separate the code for each step.
"""
###############################################################################
# Perform required imports
# ~~~~~~~~~~~~~~~~~~~~~~~~

import json
import os
import random
from math import sqrt

import joblib
import numpy as np
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVR

import pyaedt
import tempfile
from pyaedt.modeler.advanced_cad.stackup_3d import Stackup3D
from pyaedt.generic import constants as const

###############################################################################
# Set non-graphical mode
# ~~~~~~~~~~~~~~~~~~~~~~
# Set non-graphical mode. ``"PYAEDT_NON_GRAPHICAL"`` is set to ``False``
# to create this documentation.
#
# You can set ``non_graphical``  to ``True`` in order to view
# HFSS while the notebook cells are executed.
#
# Use the 2023R1 release of HFSS.

non_graphical = False
desktop_version = "2023.1"


c0 = 2.99792458e8  # Speed of light in free space.
n_s = 2
freq_units = "MHz"
length_units = "mm"
freq_scale = const.scale_units(freq_units)

####################################################################
# ``freq_str()`` is used to generate the setup name
# for the HFSS solution in subsequent cells.

setup_prefix = "Setup"
freq_str = lambda freq: str(str(int(int(freq*100)/100.0 / freq_scale))) + freq_units
setup_name = lambda freq: setup_prefix + "_" + freq_str(freq)
sweep_name = "Sweep"  # Use this name for all frequency sweeps.

###############################################################################
# Generate the test data.
# -------------------------
# This section describes how data are generated to subsequently
# be used to test the machine learning results.
#
# Test Data
# ~~~~~~~~~~~~~~
# Generate four random strings:
# - frequency (0.1 GHz - 1 GHz)
# - substrate permittivity (1 - 12)
# - substrate thickness
# - patch width
#
# The following code generates a data set consisting of
# - 1 frequency value
# - ``n_s`` permittivity values
# - ``n_s`` thickness values
# - n_s width values
#
# resulting in :math:`n_s^3` samples.  Use ``n_s`` = 2.
#
# Each test case is defined in a dictionary. All test cases are compiled
# in a list. Length units are relative to the free space wavelength. The keys in the
# used for each test case are:
# - frequency (frequency in Hz)
# - permittivity (relative permittivity)
# - thickness (relative to free-space wavelength)
# - width (relative to free-space wavelength)
# - length (relative to free-space wavelength)
# - previous_impedance
#
# This data set will be used to test
# the model. Later in this example, a large dataset consisting of
# more than 3,300 variations
# over 74 frequencies
# x 5 permittivity x 3 thickness x 3 width will be imported and
# used to train the model.

tuple_random_frequency_permittivity = []
frequencies= [150 * freq_scale]  # Allow for multiple frequency values.  # 150 MHz
for freq in frequencies:
    for i in range(n_s):
        rel_permittivity = 1.0 + 11.0 * int(random.random() * 100) / 100.0  # Rel permittivity to 2 decimal places.
        temp_tuple = (freq, rel_permittivity)
        tuple_random_frequency_permittivity.append(temp_tuple)

###############################################################################
# The substrate thickness ranges from 0.0025 to 0.055 wavelength in the void.
# The width ranges from 0.5 to 1.5 relative to the theoretical optimum:
#
# ``c / (2 * frequency * sqrt((permittivity + 1) / 2))``
#
# For frequency-permittivity pairs, three random thicknesses and three
# random widths are generated. The patch length will be calculated analytically.
# Use of the analytic formula reduces the required
# frequency range. Every case is stored in a list whose elements are
# dictionaries.

samples = []

for f, er in tuple_random_frequency_permittivity:
    thickness = []
    width = []

    wave_length_0 = c0 / f

    min_thickness = 0.0025 * wave_length_0
    inter_thickness = 0.01 * wave_length_0
    max_thickness = 0.055 * wave_length_0

    # "Random" thickness has equal probability to lie in the lower or upper thickness range:
    for i in random.sample((0,1), n_s):
        if i == 0:
            thickness.append(min_thickness + (inter_thickness - min_thickness) * random.random())
        else:
            thickness.append(inter_thickness + (max_thickness - inter_thickness) * random.random())

    min_width = 0.5 * c0 / (2.0 * f * sqrt((er + 1.0) / 2.0))
    max_width = 1.5 * c0 / (2 * f * sqrt((er + 1.0) / 2.0))
    for i in range(n_s):
        width.append(min_width + (max_width - min_width) * random.random())

    for w in width:
        for t in thickness:
            er_e = (er + 1.0) / 2.0 + (er - 1.0) / (2.0 * sqrt(1 + 10.0 * t / w))
            w_h = w / t
            added_length = 0.412 * t * (er_e + 0.3) * (w_h + 0.264) / ((er_e - 0.258) * (w_h + 0.813))
            wave_length = c0 / (f * sqrt(er_e))
            length = wave_length / 2.0 - 2.0 * added_length
            sample = {
                "frequency": f,
                "permittivity": er,
                "thickness": t,
                "width": w,
                "length": length,
                "previous_impedance": 0,
            }
            samples.append(sample)

print("Test Samples:")
for s in samples:
    print(f">> {s}")

###############################################################################
# Generate HFSS design
# ~~~~~~~~~~~~~~~~~~~~
# Generate the HFSS design using the ``Stackup3D`` method.
# 1. Open an HFSS design and create the stackup.
# 2. Add the different layers
# 3. Add the patch.
# The layers and patch,
# are already parametrized in the stackup library.

# new_desktop_session=True

project_folder = os.path.join(tempfile.gettempdir(), "ML_patch")
if not os.path.exists(project_folder):
    os.mkdir(project_folder)
project_name = os.path.join(project_folder, pyaedt.general_methods.generate_unique_name("Proj", n=3))
hfss = pyaedt.Hfss(projectname=project_name,
                   solution_type="Terminal",
                   designname="patch",
                   non_graphical=non_graphical,
                   specified_version=desktop_version)

hfss.modeler.model_units = length_units

###############################################################################
# PCB Stackup
# ~~~~~~~~~~~~~~~~~~~~~~~~~~
# Length units are mm.

stackup = Stackup3D(hfss)
ground = stackup.add_ground_layer("ground", material="copper", thickness=0.035, fill_material="air")
dielectric = stackup.add_dielectric_layer("dielectric", thickness=10, material="Duroid (tm)")
signal = stackup.add_signal_layer("signal", material="copper", thickness=0.035, fill_material="air")
patch = signal.add_patch(patch_length=1009.86, patch_width=1185.9, patch_name="Patch", frequency=100e6)

###############################################################################
# Resize layers around patch
# ~~~~~~~~~~~~~~~~~~~~~~~~~~
# Resize the layers around the patch so they adapt to changes in
# the patch dimensions.

stackup.resize_around_element(patch)

###############################################################################
# Create lumped port
# ~~~~~~~~~~~~~~~~~~
# Create a lumped port to feed the patch antenna.

patch.create_lumped_port(reference_layer=ground, opposite_side=False, port_name="one")

###############################################################################
# Define Air Volume
# ~~~~~~~~~~~~~~~~~
# The air bounding box is defined using a region with relative (percentage)
# padding in the x,y,z directions.
#
# Create a line perpendicular to the patch surface
# ensures sufficient size of the air bounding box in the
# +/- z directions.

points_list = [
    [patch.position_x.name, patch.position_y.name, signal.elevation.name],
    [patch.position_x.name, patch.position_y.name, signal.elevation.name + " + " + patch.length.name],
]
hfss.modeler.create_polyline(position_list=points_list, name="adjust_airbox")
pad_percent = [50, 50, 300, 50, 50, 10]
region = hfss.modeler.create_region(pad_percent)
hfss.assign_radiation_boundary_to_objects(region)

###############################################################################
# Plot
# ~~~~
# Plot patch

hfss.plot(show=False, export_path=os.path.join(hfss.working_directory, "Image.jpg"), plot_air_objects=True)

###############################################################################
# Create setup and sweep
# ~~~~~~~~~~~~~~~~~~~~~~
# Create a setup and a sweep by frequency.

for freq in frequencies:
    current_setup = hfss.create_setup(setupname=setup_name(freq),
                                      Frequency=freq_str(freq),
                                      MaximumPasses=2,  # Increase to 30 to improve accuracy.
                                      MinimumConvergedPasses=1)

    freq_start = int(freq/freq_scale*100)/100.0 * 0.75
    freq_stop = int(freq/freq_scale*100)/100.0 * 1.25
    current_setup.create_frequency_sweep(
        unit=freq_units,
        sweepname=sweep_name,
        freqstart=freq_start,
        freqstop=freq_stop,
        num_of_freq_points=2501,
        sweep_type="Interpolating",
    )


###############################################################################
# Define function
# ~~~~~~~~~~~~~~~
# Define a function to recover the index of the resonance frequency.


def index_of_resonance(imaginary_list, real_list):
    list_of_index = []
    for i in range(1, len(imaginary_list)):
        if imaginary_list[i] * imaginary_list[i - 1] < 0:
            if abs(imaginary_list[i]) < abs(imaginary_list[i - 1]):
                list_of_index.append(i)
            elif abs(imaginary_list[i]) > abs(imaginary_list[i - 1]):
                list_of_index.append(i - 1)
    if len(list_of_index) == 0:
        return 0
    elif len(list_of_index) == 1:
        return list_of_index[0]
    else:
        storage = 0
        resonance_index = 0
        for index in list_of_index:
            if storage < real_list[index]:
                storage = real_list[index]
                resonance_index = index
        return resonance_index


###############################################################################
# Create parametric variation over all samples
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Use a loop to create a parametric analysis for each
# sample and associate it with a setup.
# The parametric variation is comprised of the patch length and width and substrate
# permittivity and thickness. For each, measure the real resonance frequency to
# obtain the data length, width, permittivity, and thickness that corresponds
# to a resonance frequency. Use an error counter to verify that the resonance
# frequency is contained in the sweep. To make it easy, calculate the length
# of each case using the analytic formula.

error_counter = []
count = 1
for sample in samples:
    length_variation = sample["length"] * 1e3
    width_variation = sample["width"] * 1e3
    thickness_variation = sample["thickness"] * 1e3
    permittivity_variation = sample["permittivity"]
    param_name = "para_" + freq_str(sample["frequency"]) + "_" + str(count) #

    # Add the parametric setup. Specify length.
    this_param = hfss.parametrics.add(
        patch.length.name,
        length_variation,
        length_variation,
        step=1,
        variation_type="LinearCount",
        solution=setup_name(sample["frequency"]),
        parametricname=param_name,
    )
    this_param.add_variation(
        patch.width.name, width_variation, width_variation, step=1, unit=None, variation_type="LinearCount"
    )
    this_param.add_variation(
        dielectric.thickness.name,
        thickness_variation,
        thickness_variation,
        step=1,
        unit=None,
        variation_type="LinearCount",
    )
    this_param.add_variation(
        "$cloned_Duroid_tm_permittivity",
        permittivity_variation,
        permittivity_variation,
        step=1,
        unit=None,
        variation_type="LinearCount",
    )
    this_param.analyze()
    data = hfss.post.get_solution_data(
        "Zt(one_T1, one_T1)",
        setup_sweep_name=setup_name(frequencies[0]) + " : " + sweep_name,
        domain="Sweep",
        variations={
            patch.length.name: [str(length_variation) + "mm"],
            patch.width.name: [str(width_variation) + "mm"],
            dielectric.thickness.name: [str(thickness_variation) + "mm"],
            "$cloned_Duroid_tm_permittivity": [str(permittivity_variation)],
        },
        polyline_points=2501,
    )
    imaginary_part = data.data_imag()
    real_part = data.data_real()
    corresponding_index = index_of_resonance(imaginary_part, real_part)
    if corresponding_index == 0:
        hfss.logger.error("The resonance is out of the range")
        error_counter.append(i)
    minimum_imaginary = imaginary_part[corresponding_index]
    previous_impedance = real_part[corresponding_index]
    print("minimum_imaginary: " + str(minimum_imaginary))
    print("previous_impedance: " + str(previous_impedance))
    frequency_list = data.primary_sweep_values
    resonance_frequency = frequency_list[corresponding_index]
    print(resonance_frequency)
    sample["frequency"] = resonance_frequency
    sample["previous_impedance"] = previous_impedance
    count += 1

###############################################################################
# Print error
# ~~~~~~~~~~~
# Print the number of range error.

print("number of range error: " + str(error_counter))

###############################################################################
# End data recovery step
# ~~~~~~~~~~~~~~~~~~~~~~
# End the data recovery step by dumping the dictionary list into a JSON file.
# Saving the data allows you to use it in another Python script.

json_file_path = os.path.join(hfss.working_directory, "ml_data_for_test.json")
with open(json_file_path, "w") as readfile:
    json.dump(samples, readfile)

###############################################################################
# Create machine learning algorithm
# ----------------------------------
# This section describes the second step, which is for creating the machine
# learning algorithm.
#
# Import training cases
# ~~~~~~~~~~~~~~~~~~~~~
# Import the 3,300 cases in the supplied JSON file to train the model. As mentioned
# earlier, you cannot use the small database that you generated earlier for training
# the model. Its 8 cases are used later to test the model.

path_folder = hfss.pyaedt_dir
training_file = os.path.join(path_folder, "misc", "ml_data_file_train_100MHz_1GHz.json")
with open(training_file) as readfile:
    my_dictio_list_train = json.load(readfile)

with open(json_file_path, "r") as readfile:
    my_dictio_list_test = json.load(readfile)

print(len(my_dictio_list_train))
print(len(my_dictio_list_test))

###############################################################################
# Create lists
# ~~~~~~~~~~~~
# Create four lists:
# 
# - One for the input of the training
# - One for the output of training
# - One for the input of the test
# - One for the output of the test

input_for_training_list = []
output_for_training_list = []
input_for_test_list = []
output_for_test_list = []

###############################################################################
# Fill list for input of training
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Fill the list for the input of the training with frequency, width, permittivity,
# and thickness so that the output is the length. The objective of this
# algorithm is to predict the length according to the rest.

for i in range(len(my_dictio_list_train)):
    freq_width_perm_thick = [
        my_dictio_list_train[i]["frequency"] * 1e9,
        my_dictio_list_train[i]["width"] * 1000,
        my_dictio_list_train[i]["permittivity"],
        my_dictio_list_train[i]["thickness"] * 1000,
    ]
    length = my_dictio_list_train[i]["length"] * 1000
    input_for_training_list.append(freq_width_perm_thick)
    output_for_training_list.append(length)

for i in range(len(my_dictio_list_test)):
    freq_width_perm_thick = [
        my_dictio_list_test[i]["frequency"] * 1e9,
        my_dictio_list_test[i]["width"] * 1000,
        my_dictio_list_test[i]["permittivity"],
        my_dictio_list_test[i]["thickness"] * 1000,
    ]
    length = my_dictio_list_test[i]["length"] * 1000
    input_for_test_list.append(freq_width_perm_thick)
    output_for_test_list.append(length)

print("number of test cases: " + str(len(output_for_test_list)))
print("number of training cases: " + str(len(output_for_training_list)))

###############################################################################
# Convert lists in array
# ~~~~~~~~~~~~~~~~~~~~~~
# Convert the lists in an array.

input_for_training_array = np.array(input_for_training_list, dtype=np.float32)
output_for_training_array = np.array(output_for_training_list, dtype=np.float32)
input_for_test_array = np.array(input_for_test_list, dtype=np.float32)
output_for_test_array = np.array(output_for_test_list, dtype=np.float32)

print("input array for training: " + str(input_for_training_array))
print("output array for training: " + str(output_for_training_array))

###############################################################################
# Create model
# ~~~~~~~~~~~~
# Create the model. Depending on the app, you can use different models.
# The easiest way to find the correct model for an app is to search
# for this app or one that is close to it.
# 
# To predict characteristics of a patch antenna (resonance frequency, bandwidth,
# and input impedance), you can use SVR (Support Vector Regression) or ANN
# (Analyze Neuronal Network). The following code uses SVR because it is easier
# to implement. ANN is a more general method that also works with other
# high frequency components. While it is more likely to work for other app,
# implementing ANN is much more complex.
#
# For SVR, there are three different kernels. For the patch antenna, RBF (Radial Basic
# Function) is preferred. There are three other arguments that have a big impact
# on the accuracy of the model: C, gamma, and epsilon. Sometimes they are given
# with the necessary model for the app. Otherwise, you can try different
# values and see which one is the best by measuring the accuracy of the model.
# To make this example shorter, ``C=1e4``. However, the optimal value
# in this app is ``C=5e4``.

svr_rbf = SVR(kernel="rbf", C=1e4, gamma="auto", epsilon=0.05)
regression = make_pipeline(StandardScaler(), svr_rbf)

###############################################################################
# Train model
# ~~~~~~~~~~~
# Train the model.

regression.fit(input_for_training_array, output_for_training_array)

###############################################################################
# Dump model into JOBLIB file
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Dump the model into a JOBLIB file using the same method as you used earlier
# for the JSON file.

model_file = os.path.join(hfss.working_directory, "svr_model.joblib")
joblib.dump(regression, model_file)

###############################################################################
# Implement model in PyAEDT method
# -------------------------------------
# This section describes the third step, which is for implementing the model
# in the PyAEDT method.
# 
# Load model
# ~~~~~~~~~~
# Load the model in another Python file to predict different cases.
# Here the correct model with ``C=5e4`` is loaded rather than the one you made
# earlier with ``C=1e4``.

model_path = os.path.join(path_folder, "misc", "patch_svr_model_100MHz_1GHz.joblib")
regression = joblib.load(model_path)

###############################################################################
# Predict length of patch
# ~~~~~~~~~~~~~~~~~~~~~~~
# Predict the length of the patch as a function of its resonant frequency and width
# and substrate thickness and permittivity.

prediction_of_length = regression.predict(input_for_test_list)

###############################################################################
# Measure model efficiency
# ~~~~~~~~~~~~~~~~~~~~~~~~
# Measure the model efficiency.

average_relative_gap = 0
counter_under_zero_five = 0
counter_under_one = 0
counter_under_two = 0
counter_under_five = 0
counter_under_ten = 0
counter_upper_ten = 0
rel_counter_under_one = 0
rel_counter_under_two = 0
rel_counter_under_five = 0
rel_counter_under_ten = 0
rel_counter_under_twenty = 0
rel_counter_upper_twenty = 0
for index in range(len(prediction_of_length)):
    print(
        "value: "
        + str(input_for_test_list[index])
        + ", prediction: "
        + str(prediction_of_length[index] * 1000)
        + ", reality: "
        + str(output_for_test_list[index] * 1000)
    )
    gap = abs(prediction_of_length[index] - output_for_test_list[index])
    relative_gap = gap / output_for_test_list[index]
    average_relative_gap = average_relative_gap + relative_gap
    if gap < 0.5:
        counter_under_zero_five += 1
    elif 0.5 <= gap < 1:
        counter_under_one += 1
    elif 1 <= gap < 2:
        counter_under_two += 1
    elif 2 <= gap < 5:
        counter_under_five += 1
    elif 5 <= gap < 10:
        counter_under_ten += 1
    else:
        counter_upper_ten += 1
    if relative_gap < 0.01:
        rel_counter_under_one += 1
    elif relative_gap < 0.02:
        rel_counter_under_two += 1
    elif relative_gap < 0.05:
        rel_counter_under_five += 1
    elif relative_gap < 0.1:
        rel_counter_under_ten += 1
    elif relative_gap < 0.2:
        rel_counter_under_twenty += 1
    else:
        rel_counter_upper_twenty += 1
average_relative_gap = average_relative_gap / len(prediction_of_length)

###############################################################################
# The first displays are the gap ``(prediction - real)``. The second displays are
# the relative gap ``((prediction - real)/real)``.

print("sample size: " + str(len(prediction_of_length)))
print("<0.5 : " + str(counter_under_zero_five))
print("<1 : " + str(counter_under_one))
print("<2 : " + str(counter_under_two))
print("<5 : " + str(counter_under_five))
print("<10 : " + str(counter_under_ten))
print(">10 : " + str(counter_upper_ten) + "\n")
print(
    "sum : "
    + str(
        counter_under_zero_five
        + counter_under_one
        + counter_under_two
        + counter_under_five
        + counter_under_ten
        + counter_upper_ten
    )
)

print("-------------------------------------------\n")
print("<0.01 : " + str(rel_counter_under_one))
print("<0.02 : " + str(rel_counter_under_two))
print("<0.05 : " + str(rel_counter_under_five))
print("<0.1 : " + str(rel_counter_under_ten))
print("<0.2 : " + str(rel_counter_under_twenty))
print(">0.2 : " + str(rel_counter_upper_twenty))
print(
    "sum : "
    + str(
        rel_counter_under_one
        + rel_counter_under_two
        + rel_counter_under_five
        + rel_counter_under_ten
        + rel_counter_under_twenty
        + rel_counter_upper_twenty
    )
)
print("average is : " + str(average_relative_gap))

###############################################################################
# Release AEDT
# ------------
# Release AEDT.

hfss.release_desktop()
