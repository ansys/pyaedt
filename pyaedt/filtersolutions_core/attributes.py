from ctypes import POINTER
from ctypes import byref
from ctypes import c_bool
from ctypes import c_char_p
from ctypes import c_int
from enum import Enum

import pyaedt.filtersolutions_core as fspy


class FilterType(Enum):
    """Selects type of filter with the associated mathematical formulation.

    Attributes:
    GAUSSIAN: Represents a Gaussian filter.
    BESSEL: Represents a Bessel filter.
    BUTTERWORTH: Represents a Butterworth filter.
    LEGENDRE: Represents a Legendre filter.
    CHEBYSHEV_I: Represents a Chevyshev type I filter.
    CHEBYSHEV_II: Represents a Chevyshev type II filter.
    HOURGLASS: Represents a Hourglass filter.
    ELLIPTIC: Represents a elliptic filter.
    Custom, rasied-cos, matched, and delay filter types are not available in this release.
    """

    GAUSSIAN = 0
    BESSEL = 1
    BUTTERWORTH = 2
    LEGENDRE = 3
    CHEBYSHEV_I = 4
    CHEBYSHEV_II = 5
    HOURGLASS = 6
    ELLIPTIC = 7


#   CUSTOM = 8
#   RAISED_COS = 9
#   MATCHED = 10
#   DELAY = 11


class FilterClass(Enum):
    """Selects class of filter for single band and multiple bands filters.

    Attributes:
    LOW_PASS: Represents a low pass filter.
    HIGH_PASS: Represents a high pass filter.
    DIPLEXER_1: Represents a first group of diplexer filter.
    BAND_PASS: Represents a band pass filter.
    BAND_STOP: Represents a band stop filter.
    DIPLEXER_2: Represents a second group of diplexer filter.
    LOW_BAND: Represents a combined low pass and multi band filter.
    BAND_HIGH: Represents a combined high pass and multi band filter.
    BAND_BAND: Represents a multi band passfilter.
    STOP_STOP: Represents a multi band stop filter.
    """

    LOW_PASS = 0
    HIGH_PASS = 1
    DIPLEXER_1 = 2
    BAND_PASS = 3
    BAND_STOP = 4
    DIPLEXER_2 = 5
    LOW_BAND = 6
    BAND_HIGH = 7
    BAND_BAND = 8
    STOP_STOP = 9


class FilterImplementation(Enum):
    """Selects implementations type of filter. This release covers only lumped filter technology.

    Attributes:
    LUMPED: Represents a lumped implementation.
    DISTRIB: Represents a distributed implementation.
    ACTIVE: Represents a active implementation.
    SWCAP: Represents a switched capacitor implementation.
    DIGITAL: Represents a digital implementation.
    """

    LUMPED = 0
    DISTRIB = 1
    ACTIVE = 2
    SWCAP = 3
    DIGITAL = 4


class DiplexerType(Enum):
    """Selects topology of diplexers.

    Attributes:
    HI_LO: Represents a high pass low pass diplexer type.
    BP_1: Represents a band pass band pass diplexer type.
    BP_2: Represents a band pass band pass diplexer type.
    BP_BS: Represents a band pass band stop diplexer type.
    TRIPLEXER_1: Represents a low pass, band pass, and high pass triplexer type.
    TRIPLEXER_2: Represents a low pass, band pass, and high pass triplexer type.
    """

    HI_LO = 0
    BP_1 = 1
    BP_2 = 2
    BP_BS = 3
    TRIPLEXER_1 = 4
    TRIPLEXER_2 = 5


class BesselRipplePercentage(Enum):
    """Selects peak to peak group delay ripple magnitude as percent of average for Bessl filters.
    Attributes:
    ZERO: 0%
    HALF: 0.5%
    ONE: 1%
    TWO: 2%
    FIVE: 5%
    TEN: 10%
    """

    ZERO = 0
    HALF = 1
    ONE = 2
    TWO = 3
    FIVE = 4
    TEN = 5


class GaussianTransition(Enum):
    """Selects transition attenuation in dB for Gaussian filters to improve group delay response.
    Attributes:
    TRANSITION_NONE: 0dB
    TRANSITION_3_DB: 3dB
    TRANSITION_6_DB: 6dB
    TRANSITION_9_DB: 9dB
    TRANSITION_12_DB: 12dB
    TRANSITION_15_DB: 15dB
    """

    TRANSITION_NONE = 0
    TRANSITION_3_DB = 1
    TRANSITION_6_DB = 2
    TRANSITION_9_DB = 3
    TRANSITION_12_DB = 4
    TRANSITION_15_DB = 5


class GaussianBesselReflection(Enum):
    """Selects various synthesis methods for Gaussian and Bessel filters."""

    OPTION_1 = 0
    OPTION_2 = 1
    OPTION_3 = 2


class RippleConstrictionBandSelect(Enum):
    """Selects the bands to apply the constrict ripple parameter.
    Attributes:
    STOP: stop band
    PASS: pass band
    BOTH: stop and pass bands
    """

    STOP = 0
    PASS = 1
    BOTH = 2


class SinglePointRippleInfZeros(Enum):
    """Selects either 1 or 3 non-infifnite zeros at single frequency point to confine ripple.
    Attributes:
    RIPPLE_INF_ZEROS_1: 1 zero
    RIPPLE_INF_ZEROS_3: 3 zeros
    """

    RIPPLE_INF_ZEROS_1 = 0
    RIPPLE_INF_ZEROS_3 = 1


class PassbandDefinition(Enum):
    """Selects type of frequency entries to get either center frequency and bandwidth or corner frequencies."""

    CENTER_FREQUENCY = 0
    CORNER_FREQUENCIES = 1


class StopbandDefinition(Enum):
    """Selects stop band parameter to be compared to pass band."""

    RATIO = 0
    FREQUENCY = 1
    ATTENUATION_DB = 2


