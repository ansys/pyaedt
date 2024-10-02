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

from ansys.aedt.core.generic.constants import unit_converter
from ansys.aedt.core.generic.general_methods import check_and_download_folder
from ansys.aedt.core.generic.general_methods import open_file
from ansys.aedt.core.generic.general_methods import pyaedt_function_handler
from ansys.aedt.core.generic.settings import settings
from ansys.aedt.core.visualization.advanced.rcs_visualization import MonostaticRCSData


class MonostaticRCSExporter:
    """Class to enable export of radar cross-section (RCS) data from HFSS.

    An instance of this class is returned from the
    :meth:`pyaedt.Hfss.get_monostatic_rcs` method. This class creates a
    ``metadata_file`` that can be passed as argument to instantiate an instance of the
    :class:`pyaedt.generic.rcs_visualization.MonostaticRCSData` class for subsequent analysis and postprocessing.

    Note that this class is derived from the :class:`MonostaticRCSData` class and can be used directly for
    RCS postprocessing, but it remains as a property of the :class:`pyaedt.Hfss` application.

    Parameters
    ----------
    app : :class:`pyaedt.Hfss`
        HFSS application instance.
    setup_name : str
        Name of the setup. Make sure to build a setup string in the form of ``"SetupName : SetupSweep"``.
    frequencies : list
        Frequency list to export. Specify either a list of strings with units or a list of floats in Hertz units.
        For example, ``["9GHz", 9e9]``.
    expression : str, optional
        Monostatic expression name. The default value is ``"ComplexMonostaticRCSTheta"``.
    variations : dict, optional
        Dictionary of all families including the primary sweep. The default value is ``None``.
    overwrite : bool, optional
        Whether to overwrite the existing far field solution data. The default is ``True``.

    Examples
    --------
    >>> import ansys.aedt.core
    >>> app = ansys.aedt.core.Hfss(version="2023.2", design="Antenna")
    >>> setup_name = "Setup1 : LastAdaptive"
    >>> frequencies = [77e9]
    >>> sphere = "3D"
    >>> data = app.get_monostatic_rcs(frequencies,setup_name,sphere)
    >>> data.plot_3d(quantity_format="dB10")
    """

    def __init__(
        self,
        app,
        setup_name,
        frequencies,
        expression=None,
        variations=None,
        overwrite=True,
    ):
        # Public
        self.setup_name = setup_name
        self.variation_name = ""
        self.export_format = "pkl"
        self.expression = expression
        if not self.expression:
            self.expression = "ComplexMonostaticRCSTheta"

        if not variations:
            variations = app.available_variations.nominal_w_values_dict_w_dependent
        else:
            # Set variation to Nominal
            for var_name, var_value in variations.items():
                app[var_name] = var_value

        self.variations = variations
        self.overwrite = overwrite

        if not isinstance(frequencies, list):
            self.frequencies = [frequencies]
        else:
            self.frequencies = frequencies

        # Private
        self.__app = app
        self.__model_info = {}
        self.__rcs_data = None
        self.__metadata_file = ""
        self.__frequency_unit = self.__app.odesktop.GetDefaultUnit("Frequency")

        self.__column_name = self.expression
        self.__phi_column_name = "ComplexMonostaticRCSPhi"

    @property
    def model_info(self):
        """List of models."""
        return self.__model_info

    @property
    def rcs_data(self):
        """Monostatic RCS data."""
        return self.__rcs_data

    @property
    def metadata_file(self):
        """Metadata file."""
        return self.__metadata_file

    @property
    def column_name(self):
        """Column name."""
        return self.__column_name

    @column_name.setter
    def column_name(self, value):
        """Column name."""
        self.__column_name = value

    @pyaedt_function_handler()
    def get_monostatic_rcs(self):
        """Get RCS solution data."""

        variations = self.variations
        variations["IWaveTheta"] = ["All"]
        variations["IWavePhi"] = ["All"]
        variations["Freq"] = self.frequencies

        solution_data = self.__app.post.get_solution_data(
            expressions=self.expression,
            variations=variations,
            setup_sweep_name=self.setup_name,
            report_category="Monostatic RCS",
        )

        self.__frequency_unit = solution_data.units_sweeps["Freq"]
        solution_data.enable_pandas_output = True
        return solution_data

    @pyaedt_function_handler()
    def export_rcs(self, name="monostatic_data", metadata_name="pyaedt_rcs_metadata", output_format="pkl"):
        """Export RCS solution data."""

        # Output directory
        solution_setup_name = self.setup_name.replace(":", "_").replace(" ", "")
        full_setup = "{}".format(solution_setup_name)
        export_path = "{}/{}/".format(self.__app.working_directory, full_setup)
        local_path = "{}/{}/".format(settings.remote_rpc_session_temp_folder, full_setup)
        export_path = os.path.abspath(check_and_download_folder(local_path, export_path))

        # Variation name
        var = []
        if self.variations:
            for k, v in self.variations.items():
                var.append("{}='{}'".format(k, v))
            variation = " ".join(var)
        else:
            variation = self.__app.odesign.GetNominalVariation()

        if not self.variation_name:
            self.variation_name = variation

        file_name = f"{name}.{output_format}"
        full_path = os.path.join(export_path, file_name)
        pyaedt_metadata_file = os.path.join(export_path, f"{metadata_name}_{self.variation_name}.json")

        # Create directory or check if files already exist
        if settings.remote_rpc_session:  # pragma: no cover
            settings.remote_rpc_session.filemanager.makedirs(export_path)
            file_exists = settings.remote_rpc_session.filemanager.pathexists(pyaedt_metadata_file)
        elif not os.path.exists(export_path):
            os.makedirs(export_path)
            file_exists = False
        else:
            file_exists = os.path.exists(pyaedt_metadata_file)

        # Export monostatic RCS
        if self.overwrite or not file_exists:

            data = self.get_monostatic_rcs()

            if not data or data.number_of_variations != 1:  # pragma: no cover
                self.__app.logger.error("Data can not be obtained.")
                return False

            df = data.full_matrix_real_imag[0] + complex(0, 1) * data.full_matrix_real_imag[1]
            df.index.names = [*data.variations[0].keys(), *data.intrinsics.keys()]
            df = df.reset_index(level=[*data.variations[0].keys()], drop=True)
            df = unit_converter(
                df, unit_system="Length", input_units=data.units_data[self.expression], output_units="meter"
            )

            df.rename(
                columns={
                    self.expression: self.column_name,
                }
            )

            if output_format == "h5":
                try:
                    df.to_hdf(full_path, key="df", mode="w", format="table")
                except ImportError as e:  # pragma: no cover
                    self.__app.logger.error(f"PyTables is not installed: {e}")
                    return False
            else:
                df.to_pickle(full_path)

            if not os.path.isfile(full_path):  # pragma: no cover
                self.__app.logger.error("RCS data file not exported.")
                return False
        else:
            self.__app.logger.info("Using existing RCS file.")

        # Export geometry
        if os.path.isfile(full_path):
            geometry_path = os.path.join(export_path, "geometry")
            if not os.path.exists(geometry_path):
                os.mkdir(geometry_path)
            obj_list = self.__create_geometries(geometry_path)
            if obj_list:
                self.__model_info["object_list"] = obj_list

        items = {
            "variation": self.variation_name,
            "monostatic_file": file_name,
            "model_units": self.__app.modeler.model_units,
            "frequency_units": self.__frequency_unit,
            "model_info": [],
        }

        if self.model_info and "object_list" in self.model_info:
            items["model_info"] = self.model_info["object_list"]

        with open_file(pyaedt_metadata_file, "w") as f:
            json.dump(items, f, indent=2)
        if not pyaedt_metadata_file:  # pragma: no cover
            return False

        self.__metadata_file = pyaedt_metadata_file
        self.__rcs_data = MonostaticRCSData(pyaedt_metadata_file)
        return pyaedt_metadata_file

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
                os.remove(os.path.join(original_path, name + ".mtl"))
            obj_list[obj.name] = [
                os.path.join(os.path.basename(export_path), object_name),
                obj.color,
                obj.opacity,
                obj.units,
            ]
        return obj_list

    @staticmethod
    @pyaedt_function_handler()
    def __find_nearest(array, value):
        idx = np.searchsorted(array, value, side="left")
        if idx > 0 and (idx == len(array) or math.fabs(value - array[idx - 1]) < math.fabs(value - array[idx])):
            return idx - 1
        else:
            return idx
