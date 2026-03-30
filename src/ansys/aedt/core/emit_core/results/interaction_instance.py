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

from ansys.aedt.core.emit_core.emit_constants import ResultType


class InteractionInstance:
    def __init__(self, emit_obj):
        self.emit_project = emit_obj
        self.odesktop = self.emit_project.odesktop

    def get_results_warning(self) -> str:
        """Get the results warning for this interaction."""
        self.emit_project._emit_com_module.CheckInstanceValidity()

    def has_valid_values(self) -> bool:
        """Check if this interaction has valid values."""
        return self._emit_com.HasValidValues()

    def get_value(self, result_type: ResultType) -> float:
        """Get the value of this interaction."""
        return self._emit_com.GetValue()

    def get_largest_problem_type(self):
        """Get the largest problem type for this interaction."""
        return self._emit_com.GetLargestProblemType()

    def get_largest_emi_problem_type(self) -> str:
        """Get the largest EMI problem type for this interaction."""
        return self._emit_com.GetLargestEMIProblemType()
