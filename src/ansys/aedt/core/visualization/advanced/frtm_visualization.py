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

from scipy.signal import find_peaks

current_python_version = sys.version_info[:2]
if current_python_version < (3, 10):  # pragma: no cover
    raise Exception("Python 3.10 or higher is required for Monostatic RCS post-processing.")

import csv
import time as walltime
import warnings

from ansys.aedt.core.aedt_logger import pyaedt_logger as logger
from ansys.aedt.core.generic.constants import SpeedOfLight
from ansys.aedt.core.generic.general_methods import conversion_function
from ansys.aedt.core.generic.general_methods import pyaedt_function_handler
from ansys.aedt.core.visualization.plot.matplotlib import ReportPlotter

# import matplotlib.pyplot as plt
# from matplotlib.animation import FuncAnimation

try:
    import numpy as np
except ImportError:  # pragma: no cover
    warnings.warn(
        "The NumPy module is required to use module rcs_visualization.py.\n" "Install with \n\npip install numpy"
    )
    np = None

try:
    import pyvista as pv
except ImportError:  # pragma: no cover
    warnings.warn(
        "The PyVista module is required to use module rcs_visualization.py.\n" "Install with \n\npip install pyvista"
    )
    pv = None

try:
    import pandas as pd
except ImportError:  # pragma: no cover
    warnings.warn(
        "The Pandas module is required to use module rcs_visualization.py.\n" "Install with \n\npip install pandas"
    )
    pd = None


