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

from enum import Enum
import json
from pathlib import Path

from ansys.aedt.core.generic.general_methods import pyaedt_function_handler
from ansys.aedt.core.generic.settings import settings
from ansys.aedt.core.visualization.post.spisim_com_configuration_files.com_settings_mapping import (
    spimsim_matlab_keywords_mapping,
)

logger = settings.logger


class COMStandards(Enum):
    COM_CUSTOM = 0
    COM_50GAUI_1_C2C = 1  # com_120d_8
    COM_100GAUI_2_C2C = 2  # com_120d_8
    COM_200GAUI_4 = 3  # com_120d_8
    COM_400GAUI_8 = 4  # com_120d_8
    COM_100GBASE_KR4 = 5  # com_93_8
    COM_100GBASE_KP4 = 6  # com_94_17


class COMParameters:
    """Base class to manage COM parameters.

    Parameters
    ----------
    standard  : int
    """

    _CFG_DIR = Path(__file__).parent
    _STD_TABLE_MAPPING = {
        "COM_50GAUI_1_C2C": "com_120d_8.json",
        "COM_100GAUI_2_C2C": "com_120d_8.json",
        "COM_200GAUI_4": "com_120d_8.json",
        "COM_400GAUI_8": "com_120d_8.json",
        "COM_100GBASE_KR4": "com_93_8.json",
        "COM_100GBASE_KP4": "com_94_17.json",
    }

    def __init__(self, standard):
        self.table_93a1 = {}
        self.filter_and_eq = {}
        self.io_control = {}
        self.operational = {}
        self.tdr_and_erl_options = {}
        self.noise_jitter = {}
        self.table_93a3 = {}
        self.table_92_12 = {}
        self.floating_tap_control = {}
        self.icn_fom_ild_parameters = {}
        self.receiver_testing = {}
        self.spisim_control = {}
        self.other_parameters = {}

        self._init()
        self.standard = standard

    @pyaedt_function_handler
    def _init(self):
        pass  # pragma: no cover

    @property
    def parameters(self):
        """All parameters."""
        temp = {
            **self.spisim_control,
            **self.table_93a1,
            **self.filter_and_eq,
            **self.io_control,
            **self.operational,
            **self.tdr_and_erl_options,
            **self.noise_jitter,
            **self.table_93a3,
            **self.table_92_12,
            **self.floating_tap_control,
            **self.icn_fom_ild_parameters,
            **self.receiver_testing,
            **self.other_parameters,
        }
        return temp

    @property
    def standard(self):
        """Standard name.

        Returns
        -------
        str
        """
        return self._standard  # pragma: no cover

    @standard.setter
    def standard(self, value):
        std_table = self._STD_TABLE_MAPPING[COMStandards(value).name]
        cfg_path = self._CFG_DIR / std_table
        self.load(cfg_path)
        self._standard = value

    @pyaedt_function_handler
    def set_parameter(self, keyword, value):
        """Set a COM parameter.

        Parameters
        ----------
        keyword : str,
            Keyword of the COM parameter.
        value : str,
            Value of the COM parameter.
        """
        if keyword in self.table_93a1:
            self.table_93a1[keyword] = value
        elif keyword in self.filter_and_eq:
            self.filter_and_eq[keyword] = value
        elif keyword in self.io_control:
            self.io_control[keyword] = value
        elif keyword in self.operational:
            self.operational[keyword] = value
        elif keyword in self.tdr_and_erl_options:
            self.tdr_and_erl_options[keyword] = value
        elif keyword in self.noise_jitter:
            self.noise_jitter[keyword] = value
        elif keyword in self.table_93a3:
            self.table_93a3[keyword] = value
        elif keyword in self.table_92_12:
            self.table_92_12[keyword] = value
        elif keyword in self.floating_tap_control:
            self.floating_tap_control[keyword] = value
        elif keyword in self.icn_fom_ild_parameters:
            self.icn_fom_ild_parameters[keyword] = value
        elif keyword in self.receiver_testing:
            self.receiver_testing[keyword] = value
        elif keyword in self.spisim_control:
            self.spisim_control[keyword] = value
        else:
            self.other_parameters[keyword] = value

    @pyaedt_function_handler
    def export(self, file_path):
        """Export COM parameter to a JSON file.

        Parameters
        ----------
        file_path : str
            Path of file.
        """
        temp = dict()
        temp["table_93a1"] = self.table_93a1
        temp["filter_and_eq"] = self.filter_and_eq
        temp["io_control"] = self.io_control
        temp["operational"] = self.operational
        temp["tdr_and_erl_options"] = self.tdr_and_erl_options
        temp["noise_jitter"] = self.noise_jitter
        temp["table_93a3"] = self.table_93a3
        temp["table_92_12"] = self.table_92_12
        temp["floating_tap_control"] = self.floating_tap_control
        temp["icn_fom_ild_parameters"] = self.icn_fom_ild_parameters
        temp["receiver_testing"] = self.receiver_testing
        temp["spisim_control"] = self.spisim_control
        temp["other_parameters"] = self.other_parameters

        with open(file_path, "w", encoding="utf-8") as f:
            f.write(json.dumps(temp, indent=4, ensure_ascii=False))

    @pyaedt_function_handler
    def load(self, file_path):
        """Load COM parameters from a JSON file.

        Parameters
        ----------
        file_path : str,
            Path of file.
        """
        self._init()
        with open(file_path) as f:  # pragma: no cover
            temp = json.load(f)

        for k, v in temp.items():  # pragma: no cover
            for k2, v2 in v.items():
                self.__getattribute__(k)[k2] = v2

    @pyaedt_function_handler
    def export_spisim_cfg(self, file_path):
        """Export COM parameter to a SPISim cfg file.

        Parameters
        ----------
        file_path : str, Path
            Full path of file.
        """
        with open(file_path, "w") as fp:
            fp.write("################################################################################\n")
            fp.write("# MODULE: COM\n")
            fp.write("# GENERATED ON\n")
            fp.write("################################################################################\n")
            for kw, v in self.parameters.items():
                if kw in spimsim_matlab_keywords_mapping:
                    kw = spimsim_matlab_keywords_mapping[kw]
                fp.write(f"# {kw.upper()}: {kw.upper()}\n")
                fp.write(f"{kw.upper()} = {v}\n")
        return True

    @pyaedt_function_handler
    def load_spisim_cfg(self, file_path):
        """Load a SPIsim configuration file.

        Parameters
        ----------
        file_path : str
            Path of the configuration file.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.
        """
        reverse_map = {j: i for i, j in spimsim_matlab_keywords_mapping.items()}

        with open(file_path, "r") as fp:
            lines = fp.readlines()
            for line in lines:
                if not line.startswith("#") and "=" in line:
                    split_line = [i.strip() for i in line.split("=")]
                    kw, value = split_line
                    if kw in reverse_map:  # Get Matlab keyword
                        kw = reverse_map[kw]
                    self.set_parameter(kw, value)
        return True


