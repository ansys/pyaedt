# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 - 2024 ANSYS, Inc. and/or its affiliates.
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
import re
import subprocess

from pyaedt.generic.general_methods import is_ironpython
from pyaedt.misc.misc import installed_versions

if not is_ironpython:
    import matplotlib.pyplot as plt
    import numpy as np
    import skrf as rf

from pyaedt.generic.general_methods import pyaedt_function_handler

REAL_IMAG = "RI"
MAG_ANGLE = "MA"
DB_ANGLE = "DB"

keys = {REAL_IMAG: ("real", "imag"), MAG_ANGLE: ("mag", "deg"), DB_ANGLE: ("db20", "deg")}


def _parse_ports_name(file):
    """Parse and interpret the option line in the touchstone file.

    Parameters
    ----------
    file : str
        Path of the touchstone file.

    Returns
    -------
    List of str
        Names of the ports in the touchstone file.

    """
    portnames = []
    line = file.readline()
    while not line.startswith("! Port"):
        line = file.readline()
    while line.startswith("! Port"):
        portnames.append(line.split(" = ")[1].strip())
        line = file.readline()
    return portnames


class TouchstoneData(rf.Network):
    """Contains data information from Touchstone Read call"""

    def __init__(self, solution_data=None, touchstone_file=None):
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
                sdata_real = solution_data.data_real(expression, True)
                sdata_img = solution_data.data_imag(expression, True)
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

        elif os.path.exists(touchstone_file):
            rf.Network.__init__(self, touchstone_file)
        self.log_x = True

    @pyaedt_function_handler()
    def get_insertion_loss_index(self, threshold=-3):
        """Get all insertion losses. The first frequency point is used to determine whether two
        ports are shorted.

        Parameters
        ----------
        threshold : float, int, optional
            Threshold to determine shorted ports in dB.

        Returns
        -------
         list
            List of index couples representing Insertion Losses of excitations.

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

    def plot_insertion_losses(self, threshold=-3, plot=True):
        """Plot all insertion losses. The first frequency point is used to determine whether two
        ports are shorted.

        Parameters
        ----------
        threshold : float, int, optional
            Threshold to determine shorted ports in dB.
        plot: bool
            Whether to plot.

        Returns
        -------
        list
            List of tuples representing insertion loss excitations.
        """
        temp_list = self.get_insertion_loss_index(threshold=threshold)
        if plot:  # pragma: no cover
            for i in temp_list:
                self.plot_s_db(*i, logx=self.log_x)
            plt.show()
        return temp_list

    def plot(self, index_couples=None, show=True):
        """Plot a list of curves.

        Parameters
        ----------
        index_couples : list, optional
            List of indexes couple to plot. Default is ``None`` to plot all ``port_tuples``.
        show: bool
            Whether to plot. Default is ``True``.

        Returns
        -------
        :class:`matplotlib.plt`
        """

        if not index_couples:
            index_couples = self.port_tuples[:]

        for i in index_couples:
            self.plot_s_db(*i, logx=self.log_x)
        if show:
            plt.show()
        return plt

    def plot_return_losses(self):  # pragma: no cover
        """Plot all return losses.

        Parameters
        ----------
        Returns
        -------
        bool
        """
        for i in np.arange(self.number_of_ports):
            self.plot_s_db(i, i, logx=self.log_x)
        plt.show()
        return True

    def get_mixed_mode_touchstone_data(self, num_of_diff_ports=None, port_ordering="1234"):
        """Transform network from single ended parameters to generalized mixed mode parameters.

        Example 1, an N-port single-ended network with port order 1234 is converted to mixed-mode
        parameters.

             A                                  B
             +------------+                     +-----------+
           0-|s0========s2|-2                 0-|d0=======d1|-1
           1-|s1========s3|-3                 2-|d2=======d3|-3
            ...          ...     =se2gmm=>     ...         ...
        2N-4-|s2N-4==s2N-2|-2N-2           2N-4-|cN-4===cN-3|-2N-3
        2N-3-|s2N-3==s2N-1|-2N-1           2N-2-|cN-2===cN-1|-2N-1
             +------------+                     +-----------+

        Example 2, an N-port single-ended network with port order 1324 is converted to mixed-mode
        parameters.

             A                                  B
             +------------+                     +-----------+
           0-|s0========s2|-1                 0-|d0=======d1|-1
           2-|s1========s3|-3                 2-|d2=======d3|-3
            ...          ...     =se2gmm=>     ...         ...
        2N-4-|s2N-4==s2N-2|-2N-3           2N-4-|cN-4===cN-3|-2N-3
        2N-2-|s2N-3==s2N-1|-2N-1           2N-2-|cN-2===cN-1|-2N-1
             +------------+                     +-----------+

        Parameters
        ----------
        num_of_diff_ports : int, optional
            The number of differential ports.
        port_ordering : str, optional
            The current port ordering. Options are ``"1234"``, ``"1324"``. The default
            is ``1234``

        Returns
        -------
        TouchstoneData

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
            return False

        ts_diff.se2gmm(num_of_diff_ports)

        new_port_names = ["D{}".format(i) for i in np.arange(num_of_diff_ports)]
        new_port_names.extend(["C{}".format(i) for i in np.arange(num_of_diff_ports)])
        ts_diff.port_names[: len(new_port_names)] = new_port_names
        return ts_diff

    @pyaedt_function_handler()
    def get_return_loss_index(self, excitation_name_prefix=""):
        """Get the list of all the Returnloss from a list of exctitations.

        If no excitation is provided it will provide a full list of return losses.

        Example: excitation_names ["1","2"] is_touchstone_expression=False output ["S(1,1)", S(2,2)]
        Example: excitation_names ["S(1,1)","S(1,2)", S(2,2)] is_touchstone_expression=True output ["S(1,1)", S(2,2)]

        Parameters
        ----------

        excitation_name_prefix :
             (Default value = '')

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
        """Get the list of all the Insertion Losses from prefix.

        Parameters
        ----------
        expressions :
            list of Drivers to include or all nets
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
            print("TX and RX should be same length lists")
            return False
        for i, j in zip(trlist, receiver_list):
            values.append([self.port_names.index(i), self.port_names.index(j)])
        return values

    @pyaedt_function_handler()
    def get_next_xtalk_index(self, tx_prefix=""):
        """Get the list of all the Near End XTalk a list of excitation. Optionally prefix can
        be used to retrieve driver names.
        Example: excitation_names ["1", "2", "3"] output ["S(1,2)", "S(1,3)", "S(2,3)"]

        Parameters
        ----------
        tx_prefix :
            prefix for TX (eg. "DIE") (Default value = "")

        Returns
        -------
        list
            list of index couples representing Near End XTalks

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
        """Get the list of all the Far End XTalk from a list of exctitations and a prefix that will
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

    def plot_next_xtalk_losses(self, tx_prefix=""):
        """Plot all next crosstalk curves.

        Parameters
        ----------
        Returns
        -------
        bool
        """
        index = self.get_next_xtalk_index(tx_prefix=tx_prefix)

        for ind in index:
            self.plot_s_db(ind[0], ind[1], logx=self.log_x)
        plt.show()
        return True

    def plot_fext_xtalk_losses(self, tx_prefix, rx_prefix, skip_same_index_couples=True):
        """Plot all fext crosstalk curves.

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
        bool
        """
        index = self.get_fext_xtalk_index_from_prefix(
            tx_prefix=tx_prefix, rx_prefix=rx_prefix, skip_same_index_couples=skip_same_index_couples
        )
        for ind in index:
            self.plot_s_db(ind[0], ind[1], logx=self.log_x)
        plt.show()
        return True

    @pyaedt_function_handler()
    def get_worst_curve(self, freq_min=None, freq_max=None, worst_is_higher=True, curve_list=None, plot=True):
        """This method analyze a solution data object with multiple curves and
        find the worst curve returning its name and an ordered dictionary with each curve mean.
        Actual algorithm simply takes the mean of the magnitude over the frequency range.

        Parameters
        ----------
        freq_min : float, optional
            minimum frequency to analyze in GHz (None to 0). Default value is ``None``.
        freq_max : float, optional
            maximum frequency to analyze in GHz (None to max freq). Default value is ``None``.
        worst_is_higher : bool
            boolean. if True, the worst curve is the one with higher mean value. Default value is ``None``.
        curve_list : list
            List of [m,n] index of curves on which to search. None to search on all curves. Default value is ``None``.

        Returns
        -------
        type
            worst element str, dictionary of ordered expression and their mean

        """

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


