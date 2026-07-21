# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 - 2026 Synopsys, Inc. and ANSYS, Inc. All rights reserved.
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

from ansys.aedt.core.emit_core.nodes.generated import AntennaNode

from enum import Enum

from ansys.aedt.core.emit_core.nodes.emit_node import EmitNode
from ansys.aedt.core.internal.checks import min_aedt_version


class ErcegCouplingNode(EmitNode):
    """Provide erceg coupling node."""

    def __init__(self, emit_obj, result_id, node_id) -> None:
        EmitNode.__init__(self, emit_obj, result_id, node_id)
        self._is_component = False

    @property
    @min_aedt_version("2025.2")
    def parent(self) -> EmitNode:
        """The parent of this emit node.

        Examples
        --------
        >>> from ansys.aedt.core import Emit
        >>> app = Emit()
        >>> rev = app.results.get_revision()
        >>> cpl = rev.get_coupling_data_node()
        >>> ereg = cpl.add_erceg_coupling()
        >>> ereg.parent

        """
        return self._parent

    @property
    @min_aedt_version("2025.2")
    def node_type(self) -> str:
        """The type of this emit node.

        Examples
        --------
        >>> from ansys.aedt.core import Emit
        >>> app = Emit()
        >>> rev = app.results.get_revision()
        >>> cpl = rev.get_coupling_data_node()
        >>> ereg = cpl.add_erceg_coupling()
        >>> ereg.node_type

        """
        return self._node_type

    @min_aedt_version("2027.1")
    def export_to_csv(self, file_name: str, antennas: tuple[AntennaNode, AntennaNode] | None = None, ports: str = "") -> str:
        """Export's the data for this node

        Parameters
        ----------
        file_name: str[optional]
            full path to the file to export to.
        antennas: tuple(AntennaNode, AntennaNode), optional
            tuple of antenna nodes to pull the selected Tx and Rx antenna names from for the export.
            If not specified, will use the names specified by the ports parameter.
        ports: str, optional
            the ports to export the data for.

        Returns
        -------
        csv_data: str
            stringified data for the node returned if file_name not specified"""
        if antennas is not None and all(isinstance(x, AntennaNode) for x in antennas):
            a1, a2 = antennas
            vals = f"{a1.name}|{a2.name}"
        else:
            vals = f"{ports}"
        return self._export_to_csv(file_name, "SelectedRxAntenna|SelectedTxAntenna", vals)

    @min_aedt_version("2027.1")
    def plot(self, antennas: tuple[AntennaNode, AntennaNode] | None = None, ports: str = ""):
        """Bring up a Cartesian plot for this node

        Parameters
        ----------
        antennas: tuple(AntennaNode, AntennaNode), optional
            tuple of antenna nodes to pull the selected Tx and Rx antenna names from for the export.
            If not specified, will use the names specified by the ports parameter.
        ports: str, optional
            the ports to export the data for."""
        if antennas is not None and all(isinstance(x, AntennaNode) for x in antennas):
            a1, a2 = antennas
            vals = f"{a1.name}|{a2.name}"
        else:
            vals = f"{ports}"
        return self._plot("SelectedRxAntenna|SelectedTxAntenna", vals)

    @min_aedt_version("2025.2")
    def duplicate(self, new_name: str = "") -> EmitNode:
        """Duplicate this node.

        Examples
        --------
        >>> from ansys.aedt.core import Emit
        >>> app = Emit()
        >>> rev = app.results.get_revision()
        >>> cpl = rev.get_coupling_data_node()
        >>> ereg = cpl.add_erceg_coupling()
        >>> erceg_coupling_copy = erceg_coupling.duplicate("erceg_coupling_copy")

        """
        return self._duplicate(new_name)

    @min_aedt_version("2025.2")
    def delete(self) -> None:
        """Delete this node.

        Examples
        --------
        >>> from ansys.aedt.core import Emit
        >>> app = Emit()
        >>> rev = app.results.get_revision()
        >>> cpl = rev.get_coupling_data_node()
        >>> ereg = cpl.add_erceg_coupling()
        >>> ereg.delete()

        """
        self._delete()

    @property
    @min_aedt_version("2025.2")
    def enabled(self) -> bool:
        """Enable/Disable coupling.

        Value should be 'true' or 'false'.

        Examples
        --------
        >>> from ansys.aedt.core import Emit
        >>> app = Emit()
        >>> rev = app.results.get_revision()
        >>> cpl = rev.get_coupling_data_node()
        >>> ereg = cpl.add_erceg_coupling()
        >>> ereg.enabled = True

        """
        val = self._get_property("Enabled")
        return val == "true"

    @enabled.setter
    @min_aedt_version("2025.2")
    def enabled(self, value: bool) -> None:
        self._set_property("Enabled", f"{str(value).lower()}")

    @property
    @min_aedt_version("2025.2")
    def base_antenna(self) -> EmitNode:
        """First antenna of the pair to apply the coupling values to.

        Examples
        --------
        >>> from ansys.aedt.core import Emit
        >>> app = Emit()
        >>> rev = app.results.get_revision()
        >>> cpl = rev.get_coupling_data_node()
        >>> ereg = cpl.add_erceg_coupling()
        >>> ereg.base_antenna

        """
        val = self._get_property("Base Antenna")
        return val

    @base_antenna.setter
    @min_aedt_version("2025.2")
    def base_antenna(self, value: EmitNode) -> None:
        self._set_property("Base Antenna", f"{value}")

    @property
    @min_aedt_version("2025.2")
    def mobile_antenna(self) -> EmitNode:
        """Second antenna of the pair to apply the coupling values to.

        Examples
        --------
        >>> from ansys.aedt.core import Emit
        >>> app = Emit()
        >>> rev = app.results.get_revision()
        >>> cpl = rev.get_coupling_data_node()
        >>> ereg = cpl.add_erceg_coupling()
        >>> ereg.mobile_antenna

        """
        val = self._get_property("Mobile Antenna")
        return val

    @mobile_antenna.setter
    @min_aedt_version("2025.2")
    def mobile_antenna(self, value: EmitNode) -> None:
        self._set_property("Mobile Antenna", f"{value}")

    class TerrainCategoryOption(Enum):
        TYPE_A = "TypeA"
        TYPE_B = "TypeB"
        TYPE_C = "TypeC"

    @property
    @min_aedt_version("2025.2")
    def terrain_category(self) -> TerrainCategoryOption:
        """Specify the terrain category type for the Erceg model.

        Examples
        --------
        >>> from ansys.aedt.core import Emit
        >>> app = Emit()
        >>> rev = app.results.get_revision()
        >>> cpl = rev.get_coupling_data_node()
        >>> ereg = cpl.add_erceg_coupling()
        >>> ereg.terrain_category = ErcegCouplingNode.TerrainCategoryOption.TYPE_A

        """
        val = self._get_property("Terrain Category")
        val = self.TerrainCategoryOption[val.upper()]
        return val

    @terrain_category.setter
    @min_aedt_version("2025.2")
    def terrain_category(self, value: TerrainCategoryOption) -> None:
        self._set_property("Terrain Category", f"{value.value}")

    @property
    @min_aedt_version("2025.2")
    def custom_fading_margin(self) -> float:
        """Custom Fading Margin.

        Sets a custom fading margin to be applied to all coupling defined by
        this node.

        Value should be between 0 and 100.

        Examples
        --------
        >>> from ansys.aedt.core import Emit
        >>> app = Emit()
        >>> rev = app.results.get_revision()
        >>> cpl = rev.get_coupling_data_node()
        >>> ereg = cpl.add_erceg_coupling()
        >>> ereg.custom_fading_margin = 0

        """
        val = self._get_property("Custom Fading Margin")
        return float(val)

    @custom_fading_margin.setter
    @min_aedt_version("2025.2")
    def custom_fading_margin(self, value: float) -> None:
        self._set_property("Custom Fading Margin", f"{value}")

    @property
    @min_aedt_version("2025.2")
    def polarization_mismatch(self) -> float:
        """Polarization Mismatch.

        Sets a margin for polarization mismatch to be applied to all coupling
        defined by this node.

        Value should be between 0 and 100.

        Examples
        --------
        >>> from ansys.aedt.core import Emit
        >>> app = Emit()
        >>> rev = app.results.get_revision()
        >>> cpl = rev.get_coupling_data_node()
        >>> ereg = cpl.add_erceg_coupling()
        >>> ereg.polarization_mismatch = 0

        """
        val = self._get_property("Polarization Mismatch")
        return float(val)

    @polarization_mismatch.setter
    @min_aedt_version("2025.2")
    def polarization_mismatch(self, value: float) -> None:
        self._set_property("Polarization Mismatch", f"{value}")

    @property
    @min_aedt_version("2025.2")
    def pointing_error_loss(self) -> float:
        """Pointing Error Loss.

        Sets a margin for pointing error loss to be applied to all coupling
        defined by this node.

        Value should be between 0 and 100.

        Examples
        --------
        >>> from ansys.aedt.core import Emit
        >>> app = Emit()
        >>> rev = app.results.get_revision()
        >>> cpl = rev.get_coupling_data_node()
        >>> ereg = cpl.add_erceg_coupling()
        >>> ereg.pointing_error_loss = 0

        """
        val = self._get_property("Pointing Error Loss")
        return float(val)

    @pointing_error_loss.setter
    @min_aedt_version("2025.2")
    def pointing_error_loss(self, value: float) -> None:
        self._set_property("Pointing Error Loss", f"{value}")

    class FadingTypeOption(Enum):
        NONE = "NoFading"
        FAST_FADING_ONLY = "FastFadingOnly"
        SHADOWING_ONLY = "ShadowingOnly"
        FAST_FADING_AND_SHADOWING = "ShadowingAndFastFading"

    @property
    @min_aedt_version("2025.2")
    def fading_type(self) -> FadingTypeOption:
        """Specify the type of fading to include.

        Examples
        --------
        >>> from ansys.aedt.core import Emit
        >>> app = Emit()
        >>> rev = app.results.get_revision()
        >>> cpl = rev.get_coupling_data_node()
        >>> ereg = cpl.add_erceg_coupling()
        >>> ereg.fading_type = ErcegCouplingNode.FadingTypeOption.NONE

        """
        val = self._get_property("Fading Type")
        val = self.FadingTypeOption[val.upper()]
        return val

    @fading_type.setter
    @min_aedt_version("2025.2")
    def fading_type(self, value: FadingTypeOption) -> None:
        self._set_property("Fading Type", f"{value.value}")

    @property
    @min_aedt_version("2025.2")
    def fading_availability(self) -> float:
        """Fading Availability.

        The probability that the propagation loss in dB is below its median
        value plus the margin.

        Value should be between 0.0 and 100.0.

        Examples
        --------
        >>> from ansys.aedt.core import Emit
        >>> app = Emit()
        >>> rev = app.results.get_revision()
        >>> cpl = rev.get_coupling_data_node()
        >>> ereg = cpl.add_erceg_coupling()
        >>> ereg.fading_availability = 0.0

        """
        val = self._get_property("Fading Availability")
        return float(val)

    @fading_availability.setter
    @min_aedt_version("2025.2")
    def fading_availability(self, value: float) -> None:
        self._set_property("Fading Availability", f"{value}")

    @property
    @min_aedt_version("2025.2")
    def std_deviation(self) -> float:
        """Standard deviation modeling the random amount of shadowing loss.

        Value should be between 0.0 and 100.0.

        Examples
        --------
        >>> from ansys.aedt.core import Emit
        >>> app = Emit()
        >>> rev = app.results.get_revision()
        >>> cpl = rev.get_coupling_data_node()
        >>> ereg = cpl.add_erceg_coupling()
        >>> ereg.std_deviation = 0.0

        """
        val = self._get_property("Std Deviation")
        return float(val)

    @std_deviation.setter
    @min_aedt_version("2025.2")
    def std_deviation(self, value: float) -> None:
        self._set_property("Std Deviation", f"{value}")

    @property
    @min_aedt_version("2025.2")
    def include_rain_attenuation(self) -> bool:
        """Adds a margin for rain attenuation to the computed coupling.

        Value should be 'true' or 'false'.

        Examples
        --------
        >>> from ansys.aedt.core import Emit
        >>> app = Emit()
        >>> rev = app.results.get_revision()
        >>> cpl = rev.get_coupling_data_node()
        >>> ereg = cpl.add_erceg_coupling()
        >>> ereg.include_rain_attenuation = True

        """
        val = self._get_property("Include Rain Attenuation")
        return val == "true"

    @include_rain_attenuation.setter
    @min_aedt_version("2025.2")
    def include_rain_attenuation(self, value: bool) -> None:
        self._set_property("Include Rain Attenuation", f"{str(value).lower()}")

    @property
    @min_aedt_version("2025.2")
    def rain_availability(self) -> float:
        """Rain Availability.

        Percentage of time attenuation due to range is < computed margin (range
        from 99-99.999%).

        Value should be between 99 and 99.999.

        Examples
        --------
        >>> from ansys.aedt.core import Emit
        >>> app = Emit()
        >>> rev = app.results.get_revision()
        >>> cpl = rev.get_coupling_data_node()
        >>> ereg = cpl.add_erceg_coupling()
        >>> ereg.rain_availability = 99

        """
        val = self._get_property("Rain Availability")
        return float(val)

    @rain_availability.setter
    @min_aedt_version("2025.2")
    def rain_availability(self, value: float) -> None:
        self._set_property("Rain Availability", f"{value}")

    @property
    @min_aedt_version("2025.2")
    def rain_rate(self) -> float:
        """Rain rate (mm/hr) exceeded for 0.01% of the time.

        Value should be between 0.0 and 1000.0.

        Examples
        --------
        >>> from ansys.aedt.core import Emit
        >>> app = Emit()
        >>> rev = app.results.get_revision()
        >>> cpl = rev.get_coupling_data_node()
        >>> ereg = cpl.add_erceg_coupling()
        >>> ereg.rain_rate = 0.0

        """
        val = self._get_property("Rain Rate")
        return float(val)

    @rain_rate.setter
    @min_aedt_version("2025.2")
    def rain_rate(self, value: float) -> None:
        self._set_property("Rain Rate", f"{value}")

    @property
    @min_aedt_version("2025.2")
    def polarization_tilt_angle(self) -> float:
        """Polarization Tilt Angle.

        Polarization tilt angle of the transmitted signal relative to the
        horizontal.

        Value should be between 0.0 and 180.0.

        Examples
        --------
        >>> from ansys.aedt.core import Emit
        >>> app = Emit()
        >>> rev = app.results.get_revision()
        >>> cpl = rev.get_coupling_data_node()
        >>> ereg = cpl.add_erceg_coupling()
        >>> ereg.polarization_tilt_angle = 0.0

        """
        val = self._get_property("Polarization Tilt Angle")
        return float(val)

    @polarization_tilt_angle.setter
    @min_aedt_version("2025.2")
    def polarization_tilt_angle(self, value: float) -> None:
        self._set_property("Polarization Tilt Angle", f"{value}")

    @property
    @min_aedt_version("2025.2")
    def include_atmospheric_absorption(self) -> bool:
        """Include Atmospheric Absorption.

        Adds a margin for atmospheric absorption due to oxygen/water vapor to
        the computed coupling.

        Value should be 'true' or 'false'.

        Examples
        --------
        >>> from ansys.aedt.core import Emit
        >>> app = Emit()
        >>> rev = app.results.get_revision()
        >>> cpl = rev.get_coupling_data_node()
        >>> ereg = cpl.add_erceg_coupling()
        >>> ereg.include_atmospheric_absorption = True

        """
        val = self._get_property("Include Atmospheric Absorption")
        return val == "true"

    @include_atmospheric_absorption.setter
    @min_aedt_version("2025.2")
    def include_atmospheric_absorption(self, value: bool) -> None:
        self._set_property("Include Atmospheric Absorption", f"{str(value).lower()}")

    @property
    @min_aedt_version("2025.2")
    def temperature(self) -> float:
        """Air temperature in degrees Celsius.

        Value should be between -273.0 and 100.0.

        Examples
        --------
        >>> from ansys.aedt.core import Emit
        >>> app = Emit()
        >>> rev = app.results.get_revision()
        >>> cpl = rev.get_coupling_data_node()
        >>> ereg = cpl.add_erceg_coupling()
        >>> ereg.temperature = -273.0

        """
        val = self._get_property("Temperature")
        return float(val)

    @temperature.setter
    @min_aedt_version("2025.2")
    def temperature(self, value: float) -> None:
        self._set_property("Temperature", f"{value}")

    @property
    @min_aedt_version("2025.2")
    def total_air_pressure(self) -> float:
        """Total air pressure.

        Value should be between 0.0 and 2000.0.

        Examples
        --------
        >>> from ansys.aedt.core import Emit
        >>> app = Emit()
        >>> rev = app.results.get_revision()
        >>> cpl = rev.get_coupling_data_node()
        >>> ereg = cpl.add_erceg_coupling()
        >>> ereg.total_air_pressure = 0.0

        """
        val = self._get_property("Total Air Pressure")
        return float(val)

    @total_air_pressure.setter
    @min_aedt_version("2025.2")
    def total_air_pressure(self, value: float) -> None:
        self._set_property("Total Air Pressure", f"{value}")

    @property
    @min_aedt_version("2025.2")
    def water_vapor_concentration(self) -> float:
        """Water vapor concentration.

        Value should be between 0.0 and 2000.0.

        Examples
        --------
        >>> from ansys.aedt.core import Emit
        >>> app = Emit()
        >>> rev = app.results.get_revision()
        >>> cpl = rev.get_coupling_data_node()
        >>> ereg = cpl.add_erceg_coupling()
        >>> ereg.water_vapor_concentration = 0.0

        """
        val = self._get_property("Water Vapor Concentration")
        return float(val)

    @water_vapor_concentration.setter
    @min_aedt_version("2025.2")
    def water_vapor_concentration(self, value: float) -> None:
        self._set_property("Water Vapor Concentration", f"{value}")
