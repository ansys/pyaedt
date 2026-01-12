# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 - 2026 ANSYS, Inc. and/or its affiliates.
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

from pathlib import Path
import uuid

import pytest

import ansys.aedt.core
from ansys.aedt.core import Quantity
from ansys.aedt.core.generic.constants import LineStyle
from ansys.aedt.core.generic.constants import SymbolStyle
from ansys.aedt.core.generic.constants import TraceType
from ansys.aedt.core.generic.file_utils import read_json
from ansys.aedt.core.internal.errors import AEDTRuntimeError
from ansys.aedt.core.visualization.plot.pyvista import ModelPlotter
from ansys.aedt.core.visualization.plot.pyvista import _parse_aedtplt
from tests import TESTS_VISUALIZATION_PATH
from tests.conftest import NON_GRAPHICAL

TEST_PROJECT_NAME = "coax_setup_solved_231"
M2D_TRACE_EXPORT_TABLE = "m2d"

TEST_SUBFOLDER = "T12"


@pytest.fixture
def aedt_app(add_app_example):
    app = add_app_example(project=TEST_PROJECT_NAME, subfolder=TEST_SUBFOLDER)
    yield app
    app.close_project(app.project_name, save=False)


@pytest.fixture
def m2d_app(add_app_example):
    app = add_app_example(
        project=M2D_TRACE_EXPORT_TABLE, subfolder=TEST_SUBFOLDER, application=ansys.aedt.core.Maxwell2d
    )
    yield app
    app.close_project(app.project_name, save=False)


@pytest.fixture
def m2d_blank(add_app):
    app = add_app(application=ansys.aedt.core.Maxwell2d)
    yield app
    app.close_project(app.project_name, save=False)


def test_export_model_picture(aedt_app, test_tmp_dir):
    path = aedt_app.post.export_model_picture(full_name=test_tmp_dir / "images2.jpg")
    assert path
    path = aedt_app.post.export_model_picture(
        full_name=test_tmp_dir / "images3.jpg",
        show_axis=True,
        show_grid=False,
        show_ruler=True,
    )
    assert Path(path).is_file()
    path = aedt_app.post.export_model_picture(full_name=test_tmp_dir / "images4.jpg")
    assert path


def test_create_fieldplot_cutplane(aedt_app):
    cutlist = ["Global:XY", "Global:XZ", "Global:YZ"]
    setup_name = aedt_app.existing_analysis_sweeps[0]
    assert aedt_app.setups[0].is_solved
    quantity_name = "ComplexMag_E"
    frequency = Quantity("5GHz")
    phase = Quantity("180deg")
    intrinsic = {"Freq": frequency, "Phase": phase}
    aedt_app.post.get_scalar_field_value(quantity_name, "Minimum", setup_name, intrinsics="5GHz")
    plot1 = aedt_app.post.create_fieldplot_cutplane(cutlist, quantity_name, setup_name, intrinsic)
    plot1.IsoVal = "Tone"
    plot1.update_field_plot_settings()
    plot1.update()
    assert aedt_app.post.field_plots[plot1.name].IsoVal == "Tone"


def test_create_fieldplot_cutplane_1(aedt_app):
    cutlist = ["Global:XY", "Global:XZ", "Global:YZ"]
    setup_name = aedt_app.existing_analysis_sweeps[0]
    quantity_name = "ComplexMag_E"
    frequency = Quantity("5GHz")
    phase = Quantity("180deg")
    intrinsic = {"Freq": frequency, "Phase": phase}
    assert aedt_app.post.create_fieldplot_cutplane(cutlist, quantity_name, setup_name, intrinsic, "Plot_1")


def test_change_plot_scale(aedt_app):
    cutlist = ["Global:XY", "Global:XZ", "Global:YZ"]
    setup_name = aedt_app.existing_analysis_sweeps[0]
    quantity_name = "ComplexMag_E"
    frequency = Quantity("5GHz")
    phase = Quantity("180deg")
    intrinsic = {"Freq": frequency, "Phase": phase}
    min_value = aedt_app.post.get_scalar_field_value(quantity_name, "Minimum", setup_name, intrinsics="5GHz")
    plot1 = aedt_app.post.create_fieldplot_cutplane(cutlist, quantity_name, setup_name, intrinsic)
    plot1.IsoVal = "Tone"
    plot1.update_field_plot_settings()
    plot1.update()
    aedt_app.save_project()
    plot1.folder_settings.scale_settings.scale_type = "MinMax"
    plot1.folder_settings.update()
    plot1.folder_settings.scale_settings.scale_settings.max_value = 30000
    plot1.folder_settings.scale_settings.scale_settings.min_value = min_value
    plot1.folder_settings.scale_settings.scale_settings.n_levels = 50
    plot1.folder_settings.update()


def test_create_fieldplot_volume_invalid(aedt_app):
    frequency = Quantity("5GHz")
    phase = Quantity("180deg")
    setup_name = aedt_app.existing_analysis_sweeps[0]
    intrinsic = {"Freq": frequency, "Phase": phase}
    assert not aedt_app.post.create_fieldplot_volume("invalid", "Vector_E", setup_name, intrinsic)


def test_create_fieldplot_volume(aedt_app):
    quantity_name = "ComplexMag_E"
    frequency = Quantity("5GHz")
    phase = Quantity("180deg")
    setup_name = aedt_app.existing_analysis_sweeps[0]
    intrinsic = {"Freq": frequency, "Phase": phase}
    field_plot = aedt_app.post.create_fieldplot_volume("inner", quantity_name, setup_name, intrinsic)
    assert field_plot


def test_create_fieldplot_volume_1(aedt_app):
    quantity_name = "ComplexMag_E"
    frequency = Quantity("5GHz")
    phase = Quantity("180deg")
    setup_name = aedt_app.existing_analysis_sweeps[0]
    intrinsic = {"Freq": frequency, "Phase": phase}
    assert aedt_app.post.create_fieldplot_volume("inner", quantity_name, setup_name, intrinsic, "Plot_1")