@pyaedt_function_handler()
def read_touchstone(file_path):
    """Load the contents of a Touchstone file into an NPort.

    Parameters
    ----------
    file_path : str
        The path of the touchstone file.

    Returns
    -------
    class:`pyaedt.generic.touchstone_parser.TouchstoneData`
        NPort holding data contained in the touchstone file.

    """
    data = TouchstoneData(touchstone_file=file_path)
    return data


@pyaedt_function_handler()
def check_touchstone_files(folder="", passivity=True, causality=True):
    """Check passivity and causality for all Touchstone files included in the folder.

    Parameters
    ----------
    folder : str
        Folder path. The default is ``""``.
    passivity : bool, optional
        Whether the passivity check is enabled, The default is ``True``.
    causality : bool, optional
        Whether the causality check is enabled. The default is ``True``.

    Returns
    ----------
    dict
        Dictionary with the SNP file name as the key and a list if the passivity and/or causality checks are enabled.
        The first element in the list is a str with ``"passivity"`` or ``"causality"`` as a value. The second element
        is a Boolean that is set to ``True`` when the criteria passed or ``False`` otherwise. The last element
        is a string with the log information.

    """
    out = {}
    if not os.path.exists(folder):
        return out
    aedt_install_folder = list(installed_versions().values())[0]
    pat_snp = re.compile("\.s\d+p$")
    sNpFiles = {f: os.path.join(folder, f) for f in os.listdir(folder) if re.search(pat_snp, f)}
    pat_ts = re.compile("\.ts$")
    for f in os.listdir(folder):
        if re.search(pat_ts, f):
            sNpFiles[f] = os.path.join(folder, f)
    if sNpFiles == {}:
        return out
    for snpf in sNpFiles:
        out[snpf] = []
        if os.name == "nt":
            genequiv_path = os.path.join(aedt_install_folder, "genequiv.exe")
        else:
            genequiv_path = os.path.join(aedt_install_folder, "genequiv")
        cmd = [genequiv_path]
        if passivity:
            cmd.append("-checkpassivity")
        if causality:
            cmd.append("-checkcausality")

        cmd.append(sNpFiles[snpf])
        my_env = os.environ.copy()
        p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=my_env)  # nosec
        output = p.communicate()
        output_str = str(output[0])
        output_lst = output_str.split("\\r\\n")

        if len(output_lst) == 1:
            output_lst = output_str.splitlines()
        for line in output_lst:
            if "Input data" in line and passivity:
                msg_log = line[17:]
                is_passive = True
                if "non-passive" in msg_log:
                    is_passive = False
                out[snpf].append(["passivity", is_passive, msg_log])
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
                out[snpf].append(["causality", is_causal, msg_log])
            if "Causality check is inconclusive" in line and causality:
                is_causal = False
                out[snpf].append(["causality", is_causal, line[17:]])
    return out
