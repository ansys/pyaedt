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

import re

from ansys.aedt.core.generic.general_methods import pyaedt_function_handler


@pyaedt_function_handler()
def _get_data_model(child_object, level=-1):
    import json

    def _fix_dict(p_list, p_out):
        for p, val in p_list.items():
            if p == "properties":
                for prop in val:
                    if "value" in prop:
                        p_out[prop["name"]] = prop["value"]
                    elif "values" in prop:
                        p_out[prop["name"]] = prop["values"]
                    else:
                        p_out[prop["name"]] = None
            elif isinstance(val, dict):
                _fix_dict(val, p_out[p])
            elif isinstance(val, list):
                p_out[p] = []
                for el in val:
                    children = {}
                    _fix_dict(el, children)
                    p_out[p].append(children)
            else:
                p_out[p] = val

    input_str = child_object.GetDataModel(level, 1, 1)
    if input_str:
        input_str = re.sub(r'("value":\s*)(-?inf)(?=[,}])', r"\1null", input_str)

    props_list = json.loads(input_str)
    props = {}
    _fix_dict(props_list, props)
    return props
