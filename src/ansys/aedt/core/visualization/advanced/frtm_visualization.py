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
    raise Exception("Python 3.10 or higher is required for Monostatic RCS post-processing.")

import csv
import warnings

from ansys.aedt.core.aedt_logger import pyaedt_logger as logger
from ansys.aedt.core.generic.constants import SpeedOfLight
from ansys.aedt.core.generic.general_methods import conversion_function
from ansys.aedt.core.generic.general_methods import pyaedt_function_handler
from ansys.aedt.core.visualization.plot.matplotlib import ReportPlotter

try:
    import numpy as np
except ImportError:  # pragma: no cover
    warnings.warn(
        "The NumPy module is required to use module rcs_visualization.py.\nInstall with \n\npip install numpy"
    )
    np = None


class FRTMData(object):
    """Provides FRTM data.

    Read FRTM data and return the Python interface to analyze the data. All units are in SI.

    Parameters
    ----------
    input_file : str or :class:`pathlib.Path`
        Data in a FRTM file.

    Examples
    --------
    >>> from ansys.aedt.core.visualization.advanced.frtm_visualization import FRTMData
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
        self.__cpi_frames = None
        self.__time_sweep = None
        self.__cpi_duration = None
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
        self.__receiver_position = {}
        self.__channel_names = []
        self.__all_data = {}
        self.__data_conversion_function = None
        self.__read_frtm()

        self.__receiver_position = {channel: [0.0, 0.0, 0.0] for channel in self.channel_names}

    @property
    def dlxcd_version(self):
        """DlxCd version."""
        return self.__dlxcd_version

    @property
    def row_count(self):
        """Number of rows in the dataset."""
        return self.__row_count

    @property
    def col_count(self):
        """Number of columns in the dataset."""
        return self.__col_count

    @property
    def col_header1(self):
        """Primary column header names."""
        return self.__col_header1

    @property
    def col_header2(self):
        """Secondary column header names."""
        return self.__col_header2

    @property
    def binary_record_length(self):
        """Length of each binary record."""
        return self.__binary_record_length

    @property
    def binary_start_byte(self):
        """Start byte index for binary data."""
        return self.__binary_start_byte

    @property
    def binary_byte_type_line(self):
        """Byte type definition line for binary parsing."""
        return self.__binary_byte_type_line

    @property
    def radar_waveform(self):
        """Radar waveform configuration."""
        return self.__radar_waveform

    @property
    def radar_channels(self):
        """List of radar channel configurations."""
        return self.__radar_channels

    @property
    def time_start(self):
        """Start time of the radar data collection."""
        return self.__time_start

    @property
    def time_stop(self):
        """Stop time of the radar data collection."""
        return self.__time_stop

    @property
    def cpi_frames(self):
        """Number of coherent processing interval frames."""
        return self.__cpi_frames

    @property
    def time_sweep(self):
        """Sweep duration for each pulse."""
        return self.__time_sweep

    @property
    def cpi_duration(self):
        """Coherent processing interval duration."""
        return self.__cpi_duration

    @property
    def pulse_repetition_frequency(self):
        """Pulse repetition frequency (Hz)."""
        return 1 / self.__cpi_duration

    @property
    def time_duration(self):
        """Total time duration of signal capture."""
        return self.__time_duration

    @property
    def frequency_domain_type(self):
        """Type of frequency domain representation."""
        return self.__frequency_domain_type

    @property
    def frequency_start(self):
        """Start frequency (Hz)."""
        return self.__frequency_start

    @property
    def frequency_stop(self):
        """Stop frequency (Hz)."""
        return self.__frequency_stop

    @property
    def frequency_number(self):
        """Number of frequency steps."""
        return self.__frequency_number

    @property
    def frequency_sweep(self):
        """Available frequencies."""
        return self.__frequency_sweep

    @property
    def frequency_delta(self):
        """Frequency step size."""
        return self.__frequency_delta

    @property
    def frequency_bandwidth(self):
        """Total bandwidth of frequency sweep."""
        return self.__frequency_bandwidth

    @property
    def frequency_center(self):
        """Center frequency of the sweep."""
        return self.__frequency_center

    @property
    def antenna_names(self):
        """Names of the antennas used."""
        return self.__antenna_names

    @property
    def channel_number(self):
        """Number of radar channels."""
        return self.__channel_number

    @property
    def coupling_combos(self):
        """List of transmit-receive antenna combinations."""
        return self.__coupling_combos

    @property
    def channel_names(self):
        """Names assigned to radar channels."""
        return self.__channel_names

    @property
    def receiver_position(self):
        """Position of receivers respected the transmitters."""
        return self.__receiver_position

    @receiver_position.setter
    def receiver_position(self, value):
        """Position of receivers respected the transmitters."""
        self.__receiver_position = value

    @property
    def all_data(self):
        """Complete dataset."""
        return self.__all_data

    @property
    def range_resolution(self):
        """Radar range resolution (meters)."""
        bw = self.frequency_bandwidth
        rr = SpeedOfLight / 2 / bw
        return rr

    @property
    def range_maximum(self):
        """Maximum detectable range (meters)."""
        rr = self.range_resolution
        max_range = rr * self.frequency_number
        if self.col_count != 2:  # I
            max_range = max_range / 2.0
        return max_range

    @property
    def velocity_resolution(self):
        """Velocity resolution (m/s)."""
        fc = self.frequency_center
        tpt = self.time_duration
        vr = SpeedOfLight / (2 * fc * tpt)
        return vr

    @property
    def velocity_maximum(self):
        """Maximum measurable velocity (m/s)."""
        vr = self.velocity_resolution
        time_step = self.cpi_frames
        vp = time_step * vr
        return vp / 2

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
    def get_data_pulse(self, pulse: int = None) -> np.ndarray:
        """
        Get the data for a specified pulse.

        Parameters
        ----------
        pulse: int, optional
            Number of points to window. The default is ``None``.

        Returns
        -------
        numpy.ndarray
            Data for specified pulse.
        """

        if pulse is None:
            pulse = int(self.cpi_frames / 2)
        elif pulse > self.cpi_frames:
            raise ValueError(f"Pulse must be less than {self.cpi_frames}.")
        else:
            pulse = int(pulse)

        data_array = np.stack(list(self.all_data.values()))
        pulse_data = data_array[:, pulse]
        return pulse_data

    @pyaedt_function_handler()
    def range_profile(self, data: np.ndarray, window: str = None, size: int = None) -> np.ndarray:
        """
        Calculate the range profile of a specific CPI frame.

        Parameters
        ----------
        data : numpy.ndarray
            Array of complex samples with ``frequency_number`` elements.
        window: str, optional
            Type of window. The default is ``None``. Available options are ``"Hann"``, ``"Hamming"``, and ``"Flat"``.
        size: int, optional
            Output number of samples. The default is ``None``.

        Returns
        -------
        numpy.ndarray
            Range profile data.
        """
        data_conversion_function_original = self.data_conversion_function
        self.data_conversion_function = None

        data_size = int(np.shape(np.squeeze(data))[0])

        if size is None:
            size = data_size

        if window:
            window_function = self.window_function(window, data_size)
            window_function_sum = np.sum(window_function)
            sampling_factor = data_size / window_function_sum
            window_function = window_function * sampling_factor
            new_data = np.multiply(data, window_function)
        else:
            new_data = data

        up_sample = size / data_size

        # FFT with oversampling
        range_profile_data = up_sample * np.fft.ifft(new_data, n=size)

        # Convert data to original function
        self.data_conversion_function = data_conversion_function_original
        if data_conversion_function_original is not None:
            range_profile_data = conversion_function(range_profile_data, self.data_conversion_function)
        return range_profile_data

    @pyaedt_function_handler()
    def range_doppler(
        self, channel: str = None, window: str = "Hann", range_bins: int = None, doppler_bins: int = None
    ) -> np.ndarray:
        """
        Calculate the range-Doppler map of a frame.

        Parameters
        ----------
        channel : str, optional
            Channel name. The default is the first one.
        window : str, optional
            Type of window to apply in both Doppler and Range dimensions. The default is ``"Hann"``.
            Options are ``"Hann"``, ``"Hamming"``, ``"Flat"``, etc.
        range_bins : int, optional
            Number of output bins in range (frequency) dimension.
            If not specified, uses the original number of frequencies.
        doppler_bins : int, optional
            Number of output bins in Doppler (pulse/time) dimension.
             If not specified, uses the original number of CPI frames.

        Returns
        -------
        numpy.ndarray
            Range doppler array of shape (doppler_bins, range_bins), where:
            - Each column corresponds to a Doppler velocity bin.
            - Each row corresponds to a range bin.
        """
        if channel is None:
            channel = self.channel_names[0]

        original_function = self.data_conversion_function
        self.data_conversion_function = None

        data = self.all_data[channel]

        num_cpi_frames, num_freq = data.shape

        if doppler_bins is None:
            doppler_bins = num_cpi_frames

        if range_bins is None:
            range_bins = num_freq

        range_profile_cpi_frame = np.zeros((doppler_bins, range_bins), dtype=complex)
        data_range_pulse_out = np.zeros((range_bins, doppler_bins), dtype=complex)

        for n, p in enumerate(data[:doppler_bins]):
            rp = self.range_profile(p, window=window, oversampling=1, window_size=range_bins)
            range_profile_cpi_frame[n] = rp

        # Place doppler as first dimension
        range_profile_cpi_frame = np.swapaxes(range_profile_cpi_frame, 0, 1)
        # Swap first and second half to place zero at first index
        data_range_pulse_flip = np.fliplr(range_profile_cpi_frame)

        # Window over doppler axis
        win_doppler, _ = self.window_function(window, doppler_bins)

        for r, pulse in enumerate(data_range_pulse_flip):
            pulse_f_win = np.multiply(pulse, win_doppler)
            pulse_t = np.fft.ifftshift(np.fft.ifft(pulse_f_win, n=doppler_bins))
            data_range_pulse_out[r] = pulse_t

        self.data_conversion_function = original_function
        if original_function is not None:
            data_range_pulse_out = conversion_function(data_range_pulse_out, self.data_conversion_function)
        return data_range_pulse_out

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
        numpy.ndarray
            The window with the maximum value normalized to one.
        """
        if window is None or window == "Flat":
            win = np.ones(size)
        elif window == "Hann":
            win = np.hanning(size)
        elif window == "Hamming":
            win = np.hamming(size)
        else:
            raise ValueError(f"Window function {window} not supported.")
        return win

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
                    self.__cpi_frames = int(c[2].replace('"', "")) + 1
                    self.__time_sweep = np.linspace(self.time_start, self.time_stop, num=self.cpi_frames)
                    self.__cpi_duration = self.time_sweep[1] - self.time_sweep[0]
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
                raw_data[self.col_header1], (self.channel_number, self.cpi_frames, self.frequency_number)
            )
            cdat_imag = np.reshape(
                raw_data[self.col_header2], (self.channel_number, self.cpi_frames, self.frequency_number)
            )
            # cdat_imag = np.moveaxis(cdat_imag,-1,0)
            for n, ch in enumerate(self.channel_names):
                self.__all_data[ch] = cdat_real[n] + cdat_imag[n] * 1j
        else:
            cdat_real = np.reshape(
                raw_data[self.col_header1], (self.channel_number, self.cpi_frames, int(self.frequency_number * 2))
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
    frtm_data : dict or FRTMData
        Dictionary with multiple FRTMData objects or one single FRTMData.

    Examples
    --------
    >>> from ansys.aedt.core.visualization.advanced.doppler_range_visualization import RangeDopplerData
    >>> file = "RxSignal.frtm"
    >>> data = RangeDopplerData(file)
    """

    def __init__(self, frtm_data):
        if not isinstance(frtm_data, dict):
            frtm_data = {0: frtm_data}

        # Private
        self.__all_data = frtm_data
        self.__logger = logger

    @property
    def all_data(self):
        """RCS data object."""
        return self.__all_data

    @property
    def frames(self):
        """Frames."""
        return list(self.__all_data.keys())

    @pyaedt_function_handler()
    def plot_range_profile(
        self,
        channel: str = None,
        frame: int = None,
        cpi_frame: int = None,
        window: str = None,
        size: int = None,
        quantity_format: str = None,
        title: str = "Range profile",
        output_file: str = None,
        show: bool = True,
        show_legend: bool = True,
        plot_size: tuple = (1920, 1440),
        animation: bool = True,
        figure=None,
    ):
        """Create a 2D plot of the range profile.

        Parameters
        ----------
        channel : str, optional
            Channel name. The default is ``None``, in which case the first channel is used.
        frame : int, optional
            Frame number. The default is ``None``, in which case all frames are used.
        cpi_frame : int, optional
            Cpi frame number. The default is ``None``, in which case the middle cpi frame is used.
        window: str, optional
            Type of window. The default is ``None``. Available options are ``"Hann"``, ``"Hamming"``, and ``"Flat"``.
        size: int, optional
            Output number of samples. The default is ``None``.
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
        animation : bool, optional
            Create an animated plot or overlap the frames. The default is ``True``.
        figure : :class:`matplotlib.pyplot.Figure`, optional
            An existing Matplotlib `Figure` to which the plot is added.
            If not provided, a new `Figure` and `Axes` objects are created.
            Default is ``None``.

        Returns
        -------
        :class:`ansys.aedt.core.visualization.plot.matplotlib.ReportPlotter`
            PyAEDT matplotlib figure object.
        """
        all_data = self.all_data
        if frame is not None:
            all_data = {frame: self.all_data[frame]}

        curve_list = []
        new = ReportPlotter()
        new.show_legend = show_legend
        new.title = title
        new.size = plot_size
        for frame, data in all_data.items():
            if channel is not None and channel not in data.channel_names:
                raise ValueError(f"Channel {channel} not found in data.")
            elif channel is None:
                channel = data.channel_names[0]

            if cpi_frame is None:
                cpi_frame = int(data.cpi_frames / 2)
            elif cpi_frame >= (data.cpi_frames - 1):
                raise ValueError(f"Chirp {cpi_frame} is out of range.")

            data_pulse = data.all_data[channel][cpi_frame]

            if data.data_conversion_function is None:
                if quantity_format is None:
                    data.data_conversion_function = "dB10"
                else:
                    data.data_conversion_function = quantity_format

            data_range_profile = data.range_profile(data_pulse, size=size, window=window)

            x = np.linspace(0, data.range_maximum, np.shape(data_range_profile)[0])

            y = data_range_profile

            legend = f"Frame {frame}, CPI {cpi_frame}"
            curve = [x.tolist(), y.tolist(), legend]
            curve_list.append(curve)

            if len(all_data) == 1:
                # Single plot
                props = {"x_label": "Range (m)", "y_label": f"Range Profile ({data.data_conversion_function})"}
                name = curve[2]
                new.add_trace(curve[:2], 0, props, name)
                new.x_margin_factor = 0.0
                new.y_margin_factor = 0.2
                _ = new.plot_2d(None, output_file, show, figure=figure)
                return new
            else:
                props = {"x_label": "Range (m)", "y_label": f"Range Profile ({data.data_conversion_function})"}
                name = curve[2]
                new.add_trace(curve[:2], 0, props, name)

        if animation:
            new.animate_2d(show=show, snapshot_path=output_file, figure=figure)
        else:
            new.x_margin_factor = 0.0
            new.y_margin_factor = 0.2
            new.plot_2d(traces=None, snapshot_path=output_file, show=show, figure=figure)
        return new

    @pyaedt_function_handler()
    def plot_range_doppler(
        self,
        channel: str = None,
        frame: int = None,
        range_bins: int = None,
        doppler_bins: int = None,
        window: str = None,
        title: str = "Doppler Velocity-Range",
        output_file: str = None,
        show: bool = True,
        show_legend: bool = True,
        size: tuple = (1920, 1440),
        figure=None,
    ):
        """Create range-Doppler contour plot.

        Parameters
        ----------
        channel : str, optional
            Channel name. The default is ``None``, in which case the first channel is used.
        frame : int, optional
            Frame number. The default is ``None``, in which case all frames are used.
        range_bins : int, optional
            Number of output bins in range (frequency) dimension.
            If not specified, uses the original number of frequencies.
        doppler_bins : int, optional
            Number of output bins in Doppler (pulse/time) dimension.
             If not specified, uses the original number of CPI frames.
        window: str, optional
            Type of window. The default is ``None``. Available options are ``"Hann"``, ``"Hamming"``, and ``"Flat"``.
        title : str, optional
            Title of the plot. The default is ``"Range profile"``.
        output_file : str or :class:`pathlib.Path`, optional
            Full path for the image file. The default is ``None``, in which case an image in not exported.
        show : bool, optional
            Whether to show the plot. The default is ``True``.
            If ``False``, the Matplotlib instance of the plot is shown.
        show_legend : bool, optional
            Whether to display the legend or not. The default is ``True``.
        size : tuple, optional
            Image size in pixel (width, height).
        figure : :class:`matplotlib.pyplot.Figure`, optional
            An existing Matplotlib `Figure` to which the plot is added.
            If not provided, a new `Figure` and `Axes` objects are created.
            Default is ``None``.

        Returns
        -------
        :class:`ansys.aedt.core.visualization.plot.matplotlib.ReportPlotter`
            PyAEDT matplotlib figure object.
        """
        all_data = self.all_data
        if frame is not None:
            all_data = {frame: self.all_data[frame]}

        new = ReportPlotter()
        new.show_legend = show_legend
        new.title = title
        new.size = size

        for frame, data in all_data.items():
            if channel is not None and channel not in data.channel_names:
                raise ValueError(f"Channel {channel} not found in data.")
            elif channel is None:
                channel = data.channel_names[0]

            data_range_profile = data.range_doppler(
                channel=channel, range_bins=range_bins, doppler_bins=doppler_bins, window=window
            )

            range_bins_plot, doppler_bins_plot = data_range_profile.shape

            doppler_axis = np.linspace(-data.velocity_maximum, data.velocity_maximum, doppler_bins_plot)
            range_axis = np.linspace(0, data.range_maximum, range_bins_plot)

            doppler_grid, range_grid = np.meshgrid(doppler_axis, range_axis)
            x = doppler_grid
            y = range_grid
            ylabel = "Range (m)"
            xlabel = "Doppler Velocity (m/s)"
            plot_data = [data_range_profile, y, x]

            legend = f"Frame {frame}"

            if len(all_data) == 1:
                # Single plot
                props = {
                    "x_label": xlabel,
                    "y_label": ylabel,
                }
                new.add_trace(plot_data, 0, props, legend)
                _ = new.plot_contour(
                    trace=0,
                    snapshot_path=output_file,
                    show=show,
                    figure=figure,
                    is_spherical=False,
                )
                return new
            else:
                props = {
                    "x_label": xlabel,
                    "y_label": ylabel,
                }
                new.add_trace(plot_data, 0, props, legend)

        new.animate_contour(
            trace=None,
            polar=False,
            levels=64,
            max_theta=180,
            min_theta=0,
            color_bar=None,
            snapshot_path=output_file,
            show=show,
            figure=figure,
            is_spherical=False,
        )
        return new


@pyaedt_function_handler()
def get_results_files(input_dir, var_name="time_var"):
    path = Path(input_dir)

    # Find all CSV files recursively
    index_files = list(path.rglob("*.csv"))

    if not index_files:
        all_paths = list(Path(path).rglob("*_Data.transient"))
        index_files = []
        for filename in all_paths:
            index_files.append(int(filename.stem.split("DV")[1].split("_")[0]))

        if not index_files:  # pragma: no cover
            logger.error("FRTM files not found.")
            return None

        all_paths_sorted = sorted(zip(index_files, all_paths))
        all_frtm_dict = {}
        for each in all_paths_sorted:
            frtm_file = each[1] / "RxSignal.frtm"
            if not frtm_file.is_file():  # pragma: no cover
                logger.error(f"{str(frtm_file)} does not exist.")
                return
            all_frtm_dict[each[0]] = frtm_file

    else:
        # If multiple files are found, use the first one
        index_file_full_path = index_files[0].resolve()
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
                    line_count += 1
                if row["Var_ID"] not in var_IDS:
                    var_IDS.append(row["Var_ID"])
                    if "s" in row[var_name]:
                        val = float(row[var_name].replace("s", ""))
                    else:  # pragma: no cover
                        val = float(row[var_name])
                    var_vals.append(val)

                line_count += 1

        variation_var_IDS = sorted(zip(var_vals, var_IDS))

        all_frtm_dict = {}
        for var_val, id_num in variation_var_IDS:
            file_path = Path(path) / f"{file_name_prefix}_DV{id_num}.frtm"
            all_frtm_dict[var_val] = file_path

        all_frtm_dict = dict(sorted(all_frtm_dict.items()))
    return all_frtm_dict
