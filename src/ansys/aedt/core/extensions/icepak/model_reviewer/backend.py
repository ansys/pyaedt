import json
import os

def export_config_file(aedtapp):
    aedtapp.configurations.options.export_monitor = False
    aedtapp.configurations.options.export_native_components = False
    aedtapp.configurations.options.export_datasets = False
    aedtapp.configurations.options.export_parametrics = False
    aedtapp.configurations.options.export_variables = False
    aedtapp.configurations.options.export_mesh_operations = False
    aedtapp.configurations.options.export_optimizations = False
    config_file = aedtapp.configurations.export_config()
    with open(config_file, 'r') as file:
        data = json.load(file)
    return data

def import_config_file(aedtapp, json_data):
    full_path = os.path.abspath("load.json")
    with open(full_path, 'w') as file:
        json.dump(json_data, file)
    print(f"json file path is {full_path}")
    out = aedtapp.configurations.import_config(full_path)
    result = aedtapp.configurations.validate(out)
    if result:
        print("sucessfully imported configuration")
    else:
        print("import has issues")
    return None

def get_object_id_mapping(aedtapp):
    object_id_map = {name: aedtapp.modeler.get_obj_id(name) for name in aedtapp.modeler.object_names}
    return object_id_map
