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
    with open(config_file, "r") as file:
        data = json.load(file)
    return data


def import_config_file(aedtapp, json_data):
    full_path = os.path.abspath("load.json")
    with open(full_path, "w") as file:
        json.dump(json_data, file)
    out = aedtapp.configurations.import_config(full_path)
    result = aedtapp.configurations.validate(out)
    if result:
        aedtapp.logger.info("Sucessfully imported configuration")
    else:
        aedtapp.logger.info("Import has issues")
    return result


def get_object_id_mapping(aedtapp):
    object_id_map = {name: aedtapp.modeler.get_obj_id(name) for name in aedtapp.modeler.object_names}
    return object_id_map
