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


class FilterSolutions:
    """Provides the FilterSolutions application interface.

    The class has access to ideal filter attributes and calcultaed output parameters.

    Parameters
    ----------
    implementation_type: FilterImplementation, optional
        The technology used to implement the filter.
        The full list of implementations are listed in FilterImplementation enum.
        The default is `LUMPED`.


    Examples
    --------
    Create an instance of FilterSolutions with a band pass elliptic ideal filter.

    >>> import pyaedt
    >>> from pyaedt.filtersolutions_core.attributes import FilterImplementation

    >>> design = pyaedt.FilterSolutions(projectname= "fs1",
    >>> implementation_type= FilterImplementation.LUMPED,
    >>> )
    """

    def __init__(self, implementation_type=FilterImplementation.LUMPED):
        implementation_type = implementation_type
        if implementation_type == FilterImplementation.LUMPED:
            self._init_lumped_design()
        else:
            raise RuntimeError("The " + str(implementation_type) + " is not supported on this release.")

    def _init_lumped_design(self):
        """Initialize the FilterSolutions object to support lumped filter design."""

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
