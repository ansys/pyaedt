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

from unittest.mock import MagicMock

import pytest

from ansys.aedt.core.modules.boundary.common import BoundaryProps


@pytest.fixture(scope="module", autouse=True)
def desktop() -> None:
    """Override the desktop fixture to DO NOT open the Desktop when running this test class."""
    return


class DummyBoundary:
    def __init__(self) -> None:
        self.auto_update = False
        self._app = MagicMock()
        self.updated_with = None
        self.assignment_updated = False

    def update(self, props=None):
        self.updated_with = props
        return True

    def update_assignment(self):
        self.assignment_updated = True
        return True


def test_nested_setitem_updates_root_props() -> None:
    boundary = DummyBoundary()
    props = BoundaryProps(
        boundary,
        {"Parameters": {"subparameter": {"subsub": 1}}},
    )
    boundary.auto_update = True

    props["Parameters"]["subparameter"]["subsub"] = 42

    assert props["Parameters"]["subparameter"]["subsub"] == 42
    assert boundary.updated_with is props
    assert "Parameters" in boundary.updated_with
    assert boundary.updated_with["Parameters"]["subparameter"]["subsub"] == 42


def test_top_level_setitem_still_updates_root() -> None:
    boundary = DummyBoundary()
    props = BoundaryProps(boundary, {"Parameters": {"subparameter": 1}})
    boundary.auto_update = True

    props["Parameters"] = {"subparameter": 2}

    assert props["Parameters"]["subparameter"] == 2
    assert boundary.updated_with is props


def test_nested_dict_assignment_keeps_parent_keys() -> None:
    boundary = DummyBoundary()
    props = BoundaryProps(boundary, {"Parameters": {"subparameter": {"a": 1, "b": 2}}})
    boundary.auto_update = True

    props["Parameters"]["subparameter"]["a"] = 9

    assert set(props["Parameters"]["subparameter"]) == {"a", "b"}
    assert props["Parameters"]["subparameter"]["b"] == 2
    assert boundary.updated_with is props


def test_list_of_dicts_nested_setitem_updates_root() -> None:
    boundary = DummyBoundary()
    props = BoundaryProps(boundary, {"Entries": [{"Name": "e1", "Value": 1}]})
    boundary.auto_update = True

    props["Entries"][0]["Value"] = 5

    assert props["Entries"][0]["Value"] == 5
    assert boundary.updated_with is props


def test_faces_key_calls_update_assignment() -> None:
    boundary = DummyBoundary()
    props = BoundaryProps(boundary, {"Faces": [1]})
    boundary.auto_update = True

    props["Faces"] = [1, 2]

    assert boundary.assignment_updated is True
    assert boundary.updated_with is None
