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

from pyaedt.generic.LoadAEDTFile import load_keyword_in_aedt_file
from pyaedt.generic.constants import SI_UNITS
from pyaedt.generic.constants import unit_system


def parse_rdat_file(file_path):
    """
    Parse Ansys report .rdat file

    Returns:
        (dict) report data
    """
    report_dict = {}
    # data = load_entire_aedt_file(file_path)
    data = load_keyword_in_aedt_file(file_path, "ReportsData")

    report_data = data["ReportsData"]["RepMgrRepsData"]
    for report_name in report_data:
        report_dict[report_name] = {}
        for trace, trace_data in report_data[report_name]["Traces"].items():
            all_data = trace_data["TraceComponents"]["TraceDataComps"]["0"]
            if all_data["TraceDataCol"]["ParameterType"] == "ComplexParam":
                all_data_values = all_data["TraceDataCol"]["ColumnValues"]
                all_re_values = all_data_values[0::2]
                all_im_values = all_data_values[1::2]
                all_x_values = trace_data["PrimarySweepInfo"]["PrimarySweepCol"]["ColumnValues"]
                si_unit_x = SI_UNITS[unit_system(trace_data["PrimarySweepInfo"]["PrimarySweepCol"]["Units"])]
                si_unit_y = SI_UNITS[unit_system(all_data["TraceDataCol"]["Units"])]
                report_dict[report_name][trace_data["TraceName"]] = {
                    "x_name": all_data["TraceCompExpr"],
                    "x_unit": si_unit_x,
                    "y_unit": si_unit_y,
                    "curves": {},
                }
                for curve, curve_data in trace_data["CurvesInfo"].items():
                    report_dict[report_name][trace_data["TraceName"]]["curves"][curve_data[1] + "real"] = {
                        "x_data": all_x_values[0 : curve_data[0]],
                        "y_data": all_re_values[0 : curve_data[0]],
                    }
                    report_dict[report_name][trace_data["TraceName"]]["curves"][curve_data[1] + "imag"] = {
                        "x_data": all_x_values[0 : curve_data[0]],
                        "y_data": all_im_values[0 : curve_data[0]],
                    }
                    all_x_values = all_x_values[curve_data[0] :]
                    all_re_values = all_re_values[curve_data[0] :]
                    all_im_values = all_im_values[curve_data[0] :]

            else:
                y_data = trace_data["TraceComponents"]["TraceDataComps"]["1"]
                all_x_values = all_data["TraceDataCol"]["ColumnValues"]
                all_y_values = y_data["TraceDataCol"]["ColumnValues"]
                si_unit_x = SI_UNITS[unit_system(all_data["TraceDataCol"]["Units"])]
                si_unit_y = SI_UNITS[unit_system(y_data["TraceDataCol"]["Units"])]
                report_dict[report_name][trace_data["TraceName"]] = {
                    "x_name": all_data["TraceCompExpr"],
                    "x_unit": si_unit_x,
                    "y_unit": si_unit_y,
                    "curves": {},
                }
                for curve, curve_data in trace_data["CurvesInfo"].items():
                    report_dict[report_name][trace_data["TraceName"]]["curves"][curve_data[1]] = {
                        "x_data": all_x_values[0 : curve_data[0]],
                        "y_data": all_y_values[0 : curve_data[0]],
                    }
                    all_x_values = all_x_values[curve_data[0] :]
                    all_y_values = all_y_values[curve_data[0] :]

    return report_dict
