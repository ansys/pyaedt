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
import sys

current_python_version = sys.version_info[:2]
if current_python_version < (3, 10):  # pragma: no cover
    raise Exception("Python 3.10 or higher is required for direction of arrival (DoA) post-processing.")

import numpy as np


class DirectionOfArrival:
    def __init__(self, virtual_position, wavelength, angle_grid_azimuth, angle_grid_elevation):
        """Provides Direction of Arrival (DoA) methods.

        Parameters
        ----------
        virtual_position : array_like of shape (N_channels, 3)
            Relative positions of virtual array elements.
        wavelength : float
        angle_grid_azimuth : array_like
            Azimuth angles in degrees.
        angle_grid_elevation : array_like
            Elevation angles in degrees.
        """
        self.virtual_position = np.array([virtual_position[ch] for ch in virtual_position])
        self.N_channels = self.virtual_position.shape[0]
        self.wavelength = wavelength
        self.angle_grid_azimuth = angle_grid_azimuth
        self.angle_grid_elevation = angle_grid_elevation

        self.scanning_vectors = self._compute_scanning_vectors()

    def _direction_vector(self, az_deg, el_deg):
        az = np.radians(az_deg)
        el = np.radians(el_deg)
        return np.array([np.cos(el) * np.cos(az), np.cos(el) * np.sin(az), np.sin(el)])

    def _compute_scanning_vectors(self):
        A = len(self.angle_grid_azimuth)
        E = len(self.angle_grid_elevation)
        vectors = np.zeros((self.N_channels, A * E), dtype=complex)

        idx = 0
        for el in self.angle_grid_elevation:
            for az in self.angle_grid_azimuth:
                u = self._direction_vector(az, el)
                phase = 2 * np.pi / self.wavelength * self.virtual_position @ u
                vectors[:, idx] = np.exp(1j * phase)
                idx += 1

        return vectors

    def estimate_bartlett(self, R):
        if R.shape[0] != R.shape[1]:
            raise ValueError("Correlation matrix must be square.")
        if R.shape[0] != self.N_channels:
            raise ValueError(f"Correlation matrix must be of size {self.N_channels}.")
        PAD = np.einsum("ij,ji->i", np.conj(self.scanning_vectors.T) @ R, self.scanning_vectors)
        return PAD.real
