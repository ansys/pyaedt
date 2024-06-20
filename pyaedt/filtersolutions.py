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

from pyaedt.filtersolutions_core.attributes import Attributes
from pyaedt.filtersolutions_core.attributes import FilterImplementation
from pyaedt.filtersolutions_core.graph_setup import GraphSetup
from pyaedt.filtersolutions_core.ideal_response import IdealResponse
from pyaedt.filtersolutions_core.lumped_nodes_and_leads import LumpedNodesandLeads
from pyaedt.filtersolutions_core.lumped_parasitics import LumpedParasitics
from pyaedt.filtersolutions_core.lumped_termination_impedance import LumpedTerminationImpedance
from pyaedt.filtersolutions_core.lumped_termination_impedance import TerminationType
from pyaedt.filtersolutions_core.lumped_topology import LumpedTopology
from pyaedt.filtersolutions_core.multiple_bands_table import MultipleBandsTable
from pyaedt.filtersolutions_core.transmission_zeros import TableFormat
from pyaedt.filtersolutions_core.transmission_zeros import TransmissionZeros
from pyaedt.misc.misc import current_version
from pyaedt.misc.misc import installed_versions


class FilterSolutions:
    """Provides the ``FilterSolutions`` application interface.

    The class has access to ideal filter attributes and calculated output parameters.

    Parameters
    ----------
    implementation_type: FilterImplementation, optional
        The technology used to implement the filter.
        The technology used to implement the filter. The default is ``LUMPED``.
        The ``FilterImplementation`` enum provides the list of implementations.


    Examples
    --------
    Create a ``FilterSolutions`` instance with a band pass elliptic ideal filter.

    >>> import pyaedt
    >>> from pyaedt.filtersolutions_core.attributes import FilterImplementation

    >>> design = pyaedt.FilterSolutions(projectname= "fs1",
    >>> implementation_type= FilterImplementation.LUMPED,
    >>> )
    """

    def __init__(self, version=None, implementation_type=FilterImplementation.LUMPED):
        version = version
        implementation_type = implementation_type
        self.version_check(version)

        if implementation_type == FilterImplementation.LUMPED:
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
        self.transmission_zeros_frequency = TransmissionZeros(TableFormat.FREQUENCY)

    def version_check(self, version):
        self_current_version = current_version()
        if current_version == "":
            raise Exception("AEDT is not installed on your system. Install AEDT version 2025 R1 or higher.")
        if version is None:
            version = self_current_version
        if float(version[0:6]) < 2024:
            raise ValueError("PyAEDT supports AEDT version 2025 R1 and later. Recommended version is 2025 R1 or later.")
        if not (version in installed_versions()) and not (version + "CL" in installed_versions()):
            raise ValueError("Specified version {} is not installed on your system".format(version[0:6]))
