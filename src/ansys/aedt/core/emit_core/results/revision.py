# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 - 2026 ANSYS, Inc. and/or its affiliates.
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

from __future__ import annotations

import warnings

from ansys.aedt.core.emit_core.emit_constants import EmiCategoryFilter
from ansys.aedt.core.emit_core.emit_constants import InterfererType
from ansys.aedt.core.emit_core.emit_constants import TxRxMode
from ansys.aedt.core.emit_core.nodes import generated
from ansys.aedt.core.emit_core.nodes.emit_node import EmitNode
from ansys.aedt.core.emit_core.nodes.emitter_node import EmitterNode
from ansys.aedt.core.emit_core.nodes.generated import Band
from ansys.aedt.core.emit_core.nodes.generated import BandFolder
from ansys.aedt.core.emit_core.nodes.generated import CouplingsNode
from ansys.aedt.core.emit_core.nodes.generated import EmitSceneNode
from ansys.aedt.core.emit_core.nodes.generated import RadioNode
from ansys.aedt.core.emit_core.nodes.generated import ResultPlotNode
from ansys.aedt.core.emit_core.nodes.generated import Waveform
from ansys.aedt.core.emit_core.results.simulation import Simulation
from ansys.aedt.core.generic.general_methods import deprecate_argument
from ansys.aedt.core.generic.general_methods import pyaedt_function_handler
from ansys.aedt.core.internal.checks import min_aedt_version


