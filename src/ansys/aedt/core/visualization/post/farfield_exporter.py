# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 - 2024 ANSYS, Inc. and/or its affiliates.
# SPDX-License-Identifier: MIT
#
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import json
import os
import shutil
import time

from ansys.aedt.core.application.analysis_hf import ScatteringMethods
from ansys.aedt.core.application.variables import decompose_variable_value
from ansys.aedt.core.generic.constants import unit_converter
from ansys.aedt.core.generic.general_methods import check_and_download_folder
from ansys.aedt.core.generic.general_methods import open_file
from ansys.aedt.core.generic.general_methods import pyaedt_function_handler
from ansys.aedt.core.generic.settings import settings
from ansys.aedt.core.visualization.advanced.farfield_visualization import FfdSolutionData

np = None
pv = None

try:
    import numpy as np
except ImportError:  # pragma: no cover
    np = None
try:
    import pyvista as pv
except ImportError:  # pragma: no cover
    pv = None


class FfdSolutionDataExporter:
    """Class to enable export of embedded element pattern data from HFSS.

    An instance of this class is returned from the
    :meth:`ansys.aedt.core.Hfss.get_antenna_data` method. This method allows creation of
    the embedded
    element pattern files for an antenna that have been solved in HFSS. The
    ``metadata_file`` properties can then be passed as arguments to
    instantiate an instance of the :class:`ansys.aedt.core.generic.farfield_visualization.FfdSolutionData` class for
    subsequent analysis and postprocessing of the array data.

    Note that this class is derived from the :class:`FfdSolutionData` class and can be used directly for
    far-field postprocessing and array analysis, but it remains a property of the
    :class:`ansys.aedt.core.Hfss` application.

    Parameters
    ----------
    app : :class:`ansys.aedt.core.Hfss`
        HFSS application instance.
    sphere_name : str
        Infinite sphere to use.
    setup_name : str
        Name of the setup. Make sure to build a setup string in the form of ``"SetupName : SetupSweep"``.
    frequencies : list
        Frequency list to export. Specify either a list of strings with units or a list of floats in Hertz units.
        For example, ``["9GHz", 9e9]``.
    variations : dict, optional
        Dictionary of all families including the primary sweep. The default value is ``None``.
    overwrite : bool, optional
        Whether to overwrite the existing far field solution data. The default is ``True``.
    export_touchstone : bool, optional
        Whether to export touchstone file. The default is ``False``. Working from 2024 R1.
    set_phase_center_per_port : bool, optional
        Set phase center per port location. The default is ``True``.

    Examples
    --------
    >>> from ansys.aedt.core
    >>> app = ansys.aedt.core.Hfss(version="2023.2", design="Antenna")
    >>> setup_name = "Setup1 : LastAdaptive"
    >>> frequencies = [77e9]
    >>> sphere = "3D"
    >>> data = app.get_antenna_data(frequencies,setup_name,sphere)
    >>> data.plot_3d(quantity_format="dB10")
    """

    def __init__(
        self,
        app,
        sphere_name,
        setup_name,
        frequencies,
        variations=None,
        overwrite=True,
        export_touchstone=True,
        set_phase_center_per_port=True,
    ):
        # Public
        self.sphere_name = sphere_name
        self.setup_name = setup_name

        if not variations:
            variations = app.available_variations.nominal_w_values_dict_w_dependent
        else:
            # Set variation to Nominal
            for var_name, var_value in variations.items():
                app[var_name] = var_value

        self.variations = variations
        self.overwrite = overwrite
        self.export_touchstone = export_touchstone
        if not isinstance(frequencies, list):
            self.frequencies = [frequencies]
        else:
            self.frequencies = frequencies

        # Private
        self.__app = app
        self.__model_info = {}
        self.__farfield_data = None
        self.__metadata_file = ""

        if self.__app.desktop_class.is_grpc_api and set_phase_center_per_port:
            self.__app.set_phase_center_per_port()
        else:  # pragma: no cover
            self.__app.logger.warning("Set phase center in port location manually.")

    @property
    def model_info(self):
        """List of models."""
        return self.__model_info

    @property
    def farfield_data(self):
        """Farfield data."""
        return self.__farfield_data

    @property
    def metadata_file(self):
        """Metadata file."""
        return self.__metadata_file

    @pyaedt_function_handler()
    def export_farfield(self):
        """Export far field solution data of each element."""

        # Output directory
        exported_name_map = "element.txt"
        solution_setup_name = self.setup_name.replace(":", "_").replace(" ", "")
        full_setup = "{}-{}".format(solution_setup_name, self.sphere_name)
        export_path = "{}/{}/".format(self.__app.working_directory, full_setup)
        local_path = "{}/{}/".format(settings.remote_rpc_session_temp_folder, full_setup)
        export_path = os.path.abspath(check_and_download_folder(local_path, export_path))

        # 2024.1
        file_path_xml = os.path.join(export_path, self.__app.design_name + ".xml")
        # 2023.2
        file_path_txt = os.path.join(export_path, exported_name_map)

        input_file = file_path_xml
        if self.__app.desktop_class.aedt_version_id < "2024.1":  # pragma: no cover
            input_file = file_path_txt

        # Create directory or check if files already exist
        if settings.remote_rpc_session:  # pragma: no cover
            settings.remote_rpc_session.filemanager.makedirs(export_path)
            file_exists = settings.remote_rpc_session.filemanager.pathexists(input_file)
        elif not os.path.exists(export_path):
            os.makedirs(export_path)
            file_exists = False
        else:
            file_exists = os.path.exists(input_file)

        time_before = time.time()

        # Export far field
        if self.overwrite or not file_exists:
            if self.__app.desktop_class.aedt_version_id < "2024.1":  # pragma: no cover
                is_exported = self.__app.export_element_pattern(
                    frequencies=self.frequencies,
                    setup=self.setup_name,
                    sphere=self.sphere_name,
                    variations=self.variations,
                    output_dir=export_path,
                )
                if not is_exported:  # pragma: no cover
                    return False
                if self.export_touchstone:
                    scattering = ScatteringMethods(self.__app)
                    setup_sweep_parts = self.setup_name.split(":")

                    setup_name = setup_sweep_parts[0].strip()
                    sweep_name = setup_sweep_parts[1].strip()

                    touchstone_file = scattering.export_touchstone(setup=setup_name, sweep=sweep_name)

                    if touchstone_file:
                        touchstone_name = os.path.basename(touchstone_file)
                        output_file = os.path.join(export_path, touchstone_name)
                        shutil.move(touchstone_file, output_file)
            else:
                is_exported = self.__app.export_antenna_metadata(
                    frequencies=self.frequencies,
                    setup=self.setup_name,
                    sphere=self.sphere_name,
                    variations=self.variations,
                    output_dir=export_path,
                    export_element_pattern=True,
                    export_objects=False,
                    export_touchstone=True,
                    export_power=True,
                )
                if not is_exported:  # pragma: no cover
                    return False
        else:
            self.__app.logger.info("Using existing element patterns files.")

        # Export geometry
        if os.path.isfile(input_file):
            geometry_path = os.path.join(export_path, "geometry")
            if not os.path.exists(geometry_path):
                os.mkdir(geometry_path)
            obj_list = self.__create_geometries(geometry_path)
            if obj_list:
                self.__model_info["object_list"] = obj_list

            if self.__app.component_array:
                component_array = self.__app.component_array[self.__app.component_array_names[0]]
                self.__model_info["component_objects"] = component_array.get_component_objects()
                self.__model_info["cell_position"] = component_array.get_cell_position()
                self.__model_info["array_dimension"] = [
                    component_array.a_length,
                    component_array.b_length,
                    component_array.a_length / component_array.a_size,
                    component_array.b_length / component_array.b_size,
                ]
                self.__model_info["lattice_vector"] = component_array.lattice_vector()

        # Create PyAEDT Metadata
        var = []
        if self.variations:
            for k, v in self.variations.items():
                var.append("{}='{}'".format(k, v))
            variation = " ".join(var)
        else:
            variation = self.__app.odesign.GetNominalVariation()

        power = {}

        if self.__app.desktop_class.aedt_version_id < "2024.1":

            available_categories = self.__app.post.available_quantities_categories()
            excitations = []
            is_power = True
            if "Active VSWR" in available_categories:  # pragma: no cover
                quantities = self.post.available_report_quantities(quantities_category="Active VSWR")
                for quantity in quantities:
                    excitations.append("ElementPatterns:=")
                    excitations.append(quantity.strip("ActiveVSWR(").strip(")"))
            elif "Terminal VSWR" in available_categories:
                quantities = self.__app.post.available_report_quantities(quantities_category="Terminal VSWR")
                for quantity in quantities:
                    excitations.append("ElementPatterns:=")
                    excitations.append(quantity.strip("VSWRt(").strip(")"))
                is_power = False
            elif "Gamma" in available_categories:
                quantities = self.__app.post.available_report_quantities(quantities_category="Gamma")
                for quantity in quantities:
                    excitations.append("ElementPatterns:=")
                    excitations.append(quantity.strip("Gamma(").strip(")"))
            else:  # pragma: no cover
                for excitation in self.__app.get_all_sources():
                    excitations.append("ElementPatterns:=")
                    excitations.append(excitation)
            for excitation_cont1 in range(len(excitations)):
                sources = {}
                incident_power = {}
                accepted_power = {}
                radiated_power = {}
                unit = "V"
                if is_power:
                    unit = "W"
                active_element = excitations[0]
                for excitation_cont2, port in enumerate(excitations):
                    if excitation_cont1 == excitation_cont2:
                        active_element = port
                        sources[port] = (f"1{unit}", "0deg")
                    else:
                        sources[port] = (f"0{unit}", "0deg")

                power[active_element] = {}

                self.__app.edit_sources(sources)

                report = self.__app.post.reports_by_category.antenna_parameters(
                    "IncidentPower", self.setup_name, self.sphere_name
                )
                data = report.get_solution_data()
                incident_powers = data.data_magnitude()

                report = self.__app.post.reports_by_category.antenna_parameters(
                    "RadiatedPower", self.setup_name, self.sphere_name
                )
                data = report.get_solution_data()
                radiated_powers = data.data_magnitude()

                report = self.__app.post.reports_by_category.antenna_parameters(
                    "AcceptedPower", self.setup_name, self.sphere_name
                )
                data = report.get_solution_data()
                accepted_powers = data.data_magnitude()

                for freq_cont, freq_str in enumerate(self.frequencies):
                    frequency = freq_str
                    if isinstance(freq_str, str):
                        frequency, units = decompose_variable_value(freq_str)
                        frequency = unit_converter(frequency, "Freq", units, "Hz")
                    incident_power[frequency] = incident_powers[freq_cont]
                    radiated_power[frequency] = radiated_powers[freq_cont]
                    accepted_power[frequency] = accepted_powers[freq_cont]

                power[active_element]["IncidentPower"] = incident_power
                power[active_element]["AcceptedPower"] = accepted_power
                power[active_element]["RadiatedPower"] = radiated_power

        pyaedt_metadata_file = FfdSolutionDataExporter.export_pyaedt_antenna_metadata(
            input_file=input_file, output_dir=export_path, variation=variation, model_info=self.model_info, power=power
        )
        if not pyaedt_metadata_file:  # pragma: no cover
            return False
        elapsed_time = time.time() - time_before
        self.__app.logger.info("Exporting embedded element patterns.... Done: %s seconds", elapsed_time)
        self.__metadata_file = pyaedt_metadata_file
        self.__farfield_data = FfdSolutionData(pyaedt_metadata_file)
        return pyaedt_metadata_file

    @staticmethod
    @pyaedt_function_handler()
    def export_pyaedt_antenna_metadata(
        input_file, output_dir, variation=None, model_info=None, power=None, touchstone_file=None
    ):
        """Obtain PyAEDT metadata JSON file from AEDT metadata XML file or embedded element pattern TXT file.

        Parameters
        ----------
        input_file : str
            Full path to the XML or TXT file.
        output_dir : str
            Full path to save the file to.
        variation : str, optional
            Label to identify corresponding variation.
        model_info : dict, optional
        power : dict, optional
            Dictionary with information of the incident power for each frequency.
            The default is ``None``, in which case an empty dictionary is applied.
            From AEDT 2024.1, this information is available from the XML input file.
            For example, the dictionary format for a two element farfield
            data = power[1000000000.0]["IncidentPower"]
            data = [1, 0.99]
        touchstone_file : str, optional
            Touchstone file name. The default is ``None``.

        Returns
        -------
        str
            Metadata JSON file.
        """
        from ansys.aedt.core.post.touchstone_parser import find_touchstone_files

        if not variation:
            variation = "Nominal"

        if not power:
            power = {}

        if not touchstone_file:
            touchstone_file = ""

        pyaedt_metadata_file = os.path.join(output_dir, "pyaedt_antenna_metadata.json")
        items = {"variation": variation, "element_pattern": {}, "touchstone_file": touchstone_file}

        if os.path.isfile(input_file) and os.path.basename(input_file).split(".")[1] == "xml":
            # Metadata available from 2024.1
            antenna_metadata = FfdSolutionDataExporter.antenna_metadata(input_file)

            # Find all ffd files and move them to main directory
            for dir_path, _, filenames in os.walk(output_dir):
                ffd_files = [file for file in filenames if file.endswith(".ffd")]
                sNp_files = find_touchstone_files(dir_path)
                if ffd_files:
                    # Move ffd files to main directory
                    for ffd_file in ffd_files:
                        output_file = os.path.join(output_dir, ffd_file)
                        pattern_file = os.path.join(dir_path, ffd_file)
                        shutil.move(pattern_file, output_file)
                if sNp_files and not touchstone_file:
                    # Only one Touchstone allowed
                    sNp_name, sNp_path = next(iter(sNp_files.items()))
                    output_file = os.path.join(output_dir, sNp_name)
                    exported_touchstone_file = os.path.join(sNp_path)
                    shutil.move(exported_touchstone_file, output_file)
                    items["touchstone_file"] = sNp_name

            for metadata in antenna_metadata:

                incident_power = {}
                for i_freq, i_power_value in metadata["incident_power"].items():
                    frequency = i_freq
                    if isinstance(i_freq, str):
                        frequency, units = decompose_variable_value(i_freq)
                        if units:
                            frequency = unit_converter(frequency, "Freq", units, "Hz")
                    incident_power[frequency] = float(i_power_value)

                radiated_power = {}
                for i_freq, i_power_value in metadata["radiated_power"].items():
                    frequency = i_freq
                    if isinstance(i_freq, str):
                        frequency, units = decompose_variable_value(i_freq)
                        if units:
                            frequency = unit_converter(frequency, "Freq", units, "Hz")
                    radiated_power[frequency] = float(i_power_value)

                accepted_power = {}
                for i_freq, i_power_value in metadata["accepted_power"].items():
                    frequency = i_freq
                    if isinstance(i_freq, str):
                        frequency, units = decompose_variable_value(i_freq)
                        if units:
                            frequency = unit_converter(frequency, "Freq", units, "Hz")
                    accepted_power[frequency] = float(i_power_value)

                pattern = {
                    "file_name": metadata["file_name"],
                    "location": metadata["location"],
                    "incident_power": incident_power,
                    "radiated_power": radiated_power,
                    "accepted_power": accepted_power,
                }

                items["element_pattern"][metadata["name"]] = pattern
                pattern_file = os.path.join(output_dir, metadata["file_name"])
                if not os.path.isfile(pattern_file):  # pragma: no cover
                    return False

        elif os.path.isfile(input_file) and os.path.basename(input_file).split(".")[1] == "txt":

            # Find all ffd files and move them to main directory
            for dir_path, _, _ in os.walk(output_dir):
                sNp_files = find_touchstone_files(dir_path)
                if sNp_files and not touchstone_file:
                    # Only one Touchstone allowed
                    sNp_name, sNp_path = next(iter(sNp_files.items()))
                    output_file = os.path.join(output_dir, sNp_name)
                    exported_touchstone_file = os.path.join(sNp_path)
                    shutil.move(exported_touchstone_file, output_file)
                    items["touchstone_file"] = sNp_name
                    break

            with open_file(input_file, "r") as file:
                # Skip the first line
                file.readline()
                # Read and process the remaining lines
                for line in file:
                    antenna_metadata = line.strip().split()
                    if len(antenna_metadata) == 5:
                        element_name = antenna_metadata[0]
                        file_name = antenna_metadata[1]
                        if ".ffd" not in file_name:
                            file_name = file_name + ".ffd"
                        incident_power = None
                        radiated_power = None
                        accepted_power = None
                        if power:
                            incident_power = power[element_name]["IncidentPower"]
                            radiated_power = power[element_name]["RadiatedPower"]
                            accepted_power = power[element_name]["AcceptedPower"]

                        pattern = {
                            "file_name": file_name,
                            "location": [
                                float(antenna_metadata[2]),
                                float(antenna_metadata[3]),
                                float(antenna_metadata[4]),
                            ],
                            "incident_power": incident_power,
                            "radiated_power": radiated_power,
                            "accepted_power": accepted_power,
                        }
                        items["element_pattern"][antenna_metadata[0]] = pattern

        items["model_info"] = []
        if model_info:
            if "object_list" in model_info:
                items["model_info"] = model_info["object_list"]

            required_array_keys = ["array_dimension", "component_objects", "lattice_vector", "cell_position"]

            if all(key in model_info for key in required_array_keys):
                items["component_objects"] = model_info["component_objects"]
                items["cell_position"] = model_info["cell_position"]
                items["array_dimension"] = model_info["array_dimension"]
                items["lattice_vector"] = model_info["lattice_vector"]

        with open_file(pyaedt_metadata_file, "w") as f:
            json.dump(items, f, indent=2)
        return pyaedt_metadata_file

    @staticmethod
    @pyaedt_function_handler()
    def antenna_metadata(input_file):
        """Obtain metadata information from metadata XML file.

        Parameters
        ----------
        input_file : str
            Full path to the XML file.

        Returns
        -------
        dict
            Metadata information.

        """
        import xml.etree.ElementTree as ET  # nosec

        # Load the XML file
        tree = ET.parse(input_file)  # nosec
        root = tree.getroot()

        element_patterns = root.find("ElementPatterns")

        sources = []
        if element_patterns is None:  # pragma: no cover
            print("Element Patterns section not found in XML.")
        else:
            cont = 0
            # Iterate over each Source element
            for source in element_patterns.findall("Source"):
                source_info = {
                    "name": source.get("name"),
                    "file_name": source.find("Filename").text.strip(),
                    "location": source.find("ReferenceLocation").text.strip().split(","),
                }

                # Iterate over Power elements
                power_info = source.find("PowerInfo")
                if power_info is not None:
                    source_info["incident_power"] = {}
                    source_info["accepted_power"] = {}
                    source_info["radiated_power"] = {}
                    for power in power_info.findall("Power"):
                        freq = power.get("Freq")
                        source_info["incident_power"][freq] = {}
                        source_info["incident_power"][freq] = power.find("IncidentPower").text.strip()
                        source_info["accepted_power"][freq] = {}
                        source_info["accepted_power"][freq] = power.find("AcceptedPower").text.strip()
                        source_info["radiated_power"][freq] = {}
                        source_info["radiated_power"][freq] = power.find("RadiatedPower").text.strip()

                sources.append(source_info)
                cont += 1
        return sources

    @pyaedt_function_handler()
    def __create_geometries(self, export_path):
        """Export the geometry in OBJ format."""
        self.__app.logger.info("Exporting geometry...")
        model_pv = self.__app.post.get_model_plotter_geometries(plot_air_objects=False)
        obj_list = {}
        for obj in model_pv.objects:
            object_name = os.path.basename(obj.path)
            name = os.path.splitext(object_name)[0]
            original_path = os.path.dirname(obj.path)
            new_path = os.path.join(os.path.abspath(export_path), object_name)

            if not os.path.exists(new_path):
                new_path = shutil.move(obj.path, export_path)
            if os.path.exists(os.path.join(original_path, name + ".mtl")):  # pragma: no cover
                shutil.rmtree(os.path.join(original_path, name + ".mtl"), ignore_errors=True)
            obj_list[obj.name] = [
                os.path.join(os.path.basename(export_path), object_name),
                obj.color,
                obj.opacity,
                obj.units,
            ]
        return obj_list
