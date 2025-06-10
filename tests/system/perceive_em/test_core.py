# ruff: noqa: E402

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

from pathlib import Path

import pytest

from ansys.aedt.core.perceive_em.core.api_interface import PerceiveEM


def test_real_api_initialization():
    """Test that the PerceiveEM class initializes and loads the real API."""
    em = PerceiveEM()
    assert em.installation_path is not None
    assert isinstance(em.version, str)
    assert isinstance(em.copyright, str)


def test_apply_perceive_license_real():
    em = PerceiveEM()
    assert em.apply_perceive_em_license()


def test_apply_hpc_license_real():
    em1 = PerceiveEM()
    em1.apply_perceive_em_license()
    assert em1.apply_hpc_license(is_pack=True)

    em2 = PerceiveEM()
    em2.apply_perceive_em_license()
    assert em2.apply_hpc_license(is_pack=False)
