DATA = {
    "coordinate_system": {
        "GLOBAL_2": {
            "origin": [
                "100mm",
                "0mm",
                "0mm"
            ],
            "reference_cs": "Global"
        },
        "CS_CLAMP": {
            "origin": [
                "-130mm",
                "80mm",
                "12mm"
            ],
            "reference_cs": "GLOBAL_2"
        }
    },
    "assembly": {
        "case": {
            "component_type": "mcad",
            "file_path": "E:\\_pycharm_project\\my_docs\\database\\wf_cad_assembly\\models\\Chassi.a3dcomp",
            "reference_coordinate_system": "Global",
            "target_coordinate_system": "GLOBAL_2",
            "arrange": [
                {"operation": "rotate", "axis": "X", "angle": "0deg"},
                {"operation": "move", "vector": ["0mm", "0mm", "0mm"]}
            ],
            "sub_components": {
                "pcb": {
                    "component_type": "ecad",
                    "file_path": "E:\\_pycharm_project\\my_docs\\database\\wf_cad_assembly\\models\\DCDC-Converter-App_main.aedbcomp",
                    "target_coordinate_system": "Guiding_Pin",
                    "layout_coordinate_systems": [
                        "CABLE1_via_65",
                        "CABLE2_via_65",
                        "H0_via_65"
                    ],
                    "reference_coordinate_system": "H0_via_65",
                    "arrange": [
                        {"operation": "rotate", "axis": "X", "angle": "0deg"},
                        {"operation": "move", "vector": ["0mm", "0mm", "0mm"]}
                    ],
                    "sub_components": {
                        "cable_1": {
                            "component_type": "mcad",
                            "file_path": "E:\\_pycharm_project\\my_docs\\database\\wf_cad_assembly\\models\\Cable_1.a3dcomp",
                            "target_coordinate_system": "CABLE1_via_65"
                        },
                        "cable_2": {
                            "component_type": "mcad",
                            "file_path": "E:\\_pycharm_project\\my_docs\\database\\wf_cad_assembly\\models\\Cable_1.a3dcomp",
                            "target_coordinate_system": "CABLE2_via_65"
                        }
                    }
                }
            }
        },
        "clamp_monitor": {
            "component_type": "mcad",
            "file_path": "E:\\_pycharm_project\\my_docs\\database\\wf_cad_assembly\\models\\BCI_MONITORING_CLAMP.a3dcomp",
            "reference_coordinate_system": "Global",
            "target_coordinate_system": "CS_CLAMP"
        }
    }
}
