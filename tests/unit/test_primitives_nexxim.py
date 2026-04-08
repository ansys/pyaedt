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
from unittest.mock import MagicMock
from unittest.mock import patch
import warnings

import pytest

from ansys.aedt.core.modeler.circuits.primitives_nexxim import NexximComponents


def test_add_siwave_dynamic_link_failure_with_file_not_found() -> None:
    file = Path("dummy")
    modeler = MagicMock()
    nexxim = NexximComponents(modeler)

    with pytest.raises(FileNotFoundError):
        nexxim.add_siwave_dynamic_link(file)


@patch.object(warnings, "warn")
def test_add_subcircuit_link_warning_call(mock_warn) -> None:
    file = Path("dummy")
    modeler = MagicMock()
    nexxim = NexximComponents(modeler)

    nexxim._add_subcircuit_link("dummy_comp", ["dummy_pin"], file, "dummy_source_design", image_subcircuit_path=file)

    mock_warn.assert_any_call("Image extension is not valid. Use default image instead.")
