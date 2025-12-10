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

import pytest

import ansys.aedt.core.filtersolutions
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
from ansys.aedt.core.generic.settings import is_linux
from tests.conftest import DESKTOP_VERSION

default_center_freq = "1G"
changed_freq = "500M"
default_band_width_freq = "200M"
default_attenuation = "3.01"
changed_attenuation = "4"
default_ripple = ".05"
changed_ripple = ".03"


@pytest.mark.skipif(is_linux, reason="FilterSolutions API is not supported on Linux.")
@pytest.mark.skipif(DESKTOP_VERSION < "2025.1", reason="Skipped on versions earlier than 2025.1")
class TestClass:
    def test_multiple_designs(self, lumped_design):
        lumped_design.attributes.filter_class = FilterClass.BAND_PASS
        assert lumped_design.attributes.filter_class == FilterClass.BAND_PASS
        lumped_design.attributes.filter_type = FilterType.ELLIPTIC
        assert lumped_design.attributes.filter_type == FilterType.ELLIPTIC
        lumped_design.attributes.filter_order = 8
        assert lumped_design.attributes.filter_order == 8
        with pytest.warns(
            UserWarning,
            match="FilterSolutions API currently supports only one design at a time. \n"
            "Opening a new design will overwrite the existing design with default values.",
        ):
            new_lumped_design = ansys.aedt.core.filtersolutions.LumpedDesign()
        new_lumped_design = ansys.aedt.core.filtersolutions.LumpedDesign()
        assert new_lumped_design.attributes.filter_class == FilterClass.LOW_PASS
        assert new_lumped_design.attributes.filter_type == FilterType.BUTTERWORTH
        assert new_lumped_design.attributes.filter_order == 5

    def test_filter_type(self, lumped_design):
        assert lumped_design.attributes.filter_type == FilterType.BUTTERWORTH
        assert hasattr(FilterType, "CHEBY") is False
        with pytest.raises(RuntimeError) as info:
            lumped_design.attributes.filter_type = "CHEBY"
        assert info.value.args[0] == "The filter type 'CHEBY' is not available"
        assert len(FilterType) == 10
        for ftype in FilterType:
            lumped_design.attributes.filter_type = ftype
            assert lumped_design.attributes.filter_type == ftype

    def test_filter_class(self, lumped_design):
        assert lumped_design.attributes.filter_class == FilterClass.LOW_PASS
        assert hasattr(FilterClass, "MULTI_BAND") is False
        with pytest.raises(RuntimeError) as info:
            lumped_design.attributes.filter_class = "MULTI_BAND"
        assert info.value.args[0] == "The filter class 'MULTI_BAND' for single band filter is not available"

        # Only lumped supports all classes
        # TODO: Confirm proper exceptions are raised when setting unsupported filter class for each implementation.

        assert len(FilterClass) == 10
        for index, fclass in enumerate(FilterClass):
            if index > 5:
                lumped_design.attributes.filter_multiple_bands_enabled = True
            lumped_design.attributes.filter_class = fclass
            assert lumped_design.attributes.filter_class == fclass
        lumped_design.attributes.filter_multiple_bands_enabled = True
        with pytest.raises(RuntimeError) as info:
            lumped_design.attributes.filter_class = FilterClass.BAND_PASS
        assert info.value.args[0] == "The filter class 'band pass' for multiple bands filter is not available"

    def test_filter_multiple_bands_enabled(self, lumped_design):
        with pytest.raises(RuntimeError) as info:
            lumped_design.attributes.filter_class = FilterClass.BAND_HIGH
        assert info.value.args[0] == "The filter class 'band high' for single band filter is not available"
        assert lumped_design.attributes.filter_multiple_bands_enabled is False
        lumped_design.attributes.filter_multiple_bands_enabled = True
        assert lumped_design.attributes.filter_multiple_bands_enabled

    def test_filter_multiple_bands_low_pass_frequency(self, lumped_design):
        lumped_design.attributes.filter_multiple_bands_enabled = True
        lumped_design.attributes.filter_class = FilterClass.BAND_HIGH
        if DESKTOP_VERSION > "2025.1":
            with pytest.raises(RuntimeError) as info:
                lumped_design.attributes.filter_multiple_bands_low_pass_frequency = changed_freq
            assert info.value.args[0] == "This filter does not have multiple bands low pass frequency"
        lumped_design.attributes.filter_class = FilterClass.LOW_BAND
        assert lumped_design.attributes.filter_multiple_bands_low_pass_frequency == default_center_freq
        lumped_design.attributes.filter_multiple_bands_low_pass_frequency = changed_freq
        assert lumped_design.attributes.filter_multiple_bands_low_pass_frequency == changed_freq

    def test_filter_multiple_bands_high_pass_frequency(self, lumped_design):
        lumped_design.attributes.filter_multiple_bands_enabled = True
        lumped_design.attributes.filter_class = FilterClass.BAND_BAND
        if DESKTOP_VERSION > "2025.1":
            with pytest.raises(RuntimeError) as info:
                lumped_design.attributes.filter_multiple_bands_high_pass_frequency = changed_freq
            assert info.value.args[0] == "This filter does not have multiple bands high pass frequency"
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
        lumped_design.attributes.filter_class = FilterClass.DIPLEXER_1
        with pytest.raises(RuntimeError) as info:
            lumped_design.attributes.minimum_order_stop_band_attenuation_db = "40"
        assert info.value.args[0] == "It is not possible to calculate the minimum order for this filter"
        lumped_design.attributes.filter_class = FilterClass.LOW_PASS
        assert lumped_design.attributes.minimum_order_stop_band_attenuation_db == "60 dB"
        lumped_design.attributes.minimum_order_stop_band_attenuation_db = "40 dB"
        assert lumped_design.attributes.minimum_order_stop_band_attenuation_db == "40 dB"

    def test_minimum_order_stop_band_freq(self, lumped_design):
        lumped_design.attributes.filter_class = FilterClass.DIPLEXER_1
        with pytest.raises(RuntimeError) as info:
            lumped_design.attributes.minimum_order_stop_band_frequency = "10 GHz"
        assert info.value.args[0] == "It is not possible to calculate the minimum order for this filter"
        lumped_design.attributes.filter_class = FilterClass.LOW_PASS
        assert lumped_design.attributes.minimum_order_stop_band_frequency == "10 GHz"
        lumped_design.attributes.minimum_order_stop_band_frequency = "500 MHz"
        assert lumped_design.attributes.minimum_order_stop_band_frequency == "500 MHz"

    def test_minimum_order_group_delay_error_percent(self, lumped_design):
        lumped_design.attributes.filter_class = FilterClass.DIPLEXER_1
        with pytest.raises(RuntimeError) as info:
            lumped_design.attributes.minimum_order_group_delay_error_percent = "5"
        assert info.value.args[0] == "It is not possible to calculate the minimum order for this filter"
        lumped_design.attributes.filter_type = FilterType.DELAY
        assert lumped_design.attributes.minimum_order_group_delay_error_percent == "5"
        lumped_design.attributes.minimum_order_group_delay_error_percent = "7"
        assert lumped_design.attributes.minimum_order_group_delay_error_percent == "7"

    def test_minimum_order_group_delay_cutoff(self, lumped_design):
        lumped_design.attributes.filter_class = FilterClass.DIPLEXER_1
        with pytest.raises(RuntimeError) as info:
            lumped_design.attributes.minimum_order_group_delay_cutoff = "2 GHz"
        assert info.value.args[0] == "It is not possible to calculate the minimum order for this filter"
        lumped_design.attributes.filter_type = FilterType.DELAY
        assert lumped_design.attributes.minimum_order_group_delay_cutoff == "2 GHz"
        lumped_design.attributes.minimum_order_group_delay_cutoff = "500 MHz"
        assert lumped_design.attributes.minimum_order_group_delay_cutoff == "500 MHz"

    def test_minimum_order(self, lumped_design):
        lumped_design.attributes.filter_class = FilterClass.DIPLEXER_1
        with pytest.raises(RuntimeError) as info:
            assert lumped_design.attributes.ideal_minimum_order == 3
        assert info.value.args[0] == "It is not possible to calculate the minimum order for this filter"
        lumped_design.attributes.filter_class = FilterClass.LOW_PASS
        assert lumped_design.attributes.filter_order == 5
        assert lumped_design.attributes.ideal_minimum_order == 3
        assert lumped_design.attributes.filter_order == 3

    def test_delay_time(self, lumped_design):
        with pytest.raises(RuntimeError) as info:
            lumped_design.attributes.delay_time = "1 n"
        assert info.value.args[0] == "The Butterworth filter does not have delay time"
        lumped_design.attributes.filter_type = FilterType.DELAY
        assert lumped_design.attributes.delay_time == "1 n"
        lumped_design.attributes.delay_time = "500 ps"
        assert lumped_design.attributes.delay_time == "500 ps"

    def test_pass_band_definition(self, lumped_design):
        with pytest.raises(RuntimeError) as info:
            lumped_design.attributes.pass_band_definition = PassbandDefinition.CENTER_FREQUENCY
        assert info.value.args[0] == "The Low Pass filter does not have pass band frequency"
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
        lumped_design.attributes.filter_type = FilterType.DELAY
        with pytest.raises(RuntimeError) as info:
            lumped_design.attributes.pass_band_center_frequency = default_center_freq
        assert info.value.args[0] == "The Delay filter does not have center frequency"
        lumped_design.attributes.filter_type = FilterType.BUTTERWORTH
        lumped_design.attributes.filter_class = FilterClass.DIPLEXER_1
        lumped_design.attributes.diplexer_type = DiplexerType.BP_2
        with pytest.raises(RuntimeError) as info:
            lumped_design.attributes.pass_band_center_frequency = default_center_freq
        assert info.value.args[0] == (
            "This function is not supported for the Butterworth diplexer with BP2 or Triplexer2 configuration "
            "including two lower and upper center frequencies"
        )

    def test_pass_band_frequency(self, lumped_design):
        lumped_design.attributes.filter_class = FilterClass.BAND_PASS
        assert lumped_design.attributes.pass_band_width_frequency == default_band_width_freq
        lumped_design.attributes.pass_band_width_frequency = changed_freq
        assert lumped_design.attributes.pass_band_width_frequency == changed_freq
        lumped_design.attributes.filter_class = FilterClass.LOW_PASS
        with pytest.raises(RuntimeError) as info:
            lumped_design.attributes.pass_band_width_frequency = default_band_width_freq
        assert info.value.args[0] == "The Low Pass filter does not have pass band frequency"
        lumped_design.attributes.filter_class = FilterClass.DIPLEXER_1
        lumped_design.attributes.diplexer_type = DiplexerType.BP_2
        with pytest.raises(RuntimeError) as info:
            lumped_design.attributes.pass_band_width_frequency = default_band_width_freq
        assert info.value.args[0] == (
            "This function is not supported for the Butterworth diplexer with BP2 or Triplexer2 configuration "
            "including two lower and upper pass band frequencies"
        )

    def test_lower_frequency(self, lumped_design):
        lumped_design.attributes.filter_class = FilterClass.BAND_PASS
        lumped_design.attributes.pass_band_definition = PassbandDefinition.CORNER_FREQUENCIES
        assert lumped_design.attributes.lower_frequency == "905 M"
        lumped_design.attributes.lower_frequency = "800M"
        assert lumped_design.attributes.lower_frequency == "800M"
        lumped_design.attributes.filter_class = FilterClass.LOW_PASS
        with pytest.raises(RuntimeError) as info:
            lumped_design.attributes.lower_frequency = "905 M"
        if DESKTOP_VERSION > "2025.1":
            assert info.value.args[0] == "The Low Pass filter does not have lower frequency"
        else:
            assert info.value.args[0] == "The Low Pass filter does not have pass band frequency"
        lumped_design.attributes.filter_class = FilterClass.DIPLEXER_1
        lumped_design.attributes.diplexer_type = DiplexerType.BP_2
        with pytest.raises(RuntimeError) as info:
            lumped_design.attributes.lower_frequency = "905 M"
        assert info.value.args[0] == (
            "This function is not supported for the Butterworth diplexer with BP2 or Triplexer2 configuration, "
            "diplexer type filters should utilize the lower and upper frequency ranges accordingly"
        )

    def test_upper_frequency(self, lumped_design):
        lumped_design.attributes.filter_class = FilterClass.BAND_PASS
        lumped_design.attributes.pass_band_definition = PassbandDefinition.CORNER_FREQUENCIES
        assert lumped_design.attributes.upper_frequency == "1.105 G"
        lumped_design.attributes.upper_frequency = "1.2 G"
        assert lumped_design.attributes.upper_frequency == "1.2 G"
        lumped_design.attributes.filter_class = FilterClass.LOW_PASS
        with pytest.raises(RuntimeError) as info:
            lumped_design.attributes.upper_frequency = "1.105 M"
        if DESKTOP_VERSION > "2025.1":
            assert info.value.args[0] == "The Low Pass filter does not have upper frequency"
        else:
            assert info.value.args[0] == "The Low Pass filter does not have pass band frequency"
        lumped_design.attributes.filter_class = FilterClass.DIPLEXER_1
        lumped_design.attributes.diplexer_type = DiplexerType.BP_2
        with pytest.raises(RuntimeError) as info:
            lumped_design.attributes.upper_frequency = "1.105 M"
        assert info.value.args[0] == (
            "This function is not supported for the Butterworth diplexer with BP2 or Triplexer2 configuration, "
            "diplexer type filters should utilize the lower and upper frequency ranges accordingly"
        )

    def test_diplexer_inner_band_width(self, lumped_design):
        lumped_design.attributes.filter_class = FilterClass.DIPLEXER_1
        lumped_design.attributes.diplexer_type = DiplexerType.BP_1
        assert lumped_design.attributes.diplexer_inner_band_width == "200M"
        lumped_design.attributes.diplexer_inner_band_width = "500M"
        assert lumped_design.attributes.diplexer_inner_band_width == "500M"
        lumped_design.attributes.diplexer_type = DiplexerType.BP_2
        with pytest.raises(RuntimeError) as info:
            lumped_design.attributes.diplexer_inner_band_width = "500M"
        assert info.value.args[0] == (
            "This function is defined exclusively for diplexer with BP1 or Triplexer1 configuration, "
            "including inner and outer pass band frequencies"
        )

    def test_diplexer_outer_band_width(self, lumped_design):
        lumped_design.attributes.filter_class = FilterClass.DIPLEXER_1
        lumped_design.attributes.diplexer_type = DiplexerType.BP_1
        assert lumped_design.attributes.diplexer_outer_band_width == "2G"
        lumped_design.attributes.diplexer_outer_band_width = "3G"
        assert lumped_design.attributes.diplexer_outer_band_width == "3G"
        lumped_design.attributes.diplexer_type = DiplexerType.BP_2
        with pytest.raises(RuntimeError) as info:
            lumped_design.attributes.diplexer_outer_band_width = "3G"
        assert info.value.args[0] == (
            "This function is defined exclusively for diplexer with BP1 or Triplexer1 configuration, "
            "including inner and outer pass band frequencies"
        )

    def test_diplexer_lower_center_frequency(self, lumped_design):
        lumped_design.attributes.filter_class = FilterClass.DIPLEXER_1
        lumped_design.attributes.diplexer_type = DiplexerType.BP_2
        assert lumped_design.attributes.diplexer_lower_center_frequency == ".5G"
        lumped_design.attributes.diplexer_lower_center_frequency = ".4G"
        assert lumped_design.attributes.diplexer_lower_center_frequency == ".4G"
        lumped_design.attributes.diplexer_type = DiplexerType.BP_1
        with pytest.raises(RuntimeError) as info:
            lumped_design.attributes.diplexer_lower_center_frequency = ".4G"
        assert info.value.args[0] == (
            "This function is defined exclusively for diplexer with BP2 or Triplexer2 configuration, "
            "including two lower and upper center frequencies"
        )

    def test_diplexer_upper_center_frequency(self, lumped_design):
        lumped_design.attributes.filter_class = FilterClass.DIPLEXER_1
        lumped_design.attributes.diplexer_type = DiplexerType.BP_2
        assert lumped_design.attributes.diplexer_upper_center_frequency == "2G"
        lumped_design.attributes.diplexer_upper_center_frequency = "1.6G"
        assert lumped_design.attributes.diplexer_upper_center_frequency == "1.6G"
        lumped_design.attributes.diplexer_type = DiplexerType.BP_1
        with pytest.raises(RuntimeError) as info:
            lumped_design.attributes.diplexer_upper_center_frequency = "1.6G"
        assert info.value.args[0] == (
            "This function is defined exclusively for diplexer with BP2 or Triplexer2 configuration, "
            "including two lower and upper center frequencies"
        )

    def test_diplexer_lower_band_width(self, lumped_design):
        lumped_design.attributes.filter_class = FilterClass.DIPLEXER_1
        lumped_design.attributes.diplexer_type = DiplexerType.BP_2
        assert lumped_design.attributes.diplexer_lower_band_width == ".5G"
        lumped_design.attributes.diplexer_lower_band_width = ".4G"
        assert lumped_design.attributes.diplexer_lower_band_width == ".4G"
        lumped_design.attributes.diplexer_type = DiplexerType.BP_1
        with pytest.raises(RuntimeError) as info:
            lumped_design.attributes.diplexer_lower_band_width = ".4G"
        assert info.value.args[0] == (
            "This function is defined exclusively for diplexer with BP2 or Triplexer2 configuration, "
            "including two lower and upper pass band frequencies"
        )

    def test_diplexer_upper_band_width(self, lumped_design):
        lumped_design.attributes.filter_class = FilterClass.DIPLEXER_1
        lumped_design.attributes.diplexer_type = DiplexerType.BP_2
        assert lumped_design.attributes.diplexer_upper_band_width == "2G"
        lumped_design.attributes.diplexer_upper_band_width = "1.6G"
        assert lumped_design.attributes.diplexer_upper_band_width == "1.6G"
        lumped_design.attributes.diplexer_type = DiplexerType.BP_1
        with pytest.raises(RuntimeError) as info:
            lumped_design.attributes.diplexer_upper_band_width = "1.6G"
        assert info.value.args[0] == (
            "This function is defined exclusively for diplexer with BP2 or Triplexer2 configuration, "
            "including two lower and upper pass band frequencies"
        )

    def test_stop_band_definition(self, lumped_design):
        with pytest.raises(RuntimeError) as info:
            lumped_design.attributes.stop_band_definition = StopbandDefinition.RATIO
        if DESKTOP_VERSION > "2025.1":
            assert info.value.args[0] == "The Butterworth filter does not have stop band definition"
        else:
            assert info.value.args[0] == "The Butterworth filter does not have stop band ratio"
        lumped_design.attributes.filter_type = FilterType.ELLIPTIC
        assert len(StopbandDefinition) == 3
        assert lumped_design.attributes.stop_band_definition == StopbandDefinition.RATIO
        for sbd in StopbandDefinition:
            lumped_design.attributes.stop_band_definition = sbd
            assert lumped_design.attributes.stop_band_definition == sbd

    def test_stop_band_ratio(self, lumped_design):
        with pytest.raises(RuntimeError) as info:
            lumped_design.attributes.stop_band_ratio = "1.2"
        assert info.value.args[0] == "The Butterworth filter does not have stop band ratio"
        lumped_design.attributes.filter_type = FilterType.ELLIPTIC
        assert lumped_design.attributes.stop_band_ratio == "1.2"
        lumped_design.attributes.stop_band_ratio = "1.5"
        assert lumped_design.attributes.stop_band_ratio == "1.5"

    def test_stop_band_frequency(self, lumped_design):
        with pytest.raises(RuntimeError) as info:
            lumped_design.attributes.stop_band_frequency = "1.2 G"
        if DESKTOP_VERSION > "2025.1":
            assert info.value.args[0] == "The Butterworth filter does not have stop band frequency"
        else:
            assert info.value.args[0] == "The Butterworth and diplexer filters do not have stop band frequency"
        lumped_design.attributes.filter_type = FilterType.ELLIPTIC
        lumped_design.attributes.filter_class = FilterClass.DIPLEXER_1
        with pytest.raises(RuntimeError) as info:
            lumped_design.attributes.stop_band_frequency = "1.2 G"
        if DESKTOP_VERSION > "2025.1":
            assert info.value.args[0] == "The Diplexer 1 filter does not have stop band frequency"
        else:
            assert info.value.args[0] == "The Diplexer 1 and diplexer filters do not have stop band frequency"
        lumped_design.attributes.filter_class = FilterClass.LOW_PASS
        lumped_design.attributes.stop_band_definition = StopbandDefinition.FREQUENCY
        assert lumped_design.attributes.stop_band_frequency == "1.2 G"
        lumped_design.attributes.stop_band_frequency = "1.5 G"
        assert lumped_design.attributes.stop_band_frequency == "1.5 G"

    def test_stop_band_attenuation(self, lumped_design):
        with pytest.raises(RuntimeError) as info:
            lumped_design.attributes.stop_band_attenuation_db = "60"
        assert info.value.args[0] == "The Butterworth filter does not have stop band attenuation"
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
        with pytest.raises(RuntimeError) as info:
            lumped_design.attributes.root_raised_cosine = True
        assert info.value.args[0] == "The root raised cosine option is not available for Butterworth filter type"
        lumped_design.attributes.filter_type = FilterType.RAISED_COS
        assert lumped_design.attributes.root_raised_cosine is False
        lumped_design.attributes.root_raised_cosine = True
        assert lumped_design.attributes.root_raised_cosine

    def test_data_transmission_filter(self, lumped_design):
        with pytest.raises(RuntimeError) as info:
            lumped_design.attributes.data_transmission_filter = True
        assert info.value.args[0] == "The root raised cosine option is not available for Butterworth filter type"
        lumped_design.attributes.filter_type = FilterType.RAISED_COS
        assert lumped_design.attributes.data_transmission_filter is False
        lumped_design.attributes.data_transmission_filter = True
        assert lumped_design.attributes.data_transmission_filter

    def test_raised_cosine_alpha_percentage(self, lumped_design):
        with pytest.raises(RuntimeError) as info:
            lumped_design.attributes.raised_cosine_alpha_percentage = RaisedCosineAlphaPercentage.FORTY
        assert info.value.args[0] == "The Butterworth filter does not have raised cosine alpha percentage"
        lumped_design.attributes.filter_type = FilterType.RAISED_COS
        assert lumped_design.attributes.raised_cosine_alpha_percentage == RaisedCosineAlphaPercentage.FORTY
        lumped_design.attributes.raised_cosine_alpha_percentage = RaisedCosineAlphaPercentage.THIRTY
        assert lumped_design.attributes.raised_cosine_alpha_percentage == RaisedCosineAlphaPercentage.THIRTY

    def test_equiripple_delay_enabled(self, lumped_design):
        with pytest.raises(RuntimeError) as info:
            lumped_design.attributes.equiripple_delay_enabled = True
        assert info.value.args[0] == "The Butterworth filter does not have equiripple delay"
        lumped_design.attributes.filter_type = FilterType.DELAY
        assert lumped_design.attributes.equiripple_delay_enabled
        lumped_design.attributes.equiripple_delay_enabled = False
        assert lumped_design.attributes.equiripple_delay_enabled is False

    def test_group_delay_ripple_period(self, lumped_design):
        with pytest.raises(RuntimeError) as info:
            lumped_design.attributes.group_delay_ripple_period = "2"
        assert info.value.args[0] == "The Butterworth filter does not have group delay ripple period"
        lumped_design.attributes.filter_type = FilterType.DELAY
        assert lumped_design.attributes.group_delay_ripple_period == "2"
        lumped_design.attributes.group_delay_ripple_period = "3"
        assert lumped_design.attributes.group_delay_ripple_period == "3"
        lumped_design.attributes.equiripple_delay_enabled = False
        with pytest.raises(RuntimeError) as info:
            lumped_design.attributes.group_delay_ripple_period = "1"
        assert info.value.args[0] == (
            "Equiripple delay option is disabled, it is not possible to define group delay "
            "ripple period for this filter"
        )

    def test_normalized_group_delay_percentage(self, lumped_design):
        with pytest.raises(RuntimeError) as info:
            lumped_design.attributes.normalized_group_delay_percentage = BesselRipplePercentage.TEN
        assert info.value.args[0] == "The Butterworth filter does not have group delay ripple percentage"
        lumped_design.attributes.filter_type = FilterType.DELAY
        assert len(BesselRipplePercentage) == 6
        for normalized_group_delay_percentage in BesselRipplePercentage:
            lumped_design.attributes.normalized_group_delay_percentage = normalized_group_delay_percentage
            assert lumped_design.attributes.normalized_group_delay_percentage == normalized_group_delay_percentage
        lumped_design.attributes.equiripple_delay_enabled = False
        with pytest.raises(RuntimeError) as info:
            lumped_design.attributes.normalized_group_delay_percentage = BesselRipplePercentage.TEN
        assert info.value.args[0] == (
            "Equiripple delay option is disabled, it is not possible to define group delay "
            "ripple percentage for this filter"
        )

    def test_bessel_normalized_delay_enabled(self, lumped_design):
        with pytest.raises(RuntimeError) as info:
            lumped_design.attributes.bessel_normalized_delay_enabled = True
        if DESKTOP_VERSION > "2025.1":
            assert info.value.args[0] == "The Butterworth filter does not have Bessel normalized delay"
        else:
            assert info.value.args[0] == "The Butterworth filter does not have equiripple delay"
        lumped_design.attributes.filter_type = FilterType.BESSEL
        assert lumped_design.attributes.bessel_normalized_delay_enabled is False
        lumped_design.attributes.bessel_normalized_delay_enabled = True
        assert lumped_design.attributes.bessel_normalized_delay_enabled

    def test_bessel_normalized_delay_period(self, lumped_design):
        with pytest.raises(RuntimeError) as info:
            lumped_design.attributes.bessel_normalized_delay_period = "2"
        if DESKTOP_VERSION > "2025.1":
            assert info.value.args[0] == "The Butterworth filter does not have Bessel normalized delay period"
        else:
            assert info.value.args[0] == "The Butterworth filter does not have equiripple delay"
        lumped_design.attributes.filter_type = FilterType.BESSEL
        lumped_design.attributes.bessel_normalized_delay_enabled = True
        assert lumped_design.attributes.bessel_normalized_delay_period == "2"
        lumped_design.attributes.bessel_normalized_delay_period = "3"
        assert lumped_design.attributes.bessel_normalized_delay_period == "3"
        lumped_design.attributes.bessel_normalized_delay_enabled = False
        with pytest.raises(RuntimeError) as info:
            lumped_design.attributes.bessel_normalized_delay_period = "1"
        if DESKTOP_VERSION > "2025.1":
            assert info.value.args[0] == (
                "Equiripple delay option is disabled, it is not possible to define group delay ripple period "
                "for this filter"
            )
        else:
            assert info.value.args[0] == (
                "Equiripple delay option is disabled, it is not possible to define group delay ripple percentage "
                "for this filter"
            )

    def test_bessel_normalized_delay_percentage(self, lumped_design):
        with pytest.raises(RuntimeError) as info:
            lumped_design.attributes.bessel_normalized_delay_percentage = BesselRipplePercentage.TEN
        if DESKTOP_VERSION > "2025.1":
            assert info.value.args[0] == "The Butterworth filter does not have Bessel normalized delay percentage"
        else:
            assert info.value.args[0] == "The Butterworth filter has no ripple percentage parameter option"
        lumped_design.attributes.filter_type = FilterType.BESSEL
        lumped_design.attributes.bessel_normalized_delay_enabled = True
        assert len(BesselRipplePercentage) == 6
        for bessel_normalized_delay_percentage in BesselRipplePercentage:
            lumped_design.attributes.bessel_normalized_delay_percentage = bessel_normalized_delay_percentage
            assert lumped_design.attributes.bessel_normalized_delay_percentage == bessel_normalized_delay_percentage
        lumped_design.attributes.bessel_normalized_delay_enabled = False
        with pytest.raises(RuntimeError) as info:
            lumped_design.attributes.bessel_normalized_delay_percentage = BesselRipplePercentage.TEN
        assert info.value.args[0] == (
            "Equiripple delay option is disabled, it is not possible to define group delay ripple "
            "percentage for this filter"
        )

    def test_pass_band_ripple(self, lumped_design):
        with pytest.raises(RuntimeError) as info:
            lumped_design.attributes.pass_band_ripple = default_ripple
        assert info.value.args[0] == "The Butterworth filter does not have pass band ripple"
        lumped_design.attributes.filter_type = FilterType.ELLIPTIC
        assert lumped_design.attributes.pass_band_ripple == default_ripple
        lumped_design.attributes.pass_band_ripple = changed_ripple
        assert lumped_design.attributes.pass_band_ripple == changed_ripple

    def test_arith_symmetry(self, lumped_design):
        with pytest.raises(RuntimeError) as info:
            lumped_design.attributes.arith_symmetry = True
        assert info.value.args[0] == "The Low Pass filter does not support arithmetic symmetry option"
        lumped_design.attributes.filter_type = FilterType.ELLIPTIC
        lumped_design.attributes.filter_class = FilterClass.BAND_PASS
        assert lumped_design.attributes.arith_symmetry is False
        lumped_design.attributes.arith_symmetry = True
        assert lumped_design.attributes.arith_symmetry

    def test_asymmetric(self, lumped_design):
        with pytest.raises(RuntimeError) as info:
            lumped_design.attributes.asymmetric = True
        assert info.value.args[0] == "The Low Pass filter does not support asymmetric option"
        lumped_design.attributes.filter_class = FilterClass.BAND_PASS
        assert lumped_design.attributes.asymmetric is False
        lumped_design.attributes.asymmetric = True
        assert lumped_design.attributes.asymmetric

    def test_asymmetric_low_order(self, lumped_design):
        lumped_design.attributes.filter_class = FilterClass.BAND_PASS
        with pytest.raises(RuntimeError) as info:
            lumped_design.attributes.asymmetric_low_order = 5
        if DESKTOP_VERSION > "2025.1":
            assert info.value.args[0] == "The asymmetric option is disabled"
        else:
            assert info.value.args[0] == "The Butterworth filter does not support asymmetric option"
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
        with pytest.raises(RuntimeError) as info:
            lumped_design.attributes.asymmetric_high_order = 5
        if DESKTOP_VERSION > "2025.1":
            assert info.value.args[0] == "The asymmetric option is disabled"
        else:
            assert info.value.args[0] == "The Butterworth filter does not support asymmetric option"
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
        with pytest.raises(RuntimeError) as info:
            lumped_design.attributes.asymmetric_low_stop_band_ratio = "1.2"
        if DESKTOP_VERSION > "2025.1":
            assert info.value.args[0] == "The Butterworth filter does not have stop band ratio"
        else:
            assert info.value.args[0] == "The Butterworth filter does not support asymmetric option"
        lumped_design.attributes.filter_type = FilterType.ELLIPTIC
        with pytest.raises(RuntimeError) as info:
            lumped_design.attributes.asymmetric_low_stop_band_ratio = "1.2"
        if DESKTOP_VERSION > "2025.1":
            assert info.value.args[0] == "The asymmetric option is disabled"
        else:
            assert info.value.args[0] == "The Elliptic filter does not support asymmetric option"
        lumped_design.attributes.asymmetric = True
        assert lumped_design.attributes.asymmetric_low_stop_band_ratio == "1.2"
        lumped_design.attributes.asymmetric_low_stop_band_ratio = "1.5"
        assert lumped_design.attributes.asymmetric_low_stop_band_ratio == "1.5"

    def test_asymmetric_high_stop_band_ratio(self, lumped_design):
        lumped_design.attributes.filter_class = FilterClass.BAND_PASS
        with pytest.raises(RuntimeError) as info:
            lumped_design.attributes.asymmetric_high_stop_band_ratio = "1.2"
        if DESKTOP_VERSION > "2025.1":
            assert info.value.args[0] == "The Butterworth filter does not have stop band ratio"
        else:
            assert info.value.args[0] == "The Butterworth filter does not support asymmetric option"
        lumped_design.attributes.filter_type = FilterType.ELLIPTIC
        with pytest.raises(RuntimeError) as info:
            lumped_design.attributes.asymmetric_high_stop_band_ratio = "1.2"
        if DESKTOP_VERSION > "2025.1":
            assert info.value.args[0] == "The asymmetric option is disabled"
        else:
            assert info.value.args[0] == "The Elliptic filter does not support asymmetric option"
        lumped_design.attributes.asymmetric = True
        assert lumped_design.attributes.asymmetric_high_stop_band_ratio == "1.2"
        lumped_design.attributes.asymmetric_high_stop_band_ratio = "1.5"
        assert lumped_design.attributes.asymmetric_high_stop_band_ratio == "1.5"

    def test_asymmetric_low_stop_band_attenuation_db(self, lumped_design):
        lumped_design.attributes.filter_class = FilterClass.BAND_PASS
        with pytest.raises(RuntimeError) as info:
            lumped_design.attributes.asymmetric_low_stop_band_attenuation_db = "40"
        if DESKTOP_VERSION > "2025.1":
            assert info.value.args[0] == "The Butterworth filter does not have stop band attenuation"
        else:
            assert info.value.args[0] == "The Butterworth filter does not support asymmetric option"
        lumped_design.attributes.filter_type = FilterType.ELLIPTIC
        with pytest.raises(RuntimeError) as info:
            lumped_design.attributes.asymmetric_low_stop_band_attenuation_db = "40"
        if DESKTOP_VERSION > "2025.1":
            assert info.value.args[0] == "The asymmetric option is disabled"
        else:
            assert info.value.args[0] == "The Elliptic filter does not support asymmetric option"
        lumped_design.attributes.asymmetric = True
        assert lumped_design.attributes.asymmetric_low_stop_band_attenuation_db == "60"
        lumped_design.attributes.asymmetric_low_stop_band_attenuation_db = "40"
        assert lumped_design.attributes.asymmetric_low_stop_band_attenuation_db == "40"

    def test_asymmetric_high_stop_band_attenuation_db(self, lumped_design):
        lumped_design.attributes.filter_class = FilterClass.BAND_PASS
        with pytest.raises(RuntimeError) as info:
            lumped_design.attributes.asymmetric_high_stop_band_attenuation_db = "40"
        if DESKTOP_VERSION > "2025.1":
            assert info.value.args[0] == "The Butterworth filter does not have stop band attenuation"
        else:
            assert info.value.args[0] == "The Butterworth filter does not support asymmetric option"
        lumped_design.attributes.filter_type = FilterType.ELLIPTIC
        with pytest.raises(RuntimeError) as info:
            lumped_design.attributes.asymmetric_high_stop_band_attenuation_db = "40"
        if DESKTOP_VERSION > "2025.1":
            assert info.value.args[0] == "The asymmetric option is disabled"
        else:
            assert info.value.args[0] == "The Elliptic filter does not support asymmetric option"
        lumped_design.attributes.asymmetric = True
        assert lumped_design.attributes.asymmetric_high_stop_band_attenuation_db == "60"
        lumped_design.attributes.asymmetric_high_stop_band_attenuation_db = "40"
        assert lumped_design.attributes.asymmetric_high_stop_band_attenuation_db == "40"

    def test_gaussian_transition(self, lumped_design):
        with pytest.raises(RuntimeError) as info:
            lumped_design.attributes.gaussian_transition = GaussianTransition.TRANSITION_3_DB
        if DESKTOP_VERSION > "2025.1":
            assert info.value.args[0] == "The Butterworth filter does not have Gaussian transition"
        else:
            assert info.value.args[0] == "The Butterworth filter has no tranisiotn parameter option"
        lumped_design.attributes.filter_type = FilterType.GAUSSIAN
        assert len(GaussianTransition) == 6
        for gaussian_transition in GaussianTransition:
            lumped_design.attributes.gaussian_transition = gaussian_transition
            assert lumped_design.attributes.gaussian_transition == gaussian_transition

    def test_gaussian_bessel_reflection(self, lumped_design):
        with pytest.raises(RuntimeError) as info:
            lumped_design.attributes.gaussian_bessel_reflection = GaussianBesselReflection.OPTION_1
        if DESKTOP_VERSION > "2025.1":
            assert info.value.args[0] == "The Butterworth filter does not have Gaussian Bessel reflection"
        else:
            assert info.value.args[0] == "The Butterworth filter has no synthesis reflection option"
        lumped_design.attributes.filter_type = FilterType.BESSEL
        assert len(GaussianBesselReflection) == 3
        for gaussian_bessel_reflection in GaussianBesselReflection:
            lumped_design.attributes.gaussian_bessel_reflection = gaussian_bessel_reflection
            assert lumped_design.attributes.gaussian_bessel_reflection == gaussian_bessel_reflection

    def test_even_order(self, lumped_design):
        with pytest.raises(RuntimeError) as info:
            lumped_design.attributes.even_order = True
        if DESKTOP_VERSION > "2025.1":
            assert (
                info.value.args[0] == "The Butterworth, Low Pass, and odd filter does not have even order mode option"
            )
        else:
            assert info.value.args[0] == "The Butterworth ,Low Pass , and odd filters have no even order mode option"
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
        lumped_design.attributes.filter_order = 5
        with pytest.raises(RuntimeError) as info:
            lumped_design.attributes.even_order_refl_zero = True
        assert info.value.args[0] == "It is not possible to set the reflection zeros of this filter to 0"

    def test_even_order_trn_zero(self, lumped_design):
        lumped_design.attributes.filter_type = FilterType.ELLIPTIC
        lumped_design.attributes.filter_order = 4
        assert lumped_design.attributes.even_order_trn_zero
        lumped_design.attributes.even_order_trn_zero = False
        assert lumped_design.attributes.even_order_trn_zero is False
        lumped_design.attributes.filter_order = 5
        with pytest.raises(RuntimeError) as info:
            lumped_design.attributes.even_order_trn_zero = True
            if DESKTOP_VERSION > "2025.1":
                assert info.value.args[0] == "The even order filter does not have transmission zeros"
            else:
                assert info.value.args[0] == "The even order filter does not have transmission zeros"

    def test_constrict_ripple(self, lumped_design):
        with pytest.raises(RuntimeError) as info:
            lumped_design.attributes.constrict_ripple = True
        if DESKTOP_VERSION > "2025.1":
            assert info.value.args[0] == "It is not possible to constrict ripple for Butterworth filter"
        else:
            assert info.value.args[0] == "It is not possible to constrict the ripple for this filter"
        lumped_design.attributes.filter_type = FilterType.ELLIPTIC
        assert lumped_design.attributes.constrict_ripple is False
        lumped_design.attributes.constrict_ripple = True
        assert lumped_design.attributes.constrict_ripple

    def test_single_point_ripple(self, lumped_design):
        with pytest.raises(RuntimeError) as info:
            lumped_design.attributes.single_point_ripple = True
        if DESKTOP_VERSION > "2025.1":
            assert (
                info.value.args[0]
                == "It is not possible to confine ripple to single frequency for Butterworth asymmetric filter"
            )
        else:
            assert (
                info.value.args[0]
                == "It is not possible to confine ripple to single frequency for Butterworth asymmetric filters"
            )
        lumped_design.attributes.filter_type = FilterType.ELLIPTIC
        assert lumped_design.attributes.single_point_ripple is False
        lumped_design.attributes.single_point_ripple = True
        assert lumped_design.attributes.single_point_ripple

    def test_half_band_ripple(self, lumped_design):
        with pytest.raises(RuntimeError) as info:
            lumped_design.attributes.half_band_ripple = True
        if DESKTOP_VERSION > "2025.1":
            assert (
                info.value.args[0]
                == "It is not possible to use half of the zeros in the selected band for Butterworth asymmetric filter"
            )
        else:
            assert (
                info.value.args[0]
                == "It is not possible to use half of the zeros in the selected band for Butterworth asymmetric filters"
            )
        lumped_design.attributes.filter_type = FilterType.ELLIPTIC
        assert lumped_design.attributes.half_band_ripple is False
        lumped_design.attributes.half_band_ripple = True
        assert lumped_design.attributes.half_band_ripple

    def test_constrict_ripple_percent(self, lumped_design):
        with pytest.raises(RuntimeError) as info:
            lumped_design.attributes.constrict_ripple_percent = "50%"
        if DESKTOP_VERSION > "2025.1":
            assert info.value.args[0] == "It is not possible to constrict ripple for Butterworth asymmetric filter"
        else:
            assert info.value.args[0] == "It is not possible to constrict the ripple for Butterworth asymmetric filters"
        lumped_design.attributes.filter_type = FilterType.ELLIPTIC
        lumped_design.attributes.constrict_ripple = True
        assert lumped_design.attributes.constrict_ripple_percent == "50%"
        lumped_design.attributes.constrict_ripple_percent = "40%"
        assert lumped_design.attributes.constrict_ripple_percent == "40%"

    def test_ripple_constriction_band(self, lumped_design):
        with pytest.raises(RuntimeError) as info:
            lumped_design.attributes.ripple_constriction_band = RippleConstrictionBandSelect.PASS
        if DESKTOP_VERSION > "2025.1":
            assert (
                info.value.args[0] == "The ripple constriction band is not available for Butterworth asymmetric filter"
            )
        else:
            assert (
                info.value.args[0] == "The ripple constriction band is not available for Butterworth asymmetric filters"
            )
        lumped_design.attributes.filter_type = FilterType.ELLIPTIC
        lumped_design.attributes.constrict_ripple = True
        assert len(RippleConstrictionBandSelect) == 3
        for ripple_constriction_band in RippleConstrictionBandSelect:
            lumped_design.attributes.ripple_constriction_band = ripple_constriction_band
            assert lumped_design.attributes.ripple_constriction_band == ripple_constriction_band

    def test_single_point_ripple_inf_zeros(self, lumped_design):
        with pytest.raises(RuntimeError) as info:
            lumped_design.attributes.single_point_ripple_inf_zeros = SinglePointRippleInfZeros.RIPPLE_INF_ZEROS_1
        if DESKTOP_VERSION > "2025.1":
            assert (
                info.value.args[0]
                == "The single point ripple with infinite zeros are not available for Butterworth odd asymmetric filter"
            )
        else:
            assert (
                info.value.args[0] == "The single point ripple with infinite zeros are not available "
                "for Butterworth odd asymmetric filters"
            )
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
        lumped_design.attributes.filter_type = FilterType.GAUSSIAN
        with pytest.raises(RuntimeError) as info:
            lumped_design.attributes.delay_equalizer = True
        assert info.value.args[0] == "The Gaussian filter has no delay equalizer option"

    def test_delay_equalizer_order(self, lumped_design):
        with pytest.raises(RuntimeError) as info:
            lumped_design.attributes.delay_equalizer_order = 2
        assert info.value.args[0] == "The delay equalizer option is not set for this filter"
        lumped_design.attributes.delay_equalizer = True
        assert lumped_design.attributes.delay_equalizer_order == 2

        for i in range(0, 21):
            lumped_design.attributes.delay_equalizer_order = i
            assert lumped_design.attributes.delay_equalizer_order == i

        with pytest.raises(RuntimeError) as info:
            lumped_design.attributes.delay_equalizer_order = 21
        assert info.value.args[0] == "The maximum order is 20"

    def test_standard_delay_equ_pass_band_attenuation(self, lumped_design):
        with pytest.raises(RuntimeError) as info:
            lumped_design.attributes.standard_delay_equ_pass_band_attenuation = True
        if DESKTOP_VERSION > "2025.1":
            assert info.value.args[0] == "The delay equalizer option is not set for this filter"
        else:
            assert (
                info.value.args[0]
                == "The standard delay equalizer attenuation is not available for Butterworth filters"
            )
        lumped_design.attributes.delay_equalizer = True
        assert lumped_design.attributes.standard_delay_equ_pass_band_attenuation
        lumped_design.attributes.standard_delay_equ_pass_band_attenuation = False
        assert lumped_design.attributes.standard_delay_equ_pass_band_attenuation is False

    def test_standard_delay_equ_pass_band_attenuation_value_db(self, lumped_design):
        with pytest.raises(RuntimeError) as info:
            lumped_design.attributes.standard_delay_equ_pass_band_attenuation_value_db = default_attenuation
        if DESKTOP_VERSION > "2025.1":
            assert info.value.args[0] == "The delay equalizer option is not set for this filter"
        else:
            assert (
                info.value.args[0] == "The delay equalizer attenuation setting is not available for Butterworth filters"
            )
        lumped_design.attributes.delay_equalizer = True
        with pytest.raises(RuntimeError) as info:
            lumped_design.attributes.standard_delay_equ_pass_band_attenuation_value_db = default_attenuation
        if DESKTOP_VERSION > "2025.1":
            assert info.value.args[0] == "The standard delay equalizer pass band attenuation is enabled"
        else:
            assert info.value.args[0] == "The standard delay equalizer attenuation is enabled"
        lumped_design.attributes.standard_delay_equ_pass_band_attenuation = False
        assert lumped_design.attributes.standard_delay_equ_pass_band_attenuation_value_db == default_attenuation
        lumped_design.attributes.standard_delay_equ_pass_band_attenuation_value_db = changed_attenuation
        assert lumped_design.attributes.standard_delay_equ_pass_band_attenuation_value_db == changed_attenuation
