# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 - 2026 Synopsys, Inc. and ANSYS, Inc. All rights reserved.
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

from __future__ import annotations

from unittest.mock import MagicMock
from unittest.mock import patch

import pytest

from ansys.aedt.core import Hfss
from ansys.aedt.core.extensions.common.result_calculator import ResultCalculatorExtension

SUBFOLDER = "result_calculator_test_data"
SHOW_ERROR = "ansys.aedt.core.extensions.common.result_calculator.messagebox.showerror"


def _sync_run_async(self, task, on_done):
    """Synchronous replacement for ``_run_async`` (no background thread)."""
    try:
        result = task()
    except Exception as exc:
        result = exc
    on_done(result)


def _reset_extension(extension):
    """Drop the state left by a previous test, so one extension can be reused."""
    extension.store.data.clear()
    extension.service._cache_by_session.clear()
    extension._ex_preview_curves = None
    extension._ex_preview_key = None
    extension._formula_result = None
    extension._ds_manual_xy = None
    extension._ds_aedt_xy = None
    extension._fi_preview_xy = None
    extension.ds_x_text.delete("1.0", "end")
    extension.ds_y_text.delete("1.0", "end")


@pytest.fixture(scope="module")
def rc_extension_holder():
    """Keep a single extension (a single Tk root) for the whole module.

    Creating many Tk roots in the same process makes the Tcl initialization fail randomly.
    """
    holder = {}
    yield holder
    extension = holder.get("extension")
    if extension is not None:
        try:
            extension.root.destroy()
        except Exception:
            pass


@pytest.fixture()
def rc_extension_factory(add_app_example, rc_extension_holder):
    """Factory fixture: call it with (project, design) to get a wired extension."""
    created_app = None

    def _make(project: str, design: str):
        nonlocal created_app
        app = add_app_example(
            application=Hfss,
            project=project,
            design=design,
            subfolder=SUBFOLDER,
        )
        extension = rc_extension_holder.get("extension")
        if extension is None:
            extension = ResultCalculatorExtension(withdraw=True)
            rc_extension_holder["extension"] = extension
        _reset_extension(extension)
        service = extension.service
        service.desktop = app.desktop_class
        pid = app.desktop_class.aedt_process_id
        service.current_session_pid = pid
        service._cache_by_session[pid] = service._empty_session_cache()
        created_app = app
        return extension, app, app.project_name, design

    yield _make

    if created_app is not None:
        try:
            created_app.close_project(save=False)
        except Exception:
            pass


@pytest.fixture()
def rc_extension_dataset(rc_extension_factory):
    return rc_extension_factory("Datasets", "HFSSDesign1")


@pytest.fixture()
def rc_extension_get_results(rc_extension_factory):
    return rc_extension_factory("res_calc_test_v2", "with_results")


@pytest.mark.flaky(reruns=3, reruns_delay=2)
@patch(SHOW_ERROR, new=MagicMock())
@patch.object(ResultCalculatorExtension, "_run_async", _sync_run_async)
def test_import_dataset(rc_extension_dataset):
    """Importing a project dataset ($ds1) adds it to the result store.
    Importing a design dataset (ds2) adds it to the result store.
    """
    extension, datasets_app, project, design = rc_extension_dataset

    datasets_to_test = ["$ds1", "ds2"]

    for dataset in datasets_to_test:
        # Load datasets and verify that dataset is present.
        names, err = extension.service.load_datasets_for_design(project, design)
        assert err is None
        assert dataset in names

        # Simulate the UI: set cascade vars and dataset var, then call _ds_aedt_add.
        extension._ds_cascade.project_var.set(project)
        extension._ds_cascade.design_var.set(design)

        # test import Dataset
        extension.ds_aedt_dataset_var.set(dataset)

        extension._ds_aedt_add()

        # The dataset name is sanitized: "$ds1" -> "project_ds1"
        if dataset.startswith("$"):
            name_to_verify = "project_" + dataset[1:]
            desc_to_verify = "project"
        else:
            name_to_verify = dataset
            desc_to_verify = "design"

        assert name_to_verify in extension.store.data
        meta = extension.store.data[name_to_verify]["metadata"]
        assert desc_to_verify in meta["description"].lower()


@pytest.mark.flaky(reruns=3, reruns_delay=2)
@patch(SHOW_ERROR, new=MagicMock())
@patch.object(ResultCalculatorExtension, "_run_async", _sync_run_async)
def test_push_manual_dataset_as_project_dataset(rc_extension_dataset):
    """The 'Add Manual Dataset as Project Dataset' button creates a project dataset in AEDT."""
    extension, datasets_app, project, design = rc_extension_dataset

    # Fill in the UI fields for the manual dataset.
    extension._ds_cascade.project_var.set(project)
    extension._ds_cascade.design_var.set(design)
    extension.ds_name_var.set("manual_proj_ds")
    extension.ds_x_text.insert("1.0", "1, 2, 3")
    extension.ds_y_text.insert("1.0", "10, 20, 30")

    extension._ds_push_to_aedt(is_project_dataset=True)

    # Need to save the project as the datasets are retrieved from the aedt file
    datasets_app.save_project()

    # Verify the dataset was created in AEDT as a project dataset ($manual_proj_ds).
    assert "$manual_proj_ds" in datasets_app.project_datasets
    ds = datasets_app.project_datasets["$manual_proj_ds"]
    assert list(ds.x) == [1.0, 2.0, 3.0]
    assert list(ds.y) == [10.0, 20.0, 30.0]


