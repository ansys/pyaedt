"""
Maxwell 3D: Transformer
-----------------------
This example shows how you can use PyAEDT to set core loss given a set
of BP curves at different frequencies.
"""
###############################################################################
# Perform required imports
# ~~~~~~~~~~~~~~~~~~~~~~~~
# Perform required imports.

from pyaedt import downloads
from pyaedt import generate_unique_folder_name
from pyaedt import Maxwell3d
from pyaedt.generic.constants import unit_converter
from pyaedt.generic.general_methods import read_csv


def _convert_tuple_to_float(curves_csv):
    curves_csv.pop(0)
    new_list = []
    for tup in curves_csv:
        float_tuple = []
        for bp in tup:
            float_tuple.append(float(bp))
        new_list.append(float_tuple)
    return new_list


#################################################################################
# Download .aedt file example
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Set local temporary folder to export the .aedt file to.

temp_folder = generate_unique_folder_name()
aedt_file = downloads.download_file("core_loss_transformer", "Ex2-PlanarTransformer_2023R2.aedt", temp_folder)
freq_curve_csv_1MHz = downloads.download_file("core_loss_transformer", "mf3_1MHz.csv", temp_folder)
freq_curve_csv_100kHz = downloads.download_file("core_loss_transformer", "mf3_100kHz.csv", temp_folder)
freq_curve_csv_200kHz = downloads.download_file("core_loss_transformer", "mf3_200kHz.csv", temp_folder)
freq_curve_csv_400kHz = downloads.download_file("core_loss_transformer", "mf3_400kHz.csv", temp_folder)
freq_curve_csv_700kHz = downloads.download_file("core_loss_transformer", "mf3_700kHz.csv", temp_folder)

curves_csv_1MHz = read_csv(filename=freq_curve_csv_1MHz)
curves_csv_100kHz = read_csv(filename=freq_curve_csv_100kHz)
curves_csv_200kHz = read_csv(filename=freq_curve_csv_200kHz)
curves_csv_400kHz = read_csv(filename=freq_curve_csv_400kHz)
curves_csv_700kHz = read_csv(filename=freq_curve_csv_700kHz)

float_curves_csv_1MHz = _convert_tuple_to_float(curves_csv_1MHz)
float_curves_csv_100kHz = _convert_tuple_to_float(curves_csv_100kHz)
float_curves_csv_200kHz = _convert_tuple_to_float(curves_csv_200kHz)
float_curves_csv_400kHz = _convert_tuple_to_float(curves_csv_400kHz)
float_curves_csv_700kHz = _convert_tuple_to_float(curves_csv_700kHz)

###############################################################################
# Launch AEDT
# ~~~~~~~~~~~
# Launch AEDT 2023 R2 in graphical mode.

m3d = Maxwell3d(projectname=aedt_file,
                specified_version="2023.2",
                new_desktop_session=True,
                non_graphical=False)

###############################################################################
# Create new material
# ~~~~~~~~~~~~~~~~~~~
# Create new material.

mat1 = m3d.materials.add_material("newmat1")

###############################################################################
# Set core loss at frequency from csv
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Delete first row of csv file (header), convert frequency unit,
# set core loss at frequency.

freq = unit_converter(1, unit_system="Freq", input_units="MHz", output_units="Hz")
bp_at_1MHz = {freq: float_curves_csv_1MHz}
m3d.materials[mat1.name].set_coreloss_at_frequency(bp_at_1MHz, core_loss_model_type="Power Ferrite")

###############################################################################
# Get core loss coefficients at a given frequency
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Get core loss coefficients at a given frequency.

coefficients_at_1MHz = m3d.materials[mat1.name].get_core_loss_coefficients(points_list_at_freq=bp_at_1MHz)

###############################################################################
# Set core loss at frequency manually
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Add a new material and set core loss at frequency manually

mat2 = m3d.materials.add_material("newmat2")
freq = unit_converter(25, unit_system="Freq", input_units="kHz", output_units="Hz")
bp_at_25kHz = {freq: [[0, 0],
                      [0.101574399, 12.35342661],
                      [0.121373767, 20.37880642],
                      [0.128395017, 24.34856831],
                      [0.14101124, 29.74609439],
                      [0.153422388, 38.41855824],
                      [0.170084547, 48],
                      [0.178245116, 58],
                      [0.201342228, 78],
                      [0.211002525, 100],
                      [0.242854412, 125],
                      [0.256903094, 154.3141664],
                      [0.276906905, 184.3743419],
                      [0.287485544, 217.8533543]]}
m3d.materials[mat2.name].set_coreloss_at_frequency(bp_at_25kHz, core_loss_model_type="Power Ferrite")
coefficients_at_25kHz = m3d.materials[mat1.name].get_core_loss_coefficients(points_list_at_freq=bp_at_25kHz)

###############################################################################
# Set core loss at frequencies
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Provide BP values for a set of frequencies

mat3 = m3d.materials.add_material("newmat3")
freq_100kHz = unit_converter(100, unit_system="Freq", input_units="kHz", output_units="Hz")
freq_200kHz = unit_converter(200, unit_system="Freq", input_units="kHz", output_units="Hz")
freq_400kHz = unit_converter(400, unit_system="Freq", input_units="kHz", output_units="Hz")
freq_700kHz = unit_converter(700, unit_system="Freq", input_units="kHz", output_units="Hz")
bp = {freq_100kHz: float_curves_csv_100kHz,
      freq_200kHz: float_curves_csv_200kHz,
      freq_400kHz: float_curves_csv_400kHz,
      freq_700kHz: float_curves_csv_700kHz}
m3d.materials[mat3.name].set_coreloss_at_frequency(bp, core_loss_model_type="Power Ferrite")
coefficients_vs_freqs = m3d.materials[mat1.name].get_core_loss_coefficients(points_list_at_freq=bp)

###################################################################################
# Save project and close AEDT
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Save the project and close AEDT.

m3d.save_project()
m3d.release_desktop()
