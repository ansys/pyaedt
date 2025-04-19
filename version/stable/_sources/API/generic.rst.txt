Generic
=======

PyAEDT has some generic features.


File utils
~~~~~~~~~~

The following methods allows to read and parse files.

.. currentmodule:: ansys.aedt.core.generic.file_utils

.. autosummary::
   :toctree: _autosummary
   :nosignatures:

   normalize_path
   get_filename_without_extension
   check_and_download_file
   check_if_path_exists
   check_and_download_folder
   generate_unique_name
   generate_unique_folder_name
   generate_unique_project_name
   recursive_glob
   is_project_locked
   remove_project_lock
   open_file
   read_json
   read_toml
   read_csv
   read_csv_pandas
   write_csv
   read_tab
   read_xlsx
   get_dxf_layers
   read_component_file
   parse_excitation_file
   tech_to_control_file
   read_configuration_file
   write_configuration_file
   compute_fft