@pytest.mark.flaky(reruns=3, reruns_delay=2)
@patch(SHOW_ERROR, new=MagicMock())
@patch.object(ResultCalculatorExtension, "_run_async", _sync_run_async)
def test_push_manual_dataset_as_design_dataset(rc_extension_dataset):
    """The 'Add Manual Dataset as Design Dataset' button creates a design dataset in AEDT."""
    extension, datasets_app, project, design = rc_extension_dataset

    extension._ds_cascade.project_var.set(project)
    extension._ds_cascade.design_var.set(design)
    extension.ds_name_var.set("manual_design_ds")
    extension.ds_x_text.insert("1.0", "5, 10, 15")
    extension.ds_y_text.insert("1.0", "50, 100, 150")

    extension._ds_push_to_aedt(is_project_dataset=False)

    # Need to save the project as the datasets are retrieved from the aedt file
    datasets_app.save_project()

    # Verify the dataset was created in AEDT as a design dataset (no $ prefix).
    assert "manual_design_ds" in datasets_app.design_datasets
    ds = datasets_app.design_datasets["manual_design_ds"]
    assert list(ds.x) == [5.0, 10.0, 15.0]
    assert list(ds.y) == [50.0, 100.0, 150.0]


@pytest.mark.flaky(reruns=3, reruns_delay=2)
@patch(SHOW_ERROR, new=MagicMock())
@patch.object(ResultCalculatorExtension, "_run_async", _sync_run_async)
def test_import_existing_report_trace(rc_extension_get_results):
    """Importing a trace from an existing AEDT report adds it to the result store."""
    extension, results_app, project, design = rc_extension_get_results

    report_trace_list = [["S11", "dB(S(1,1))"], ["Gain", "dB(GainTotal)"]]

    for i, report_trace in enumerate(report_trace_list):
        report_name, trace_name = report_trace

        # Pre-populate the service cache exactly as the UI cascade would do:
        # Session -> Project -> Design -> Reports -> Traces.
        # Without this, get_trace_data raises KeyError on the empty cache.
        service = extension.service
        service.load_designs(project)
        service.load_reports_for_design(project, design)
        service.load_traces_for_report(project, design, report_name)

        extension._ex_cascade.project_var.set(project)
        extension._ex_cascade.design_var.set(design)
        extension.ex_report.set(report_name)
        extension.ex_trace.set(trace_name)

        extension._import_existing_trace()

        assert len(extension.store.data) == i + 1
        key = list(extension.store.data.keys())[i]
        entry = extension.store.data[key]
        assert entry["source"] == "existing_report"
        assert entry["metadata"]["report"] == report_name
        assert entry["metadata"]["trace"] == trace_name
        assert len(entry["x"]) > 0
        assert len(entry["y"]) > 0


def _select_existing_trace(extension, project, design, report_name, trace_name):
    """Select an existing report trace in the extension and return all its plot data.

    Test names must stay short: the pytest temporary folder is named after the test, and
    the AEDT results files exceed the Windows 260 characters path limit otherwise.
    """
    service = extension.service
    service.load_designs(project)
    service.load_reports_for_design(project, design)
    service.load_traces_for_report(project, design, report_name)

    extension._ex_cascade.project_var.set(project)
    extension._ex_cascade.design_var.set(design)
    extension.ex_report.set(report_name)
    extension.ex_trace.set(trace_name)

    extension._ex_trace_changed()

    return service.get_trace_data(project, design, report_name, trace_name, plot_index=None)


@pytest.mark.flaky(reruns=3, reruns_delay=2)
@patch(SHOW_ERROR, new=MagicMock())
@patch.object(ResultCalculatorExtension, "_run_async", _sync_run_async)
def test_ex_plot_multiple(rc_extension_get_results):
    """The Plot dropdown lists an 'All' entry and each plot when the trace has multiple plots."""
    extension, results_app, project, design = rc_extension_get_results

    all_data = _select_existing_trace(extension, project, design, "Gain_3Curves", "dB(GainTheta)")
    n_plots = len(all_data["plot_names"])
    assert n_plots > 1

    values = list(extension.ex_plot_cb["values"])
    assert values == [extension._ALL_PLOTS, *all_data["plot_names"]]
    assert extension.ex_plot.get() == extension._ALL_PLOTS
    assert str(extension.ex_plot_cb.cget("state")) == "readonly"
    assert str(extension.btn_import_existing.cget("state")) == "disabled"
    assert len(extension._ex_preview_curves) == n_plots

    # Selecting a single plot shows only that plot and enables the import.
    extension.ex_plot.set(all_data["plot_names"][0])
    extension._ex_plot_changed()
    assert len(extension._ex_preview_curves) == 1
    assert str(extension.btn_import_existing.cget("state")) == "normal"
    extension._import_existing_trace()
    entry = list(extension.store.data.values())[-1]
    assert entry["metadata"]["plot"] == all_data["plot_names"][0]


@pytest.mark.flaky(reruns=3, reruns_delay=2)
@patch(SHOW_ERROR, new=MagicMock())
@patch.object(ResultCalculatorExtension, "_run_async", _sync_run_async)
def test_ex_plot_single(rc_extension_get_results):
    """The Plot dropdown is disabled and the import is enabled when the trace has a single plot."""
    extension, results_app, project, design = rc_extension_get_results

    all_data = _select_existing_trace(extension, project, design, "S11", "dB(S(1,1))")
    assert len(all_data["plot_names"]) == 1

    values = list(extension.ex_plot_cb["values"])
    assert values == [extension._SINGLE_PLOT_MSG]
    assert str(extension.ex_plot_cb.cget("state")) == "disabled"
    assert str(extension.btn_import_existing.cget("state")) == "normal"
    assert len(extension._ex_preview_curves) == 1
