# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 - 2026 ANSYS, Inc. and/or its affiliates.
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

import ast
from typing import List
from typing import Union
import warnings

from ansys.aedt.core.emit_core.emit_constants import EMIT_FN_ALLOWED_FUNCS
from ansys.aedt.core.emit_core.emit_constants import EMIT_FN_ALLOWED_OPS
from ansys.aedt.core.emit_core.emit_constants import EMIT_FN_ALLOWED_VARS
from ansys.aedt.core.emit_core.emit_constants import EMIT_INTERNAL_UNITS
from ansys.aedt.core.emit_core.emit_constants import EMIT_VALID_UNITS
from ansys.aedt.core.emit_core.emit_constants import data_rate_conv
from ansys.aedt.core.emit_core.emit_function_validator import FunctionValidator
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

    @name.setter
    def name(self, requested_name: str):
        """Renames the node/component.

        Parameters
        ----------
        requested_name : str
            New name for the node/component.

        Raises
        ------
        ValueError
            If the node is read-only or cannot be renamed.
        """
        if self._result_id > 0:
            raise ValueError("This node is read-only for kept results.")

        if self.get_is_component():
            try:
                self._emit_obj.oeditor.RenameComponent(self.name, requested_name)
            except Exception:
                raise ValueError(f"Failed to rename {self.name} to {requested_name}")
        else:
            _ = self._oRevisionData.RenameEmitNode(self._result_id, self._node_id, requested_name)

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
            Parent node.
        """
        parent_name = self._get_property("Parent", True)
        parent_name = parent_name.replace("NODE-*-", "")
        node_id = self._oRevisionData.GetTopLevelNodeID(0, parent_name)
        return self._get_node(node_id)

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
    def warnings(self) -> str:
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
        from ansys.aedt.core.emit_core.nodes.emitter_node import EmitterNode

        props = self._oRevisionData.GetEmitNodeProperties(self._result_id, node_id, True)
        props = self.props_to_dict(props)
        node_type = props["Type"]

        prefix = "" if self._result_id == 0 else "ReadOnly"

        node = None
        try:
            type_class = EmitNode
            if node_type == "RadioNode" and props["IsEmitter"] == "true":
                type_class = EmitterNode
                # TODO: enable when we add ReadOnlyNodes
                # if prefix == "":
                # type_class = EmitterNode
                # else:
                #    type_class = ReadOnlyEmitterNode
            elif node_type == "Band" and props["IsEmitterBand"] == "true":
                type_class = getattr(generated, f"{prefix}Waveform")
            elif node_type == "TxSpectralProfNode":
                if self.properties["IsEmitterBand"] == "true":
                    type_class = getattr(generated, f"{prefix}TxSpectralProfEmitterNode")
                else:
                    type_class = getattr(generated, f"{prefix}TxSpectralProfNode")
            else:
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

    def _get_property(self, prop, skipChecks: bool = False, isTable: bool = False) -> Union[str, List[str]]:
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
                raise ValueError(f"Property {prop} not found or not available for {self._node_type} configuration.")

            selected_kv_pair = selected_kv_pairs[0]
            val = selected_kv_pair[1]

            if isTable:
                # Node Prop tables
                # Data formatted using compact string serialization
                # with ';' separating rows and '|' separating columns
                rows = val.split(";")
                table = [tuple(row.split("|")) for row in rows if row]
                return table
            elif val.find("|") != -1:
                return val.split("|")
            else:
                return val
        except ValueError:
            raise
        except Exception:
            raise self._emit_obj.logger.aedt_messages.error_level[-1]

    def _set_property(self, prop, value, skipChecks=False):
        try:
            self._oRevisionData.SetEmitNodeProperties(self._result_id, self._node_id, [f"{prop}={value}"], skipChecks)
        except Exception:
            error_text = None
            if len(self._emit_obj.logger.messages.error_level) > 0:
                error_text = self._emit_obj.logger.aedt_messages.error_level[-1]
            else:
                error_text = (
                    f'Exception in SetEmitNodeProperties: Failed setting property "{prop}" to "{value}" for '
                    f'{self.properties["Type"]} node "{self.name}"'
                )
            raise ValueError(error_text)

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
        units = ""
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
        # maybe it's a string but with no units
        try:
            return float(value), units
        except ValueError:
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
            if unit_system == "Data Rate":
                # Data rate isn't included as part of PyAedt's unit class
                units = "bps"
            else:
                units = consts.SI_UNITS[unit_system]
        else:
            value, units = self._string_to_value_units(value)
            # make sure units were specified, if not use SI Units
            if units == "":
                if unit_system == "Data Rate":
                    # Data rate isn't included as part of PyAedt unit class
                    units = "bps"
                else:
                    units = consts.SI_UNITS[unit_system]
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
        if unit_system == "Data Rate":
            units = "bps"
            converted_value = data_rate_conv(value, units, False)
        else:
            units = consts.SI_UNITS[unit_system]
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

        .. deprecated: 0.21.3
            Use name property instead

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
        warnings.warn("This property is deprecated in 0.21.3. Use the name property instead.", DeprecationWarning)
        self.name = requested_name

        return self.name

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

        Returns
        -------
        node: EmitNode
            The node.
        """
        try:
            node_id = self._oRevisionData.EmitNodeImport(self._result_id, self._node_id, file_path, import_type)
        except Exception:
            error_text = None
            if len(self._emit_obj.logger.messages.error_level) > 0:
                error_text = self._emit_obj.logger.aedt_messages.error_level[-1]
            else:
                error_text = (
                    f'Exception in EmitNodeImport: Failed to import: "{file_path}" of node type: "{import_type}"'
                )
            raise Exception(error_text)
        return self._get_node(node_id)

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

    def _is_column_data_table(self):
        """Returns true if the node uses column data tables.

        Returns
        -------
        bool
            True if the table is ColumnData, False otherwise.
        """
        # BB Emission Nodes can have ColumnData or NodeProp tables
        # so handle them first
        if self._node_type == "TxBbEmissionNode":
            if self._get_property("Noise Behavior") == "BroadbandEquation":
                return False
            return True

        try:
            table_title = self._get_property("CDTableTitle", True)
            if table_title == "":
                # No ColumnData Table Title, so it's a NodePropTable
                return False
        except ValueError:
            # Exception returned since "CDTableTitle" doesn't exist
            # so it's a NodePropTable
            return False
        return True

    def _check_column_table_data(self, data):
        """Converts user inputted int or string table data to SI units.

        The table nodes affected are:
        TxHarmonicNode, TxNbEmissionNode,
        TxBbEmissionNode (except equation table), RxMixerProductNode,
        RxSaturationNode, RxSelectivityNode.

        Parameters
        ----------
        data : list of tuples
            User inputted table data.

        Returns
        -------
        list of tuples
            Data converted to SI units.
        """
        exceptions = {
            "TxHarmonicNode": {"Absolute": [None, "PowerUnit"], "Relative": [None, "Power (dBc)"]},
            "TxNbEmissionNode": {
                "Absolute": ["FrequencyUnit", "PowerUnit"],
                "RelativeBandwidth": ["FrequencyUnit", "Attenuation (dB)"],
            },
            "TxBbEmissionNode": {
                "Absolute": ["FrequencyUnit", "Amplitude (dBm/Hz)"],
                "RelativeBandwidth": ["FrequencyUnit", "Amplitude (dBm/Hz)"],
                "RelativeOffset": ["FrequencyUnit", "Amplitude (dBm/Hz)"],
                "BroadbandEquation": ["FrequencyUnit (MHz)", "Amplitude (dBm/Hz)"],
            },
            "RxMixerProductNode": {"Absolute": [None, None, "PowerUnit"], "Relative": [None, None, "Power (dBc)"]},
            "RxSaturationNode": ["FrequencyUnit", "PowerUnit"],
            "RxSelectivityNode": ["FrequencyUnit", "Attenuation (dB)"],
        }

        # Grab table behavior and units based on dropdown selection
        node_type = self._node_type
        if node_type in exceptions:
            if node_type in ["TxHarmonicNode", "TxNbEmissionNode", "TxBbEmissionNode", "RxMixerProductNode"]:
                behavior_key = ""
                if node_type == "TxHarmonicNode":
                    behavior_key = "Harmonic Table Units"
                elif node_type == "TxNbEmissionNode":
                    behavior_key = "Narrowband Behavior"
                elif node_type == "TxBbEmissionNode":
                    behavior_key = "Noise Behavior"
                elif node_type == "RxMixerProductNode":
                    behavior_key = "Mixer Product Table Units"
                behavior = self._get_property(behavior_key)
                units = exceptions[node_type][behavior]
            else:
                units = exceptions[node_type]
        else:
            raise ValueError(f"No table exceptions defined for node type {node_type}.")

        data_return = []
        for row in data:
            row_list = list(row)
            for i, value in enumerate(row):
                valid_unit = False
                if isinstance(value, str):
                    val, unit = self._string_to_value_units(value)
                    if units[i] is not None and "(" in units[i]:
                        # Handle columns with specific units in header
                        input_unit = units[i][units[i].find("(") + 1 : units[i].find(")")]
                        if input_unit == "MHz":
                            row_list[i] = consts.unit_converter(val, "Frequency", unit, input_unit)
                        elif unit != input_unit:
                            raise ValueError(f"{unit} are not valid units for this property.")
                        elif isinstance(val, (float, int)):
                            row_list[i] = val
                        else:
                            raise ValueError(f"{value} is not valid for this property.")
                    else:
                        # Handle columns with SI units
                        for unit_type, valid_units_list in EMIT_VALID_UNITS.items():
                            if unit in valid_units_list:
                                valid_unit = True
                                unit_system = unit_type
                                break
                        if valid_unit:
                            row_list[i] = self._convert_to_internal_units(value, unit_system)
                        else:
                            raise ValueError(f"{unit} is not valid for this property.")
                else:
                    # Handle numeric inputs
                    row_list[i] = value
            data_return.append(tuple(row_list))
        return data_return

    def _check_valid_function(self, expr: str) -> None:
        """Validates a function expression for use in table data.

        Parameters
        ----------
        expr : str
            The function expression to validate.

        Raises
        ------
        ValueError
            If the function expression is invalid.
        """
        try:
            tree = ast.parse(expr, mode="eval")
            validator = FunctionValidator()
            validator.visit(tree)
        except ValueError as e:
            raise ValueError(f"Invalid function expression: {e}")
        except Exception as e:
            raise ValueError(f"Error parsing function expression: {e}")

    def _check_node_prop_table_data(self, data):
        """Converts user inputted int or string table data to SI units.

        The table nodes affected are:
        SamplingNode, TxSpurNode,
        RxSpurNode, TxBbEmissionNode (equation table only).

        Parameters
        ----------
        data : list of tuples
            User inputted table data.

        Returns
        -------
        list of tuples
            Data converted to SI units.
        """
        units = self._get_property("TableUnitTypes", True)
        cols = self._get_property("TableColumns", True)

        data_return = []
        for row in data:
            row_list = list(row)
            if len(row) > len(units):
                raise ValueError(f"Row {row} has more columns than expected ({len(units)}).")
            for i, val in enumerate(row):
                # Extract column unit if present in column header
                col_unit = None
                if "(" in cols[i]:
                    col_unit = cols[i][cols[i].find("(") + 1 : cols[i].find(")")]

                    # Update unit type based on column unit
                    if col_unit in EMIT_VALID_UNITS["Frequency"]:
                        units[i] = "FrequencyUnit"
                    elif col_unit in EMIT_VALID_UNITS["Power"]:
                        units[i] = "PowerUnit"

                if "(" in cols[i] and isinstance(val, str):
                    # Check for function inputs (TxSpurNode, RxSpurNode, TxBbEmissionNode (equation table only))
                    is_function = (
                        any(op in val for op in EMIT_FN_ALLOWED_OPS)
                        or any(fn in val for fn in EMIT_FN_ALLOWED_FUNCS)
                        or any(var in val for var in EMIT_FN_ALLOWED_VARS)
                    )
                    if i == 0 and self._node_type in ["TxSpurNode", "RxSpurNode", "TxBbEmissionNode"] and is_function:
                        try:
                            self._check_valid_function(val)
                            row_list[i] = val
                            continue
                        except Exception:
                            raise ValueError(f"{val} is not a valid function expression.")

                    # Process input values and units
                    s = val.strip().replace(" ", "")
                    unit_index = s.find(next(filter(str.isalpha, s)))
                    value = float(s[:unit_index])
                    input_unit = s[unit_index:]

                    # Handle dBc and dBm/Hz units
                    if input_unit == "dBc" or input_unit == "dBm/Hz":
                        row_list[i] = value
                    elif input_unit not in EMIT_VALID_UNITS[units[i][:-4]]:
                        raise ValueError(f"{input_unit} is not valid for this property.")
                    else:
                        row_list[i] = consts.unit_converter(value, units[i][:-4], input_unit, col_unit)
                else:
                    # Process values that are stored in SI units
                    if isinstance(val, str):
                        value, unit = self._string_to_value_units(val)
                        if unit == "dBc":
                            row_list[i] = value
                        elif unit not in EMIT_VALID_UNITS[units[i][:-4]]:
                            raise ValueError(f"{unit} is not valid for this property.")
                        else:
                            row_list[i] = self._convert_to_internal_units(val, units[i][:-4])
                    elif isinstance(val, (float, int)):
                        row_list[i] = val
                    else:
                        raise ValueError(f"{val} is not valid for this property.")
            data_return.append(tuple(row_list))
        return data_return

    def _get_table_data(self):
        """Returns the node's table data.

        Returns
        -------
        list of tuples
            The node's table data as a list of tuples.
            [(x1, y1, z1), (x2, y2, z2)]
        """
        try:
            if self._is_column_data_table():
                # Column Data tables
                # Data formatted using compact string serialization
                # with '|' separating rows and ';' separating columns
                data = self._oRevisionData.GetTableData(self._result_id, self._node_id)
                rows = data.split("|")
                string_table = [tuple(row.split(";")) for row in rows if row]
            else:
                # Node Prop tables
                # Data formatted using compact string serialization
                # with ';' separating rows and '|' separating columns
                table_key = self._get_property("TableKey", True)
                string_table = self._get_property(table_key, True, True)

            if len(string_table) == 0 or string_table == "":
                return None

            def try_float(val):
                try:
                    return float(val)
                except ValueError:
                    return val  # keep as string for non-numeric (e.g. equations)

            table = [tuple(try_float(x) for x in t) for t in string_table]
        except Exception as e:
            print(f"Failed to get table data for node {self.name}. Error: {e}")
        return table

    def _set_table_data(self, table):
        """Sets the table data for the node.

        Parameters
        ----------
        list of tuples
            Data to populate the table with.
            [(x1, y1, z1), (x2, y2, z2)]
        """
        try:
            if self._is_column_data_table():
                # Column Data tables
                # Data formatted using compact string serialization
                # with '|' separating rows and ';' separating columns
                if self._node_type in [
                    "TxHarmonicNode",
                    "TxNbEmissionNode",
                    "TxBbEmissionNode",
                    "RxMixerProductNode",
                    "RxSaturationNode",
                    "RxSelectivityNode",
                ]:
                    table = self._check_column_table_data(table)
                data = "|".join(";".join(map(str, row)) for row in table)
                self._oRevisionData.SetTableData(self._result_id, self._node_id, data)
            else:
                # Node Prop tables
                # Data formatted using compact string serialization
                # with ';' separating rows and '|' separating columns
                table = self._check_node_prop_table_data(table)
                table_key = self._get_property("TableKey", True)
                data = ";".join("|".join(map(str, row)) for row in table)
                self._set_property(table_key, data, True)
        except Exception as e:
            raise ValueError(f"Failed to set table data for node {self.name}. Error: {e}")

    def _add_child_node(self, child_type, child_name=None):
        """Creates a child node of the given type and name.

        Parameters
        ----------
        child_type : EmitNode
            Type of child node to create.
        child_name : str, optional
            Name to use for the child node. If None, a default name is used.

        Returns
        -------
        node: EmitNode
            The node.

        Raises
        ------
        ValueError
            If the specified child type is not allowed.
        """
        if not child_name:
            child_name = f"{child_type}"

        new_node = None
        if child_type not in self.allowed_child_types:
            raise ValueError(
                f"Child type {child_type} is not allowed for this node. Allowed types are: {self.allowed_child_types}"
            )
        try:
            new_id = self._oRevisionData.CreateEmitNode(self._result_id, self._node_id, child_name, child_type)
            new_node = self._get_node(new_id)
        except Exception as e:
            print(f"Failed to add child node of type {child_type} to node {self.name}. Error: {e}")
        return new_node
