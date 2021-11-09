from pyaedt.generic.LoadAEDTFile import load_entire_aedt_file
from pyaedt.application.Variables import VariableManager, DataSet, AEDT_units, unit_system

def parse_file(file_path):
    report_dict = {}
    data = load_entire_aedt_file(file_path)

    report_data = data['ReportsData']['RepMgrRepsData']
    for report_name in report_data:
        report_dict[report_name] = {}
        for trace, trace_data in report_data[report_name]["Traces"].items():
            component_data = trace_data['TraceComponents']['TraceDataComps']
            all_x_values = component_data["0"]['TraceDataCol']['ColumnValues']
            all_y_values = component_data["1"]['TraceDataCol']['ColumnValues']

            report_dict[report_name][trace_data['TraceName']] = {
                "x_name": component_data["0"]['TraceCompExpr'],
                "curves": {}
            }
            for curve, curve_data in trace_data['CurvesInfo'].items():
                report_dict[report_name][trace_data['TraceName']]["curves"][curve_data[1]] = {
                    "x_data": all_x_values[0:curve_data[0]],
                    "y_data": all_y_values[0:curve_data[0]],
                }
                all_x_values = all_x_values[curve_data[0] + 1 :]
                all_y_values = all_y_values[curve_data[0] + 1 :]

    return report_dict
