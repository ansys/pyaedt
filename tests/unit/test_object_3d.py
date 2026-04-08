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

from unittest.mock import MagicMock
from unittest.mock import patch

import pytest

from ansys.aedt.core.internal.errors import AEDTRuntimeError
from ansys.aedt.core.modeler.cad.object_3d import Object3d


@pytest.fixture
def object_3d_setup():
    """Fixture used to mock the creation of a Object3d instance."""
    with patch("ansys.aedt.core.modeler.cad.object_3d.Object3d.__init__", lambda x: None):
        mock_instance = MagicMock(spec=Object3d)
        yield mock_instance


def test_clone_failure(object_3d_setup) -> None:
    mock_primitives = MagicMock()
    mock_primitives.clone.return_value = [False]
    object_3d = Object3d()
    object_3d._primitives = mock_primitives
    object_3d._m_name = "dummy"
    object_3d._id = 12

    with pytest.raises(AEDTRuntimeError, match="Could not clone the object dummy"):
        object_3d.clone()
