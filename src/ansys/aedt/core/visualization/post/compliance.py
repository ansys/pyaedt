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
import os.path
from pathlib import Path
import time
from typing import List

import numpy as np
from pyedb.generic.constants import unit_converter

from ansys.aedt.core import settings
from ansys.aedt.core.base import PyAedtBase
from ansys.aedt.core.generic.design_types import get_pyaedt_app
from ansys.aedt.core.generic.file_utils import generate_unique_name
from ansys.aedt.core.generic.file_utils import read_configuration_file
from ansys.aedt.core.generic.file_utils import read_csv
from ansys.aedt.core.generic.file_utils import write_configuration_file
from ansys.aedt.core.generic.file_utils import write_csv
from ansys.aedt.core.generic.general_methods import pyaedt_function_handler
from ansys.aedt.core.internal.filesystem import search_files
from ansys.aedt.core.visualization.plot.pdf import AnsysReport
from ansys.aedt.core.visualization.post.spisim import SpiSim

default_keys = [
    "file",
    "power",
    "buffer",
    "trise",
    "tfall",
    "UIorBPSValue",
    "BitPattern",
    "R",
    "L",
    "C",
    "DC",
    "V1",
    "V2",
    "TD",
]


class CommonTemplate(PyAedtBase):
    def __init__(self, report):
        self._name = report["name"]
        self.report_type = report.get("type", "frequency")
        self.config_file = report.get("config", "")
        self.design_name = report.get("design_name", "")
        self.traces = report.get("traces", [])
        self.pass_fail = report.get("pass_fail", False)
        self.group_plots = report.get("group_plots", False)
        self._project_name = None
        self.project = report.get("project", None)
        self._pass_fail_criteria = report.get("pass_fail_criteria", "")

    @property
    def name(self):
        """Report name.

        Returns
        -------
        str
        """
        return self._name

    @property
    def project_name(self):
        """Project name.

        Returns
        -------
        str
        """
        if self._project_name:
            return self._project_name
        if self.project and self.project.endswith(".aedt"):
            return os.path.split(os.path.splitext(self.project)[0])[-1]
        return

    @project_name.setter
    def project_name(self, val):
        self._project_name = val

    @property
    def project(self):
        """Project path."""
        return self._project

    @project.setter
    def project(self, val):
        self._project = val

    @property
    def report_type(self):
        """Report type.

        Returns
        -------
        str
        """
        return self._report_type

    @report_type.setter
    def report_type(self, val):
        self._report_type = val

    @property
    def config_file(self):
        """Configuration file.

        Returns
        -------
        str
        """
        return self._config_file

    @config_file.setter
    def config_file(self, val):
        self._config_file = val

    @property
    def design_name(self):
        """Design name in AEDT.

        Returns
        -------
        str
        """
        return self._design_name

    @design_name.setter
    def design_name(self, val):
        self._design_name = val

    @property
    def traces(self):
        """Trace list.

        Returns
        -------
        list
        """
        return self._traces

    @traces.setter
    def traces(self, val):
        if not isinstance(val, list):
            self._traces = [val]
        else:
            self._traces = val

    @property
    def pass_fail(self):
        """Flag indicating if pass/fail criteria is applied.

        Returns
        -------
        bool
        """
        return self._pass_fail

    @pass_fail.setter
    def pass_fail(self, val):
        self._pass_fail = val

    @property
    def pass_fail_criteria(self):
        """Pass/fail criteria.

        Returns
        -------
        float, int
        """
        return self._pass_fail_criteria

    @pass_fail_criteria.setter
    def pass_fail_criteria(self, val):
        self._pass_fail_criteria = val


class ReportTemplate(CommonTemplate):
    def __init__(self, report):
        CommonTemplate.__init__(self, report)
        self.group_plots = report.get("group_plots", False)

    @property
    def group_plots(self):
        """Flag indicating if plots are grouped into a single chart or kept independent.

        Returns
        -------
        bool
        """
        return self._group_plots

    @group_plots.setter
    def group_plots(self, val):
        self._group_plots = val


class ReportParametersTemplate(CommonTemplate):
    def __init__(self, report):
        CommonTemplate.__init__(self, report)
        self._parameter_name = report.get("parameter_name", "")
        self._pass_fail_criteria = report.get("pass_fail_criteria", 1e9)

    @property
    def parameter_name(self):
        """Parameter name.

        Returns
        -------
        str
        """
        return self._parameter_name

    @parameter_name.setter
    def parameter_name(self, val):
        self._parameter_name = val


class ParametersTemplate(CommonTemplate):
    def __init__(self, report):
        CommonTemplate.__init__(self, report)
        self.trace_pins = report.get("trace_pins", [])
        self._pass_fail_criteria = report.get("pass_fail_criteria", 1e9)

    @property
    def trace_pins(self):
        """Trace pin coupling list.

        Returns
        -------
        list
        """
        return self._trace_pins

    @trace_pins.setter
    def trace_pins(self, val):
        self._trace_pins = val


