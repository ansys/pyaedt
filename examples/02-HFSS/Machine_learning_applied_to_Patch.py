"""
HFSS: Machine learning applied to Patch
---------------------------------------
This example shows how you can use PyAEDT to create a machine learning algorithm in three steps:
- Generate the database
- Create the machine learning algorithm
- Implement the model in a PyAEDT method
These three steps are in one file available for the example but it would be
better to separate them in different python file.
"""

import json
import os
import random
from math import sqrt

import joblib
import numpy as np
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVR

from pyaedt import Hfss
from pyaedt.modeler.stackup_3d import Stackup3D

##########################################################
# Set Non Graphical Mode.
# Default is False

non_graphical = os.getenv("PYAEDT_NON_GRAPHICAL", "False").lower() in ("true", "1", "t")

###############################################################################
# Generation of a database.
# ~~~~~~~~~~~~~~~~~~~~~~~~~
# Create function to randomly generate input. In this case there are 4 input: frequency, substrat permittivity,
# substrat thickness, patch width.
# Frequency is from 0.1GHz to 1GHz
# Permittivity is from 1 to 12
# In this example we will generate a data base of 1 frequencies x 2 permittivity x 2 thickness x 2 width.
# It will make 8 cases, it is too little for a real database. Indeed the cases generated will be use for test.
# For the training of the machine learning, we will use a previously generated database
# of more than 3300 different cases, 74 frequencies x 5 permittivity x 3 thickness x 3 width.

tuple_random_frequency_permittivity = []
frequency_list = [150 * 1e6]
for in_list in frequency_list:
    for i in range(2):
        random_permittivity = 1 + 11 * int(random.random() * 100) / 100
        temp_tuple = (in_list, random_permittivity)
        tuple_random_frequency_permittivity.append(temp_tuple)

###############################################################################
# Thickness is generated from 0.0025 to 0.055 of the wave length in the void.
# Width is generated from 0.5 to 1.5 of the optimal theoretical width:
# c / (2 * frequency * sqrt((permittivity + 1) / 2))
# For each couple of frequency-permittivity, it generates 3 random thickness and 3 random width
# Then patch length is calculated using the analytic formula.
# It is important to do like that to reduce the sweep frequency needed for the data recovery.
# Every case is stored in a list of dictionary.

dictionary_list = []
c = 2.99792458e8
for couple in tuple_random_frequency_permittivity:
    list_thickness = []
    list_width = []
    frequency = couple[0]
    permittivity = couple[1]
    er = permittivity
    wave_length_0 = c / frequency

    min_thickness = 0.0025 * wave_length_0
    inter_thickness = 0.01 * wave_length_0
    max_thickness = 0.055 * wave_length_0
    for i in range(2):
        random_int = random.randint(0, 1)
        if random_int == 0:
            thickness = min_thickness + (inter_thickness - min_thickness) * random.random()
        else:
            thickness = inter_thickness + (max_thickness - inter_thickness) * random.random()
        list_thickness.append(thickness)

    min_width = 0.5 * c / (2 * frequency * sqrt((er + 1) / 2))
    max_width = 1.5 * c / (2 * frequency * sqrt((er + 1) / 2))
    for i in range(2):
        width = min_width + (max_width - min_width) * random.random()
        list_width.append(width)

    for width in list_width:
        for thickness in list_thickness:
            effective_permittivity = (er + 1) / 2 + (er - 1) / (2 * sqrt(1 + 10 * thickness / width))
            er_e = effective_permittivity
            w_h = width / thickness
            added_length = 0.412 * thickness * (er_e + 0.3) * (w_h + 0.264) / ((er_e - 0.258) * (w_h + 0.813))
            wave_length = c / (frequency * sqrt(er_e))
            length = wave_length / 2 - 2 * added_length
            dictionary = {
                "frequency": frequency,
                "permittivity": permittivity,
                "thickness": thickness,
                "width": width,
                "length": length,
                "previous_impedance": 0,
            }
            dictionary_list.append(dictionary)

print("List of data: " + str(dictionary_list))
print("Its length is: " + str(len(dictionary_list)))

###############################################################################
# Now, the HFSS design will be generated using the PyAEDT Stackup3D function.
# Open an Hfss Design and create the stackup, add the different layers, add the patch.
# In Stackup Library, most things are already parameterized like the layers and the patch.
desktopVersion = "2022.2"

