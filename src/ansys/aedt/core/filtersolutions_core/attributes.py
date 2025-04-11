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

from ctypes import POINTER
from ctypes import byref
from ctypes import c_bool
from ctypes import c_char_p
from ctypes import c_int
from enum import Enum

import ansys.aedt.core


class FilterType(Enum):
    """Provides an enum of filter types with associated mathematical formulations.

    **Attributes:**

    - GAUSSIAN: Represents a Gaussian filter.
    - BESSEL: Represents a Bessel filter.
    - BUTTERWORTH: Represents a Butterworth filter.
    - LEGENDRE: Represents a Legendre filter.
    - CHEBYSHEV_I: Represents a Chevyshev type I filter.
    - CHEBYSHEV_II: Represents a Chevyshev type II filter.
    - HOURGLASS: Represents an hourglass filter.
    - ELLIPTIC: Represents an elliptic filter.
    - DELAY: Represents a delay filter.
    - RAISED_COS: Represents a raised cosine filter.

    Custom and matched filter types are not available in this release.
    """

    GAUSSIAN = 0
    BESSEL = 1
    BUTTERWORTH = 2
    LEGENDRE = 3
    CHEBYSHEV_I = 4
    CHEBYSHEV_II = 5
    HOURGLASS = 6
    ELLIPTIC = 7
    DELAY = 8
    RAISED_COS = 9


#   CUSTOM = 8
#   MATCHED = 10
#   DELAY = 11