def test_export_field_plot(aedt_app):
    frequency = Quantity("5GHz")
    phase = Quantity("180deg")
    setup_name = aedt_app.existing_analysis_sweeps[0]
    intrinsic = {"Freq": frequency, "Phase": phase}
    volume_plot = aedt_app.post.create_fieldplot_volume("NewObject_IJD39Q", "Vector_E", setup_name, intrinsic)
    export_status = aedt_app.post.export_field_plot(
        plot_name=volume_plot.name, output_dir=aedt_app.working_directory, file_format="case"
    )
    assert export_status
    assert Path(export_status).suffix == ".case"


def test_create_fieldplot_surface(aedt_app):
    frequency = Quantity("5GHz")
    phase = Quantity("180deg")
    setup_name = aedt_app.existing_analysis_sweeps[0]
    intrinsic = {"Freq": frequency, "Phase": phase}
    field_plot = aedt_app.post.create_fieldplot_surface(
        aedt_app.modeler["outer"].faces[0].id, "Mag_E", setup_name, intrinsic
    )
    assert field_plot


def test_create_fieldplot_surface_1(aedt_app):
    frequency = Quantity("5GHz")
    phase = Quantity("180deg")
    setup_name = aedt_app.existing_analysis_sweeps[0]
    intrinsic = {"Freq": frequency, "Phase": phase}
    assert aedt_app.post.create_fieldplot_surface(
        aedt_app.modeler["outer"].faces[0].id, "Mag_E", setup_name, intrinsic, "Plot_1"
    )


def test_create_fieldplot_surface_2(aedt_app):
    frequency = Quantity("5GHz")
    phase = Quantity("180deg")
    setup_name = aedt_app.existing_analysis_sweeps[0]
    intrinsic = {"Freq": frequency, "Phase": phase}
    assert aedt_app.post.create_fieldplot_surface(aedt_app.modeler["outer"], "Mag_E", setup_name, intrinsic)


def test_create_fieldplot_surface_3(aedt_app):
    frequency = Quantity("5GHz")
    phase = Quantity("180deg")
    setup_name = aedt_app.existing_analysis_sweeps[0]
    intrinsic = {"Freq": frequency, "Phase": phase}
    assert aedt_app.post.create_fieldplot_surface(aedt_app.modeler["outer"].faces, "Mag_E", setup_name, intrinsic)


def test_create_fieldplot_surface_4(aedt_app):
    frequency = Quantity("5GHz")
    phase = Quantity("180deg")
    setup_name = aedt_app.existing_analysis_sweeps[0]
    intrinsic = {"Freq": frequency, "Phase": phase}
    assert not aedt_app.post.create_fieldplot_surface(123123123, "Mag_E", setup_name, intrinsic)


def test_design_setups(aedt_app):
    assert len(aedt_app.design_setups["Setup1"].sweeps[0].frequencies) > 0
    assert isinstance(aedt_app.design_setups["Setup1"].sweeps[0].basis_frequencies, list)


def test_export_mesh_obj(aedt_app):
    frequency = Quantity("5GHz")
    phase = Quantity("180deg")
    setup_name = aedt_app.existing_analysis_sweeps[0]
    intrinsic = {"Freq": frequency, "Phase": phase}
    mesh_file_path = aedt_app.post.export_mesh_obj(setup_name, intrinsic)
    assert Path(mesh_file_path).is_file()
    mesh_file_path2 = aedt_app.post.export_mesh_obj(setup_name, intrinsic, export_air_objects=False, on_surfaces=False)
    assert Path(mesh_file_path2).is_file()


def test_get_scalar_field_value(aedt_app):
    setup_name = aedt_app.existing_analysis_sweeps[0]
    min_value = aedt_app.post.get_scalar_field_value("E", "Minimum", setup_name, intrinsics="5GHz", is_vector=True)
    assert isinstance(min_value, float)


@pytest.mark.avoid_ansys_load
def test_plot_animated_field(aedt_app, test_tmp_dir):
    cutlist = ["Global:XY"]
    phases = [str(i * 5) + "deg" for i in range(2)]
    model_gif = aedt_app.post.plot_animated_field(
        quantity="Mag_E",
        assignment=cutlist,
        plot_type="CutPlane",
        setup=aedt_app.nominal_adaptive,
        intrinsics={"Freq": "5GHz", "Phase": "0deg"},
        variation_variable="Phase",
        variations=phases,
        show=False,
        export_gif=True,
        export_path=test_tmp_dir,
    )
    assert Path(model_gif.gif_file).is_file()


@pytest.mark.avoid_ansys_load
def test_animate_fields_from_aedtplt(aedt_app):
    setup_name = aedt_app.existing_analysis_sweeps[0]
    intrinsic = {"Freq": "5GHz", "Phase": "180deg"}
    phases = [str(i * 5) + "deg" for i in range(2)]
    pl1 = aedt_app.post.create_fieldplot_volume("NewObject_IJD39Q", "Mag_E", setup_name, intrinsic)
    model_gif2 = aedt_app.post.animate_fields_from_aedtplt(
        plot_name=pl1.name,
        plot_folder=None,
        variation_variable="Phase",
        variations=phases,
        project_path="",
        export_gif=False,
        show=False,
    )
    model_gif2.gif_file = Path(aedt_app.working_directory) / "test2.gif"
    model_gif2.camera_position = [0, 50, 200]
    model_gif2.focal_point = [0, 50, 0]
    model_gif2.animate(show=False)
    assert model_gif2.gif_file.is_file()


@pytest.mark.skipif(NON_GRAPHICAL, reason="Not running in non-graphical mode")
def test_create_fieldplot_volume_2(aedt_app, test_tmp_dir):
    quantity_name2 = "ComplexMag_H"
    setup_name = "Setup1 : LastAdaptive"
    intrinsic = {"Freq": "5GHz", "Phase": "180deg"}
    vollist = ["NewObject_IJD39Q"]
    plot2 = aedt_app.post.create_fieldplot_volume(vollist, quantity_name2, setup_name, intrinsic)
    file_path = Path(test_tmp_dir, "test_x.jpg")
    exported_file = plot2.export_image(str(file_path))
    assert Path(exported_file).is_file()


