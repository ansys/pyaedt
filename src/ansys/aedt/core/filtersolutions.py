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

import warnings

from ansys.aedt.core import Circuit
from ansys.aedt.core import Hfss
from ansys.aedt.core import Hfss3dLayout
from ansys.aedt.core import settings
from ansys.aedt.core.base import PyAedtBase
import ansys.aedt.core.filtersolutions_core
from ansys.aedt.core.filtersolutions_core.attributes import Attributes
from ansys.aedt.core.filtersolutions_core.distributed_geometry import DistributedGeometry
from ansys.aedt.core.filtersolutions_core.distributed_parasitics import DistributedParasitics
from ansys.aedt.core.filtersolutions_core.distributed_radial import DistributedRadial
from ansys.aedt.core.filtersolutions_core.distributed_substrate import DistributedSubstrate
from ansys.aedt.core.filtersolutions_core.distributed_topology import DistributedTopology
from ansys.aedt.core.filtersolutions_core.export_to_aedt import ExportToAedt
from ansys.aedt.core.filtersolutions_core.graph_setup import GraphSetup
from ansys.aedt.core.filtersolutions_core.ideal_response import IdealResponse
from ansys.aedt.core.filtersolutions_core.lumped_nodes_and_leads import LumpedNodesandLeads
from ansys.aedt.core.filtersolutions_core.lumped_parasitics import LumpedParasitics
from ansys.aedt.core.filtersolutions_core.lumped_termination_impedance_table import LumpedTerminationImpedance
from ansys.aedt.core.filtersolutions_core.lumped_termination_impedance_table import TerminationType
from ansys.aedt.core.filtersolutions_core.lumped_topology import LumpedTopology
from ansys.aedt.core.filtersolutions_core.multiple_bands_table import MultipleBandsTable
from ansys.aedt.core.filtersolutions_core.optimization_goals_table import OptimizationGoalsTable
from ansys.aedt.core.filtersolutions_core.transmission_zeros import TableFormat
from ansys.aedt.core.filtersolutions_core.transmission_zeros import TransmissionZeros


class FilterDesignBase(PyAedtBase):
    """Provides the `FilterSolutions` main parameters applicable for all design types."""

    _active_design = None

    def __init__(self, version=None):
        if FilterDesignBase._active_design:
            warnings.warn(
                "FilterSolutions API currently supports only one design at a time. \n"
                "Opening a new design will overwrite the existing design with default values.",
                UserWarning,
            )
            FilterDesignBase._active_design.close()
        FilterDesignBase._active_design = self
        self.version = version if version else settings.aedt_version
        ansys.aedt.core.filtersolutions_core._dll_interface(version)
        self.attributes = Attributes()
        self.ideal_response = IdealResponse()
        self.graph_setup = GraphSetup()
        self.transmission_zeros_ratio = TransmissionZeros(TableFormat.RATIO)
        self.transmission_zeros_bandwidth = TransmissionZeros(TableFormat.BANDWIDTH)
        self.export_to_aedt = ExportToAedt()

    def close(self):
        """Closes the current design and clears the active design."""
        if FilterDesignBase._active_design == self:
            print(f"Closing design: {self}")
            self._cleanup_resources()
            FilterDesignBase._active_design = None

    def _cleanup_resources(self):
        """Perform cleanup operations for the design."""
        print("Cleaning up resources...")
        self.attributes = None
        self.ideal_response = None
        self.graph_setup = None
        self.transmission_zeros_ratio = None
        self.transmission_zeros_bandwidth = None
        self.export_to_aedt = None
        self.source_impedance_table = None
        self.load_impedance_table = None
        self.multiple_bands_table = None
        self.optimization_goals_table = None
        self.topology = None
        self.parasitics = None
        self.leads_and_nodes = None
        self.substrate = None
        self.geometry = None
        self.radial = None

    def _create_design(self, desktop_version, desktop_process_id):
        """Create a new design in AEDT.
        This method is called to create an ``AEDT`` object when the design is exported to ``AEDT``.

        Parameters
        ----------
        desktop_version : str
            Version of AEDT in ``xxxx.x`` format.

        desktop_process_id : int
            Process ID of the AEDT instance.

        Returns
        -------
        :class:``AEDT`` design object
        """
        settings.use_grpc_api = False
        if isinstance(FilterDesignBase._active_design, LumpedDesign):
            return Circuit(version=desktop_version, aedt_process_id=desktop_process_id)
        elif isinstance(FilterDesignBase._active_design, DistributedDesign):
            if getattr(self, "insert_hfss_3dl_design", True):
                return Hfss3dLayout(version=desktop_version, aedt_process_id=desktop_process_id)
            elif getattr(self, "insert_hfss_design", True):
                return Hfss(version=desktop_version, aedt_process_id=desktop_process_id)
            elif getattr(self, "insert_circuit_design", True):
                return Circuit(version=desktop_version, aedt_process_id=desktop_process_id)


