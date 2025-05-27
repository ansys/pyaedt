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
    def __init__(self, pos_tx, pos_rx, wavelength, angle_grid_azimuth):
        """
        pos_tx, pos_rx: arrays (N_tx,3) y (N_rx,3)
        wavelength: float
        angle_grid_azimuth: array de ángulos azimutales en grados
        """
        self.pos_tx = np.array(pos_tx)
        self.pos_rx = np.array(pos_rx)
        self.N_tx = self.pos_tx.shape[0]
        self.N_rx = self.pos_rx.shape[0]
        self.wavelength = wavelength
        self.angle_grid = angle_grid_azimuth
        self.scanning_vectors = self._compute_scanning_vectors()

    def _compute_scanning_vectors(self):
        vectors_tx = np.zeros((self.N_tx, len(self.angle_grid)), dtype=complex)
        vectors_rx = np.zeros((self.N_rx, len(self.angle_grid)), dtype=complex)

        for i, az_deg in enumerate(self.angle_grid):
            az_rad = np.radians(az_deg)
            # Vector unitario dirección en plano XY
            u = np.array([np.cos(az_rad), np.sin(az_rad), 0])  # elevación = 0

            # Producto escalar posición * u para cada antena Tx y Rx
            phase_tx = 2 * np.pi / self.wavelength * self.pos_tx @ u
            phase_rx = 2 * np.pi / self.wavelength * self.pos_rx @ u

            vectors_tx[:, i] = np.exp(1j * phase_tx)
            vectors_rx[:, i] = np.exp(1j * phase_rx)

        scanning_vectors = np.zeros((self.N_tx * self.N_rx, len(self.angle_grid)), dtype=complex)
        for i in range(len(self.angle_grid)):
            scanning_vectors[:, i] = np.kron(vectors_rx[:, i], vectors_tx[:, i])
        return scanning_vectors

    def estimate_bartlett(self, R):
        if R.shape[0] != R.shape[1]:
            raise ValueError("Matriz de correlación debe set cuadrada.")
        if R.shape[0] != self.N_tx * self.N_rx:
            raise ValueError(f"Matriz de correlación debe set de tamaño {(self.N_tx * self.N_rx)}.")
        PAD = np.einsum("ij,ji->i", np.conj(self.scanning_vectors.T) @ R, self.scanning_vectors)
        return PAD.real