@pytest.mark.skipif(NON_GRAPHICAL, reason="Not running in non-graphical mode")
def test_export_field_jpg(aedt_app, test_tmp_dir):
    quantity_name2 = "ComplexMag_H"
    setup_name = "Setup1 : LastAdaptive"
    intrinsic = {"Freq": "5GHz", "Phase": "180deg"}
    vollist = ["NewObject_IJD39Q"]
    plot2 = aedt_app.post.create_fieldplot_volume(vollist, quantity_name2, setup_name, intrinsic)
    exported_file = test_tmp_dir / "prova2.jpg"
    aedt_app.post.export_field_jpg(exported_file, plot2.name, plot2.plot_folder)
    assert exported_file.is_file()


def test_create_scattering(aedt_app):
    portnames = ["1", "2"]
    assert aedt_app.create_scattering("MyTestScattering")
    setup_name = "Setup2 : Sweep"
    with pytest.raises(KeyError):
        aedt_app.create_scattering("MyTestScattering2", setup_name, portnames, portnames)


def test_get_solution_data(aedt_app):
    trace_names = []
    portnames = ["1", "2"]
    for el in portnames:
        for el2 in portnames:
            trace_names.append("S(" + el + "," + el2 + ")")
    families = {"Freq": ["All"]}
    nominal_values = aedt_app.available_variations.get_independent_nominal_values()
    for key, value in nominal_values.items():
        families[key] = value

    my_data = aedt_app.post.get_solution_data(expressions=trace_names, variations=families)
    assert my_data
    assert my_data.expressions
    assert len(my_data.get_expression_data(trace_names[0], formula="db10")[1]) > 0
    assert len(my_data.get_expression_data(trace_names[0], formula="imag")[1]) > 0
    assert len(my_data.get_expression_data(trace_names[0])[1]) > 0
    assert len(my_data.get_expression_data(trace_names[0], formula="magnitude")[1]) > 0


def test_export_data_to_csv(aedt_app, test_tmp_dir):
    trace_names = []
    portnames = ["1", "2"]
    for el in portnames:
        for el2 in portnames:
            trace_names.append("S(" + el + "," + el2 + ")")
    families = {"Freq": ["All"]}
    nominal_values = aedt_app.available_variations.get_independent_nominal_values()
    for key, value in nominal_values.items():
        families[key] = value
    my_data = aedt_app.post.get_solution_data(expressions=trace_names, variations=families)
    output_csv = test_tmp_dir / "output.csv"
    assert my_data.export_data_to_csv(str(output_csv))
    assert output_csv.is_file()


def test_get_touchstone_data(aedt_app):
    assert aedt_app.get_touchstone_data("Setup1")


def test_export_touchstone(aedt_app, test_tmp_dir):
    setup_name = "Setup1"
    sweep_name = "Sweep"
    output_file = test_tmp_dir / "Setup1_Sweep.S2p"
    aedt_app.export_touchstone(setup_name, sweep_name, str(output_file))
    assert output_file.is_file()


def test_export_touchstone_1(aedt_app, test_tmp_dir):
    setup_name = "Setup1"
    sweep_name = None
    output_file = test_tmp_dir / "Setup1_Sweep2.S2p"
    aedt_app.export_touchstone(setup_name, sweep_name, str(output_file))
    assert output_file.is_file()


def test_export_touchstone_2(aedt_app, test_tmp_dir):
    setup_name = None
    sweep_name = None
    output_file = test_tmp_dir / "Setup1_Sweep3.S2p"
    aedt_app.export_touchstone(setup_name, sweep_name, str(output_file))
    assert output_file.is_file()


def test_export_touchstone_3(aedt_app):
    setup_name = None
    sweep_name = None
    assert aedt_app.export_touchstone(setup_name, sweep_name)


def test_export_report_to_jpg(aedt_app, test_tmp_dir):
    aedt_app.create_scattering("MyTestScattering")
    aedt_app.post.export_report_to_jpg(test_tmp_dir, "MyTestScattering")
    output_file = test_tmp_dir / "MyTestScattering.jpg"
    assert output_file.is_file()


def test_export_report_to_csv(aedt_app, test_tmp_dir):
    aedt_app.create_scattering("MyTestScattering")
    aedt_app.post.export_report_to_csv(
        test_tmp_dir,
        "MyTestScattering",
        start="3GHz",
        end="6GHz",
        step="0.12GHz",
        uniform=True,
        use_trace_number_format=False,
    )
    output_file = test_tmp_dir / "MyTestScattering.csv"
    assert output_file.is_file()


def test_export_report_to_rdat(aedt_app, test_tmp_dir):
    aedt_app.create_scattering("MyTestScattering")
    output_file = test_tmp_dir / "MyTestScattering.rdat"
    aedt_app.post.export_report_to_file(test_tmp_dir, "MyTestScattering", ".rdat")
    assert output_file.is_file()


def test_export_field_file_on_grid(aedt_app, test_tmp_dir):
    file_path = aedt_app.post.export_field_file_on_grid(
        "E",
        "Setup1 : LastAdaptive",
        aedt_app.available_variations.nominal_values,
        test_tmp_dir,
        grid_stop=[5, 5, 5],
        grid_step=[0.5, 0.5, 0.5],
        is_vector=True,
        intrinsics="5GHz",
    )
    assert Path(file_path).is_file()


def test_export_field_file_on_grid_1(aedt_app, test_tmp_dir):
    output_file = test_tmp_dir / "Efield.fld"
    aedt_app.post.export_field_file_on_grid(
        "E",
        "Setup1 : LastAdaptive",
        aedt_app.available_variations.nominal_values,
        str(output_file),
        grid_stop=[5, 5, 5],
        grid_step=[0.5, 0.5, 0.5],
        is_vector=True,
        intrinsics="5GHz",
    )
    assert output_file.is_file()


def test_export_field_file_on_grid_spherical(aedt_app, test_tmp_dir):
    output_file = test_tmp_dir / "MagEfieldSph.fld"
    aedt_app.post.export_field_file_on_grid(
        "Mag_E",
        "Setup1 : LastAdaptive",
        aedt_app.available_variations.nominal_values,
        str(output_file),
        grid_type="Spherical",
        grid_stop=[5, 300, 300],
        grid_step=[5, 50, 50],
        is_vector=False,
        intrinsics="5GHz",
    )
    assert output_file.is_file()


