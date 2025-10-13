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

from ansys.aedt.core.base import PyAedtBase
from ansys.aedt.core.generic.general_methods import pyaedt_function_handler


class ScatteringMethods(PyAedtBase):
    """Class containing all methods related to scattering matrix management that are common to Hfss, Circuit and
    Hfss3dLayout classes.
    """

    def __init__(self, app):
        self._app = app

    @property
    def get_all_sparameter_list(self, excitation_names=None):
        """List of all S parameters for a list of excitations.

        Parameters
        ----------
        excitation_names : list, optional
            List of excitations. The default is ``None``, in which case
            the S parameters for all excitations are to be provided.
            For example, ``["1", "2"]``.

        Returns
        -------
        list
            Strings representing the S parameters of the excitations.
            For example, ``["S(1, 1)", "S(1, 2)", S(2, 2)]``.

        """
        if not excitation_names:
            excitation_names = self._app.excitation_names
        spar = []
        k = 0
        for i in excitation_names:
            k = excitation_names.index(i)
            while k < len(excitation_names):
                spar.append(f"S({i},{excitation_names[k]})")
                k += 1
        return spar

    @pyaedt_function_handler(excitation_names="excitations", net_list="nets")
    def get_all_return_loss_list(self, excitations=None, excitation_name_prefix="", math_formula="", nets=None):
        """Get a list of all return losses for a list of excitations.

        Parameters
        ----------
        excitations : list, optional
            List of excitations. The default is ``None``, in which case
            the return losses for all excitations are provided.
            For example ``["1", "2"]``.
        excitation_name_prefix : string, optional
             Prefix to add to the excitation names. The default is ``""``,
        math_formula : str, optional
            One of the available AEDT mathematical formulas to apply. For example, ``abs, dB``.
        nets : list, optional
            List of nets to filter the output. The default is ``None``, in which case all parameters are returned.

        Returns
        -------
        list of str
            List of strings representing the return losses of the excitations.
            For example, ``["S(1, 1)", S(2, 2)]``.

        References
        ----------
        >>> oEditor.GetAllPorts
        """
        if excitations is None:
            excitations = []

        if not excitations:
            excitations = list(self._app.excitation_names)
        if excitation_name_prefix:
            excitations = [i for i in excitations if excitation_name_prefix.lower() in i.lower()]
        spar = []
        for i in excitations:
            if not nets or (nets and [net for net in nets if net in i]):
                if math_formula:
                    spar.append(f"{math_formula}(S({i},{i}))")
                else:
                    spar.append(f"S({i},{i})")
        return spar

    @pyaedt_function_handler(
        trlist="drivers",
        reclist="receivers",
        tx_prefix="drivers_prefix_name",
        rx_prefix="receivers_prefix_name",
        net_list="nets",
    )
    def get_all_insertion_loss_list(
        self, drivers=None, receivers=None, drivers_prefix_name="", receivers_prefix_name="", math_formula="", nets=None
    ):
        """Get a list of all insertion losses from two lists of excitations (driver and receiver).

        Parameters
        ----------
        drivers : list, optional
            List of drivers. The default is ``[]``. For example, ``["1"]``.
        receivers : list, optional
            List of receivers. The default is ``[]``. The number of drivers equals
            the number of receivers. For example, ``["2"]``.
        drivers_prefix_name : str, optional
            Prefix to add to driver names. For example, ``"DIE"``. The default is ``""``.
        receivers_prefix_name : str, optional
            Prefix to add to receiver names. For example, ``"BGA"``. The default is ``""``.
        math_formula : str, optional
            One of the available AEDT mathematical formulas to apply. For example, ``abs, dB``.
        nets : list, optional
            List of nets to filter the output. The default is ``None``, in which
            case all parameters are returned.

        Returns
        -------
        list of str
            List of strings representing insertion losses of the excitations.
            For example, ``["S(1,2)"]``.

        References
        ----------
        >>> oEditor.GetAllPorts
        """
        if drivers is None:
            drivers = [i for i in list(self._app.excitation_names)]
        if receivers is None:
            receivers = [i for i in list(self._app.excitation_names)]
        if drivers_prefix_name:
            drivers = [i for i in drivers if i.startswith(drivers_prefix_name)]
        if receivers_prefix_name:
            receivers = [i for i in receivers if i.startswith(receivers_prefix_name)]
        spar = []
        if not nets and len(drivers) != len(receivers):
            self.logger.error("The TX and RX lists should be the same length.")
            return False
        if nets:
            for el in nets:
                x = [i for i in drivers if el in i]
                y = [i for i in receivers if el in i]
                for x1 in x:
                    for y1 in y:
                        if x1[-2:] == y1[-2:] and x1 != y1:
                            if (
                                math_formula
                                and f"{math_formula}(S({x1},{y1}))" not in spar
                                and f"{math_formula}(S({y1},{x1}))" not in spar
                            ):
                                spar.append(f"{math_formula}(S({x1},{y1}))")
                            elif not math_formula and f"S({y1},{x1})" not in spar and f"S({x1},{y1})" not in spar:
                                spar.append(f"S({x1},{y1})")
                            break
        else:
            for i in drivers:
                for j in receivers:
                    if i == j:
                        continue
                    if (
                        math_formula
                        and f"{math_formula}(S({j},{i}))" not in spar
                        and f"{math_formula}(S({i},{j}))" not in spar
                    ):
                        spar.append(f"{math_formula}(S({i},{j}))")
                    elif not math_formula and f"S({i},{j})" not in spar and f"S({j},{i})" not in spar:
                        spar.append(f"S({i},{j})")
        return spar

    @pyaedt_function_handler(trlist="drivers", tx_prefix="drivers_prefix_name", net_list="nets")
    def get_next_xtalk_list(self, drivers=None, drivers_prefix_name="", math_formula="", nets=None):
        """Get a list of all the near end XTalks from a list of excitations (driver and receiver).

        Parameters
        ----------
        drivers : list, optional
            List of drivers. The default is ``None``. For example,
            ``["1", "2", "3"]``.
        drivers_prefix_name : str, optional
            Prefix to add to driver names. For example, ``"DIE"``.  The default is ``""``.
        math_formula : str, optional
            One of the available AEDT mathematical formulas to apply. For example, ``abs, dB``.
        nets : list, optional
            List of nets to filter the output. The default is ``None``, in which case
            all parameters are returned.

        Returns
        -------
        list of str
            List of strings representing near end XTalks of the excitations.
            For example, ``["S(1, 2)", "S(1, 3)", "S(2, 3)"]``.

        References
        ----------
        >>> oEditor.GetAllPorts
        """
        next_xtalks = []
        if not drivers:
            drivers = [i for i in list(self._app.excitation_names) if drivers_prefix_name in i]
        for i in drivers:
            if not nets or (nets and [net for net in nets if net in i]):
                k = drivers.index(i) + 1
                while k < len(drivers):
                    if math_formula:
                        next_xtalks.append(f"{math_formula}(S({i},{drivers[k]}))")
                    else:
                        next_xtalks.append(f"S({i},{drivers[k]})")
                    k += 1
        return next_xtalks

    @pyaedt_function_handler(
        trlist="drivers",
        reclist="receivers",
        tx_prefix="drivers_prefix_name",
        rx_prefix="receivers_prefix_name",
        net_list="nets",
    )
    def get_fext_xtalk_list(
        self,
        drivers=None,
        receivers=None,
        drivers_prefix_name="",
        receivers_prefix_name="",
        skip_same_index_couples=True,
        math_formula="",
        nets=None,
    ):
        """Geta list of all the far end XTalks from two lists of excitations (driver and receiver).

        Parameters
        ----------
        drivers : list, optional
            List of drivers. The default is ``[]``. For example,
            ``["1", "2"]``.
        receivers : list, optional
            List of receivers. The default is ``[]``. For example,
            ``["3", "4"]``.
        drivers_prefix_name : str, optional
            Prefix for driver names. For example, ``"DIE"``.  The default is ``""``.
        receivers_prefix_name : str, optional
            Prefix for receiver names. For examples, ``"BGA"`` The default is ``""``.
        skip_same_index_couples : bool, optional
            Whether to skip driver and receiver couples with the same index position.
            The default is ``True``, in which case the drivers and receivers
            with the same index position are considered insertion losses and
            excluded from the list.
        math_formula : str, optional
            One of the available AEDT mathematical formulas to apply. For example, ``abs, dB``.
        nets : list, optional
            List of nets to filter the output. The default is ``None``, in which case all
            parameters are returned.

        Returns
        -------
        list of str
            List of strings representing the far end XTalks of the excitations.
            For example, ``["S(1, 4)", "S(2, 3)"]``.

        References
        ----------
        >>> oEditor.GetAllPorts
        """
        fext = []
        if drivers is None:
            drivers = [i for i in list(self._app.excitation_names) if drivers_prefix_name in i]
        if receivers is None:
            receivers = [i for i in list(self._app.excitation_names) if receivers_prefix_name in i]
        for i in drivers:
            if not nets or (nets and [net for net in nets if net in i]):
                for k in receivers:
                    if not skip_same_index_couples or receivers.index(k) != drivers.index(i):
                        if math_formula:
                            fext.append(f"{math_formula}(S({i},{k}))")
                        else:
                            fext.append(f"S({i},{k})")
        return fext

    @pyaedt_function_handler(setup_name="setup", sweep_name="sweep")
    def get_touchstone_data(self, setup=None, sweep=None, variations=None):
        """
        Return a Touchstone data plot.

        Parameters
        ----------
        setup : list
            Name of the setup.
        sweep : str, optional
            Name of the sweep. The default value is ``None``.
        variations : dict, optional
            Dictionary of variation names. The default value is ``None``.

        Returns
        -------
        :class:`ansys.aedt.core.generic.touchstone_parser.TouchstoneData`
           Class containing all requested data.

        References
        ----------
        >>> oModule.GetSolutionDataPerVariation
        """
        from ansys.aedt.core.visualization.advanced.touchstone_parser import TouchstoneData

        if not setup:
            setup = self._app.setups[0].name

        if self._app.design_type != "Circuit Design" and not sweep:
            for s in self._app.setups:
                if s.name == setup:
                    sweep = s.sweeps[0].name
            solution = f"{setup} : {sweep}"
        else:
            solution = setup
        s_parameters = []
        expression = self._app.get_traces_for_plot(category="S")
        sol_data = self._app.post.get_solution_data(expression, solution, variations=variations)
        for i in range(sol_data.number_of_variations):
            sol_data.set_active_variation(i)
            s_parameters.append(TouchstoneData(solution_data=sol_data))
        return s_parameters

    @pyaedt_function_handler(setup_name="setup", sweep_name="sweep", file_name="output_file")
    def export_touchstone(
        self,
        setup=None,
        sweep=None,
        output_file=None,
        variations=None,
        variations_value=None,
        renormalization=False,
        impedance=None,
        gamma_impedance_comments=False,
    ):
        """Export a Touchstone file.

        Parameters
        ----------
        setup : str, optional
            Name of the setup that has been solved.
        sweep : str, optional
            Name of the sweep that has been solved.
        output_file : str, optional
            Full path and name for the Touchstone file.
            The default is ``None``, in which case the Touchstone file is exported to
            the working directory.
        variations : list, optional
            List of all parameter variations. For example, ``["$AmbientTemp", "$PowerIn"]``.
            The default is ``None``.
        variations_value : list, optional
            List of all parameter variation values. For example, ``["22cel", "100"]``.
            The default is ``None``.
        renormalization : bool, optional
            Perform renormalization before export.
            The default is ``False``.
        impedance : float, optional
            Real impedance value in ohm, for renormalization, if not specified considered 50 ohm.
            The default is ``None``.
        gamma_impedance_comments : bool, optional
            Include Gamma and Impedance values in comments.
            The default is ``False``.

        Returns
        -------
        str
            Filename when successful, ``False`` when failed.

        References
        ----------
        >>> oDesign.ExportNetworkData
        """
        if output_file is not None:
            output_file = str(output_file)

        return self._app._export_touchstone(
            setup_name=setup,
            sweep_name=sweep,
            file_name=output_file,
            variations=variations,
            variations_value=variations_value,
            renormalization=renormalization,
            impedance=impedance,
            comments=gamma_impedance_comments,
        )
