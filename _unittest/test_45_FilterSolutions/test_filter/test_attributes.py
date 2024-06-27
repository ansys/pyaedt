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

from _unittest.conftest import config
import pytest

import pyaedt
from pyaedt.filtersolutions_core.attributes import BesselRipplePercentage
from pyaedt.filtersolutions_core.attributes import DiplexerType
from pyaedt.filtersolutions_core.attributes import FilterClass
from pyaedt.filtersolutions_core.attributes import FilterImplementation
from pyaedt.filtersolutions_core.attributes import FilterType
from pyaedt.filtersolutions_core.attributes import GaussianBesselReflection
from pyaedt.filtersolutions_core.attributes import GaussianTransition
from pyaedt.filtersolutions_core.attributes import PassbandDefinition
from pyaedt.filtersolutions_core.attributes import RippleConstrictionBandSelect
from pyaedt.filtersolutions_core.attributes import SinglePointRippleInfZeros
from pyaedt.filtersolutions_core.attributes import StopbandDefinition
from pyaedt.generic.general_methods import is_linux


@pytest.mark.skipif(is_linux, reason="FilterSolutions API is not supported on Linux.")
@pytest.mark.skipif(config["desktopVersion"] <= "2025.1", reason="Skipped on versions earlier than 2025.1")
class TestClass:
    def test_filter_type(self):
        design = pyaedt.FilterSolutions(implementation_type=FilterImplementation.LUMPED)
        assert design.attributes.filter_type == FilterType.BUTTERWORTH

        assert len(FilterType) == 9

        for fimp in [FilterImplementation.LUMPED]:
            design.attributes.filter_implementation = fimp
            for ftype in FilterType:
                design.attributes.filter_type = ftype
                assert design.attributes.filter_type == ftype

    def test_filter_class(self):
        design = pyaedt.FilterSolutions(implementation_type=FilterImplementation.LUMPED)
        assert design.attributes.filter_class == FilterClass.LOW_PASS

        # Only lumped supports all classes
        # TODO: Confirm proper exceptions are raised when setting unsupported filter class for each implementation.

        assert len(FilterClass) == 10
        for index, fclass in enumerate(FilterClass):
            if index > 5:
                design.attributes.filter_multiple_bands_enabled = True
            design.attributes.filter_class = fclass
            assert design.attributes.filter_class == fclass

    def test_filter_multiple_bands_enabled(self):
        design = pyaedt.FilterSolutions(implementation_type=FilterImplementation.LUMPED)
        assert design.attributes.filter_multiple_bands_enabled is False
        design.attributes.filter_multiple_bands_enabled = True
        assert design.attributes.filter_multiple_bands_enabled

    def test_filter_multiple_bands_low_pass_frequency(self):
        design = pyaedt.FilterSolutions(implementation_type=FilterImplementation.LUMPED)
        design.attributes.filter_multiple_bands_enabled = True
        design.attributes.filter_class = FilterClass.LOW_BAND
        assert design.attributes.filter_multiple_bands_low_pass_frequency == "1G"
        design.attributes.filter_multiple_bands_low_pass_frequency = "500M"
        assert design.attributes.filter_multiple_bands_low_pass_frequency == "500M"

    def test_filter_multiple_bands_high_pass_frequency(self):
        design = pyaedt.FilterSolutions(implementation_type=FilterImplementation.LUMPED)
        design.attributes.filter_multiple_bands_enabled = True
        design.attributes.filter_class = FilterClass.BAND_HIGH
        assert design.attributes.filter_multiple_bands_high_pass_frequency == "1G"
        design.attributes.filter_multiple_bands_high_pass_frequency = "500M"
        assert design.attributes.filter_multiple_bands_high_pass_frequency == "500M"

    def test_filter_implementation(self):
        design = pyaedt.FilterSolutions(implementation_type=FilterImplementation.LUMPED)
        assert len(FilterImplementation) == 5
        for fimplementation in FilterImplementation:
            design.attributes.filter_implementation = fimplementation
            assert design.attributes.filter_implementation == fimplementation

    def test_diplexer_type(self):
        design = pyaedt.FilterSolutions(implementation_type=FilterImplementation.LUMPED)
        assert len(DiplexerType) == 6
        for index, diplexer_type in enumerate(DiplexerType):
            if index < 3:
                design.attributes.filter_class = FilterClass.DIPLEXER_1
            elif index > 2:
                design.attributes.filter_class = FilterClass.DIPLEXER_2
            design.attributes.diplexer_type = diplexer_type
            assert design.attributes.diplexer_type == diplexer_type

    def test_order(self):
        design = pyaedt.FilterSolutions(implementation_type=FilterImplementation.LUMPED)
        assert design.attributes.order == 5

        with pytest.raises(RuntimeError) as info:
            design.attributes.order = 0
        assert info.value.args[0] == "The minimum order is 1"

        for i in range(1, 22):
            design.attributes.order = i
            assert design.attributes.order == i

        with pytest.raises(RuntimeError) as info:
            design.attributes.order = 22
        assert info.value.args[0] == "The maximum order is 21"

    def test_minimum_order_stop_band_att(self):
        design = pyaedt.FilterSolutions(implementation_type=FilterImplementation.LUMPED)
        assert design.attributes.minimum_order_stop_band_attenuation_db == "60 dB"
        design.attributes.minimum_order_stop_band_attenuation_db = "40 dB"
        assert design.attributes.minimum_order_stop_band_attenuation_db == "40 dB"

    def test_minimum_order_stop_band_freq(self):
        design = pyaedt.FilterSolutions(implementation_type=FilterImplementation.LUMPED)
        assert design.attributes.minimum_order_stop_band_frequency == "10 GHz"
        design.attributes.minimum_order_stop_band_frequency = "500 MHz"
        assert design.attributes.minimum_order_stop_band_frequency == "500 MHz"

    def test_minimum_order_group_delay_error_percent(self):
        design = pyaedt.FilterSolutions(implementation_type=FilterImplementation.LUMPED)
        design.attributes.filter_type = FilterType.DELAY
        assert design.attributes.minimum_order_group_delay_error_percent == "5"
        design.attributes.minimum_order_group_delay_error_percent = "7"
        assert design.attributes.minimum_order_group_delay_error_percent == "7"

    def test_minimum_order_group_delay_cutoff(self):
        design = pyaedt.FilterSolutions(implementation_type=FilterImplementation.LUMPED)
        design.attributes.filter_type = FilterType.DELAY
        assert design.attributes.minimum_order_group_delay_cutoff == "2 GHz"
        design.attributes.minimum_order_group_delay_cutoff = "500 MHz"
        assert design.attributes.minimum_order_group_delay_cutoff == "500 MHz"

    def test_minimum_order_stop_band_freq(self):
        design = pyaedt.FilterSolutions(implementation_type=FilterImplementation.LUMPED)
        assert design.attributes.minimum_order_stop_band_frequency == "10 GHz"
        design.attributes.minimum_order_stop_band_frequency = "500 MHz"
        assert design.attributes.minimum_order_stop_band_frequency == "500 MHz"

    def test_minimum_order(self):
        design = pyaedt.FilterSolutions(implementation_type=FilterImplementation.LUMPED)
        assert design.attributes.order == 5
        design.attributes.ideal_minimum_order
        assert design.attributes.order == 3

    def test_pass_band_definition(self):
        design = pyaedt.FilterSolutions(implementation_type=FilterImplementation.LUMPED)
        design.attributes.filter_class = FilterClass.BAND_PASS
        assert len(PassbandDefinition) == 2
        assert design.attributes.pass_band_definition == PassbandDefinition.CENTER_FREQUENCY
        for pbd in PassbandDefinition:
            design.attributes.pass_band_definition = pbd
            assert design.attributes.pass_band_definition == pbd

    def test_pass_band_center_frequency(self):
        design = pyaedt.FilterSolutions(implementation_type=FilterImplementation.LUMPED)
        assert design.attributes.pass_band_center_frequency == "1G"
        design.attributes.pass_band_center_frequency = "500M"
        assert design.attributes.pass_band_center_frequency == "500M"

    def test_pass_band_frequency(self):
        design = pyaedt.FilterSolutions(implementation_type=FilterImplementation.LUMPED)
        design.attributes.filter_class = FilterClass.BAND_PASS
        assert design.attributes.pass_band_width_frequency == "200M"
        design.attributes.pass_band_width_frequency = "500M"
        assert design.attributes.pass_band_width_frequency == "500M"

    def test_lower_frequency(self):
        design = pyaedt.FilterSolutions(implementation_type=FilterImplementation.LUMPED)
        design.attributes.filter_class = FilterClass.BAND_PASS
        design.attributes.pass_band_definition = PassbandDefinition.CORNER_FREQUENCIES
        assert design.attributes.lower_frequency == "905 M"
        design.attributes.lower_frequency = "800M"
        assert design.attributes.lower_frequency == "800M"

    def test_upper_frequency(self):
        design = pyaedt.FilterSolutions(implementation_type=FilterImplementation.LUMPED)
        design.attributes.filter_class = FilterClass.BAND_PASS
        design.attributes.pass_band_definition = PassbandDefinition.CORNER_FREQUENCIES
        assert design.attributes.upper_frequency == "1.105 G"
        design.attributes.upper_frequency = "1.2 G"
        assert design.attributes.upper_frequency == "1.2 G"

    def test_stop_band_definition(self):
        design = pyaedt.FilterSolutions(implementation_type=FilterImplementation.LUMPED)
        design.attributes.filter_type = FilterType.ELLIPTIC
        assert len(StopbandDefinition) == 3
        assert design.attributes.stop_band_definition == StopbandDefinition.RATIO
        for sbd in StopbandDefinition:
            design.attributes.stop_band_definition = sbd
            assert design.attributes.stop_band_definition == sbd

    def test_stop_band_ratio(self):
        design = pyaedt.FilterSolutions(implementation_type=FilterImplementation.LUMPED)
        design.attributes.filter_type = FilterType.ELLIPTIC
        assert design.attributes.stop_band_ratio == "1.2"
        design.attributes.stop_band_ratio = "1.5"
        assert design.attributes.stop_band_ratio == "1.5"

    def test_stop_band_frequency(self):
        design = pyaedt.FilterSolutions(implementation_type=FilterImplementation.LUMPED)
        design.attributes.filter_type = FilterType.ELLIPTIC
        design.attributes.stop_band_definition = StopbandDefinition.FREQUENCY
        assert design.attributes.stop_band_frequency == "1.2 G"
        design.attributes.stop_band_frequency = "1.5 G"
        assert design.attributes.stop_band_frequency == "1.5 G"

    def test_stop_band_attenuation(self):
        design = pyaedt.FilterSolutions(implementation_type=FilterImplementation.LUMPED)
        design.attributes.filter_type = FilterType.ELLIPTIC
        design.attributes.stop_band_definition = StopbandDefinition.ATTENUATION_DB
        assert design.attributes.stop_band_attenuation_db == "60"
        design.attributes.stop_band_attenuation_db = "40 dB"
        assert design.attributes.stop_band_attenuation_db == "40"

    def test_standard_pass_band_attenuation(self):
        design = pyaedt.FilterSolutions(implementation_type=FilterImplementation.LUMPED)
        assert design.attributes.standard_pass_band_attenuation
        design.attributes.standard_pass_band_attenuation = False
        assert design.attributes.standard_pass_band_attenuation is False

    def test_standard_pass_band_attenuation_value_db(self):
        design = pyaedt.FilterSolutions(implementation_type=FilterImplementation.LUMPED)
        design.attributes.standard_pass_band_attenuation = False
        assert design.attributes.standard_pass_band_attenuation_value_db == "3.01"
        design.attributes.standard_pass_band_attenuation_value_db = "4"
        assert design.attributes.standard_pass_band_attenuation_value_db == "4"

    def test_equiripple_delay(self):
        design = pyaedt.FilterSolutions(implementation_type=FilterImplementation.LUMPED)
        design.attributes.filter_type = FilterType.DELAY
        assert design.attributes.equiripple_delay
        design.attributes.equiripple_delay = False
        assert design.attributes.equiripple_delay is False

    def test_group_delay_ripple_period(self):
        design = pyaedt.FilterSolutions(implementation_type=FilterImplementation.LUMPED)
        design.attributes.filter_type = FilterType.DELAY
        assert design.attributes.group_delay_ripple_period == "2"
        design.attributes.group_delay_ripple_period = "3"
        assert design.attributes.group_delay_ripple_period == "3"

    def test_normalized_group_delay_percentage(self):
        design = pyaedt.FilterSolutions(implementation_type=FilterImplementation.LUMPED)
        design.attributes.filter_type = FilterType.DELAY
        assert len(BesselRipplePercentage) == 6
        for normalized_group_delay_percentage in BesselRipplePercentage:
            design.attributes.normalized_group_delay_percentage = normalized_group_delay_percentage
            assert design.attributes.normalized_group_delay_percentage == normalized_group_delay_percentage

    def test_bessel_normalized_delay(self):
        design = pyaedt.FilterSolutions(implementation_type=FilterImplementation.LUMPED)
        design.attributes.filter_type = FilterType.BESSEL
        assert design.attributes.bessel_normalized_delay is False
        design.attributes.bessel_normalized_delay = True
        assert design.attributes.bessel_normalized_delay

    def test_bessel_normalized_delay_period(self):
        design = pyaedt.FilterSolutions(implementation_type=FilterImplementation.LUMPED)
        design.attributes.filter_type = FilterType.BESSEL
        design.attributes.bessel_normalized_delay = True
        assert design.attributes.bessel_normalized_delay_period == "2"
        design.attributes.bessel_normalized_delay_period = "3"
        assert design.attributes.bessel_normalized_delay_period == "3"

    def test_bessel_normalized_delay_percentage(self):
        design = pyaedt.FilterSolutions(implementation_type=FilterImplementation.LUMPED)
        design.attributes.filter_type = FilterType.BESSEL
        design.attributes.bessel_normalized_delay = True
        assert len(BesselRipplePercentage) == 6
        for bessel_normalized_delay_percentage in BesselRipplePercentage:
            design.attributes.bessel_normalized_delay_percentage = bessel_normalized_delay_percentage
            assert design.attributes.bessel_normalized_delay_percentage == bessel_normalized_delay_percentage

    def test_pass_band_ripple(self):
        design = pyaedt.FilterSolutions(implementation_type=FilterImplementation.LUMPED)
        design.attributes.filter_type = FilterType.ELLIPTIC
        assert design.attributes.pass_band_ripple == ".05"
        design.attributes.pass_band_ripple = ".03"
        assert design.attributes.pass_band_ripple == ".03"

    def test_arith_symmetry(self):
        design = pyaedt.FilterSolutions(implementation_type=FilterImplementation.LUMPED)
        design.attributes.filter_type = FilterType.ELLIPTIC
        design.attributes.filter_class = FilterClass.BAND_PASS
        assert design.attributes.arith_symmetry is False
        design.attributes.arith_symmetry = True
        assert design.attributes.arith_symmetry

    def test_asymmetric(self):
        design = pyaedt.FilterSolutions(implementation_type=FilterImplementation.LUMPED)
        design.attributes.filter_class = FilterClass.BAND_PASS
        assert design.attributes.asymmetric is False
        design.attributes.asymmetric = True
        assert design.attributes.asymmetric

    def test_asymmetric_low_order(self):
        design = pyaedt.FilterSolutions(implementation_type=FilterImplementation.LUMPED)
        design.attributes.filter_class = FilterClass.BAND_PASS
        design.attributes.asymmetric = True
        assert design.attributes.asymmetric_low_order == 5

        with pytest.raises(RuntimeError) as info:
            design.attributes.asymmetric_low_order = 0
        assert info.value.args[0] == "The minimum order is 1"

        for i in range(1, 22):
            design.attributes.asymmetric_low_order = i
            assert design.attributes.asymmetric_low_order == i

        with pytest.raises(RuntimeError) as info:
            design.attributes.asymmetric_low_order = 22
        assert info.value.args[0] == "The maximum order is 21"

    def test_asymmetric_high_order(self):
        design = pyaedt.FilterSolutions(implementation_type=FilterImplementation.LUMPED)
        design.attributes.filter_class = FilterClass.BAND_PASS
        design.attributes.asymmetric = True
        assert design.attributes.asymmetric_high_order == 5

        with pytest.raises(RuntimeError) as info:
            design.attributes.asymmetric_high_order = 0
        assert info.value.args[0] == "The minimum order is 1"

        for i in range(1, 22):
            design.attributes.asymmetric_high_order = i
            assert design.attributes.asymmetric_high_order == i

        with pytest.raises(RuntimeError) as info:
            design.attributes.asymmetric_high_order = 22
        assert info.value.args[0] == "The maximum order is 21"

    def test_asymmetric_low_stop_band_ratio(self):
        design = pyaedt.FilterSolutions(implementation_type=FilterImplementation.LUMPED)
        design.attributes.filter_class = FilterClass.BAND_PASS
        design.attributes.filter_type = FilterType.ELLIPTIC
        design.attributes.asymmetric = True
        assert design.attributes.asymmetric_low_stop_band_ratio == "1.2"
        design.attributes.asymmetric_low_stop_band_ratio = "1.5"
        assert design.attributes.asymmetric_low_stop_band_ratio == "1.5"

    def test_asymmetric_high_stop_band_ratio(self):
        design = pyaedt.FilterSolutions(implementation_type=FilterImplementation.LUMPED)
        design.attributes.filter_class = FilterClass.BAND_PASS
        design.attributes.filter_type = FilterType.ELLIPTIC
        design.attributes.asymmetric = True
        assert design.attributes.asymmetric_high_stop_band_ratio == "1.2"
        design.attributes.asymmetric_high_stop_band_ratio = "1.5"
        assert design.attributes.asymmetric_high_stop_band_ratio == "1.5"

    def test_asymmetric_low_stop_band_attenuation_db(self):
        design = pyaedt.FilterSolutions(implementation_type=FilterImplementation.LUMPED)
        design.attributes.filter_class = FilterClass.BAND_PASS
        design.attributes.filter_type = FilterType.ELLIPTIC
        design.attributes.asymmetric = True
        assert design.attributes.asymmetric_low_stop_band_attenuation_db == "60"
        design.attributes.asymmetric_low_stop_band_attenuation_db = "40"
        assert design.attributes.asymmetric_low_stop_band_attenuation_db == "40"

    def test_asymmetric_high_stop_band_attenuation_db(self):
        design = pyaedt.FilterSolutions(implementation_type=FilterImplementation.LUMPED)
        design.attributes.filter_class = FilterClass.BAND_PASS
        design.attributes.filter_type = FilterType.ELLIPTIC
        design.attributes.asymmetric = True
        assert design.attributes.asymmetric_high_stop_band_attenuation_db == "60"
        design.attributes.asymmetric_high_stop_band_attenuation_db = "40"
        assert design.attributes.asymmetric_high_stop_band_attenuation_db == "40"

    def test_gaussian_transition(self):
        design = pyaedt.FilterSolutions(implementation_type=FilterImplementation.LUMPED)
        design.attributes.filter_type = FilterType.GAUSSIAN
        assert len(GaussianTransition) == 6
        for gaussian_transition in GaussianTransition:
            design.attributes.gaussian_transition = gaussian_transition
            assert design.attributes.gaussian_transition == gaussian_transition

    def test_gaussian_bessel_reflection(self):
        design = pyaedt.FilterSolutions(implementation_type=FilterImplementation.LUMPED)
        design.attributes.filter_type = FilterType.BESSEL
        assert len(GaussianBesselReflection) == 3
        for gaussian_bessel_reflection in GaussianBesselReflection:
            design.attributes.gaussian_bessel_reflection = gaussian_bessel_reflection
            assert design.attributes.gaussian_bessel_reflection == gaussian_bessel_reflection

    def test_even_order(self):
        design = pyaedt.FilterSolutions(implementation_type=FilterImplementation.LUMPED)
        design.attributes.filter_type = FilterType.ELLIPTIC
        design.attributes.order = 4
        assert design.attributes.even_order
        design.attributes.even_order = False
        assert design.attributes.even_order is False

    def test_even_order_refl_zero(self):
        design = pyaedt.FilterSolutions(implementation_type=FilterImplementation.LUMPED)
        design.attributes.filter_type = FilterType.ELLIPTIC
        design.attributes.order = 4
        assert design.attributes.even_order_refl_zero
        design.attributes.even_order_refl_zero = False
        assert design.attributes.even_order_refl_zero is False

    def test_even_order_trn_zero(self):
        design = pyaedt.FilterSolutions(implementation_type=FilterImplementation.LUMPED)
        design.attributes.filter_type = FilterType.ELLIPTIC
        design.attributes.order = 4
        assert design.attributes.even_order_trn_zero
        design.attributes.even_order_trn_zero = False
        assert design.attributes.even_order_trn_zero is False

    def test_constrict_ripple(self):
        design = pyaedt.FilterSolutions(implementation_type=FilterImplementation.LUMPED)
        design.attributes.filter_type = FilterType.ELLIPTIC
        assert design.attributes.constrict_ripple is False
        design.attributes.constrict_ripple = True
        assert design.attributes.constrict_ripple

    def test_single_point_ripple(self):
        design = pyaedt.FilterSolutions(implementation_type=FilterImplementation.LUMPED)
        design.attributes.filter_type = FilterType.ELLIPTIC
        assert design.attributes.single_point_ripple is False
        design.attributes.single_point_ripple = True
        assert design.attributes.single_point_ripple

    def test_half_band_ripple(self):
        design = pyaedt.FilterSolutions(implementation_type=FilterImplementation.LUMPED)
        design.attributes.filter_type = FilterType.ELLIPTIC
        assert design.attributes.half_band_ripple is False
        design.attributes.half_band_ripple = True
        assert design.attributes.half_band_ripple

    def test_constrict_ripple_percent(self):
        design = pyaedt.FilterSolutions(implementation_type=FilterImplementation.LUMPED)
        design.attributes.filter_type = FilterType.ELLIPTIC
        design.attributes.constrict_ripple = True
        assert design.attributes.constrict_ripple_percent == "50%"
        design.attributes.constrict_ripple_percent = "40%"
        assert design.attributes.constrict_ripple_percent == "40%"

    def test_ripple_constriction_band(self):
        design = pyaedt.FilterSolutions(implementation_type=FilterImplementation.LUMPED)
        design.attributes.filter_type = FilterType.ELLIPTIC
        design.attributes.constrict_ripple = True
        assert len(RippleConstrictionBandSelect) == 3
        for ripple_constriction_band in RippleConstrictionBandSelect:
            design.attributes.ripple_constriction_band = ripple_constriction_band
            assert design.attributes.ripple_constriction_band == ripple_constriction_band

    def test_single_point_ripple_inf_zeros(self):
        design = pyaedt.FilterSolutions(implementation_type=FilterImplementation.LUMPED)
        design.attributes.filter_type = FilterType.ELLIPTIC
        design.attributes.single_point_ripple = True
        assert len(SinglePointRippleInfZeros) == 2
        for single_point_ripple_inf_zeros in SinglePointRippleInfZeros:
            design.attributes.single_point_ripple_inf_zeros = single_point_ripple_inf_zeros
            assert design.attributes.single_point_ripple_inf_zeros == single_point_ripple_inf_zeros

    def test_delay_equalizer(self):
        design = pyaedt.FilterSolutions(implementation_type=FilterImplementation.LUMPED)
        assert design.attributes.delay_equalizer is False
        design.attributes.delay_equalizer = True
        assert design.attributes.delay_equalizer

    def test_delay_equalizer_order(self):
        design = pyaedt.FilterSolutions(implementation_type=FilterImplementation.LUMPED)
        design.attributes.delay_equalizer = True
        assert design.attributes.delay_equalizer_order == 2

        for i in range(0, 21):
            design.attributes.delay_equalizer_order = i
            assert design.attributes.delay_equalizer_order == i

        with pytest.raises(RuntimeError) as info:
            design.attributes.delay_equalizer_order = 21
        assert info.value.args[0] == "The maximum order is 20"

    def test_standard_delay_equ_pass_band_attenuation(self):
        design = pyaedt.FilterSolutions(implementation_type=FilterImplementation.LUMPED)
        design.attributes.delay_equalizer = True
        assert design.attributes.standard_delay_equ_pass_band_attenuation
        design.attributes.standard_delay_equ_pass_band_attenuation = False
        assert design.attributes.standard_delay_equ_pass_band_attenuation is False

    def test_standard_delay_equ_pass_band_attenuation_value_db(self):
        design = pyaedt.FilterSolutions(implementation_type=FilterImplementation.LUMPED)
        design.attributes.delay_equalizer = True
        design.attributes.standard_delay_equ_pass_band_attenuation = False
        assert design.attributes.standard_delay_equ_pass_band_attenuation_value_db == "3.01"
        design.attributes.standard_delay_equ_pass_band_attenuation_value_db = "4"
        assert design.attributes.standard_delay_equ_pass_band_attenuation_value_db == "4"
