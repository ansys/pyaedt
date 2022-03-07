from pyaedt.generic.constants import SI_UNITS
from pyaedt.generic.constants import unit_system
from pyaedt.generic.LoadAEDTFile import load_entire_aedt_file


def parse_rdat_file(file_path):
    """
    Parse Ansys report .rdat file

    Returns:
        (dict) report data
    """
    report_dict = {}
    data = load_entire_aedt_file(file_path)

    report_data = data["ReportsData"]["RepMgrRepsData"]
    for report_name in report_data:
        report_dict[report_name] = {}
        for trace, trace_data in report_data[report_name]["Traces"].items():
            x_data = trace_data["TraceComponents"]["TraceDataComps"]["0"]
            y_data = trace_data["TraceComponents"]["TraceDataComps"]["1"]
            all_x_values = x_data["TraceDataCol"]["ColumnValues"]
            all_y_values = y_data["TraceDataCol"]["ColumnValues"]

            si_unit_x = SI_UNITS[unit_system(x_data["TraceDataCol"]["Units"])]
            si_unit_y = SI_UNITS[unit_system(y_data["TraceDataCol"]["Units"])]
            report_dict[report_name][trace_data["TraceName"]] = {
                "x_name": x_data["TraceCompExpr"],
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
