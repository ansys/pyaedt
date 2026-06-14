# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 - 2026 ANSYS, Inc. and/or its affiliates.
# SPDX-License-Identifier: MIT

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


def test_parse_property_value() -> None:
    assert EmitNode._parse_property_value("Position", "1 2 3") == [1.0, 2.0, 3.0]
    assert EmitNode._parse_property_value("Enabled", "true") == "true"
    assert EmitNode._parse_property_value("Tags", "a|b|c") == ["a", "b", "c"]
