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

from unittest import mock

import pytest

from ansys.aedt.core.internal.filesystem import is_safe_path


@pytest.fixture(scope="module", autouse=True)
def desktop():
    """Override the desktop fixture to DO NOT open the Desktop when running this test class"""
    return


@pytest.mark.parametrize(
    "path, allowed_extensions, expected",
    [
        ("/path/to/file.txt", [".txt", ".pdf"], True),
        ("/path/to/file.exe", [".txt", ".pdf"], False),
        ("/path/to/file.txt", None, True),
        ("/path/to/file.txt", [".pdf"], False),
        ("/path/;rm -rf /file.txt", [".txt"], False),
    ],
)
def test_is_safe_path(path, allowed_extensions, expected):
    """Test the is_safe_path function."""
    with mock.patch("pathlib.Path.exists", return_value=True), mock.patch("pathlib.Path.is_file", return_value=True):
        assert is_safe_path(path, allowed_extensions) == expected

    # Test case for an invalid path
    with mock.patch("pathlib.Path.exists", return_value=False):
        assert not is_safe_path("/invalid/path/file.txt", [".txt"])