class VirtualComplianceGenerator(PyAedtBase):
    """Class to generate a Virtual Compliance configuration."""

    def __init__(self, compliance_name, project_name, specification_folder=None):
        self.config = {
            "general": {
                "name": compliance_name,
                "version": "1.0",
                "add_project_info": True,
                "add_specs_info": True if specification_folder else False,
                "project_info_keys": [
                    "file",
                    "power",
                    "buffer",
                    "trise",
                    "tfall",
                    "UIorBPSValue",
                    "BitPattern",
                    "R",
                    "L",
                    "C",
                    "DC",
                    "V1",
                    "V2",
                    "TD",
                ],
                "specs_folder": specification_folder if specification_folder else "",
                "delete_after_export": True,
                "project": project_name,
                "use_portrait": True,
            },
            "parameters": [],
            "reports": [],
            "report_derived_parameters": [],
        }

    @property
    def project_file(self):
        """Project file."""
        return self.config["general"]["project"]

    @project_file.setter
    def project_file(self, val):
        self.config["general"]["project"] = val

    @pyaedt_function_handler()
    def add_erl_parameters(
        self, design_name, config_file, traces, pins, pass_fail, pass_fail_criteria=0, name="ERL", project=None
    ):
        """Add Com parameters computed by SpiSim into the configuration.

        Parameters
        ----------
        design_name : str
            Design name.
        config_file : str or :class:`pathlib.Path`
            Full path to ``cfg`` file.
        traces : list
            List of traces to compute com parameters.
        pins : list
            List of list containing input pints and output pins on which compute com parameters.
            Pins can be names or numbers.
        pass_fail : bool
            Whether if to compute pass fail on this parameter or not.
            If True, then the parameter ``pass_fail_criteria`` has to be set accordingly.
        pass_fail_criteria : float
            If the criteria is greater
        name : str, optional
            Name of the report.
        project : str, optional
            Full path to the project to use for the computation of this report.
            If ``None`` the default project will be used.
        """
        pars = {
            "name": name,
            "design_name": design_name,
            "config": str(config_file),
            "traces": traces,
            "trace_pins": pins,
            "pass_fail": pass_fail,
            "pass_fail_criteria": pass_fail_criteria,
        }
        if project:
            pars["project"] = project
        self.config["parameters"].append(pars)

    @pyaedt_function_handler()
    def add_report_derived_parameter(
        self, design_name, config_file, parameter, traces, report_type, pass_fail_criteria, name, project=None
    ):
        """Add report derived parameters computed by AEDT and python into the configuration.

        Parameters
        ----------
        design_name : str
            Design name.
        config_file : str or :class:`pathlib.Path`
            Full path to ``cfg`` file.
        parameter: str,
            Parameter name. Allowed value are ``"skew"``.
        traces : list
            List of traces to compute com parameters.
        report_type : str
            Report Type.
        pass_fail_criteria : int, float
           Pass fail criterial for parameter.
        name : str, optional
            Name of the report.
        project : str, optional
            Full path to the project to use for the computation of this report.
            If ``None`` the default project will be used.
        """
        pars = {
            "name": name,
            "design_name": design_name,
            "type": report_type,
            "config": str(config_file),
            "traces": traces,
            "pass_fail": True,
            "pass_fail_criteria": pass_fail_criteria,
            "parameter_name": parameter,
        }
        if project:
            pars["project"] = project
        self.config["report_derived_parameters"].append(pars)

    @pyaedt_function_handler()
    def add_report(self, design_name, config_file, traces, report_type, pass_fail, group_plots, name, project=None):
        """Add Com parameters computed by SpiSim into the configuration.

        Parameters
        ----------
        design_name : str
            Design name.
        config_file : str
            Full path to ``cfg`` file.
        traces : list
            List of traces to compute com parameters.
        report_type : str
            Report Type.
        pass_fail : bool
            Whether if to compute pass fail on this parameter or not.
        group_plots : bool
           Whether if to group all the traces in the same plot or not.
        name : str, optional
            Name of the report.
        project : str, optional
            Full path to the project to use for the computation of this report.
            If ``None`` the default project will be used.
        """
        pars = {
            "name": name,
            "design_name": design_name,
            "type": report_type,
            "config": config_file,
            "traces": traces,
            "pass_fail": pass_fail,
            "group_plots": group_plots,
        }
        if project:
            pars["project"] = project
        self.config["reports"].append(pars)

    @pyaedt_function_handler()
    def add_report_from_folder(self, input_folder, design_name, group_plots=False, project=None):
        """Add multiple reports from a folder.

        Parameters
        ----------
        input_folder : str or :class:`pathlib.Path`
            Full path to the folder containing configuration files.
        design_name : str
            Name of design to apply the configuration.
        group_plots : bool
            Whether to group plot traces or not.
        """
        input_reports = search_files(input_folder, "*.json")
        for input_report in input_reports:
            conf = read_configuration_file(input_report)
            if "limitLines" in conf and conf["limitLines"] or "eye_mask" in conf:
                pass_fail = True
            else:
                pass_fail = False
            expr = list(conf["expressions"].keys()) if conf.get("expressions", []) else []
            rep_type = conf.get("report_category", "frequency").lower()
            name = conf.get("plot_name", generate_unique_name("Report"))
            self.add_report(
                design_name,
                str(input_report),
                traces=expr,
                report_type=rep_type,
                pass_fail=pass_fail,
                group_plots=group_plots,
                name=name,
                project=project,
            )

    @pyaedt_function_handler()
    def save_configuration(self, output_file):
        """Save the configuration to a json file.

        Parameters
        ----------
        output_file : str or :class:`pathlib.Path`
            Full path of the output file.

        Returns
        -------
        bool
            ``True`` if export is successful, ``False`` if not.
        """
        return write_configuration_file(self.config, output_file)


class VirtualComplianceChaptersData(PyAedtBase):
    def __init__(self, title):
        self.title = title
        self.content = []

    def add_content(self, content, content_type=0) -> dict:
        """Add content to the chapter.

        Parameters
        ----------
        content : dict
            Data to be added.
        content_type : int, optional
            Content type. 0 is subchapter, 1 is text, 2 is image, 3 is table, 4 is section.
        """
        self.content.append({"type": content_type, "data": content})
        return self.content[-1]

    def add_section(self) -> dict:
        """Add a section to the chapter."""
        self.add_content("", 4)

    def add_subchapter(self, text) -> dict:
        """Add a subchapter to the chapter."""
        return self.add_content(text, 0)

    def add_text(self, text) -> dict:
        """Add text to the chapter."""
        return self.add_content(text, 1)

    def add_image(self, image_data) -> dict:
        """Add image to the chapter."""
        return self.add_content(image_data, 2)

    def add_table(self, table_data) -> dict:
        """Add table to the chapter."""
        return self.add_content(table_data, 3)


class VirtualComplianceData(PyAedtBase):
    """Virtual compliance data class."""

    def __init__(self):
        self._chapters = []

    @property
    def chapters(self) -> List[VirtualComplianceChaptersData]:
        """Chapters list.

        Returns
        -------
        list[:class:`ansys.aedt.core.visualization.post.compliance.VirtualComplianceChaptersData`]
        """
        return self._chapters

    @chapters.setter
    def chapters(self, val):
        self._chapters = val

    def add_chapter(self, chapter, position=None) -> VirtualComplianceChaptersData:
        """Add a new chapter to the compliance data.

        Returns
        -------
        :class:`ansys.aedt.core.visualization.post.compliance.VirtualComplianceChaptersData`
        """
        if position is None:
            self.chapters.append(VirtualComplianceChaptersData(chapter))
            return self.chapters[-1]
        else:
            self.chapters.insert(position, VirtualComplianceChaptersData(chapter))
            return self.chapters[position]


