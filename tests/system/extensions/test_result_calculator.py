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

from unittest.mock import patch

import pytest

from ansys.aedt.core import Hfss
from ansys.aedt.core.extensions.common.result_calculator import ResultCalculatorExtension

SUBFOLDER = "result_calculator_test_data"
DESIGN_NAME = "HFSSDesign1"


@pytest.fixture()
def rc_extension_factory(add_app_example):
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
        extension = ResultCalculatorExtension(withdraw=True)
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
    extension, app, project, design = rc_extension_factory("Datasets", "HFSSDesign1")
    return extension, app, project


@pytest.fixture()
def rc_extension_get_results(rc_extension_factory):
    extension, app, project, design = rc_extension_factory("res_calc_test_v2", "with_results")
    return extension, app, project


@pytest.fixture()
def sync_run_async():
    """Return a synchronous replacement for _run_async.
    Mock _run_async to execute synchronously (no background thread).
    """

    def _impl(task, on_done):
        try:
            result = task()
        except Exception as exc:
            result = exc
        on_done(result)

    return _impl


@pytest.mark.flaky(reruns=3, reruns_delay=2)
def test_import_dataset(rc_extension_dataset, sync_run_async):
    """Importing a project dataset ($ds1) adds it to the result store.
    Importing a design dataset (ds2) adds it to the result store.
    """
    extension, datasets_app, project = rc_extension_dataset

    datasets_to_test = ["$ds1", "ds2"]

    for dataset in datasets_to_test:
        # Load datasets and verify that dataset is present.
        names, err = extension.service.load_datasets_for_design(project, DESIGN_NAME)
        assert err is None
        assert dataset in names

        # Simulate the UI: set cascade vars and dataset var, then call _ds_aedt_add.
        extension._ds_cascade.project_var.set(project)
        extension._ds_cascade.design_var.set(DESIGN_NAME)

        # test import Dataset
        extension.ds_aedt_dataset_var.set(dataset)

        # Suppress any messagebox that would block CI/CD.
        with (
            patch("ansys.aedt.core.extensions.common.result_calculator.messagebox.showerror"),
            patch.object(extension, "_run_async", side_effect=sync_run_async),
        ):
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
def test_push_manual_dataset_as_project_dataset(rc_extension_dataset, sync_run_async):
    """The 'Add Manual Dataset as Project Dataset' button creates a project dataset in AEDT."""
    extension, datasets_app, project = rc_extension_dataset

    # Fill in the UI fields for the manual dataset.
    extension._ds_cascade.project_var.set(project)
    extension._ds_cascade.design_var.set(DESIGN_NAME)
    extension.ds_name_var.set("manual_proj_ds")
    extension.ds_x_text.insert("1.0", "1, 2, 3")
    extension.ds_y_text.insert("1.0", "10, 20, 30")

    # Suppress any messagebox that would block CI/CD.
    with (
        patch("ansys.aedt.core.extensions.common.result_calculator.messagebox.showerror"),
        patch.object(extension, "_run_async", side_effect=sync_run_async),
    ):
        extension._ds_push_to_aedt(is_project_dataset=True)

    # Need to save the project as the datasets are retrieved from the aedt file
    datasets_app.save_project()

    # Verify the dataset was created in AEDT as a project dataset ($manual_proj_ds).
    assert "$manual_proj_ds" in datasets_app.project_datasets
    ds = datasets_app.project_datasets["$manual_proj_ds"]
    assert list(ds.x) == [1.0, 2.0, 3.0]
    assert list(ds.y) == [10.0, 20.0, 30.0]


@pytest.mark.flaky(reruns=3, reruns_delay=2)
def test_push_manual_dataset_as_design_dataset(rc_extension_dataset, sync_run_async):
    """The 'Add Manual Dataset as Design Dataset' button creates a design dataset in AEDT."""
    extension, datasets_app, project = rc_extension_dataset

    extension._ds_cascade.project_var.set(project)
    extension._ds_cascade.design_var.set(DESIGN_NAME)
    extension.ds_name_var.set("manual_design_ds")
    extension.ds_x_text.insert("1.0", "5, 10, 15")
    extension.ds_y_text.insert("1.0", "50, 100, 150")

    # Suppress any messagebox that would block CI/CD.
    with (
        patch("ansys.aedt.core.extensions.common.result_calculator.messagebox.showerror"),
        patch.object(extension, "_run_async", side_effect=sync_run_async),
    ):
        extension._ds_push_to_aedt(is_project_dataset=False)

    # Need to save the project as the datasets are retrieved from the aedt file
    datasets_app.save_project()

    # Verify the dataset was created in AEDT as a design dataset (no $ prefix).
    assert "manual_design_ds" in datasets_app.design_datasets
    ds = datasets_app.design_datasets["manual_design_ds"]
    assert list(ds.x) == [5.0, 10.0, 15.0]
    assert list(ds.y) == [50.0, 100.0, 150.0]


@pytest.mark.flaky(reruns=3, reruns_delay=2)
def test_import_existing_report_trace(rc_extension_get_results, sync_run_async):
    """Importing a trace from an existing AEDT report adds it to the result store."""
    extension, results_app, project = rc_extension_get_results

    design_with_results = "with_results"
    report_trace_list = [["S11", "dB(S(1,1))"], ["Gain", "dB(GainTotal)"]]

    for i, report_trace in enumerate(report_trace_list):
        report_name, trace_name = report_trace

        # Pre-populate the service cache exactly as the UI cascade would do:
        # Session -> Project -> Design -> Reports -> Traces.
        # Without this, get_trace_data raises KeyError on the empty cache.
        service = extension.service
        service.load_designs(project)
        service.load_reports_for_design(project, design_with_results)
        service.load_traces_for_report(project, design_with_results, report_name)

        extension._ex_cascade.project_var.set(project)
        extension._ex_cascade.design_var.set(design_with_results)
        extension.ex_report.set(report_name)
        extension.ex_trace.set(trace_name)

        # Suppress any messagebox that would block CI/CD.
        with (
            patch("ansys.aedt.core.extensions.common.result_calculator.messagebox.showerror"),
            patch.object(extension, "_run_async", side_effect=sync_run_async),
        ):
            extension._import_existing_trace()

        assert len(extension.store.data) == i + 1
        key = list(extension.store.data.keys())[i]
        entry = extension.store.data[key]
        assert entry["source"] == "existing_report"
        assert entry["metadata"]["report"] == report_name
        assert entry["metadata"]["trace"] == trace_name
        assert len(entry["x"]) > 0
        assert len(entry["y"]) > 0
