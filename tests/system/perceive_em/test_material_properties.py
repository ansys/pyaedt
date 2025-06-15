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

import pytest

from ansys.aedt.core.perceive_em.modules.material_properties import (
    MaterialProperties,  # Update this with the actual import
)


def test_default_values():
    mat = MaterialProperties()
    assert mat.thickness == -1.0
    assert mat.rel_eps_real == 1.0
    assert mat.rel_eps_imag == 0.0
    assert mat.rel_mu_real == 1.0
    assert mat.rel_mu_imag == 0.0
    assert mat.conductivity == 0.0
    assert mat.height_standard_dev is None
    assert mat.roughness is None
    assert mat.backing is None
    assert mat.coating_idx == 1


def test_from_dict_partial():
    data = {
        "thickness": 0.5,
        "relEpsReal": 2.1,
    }
    mat = MaterialProperties.from_dict(data)
    assert mat.thickness == 0.5
    assert mat.rel_eps_real == 2.1
    assert mat.rel_eps_imag == 0.0  # default
    assert mat.rel_mu_real == 1.0
    assert mat.backing is None


def test_from_dict_full():
    data = {
        "thickness": 0.5,
        "relEpsReal": 2.2,
        "relEpsImag": 0.01,
        "relMuReal": 1.5,
        "relMuImag": 0.001,
        "conductivity": 1000.0,
        "height_standard_dev": 0.01,
        "roughness": 0.005,
        "backing": "metal",
        "coating_idx": 3,
    }
    assert MaterialProperties.from_dict(data)


def test_to_dict_output():
    mat = MaterialProperties(
        thickness=0.7,
        rel_eps_real=3.0,
        rel_eps_imag=0.1,
        rel_mu_real=1.1,
        rel_mu_imag=0.02,
        conductivity=500,
        height_standard_dev=0.002,
        roughness=0.0005,
        backing="polymer",
        coating_idx=2,
    )
    d = mat.to_dict()
    assert d["thickness"] == 0.7
    assert d["relEpsReal"] == 3.0
    assert d["backing"] == "polymer"
    assert d["coating_idx"] == 2


def test_round_trip_conversion():
    original = MaterialProperties(
        thickness=1.0,
        rel_eps_real=2.5,
        rel_eps_imag=0.1,
        rel_mu_real=1.2,
        rel_mu_imag=0.05,
        conductivity=1500,
        height_standard_dev=0.003,
        roughness=0.002,
        backing="foam",
        coating_idx=4,
    )
    converted = MaterialProperties.from_dict(original.to_dict())
    assert original == converted