class FRTMData(object):
    """Provides FRTM data.

    Read FRTM data and return the Python interface to analyze the data. All units are in SI.

    Parameters
    ----------
    input_file : str
        Data in a FRTM file.

    Examples
    --------
    >>> from ansys.aedt.core.visualization.advanced.frtm_visualization import FR
    >>> file = "RxSignal.frtm"
    >>> data = RangeDopplerData(file)
    """

    def __init__(self, input_file):
        input_file = Path(input_file)

        if not input_file.is_file():
            raise FileNotFoundError("FRTM file does not exist.")

        # Private
        self.__logger = logger
        self.__input_file = input_file
        self.__dlxcd_version = None
        self.__frequency_bandwidth = None
        self.__row_count = None
        self.__col_header1 = None
        self.__col_header2 = None
        self.__binary_record_length = None
        self.__binary_start_byte = None
        self.__binary_byte_type_line = None
        self.__radar_waveform = None
        self.__radar_channels = None
        self.__time_start = None
        self.__time_stop = None
        self.__time_number = None
        self.__time_sweep = None
        self.__pulse_repetition = None
        self.__time_duration = None
        self.__frequency_domain_type = None
        self.__frequency_start = None
        self.__frequency_stop = None
        self.__frequency_numbe = None
        self.__frequency_sweep = None
        self.__frequency_delta = None
        self.__frequency_bandwidth = None
        self.__frequency_center = None
        self.__antenna_names = None
        self.__channel_number = None
        self.__coupling_combos = None
        self.__channel_names = []
        self.__all_data = {}
        self.__data_conversion_function = "dB20"

        self.__read_frtm()

    @property
    def dlxcd_version(self):
        return self.__dlxcd_version

    @property
    def row_count(self):
        return self.__row_count

    @property
    def col_count(self):
        return self.__col_count

    @property
    def col_header1(self):
        return self.__col_header1

    @property
    def col_header2(self):
        return self.__col_header2

    @property
    def binary_record_length(self):
        return self.__binary_record_length

    @property
    def binary_start_byte(self):
        return self.__binary_start_byte

    @property
    def binary_byte_type_line(self):
        return self.__binary_byte_type_line

    @property
    def radar_waveform(self):
        return self.__radar_waveform

    @property
    def radar_channels(self):
        return self.__radar_channels

    @property
    def time_start(self):
        return self.__time_start

    @property
    def time_stop(self):
        return self.__time_stop

    @property
    def time_number(self):
        """Number of pulses for Pulse-Doppler or number of chirps for FMCW radar."""
        return self.__time_number

    @property
    def time_sweep(self):
        return self.__time_sweep

    @property
    def pulse_repetition(self):
        """Pulse repetition."""
        return self.__pulse_repetition

    @property
    def time_duration(self):
        return self.__time_duration

    @property
    def frequency_domain_type(self):
        return self.__frequency_domain_type

    @property
    def frequency_start(self):
        return self.__frequency_start

    @property
    def frequency_stop(self):
        return self.__frequency_stop

    @property
    def frequency_number(self):
        return self.__frequency_number

    @property
    def frequency_sweep(self):
        return self.__frequency_sweep

    @property
    def frequency_delta(self):
        return self.__frequency_delta

    @property
    def frequency_bandwidth(self):
        return self.__frequency_bandwidth

    @property
    def frequency_center(self):
        return self.__frequency_center

    @property
    def antenna_names(self):
        return self.__antenna_names

    @property
    def channel_number(self):
        return self.__channel_number

    @property
    def coupling_combos(self):
        return self.__coupling_combos

    @property
    def channel_names(self):
        return self.__channel_names

    @property
    def all_data(self):
        return self.__all_data

    @property
    def range_resolution(self):
        bw = self.frequency_bandwidth
        rr = SpeedOfLight / 2 / bw
        return rr

    @property
    def range_period(self):
        rr = self.range_resolution
        max_range = rr * self.frequency_number
        if self.col_count != 2:  # I
            max_range = max_range / 2.0
        return max_range

    @property
    def velocity_resolution(self):
        fc = self.frequency_center
        tpt = self.time_duration
        vr = 299792458.0 / (2 * fc * tpt)
        return vr

    @property
    def velocity_period(self):
        vr = self.velocity_resolution
        time_step = self.time_number
        vp = time_step * vr
        return vp

    @pyaedt_function_handler()
    def load_data(self, order="frequency_pulse"):
        """Load and return range doppler data.

        Parameters
        ----------
        order : str, optional
            The order of the data array. It can be either ``"frequency_pulse"`` or ``"pulse_frequency"``.
            ``"frequency_pulse"`` indicates the array order is [frequency_number][pulse_number],
            while ``"pulse_frequency"`` indicates the array order is [pulse_number][frequency_number].
            The choice of order affects many post-processing steps, so choose accordingly.
            The default is ``"frequency_pulse"``.

        Returns
        -------
        dict

        """

        if order.lower() == "frequency_pulse":
            for ch in self.all_data.keys():
                self.__all_data[ch] = self.all_data[ch].T
            return self.all_data
        else:
            return self.all_data

    @property
    def data_conversion_function(self):
        """RCS data conversion function.

        The available functions are:

        - `"dB10"`: Converts the data to decibels using base 10 logarithm.
        - `"dB20"`: Converts the data to decibels using base 20 logarithm.
        - `"abs"`: Computes the absolute value of the data.
        - `"real"`: Computes the real part of the data.
        - `"imag"`: Computes the imaginary part of the data.
        - `"norm"`: Normalizes the data to have values between 0 and 1.
        - `"ang"`: Computes the phase angle of the data in radians.
        - `"ang_deg"`: Computes the phase angle of the data in degrees.
        """
        return self.__data_conversion_function

    @data_conversion_function.setter
    def data_conversion_function(self, val):
        available_functions = ["dB10", "dB20", "abs", "real", "imag", "norm", "ang", "ang_deg", None]
        if val in available_functions:
            self.__data_conversion_function = val

    @pyaedt_function_handler()
    def range_profile(self, data_channel, upsample=1, window=None, window_size=None):
        """
        range profile calculation

        input: 1D array [freq_samples]

        returns: 1D array in original_lenth * upsample

        """
        value = None
        if self.all_data:
            data_conversion_function_original = self.data_conversion_function
            self.data_conversion_function = None
            if not window_size:
                window_size = self.frequency_number

            # Compute window
            win_range, _ = self.window_function(window, window_size)
            windowed_data = data_channel * win_range

            # Perform FFT
            new_frequency_size = window_size * upsample
            windowed_data = np.fft.fftshift(upsample * np.fft.ifft(windowed_data, n=new_frequency_size))

            self.data_conversion_function = data_conversion_function_original
            value = conversion_function(windowed_data, self.data_conversion_function)

        return value

        # nfreq = int(np.shape(np.squeeze(data))[0])
        # # scale factors used for windowing function
        # if window:
        #     win_range = np.hanning(nfreq)
        #     win_range_sum = np.sum(win_range)
        #     sf_rng = len(win_range) / (win_range_sum)
        #     win_range = win_range * sf_rng
        # else:
        #     win_range = 1
        #
        # # perform ifft on each channel
        # pulse_f = data
        # pulse_f_win = np.multiply(pulse_f, win_range)  # apply windowing
        #
        # sf_upsample = nfreq * upsample / nfreq
        # # should probably upsample to closest power of 2 for faster processing, but not going to for now
        # pulse_t_win_up = sf_upsample * ifft(pulse_f_win, n=nfreq * upsample)
        # return pulse_t_win_up

    @staticmethod
    def window_function(window="Flat", size=512):
        """Window function.

        Parameters
        ----------
        window : str, optional.
            Window function. The default is ``"Flat"``. Options are ``"Flat"``, ``"Hamming``", and ``"Hann"``.
        size : int, optional
            Window size. The default is ``512``.

        Returns
        -------
        tuple
            Data windowed and data sum.
        """
        if window is None or window == "Flat":
            win = np.ones(size)
        elif window == "Hann":
            win = np.hanning(size)
        elif window == "Hamming":
            win = np.hamming(size)
        else:
            raise ValueError(f"Window function {window} not supported.")

        win_sum = np.sum(win)
        win *= size / win_sum
        return win, win_sum

    @pyaedt_function_handler()
    def range_doppler_map(self, channel, size=(256, 256)):
        """
        Calculate the range-doppler map.

        Parameters
        ----------
        channel : str
            The channel name to process.
        size : tuple of int, optional
            Desired output size in (ndoppler, nrange). The default is ``(256, 256)``.

        Returns
        -------
        tuple
            A tuple containing:
            - 2D numpy array: The range-Doppler map in [range][doppler].
            - int: Reserved for future use, currently returns 0.
            - float: Frames per second (FPS) of the processing.
        """

        time_before = walltime.time()

        # I think something is wrong with data being returned as opposite, freq and pulse are swapped
        frequency_number = int(np.shape(self.all_data[channel])[0])
        time_number = int(np.shape(self.all_data[channel])[1])

        range_pixels = size[0]
        doppler_pixels = size[1]

        h_dop = np.hanning(time_number)
        sf_dop = len(h_dop) / np.sum(h_dop)
        sf_upsample_dop = doppler_pixels / time_number

        h_rng = np.hanning(frequency_number)
        sf_rng = len(h_rng) / np.sum(h_rng)
        sf_upsample_rng = range_pixels / frequency_number

        h_dop = h_dop * sf_rng
        h_rng = h_rng * sf_dop

        fp_win = sf_upsample_dop * np.multiply(self.all_data[channel], h_dop)
        s1 = np.fft.ifft(fp_win, n=doppler_pixels)
        s1 = np.rot90(s1)

        s1_win = sf_upsample_rng * np.multiply(h_rng, s1)
        s2 = np.fft.ifft(s1_win, n=range_pixels)
        s2 = np.rot90(s2)
        s2_shift = np.fft.fftshift(s2, axes=1)
        # range_doppler = np.flipud(s2_shift)
        range_doppler = np.flipud(s2_shift)
        # range_doppler=s2_shift
        time_after = walltime.time()
        duration_time = time_after - time_before
        if duration_time == 0:
            duration_time = 1
        duration_fps = 1 / duration_time

        rp = 0
        return range_doppler, rp, duration_fps

    @pyaedt_function_handler()
    def convert_frequency_pulse_to_range_pulse(self, data, output_size=256, pulse=None):
        """
        Convert frequency-pulse data to range-pulse data.

        Parameters
        ----------
        data : 3D array
            Input data array with dimensions [channel][freq_samples][pulses].
        output_size : int, optional
            Desired output size in range dimensions. Default is 256.
        pulse : int, optional
            Pulse index to use. If None, the center pulse is used. Default is None.

        Returns
        -------
        3D array
            Converted data array with dimensions [channel][range].
        """

        range_pixels = output_size

        # input shape
        rng_dims = np.shape(data)[1]
        dop_dims = np.shape(data)[2]

        if pulse is None:
            pulse = int(dop_dims / 2)
        else:
            pulse = int(pulse)

        freq_ch = np.swapaxes(data, 0, 2)
        freq_ch = freq_ch[pulse]  # only extract this pulse
        ch_freq = np.swapaxes(freq_ch, 0, 1)

        # window
        h_rng = np.hanning(rng_dims)
        sf_rng = len(h_rng) / np.sum(h_rng)
        sf_upsample_rng = range_pixels / rng_dims
        h_rng = h_rng * sf_rng

        # apply windowing
        ch_freq_win = sf_upsample_rng * np.multiply(ch_freq, h_rng)

        # take fft
        # [ch][range][dop] fft across dop dimensions
        ch_rng_win = np.fft.ifft(ch_freq_win, n=range_pixels)
        ch_rng_win = np.fliplr(ch_rng_win)

        return ch_rng_win

    @pyaedt_function_handler()
    def range_angle_map(
        self,
        data,
        antenna_spacing=0.5,
        source_data="range_doppler",
        doa_method="fft",
        field_of_view=None,
        out_size=(256, 256),
        range_bin_idx=-1,
    ):
        """
        Calculate the range-angle map.

        Parameters
        ----------
        data : numpy.ndarray
            3D array of input data. Format can be [channel][freq_samples][pulses] for FreqPulse mode
            or [channel][range][doppler] for RangeDoppler mode.
        antenna_spacing : float, optional
            Spacing between antennas in wavelengths. Default is 0.5.
        source_data : str, optional
            Source data format. Can be 'range_doppler' or 'frequency_pulse'. Default is 'range_doppler'.
        doa_method : str, optional
            Direction of Arrival (DoA) method. Options are 'fft', 'bartlett', 'capon', 'mem', 'music'.
            Default is 'fft'.
        field_of_view : list of float, optional
            Field of view in degrees. Default is [-90, 90].
        out_size : tuple of int, optional
            Output size in (range, cross-range). Default is (256, 256).
        range_bin_idx : int, optional
            Index of the specific range bin to process. Default is -1 (process all range bins).

        Returns
        -------
        numpy.ndarray
            2D array of size [range][cross-range] representing the range-angle map.
        float
            Frames per second (FPS) of the processing.
        """
        if field_of_view is None:
            field_of_view = [-90, 90]

        time_before = walltime.time()

        range_pixels = out_size[0]
        xrPixels = out_size[1]

        xrng_dims = np.shape(data)[0]
        nchannel = xrng_dims

        doa_method = doa_method.lower()
        rng_xrng = None
        range_bin = None
        if source_data == "frequency_pulse":
            ch_range = self.convert_frequency_pulse_to_range_pulse(data, output_size=range_pixels)
            if doa_method == "fft":
                h_xrng = np.hanning(xrng_dims)
                sf_xrng = len(h_xrng) / np.sum(h_xrng)
                sf_upsample_xrng = xrPixels / xrng_dims

                h_xrng = np.atleast_2d(h_xrng * sf_xrng)

                rng_ch_win = sf_upsample_xrng * np.multiply(ch_range, h_xrng.T)
                rng_ch_win = rng_ch_win.T  # correct order after multiplication (same as swapaxes)
                rng_xrng = np.fft.ifft(rng_ch_win, n=xrPixels)
                rng_xrng = np.fft.fftshift(rng_xrng, axes=1)

            else:
                # for DoA_method = bartlett, capon mem and music
                ang_stop = field_of_view[1] + 90  # offset fov because beam search is from 0 to 180
                ang_start = field_of_view[0] + 90
                range_ch = np.swapaxes(ch_range, 0, 1)
                array_alignment = np.arange(0, nchannel, 1) * antenna_spacing
                incident_angles = np.linspace(ang_start, ang_stop, num=xrPixels)
                ula_scanning_vectors = self.generate_ula_scanning_vectors(array_alignment, incident_angles)
                sf = len(incident_angles) / xrng_dims
                if range_bin_idx != -1:  # do only specific range bin
                    range_pixels = 1
                    range_ch = np.atleast_2d(range_ch[range_bin_idx])

                rng_xrng = np.zeros((range_pixels, xrPixels), dtype=complex)  # (pulse,range)
                for n, rb in enumerate(range_ch):  # if range bin is specified it will only go once
                    ## R matrix calculation
                    rb = np.reshape(rb, (1, nchannel))
                    # R = de.corr_matrix_estimate(rb, imp="fast")
                    R = np.outer(rb, rb.conj())
                    # R = de.forward_backward_avg(R)
                    if doa_method == "bartlett":
                        range_bin = self.DOA_Bartlett(R, ula_scanning_vectors)
                    elif doa_method == "capon":
                        range_bin = self.DOA_Capon(R, ula_scanning_vectors)
                    elif doa_method == "mem":
                        range_bin = self.DOA_MEM(R, ula_scanning_vectors, column_select=0)
                    elif doa_method == "music":
                        range_bin = self.DOA_MUSIC(R, ula_scanning_vectors, signal_dimension=1)
                    if range_bin is None:
                        self.__logger.error(f"Invalid DoA method {doa_method}.")
                        return
                    rng_xrng[n] = range_bin * sf

        elif source_data == "range_doppler":
            if doa_method == "fft":
                # fft to get to range vs pulse
                ch_rng_pulse = np.fft.fft(data)
                ch_rng_pulse = np.fft.fftshift(ch_rng_pulse, axes=2)
                ch_rng_pulse = np.fliplr(ch_rng_pulse)

                rng_dims = np.shape(ch_rng_pulse)[1]
                dop_dims = np.shape(ch_rng_pulse)[2]

                range_ch = np.swapaxes(data, 2, 0)
                range_ch = np.fliplr(range_ch)
                range_ch = range_ch[int(dop_dims / 2)]

                ch_range = np.swapaxes(range_ch, 0, 1)

                h_xrng = np.hanning(xrng_dims)
                sf_xrng = len(h_xrng) / np.sum(h_xrng)
                sf_upsample_xrng = xrPixels / xrng_dims

                h_xrng = np.atleast_2d(h_xrng * sf_xrng)

                rng_ch_win = np.multiply(ch_range, h_xrng.T)
                rng_ch_win = rng_ch_win.T  # correct order after multiplication (same as swapaxes)
                rng_xrng = np.fft.ifft(rng_ch_win, n=xrPixels)

                rng_xrng = np.fft.fftshift(rng_xrng, axes=1)
            else:  # for DoA_method = bartlett, capon mem and music
                rng_dims = np.shape(data)[1]
                dop_dims = np.shape(data)[2]
                xrng_dims = np.shape(data)[0]

                ch_rng_pulse = np.fft.fft(data)
                ch_rng_pulse = np.fft.fftshift(ch_rng_pulse, axes=2)
                ch_rng_pulse = np.fliplr(ch_rng_pulse)

                range_ch = np.swapaxes(ch_rng_pulse, 2, 0)
                range_ch = range_ch[int(dop_dims / 2)]

                ang_stop = field_of_view[1] + 90  # offset fov because beam search is from 0 to 180
                ang_start = field_of_view[0] + 90
                array_alignment = np.arange(0, nchannel, 1) * antenna_spacing
                incident_angles = np.linspace(ang_start, ang_stop, num=xrPixels)
                ula_scanning_vectors = self.generate_ula_scanning_vectors(array_alignment, incident_angles)

                sf = len(incident_angles) / xrng_dims
                if range_bin_idx != -1:  # do only specific range bin
                    rng_dims = 1
                    range_ch = np.atleast_2d(range_ch[range_bin_idx])
                rng_xrng = np.zeros((rng_dims, xrPixels), dtype=complex)  # (pulse,range)
                for n, rb in enumerate(range_ch):
                    ## R matrix calculation
                    rb = np.reshape(rb, (1, nchannel))
                    # R = de.corr_matrix_estimate(rb, imp="fast")
                    R = np.outer(rb, rb.conj())
                    # R = de.forward_backward_avg(R)
                    if doa_method == "bartlett":
                        range_bin = self.DOA_Bartlett(R, ula_scanning_vectors)
                    elif doa_method == "capon":
                        range_bin = self.DOA_Capon(R, ula_scanning_vectors)
                    elif doa_method == "mem":
                        range_bin = self.DOA_MEM(R, ula_scanning_vectors, column_select=0)
                    elif doa_method == "music":
                        range_bin = self.DOA_MUSIC(R, ula_scanning_vectors, signal_dimension=1)

                    if range_bin is None:
                        self.__logger.error(f"Invalid DoA method {doa_method}.")

                    rng_xrng[n] = range_bin * sf

        if rng_xrng is None:
            return

        rng_xrng = np.flipud(rng_xrng)

        time_after = walltime.time()
        duration_time = time_after - time_before
        if duration_time == 0:
            duration_time = 1
        duration_fps = 1 / duration_time

        return rng_xrng, duration_fps

    @pyaedt_function_handler()
    def generate_ula_scanning_vectors(self, array_alignment, thetas):
        """
        Generate scanning vectors for Uniform Linear Array (ULA) antenna systems.

        Parameters
        ----------
        array_alignment : numpy.ndarray
            A 1D array containing the distances between the antenna elements.
            e.g., [0, 0.5*lambda, 1*lambda, ...]
        thetas : numpy.ndarray
            A 1D array containing the incident angles in degrees.
            e.g., [0, 1, 2, ..., 180]

        Returns
        -------
        numpy.ndarray
            A 2D array of complex numbers with shape (M, P), where M is the number of antenna elements
            and P is the number of incident angles. Each column represents a scanning vector for a specific angle.
        """
        M = np.size(array_alignment, 0)  # Number of antenna elements
        scanning_vectors = np.zeros((M, np.size(thetas)), dtype=complex)
        for i in range(np.size(thetas)):
            scanning_vectors[:, i] = np.exp(array_alignment * 1j * 2 * np.pi * np.cos(np.radians(thetas[i])))

        return scanning_vectors

    @pyaedt_function_handler()
    def create_target_list(
        self,
        rd_all_channels_az=None,
        rd_all_channels_el=None,
        rngDomain=None,
        velDomain=None,
        azPixels=256,
        elPixels=256,
        antenna_spacing_wl=0.5,
        radar_fov=[-90, 90],
        centerFreq=76.5e9,
        rcs_min_detect=0,
        min_detect_range=7.5,
        rel_peak_threshold=1e-2,
        max_detections=100,
        return_cfar=False,
    ):

        if rd_all_channels_el is None:
            includes_elevation = False
        else:
            includes_elevation = True

        time_before_target_list = walltime.time()
        target_list = {}
        # this CA_CFAR is too slow, doing to just use local peak detection instead
        # rd_cfar, cfar_fps = pp.CA_CFAR(rd, win_len=50,win_width=50,guard_len=10,guard_width=10, threshold=20)
        rd_cfar, fps_cfar = self.peak_detector2(
            rd_all_channels_az[0], max_detections=max_detections, threshold_rel=rel_peak_threshold
        )
        target_index = np.where(rd_cfar == 1)  # any where there is a hit, get the index of that location
        num_targets = len(target_index[0])
        if num_targets == 0:
            print("no targets")
            target_list = None

        hit_idx = 0  # some hit targets may generate multiple hits (ie, multiple at same range, but different azimuth)
        for hit in range(num_targets):

            loc_dict = {}
            ddim_idx = target_index[1][hit]  # index  in doopper dimension
            rdim_idx = target_index[0][hit]  # index  in range dimension
            doa_az, all_doa_az_bins = self.target_DOA_estimation(
                rd_all_channels_az,
                azPixels,
                rdim_idx,
                ddim_idx,
                antenna_spacing_wl=antenna_spacing_wl,
                fov=radar_fov,
                DOA_method="Bartlett",
            )

            if includes_elevation == False:
                doa_el = 0
                all_doa_el_bins = [0]
            elif len(rd_all_channels_el) < 2:  # needs to have at least 2 channel to get elevation
                doa_el = 0
                all_doa_el_bins = [0]
            else:
                doa_el, all_doa_el_bins = target_DOA_estimation(
                    rd_all_channels_el, elPixels, rdim_idx, ddim_idx, fov=[radar_fov[0], 0], DOA_method="Bartlett"
                )

            R_dist = rngDomain[rdim_idx]  # get range at index where peak/hit was detected
            loc_dict["range"] = R_dist
            # ignore hits that are closer than this distance and further than 90%of max range
            # for doa_az_peak in all_doa_az_bins:
            #     for doa_el_peak in all_doa_el_bins:
            if (loc_dict["range"] > min_detect_range) and (loc_dict["range"] < np.max(rngDomain) * 0.9):
                loc_dict["azimuth"] = doa_az  # in degrees
                loc_dict["elevation"] = doa_el
                loc_dict["cross_range_dist"] = rngDomain[rdim_idx] * np.sin(doa_az * np.pi / 180)
                loc_dict["xpos"] = R_dist * np.cos(
                    doa_az * np.pi / 180
                )  # this is distance as defined in +x in front of sensor
                loc_dict["ypos"] = R_dist * np.sin(doa_az * np.pi / 180)  # +y and -y is cross range dimenionson,
                loc_dict["zpos"] = R_dist * np.sin(doa_el * np.pi / 180)
                loc_dict["velocity"] = velDomain[ddim_idx]
                Pr = np.abs(rd_all_channels_az[0][rdim_idx][ddim_idx])
                loc_dict["p_received"] = Pr
                Pr_dB = 10 * np.log10(Pr)
                # TODO get transmit power from API
                Pt = 1  # 1Watt, input power, 0dBw is source power
                Pt_dB = 10 * np.log10(Pt)

                # user radar range equation to scale results by range to get relative rcs
                # is there a better way to do this? This will not work for objects in near field
                # gain used in dB, should probably use the actual antenna pattern gain,
                # but
                # this
                # will
                # be
                # used
                # for testing
                #     Gt = 10.67  # this is about the gain for hpbw =120deg
                Gr = 10.67
                # radar range equation in dB
                rcs_scaled_dB = (
                    Pr_dB
                    + 30 * np.log10(4 * np.pi)
                    + 40 * np.log10(R_dist)
                    - (Pt_dB + Gt + Gr + 20 * np.log10(3e8 / (centerFreq)))
                )
                if rcs_scaled_dB > rcs_min_detect:  # only add if peak rcs is above min value specified
                    loc_dict["rcs"] = rcs_scaled_dB
                    target_list[hit_idx] = deepcopy(loc_dict)
                    hit_idx += 1
                    # target_list['original_time_index'] = time
        # if target recorded, add it to the list

        time_after_target_list = walltime.time()
        time_target_list = time_after_target_list - time_before_target_list
        if time_target_list == 0:
            time_target_list = 1
        fps_target_list = 1 / time_target_list

        if return_cfar:
            return target_list, fps_target_list, rd_cfar
        else:
            return target_list, fps_target_list

    @pyaedt_function_handler()
    def peak_detector2(self, data, max_detections=20, threshold_rel=1e-2):
        time_before = walltime.time()
        size = np.shape(data)
        if len(size) > 2:
            data = data[0]

        data = np.abs(data)
        coordinates, properties = find_peaks(data.flatten(), distance=5, height=threshold_rel * data.max())
        coordinates = np.column_stack(np.unravel_index(coordinates, data.shape))

        # Sort peaks by height and select the top max_detections peaks
        if len(properties["peak_heights"]) > max_detections:
            sorted_indices = np.argsort(properties["peak_heights"])[-max_detections:]
            coordinates = coordinates[sorted_indices]

        peak_mask = np.zeros_like(data, dtype=bool)
        peak_mask[tuple(coordinates.T)] = True

        time_after = walltime.time()
        duration_time = time_after - time_before
        if duration_time == 0:
            duration_time = 1
        duration_fps = 1 / duration_time

        return peak_mask.astype(int), duration_fps

    @pyaedt_function_handler()
    def target_DOA_estimation(
        data, xrPixels, range_idx, doppler_idx, fov=[-90, 90], antenna_spacing_wl=0.5, DOA_method="Bartlett"
    ):
        """
            Performs DOA (Direction of Arrival) estimation for the given hits.
            To speed up the calculation for multiple
            hits this function requires the calculated range-Doppler maps from all the surveillance channels.

        Parameters:
        -----------
            :param: rd_maps: range-Doppler matrices from which the azimuth vector can be extracted
            :param: hit_list: Contains the delay and Doppler coordinates of the targets.
            :param: DOA_method: Name of the required algorithm to use for the estimation
            :param: array_alignment: One dimensional array, which describes the active antenna positions

            :type : rd_maps: complex valued numpy array with the size of  Μ x D x R , where R is equal to
                                    the number of range cells, and D denotes the number of Doppler cells.
            :type: hit_list: Python list [[delay1, Doppler1],[delay2, Doppler2]...].
            :type: DOA_method: string
            :type: array_alignment: real valued numpy array with size of 1 x M, where M is the number of
                                surveillance antenna channels.

        Return values:
        --------------
            target_doa : Measured incident angles of the targets

        TODO: Extend with decorrelation support
        """
        size = np.shape(data)
        doa_list = []  # This list will contains the measured DOA values
        nchannel = int(size[0])

        ang_stop = fov[1] + 90  # offset fov because beam search is from 0 to 180
        ang_start = fov[0] + 90

        array_alignment = np.arange(0, nchannel, 1) * antenna_spacing_wl

        incident_angles = np.linspace(ang_start, ang_stop, num=xrPixels)
        ula_scanning_vectors = self.generate_ula_scanning_vectors(array_alignment, incident_angles)
        DOA_method = DOA_method.lower()
        azimuth_vector = data[:, range_idx, doppler_idx]
        R = np.outer(azimuth_vector, azimuth_vector.conj())
        if DOA_method == "bartlett":
            doa_res = de.DOA_Bartlett(R, ula_scanning_vectors)
        elif DOA_method == "capon":
            doa_res = de.DOA_Capon(R, ula_scanning_vectors)
        elif DOA_method == "mem":
            doa_res = de.DOA_MEM(R, ula_scanning_vectors, column_select=0)
        elif DOA_method == "music":
            doa_res = de.DOA_MUSIC(R, ula_scanning_vectors, signal_dimension=1)

        doa_res_abs = np.abs(doa_res)
        max_location = np.argmax(doa_res_abs)
        # this is slowing down post processing and is not currently used
        # commenting out for now
        # max_value = np.max(doa_res_abs)
        # peaks_indices = find_peaks(doa_res_abs)
        # peaks_indices = peaks_indices[0]
        # peaks_values = doa_res_abs[peaks_indices]
        # #find_peaks does not identify peaks and start or end of data set. I'll
        # #check if the max value is not in the peak dataset, if it isn't add it
        # if max_location not in peaks_indices:
        #     peaks_indices = np.append(peaks_indices,max_location)
        #     peaks_values = np.append(peaks_values,max_value)
        # peaks = list(zip(peaks_indices, peaks_values))
        # peaks = np.array(peaks)

        # threshold = 0.9 * max_value

        # filtered_peaks_indices = [int(index) for index, value in peaks if value > threshold]

        # minus 90 because original scan was 0 to 180,
        # coordinate sys for osi would mean these angles are reversed
        # assumes the Y axis is to the left if the vehicke is looking forward
        hit_doa = -1 * (incident_angles[max_location] - 90)
        # hit_doa_all = -1*(incident_angles[filtered_peaks_indices]-90)
        hit_doa_all = []
        return hit_doa, hit_doa_all

    def DOA_Bartlett(self, R, scanning_vectors):
        """
                     Fourier(Bartlett) - DIRECTION OF ARRIVAL ESTIMATION



         Description:
         ------------
            The function implements the Bartlett method for direction estimation

            Calculation method :
                                                               H
                             PAD(theta) = S(theta) * R_xx * S(theta)


         Parameters:
         -----------

             :param R: spatial correlation matrix
             :param scanning_vectors : Generated using the array alignment and the incident angles

             :type R: 2D numpy array with size of M x M, where M is the number of antennas in the antenna system
             :type scanning vectors: 2D numpy array with size: M x P, where P is the number of incident angles

        Return values:
        --------------

             :return PAD: Angular distribution of the power ("Power angular densitiy"- not normalized to 1 deg)
             :rtype PAD: numpy array

             :return -1, -1: Input spatial correlation matrix is not quadratic
             :return -2, -2: dimension of R not equal with dimension of the antenna array

        """

        # --- Parameters ---

        # --> Input check
        if np.size(R, 0) != np.size(R, 1):
            print("ERROR: Correlation matrix is not quadratic")
            return -1, -1

        if np.size(R, 0) != np.size(scanning_vectors, 0):
            print("ERROR: Correlation matrix dimension does not match with the antenna array dimension")
            return -2, -2

        PAD = np.zeros(np.size(scanning_vectors, 1), dtype=complex)

        # --- Calculation ---
        theta_index = 0
        for i in range(np.size(scanning_vectors, 1)):
            S_theta_ = scanning_vectors[:, i]
            PAD[theta_index] = np.dot(np.conj(S_theta_), np.dot(R, S_theta_))
            theta_index += 1

        return PAD

    def DOA_Capon(self, R, scanning_vectors):
        """
                     Capon's method - DIRECTION OF ARRIVAL ESTIMATION



         Description:
         ------------
             The function implements Capon's direction of arrival estimation method

             Calculation method :

                                                   1
                           SINR(theta) = ---------------------------
                                             H        -1
                                      S(theta) * R_xx * S(theta)

         Parameters:
         -----------
             :param R: spatial correlation matrix
             :param scanning_vectors : Generated using the array alignment and the incident angles

             :type R: 2D numpy array with size of M x M, where M is the number of antennas in the antenna system
             :type scanning vectors: 2D numpy array with size: M x P, where P is the number of incident angles

        Return values:
        --------------

             :return ADSINR:  Angular dependenet signal to noise ratio
             :rtype ADSINR: numpy array

             :return -1, -1: Input spatial correlation matrix is not quadratic
             :return -2, -2: dimension of R not equal with dimension of the antenna array
             :return -3, -3: Spatial correlation matrix is singular
        """
        # --- Parameters ---

        # --> Input check
        if np.size(R, 0) != np.size(R, 1):
            print("ERROR: Correlation matrix is not quadratic")
            return -1, -1
        if np.size(R, 0) != np.size(scanning_vectors, 0):
            print("ERROR: Correlation matrix dimension does not match with the antenna array dimension")
            return -2, -2

        ADSINR = np.zeros(np.size(scanning_vectors, 1), dtype=complex)

        # --- Calculation ---
        try:
            R_inv = np.linalg.inv(R)  # invert the cross correlation matrix
        except:
            print("ERROR: Singular matrix")
            return -3, -3

        theta_index = 0
        for i in range(np.size(scanning_vectors, 1)):
            S_theta_ = scanning_vectors[:, i]
            ADSINR[theta_index] = np.dot(np.conj(S_theta_), np.dot(R_inv, S_theta_))
            theta_index += 1

        ADSINR = np.reciprocal(ADSINR)

        return ADSINR

    def DOA_MEM(self, R, scanning_vectors, column_select=0):
        """
                     Maximum Entropy Method - DIRECTION OF ARRIVAL ESTIMATION



         Description:
          ------------
             The function implements the MEM method for direction estimation


             Calculation method :

                                                   1
                         PAD(theta) = ---------------------------
                                              H        H
                                       S(theta) * rj rj  * S(theta)
         Parameters:
         -----------
             :param R: spatial correlation matrix
             :param scanning_vectors : Generated using the array alignment and the incident angles
             :param column_select: Selects the column of the R matrix used in the MEM algorithm (default : 0)

             :type R: 2D numpy array with size of M x M, where M is the number of antennas in the antenna system
             :type scanning vectors: 2D numpy array with size: M x P, where P is the number of incident angles
             :type column_select: int

        Return values:
        --------------

             :return PAD: Angular distribution of the power ("Power angular densitiy"- not normalized to 1 deg)
             :rtype : numpy array

             :return -1, -1: Input spatial correlation matrix is not quadratic
             :return -2, -2: dimension of R not equal with dimension of the antenna array
             :return -3, -3: Spatial correlation matrix is singular
        """
        # --- Parameters ---

        # --> Input check
        if np.size(R, 0) != np.size(R, 1):
            print("ERROR: Correlation matrix is not quadratic")
            return -1, -1

        if np.size(R, 0) != np.size(scanning_vectors, 0):
            print("ERROR: Correlation matrix dimension does not match with the antenna array dimension")
            return -2, -2

        PAD = np.zeros(np.size(scanning_vectors, 1), dtype=complex)

        # --- Calculation ---
        try:
            R_inv = np.linalg.inv(R)  # invert the cross correlation matrix
        except:
            print("ERROR: Singular matrix")
            return -3, -3

        # Create matrix from one of the column of the cross correlation matrix with
        # dyadic multiplication
        R_invc = np.outer(R_inv[:, column_select], np.conj(R_inv[:, column_select]))

        theta_index = 0
        for i in range(np.size(scanning_vectors, 1)):
            S_theta_ = scanning_vectors[:, i]
            PAD[theta_index] = np.dot(np.conj(S_theta_), np.dot(R_invc, S_theta_))
            theta_index += 1

        PAD = np.reciprocal(PAD)

        return PAD

    def DOA_LPM(self, R, scanning_vectors, element_select, angle_resolution=1):
        """
                     LPM - Linear Prediction method



         Description:
          ------------
            The function implements the Linear prediction method for direction estimation

            Calculation method :
                                                   H    -1
                                                  U    R    U
                         PLP(theta) = ---------------------------
                                           |    H   -1           |2
                                           |   U * R  * S(theta) |


         Parameters:
         -----------
             :param R: spatial correlation matrix
             :param scanning_vectors : Generated using the array alignment and the incident angles
             :param element_select: Antenna element index used for the predection.
             :param angle_resolution: Angle resolution of scanning vector s(theta) [deg] (default : 1)

             :type R: 2D numpy array with size of M x M, where M is the number of antennas in the antenna system
             :type scanning vectors: 2D numpy array with size: M x P, where P is the number of incident angles
             :type element_select: int
             :type angle_resolution: float

        Return values:
        --------------

             :return PLP : Angular distribution of the power ("Power angular densitiy"- not normalized to 1 deg)
             :rtype : numpy array

             :return -1, -1: Input spatial correlation matrix is not quadratic
             :return -2, -2: dimension of R not equal with dimension of the antenna array
             :return -3, -3: Spatial correlation matrix is singular
        """
        # --- Parameters ---

        # --> Input check
        if np.size(R, 0) != np.size(R, 1):
            print("ERROR: Correlation matrix is not quadratic")
            return -1, -1

        if np.size(R, 0) != np.size(scanning_vectors, 0):
            print("ERROR: Correlation matrix dimension does not match with the antenna array dimension")
            return -2, -2

        PLP = np.zeros(np.size(scanning_vectors, 1), dtype=complex)

        # --- Calculation ---
        try:
            R_inv = np.linalg.inv(R)  # invert the cross correlation matrix
        except:
            print("ERROR: Singular matrix")
            return -3, -3

        R_inv = np.matrix(R_inv)
        M = np.size(scanning_vectors, 0)

        # Create element selector vector
        u = np.zeros(M, dtype=complex)
        u[element_select] = 1
        u = np.matrix(u).getT()

        theta_index = 0
        for i in range(np.size(scanning_vectors, 1)):
            S_theta_ = scanning_vectors[:, i]
            S_theta_ = np.matrix(S_theta_).getT()
            PLP[theta_index] = np.real(u.getH() * R_inv * u) / np.abs(u.getH() * R_inv * S_theta_) ** 2
            theta_index += 1

        return PLP

    def DOA_MUSIC(self, R, scanning_vectors, signal_dimension, angle_resolution=1):
        """
                     MUSIC - Multiple Signal Classification method



         Description:
          ------------
            The function implements the MUSIC method for direction estimation

            Calculation method :

                                                     1
                         ADORT(theta) = ---------------------------
                                              H        H
                                       S(theta) * En En  * S(theta)
          Parameters:
         -----------
             :param R: spatial correlation matrix
             :param scanning_vectors : Generated using the array alignment and the incident angles
             :param signal_dimension:  Number of signal sources

             :type R: 2D numpy array with size of M x M, where M is the number of antennas in the antenna system
             :type scanning vectors: 2D numpy array with size: M x P, where P is the number of incident angles
             :type signal_dimension: int

        Return values:
        --------------

             :return  ADORT : Angular dependent orthogonality.
              Expresses the orthogonality of the current steering vector to the noise subspace
             :rtype : numpy array

             :return -1, -1: Input spatial correlation matrix is not quadratic
             :return -2, -2: dimension of R not equal with dimension of the antenna array
             :return -3, -3: Spatial correlation matrix is singular
        """
        # --- Parameters ---

        # --> Input check
        if np.size(R, 0) != np.size(R, 1):
            print("ERROR: Correlation matrix is not quadratic")
            return -1, -1

        if np.size(R, 0) != np.size(scanning_vectors, 0):
            print("ERROR: Correlation matrix dimension does not match with the antenna array dimension")
            return -2, -2

        ADORT = np.zeros(np.size(scanning_vectors, 1), dtype=complex)
        M = np.size(R, 0)

        # --- Calculation ---
        # Determine eigenvectors and eigenvalues
        sigmai, vi = lin.eig(R)
        # Sorting
        eig_array = []
        for i in range(M):
            eig_array.append([np.abs(sigmai[i]), vi[:, i]])
        eig_array = sorted(eig_array, key=lambda eig_array: eig_array[0], reverse=False)

        # Generate noise subspace matrix
        noise_dimension = M - signal_dimension
        E = np.zeros((M, noise_dimension), dtype=complex)
        for i in range(noise_dimension):
            E[:, i] = eig_array[i][1]

        E = np.matrix(E)

        theta_index = 0
        for i in range(np.size(scanning_vectors, 1)):
            S_theta_ = scanning_vectors[:, i]
            S_theta_ = np.matrix(S_theta_).getT()
            ADORT[theta_index] = 1 / np.abs(S_theta_.getH() * (E * E.getH()) * S_theta_)
            theta_index += 1

        return ADORT

    def DOAMD_MUSIC(
        self,
        R,
        array_alignment,
        signal_dimension,
        coherent_sources=2,
        angle_resolution=1,
    ):
        """
                     MD-MUSIC - Multi Dimensional Multiple Signal Classification method



          Description:
          ------------
            The function implements the MD-MUSIC method for direction estimation

            Calculation method :

                                                     1
                         ADORT(theta) = ---------------------------
                                             H H       H
                                            A*c * En En  * A c

                         A  - Array response matrix
                         C  - Liner combiner vector
                         En - Noise subspace matrix

         Implementation notes:
         ---------------------

             This function works only for two coherent signal sources. Note that, however the algorithm works
             for arbitrary number of coherent sources, the computational cost increases exponentially, thus
             using this algorithm for higher number of sources is impractical.

         Parameters:
         -----------

             :param R: spatial correlation matrix
             :param array_alignment : Array containing the antenna positions measured in the wavelength
             :param signal_dimension: Number of signal sources
             :param coherent_sources: Number of coherent sources
             :param angle_resolution: Angle resolution of scanning vector s(theta) [deg] (default : 1)

             :type R: 2D numpy array with size of M x M, where M is the number of antennas in the antenna system
             :type array_alignment: 1D numpy array with size: M x 1
             :type signal_dimension: int
             :type: coherent_sources: int
             :type angle_resolution: float

        Return values:
        --------------

             :return  ADORT : Angular dependent orthogonality.
              Expresses the orthogonality of the current steering vector to the noise subspace
             :rtype : L dimensional numpy array, where L is the number of coherent sources

             :return -1, -1: Input spatial correlation matrix is not quadratic
             :return -2, -2: dimension of R not equal with dimension of the antenna array

        """

        # --- Parameters ---

        # --> Input check
        if np.size(R, 0) != np.size(R, 1):
            print("ERROR: Correlation matrix is not quadratic")
            return -1, -1

        if np.size(R, 0) != np.size(array_alignment, 0):
            print("ERROR: Correlation matrix dimension does not match with the antenna array dimension")
            return -2, -2

        incident_angles = np.arange(0, 180 + angle_resolution, angle_resolution)
        ADORT = np.zeros((int(180 / angle_resolution + 1), int(180 / angle_resolution + 1)), dtype=float)

        M = np.size(R, 0)  # Number of antenna elements

        # --- Calculation ---
        # Determine eigenvectors and eigenvalues
        sigmai, vi = lin.eig(R)
        # Sorting
        eig_array = []
        for i in range(M):
            eig_array.append([np.abs(sigmai[i]), vi[:, i]])
        eig_array = sorted(eig_array, key=lambda eig_array: eig_array[0], reverse=False)

        # Generate noise subspace matrix
        noise_dimension = M - signal_dimension
        E = np.zeros((M, noise_dimension), dtype=complex)
        for i in range(noise_dimension):
            E[:, i] = eig_array[i][1]

        E = np.matrix(E)

        theta_index = 0
        theta2_index = 0

        for theta in incident_angles:
            S_theta_ = np.exp(array_alignment * 1j * 2 * np.pi * np.cos(np.radians(theta)))  # Scanning vector
            theta2_index = 0
            for theta2 in incident_angles[0:theta_index]:
                S_theta_2_ = np.exp(array_alignment * 1j * 2 * np.pi * np.cos(np.radians(theta2)))  # Scanning vector
                a = np.matrix(S_theta_ + S_theta_2_).getT()  # Spatial signature vector
                ADORT[theta_index, theta2_index] = np.real(1 / np.abs(a.getH() * (E * E.getH()) * a))
                theta2_index += 1
            theta_index += 1

        return ADORT, incident_angles

    def __read_frtm(self):
        string_to_stop_reading_header = "@ BeginData"
        header = []

        with open(self.__input_file, "rb") as binary_file:
            line = binary_file.readline()
            line_str = line.decode("ascii")
            while string_to_stop_reading_header not in line_str:
                header.append(line_str)
                line = binary_file.readline()
                line_str = line.decode("ascii")
                if line_str.replace(" ", "") == "":
                    pass
                elif "DlxCdVersion" in line_str:
                    dlxcd_vers_line = line_str
                    c = dlxcd_vers_line.split("=")
                    c = c[1].replace("\n", "").replace('"', "").replace(" ", "")
                    self.__dlxcd_version = int(c)
                elif "@ RowCount" in line_str:
                    c = line_str.split("=")
                    c = c[1].replace("\n", "").replace('"', "").replace(" ", "")
                    self.__row_count = int(c)

                elif "@ ColumnCount" in line_str:
                    c = line_str.split("=")
                    c = c[1].replace("\n", "").replace('"', "").replace(" ", "")
                    self.__col_count = int(c)
                elif "@ ColHead1" in line_str:
                    c = line_str.split("=")

                    c = c[1].split(" ")
                    c = [i for i in c if i]
                    c = c[0].replace("\n", "").replace('"', "").replace(" ", "")
                    self.__col_header1 = c
                elif "@ ColHead2" in line_str:
                    c = line_str.split("=")

                    c = c[1].split(" ")
                    c = [i for i in c if i]
                    c = c[0].replace("\n", "").replace('"', "").replace(" ", "")
                    self.__col_header2 = c
                elif "@ BinaryRecordLength " in line_str:
                    bin_record_length_line = line_str
                    c = bin_record_length_line.split("=")
                    c = c[1].replace("\n", "").replace('"', "").replace(" ", "")
                    self.__binary_record_length = int(c)
                elif "@ BinaryStartByte " in line_str:
                    c = line_str.split("=")
                    c = c[1].replace("\n", "").replace('"', "").replace(" ", "")
                    self.__binary_start_byte = int(c)
                elif "@ BinaryRecordSchema " in line_str:
                    c = line_str.split("=")
                    c = c[1].replace("\n", "").replace('"', "").replace(" ", "")
                    self.__binary_byte_type_line = c
                elif "@ RadarWaveform " in line_str:
                    radarwaveform_line = line_str
                    rw = radarwaveform_line.split("=")
                    self.__radar_waveform = rw[1].replace("\n", "").replace('"', "").replace(" ", "")
                elif "@ RadarChannels " in line_str:
                    radarchannels_line = line_str
                    rc = radarchannels_line.split("=")
                    self.__radar_channels = rc[1].replace("\n", "").replace('"', "").replace(" ", "")
                elif "@ TimeSteps " in line_str:
                    time_steps_line = line_str
                    c = time_steps_line.split("=")
                    c = c[1].split(" ")
                    c = [i for i in c if i]
                    self.__time_start = float(c[0].replace('"', ""))
                    self.__time_stop = float(c[1].replace('"', ""))
                    c = time_steps_line.split("=")
                    c = c[1].split(" ")
                    c = [i for i in c if i]
                    self.__time_number = int(c[2].replace('"', "")) + 1
                    self.__time_sweep = np.linspace(self.time_start, self.time_stop, num=self.time_number)
                    self.__pulse_repetition = self.time_sweep[1] - self.time_sweep[0]
                    self.__time_duration = self.time_sweep[-1] - self.time_sweep[0]
                elif "@ FreqDomainType " in line_str:
                    freq_dom_type_line = line_str
                    rc = freq_dom_type_line.split("=")
                    self.__frequency_domain_type = rc[1].replace("\n", "").replace('"', "").replace(" ", "")
                elif "@ FreqSweep " in line_str:
                    freq_sweep_line = line_str
                    c = freq_sweep_line.split("=")
                    c = c[1].replace('"', "")
                    c = c.lstrip()
                    c = c.rstrip()
                    c = c.split(" ")
                    c = [i for i in c if i]
                    self.__frequency_start = float(c[0])
                    self.__frequency_stop = float(c[1])
                    self.__frequency_number = int(c[2].replace('"', "")) + 1
                    if self.radar_waveform == "CS-FMCW" and self.radar_channels == "I":
                        self.__frequency_number = int(self.frequency_number / 2)
                    self.__frequency_sweep = np.linspace(
                        self.frequency_start, self.frequency_stop, num=self.frequency_number
                    )
                    self.__frequency_delta = self.frequency_sweep[1] - self.frequency_sweep[0]
                    self.__frequency_bandwidth = self.frequency_sweep[-1] - self.frequency_sweep[0]
                    center_index = int(self.frequency_number / 2)
                    self.__frequency_center = float(self.frequency_sweep[center_index])
                elif "@ AntennaNames " in line_str:
                    ant_names_line = line_str
                    c = ant_names_line.split("=")
                    c = c[1].replace("\n", "")
                    c = c.replace('"', "").replace(" ", "")
                    an = c.split(";")
                    self.__antenna_names = an
                elif "@ CouplingCombos " in line_str:
                    coupling_combos_line = line_str
                    c = coupling_combos_line.replace('"', "")
                    c = c.replace("\n", "")
                    c = c.split("=")[1]
                    c = c.split(" ")
                    c = [i for i in c if i]
                    self.__channel_number = int(c[0])
                    self.__coupling_combos = c[1].split(";")

        # this is the order in the frtm file

        for each in self.coupling_combos:
            index_values = each.split(",")
            rx_idx = index_values[0]
            tx_idx = index_values[1]
            if ":" in rx_idx:
                rx_idx = int(rx_idx.split(":")[0])
            if ":" in tx_idx:
                tx_idx = int(tx_idx.split(":")[0])
            tx_idx = int(tx_idx) - 1
            rx_idx = int(rx_idx) - 1
            self.__channel_names.append(self.antenna_names[rx_idx] + ":" + self.antenna_names[tx_idx])

        if self.col_count == 2:
            dt = np.dtype([(self.col_header1, float), (self.col_header2, float)])
        else:
            dt = np.dtype([(self.col_header1, float)])
        raw_data = np.fromfile(self.__input_file, dtype=dt, offset=self.binary_start_byte)

        # cdat_real = np.moveaxis(cdat_real,-1,0)
        if self.col_count == 2:
            cdat_real = np.reshape(
                raw_data[self.col_header1], (self.channel_number, self.time_number, self.frequency_number)
            )
            cdat_imag = np.reshape(
                raw_data[self.col_header2], (self.channel_number, self.time_number, self.frequency_number)
            )
            # cdat_imag = np.moveaxis(cdat_imag,-1,0)
            for n, ch in enumerate(self.channel_names):
                self.__all_data[ch] = cdat_real[n] + cdat_imag[n] * 1j
        else:
            cdat_real = np.reshape(
                raw_data[self.col_header1], (self.channel_number, self.time_number, int(self.frequency_number * 2))
            )  # fmcw I channel
            for n, ch in enumerate(self.channel_names):
                temp = cdat_real[n]
                # temp2 = temp.T[0::2] #every other sample for fmcw I channel only
                # temp2 = temp.T[0:80]
                self.__all_data[ch] = temp


