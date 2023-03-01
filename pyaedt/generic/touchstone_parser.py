import os
import re
from copy import deepcopy as copy

import numpy as np
import skrf
import skrf as rf
import matplotlib.pyplot as plt

from pyaedt.generic.general_methods import pyaedt_function_handler

REAL_IMAG = "RI"
MAG_ANGLE = "MA"
DB_ANGLE = "DB"

keys = {REAL_IMAG: ("real", "imag"), MAG_ANGLE: ("mag", "deg"), DB_ANGLE: ("db20", "deg")}


def _parse_ports_name(file):
    """Parse and interpret the option line in the touchstone file
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


class TouchstoneData(skrf.Network):
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
            skrf.Network.__init__(self, s=sdata_3d, frequency=freq_points, z0=50.0 + 0.0j, params=params)
            rf.stylely()
            self.port_names = ports

        elif os.path.exists(touchstone_file):
            skrf.Network.__init__(self, touchstone_file)
        pass

    def plot_insertion_losses(self, threshold=-3, plot=True):
        temp_list = []
        freq_idx = 0
        for i in self.port_tuples:
            loss = self.s_db[freq_idx, i[0], i[1]]
            if loss > threshold:
                temp_list.append(i)

        if plot:
            for i in temp_list:
                self.plot_s_db(*i)
            plt.show()
        return temp_list



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

        Example: excitation_names ["1","2"] is_touchstone_expression=False output ["S(1,1)",, S(2,2)]
        Example: excitation_names ["S(1,1)","S(1,2)", S(2,2)] is_touchstone_expression=True output ["S(1,1)",, S(2,2)]

        Parameters
        ----------
        excitation_names :
            list of excitation to include
        excitation_name_prefix :
             (Default value = '')

        Returns
        -------
        list, list
            list of string representing Return Losses of excitations

        """
        spar = []
        values = []
        if excitation_name_prefix:
            excitation_names = [i for i in self.port_names if excitation_name_prefix.lower() in i.lower()]
        else:
            excitation_names = [i for i in self.port_names]
        for i in excitation_names:
            spar.append("S({},{})".format(i, i))
            values.append([self.port_names.index(i), self.port_names.index(i)])
        return spar, values

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
        list, list
            List of string representing Insertion Losses of excitations.

        """
        spar = []
        trlist = [i for i in self.port_names if tx_prefix in i]
        receiver_list = [i for i in self.port_names if rx_prefix in i]
        values = []
        if len(trlist) != len(receiver_list):
            print("TX and RX should be same length lists")
            return False
        for i, j in zip(trlist, receiver_list):
            spar.append("S({},{})".format(i, j))
            values.append([self.port_names.index(i), self.port_names.index(j)])
        return spar, values

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
        list, list
            list of string representing Near End XTalks

        """
        next = []
        if tx_prefix:
            trlist = [i for i in self.port_names if tx_prefix in i]
        else:
            trlist = self.port_names
        values = []
        for i in trlist:
            k = trlist.index(i) + 1
            while k < len(trlist):
                next.append("S({},{})".format(i, trlist[k]))
                values.append([self.port_names.index(i), self.port_names.index(trlist[k])])
                k += 1
        return next, values

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
        reclist :
            list of Receiver to include
        rx_prefix : str
            prefix for RX (eg. "BGA")
        skip_same_index_couples : bool
            Boolean ignore TX and RX couple with same index. The default value is ``True``.

        Returns
        -------
        list, list
            List of string representing Far End XTalks.

        """
        fext = []
        trlist = [i for i in self.port_names if tx_prefix in i]
        reclist = [i for i in self.port_names if rx_prefix in i]
        values = []
        for i in trlist:
            for k in reclist:
                if not skip_same_index_couples or reclist.index(k) != trlist.index(i):
                    fext.append("S({},{})".format(i, k))
                    values.append([self.port_names.index(i), self.port_names.index(k)])
        return fext


@pyaedt_function_handler()
def get_worst_curve_from_solution_data(
    solution_data, freq_min=None, freq_max=None, worst_is_higher=True, curve_list=None
):
    """This method analyze a solution data object with multiple curves and find the worst curve returning its name and
     an ordered dictionary with each curve mean. Actual algorithm simply takes the mean of the magnitude over the
     frequency range

    Parameters
    ----------
    solution_data :
        SolutionData or TouchstoneData object
    freq_min :
        minimum frequency to analyze (None to 0) (Default value = None)
    freq_max :
        maximum frequency to analyze (None to max freq) (Default value = None)
    worst_is_higher : bool
        boolean. if True, the worst curve is the one with higher mean value (Default value = True)
    curve_list :
        list of curves on which to search. None to search on all curves (Default value = None)

    Returns
    -------
    type
        worst element str, dictionary of ordered expression and their mean

    """
    if not curve_list:
        curve_list = solution_data.expressions
    return_loss_freq = solution_data.sweeps["Freq"]
    if not freq_min:
        lower_id = 0
    else:
        lower_id = next(x[0] for x in enumerate(return_loss_freq) if x[1] >= freq_min)
    if not freq_max:
        higher_id = len(return_loss_freq) - 1
    else:
        if freq_max >= return_loss_freq[-1]:
            higher_id = len(return_loss_freq) - 1
        else:
            higher_id = next(x[0] for x in enumerate(return_loss_freq) if x[1] >= freq_max)

    dict_means = {}
    for el in curve_list:
        data1 = solution_data.data_magnitude(el)[lower_id:higher_id]
        mean1 = sum(data1) / len(data1)
        dict_means[el] = mean1
    dict_means = dict(sorted(dict_means.items(), key=lambda item: item[1], reverse=worst_is_higher))
    worst_el = next(iter(dict_means))
    return worst_el, dict_means


@pyaedt_function_handler()
def read_touchstone(file_path, port_names=None):
    """Load the contents of a Touchstone file into an NPort

    Parameters
    ----------
    file_path : str
        The path of the touchstone file.

    port_names : list, optional
         List of port names.

    Returns
    -------
    class:`pyaedt.generic.TouchoneParser.TouchstoneData`
        NPort holding data contained in the touchstone file.

    """
    data = TouchstoneData(touchstone_file=file_path, port_names=port_names)
    return data