def test_export_field_file_on_grid_cylindrical(aedt_app, test_tmp_dir):
    output_file = test_tmp_dir / "MagEfieldCyl.fld"
    aedt_app.post.export_field_file_on_grid(
        "Mag_E",
        "Setup1 : LastAdaptive",
        aedt_app.available_variations.nominal_values,
        str(output_file),
        grid_type="Cylindrical",
        grid_stop=[5, 300, 5],
        grid_step=[5, 50, 5],
        is_vector=False,
        intrinsics="5GHz",
    )
    assert output_file.is_file()


def test_ModelPlotter_plot(aedt_app, test_tmp_dir):
    file_path = aedt_app.post.export_field_file_on_grid(
        "E",
        "Setup1 : LastAdaptive",
        aedt_app.available_variations.nominal_values,
        test_tmp_dir,
        grid_stop=[5, 5, 5],
        grid_step=[0.5, 0.5, 0.5],
        is_vector=True,
        intrinsics="5GHz",
    )
    model_pv = ModelPlotter()
    model_pv.add_field_from_file(file_path)
    assert model_pv.plot(show=False)


def test_ModelPlotter_clean_cache_and_files(aedt_app, test_tmp_dir):
    file_path = aedt_app.post.export_field_file_on_grid(
        "E",
        "Setup1 : LastAdaptive",
        aedt_app.available_variations.nominal_values,
        test_tmp_dir,
        grid_stop=[5, 5, 5],
        grid_step=[0.5, 0.5, 0.5],
        is_vector=True,
        intrinsics="5GHz",
    )
    model_pv = ModelPlotter()
    model_pv.add_field_from_file(file_path)
    model_pv.plot(show=False)
    assert model_pv.clean_cache_and_files(clean_cache=True)


def test_copydata(aedt_app, test_tmp_dir):
    aedt_app.create_scattering("MyTestScattering")
    assert aedt_app.post.copy_report_data("MyTestScattering")


def test_rename_report(aedt_app):
    aedt_app.create_scattering("MyTestScattering")
    assert aedt_app.post.rename_report("MyTestScattering", "MyNewScattering")


def test_rename_report_1(aedt_app):
    aedt_app.create_scattering("MyTestScattering")
    assert [plot for plot in aedt_app.post.plots if plot.plot_name == "MyTestScattering"]
    assert not aedt_app.post.rename_report("invalid", "MyTestScattering")


def test_create_report(aedt_app, test_tmp_dir):
    plot = aedt_app.post.create_report("dB(S(1,1))")
    assert plot
    plot_tdr = aedt_app.post.create_report(
        expressions="TDRZ(1,1)",
        report_category="TDR Impedance",
        domain="Time",
        primary_sweep_variable="Time",
        plot_name="batch_1_TDR",
        variations={"Time": ["All"]},
    )
    assert not plot_tdr.use_pulse_in_tdr
    assert plot_tdr.maximum_time == 3.33333333333333e-10
    assert plot_tdr.pulse_rise_time == 1.66666666666667e-11
    assert plot_tdr.time_windowing == 4


def test_create_report_from_configuration(aedt_app, test_tmp_dir):
    plot = aedt_app.post.create_report("dB(S(1,1))")
    assert plot
    output_file = test_tmp_dir / f"{plot.plot_name}.json"
    assert plot.export_config(str(output_file))
    output_file = test_tmp_dir / f"{plot.plot_name}.json"
    assert aedt_app.post.create_report_from_configuration(str(output_file), solution_name=aedt_app.nominal_sweep)


def test_create_report_from_configuration_1(aedt_app, test_tmp_dir):
    plot = aedt_app.post.create_report("dB(S(1,1))")
    assert plot
    output_file = test_tmp_dir / f"{plot.plot_name}.json"
    assert plot.export_config(str(output_file))
    assert aedt_app.post.create_report_from_configuration(
        str(output_file),
        solution_name=aedt_app.nominal_sweep,
        matplotlib=True,
        show=False,
    )


def test_create_report_from_configuration_2(aedt_app):
    assert aedt_app.post.create_report(
        expressions="MaxMagDeltaS",
        variations={"Pass": ["All"]},
        primary_sweep_variable="Pass",
        report_category="Modal Solution Data",
        plot_type="Rectangular Plot",
    )


def test_get_solution_data_2(aedt_app):
    aedt_app.post.create_report("dB(S(1,1))")
    data = aedt_app.post.get_solution_data("S(1,1)")
    assert data.primary_sweep == "Freq"
    assert data.expressions[0] == "S(1,1)"
    assert len(aedt_app.post.all_report_names) > 0


def test_eports_by_category_modal_solution(aedt_app):
    new_report = aedt_app.post.reports_by_category.modal_solution("dB(S(1,1))", setup=aedt_app.nominal_sweep)
    assert new_report.create()


def test_import_traces(aedt_app, test_tmp_dir):
    new_report = aedt_app.create_scattering("import_test")
    csv_file_path = aedt_app.post.export_report_to_csv(test_tmp_dir, "import_test")
    rdat_file_path = aedt_app.post.export_report_to_file(test_tmp_dir, "import_test", ".rdat")
    plot_name = new_report.plot_name

    trace_names = []
    trace_names.append(new_report.expressions[0])
    families = {"Freq": ["All"]}

    for key, value in aedt_app.available_variations.nominal_values.items():
        families[key] = value

    # get solution data and save in .csv file
    my_data = aedt_app.post.get_solution_data(expressions=trace_names, variations=families)
    output_csv = test_tmp_dir / "output.csv"
    my_data.export_data_to_csv(str(output_csv))
    assert not new_report.import_traces(str(output_csv), plot_name)

    # test import with correct inputs from csv
    assert new_report.import_traces(csv_file_path, plot_name)

    assert len(new_report.traces) == 4

    # test import with correct inputs from rdat
    assert new_report.import_traces(rdat_file_path, plot_name)
    # test import with not existing plot_name
    with pytest.raises(ValueError):
        new_report.import_traces(csv_file_path, "plot_name")
    # test import with random file path
    with pytest.raises(FileExistsError):
        new_report.import_traces(str(uuid.uuid4()), plot_name)
    # test import without plot_name
    with pytest.raises(ValueError):
        new_report.import_traces(csv_file_path, None)