hfss = Hfss(new_desktop_session=True, solution_type="Terminal", non_graphical=non_graphical,
            specified_version=desktopVersion)

stackup = Stackup3D(hfss)
ground = stackup.add_ground_layer("ground", material="copper", thickness=0.035, fill_material="air")
dielectric = stackup.add_dielectric_layer("dielectric", thickness=10, material="Duroid (tm)")
signal = stackup.add_signal_layer("signal", material="copper", thickness=0.035, fill_material="air")
patch = signal.add_patch(patch_length=1009.86, patch_width=1185.9, patch_name="Patch", frequency=100e6)

###############################################################################
# The layers are resized around the patch so that they change when the patch changes in a parametric.

stackup.resize_around_element(patch)

###############################################################################
# A lumped port is created and parametrized in function of the patch.

patch.create_lumped_port(reference_layer=ground, opposite_side=False, port_name="one")

###############################################################################
# A line is created and parametrized in function of the patch length to ensure
# that the air box is large enough in the normal direction of the patch

points_list = [
    [patch.position_x.name, patch.position_y.name, signal.elevation.name],
    [patch.position_x.name, patch.position_y.name, signal.elevation.name + " + " + patch.length.name],
]
hfss.modeler.primitives.create_polyline(position_list=points_list, name="adjust_airbox")
pad_percent = [50, 50, 300, 50, 50, 10]
region = hfss.modeler.primitives.create_region(pad_percent)
hfss.assign_radiation_boundary_to_objects(region)

hfss.plot(show=False)

###############################################################################
# Then a setup and a frequency sweep will be created by frequency.

print(len(dictionary_list))
for freq in frequency_list:
    frequency_name = str(int(freq * 1e-6))
    setup_name = "Setup_" + str(frequency_name)
    current_setup = hfss.create_setup(setupname=setup_name)
    current_setup.props["Frequency"] = str(freq) + "Hz"
    current_setup.props["MaximumPasses"] = 30
    current_setup.props["MinimumConvergedPasses"] = 2
    current_setup.props["MaxDeltaS"] = 0.05
    current_setup.update()
    current_setup["SaveAnyFields"] = False

    freq_start = freq * 0.75
    freq_stop = freq * 1.25
    sweep_name = "Sweep_of_" + setup_name
    hfss.create_linear_count_sweep(
        setupname=setup_name,
        unit="Hz",
        freqstart=freq_start,
        freqstop=freq_stop,
        num_of_freq_points=25000,
        sweepname="Sweep_of_" + setup_name,
        save_fields=False,
        sweep_type="Interpolating",
    )


###############################################################################
# Define a function to recovery the index of the resonance frequency.


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
# In this loop, we create a parametric by case and associate it with a setup.
# The parametric is composed of the patch length and width and substrat permittivity and thickness.
# For each, we measure the real resonance frequency and then we have our data length, width,
# permittivity and thickness which correspond to a resonance frequency.
# There is an error counter to verify that the resonance frequency is contained in the sweep.
# To make it easy, the length of each case was calculated using the analytic formula.

