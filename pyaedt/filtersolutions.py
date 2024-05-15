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

    This class allows you to create an instance of FilterSolutions and
    define the parameters for an ideal filter.
    The class has access to ideal filter attributes and calcultaed output parameters.

    Parameters
    ----------
    filter_name: str, optional
        Name of the filter to select. The default is ``FilterSolutions API Session``.
    filter_class: str, optional
        The class (band definition) of filter. The full list of classes are listed in FilterClass enum.
        The default is `LOW_PASS`.
    filter_type: str, optional
        The type (mathematical formulation) of filter. The full list of types are listed in FilterType enum.
        The default is `BUTTERWORTH`.


    Examples
    --------
    Create an instance of FilterSolutions with a band pass elliptic ideal filter.

    >>> from pyaedt import fspy.ideal_filters
    >>> from fspy.filter_design import FilterClass
    >>> from fspy.filter_design import FilterType

    >>> design = fspy.ideal_filters.IdealDesign(
    >>> filter_name = "filter_design",
    >>> filter_class = FilterClass.BAND_PASS,
    >>> filter_type = FilterType.ELLIPTIC,
    >>> )
    """

    def __init__(self, projectname=None, implementation_type=None):
        projectname = projectname
        implementation_type = implementation_type
        if implementation_type == FilterImplementation.LUMPED:
            self._init_lumped_design()
        else:
            raise RuntimeError("The " + str(implementation_type) + " is not supported on this release.")

    def _init_lumped_design(self):
        """Provides the FilterSolutions application interface.

        This class allows you to create an instance of FilterSolutions and
        define the parameters for a lumped filter. The class has access to ideal
        and lumped filter attributes and calcultaed output parameters.

        Parameters
        ----------
        filter_name: str, optional
            Name of the filter to select. The default is ``FilterSolutions API Session``.
        filter_class: str, optional
            The class (band definition) of filter. The full list of classes are listed in FilterClass enum.
            The default is `LOW_PASS`.
        filter_type: str, optional
            The type (mathematical formulation) of filter. The full list of types are listed in FilterType enum.
            The default is `BUTTERWORTH`.


        Examples
        --------
        Create an instance of FilterSolutions with a band pass elliptic lumped filter.

        >>> from pyaedt import fspy.lumped_filters
        >>> from fspy.filter_design import FilterClass
        >>> from fspy.filter_design import FilterType

        >>> design = fspy.ideal_filters.LumpedDesign(
        >>> filter_name = "filter_design",
        >>> filter_class = FilterClass.BAND_PASS,
        >>> filter_type = FilterType.ELLIPTIC,
        >>> )
        """

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
