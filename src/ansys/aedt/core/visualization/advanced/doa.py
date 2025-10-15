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

import sys

import numpy as np

from ansys.aedt.core.base import PyAedtBase
from ansys.aedt.core.generic.constants import SpeedOfLight
from ansys.aedt.core.generic.general_methods import conversion_function
from ansys.aedt.core.generic.general_methods import pyaedt_function_handler
from ansys.aedt.core.visualization.plot.matplotlib import ReportPlotter

current_python_version = sys.version_info[:2]
if current_python_version < (3, 10):  # pragma: no cover
    raise Exception("Python 3.10 or higher is required for direction of arrival (DoA) post-processing.")


class DirectionOfArrival(PyAedtBase):
    """
    Class for direction of arrival (DoA) estimation using 2D planar antenna arrays
    with coordinates in meters and user-defined frequency.
    """

    def __init__(self, x_position: np.array, y_position: np.array, frequency: float):
        """
        Initialize with antenna element positions in meters and signal frequency in Hertz.

        Parameters
        ----------
        x_position : np.ndarray
            X coordinates of the antenna elements in meters.
        y_position : np.ndarray
            Y coordinates of the antenna elements in meters.
        frequency : float
            Signal frequency in Hertz.
        """
        self.x = np.asarray(x_position)
        self.y = np.asarray(y_position)
        self.elements = len(self.x)
        self.frequency = frequency
        self.wavelength = SpeedOfLight / self.frequency
        self.k = 2 * np.pi / self.wavelength

        if self.elements != len(self.y):
            raise ValueError("X and Y coordinate arrays must have the same length.")

    @pyaedt_function_handler()
    def get_scanning_vectors(self, azimuth_angles: np.ndarray) -> np.ndarray:
        """
        Generate scanning vectors for the given azimuth angles in degrees.

        Parameters
        ----------
        azimuth_angles : np.ndarray
            Incident azimuth angles in degrees.

        Returns
        -------
        scanning_vectors : np.ndarray
            Scanning vectors.
        """
        thetas_rad = np.deg2rad(azimuth_angles)
        P = len(thetas_rad)
        scanning_vectors = np.zeros((self.elements, P), dtype=complex)

        for i in range(P):
            scanning_vectors[:, i] = np.exp(
                1j * self.k * (self.x * np.sin(thetas_rad[i]) + self.y * np.cos(thetas_rad[i]))
            )

        return scanning_vectors

    @pyaedt_function_handler()
    def bartlett(
        self, data: np.ndarray, scanning_vectors: np.ndarray, range_bins: int = None, cross_range_bins: int = None
    ):
        """
        Estimate the direction of arrival (DoA) using the Bartlett (classical beamforming) method.

        Parameters
        ----------
        data : np.ndarray
            Complex-valued array of shape (range_bins, elements), typically output from range FFT.
            Each row represents the antenna data for a specific range bin.
        scanning_vectors : np.ndarray
            Complex matrix of shape (elements, num_angles), where each column corresponds to
            a scanning vector for a different azimuth/elevation angle.
        range_bins : int, optional
            Number of range bins (rows of the output), defaults to the first dimension of `data`.
        cross_range_bins : int, optional
            Number of cross-range (angular) bins, defaults to the second dimension of `scanning_vectors`.

        Returns
        -------
        np.ndarray
            2D complex-valued array of shape (range_bins, cross_range_bins), representing the
            power angular density (PAD) for each range bin and angle.
        """
        if range_bins is None:
            range_bins = data.shape[0]
        if cross_range_bins is None:
            cross_range_bins = scanning_vectors.shape[1]

        scale_factor = scanning_vectors.shape[1] / cross_range_bins
        pad_output = np.zeros((range_bins, cross_range_bins), dtype=complex)

        for n, range_bin_data in enumerate(data):
            range_bin_data = np.reshape(range_bin_data, (1, self.elements))
            correlation_matrix = np.dot(range_bin_data.T, range_bin_data.conj())

            if correlation_matrix.shape[0] != correlation_matrix.shape[1]:
                raise ValueError("Correlation matrix is not square.")
            if correlation_matrix.shape[0] != scanning_vectors.shape[0]:
                raise ValueError("Dimension mismatch between correlation matrix and scanning vectors.")

            pad = np.zeros(scanning_vectors.shape[1], dtype=complex)
            for i in range(scanning_vectors.shape[1]):
                steering_vector = scanning_vectors[:, i]
                pad[i] = steering_vector.conj().T @ correlation_matrix @ steering_vector

            pad_output[n] = pad * scale_factor

        return pad_output

    def capon(
        self, data: np.ndarray, scanning_vectors: np.ndarray, range_bins: int = None, cross_range_bins: int = None
    ) -> np.ndarray:
        """
        Estimate the direction of arrival using the Capon (Minimum variance distortion less response)
        beamforming method.

        Parameters
        ----------
        data : np.ndarray
            Complex-valued array of shape (range_bins, elements), typically output from range FFT.
            Each row represents the antenna data for a specific range bin.
        scanning_vectors : np.ndarray
            Complex matrix of shape (elements, num_angles), where each column corresponds to
            a scanning vector for a different azimuth/elevation angle.
        range_bins : int, optional
            Number of range bins (rows of the output), defaults to the first dimension of `data`.
        cross_range_bins : int, optional
            Number of cross-range (angular) bins, defaults to the second dimension of `scanning_vectors`.

        Returns
        -------
        np.ndarray
            2D real-valued array of shape (range_bins, cross_range_bins), representing the
            Capon spatial spectrum (inverse of interference power) for each range bin and angle.
        """
        if range_bins is None:
            range_bins = data.shape[0]
        if cross_range_bins is None:
            cross_range_bins = scanning_vectors.shape[1]

        scale_factor = scanning_vectors.shape[1] / cross_range_bins
        spectrum_output = np.zeros((range_bins, cross_range_bins), dtype=float)

        for n, range_bin_data in enumerate(data):
            range_bin_data = np.reshape(range_bin_data, (1, self.elements))
            R = range_bin_data.T @ range_bin_data.conj()

            if R.shape[0] != R.shape[1]:
                raise ValueError("Correlation matrix is not square.")
            if R.shape[0] != scanning_vectors.shape[0]:
                raise ValueError("Dimension mismatch between correlation matrix and scanning vectors.")

            try:
                R_inv = np.linalg.inv(R)
            except np.linalg.LinAlgError:
                raise ValueError("Correlation matrix is singular or ill-conditioned.")

            for i in range(cross_range_bins):
                sv = scanning_vectors[:, i]
                denom = np.conj(sv).T @ R_inv @ sv
                spectrum_output[n, i] = scale_factor / np.real(denom)

        return spectrum_output

    @pyaedt_function_handler()
    def music(
        self,
        data: np.ndarray,
        scanning_vectors: np.ndarray,
        signal_dimension: int,
        range_bins: int = None,
        cross_range_bins: int = None,
    ) -> np.ndarray:
        """
        Estimate the direction of arrival (DoA) using the MUSIC method.

        Parameters
        ----------
        data : np.ndarray
            Complex-valued array of shape (range_bins, elements), typically output from range FFT.
            Each row represents the antenna data for a specific range bin.
        scanning_vectors : np.ndarray
            Matrix of shape (elements, num_angles), where each column is a steering vector for a test angle.
        signal_dimension : int
            Number of sources/signals (model order).
        range_bins : int, optional
            Number of range bins to process. Defaults to `data.shape[0]`.
        cross_range_bins : int, optional
            Number of angle bins (scan directions). Defaults to `scanning_vectors.shape[1]`.

        Returns
        -------
        np.ndarray
            2D real-valued array of shape (range_bins, cross_range_bins),
            representing the MUSIC spectrum for each range bin and angle.
        """
        if range_bins is None:
            range_bins = data.shape[0]
        if cross_range_bins is None:
            cross_range_bins = scanning_vectors.shape[1]

        output = np.zeros((range_bins, cross_range_bins), dtype=float)

        for n, snapshot in enumerate(data):
            snapshot = snapshot.reshape((1, self.elements))
            R = np.dot(snapshot.T, snapshot.conj())

            if R.shape[0] != R.shape[1]:
                raise ValueError("Correlation matrix is not square.")
            if R.shape[0] != scanning_vectors.shape[0]:
                raise ValueError("Dimension mismatch between correlation matrix and scanning vectors.")

            try:
                eigenvalues, eigenvectors = np.linalg.eigh(R)
            except np.linalg.LinAlgError:
                raise np.linalg.LinAlgError("Failed to compute eigendecomposition (singular matrix).")

            M = R.shape[0]
            noise_dim = M - signal_dimension
            idx = np.argsort(eigenvalues)
            En = eigenvectors[:, idx[:noise_dim]]  # Noise subspace

            spectrum = np.zeros(cross_range_bins, dtype=float)
            for i in range(cross_range_bins):
                sv = scanning_vectors[:, i]
                denom = np.abs(sv.conj().T @ En @ En.conj().T @ sv)
                spectrum[i] = 0.0 if denom == 0 else 1.0 / denom

            output[n] = spectrum

        return output

    @pyaedt_function_handler()
    def plot_angle_of_arrival(
        self,
        signal: np.ndarray,
        doa_method: str = None,
        field_of_view=None,
        quantity_format: str = None,
        title: str = "Angle of Arrival",
        output_file: str = None,
        show: bool = True,
        show_legend: bool = True,
        plot_size: tuple = (1920, 1440),
        figure=None,
    ):
        """Create angle of arrival plot.

        Parameters
        ----------
        signal : np.ndarray
            Frame number. The default is ``None``, in which case all frames are used.
        doa_method : str, optional
            Method used for direction of arrival estimation.
            Available options are: ``"Bartlett"``, ``"Capon"``, and ``"Music"``.
            The default is ``None``, in which case ``"Bartlett"`` is selected.
        field_of_view : np.ndarray, optional
            Azimuth angular span in degrees to plot. The default is from -90 to 90 dregress.
        quantity_format : str, optional
            Conversion data function. The default is ``None``.
            Available functions are: ``"abs"``, ``"ang"``, ``"dB10"``, ``"dB20"``, ``"deg"``, ``"imag"``, ``"norm"``,
            and ``"real"``.
        title : str, optional
            Title of the plot. The default is ``"Range profile"``.
        output_file : str or :class:`pathlib.Path`, optional
            Full path for the image file. The default is ``None``, in which case an image in not exported.
        show : bool, optional
            Whether to show the plot. The default is ``True``.
            If ``False``, the Matplotlib instance of the plot is shown.
        show_legend : bool, optional
            Whether to display the legend or not. The default is ``True``.
        plot_size : tuple, optional
            Image size in pixel (width, height).
        figure : :class:`matplotlib.pyplot.Figure`, optional
            An existing Matplotlib `Figure` to which the plot is added.
            If not provided, a new `Figure` and `Axes` objects are created.
            Default is ``None``.

        Returns
        -------
        :class:`ansys.aedt.core.visualization.plot.matplotlib.ReportPlotter`
            PyAEDT matplotlib figure object.

        Examples
        --------
        >>> from ansys.aedt.core.visualization.advanced.doa import DirectionOfArrival
        >>> import numpy as np
        >>> freq = 10e9
        >>> signal_angle = 30
        >>> num_elements_x = 4
        >>> num_elements_y = 4
        >>> d = 0.015
        >>> x = np.tile(np.arange(num_elements_x) * d, num_elements_y)
        >>> y = np.repeat(np.arange(num_elements_y) * d, num_elements_x)
        >>> k = 2 * np.pi * freq / 3e8
        >>> signal_vector = np.exp(
        ...     1j * k * (x * np.sin(np.radians(signal_angle)) + y * np.cos(np.radians(signal_angle)))
        ... )
        >>> signal_snapshot = signal_vector + 0.1 * (
        ...     np.random.randn(len(signal_vector)) + 1j * np.random.randn(len(signal_vector))
        ... )
        >>> doa = DirectionOfArrival(x, y, freq)
        >>> doa.plot_angle_of_arrival(signal_snapshot)
        >>> doa.plot_angle_of_arrival(signal_snapshot, doa_method="MUSIC")
        """
        data = np.array([signal])

        if field_of_view is None:
            field_of_view = np.linspace(-90, 90, 181)

        if doa_method is None:
            doa_method = "Bartlett"

        scanning_vectors = self.get_scanning_vectors(field_of_view)

        if doa_method.lower() == "bartlett":
            output = self.bartlett(data, scanning_vectors)
        elif doa_method.lower() == "capon":
            output = self.capon(data, scanning_vectors)
        elif doa_method.lower() == "music":
            output = self.music(data, scanning_vectors, 1)
        else:
            raise ValueError(f"Unknown {doa_method} method.")

        if quantity_format is None:
            quantity_format = "dB20"

        output = conversion_function(output, quantity_format)

        new = ReportPlotter()
        new.show_legend = show_legend
        new.title = title
        new.size = plot_size

        x = field_of_view
        y = output.T

        legend = f"DoA {doa_method}"
        curve = [x.tolist(), y.tolist(), legend]

        # Single plot
        props = {"x_label": "Azimuth (°)", "y_label": "Power"}
        name = curve[2]
        new.add_trace(curve[:2], 0, props, name)
        new.x_margin_factor = 0.0
        new.y_margin_factor = 0.2
        _ = new.plot_2d(None, output_file, show, figure=figure)
        return new