class Revision:
    """
    Provides the ``Revision`` object.

    Parameters
    ----------
    parent_results :
        ``Results`` object that this revision is associated with.
    emit_project : Emit
         ``Emit`` object that this revision is associated with.
    name : str, optional
        Name of the revision to load . The default is ``None``, in which
        case the Current revision is used.

    Raises
    ------
    RuntimeError if the name given is not the name of an existing result set and a current result set already exists.

    Examples
    --------
    Create a ``Revision`` instance.

    >>> aedtapp = Emit()
    >>> rev = Revision(results, aedtapp, "Revision 1")
    >>> domain = aedtapp.interaction_domain()
    >>> rev.run(domain)
    """

    def __init__(self, parent_results, emit_project, name: str | None = None) -> None:
        self.emit_project = emit_project
        """EMIT project."""

        self.odesktop = emit_project.odesktop
        """Desktop object."""

        self.parent_results = parent_results
        """Parent Results object."""

        self.aedt_version = int(parent_results.emit_project.aedt_version_id[-3:])
        """AEDT version."""

        if self.aedt_version > 251:
            self._emit_com = self.emit_project._emit_com_module

            if not name:
                # User didn't specify a specific revision name to load- use the Current revision
                self.results_index = 0

                self.name = "Current"
                """Name of the revision."""

                self.emit_project.odesign.SaveEmitProject()

                self.path = self.emit_project.odesign.GetManagedFilesPath()
                """Path to the EMIT result folder for the revision."""
            else:
                kept_result_names = self.emit_project.odesign.GetKeptResultNames()
                if name not in kept_result_names:
                    raise ValueError(f'Revision "{name}" does not exist in the project.')

                self.results_index = self._emit_com.GetKeptResultIndex(name)
                """Index of the result for this revision."""

                self.path = self.emit_project.odesign.GetResultDirectory(name)
                """Path to the EMIT result folder for the revision."""

                self.name = name
                """Name of the revision."""

        else:  # pragma: no cover
            if not name:
                name = self.emit_project.odesign.GetCurrentResult()
                if not name:
                    name = self.emit_project.odesign.AddResult("")
            else:
                if name not in self.emit_project.odesign.GetResultList():
                    name = self.emit_project.odesign.AddResult(name)
            full = self.emit_project.odesign.GetResultDirectory(name)

            self.name = name
            """Name of the revision."""

            self.path = full
            """Full path of the revision."""

            raw_props = self.emit_project.odesign.GetResultProperties(name)

            props = dict(s.split("=", 1) for s in raw_props)

            self.revision_number = int(props["Revision"])
            """Unique revision number from the EMIT design"""

            self.timestamp = props["Timestamp"]
            """Unique timestamp for the revision"""

        self.revision_loaded = False
        """``True`` if the revision is loaded and ``False`` if it is not."""

        self._load_revision()

    @pyaedt_function_handler()
    def _load_revision(self) -> None:
        """
        Load this revision.

        Examples
        --------
        >>> aedtapp.results.revision.load_revision()
        """
        if self.revision_loaded:
            return
        self.parent_results._unload_revisions()
        self.emit_project._emit_api.load_project(self.path)
        self.revision_loaded = True

    @staticmethod
    def result_mode_error() -> str:
        """
        Print the function mode error message.

        Returns
        -------
        err_msg : str
            Error/warning message that the specified revision is not accessible.
        """
        err_msg = "This function is inaccessible when the revision is not loaded."
        print(err_msg)
        return err_msg

    @pyaedt_function_handler()
    def get_simulation(self) -> Simulation:
        """
        Get the simulation object for this revision.

        The Simulation object contains methods for running interference analyses,
        getting interactions, and managing simulation parameters.

        Returns
        -------
        simulation : Simulation
            Simulation object for this revision.

        Examples
        --------
        >>> rev = aedtapp.results.current_revision
        >>> sim = rev.get_simulation()
        >>> domain = aedtapp.interaction_domain()
        >>> sim.run(domain)
        """
        return Simulation(self)

    @pyaedt_function_handler()
    def get_interaction(self, domain):
        """
        Create a new interaction for a domain.

        .. deprecated::
            Use :meth:`get_simulation().get_interaction()` instead.

        Parameters
        ----------
        domain : class:`Emit.InteractionDomain`
            ``InteractionDomain`` object for constraining the analysis parameters.

        Returns
        -------
        interaction:class: `Interaction`
            Interaction object.

        Examples
        --------
        >>> domain = aedtapp.results.interaction_domain()
        >>> rev.get_interaction(domain)

        """
        warnings.warn(
            "This function is deprecated. Use `get_simulation().get_interaction()` instead.", DeprecationWarning
        )
        return self.get_simulation().get_interaction(domain)

    @pyaedt_function_handler()
    def run(self, domain: object) -> object:
        """
        Load the revision and then analyze along the given domain.

        .. deprecated::
            Use :meth:`get_simulation().run()` instead.

        Parameters
        ----------
        domain :
            ``InteractionDomain`` object for constraining the analysis parameters.

        Returns
        -------
        interaction:class: `Interaction`
            Interaction object.

        Examples
        --------
        >>> domain = aedtapp.results.interaction_domain()
        >>> rev.run(domain)

        """
        warnings.warn("This function is deprecated. Use `get_simulation().run()` instead.", DeprecationWarning)
        return self.get_simulation().run(domain)

    @pyaedt_function_handler()
    def is_domain_valid(self, domain: object) -> bool:
        """
        Return ``True`` if the given domain is valid for the current revision.

        .. deprecated::
            Use :meth:`get_simulation().is_domain_valid()` instead.

        Parameters
        ----------
        domain :
            ``InteractionDomain`` object for constraining the analysis parameters.

        Examples
        --------
        >>> domain = aedtapp.interaction_domain()
        >>> aedtapp.results.current_revision.is_domain_valid(domain)
        True
        """
        warnings.warn(
            "This function is deprecated. Use `get_simulation().is_domain_valid()` instead.", DeprecationWarning
        )
        return self.get_simulation().is_domain_valid(domain)

    @pyaedt_function_handler()
    def get_instance_count(self, domain: object) -> int:
        """
        Return the number of instances in the domain for the current revision.

        .. deprecated::
            Use :meth:`get_simulation().get_instance_count()` instead.

        Parameters
        ----------
        domain :
            ``InteractionDomain`` object for constraining the analysis parameters.

        Returns
        -------
        count : int
            Number of instances in the domain for the current revision.

        Examples
        --------
        >>> domain = aedtapp.interaction_domain()
        >>> num_instances = aedtapp.results.current_revision.get_instance_count(domain)
        """
        warnings.warn(
            "This function is deprecated. Use `get_simulation().get_instance_count()` instead.", DeprecationWarning
        )
        return self.get_simulation().get_instance_count(domain)

    @pyaedt_function_handler()
    def get_all_band_nodes(
        self, radio: RadioNode, tx_rx_mode: TxRxMode = None, enabled_only: bool = False
    ) -> list[Band]:
        """
        Returns all the Bands within a Radio

        Parameters
        ----------
        radio: RadioNode
            The radio to iterate through.

        tx_rx_mode : :class:`emit_constants.TxRxMode`, optional
            Specifies whether to get ``tx`` or ``rx`` band names. The default
            is ``None``, in which case the names of all enabled bands are returned.

        enabled_only : bool
            If True, only returns Band nodes that are enabled, otherwise
            it returns all Band nodes.

        Returns
        -------
        bands: list[Band]
            List of all Band (nodes) in a radio.
        """
        radio_children = radio.children
        bands = []
        for radio_child in radio_children:
            if isinstance(radio_child, Band):
                if enabled_only and not radio_child.enabled:
                    # Skip disabled Bands if caller doesn't want all Bands
                    continue
                if tx_rx_mode == TxRxMode.RX:
                    if "true" in radio_child._get_property("RxEnabled", True):
                        bands.append(radio_child)
                elif tx_rx_mode == TxRxMode.TX:
                    if "true" in radio_child._get_property("TxEnabled", True):
                        bands.append(radio_child)
                else:
                    bands.append(radio_child)
            elif isinstance(radio_child, Waveform):
                if enabled_only and not radio_child.enabled:
                    # Skip disabled Bands if caller doesn't want all Bands
                    continue
                if tx_rx_mode == TxRxMode.RX:
                    # Skip Waveforms for Rx mode
                    continue
                elif "true" in radio_child._get_property("TxEnabled", True):
                    bands.append(radio_child)
            elif isinstance(radio_child, BandFolder):
                folder_children = radio_child.children
                for folder_child in folder_children:
                    if enabled_only and not folder_child.enabled:
                        # Skip disabled Bands if caller doesn't want all Bands
                        continue
                    if tx_rx_mode == TxRxMode.RX:
                        if "true" in folder_child._get_property("RxEnabled", True):
                            bands.append(folder_child)
                    elif tx_rx_mode == TxRxMode.TX:
                        if "true" in folder_child._get_property("TxEnabled", True):
                            bands.append(folder_child)
                    else:
                        bands.append(folder_child)
        return bands

    def get_band_node(self, band_name: str) -> Band:
        """
        Get a Band node by name.

        Parameters
        ----------
        band_name: str
            The name of the Band node to get.

        Returns
        -------
        band: Band
            The Band node with the specified name, or None if no such node exists.
        """
        radios = self.get_all_radio_nodes()
        for radio in radios:
            radio: RadioNode
            bands = self.get_all_band_nodes(radio=radio, enabled_only=False)
            for band in bands:
                if band.name == band_name:
                    return band
        return None

    @pyaedt_function_handler()
    def _is_receiver(self, radio: RadioNode):
        """
        Check if a given radio is a receiver.

        Parameters
        ----------
        radio: RadioNode
            The radio to check.

        Returns
        -------
        is_rx: bool
            True if the Radio can receive, False otherwise.
        """
        bands = self.get_all_band_nodes(radio=radio, tx_rx_mode=TxRxMode.RX, enabled_only=True)
        return len(bands) > 0

    @pyaedt_function_handler()
    def _is_transmitter(self, radio: RadioNode):
        """
        Check if a given radio is a transmitter.

        Parameters
        ----------
        radio: RadioNode
            The radio to check.

        Returns
        -------
        is_tx: bool
            True if the Radio can transmit, False otherwise.
        """
        bands = self.get_all_band_nodes(radio=radio, tx_rx_mode=TxRxMode.TX, enabled_only=True)
        return len(bands) > 0

    @pyaedt_function_handler()
    def get_receiver_names(self) -> list[str]:
        """
        Get a list of all receivers in the project.

        Parameters
        ----------
        None

        Returns
        -------
        radios:class:`list of str`
            List of receiver names.

        Examples
        --------
        >>> rxs = aedtapp.results.current_revision.get_reciver_names()
        """
        receivers = []
        if self.revision_loaded:
            radios = self.get_all_radio_nodes()
            for radio in radios:
                radio: RadioNode
                if self._is_receiver(radio):
                    receivers.append(radio.name)
        else:
            err_msg = self.result_mode_error()
            warnings.warn(err_msg)
            return None
        if len(receivers) == 0:
            warnings.warn("No valid receivers in the project.")
        return receivers

    @pyaedt_function_handler()
    def get_interferer_names(self, interferer_type: object = None) -> list[str]:
        """
        Get a list of all interfering transmitters/emitters in the project.

        Parameters
        ----------
        interferer_type : interferer_type object, optional
            Type of interferer to return. The default is ``None``, in which
            case both transmitters and emitters are returned. Options are:
                - transmitters
                - emitters
                - transmitters_and_emitters

        Returns
        -------
        radios:class:`list of str`
            List of interfering systems' names.

        Examples
        --------
        >>> transmitters = aedtapp.results.current_revision.get_interferer_names(InterfererType.TRANSMITTERS)
        >>> emitters = aedtapp.results.current_revision.get_interferer_names(InterfererType.EMITTERS)
        >>> both = aedtapp.results.current_revision.get_interferer_names(InterfererType.TRANSMITTERS_AND_EMITTERS)
        """
        transmitters = []
        if interferer_type is None:
            interferer_type = InterfererType.TRANSMITTERS_AND_EMITTERS
        if self.revision_loaded:
            radios = []
            if interferer_type == InterfererType.TRANSMITTERS:
                radios = self.get_all_radio_nodes(include_emitters=False)
            elif interferer_type == InterfererType.EMITTERS:
                radios = self.get_all_emitter_radios()
            else:
                radios = self.get_all_radio_nodes(include_emitters=True)
            for radio in radios:
                radio: RadioNode
                if self._is_transmitter(radio):
                    transmitters.append(radio.name)
        else:
            err_msg = self.result_mode_error()
            warnings.warn(err_msg)
            return None
        if len(transmitters) == 0:
            warnings.warn("No valid radios or emitters in the project.")
            return None
        return transmitters

    @pyaedt_function_handler()
    @deprecate_argument(
        arg_name="radio_name",
        message=(
            "The ''radio_name'' argument will be removed in future versions. Use the ''radio_node'' argument instead."
        ),
    )
    def get_band_names(
        self, radio_node: RadioNode = None, radio_name: str = "", tx_rx_mode: TxRxMode = None
    ) -> list[str]:
        """Get a list of all enabled ``tx`` or ``rx`` bands (or waveforms) in a given radio/emitter.

        Parameters
        ----------
        radio_name : str
            The name of the radio/emitter
        radio_node : RadioNode
            The radio/emitter.
        tx_rx_mode : :class:`emit_constants.TxRxMode`, optional
            Specifies whether to get ``tx`` or ``rx`` band names. The default
            is ``None``, in which case the names of all enabled bands are returned.

        Returns
        -------
        bands: list[str]
            List of ``tx`` or ``rx`` band/waveform names.

        Examples
        --------
        >>> bands = aedtapp.results.current_revision.get_band_names("Bluetooth", TxRxMode.RX)
        >>> waveforms = aedtapp.results.current_revision.get_band_names("USB_3.x", TxRxMode.TX)
        """
        band_names = []
        if self.revision_loaded:
            if radio_node is None:
                if radio_name == "":
                    raise ValueError("A radio_node or radio_name must be specified.")
                radio_node = self.get_component_node(radio_name)
            bands = self.get_all_band_nodes(radio=radio_node, enabled_only=True, tx_rx_mode=tx_rx_mode)
            for band in bands:
                band_names.append(band.name)
        else:
            self.result_mode_error()
            err_msg = self.result_mode_error()
            warnings.warn(err_msg)
            return None
        if len(band_names) == 0:
            warnings.warn("No valid radios or emitters in the project.")
            return None
        return band_names

    @pyaedt_function_handler()
    def get_active_frequencies(
        self, radio_name: str, band_name: str, tx_rx_mode: TxRxMode, units: str = ""
    ) -> list[float]:
        """
        Get a list of active frequencies for a ``tx`` or ``rx`` band in a radio/emitter.

        Parameters
        ----------
        radio_name : str
            Name of the radio/emitter.
        band_name : str
           Name of the band.
        tx_rx_mode : :class:`emit_constants.TxRxMode`
            Specifies whether to get ``tx`` or ``rx`` radio frequencies.
        units : str, optional
            Units for the frequencies. The default is ``None`` which uses the units
            specified globally for the project.

        Returns
        -------
        freqs : List of float
            List of ``tx`` or ``rx`` radio/emitter frequencies.

        Examples
        --------
        >>> freqs = aedtapp.results.current_revision.get_active_frequencies(
                'Bluetooth', 'Rx - Base Data Rate', TxRxMode.RX)
        """
        warnings.warn(
            "The ``revision.get_active_frequencies`` method will be removed in future versions.\n"
            "Use the ``band_node.get_active_frequencies`` method instead. For example: \n\n"
            ">>> tx_band = [band for band in radio_node.children if band._node_type == 'Band'][0]\n"
            '>>> freqs = tx_band.get_active_frequencies(is_rx=False, units="Hz")\n\n',
            DeprecationWarning,
        )

        if tx_rx_mode is None or tx_rx_mode == TxRxMode.BOTH:
            raise ValueError("The mode type must be specified as either Tx or Rx.")
        if self.revision_loaded:
            freqs = self.emit_project._emit_api.get_active_frequencies(radio_name, band_name, tx_rx_mode, units)
        else:
            freqs = None
            err_msg = self.result_mode_error()
            warnings.warn(err_msg)
            return freqs
        return freqs

    @property
    def notes(self) -> str:
        """
        Add notes to the revision.

        Examples
        --------
        >>> aedtapp.results.current_revision.notes = "Added a filter to the WiFi Radio."
        >>> aedtapp.results.current_revision.notes
        'Added a filter to the WiFi Radio.'
        """
        design = self.emit_project.odesign
        return design.GetResultNotes(self.name)

    @notes.setter
    def notes(self, notes: str) -> None:
        self.emit_project.odesign.SetResultNotes(self.name, notes)
        self.emit_project.save_project()

    @property
    def n_to_1_limit(self) -> int:
        """
        Maximum number of interference combinations to run per receiver for N to 1.

        .. deprecated::
            Use :attr:`get_simulation().n_to_1_limit` instead.

        - A value of ``0`` disables N to 1 entirely.
        - A value of  ``-1`` allows unlimited N to 1. (N is set to the maximum.)

        Examples
        --------
        >>> aedtapp.results.current_revision.n_to_1_limit = 2**20
        >>> aedtapp.results.current_revision.n_to_1_limit
        1048576
        """
        warnings.warn("This property is deprecated. Use `get_simulation().n_to_1_limit` instead.", DeprecationWarning)
        return self.get_simulation().n_to_1_limit

    @n_to_1_limit.setter
    def n_to_1_limit(self, max_instances):
        self.get_simulation().n_to_1_limit = max_instances

    @pyaedt_function_handler()
    def interference_type_classification(
        self,
        domain: object,
        interferer_type: InterfererType = InterfererType.TRANSMITTERS,
        use_filter: bool = False,
        filter_list: list[str] = None,
    ) -> tuple[list, list]:  # pragma: no cover
        """Classify interference type as according to inband/inband,
        out of band/in band, inband/out of band, and out of band/out of band.

        .. deprecated::
            Use :meth:`get_simulation().interference_type_classification()` instead.

        Parameters
        ----------
            domain :
                ``InteractionDomain`` object for constraining the analysis parameters.
            interferer_type : TxRxMode, optional
                Specifies whether to analyze all interferers, radios only, or emitters only.
            use_filter : bool, optional
                Whether filtering is being used. The default is ``False``.
            filter_list : list[str], optional
                List of filter values selected by the user via the GUI if filtering is in use.

        Returns
        -------
            power_matrix : list
                List of worst case interference power at Rx.
            all_colors : list
                Color classification of interference types.

        Examples
        --------
        >>> interference_results = rev.interference_type_classification(domain)
        """
        warnings.warn(
            "This function is deprecated. Use `get_simulation().interference_type_classification()` instead.",
            DeprecationWarning,
        )
        return self.get_simulation().interference_type_classification(domain, interferer_type, use_filter, filter_list)

    @pyaedt_function_handler()
    def protection_level_classification(
        self,
        domain: object,
        interferer_type: InterfererType = InterfererType.TRANSMITTERS,
        global_protection_level: bool = True,
        global_levels: list = None,
        protection_levels: dict = None,
        use_filter: bool = False,
        filter_list: list[str] = None,
    ) -> tuple[list, list]:  # pragma: no cover
        """
        Classify worst-case power at each Rx radio according to interference type.

        .. deprecated::
            Use :meth:`get_simulation().protection_level_classification()` instead.

        Options for interference type are `inband/inband, out of band/in band,
        inband/out of band, and out of band/out of band.

        Parameters
        ----------
            domain :
                ``InteractionDomain`` object for constraining the analysis parameters.
            interferer_type : TxRxMode, optional
                Specifies whether to analyze all interferers, radios only, or emitters only.
            global_protection_level : bool, optional
                Whether to use the same protection levels for all radios. The default is ``True``.
            global_levels : list, optional
                List of protection levels to use for all radios.
            protection_levels : dict, optional
                Dictionary of protection levels for each Rx radio.
            use_filter : bool, optional
                Whether to use filtering. The default is ``False``.
            filter_list : list, optional
                List of filter values selected by the user via the GUI if filtering is in use.

        Returns
        -------
            power_matrix : list
                Worst case interference according to power at each Rx radio.
            all_colors : list
                Color classification of protection level.

        Examples
        --------
        >>> protection_results = rev.protection_level_classification(domain)
        """
        warnings.warn(
            "This function is deprecated. Use `get_simulation().protection_level_classification()` instead.",
            DeprecationWarning,
        )
        return self.get_simulation().protection_level_classification(
            domain, interferer_type, global_protection_level, global_levels, protection_levels, use_filter, filter_list
        )

    def get_emi_category_filter_enabled(self, category: EmiCategoryFilter) -> bool:
        """Get whether the EMI category filter is enabled.

        .. deprecated::
            Use :meth:`get_simulation().get_emi_category_filter_enabled()` instead.

        Parameters
        ----------
        category : :class:`EmiCategoryFilter`
            EMI category filter.

        Returns
        -------
        bool
            ``True`` when the EMI category filter is enabled, ``False`` otherwise.
        """
        warnings.warn(
            "This function is deprecated. Use `get_simulation().get_emi_category_filter_enabled()` instead.",
            DeprecationWarning,
        )
        return self.get_simulation().get_emi_category_filter_enabled(category)

    def set_emi_category_filter_enabled(self, category: EmiCategoryFilter, enabled: bool):
        """Set whether the EMI category filter is enabled.

        .. deprecated::
            Use :meth:`get_simulation().set_emi_category_filter_enabled()` instead.

        Parameters
        ----------
        category : :class:`EmiCategoryFilter`
            EMI category filter.
        enabled : bool
            Whether to enable the EMI category filter.
        """
        self.get_simulation().set_emi_category_filter_enabled(category, enabled)

    @pyaedt_function_handler
    def get_license_session(self) -> object:
        """Get a license session.

        .. deprecated::
            Use :meth:`get_simulation().get_license_session()` instead.

        A license session can be started with checkout(), and ended with check in().
        The `with` keyword can also be used, where checkout() is called on enter, and check in() is called on exit.

        Avoids having to wait for license check in and checkout when doing many runs.

        Examples
        --------
        with revision.get_license_session():
            domain = aedtapp.interaction_domain()
            revision.run(domain)
        """
        warnings.warn(
            "This function is deprecated. Use `get_simulation().get_license_session()` instead.", DeprecationWarning
        )
        return self.get_simulation().get_license_session()

    @pyaedt_function_handler
    @min_aedt_version("2025.2")
    def _get_all_component_names(self) -> list[str]:
        """Gets all component names from this revision.

        Returns
        -------
        component_names: list
            List of component names.

        Examples
        --------
        >>> components = revision._get_all_component_names()
        """
        component_names = self._emit_com.GetComponentNames(self.results_index, "")
        return component_names

    @pyaedt_function_handler
    @min_aedt_version("2025.2")
    def _get_all_top_level_node_ids(self) -> list[int]:
        """Gets all top level node ids from this revision.

        Returns
        -------
        node_ids: list
            List of top level node ids.

        Examples
        --------
        >>> top_level_node_ids = revision._get_all_top_level_node_ids()
        """
        top_level_node_names = [
            # 'Windows-*-Configuration Diagram',
            "Windows-*-Result Plot",
            # 'Windows-*-EMI Margin Plot',
            "Windows-*-Result Categorization",
            # 'Windows-*-Plot',
            # 'Windows-*-Coupling Plot',
            "Windows-*-Project Tree",
            "Windows-*-Properties",
            # 'Windows-*-JETS Search',
            "Windows-*-Antenna Coupling Matrix",
            "Windows-*-Scenario Matrix",
            "Windows-*-Scenario Details",
            "Windows-*-Interaction Diagram",
            # 'Windows-*-Link Analysis',
            # 'Windows-*-Event Log',
            # 'Windows-*-Library Tree',
            # 'Windows-*-Python Script Window',
            "RF Systems",
            "Couplings",
            # 'Analysis',
            "Simulation",
            "Scene",
        ]
        top_level_node_ids = []
        for name in top_level_node_names:
            top_level_node_id = self._emit_com.GetTopLevelNodeID(self.results_index, name)
            top_level_node_ids.append(top_level_node_id)
        return top_level_node_ids

    @pyaedt_function_handler
    @min_aedt_version("2025.2")
    def get_all_top_level_nodes(self) -> list[EmitNode]:
        """Gets all top level nodes from this revision.

        Returns
        -------
        nodes: list
            List of top level nodes.

        Examples
        --------
        >>> top_level_nodes = revision.get_all_top_level_nodes()
        """
        top_level_node_ids = self._get_all_top_level_node_ids()
        top_level_nodes = [self._get_node(node_id) for node_id in top_level_node_ids]
        return top_level_nodes

    @pyaedt_function_handler
    @min_aedt_version("2025.2")
    def get_all_component_nodes(self) -> list[EmitNode]:
        """Gets all component nodes from this revision.

        Returns
        -------
        component_nodes: list
            List of component nodes.

        Examples
        --------
        >>> nodes = revision.get_all_component_nodes()
        """
        component_names = self._get_all_component_names()
        component_node_ids = [self._emit_com.GetComponentNodeID(self.results_index, name) for name in component_names]
        component_nodes = [self._get_node(node_id) for node_id in component_node_ids]
        return component_nodes

    @pyaedt_function_handler
    @min_aedt_version("2025.2")
    def get_all_radio_nodes(self, tx_rx_mode: TxRxMode = None, include_emitters: bool = False) -> list[RadioNode]:
        """Gets all Radio nodes from this revision.

        Parameters
        ----------
        tx_rx_mode: TxRxMode
            Specifies the type (Tx, Rx, or Both) of Radios to include.

        include_emitters: bool
            Includes Emitters if True.

        Returns
        -------
        radio_nodes: list
            List of radio nodes.

        Examples
        --------
        >>> radios = revision.get_all_radio_nodes()
        """
        comp_nodes: EmitNode = self.get_all_component_nodes()
        radio_nodes = []
        for comp in comp_nodes:
            if include_emitters and isinstance(comp, EmitterNode):
                comp: EmitterNode
                radio_nodes.append(comp.get_radio())
            elif isinstance(comp, RadioNode):
                if tx_rx_mode == TxRxMode.TX and self._is_transmitter(comp):
                    radio_nodes.append(comp)
                elif tx_rx_mode == TxRxMode.RX and self._is_receiver(comp):
                    radio_nodes.append(comp)
                elif tx_rx_mode == TxRxMode.BOTH or tx_rx_mode is None:
                    radio_nodes.append(comp)

        if len(radio_nodes) == 0:
            warnings.warn("No valid radios in the project.")
            return None
        return radio_nodes

    @pyaedt_function_handler
    @min_aedt_version("2025.2")
    def get_radio_node(self, radio_name: str) -> RadioNode:
        """Gets a Radio node by name.

        Parameters
        ----------
        radio_name: str
            The name of the Radio node to get.

        Returns
        -------
        radio: RadioNode
            The Radio node with the specified name, or None if no such node exists.
        """
        comp_nodes: EmitNode = self.get_all_component_nodes()
        for comp in comp_nodes:
            if isinstance(comp, RadioNode) and comp.name == radio_name:
                return comp
            elif isinstance(comp, EmitterNode):
                comp: EmitterNode
                radio = comp.get_radio()
                if radio.name == radio_name:
                    return radio
        return None

    @pyaedt_function_handler
    @min_aedt_version("2025.2")
    def get_all_emitter_radios(self) -> list[RadioNode]:
        """Gets all Emitter Radio nodes from this revision.

        Returns
        -------
        radio_nodes: list
            List of radio nodes belonging to Emitters.

        Examples
        --------
        >>> radios = revision.get_all_radio_nodes()
        """
        comp_nodes: EmitNode = self.get_all_component_nodes()
        radio_nodes = []
        for comp in comp_nodes:
            if isinstance(comp, EmitterNode):
                comp: EmitterNode
                radio_nodes.append(comp.get_radio())
        if len(radio_nodes) == 0:
            warnings.warn("No valid emitters in the project.")
            return None
        return radio_nodes

    @pyaedt_function_handler
    @min_aedt_version("2025.2")
    def get_component_node(self, component_name: str) -> EmitNode:
        """Gets the component node.

        Parameters
        ----------
        component_name: str
            Name of the component.

        Returns
        -------
        component_node: EmitNode
            Component node.

        Examples
        --------
        >>> node = revision.get_component_node("wifi radio")
        """
        comp_id = self._emit_com.GetComponentNodeID(self.results_index, component_name)
        if comp_id > 0:
            return self._get_node(comp_id)
        return None

    @pyaedt_function_handler
    @min_aedt_version("2025.2")
    def _get_all_node_ids(self) -> list[int]:
        """Gets all node ids from this revision.

        Returns
        -------
        node_ids: list
            List of node ids.

        Examples
        --------
        >>> node_ids = revision._get_all_node_ids()
        """
        node_ids = []
        node_ids_to_search = []

        top_level_node_ids = self._get_all_top_level_node_ids()
        node_ids_to_search.extend(top_level_node_ids)

        component_names = self._get_all_component_names()
        component_node_ids = [self._emit_com.GetComponentNodeID(self.results_index, name) for name in component_names]
        node_ids_to_search.extend(component_node_ids)

        while len(node_ids_to_search) > 0:
            node_id_to_search = node_ids_to_search.pop()
            if node_id_to_search not in node_ids:
                node_ids.append(node_id_to_search)

                child_names = self._emit_com.GetChildNodeNames(self.results_index, node_id_to_search)
                child_ids = [
                    self._emit_com.GetChildNodeID(self.results_index, node_id_to_search, name) for name in child_names
                ]
                if len(child_ids) > 0:
                    node_ids_to_search.extend(child_ids)

        return node_ids

    @pyaedt_function_handler
    @min_aedt_version("2025.2")
    def _get_node(self, node_id: int) -> EmitNode:
        """Gets a node for this revision with the given id.

        Parameters
        ----------
        node_id: int
            node_id of node to construct.

        Returns
        -------
        node: EmitNode
            The node.

        Examples
        --------
        >>> node = revision._get_node(node_id)
        """
        props = self._emit_com.GetEmitNodeProperties(self.results_index, node_id, True)
        props = EmitNode.props_to_dict(props)
        node_type = props["Type"]

        node_type = node_type.replace(" ", "_")

        prefix = "" if self.results_index == 0 else "ReadOnly"

        # Remove the following statement to construct ReadOnly nodes
        prefix = ""

        node = None
        try:
            type_class = EmitNode
            if node_type == "RadioNode" and props["IsEmitter"] == "true":
                type_class = EmitterNode
                # TODO: enable when we add ReadOnlyNodes
                # if prefix == "":
                # type_class = EmitterNode
                # else:
                #    type_class = ReadOnlyEmitterNode
            elif node_type == "Band" and props["IsEmitterBand"] == "true":
                type_class = getattr(generated, f"{prefix}Waveform")
            elif node_type == "TxSpectralProfNode":
                parent_name = props["Parent"]
                parent_name = parent_name.replace("NODE-*-", "")
                node_id = self._emit_com.GetTopLevelNodeID(0, parent_name)
                parent_node = self._get_node(node_id)
                if isinstance(parent_node, Waveform):
                    type_class = getattr(generated, f"{prefix}TxSpectralProfEmitterNode")
            else:
                type_class = getattr(generated, f"{prefix}{node_type}")
            node = type_class(self.emit_project, self.results_index, node_id)
        except AttributeError:
            node = EmitNode(self.emit_project, self.results_index, node_id)
        return node

    @pyaedt_function_handler
    @min_aedt_version("2025.2")
    def get_all_nodes(self) -> list[EmitNode]:
        """Gets all nodes for this revision.

        Returns
        -------
        nodes: list
            List of all nodes from this revision.

        Examples
        --------
        >>> nodes = revision.get_all_nodes()
        """
        ids = self._get_all_node_ids()
        nodes = [self._get_node(id) for id in ids]
        return nodes

    # Methods to get specific top level nodes
    @pyaedt_function_handler
    @min_aedt_version("2025.2")
    def get_scene_node(self) -> EmitSceneNode:
        """Gets the Scene node for this revision.

        Returns
        -------
        node: EmitSceneNode
            The Scene node for this revision.

        Examples
        --------
        >>> scene_node = revision.get_scene_node()
        """
        scene_node_id = self._emit_com.GetTopLevelNodeID(self.results_index, "Scene")
        scene_node = self._get_node(scene_node_id)
        return scene_node

    @pyaedt_function_handler
    @min_aedt_version("2025.2")
    def get_coupling_data_node(self) -> CouplingsNode:
        """Gets the Coupling Data node for this revision.

        Returns
        -------
        node: CouplingsNode
            The Coupling Data node for this revision.

        Examples
        --------
        >>> coupling_data_node = revision.get_coupling_data_node()
        """
        coupling_data_node_id = self._emit_com.GetTopLevelNodeID(self.results_index, "Couplings")
        coupling_data_node = self._get_node(coupling_data_node_id)
        return coupling_data_node

    @pyaedt_function_handler
    @min_aedt_version("2025.2")
    def get_simulation_node(self) -> EmitNode:
        """Gets the Simulation node for this revision.

        Returns
        -------
        node: EmitNode
            The Simulation node for this revision.

        Examples
        --------
        >>> simulation_node = revision.get_simulation_node()
        """
        simulation_node_id = self._emit_com.GetTopLevelNodeID(self.results_index, "Simulation")
        simulation_node = self._get_node(simulation_node_id)
        return simulation_node

    @pyaedt_function_handler
    @min_aedt_version("2025.2")
    def get_preferences_node(self) -> EmitNode:
        """Gets the Preferences node for this revision.

        Returns
        -------
        node: EmitNode
            The Preferences node for this revision.

        Examples
        --------
        >>> preferences_node = revision.get_preferences_node()
        """
        preferences_node_id = self._emit_com.GetTopLevelNodeID(self.results_index, "Preferences")
        preferences_node = self._get_node(preferences_node_id)
        return preferences_node

    @pyaedt_function_handler
    @min_aedt_version("2025.2")
    def get_result_plot_node(self) -> ResultPlotNode:
        """Gets the Result Plot node for this revision.

        Returns
        -------
        node: ResultPlotNode
            The Result Plot node for this revision.

        Examples
        --------
        >>> result_plot_node = revision.get_result_plot_node()
        """
        result_plot_node_id = self._emit_com.GetTopLevelNodeID(self.results_index, "Windows-*-Result Plot")
        result_plot_node = self._get_node(result_plot_node_id)
        return result_plot_node

    @pyaedt_function_handler
    @min_aedt_version("2025.2")
    def get_result_categorization_node(self) -> EmitNode:
        """Gets the Result Categorization node for this revision.

        Returns
        -------
        node: EmitNode
            The Result Categorization node for this revision.

        Examples
        --------
        >>> result_categorization_node = revision.get_result_categorization_node()
        """
        result_categorization_node_id = self._emit_com.GetTopLevelNodeID(
            self.results_index, "Windows-*-Result Categorization"
        )
        result_categorization_node = self._get_node(result_categorization_node_id)
        return result_categorization_node

    @pyaedt_function_handler
    @min_aedt_version("2025.2")
    def _get_disconnected_radios(self) -> list[str]:
        """Gets a list of disconnected radios for this revision.

        Returns
        -------
        list: str
            All radios in the revision that are not connected to an antenna. A radio
            is only considered "disconnected" if any of the components' ports in its
            chain are left open.
        """
        rf_systems_id = self._emit_com.GetTopLevelNodeID(self.results_index, "RF Systems")
        sys_names = self._emit_com.GetChildNodeNames(self.results_index, rf_systems_id)
        if "Disconnected Components" in sys_names:
            dis_comp_id = self._emit_com.GetChildNodeID(self.results_index, rf_systems_id, "Disconnected Components")
            radios_id = self._emit_com.GetChildNodeID(self.results_index, dis_comp_id, "Radios")
            return self._emit_com.GetChildNodeNames(0, radios_id)
        return []