class FRTMPlotter(object):
    """Provides range doppler data.

    Read FRTM data and return the Python interface to analyze the range doppler data. All units are in SI.

    Parameters
    ----------
    input_file : str
        Data in a FRTM file.

    Examples
    --------
    >>> from ansys.aedt.core.visualization.advanced.doppler_range_visualization import RangeDopplerData
    >>> file = "RxSignal.frtm"
    >>> data = RangeDopplerData(file)
    """

    def __init__(self, frtm_data):

        if not isinstance(frtm_data, list):
            frtm_data = [frtm_data]

        # Private
        self.__all_data = frtm_data
        self.__logger = logger

    @property
    def all_data(self):
        """RCS data object."""
        return self.__all_data

    @pyaedt_function_handler()
    def plot_range_profile(
        self,
        channel=None,
        pulse=None,
        chirp=None,
        title="Range profile",
        output_file=None,
        show=True,
        show_legend=True,
        size=(1920, 1440),
    ):
        """Create a 2D plot of the range profile.

        Parameters
        ----------
        title : str, optional
            Plot title. The default is ``"RectangularPlot"``.
        output_file : str, optional
            Full path for the image file. The default is ``None``, in which case an image in not exported.
        show : bool, optional
            Whether to show the plot. The default is ``True``.
            If ``False``, the Matplotlib instance of the plot is shown.
        show_legend : bool, optional
            Whether to display the legend or not. The default is ``True``.
        size : tuple, optional
            Image size in pixel (width, height).

        Returns
        -------
        :class:`ansys.aedt.core.visualization.plot.matplotlib.ReportPlotter`
            PyAEDT matplotlib figure object.
        """
        all_data = self.all_data
        if pulse is not None:
            all_data = [self.all_data[pulse]]

        curve_list = []
        new = ReportPlotter()
        new.show_legend = show_legend
        new.title = title
        new.size = size
        for pulse, data in enumerate(all_data):
            if channel is not None and channel not in data.channel_names:
                raise ValueError(f"Channel {channel} not found in data.")
            elif channel is None:
                channel = data.channel_names[0]

            if chirp is None:
                chirp = int(data.time_number / 2)
            elif chirp >= (data.time_number - 1):
                raise ValueError(f"Chirp {chirp} is out of range.")

            data_range_profile = data.range_profile(data.all_data[channel])
            range_profile_chirp = data_range_profile[chirp]

            x = np.linspace(0, data.range_period, np.shape(range_profile_chirp)[0])
            y = range_profile_chirp

            legend = f"pulse {pulse}, chirp {chirp}"
            curve = [x.tolist(), y.tolist(), legend]
            curve_list.append(curve)

            if len(all_data) == 1:
                # Single plot
                props = {"x_label": "Range (m)", "y_label": f"Range Profile ({data.data_conversion_function})"}
                name = curve[2]
                new.add_trace(curve[:2], 0, props, name)
                _ = new.plot_2d(None, output_file, show)
                return new
            else:
                props = {"x_label": "Range (m)", "y_label": f"Range Profile ({data.data_conversion_function})"}
                name = curve[2]
                new.add_trace(curve[:2], 0, props, name)

        new.animate_2d(show=show, snapshot_path=output_file)
        return new

    @property
    def doppler_data(self):
        return self.__doppler_data

    @property
    def oversampling(self):
        return self.__oversampling

    @oversampling.setter
    def oversampling(self, value):
        self.__oversampling = value

    @pyaedt_function_handler()
    def power_range(
        self,
        chirp,
    ):
        curves = []
        for cont, doppler_data in enumerate(self.doppler_data):
            # IFFT over the frequency, over the channels at a given chirp
            range_arr = doppler_data.range(chirp, cont, self.oversampling)
            if range_arr is None:
                self.__logger.error(f"Power range could not be computer for chirp number {chirp}. ")
            x = np.linspace(0, doppler_data.range_period, np.shape(range_arr)[1])
            y = 20 * np.log10(np.abs(range_arr[0, :].T))
            curves.append([x, y])

        if curves is not None:
            new = ReportPlotter()
            # new.show_legend = show_legend
            # new.title = title
            # new.size = size

            for data in curves:
                new.add_trace(data[:2], 0)
            _ = new.plot_2d(None, output_file, show)
            return new

    # def peak_detector(data, max_detections=20):
    #     '''
    #     passing data in as linear, but converting to dB seems to work
    #     '''
    #     time_before = walltime.time()
    #     size = np.shape(data)
    #     if len(size) > 2:
    #         data = data[0]
    #     data = np.abs(data)
    #     # data = 20*np.log10(np.abs(data))
    #     data[data > 1e-7] = 1
    #     data[data < 1e-7] = 0
    #
    #     time_after = walltime.time()
    #     duration_time = time_after - time_before
    #     if duration_time == 0:
    #         duration_time = 1
    #     duration_fps = 1 / duration_time
    #
    #     # return as 1 or zero to be consistent with CFAR processing below
    #     return data, duration_fps
    #
    # ######################################################################
    # """
    #
    #                              Python based Advanced Passive Radar Library (pyAPRiL)
    #
    #                                           Hit Processor Module
    #
    #
    #      Description:
    #      ------------
    #          Contains the implementation of the most common hit processing algorithms.
    #
    #              - CA-CFAR processor:
    #              Implements an automatic detection with (Cell Averaging - Constant False Alarm Rate)
    #              detection.
    #              - Target DOA estimator:
    #              Estimates direction of arrival for the target reflection from the range-Doppler
    #                                      maps of the surveillance channels using phased array techniques.
    #
    #      Notes:
    #      ------------
    #
    #      Features:
    #      ------------
    #
    #      Project: pyAPRIL
    #      Authors: Tamás Pető
    #      License: GNU General Public License v3 (GPLv3)
    #
    #      Changelog :
    #          - Ver 1.0.0    : Initial version (2017 11 02)
    #          - Ver 1.0.1    : Faster CFAR implementation(2019 02 15)
    #          - Ver 1.1.0    : Target DOA estimation (2019 04 11)
    #
    #  """
    #
    # def CA_CFAR(rd_matrix, win_len=50, win_width=50, guard_len=10, guard_width=10, threshold=20):
    #     """
    #     Description:
    #     ------------
    #         Cell Averaging - Constant False Alarm Rate algorithm
    #
    #         Performs an automatic detection on the input range-Doppler matrix with an adaptive thresholding.
    #         The threshold level is determined for each cell in the range-Doppler map with the estimation
    #         of the power level of its surrounding noise. The average power of the noise is estimated on a
    #         rectangular window, that is defined around the CUT (Cell Under Test). In order the mitigate the effect
    #         of the target reflection energy spreading some cells are left out from the calculation in the immediate
    #         vicinity of the CUT. These cells are the guard cells.
    #         The size of the estimation window and guard window can be set with the win_param parameter.
    #
    #     Implementation notes:
    #     ---------------------
    #
    #     Parameters:
    #     -----------
    #
    #     :param rd_matrix: Range-Doppler map on which the automatic detection should be performed
    #     :param win_param: Parameters of the noise power estimation window
    #                       [Est. window length, Est. window width, Guard window length, Guard window width]
    #     :param threshold: Threshold level above the estimated average noise power
    #
    #     :type rd_matrix: R x D complex numpy array
    #     :type win_param: python list with 4 elements
    #     :type threshold: float
    #
    #     Return values:
    #     --------------
    #
    #     :return hit_matrix: Calculated hit matrix
    #
    #     """
    #
    #     time_before = walltime.time()
    #
    #     norc = np.size(rd_matrix, 1)  # number of range cells
    #     noDc = np.size(rd_matrix, 0)  # number of Doppler cells
    #     hit_matrix = np.zeros((noDc, norc), dtype=float)
    #
    #     # Convert range-Doppler map values to power
    #     rd_matrix = np.abs(rd_matrix) ** 2
    #
    #     # Generate window mask
    #     rd_block = np.zeros((2 * win_width + 1, 2 * win_len + 1), dtype=float)
    #     mask = np.ones((2 * win_width + 1, 2 * win_len + 1))
    #     mask[win_width - guard_width:win_width + 1 + guard_width,
    #     win_len - guard_len:win_len + 1 + guard_len] = np.zeros(
    #         (guard_width * 2 + 1, guard_len * 2 + 1))
    #
    #     cell_counter = np.sum(mask)
    #
    #     # Convert threshold value
    #     threshold = 10 ** (threshold / 10)
    #     threshold /= cell_counter
    #
    #     # -- Perform automatic detection --
    #     for j in np.arange(win_width, noDc - win_width, 1):  # Range loop
    #         for i in np.arange(win_len, norc - win_len, 1):  # Doppler loop
    #             rd_block = rd_matrix[j - win_width:j + win_width + 1, i - win_len:i + win_len + 1]
    #             rd_block = np.multiply(rd_block, mask)
    #             cell_SINR = rd_matrix[j, i] / np.sum(rd_block)  # esimtate CUT SINR
    #
    #             # Hard decision
    #             if cell_SINR > threshold:
    #                 hit_matrix[j, i] = 1
    #     time_after = walltime.time()
    #     duration_time = time_after - time_before
    #     duration_fps = 1 / duration_time
    #     return hit_matrix, duration_fps
    #


