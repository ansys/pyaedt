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

from pathlib import Path

TESTS_PATH = Path(__file__).resolve().parent
TESTS_SYSTEM_PATH = TESTS_PATH / "system"
TESTS_UNIT_PATH = TESTS_PATH / "unit"
TESTS_EMIT_PATH = TESTS_SYSTEM_PATH / "emit"
TESTS_FILTER_SOLUTIONS_PATH = TESTS_SYSTEM_PATH / "filter_solutions"
TESTS_GENERAL_PATH = TESTS_SYSTEM_PATH / "general"
TESTS_SOLVERS_PATH = TESTS_SYSTEM_PATH / "solvers"
TESTS_VISUALIZATION_PATH = TESTS_SYSTEM_PATH / "visualization"
TESTS_SEQUENTIAL_PATH = TESTS_SOLVERS_PATH / "sequential"
TESTS_ICEPAK_PATH = TESTS_SYSTEM_PATH / "icepak"
TESTS_LAYOUT_PATH = TESTS_SYSTEM_PATH / "layout"
