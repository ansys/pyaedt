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

from enum import Enum
from ansys.aedt.core.emit_core.results import revision
from ..emit_constants import EMIT_VALID_UNITS, EMIT_DEFAULT_UNITS, EMIT_TO_AEDT_UNITS, data_rate_conv
import ansys.aedt.core.generic.constants as consts

class EmitNode:
    # meant to only be used as a parent class
    def __init__(self, oDesign, result_id, node_id):
        self._oDesign = oDesign
        self._oRevisionData = oDesign.GetModule("EmitCom")
        self._result_id = result_id
        self._node_id = node_id
        self._valid = True
    
    def __eq__(self, other):
        return ((self._result_id == other._result_id) and (self._node_id == other._node_id))

    @staticmethod
    def props_to_dict(props):
        result = {}
        for prop in props:
            split_prop = prop.split("=")
            if split_prop[1].find('|') != -1:
                result[split_prop[0]] = split_prop[1].split('|')
            result[split_prop[0]] = split_prop[1]
        return result

    @property
    def valid(self):
        """Is false if this object has been detached from its EMIT node."""
        return self._valid

    @property
    def name(self):
        return self._get_property("Name")

    @property
    def _parent(self):
        # parent_id = self._oDesign.GetModule('EmitCom').GetParentNodeID(self._result_id, self._node_id)
        parent_id = 1
        parent_node = self._get_node(parent_id)
        return parent_node

    @property
    def properties(self):
        props = self._oRevisionData.GetEmitNodeProperties(self._result_id, self._node_id, True)
        props = self.props_to_dict(props)
        return props

    @property
    def warnings(self):
        warnings = ''
        try:
            warnings = self._get_property("Warnings")
        except Exception:
            pass
        return warnings

    @property
    def allowed_child_types(self):
        return self._oRevisionData.GetAllowedChildTypes(self._result_id, self._node_id)

    def _get_node(self, id: int):
        """Gets a node for this node's revision with the given id.

        Parameters
        ----------
        id: int
            id of node to construct.

        Returns
        -------
        node: EmitNode
            The node.

        Examples
        --------
        >>> new_node = node._get_node(node_id)
        """
        from . import generated

        props = self._oRevisionData.GetEmitNodeProperties(self._result_id, id, True)
        props = self.props_to_dict(props)
        type = props['Type']

        node = None
        try:
            type_class = getattr(generated, type)
            node = type_class(self._oDesign, self._result_id, id)
        except AttributeError:
            node = EmitNode(self._oDesign, self._result_id, id)
        return node
    
    @property
    def children(self):
        child_names = self._oRevisionData.GetChildNodeNames(self._result_id, self._node_id)
        child_ids = [self._oRevisionData.GetChildNodeID(self._result_id, self._node_id, name) for name in child_names]
        child_nodes = [self._get_node(child_id) for child_id in child_ids]
        return child_nodes 
    
    def _get_property(self, prop):
        props = self._oRevisionData.GetEmitNodeProperties(self._result_id, self._node_id, True)
        kv_pairs = [prop.split('=') for prop in props]
        selected_kv_pairs = [kv for kv in kv_pairs if kv[0] == prop]
        if len(selected_kv_pairs) != 1:
            return ''

        selected_kv_pair = selected_kv_pairs[0]
        val = selected_kv_pair[1]

        if val.find('|') != -1:
            return val.split('|')
        else:
            return val
    
    def _string_to_value_units(self, value):
        # see if we can split it based on a space between number 
        # and units
        vals = value.split(" ")
        if len(vals) == 2:
            dec_val = float(vals[0])
            units = vals[1].strip()
            return dec_val, units
        # no space before units, so find the first letter
        for i, char in enumerate(value):
            if char.isalpha():
                dec_val = float(value[:i])
                units = value[i:]
                return dec_val, units
        raise ValueError(f"{value} are not valid units for this property.")
            
    def _convert_to_default_units(self, value : float|str, unit_type : str) -> float:
        """Takes a value and converts to default EMIT units
        used for internally storing the values.

        Args:
            value (float | str): the specified value. If a float is specified, 
                then global unit settings are applied. If a string is specified, 
                then this function will split the value from the units and verify
                that valid units are given.
            unit_type (str): type of units. (e.g. FrequencyUnit, PowerUnit, etc)

        Returns:
            converted_value (float): value in EMIT default units (SI units where applicable).
            
        Examples:
            val = self._convert_to_default_units(25, "FrequencyUnits")
            val2 = self._convert_to_default_units("10 W", "PowerUnits")
        """
        unit_system = unit_type.split(' ')[0]
        if isinstance(value, float) or isinstance(value, int):
            # get the global units            
            pref_node_id = self._oRevisionData.GetTopLevelNodeID(self._result_id, "Preferences")
            props = self._oRevisionData.GetEmitNodeProperties(self._result_id, pref_node_id, True)
            kv_pairs = [prop.split('=') for prop in props]
            selected_kv_pairs = [kv for kv in kv_pairs if kv[0] == unit_type]
            units = selected_kv_pairs[0][1]
            units = EMIT_TO_AEDT_UNITS[units]
        else:
            value, units = self._string_to_value_units(value)
            # verify the units are valid for the specified type            
            if units not in EMIT_VALID_UNITS[unit_system]:
                raise ValueError(f"{units} are not valid units for this property.")
            
        if unit_system == "Data Rate":
            converted_value = data_rate_conv(value, units, True)
        else:
            converted_value = consts.unit_converter(value, unit_system, units, EMIT_DEFAULT_UNITS[unit_system])   
        return converted_value
    
    def _convert_from_default_units(self, value : float, unit_type : str) -> float:
        """Takes a value and converts from default EMIT units to
        the user specified units.

        Args:
            value (float): the specified value.
            unit_type (str): type of units. (e.g. Frequency Unit, Power Unit, etc)

        Returns:
            converted_value (float): value in global units.
        """
        unit_system = unit_type.rsplit(' ', 1)[0]        
        # get the global units            
        pref_node_id = self._oRevisionData.GetTopLevelNodeID(self._result_id, "Preferences")
        props = self._oRevisionData.GetEmitNodeProperties(self._result_id, pref_node_id, True)
        kv_pairs = [prop.split('=') for prop in props]
        selected_kv_pairs = [kv for kv in kv_pairs if kv[0] == unit_type]
        units = selected_kv_pairs[0][1]
        units = EMIT_TO_AEDT_UNITS[units]
            
        if units not in EMIT_VALID_UNITS[unit_system]:
            raise ValueError(f"{units} are not valid units for this property.")
        if unit_system == "Data Rate":
            converted_value = data_rate_conv(value, units, False)
        else:
            converted_value = consts.unit_converter(value, unit_system, EMIT_DEFAULT_UNITS[unit_system], units)
        return converted_value

    def _delete(self):
        if self._is_component(): self._oRevisionData.DeleteEmitComponent(self._result_id, self._node_id)
        else: self._oRevisionData.DeleteEmitNode(self._result_id, self._node_id)

    def _rename(self, requested_name):
        new_name = self._oRevisionData.RenameEmitNode(self._result_id, self._node_id, requested_name)
        return new_name

    def _duplicate(self):
        # TODO (maybe needs to be custom?)
        pass

    def _import(self, file_path, import_type):
        self._oRevisionData.EmitNodeImport(self._result_id, self._node_id, file_path, import_type)

    def _export_model(self, file_path):
        self._oRevisionData.EmitExportModel(self._result_id, self._node_id, file_path)

    def _is_component(self):
        return self._is_component

    def _get_child_node_id(self, child_name):
        return self._oRevisionData.GetChildNodeID(self._result_id, self._node_id, child_name)

    def _get_table_data(self):
        rows = self._oRevisionData.GetTableData(self._result_id, self._node_id)
        nested_list = [col.split(' ') for col in rows]
        return nested_list

    def _set_table_data(self, nested_list):
        rows = [col.join(' ') for col in nested_list]
        self._oRevisionData.SetTableData(self._result_id, self._node_id, rows)
    
    def _add_child_node(self, child_type, child_name = None):
        if not child_name:
            child_name = f'New {child_type}'

        new_id = None
        if child_type not in self.allowed_child_types:
            raise ValueError(f"Child type {child_type} is not allowed for this node. Allowed types are: {self.allowed_child_types}")
        try:
            new_id = self._oRevisionData.CreateEmitNode(self._result_id, self._node_id, child_name, child_type)
        except Exception as e:
            print(f"Failed to add child node of type {child_type} to node {self.name}. Error: {e}")
        return new_id