def test_delete_traces(aedt_app, test_tmp_dir):
    new_report = aedt_app.create_scattering("delete_traces_test")
    traces_to_delete = [new_report.expressions[0]]
    plot_name = new_report.plot_name
    assert new_report.delete_traces(plot_name, traces_to_delete)
    with pytest.raises(ValueError):
        new_report.delete_traces("plot_name", traces_to_delete)
    with pytest.raises(ValueError):
        new_report.delete_traces(plot_name, ["V(out)_Test"])


def test_add_traces_to_report(aedt_app):
    new_report = aedt_app.create_scattering("add_traces_test")
    traces = new_report.get_solution_data().expressions
    assert new_report.add_trace_to_report(traces)
    setup = aedt_app.post.plots[0].setup
    variations = aedt_app.post.plots[0].variations["height"] = "10mm"
    assert not new_report.add_trace_to_report(traces, setup, variations)
    variations = aedt_app.post.plots[0].variations
    assert new_report.add_trace_to_report(traces, setup, variations)
    setup = "Transient"
    assert not new_report.add_trace_to_report(traces, setup, variations)


def test_update_trace_name(aedt_app):
    report = aedt_app.create_scattering("add_traces_test_2")
    old_trace_name = report.traces[0].name
    assert old_trace_name in report.traces[0].aedt_name
    new_name = "update_trace_name_test"
    report.traces[0].name = new_name
    assert new_name in report.traces[0].aedt_name


def test_update_traces_in_report(aedt_app):
    new_report = aedt_app.create_scattering("update_traces_test")
    traces = new_report.get_solution_data().expressions
    assert new_report.update_trace_in_report(traces)
    setup = aedt_app.post.plots[0].setup
    variations = aedt_app.post.plots[0].variations["height"] = "10mm"
    assert not new_report.add_trace_to_report(traces, setup, variations)
    variations = aedt_app.post.plots[0].variations
    assert new_report.update_trace_in_report(traces, setup, variations)


def test_create_monitor(aedt_app):  # pragma: no cover
    aedt_app.post.create_report("dB(S(1,1))")
    new_report = aedt_app.post.reports_by_category.modal_solution("dB(S(1,1))")
    new_report.create()
    assert new_report.add_cartesian_x_marker("3GHz")
    assert new_report.add_cartesian_y_marker("-55")


def test_add_line_from_point(aedt_app):  # pragma: no cover
    new_report = aedt_app.post.reports_by_category.modal_solution("dB(S(1,1))")
    new_report.create()
    assert new_report.add_limit_line_from_points([3, 5, 5, 3], [-50, -50, -60, -60], "GHz")


def test_add_line_from_equation(aedt_app):
    new_report = aedt_app.post.reports_by_category.modal_solution("dB(S(1,1))")
    new_report.create()
    assert new_report.add_limit_line_from_equation(start_x=1, stop_x=20, step=0.5, units="GHz")


def test_edit_grid(aedt_app):
    report = aedt_app.post.create_report("dB(S(1,1))")
    assert report.edit_grid()
    assert report.edit_grid(minor_x=False)
    assert report.edit_grid(major_y=False)
    assert report.edit_grid(major_color=(0, 0, 125))
    assert report.edit_grid(major_color=(0, 255, 0))
    assert report.edit_grid(style_major="Dot")


def test_edit_x_axis(aedt_app):
    report = aedt_app.post.create_report("dB(S(1,1))")
    assert report.edit_x_axis(
        font="Bangers", font_size=14, italic=True, bold=False, color=(0, 128, 0), display_units=False
    )


def test_edit_y_axis(aedt_app):
    report = aedt_app.post.create_report("dB(S(1,1))")
    assert report.edit_y_axis(
        font="Bangers", font_size=14, italic=True, bold=False, color=(0, 128, 0), display_units=False
    )


def test_edit_x_axis_label(aedt_app):
    report = aedt_app.post.create_report("dB(S(1,1))")
    assert report.edit_x_axis(font="Courier", font_size=14, italic=True, bold=False, color=(0, 128, 0), label="Freq")


def test_edit_y_axis_label(aedt_app):
    report = aedt_app.post.create_report("dB(S(1,1))")
    assert report.edit_y_axis(
        font="Courier", font_size=14, italic=True, bold=False, color=(0, 128, 0), label="Touchstone"
    )


def test_edit_x_axis_scaling(aedt_app):
    report = aedt_app.post.create_report("dB(S(1,1))")
    assert report.edit_x_axis_scaling(
        linear_scaling=True,
        min_scale="1GHz",
        max_scale="5GHz",
        minor_tick_divs=10,
        min_spacing="0.5GHz",
        units="MHz",
    )


def test_edit_y_axis_scaling(aedt_app):
    report = aedt_app.post.create_report("dB(S(1,1))")
    assert report.edit_y_axis_scaling(
        linear_scaling=False, min_scale="-50", max_scale="10", minor_tick_divs=10, min_spacing="5"
    )


def test_edit_legend(aedt_app):
    report = aedt_app.post.create_report("dB(S(1,1))")
    assert report.edit_legend(
        show_solution_name=True, show_variation_key=False, show_trace_name=False, back_color=(255, 255, 255)
    )


def test_edit_header(aedt_app):
    report = aedt_app.post.create_report("dB(S(1,1))")
    assert report.edit_header(
        company_name="PyAEDT",
        show_design_name=True,
        font="Arial",
        title_size=12,
        subtitle_size=12,
        italic=False,
        bold=False,
        color=(0, 125, 125),
    )


def test_edit_general_settings(aedt_app):
    report = aedt_app.post.create_report("dB(S(1,1))")
    assert report.edit_general_settings(
        background_color=(128, 255, 255),
        plot_color=(255, 0, 255),
        enable_y_stripes=True,
        field_width=6,
        precision=6,
        use_scientific_notation=True,
    )


