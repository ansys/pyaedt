# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 - 2025 ANSYS, Inc. and/or its affiliates.
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

import copy
import json
from pathlib import Path
import shutil

from ansys.aedt.core.generic.constants import unit_converter
from ansys.aedt.core.generic.errors import AEDTRuntimeError
from ansys.aedt.core.generic.file_utils import check_and_download_folder
from ansys.aedt.core.generic.general_methods import pyaedt_function_handler
from ansys.aedt.core.generic.settings import settings
from ansys.aedt.core.visualization.advanced.rcs_visualization import MonostaticRCSData

DEFAULT_EXPRESSION = "ComplexMonostaticRCSTheta"


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
    setup_name : str, optional
        Name of the setup. Make sure to build a setup string in the form of ``"SetupName : SetupSweep"``.
        The default is ``None``, in which case only the geometry is exported.
    frequencies : list, optional
        Frequency list to export. Specify either a list of strings with units or a list of floats in Hertz units.
        For example, ``["9GHz", 9e9]``. The default is ``None``, in which case only the geometry is exported.
    expression : str, optional
        Monostatic expression name. The default value is ``"ComplexMonostaticRCSTheta"``.
    variations : dict, optional
        Dictionary of all families including the primary sweep. The default value is ``None``.
    overwrite : bool, optional
        Whether to overwrite the existing far field solution data. The default is ``True``.

    Examples
    --------
    >>> import ansys.aedt.core
    >>> app = ansys.aedt.core.Hfss(version="2025.1", design="Antenna")
    >>> setup_name = "Setup1 : LastAdaptive"
    >>> frequencies = [77e9]
    >>> sphere = "3D"
    >>> data = app.get_monostatic_rcs(frequencies,setup_name,sphere)
    >>> data.plot_3d(quantity_format="dB10")
    """

    def __init__(
        self,
        app,
        setup_name=None,
        frequencies=None,
        expression=None,
        variations=None,
        overwrite=True,
    ):
        # Public
        self.setup_name = setup_name
        self.solution = ""
        self.expression = expression
        if not self.expression:
            self.expression = "ComplexMonostaticRCSTheta"

        if not variations:
            variations = app.available_variations.get_independent_nominal_values()
        else:
            # Set variation to Nominal
            for var_name, var_value in variations.items():
                if var_name in app.variable_manager.independent_variable_names:
                    app[var_name] = var_value

        self.variations = variations
        self.overwrite = overwrite

        if frequencies is not None and not isinstance(frequencies, list):
            self.frequencies = [frequencies]
        else:
            self.frequencies = frequencies
        self.data_file = None

        # Private
        self.__app = app
        self.__model_info = {}
        self.__rcs_data = None
        self.__metadata_file = ""
        self.__frequency_unit = self.__app.units.frequency

        self.__column_name = copy.deepcopy(self.expression)

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
        """Get RCS solution data.

        Returns
        -------
        :class:`ansys.aedt.core.modules.solutions.SolutionData`
            Solution Data object.
        """

        def compare_lists(list1, list2):
            if len(list1) != len(list2):
                return False

            for elem1, elem2 in zip(list1, list2):
                if elem1 != elem2:
                    return False

            return True

        variations = {i: k for i, k in self.variations.items()}
        variations["IWaveTheta"] = ["All"]
        variations["IWavePhi"] = ["All"]
        frequencies = self.frequencies[::]
        if frequencies is not None:
            frequencies = [str(freq) for freq in frequencies]
        variations["Freq"] = frequencies
        check_freq = [
            "9.250518854999999GHz",
            "9.258846423277779GHz",
            "9.267173991555561GHz",
            "9.27550155983333GHz",
            "9.28382912811111GHz",
            "9.29215669638889GHz",
            "9.30048426466667GHz",
            "9.308811832944439GHz",
            "9.317139401222221GHz",
            "9.325466969500001GHz",
            "9.333794537777781GHz",
            "9.342122106055561GHz",
            "9.35044967433333GHz",
            "9.358777242611112GHz",
            "9.36710481088889GHz",
            "9.37543237916667GHz",
            "9.383759947444441GHz",
            "9.392087515722221GHz",
            "9.400415084GHz",
            "9.40874265227778GHz",
            "9.41707022055555GHz",
            "9.42539778883333GHz",
            "9.433725357111109GHz",
            "9.442052925388889GHz",
            "9.450380493666669GHz",
            "9.45870806194444GHz",
            "9.46703563022222GHz",
            "9.4753631985GHz",
            "9.48369076677778GHz",
            "9.492018335055549GHz",
            "9.500345903333329GHz",
            "9.508673471611109GHz",
            "9.517001039888889GHz",
            "9.525328608166673GHz",
            "9.533656176444451GHz",
            "9.54198374472222GHz",
            "9.550311313GHz",
            "9.55863888127778GHz",
            "9.56696644955556GHz",
            "9.575294017833331GHz",
            "9.583621586111111GHz",
            "9.591949154388891GHz",
            "9.600276722666671GHz",
            "9.60860429094445GHz",
            "9.61693185922222GHz",
            "9.6252594275GHz",
            "9.633586995777778GHz",
            "9.641914564055559GHz",
            "9.650242132333331GHz",
            "9.65856970061111GHz",
            "9.66689726888889GHz",
            "9.67522483716667GHz",
            "9.68355240544444GHz",
            "9.691879973722219GHz",
            "9.700207541999999GHz",
            "9.708535110277779GHz",
            "9.716862678555559GHz",
            "9.72519024683333GHz",
            "9.73351781511111GHz",
            "9.74184538338889GHz",
            "9.75017295166667GHz",
            "9.758500519944439GHz",
            "9.766828088222219GHz",
            "9.775155656500001GHz",
            "9.783483224777781GHz",
            "9.791810793055561GHz",
            "9.80013836133333GHz",
            "9.80846592961111GHz",
            "9.81679349788889GHz",
            "9.82512106616667GHz",
            "9.833448634444441GHz",
            "9.841776202722221GHz",
            "9.850103771000001GHz",
            "9.85843133927778GHz",
            "9.86675890755556GHz",
            "9.87508647583333GHz",
            "9.88341404411111GHz",
            "9.891741612388889GHz",
            "9.900069180666669GHz",
            "9.90839674894444GHz",
            "9.916724317222219GHz",
            "9.9250518855GHz",
            "9.93337945377778GHz",
            "9.941707022055549GHz",
            "9.950034590333329GHz",
            "9.958362158611109GHz",
            "9.966689726888889GHz",
            "9.975017295166669GHz",
            "9.983344863444451GHz",
            "9.99167243172222GHz",
            "10GHz",
            "10.0083275682778GHz",
            "10.0166551365556GHz",
            "10.0249827048333GHz",
            "10.0333102731111GHz",
            "10.0416378413889GHz",
            "10.0499654096667GHz",
            "10.0582929779444GHz",
            "10.0666205462222GHz",
            "10.0749481145GHz",
            "10.0832756827778GHz",
            "10.0916032510556GHz",
            "10.0999308193333GHz",
            "10.1082583876111GHz",
            "10.1165859558889GHz",
            "10.1249135241667GHz",
            "10.1332410924444GHz",
            "10.1415686607222GHz",
            "10.149896229GHz",
            "10.1582237972778GHz",
            "10.1665513655556GHz",
            "10.1748789338333GHz",
            "10.1832065021111GHz",
            "10.1915340703889GHz",
            "10.1998616386667GHz",
            "10.2081892069444GHz",
            "10.2165167752222GHz",
            "10.2248443435GHz",
            "10.2331719117778GHz",
            "10.2414994800556GHz",
            "10.2498270483333GHz",
            "10.2581546166111GHz",
            "10.2664821848889GHz",
            "10.2748097531667GHz",
            "10.2831373214444GHz",
            "10.2914648897222GHz",
            "10.299792458GHz",
            "10.3081200262778GHz",
            "10.3164475945556GHz",
            "10.3247751628333GHz",
            "10.3331027311111GHz",
            "10.3414302993889GHz",
            "10.3497578676667GHz",
            "10.3580854359444GHz",
            "10.3664130042222GHz",
            "10.3747405725GHz",
            "10.3830681407778GHz",
            "10.3913957090556GHz",
            "10.3997232773333GHz",
            "10.4080508456111GHz",
            "10.4163784138889GHz",
            "10.4247059821667GHz",
            "10.4330335504444GHz",
            "10.4413611187222GHz",
            "10.449688687GHz",
            "10.4580162552778GHz",
            "10.4663438235556GHz",
            "10.4746713918333GHz",
            "10.4829989601111GHz",
            "10.4913265283889GHz",
            "10.4996540966667GHz",
            "10.5079816649444GHz",
            "10.5163092332222GHz",
            "10.5246368015GHz",
            "10.5329643697778GHz",
            "10.5412919380556GHz",
            "10.5496195063333GHz",
            "10.5579470746111GHz",
            "10.5662746428889GHz",
            "10.5746022111667GHz",
            "10.5829297794444GHz",
            "10.5912573477222GHz",
            "10.599584916GHz",
            "10.6079124842778GHz",
            "10.6162400525556GHz",
            "10.6245676208333GHz",
            "10.6328951891111GHz",
            "10.6412227573889GHz",
            "10.6495503256667GHz",
            "10.6578778939444GHz",
            "10.6662054622222GHz",
            "10.6745330305GHz",
            "10.6828605987778GHz",
            "10.6911881670556GHz",
            "10.6995157353333GHz",
            "10.7078433036111GHz",
            "10.7161708718889GHz",
            "10.7244984401667GHz",
            "10.7328260084444GHz",
            "10.7411535767222GHz",
            "10.749481145GHz",
        ]

        flag = compare_lists(frequencies, check_freq)
        self.__app.logger.info(flag)
        self.__app.logger.info(frequencies)

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
    def export_rcs(self, name="rcs_data", metadata_name="pyaedt_rcs_metadata", only_geometry=False):
        """Export RCS solution data.

        Parameters
        ----------
        name : str, optional
            Name of the RCS data file. The default is ``"rcs_data"``.
        metadata_name : str, optional
            Name of the metadata file. The default is ``"pyaedt_rcs_metadata"``.
        only_geometry : bool, optional
           Export only the geometry. The default is ``False``.

        Returns
        -------
        str
            Metadata file.

        """
        # Output directory
        if not self.setup_name:
            self.setup_name = "Nominal"
        solution_setup_name = self.setup_name.replace(":", "_").replace(" ", "")
        full_setup = f"{solution_setup_name}"
        export_path = Path(self.__app.working_directory) / full_setup
        local_path = Path(settings.remote_rpc_session_temp_folder) / full_setup
        export_path = Path(check_and_download_folder(str(local_path), str(export_path))).resolve()

        if not self.solution:
            self.solution = self.__app.design_name

        file_name = f"{name}_{self.solution}.h5"
        self.data_file = export_path / file_name
        pyaedt_metadata_file = export_path / f"{metadata_name}_{self.solution}.json"

        # Create directory or check if files already exist
        if settings.remote_rpc_session:
            settings.remote_rpc_session.filemanager.makedirs(export_path)
            file_exists = settings.remote_rpc_session.filemanager.pathexists(pyaedt_metadata_file)
        elif not export_path.exists():
            export_path.mkdir(parents=True, exist_ok=True)
            file_exists = False
        else:
            file_exists = pyaedt_metadata_file.exists()

        # Export monostatic RCS
        if self.overwrite or not file_exists:
            # Export geometry
            geometry_path = export_path / "geometry"

            if settings.remote_rpc_session:
                settings.remote_rpc_session.filemanager.makedirs(geometry_path)
            elif not geometry_path.exists():
                geometry_path.mkdir()

            obj_list = self.__create_geometries(geometry_path)
            if obj_list:
                self.__model_info["object_list"] = obj_list

            if only_geometry:
                file_name = None
            else:
                data = self.get_monostatic_rcs()
                if not data or data.number_of_variations != 1:  # pragma: no cover
                    raise AEDTRuntimeError("Data can not be obtained.")

                df = data.full_matrix_real_imag[0] + complex(0, 1) * data.full_matrix_real_imag[1]
                df.index.names = [*data.variations[0].keys(), *data.intrinsics.keys()]

                df = df.reset_index(level=[*data.variations[0].keys()], drop=True)
                df = unit_converter(
                    df, unit_system="Length", input_units=data.units_data[self.expression], output_units="meter"
                )
                df.rename(
                    columns={
                        self.expression: self.column_name,
                    },
                    inplace=True,
                )
                try:
                    df.to_hdf(self.data_file, key="df", mode="w", format="table")
                except ImportError as e:  # pragma: no cover
                    raise AEDTRuntimeError("PyTables is not installed") from e

                if not self.data_file.is_file():
                    raise AEDTRuntimeError("RCS data file not exported.")

        else:
            self.__app.logger.info("Using existing RCS file.")

        items = {
            "solution": self.solution,
            "monostatic_file": file_name,
            "model_units": self.__app.modeler.model_units,
            "frequency_units": self.__frequency_unit,
            "model_info": [],
        }

        if self.model_info and "object_list" in self.model_info:
            items["model_info"] = self.model_info["object_list"]

        try:
            with pyaedt_metadata_file.open("w") as f:
                json.dump(items, f, indent=2)
        except Exception as e:
            raise AEDTRuntimeError(f"An error occurred when writing metadata") from e

        self.__metadata_file = pyaedt_metadata_file
        if not only_geometry:
            self.__rcs_data = MonostaticRCSData(str(pyaedt_metadata_file))
        return pyaedt_metadata_file

    @pyaedt_function_handler()
    def __create_geometries(self, export_path):
        """Export the geometry in OBJ format."""
        self.__app.logger.info("Exporting geometry...")
        export_path = Path(export_path).resolve()
        model_pv = self.__app.post.get_model_plotter_geometries(plot_air_objects=False)
        obj_list = {}
        for obj in model_pv.objects:
            object_name = Path(obj.path).name
            name = Path(object_name).stem
            original_path = Path(obj.path).parent
            new_path = export_path / object_name

            if not new_path.exists():
                shutil.move(str(obj.path), str(export_path))
            else:
                new_path.unlink()
                shutil.move(str(obj.path), str(export_path))

            mtl_file = original_path / f"{name}.mtl"
            if mtl_file.exists():  # pragma: no cover
                mtl_file.unlink()

            obj_list[obj.name] = [
                object_name,
                obj.color,
                obj.opacity,
                obj.units,
            ]
        return obj_list