class FilterClass(Enum):
    """Provides an enum of filter types for single-band and multiple-bands filters.

    **Attributes:**

    - LOW_PASS: Represents a low-pass filter.
    - HIGH_PASS: Represents a high-pass filter.
    - DIPLEXER_1: Represents a first group of diplexer filter.
    - BAND_PASS: Represents a band-pass filter.
    - BAND_STOP: Represents a band-stop filter.
    - DIPLEXER_2: Represents a second group of diplexer filter.
    - LOW_BAND: Represents a combined low-pass and multi-band filter.
    - BAND_HIGH: Represents a combined high-pass and multi-band filter.
    - BAND_BAND: Represents a multi-band pass filter.
    - STOP_STOP: Represents a multi-band stop filter.
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


class DiplexerType(Enum):
    """Provides an enum of diplexer and triplexer types.

    **Attributes:**

    - HI_LO: Represents a high-pass, low-pass diplexer type.
    - BP_1: Represents a band-pass, band-pass diplexer type.
    - BP_2: Represents a band-pass, band-pass diplexer type.
    - BP_BS: Represents a band-pass, band-stop diplexer type.
    - TRIPLEXER_1: Represents a low-pass, band-pass, and high-pass triplexer type.
    - TRIPLEXER_2: Represents a low-pass, band-pass, and high-pass triplexer type.
    """

    HI_LO = 0
    BP_1 = 1
    BP_2 = 2
    BP_BS = 3
    TRIPLEXER_1 = 4
    TRIPLEXER_2 = 5


class RaisedCosineAlphaPercentage(Enum):
    """Provides an enum of alpha percentage for raised, root raised, or data transmission filters.

    **Attributes:**

    - FIFTEEN: 15%
    - TWENTY: 20%
    - TWENTY_FIVE: 25%
    - THIRTY: 30%
    - THIRTY_FIVE: 35%
    - FORTY: 40%
    - FORTY_FIVE: 45%
    - FIFTY: 50%
    - SEVENTY_FIVE: 75%
    - HUNDRED: 100%
    """

    FIFTEEN = 0
    FORTY = 1
    TWENTY = 2
    FORTY_FIVE = 3
    TWENTY_FIVE = 4
    FIFTY = 5
    THIRTY = 6
    SEVENTY_FIVE = 7
    THIRTY_FIVE = 8
    HUNDRED = 9


class BesselRipplePercentage(Enum):
    """Provides an enum of peak-to-peak group delay ripple magnitudes as percents of averages for Bessel filters.

    **Attributes:**

    - ZERO: 0%
    - HALF: 0.5%
    - ONE: 1%
    - TWO: 2%
    - FIVE: 5%
    - TEN: 10%
    """

    ZERO = 0
    HALF = 1
    ONE = 2
    TWO = 3
    FIVE = 4
    TEN = 5


class GaussianTransition(Enum):
    """Provides an enum of transition attenuations in dB for Gaussian filters to improve group delay response.

    **Attributes:**

    - TRANSITION_NONE: 0dB
    - TRANSITION_3_DB: 3dB
    - TRANSITION_6_DB: 6dB
    - TRANSITION_9_DB: 9dB
    - TRANSITION_12_DB: 12dB
    - TRANSITION_15_DB: 15dB
    """

    TRANSITION_NONE = 0
    TRANSITION_3_DB = 1
    TRANSITION_6_DB = 2
    TRANSITION_9_DB = 3
    TRANSITION_12_DB = 4
    TRANSITION_15_DB = 5


class GaussianBesselReflection(Enum):
    """Provides an enum of synthesis methods for Gaussian and Bessel filters.

    **Attributes:**

    - OPTION_1: The first method for filter synthesis.
    - OPTION_2: The second method for filter synthesis.
    - OPTION_3: The third method for filter synthesis.
    """

    OPTION_1 = 0
    OPTION_2 = 1
    OPTION_3 = 2


class RippleConstrictionBandSelect(Enum):
    """Provides an enum of the bands to apply constrict the ripple parameter.

    **Attributes:**

    - STOP: Stop band
    - PASS: Pass band
    - BOTH: Stop and pass bands
    """

    STOP = 0
    PASS = 1
    BOTH = 2


class SinglePointRippleInfZeros(Enum):
    """Provides an enum for either one or three non-infinite zeros at the single frequency point to confine the ripple.

    **Attributes:**

    - RIPPLE_INF_ZEROS_1: One zero
    - RIPPLE_INF_ZEROS_3: Three zeros
    """

    RIPPLE_INF_ZEROS_1 = 0
    RIPPLE_INF_ZEROS_3 = 1


class PassbandDefinition(Enum):
    """Provides an enum to get either center frequency and bandwidth or corner frequencies.

    **Attributes:**

    - CENTER_FREQUENCY: Define the passband by the center frequency and bandwidth.
    - CORNER_FREQUENCIES: Define the passband by the corner frequencies.
    """

    CENTER_FREQUENCY = 0
    CORNER_FREQUENCIES = 1


class StopbandDefinition(Enum):
    """Provides an enum for comparing the stop band parameter to the pass band parameter.

    **Attributes:**

    - RATIO: Ratio between the stop band and pass band frequencies.
    - FREQUENCY: Explicit frequency.
    - ATTENUATION_DB: Attenuation in decibels.
    """

    RATIO = 0
    FREQUENCY = 1
    ATTENUATION_DB = 2


class Attributes:
    """Defines attributes and parameters of filters.

    This class lets you construct all the necessary attributes for the ``FilterDesign`` class.
    """

    def __init__(self):
        self._dll = ansys.aedt.core.filtersolutions_core._dll_interface()._dll
        self._dll_interface = ansys.aedt.core.filtersolutions_core._dll_interface()
        self._dll_interface.restore_defaults()
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

        self._dll.setFilterImplementation.argtype = c_int
        self._dll.setFilterImplementation.restype = c_int
        self._dll.getFilterImplementation.argtype = POINTER(c_int)
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

        self._dll.setDiplexerInnerPassbandWidth.argtype = c_char_p
        self._dll.setDiplexerInnerPassbandWidth.restype = c_int
        self._dll.getDiplexerInnerPassbandWidth.argtypes = [c_char_p, c_int]
        self._dll.getDiplexerInnerPassbandWidth.restype = c_int

        self._dll.setDiplexerOuterPassbandWidth.argtype = c_char_p
        self._dll.setDiplexerOuterPassbandWidth.restype = c_int
        self._dll.getDiplexerOuterPassbandWidth.argtypes = [c_char_p, c_int]
        self._dll.getDiplexerOuterPassbandWidth.restype = c_int

        self._dll.setDiplexerLowerCenterFrequency.argtype = c_char_p
        self._dll.setDiplexerLowerCenterFrequency.restype = c_int
        self._dll.getDiplexerLowerCenterFrequency.argtypes = [c_char_p, c_int]
        self._dll.getDiplexerLowerCenterFrequency.restype = c_int

        self._dll.setDiplexerUpperCenterFrequency.argtype = c_char_p
        self._dll.setDiplexerUpperCenterFrequency.restype = c_int
        self._dll.getDiplexerUpperCenterFrequency.argtypes = [c_char_p, c_int]
        self._dll.getDiplexerUpperCenterFrequency.restype = c_int

        self._dll.setDiplexerLowerBandwidth.argtype = c_char_p
        self._dll.setDiplexerLowerBandwidth.restype = c_int
        self._dll.getDiplexerLowerBandwidth.argtypes = [c_char_p, c_int]
        self._dll.getDiplexerLowerBandwidth.restype = c_int

        self._dll.setDiplexerUpperBandwidth.argtype = c_char_p
        self._dll.setDiplexerUpperBandwidth.restype = c_int
        self._dll.getDiplexerUpperBandwidth.argtypes = [c_char_p, c_int]
        self._dll.getDiplexerUpperBandwidth.restype = c_int

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

        self._dll.setMinimumOrderGroupDelayError.argtype = c_char_p
        self._dll.setMinimumOrderGroupDelayError.restype = c_int
        self._dll.getMinimumOrderGroupDelayError.argtypes = [c_char_p, c_int]
        self._dll.getMinimumOrderGroupDelayError.restype = c_int

        self._dll.setMinimumOrderGroupDelayCutoff.argtype = c_char_p
        self._dll.setMinimumOrderGroupDelayCutoff.restype = c_int
        self._dll.getMinimumOrderGroupDelayCutoff.argtypes = [c_char_p, c_int]
        self._dll.getMinimumOrderGroupDelayCutoff.restype = c_int

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

        self._dll.setDelayTime.argtype = c_char_p
        self._dll.setDelayTime.restype = c_int
        self._dll.getDelayTime.argtypes = [c_char_p, c_int]
        self._dll.getDelayTime.restype = c_int

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

        self._dll.setEquirippleDelayEnabled.argtype = c_bool
        self._dll.setEquirippleDelayEnabled.restype = c_int
        self._dll.getEquirippleDelayEnabled.argtype = POINTER(c_bool)
        self._dll.getEquirippleDelayEnabled.restype = c_int

        self._dll.setRootRaisedCosineEnabled.argtype = c_bool
        self._dll.setRootRaisedCosineEnabled.restype = c_int
        self._dll.getRootRaisedCosineEnabled.argtype = POINTER(c_bool)
        self._dll.getRootRaisedCosineEnabled.restype = c_int

        self._dll.setDataTransmissionEnabled.argtype = c_bool
        self._dll.setDataTransmissionEnabled.restype = c_int
        self._dll.getDataTransmissionEnabled.argtype = POINTER(c_bool)
        self._dll.getDataTransmissionEnabled.restype = c_int

        self._dll.setRaisedCosineAlphaPercentage.argtype = c_int
        self._dll.setRaisedCosineAlphaPercentage.restype = c_int
        self._dll.getRaisedCosineAlphaPercentage.argtype = POINTER(c_int)
        self._dll.getRaisedCosineAlphaPercentage.restype = c_int

        self._dll.setDelayRipplePeriod.argtype = c_char_p
        self._dll.setDelayRipplePeriod.restype = c_int
        self._dll.getDelayRipplePeriod.argtypes = [c_char_p, c_int]
        self._dll.getDelayRipplePeriod.restype = c_int

        self._dll.setGroupDelayRipplePercentage.argtype = c_int
        self._dll.setGroupDelayRipplePercentage.restype = c_int
        self._dll.getGroupDelayRipplePercentage.argtype = POINTER(c_int)
        self._dll.getGroupDelayRipplePercentage.restype = c_int

        self._dll.setCutoffAttenuationdB.argtype = c_char_p
        self._dll.setCutoffAttenuationdB.restype = c_int
        self._dll.getCutoffAttenuationdB.argtypes = [c_char_p, c_int]
        self._dll.getCutoffAttenuationdB.restype = c_int

        self._dll.setBesselNormalizedDelayEnabled.argtype = c_bool
        self._dll.setBesselNormalizedDelayEnabled.restype = c_int
        self._dll.getBesselNormalizedDelayEnabled.argtype = POINTER(c_bool)
        self._dll.getBesselNormalizedDelayEnabled.restype = c_int

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
        """Type (mathematical formulation) of the filter. The default is ``BUTTERWORTH``.

        The ``FilterType`` enum provides a list of all types.

        Returns
        -------
        :enum:`FilterType`
        """
        type_string = self._dll_interface.get_string(self._dll.getFilterType)
        return self._dll_interface.string_to_enum(FilterType, type_string)

    @filter_type.setter
    def filter_type(self, filter_type: FilterType):
        if not isinstance(filter_type, str):
            string_value = self._dll_interface.enum_to_string(filter_type)
        else:
            string_value = filter_type
        self._dll_interface.set_string(self._dll.setFilterType, string_value)

    @property
    def filter_class(self) -> FilterClass:
        """Class (band definition) of the filter. The default is ``LOW_PASS``.

        The ``FilterClass`` enum provides a list of all classes.

        Returns
        -------
        :enum:`FilterClass`
        """
        type_string = self._dll_interface.get_string(self._dll.getFilterClass)
        return self._dll_interface.string_to_enum(FilterClass, type_string)

    @filter_class.setter
    def filter_class(self, filter_class: FilterClass):
        if not isinstance(filter_class, str):
            string_value = self._dll_interface.enum_to_string(filter_class)
        else:
            string_value = filter_class
        self._dll_interface.set_string(self._dll.setFilterClass, string_value)

    @property
    def diplexer_type(self) -> DiplexerType:
        """Type of diplexer topology. This property is only applicable to lumped filters.

        - The default is ``HI_LO`` for the ``DIPLEXER_1`` filter class.

        - The default is ``BP_BS`` for the ``DIPLEXER_2`` filter class.

        The ``DiplexerType`` enum provides a full list of diplexer types.

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
        """Flag indicating if the multiple bands table is enabled.

        Returns
        -------
        bool
        """
        filter_multiple_bands_enabled = c_bool()
        status = self._dll.getMultipleBandsEnabled(byref(filter_multiple_bands_enabled))
        self._dll_interface.raise_error(status)
        return bool(filter_multiple_bands_enabled.value)

    @filter_multiple_bands_enabled.setter
    def filter_multiple_bands_enabled(self, filter_multiple_bands_enabled: bool):
        status = self._dll.setMultipleBandsEnabled(filter_multiple_bands_enabled)
        self._dll_interface.raise_error(status)

    @property
    def filter_multiple_bands_low_pass_frequency(self) -> str:
        """Multiple bands low-pass frequency of combined low-pass and band-pass filters. The default is ``1GHz``.

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
        """Multiple bands high-pass frequency of combined high-pass and band-pass filters. The default is ``1GHz``.

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
    def filter_order(self) -> int:
        """Order of the filter. The default is ``5``.

        Returns
        -------
        int
        """
        order = c_int()
        status = self._dll.getOrder(byref(order))
        self._dll_interface.raise_error(status)
        return int(order.value)

    @filter_order.setter
    def filter_order(self, filter_order: int):
        status = self._dll.setOrder(filter_order)
        self._dll_interface.raise_error(status)

    @property
    def minimum_order_stop_band_attenuation_db(self) -> str:
        """Filter stop band attenuation in dB for calculation of the filter minimum order.

        The default is ``50``.

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

        The default is ``10 GHz``.

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
    def minimum_order_group_delay_error_percent(self) -> str:
        """Filter maximum group delay in % for calculation of the filter minimum order.

        The default is ``5``.

        Returns
        -------
        str
        """
        minimum_order_group_delay_error_percent_string = self._dll_interface.get_string(
            self._dll.getMinimumOrderGroupDelayError
        )
        return minimum_order_group_delay_error_percent_string

    @minimum_order_group_delay_error_percent.setter
    def minimum_order_group_delay_error_percent(self, minimum_order_group_delay_error_percent):
        self._dll_interface.set_string(
            self._dll.setMinimumOrderGroupDelayError,
            minimum_order_group_delay_error_percent,
        )

    @property
    def minimum_order_group_delay_cutoff(self) -> str:
        """Filter group delay cutoff frequency for calculation of the filter minimum order.

        The default is ``10 GHz``.

        Returns
        -------
        str
        """
        minimum_order_group_delay_cutoff_string = self._dll_interface.get_string(
            self._dll.getMinimumOrderGroupDelayCutoff
        )
        return minimum_order_group_delay_cutoff_string

    @minimum_order_group_delay_cutoff.setter
    def minimum_order_group_delay_cutoff(self, minimum_order_group_delay_cutoff_string):
        self._dll_interface.set_string(
            self._dll.setMinimumOrderGroupDelayCutoff,
            minimum_order_group_delay_cutoff_string,
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
        self._dll_interface.raise_error(status)
        return int(minimum_order.value)

    @property
    def delay_time(self) -> str:
        """Filter delay time.

        The default is ``1 ns``.

        Returns
        -------
        str
        """
        delay_time_string = self._dll_interface.get_string(self._dll.getDelayTime)
        return delay_time_string

    @delay_time.setter
    def delay_time(self, delay_time_string):
        self._dll_interface.set_string(self._dll.setDelayTime, delay_time_string)

    @property
    def pass_band_definition(self) -> PassbandDefinition:
        """Pass band frequency entry options.

        The default is ``CENTER_FREQUENCY``.

        Returns
        -------
        :enum:`PassbandDefinition`
        """
        index = c_int()
        pass_band_definition = list(PassbandDefinition)
        status = self._dll.getPassbandDef(byref(index))
        self._dll_interface.raise_error(status)
        pass_band_definition = pass_band_definition[index.value]
        return pass_band_definition

    @pass_band_definition.setter
    def pass_band_definition(self, column: PassbandDefinition):
        status = self._dll.setPassbandDef(column.value)
        self._dll_interface.raise_error(status)

    @property
    def pass_band_center_frequency(self) -> str:
        """Filter pass band or center frequency.

        The default is ``1 GHz``.

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
        The default is ``200 MHz``.

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

        The default is ``905 MHz``.

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

        The default is ``1.105 MHz``.

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
    def diplexer_inner_band_width(self) -> str:
        """Diplexer inner band width for ``BP1`` and ``Triplexer1`` diplexer types.

        The default is ``200 MHz``.

        Returns
        -------
        str
        """
        diplexer_inner_band_width_string = self._dll_interface.get_string(self._dll.getDiplexerInnerPassbandWidth)
        return diplexer_inner_band_width_string

    @diplexer_inner_band_width.setter
    def diplexer_inner_band_width(self, diplexer_inner_band_width_string):
        self._dll_interface.set_string(self._dll.setDiplexerInnerPassbandWidth, diplexer_inner_band_width_string)

    @property
    def diplexer_outer_band_width(self) -> str:
        """Diplexer outer band width for ``BP1`` and ``Triplexer1`` diplexer types.

        The default is ``2 GHz``.

        Returns
        -------
        str
        """
        diplexer_outer_band_width_string = self._dll_interface.get_string(self._dll.getDiplexerOuterPassbandWidth)
        return diplexer_outer_band_width_string

    @diplexer_outer_band_width.setter
    def diplexer_outer_band_width(self, diplexer_outer_band_width_string):
        self._dll_interface.set_string(self._dll.setDiplexerOuterPassbandWidth, diplexer_outer_band_width_string)

    @property
    def diplexer_lower_center_frequency(self) -> str:
        """Diplexer lower center frequency for ``BP2`` and ``Triplexer2`` diplexer types.

        The default is ``500 MHz``.

        Returns
        -------
        str
        """
        diplexer_lower_center_frequency_string = self._dll_interface.get_string(
            self._dll.getDiplexerLowerCenterFrequency
        )
        return diplexer_lower_center_frequency_string

    @diplexer_lower_center_frequency.setter
    def diplexer_lower_center_frequency(self, diplexer_lower_center_frequency_string):
        self._dll_interface.set_string(
            self._dll.setDiplexerLowerCenterFrequency, diplexer_lower_center_frequency_string
        )

    @property
    def diplexer_upper_center_frequency(self) -> str:
        """Diplexer upper center frequency for ``BP2`` and ``Triplexer2`` diplexer types.

        The default is ``2 GHz``.

        Returns
        -------
        str
        """
        diplexer_upper_center_frequency_string = self._dll_interface.get_string(
            self._dll.getDiplexerUpperCenterFrequency
        )
        return diplexer_upper_center_frequency_string

    @diplexer_upper_center_frequency.setter
    def diplexer_upper_center_frequency(self, diplexer_upper_center_frequency_string):
        self._dll_interface.set_string(
            self._dll.setDiplexerUpperCenterFrequency, diplexer_upper_center_frequency_string
        )

    @property
    def diplexer_lower_band_width(self) -> str:
        """Diplexer lower band width for ``BP2`` and ``Triplexer2`` diplexer types.

        The default is ``500 MHz``.

        Returns
        -------
        str
        """
        diplexer_lower_band_width_string = self._dll_interface.get_string(self._dll.getDiplexerLowerBandwidth)
        return diplexer_lower_band_width_string

    @diplexer_lower_band_width.setter
    def diplexer_lower_band_width(self, diplexer_lower_band_width_string):
        self._dll_interface.set_string(self._dll.setDiplexerLowerBandwidth, diplexer_lower_band_width_string)

    @property
    def diplexer_upper_band_width(self) -> str:
        """Diplexer upper band width for ``BP2`` and ``Triplexer2`` diplexer types.

        The default is ``2 GHz``.

        Returns
        -------
        str
        """
        diplexer_upper_band_width_string = self._dll_interface.get_string(self._dll.getDiplexerUpperBandwidth)
        return diplexer_upper_band_width_string

    @diplexer_upper_band_width.setter
    def diplexer_upper_band_width(self, diplexer_upper_band_width_string):
        self._dll_interface.set_string(self._dll.setDiplexerUpperBandwidth, diplexer_upper_band_width_string)

    @property
    def stop_band_definition(self) -> StopbandDefinition:
        """Stop band parameter entry option.

        The default is ``RATIO``.

        Returns
        -------
        :enum:`StopbandDefinition`
        """
        index = c_int()
        stop_band_definition = list(StopbandDefinition)
        status = self._dll.getStopbandDef(byref(index))
        self._dll_interface.raise_error(status)
        stop_band_definition = stop_band_definition[index.value]
        return stop_band_definition

    @stop_band_definition.setter
    def stop_band_definition(self, column: StopbandDefinition):
        status = self._dll.setStopbandDef(column.value)
        self._dll_interface.raise_error(status)

    @property
    def stop_band_ratio(self) -> str:
        """Filter stop band ratio.

        The default is ``1.2``.

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

        The default is ``1.2 GHz``.

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

        The default is ``60 dB``.

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
        """Flag indicating if the standard cut is enabled.

        Returns
        -------
        bool
        """
        standard_pass_band_attenuation = c_bool()
        status = self._dll.getStandardCutoffEnabled(byref(standard_pass_band_attenuation))
        self._dll_interface.raise_error(status)
        return bool(standard_pass_band_attenuation.value)

    @standard_pass_band_attenuation.setter
    def standard_pass_band_attenuation(self, standard_pass_band_attenuation: bool):
        status = self._dll.setStandardCutoffEnabled(standard_pass_band_attenuation)
        self._dll_interface.raise_error(status)

    @property
    def root_raised_cosine(self) -> bool:
        """Flag indicating if the root raised cosine is enabled.

        Returns
        -------
        bool
        """
        root_raised_cosine = c_bool()
        status = self._dll.getRootRaisedCosineEnabled(byref(root_raised_cosine))
        self._dll_interface.raise_error(status)
        return bool(root_raised_cosine.value)

    @root_raised_cosine.setter
    def root_raised_cosine(self, root_raised_cosine: bool):
        status = self._dll.setRootRaisedCosineEnabled(root_raised_cosine)
        self._dll_interface.raise_error(status)

    @property
    def data_transmission_filter(self) -> bool:
        """Flag indicating if the data transmission filter is enabled.

        Returns
        -------
        bool
        """
        data_transmission_filter = c_bool()
        status = self._dll.getDataTransmissionEnabled(byref(data_transmission_filter))
        self._dll_interface.raise_error(status)
        return bool(data_transmission_filter.value)

    @data_transmission_filter.setter
    def data_transmission_filter(self, data_transmission_filter: bool):
        status = self._dll.setDataTransmissionEnabled(data_transmission_filter)
        self._dll_interface.raise_error(status)

    @property
    def raised_cosine_alpha_percentage(self) -> RaisedCosineAlphaPercentage:
        """Raised cosine alpha percentage.

        The default is ''FORTY''.

        Returns
        -------
        :enum:`RaisedCosineAlphaPercentage`
        """
        index = c_int()
        raised_cosine_alpha_percentage = list(RaisedCosineAlphaPercentage)
        status = self._dll.getRaisedCosineAlphaPercentage(byref(index))
        self._dll_interface.raise_error(status)
        raised_cosine_alpha_percentage = raised_cosine_alpha_percentage[index.value]
        return raised_cosine_alpha_percentage

    @raised_cosine_alpha_percentage.setter
    def raised_cosine_alpha_percentage(self, column: RaisedCosineAlphaPercentage):
        status = self._dll.setRaisedCosineAlphaPercentage(column.value)
        self._dll_interface.raise_error(status)

    @property
    def equiripple_delay_enabled(self) -> bool:
        """Flag indicating if the equiripple delay is enabled.

        Returns
        -------
        bool
        """
        equiripple_delay_enabled = c_bool()
        status = self._dll.getEquirippleDelayEnabled(byref(equiripple_delay_enabled))
        self._dll_interface.raise_error(status)
        return bool(equiripple_delay_enabled.value)

    @equiripple_delay_enabled.setter
    def equiripple_delay_enabled(self, equiripple_delay_enabled: bool):
        status = self._dll.setEquirippleDelayEnabled(equiripple_delay_enabled)
        self._dll_interface.raise_error(status)

    @property
    def group_delay_ripple_period(self) -> str:
        """Filter approximate normalized group delay ripple period.

        The default is ''2''.

        Returns
        -------
        str
        """
        group_delay_ripple_period_string = self._dll_interface.get_string(self._dll.getDelayRipplePeriod)
        return group_delay_ripple_period_string

    @group_delay_ripple_period.setter
    def group_delay_ripple_period(self, group_delay_ripple_period_string):
        self._dll_interface.set_string(
            self._dll.setDelayRipplePeriod,
            group_delay_ripple_period_string,
        )

    @property
    def normalized_group_delay_percentage(self) -> int:
        """Normalized group delay percentage.

        The default is ''0''.

        Returns
        -------
        int
        """
        index = c_int()
        normalized_group_delay_percentage = list(BesselRipplePercentage)
        status = self._dll.getGroupDelayRipplePercentage(byref(index))
        self._dll_interface.raise_error(status)
        normalized_group_delay_percentage_string = normalized_group_delay_percentage[index.value]
        return normalized_group_delay_percentage_string

    @normalized_group_delay_percentage.setter
    def normalized_group_delay_percentage(self, column: BesselRipplePercentage):
        status = self._dll.setGroupDelayRipplePercentage(column.value)
        self._dll_interface.raise_error(status)

    @property
    def standard_pass_band_attenuation_value_db(self) -> str:
        """Filter cut off attenuation in dB.

        The default is ''3.01 dB''.

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
    def bessel_normalized_delay_enabled(self) -> bool:
        """Flag indicating if the normalized delay is enabled.

        Returns
        -------
        bool
        """
        bessel_normalized_delay_enabled = c_bool()
        status = self._dll.getBesselNormalizedDelayEnabled(byref(bessel_normalized_delay_enabled))
        self._dll_interface.raise_error(status)
        return bool(bessel_normalized_delay_enabled.value)

    @bessel_normalized_delay_enabled.setter
    def bessel_normalized_delay_enabled(self, bessel_normalized_delay_enabled: bool):
        status = self._dll.setBesselNormalizedDelayEnabled(bessel_normalized_delay_enabled)
        self._dll_interface.raise_error(status)

    @property
    def bessel_normalized_delay_period(self) -> str:
        """Bessel filter normalized delay period.

        The default is ''2''.

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

        The default is ''0''.

        Returns
        -------
        int
        """
        index = c_int()
        bessel_normalized_delay_percentage = list(BesselRipplePercentage)
        status = self._dll.getBesselRipplePercentage(byref(index))
        self._dll_interface.raise_error(status)
        bessel_normalized_delay_percentage_string = bessel_normalized_delay_percentage[index.value]
        return bessel_normalized_delay_percentage_string

    @bessel_normalized_delay_percentage.setter
    def bessel_normalized_delay_percentage(self, column: BesselRipplePercentage):
        status = self._dll.setBesselRipplePercentage(column.value)
        self._dll_interface.raise_error(status)

    @property
    def pass_band_ripple(self) -> str:
        """Filter pass band ripple in dB.

        The default is ''0.05 dB''.

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
        """Flag indicating if the arithmetic symmetry is enabled.

        Returns
        -------
        bool
        """
        arith_symmetry = c_bool()
        status = self._dll.getArithSymmetry(byref(arith_symmetry))
        self._dll_interface.raise_error(status)
        return bool(arith_symmetry.value)

    @arith_symmetry.setter
    def arith_symmetry(self, arith_symmetry: bool):
        status = self._dll.setArithSymmetry(arith_symmetry)
        self._dll_interface.raise_error(status)

    @property
    def asymmetric(self) -> bool:
        """Flag indicating if the asymmetric is enabled.

        Returns
        -------
        bool
        """
        asymmetric = c_bool()
        status = self._dll.getAsymmetric(byref(asymmetric))
        self._dll_interface.raise_error(status)
        return bool(asymmetric.value)

    @asymmetric.setter
    def asymmetric(self, asymmetric: bool):
        status = self._dll.setAsymmetric(asymmetric)
        self._dll_interface.raise_error(status)

    @property
    def asymmetric_low_order(self) -> int:
        """Order for low side of an asymmetric filter.

        The default is ''5''.

        Returns
        -------
        int
        """
        asymmetric_low_order = c_int()
        status = self._dll.getAsymmetricLowOrder(byref(asymmetric_low_order))
        self._dll_interface.raise_error(status)
        return int(asymmetric_low_order.value)

    @asymmetric_low_order.setter
    def asymmetric_low_order(self, asymmetric_low_order: int):
        status = self._dll.setAsymmetricLowOrder(asymmetric_low_order)
        self._dll_interface.raise_error(status)

    @property
    def asymmetric_high_order(self) -> int:
        """Order for high side of an asymmetric filter.

        The default is ''5''.

        Returns
        -------
        int
        """
        asymmetric_high_order = c_int()
        status = self._dll.getAsymmetricHighOrder(byref(asymmetric_high_order))
        self._dll_interface.raise_error(status)
        return int(asymmetric_high_order.value)

    @asymmetric_high_order.setter
    def asymmetric_high_order(self, asymmetric_high_order: int):
        status = self._dll.setAsymmetricHighOrder(asymmetric_high_order)
        self._dll_interface.raise_error(status)

    @property
    def asymmetric_low_stop_band_ratio(self) -> str:
        """Stop-band ratio for low side of an asymmetric filter.

        The default is ''1.2''.

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
        """Stop-band ratio for high side of an asymmetric filter.

        The default is ''1.2''.

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
        """Stop-band attenuation for low side of an asymmetric filter.

        The default is ''60 dB''.

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
        """Stop-band attenuation for high side of an asymmetric filter.

        The default is ''60 dB''.

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

        The default is ''TRANSITION_NONE''.

        Returns
        -------
        :enum:`GaussianTransition`
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
        The default is ''OPTION_1''.

        Returns
        -------
        :enum:`GaussianBesselReflection`
        """
        index = c_int()
        gaussian_bessel_reflection = list(GaussianBesselReflection)
        status = self._dll.getGaussianBesselReflection(byref(index))
        self._dll_interface.raise_error(status)
        gaussian_bessel_reflection = gaussian_bessel_reflection[index.value]
        return gaussian_bessel_reflection

    @gaussian_bessel_reflection.setter
    def gaussian_bessel_reflection(self, column: GaussianBesselReflection):
        status = self._dll.setGaussianBesselReflection(column.value)
        self._dll_interface.raise_error(status)

    @property
    def even_order(self) -> bool:
        """Flag indicating if the even order mode for a filter with even orders is enabled.

        Returns
        -------
        bool
        """
        even_order = c_bool()
        status = self._dll.getEvenOrderMode(byref(even_order))
        self._dll_interface.raise_error(status)
        return bool(even_order.value)

    @even_order.setter
    def even_order(self, even_order: bool):
        status = self._dll.setEvenOrderMode(even_order)
        self._dll_interface.raise_error(status)

    @property
    def even_order_refl_zero(self) -> bool:
        """Flag indicating if the even order reflection zeros translation to 0 is enabled.

        Returns
        -------
        bool
        """
        even_order_refl_zero = c_bool()
        status = self._dll.getEvenReflZeroTo0(byref(even_order_refl_zero))
        self._dll_interface.raise_error(status)
        return bool(even_order_refl_zero.value)

    @even_order_refl_zero.setter
    def even_order_refl_zero(self, even_order_refl_zero: bool):
        status = self._dll.setEvenReflZeroTo0(even_order_refl_zero)
        self._dll_interface.raise_error(status)

    @property
    def even_order_trn_zero(self) -> bool:
        """Flag indicating if the even order reflection zeros translation to infinite is enabled.

        Returns
        -------
        bool
        """
        even_order_trn_zero = c_bool()
        status = self._dll.getEvenTrnZeroToInf(byref(even_order_trn_zero))
        self._dll_interface.raise_error(status)
        return bool(even_order_trn_zero.value)

    @even_order_trn_zero.setter
    def even_order_trn_zero(self, even_order_trn_zero: bool):
        status = self._dll.setEvenTrnZeroToInf(even_order_trn_zero)
        self._dll_interface.raise_error(status)

    @property
    def constrict_ripple(self) -> bool:
        """Flag indicating if the equiripple constriction is enabled.

        Returns
        -------
        bool
        """
        constrict_ripple = c_bool()
        status = self._dll.getConstrictRipple(byref(constrict_ripple))
        self._dll_interface.raise_error(status)
        return bool(constrict_ripple.value)

    @constrict_ripple.setter
    def constrict_ripple(self, constrict_ripple: bool):
        status = self._dll.setConstrictRipple(constrict_ripple)
        self._dll_interface.raise_error(status)

    @property
    def single_point_ripple(self) -> bool:
        """Flag indicating if the ripple confinement to a single frequency point is enabled.

        Returns
        -------
        bool
        """
        single_point_ripple = c_bool()
        status = self._dll.getSinglePointRipple(byref(single_point_ripple))
        self._dll_interface.raise_error(status)
        return bool(single_point_ripple.value)

    @single_point_ripple.setter
    def single_point_ripple(self, single_point_ripple: bool):
        status = self._dll.setSinglePointRipple(single_point_ripple)
        self._dll_interface.raise_error(status)

    @property
    def half_band_ripple(self) -> bool:
        """Flag indicating if the ripple with half of the zeros in the given band is enabled.

        Returns
        -------
        bool
        """
        half_band_point_ripple = c_bool()
        status = self._dll.getHalfBandRipple(byref(half_band_point_ripple))
        self._dll_interface.raise_error(status)
        return bool(half_band_point_ripple.value)

    @half_band_ripple.setter
    def half_band_ripple(self, half_band_ripple: bool):
        status = self._dll.setHalfBandRipple(half_band_ripple)
        self._dll_interface.raise_error(status)

    @property
    def constrict_ripple_percent(self) -> str:
        """Filter ripple constriction percentage.

        The default is ''50%''.

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

        The default is ''STOP''.

        Returns
        -------
        :enum:`RippleConstrictionBandSelect`
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

        The default is ''RIPPLE_INF_ZEROS_1''.

        Returns
        -------
        :enum:`SinglePointRippleInfZeros`
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
        """Flag indicating if the delay equalizer is enabled.

        Returns
        -------
        bool
        """
        delay_equalizer = c_bool()
        status = self._dll.getDelayEqualizer(byref(delay_equalizer))
        self._dll_interface.raise_error(status)
        return bool(delay_equalizer.value)

    @delay_equalizer.setter
    def delay_equalizer(self, delay_equalizer: bool):
        status = self._dll.setDelayEqualizer(delay_equalizer)
        self._dll_interface.raise_error(status)

    @property
    def delay_equalizer_order(self) -> int:
        """Filter delay equalizer order.

        The default is ''2''.

        Returns
        -------
        int
        """
        delay_equalizer_order = c_int()
        status = self._dll.getDelayEqualizerOrder(byref(delay_equalizer_order))
        self._dll_interface.raise_error(status)
        return int(delay_equalizer_order.value)

    @delay_equalizer_order.setter
    def delay_equalizer_order(self, delay_equalizer_order: int):
        status = self._dll.setDelayEqualizerOrder(delay_equalizer_order)
        self._dll_interface.raise_error(status)

    @property
    def standard_delay_equ_pass_band_attenuation(self) -> bool:
        """Flag indicating if the standard delay equalizer attenuation is enabled.

        Returns
        -------
        bool
        """
        standard_delay_equ_cut = c_bool()
        status = self._dll.getStandardDelayEquCut(byref(standard_delay_equ_cut))
        self._dll_interface.raise_error(status)
        return bool(standard_delay_equ_cut.value)

    @standard_delay_equ_pass_band_attenuation.setter
    def standard_delay_equ_pass_band_attenuation(self, standard_delay_equ_pass_band_attenuation: bool):
        status = self._dll.setStandardDelayEquCut(standard_delay_equ_pass_band_attenuation)
        self._dll_interface.raise_error(status)

    @property
    def standard_delay_equ_pass_band_attenuation_value_db(self) -> str:
        """Filter standard delay equalizer cut off attenuation in dB.

        The default is ''3.01 dB''.

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