def test_set_trace_properties(aedt_app):  # pragma: no cover
    new_report = aedt_app.post.reports_by_category.modal_solution("dB(S(1,1))")
    new_report.create()
    assert new_report.traces[0].set_trace_properties(
        style=LineStyle.Dot, width=5, trace_type=TraceType.Digital, color=(0, 255, 0)
    )


def test_set_symbol_properties(aedt_app):  # pragma: no cover
    new_report = aedt_app.post.reports_by_category.modal_solution("dB(S(1,1))")
    new_report.create()
    assert new_report.traces[0].set_symbol_properties(
        show=True, style=SymbolStyle.Box, show_arrows=False, fill=False, color=(0, 0, 255)
    )


def test_set_line_properties(aedt_app):  # pragma: no cover
    new_report = aedt_app.post.reports_by_category.modal_solution("dB(S(1,1))")
    new_report.create()
    new_report.add_limit_line_from_points([3, 5, 5, 3], [-50, -50, -60, -60], "GHz")
    assert new_report.limit_lines[0].set_line_properties(
        style=LineStyle.Dot,
        width=4,
        hatch_above=False,
        violation_emphasis=True,
        hatch_pixels=1,
        color=(255, 255, 0),
    )


def test_add_note(aedt_app):  # pragma: no cover
    new_report = aedt_app.post.reports_by_category.modal_solution()
    new_report.create()
    new_report.add_note("Test", 8000, 1500)
    assert new_report.notes[0].set_note_properties(
        back_color=(0, 0, 255),
        border_visibility=False,
        border_width=3,
        font="Cambria",
        italic=True,
        bold=True,
        font_size=10,
        color=(255, 0, 0),
    )


def test_delete_report(aedt_app):
    aedt_app.create_scattering("MyTestScattering")
    plots_number = len(aedt_app.post.plots)
    assert aedt_app.post.delete_report("MyTestScattering")
    assert len(aedt_app.post.plots) == plots_number - 1
    aedt_app.create_scattering("MyTestScattering1")
    assert aedt_app.post.delete_report()
    assert len(aedt_app.post.plots) == 0


def test_steal_focus_oneditor(aedt_app):
    assert aedt_app.post.steal_focus_oneditor()


def test_create_fieldplot_cutplane_3(aedt_app):
    cutlist = ["Global:XY"]
    setup_name = aedt_app.existing_analysis_sweeps[0]
    quantity_name = "ComplexMag_E"
    intrinsic = {"Freq": "5GHz", "Phase": "180deg"}
    aedt_app.logger.info("Generating the plot")
    plot1 = aedt_app.post.create_fieldplot_cutplane(cutlist, quantity_name, setup_name, intrinsic)
    plot1.IsoVal = "Tone"
    assert plot1.update_field_plot_settings()


@pytest.mark.avoid_ansys_load
def test_plot_field_from_fieldplot(aedt_app, test_tmp_dir):
    cutlist = ["Global:XY"]
    setup_name = aedt_app.existing_analysis_sweeps[0]
    quantity_name = "ComplexMag_E"
    intrinsic = {"Freq": "5GHz", "Phase": "180deg"}
    plot1 = aedt_app.post.create_fieldplot_cutplane(cutlist, quantity_name, setup_name, intrinsic)
    plot1.IsoVal = "Tone"
    aedt_app.logger.info("Generating the image")
    plot_obj = aedt_app.post.plot_field_from_fieldplot(
        plot_name=plot1.name,
        project_path=test_tmp_dir,
        mesh_plot=False,
        image_format="jpg",
        view="xy",
        plot_label=plot1.name + " label",
        show=False,
    )
    assert Path(plot_obj.image_file).is_file()


@pytest.mark.avoid_ansys_load
def test_plot_field_from_fieldplot_scale(aedt_app, test_tmp_dir):
    plot_obj = aedt_app.post.plot_field_from_fieldplot(
        plot_name="plot_test",
        project_path=test_tmp_dir,
        mesh_plot=False,
        image_format="jpg",
        view="xy",
        plot_label="plot_test" + " label",
        show=False,
    )
    Path(plot_obj.image_file).unlink()
    plot_obj.x_scale = 1.1
    plot_obj.y_scale = 0.9
    plot_obj.z_scale = 0.3
    assert plot_obj.x_scale == 1.1
    assert plot_obj.y_scale == 0.9
    assert plot_obj.z_scale == 0.3


@pytest.mark.avoid_ansys_load
def test_plot_field_from_fieldplot_background(aedt_app, test_tmp_dir):
    plot_obj = aedt_app.post.plot_field_from_fieldplot(
        plot_name="plot_test",
        project_path=test_tmp_dir,
        mesh_plot=False,
        image_format="jpg",
        view="xy",
        plot_label="plot_test" + " label",
        show=False,
    )
    plot_obj.background_image = test_tmp_dir / "file_not_exists.jpg"
    assert not plot_obj.background_image


@pytest.mark.avoid_ansys_load
def test_plot_field_from_fieldplot_configurations(aedt_app, test_tmp_dir):
    plot_obj = aedt_app.post.plot_field_from_fieldplot(
        plot_name="plot_test",
        project_path=test_tmp_dir,
        mesh_plot=False,
        image_format="jpg",
        view="xy",
        plot_label="plot_test" + " label",
        show=False,
    )
    plot_obj.convert_fields_in_db = True
    plot_obj.log_multiplier = 20
    plot_obj.plot(plot_obj.image_file, show=False)
    assert Path(plot_obj.image_file).is_file()


@pytest.mark.avoid_ansys_load
def test_plot_field_from_fieldplot_aedtplt(aedt_app, test_tmp_dir):
    plot_obj = aedt_app.post.plot_field_from_fieldplot(
        plot_name="plot_test",
        project_path=test_tmp_dir,
        mesh_plot=False,
        image_format="jpg",
        view="xy",
        plot_label="plot_test" + " label",
        show=False,
        file_format="aedtplt",
    )
    assert Path(plot_obj.image_file).is_file()


