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

import warnings

from ansys.aedt.core.emit_core.emit_constants import EMIT_INTERNAL_UNITS
from ansys.aedt.core.emit_core.emit_constants import EMIT_VALID_UNITS
from ansys.aedt.core.emit_core.emit_constants import data_rate_conv
import ansys.aedt.core.generic.constants as consts


class EmitNode:
    # meant to only be used as a parent class
    def __init__(self, emit_obj, result_id, node_id):
        self._emit_obj = emit_obj
        self._oDesign = emit_obj.odesign
        self._oRevisionData = self._oDesign.GetModule("EmitCom")
        self._result_id = result_id
        self._node_id = node_id
        self._valid = True
        self._is_component = False

    def __eq__(self, other):
        return (self._result_id == other._result_id) and (self._node_id == other._node_id)

    @staticmethod
    def props_to_dict(props):
        """Converts a list of key/value pairs to a dictionary.

        Args:
            props (List[str]): List of strings. Each string
                is a key/value pair in the form: 'key=value'

        Returns:
            dict: properties returned as a dictionary
        """
        result = {}
        for prop in props:
            split_prop = prop.split("=")
            if split_prop[1].find("|") != -1:
                result[split_prop[0]] = split_prop[1].split("|")
            result[split_prop[0]] = split_prop[1]
        return result

    @property
    def valid(self):
        """Is false if this object has been detached from its EMIT node."""
        return self._valid

    @property
    def name(self) -> str:
        """Returns the name of the node.

        Returns:
            str: name of the node.
        """
        return self._get_property("Name")

    @property
    def type(self) -> str:
        """Returns the type of the node.

        Returns:
            str: type of the node.
        """
        return self._get_property("Type")

    @property
    def _parent(self):
        """Returns the parent node for this node.

        Returns:
            EmitNode: parent node for the current node.
        """
        parent_id = 1
        parent_node = self._get_node(parent_id)
        return parent_node

    @property
    def properties(self):
        """Get's the node's properties.

        Returns:
            Dict: dictionary of the node's properties. The display name
                of each property as the key.
        """
        props = self._oRevisionData.GetEmitNodeProperties(self._result_id, self._node_id, True)
        props = self.props_to_dict(props)
        return props

    @property
    def node_warnings(self):
        """Returns any warnings that the node might have.

        Returns:
            str: Warning(s) for the node.
        """
        node_warnings = ""
        try:
            node_warnings = self._get_property("Warnings")
        except Exception:
            warnings.warn(
                f"Unable to get the warnings for node: {self.name}.",
                UserWarning,
            )
        return node_warnings

    @property
    def allowed_child_types(self):
        """A list of child types that can be added to this node.

        Returns:
            list[str]: A list of child types that can be added to this node.
        """
        return self._oRevisionData.GetAllowedChildTypes(self._result_id, self._node_id)

    def _get_node(self, node_id: int):
        """Gets a node for this node's revision with the given id.

        Parameters
        ----------
        node_id: int
            id of node to construct.

        Returns
        -------
        node: EmitNode
            The node.

        Examples
        --------
        >>> new_node = node._get_node(node_id)
        """
        from ansys.aedt.core.emit_core.nodes import generated

        props = self._oRevisionData.GetEmitNodeProperties(self._result_id, node_id, True)
        props = self.props_to_dict(props)
        node_type = props["Type"]

        prefix = "" if self._result_id == 0 else "ReadOnly"

        node = None
        try:
            type_class = getattr(generated, f"{prefix}{node_type}")
            node = type_class(self._emit_obj, self._result_id, node_id)
        except AttributeError:
            node = EmitNode(self._emit_obj, self._result_id, node_id)
        return node

    @property
    def children(self):
        """A list of nodes that are children of the current node.

        Returns:
            list[EmitNode]: list of child nodes that are children
                of the current node.
        """
        child_names = self._oRevisionData.GetChildNodeNames(self._result_id, self._node_id)
        child_ids = [self._oRevisionData.GetChildNodeID(self._result_id, self._node_id, name) for name in child_names]
        child_nodes = [self._get_node(child_id) for child_id in child_ids]
        return child_nodes

    def _get_property(self, prop):
        """Returns the value of the specified property.

        Args:
            prop (str): the name of the property to extract for this node.
                The name should match the value displayed in the UI.

        Returns:
            str or list[str]: the value of the property.
        """
        props = self._oRevisionData.GetEmitNodeProperties(self._result_id, self._node_id, True)
        kv_pairs = [prop.split("=") for prop in props]
        selected_kv_pairs = [kv for kv in kv_pairs if kv[0] == prop]
        if len(selected_kv_pairs) != 1:
            return ""

        selected_kv_pair = selected_kv_pairs[0]
        val = selected_kv_pair[1]

        if val.find("|") != -1:
            return val.split("|")
        else:
            return val

    def _set_property(self, prop, value):
        self._oRevisionData.SetEmitNodeProperties(self._result_id, self._node_id, [f"{prop}={value}"], True)

    def _string_to_value_units(self, value):
        """Given a value with units specified, this function
        will separate the units string from the decimal value.

        Args:
            value (str): string containing both the decimal value
                and the units used.

        Raises:
            ValueError: throws an error if the units can't be determined.

        Returns:
            dec_val: decimal value of the specified property.
            units: units specified with the property.
        """
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

    def _convert_to_internal_units(self, value: float | str, unit_system: str) -> float:
        """Takes a value and converts to internal EMIT units
        used for internally storing the values.

        Args:
            value (float | str): the specified value. If a float is specified,
                then global unit settings are applied. If a string is specified,
                then this function will split the value from the units and verify
                that valid units are given.
            unit_system (str): type of units. (e.g. FrequencyUnit, PowerUnit, etc)

        Returns:
            converted_value (float): value in EMIT internal units (SI units where applicable).

        Examples:
            val = self._convert_to_default_units(25, "FrequencyUnits")
            val2 = self._convert_to_default_units("10 W", "PowerUnits")
        """
        if isinstance(value, float) or isinstance(value, int):
            # unitless, so assume SI Units
            units = consts.SI_UNITS[unit_system]
        else:
            value, units = self._string_to_value_units(value)
            # verify the units are valid for the specified type
            if units not in EMIT_VALID_UNITS[unit_system]:
                raise ValueError(f"{units} are not valid units for this property.")

        if unit_system == "Data Rate":
            converted_value = data_rate_conv(value, units, True)
        else:
            converted_value = consts.unit_converter(value, unit_system, units, EMIT_INTERNAL_UNITS[unit_system])
        return converted_value

    def _convert_from_internal_units(self, value: float, unit_system: str) -> float:
        """Takes a value and converts from internal EMIT units to
        SI Units

        Args:
            value (float): the specified value.
            unit_system (str): type of units. (e.g. Freq, Power, etc)

        Returns:
            converted_value (float): value in SI units.
        """
        # get the SI units
        units = consts.SI_UNITS[unit_system]
        if unit_system == "Data Rate":
            converted_value = data_rate_conv(value, units, False)
        else:
            converted_value = consts.unit_converter(value, unit_system, EMIT_INTERNAL_UNITS[unit_system], units)
        return converted_value

    def _delete(self):
        """Deletes the current node (component)."""
        if self.get_is_component():
            self._oRevisionData.DeleteEmitComponent(self._result_id, self._node_id)
        else:
            self._oRevisionData.DeleteEmitNode(self._result_id, self._node_id)

    def _rename(self, requested_name):
        """Renames the node/component.

        Args:
            requested_name (str): New name for the node/component.

        Raises:
            ValueError: Error if the node is read-only and cannot be renamed.

        Returns:
            str: new name of the node/component. Note that it may be different
                than requested_name if a node/component already exists with
                requested_name.
        """
        new_name = None
        if self.get_is_component():
            if self._result_id > 0:
                raise ValueError("This node is read-only for kept results.")
            self._emit_obj.oeditor.RenameComponent(self.name, requested_name)
            new_name = requested_name
        else:
            new_name = self._oRevisionData.RenameEmitNode(self._result_id, self._node_id, requested_name)

        return new_name

    def _duplicate(self, new_name):
        # TODO (maybe needs to be custom?)
        pass

    def _import(self, file_path, import_type):
        """Imports a file into an Emit node creating a child node for the
        imported data where necessary.

        Args:
            file_path (str): Fullpath to the file to import.
            import_type (str): Type of import desired. Options are: CsvFile,
                TxMeasurement, RxMeasurement, SpectralData, TouchstoneCoupling, CAD
        """
        self._oRevisionData.EmitNodeImport(self._result_id, self._node_id, file_path, import_type)

    def _export_model(self, file_path):
        """Exports an Emit node's model to a file. Currently limited
        to plot trace nodes and the exporting of csv files.

        Args:
            file_path (str): Fullpath to export the data to.
        """
        self._oRevisionData.EmitExportModel(self._result_id, self._node_id, file_path)

    def get_is_component(self):
        """Returns true if the node is also a component.

        Returns:
            bool: True if the node is a component. False otherwise.
        """
        return self._is_component

    def _get_child_node_id(self, child_name):
        """Returns the node ID for the specified child node.

        Args:
            child_name (str): shortname of the desired child node.

        Returns:
            int: unique ID assigned to the child node.
        """
        return self._oRevisionData.GetChildNodeID(self._result_id, self._node_id, child_name)

    def _get_table_data(self):
        """Returns a nested with the node's table data.

        Returns:
            list[list]: the node's table data.
        """
        rows = self._oRevisionData.GetTableData(self._result_id, self._node_id)
        nested_list = [col.split(" ") for col in rows]
        return nested_list

    def _set_table_data(self, nested_list):
        """Sets the table data for the node.

        Args:
            nested_list (list[list]): data to populate the table with.
        """
        rows = [col.join(" ") for col in nested_list]
        self._oRevisionData.SetTableData(self._result_id, self._node_id, rows)

    def _add_child_node(self, child_type, child_name=None):
        """Creates a child node of the given type and name.

        Args:
            child_type (EmitNode): type of child node to create
            child_name (str, optional): Optional name to use for the
                child node. If None, the default name for the node type
                will be used.

        Raises:
            ValueError: error if the specified child type is not allowed
                for the current node.

        Returns:
            int: unique node ID given to the created child node.
        """
        if not child_name:
            child_name = f"New {child_type}"

        new_id = None
        if child_type not in self.allowed_child_types:
            raise ValueError(
                f"Child type {child_type} is not allowed for this node. Allowed types are: {self.allowed_child_types}"
            )
        try:
            new_id = self._oRevisionData.CreateEmitNode(self._result_id, self._node_id, child_name, child_type)
        except Exception as e:
            print(f"Failed to add child node of type {child_type} to node {self.name}. Error: {e}")
        return new_id
