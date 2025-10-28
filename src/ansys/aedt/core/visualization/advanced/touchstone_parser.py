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
from copy import copy
import itertools
import os
from pathlib import Path
import re
import tempfile
from typing import List
from typing import Optional
from typing import Union
import warnings

import numpy as np

from ansys.aedt.core import Edb
from ansys.aedt.core.aedt_logger import pyaedt_logger as logger
from ansys.aedt.core.base import PyAedtBase
from ansys.aedt.core.generic.file_utils import open_file
from ansys.aedt.core.generic.general_methods import pyaedt_function_handler
from ansys.aedt.core.internal.aedt_versions import aedt_versions
from ansys.aedt.core.internal.checks import graphics_required
from ansys.aedt.core.internal.errors import AEDTRuntimeError

try:
    import skrf as rf
except ImportError:  # pragma: no cover
    warnings.warn(
        "The Scikit-rf module is required to run functionalities of TouchstoneData.\n"
        "Install with \n\npip install scikit-rf"
    )
    rf = None

REAL_IMAG = "RI"
MAG_ANGLE = "MA"
DB_ANGLE = "DB"

keys = {REAL_IMAG: ("real", "imag"), MAG_ANGLE: ("mag", "deg"), DB_ANGLE: ("db20", "deg")}


class TouchstoneData(rf.Network, PyAedtBase):
    """Contains data information from Touchstone Read call.

    Parameters
    ----------
    solution_data : :class:`ansys.aedt.core.modules.solutions.SolutionData`, optional
        HFSS solution data. The default is ``None``.
    touchstone_file : str or :class:'pathlib.Path', optional
        Path for the touchstone file. The default is ``None``.
    """

    def __init__(self, solution_data=None, touchstone_file=None):
        if touchstone_file is not None:
            touchstone_file = Path(touchstone_file)

        if solution_data is not None:
            self.solution_data = solution_data
            freq_points = solution_data.primary_sweep_values
            ports = []
            for i in solution_data.expressions:
                m = re.search(r"S\(\s*(\S+)\s*,\s*(\S+)\s*\)", i)
                if m:
                    ports.append(m.group(1))
                    ports.append(m.group(2))

            ports = list(set(ports))
            ports.sort()
            port_order = {ports.index(p): p for p in ports}
            sdata_3d = np.zeros([len(freq_points), len(ports), len(ports)], dtype=complex)
            for expression in solution_data.expressions:
                m = re.search(r"S\(\s*(\S+)\s*,\s*(\S+)\s*\)", expression)
                if m:
                    p_a = m.group(1)
                    p_b = m.group(2)
                p_a_number = ports.index(p_a)
                p_b_number = ports.index(p_b)
                sdata_real = solution_data.get_expression_data(expression, formula="real", convert_to_SI=True)[1]
                sdata_img = solution_data.get_expression_data(expression, formula="imag", convert_to_SI=True)[1]
                sdata_2d = np.array(sdata_real, dtype=complex) + 1j * np.array(sdata_img, dtype=complex)
                sdata_3d[:, p_a_number, p_b_number] = sdata_2d
                sdata_3d[:, p_b_number, p_a_number] = sdata_2d

            var = {}
            for name, value in solution_data.active_variation.items():
                var[name] = value
            params = {"variant": var, "port_order": port_order}
            rf.Network.__init__(self, s=sdata_3d, frequency=freq_points, z0=50.0 + 0.0j, params=params)
            rf.stylely()
            self.port_names = ports

        elif touchstone_file and touchstone_file.is_file():
            rf.Network.__init__(self, touchstone_file)
            if not self.port_names:
                with open(touchstone_file, "r") as f:
                    lines = f.readlines()
                    pnames = []
                    for line in lines:
                        if line.lower().startswith("! port"):
                            pnames.append(line.split("=")[-1].strip())
                    if not pnames:
                        pnames = [f"{i + 1}" for i in range(self.nports)]
                self.port_names = pnames
        self.log_x = True

    @pyaedt_function_handler()
    def reduce(
        self, ports: Union[List[str], List[int]], output_file: Optional[Union[str, Path]] = None, reordered: bool = True
    ) -> str:
        """Reduce the Touchstone file and export it.

        Parameters
        ----------
        ports : list
            List of ports or port indexes to use for the reduction.
        output_file : str or :class:'pathlib.Path', optional
            Output file path. The default is ``None``.
        reordered : bool, optional
            Whether to reorder the ports in the output file with given input order or not. The default is ``True``.

        Returns
        -------
        str
            Output file path

        """
        name = f"temp_touchstone.s{len(self.port_names)}p"
        temp_touch = Path(tempfile.gettempdir()) / name
        self.write_touchstone(temp_touch)
        network = rf.Network(str(temp_touch))
        reduced = []
        reduced_names = []
        for p in ports:
            if isinstance(p, str) and p in self.port_names:
                reduced.append(self.port_names.index(p))
                reduced_names.append(p)
            elif isinstance(p, int) and p < len(self.port_names):
                reduced.append(p)
                reduced_names.append(self.port_names[p])
        if reordered and reduced != sorted(reduced):
            network = network.renumbered(reduced, sorted(reduced))
        reduced_network = network.subnetwork(sorted(reduced))

        if output_file:
            output_file = Path(output_file)

        if not output_file:
            new_name = temp_touch.stem + f"_reduced.s{len(reduced)}p"
            output_file = temp_touch.parent / new_name
        elif output_file and f"s{len(reduced)}p" not in output_file.suffix:
            raise AEDTRuntimeError(f"Wrong number of ports in output file name. Ports should be s{len(reduced)}p")

        # Save the reduced 4-port network to a new Touchstone file
        reduced_network.write_touchstone(output_file)

        return str(output_file)

    @pyaedt_function_handler()
    def get_coupling_in_range(
        self,
        start_frequency=1e9,
        low_loss=-40,
        high_loss=-60,
        frequency_sample=5,
        output_file=None,
        aedb_path=None,
        design_name=None,
    ):
        """Get coupling losses, excluding return loss, that has at least one frequency point between a range of
        losses.

        Parameters
        ----------
        start_frequency : float, optional
            Specify frequency value below which not check will be done. The default is ``1e9``.
        low_loss: float, optional
            Specify range lower loss. The default is ``-40``.
        high_loss: float, optional
            Specify range higher loss. The default is ``-60``.
        frequency_sample : integer, optional
            Specify frequency sample at which coupling check will be done. The default is ``5``.
        output_file : str, or :class:'pathlib.Path', optional
            Output file path to save where identified coupling will be listed. The default is ``None``.
        aedb_path : path, optional
            Full path to the ``aedb`` folder. This project is used to identify ports location. The default is ``None``.
        design_name : string, optional
            Design name from the project where to identify ports location. The default is ``None``.

        Returns
        -------
         list
            List of S parameters in the range [high_loss, low_loss] to plot.

        """
        nb_freq = self.frequency.npoints
        k = 0
        k_start = 0

        # identify frequency index at which to start the check
        while k < nb_freq:
            if self.frequency.f[k] >= start_frequency:
                k_start = k
                break
            else:
                k = k + 1

        s_db = self.s_db[:, :, :]
        temp_list = []
        temp_file = []
        if aedb_path is not None:
            edbapp = Edb(edbpath=aedb_path, cellname=design_name, edbversion=aedt_versions.latest_version)
            for i in range(self.number_of_ports):
                for j in range(i, self.number_of_ports):
                    if i == j:
                        continue
                    for k in range(k_start, nb_freq, frequency_sample):
                        loss = s_db[k, i, j]
                        if high_loss < loss < low_loss:
                            temp_list.append((i, j))
                            port1 = self.port_names[i]
                            port2 = self.port_names[j]
                            # This if statement is mandatory as the codeword to use is different with regard to
                            # port type: Circuit(.location) or Gap(.position)
                            if edbapp.ports[port1].hfss_type == "Circuit":
                                loc_port_1 = edbapp.ports[port1].location
                            else:
                                loc_port_1 = edbapp.ports[port1].position
                            if edbapp.ports[port2].hfss_type == "Circuit":
                                loc_port_2 = edbapp.ports[port2].location
                            else:
                                loc_port_2 = edbapp.ports[port2].position
                            # This if statement is mandatory as some port return None for port location which will
                            # issue error on the formatting
                            if loc_port_1 is not None:
                                loc_port_1[0] = f"{loc_port_1[0]:.4f}"
                                loc_port_1[1] = f"{loc_port_1[1]:.4f}"
                            if loc_port_2 is not None:
                                loc_port_2[0] = f"{loc_port_2[0]:.4f}"
                                loc_port_2[1] = f"{loc_port_2[1]:.4f}"
                            sxy = f"S({port1},{port2})"
                            ports_location = f"{port1}: {loc_port_1}, {port2}: {loc_port_2}"
                            line = f"{sxy} Loss= {loss:.2f}dB Freq= {(self.f[k] * 1e-9):.3f}GHz, {ports_location}\n"
                            temp_file.append(line)
                            break
            edbapp.close()
        else:
            for i in range(self.number_of_ports):
                for j in range(i, self.number_of_ports):
                    if i == j:
                        continue
                    for k in range(k_start, nb_freq, frequency_sample):
                        loss = s_db[k, i, j]
                        if high_loss < loss < low_loss:
                            temp_list.append((i, j))
                            sxy = f"S({self.port_names[i]},{self.port_names[j]})"
                            line = f"{sxy} Loss= {loss:.2f}dB Freq= {(self.f[k] * 1e-9):.3f}GHz\n"
                            temp_file.append(line)
                            break
        if output_file is not None:
            output_file = Path(output_file)
            if output_file.is_file():
                logger.info("File " + str(output_file) + " exist and we be replace by new one.")
            with open_file(output_file, "w") as f:
                for s in temp_file:
                    f.write(s)
            logger.info("File " + str(output_file) + " created.")
            f.close()
        return temp_list

    @pyaedt_function_handler()
    def get_insertion_loss_index(self, threshold=-3):
        """Get all insertion losses.

        The first frequency point is used to determine whether two ports are shorted.

        Parameters
        ----------
        threshold : float, int, optional
            Threshold to determine shorted ports in dB. The default value is ``-3``.

        Returns
        -------
         list
            List of index couples representing insertion losses of excitations.

        """
        temp_list = []
        s_db = self.s_db[0:2, :, :]
        for i in self.port_tuples:
            if i[0] != i[1]:
                loss = s_db[0, i[0], i[1]]
                if loss > threshold:
                    temp_list.append(i)
                elif loss < -90:
                    loss = s_db[1, i[0], i[1]]
                    if loss > threshold:
                        temp_list.append(i)
        return temp_list

    @graphics_required
    def plot_insertion_losses(self, threshold=-3, plot=True):
        """Plot all insertion losses.

        The first frequency point is used to determine whether two ports are shorted.

        Parameters
        ----------
        threshold : float, int, optional
            Threshold to determine shorted ports in dB. The default value is ``-3``.
        plot : bool, optional
            Whether to plot. The default is ``True``.

        Returns
        -------
        list
            List of tuples representing insertion loss excitations.
        """
        import matplotlib.pyplot as plt

        temp_list = self.get_insertion_loss_index(threshold=threshold)
        if plot:
            for i in temp_list:
                self.plot_s_db(*i, logx=self.log_x)
            plt.show()
        return temp_list

    @graphics_required
    def plot(self, index_couples=None, show=True):
        """Plot a list of curves.

        Parameters
        ----------
        index_couples : list, optional
            List of indexes couple to plot. The default value is ``None`` to plot all ``port_tuples``.
        show : bool
            Whether to plot. The default value is ``True``.

        Returns
        -------
        :class:`matplotlib.plt`
        """
        import matplotlib.pyplot as plt

        if not index_couples:
            index_couples = self.port_tuples[:]

        for i in index_couples:
            self.plot_s_db(*i, logx=self.log_x)
        if show:
            plt.show()
        return True

    @graphics_required
    def plot_return_losses(self):
        """Plot all return losses.

        Returns
        -------
        bool
        """
        import matplotlib.pyplot as plt

        for i in np.arange(self.number_of_ports):
            self.plot_s_db(i, i, logx=self.log_x)
        plt.show()
        return True

    def get_mixed_mode_touchstone_data(self, num_of_diff_ports=None, port_ordering="1234"):
        """Transform network from single ended parameters to generalized mixed mode parameters.

        Parameters
        ----------
        num_of_diff_ports : int, optional
            The number of differential ports.
        port_ordering : str, optional
            The current port ordering. Options are ``"1234"``, ``"1324"``. The default
            is ``1234``.

        Returns
        -------
        class:`ansys.aedt.core.generic.touchstone_parser.TouchstoneData`

        """
        ts_diff = copy(self)
        port_count = len(ts_diff.port_names)

        if num_of_diff_ports is None:
            num_of_diff_ports = port_count // 4 * 2

        if port_ordering == "1234":
            pass
        elif port_ordering == "1324":
            temp_port_order = np.arange(port_count)
            for i in np.arange(port_count):
                if i % 4 == 1:
                    temp_port_order[i] = temp_port_order[i] + 1
                elif i % 4 == 2:
                    temp_port_order[i] = temp_port_order[i] - 1

            port_order = np.arange(port_count)
            new_port_order = np.arange(port_count)
            new_port_order[: len(temp_port_order)] = temp_port_order

            ts_diff.renumber(port_order, new_port_order)
        else:
            logger.error("Invalid input provided for 'port_ordering'.")
            return False

        ts_diff.se2gmm(num_of_diff_ports)

        new_port_names = [f"D{i}" for i in np.arange(num_of_diff_ports)]
        new_port_names.extend([f"C{i}" for i in np.arange(num_of_diff_ports)])
        ts_diff.port_names[: len(new_port_names)] = new_port_names
        return ts_diff

    @pyaedt_function_handler()
    def get_return_loss_index(self, excitation_name_prefix=""):
        """Get the list of all the return loss from a list of excitations.

        If no excitation is provided it will provide a full list of return losses.

        Example: excitation_names ["1","2"] is_touchstone_expression=False output ["S(1,1)", S(2,2)]
        Example: excitation_names ["S(1,1)","S(1,2)", S(2,2)] is_touchstone_expression=True output ["S(1,1)", S(2,2)]

        Parameters
        ----------
        excitation_name_prefix :str, optional
            Prefix of the excitation. The default value is ``""``.

        Returns
        -------
        list
            List of index couples representing return losses of excitations.

        """
        values = []
        if excitation_name_prefix:
            excitation_names = [i for i in self.port_names if excitation_name_prefix.lower() in i.lower()]
        else:
            excitation_names = [i for i in self.port_names]
        for i in excitation_names:
            values.append([self.port_names.index(i), self.port_names.index(i)])
        return values

    @pyaedt_function_handler()
    def get_insertion_loss_index_from_prefix(self, tx_prefix, rx_prefix):
        """Get the list of all the insertion losses from prefix.

        Parameters
        ----------
        tx_prefix : str
            Prefix for TX (eg. "DIE").
        rx_prefix : str
            Prefix for RX (eg. "BGA").

        Returns
        -------
        list
            List of index couples representing Insertion Losses of excitations.

        """
        trlist = [i for i in self.port_names if tx_prefix in i]
        receiver_list = [i for i in self.port_names if rx_prefix in i]
        values = []
        if len(trlist) != len(receiver_list):
            logger.error("TX and RX should be same length lists.")
            return False
        for i, j in zip(trlist, receiver_list):
            values.append([self.port_names.index(i), self.port_names.index(j)])
        return values

    @pyaedt_function_handler()
    def get_next_xtalk_index(self, tx_prefix=""):
        """Get the list of all the Near End XTalk a list of excitation.

        Optionally prefix can be used to retrieve driver names.
        Example: excitation_names ["1", "2", "3"] output ["S(1,2)", "S(1,3)", "S(2,3)"].

        Parameters
        ----------
        tx_prefix :str, optional
            Prefix for TX (eg. "DIE"). The default value is ``""``.

        Returns
        -------
        list
            List of index couples representing Near End XTalks.
        """
        if tx_prefix:
            trlist = [i for i in self.port_names if tx_prefix in i]
        else:
            trlist = self.port_names
        values = []
        for i in trlist:
            k = trlist.index(i) + 1
            while k < len(trlist):
                values.append([self.port_names.index(i), self.port_names.index(trlist[k])])
                k += 1
        return values

    @pyaedt_function_handler()
    def get_fext_xtalk_index_from_prefix(self, tx_prefix, rx_prefix, skip_same_index_couples=True):
        """Get the list of all the Far End XTalk from a list of excitations and a prefix that will
        be used to retrieve driver and receivers names.
        If skip_same_index_couples is true, the tx and rx with same index
        position will be considered insertion losses and excluded from the list.

        Parameters
        ----------
        tx_prefix : str
            prefix for TX (eg. "DIE")
        rx_prefix : str
            prefix for RX (eg. "BGA")
        skip_same_index_couples : bool
            Boolean ignore TX and RX couple with same index. The default value is ``True``.

        Returns
        -------
        list
            List of index couples representing Far End XTalks.
        """
        trlist = [i for i in self.port_names if tx_prefix in i]
        reclist = [i for i in self.port_names if rx_prefix in i]
        values = []
        for i in trlist:
            for k in reclist:
                if not skip_same_index_couples or reclist.index(k) != trlist.index(i):
                    values.append([self.port_names.index(i), self.port_names.index(k)])
        return values

    @graphics_required
    def plot_next_xtalk_losses(self, tx_prefix=""):
        """Plot all next crosstalk curves.

        Parameters
        ----------
        tx_prefix: str, optional
            Prefix for TX. The default value is ``""``.

        Returns
        -------
        bool
        """
        import matplotlib.pyplot as plt

        index = self.get_next_xtalk_index(tx_prefix=tx_prefix)

        for ind in index:
            self.plot_s_db(ind[0], ind[1], logx=self.log_x)
        plt.show()
        return True

    @graphics_required
    def plot_fext_xtalk_losses(self, tx_prefix, rx_prefix, skip_same_index_couples=True):
        """Plot all fext crosstalk curves.

        Parameters
        ----------
        tx_prefix : str
            Prefix for TX (eg. "DIE").
        rx_prefix : str
            Prefix for RX (eg. "BGA").
        skip_same_index_couples : bool, optional
            Boolean ignore TX and RX couple with same index. The default value is ``True``.

        Returns
        -------
        bool
        """
        import matplotlib.pyplot as plt

        index = self.get_fext_xtalk_index_from_prefix(
            tx_prefix=tx_prefix, rx_prefix=rx_prefix, skip_same_index_couples=skip_same_index_couples
        )
        for ind in index:
            self.plot_s_db(ind[0], ind[1], logx=self.log_x)
        plt.show()
        return True

    @pyaedt_function_handler()
    @graphics_required
    def get_worst_curve(self, freq_min=None, freq_max=None, worst_is_higher=True, curve_list=None, plot=True):
        """Analyze a solution data object with multiple curves and find the worst curve.

        Take the mean of the magnitude over the frequency range.

        Parameters
        ----------
        freq_min : float, optional
            Minimum frequency to analyze in GHz (None to 0). The default value is ``None``.
        freq_max : float, optional
            Maximum frequency to analyze in GHz (None to max freq). The default value is ``None``.
        worst_is_higher : bool
            Worst curve is the one with higher mean value. The default value is ``True``.
        curve_list : list
            List of [m,n] index of curves on which to search. None to search on all curves.
            The default value is ``None``.
        plot : bool, optional
            Whether to plot or not the chart. The default value is ``True``.

        Returns
        -------
        tuple
            Worst element, dictionary of ordered expression.
        """
        import matplotlib.pyplot as plt

        return_loss_freq = [float(i.center) for i in list(self.frequency)]
        if not freq_min:
            lower_id = 0
        else:
            lower_id = next(x[0] for x in enumerate(return_loss_freq) if x[1] >= freq_min * 1e9)
        if not freq_max:
            higher_id = len(return_loss_freq) - 1
        else:
            if freq_max * 1e9 >= return_loss_freq[-1]:
                higher_id = len(return_loss_freq) - 1
            else:
                higher_id = next(x[0] for x in enumerate(return_loss_freq) if x[1] >= freq_max * 1e9)

        dict_means = {}
        if not curve_list:
            curve_list = list(itertools.combinations(range(0, len(self.port_names)), 2))
            for i in range(0, len(self.port_names)):
                curve_list.append([i, i])
        for el in curve_list:
            data1 = np.absolute(self.s[lower_id:higher_id, el[0], el[1]])
            mean1 = sum(data1) / len(data1)
            dict_means[tuple(el)] = mean1
        dict_means = dict(sorted(dict_means.items(), key=lambda item: item[1], reverse=worst_is_higher))
        worst_el = next(iter(dict_means))
        if plot:  # pragma: no cover
            self.plot_s_db(*worst_el, logx=self.log_x)
            plt.show()
        return worst_el, dict_means