error_counter = []
for i in range(len(dictionary_list)):
    dictio = dictionary_list[i]
    frequency_name = str(int(dictio["frequency"] * 1e-6))
    setup_name = "Setup_" + str(frequency_name)
    sweep_name = "Sweep_of_" + setup_name
    length_variation = dictio["length"] * 1e3
    width_variation = dictio["width"] * 1e3
    thickness_variation = dictio["thickness"] * 1e3
    permittivity_variation = dictio["permittivity"]
    param_name = "para_" + setup_name + "_" + str(i)
    this_param = hfss.parametrics.add(
        patch.length.name,
        length_variation,
        length_variation,
        step=1,
        variation_type="LinearCount",
        solution=setup_name,
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
        "$cloned_Duroid__tm__permittivity",
        permittivity_variation,
        permittivity_variation,
        step=1,
        unit=None,
        variation_type="LinearCount",
    )
    hfss.analyze_setup(param_name, num_cores=4, num_tasks=None)
    data = hfss.post.get_solution_data(
        "Zt(one_T1, one_T1)",
        setup_sweep_name=setup_name + " : " + sweep_name,
        domain="Sweep",
        variations={
            patch.length.name: [str(length_variation) + "mm"],
            patch.width.name: [str(width_variation) + "mm"],
            dielectric.thickness.name: [str(thickness_variation) + "mm"],
            "$cloned_Duroid__tm__permittivity": [str(permittivity_variation)],
        },
        polyline_points=25000,
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
    dictio["frequency"] = resonance_frequency
    dictio["previous_impedance"] = previous_impedance

###############################################################################
# Print the number of error.

print("number of range error: " + str(error_counter))

###############################################################################
# End of the data recovery step.
# Dump the dictionary list in a json file to save the data and maybe use it in another python script.

json_file_path = os.path.join(hfss.working_directory, "ml_data_for_test.json")
with open(json_file_path, "w") as readfile:
    json.dump(dictionary_list, readfile)

###############################################################################
# Construction of machine learning model.
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# First we import the 3300 cases json file, not the one we construct before because it is too small.
# The one we generated is imported to test our model after the training.

path_folder = hfss.pyaedt_dir
training_file = os.path.join(path_folder, "misc", "ml_data_file_train_100GMHz_1GHz.json")
with open(training_file) as readfile:
    my_dictio_list_train = json.load(readfile)

with open(json_file_path, "r") as readfile:
    my_dictio_list_test = json.load(readfile)

print(len(my_dictio_list_train))
print(len(my_dictio_list_test))

###############################################################################
# We create four list, one list for the input of the training, one list for the output of training,
# one list for the input of the test, one list for the output of the test.

input_for_training_list = []
output_for_training_list = []
input_for_test_list = []
output_for_test_list = []

###############################################################################
# The list of input is filled with frequency, width, permittivity and thickness, and so the output is the length.
# Indeed the objective of this algorithm is to predict the length according to the rest.

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
# We convert the lists in array.

input_for_training_array = np.array(input_for_training_list, dtype=np.float32)
output_for_training_array = np.array(output_for_training_list, dtype=np.float32)
input_for_test_array = np.array(input_for_test_list, dtype=np.float32)
output_for_test_array = np.array(output_for_test_list, dtype=np.float32)

print("input array for training: " + str(input_for_training_array))
print("output array for training: " + str(output_for_training_array))

###############################################################################
# We create the model. Depending on the application different models can be used.
# To find the correct model for an application the easiest way is to search
# for this application or one that is close to it.
# To predict characteristic of a patch antenna (resonance frequency, bandwidth, input impedance)
# you can use a Support Vector Regression (like in this example) or Analyse Neuronal Network.
# SVR is easier to implement.
# ANN is a more general way of doing that also works with other high frequency components and
# is more likely to work for other applications but its implementation is much more complex.
# For the SVR, there are three different kernels, for the patch antenna the preferred one is the Radial Basic Function.
# There are three other arguments that have a big impact on the accuracy of the model, C, gamma and epsilon.
# Sometimes they are given with the necessary model for the application.
# Else, you can try different values and see which one is the best by measuring the accuracy of the model.
# C is equal to 1e4 to make this example shorter, but the optimal value in this application is 5e4.

svr_rbf = SVR(kernel="rbf", C=1e4, gamma="auto", epsilon=0.05)
regression = make_pipeline(StandardScaler(), svr_rbf)

###############################################################################
# We train the model.

regression.fit(input_for_training_array, output_for_training_array)

###############################################################################
# We can dump the model into a joblib file with the same method as for a json file.

model_file = os.path.join(hfss.working_directory, "svr_model.joblib")
joblib.dump(regression, model_file)

###############################################################################
# Implement the model in the PyAEDT method and test the model.
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# So we can load the model in another python file and predict different cases.
# But here, we load the correct model with C=5e4 rather than the one made in this example.

model_path = os.path.join(path_folder, "misc", "patch_svr_model_100MHz_1GHz.joblib")
regression = joblib.load(model_path)

###############################################################################
# The model we developed will predict the length of a patch as a function of
# its resonant frequency, width, substrate thickness and permittivity.

prediction_of_length = regression.predict(input_for_test_list)

###############################################################################
# Finally we will measure the efficiency of our model.

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
# The first displays are the gap (prediction - real) and the second the relative gap  ((prediction - real)/real).

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
# Release the desktop.

hfss.release_desktop()
