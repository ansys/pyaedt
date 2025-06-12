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


class TopologyType(Enum):
    """Provides an enum of distributed topologies.

    **Attributes:**

    - LUMPED_TRANSLATION: Represents lumped translation topology.
    - INDUCTOR_TRANSLATION: Represents inductor translation topology.
    - STEPPED_IMPEDANCE: Represents stepped impedance topology.
    - COUPLED_SEGMENTS: Represents coupled segments topology.
    - SPACED_STUBS: Represents spaced stubs topology.
    - SHUNT_STUB_RESONATORS: Represents shunt stub resonators topology.
    - OPEN_STUB_RESONATORS: Represents open stub resonators topology.
    - PARALLEL_EDGE_COUPLED: Represents parallel edge coupled topology.
    - HAIRPIN: Represents hairpin topology.
    - MINIATURE_HAIRPIN: Represents miniature hairpin topology.
    - RING_RESONATORS: Represents ring resonators topology.
    - INTERDIGITAL: Represents interdigital topology.
    - COMBLINE: Represents combline topology.
    - DUAL_RESONATORS: Represents dual resonators topology.
    - SPACED_DUAL_RESONATORS: Represents spaced dual resonators topology.
    - NOTCH_RESONATORs: Represents notch resonators topology.
    """

    LUMPED_TRANSLATION = 0
    INDUCTOR_TRANSLATION = 1
    STEPPED_IMPEDANCE = 2
    COUPLED_SEGMENTS = 3
    SPACED_STUBS = 4
    SHUNT_STUB_RESONATORS = 5
    OPEN_STUB_RESONATORS = 6
    PARALLEL_EDGE_COUPLED = 7
    HAIRPIN = 8
    MINIATURE_HAIRPIN = 9
    RING_RESONATOR = 10
    INTERDIGITAL = 11
    COMBLINE = 12
    DUAL_RESONATORS = 13
    SPACED_DUAL_RESONATORS = 14
    NOTCH_RESONATORS = 15


class TapPosition(Enum):
    """Provides an enum of position of tap points of ``Miniature Hairpin`` and ``Ring Resonator`` topologies.

    **Attributes:**

    - AUTO: Represents an automatic tap position.
    - BACK: Represents a tap position at the back of the ending resonator.
    - SIDES: Represents tap positions at the sides of the ending resonator.
    - CORNER: Represents tap positions at the corners of the ending resonator.
    """

    AUTO = 0
    BACK = 1
    SIDES = 2
    CORNER = 3