class VirtualCompliance(PyAedtBase):
    """Provides automatic report generation with pass/fail criteria on virtual compliance.

    Parameters
    ----------
    desktop : :class:``ansys.aedt.core.desktop.Desktop``
        Desktop object.
    template : str or :class:`pathlib.Path`
        Full path to the template. Supported formats are JSON and TOML.

    """

    def __init__(self, desktop, template):
        self._add_project_info = True
        self._add_specs_info = False
        self._specs_folder = None
        self._use_portrait = True
        self._template = template
        self._template_name = "Compliance"
        self._template_folder = Path(template).parent
        self._project_file = None
        self._reports = {}
        self._reports_parameters = {}
        self._parameters = {}
        self._project_name = None
        self._output_folder = None
        self._parse_template()
        self._desktop_class = desktop
        self._dut = None
        self._summary = [["Test", "Results"]]
        self._summary_font = [["", None]]
        self.report_data = VirtualComplianceData()
        self.revision = "1.0"
        self._image_width = 800
        self._image_height = 450

    @property
    def image_width(self):
        """Image width resolution during export."""
        return self._image_width

    @image_width.setter
    def image_width(self, val):
        self._image_width = val

    @property
    def image_height(self):
        """Image height resolution during export."""
        return self._image_height

    @image_height.setter
    def image_height(self, val):
        self._image_height = val

    @property
    def dut_image(self):
        """DUT image.

        Returns
        -------
        str
        """
        return self._dut

    @dut_image.setter
    def dut_image(self, val):
        self._dut = val

    @pyaedt_function_handler()
    @pyaedt_function_handler()
    def load_project(self):
        """Open the aedt project in Electronics Desktop.

        Returns
        -------
        bool
        """
        if not self._project_file:
            self._desktop_class.logger.error("Project path has not been provided.")
            return False
        self._desktop_class.load_project(self._project_file)
        project = self._desktop_class.active_project()
        self._project_name = project.GetName()
        self._output_folder = os.path.join(
            project.GetPath(), self._project_name + ".pyaedt", generate_unique_name(self._template_name)
        )
        os.makedirs(self._output_folder, exist_ok=True)
        return True

    @property
    def reports(self):
        """Reports available in the virtual compliance.

        Returns
        -------
        dict[str, :class:`ansys.aedt.core.generic.compliance.ReportTemplate`]
        """
        return self._reports

    @reports.setter
    def reports(self, val):
        self._reports = val

    @property
    def parameters(self):
        """Parameters available in the Virtual compliance.

        Returns
        -------
        dict[str, :class:`ansys.aedt.core.generic.compliance.ParametersTemplate`]
        """
        return self._parameters

    @parameters.setter
    def parameters(self, val):
        self._parameters = val

    @property
    def add_project_info(self):
        """Add project information."""
        return self._add_project_info

    @add_project_info.setter
    def add_project_info(self, val):
        self._add_project_info = val

    @property
    def add_specs_info(self):
        """Add specification information."""
        return self._add_specs_info

    @add_specs_info.setter
    def add_specs_info(self, val):
        self._add_specs_info = val

    @property
    def specs_folder(self):
        """Add specification folder."""
        return self._specs_folder

    @specs_folder.setter
    def specs_folder(self, val):
        self._specs_folder = val
        if self._specs_folder and os.path.exists(os.path.join(self._template_folder, self._specs_folder)):
            self._specs_folder = os.path.join(self._template_folder, self._specs_folder)

    @property
    def template_name(self):
        """Template name."""
        return self._template_name

    @template_name.setter
    def template_name(self, val):
        self._template_name = val

    @property
    def project_file(self):
        """Project file."""
        return self._project_file

    @project_file.setter
    def project_file(self, val):
        self._project_file = val

    @property
    def project_name(self):
        """Project name."""
        return Path(self.project_file).stem

    @property
    def use_portrait(self):
        """Use portrait."""
        return self._use_portrait

    @use_portrait.setter
    def use_portrait(self, val):
        self._use_portrait = val

    @pyaedt_function_handler()
    def _parse_template(self):
        if self._template:
            self.local_config = read_configuration_file(self._template)
            if "general" in self.local_config:
                self._add_project_info = self.local_config["general"].get("add_project_info", True)
                self._add_specs_info = self.local_config["general"].get("add_specs_info", False)
                self._specs_folder = self.local_config["general"].get("specs_folder", "")
                self._template_name = self.local_config["general"].get("name", "Compliance")
                self._project_file = self.local_config["general"].get("project", None)
                self._use_portrait = self.local_config["general"].get("use_portrait", True)
            if "reports" in self.local_config:
                for report in self.local_config["reports"]:
                    self._parse_reports(report)
            if "report_derived_parameters" in self.local_config:
                for report in self.local_config["report_derived_parameters"]:
                    self._parse_reports(report, is_report_parameters=True)

            if "parameters" in self.local_config:
                for parameter in self.local_config["parameters"]:
                    self._parse_reports(parameter, True)

    @pyaedt_function_handler()
    def _parse_reports(self, report, is_parameter=False, is_report_parameters=False):
        name = report["name"]

        if name in self._reports.values():
            self._desktop_class.logger.warning(f"{name} already exists. The name must be unique.")
        else:
            if is_parameter:
                self._parameters[report["name"]] = ParametersTemplate(report)
            elif is_report_parameters:
                self._reports_parameters[report["name"]] = ReportParametersTemplate(report)
            else:
                self._reports[report["name"]] = ReportTemplate(report)

    @pyaedt_function_handler()
    def _get_frequency_range(self, data_list, f1, f2):
        indices = np.where((f1 <= data_list[0]) & (data_list[0] <= f2))
        x_range = data_list[0][indices]
        y_range = data_list[1][indices]
        return x_range, y_range

    @pyaedt_function_handler()
    def _check_test_value(self, filtered_range, test_value, hatch_above):
        worst = 1e9
        worst_f = 0
        val = None
        for filt, t in zip(filtered_range, test_value):
            if hatch_above:
                if t - filt[1] < worst:
                    worst = t - filt[1]
                    worst_f = filt[0]
                    val = filt[1]
            else:
                if filt[1] - t < worst:
                    worst = filt[1] - t
                    worst_f = filt[0]
                    val = filt[1]
        if worst < 0:
            result = "FAIL"
        else:
            result = "PASS"
        return round(val, 5), round(worst_f, 5), result

    @pyaedt_function_handler()
    def add_aedt_report(
        self,
        name,
        report_type,
        config_file,
        design_name,
        traces,
        setup_name=None,
        pass_fail=True,
        pass_fail_criteria=None,
    ):
        """Add a new custom aedt report to the compliance.

        Parameters
        ----------
        name : str
            Name of the report.
        report_type : str
            Report type. Options are "contour eye diagram", "eye diagram", "frequency", "statistical eye", and "time".
        config_file : str
            Path to the config file.
        design_name : str
            Name of the AEDT design to be used to create the project.
        traces : list
           Traces to be added.
        setup_name : str, optional
            Name of the setup to use. If None, the nominal sweep will be used.
        pass_fail : bool, optional
            Whether if the pass/fail criteria has to be used to check the compliance or not.
        pass_fail_criteria : float, string, dict, optional
            Pass/fail criteria to be used. If None, no criteria will be used.

        Returns
        -------

        """
        new_rep = {
            "name": name,
            "type": report_type,
            "config": config_file,
            "design_name": design_name,
            "traces": traces,
            "setup_name": setup_name,
            "pass_fail": pass_fail,
            "pass_fail_criteria": "" if pass_fail_criteria is None else pass_fail_criteria,
        }
        self._reports[name] = ReportTemplate(new_rep)

    @pyaedt_function_handler()
    def _get_sweep_name(self, design, solution_name):
        sweep_name = None
        if solution_name:
            solution_names = [
                i for i in design.existing_analysis_sweeps if solution_name == i or i.startswith(solution_name + " ")
            ]
            if solution_names:  # pragma: no cover
                sweep_name = solution_names[0]
        return sweep_name

    def _add_skew(self, _design, aedt_report, chapter, name, pass_fail_criteria):
        _design.logger.info("Adding single lines violations")
        font_table = [["", None]]
        trace_data = aedt_report.get_solution_data()
        pass_fail_table = [
            [
                "Trace Name",
                "Crossing Point",
                "Skew",
                "Limit value",
                "Test Result",
            ]
        ]
        if not trace_data:  # pragma: no cover
            msg = "Failed to get solution data. Check if the design is solved or if the report data is correct."
            self._desktop_class.logger.error(msg)
        else:
            units = trace_data.units_sweeps["Time"]
            pass_fail_table = [
                [
                    "Trace Name",
                    f"Crossing Point ({units})",
                    f"Skew ({units})",
                    f"Limit value ({units})",
                    "Test Result",
                ]
            ]
            reference_value = 1e12
            for trace_name in trace_data.expressions:
                time_vals, value = trace_data.get_expression_data(trace_name, formula="real")
                center = (np.max(value) + np.min(value)) / 2
                line_name = aedt_report.add_cartesian_y_marker(f"{center}{list(trace_data.units_data.values())[0]}")
                _design.oreportsetup.ChangeProperty(
                    [
                        "NAME:AllTabs",
                        [
                            "NAME:Y Marker",
                            ["NAME:PropServers", f"{aedt_report.plot_name}:{line_name}"],
                            [
                                "NAME:ChangedProps",
                                ["NAME:Line Color", "R:=", 255, "G:=", 255, "B:=", 0],
                                ["NAME:Line Width", "Value:=", "4"],
                            ],
                        ],
                    ]
                )
                neg_indices = np.where(value < center)[0]
                pos_indices = np.where(value > center)[0]

                if not (np.any(neg_indices) and np.any(pos_indices)):
                    settings.logger.warning("Error identifying transition to zero.")
                    continue
                if pos_indices[0] < neg_indices[0]:
                    value = value[pos_indices[0] : neg_indices[0] - pos_indices[0] + 5]
                    time_vals = time_vals[pos_indices[0] : neg_indices[0] - pos_indices[0] + 5]
                else:
                    value = value[neg_indices[0] : pos_indices[0] - neg_indices[0] + 5]
                    time_vals = time_vals[neg_indices[0] : pos_indices[0] - neg_indices[0] + 5]
                result = round(np.interp(center, value, time_vals), 6)
                test_result = "PASS"
                if reference_value == 1e12:
                    reference_value = result
                    test_result = " "
                skew = abs(result - reference_value)
                if skew > pass_fail_criteria:
                    test_result = "FAIL"
                pass_fail_table.append(
                    [trace_name, f"{result:.3f}", " " if skew == 0 else f"{skew:.5f}", pass_fail_criteria, test_result]
                )
                font_table.append([[255, 255, 255], [255, 0, 0]] if test_result == "FAIL" else ["", None])

        chapter.add_table(
            {
                "title": f"Pass Fail Criteria on {name}",
                "content": pass_fail_table,
                "formatting": font_table,
                "col_widths": [45 if self.use_portrait else 150, 30, 30, 30, 30],
            }
        )
        failed = "COMPLIANCE PASSED"
        if pass_fail_table:
            for i in pass_fail_table:
                if i[-1] == "FAIL":
                    failed = "COMPLIANCE FAILED"
                    break
        self._summary.append([name, failed])
        self._summary_font.append([[255, 255, 255], [255, 0, 0]] if "FAIL" in failed else ["", None])
        write_csv(os.path.join(self._output_folder, f"{name}_pass_fail.csv"), pass_fail_table)
        return True

    @pyaedt_function_handler()
    def _create_derived_reports(self):
        _design = None
        if not self._reports_parameters:
            return
        compliance_reports = self.report_data.add_chapter("Report Derived Parameters Results")
        for tpx, template_report in enumerate(self._reports_parameters.values()):
            if self._desktop_class:
                time.sleep(1)
                self._desktop_class.odesktop.CloseAllWindows()
            settings.logger.info(f"Adding report {template_report.name}.")
            config_file = template_report.config_file
            if not os.path.exists(config_file) and not os.path.exists(os.path.join(self._template_folder, config_file)):
                self._desktop_class.logger.error(f"{config_file} is not found.")
                continue
            name = template_report.name
            traces = template_report.traces
            pass_fail = template_report.pass_fail
            design_name = template_report.design_name
            report_type = template_report.report_type
            if template_report.project_name:
                if template_report.project_name not in self._desktop_class.project_list:
                    self._desktop_class.load_project(template_report.project)
            else:
                template_report.project_name = self._project_name
            if _design and _design.design_name != design_name or _design is None:
                try:
                    _design = get_pyaedt_app(template_report.project_name, design_name)
                    self._desktop_class.odesktop.CloseAllWindows()
                except Exception:  # pragma: no cover
                    self._desktop_class.logger.error(f"Failed to retrieve design {design_name}")
                    continue
            if os.path.exists(os.path.join(self._template_folder, config_file)):
                config_file = os.path.join(self._template_folder, config_file)
            if not os.path.exists(config_file):
                continue
            local_config = read_configuration_file(config_file)
            new_dict = {}
            idx = 0
            for trace in traces:
                if local_config.get("expressions", {}):
                    if isinstance(local_config["expressions"], dict):
                        if trace in local_config["expressions"]:
                            new_dict[trace] = local_config["expressions"][trace]
                        elif len(local_config["expressions"]) > idx:
                            new_dict[trace] = list(local_config["expressions"].values())[idx]
                        else:
                            new_dict[trace] = {}
                idx += 1
            local_config["expressions"] = new_dict
            sw_name = self._get_sweep_name(_design, local_config.get("solution_name", None))
            _design.logger.info(f"Creating report {name}")
            aedt_report = _design.post.create_report_from_configuration(
                report_settings=local_config, solution_name=sw_name
            )
            if not aedt_report or not aedt_report.traces:  # pragma: no cover
                _design.logger.error(f"Failed to create report {name}")
                self._summary.append([template_report.name, "FAILED TO CREATE THE REPORT"])
                self._summary_font.append([[255, 255, 255], [255, 0, 0]])
                continue
            aedt_report.hide_legend()

            time.sleep(1)
            if tpx > 0:
                compliance_reports.add_section()
            compliance_reports.add_subchapter(f"{name}")
            if pass_fail and template_report.parameter_name:
                if template_report.parameter_name == "skew":
                    self._add_skew(
                        _design,
                        aedt_report,
                        compliance_reports,
                        template_report.name,
                        template_report.pass_fail_criteria,
                    )
            else:
                self._summary.append([template_report.name, "NO PASS/FAIL"])
                self._summary_font.append(["", None])
            out = _design.post.export_report_to_jpg(
                self._output_folder, aedt_report.plot_name, width=self.image_width, height=self.image_height
            )
            if out:
                compliance_reports.add_image(
                    {
                        "path": os.path.join(self._output_folder, aedt_report.plot_name + ".jpg"),
                        "caption": f"Plot {report_type} for {name}",
                    }
                )
            if self.local_config["general"].get("delete_after_export", True):
                aedt_report.delete()
            else:
                _design.save_project()
            _design.logger.info(f"Successfully parsed report {name}")
            settings.logger.info(f"Report {template_report.name} added to the pdf.")

    @pyaedt_function_handler()
    def _create_aedt_reports(self):
        _design = None
        if not self._reports:
            return False
        compliance_reports = self.report_data.add_chapter("Compliance Results")
        for tpx, template_report in enumerate(self._reports.values()):
            if self._desktop_class:
                time.sleep(1)
                self._desktop_class.odesktop.CloseAllWindows()
            try:
                settings.logger.info(f"Adding report  {template_report.name}.")
                config_file = template_report.config_file
                if not os.path.exists(config_file) and not os.path.exists(
                    os.path.join(self._template_folder, config_file)
                ):
                    self._desktop_class.logger.error(f"{config_file} is not found.")
                    continue
                name = template_report.name
                traces = template_report.traces
                pass_fail = template_report.pass_fail
                pass_fail_criteria = template_report.pass_fail_criteria
                design_name = template_report.design_name
                report_type = template_report.report_type
                group = template_report.group_plots
                if template_report.project_name:
                    if template_report.project_name not in self._desktop_class.project_list:
                        self._desktop_class.load_project(template_report.project)
                else:
                    template_report.project_name = self._project_name
                if _design and _design.design_name != design_name or _design is None:
                    try:
                        _design = get_pyaedt_app(template_report.project_name, design_name)
                        self._desktop_class.odesktop.CloseAllWindows()
                    except Exception:  # pragma: no cover
                        self._desktop_class.logger.error(f"Failed to retrieve design {design_name}")
                        continue
                if os.path.exists(os.path.join(self._template_folder, config_file)):
                    config_file = os.path.join(self._template_folder, config_file)
                if not os.path.exists(config_file):
                    continue
                local_config = read_configuration_file(config_file)
                if pass_fail and not pass_fail_criteria:
                    if report_type in ["standard", "frequency", "time"]:
                        pass_fail_criteria = local_config.get("limitLines", None)
                    elif "eye" in report_type:
                        pass_fail_criteria = local_config.get("eye_mask", None)
                elif pass_fail and pass_fail_criteria:
                    if report_type in ["standard", "frequency", "time"]:
                        local_config["limitLines"] = pass_fail_criteria
                    elif "eye" in report_type:
                        local_config["eye_mask"] = pass_fail_criteria
                if group and report_type in ["standard", "frequency", "time"]:
                    new_dict = {}
                    idx = 0
                    for trace in traces:
                        if local_config.get("expressions", {}):
                            if isinstance(local_config["expressions"], dict):
                                if trace in local_config["expressions"]:
                                    new_dict[trace] = local_config["expressions"][trace]
                                elif len(local_config["expressions"]) > idx:
                                    new_dict[trace] = list(local_config["expressions"].values())[idx]
                                else:
                                    new_dict[trace] = {}
                        idx += 1
                    local_config["expressions"] = new_dict
                    image_name = name
                    sw_name = self._get_sweep_name(_design, local_config.get("solution_name", None))
                    _design.logger.info(f"Creating report {name}")
                    aedt_report = _design.post.create_report_from_configuration(
                        report_settings=local_config, solution_name=sw_name
                    )
                    if not aedt_report or not aedt_report.traces:  # pragma: no cover
                        _design.logger.error(f"Failed to create report {name}")
                        self._summary.append([template_report.name, "FAILED TO CREATE THE REPORT"])
                        self._summary_font.append([[255, 255, 255], [255, 0, 0]])

                        continue
                    aedt_report.hide_legend()

                    time.sleep(1)
                    out = _design.post.export_report_to_jpg(
                        self._output_folder, aedt_report.plot_name, width=self.image_width, height=self.image_height
                    )
                    if tpx > 0:
                        compliance_reports.add_section()
                    compliance_reports.add_subchapter(f"{name}")

                    if (
                        pass_fail and pass_fail_criteria and report_type in ["standard", "frequency", "time"]
                    ):  # pragma: no cover
                        _design.logger.info("Checking lines violations")
                        table = self._add_lna_violations(
                            aedt_report, compliance_reports, image_name, pass_fail_criteria
                        )
                        failed = "COMPLIANCE PASSED"
                        if table:
                            for i in table:
                                if i[-1] == "FAIL":
                                    failed = "COMPLIANCE FAILED"
                                    break
                        self._summary.append([template_report.name, failed])
                        self._summary_font.append([[255, 255, 255], [255, 0, 0]] if "FAIL" in failed else ["", None])

                        write_csv(os.path.join(self._output_folder, f"{name}_pass_fail.csv"), table)
                    else:
                        self._summary.append([template_report.name, "NO PASS/FAIL"])
                        self._summary_font.append(["", None])

                    if out:
                        compliance_reports.add_image(
                            {
                                "path": os.path.join(self._output_folder, aedt_report.plot_name + ".jpg"),
                                "caption": f"Plot {report_type} for {name}",
                            }
                        )

                    if self.local_config["general"].get("delete_after_export", True):
                        aedt_report.delete()
                    else:
                        _design.save_project()
                    _design.logger.info(f"Successfully parsed report {name}")
                else:
                    legacy_local_config = copy.deepcopy(local_config)
                    for tpx1, trace in enumerate(traces):
                        if local_config.get("expressions", {}):
                            if isinstance(local_config["expressions"], dict):
                                if trace in legacy_local_config["expressions"]:
                                    local_config["expressions"] = {trace: legacy_local_config["expressions"][trace]}
                                elif len(legacy_local_config["expressions"]) > 0:
                                    local_config["expressions"] = {
                                        trace: list(legacy_local_config["expressions"].values())[0]
                                    }
                                else:
                                    local_config["expressions"] = {trace: {}}
                        image_name = name + f"_{trace}"
                        sw_name = self._get_sweep_name(_design, local_config.get("solution_name", None))
                        _design.logger.info(f"Creating report {name}")
                        aedt_report = _design.post.create_report_from_configuration(
                            report_settings=local_config, solution_name=sw_name
                        )
                        if not aedt_report or not aedt_report.traces:  # pragma: no cover
                            _design.logger.error(f"Failed to create report {name}")
                            self._summary.append([template_report.name, "FAILED TO CREATE THE REPORT"])
                            self._summary_font.append([[255, 255, 255], [255, 0, 0]])

                            continue
                        if report_type != "contour eye diagram" and "3D" not in local_config["report_type"]:
                            aedt_report.hide_legend()
                        time.sleep(1)
                        out = _design.post.export_report_to_jpg(
                            self._output_folder, aedt_report.plot_name, width=self.image_width, height=self.image_height
                        )
                        time.sleep(1)
                        if out:
                            if tpx + tpx1 > 0:
                                compliance_reports.add_section()
                            compliance_reports.add_subchapter(f"{name}")
                            if pass_fail and pass_fail_criteria:
                                table = None
                                if report_type in ["frequency", "time"]:
                                    _design.logger.info("Checking lines violations")
                                    table = self._add_lna_violations(
                                        aedt_report, compliance_reports, image_name, pass_fail_criteria
                                    )
                                elif report_type == "statistical eye":
                                    _design.logger.info("Checking eye violations")
                                    table = self._add_statistical_violations(
                                        aedt_report, compliance_reports, image_name, pass_fail_criteria
                                    )
                                elif report_type == "eye diagram":
                                    _design.logger.info("Checking eye violations")
                                    table = self._add_eye_diagram_violations(
                                        aedt_report, compliance_reports, image_name
                                    )
                                elif report_type == "contour eye diagram":
                                    _design.logger.info("Checking eye violations")
                                    table = self._add_contour_eye_diagram_violations(
                                        aedt_report, compliance_reports, image_name, pass_fail_criteria
                                    )
                                failed = "COMPLIANCE PASSED"
                                if table:
                                    for i in table:
                                        if "FAIL" in i[-1]:
                                            failed = "COMPLIANCE FAILED"
                                            break
                                self._summary.append([template_report.name, failed])
                                self._summary_font.append(
                                    [[255, 255, 255], [255, 0, 0]] if "FAIL" in failed else ["", None]
                                )

                                if table:  # pragma: no cover
                                    write_csv(os.path.join(self._output_folder, f"{name}{trace}_pass_fail.csv"), table)
                                else:
                                    _design.logger.warning(f"Failed to compute violation for chart {name}{trace}")
                            else:
                                self._summary.append([template_report.name, "NO PASS/FAIL"])
                                self._summary_font.append(["", None])
                            compliance_reports.add_image(
                                {
                                    "path": os.path.join(self._output_folder, aedt_report.plot_name + ".jpg"),
                                    "caption": f"Plot {report_type} for {name}",
                                }
                            )
                            if report_type in ["eye diagram", "statistical eye"]:
                                _design.logger.info("Adding eye measurements.")
                                table = self._add_eye_measurement(aedt_report, compliance_reports, image_name)
                                write_csv(
                                    os.path.join(
                                        self._output_folder,
                                        f"{name}{trace}_eye_meas.csv".replace("<", "").replace(">", ""),
                                    ),
                                    table,
                                )
                            if self.local_config["general"].get("delete_after_export", True):
                                aedt_report.delete()
                            else:
                                _design.save_project()
                            _design.logger.info(f"Successfully parsed report {name} for trace {trace}")

                        else:  # pragma: no cover
                            msg = f"Failed to create the report. Check {config_file} configuration file."
                            self._desktop_class.logger.error(msg)
                settings.logger.info(f"Report {template_report.name} added to the pdf.")
            except Exception:
                settings.logger.error(f"Failed to add {template_report.name} to the pdf.")
                self._summary.append([template_report.name, "Failed to create report"])
                self._summary_font.append([[255, 255, 255], [255, 0, 0]])

    @pyaedt_function_handler()
    def _create_parameters(self):
        start = True
        _design = None

        for templ_name, template_report in self._parameters.items():
            config_file = template_report.config_file
            if not os.path.exists(config_file):
                config_file = os.path.join(self._template_folder, config_file)
            if not os.path.exists(config_file):
                self._desktop_class.logger.error(f"{config_file} not found.")
                continue
            name = template_report.name
            pass_fail = template_report.pass_fail
            pass_fail_criteria = template_report.pass_fail_criteria
            design_name = template_report.design_name
            if _design and _design.design_name != design_name or _design is None:
                _design = get_pyaedt_app(self._project_name, design_name)

            if start:
                parameters = self.report_data.add_chapter("Parameters Results")
                start = False
            spisim = SpiSim(None)
            if name == "erl":
                parameters.add_subchapter(f"Effective Return Loss: {templ_name}")
                table_out = [["ERL", "Value", "Criteria", "Pass/Fail"]]
                font_table = [["", None]]

                traces = template_report.traces
                trace_pins = template_report.trace_pins
                for trace_name, trace_pin in zip(traces, trace_pins):
                    spisim.touchstone_file = _design.export_touchstone()
                    if not isinstance(trace_pin[0], int):
                        try:
                            ports = list(_design.excitation_names)
                            thrus4p = [ports.index(i) + 1 for i in trace_pin]
                            trace_pin = thrus4p
                        except IndexError:
                            _design.logger.error("Port not found.")
                    erl_value = spisim.compute_erl(specify_through_ports=trace_pin, config_file=config_file)
                    if erl_value:
                        if pass_fail:
                            try:
                                failed = True if float(erl_value) > float(pass_fail_criteria) else False
                            except ValueError:
                                failed = True
                            table_out.append(
                                [trace_name, erl_value, pass_fail_criteria, "PASS" if not failed else "FAIL"]
                            )
                            self._summary.append(
                                ["Effective Return Loss", "COMPLIANCE PASSED" if not failed else "COMPLIANCE FAILED"]
                            )

                            self._summary_font.append([[255, 255, 255], [255, 0, 0]] if failed else ["", None])
                            font_table.append([[255, 255, 255], [255, 0, 0]] if failed else ["", None])

                        else:
                            table_out.append([trace_name, erl_value, "NA", "PASS"])
                            self._summary.append(["Effective Return Loss", "COMPLIANCE PASSED"])
                            self._summary_font.append(["", None])
                            font_table.append(["", None])

                    else:
                        table_out.append(
                            [
                                trace_name,
                                "Failed to Compute",
                                pass_fail_criteria if pass_fail else "NA",
                                "PASS" if not failed else "FAIL",
                            ]
                        )

                        self._summary.append(["Effective Return Loss", "Failed to compute ERL."])
                        self._summary_font.append([[255, 255, 255], [255, 0, 0]])
                        font_table.append([[255, 255, 255], [255, 0, 0]])

                parameters.add_table(
                    {"title": "Effective Return Losses", "content": table_out, "formatting": font_table}
                )
            settings.logger.info(f"Parameters {template_report.name} added to the report.")

    @staticmethod
    def points_in_polygon(points, polygon):
        path = Path(polygon)
        return path.contains_points(points)

    @pyaedt_function_handler()
    def _add_statistical_violations(self, report, chapter, image_name, pass_fail_criteria):
        font_table = [["", None]]
        pass_fail_table = [["Pass Fail Criteria", "Test Result"]]
        sols = report.get_solution_data()
        if not sols:  # pragma: no cover
            msg = "Failed to get Solution Data. Check if the design is solved or the report data are correct."
            self._desktop_class.logger.error(msg)
            return
        mag_data_in = sols.get_expression_data(
            sols.expressions[0], formula="magnitude", sweeps=["__UnitInterval", "__Amplitude"]
        )
        filter_in = np.where(mag_data_in[1] > 0)
        x_data = mag_data_in[0][filter_in]

        # mag_data is a dictionary. The key isa tuple (__Amplitude, __UnitInterval), and the value is the eye value.
        mystr = "Eye Mask Violation:"
        result_value = "PASS"
        points_to_check = [[i[0] for i in pass_fail_criteria["points"]], [i[1] for i in pass_fail_criteria["points"]]]
        points_to_check[1] = unit_converter(
            points_to_check[1],
            unit_system="Voltage",
            input_units=pass_fail_criteria.get("yunits", "V"),
            output_units=sols.units_sweeps["__Amplitude"],
        )

        poly = np.array(points_to_check).T

        mask = self.points_in_polygon(x_data, poly)
        inside_points = x_data[np.where(mask)]
        num_failed = len(inside_points)
        output_array = np.empty((0, 3))
        if num_failed > 0:
            result_value = "FAIL"
            text_column = np.full((inside_points.shape[0], 1), "EYE")
            output_array = np.hstack((inside_points, text_column))

        font_table.append([[255, 255, 255], [255, 0, 0]] if result_value == "FAIL" else ["", None])
        if result_value == "FAIL":
            result_value = f"FAIL on {num_failed} points."
        pass_fail_table.append([mystr, result_value])
        result_value = "PASS"
        if pass_fail_criteria["enable_limits"]:
            mystr = "Upper/Lower Mask Violation:"
            upper_limit = unit_converter(
                pass_fail_criteria.get("upper_limit", 1e12),
                unit_system="Voltage",
                input_units=pass_fail_criteria.get("yunits", "V"),
                output_units=sols.units_sweeps["__Amplitude"],
            )
            lower_limit = unit_converter(
                pass_fail_criteria.get("lower_limit", -1e12),
                unit_system="Voltage",
                input_units=pass_fail_criteria.get("yunits", "V"),
                output_units=sols.units_sweeps["__Amplitude"],
            )
            # checking if amplitude is overcoming limits.
            upper_violations = x_data[x_data[:, 1] > upper_limit]
            lower_violations = x_data[x_data[:, 1] < lower_limit]
            if len(upper_violations) > 0:
                result_value = "FAIL"
                text_column = np.full((upper_violations.shape[0], 1), "UPPER")
                upper_violations = np.hstack((upper_violations, text_column))
                output_array = np.vstack((output_array, upper_violations))
            if len(lower_violations) > 0:
                result_value = "FAIL"
                text_column = np.full((lower_violations.shape[0], 1), "LOWER")
                lower_violations = np.hstack((lower_violations, text_column))
                output_array = np.vstack((output_array, lower_violations))
            if len(output_array) > 0:
                unit = sols.units_sweeps["__Amplitude"]
                header = f"Value{unit},Unit Interval,Violation"
                file_path = os.path.join(self._output_folder, f"{image_name}_statistical_eye_violations.csv")
                np.savetxt(
                    file_path,
                    output_array,
                    delimiter=",",
                    header=header,
                    comments="",
                    fmt=("%s", "%s", "%s"),
                )
            font_table.append([[255, 255, 255], [255, 0, 0]] if result_value == "FAIL" else ["", None])
            pass_fail_table.append([mystr, result_value])
        chapter.add_table(
            {"title": f"Pass Fail Criteria on {image_name}", "content": pass_fail_table, "formatting": font_table}
        )
        return pass_fail_table

    @pyaedt_function_handler()
    def _add_contour_eye_diagram_violations(self, report, chapter, image_name, pass_fail_criteria):
        pass_fail_table = [["Pass Fail Criteria", "Test Result"]]
        sols = report.get_solution_data()
        if not sols:  # pragma: no cover
            msg = "Failed to get Solution Data. Check if the design is solved or the report data are correct."
            self._desktop_class.logger.error(msg)
            return
        bit_error_rates = [1e-3, 1e-6, 1e-9, 1e-12]
        font_table = [["", None]]
        points_to_check = [[i[0] for i in pass_fail_criteria["points"]], [i[1] for i in pass_fail_criteria["points"]]]
        points_to_check[1] = unit_converter(
            points_to_check[1],
            unit_system="Voltage",
            input_units=pass_fail_criteria.get("yunits", "V"),
            output_units=sols.units_sweeps["__Amplitude"],
        )
        for ber in bit_error_rates:
            mag_data_in = sols.get_expression_data(sols.expressions[0], sweeps=["__UnitInterval", "__Amplitude"])
            filter_in = np.where(mag_data_in[1] <= ber)
            x_data = mag_data_in[0][filter_in]

            mystr = f"Eye Mask Violation BER at {ber}:"
            result_value = "PASS"
            if not np.any(x_data):
                min_ber = np.min(mag_data_in[1])
                result_value = f"FAILED. Minimum available BER  is {min_ber}"
            else:
                poly = np.array(points_to_check).T
                mask = self.points_in_polygon(x_data, poly)
                inside_points = x_data[np.where(mask)]
                num_failed = len(inside_points)
                if num_failed > 0:
                    result_value = "FAILED. Mask Violation"
            font_table.append([[255, 255, 255], [255, 0, 0]] if "FAIL" in result_value else ["", None])
            pass_fail_table.append([mystr, result_value])

        chapter.add_table(
            {"title": f"Pass Fail Criteria on {image_name}", "content": pass_fail_table, "formatting": font_table}
        )
        return pass_fail_table

    @pyaedt_function_handler()
    def _add_lna_violations(self, report, chapter, image_name, pass_fail_criteria):
        font_table = [["", None]]
        trace_data = report.get_solution_data()
        pass_fail_table = [
            [
                "Check Zone",
                "Trace Name",
                "Criteria",
                "Limit value",
                "Worst freq.",
                "Worst value",
                "Test Result",
            ]
        ]
        if not trace_data:  # pragma: no cover
            msg = "Failed to get solution data. Check if the design is solved or if the report data is correct."
            self._desktop_class.logger.error(msg)
            return pass_fail_table
        for trace_name in trace_data.expressions:
            trace_values = trace_data.get_expression_data(trace_name)
            for limit_name, limit_v in pass_fail_criteria.items():
                yy = 0
                zones = 0
                if trace_data.primary_sweep == "Freq":
                    default = "Hz"
                else:
                    default = "s"
                default = default if limit_v.get("xunits", "") == "" else limit_v["xunits"]
                limit_x = unit_converter(
                    values=limit_v["xpoints"],
                    unit_system=trace_data.primary_sweep,
                    input_units=default,
                    output_units=trace_data.units_sweeps[trace_data.primary_sweep],
                )
                while yy < len(limit_x) - 1:
                    if limit_x[yy] != limit_x[yy + 1]:
                        zones += 1
                        freq, interpolated_values = self._get_frequency_range(
                            trace_values, limit_x[yy], limit_x[yy + 1]
                        )
                        if not np.any(freq):
                            yy += 1
                            continue
                        hatch_above = False
                        if limit_v.get("hatch_above", True):
                            hatch_above = True

                        test_value = limit_v["ypoints"][yy]
                        indices = (
                            np.where(interpolated_values > test_value)
                            if hatch_above
                            else np.where(interpolated_values < test_value)
                        )
                        result_y = interpolated_values[indices]
                        result_value = "FAIL" if np.any(result_y) else "PASS"

                        worst_index = np.argmax(interpolated_values) if hatch_above else np.argmin(interpolated_values)
                        x_value_worst = round(freq[worst_index], 5)
                        y_value_worst = round(interpolated_values[worst_index], 5)
                        units = limit_v.get("yunits", "")
                        mystr = limit_name
                        font_table.append([[255, 255, 255], [255, 0, 0]] if result_value == "FAIL" else ["", None])
                        criteria = "Upper Limit:" if hatch_above else "Lower Limit:"
                        criteria = criteria + f"{limit_x[yy]}-{limit_x[yy + 1]}{default}"
                        pass_fail_table.append(
                            [
                                mystr,
                                trace_name,
                                criteria,
                                f"{test_value}{units}",
                                f"{x_value_worst}{trace_data.units_sweeps[trace_data.primary_sweep]}",
                                f"{y_value_worst}{units}",
                                result_value,
                            ]
                        )
                    yy += 1
        chapter.add_table(
            {
                "title": f"Pass Fail Criteria on {image_name}",
                "content": pass_fail_table,
                "formatting": font_table,
                "col_widths": [23, 45 if self.use_portrait else 165, 50, 23, 23, 23, 23],
            }
        )

        return pass_fail_table

    @pyaedt_function_handler()
    def _add_eye_diagram_violations(self, report, chapter, image_name):
        try:
            out_eye = os.path.join(self._output_folder, "violations.tab")
            viol = report.export_mask_violation(out_eye)
        except Exception:  # pragma: no cover
            viol = None
        font_table = [["", None]]
        pass_fail_table = [["Pass Fail Criteria", "Test Result"]]
        mystr1 = "Eye Mask Violation:"
        result_value_mask = "PASS"
        mystr2 = "Upper/Lower Mask Violation:"
        result_value_upper = "PASS"
        if os.path.exists(viol):
            try:  # pragma: no cover
                import pandas as pd
            except ImportError:  # pragma: no cover
                return
            file_in = pd.read_table(viol, header=0)

            for k in file_in.values:
                if k[3].strip() == "Central":
                    result_value_mask = "FAIL"
                elif k[3].strip() in ["Upper", "Lower"]:
                    result_value_upper = "FAIL"
        pass_fail_table.append([mystr1, result_value_mask])
        font_table.append([[255, 255, 255], [255, 0, 0]] if result_value_mask == "FAIL" else ["", None])
        pass_fail_table.append([mystr2, result_value_upper])
        font_table.append([[255, 255, 255], [255, 0, 0]] if result_value_upper == "FAIL" else ["", None])
        chapter.add_table(
            {"title": f"Pass Fail Criteria on {image_name}", "content": pass_fail_table, "formatting": font_table}
        )
        return pass_fail_table

    @pyaedt_function_handler()
    def _add_eye_measurement(self, report, chapter, image_name):
        report.add_all_eye_measurements()
        out_eye = os.path.join(self._output_folder, f"eye_measurements_{image_name}.csv")
        report._post.oreportsetup.ExportTableToFile(report.plot_name, out_eye, "Legend")
        report.clear_all_eye_measurements()
        table = read_csv(out_eye)
        new_table = []
        for line in table:
            new_table.append(line)
        chapter.add_table({"title": f"Eye Measurements on {image_name}", "content": new_table})
        return new_table

    @pyaedt_function_handler()
    def add_specs_to_report(self, folder):
        """Add specs to the report from a given folder.

        All images in such folder will be added to the report.

        Parameters
        ----------
        folder : str
            Folder relative path to compliance report or absolute path.
        """
        if folder:
            self._specs_folder = folder
            self._add_specs_info = True

    @pyaedt_function_handler()
    def _create_project_info(self, report):
        report.add_section()
        designs = []
        _design = None
        for template_report in self.reports.values():
            design_name = template_report.design_name
            if design_name in designs:
                continue
            designs.append(design_name)
            if _design and _design.design_name != design_name or _design is None:
                _design = get_pyaedt_app(template_report.project_name, design_name)
            report.add_project_info(_design)

            report.add_empty_line(3)

            if _design.design_type == "Circuit Design":
                if not self._desktop_class.non_graphical:
                    for page in range(1, _design.modeler.pages + 1):
                        name = os.path.join(self._output_folder, f"{_design.design_name}_{page}.jpg")
                        image = _design.post.export_model_picture(name, page)
                        if os.path.exists(image):
                            report.add_image(image, caption=f"Schematic {_design.design_name}, page {page}.")
                components = [["Reference Designator", "Parameters"]]
                for element in _design.modeler.components.components.values():
                    if "refdes" in dir(element):
                        pars = []
                        for el, val in element.parameters.items():
                            if el in self.local_config.get("project_info_keys", default_keys) and el not in [
                                "DefaultNetlist",
                                "CoSimulator",
                                "NexximNetList",
                                "CosimDefinition",
                            ]:
                                pars.append(f"{el}={val}")
                        if pars:
                            components.append([element.refdes, ", ".join(pars)])
                if len(components) > 1:
                    report.add_sub_chapter(f"Design Information: {_design.design_name}")
                    report.add_table("Components", components, col_widths=[75, 275])

    @pyaedt_function_handler()
    def create_compliance_report(self, file_name="compliance_test.pdf", close_project=True):
        """Create the Virtual Compliance report.

        Parameters
        ----------
        file_name : str
            Output file name.
        close_project : bool, optional
            Whether to close the project at the end of the report generation or not. Default is `True`.

        Returns
        -------
        str
            Path to the output file.
        """
        self.compute_report_data()
        return self.create_pdf(file_name=file_name, close_project=close_project)

    def compute_report_data(self) -> VirtualComplianceData:
        """Compute the report data and exports all the images and table without creating the pdf."""
        self.report_data = VirtualComplianceData()
        if not self._project_name:
            self.load_project()

        if self._specs_folder and self._add_specs_info:
            specs = self.report_data.add_chapter("Specifications Info")
            file_list = search_files(
                self._specs_folder,
            )
            for file in file_list:
                if os.path.splitext(file)[1] in [".jpg", ".png", ".gif"]:
                    # noinspection PyBroadException
                    try:
                        caption = " ".join(os.path.splitext(os.path.split(file)[-1])[0].split("_"))
                    except Exception:  # pragma: no cover
                        caption = os.path.split(file)[-1]
                    specs.add_image({"path": file, "caption": caption})
            settings.logger.info("Specifications info added to the report.")
        if self.dut_image:
            dut = self.report_data.add_chapter("Device under test")
            caption = "DUT drawing with victims and aggressors."
            dut.add_image({"path": self.dut_image, "caption": caption})

        self._create_parameters()
        self._create_derived_reports()
        self._create_aedt_reports()
        if len(self._summary) > 1:
            summary = self.report_data.add_chapter("Summary", 0)
            failed_tests = 0
            for sum_el in self._summary:
                if "COMPLIANCE FAILED" in sum_el[-1]:
                    failed_tests += 1
            if failed_tests > 0:
                summary.add_text("The virtual compliance on the project has failed.")
                summary.add_text(f"There are {failed_tests} failed tests.")
            else:
                summary.add_text("The virtual compliance on the project has successfully passed.")
            summary.add_table(
                {"title": "Simulation Summary", "content": self._summary, "formatting": self._summary_font}
            )
        return self.report_data

    def create_pdf(self, file_name, close_project=True):
        """Create the PDF report after the method ``compute_report_data`` is called.

        Parameters
        ----------
        file_name : str
            Output file name.
        close_project : bool, optional
            Whether to close the project at the end of the report generation or not. Default is `True`.

        Returns
        -------
        str
            Path to the output file.
        """
        if not self.report_data.chapters:
            self.create_compliance_report()
        report = AnsysReport()
        report.aedt_version = self._desktop_class.aedt_version_id
        report.design_name = self._template_name
        report.report_specs.table_font_size = 7
        report.report_specs.revision = f"Revision {self.revision}"
        report.use_portrait = self._use_portrait
        report.create()

        for cpt, chapter in enumerate(self.report_data.chapters):
            if cpt > 0:
                report.add_section()
            report.add_chapter(chapter.title)
            for content in chapter.content:
                if content["type"] == 2:
                    report.add_image_with_aspect_ratio(**content["data"])
                elif content["type"] == 3:
                    y = report.get_y()
                    table_height = report.font_size * 5 * len(content["data"]["content"])
                    if y > report.h / 2 and y + table_height > (report.h - ((report.h - report.eph) / 2)):
                        report.add_page_break()
                    report.add_table(**content["data"])
                elif content["type"] == 1:
                    report.add_text(content["data"])
                elif content["type"] == 0:
                    report.add_sub_chapter(content["data"])
                elif content["type"] == 4:
                    report.add_section()
        if self._add_project_info:
            self._create_project_info(report)
            settings.logger.info("Project info added to the report.")
        report.add_toc()
        output = report.save_pdf(self._output_folder, file_name=file_name)
        if close_project:
            self._desktop_class.odesktop.CloseProject(self.project_name)
        if output:
            self._desktop_class.logger.info(f"Report has been saved in {output}")
        return output
