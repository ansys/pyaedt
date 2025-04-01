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
from ansys.aedt.core.generic.general_methods import pyaedt_function_handler

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


class RangeDopplerData(object):
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

    def __init__(self, input_file):
        input_file = Path(input_file)

        if not input_file.is_file():
            raise FileNotFoundError("FRTM file does not exist.")

        # Private
        self.__logger = logger
        self.__input_file = input_file
        self.__dlxcd_vers = None
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
        self.__time_step = None
        self.__time_sweep = None
        self.__time_delta = None
        self.__time_duration = None
        self.__frequency_domain_type = None
        self.__frequency_start = None
        self.__frequency_stop = None
        self.__frequency_step = None
        self.__frequency_sweep = None
        self.__frequency_delta = None
        self.__frequency_bandwidth = None
        self.__frequency_center = None
        self.__antenna_names = None
        self.__channel_number = None
        self.__coupling_combos = None
        self.__channel_names = []
        self.__all_data = {}

        self.__read_frtm()

    @property
    def dlxcd_vers(self):
        return self.__dlxcd_vers

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
    def time_step(self):
        return self.__time_step

    @property
    def time_sweep(self):
        return self.__time_sweep

    @property
    def time_delta(self):
        return self.__time_delta

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
    def frequency_step(self):
        return self.__frequency_step

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
        max_range = rr * self.frequency_step
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
        time_step = self.time_step
        vp = time_step * vr
        return vp

    @pyaedt_function_handler()
    def load_data(self, order="FreqPulse"):
        """Provides range doppler data.

        Parameters
        ----------
        order : str, optional
            DESCRIPTION. order is either 'FreqPulse' or 'PulseFreq'. this is
            the index order of the array, [numFreq][numPulse] or [numPulse][numFreq]
            many of the post processing depend on this order so just choose accordingly

        Returns
        -------
        dict
            DESCRIPTION.

        """
        if order.lower() == "freqpulse":
            for ch in self.all_data.keys():
                self.__all_data[ch] = self.all_data[ch].T
            return self.all_data
        else:
            # This is how the data is read in with [pulse][freq] order
            return self.all_data

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
                    vers = dlxcd_vers_line.split("=")
                    self.__dlxcd_vers = vers
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
                    self.__binary_record_length = c[1]
                elif "@ BinaryStartByte " in line_str:
                    c = line_str.split("=")
                    c = c[1].replace("\n", "").replace('"', "").replace(" ", "")
                    self.__binary_start_byte = int(c)
                elif "@ BinaryRecordSchema " in line_str:
                    self.__binary_byte_type_line = line_str
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
                    self.__time_step = int(c[2].replace('"', "")) + 1
                    self.__time_sweep = np.linspace(self.time_start, self.time_stop, num=self.time_step)
                    self.__time_delta = self.time_sweep[1] - self.time_sweep[0]
                    self.__time_duration = self.time_sweep[-1] - self.time_sweep[0]
                elif "@ FreqDomainType " in line_str:
                    freq_dom_type_line = line_str
                    self.__frequency_domain_type = freq_dom_type_line.split("=")[1]
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
                    self.__frequency_step = int(c[2].replace('"', "")) + 1
                    if self.radar_waveform == "CS-FMCW" and self.radar_channels == "I":
                        self.__frequency_step = int(self.frequency_step / 2)
                    self.__frequency_sweep = np.linspace(
                        self.frequency_start, self.frequency_stop, num=self.frequency_step
                    )
                    self.__frequency_delta = self.frequency_sweep[1] - self.frequency_sweep[0]
                    self.__frequency_bandwidth = self.frequency_sweep[-1] - self.frequency_sweep[0]
                    center_index = int(self.frequency_step / 2)
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
                raw_data[self.col_header1], (self.channel_number, self.time_step, self.frequency_step)
            )
            cdat_imag = np.reshape(
                raw_data[self.col_header2], (self.channel_number, self.time_step, self.frequency_step)
            )
            # cdat_imag = np.moveaxis(cdat_imag,-1,0)
            for n, ch in enumerate(self.channel_names):
                self.__all_data[ch] = cdat_real[n] + cdat_imag[n] * 1j
        else:
            cdat_real = np.reshape(
                raw_data[self.col_header1], (self.channel_number, self.time_step, int(self.frequency_step * 2))
            )  # fmcw I channel
            for n, ch in enumerate(self.channel_names):
                temp = cdat_real[n]
                # temp2 = temp.T[0::2] #every other sample for fmcw I channel only
                # temp2 = temp.T[0:80]
                self.__all_data[ch] = temp


@pyaedt_function_handler()
def get_results_files(input_file, var_name="time_var"):

    path = Path(input_file)

    # Find all CSV files recursively
    index_files = list(path.rglob("*.csv"))

    if not index_files:
        logger.error("FRTM Index file not found, check path")
        return None

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