class LumpedDesign(FilterDesignBase):
    """Provides the `FilterSolutions` application interface for lumped filter designs.
    This class provides access to lumped filter design parameters.

    Parameters
    ----------
    version : str, optional
        Version of AEDT in ``xxxx.x`` format. The default is ``None``.

    Example
    --------
    Create a ``FilterSolutions.LumpedDesign`` instance with a band-pass elliptic filter.

    >>> import ansys.aedt.core
    >>> import ansys.aedt.core.filtersolutions
    >>> LumpedDesign = ansys.aedt.core.FilterSolutions.LumpedDesign(version="2025.1")
    >>> LumpedDesign.attributes.filter_class = FilterClass.BAND_PASS
    >>> LumpedDesign.attributes.filter_type = FilterType.ELLIPTIC
    """

    def __init__(self, version=None):
        super().__init__(version)
        self._init_lumped_design()

    def _init_lumped_design(self):
        """Initialize the ``FilterSolutions`` object to support a lumped filter design."""
        self.source_impedance_table = LumpedTerminationImpedance(TerminationType.SOURCE)
        self.load_impedance_table = LumpedTerminationImpedance(TerminationType.LOAD)
        self.multiple_bands_table = MultipleBandsTable()
        self.optimization_goals_table = OptimizationGoalsTable()
        self.topology = LumpedTopology()
        self.parasitics = LumpedParasitics()
        self.leads_and_nodes = LumpedNodesandLeads()


class DistributedDesign(FilterDesignBase):
    """Provides the `FilterSolutions` application interface for distributed filter designs.
    This class provides access to distributed filter design parameters.

    Parameters
    ----------
    version : str, optional
        Version of AEDT in ``xxxx.x`` format. The default is ``None``.

    Example
    --------
    Create a ``FilterSolutions.DistributedDesign`` instance with a band-pass interdigital filter.

    >>> import ansys.aedt.core
    >>> import ansys.aedt.core.filtersolutions
    >>> DistributedDesign = ansys.aedt.core.FilterSolutions.DistributedDesign(version="2025.2")
    >>> DistributedDesign.attributes.filter_class = FilterClass.BAND_PASS
    >>> DistributedDesign.topology.topology_type = TopologyType.INTERDIGITAL
    """

    def __init__(self, version=None):
        super().__init__(version)
        self._dll = ansys.aedt.core.filtersolutions_core._dll_interface()._dll
        self._dll_interface = ansys.aedt.core.filtersolutions_core._dll_interface()
        self._check_version()
        self._init_distributed_design()
        self._set_distributed_implementation()

    def _init_distributed_design(self):
        """Initialize the ``FilterSolutions`` object to support a distributed filter design."""
        self.topology = DistributedTopology()
        self.substrate = DistributedSubstrate()
        self.geometry = DistributedGeometry()
        self.radial = DistributedRadial()
        self.parasitics = DistributedParasitics()

    def _set_distributed_implementation(self):
        """Set ``FilterSolutions`` implementation to ``Distributed Design``."""
        filter_implementation_status = self._dll.setFilterImplementation(1)
        self._dll_interface.raise_error(filter_implementation_status)
        first_shunt_status = self._dll.setDistributedFirstElementShunt(True)
        self._dll_interface.raise_error(first_shunt_status)

    def _check_version(self):
        if self._dll_interface._version < "2025.2":
            raise ValueError("FilterSolutions API supports distributed designs in version 2025 R2 and later.")
