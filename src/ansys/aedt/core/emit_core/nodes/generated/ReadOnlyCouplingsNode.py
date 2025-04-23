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

from ..EmitNode import EmitNode


class ReadOnlyCouplingsNode(EmitNode):
    def __init__(self, oDesign, result_id, node_id):
        self._is_component = False
        EmitNode.__init__(self, oDesign, result_id, node_id)

    @property
    def minimum_allowed_coupling(self) -> float:
        """Minimum Allowed Coupling
        "Global minimum allowed coupling value. All computed coupling within this project will be >= this value."
        "Value should be between -1000 and 1000."
        """
        val = self._get_property("Minimum Allowed Coupling")
        return val

    @property
    def global_default_coupling(self) -> float:
        """Global Default Coupling
        "Default antenna-to-antenna coupling loss value."
        "Value should be between -1000 and 0."
        """
        val = self._get_property("Global Default Coupling")
        return val

    @property
    def antenna_tags(self) -> str:
        """Antenna Tags
        "All tags currently used by all antennas in the project."
        " """
        val = self._get_property("Antenna Tags")
        return val