@pytest.mark.avoid_ansys_load
def test_create_fieldplot_cutplane_vector(aedt_app, test_tmp_dir):
    cutlist = ["Global:XY"]
    setup_name = aedt_app.existing_analysis_sweeps[0]
    quantity_name = "Vector_E"
    intrinsic = {"Freq": "5GHz", "Phase": "180deg"}
    aedt_app.logger.info("Generating the plot")
    assert aedt_app.post.create_fieldplot_cutplane(
        cutlist, quantity_name, setup_name, intrinsic, filter_objects=aedt_app.modeler.object_names
    )


@pytest.mark.avoid_ansys_load
def test_plot_field_range_min_max(aedt_app, test_tmp_dir):
    cutlist = ["Global:XY"]
    setup_name = aedt_app.existing_analysis_sweeps[0]
    quantity_name = "Vector_E"
    intrinsic = {"Freq": "5GHz", "Phase": "180deg"}
    assert aedt_app.post.create_fieldplot_cutplane(
        cutlist, quantity_name, setup_name, intrinsic, filter_objects=aedt_app.modeler.object_names
    )
    plot_obj = aedt_app.post.plot_field(
        "Vector_E",
        cutlist,
        "CutPlane",
        setup=setup_name,
        intrinsics=intrinsic,
        mesh_on_fields=False,
        view="isometric",
        show=False,
        export_path=test_tmp_dir,
        image_format="jpg",
    )
    assert Path(plot_obj.image_file).is_file()
    assert plot_obj.range_min is None
    assert plot_obj.range_max is None


@pytest.mark.avoid_ansys_load
def test_plot_field_range_min_max_1(aedt_app, test_tmp_dir):
    cutlist = ["Global:XY"]
    setup_name = aedt_app.existing_analysis_sweeps[0]
    intrinsic = {"Freq": "5GHz", "Phase": "180deg"}
    plot_obj_1 = aedt_app.post.plot_field(
        "Vector_E",
        cutlist,
        "CutPlane",
        setup=setup_name,
        intrinsics=intrinsic,
        mesh_on_fields=False,
        view="isometric",
        show=False,
        export_path=test_tmp_dir,
        image_format="jpg",
        log_scale=False,
    )
    assert Path(plot_obj_1.image_file).is_file()
    assert plot_obj_1.range_min is None
    assert plot_obj_1.range_max is None


@pytest.mark.avoid_ansys_load
def test_plot_field_range_min_max_2(aedt_app, test_tmp_dir):
    cutlist = ["Global:XY"]
    setup_name = aedt_app.existing_analysis_sweeps[0]
    intrinsic = {"Freq": "5GHz", "Phase": "180deg"}
    plot_obj_2 = aedt_app.post.plot_field(
        "Vector_E",
        cutlist,
        "CutPlane",
        setup=setup_name,
        intrinsics=intrinsic,
        mesh_on_fields=False,
        view="isometric",
        show=False,
        export_path=test_tmp_dir,
        image_format="jpg",
        log_scale=False,
        scale_min=0,
        scale_max=10e6,
    )
    assert Path(plot_obj_2.image_file).is_file()
    assert plot_obj_2.range_min == 0
    assert plot_obj_2.range_max == 10e6
    assert plot_obj_2.range_max == 10e6


@pytest.mark.avoid_ansys_load
def test_plot_field_range_min_max_3(aedt_app, test_tmp_dir):
    cutlist = ["Global:XY"]
    setup_name = aedt_app.existing_analysis_sweeps[0]
    intrinsic = {"Freq": "5GHz", "Phase": "180deg"}

    plot_obj_1 = aedt_app.post.plot_field(
        "Vector_E",
        cutlist,
        "CutPlane",
        setup=setup_name,
        intrinsics=intrinsic,
        mesh_on_fields=False,
        view="isometric",
        show=False,
        export_path=test_tmp_dir,
        image_format="jpg",
        log_scale=False,
    )
    assert Path(plot_obj_1.image_file).is_file()
    assert plot_obj_1.range_min is None
    assert plot_obj_1.range_max is None


@pytest.mark.avoid_ansys_load
def test_plot_field_range_min_max_4(aedt_app, test_tmp_dir):
    cutlist = ["Global:XY"]
    setup_name = aedt_app.existing_analysis_sweeps[0]
    intrinsic = {"Freq": "5GHz", "Phase": "180deg"}

    plot_obj_4 = aedt_app.post.plot_field(
        "Vector_E",
        cutlist,
        "CutPlane",
        setup=setup_name,
        intrinsics=intrinsic,
        mesh_on_fields=False,
        view="isometric",
        show=False,
        export_path=test_tmp_dir,
        image_format="jpg",
        log_scale=True,
        scale_min=10e6,
        scale_max=0,
    )
    assert Path(plot_obj_4.image_file).is_file()
    assert plot_obj_4.range_min is None
    assert plot_obj_4.range_max is None


@pytest.mark.avoid_ansys_load
def test_plot_field_range_min_max_5(aedt_app, test_tmp_dir):
    cutlist = ["Global:XY"]
    setup_name = aedt_app.existing_analysis_sweeps[0]
    intrinsic = {"Freq": "5GHz", "Phase": "180deg"}
    plot_obj_5 = aedt_app.post.plot_field(
        "Vector_E",
        cutlist,
        "CutPlane",
        setup=setup_name,
        intrinsics=intrinsic,
        mesh_on_fields=False,
        view="isometric",
        show=False,
        export_path=test_tmp_dir,
        image_format="jpg",
        log_scale=False,
        scale_min=0,
    )
    assert Path(plot_obj_5.image_file).is_file()
    assert plot_obj_5.range_min is None
    assert plot_obj_5.range_max is None


@pytest.mark.avoid_ansys_load
def test_plot_model_obj(aedt_app, test_tmp_dir):
    obj = aedt_app.post.plot_model_obj(show=False, export_path=str(test_tmp_dir / "image.jpg"))
    assert Path(obj.image_file).is_file()


