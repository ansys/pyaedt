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

import builtins
from unittest.mock import mock_open

from mock import patch
import pytest

from ansys.aedt.core.visualization.advanced.sbrplus.hdm_parser import Parser

DUMMY_PATH = "some/dummy/path"
CORRECT_HDM_HEADER = b"""
# The binary data starts immediately after the '#header end' line.
{
  'types':
  {
  'Int32': {'type': 'int', 'size' : 4, },
  'Bundle': {'type': 'object', 'layout' : (
     {'type': 'Int32', 'field_names': ('version', ), },
     ),
  },
  },
'message': {'type': 'Bundle'}
}
#header end
"""
INCORRECT_HDM_HEADER = b"""
# The binary data starts immediately after the '#header end' line.
{
    12
#header end
"""


@patch.object(builtins, "open", new_callable=mock_open, read_data=CORRECT_HDM_HEADER)
def test_hdm_parser_header_loading_success(mock_file_open):
    """Test that HDM parser loads header correctly."""
    expected_result = {
        "message": {"type": "Bundle"},
        "types": {
            "Bundle": {"layout": ({"field_names": ("version",), "type": "Int32"},), "type": "object"},
            "Int32": {"size": 4, "type": "int"},
        },
    }
    hdm_parser = Parser(DUMMY_PATH)

    assert expected_result == hdm_parser.header


@patch.object(builtins, "open", new_callable=mock_open, read_data=INCORRECT_HDM_HEADER)
def test_hdm_parser_header_loading_failure(mock_file_open):
    """Test that HDM parser fails to load header."""
    with pytest.raises(SyntaxError):
        Parser(DUMMY_PATH)
