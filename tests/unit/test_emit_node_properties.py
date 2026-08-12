# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 - 2026 Synopsys, Inc. and ANSYS, Inc. All rights reserved.
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

import pytest

from ansys.aedt.core.emit_core.nodes.emit_node import EmitNode


@pytest.mark.parametrize(
    ("props", "expected"),
    [
        (["Name=Antenna1", "Enabled=true"], {"Name": "Antenna1", "Enabled": "true"}),
        (["Position=1 2 3"], {"Position": "1 2 3"}),
        (["Tags=a|b|c"], {"Tags": "a|b|c"}),
    ],
)
def test_props_to_dict(props, expected) -> None:
    assert EmitNode.props_to_dict(props) == expected


def test_format_property_value() -> None:
    assert EmitNode._format_property_value("Enabled", True) == "true"
    assert EmitNode._format_property_value("Position", [1.0, 2.0, 3.0]) == "1.0 2.0 3.0"
    assert EmitNode._format_property_value("Tags", ["a", "b"]) == "a|b"


def test_format_property_string() -> None:
    assert EmitNode._format_property_string("Enabled", True) == "Enabled=true"
    assert EmitNode._format_property_string("Position", [1.0, 2.0, 3.0]) == "Position=1.0 2.0 3.0"


def test_parse_property_value() -> None:
    assert EmitNode._parse_property_value("Position", "1 2 3") == [1.0, 2.0, 3.0]
    assert EmitNode._parse_property_value("Enabled", "true") == "true"
    assert EmitNode._parse_property_value("Tags", "a|b|c") == ["a", "b", "c"]
