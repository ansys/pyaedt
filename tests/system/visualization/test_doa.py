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

import warnings

import numpy as np
import pytest

from ansys.aedt.core.internal.checks import ERROR_GRAPHICS_REQUIRED
from ansys.aedt.core.internal.checks import check_graphics_available
from ansys.aedt.core.visualization.advanced.doa import DirectionOfArrival

try:
    check_graphics_available()
except ImportError:
    warnings.warn(ERROR_GRAPHICS_REQUIRED)


@pytest.fixture(scope="module", autouse=True)
def desktop() -> None:
    """Override the desktop fixture to DO NOT open the Desktop when running this test class"""
    return


@pytest.fixture
def basic_doa():
    # Antenna array setup
    freq = 10e9  # Hz
    num_elements_x = 4
    num_elements_y = 4
    d = 0.015
    x = np.tile(np.arange(num_elements_x) * d, num_elements_y)
    y = np.repeat(np.arange(num_elements_y) * d, num_elements_x)
    return DirectionOfArrival(x, y, freq)


def test_initialization_error() -> None:
    x = np.array([0.0, 0.01])
    y = np.array([0.0])
    freq = 10e9
    with pytest.raises(ValueError):
        DirectionOfArrival(x, y, freq)


def test_get_scanning_vectors(basic_doa) -> None:
    azimuths = np.array([-45, 0, 45])
    vectors = basic_doa.get_scanning_vectors(azimuths)
    assert vectors.shape == (basic_doa.elements, len(azimuths))
    assert np.iscomplexobj(vectors)


def test_bartlett(basic_doa) -> None:
    azimuths = np.linspace(-90, 90, 181)
    scanning_vectors = basic_doa.get_scanning_vectors(azimuths)
    signal = np.random.randn(basic_doa.elements) + 1j * np.random.randn(basic_doa.elements)
    data = np.array([signal])
    output = basic_doa.bartlett(data, scanning_vectors)
    assert output.shape == (1, len(azimuths))
    assert np.iscomplexobj(output)


def test_capon(basic_doa) -> None:
    azimuths = np.linspace(-90, 90, 181)
    scanning_vectors = basic_doa.get_scanning_vectors(azimuths)
    signal = np.random.randn(basic_doa.elements) + 1j * np.random.randn(basic_doa.elements)
    data = np.array([signal])
    output = basic_doa.capon(data, scanning_vectors)
    assert output.shape == (1, len(azimuths))
    assert np.isrealobj(output)


def test_music(basic_doa) -> None:
    azimuths = np.linspace(-90, 90, 181)
    scanning_vectors = basic_doa.get_scanning_vectors(azimuths)
    signal = np.random.randn(basic_doa.elements) + 1j * np.random.randn(basic_doa.elements)
    data = np.array([signal])
    output = basic_doa.music(data, scanning_vectors, signal_dimension=1)
    assert output.shape == (1, len(azimuths))
    assert np.isrealobj(output)


def test_invalid_doa_method(basic_doa) -> None:
    signal = np.random.randn(basic_doa.elements) + 1j * np.random.randn(basic_doa.elements)
    with pytest.raises(ValueError):
        basic_doa.plot_angle_of_arrival(signal, doa_method="InvalidMethod")


def test_plot_angle_of_arrival(basic_doa) -> None:
    signal = np.random.randn(basic_doa.elements) + 1j * np.random.randn(basic_doa.elements)
    plotter = basic_doa.plot_angle_of_arrival(signal, doa_method="Bartlett", show=False)
    assert plotter is not None