class Attributes:
    """Defines attributes and parameters of filters.

    This class allows you to construct all the necessary attributes for the FilterDesign class.

    Attributes
    ----------
    _dll: CDLL
        FilterSolutions C++ API DLL.
    _dll_interface: DllInterface
        an instance of DllInterface class

    Methods
    ----------
    _define_attributes_dll_functions:
        Define argument types of DLL function.
    """

    def __init__(self):
        self._dll = fspy._dll_interface()._dll
        self._dll_interface = fspy._dll_interface()
        self._define_attributes_dll_functions()

    def _define_attributes_dll_functions(self):
        """Define C++ API DLL functions."""
        self._dll.setFilterType.argtype = c_char_p
        self._dll.setFilterType.restype = c_int
        self._dll.getFilterType.argtypes = [c_char_p, c_int]
        self._dll.getFilterType.restype = c_int

        self._dll.setFilterClass.argtype = c_char_p
        self._dll.setFilterClass.restype = int
        self._dll.getFilterClass.argtypes = [c_char_p, c_int]
        self._dll.getFilterClass.restype = int

        self._dll.setFilterImplementation.argtype = c_char_p
        self._dll.setFilterImplementation.restype = c_int
        self._dll.getFilterImplementation.argtypes = [c_char_p, c_int]
        self._dll.getFilterImplementation.restype = c_int

        self._dll.setMultipleBandsEnabled.argtype = c_bool
        self._dll.setMultipleBandsEnabled.restype = c_int
        self._dll.getMultipleBandsEnabled.argtype = POINTER(c_bool)
        self._dll.getMultipleBandsEnabled.restype = c_int

        self._dll.setMultipleBandsLowPassFrequency.argtype = c_char_p
        self._dll.setMultipleBandsLowPassFrequency.restype = c_int
        self._dll.getMultipleBandsLowPassFrequency.argtypes = [c_char_p, c_int]
        self._dll.getMultipleBandsLowPassFrequency.restype = c_int

        self._dll.setMultipleBandsHighPassFrequency.argtype = c_char_p
        self._dll.setMultipleBandsHighPassFrequency.restype = c_int
        self._dll.getMultipleBandsHighPassFrequency.argtypes = [c_char_p, c_int]
        self._dll.getMultipleBandsHighPassFrequency.restype = c_int

        self._dll.setDiplexerType.argtype = c_char_p
        self._dll.setDiplexerType.restype = c_int
        self._dll.getDiplexerType.argtypes = [c_char_p, c_int]
        self._dll.getDiplexerType.restype = c_int

        self._dll.setDiplexerType.argtype = c_char_p
        self._dll.setDiplexerType.restype = c_int
        self._dll.getDiplexerType.argtypes = [c_char_p, c_int]
        self._dll.getDiplexerType.restype = c_int

        self._dll.setOrder.argtype = c_int
        self._dll.setOrder.restype = c_int
        self._dll.getOrder.argtype = POINTER(c_int)
        self._dll.getOrder.restype = c_int

        self._dll.setMinimumOrderStopbandAttenuationdB.argtype = c_char_p
        self._dll.setMinimumOrderStopbandAttenuationdB.restype = c_int
        self._dll.getMinimumOrderStopbandAttenuationdB.argtypes = [c_char_p, c_int]
        self._dll.getMinimumOrderStopbandAttenuationdB.restype = c_int

        self._dll.setMinimumOrderStopbandFrequency.argtype = c_char_p
        self._dll.setMinimumOrderStopbandFrequency.restype = c_int
        self._dll.getMinimumOrderStopbandFrequency.argtypes = [c_char_p, c_int]
        self._dll.getMinimumOrderStopbandFrequency.restype = c_int

        self._dll.setIdealMinimumOrder.argtype = POINTER(c_int)
        self._dll.setIdealMinimumOrder.restype = c_int

        self._dll.getErrorMessage.argtypes = [c_char_p, c_int]
        self._dll.getErrorMessage.restype = c_int

        self._dll.setPassbandDef.argtype = c_int
        self._dll.setPassbandDef.restype = c_int
        self._dll.getPassbandDef.argtype = POINTER(c_int)
        self._dll.getPassbandDef.restype = c_int

        self._dll.setCenterFrequency.argtype = c_char_p
        self._dll.setCenterFrequency.restype = c_int
        self._dll.getCenterFrequency.argtypes = [c_char_p, c_int]
        self._dll.getCenterFrequency.restype = c_int

        self._dll.setPassbandFrequency.argtype = c_char_p
        self._dll.setPassbandFrequency.restype = c_int
        self._dll.getPassbandFrequency.argtypes = [c_char_p, c_int]
        self._dll.getPassbandFrequency.restype = c_int

        self._dll.setLowerFrequency.argtype = c_char_p
        self._dll.setLowerFrequency.restype = c_int
        self._dll.getLowerFrequency.argtypes = [c_char_p, c_int]
        self._dll.getLowerFrequency.restype = c_int

        self._dll.setUpperFrequency.argtype = c_char_p
        self._dll.setUpperFrequency.restype = c_int
        self._dll.getUpperFrequency.argtypes = [c_char_p, c_int]
        self._dll.getUpperFrequency.restype = c_int

        self._dll.setStopbandDef.argtype = c_int
        self._dll.setStopbandDef.restype = c_int
        self._dll.getStopbandDef.argtype = POINTER(c_int)
        self._dll.getStopbandDef.restype = c_int

        self._dll.setStopbandRatio.argtype = c_char_p
        self._dll.setStopbandRatio.restype = c_int
        self._dll.getStopbandRatio.argtypes = [c_char_p, c_int]
        self._dll.getStopbandRatio.restype = c_int

        self._dll.setStopbandFrequency.argtype = c_char_p
        self._dll.setStopbandFrequency.restype = c_int
        self._dll.getStopbandFrequency.argtypes = [c_char_p, c_int]
        self._dll.getStopbandFrequency.restype = c_int

        self._dll.setStopbandAttenuationdB.argtype = c_char_p
        self._dll.setStopbandAttenuationdB.restype = c_int
        self._dll.getStopbandAttenuationdB.argtypes = [c_char_p, c_int]
        self._dll.getStopbandAttenuationdB.restype = c_int

        self._dll.setStandardCutoffEnabled.argtype = c_bool
        self._dll.setStandardCutoffEnabled.restype = c_int
        self._dll.getStandardCutoffEnabled.argtype = POINTER(c_bool)
        self._dll.getStandardCutoffEnabled.restype = c_int

        self._dll.setCutoffAttenuationdB.argtype = c_char_p
        self._dll.setCutoffAttenuationdB.restype = c_int
        self._dll.getCutoffAttenuationdB.argtypes = [c_char_p, c_int]
        self._dll.getCutoffAttenuationdB.restype = c_int

        self._dll.setBesselNormalizedDelay.argtype = c_bool
        self._dll.setBesselNormalizedDelay.restype = c_int
        self._dll.getBesselNormalizedDelay.argtype = POINTER(c_bool)
        self._dll.getBesselNormalizedDelay.restype = c_int

        self._dll.setBesselEquiRippleDelayPeriod.argtype = c_char_p
        self._dll.setBesselEquiRippleDelayPeriod.restype = c_int
        self._dll.getBesselEquiRippleDelayPeriod.argtypes = [c_char_p, c_int]
        self._dll.getBesselEquiRippleDelayPeriod.restype = c_int

        self._dll.setBesselRipplePercentage.argtype = c_int
        self._dll.setBesselRipplePercentage.restype = c_int
        self._dll.getBesselRipplePercentage.argtype = POINTER(c_int)
        self._dll.getBesselRipplePercentage.restype = c_int

        self._dll.setPassbandRipple.argtype = c_char_p
        self._dll.setPassbandRipple.restype = c_int
        self._dll.getPassbandRipple.argtypes = [c_char_p, c_int]
        self._dll.getPassbandRipple.restype = c_int

        self._dll.setArithSymmetry.argtype = c_bool
        self._dll.setArithSymmetry.restype = c_int
        self._dll.getArithSymmetry.argtype = POINTER(c_bool)
        self._dll.getArithSymmetry.restype = c_int

        self._dll.setAsymmetric.argtype = c_bool
        self._dll.setAsymmetric.restype = c_int
        self._dll.getAsymmetric.argtype = POINTER(c_bool)
        self._dll.getAsymmetric.restype = c_int

        self._dll.setAsymmetricLowOrder.argtype = c_int
        self._dll.setAsymmetricLowOrder.restype = c_int
        self._dll.getAsymmetricLowOrder.argtype = POINTER(c_int)
        self._dll.getAsymmetricLowOrder.restype = c_int

        self._dll.setAsymmetricHighOrder.argtype = c_int
        self._dll.setAsymmetricHighOrder.restype = c_int
        self._dll.getAsymmetricHighOrder.argtype = POINTER(c_int)
        self._dll.getAsymmetricHighOrder.restype = c_int

        self._dll.setAsymmetricLowStopbandRatio.argtype = c_char_p
        self._dll.setAsymmetricLowStopbandRatio.restype = c_int
        self._dll.getAsymmetricLowStopbandRatio.argtypes = [c_char_p, c_int]
        self._dll.getAsymmetricLowStopbandRatio.restype = c_int

        self._dll.setAsymmetricHighStopbandRatio.argtype = c_char_p
        self._dll.setAsymmetricHighStopbandRatio.restype = c_int
        self._dll.getAsymmetricHighStopbandRatio.argtypes = [c_char_p, c_int]
        self._dll.getAsymmetricHighStopbandRatio.restype = c_int

        self._dll.setAsymmetricLowStopbandAttenuationdB.argtype = c_char_p
        self._dll.setAsymmetricLowStopbandAttenuationdB.restype = c_int
        self._dll.getAsymmetricLowStopbandAttenuationdB.argtypes = [c_char_p, c_int]
        self._dll.getAsymmetricLowStopbandAttenuationdB.restype = c_int

        self._dll.setAsymmetricHighStopbandAttenuationdB.argtype = c_char_p
        self._dll.setAsymmetricHighStopbandAttenuationdB.restype = c_int
        self._dll.getAsymmetricHighStopbandAttenuationdB.argtypes = [c_char_p, c_int]
        self._dll.getAsymmetricHighStopbandAttenuationdB.restype = c_int

        self._dll.setGaussianTransition.argtype = c_char_p
        self._dll.setGaussianTransition.restype = c_int
        self._dll.getGaussianTransition.argtypes = [c_char_p, c_int]
        self._dll.getGaussianTransition.restype = c_int

        self._dll.setGaussianBesselReflection.argtype = c_int
        self._dll.setGaussianBesselReflection.restype = c_int
        self._dll.getGaussianBesselReflection.argtype = POINTER(c_int)
        self._dll.getGaussianBesselReflection.restype = c_int

        self._dll.setEvenOrderMode.argtype = c_bool
        self._dll.setEvenOrderMode.restype = c_int
        self._dll.getEvenOrderMode.argtype = POINTER(c_bool)
        self._dll.getEvenOrderMode.restype = c_int

        self._dll.setEvenReflZeroTo0.argtype = c_bool
        self._dll.setEvenReflZeroTo0.restype = c_int
        self._dll.getEvenReflZeroTo0.argtype = POINTER(c_bool)
        self._dll.getEvenReflZeroTo0.restype = c_int

        self._dll.setEvenTrnZeroToInf.argtype = c_bool
        self._dll.setEvenTrnZeroToInf.restype = c_int
        self._dll.getEvenTrnZeroToInf.argtype = POINTER(c_bool)
        self._dll.getEvenTrnZeroToInf.restype = c_int

        self._dll.setConstrictRipple.argtype = c_bool
        self._dll.setConstrictRipple.restype = c_int
        self._dll.getConstrictRipple.argtype = POINTER(c_bool)
        self._dll.getConstrictRipple.restype = c_int

        self._dll.setSinglePointRipple.argtype = c_bool
        self._dll.setSinglePointRipple.restype = c_int
        self._dll.getSinglePointRipple.argtype = POINTER(c_bool)
        self._dll.getSinglePointRipple.restype = c_int

        self._dll.setHalfBandRipple.argtype = c_bool
        self._dll.setHalfBandRipple.restype = c_int
        self._dll.getHalfBandRipple.argtype = POINTER(c_bool)
        self._dll.getHalfBandRipple.restype = c_int

        self._dll.setRippleConstrictionPercent.argtype = c_char_p
        self._dll.setRippleConstrictionPercent.restype = c_int
        self._dll.getRippleConstrictionPercent.argtypes = [c_char_p, c_int]
        self._dll.getRippleConstrictionPercent.restype = c_int

        self._dll.setRippleConstrictionBandSelect.argtype = c_char_p
        self._dll.setRippleConstrictionBandSelect.restype = c_int
        self._dll.getRippleConstrictionBandSelect.argtypes = [c_char_p, c_int]
        self._dll.getRippleConstrictionBandSelect.restype = c_int

        self._dll.setSinglePointRippleNoninfiniteZeros.argtype = c_char_p
        self._dll.setSinglePointRippleNoninfiniteZeros.restype = c_int
        self._dll.getSinglePointRippleNoninfiniteZeros.argtypes = [c_char_p, c_int]
        self._dll.getSinglePointRippleNoninfiniteZeros.restype = c_int

        self._dll.setDelayEqualizer.argtype = c_bool
        self._dll.setDelayEqualizer.restype = c_int
        self._dll.getDelayEqualizer.argtype = POINTER(c_bool)
        self._dll.getDelayEqualizer.restype = c_int

        self._dll.setDelayEqualizerOrder.argtype = c_int
        self._dll.setDelayEqualizerOrder.restype = c_int
        self._dll.getDelayEqualizerOrder.argtype = POINTER(c_int)
        self._dll.getDelayEqualizerOrder.restype = c_int

        self._dll.setStandardDelayEquCut.argtype = c_bool
        self._dll.setStandardDelayEquCut.restype = c_int
        self._dll.getStandardDelayEquCut.argtype = POINTER(c_bool)
        self._dll.getStandardDelayEquCut.restype = c_int

        self._dll.setDelayEquCutoffAttenuationdB.argtype = c_char_p
        self._dll.setDelayEquCutoffAttenuationdB.restype = c_int
        self._dll.getDelayEquCutoffAttenuationdB.argtypes = [c_char_p, c_int]
        self._dll.getDelayEquCutoffAttenuationdB.restype = c_int

    @property
    def filter_type(self) -> FilterType:
        """The type (mathematical formulation) of filter. The full list of types are listed in FilterType enum.
        The default is `BUTTERWORTH`.

        Returns
        -------
        :enum:`FilterType`
        """
        type_string = self._dll_interface.get_string(self._dll.getFilterType)
        return self._dll_interface.string_to_enum(FilterType, type_string)

    @filter_type.setter
    def filter_type(self, filter_type: FilterType):
        if filter_type:
            string_value = self._dll_interface.enum_to_string(filter_type)
            self._dll_interface.set_string(self._dll.setFilterType, string_value)

    @property
    def filter_class(self) -> FilterClass:
        """The class (band definition) of filter. The full list of classes are listed in FilterClass enum.
        The default is `LOW_PASS`.

        Returns
        -------
        :enum:`FilterClass`
        """
        type_string = self._dll_interface.get_string(self._dll.getFilterClass)
        return self._dll_interface.string_to_enum(FilterClass, type_string)

    @filter_class.setter
    def filter_class(self, filter_class: FilterClass):
        if filter_class:
            string_value = self._dll_interface.enum_to_string(filter_class)
            self._dll_interface.set_string(self._dll.setFilterClass, string_value)

    @property
    def filter_implementation(self) -> FilterImplementation:
        """The technology used to implement the filter.
        The full list of implementations are listed in FilterImplementation enum.
        The default is `LUMPED`.

        Returns
        -------
        :enum:'FilterImplementation'
        """
        type_string = self._dll_interface.get_string(self._dll.getFilterImplementation)
        return self._dll_interface.string_to_enum(FilterImplementation, type_string)

    @filter_implementation.setter
    def filter_implementation(self, filter_implementation: FilterImplementation):
        if filter_implementation:
            string_value = self._dll_interface.enum_to_string(filter_implementation)
            self._dll_interface.set_string(self._dll.setFilterImplementation, string_value)

    @property
    def diplexer_type(self) -> DiplexerType:
        """The type of diplexer topology. Only applicable to lumped filters.
        The full list of diplexer types are listed in DiplexerType enum.
        The default is `HI_LO` for `DIPLEXER_1` filter class.
        The default is `BP_BS` for `DIPLEXER_2` filter class.

        Returns
        -------
        :enum:`DiplexerType`
        """
        type_string = self._dll_interface.get_string(self._dll.getDiplexerType)
        return self._dll_interface.string_to_enum(DiplexerType, type_string)

    @diplexer_type.setter
    def diplexer_type(self, diplexer_type: DiplexerType):
        string_value = self._dll_interface.enum_to_string(diplexer_type)
        self._dll_interface.set_string(self._dll.setDiplexerType, string_value)

    @property
    def filter_multiple_bands_enabled(self) -> bool:
        """Whether to enable the multiple bands table. The default is `False`.

        Returns
        -------
        bool
        """
        filter_multiple_bands_enabled = c_bool()
        status = self._dll.getMultipleBandsEnabled(byref(filter_multiple_bands_enabled))
        fspy._dll_interface().raise_error(status)
        return bool(filter_multiple_bands_enabled.value)

    @filter_multiple_bands_enabled.setter
    def filter_multiple_bands_enabled(self, filter_multiple_bands_enabled: bool):
        status = self._dll.setMultipleBandsEnabled(filter_multiple_bands_enabled)
        fspy._dll_interface().raise_error(status)

    @property
    def filter_multiple_bands_low_pass_frequency(self) -> str:
        """The multiple bands low pass frequency of combined low pass and band pass filters. The default is `1GHz`.

        Returns
        -------
        str
        """
        filter_multiple_bands_low_pass_freq_string = self._dll_interface.get_string(
            self._dll.getMultipleBandsLowPassFrequency
        )
        return filter_multiple_bands_low_pass_freq_string

    @filter_multiple_bands_low_pass_frequency.setter
    def filter_multiple_bands_low_pass_frequency(self, filter_multiple_bands_low_pass_freq_string):
        self._dll_interface.set_string(
            self._dll.setMultipleBandsLowPassFrequency,
            filter_multiple_bands_low_pass_freq_string,
        )

    @property
    def filter_multiple_bands_high_pass_frequency(self) -> str:
        """The multiple bands high pass frequency of combined high pass and band pass filters. The default is `1GHz`.

        Returns
        -------
        str
        """
        filter_multiple_bands_high_pass_freq_string = self._dll_interface.get_string(
            self._dll.getMultipleBandsHighPassFrequency
        )
        return filter_multiple_bands_high_pass_freq_string

    @filter_multiple_bands_high_pass_frequency.setter
    def filter_multiple_bands_high_pass_frequency(self, filter_multiple_bands_high_pass_freq_string):
        self._dll_interface.set_string(
            self._dll.setMultipleBandsHighPassFrequency,
            filter_multiple_bands_high_pass_freq_string,
        )

    @property
    def order(self) -> int:
        """Order of filter. The default is `5`.

        Returns
        -------
        int
        """
        order = c_int()
        status = self._dll.getOrder(byref(order))
        fspy._dll_interface().raise_error(status)
        return int(order.value)

    @order.setter
    def order(self, order: int):
        status = self._dll.setOrder(order)
        fspy._dll_interface().raise_error(status)

    @property
    def minimum_order_stop_band_attenuation_db(self) -> str:
        """Filter stop band attenuation in dB for calculation of the filter minimum order.
        The default is `50`.

        Returns
        -------
        str
        """
        minimum_order_stop_band_attenuation_db_string = self._dll_interface.get_string(
            self._dll.getMinimumOrderStopbandAttenuationdB
        )
        return minimum_order_stop_band_attenuation_db_string

    @minimum_order_stop_band_attenuation_db.setter
    def minimum_order_stop_band_attenuation_db(self, minimum_order_stop_band_attenuation_db_string):
        self._dll_interface.set_string(
            self._dll.setMinimumOrderStopbandAttenuationdB,
            minimum_order_stop_band_attenuation_db_string,
        )

    @property
    def minimum_order_stop_band_frequency(self) -> str:
        """Filter stop band frequency for calculation of the filter minimum order.
        The default is `10 GHz`.

        Returns
        -------
        str
        """
        minimum_order_stop_band_frequency_string = self._dll_interface.get_string(
            self._dll.getMinimumOrderStopbandFrequency
        )
        return minimum_order_stop_band_frequency_string

    @minimum_order_stop_band_frequency.setter
    def minimum_order_stop_band_frequency(self, minimum_order_stop_band_frequency_string):
        self._dll_interface.set_string(
            self._dll.setMinimumOrderStopbandFrequency,
            minimum_order_stop_band_frequency_string,
        )

    @property
    def ideal_minimum_order(self) -> int:
        """Filter minimum order for the defined stop band frequency and attenuation parameters.

        Returns
        -------
        int
        """
        minimum_order = c_int()
        status = self._dll.setIdealMinimumOrder(byref(minimum_order))
        fspy._dll_interface().raise_error(status)
        return int(minimum_order.value)

    @property
    def pass_band_definition(self) -> PassbandDefinition:
        """Pass band frequency entry options.
        The default is `CENTER_FREQUENCY`.

        Returns
        -------
        :enum: PassbandDefinition
        """
        index = c_int()
        pass_band_definition = list(PassbandDefinition)
        status = self._dll.getPassbandDef(byref(index))
        fspy._dll_interface().raise_error(status)
        pass_band_definition = pass_band_definition[index.value]
        return pass_band_definition

    @pass_band_definition.setter
    def pass_band_definition(self, column: PassbandDefinition):
        status = self._dll.setPassbandDef(column.value)
        fspy._dll_interface().raise_error(status)

    @property
    def pass_band_center_frequency(self) -> str:
        """Filter pass band or center frequency.
        The default is `1 GHz`.

        Returns
        -------
        str
        """
        center_freq_string = self._dll_interface.get_string(self._dll.getCenterFrequency)
        return center_freq_string

    @pass_band_center_frequency.setter
    def pass_band_center_frequency(self, center_freq_string):
        self._dll_interface.set_string(self._dll.setCenterFrequency, center_freq_string)

    @property
    def pass_band_width_frequency(self) -> str:
        """Pass band width frequency for band pass or band stop filters.
        The default is `200 MHz`.

        Returns
        -------
        str
        """
        pass_band_freq_string = self._dll_interface.get_string(self._dll.getPassbandFrequency)
        return pass_band_freq_string

    @pass_band_width_frequency.setter
    def pass_band_width_frequency(self, pass_band_freq_string):
        self._dll_interface.set_string(self._dll.setPassbandFrequency, pass_band_freq_string)

    @property
    def lower_frequency(self) -> str:
        """Filter lower corner frequency.
        The default is `905 MHz`.

        Returns
        -------
        str
        """
        lower_freq_string = self._dll_interface.get_string(self._dll.getLowerFrequency)
        return lower_freq_string

    @lower_frequency.setter
    def lower_frequency(self, lower_freq_string):
        self._dll_interface.set_string(self._dll.setLowerFrequency, lower_freq_string)

    @property
    def upper_frequency(self) -> str:
        """Filter upper corner frequency.
        The default is `1.105 MHz`.

        Returns
        -------
        str
        """
        upper_freq_string = self._dll_interface.get_string(self._dll.getUpperFrequency)
        return upper_freq_string

    @upper_frequency.setter
    def upper_frequency(self, upper_freq_string):
        self._dll_interface.set_string(self._dll.setUpperFrequency, upper_freq_string)

    @property
    def stop_band_definition(self) -> StopbandDefinition:
        """Stop band parameter entry option.
        The default is `RATIO`.

        Returns
        -------
        :enum: StopbandDefinition
        """
        index = c_int()
        stop_band_definition = list(StopbandDefinition)
        status = self._dll.getStopbandDef(byref(index))
        fspy._dll_interface().raise_error(status)
        stop_band_definition = stop_band_definition[index.value]
        return stop_band_definition

    @stop_band_definition.setter
    def stop_band_definition(self, column: StopbandDefinition):
        status = self._dll.setStopbandDef(column.value)
        fspy._dll_interface().raise_error(status)

    @property
    def stop_band_ratio(self) -> str:
        """Filter stop band ratio.
        The default is `1.2`.

        Returns
        -------
        str
        """
        stop_band_ratio_string = self._dll_interface.get_string(self._dll.getStopbandRatio)
        return stop_band_ratio_string

    @stop_band_ratio.setter
    def stop_band_ratio(self, stop_band_ratio_string):
        self._dll_interface.set_string(self._dll.setStopbandRatio, stop_band_ratio_string)

    @property
    def stop_band_frequency(self) -> str:
        """Filter stop band frequency.
        The default is `1.2 GHz`.

        Returns
        -------
        str
        """
        stop_band_frequency_string = self._dll_interface.get_string(self._dll.getStopbandFrequency)
        return stop_band_frequency_string

    @stop_band_frequency.setter
    def stop_band_frequency(self, stop_band_frequency_string):
        self._dll_interface.set_string(self._dll.setStopbandFrequency, stop_band_frequency_string)

    @property
    def stop_band_attenuation_db(self) -> str:
        """Filter stop band attenuation in dB.
        The default is `60 dB`.

        Returns
        -------
        str
        """
        stop_band_attenuation_db_string = self._dll_interface.get_string(self._dll.getStopbandAttenuationdB)
        return stop_band_attenuation_db_string

    @stop_band_attenuation_db.setter
    def stop_band_attenuation_db(self, stop_band_attenuation_db_string):
        self._dll_interface.set_string(self._dll.setStopbandAttenuationdB, stop_band_attenuation_db_string)

    @property
    def standard_pass_band_attenuation(self) -> bool:
        """Filter standard cut status.
        The default is `True`.

        Returns
        -------
        bool
        """
        standard_pass_band_attenuation = c_bool()
        status = self._dll.getStandardCutoffEnabled(byref(standard_pass_band_attenuation))
        fspy._dll_interface().raise_error(status)
        return bool(standard_pass_band_attenuation.value)

    @standard_pass_band_attenuation.setter
    def standard_pass_band_attenuation(self, standard_pass_band_attenuation: bool):
        status = self._dll.setStandardCutoffEnabled(standard_pass_band_attenuation)
        fspy._dll_interface().raise_error(status)

    @property
    def standard_pass_band_attenuation_value_db(self) -> str:
        """Filter cut off attenuation in dB.
        The default is `3.01 dB`.

        Returns
        -------
        str
        """
        standard_pass_band_attenuation_value_db_string = self._dll_interface.get_string(
            self._dll.getCutoffAttenuationdB
        )
        return standard_pass_band_attenuation_value_db_string

    @standard_pass_band_attenuation_value_db.setter
    def standard_pass_band_attenuation_value_db(self, standard_pass_band_attenuation_value_db_string):
        self._dll_interface.set_string(
            self._dll.setCutoffAttenuationdB,
            standard_pass_band_attenuation_value_db_string,
        )

    @property
    def bessel_normalized_delay(self) -> bool:
        """Bessel filter normalized delay status.
        The default is `False`.

        Returns
        -------
        bool
        """
        bessel_normalized_delay = c_bool()
        status = self._dll.getBesselNormalizedDelay(byref(bessel_normalized_delay))
        fspy._dll_interface().raise_error(status)
        return bool(bessel_normalized_delay.value)

    @bessel_normalized_delay.setter
    def bessel_normalized_delay(self, bessel_normalized_delay: bool):
        status = self._dll.setBesselNormalizedDelay(bessel_normalized_delay)
        fspy._dll_interface().raise_error(status)

    @property
    def bessel_normalized_delay_period(self) -> str:
        """Bessel filter normalized delay period.
        The default is `2`.

        Returns
        -------
        str
        """
        bessel_normalized_delay_period_string = self._dll_interface.get_string(self._dll.getBesselEquiRippleDelayPeriod)
        return bessel_normalized_delay_period_string

    @bessel_normalized_delay_period.setter
    def bessel_normalized_delay_period(self, bessel_normalized_delay_period_string):
        self._dll_interface.set_string(
            self._dll.setBesselEquiRippleDelayPeriod,
            bessel_normalized_delay_period_string,
        )

    @property
    def bessel_normalized_delay_percentage(self) -> int:
        """Bessel filter ripple percentage.
        The default is `0`.

        Returns
        -------
        int
        """
        index = c_int()
        bessel_normalized_delay_percentage = list(BesselRipplePercentage)
        status = self._dll.getBesselRipplePercentage(byref(index))
        fspy._dll_interface().raise_error(status)
        bessel_normalized_delay_percentage_string = bessel_normalized_delay_percentage[index.value]
        return bessel_normalized_delay_percentage_string

    @bessel_normalized_delay_percentage.setter
    def bessel_normalized_delay_percentage(self, column: BesselRipplePercentage):
        status = self._dll.setBesselRipplePercentage(column.value)
        fspy._dll_interface().raise_error(status)

    @property
    def pass_band_ripple(self) -> str:
        """Filter pass band ripple in dB.
        The default is `0.05 dB`.

        Returns
        -------
        str
        """
        pass_band_ripple_string = self._dll_interface.get_string(self._dll.getPassbandRipple)
        return pass_band_ripple_string

    @pass_band_ripple.setter
    def pass_band_ripple(self, pass_band_ripple_string):
        self._dll_interface.set_string(self._dll.setPassbandRipple, pass_band_ripple_string)

    @property
    def arith_symmetry(self) -> bool:
        """Filter arithmetic symmetry status.
        The default is `False`.

        Returns
        -------
        bool
        """
        arith_symmetry = c_bool()
        status = self._dll.getArithSymmetry(byref(arith_symmetry))
        fspy._dll_interface().raise_error(status)
        return bool(arith_symmetry.value)

    @arith_symmetry.setter
    def arith_symmetry(self, arith_symmetry: bool):
        status = self._dll.setArithSymmetry(arith_symmetry)
        fspy._dll_interface().raise_error(status)

    @property
    def asymmetric(self) -> bool:
        """Filter asymmetric status.
        The default is `False`.

        Returns
        -------
        bool
        """
        asymmetric = c_bool()
        status = self._dll.getAsymmetric(byref(asymmetric))
        fspy._dll_interface().raise_error(status)
        return bool(asymmetric.value)

    @asymmetric.setter
    def asymmetric(self, asymmetric: bool):
        status = self._dll.setAsymmetric(asymmetric)
        fspy._dll_interface().raise_error(status)

    @property
    def asymmetric_low_order(self) -> int:
        """Filter asymmetry lower frequency order.
        The default is `5`.

        Returns
        -------
        int
        """
        asymmetric_low_order = c_int()
        status = self._dll.getAsymmetricLowOrder(byref(asymmetric_low_order))
        fspy._dll_interface().raise_error(status)
        return int(asymmetric_low_order.value)

    @asymmetric_low_order.setter
    def asymmetric_low_order(self, asymmetric_low_order: int):
        status = self._dll.setAsymmetricLowOrder(asymmetric_low_order)
        fspy._dll_interface().raise_error(status)

    @property
    def asymmetric_high_order(self) -> int:
        """Filter asymmetry higher frequency order.
        The default is `5`.

        Returns
        -------
        int
        """
        asymmetric_high_order = c_int()
        status = self._dll.getAsymmetricHighOrder(byref(asymmetric_high_order))
        fspy._dll_interface().raise_error(status)
        return int(asymmetric_high_order.value)

    @asymmetric_high_order.setter
    def asymmetric_high_order(self, asymmetric_high_order: int):
        status = self._dll.setAsymmetricHighOrder(asymmetric_high_order)
        fspy._dll_interface().raise_error(status)

    @property
    def asymmetric_low_stop_band_ratio(self) -> str:
        """Filter asymmetry lower stop band ratio.
        The default is `1.2`.

        Returns
        -------
        str
        """
        asymmetric_low_stop_band_ratio_string = self._dll_interface.get_string(self._dll.getAsymmetricLowStopbandRatio)
        return asymmetric_low_stop_band_ratio_string

    @asymmetric_low_stop_band_ratio.setter
    def asymmetric_low_stop_band_ratio(self, asymmetric_low_stop_band_ratio_string):
        self._dll_interface.set_string(
            self._dll.setAsymmetricLowStopbandRatio,
            asymmetric_low_stop_band_ratio_string,
        )

    @property
    def asymmetric_high_stop_band_ratio(self) -> str:
        """Filter asymmetry higher stop band ratio.
        The default is `1.2`.

        Returns
        -------
        str
        """
        asymmetric_high_stop_band_ratio_string = self._dll_interface.get_string(
            self._dll.getAsymmetricHighStopbandRatio
        )
        return asymmetric_high_stop_band_ratio_string

    @asymmetric_high_stop_band_ratio.setter
    def asymmetric_high_stop_band_ratio(self, asymmetric_high_stop_band_ratio_string):
        self._dll_interface.set_string(
            self._dll.setAsymmetricHighStopbandRatio,
            asymmetric_high_stop_band_ratio_string,
        )

    @property
    def asymmetric_low_stop_band_attenuation_db(self) -> str:
        """Filter asymmetry lower stop band attenuation in dB.
        The default is `60 dB`.

        Returns
        -------
        str
        """
        asymmetric_low_stop_band_attenuation_db_string = self._dll_interface.get_string(
            self._dll.getAsymmetricLowStopbandAttenuationdB
        )
        return asymmetric_low_stop_band_attenuation_db_string

    @asymmetric_low_stop_band_attenuation_db.setter
    def asymmetric_low_stop_band_attenuation_db(self, asymmetric_low_stop_band_attenuation_db_string):
        self._dll_interface.set_string(
            self._dll.setAsymmetricLowStopbandAttenuationdB,
            asymmetric_low_stop_band_attenuation_db_string,
        )

    @property
    def asymmetric_high_stop_band_attenuation_db(self) -> str:
        """Filter asymmetry higher stop band attenuation in dB.
        The default is `60 dB`.

        Returns
        -------
        str
        """
        asymmetric_high_stop_band_attenuation_db_string = self._dll_interface.get_string(
            self._dll.getAsymmetricHighStopbandAttenuationdB
        )
        return asymmetric_high_stop_band_attenuation_db_string

    @asymmetric_high_stop_band_attenuation_db.setter
    def asymmetric_high_stop_band_attenuation_db(self, asymmetric_high_stop_band_attenuation_db_string):
        self._dll_interface.set_string(
            self._dll.setAsymmetricHighStopbandAttenuationdB,
            asymmetric_high_stop_band_attenuation_db_string,
        )

    @property
    def gaussian_transition(self) -> GaussianTransition:
        """Gaussian filter transition option.
        The default is `TRANSITION_NONE`.

        Returns
        -------
        :enum: GaussianTransition
        """
        type_string = self._dll_interface.get_string(self._dll.getGaussianTransition)
        type_string = "TRANSITION_" + type_string
        return self._dll_interface.string_to_enum(GaussianTransition, type_string)

    @gaussian_transition.setter
    def gaussian_transition(self, gaussian_transition: GaussianTransition):
        string_value = self._dll_interface.enum_to_string(gaussian_transition)
        self._dll_interface.set_string(self._dll.setGaussianTransition, string_value)

    @property
    def gaussian_bessel_reflection(self) -> GaussianBesselReflection:
        """Gaussian or Bessel filter reflection option.
        The default is `OPTION_1`.

        Returns
        -------
        :enum: GaussianBesselReflection
        """
        index = c_int()
        gaussian_bessel_reflection = list(GaussianBesselReflection)
        status = self._dll.getGaussianBesselReflection(byref(index))
        fspy._dll_interface().raise_error(status)
        gaussian_bessel_reflection = gaussian_bessel_reflection[index.value]
        return gaussian_bessel_reflection

    @gaussian_bessel_reflection.setter
    def gaussian_bessel_reflection(self, column: GaussianBesselReflection):
        status = self._dll.setGaussianBesselReflection(column.value)
        fspy._dll_interface().raise_error(status)

    @property
    def even_order(self) -> bool:
        """Filter even order mode status for filter with even orders.
        The default is `True`.

        Returns
        -------
        bool
        """
        even_order = c_bool()
        status = self._dll.getEvenOrderMode(byref(even_order))
        fspy._dll_interface().raise_error(status)
        return bool(even_order.value)

    @even_order.setter
    def even_order(self, even_order: bool):
        status = self._dll.setEvenOrderMode(even_order)
        fspy._dll_interface().raise_error(status)

    @property
    def even_order_refl_zero(self) -> bool:
        """Filter even order reflection zeros to 0 status.
        The default is `True`.

        Returns
        -------
        bool
        """
        even_order_refl_zero = c_bool()
        status = self._dll.getEvenReflZeroTo0(byref(even_order_refl_zero))
        fspy._dll_interface().raise_error(status)
        return bool(even_order_refl_zero.value)

    @even_order_refl_zero.setter
    def even_order_refl_zero(self, even_order_refl_zero: bool):
        status = self._dll.setEvenReflZeroTo0(even_order_refl_zero)
        fspy._dll_interface().raise_error(status)

    @property
    def even_order_trn_zero(self) -> bool:
        """Filter even order reflection zeros to infinite status.
        The default is `True`.

        Returns
        -------
        bool
        """
        even_order_trn_zero = c_bool()
        status = self._dll.getEvenTrnZeroToInf(byref(even_order_trn_zero))
        fspy._dll_interface().raise_error(status)
        return bool(even_order_trn_zero.value)

    @even_order_trn_zero.setter
    def even_order_trn_zero(self, even_order_trn_zero: bool):
        status = self._dll.setEvenTrnZeroToInf(even_order_trn_zero)
        fspy._dll_interface().raise_error(status)

    @property
    def constrict_ripple(self) -> bool:
        """Filter equiripple constriction status.
        The default is `False`.

        Returns
        -------
        bool
        """
        constrict_ripple = c_bool()
        status = self._dll.getConstrictRipple(byref(constrict_ripple))
        fspy._dll_interface().raise_error(status)
        return bool(constrict_ripple.value)

    @constrict_ripple.setter
    def constrict_ripple(self, constrict_ripple: bool):
        status = self._dll.setConstrictRipple(constrict_ripple)
        fspy._dll_interface().raise_error(status)

    @property
    def single_point_ripple(self) -> bool:
        """Filter ripple confinement to a single frequency point status.
        The default is `False`.

        Returns
        -------
        bool
        """
        single_point_ripple = c_bool()
        status = self._dll.getSinglePointRipple(byref(single_point_ripple))
        fspy._dll_interface().raise_error(status)
        return bool(single_point_ripple.value)

    @single_point_ripple.setter
    def single_point_ripple(self, single_point_ripple: bool):
        self._dll.setSinglePointRipple(single_point_ripple)

    @property
    def half_band_ripple(self) -> bool:
        """Filter ripple with half of the zeros in the given band status.
        The default is `False`.

        Returns
        -------
        bool
        """
        half_band_point_ripple = c_bool()
        status = self._dll.getHalfBandRipple(byref(half_band_point_ripple))
        fspy._dll_interface().raise_error(status)
        return bool(half_band_point_ripple.value)

    @half_band_ripple.setter
    def half_band_ripple(self, half_band_ripple: bool):
        status = self._dll.setHalfBandRipple(half_band_ripple)
        fspy._dll_interface().raise_error(status)

    @property
    def constrict_ripple_percent(self) -> str:
        """Filter ripple constriction percentage.
        The default is `False`.

        Returns
        -------
        str
        """
        constrict_ripple_percent_string = self._dll_interface.get_string(self._dll.getRippleConstrictionPercent)
        return constrict_ripple_percent_string

    @constrict_ripple_percent.setter
    def constrict_ripple_percent(self, constrict_ripple_percent_string):
        self._dll_interface.set_string(self._dll.setRippleConstrictionPercent, constrict_ripple_percent_string)

    @property
    def ripple_constriction_band(self) -> RippleConstrictionBandSelect:
        """Filter ripple constriction band option.
        The default is `STOP`.

        Returns
        -------
        :enum: RippleConstrictionBandSelect
        """
        type_string = self._dll_interface.get_string(self._dll.getRippleConstrictionBandSelect)
        return self._dll_interface.string_to_enum(RippleConstrictionBandSelect, type_string)

    @ripple_constriction_band.setter
    def ripple_constriction_band(self, ripple_constriction_band: RippleConstrictionBandSelect):
        string_value = self._dll_interface.enum_to_string(ripple_constriction_band)
        self._dll_interface.set_string(self._dll.setRippleConstrictionBandSelect, string_value)

    @property
    def single_point_ripple_inf_zeros(self) -> SinglePointRippleInfZeros:
        """Filter number of single point ripple infinite zeros.
        The default is `RIPPLE_INF_ZEROS_1`.

        Returns
        -------
        :enum: SinglePointRippleInfZeros
        """
        type_string = self._dll_interface.get_string(self._dll.getSinglePointRippleNoninfiniteZeros)
        type_string = "RIPPLE_INF_ZEROS_" + type_string
        return self._dll_interface.string_to_enum(SinglePointRippleInfZeros, type_string)

    @single_point_ripple_inf_zeros.setter
    def single_point_ripple_inf_zeros(self, single_point_ripple_inf_zeros: SinglePointRippleInfZeros):
        string_value = self._dll_interface.enum_to_string(single_point_ripple_inf_zeros)
        self._dll_interface.set_string(self._dll.setSinglePointRippleNoninfiniteZeros, string_value)

    @property
    def delay_equalizer(self) -> bool:
        """Filter delay equalizer status.
        The default is `False`.

        Returns
        -------
        bool
        """
        delay_equalizer = c_bool()
        status = self._dll.getDelayEqualizer(byref(delay_equalizer))
        fspy._dll_interface().raise_error(status)
        return bool(delay_equalizer.value)

    @delay_equalizer.setter
    def delay_equalizer(self, delay_equalizer: bool):
        self._dll.setDelayEqualizer(delay_equalizer)

    @property
    def delay_equalizer_order(self) -> int:
        """Filter delay equalizer order.
        The default is `2`.

        Returns
        -------
        int
        """
        delay_equalizer_order = c_int()
        status = self._dll.getDelayEqualizerOrder(byref(delay_equalizer_order))
        fspy._dll_interface().raise_error(status)
        return int(delay_equalizer_order.value)

    @delay_equalizer_order.setter
    def delay_equalizer_order(self, delay_equalizer_order: int):
        status = self._dll.setDelayEqualizerOrder(delay_equalizer_order)
        fspy._dll_interface().raise_error(status)

    @property
    def standard_delay_equ_pass_band_attenuation(self) -> bool:
        """Filter standard delay equalizer attenuation status.
        The default is `True`.

        Returns
        -------
        bool
        """
        standard_dealy_equ_cut = c_bool()
        status = self._dll.getStandardDelayEquCut(byref(standard_dealy_equ_cut))
        fspy._dll_interface().raise_error(status)
        return bool(standard_dealy_equ_cut.value)

    @standard_delay_equ_pass_band_attenuation.setter
    def standard_delay_equ_pass_band_attenuation(self, standard_delay_equ_pass_band_attenuation: bool):
        status = self._dll.setStandardDelayEquCut(standard_delay_equ_pass_band_attenuation)
        fspy._dll_interface().raise_error(status)

    @property
    def standard_delay_equ_pass_band_attenuation_value_db(self) -> str:
        """Filter standard delay equalizer cut Off attenuation in dB.
        The default is `3.01 dB`.

        Returns
        -------
        str
        """
        delay_equcutoff_attenuation_db_string = self._dll_interface.get_string(self._dll.getDelayEquCutoffAttenuationdB)
        return delay_equcutoff_attenuation_db_string

    @standard_delay_equ_pass_band_attenuation_value_db.setter
    def standard_delay_equ_pass_band_attenuation_value_db(
        self, standard_delay_equ_pass_band_attenuation_value_db_string
    ):
        self._dll_interface.set_string(
            self._dll.setDelayEquCutoffAttenuationdB,
            standard_delay_equ_pass_band_attenuation_value_db_string,
        )
