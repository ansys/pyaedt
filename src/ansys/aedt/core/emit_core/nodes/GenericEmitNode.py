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

import warnings

from . import generated

def props_to_dict(props):
    result = {}
    for prop in props:
        split_prop = prop.split("=")
        result[split_prop[0]] = split_prop[1]
    
    return result

class GenericEmitNode:
    # meant to only be used as a parent class
    def __init__(self, oDesign, result_id, node_id):
        self._oDesign = oDesign
        self._result_id = result_id
        self._node_id = node_id
        self.valid = True

    @property
    def get_valid(self):
        """Is false if this object has been detached from its EMIT node."""
        return self.valid

    def get_name(self):
        props = self._oDesign.GetModule('EmitCom').GetEmitNodeProperties(self._result_id, self._node_id, True)
        props = props_to_dict(props)
        return props["Name"]

    @property
    def parent(self):
        # parent_id = self._oDesign.GetModule('EmitCom').GetParentNodeID(self._result_id, self._node_id)
        parent_id = 1

        parent_props = self._oDesign.GetModule('EmitCom').GetEmitNodeProperties(self._result_id, parent_id, True)
        parent_props = props_to_dict(parent_props)

        parent_type = parent_props['Type']
        parent_type = f'Node_{parent_type}'

        parent_type_module = getattr(generated, parent_type)
        parent_type_class = getattr(parent_type_module, parent_type)
        parent_node = parent_type_class(self._oDesign, self._result_id, parent_id)

        return parent_node
    
    def get_parent(self):
        #TODO how to create a parent of the appropriate pyaedt node type?
        return self._oDesign.GetModule('EmitCom').GetEmitNodeParent(self._result_id, self._node_id)
        props = self.get_properties()
        parent_path = props['Parent']

    def get_properties(self):
        props = self._oDesign.GetModule('EmitCom').GetEmitNodeProperties(self._result_id, self._node_id, True)
        props = props_to_dict(props)
        return props

    def get_warnings(self):
        props = self._oDesign.GetModule('EmitCom').GetEmitNodeProperties(self._result_id, self._node_id, True)
        props = props_to_dict(props)
        return props["Warnings"]

    def get_allowed_child_types(self):
        return self._oDesign.GetModule('EmitCom').GetAllowedChildTypes(self._result_id, self._node_id)

    def _delete(self):
        if self._is_component(): self._oDesign.GetModule('EmitCom').DeleteEmitComponent(self._result_id, self._node_id)
        else: self._oDesign.GetModule('EmitCom').DeleteEmitNode(self._result_id, self._node_id)

    def _rename(self, requested_name):
        new_name = self._oDesign.GetModule('EmitCom').RenameEmitNode(self._result_id, self._node_id, requested_name)
        return new_name

    def _duplicate(self):
        # TODO (maybe needs to be custom?)
        pass

    def _import(self, file_path, import_type):
        self._oDesign.GetModule('EmitCom').EmitNodeImport(self._result_id, self._node_id, file_path, import_type)

    def _export_model(self, file_path):
        self._oDesign.GetModule('EmitCom').EmitExportModel(self._result_id, self._node_id, file_path)

    def _is_component(self):
        return self._is_component

    def _get_child_node_id(self, child_name):
        return self._oDesign.GetModule('EmitCom').GetChildNodeID(self._result_id, self._node_id, child_name)

    def _get_table_data(self):
        rows = self._oDesign.GetModule('EmitCom').GetTableData(self._result_id, self._node_id)
        nested_list = [col.split(' ') for col in rows]
        return nested_list

    def _set_table_data(self, nested_list):
        rows = [col.join(' ') for col in nested_list]
        self._oDesign.GetModule('EmitCom').SetTableData(self._result_id, self._node_id, rows)
