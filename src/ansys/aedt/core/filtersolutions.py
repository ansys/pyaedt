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

import ansys.aedt.core
from ansys.aedt.core.filtersolutions_core.attributes import Attributes
from ansys.aedt.core.filtersolutions_core.attributes import FilterImplementation
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


class FilterSolutions:
    """Provides the ``FilterSolutions`` application interface.

    This class has access to ideal filter attributes and calculated output parameters.

    Parameters
    ----------
    version : str, optional
        Version of AEDT in ``xxxx.x`` format. The default is ``None``.
    implementation_type : FilterImplementation, optional
        Technology used to implement the filter. The default is ``LUMPED``.
        The ``FilterImplementation`` enum provides the list of implementations.

    Examples
    --------
    Create a ``FilterSolutions`` instance with a band-pass elliptic ideal filter.

    >>> import ansys.aedt.core
    >>> from ansys.aedt.core.filtersolutions_core.attributes import FilterImplementation

    >>> design = ansys.aedt.core.FilterSolutions(version="2025 R1", projectname= "fs1",
    >>> implementation_type= FilterImplementation.LUMPED,
    >>> )
    """

    def __init__(self, version=None, implementation_type=None):
        self.version = version
        self.implementation_type = implementation_type
        ansys.aedt.core.filtersolutions_core._dll_interface(version)

        if implementation_type == FilterImplementation.LUMPED or implementation_type is None:
            self._init_lumped_design()
        else:
            raise RuntimeError("The " + str(implementation_type) + " is not supported in this release.")

    def _init_lumped_design(self):
        """Initialize the ``FilterSolutions`` object to support a lumped filter design."""

        self.attributes = Attributes()
        self.ideal_response = IdealResponse()
        self.graph_setup = GraphSetup()
        self.topology = LumpedTopology()
        self.parasitics = LumpedParasitics()
        self.leads_and_nodes = LumpedNodesandLeads()
        self.source_impedance_table = LumpedTerminationImpedance(TerminationType.SOURCE)
        self.load_impedance_table = LumpedTerminationImpedance(TerminationType.LOAD)
        self.multiple_bands_table = MultipleBandsTable()
        self.transmission_zeros_ratio = TransmissionZeros(TableFormat.RATIO)
        self.transmission_zeros_bandwidth = TransmissionZeros(TableFormat.BANDWIDTH)
        self.export_to_aedt = ExportToAedt()
        self.optimization_goals_table = OptimizationGoalsTable()