class COMParametersVer3p4(COMParameters):
    """Manages COM parameters of version 3.4."""

    def __init__(self, standard=1):
        super().__init__(standard)

    @pyaedt_function_handler
    def _init(self):
        """Initialize COM parameters."""
        self.table_93a1.update(
            {
                "f_b": "",
                "f_min": "",
                "Delta_f": "",
                "C_d": "",
                "L_s": "",
                "C_b": "",
                "z_p select": "",
                "z_p (TX)": "",
                "z_p (NEXT)": "",
                "z_p (FEXT)": "",
                "z_p (RX)": "",
                "C_p": "",
                "R_0": "",
                "R_d": "",
                "A_v": "",
                "A_fe": "",
                "A_ne": "",
                "AC_CM_RMS": "",
                "L": "",
                "M": "",
            }
        )
        self.filter_and_eq.update(
            {
                "f_r": "",
                "c(0)": "",
                "c(-1)": "",
                "c(-2)": "",
                "c(-3)": "",
                "c(1)": "",
                "N_b": "",
                "__b_max(1)": "",
                "__b_max(2..N_b)": "",
                "b_min(1)": "",
                "b_min(2..N_b)": "",
                "g_DC": "",
                "f_z": "",
                "f_p1": "",
                "f_p2": "",
                "g_DC_HP": "",
                "f_HP_PZ": "",
            }
        )
        self.io_control.update(
            {
                # "DIAGNOSTICS": "",
                # "DISPLAY_WINDOW": "",
                # "CSV_REPORT": "",
                "RESULT_DIR": "",
                # "SAVE_FIGURES": "",
                "Port Order": "",
                "RUNTAG": "",
                # "COM_CONTRIBUTION": "",
            }
        )
        self.operational.update(
            {
                "COM Pass threshold": "",
                "ERL Pass threshold": "",
                "DER_0": "",
                "T_r": "",
                "FORCE_TR": "",
                "Local Search": "",
                # "BREAD_CRUMBS": "",
                # "SAVE_CONFIG2MAT": "",
                # "PLOT_CM": "",
            }
        )
        self.tdr_and_erl_options.update(
            {
                "TDR": "",
                "ERL": "",
                "ERL_ONLY": "",
                "TR_TDR": "",
                "N": "",
                "beta_x": "",
                "rho_x": "",
                "fixture delay time": "",
                "TDR_W_TXPKG": "",
                "N_bx": "",
                "Tukey_Window": "",
            }
        )
        self.noise_jitter.update(
            {
                "sigma_RJ": "",
                "A_DD": "",
                "eta_0": "",
                "SNR_TX": "",
                "R_LM": "",
            }
        )
        self.table_93a3.update(
            {
                "package_tl_gamma0_a1_a2": "",
                "package_tl_tau": "",
                "package_Z_c": "",
            }
        )
        self.table_92_12.update(
            {
                "board_tl_gamma0_a1_a2": "",
                "board_tl_tau": "",
                "board_Z_c": "",
                "z_bp (TX)": "",
                "z_bp (NEXT)": "",
                "z_bp (FEXT)": "",
                "z_bp (RX)": "",
                "C_0": "",
                "C_1": "",
                "Include PCB": "",
            }
        )
        self.floating_tap_control.update(
            {
                "N_bg": "",
                "N_bf": "",
                "N_f": "",
                "bmaxg": "",
                "B_float_RSS_MAX": "",
                "N_tail_start": "",
            }
        )
        self.icn_fom_ild_parameters.update(
            {
                "f_v": "",
                "f_f": "",
                "f_n": "",
                "f_2": "",
                "A_ft": "",
                "A_nt": "",
            }
        )
        self.receiver_testing.update(
            {
                "RX_CALIBRATION": "",
                "Sigma BBN step": "",
            }
        )
        self.spisim_control.update(
            {
                "VERSION": "",
                "THRUSNP": "",
                "FEXTARY": "",
                "NEXTARY": "",
                "SPECTAG": "",
                "FSTTHRU": "",
                "NUMPORT": "",
                "GENHTML": "",
            }
        )