@pytest.mark.avoid_ansys_load
def test_plot_model_obj_1(aedt_app, test_tmp_dir):
    obj2 = aedt_app.post.plot_model_obj(
        show=False, export_path=test_tmp_dir / "image2.jpg", plot_as_separate_objects=False
    )
    assert Path(obj2.image_file).exists()


@pytest.mark.avoid_ansys_load
def test_plot_model_obj_2(aedt_app, test_tmp_dir):
    obj3 = aedt_app.post.plot_model_obj(show=False, export_path=str(test_tmp_dir / "image2.jpg"), clean_files=True)
    assert Path(obj3.image_file).is_file()


@pytest.mark.avoid_ansys_load
def test_create_field_plot(aedt_app):
    cutlist = ["Global:XY"]
    plot = aedt_app.post._create_fieldplot(
        assignment=cutlist,
        quantity="Mag_E",
        setup=aedt_app.nominal_adaptive,
        intrinsics={},
        list_type="CutPlane",
    )
    assert plot


@pytest.mark.avoid_ansys_load
def test_create_fieldplot_line(aedt_app):
    udp1 = [0, 0, 0]
    udp2 = [1, 0, 0]
    setup_name = "Setup1 : LastAdaptive"
    intrinsic = {"Freq": "5GHz", "Phase": "180deg"}
    aedt_app.modeler.create_polyline([udp1, udp2], name="Poly1", non_model=True)
    field_line_plot = aedt_app.post.create_fieldplot_line("Poly1", "Mag_E", setup_name, intrinsic)
    assert field_line_plot
    aedt_app.post.create_fieldplot_line("Poly1", "Mag_E", setup_name, intrinsic, field_line_plot.name)


def test_reload(aedt_app, add_app):
    aedt_app.post.plot_field("Mag_E", "inner", show=False, keep_plot_after_generation=True)
    aedt_app.save_project()
    app2 = add_app(project=aedt_app.project_name, close_projects=False)
    assert len(app2.post.field_plots) == len(aedt_app.post.field_plots)


def test_reports_by_category_eye_diagram_no_report(aedt_app):
    assert not aedt_app.post.reports_by_category.eye_diagram()


def test_reports_by_category_eigenmode(aedt_app):
    assert aedt_app.post.reports_by_category.eigenmode()


def test_test_parse_vector():
    input_file = TESTS_VISUALIZATION_PATH / "example_models" / TEST_SUBFOLDER / "test_vector.aedtplt"
    out = _parse_aedtplt(str(input_file))
    assert isinstance(out[0], list)
    assert isinstance(out[1], list)
    assert isinstance(out[2], list)
    assert isinstance(out[3], bool)
    input_file = TESTS_VISUALIZATION_PATH / "example_models" / TEST_SUBFOLDER / "test_vector_no_solutions.aedtplt"
    assert _parse_aedtplt(str(input_file))


def test_export_mesh(aedt_app):
    assert Path(aedt_app.export_mesh_stats("Setup1")).is_file()


def test_sweep_from_json(aedt_app):
    input_file = TESTS_VISUALIZATION_PATH / "example_models" / "report_json" / "Modal_Report_Simple.json"
    dict_vals = read_json(str(input_file))
    assert aedt_app.post.create_report_from_configuration(report_settings=dict_vals)
    assert aedt_app.post.create_report_from_configuration(report_settings=dict_vals, matplotlib=True, show=False)


def test_sweep_from_json_1(aedt_app):
    input_file = TESTS_VISUALIZATION_PATH / "example_models" / "report_json" / "Modal_Report.json"
    assert aedt_app.post.create_report_from_configuration(str(input_file))
    assert aedt_app.post.create_report_from_configuration(
        str(input_file),
        matplotlib=True,
        show=False,
    )


def test_dynamic_update(aedt_app):
    val = aedt_app.post.update_report_dynamically
    aedt_app.post.update_report_dynamically = not val
    assert aedt_app.post.update_report_dynamically != val


def test_setup_derivative(aedt_app):
    setup_derivative = aedt_app.setups[1]
    assert setup_derivative.set_tuning_offset({"inner_radius": 0.1})


def test_setup_derivative_auto(aedt_app):
    setup_derivative_auto = aedt_app.setups[2]
    assert setup_derivative_auto.set_tuning_offset({"inner_radius": 0.1})


def test_trace_characteristics(m2d_app):
    m2d_app.set_active_design("Design1")
    assert m2d_app.post.plots[0].add_trace_characteristics("XAtYVal", arguments=["0"], solution_range=["Full"])


def test_trace_export_table(m2d_app, test_tmp_dir):
    m2d_app.set_active_design("Design2")
    plot_name = m2d_app.post.plots[0].plot_name

    output_file_path = test_tmp_dir / "zeroes.tab"
    assert m2d_app.post.plots[0].export_table_to_file(plot_name, str(output_file_path), "Legend")
    assert output_file_path.is_file()


def test_trace_export_table_1(m2d_app, test_tmp_dir):
    m2d_app.set_active_design("Design2")
    plot_name = m2d_app.post.plots[0].plot_name
    output_file_path = test_tmp_dir / "zeroes.tab"
    with pytest.raises(AEDTRuntimeError):
        m2d_app.post.plots[0].export_table_to_file("Invalid Name", str(output_file_path), "Legend")
    with pytest.raises(AEDTRuntimeError):
        m2d_app.post.plots[0].export_table_to_file(plot_name, "Invalid Path", "Legend")
    with pytest.raises(AEDTRuntimeError):
        m2d_app.post.plots[0].export_table_to_file(plot_name, str(output_file_path), "Invalid Export Type")


@pytest.mark.avoid_ansys_load
def test_create_fieldplot_surface_5(m2d_blank):
    circ = m2d_blank.modeler.create_circle(origin=[0, 0, 0], radius=5, material="copper")
    m2d_blank.assign_current(assignment=circ.name, amplitude=5)
    region = m2d_blank.modeler.create_region(pad_value=100)
    m2d_blank.assign_balloon(assignment=region.edges)
    m2d_blank.create_setup()
    assert m2d_blank.post.create_fieldplot_surface(assignment=m2d_blank.modeler.object_list, quantity="Flux_Lines")
