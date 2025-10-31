# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 - 2025 ANSYS, Inc. and/or its affiliates.
# SPDX-FileCopyrightText: 2021 - 2025 ANSYS, Inc. and /or its affiliates.
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

from ansys.aedt.core.emit_core.nodes.emit_node import EmitNode


class CustomCouplingNode(EmitNode):
    def __init__(self, emit_obj, result_id, node_id):
        self._is_component = False
        EmitNode.__init__(self, emit_obj, result_id, node_id)

    @property
    def parent(self):
        """The parent of this emit node."""
        return self._parent

    @property
    def node_type(self) -> str:
        """The type of this emit node."""
        return self._node_type

    def import_csv_file(self, file_name):
        """Import a CSV File..."""
        return self._import(file_name, "Csv")

    def rename(self, new_name: str):
        """Rename this node"""
        self._rename(new_name)

    def duplicate(self, new_name: str):
        """Duplicate this node"""
        return self._duplicate(new_name)

    def delete(self):
        """Delete this node"""
        self._delete()

    @property
    def table_data(self):
        """Custom Coupling Values Table.
        Table consists of 2 columns.
        Frequency:
            Value should be between 1.0 and 100.0e9.
        Value (dB):
            Value should be between -1000.0 and 0.0.
        """
        return self._get_table_data()

    @table_data.setter
    def table_data(self, value):
        self._set_table_data(value)

    @property
    def enabled(self) -> bool:
        """Enable/Disable coupling.

        Value should be 'true' or 'false'.
        """
        val = self._get_property("Enabled")
        return val == "true"

    @enabled.setter
    def enabled(self, value: bool):
        self._set_property("Enabled", f"{str(value).lower()}")

    @property
    def antenna_a(self) -> EmitNode:
        """First antenna of the pair to apply the coupling values to."""
        val = self._get_property("Antenna A")
        return val

    @antenna_a.setter
    def antenna_a(self, value: EmitNode):
        self._set_property("Antenna A", f"{value}")

    @property
    def antenna_b(self) -> EmitNode:
        """Second antenna of the pair to apply the coupling values to."""
        val = self._get_property("Antenna B")
        return val

    @antenna_b.setter
    def antenna_b(self, value: EmitNode):
        self._set_property("Antenna B", f"{value}")

    @property
    def enable_refinement(self) -> bool:
        """Enables/disables refined sampling of the frequency domain.

        Value should be 'true' or 'false'.
        """
        val = self._get_property("Enable Refinement")
        return val == "true"

    @enable_refinement.setter
    def enable_refinement(self, value: bool):
        self._set_property("Enable Refinement", f"{str(value).lower()}")

    @property
    def adaptive_sampling(self) -> bool:
        """Enables/disables adaptive refinement the frequency domain sampling.

        Value should be 'true' or 'false'.
        """
        val = self._get_property("Adaptive Sampling")
        return val == "true"

    @adaptive_sampling.setter
    def adaptive_sampling(self, value: bool):
        self._set_property("Adaptive Sampling", f"{str(value).lower()}")

    @property
    def refinement_domain(self):
        """Points to use when refining the frequency domain."""
        val = self._get_property("Refinement Domain")
        return val

    @refinement_domain.setter
    def refinement_domain(self, value):
        self._set_property("Refinement Domain", f"{value}")
