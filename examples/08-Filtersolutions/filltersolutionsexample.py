import pyaedt
import matplotlib
from pyaedt.filtersolutions_core.attributes import FilterType
from pyaedt.filtersolutions_core.attributes import FilterImplementation
from pyaedt.filtersolutions_core.attributes import StopbandDefinition


if __name__ == "__main__":
    design = pyaedt.FilterSolutions(projectname= "fs1", implementation_type= FilterImplementation.LUMPED)
    design.attributes.filter_type = FilterType.ELLIPTIC
    design.attributes.stop_band_definition = StopbandDefinition.FREQUENCY
    print(design.attributes.stop_band_definition)