@pyaedt_function_handler(file_path="input_file")
def read_touchstone(input_file):
    """Load the contents of a Touchstone file into an NPort.

    Parameters
    ----------
    input_file : str
        The path of the touchstone file.

    Returns
    -------
    class:`ansys.aedt.core.generic.touchstone_parser.TouchstoneData`
        NPort holding data contained in the touchstone file.

    """
    data = TouchstoneData(touchstone_file=input_file)
    return data


@pyaedt_function_handler(folder="input_dir")
def check_touchstone_files(input_dir="", passivity=True, causality=True):
    """Check passivity and causality for all Touchstone files included in the folder.

    .. warning::

        Do not execute this function with untrusted function argument, environment
        variables or pyaedt global settings.
        See the :ref:`security guide<ref_security_consideration>` for details.

    Parameters
    ----------
    input_dir : str or :class:'pathlib.Path', optional
        Folder path. The default is ``""``.
    passivity : bool, optional
        Whether the passivity check is enabled, The default is ``True``.
    causality : bool, optional
        Whether the causality check is enabled. The default is ``True``.

    Returns
    -------
    dict
        Dictionary with the SNP file name as the key and a list if the passivity and/or causality checks are enabled.
        The first element in the list is a str with ``"passivity"`` or ``"causality"`` as a value. The second element
        is a Boolean that is set to ``True`` when the criteria passed or ``False`` otherwise. The last element
        is a string with the log information.

    """
    import subprocess  # nosec

    out = {}
    snp_files = find_touchstone_files(input_dir)
    if not snp_files:
        return out
    aedt_install_folder = list(aedt_versions.installed_versions.values())[0]
    for file_name, path in snp_files.items():
        out[file_name] = []
        if os.name == "nt":
            genequiv_path = Path(aedt_install_folder) / "genequiv.exe"
        else:
            genequiv_path = Path(aedt_install_folder) / "genequiv"
        cmd = [str(genequiv_path)]
        if passivity:
            cmd.append("-checkpassivity")
        if causality:
            cmd.append("-checkcausality")

        cmd.append(path)
        my_env = os.environ.copy()
        result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=my_env, text=True, check=True)  # nosec
        output_lst = result.stdout.splitlines()

        for line in output_lst:
            if "Input data" in line and passivity:
                msg_log = line[17:]
                is_passive = True
                if "non-passive" in msg_log:
                    is_passive = False
                out[file_name].append(["passivity", is_passive, msg_log])
            if "Maximum causality" in line and causality:
                msg_log = line[17:]
                is_causal = True
                try:
                    causality_check = float(msg_log.split("Maximum causality error: ")[-1].split("for entry")[0])
                    if not causality_check == 0.0:
                        is_causal = False
                except Exception:
                    is_causal = False
                    raise Exception("Failed evaluating causality value.")
                out[file_name].append(["causality", is_causal, msg_log])
            if "Causality check is inconclusive" in line and causality:
                is_causal = False
                out[file_name].append(["causality", is_causal, line[17:]])
    return out


@pyaedt_function_handler()
def find_touchstone_files(input_dir):
    """Get all Touchstone files in a directory.

    Parameters
    ----------
    input_dir : str or :class:'pathlib.Path'
        Folder path.

    Returns
    -------
    dict
        Dictionary with the SNP file names as the key and the absolute path as the value.
    """
    out = {}
    input_dir = Path(input_dir)
    if not input_dir.exists():
        return out
    pat_snp = re.compile(r"\.s\d+p$", re.IGNORECASE)
    files = {f.name: input_dir / f.name for f in input_dir.iterdir() if f.is_file() and re.search(pat_snp, f.name)}

    pat_ts = re.compile(r"\.ts$")
    for f in input_dir.iterdir():
        if f.is_file() and re.search(pat_ts, f.name):
            files[f.name] = f.resolve()

    return files
