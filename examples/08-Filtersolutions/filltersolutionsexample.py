import pyaedt
import matplotlib.pyplot as plt

from pyaedt.filtersolutions import FilterClass
from pyaedt.filtersolutions import FilterType
from pyaedt.filtersolutions import FilterImplementation
from pyaedt.filtersolutions import FrequencyResponseColumn
from pyaedt.filtersolutions import DiplexerType
from pyaedt.filtersolutions import StopbandDefinition


#if __name__ == "__main__":

design = pyaedt.FilterSolutions(projectname= "fs1", implementation_type= FilterImplementation.LUMPED)
design.attributes.filter_type = FilterType.ELLIPTIC
design.attributes.stop_band_definition = StopbandDefinition.FREQUENCY
print(design.attributes.stop_band_definition)



