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

from ansys.aedt.core.filtersolutions_core.attributes import BesselRipplePercentage
from ansys.aedt.core.filtersolutions_core.attributes import DiplexerType
from ansys.aedt.core.filtersolutions_core.attributes import FilterClass
from ansys.aedt.core.filtersolutions_core.attributes import FilterType
from ansys.aedt.core.filtersolutions_core.attributes import GaussianBesselReflection
from ansys.aedt.core.filtersolutions_core.attributes import GaussianTransition
from ansys.aedt.core.filtersolutions_core.attributes import PassbandDefinition
from ansys.aedt.core.filtersolutions_core.attributes import RaisedCosineAlphaPercentage
from ansys.aedt.core.filtersolutions_core.attributes import RippleConstrictionBandSelect
from ansys.aedt.core.filtersolutions_core.attributes import SinglePointRippleInfZeros
from ansys.aedt.core.filtersolutions_core.attributes import StopbandDefinition
from ansys.aedt.core.generic.general_methods import is_linux
import pytest

from tests.system.general.conftest import config

default_center_freq = "1G"
changed_freq = "500M"
default_band_width_freq = "200M"
default_attenuation = "3.01"
changed_attenuation = "4"
default_ripple = ".05"
changed_ripple = ".03"


@pytest.mark.skipif(is_linux, reason="FilterSolutions API is not supported on Linux.")
@pytest.mark.skipif(config["desktopVersion"] < "2025.1", reason="Skipped on versions earlier than 2025.1")
class TestClass:
    def test_filter_type(self, lumped_design):
        assert lumped_design.attributes.filter_type == FilterType.BUTTERWORTH
        assert len(FilterType) == 10
        for ftype in FilterType:
            lumped_design.attributes.filter_type = ftype
            assert lumped_design.attributes.filter_type == ftype

    def test_filter_class(self, lumped_design):
        assert lumped_design.attributes.filter_class == FilterClass.LOW_PASS

        # Only lumped supports all classes
        # TODO: Confirm proper exceptions are raised when setting unsupported filter class for each implementation.

        assert len(FilterClass) == 10
        for index, fclass in enumerate(FilterClass):
            if index > 5:
                lumped_design.attributes.filter_multiple_bands_enabled = True
            lumped_design.attributes.filter_class = fclass
            assert lumped_design.attributes.filter_class == fclass

    def test_filter_multiple_bands_enabled(self, lumped_design):
        assert lumped_design.attributes.filter_multiple_bands_enabled is False
        lumped_design.attributes.filter_multiple_bands_enabled = True
        assert lumped_design.attributes.filter_multiple_bands_enabled

    def test_filter_multiple_bands_low_pass_frequency(self, lumped_design):
        lumped_design.attributes.filter_multiple_bands_enabled = True
        lumped_design.attributes.filter_class = FilterClass.LOW_BAND
        assert lumped_design.attributes.filter_multiple_bands_low_pass_frequency == default_center_freq
        lumped_design.attributes.filter_multiple_bands_low_pass_frequency = changed_freq
        assert lumped_design.attributes.filter_multiple_bands_low_pass_frequency == changed_freq

    def test_filter_multiple_bands_high_pass_frequency(self, lumped_design):
        lumped_design.attributes.filter_multiple_bands_enabled = True
        lumped_design.attributes.filter_class = FilterClass.BAND_HIGH
        assert lumped_design.attributes.filter_multiple_bands_high_pass_frequency == default_center_freq
        lumped_design.attributes.filter_multiple_bands_high_pass_frequency = changed_freq
        assert lumped_design.attributes.filter_multiple_bands_high_pass_frequency == changed_freq

    def test_diplexer_type(self, lumped_design):
        assert len(DiplexerType) == 6
        for index, diplexer_type in enumerate(DiplexerType):
            if index < 3:
                lumped_design.attributes.filter_class = FilterClass.DIPLEXER_1
            elif index > 2:
                lumped_design.attributes.filter_class = FilterClass.DIPLEXER_2
            lumped_design.attributes.diplexer_type = diplexer_type
            assert lumped_design.attributes.diplexer_type == diplexer_type

    def test_filter_order(self, lumped_design):
        assert lumped_design.attributes.filter_order == 5
        with pytest.raises(RuntimeError) as info:
            lumped_design.attributes.filter_order = 0
        assert info.value.args[0] == "The minimum order is 1"

        for i in range(1, 22):
            lumped_design.attributes.filter_order = i
            assert lumped_design.attributes.filter_order == i

        with pytest.raises(RuntimeError) as info:
            lumped_design.attributes.filter_order = 22
        assert info.value.args[0] == "The maximum order is 21"

    def test_minimum_order_stop_band_att(self, lumped_design):
        assert lumped_design.attributes.minimum_order_stop_band_attenuation_db == "60 dB"
        lumped_design.attributes.minimum_order_stop_band_attenuation_db = "40 dB"
        assert lumped_design.attributes.minimum_order_stop_band_attenuation_db == "40 dB"

    def test_minimum_order_stop_band_freq(self, lumped_design):
        assert lumped_design.attributes.minimum_order_stop_band_frequency == "10 GHz"
        lumped_design.attributes.minimum_order_stop_band_frequency = "500 MHz"
        assert lumped_design.attributes.minimum_order_stop_band_frequency == "500 MHz"

    def test_minimum_order_group_delay_error_percent(self, lumped_design):
        lumped_design.attributes.filter_type = FilterType.DELAY
        assert lumped_design.attributes.minimum_order_group_delay_error_percent == "5"
        lumped_design.attributes.minimum_order_group_delay_error_percent = "7"
        assert lumped_design.attributes.minimum_order_group_delay_error_percent == "7"

    def test_minimum_order_group_delay_cutoff(self, lumped_design):
        lumped_design.attributes.filter_type = FilterType.DELAY
        assert lumped_design.attributes.minimum_order_group_delay_cutoff == "2 GHz"
        lumped_design.attributes.minimum_order_group_delay_cutoff = "500 MHz"
        assert lumped_design.attributes.minimum_order_group_delay_cutoff == "500 MHz"

    def test_minimum_order(self, lumped_design):
        assert lumped_design.attributes.filter_order == 5
        assert lumped_design.attributes.ideal_minimum_order == 3
        assert lumped_design.attributes.filter_order == 3

    def test_delay_time(self, lumped_design):
        lumped_design.attributes.filter_type = FilterType.DELAY
        assert lumped_design.attributes.delay_time == "1 n"
        lumped_design.attributes.delay_time = "500 ps"
        assert lumped_design.attributes.delay_time == "500 ps"

    def test_pass_band_definition(self, lumped_design):
        lumped_design.attributes.filter_class = FilterClass.BAND_PASS
        assert len(PassbandDefinition) == 2
        assert lumped_design.attributes.pass_band_definition == PassbandDefinition.CENTER_FREQUENCY
        for pbd in PassbandDefinition:
            lumped_design.attributes.pass_band_definition = pbd
            assert lumped_design.attributes.pass_band_definition == pbd

    def test_pass_band_center_frequency(self, lumped_design):
        assert lumped_design.attributes.pass_band_center_frequency == default_center_freq
        lumped_design.attributes.pass_band_center_frequency = changed_freq
        assert lumped_design.attributes.pass_band_center_frequency == changed_freq

    def test_pass_band_frequency(self, lumped_design):
        lumped_design.attributes.filter_class = FilterClass.BAND_PASS
        assert lumped_design.attributes.pass_band_width_frequency == default_band_width_freq
        lumped_design.attributes.pass_band_width_frequency = changed_freq
        assert lumped_design.attributes.pass_band_width_frequency == changed_freq

    def test_lower_frequency(self, lumped_design):
        lumped_design.attributes.filter_class = FilterClass.BAND_PASS
        lumped_design.attributes.pass_band_definition = PassbandDefinition.CORNER_FREQUENCIES
        assert lumped_design.attributes.lower_frequency == "905 M"
        lumped_design.attributes.lower_frequency = "800M"
        assert lumped_design.attributes.lower_frequency == "800M"

    def test_upper_frequency(self, lumped_design):
        lumped_design.attributes.filter_class = FilterClass.BAND_PASS
        lumped_design.attributes.pass_band_definition = PassbandDefinition.CORNER_FREQUENCIES
        assert lumped_design.attributes.upper_frequency == "1.105 G"
        lumped_design.attributes.upper_frequency = "1.2 G"
        assert lumped_design.attributes.upper_frequency == "1.2 G"

    def test_diplexer_inner_band_width(self, lumped_design):
        lumped_design.attributes.filter_class = FilterClass.DIPLEXER_1
        lumped_design.attributes.diplexer_type = DiplexerType.BP_1
        assert lumped_design.attributes.diplexer_inner_band_width == "200M"
        lumped_design.attributes.diplexer_inner_band_width = "500M"
        assert lumped_design.attributes.diplexer_inner_band_width == "500M"

    def test_diplexer_outer_band_width(self, lumped_design):
        lumped_design.attributes.filter_class = FilterClass.DIPLEXER_1
        lumped_design.attributes.diplexer_type = DiplexerType.BP_1
        assert lumped_design.attributes.diplexer_outer_band_width == "2G"
        lumped_design.attributes.diplexer_outer_band_width = "3G"
        assert lumped_design.attributes.diplexer_outer_band_width == "3G"

    def test_diplexer_lower_center_frequency(self, lumped_design):
        lumped_design.attributes.filter_class = FilterClass.DIPLEXER_1
        lumped_design.attributes.diplexer_type = DiplexerType.BP_2
        assert lumped_design.attributes.diplexer_lower_center_frequency == ".5G"
        lumped_design.attributes.diplexer_lower_center_frequency = ".4G"
        assert lumped_design.attributes.diplexer_lower_center_frequency == ".4G"

    def test_diplexer_upper_center_frequency(self, lumped_design):
        lumped_design.attributes.filter_class = FilterClass.DIPLEXER_1
        lumped_design.attributes.diplexer_type = DiplexerType.BP_2
        assert lumped_design.attributes.diplexer_upper_center_frequency == "2G"
        lumped_design.attributes.diplexer_upper_center_frequency = "1.6G"
        assert lumped_design.attributes.diplexer_upper_center_frequency == "1.6G"

    def test_diplexer_lower_band_width(self, lumped_design):
        lumped_design.attributes.filter_class = FilterClass.DIPLEXER_1
        lumped_design.attributes.diplexer_type = DiplexerType.BP_2
        assert lumped_design.attributes.diplexer_lower_band_width == ".5G"
        lumped_design.attributes.diplexer_lower_band_width = ".4G"
        assert lumped_design.attributes.diplexer_lower_band_width == ".4G"

    def test_diplexer_upper_band_width(self, lumped_design):
        lumped_design.attributes.filter_class = FilterClass.DIPLEXER_1
        lumped_design.attributes.diplexer_type = DiplexerType.BP_2
        assert lumped_design.attributes.diplexer_upper_band_width == "2G"
        lumped_design.attributes.diplexer_upper_band_width = "1.6G"
        assert lumped_design.attributes.diplexer_upper_band_width == "1.6G"

    def test_stop_band_definition(self, lumped_design):
        lumped_design.attributes.filter_type = FilterType.ELLIPTIC
        assert len(StopbandDefinition) == 3
        assert lumped_design.attributes.stop_band_definition == StopbandDefinition.RATIO
        for sbd in StopbandDefinition:
            lumped_design.attributes.stop_band_definition = sbd
            assert lumped_design.attributes.stop_band_definition == sbd

    def test_stop_band_ratio(self, lumped_design):
        lumped_design.attributes.filter_type = FilterType.ELLIPTIC
        assert lumped_design.attributes.stop_band_ratio == "1.2"
        lumped_design.attributes.stop_band_ratio = "1.5"
        assert lumped_design.attributes.stop_band_ratio == "1.5"

    def test_stop_band_frequency(self, lumped_design):
        lumped_design.attributes.filter_type = FilterType.ELLIPTIC
        lumped_design.attributes.stop_band_definition = StopbandDefinition.FREQUENCY
        assert lumped_design.attributes.stop_band_frequency == "1.2 G"
        lumped_design.attributes.stop_band_frequency = "1.5 G"
        assert lumped_design.attributes.stop_band_frequency == "1.5 G"

    def test_stop_band_attenuation(self, lumped_design):
        lumped_design.attributes.filter_type = FilterType.ELLIPTIC
        lumped_design.attributes.stop_band_definition = StopbandDefinition.ATTENUATION_DB
        assert lumped_design.attributes.stop_band_attenuation_db == "60"
        lumped_design.attributes.stop_band_attenuation_db = "40 dB"
        assert lumped_design.attributes.stop_band_attenuation_db == "40"

    def test_standard_pass_band_attenuation(self, lumped_design):
        assert lumped_design.attributes.standard_pass_band_attenuation
        lumped_design.attributes.standard_pass_band_attenuation = False
        assert lumped_design.attributes.standard_pass_band_attenuation is False

    def test_standard_pass_band_attenuation_value_db(self, lumped_design):
        lumped_design.attributes.standard_pass_band_attenuation = False
        assert lumped_design.attributes.standard_pass_band_attenuation_value_db == default_attenuation
        lumped_design.attributes.standard_pass_band_attenuation_value_db = changed_attenuation
        assert lumped_design.attributes.standard_pass_band_attenuation_value_db == changed_attenuation

    def test_root_raised_cosine(self, lumped_design):
        lumped_design.attributes.filter_type = FilterType.RAISED_COS
        assert lumped_design.attributes.root_raised_cosine is False
        lumped_design.attributes.root_raised_cosine = True
        assert lumped_design.attributes.root_raised_cosine

    def test_data_transmission_filter(self, lumped_design):
        lumped_design.attributes.filter_type = FilterType.RAISED_COS
        assert lumped_design.attributes.data_transmission_filter is False
        lumped_design.attributes.data_transmission_filter = True
        assert lumped_design.attributes.data_transmission_filter

    def test_raised_cosine_alpha_percentage(self, lumped_design):
        lumped_design.attributes.filter_type = FilterType.RAISED_COS
        assert lumped_design.attributes.raised_cosine_alpha_percentage == RaisedCosineAlphaPercentage.FORTY
        lumped_design.attributes.raised_cosine_alpha_percentage = RaisedCosineAlphaPercentage.THIRTY
        assert lumped_design.attributes.raised_cosine_alpha_percentage == RaisedCosineAlphaPercentage.THIRTY

    def test_equiripple_delay(self, lumped_design):
        lumped_design.attributes.filter_type = FilterType.DELAY
        assert lumped_design.attributes.equiripple_delay
        lumped_design.attributes.equiripple_delay = False
        assert lumped_design.attributes.equiripple_delay is False

    def test_group_delay_ripple_period(self, lumped_design):
        lumped_design.attributes.filter_type = FilterType.DELAY
        assert lumped_design.attributes.group_delay_ripple_period == "2"
        lumped_design.attributes.group_delay_ripple_period = "3"
        assert lumped_design.attributes.group_delay_ripple_period == "3"

    def test_normalized_group_delay_percentage(self, lumped_design):
        lumped_design.attributes.filter_type = FilterType.DELAY
        assert len(BesselRipplePercentage) == 6
        for normalized_group_delay_percentage in BesselRipplePercentage:
            lumped_design.attributes.normalized_group_delay_percentage = normalized_group_delay_percentage
            assert lumped_design.attributes.normalized_group_delay_percentage == normalized_group_delay_percentage

    def test_bessel_normalized_delay(self, lumped_design):
        lumped_design.attributes.filter_type = FilterType.BESSEL
        assert lumped_design.attributes.bessel_normalized_delay is False
        lumped_design.attributes.bessel_normalized_delay = True
        assert lumped_design.attributes.bessel_normalized_delay

    def test_bessel_normalized_delay_period(self, lumped_design):
        lumped_design.attributes.filter_type = FilterType.BESSEL
        lumped_design.attributes.bessel_normalized_delay = True
        assert lumped_design.attributes.bessel_normalized_delay_period == "2"
        lumped_design.attributes.bessel_normalized_delay_period = "3"
        assert lumped_design.attributes.bessel_normalized_delay_period == "3"

    def test_bessel_normalized_delay_percentage(self, lumped_design):
        lumped_design.attributes.filter_type = FilterType.BESSEL
        lumped_design.attributes.bessel_normalized_delay = True
        assert len(BesselRipplePercentage) == 6
        for bessel_normalized_delay_percentage in BesselRipplePercentage:
            lumped_design.attributes.bessel_normalized_delay_percentage = bessel_normalized_delay_percentage
            assert lumped_design.attributes.bessel_normalized_delay_percentage == bessel_normalized_delay_percentage

    def test_pass_band_ripple(self, lumped_design):
        lumped_design.attributes.filter_type = FilterType.ELLIPTIC
        assert lumped_design.attributes.pass_band_ripple == default_ripple
        lumped_design.attributes.pass_band_ripple = changed_ripple
        assert lumped_design.attributes.pass_band_ripple == changed_ripple

    def test_arith_symmetry(self, lumped_design):
        lumped_design.attributes.filter_type = FilterType.ELLIPTIC
        lumped_design.attributes.filter_class = FilterClass.BAND_PASS
        assert lumped_design.attributes.arith_symmetry is False
        lumped_design.attributes.arith_symmetry = True
        assert lumped_design.attributes.arith_symmetry

    def test_asymmetric(self, lumped_design):
        lumped_design.attributes.filter_class = FilterClass.BAND_PASS
        assert lumped_design.attributes.asymmetric is False
        lumped_design.attributes.asymmetric = True
        assert lumped_design.attributes.asymmetric

    def test_asymmetric_low_order(self, lumped_design):
        lumped_design.attributes.filter_class = FilterClass.BAND_PASS
        lumped_design.attributes.asymmetric = True
        assert lumped_design.attributes.asymmetric_low_order == 5

        with pytest.raises(RuntimeError) as info:
            lumped_design.attributes.asymmetric_low_order = 0
        assert info.value.args[0] == "The minimum order is 1"

        for i in range(1, 22):
            lumped_design.attributes.asymmetric_low_order = i
            assert lumped_design.attributes.asymmetric_low_order == i

        with pytest.raises(RuntimeError) as info:
            lumped_design.attributes.asymmetric_low_order = 22
        assert info.value.args[0] == "The maximum order is 21"

    def test_asymmetric_high_order(self, lumped_design):
        lumped_design.attributes.filter_class = FilterClass.BAND_PASS
        lumped_design.attributes.asymmetric = True
        assert lumped_design.attributes.asymmetric_high_order == 5

        with pytest.raises(RuntimeError) as info:
            lumped_design.attributes.asymmetric_high_order = 0
        assert info.value.args[0] == "The minimum order is 1"

        for i in range(1, 22):
            lumped_design.attributes.asymmetric_high_order = i
            assert lumped_design.attributes.asymmetric_high_order == i

        with pytest.raises(RuntimeError) as info:
            lumped_design.attributes.asymmetric_high_order = 22
        assert info.value.args[0] == "The maximum order is 21"

    def test_asymmetric_low_stop_band_ratio(self, lumped_design):
        lumped_design.attributes.filter_class = FilterClass.BAND_PASS
        lumped_design.attributes.filter_type = FilterType.ELLIPTIC
        lumped_design.attributes.asymmetric = True
        assert lumped_design.attributes.asymmetric_low_stop_band_ratio == "1.2"
        lumped_design.attributes.asymmetric_low_stop_band_ratio = "1.5"
        assert lumped_design.attributes.asymmetric_low_stop_band_ratio == "1.5"

    def test_asymmetric_high_stop_band_ratio(self, lumped_design):
        lumped_design.attributes.filter_class = FilterClass.BAND_PASS
        lumped_design.attributes.filter_type = FilterType.ELLIPTIC
        lumped_design.attributes.asymmetric = True
        assert lumped_design.attributes.asymmetric_high_stop_band_ratio == "1.2"
        lumped_design.attributes.asymmetric_high_stop_band_ratio = "1.5"
        assert lumped_design.attributes.asymmetric_high_stop_band_ratio == "1.5"

    def test_asymmetric_low_stop_band_attenuation_db(self, lumped_design):
        lumped_design.attributes.filter_class = FilterClass.BAND_PASS
        lumped_design.attributes.filter_type = FilterType.ELLIPTIC
        lumped_design.attributes.asymmetric = True
        assert lumped_design.attributes.asymmetric_low_stop_band_attenuation_db == "60"
        lumped_design.attributes.asymmetric_low_stop_band_attenuation_db = "40"
        assert lumped_design.attributes.asymmetric_low_stop_band_attenuation_db == "40"

    def test_asymmetric_high_stop_band_attenuation_db(self, lumped_design):
        lumped_design.attributes.filter_class = FilterClass.BAND_PASS
        lumped_design.attributes.filter_type = FilterType.ELLIPTIC
        lumped_design.attributes.asymmetric = True
        assert lumped_design.attributes.asymmetric_high_stop_band_attenuation_db == "60"
        lumped_design.attributes.asymmetric_high_stop_band_attenuation_db = "40"
        assert lumped_design.attributes.asymmetric_high_stop_band_attenuation_db == "40"

    def test_gaussian_transition(self, lumped_design):
        lumped_design.attributes.filter_type = FilterType.GAUSSIAN
        assert len(GaussianTransition) == 6
        for gaussian_transition in GaussianTransition:
            lumped_design.attributes.gaussian_transition = gaussian_transition
            assert lumped_design.attributes.gaussian_transition == gaussian_transition

    def test_gaussian_bessel_reflection(self, lumped_design):
        lumped_design.attributes.filter_type = FilterType.BESSEL
        assert len(GaussianBesselReflection) == 3
        for gaussian_bessel_reflection in GaussianBesselReflection:
            lumped_design.attributes.gaussian_bessel_reflection = gaussian_bessel_reflection
            assert lumped_design.attributes.gaussian_bessel_reflection == gaussian_bessel_reflection

    def test_even_order(self, lumped_design):
        lumped_design.attributes.filter_type = FilterType.ELLIPTIC
        lumped_design.attributes.filter_order = 4
        assert lumped_design.attributes.even_order
        lumped_design.attributes.even_order = False
        assert lumped_design.attributes.even_order is False

    def test_even_order_refl_zero(self, lumped_design):
        lumped_design.attributes.filter_type = FilterType.ELLIPTIC
        lumped_design.attributes.filter_order = 4
        assert lumped_design.attributes.even_order_refl_zero
        lumped_design.attributes.even_order_refl_zero = False
        assert lumped_design.attributes.even_order_refl_zero is False

    def test_even_order_trn_zero(self, lumped_design):
        lumped_design.attributes.filter_type = FilterType.ELLIPTIC
        lumped_design.attributes.filter_order = 4
        assert lumped_design.attributes.even_order_trn_zero
        lumped_design.attributes.even_order_trn_zero = False
        assert lumped_design.attributes.even_order_trn_zero is False

    def test_constrict_ripple(self, lumped_design):
        lumped_design.attributes.filter_type = FilterType.ELLIPTIC
        assert lumped_design.attributes.constrict_ripple is False
        lumped_design.attributes.constrict_ripple = True
        assert lumped_design.attributes.constrict_ripple

    def test_single_point_ripple(self, lumped_design):
        lumped_design.attributes.filter_type = FilterType.ELLIPTIC
        assert lumped_design.attributes.single_point_ripple is False
        lumped_design.attributes.single_point_ripple = True
        assert lumped_design.attributes.single_point_ripple

    def test_half_band_ripple(self, lumped_design):
        lumped_design.attributes.filter_type = FilterType.ELLIPTIC
        assert lumped_design.attributes.half_band_ripple is False
        lumped_design.attributes.half_band_ripple = True
        assert lumped_design.attributes.half_band_ripple

    def test_constrict_ripple_percent(self, lumped_design):
        lumped_design.attributes.filter_type = FilterType.ELLIPTIC
        lumped_design.attributes.constrict_ripple = True
        assert lumped_design.attributes.constrict_ripple_percent == "50%"
        lumped_design.attributes.constrict_ripple_percent = "40%"
        assert lumped_design.attributes.constrict_ripple_percent == "40%"

    def test_ripple_constriction_band(self, lumped_design):
        lumped_design.attributes.filter_type = FilterType.ELLIPTIC
        lumped_design.attributes.constrict_ripple = True
        assert len(RippleConstrictionBandSelect) == 3
        for ripple_constriction_band in RippleConstrictionBandSelect:
            lumped_design.attributes.ripple_constriction_band = ripple_constriction_band
            assert lumped_design.attributes.ripple_constriction_band == ripple_constriction_band

    def test_single_point_ripple_inf_zeros(self, lumped_design):
        lumped_design.attributes.filter_type = FilterType.ELLIPTIC
        lumped_design.attributes.single_point_ripple = True
        assert len(SinglePointRippleInfZeros) == 2
        for single_point_ripple_inf_zeros in SinglePointRippleInfZeros:
            lumped_design.attributes.single_point_ripple_inf_zeros = single_point_ripple_inf_zeros
            assert lumped_design.attributes.single_point_ripple_inf_zeros == single_point_ripple_inf_zeros

    def test_delay_equalizer(self, lumped_design):
        assert lumped_design.attributes.delay_equalizer is False
        lumped_design.attributes.delay_equalizer = True
        assert lumped_design.attributes.delay_equalizer

    def test_delay_equalizer_order(self, lumped_design):
        lumped_design.attributes.delay_equalizer = True
        assert lumped_design.attributes.delay_equalizer_order == 2

        for i in range(0, 21):
            lumped_design.attributes.delay_equalizer_order = i
            assert lumped_design.attributes.delay_equalizer_order == i

        with pytest.raises(RuntimeError) as info:
            lumped_design.attributes.delay_equalizer_order = 21
        assert info.value.args[0] == "The maximum order is 20"

    def test_standard_delay_equ_pass_band_attenuation(self, lumped_design):
        lumped_design.attributes.delay_equalizer = True
        assert lumped_design.attributes.standard_delay_equ_pass_band_attenuation
        lumped_design.attributes.standard_delay_equ_pass_band_attenuation = False
        assert lumped_design.attributes.standard_delay_equ_pass_band_attenuation is False

    def test_standard_delay_equ_pass_band_attenuation_value_db(self, lumped_design):
        lumped_design.attributes.delay_equalizer = True
        lumped_design.attributes.standard_delay_equ_pass_band_attenuation = False
        assert lumped_design.attributes.standard_delay_equ_pass_band_attenuation_value_db == default_attenuation
        lumped_design.attributes.standard_delay_equ_pass_band_attenuation_value_db = changed_attenuation
        assert lumped_design.attributes.standard_delay_equ_pass_band_attenuation_value_db == changed_attenuation
