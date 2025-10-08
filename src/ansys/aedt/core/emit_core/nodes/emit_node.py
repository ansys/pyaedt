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

from typing import List
from typing import Union
import warnings

from ansys.aedt.core.emit_core.emit_constants import EMIT_INTERNAL_UNITS
from ansys.aedt.core.emit_core.emit_constants import EMIT_VALID_UNITS
from ansys.aedt.core.emit_core.emit_constants import data_rate_conv
import ansys.aedt.core.generic.constants as consts


class EmitNode:
    """Emit node class for managing and interacting with EMIT nodes."""

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
    def props_to_dict(props: List[str]) -> dict:
        """Converts a list of key/value pairs to a dictionary.

        Parameters
        ----------
        props : list
            Each string is a key/value pair in the form: 'key=value'.

        Returns
        -------
        dict
            Properties returned as a dictionary.
        """
        result = {}
        for prop in props:
            split_prop = prop.split("=")
            if split_prop[1].find("|") != -1:
                result[split_prop[0]] = split_prop[1].split("|")
            result[split_prop[0]] = split_prop[1]
        return result

    @property
    def valid(self) -> bool:
        """Indicates if this object is still valid (not detached from EMIT node).

        Returns
        -------
        bool
            ``True`` if the object is valid, ``False`` otherwise.
        """
        return self._valid

    @property
    def name(self) -> str:
        """Name of the node.

        Returns
        -------
        str
            Name of the node.
        """
        return self._get_property("Name", True)

    @property
    def _node_type(self) -> str:
        """Type of the node.

        Returns
        -------
        str
            Type of the node.
        """
        return self._get_property("Type", True)

    @property
    def _parent(self):
        """Parent node name of this node.

        Returns
        -------
        EmitNode
            Parent node name.
        """
        return self._get_property("Parent", True)

    @property
    def properties(self) -> dict:
        """Node properties.

        Returns
        -------
        dict
            Dictionary of the node's properties with display name as key.
        """
        props = self._oRevisionData.GetEmitNodeProperties(self._result_id, self._node_id, True)
        props = self.props_to_dict(props)
        return props

    @property
    def node_warnings(self) -> str:
        """Warnings for the node, if any.

        Returns
        -------
        str
            Warning message(s).
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
    def allowed_child_types(self) -> List[str]:
        """Child types allowed for this node.

        Returns
        -------
        list
            Allowed child types.
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
        """Child nodes of this node.

        Returns
        -------
        list[EmitNode]
            List of child nodes.
        """
        child_names = self._oRevisionData.GetChildNodeNames(self._result_id, self._node_id)
        child_ids = [self._oRevisionData.GetChildNodeID(self._result_id, self._node_id, name) for name in child_names]
        child_nodes = [self._get_node(child_id) for child_id in child_ids]
        return child_nodes

    def _get_property(self, prop, skipChecks=False) -> Union[str, List[str]]:
        """Fetch the value of a given property.

        Parameters
        ----------
        prop : str
            Name of the property.

        Returns
        -------
        str, or list
            Property value.
        """
        try:
            props = self._oRevisionData.GetEmitNodeProperties(self._result_id, self._node_id, skipChecks)
            kv_pairs = [prop.split("=") for prop in props]
            selected_kv_pairs = [kv for kv in kv_pairs if kv[0].rstrip() == prop]
            if len(selected_kv_pairs) < 1:
                return ""

            selected_kv_pair = selected_kv_pairs[0]
            val = selected_kv_pair[1]

            if val.find("|") != -1:
                return val.split("|")
            else:
                return val
        except Exception:
            raise self._emit_obj.logger.aedt_messages.error_level[-1]

    def _set_property(self, prop, value):
        try:
            self._oRevisionData.SetEmitNodeProperties(self._result_id, self._node_id, [f"{prop}={value}"], True)
        except Exception:
            error_text = None
            if len(self._emit_obj.logger.messages.error_level) > 0:
                error_text = self._emit_obj.logger.aedt_messages.error_level[-1]
            else:
                error_text = (
                    f'Exception in SetEmitNodeProperties: Failed setting property "{prop}" to "{value}" for '
                    f'{self.properties["Type"]} node "{self.name}"'
                )
            raise Exception(error_text)

    @staticmethod
    def _string_to_value_units(value) -> tuple[float, str]:
        """Splits a value into its numeric and unit components.

        Parameters
        ----------
        value : str
            A string containing a number and unit (e.g. '10 W').

        Returns
        -------
        float
            Numeric value.
        str
            Units.

        Raises
        ------
        ValueError
             If units are not valid.
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
        raise ValueError(f"{value} is not valid for this property.")

    def _convert_to_internal_units(self, value: float | str, unit_system: str) -> float:
        """Takes a value and converts to internal EMIT units used for storing values.

        Parameters
        ----------
        value : float or str
            The specified value. If a float is specified, global unit settings are applied.
            If a string is specified, it is split into value and units and validated.
        unit_system : str
            Type of units (e.g., FrequencyUnit, PowerUnit).

        Returns
        -------
        float
            Value in EMIT internal units (SI units where applicable).
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

    @staticmethod
    def _convert_from_internal_units(value: float, unit_system: str) -> float:
        """Takes a value and converts from internal EMIT units to SI units.

        Parameters
        ----------
        value : float
            The specified value.
        unit_system : str
            Type of units (e.g., FrequencyUnit, PowerUnit).

        Returns
        -------
        float
            Value in SI units.
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

    def _rename(self, requested_name: str) -> str:
        """Renames the node/component.

        Parameters
        ----------
        requested_name : str
            New name for the node/component.

        Returns
        -------
        str
            New name of the node/component.

        Raises
        ------
        ValueError
            If the node is read-only and cannot be renamed.
        """
        if self.get_is_component():
            if self._result_id > 0:
                raise ValueError("This node is read-only for kept results.")
            self._emit_obj.oeditor.RenameComponent(self.name, requested_name)
            new_name = requested_name
        else:
            new_name = self._oRevisionData.RenameEmitNode(self._result_id, self._node_id, requested_name)

        return new_name

    def _duplicate(self, new_name):
        raise NotImplementedError("This method is not implemented yet.")

    def _import(self, file_path: str, import_type: str):
        """Imports a file into an Emit node.

        Parameters
        ----------
        file_path : str
            Full path to the file to import.
        import_type : str
            Type of import. Options are: CsvFile, TxMeasurement, RxMeasurement,
            SpectralData, TouchstoneCoupling, CAD.
        """
        self._oRevisionData.EmitNodeImport(self._result_id, self._node_id, file_path, import_type)

    def _export_model(self, file_path: str):
        """Exports an Emit node's model to a file.

        Parameters
        ----------
        file_path : str
            Full path to export the data to.
        """
        self._oRevisionData.EmitExportModel(self._result_id, self._node_id, file_path)

    def get_is_component(self) -> bool:
        """Check if node is also a component.

        Returns
        -------
        bool
            ``True`` if the node is a component. ``False`` otherwise.
        """
        return self._is_component

    def _get_child_node_id(self, child_name: str) -> int:
        """Returns the node ID for the specified child node.

        Parameters
        ----------
        child_name : str
            Short name of the desired child node.

        Returns
        -------
        int
            Unique ID assigned to the child node.
        """
        return self._oRevisionData.GetChildNodeID(self._result_id, self._node_id, child_name)

    def _get_table_data(self):
        """Returns the node's table data.

        Returns
        -------
        list
            The node's table data.
        """
        rows = self._oRevisionData.GetTableData(self._result_id, self._node_id)
        nested_list = [col.split(" ") for col in rows]
        return nested_list

    def _set_table_data(self, nested_list):
        """Sets the table data for the node.

        Parameters
        ----------
        nested_list : list
            Data to populate the table with.
        """
        rows = [col.join(" ") for col in nested_list]
        self._oRevisionData.SetTableData(self._result_id, self._node_id, rows)

    def _add_child_node(self, child_type, child_name=None):
        """Creates a child node of the given type and name.

        Parameters
        ----------
        child_type : EmitNode
            Type of child node to create.
        child_name : str, optional
            Optional name to use for the child node. If None, a default name is used.

        Returns
        -------
        int
            Unique node ID assigned to the created child node.

        Raises
        ------
        ValueError
            If the specified child type is not allowed.
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