# def get_results_files(path, wildcard=''):
#     """
#     wildcard is if we want to separate different results folder
#     different solution setups would be named something like
#     DV551_S17_V518_Data.transient
#     where the wild card could be "s17_V518" to indicate that specific setup
#     """
#     results_files = []
#     all_paths = glob.glob(path + '\\*' + wildcard + '_Data.transient')
#     index_num = []
#     for filename in all_paths:
#         index_num.append(int(filename.split('\\DV')[1].split('_')[0]))
#
#     all_paths_sorted = sorted(zip(index_num, all_paths))
#     # all_paths = sorted(all_paths)
#     for each in all_paths_sorted:
#         results_files.append(each[1] + '\\RxSignal.frtm')
#     return results_files


@pyaedt_function_handler()
def get_results_files(input_dir, var_name="time_var"):
    path = Path(input_dir)

    # Find all CSV files recursively
    index_files = list(path.rglob("*.csv"))
    sol_files = []

    if not index_files:

        all_paths = list(Path(path).rglob(f"*_Data.transient"))
        index_files = []
        for filename in all_paths:
            index_files.append(int(filename.stem.split("DV")[1].split("_")[0]))

        if not index_files:
            logger.error("FRTM files not found.")
            return None

        all_paths_sorted = sorted(zip(index_files, all_paths))
        all_frtm_dict = {}
        for each in all_paths_sorted:
            frtm_file = each[1] / "RxSignal.frtm"
            if not frtm_file.is_file():
                logger.error(f"{str(frtm_file)} does not exist.")
                return
            all_frtm_dict[each[0]] = frtm_file

    else:

        # If multiple files are found, use the first one
        index_file_full_path = index_files[0].resolve()

        if len(index_files) > 1:
            logger.warning(f"Multiple index files found, using {index_file_full_path}")
        else:
            logger.info(f"Index file found, using {index_file_full_path}")

        # Extract base path and filename
        base_path = index_file_full_path.parent

        # Find all .frtm files in the base directory
        sol_files = list(base_path.glob("*.frtm"))

        if not sol_files:
            logger.error("No .frtm solution files found in the base directory.")
            return

        # Extract the first .frtm file's name prefix
        file_name_prefix = sol_files[0].stem.split("_DV")[0]

        var_IDS = []
        var_vals = []
        with open(index_file_full_path, mode="r") as csv_file:
            csv_reader = csv.DictReader(csv_file)
            line_count = 0
            for row in csv_reader:
                if line_count == 0:
                    # print(f'Column names are {", ".join(row)}')
                    line_count += 1
                if row["Var_ID"] not in var_IDS:
                    var_IDS.append(row["Var_ID"])
                    if "s" in row[var_name]:
                        val = float(row[var_name].replace("s", ""))
                    else:
                        val = float(row[var_name])
                    var_vals.append(val)

                line_count += 1

        variation_var_IDS = sorted(zip(var_vals, var_IDS))

        all_frtm = []
        all_frtm_dict = {}
        for var_val, id_num in variation_var_IDS:
            # all_frtm[var_val]=f'{path}/{file_name_prefix}_DV{id_num}.frtm'
            all_frtm.append(f"{path}/{file_name_prefix}_DV{id_num}.frtm")
            all_frtm_dict[var_val] = f"{path}/{file_name_prefix}_DV{id_num}.frtm"

        print(f"Variations Found: {len(all_frtm)}.")
        all_frtm_dict = dict(sorted(all_frtm_dict.items()))
    return all_frtm_dict


# @pyaedt_function_handler()
# def get_results_files(self, path, wildcard=''):
#     """
#     wildcard is if we want to separate different results folder
#     different solution setups would be named something like
#     DV551_S17_V518_Data.transient
#     where the wild card could be "s17_V518" to indicate that specific setup
#     """
#     results_files = []
#     all_paths = glob.glob(path + '\\*' + wildcard + '_Data.transient')
#     index_num = []
#     for filename in all_paths:
#         index_num.append(int(filename.split('\\DV')[1].split('_')[0]))
#
#     all_paths_sorted = sorted(zip(index_num, all_paths))
#     # all_paths = sorted(all_paths)
#     for each in all_paths_sorted:
#         results_files.append(each[1] + '\\RxSignal.frtm')
#     return results_files
