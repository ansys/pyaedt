import os.path
import time

from pyaedt.generic.design_types import get_pyaedt_app
from pyaedt.generic.filesystem import search_files
from pyaedt.generic.general_methods import generate_unique_name
from pyaedt.generic.general_methods import read_configuration_file
from pyaedt.generic.general_methods import read_csv
from pyaedt.generic.general_methods import write_csv
from pyaedt.generic.pdf import AnsysReport
from pyaedt.modeler.geometry_operators import GeometryOperators

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


class VirtualCompliance:
    """Provides automatic report generation with pass/fail criteria on virtual compliance.

    Parameters
    ----------
    desktop : :class:``pyaedt.desktop.Desktop``
        Desktop object.
    template : str
        Full path to the template. Supported formats are JSON and TOML.
    """

    def __init__(self, desktop, template):
        self._add_project_info = True
        self._add_specs_info = False
        self._specs_folder = None
        self._template = template
        self._template_name = "Compliance"
        self._template_folder = os.path.dirname(template)
        self._reports = {}
        self._parse_template()
        self._desktop_class = desktop
        if self._project_file:
            self._desktop_class.load_project(self._project_file)
        project = self._desktop_class.odesktop.GetActiveProject()
        self._project_name = project.GetName()
        self._output_folder = os.path.join(
            project.GetPath(), self._project_name + ".pyaedt", generate_unique_name(self._template_name)
        )
        os.makedirs(self._output_folder, exist_ok=True)

    def _parse_template(self):
        if self._template:
            self.local_config = read_configuration_file(self._template)
            if "general" in self.local_config:
                self._add_project_info = self.local_config["general"].get("add_project_info", True)
                self._add_specs_info = self.local_config["general"].get("add_specs_info", False)
                self._specs_folder = self.local_config["general"].get("specs_folder", "")
                if self._specs_folder and os.path.exists(os.path.join(self._template_folder, self._specs_folder)):
                    self._specs_folder = os.path.join(self._template_folder, self._specs_folder)
                self._template_name = self.local_config["general"].get("name", "Compliance")
                self._project_file = self.local_config["general"].get("project", None)

    def _parse_reports(self):
        if "reports" in self.local_config:
            for report in self.local_config["reports"]:
                self._create_aedt_report(
                    report["name"],
                    report["type"],
                    report["config"],
                    report["design_name"],
                    report["traces"],
                    report["pass_fail"],
                )

    def _get_frequency_range(self, data_list, f1, f2):
        filtered_range = [(freq, db_value) for freq, db_value in data_list if f1 <= freq <= f2]
        return filtered_range

    def _check_test_value(self, filtered_range, test_value, hatch_above):
        ranges = [k[1] for k in filtered_range]
        if hatch_above:
            value_to_check = max(ranges)
        else:
            value_to_check = min(ranges)
        freq_to_check = filtered_range[ranges.index(value_to_check)][0]
        if hatch_above and value_to_check >= test_value:
            return round(value_to_check, 5), round(freq_to_check, 5), "FAIL"
        elif not hatch_above and value_to_check <= test_value:
            return round(value_to_check, 5), round(freq_to_check, 5), "FAIL"
        return round(value_to_check, 5), round(freq_to_check, 5), "PASS"

    def add_aedt_report(self, name, report_type, config_file, design_name, traces, setup_name=None, pass_fail=True):
        """Add a new custom aedt report to the compliance.

        Parameters
        ----------
        name : str
            Name of the report.
        report_type : str
            Report type. It can be "frequency", "eye diagram", "statistical eye", "contour eye diagram", "transient".
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

        Returns
        -------

        """
        self.local_config.reports.append(
            {
                "name": name,
                "type": report_type,
                "config": config_file,
                "design_name": design_name,
                "traces": traces,
                "setup_name": setup_name,
                "pass_fail": pass_fail,
            }
        )

    def _get_sweep_name(self, design, solution_name):
        sweep_name = None
        if solution_name:
            solution_names = [
                i for i in design.existing_analysis_sweeps if solution_name == i or i.startswith(solution_name + " ")
            ]
            if solution_names:
                sweep_name = solution_names[0]
        return sweep_name

    def _create_aedt_reports(self, pdf_report):
        start = True
        _design = None
        first_trace = True
        for template_report in self.local_config["reports"]:
            config_file = template_report["config"]
            name = template_report["name"]
            traces = template_report["traces"]
            pass_fail = template_report["pass_fail"]
            design_name = template_report["design_name"]
            report_type = template_report["type"]
            group = template_report.get("group_plots", False)
            if _design and _design.design_name != design_name or _design is None:
                _design = get_pyaedt_app(self._project_name, design_name)

            if os.path.exists(os.path.join(self._template_folder, config_file)):
                config_file = os.path.join(self._template_folder, config_file)
            if not os.path.exists(config_file):
                continue
            local_config = read_configuration_file(config_file)
            if start:
                pdf_report.add_section(portrait=False)
                pdf_report.add_chapter("Compliance Results")
                start = False
            if group and report_type in ["frequency", "time"]:
                local_config["expressions"] = {trace: {} for trace in traces}
                image_name = name
                sw_name = self._get_sweep_name(_design, local_config.get("solution_name", None))
                _design.logger.info(f"Creating report {name}")
                aedt_report = _design.post.create_report_from_configuration(
                    input_dict=local_config, solution_name=sw_name
                )
                aedt_report.hide_legend()
                time.sleep(1)
                out = _design.post.export_report_to_jpg(self._output_folder, aedt_report.plot_name)
                time.sleep(1)
                if out:
                    pdf_report.add_sub_chapter(f"{name}")
                    sleep_time = 10
                    while sleep_time > 0:
                        # noinspection PyBroadException
                        try:
                            pdf_report.add_image(
                                os.path.join(self._output_folder, aedt_report.plot_name + ".jpg"),
                                f"Plot {report_type} for {name}",
                                width=pdf_report.epw - 40,
                            )
                            sleep_time = 0
                        except Exception:  # pragma: no cover
                            time.sleep(1)
                            sleep_time -= 1
                    if pass_fail and report_type in ["frequency", "time"] and local_config.get("limitLines", None):
                        _design.logger.info(f"Checking lines violations")
                        table = self._add_lna_violations(aedt_report, pdf_report, image_name, local_config)
                        write_csv(os.path.join(self._output_folder, f"{name}_pass_fail.csv"), table)
                    if self.local_config.get("delete_after_export", True):
                        aedt_report.delete()
                    _design.logger.info(f"Successfully parsed report {name}")
            else:
                for trace in traces:
                    local_config["expressions"] = {trace: {}}
                    image_name = name + f"_{trace}"
                    sw_name = self._get_sweep_name(_design, local_config.get("solution_name", None))
                    _design.logger.info(f"Creating report {name} for trace {trace}")
                    aedt_report = _design.post.create_report_from_configuration(
                        input_dict=local_config, solution_name=sw_name
                    )
                    if report_type != "contour eye diagram":
                        aedt_report.hide_legend()
                    time.sleep(1)
                    out = _design.post.export_report_to_jpg(self._output_folder, aedt_report.plot_name)
                    time.sleep(1)
                    if out:
                        if not first_trace:
                            pdf_report.add_section(portrait=False)
                        else:
                            first_trace = False
                        pdf_report.add_sub_chapter(f"{name} for trace {trace}")
                        sleep_time = 10
                        while sleep_time > 0:
                            # noinspection PyBroadException
                            try:
                                pdf_report.add_image(
                                    os.path.join(self._output_folder, aedt_report.plot_name + ".jpg"),
                                    f"Plot {report_type} for trace {trace}",
                                    width=pdf_report.epw - 40,
                                )
                                sleep_time = 0
                            except Exception:  # pragma: no cover
                                time.sleep(1)
                                sleep_time -= 1
                        if pass_fail:
                            if report_type in ["frequency", "time"] and local_config.get("limitLines", None):
                                _design.logger.info(f"Checking lines violations")
                                table = self._add_lna_violations(aedt_report, pdf_report, image_name, local_config)
                            elif report_type == "statistical eye" and local_config["eye_mask"]:
                                _design.logger.info(f"Checking eye violations")
                                table = self._add_statistical_violations(
                                    aedt_report, pdf_report, image_name, local_config
                                )
                            elif report_type == "eye diagram" and local_config["eye_mask"]:
                                _design.logger.info(f"Checking eye violations")
                                table = self._add_eye_diagram_violations(aedt_report, pdf_report, image_name)
                            elif report_type == "contour eye diagram":
                                _design.logger.info(f"Checking eye violations")
                                table = self._add_contour_eye_diagram_violations(
                                    aedt_report, pdf_report, image_name, local_config
                                )
                            write_csv(os.path.join(self._output_folder, f"{name}{trace}_pass_fail.csv"), table)

                        if report_type in ["eye diagram", "statistical eye"]:
                            _design.logger.info(f"Adding eye measurements")
                            table = self._add_eye_measurement(aedt_report, pdf_report, image_name)
                            write_csv(os.path.join(self._output_folder, f"{name}{trace}_eye_meas.csv"), table)
                        if self.local_config.get("delete_after_export", True):
                            aedt_report.delete()
                        _design.logger.info(f"Successfully parsed report {name} for trace {trace}")

                    else:  # pragma: no cover
                        msg = f"Failed to create the report. Check {config_file} configuration file."
                        self._desktop_class.logger.error(msg)

    def _add_lna_violations(self, report, pdf_report, image_name, local_config):
        font_table = [["", None]]
        trace_data = report.get_solution_data()
        if not trace_data:  # pragma: no cover
            msg = "Failed to get Solution Data. Check if the design is solved or the report data are correct."
            self._desktop_class.logger.error(msg)
            return
        pass_fail_table = [
            [
                "Check Zone",
                "Trace Name",
                "Criteria",
                "Pass/Fail limit value",
                "Worst simulated value",
                "X at worst value",
                "Test Result",
            ]
        ]
        for trace_name in trace_data.expressions:
            trace_values = [(k[0], v) for k, v in trace_data.full_matrix_real_imag[0][trace_name].items()]
            for limit_v in local_config["limitLines"].values():
                yy = 0
                zones = 0
                while yy < len(limit_v["xpoints"]) - 1:
                    if limit_v["xpoints"][yy] != limit_v["xpoints"][yy + 1]:
                        zones += 1
                        result_range = self._get_frequency_range(
                            trace_values, limit_v["xpoints"][yy], limit_v["xpoints"][yy + 1]
                        )
                        hatch_above = False
                        if limit_v.get("hatch_above", True):
                            hatch_above = True
                        test_value = limit_v["ypoints"][yy]
                        range_value, x_value, result_value = self._check_test_value(
                            result_range, test_value, hatch_above
                        )
                        units = limit_v.get("y_units", "")
                        xunits = limit_v.get("x_units", "")
                        mystr = f"Zone  {zones}"
                        font_table.append([None, [255, 0, 0]] if result_value == "FAIL" else ["", None])
                        pass_fail_table.append(
                            [
                                mystr,
                                trace_name,
                                "Upper Limit" if hatch_above else "Lower Limit",
                                f"{test_value}{units}",
                                f"{range_value}{units}",
                                f"{x_value}{xunits}",
                                result_value,
                            ]
                        )
                    yy += 1
        pdf_report.add_section(portrait=True)
        pdf_report.add_table(
            f"Pass Fail Criteria on {image_name}", pass_fail_table, font_table, col_widths=[20, 45, 25, 25, 25, 25, 25]
        )
        return pass_fail_table

    def _add_statistical_violations(self, report, pdf_report, image_name, local_config):
        font_table = [["", None]]
        pass_fail_table = [["Pass Fail Criteria", "Test Result"]]
        sols = report.get_solution_data()
        if not sols:  # pragma: no cover
            msg = "Failed to get Solution Data. Check if the design is solved or the report data are correct."
            self._desktop_class.logger.error(msg)
            return
        mag_data = {i: k for i, k in sols.full_matrix_real_imag[0][sols.expressions[0]].items() if k > 0}
        mystr = "Eye Mask Violation:"
        result_value = "PASS"
        points_to_check = [i[::-1] for i in local_config["eye_mask"]["points"]]
        points_to_check = [[i[0] for i in points_to_check], [i[1] for i in points_to_check]]
        num_failed = 0
        min_x = min(points_to_check[0])
        max_x = max(points_to_check[0])
        min_y = min(points_to_check[1])
        max_y = max(points_to_check[1])
        for point in mag_data:
            if not (min_x < point[0] < max_x and min_y < point[1] < max_y):
                continue
            if GeometryOperators.point_in_polygon(point, points_to_check) >= 0:
                result_value = "FAIL"
                num_failed += 1
                # break
        font_table.append([None, [255, 0, 0]] if result_value == "FAIL" else ["", None])
        if result_value == "FAIL":
            result_value = f"FAIL on {num_failed} points."
        pass_fail_table.append([mystr, result_value])

        if local_config["eye_mask"]["enable_limits"]:
            mystr = "Upper/Lower Mask Violation:"
            for point in mag_data:
                if (
                    point[1] > local_config["eye_mask"]["upper_limit"]
                    or point[1] < local_config["eye_mask"]["lower_limit"]
                ):
                    result_value = "FAIL"
                    break
            font_table.append([None, [255, 0, 0]] if result_value == "FAIL" else ["", None])
            pass_fail_table.append([mystr, result_value])
        pdf_report.add_section(portrait=True)
        pdf_report.add_table(f"Pass Fail Criteria on {image_name}", pass_fail_table, font_table)
        return pass_fail_table

    def _add_eye_diagram_violations(self, report, pdf_report, image_name):
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
        font_table.append([None, [255, 0, 0]] if result_value_mask == "FAIL" else ["", None])
        pass_fail_table.append([mystr2, result_value_upper])
        font_table.append([None, [255, 0, 0]] if result_value_upper == "FAIL" else ["", None])
        pdf_report.add_section(portrait=True)
        pdf_report.add_table(f"Pass Fail Criteria on {image_name}", pass_fail_table, font_table)
        return pass_fail_table

    def _add_contour_eye_diagram_violations(self, report, pdf_report, image_name, local_config):
        pass_fail_table = [["Pass Fail Criteria", "Test Result"]]
        sols = report.get_solution_data()
        if not sols:  # pragma: no cover
            msg = "Failed to get Solution Data. Check if the design is solved or the report data are correct."
            self._desktop_class.logger.error(msg)
            return
        bit_error_rates = [1e-3, 1e-6, 1e-9, 1e-12]
        font_table = [["", None]]
        points_to_check = [i[::-1] for i in local_config["eye_mask"]["points"]]
        points_to_check = [[i[0] for i in points_to_check], [i[1] for i in points_to_check]]
        for ber in bit_error_rates:
            mag_data = [
                k for k, i in sols.full_matrix_real_imag[0][sols.expressions[0]].items() if ber / 990 < abs(i) <= ber
            ]
            mystr = f"Eye Mask Violation BER at {ber}:"
            result_value = "PASS"
            if not mag_data:
                result_value = "FAILED. No BER obtained"
            for point in mag_data:
                if GeometryOperators.point_in_polygon(point, points_to_check) >= 0:
                    result_value = "FAILED. Mask Violation"
                    break
            font_table.append([None, [255, 0, 0]] if "FAIL" in result_value else ["", None])
            pass_fail_table.append([mystr, result_value])
        pdf_report.add_section(portrait=True)
        pdf_report.add_table(f"Pass Fail Criteria on {image_name}", pass_fail_table, font_table)
        return pass_fail_table

    def _add_eye_measurement(self, report, pdf_report, image_name):
        report.add_all_eye_measurements()
        out_eye = os.path.join(self._output_folder, "eye_measurements_{}.csv".format(image_name))
        report._post.oreportsetup.ExportTableToFile(report.plot_name, out_eye, "Legend")
        report.clear_all_eye_measurements()
        table = read_csv(out_eye)
        new_table = []
        for line in table:
            new_table.append(line)
        pdf_report.add_section(portrait=True)
        pdf_report.add_table(f"Eye Measurements on {image_name}", new_table)
        return new_table

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

    def _create_project_info(self, report):
        report.add_section()
        designs = []
        _design = None
        for template_report in self.local_config["reports"]:
            design_name = template_report["design_name"]
            if design_name in designs:
                continue
            designs.append(design_name)
            if _design and _design.design_name != design_name or _design is None:
                _design = get_pyaedt_app(self._project_name, design_name)
            report.add_project_info(_design)

            report.add_empty_line(3)

            if _design.design_type == "Circuit Design":
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

    def create_compliance_report(self, file_name="compliance_test.pdf"):
        """Create the Virtual Compliance report.

        Parameters
        ----------
        file_name : str
            Output file name.

        Returns
        -------
        str
            Path to the output file.
        """
        report = AnsysReport()
        report.aedt_version = self._desktop_class.aedt_version_id
        report.design_name = self._template_name
        report.report_specs.table_font_size = 7
        report.create()
        if self._specs_folder and self._add_specs_info:
            report.add_chapter("Specifications Info")
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
                    report.add_image(file, caption=caption, width=report.epw - 30)

        self._create_aedt_reports(report)
        if self._add_project_info:
            self._create_project_info(report)
        report.add_toc()
        return report.save_pdf(self._output_folder, file_name=file_name)