class DistributedTopology:
    """Defines topology parameters of distributed filters.

    This class allows you to define and modify the topology parameters of distributed filters.
    """

    def __init__(self):
        self._dll = ansys.aedt.core.filtersolutions_core._dll_interface()._dll
        self._dll_interface = ansys.aedt.core.filtersolutions_core._dll_interface()
        self._define_topology_dll_functions()

    def _define_topology_dll_functions(self):
        """Define C++ API DLL functions."""
        self._dll.setDistributedTopology.argtype = c_char_p
        self._dll.setDistributedTopology.restype = int
        self._dll.getDistributedTopology.argtypes = [c_char_p, c_int]
        self._dll.getDistributedTopology.restype = int

        self._dll.setDistributedSourceResistance.argtype = c_char_p
        self._dll.setDistributedSourceResistance.restype = c_int
        self._dll.getDistributedSourceResistance.argtypes = [c_char_p, c_int]
        self._dll.getDistributedSourceResistance.restype = c_int

        self._dll.setDistributedLoadResistance.argtype = c_char_p
        self._dll.setDistributedLoadResistance.restype = c_int
        self._dll.getDistributedLoadResistance.argtypes = [c_char_p, c_int]
        self._dll.getDistributedLoadResistance.restype = c_int

        self._dll.setDistributedFirstElementShunt.argtype = c_bool
        self._dll.setDistributedFirstElementShunt.restype = c_int
        self._dll.getDistributedFirstElementShunt.argtype = POINTER(c_bool)
        self._dll.getDistributedFirstElementShunt.restype = c_int

        self._dll.setDistributedFirstElementFat.argtype = c_bool
        self._dll.setDistributedFirstElementFat.restype = c_int
        self._dll.getDistributedFirstElementFat.argtype = POINTER(c_bool)
        self._dll.getDistributedFirstElementFat.restype = c_int

        self._dll.setDistributedSeriesCaps.argtype = c_bool
        self._dll.setDistributedSeriesCaps.restype = c_int
        self._dll.getDistributedSeriesCaps.argtype = POINTER(c_bool)
        self._dll.getDistributedSeriesCaps.restype = c_int

        self._dll.setDistributedCombineStubs.argtype = c_bool
        self._dll.setDistributedCombineStubs.restype = c_int
        self._dll.getDistributedCombineStubs.argtype = POINTER(c_bool)
        self._dll.getDistributedCombineStubs.restype = c_int

        self._dll.setDistributedCoupledLines.argtype = c_bool
        self._dll.setDistributedCoupledLines.restype = c_int
        self._dll.getDistributedCoupledLines.argtype = POINTER(c_bool)
        self._dll.getDistributedCoupledLines.restype = c_int

        self._dll.setDistributedQuickOptimize.argtype = c_bool
        self._dll.setDistributedQuickOptimize.restype = c_int
        self._dll.getDistributedQuickOptimize.argtype = POINTER(c_bool)
        self._dll.getDistributedQuickOptimize.restype = c_int

        self._dll.setDistributedEnableExtensions.argtype = c_bool
        self._dll.setDistributedEnableExtensions.restype = c_int
        self._dll.getDistributedEnableExtensions.argtype = POINTER(c_bool)
        self._dll.getDistributedEnableExtensions.restype = c_int

        self._dll.setDistributedEqualWidthApprox.argtype = c_bool
        self._dll.setDistributedEqualWidthApprox.restype = c_int
        self._dll.getDistributedEqualWidthApprox.argtype = POINTER(c_bool)
        self._dll.getDistributedEqualWidthApprox.restype = c_int

        self._dll.setDistributedOpenStubGround.argtype = c_bool
        self._dll.setDistributedOpenStubGround.restype = c_int
        self._dll.getDistributedOpenStubGround.argtype = POINTER(c_bool)
        self._dll.getDistributedOpenStubGround.restype = c_int

        self._dll.setDistributedGroundSideLeft.argtype = c_bool
        self._dll.setDistributedGroundSideLeft.restype = c_int
        self._dll.getDistributedGroundSideLeft.argtype = POINTER(c_bool)
        self._dll.getDistributedGroundSideLeft.restype = c_int

        self._dll.setDistributedEqualStubWidths.argtype = c_bool
        self._dll.setDistributedEqualStubWidths.restype = c_int
        self._dll.getDistributedEqualStubWidths.argtype = POINTER(c_bool)
        self._dll.getDistributedEqualStubWidths.restype = c_int

        self._dll.setEnableDistributedCenterImpedance.argtype = c_bool
        self._dll.setEnableDistributedCenterImpedance.restype = c_int
        self._dll.getEnableDistributedCenterImpedance.argtype = POINTER(c_bool)
        self._dll.getEnableDistributedCenterImpedance.restype = c_int

        self._dll.setDistributedCenterImpedance.argtype = c_char_p
        self._dll.setDistributedCenterImpedance.restype = c_int
        self._dll.getDistributedCenterImpedance.argtypes = [c_char_p, c_int]
        self._dll.getDistributedCenterImpedance.restype = c_int

        self._dll.setDistributedTapped.argtype = c_bool
        self._dll.setDistributedTapped.restype = c_int
        self._dll.getDistributedTapped.argtype = POINTER(c_bool)
        self._dll.getDistributedTapped.restype = c_int

        self._dll.setDistributedPinned.argtype = c_bool
        self._dll.setDistributedPinned.restype = c_int
        self._dll.getDistributedPinned.argtype = POINTER(c_bool)
        self._dll.getDistributedPinned.restype = c_int

        self._dll.setDistributedStubTaps.argtype = c_bool
        self._dll.setDistributedStubTaps.restype = c_int
        self._dll.getDistributedStubTaps.argtype = POINTER(c_bool)
        self._dll.getDistributedStubTaps.restype = c_int

        self._dll.setDistributedViaEnds.argtype = c_bool
        self._dll.setDistributedViaEnds.restype = c_int
        self._dll.getDistributedViaEnds.argtype = POINTER(c_bool)
        self._dll.getDistributedViaEnds.restype = c_int

        self._dll.setEnableDistributedLineWidth.argtype = c_bool
        self._dll.setEnableDistributedLineWidth.restype = c_int
        self._dll.getEnableDistributedLineWidth.argtype = POINTER(c_bool)
        self._dll.getEnableDistributedLineWidth.restype = c_int

        self._dll.setDistributedLineWidth.argtype = c_char_p
        self._dll.setDistributedLineWidth.restype = c_int
        self._dll.getDistributedLineWidth.argtypes = [c_char_p, c_int]
        self._dll.getDistributedLineWidth.restype = c_int

        self._dll.setEnableDistributedResonatorRotationAngle.argtype = c_bool
        self._dll.setEnableDistributedResonatorRotationAngle.restype = c_int
        self._dll.getEnableDistributedResonatorRotationAngle.argtype = POINTER(c_bool)
        self._dll.getEnableDistributedResonatorRotationAngle.restype = c_int

        self._dll.setDistributedResonatorRotationAngle.argtype = c_char_p
        self._dll.setDistributedResonatorRotationAngle.restype = c_int
        self._dll.getDistributedResonatorRotationAngle.argtypes = [c_char_p, c_int]
        self._dll.getDistributedResonatorRotationAngle.restype = c_int

        self._dll.setDistributedMiteredCorners.argtype = c_bool
        self._dll.setDistributedMiteredCorners.restype = c_int
        self._dll.getDistributedMiteredCorners.argtype = POINTER(c_bool)
        self._dll.getDistributedMiteredCorners.restype = c_int

        self._dll.setEnableDistributedHGapWidth.argtype = c_bool
        self._dll.setEnableDistributedHGapWidth.restype = c_int
        self._dll.getEnableDistributedHGapWidth.argtype = POINTER(c_bool)
        self._dll.getEnableDistributedHGapWidth.restype = c_int

        self._dll.setDistributedHGapWidth.argtype = c_char_p
        self._dll.setDistributedHGapWidth.restype = c_int
        self._dll.getDistributedHGapWidth.argtypes = [c_char_p, c_int]
        self._dll.getDistributedHGapWidth.restype = c_int

        self._dll.setEnableDistributedRHGapWidth.argtype = c_bool
        self._dll.setEnableDistributedRHGapWidth.restype = c_int
        self._dll.getEnableDistributedRHGapWidth.argtype = POINTER(c_bool)
        self._dll.getEnableDistributedRHGapWidth.restype = c_int

        self._dll.setDistributedRHGapWidth.argtype = c_char_p
        self._dll.setDistributedRHGapWidth.restype = c_int
        self._dll.getDistributedRHGapWidth.argtypes = [c_char_p, c_int]
        self._dll.getDistributedRHGapWidth.restype = c_int

        self._dll.setDistributedTuningExtensionValue.argtype = c_char_p
        self._dll.setDistributedTuningExtensionValue.restype = c_int
        self._dll.getDistributedTuningExtensionValue.argtypes = [c_char_p, c_int]
        self._dll.getDistributedTuningExtensionValue.restype = c_int

        self._dll.setDistributedTuningType1.argtype = c_bool
        self._dll.setDistributedTuningType1.restype = c_int
        self._dll.getDistributedTuningType1.argtype = POINTER(c_bool)
        self._dll.getDistributedTuningType1.restype = c_int

        self._dll.setDistributedTapPosition.argtype = c_char_p
        self._dll.setDistributedTapPosition.restype = c_int
        self._dll.getDistributedTapPosition.argtypes = [c_char_p, c_int]
        self._dll.getDistributedTapPosition.restype = c_int

        self._dll.setDistributedWideBand.argtype = c_bool
        self._dll.setDistributedWideBand.restype = c_int
        self._dll.getDistributedWideBand.argtype = POINTER(c_bool)
        self._dll.getDistributedWideBand.restype = c_int

        self._dll.setDistributedOpenEnds.argtype = c_bool
        self._dll.setDistributedOpenEnds.restype = c_int
        self._dll.getDistributedOpenEnds.argtype = POINTER(c_bool)
        self._dll.getDistributedOpenEnds.restype = c_int

        self._dll.setDistributedHalfLengthFrequency.argtype = c_char_p
        self._dll.setDistributedHalfLengthFrequency.restype = c_int
        self._dll.getDistributedHalfLengthFrequency.argtypes = [c_char_p, c_int]
        self._dll.getDistributedHalfLengthFrequency.restype = c_int

        self._dll.setEnableDistributedQuarterLengthFrequency.argtype = c_bool
        self._dll.setEnableDistributedQuarterLengthFrequency.restype = c_int
        self._dll.getEnableDistributedQuarterLengthFrequency.argtype = POINTER(c_bool)
        self._dll.getEnableDistributedQuarterLengthFrequency.restype = c_int

        self._dll.setDistributedQuarterLengthFrequency.argtype = c_char_p
        self._dll.setDistributedQuarterLengthFrequency.restype = c_int
        self._dll.getDistributedQuarterLengthFrequency.argtypes = [c_char_p, c_int]
        self._dll.getDistributedQuarterLengthFrequency.restype = c_int

        self._dll.getDistributedNetlistSize.argtype = POINTER(c_int)
        self._dll.getDistributedNetlistSize.restype = c_int
        self._dll.getDistributedNetlist.argtypes = [c_char_p, c_int]
        self._dll.getDistributedNetlist.restype = c_int

    @property
    def topology_type(self) -> TopologyType:
        """Topology type of the distributed filter. The default is ``LUMPED_TRANSLATION``.
        The ``TopologyType`` enum provides a list of all classes.

        Returns
        -------
        :enum:`TopologyType`
        """
        type_string = self._dll_interface.get_string(self._dll.getDistributedTopology)
        return self._dll_interface.string_to_enum(TopologyType, type_string)

    @topology_type.setter
    def topology_type(self, topology_type: TopologyType):
        if topology_type:
            string_value = self._dll_interface.enum_to_string(topology_type)
            self._dll_interface.set_string(self._dll.setDistributedTopology, string_value)

    @property
    def source_resistance(self) -> str:
        """Source resistance. The default is ``50``.

        Returns
        -------
        str
        """
        source_resistance_string = self._dll_interface.get_string(self._dll.getDistributedSourceResistance)
        return source_resistance_string

    @source_resistance.setter
    def source_resistance(self, source_resistance_string):
        self._dll_interface.set_string(self._dll.setDistributedSourceResistance, source_resistance_string)

    @property
    def load_resistance(self) -> str:
        """Load resistance. The default is ``50``.

        Returns
        -------
        str
        """
        load_resistance_string = self._dll_interface.get_string(self._dll.getDistributedLoadResistance)
        return load_resistance_string

    @load_resistance.setter
    def load_resistance(self, load_resistance_string):
        self._dll_interface.set_string(self._dll.setDistributedLoadResistance, load_resistance_string)

    @property
    def first_shunt(self) -> bool:
        """Flag indicating if shunt elements are first in the synthesized circuit.
        This parameter is applicable for the ``Lumped Translation``, ``Inductor Translation``,
        and ``Coupled Segments`` topologies. If ``False``, series elements are first.

        Returns
        -------
        bool
        """
        first_shunt = c_bool()
        status = self._dll.getDistributedFirstElementShunt(byref(first_shunt))
        self._dll_interface.raise_error(status)
        return bool(first_shunt.value)

    @first_shunt.setter
    def first_shunt(self, first_shunt: bool):
        status = self._dll.setDistributedFirstElementShunt(first_shunt)
        self._dll_interface.raise_error(status)

    @property
    def first_fat(self) -> bool:
        """Flag indicating if fat segments are first in the synthesized circuit.
        This parameter is applicable for the ``Stepped Impedance`` topology.
        If ``False``, thin segments are first.

        Returns
        -------
        bool
        """
        first_fat = c_bool()
        status = self._dll.getDistributedFirstElementFat(byref(first_fat))
        self._dll_interface.raise_error(status)
        return bool(first_fat.value)

    @first_fat.setter
    def first_fat(self, first_fat: bool):
        status = self._dll.setDistributedFirstElementFat(first_fat)
        self._dll_interface.raise_error(status)

    @property
    def use_series_caps(self) -> bool:
        """Flag indicating if lumped capacitors and inductor segments are implemented as series LC segments.
        Series capacitors enable capacitive coupling between resonators, which can be achieved through either
        series capacitors or coupled transmission lines.
        This parameter is applicable for the ``Lumped Translation``and ``Inductor Translation`` topologies
        of band pass and high pass filters, and ``Dual Resonator`` topology of band pass filters.

        Returns
        -------
        bool
        """
        use_series_caps = c_bool()
        status = self._dll.getDistributedSeriesCaps(byref(use_series_caps))
        self._dll_interface.raise_error(status)
        return bool(use_series_caps.value)

    @use_series_caps.setter
    def use_series_caps(self, use_series_caps: bool):
        status = self._dll.setDistributedSeriesCaps(use_series_caps)
        self._dll_interface.raise_error(status)

    @property
    def combine_stubs(self) -> bool:
        """Flag indicating if resonators are created with only one stub.
        This parameter is applicable for the ``Lumped Translation``and ``Inductor Translation`` topologies
        of band pass and band stop filters, and ``Dual Resonator`` and ``Spaced Dual Resonator`` topologies
        of band pass filters.

        Returns
        -------
        bool
        """
        combine_stubs = c_bool()
        status = self._dll.getDistributedCombineStubs(byref(combine_stubs))
        self._dll_interface.raise_error(status)
        return bool(combine_stubs.value)

    @combine_stubs.setter
    def combine_stubs(self, combine_stubs: bool):
        status = self._dll.setDistributedCombineStubs(combine_stubs)
        self._dll_interface.raise_error(status)

    @property
    def use_coupled_lines(self) -> bool:
        """Flag indicating if coupled segments are used between stubs to enable capacitive coupling between resonators,
        which can be achieved through either series capacitors or coupled transmission lines.
        This parameter is applicable for the ``Lumped Translation``, ``Inductor Translation``, and ``Dual Resonator``
        topologies of band pass filters.

        Returns
        -------
        bool
        """
        use_coupled_lines = c_bool()
        status = self._dll.getDistributedCoupledLines(byref(use_coupled_lines))
        self._dll_interface.raise_error(status)
        return bool(use_coupled_lines.value)

    @use_coupled_lines.setter
    def use_coupled_lines(self, use_coupled_lines: bool):
        status = self._dll.setDistributedCoupledLines(use_coupled_lines)
        self._dll_interface.raise_error(status)

    @property
    def equal_width_approx(self) -> bool:
        """Flag indicating if all stubs are set to equal width.
        This parameter is applicable for the ``Interdigital``, ``Combline`` topologies of
        band pass filters, and ``Notch Resonators`` topology of band stop filters.

        Returns
        -------
        bool
        """
        equal_width_approx = c_bool()
        status = self._dll.getDistributedEqualWidthApprox(byref(equal_width_approx))
        self._dll_interface.raise_error(status)
        return bool(equal_width_approx.value)

    @equal_width_approx.setter
    def equal_width_approx(self, equal_width_approx: bool):
        status = self._dll.setDistributedEqualWidthApprox(equal_width_approx)
        self._dll_interface.raise_error(status)

    @property
    def open_stub_ground(self) -> bool:
        """Flag indicating if quarter length open stubs are implemented to simulate ground.
        This parameter is applicable for the ``Notch Resonators`` topology of band stop filters.

        Returns
        -------
        bool
        """
        open_stub_ground = c_bool()
        status = self._dll.getDistributedOpenStubGround(byref(open_stub_ground))
        self._dll_interface.raise_error(status)
        return bool(open_stub_ground.value)

    @open_stub_ground.setter
    def open_stub_ground(self, open_stub_ground: bool):
        status = self._dll.setDistributedOpenStubGround(open_stub_ground)
        self._dll_interface.raise_error(status)

    @property
    def left_ground_side(self) -> bool:
        """Flag indicating if grounded pins are placed on left side.
        This parameter is applicable for the ``Notch Resonators`` topology of band stop filters.
        If ``False``, right side is selected.

        Returns
        -------
        bool
        """
        left_ground_side = c_bool()
        status = self._dll.getDistributedGroundSideLeft(byref(left_ground_side))
        self._dll_interface.raise_error(status)
        return bool(left_ground_side.value)

    @left_ground_side.setter
    def left_ground_side(self, left_ground_side: bool):
        status = self._dll.setDistributedGroundSideLeft(left_ground_side)
        self._dll_interface.raise_error(status)

    @property
    def equal_stub_widths(self) -> bool:
        """Flag indicating if all stubs widths are set with equal.
        This parameter is applicable for the ``Shunt Stub Resonators`` and
        ``Open Stub Resonators`` topologies of band pass filters.

        Returns
        -------
        bool
        """
        equal_stub_widths = c_bool()
        status = self._dll.getDistributedEqualStubWidths(byref(equal_stub_widths))
        self._dll_interface.raise_error(status)
        return bool(equal_stub_widths.value)

    @equal_stub_widths.setter
    def equal_stub_widths(self, equal_stub_widths: bool):
        status = self._dll.setDistributedEqualStubWidths(equal_stub_widths)
        self._dll_interface.raise_error(status)

    @property
    def center_z0_impedance_enabled(self) -> bool:
        """Flag indicating if set center impedance is enabled.
        If ``True`` the center impedance value is applied to the internal resonators and couplers.

        Returns
        -------
        bool
        """
        center_z0_impedance_enabled = c_bool()
        status = self._dll.getEnableDistributedCenterImpedance(byref(center_z0_impedance_enabled))
        self._dll_interface.raise_error(status)
        return bool(center_z0_impedance_enabled.value)

    @center_z0_impedance_enabled.setter
    def center_z0_impedance_enabled(self, center_z0_impedance_enabled: bool):
        status = self._dll.setEnableDistributedCenterImpedance(center_z0_impedance_enabled)
        self._dll_interface.raise_error(status)

    @property
    def center_z0_impedance(self) -> str:
        """Resonator internal impedance. The default is ``75``.

        This parameter is applicable for the ``Interdigital``, ``Combline``, ``Parallel Edge Coupled``,
        ``Shunt Stub Resonators``, and  ``Open Stub Resonators`` topologies of band pass filters.

        This property is not applicable for ``Shunt Stub Resonators``, and  ``Open Stub Resonators`` topologies
        when the ``equal_stub_widths`` option is enabled.

        This property is not applicable for ``Parallel Edge Coupled`` topology
        when the ``equal_width_conductors`` option is enabled.


        Returns
        -------
        str
        """
        center_z0_impedance_string = self._dll_interface.get_string(self._dll.getDistributedCenterImpedance)
        return center_z0_impedance_string

    @center_z0_impedance.setter
    def center_z0_impedance(self, center_z0_impedance_string):
        self._dll_interface.set_string(self._dll.setDistributedCenterImpedance, center_z0_impedance_string)

    @property
    def equal_width_conductors(self) -> bool:
        """Flag indicating if all stubs are set to equal width.
        This parameter is applicable for the ``Parallel Edge Coupled`` topology of band pass filters.

        Returns
        -------
        bool
        """
        equal_width_conductors = c_bool()
        status = self._dll.getDistributedEqualWidthApprox(byref(equal_width_conductors))
        self._dll_interface.raise_error(status)
        return bool(equal_width_conductors.value)

    @equal_width_conductors.setter
    def equal_width_conductors(self, equal_width_conductors: bool):
        status = self._dll.setDistributedEqualWidthApprox(equal_width_conductors)
        self._dll_interface.raise_error(status)

    @property
    def tapped(self) -> bool:
        """Flag indicating if the outer couplers are removed and the remaining outer couplers are tapped.
        This parameter is applicable for the ``Interdigital``, ``Combline``, and ``Parallel Edge Coupled``
        topologies of band pass filters.

        This property is disabled when the ``pinned`` option is enabled for the ``Parallel Edge Coupled`` topology.

        This property is disabled when the ``wide_band`` option is enabled for the ``Interdigital`` topology.

        Returns
        -------
        bool
        """
        tapped = c_bool()
        status = self._dll.getDistributedTapped(byref(tapped))
        self._dll_interface.raise_error(status)
        return bool(tapped.value)

    @tapped.setter
    def tapped(self, tapped: bool):
        status = self._dll.setDistributedTapped(tapped)
        self._dll_interface.raise_error(status)

    @property
    def pinned(self) -> bool:
        """Flag indicating if the outer couplers are replaced with hairpin resonators.
        This parameter is applicable for the ``Interdigital``, and ``Parallel Edge Coupled``
        topologies of band pass filters.

        This property is disabled when the ``tapped`` option is enabled for the ``Parallel Edge Coupled`` topology.

        This property is only available  when the ``wide_band`` option is enabled for the ``Interdigital`` topology.

        Returns
        -------
        bool
        """
        pinned = c_bool()
        status = self._dll.getDistributedPinned(byref(pinned))
        self._dll_interface.raise_error(status)
        return bool(pinned.value)

    @pinned.setter
    def pinned(self, pinned: bool):
        status = self._dll.setDistributedPinned(pinned)
        self._dll_interface.raise_error(status)

    @property
    def stub_taps(self) -> bool:
        """Flag indicating if vertical stubs are implemented at the tap points.
        This parameter is applicable for the ``Parallel Edge Coupled`` topology.

        This property is when only available ``equal_width_conductors`` option is
        enabled and ``pinned`` option is disabled.

        Returns
        -------
        bool
        """
        stub_taps = c_bool()
        status = self._dll.getDistributedStubTaps(byref(stub_taps))
        self._dll_interface.raise_error(status)
        return bool(stub_taps.value)

    @stub_taps.setter
    def stub_taps(self, stub_taps: bool):
        status = self._dll.setDistributedStubTaps(stub_taps)
        self._dll_interface.raise_error(status)

    @property
    def via_ends(self) -> bool:
        """Flag indicating if resonators are terminated with vias instead of open ends.
        This parameter is applicable for the ``Parallel Edge Coupled`` topology of band pass filters.

        This property is disabled when the ``equal_width_conductors`` option is enabled.

        Returns
        -------
        bool
        """
        via_ends = c_bool()
        status = self._dll.getDistributedViaEnds(byref(via_ends))
        self._dll_interface.raise_error(status)
        return bool(via_ends.value)

    @via_ends.setter
    def via_ends(self, via_ends: bool):
        status = self._dll.setDistributedViaEnds(via_ends)
        self._dll_interface.raise_error(status)

    @property
    def resonator_line_width_enabled(self) -> bool:
        """Flag indicating if resonator line width is enabled.
        If ``True`` the resonator line width value is applied to the internal resonators and couplers.

        Returns
        -------
        bool
        """
        resonator_line_width_enabled = c_bool()
        status = self._dll.getEnableDistributedLineWidth(byref(resonator_line_width_enabled))
        self._dll_interface.raise_error(status)
        return bool(resonator_line_width_enabled.value)

    @resonator_line_width_enabled.setter
    def resonator_line_width_enabled(self, resonator_line_width_enabled: bool):
        status = self._dll.setEnableDistributedLineWidth(resonator_line_width_enabled)
        self._dll_interface.raise_error(status)

    @property
    def resonator_line_width(self) -> str:
        """Line width to set in ``Hairpin``, ``Miniature Hairpin``, and ``Ring Resonator`` topologies
        of band pass filters. The default is ``1.27 mm``.

        Returns
        -------
        str
        """
        resonator_line_width_string = self._dll_interface.get_string(self._dll.getDistributedLineWidth)
        return resonator_line_width_string

    @resonator_line_width.setter
    def resonator_line_width(self, resonator_line_width_string):
        self._dll_interface.set_string(self._dll.setDistributedLineWidth, resonator_line_width_string)

    @property
    def resonator_rotation_angle_enabled(self) -> bool:
        """Flag indicating if resonator rotation angle is enabled.
        If ``True`` the resonator rotation angle value is applied to the layout.

        Returns
        -------
        bool
        """
        resonator_rotation_angle_enabled = c_bool()
        status = self._dll.getEnableDistributedResonatorRotationAngle(byref(resonator_rotation_angle_enabled))
        self._dll_interface.raise_error(status)
        return bool(resonator_rotation_angle_enabled.value)

    @resonator_rotation_angle_enabled.setter
    def resonator_rotation_angle_enabled(self, resonator_rotation_angle_enabled: bool):
        status = self._dll.setEnableDistributedResonatorRotationAngle(resonator_rotation_angle_enabled)
        self._dll_interface.raise_error(status)

    @property
    def resonator_rotation_angle(self) -> str:
        """Net filter rotation angle for the ``Parallel Edge Coupled`` topology of band pass filters in degrees.
        The default is ``0``.

        Returns
        -------
        str
        """
        resonator_rotation_angle_string = self._dll_interface.get_string(self._dll.getDistributedResonatorRotationAngle)
        return resonator_rotation_angle_string

    @resonator_rotation_angle.setter
    def resonator_rotation_angle(self, resonator_rotation_angle_string):
        self._dll_interface.set_string(self._dll.setDistributedResonatorRotationAngle, resonator_rotation_angle_string)

    @property
    def mitered_corners(self) -> bool:
        """Flag indicating if mitered corners are implemented.
        This parameter is applicable for the ``Hairpin``, ``Miniature Hairpin``, and ``Ring Resonator`` topologies
        of band pass filters.

        Returns
        -------
        bool
        """
        mitered_corners = c_bool()
        status = self._dll.getDistributedMiteredCorners(byref(mitered_corners))
        self._dll_interface.raise_error(status)
        return bool(mitered_corners.value)

    @mitered_corners.setter
    def mitered_corners(self, mitered_corners: bool):
        status = self._dll.setDistributedMiteredCorners(mitered_corners)
        self._dll_interface.raise_error(status)

    @property
    def hairpin_gap_width_enabled(self) -> bool:
        """Flag indicating if hairpin gap width is enabled.
        If ``True`` the hairpin gap width value is applied to the ``Hairpin`` legs.

        Returns
        -------
        bool
        """
        hairpin_gap_width_enabled = c_bool()
        status = self._dll.getEnableDistributedHGapWidth(byref(hairpin_gap_width_enabled))
        self._dll_interface.raise_error(status)
        return bool(hairpin_gap_width_enabled.value)

    @hairpin_gap_width_enabled.setter
    def hairpin_gap_width_enabled(self, hairpin_gap_width_enabled: bool):
        status = self._dll.setEnableDistributedHGapWidth(hairpin_gap_width_enabled)
        self._dll_interface.raise_error(status)

    @property
    def hairpin_gap_width(self) -> str:
        """Gap width to set in ``Hairpin`` topology of band pass filters. The default is ``2.54 mm``.

        Returns
        -------
        str
        """
        hairpin_gap_width_string = self._dll_interface.get_string(self._dll.getDistributedHGapWidth)
        return hairpin_gap_width_string

    @hairpin_gap_width.setter
    def hairpin_gap_width(self, hairpin_gap_width_string):
        self._dll_interface.set_string(self._dll.setDistributedHGapWidth, hairpin_gap_width_string)

    @property
    def miniature_hairpin_gap_width_enabled(self) -> bool:
        """Flag indicating if ``Miniature Hairpin`` or ``Ring Resonator`` gap width is enabled.
        If ``True`` the miniature hairpin or ring resonator gap width value is applied to the
        ``Miniature Hairpin``  or ``Ring Resonator`` legs.

        Returns
        -------
        bool
        """
        miniature_hairpin_gap_width_enabled = c_bool()
        status = self._dll.getEnableDistributedRHGapWidth(byref(miniature_hairpin_gap_width_enabled))
        self._dll_interface.raise_error(status)
        return bool(miniature_hairpin_gap_width_enabled.value)

    @miniature_hairpin_gap_width_enabled.setter
    def miniature_hairpin_gap_width_enabled(self, miniature_hairpin_gap_width_enabled: bool):
        status = self._dll.setEnableDistributedRHGapWidth(miniature_hairpin_gap_width_enabled)
        self._dll_interface.raise_error(status)

    @property
    def miniature_hairpin_gap_width(self) -> str:
        """Gap width to set in ``Miniature Hairpin`` topology of band pass filters. The default is ``635 um``.

        Returns
        -------
        str
        """
        miniature_hairpin_gap_width_string = self._dll_interface.get_string(self._dll.getDistributedRHGapWidth)
        return miniature_hairpin_gap_width_string

    @miniature_hairpin_gap_width.setter
    def miniature_hairpin_gap_width(self, miniature_hairpin_gap_width_string):
        self._dll_interface.set_string(self._dll.setDistributedRHGapWidth, miniature_hairpin_gap_width_string)

    @property
    def ring_resonator_gap_width(self) -> str:
        """Gap width to set in ``Ring Resonator`` topology of band pass filters. The default is ``635 um``.

        Returns
        -------
        str
        """
        ring_resonator_gap_width_string = self._dll_interface.get_string(self._dll.getDistributedRHGapWidth)
        return ring_resonator_gap_width_string

    @ring_resonator_gap_width.setter
    def ring_resonator_gap_width(self, ring_resonator_gap_width_string):
        self._dll_interface.set_string(self._dll.setDistributedRHGapWidth, ring_resonator_gap_width_string)

    @property
    def hairpin_extension_length(self) -> str:
        """Extension length to set in ``Hairpin`` topology of band pass filters for tuning purpose.
        The default is ``0 mm``.

        Returns
        -------
        str
        """
        hairpin_extension_length_string = self._dll_interface.get_string(self._dll.getDistributedTuningExtensionValue)
        return hairpin_extension_length_string

    @hairpin_extension_length.setter
    def hairpin_extension_length(self, hairpin_extension_length_string):
        self._dll_interface.set_string(self._dll.setDistributedTuningExtensionValue, hairpin_extension_length_string)

    @property
    def miniature_hairpin_end_curl_extension(self) -> str:
        """End curl extension length to set in ``Miniature Hairpin`` topology of band pass filters for tuning purpose.
        The default is ``0 mm``.

        Returns
        -------
        str
        """
        miniature_hairpin_end_curl_extension_string = self._dll_interface.get_string(
            self._dll.getDistributedTuningExtensionValue
        )
        return miniature_hairpin_end_curl_extension_string

    @miniature_hairpin_end_curl_extension.setter
    def miniature_hairpin_end_curl_extension(self, miniature_hairpin_end_curl_extension_string):
        self._dll_interface.set_string(
            self._dll.setDistributedTuningExtensionValue, miniature_hairpin_end_curl_extension_string
        )

    @property
    def ring_resonator_end_gap_extension(self) -> str:
        """End gap extension length to set in ``Ring Resonator`` topology of band pass filters for tuning purpose.
        The default is ``0 mm``.

        Returns
        -------
        str
        """
        ring_resonator_end_gap_extension_string = self._dll_interface.get_string(
            self._dll.getDistributedTuningExtensionValue
        )
        return ring_resonator_end_gap_extension_string

    @ring_resonator_end_gap_extension.setter
    def ring_resonator_end_gap_extension(self, ring_resonator_end_gap_extension_string):
        self._dll_interface.set_string(
            self._dll.setDistributedTuningExtensionValue, ring_resonator_end_gap_extension_string
        )

    @property
    def tuning_type_1(self) -> bool:
        """Flag indicating if both legs of the outer hairpins are set for tuning in ``Hairpin``
        topology of band pass filters. If ``False``, only the outer legs of the outer hairpins are set.

        Returns
        -------
        bool
        """
        tuning_type_1 = c_bool()
        status = self._dll.getDistributedTuningType1(byref(tuning_type_1))
        self._dll_interface.raise_error(status)
        return bool(tuning_type_1.value)

    @tuning_type_1.setter
    def tuning_type_1(self, tuning_type_1: bool):
        status = self._dll.setDistributedTuningType1(tuning_type_1)
        self._dll_interface.raise_error(status)

    @property
    def tap_position(self) -> TapPosition:
        """Tap position of the tap points in ``Miniature Hairpin`` and ``Ring Resonator``
        topologies of band pass filters. The default is ``AUTO``.
        The ``TapPosition`` enum provides a list of all types.

        Returns
        -------
        :enum:`TapPosition`
        """
        type_string = self._dll_interface.get_string(self._dll.getDistributedTapPosition)
        return self._dll_interface.string_to_enum(TapPosition, type_string)

    @tap_position.setter
    def tap_position(self, tap_position: TapPosition):
        if tap_position:
            string_value = self._dll_interface.enum_to_string(tap_position)
            self._dll_interface.set_string(self._dll.setDistributedTapPosition, string_value)

    @property
    def wide_band(self) -> bool:
        """Flag indicating if ``Interdigital`` topology of band pass filters are optimized for wideband applications.

        Returns
        -------
        bool
        """
        wide_band = c_bool()
        status = self._dll.getDistributedWideBand(byref(wide_band))
        self._dll_interface.raise_error(status)
        return bool(wide_band.value)

    @wide_band.setter
    def wide_band(self, wide_band: bool):
        status = self._dll.setDistributedWideBand(wide_band)
        self._dll_interface.raise_error(status)

    @property
    def open_ends(self) -> bool:
        """Flag indicating if resonators are terminated with open ends instead of vias.
        This parameter is applicable for the ``Interdigital`` topology of band pass filters.

        This property is disabled when the ``wide_band`` option is enabled.

        Returns
        -------
        bool
        """
        open_ends = c_bool()
        status = self._dll.getDistributedOpenEnds(byref(open_ends))
        self._dll_interface.raise_error(status)
        return bool(open_ends.value)

    @open_ends.setter
    def open_ends(self, open_ends: bool):
        status = self._dll.setDistributedOpenEnds(open_ends)
        self._dll_interface.raise_error(status)

    @property
    def combline_half_length_frequency(self) -> str:
        """Half length frequency in ``Combline`` topology of band pass filters where open remains open.
        The default is ``4G``.

        Returns
        -------
        str
        """
        combline_half_length_frequency_string = self._dll_interface.get_string(
            self._dll.getDistributedHalfLengthFrequency
        )
        return combline_half_length_frequency_string

    @combline_half_length_frequency.setter
    def combline_half_length_frequency(self, combline_half_length_frequency_string):
        self._dll_interface.set_string(
            self._dll.setDistributedHalfLengthFrequency, combline_half_length_frequency_string
        )

    @property
    def coupled_segments_quarter_length_frequency_enabled(self) -> bool:
        """Flag indicating if quarter length frequency is enabled.
        If ``True`` the quarter length frequency value is applied to the layout.

        Returns
        -------
        bool
        """
        coupled_segments_quarter_length_frequency_enabled = c_bool()
        status = self._dll.getEnableDistributedQuarterLengthFrequency(
            byref(coupled_segments_quarter_length_frequency_enabled)
        )
        self._dll_interface.raise_error(status)
        return bool(coupled_segments_quarter_length_frequency_enabled.value)

    @coupled_segments_quarter_length_frequency_enabled.setter
    def coupled_segments_quarter_length_frequency_enabled(
        self, coupled_segments_quarter_length_frequency_enabled: bool
    ):
        status = self._dll.setEnableDistributedQuarterLengthFrequency(coupled_segments_quarter_length_frequency_enabled)
        self._dll_interface.raise_error(status)

    @property
    def coupled_segments_quarter_length_frequency(self) -> str:
        """Quarter length frequency in ``Coupled Segments`` topology of band pass filters where open becomes ground.
        The default is ``4G``.

        Returns
        -------
        str
        """
        coupled_segments_quarter_length_frequency_string = self._dll_interface.get_string(
            self._dll.getDistributedQuarterLengthFrequency
        )
        return coupled_segments_quarter_length_frequency_string

    @coupled_segments_quarter_length_frequency.setter
    def coupled_segments_quarter_length_frequency(self, coupled_segments_quarter_length_frequency_string):
        self._dll_interface.set_string(
            self._dll.setDistributedQuarterLengthFrequency, coupled_segments_quarter_length_frequency_string
        )

    def netlist(self):
        """Calculate and generate spice netlist of the synthesized circuit"""
        size = c_int()
        status = self._dll.getDistributedNetlistSize(byref(size))
        self._dll_interface.raise_error(status)
        netlist_string = self._dll_interface.get_string(self._dll.getDistributedNetlist, max_size=size.value)
        return netlist_string

    @property
    def quick_optimize(self) -> bool:
        """Flag indicating if the quick optimization of the synthesized circuit is enabled.
        This option provides a more accurate solution than raw synthesis alone.

        Returns
        -------
        bool
        """
        quick_optimize = c_bool()
        status = self._dll.getDistributedQuickOptimize(byref(quick_optimize))
        self._dll_interface.raise_error(status)
        return bool(quick_optimize.value)

    @quick_optimize.setter
    def quick_optimize(self, quick_optimize: bool):
        status = self._dll.setDistributedQuickOptimize(quick_optimize)
        self._dll_interface.raise_error(status)

    @property
    def resonator_length_extension(self) -> bool:
        """Flag indicating if the resonator length extension for optimization of the synthesized circuit is enabled.
        This parameter is applicable for the ``Interdigital`` topology of band pass filters.

        Returns
        -------
        bool
        """
        resonator_length_extension = c_bool()
        status = self._dll.getDistributedEnableExtensions(byref(resonator_length_extension))
        self._dll_interface.raise_error(status)
        return bool(resonator_length_extension.value)

    @resonator_length_extension.setter
    def resonator_length_extension(self, resonator_length_extension: bool):
        status = self._dll.setDistributedEnableExtensions(resonator_length_extension)
        self._dll_interface.raise_error(status)
