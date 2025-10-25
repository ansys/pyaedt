# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 - 2025 ANSYS, Inc. and/or its affiliates.
# SPDX-FileCopyrightText: 2021 - 2025 ANSYS, Inc. and /or its affiliates.
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

from enum import Enum

from ansys.aedt.core.emit_core.nodes.emit_node import EmitNode


class IndoorPropagationCouplingNode(EmitNode):
    def __init__(self, emit_obj, result_id, node_id):
        self._is_component = False
        EmitNode.__init__(self, emit_obj, result_id, node_id)

    @property
    def parent(self):
        """The parent of this emit node."""
        return self._parent

    @property
    def node_type(self) -> str:
        """The type of this emit node."""
        return self._node_type

    def rename(self, new_name: str):
        """Rename this node"""
        self._rename(new_name)

    def duplicate(self, new_name: str):
        """Duplicate this node"""
        return self._duplicate(new_name)

    def delete(self):
        """Delete this node"""
        self._delete()

    @property
    def table_data(self):
        """Custom Building Values Table.
        Table consists of 3 columns.
        Frequency:
            Value should be between 1.0 and 100.0e9.
        Power Loss Coefficient:
            Value should be between 0.0 and 100.0.
        Floor Penetration Loss (dB):
            Value should be between 0.0 and 1000.0.
        """
        return self._get_table_data()

    @table_data.setter
    def table_data(self, value):
        self._set_table_data(value)

    @property
    def enabled(self) -> bool:
        """Enable/Disable coupling.

        Value should be 'true' or 'false'.
        """
        val = self._get_property("Enabled")
        return val == "true"

    @enabled.setter
    def enabled(self, value: bool):
        self._set_property("Enabled", f"{str(value).lower()}")

    @property
    def antenna_a(self) -> EmitNode:
        """First antenna of the pair to apply the coupling values to."""
        val = self._get_property("Antenna A")
        return val

    @antenna_a.setter
    def antenna_a(self, value: EmitNode):
        self._set_property("Antenna A", f"{value}")

    @property
    def antenna_b(self) -> EmitNode:
        """Second antenna of the pair to apply the coupling values to."""
        val = self._get_property("Antenna B")
        return val

    @antenna_b.setter
    def antenna_b(self, value: EmitNode):
        self._set_property("Antenna B", f"{value}")

    @property
    def enable_refinement(self) -> bool:
        """Enables/disables refined sampling of the frequency domain.

        Value should be 'true' or 'false'.
        """
        val = self._get_property("Enable Refinement")
        return val == "true"

    @enable_refinement.setter
    def enable_refinement(self, value: bool):
        self._set_property("Enable Refinement", f"{str(value).lower()}")

    @property
    def adaptive_sampling(self) -> bool:
        """Enables/disables adaptive refinement the frequency domain sampling.

        Value should be 'true' or 'false'.
        """
        val = self._get_property("Adaptive Sampling")
        return val == "true"

    @adaptive_sampling.setter
    def adaptive_sampling(self, value: bool):
        self._set_property("Adaptive Sampling", f"{str(value).lower()}")

    @property
    def refinement_domain(self):
        """Points to use when refining the frequency domain."""
        val = self._get_property("Refinement Domain")
        return val

    @refinement_domain.setter
    def refinement_domain(self, value):
        self._set_property("Refinement Domain", f"{value}")

    class BuildingTypeOption(Enum):
        RESIDENTIAL_APARTMENT = "Residential Apartment"
        RESIDENTIAL_HOUSE = "Residential House"
        OFFICE_BUILDING = "Office Building"
        COMMERCIAL_BUILDING = "Commercial Building"
        CUSTOM_BUILDING = "Custom Building"

    @property
    def building_type(self) -> BuildingTypeOption:
        """Specify the building type for the Indoor Propagation model."""
        val = self._get_property("Building Type")
        val = self.BuildingTypeOption[val.upper()]
        return val

    @building_type.setter
    def building_type(self, value: BuildingTypeOption):
        self._set_property("Building Type", f"{value.value}")

    @property
    def number_of_floors(self) -> int:
        """The number of floors separating the antennas.

        Value should be between 1 and 3.
        """
        val = self._get_property("Number of Floors")
        return int(val)

    @number_of_floors.setter
    def number_of_floors(self, value: int):
        self._set_property("Number of Floors", f"{value}")

    @property
    def custom_fading_margin(self) -> float:
        """Custom Fading Margin.

        Sets a custom fading margin to be applied to all coupling defined by
        this node.

        Value should be between 0 and 100.
        """
        val = self._get_property("Custom Fading Margin")
        return float(val)

    @custom_fading_margin.setter
    def custom_fading_margin(self, value: float):
        self._set_property("Custom Fading Margin", f"{value}")

    @property
    def polarization_mismatch(self) -> float:
        """Polarization Mismatch.

        Sets a margin for polarization mismatch to be applied to all coupling
        defined by this node.

        Value should be between 0 and 100.
        """
        val = self._get_property("Polarization Mismatch")
        return float(val)

    @polarization_mismatch.setter
    def polarization_mismatch(self, value: float):
        self._set_property("Polarization Mismatch", f"{value}")

    @property
    def pointing_error_loss(self) -> float:
        """Pointing Error Loss.

        Sets a margin for pointing error loss to be applied to all coupling
        defined by this node.

        Value should be between 0 and 100.
        """
        val = self._get_property("Pointing Error Loss")
        return float(val)

    @pointing_error_loss.setter
    def pointing_error_loss(self, value: float):
        self._set_property("Pointing Error Loss", f"{value}")

    class FadingTypeOption(Enum):
        NONE = "None"
        FAST_FADING_ONLY = "Fast Fading Only"
        SHADOWING_ONLY = "Shadowing Only"
        FAST_FADING_AND_SHADOWING = "Fast Fading and Shadowing"

    @property
    def fading_type(self) -> FadingTypeOption:
        """Specify the type of fading to include."""
        val = self._get_property("Fading Type")
        val = self.FadingTypeOption[val.upper()]
        return val

    @fading_type.setter
    def fading_type(self, value: FadingTypeOption):
        self._set_property("Fading Type", f"{value.value}")

    @property
    def fading_availability(self) -> float:
        """Fading Availability.

        The probability that the propagation loss in dB is below its median
        value plus the margin.

        Value should be between 0.0 and 100.0.
        """
        val = self._get_property("Fading Availability")
        return float(val)

    @fading_availability.setter
    def fading_availability(self, value: float):
        self._set_property("Fading Availability", f"{value}")

    @property
    def std_deviation(self) -> float:
        """Standard deviation modeling the random amount of shadowing loss.

        Value should be between 0.0 and 100.0.
        """
        val = self._get_property("Std Deviation")
        return float(val)

    @std_deviation.setter
    def std_deviation(self, value: float):
        self._set_property("Std Deviation", f"{value}")

    @property
    def include_rain_attenuation(self) -> bool:
        """Adds a margin for rain attenuation to the computed coupling.

        Value should be 'true' or 'false'.
        """
        val = self._get_property("Include Rain Attenuation")
        return val == "true"

    @include_rain_attenuation.setter
    def include_rain_attenuation(self, value: bool):
        self._set_property("Include Rain Attenuation", f"{str(value).lower()}")

    @property
    def rain_availability(self) -> float:
        """Rain Availability.

        Percentage of time attenuation due to range is < computed margin (range
        from 99-99.999%).

        Value should be between 99 and 99.999.
        """
        val = self._get_property("Rain Availability")
        return float(val)

    @rain_availability.setter
    def rain_availability(self, value: float):
        self._set_property("Rain Availability", f"{value}")

    @property
    def rain_rate(self) -> float:
        """Rain rate (mm/hr) exceeded for 0.01% of the time.

        Value should be between 0.0 and 1000.0.
        """
        val = self._get_property("Rain Rate")
        return float(val)

    @rain_rate.setter
    def rain_rate(self, value: float):
        self._set_property("Rain Rate", f"{value}")

    @property
    def polarization_tilt_angle(self) -> float:
        """Polarization Tilt Angle.

        Polarization tilt angle of the transmitted signal relative to the
        horizontal.

        Value should be between 0.0 and 180.0.
        """
        val = self._get_property("Polarization Tilt Angle")
        return float(val)

    @polarization_tilt_angle.setter
    def polarization_tilt_angle(self, value: float):
        self._set_property("Polarization Tilt Angle", f"{value}")

    @property
    def include_atmospheric_absorption(self) -> bool:
        """Include Atmospheric Absorption.

        Adds a margin for atmospheric absorption due to oxygen/water vapor to
        the computed coupling.

        Value should be 'true' or 'false'.
        """
        val = self._get_property("Include Atmospheric Absorption")
        return val == "true"

    @include_atmospheric_absorption.setter
    def include_atmospheric_absorption(self, value: bool):
        self._set_property("Include Atmospheric Absorption", f"{str(value).lower()}")

    @property
    def temperature(self) -> float:
        """Air temperature in degrees Celsius.

        Value should be between -273.0 and 100.0.
        """
        val = self._get_property("Temperature")
        return float(val)

    @temperature.setter
    def temperature(self, value: float):
        self._set_property("Temperature", f"{value}")

    @property
    def total_air_pressure(self) -> float:
        """Total air pressure.

        Value should be between 0.0 and 2000.0.
        """
        val = self._get_property("Total Air Pressure")
        return float(val)

    @total_air_pressure.setter
    def total_air_pressure(self, value: float):
        self._set_property("Total Air Pressure", f"{value}")

    @property
    def water_vapor_concentration(self) -> float:
        """Water vapor concentration.

        Value should be between 0.0 and 2000.0.
        """
        val = self._get_property("Water Vapor Concentration")
        return float(val)

    @water_vapor_concentration.setter
    def water_vapor_concentration(self, value: float):
        self._set_property("Water Vapor Concentration", f"{value}")
