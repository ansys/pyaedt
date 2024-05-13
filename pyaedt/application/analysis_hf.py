from pyaedt.generic.general_methods import pyaedt_function_handler


class ScatteringMethods(object):
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
            excitation_names = self._app.excitations
        spar = []
        k = 0
        for i in excitation_names:
            k = excitation_names.index(i)
            while k < len(excitation_names):
                spar.append("S({},{})".format(i, excitation_names[k]))
                k += 1
        return spar

    @pyaedt_function_handler()
    def get_all_return_loss_list(
        self, excitation_names=None, excitation_name_prefix="", math_formula="", net_list=None
    ):
        """Get a list of all return losses for a list of excitations.

        Parameters
        ----------
        excitation_names : list, optional
            List of excitations. The default is ``None``, in which case
            the return losses for all excitations are provided.
            For example ``["1", "2"]``.
        excitation_name_prefix : string, optional
             Prefix to add to the excitation names. The default is ``""``,
        math_formula : str, optional
            One of the available AEDT mathematical formulas to apply. For example, ``abs, dB``.
        net_list : list, optional
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
        if excitation_names == None:
            excitation_names = []

        if not excitation_names:
            excitation_names = list(self._app.excitations)
        if excitation_name_prefix:
            excitation_names = [i for i in excitation_names if excitation_name_prefix.lower() in i.lower()]
        spar = []
        for i in excitation_names:
            if not net_list or (net_list and [net for net in net_list if net in i]):
                if math_formula:
                    spar.append("{}(S({},{}))".format(math_formula, i, i))
                else:
                    spar.append("S({},{})".format(i, i))
        return spar

    @pyaedt_function_handler()
    def get_all_insertion_loss_list(
        self, trlist=None, reclist=None, tx_prefix="", rx_prefix="", math_formula="", net_list=None
    ):
        """Get a list of all insertion losses from two lists of excitations (driver and receiver).

        Parameters
        ----------
        trlist : list, optional
            List of drivers. The default is ``[]``. For example, ``["1"]``.
        reclist : list, optional
            List of receivers. The default is ``[]``. The number of drivers equals
            the number of receivers. For example, ``["2"]``.
        tx_prefix : str, optional
            Prefix to add to driver names. For example, ``"DIE"``. The default is ``""``.
        rx_prefix : str, optional
            Prefix to add to receiver names. For example, ``"BGA"``. The default is ``""``.
        math_formula : str, optional
            One of the available AEDT mathematical formulas to apply. For example, ``abs, dB``.
        net_list : list, optional
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
        if trlist is None:
            trlist = [i for i in list(self._app.excitations)]

        if reclist is None:
            reclist = [i for i in list(self._app.excitations)]
        if tx_prefix:
            trlist = [i for i in trlist if i.startswith(tx_prefix)]
        if rx_prefix:
            reclist = [i for i in reclist if i.startswith(rx_prefix)]
        spar = []
        if not net_list and len(trlist) != len(reclist):
            self.logger.error("The TX and RX lists should be the same length.")
            return False
        if net_list:
            for el in net_list:
                x = [i for i in trlist if el in i]
                y = [i for i in reclist if el in i]
                for x1 in x:
                    for y1 in y:
                        if x1[-2:] == y1[-2:]:
                            if math_formula:
                                spar.append("{}(S({},{}))".format(math_formula, x1, y1))
                            else:
                                spar.append("S({},{})".format(x1, y1))
                            break
        else:
            for i, j in zip(trlist, reclist):
                if math_formula:
                    spar.append("{}(S({},{}))".format(math_formula, i, j))
                else:
                    spar.append("S({},{})".format(i, j))
        return spar

    @pyaedt_function_handler()
    def get_next_xtalk_list(self, trlist=None, tx_prefix="", math_formula="", net_list=None):
        """Get a list of all the near end XTalks from a list of excitations (driver and receiver).

        Parameters
        ----------
        trlist : list, optional
            List of drivers. The default is ``None``. For example,
            ``["1", "2", "3"]``.
        tx_prefix : str, optional
            Prefix to add to driver names. For example, ``"DIE"``.  The default is ``""``.
        math_formula : str, optional
            One of the available AEDT mathematical formulas to apply. For example, ``abs, dB``.
        net_list : list, optional
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
        if not trlist:
            trlist = [i for i in list(self._app.excitations) if tx_prefix in i]
        for i in trlist:
            if not net_list or (net_list and [net for net in net_list if net in i]):
                k = trlist.index(i) + 1
                while k < len(trlist):
                    if math_formula:
                        next_xtalks.append("{}(S({},{}))".format(math_formula, i, trlist[k]))
                    else:
                        next_xtalks.append("S({},{})".format(i, trlist[k]))
                    k += 1
        return next_xtalks

    @pyaedt_function_handler()
    def get_fext_xtalk_list(
        self,
        trlist=None,
        reclist=None,
        tx_prefix="",
        rx_prefix="",
        skip_same_index_couples=True,
        math_formula="",
        net_list=None,
    ):
        """Geta list of all the far end XTalks from two lists of excitations (driver and receiver).

        Parameters
        ----------
        trlist : list, optional
            List of drivers. The default is ``[]``. For example,
            ``["1", "2"]``.
        reclist : list, optional
            List of receiver. The default is ``[]``. For example,
            ``["3", "4"]``.
        tx_prefix : str, optional
            Prefix for driver names. For example, ``"DIE"``.  The default is ``""``.
        rx_prefix : str, optional
            Prefix for receiver names. For examples, ``"BGA"`` The default is ``""``.
        skip_same_index_couples : bool, optional
            Whether to skip driver and receiver couples with the same index position.
            The default is ``True``, in which case the drivers and receivers
            with the same index position are considered insertion losses and
            excluded from the list.
        math_formula : str, optional
            One of the available AEDT mathematical formulas to apply. For example, ``abs, dB``.
        net_list : list, optional
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
        if trlist is None:
            trlist = [i for i in list(self._app.excitations) if tx_prefix in i]
        if reclist is None:
            reclist = [i for i in list(self._app.excitations) if rx_prefix in i]
        for i in trlist:
            if not net_list or (net_list and [net for net in net_list if net in i]):
                for k in reclist:
                    if not skip_same_index_couples or reclist.index(k) != trlist.index(i):
                        if math_formula:
                            fext.append("{}(S({},{}))".format(math_formula, i, k))
                        else:
                            fext.append("S({},{})".format(i, k))
        return fext

    @pyaedt_function_handler()
    def get_touchstone_data(self, setup_name=None, sweep_name=None, variations=None):
        """
        Return a Touchstone data plot.

        Parameters
        ----------
        setup_name : list
            Name of the setup.
        sweep_name : str, optional
            Name of the sweep. The default value is ``None``.
        variations : dict, optional
            Dictionary of variation names. The default value is ``None``.

        Returns
        -------
        :class:`pyaedt.generic.touchstone_parser.TouchstoneData`
           Class containing all requested data.

        References
        ----------

        >>> oModule.GetSolutionDataPerVariation
        """
        from pyaedt.generic.touchstone_parser import TouchstoneData

        if not setup_name:
            setup_name = self._app.setups[0].name

        if self._app.design_type != "Circuit Design" and not sweep_name:
            for setup in self._app.setups:
                if setup.name == setup_name:
                    sweep_name = setup.sweeps[0].name
            solution = "{} : {}".format(setup_name, sweep_name)
        else:
            solution = setup_name
        s_parameters = []
        expression = self._app.get_traces_for_plot(category="S")
        sol_data = self._app.post.get_solution_data(expression, solution, variations=variations)
        for i in range(sol_data.number_of_variations):
            sol_data.set_active_variation(i)
            s_parameters.append(TouchstoneData(solution_data=sol_data))
        return s_parameters

    @pyaedt_function_handler()
    def export_touchstone(
        self,
        setup_name=None,
        sweep_name=None,
        file_name=None,
        variations=None,
        variations_value=None,
        renormalization=False,
        impedance=None,
        gamma_impedance_comments=False,
    ):
        """Export a Touchstone file.

        Parameters
        ----------
        setup_name : str, optional
            Name of the setup that has been solved.
        sweep_name : str, optional
            Name of the sweep that has been solved.
        file_name : str, optional
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
        return self._app._export_touchstone(
            setup_name=setup_name,
            sweep_name=sweep_name,
            file_name=file_name,
            variations=variations,
            variations_value=variations_value,
            renormalization=renormalization,
            impedance=impedance,
            comments=gamma_impedance_comments,
        )


def phase_expression(m, n, theta_name="theta_scan", phi_name="phi_scan"):
    """Return an expression for the source phase angle in a rectangular antenna array.

    Parameters
    ----------
    m : int, required
        Index of the rectangular antenna array element in the x direction.
    n : int, required
        Index of the rectangular antenna array element in the y direction.
    theta_name : str, optional
        Postprocessing variable name in HFSS to use for the
        theta component of the phase angle expression. The default is ``"theta_scan"``.
    phi_name : str, optional
        Postprocessing variable name in HFSS to use to generate
        the phi component of the phase angle expression. The default is ``"phi_scan"``

    Returns
    -------
    str
        Phase angle expression for the (m,n) source of
        the (m,n) antenna array element.

    """
    # px is the term for the phase variation in the x direction.
    # py is the term for the phase variation in the y direction.

    if n > 0:
        add_char = " + "
    else:
        add_char = " - "
    if m == 0:
        px = ""
    elif m == -1:
        px = "-pi*sin(theta_scan)*cos(phi_scan)"
    elif m == 1:
        px = "pi*sin(theta_scan)*cos(phi_scan)"
    else:
        px = str(m) + "*pi*sin(theta_scan)*cos(phi_scan)"
    if n == 0:
        py = ""
    elif n == -1 or n == 1:
        py = "pi*sin(theta_scan)*sin(phi_scan)"

    else:
        py = str(abs(n)) + "*pi*sin(theta_scan)*sin(phi_scan)"
    if m == 0:
        if n == 0:
            return "0"
        elif n < 0:
            return "-" + py
        else:
            return py
    elif n == 0:
        if m == 0:
            return "0"
        else:
            return px
    else:
        return px + add_char + py
