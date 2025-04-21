from ..EmitNode import *

class ReadOnlyFilter(EmitNode):
    def __init__(self, oDesign, result_id, node_id):
        self._is_component = True
        EmitNode.__init__(self, oDesign, result_id, node_id)

    @property
    def filename(self) -> str:
        """Filename
        "Name of file defining the outboard component."
        "Value should be a full file path."
        """
        val = self._get_property("Filename")
        return val

    @property
    def noise_temperature(self) -> float:
        """Noise Temperature
        "System Noise temperature (K) of the component."
        "Value should be between 0 and 1000."
        """
        val = self._get_property("Noise Temperature")
        return val

    @property
    def notes(self) -> str:
        """Notes
        "Expand to view/edit notes stored with the project."
        "        """
        val = self._get_property("Notes")
        return val

    class TypeOption(Enum):
        BY_FILE = "By File"
        LOW_PASS = "Low Pass"
        HIGH_PASS = "High Pass"
        BAND_PASS = "Band Pass"
        BAND_STOP = "Band Stop"
        TUNABLE_BANDPASS = "Tunable Bandpass"
        TUNABLE_BANDSTOP = "Tunable Bandstop"

    @property
    def type(self) -> TypeOption:
        """Type
        "Type of filter to define. The filter can be defined by file (measured or simulated data) or using one of EMIT's parametric models."
        "        """
        val = self._get_property("Type")
        val = self.TypeOption[val]
        return val

    @property
    def insertion_loss(self) -> float:
        """Insertion Loss
        "Filter pass band loss."
        "Value should be between 0 and 100."
        """
        val = self._get_property("Insertion Loss")
        return val

    @property
    def stop_band_attenuation(self) -> float:
        """Stop band Attenuation
        "Filter stop band loss (attenuation)."
        "Value should be less than 200."
        """
        val = self._get_property("Stop band Attenuation")
        return val

    @property
    def max_pass_band(self) -> float:
        """Max Pass Band
        "Maximum pass band frequency."
        "Value should be between 1 and 1e+11."
        """
        val = self._get_property("Max Pass Band")
        val = self._convert_from_internal_units(float(val), "Freq")
        return val

    @property
    def min_stop_band(self) -> float:
        """Min Stop Band
        "Minimum stop band frequency."
        "Value should be between 1 and 1e+11."
        """
        val = self._get_property("Min Stop Band")
        val = self._convert_from_internal_units(float(val), "Freq")
        return val

    @property
    def max_stop_band(self) -> float:
        """Max Stop Band
        "Maximum stop band frequency."
        "Value should be between 1 and 1e+11."
        """
        val = self._get_property("Max Stop Band")
        val = self._convert_from_internal_units(float(val), "Freq")
        return val

    @property
    def min_pass_band(self) -> float:
        """Min Pass Band
        "Minimum pass band frequency."
        "Value should be between 1 and 1e+11."
        """
        val = self._get_property("Min Pass Band")
        val = self._convert_from_internal_units(float(val), "Freq")
        return val

    @property
    def lower_stop_band(self) -> float:
        """Lower Stop Band
        "Lower stop band frequency."
        "Value should be between 1 and 1e+11."
        """
        val = self._get_property("Lower Stop Band")
        val = self._convert_from_internal_units(float(val), "Freq")
        return val

    @property
    def lower_cutoff(self) -> float:
        """Lower Cutoff
        "Lower cutoff frequency."
        "Value should be between 1 and 1e+11."
        """
        val = self._get_property("Lower Cutoff")
        val = self._convert_from_internal_units(float(val), "Freq")
        return val

    @property
    def higher_cutoff(self) -> float:
        """Higher Cutoff
        "Higher cutoff frequency."
        "Value should be between 1 and 1e+11."
        """
        val = self._get_property("Higher Cutoff")
        val = self._convert_from_internal_units(float(val), "Freq")
        return val

    @property
    def higher_stop_band(self) -> float:
        """Higher Stop Band
        "Higher stop band frequency."
        "Value should be between 1 and 1e+11."
        """
        val = self._get_property("Higher Stop Band")
        val = self._convert_from_internal_units(float(val), "Freq")
        return val

    @property
    def lower_cutoff_(self) -> float:
        """Lower Cutoff 
        "Lower cutoff frequency."
        "Value should be between 1 and 1e+11."
        """
        val = self._get_property("Lower Cutoff ")
        val = self._convert_from_internal_units(float(val), "Freq")
        return val

    @property
    def lower_stop_band_(self) -> float:
        """Lower Stop Band 
        "Lower stop band frequency."
        "Value should be between 1 and 1e+11."
        """
        val = self._get_property("Lower Stop Band ")
        val = self._convert_from_internal_units(float(val), "Freq")
        return val

    @property
    def higher_stop_band_(self) -> float:
        """Higher Stop Band 
        "Higher stop band frequency."
        "Value should be between 1 and 1e+11."
        """
        val = self._get_property("Higher Stop Band ")
        val = self._convert_from_internal_units(float(val), "Freq")
        return val

    @property
    def higher_cutoff_(self) -> float:
        """Higher Cutoff 
        "Higher cutoff frequency."
        "Value should be between 1 and 1e+11."
        """
        val = self._get_property("Higher Cutoff ")
        val = self._convert_from_internal_units(float(val), "Freq")
        return val

    @property
    def lowest_tuned_frequency_(self) -> float:
        """Lowest Tuned Frequency 
        "Lowest tuned frequency."
        "Value should be between 1 and 1e+11."
        """
        val = self._get_property("Lowest Tuned Frequency ")
        val = self._convert_from_internal_units(float(val), "Freq")
        return val

    @property
    def highest_tuned_frequency_(self) -> float:
        """Highest Tuned Frequency 
        "Highest tuned frequency."
        "Value should be between 1 and 1e+11."
        """
        val = self._get_property("Highest Tuned Frequency ")
        val = self._convert_from_internal_units(float(val), "Freq")
        return val

    @property
    def percent_bandwidth(self) -> float:
        """Percent Bandwidth
        "Tunable filter 3-dB bandwidth."
        "Value should be between 0.001 and 100."
        """
        val = self._get_property("Percent Bandwidth")
        return val

    @property
    def shape_factor(self) -> float:
        """Shape Factor
        "Ratio defining the filter rolloff."
        "Value should be between 1 and 100."
        """
        val = self._get_property("Shape Factor")
        return val

    @property
    def warnings(self) -> str:
        """Warnings
        "Warning(s) for this node."
        "        """
        val = self._get_property("Warnings")
        return val

