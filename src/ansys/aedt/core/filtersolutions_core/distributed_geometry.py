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

import ansys.aedt.core


class DistributedGeometry:
    """Defines geometry parameters of distributed filters.

    This class allows you to define and modify the layout geometry parameters of distributed filters.
    """

    def __init__(self):
        self._dll = ansys.aedt.core.filtersolutions_core._dll_interface()._dll
        self._dll_interface = ansys.aedt.core.filtersolutions_core._dll_interface()
        self._define_geomtry_dll_functions()

    def _define_geomtry_dll_functions(self):
        """Define C++ API DLL functions."""
        self._dll.setEnableDistributedCapacitorSections.argtype = c_bool
        self._dll.setEnableDistributedCapacitorSections.restype = c_int
        self._dll.getEnableDistributedCapacitorSections.argtype = POINTER(c_bool)
        self._dll.getEnableDistributedCapacitorSections.restype = c_int

        self._dll.setDistributedCapacitorSections.argtype = c_char_p
        self._dll.setDistributedCapacitorSections.restype = int
        self._dll.getDistributedCapacitorSections.argtypes = [c_char_p, c_int]
        self._dll.getDistributedCapacitorSections.restype = int

        self._dll.setEnableDistributedInductorSections.argtype = c_bool
        self._dll.setEnableDistributedInductorSections.restype = c_int
        self._dll.getEnableDistributedInductorSections.argtype = POINTER(c_bool)
        self._dll.getEnableDistributedInductorSections.restype = c_int

        self._dll.setDistributedInductorSections.argtype = c_char_p
        self._dll.setDistributedInductorSections.restype = c_int
        self._dll.getDistributedInductorSections.argtypes = [c_char_p, c_int]
        self._dll.getDistributedInductorSections.restype = c_int

        self._dll.setEnableDistributedSplitHeightRatio.argtype = c_bool
        self._dll.setEnableDistributedSplitHeightRatio.restype = c_int
        self._dll.getEnableDistributedSplitHeightRatio.argtype = POINTER(c_bool)
        self._dll.getEnableDistributedSplitHeightRatio.restype = c_int

        self._dll.setDistributedSplitHeightRatio.argtype = c_char_p
        self._dll.setDistributedSplitHeightRatio.restype = c_int
        self._dll.getDistributedSplitHeightRatio.argtypes = [c_char_p, c_int]
        self._dll.getDistributedSplitHeightRatio.restype = c_int

        self._dll.setDistributedAlternateStubOrientation.argtype = c_bool
        self._dll.setDistributedAlternateStubOrientation.restype = c_int
        self._dll.getDistributedAlternateStubOrientation.argtype = POINTER(c_bool)
        self._dll.getDistributedAlternateStubOrientation.restype = c_int

        self._dll.setDistributedGeometryMaxWidth.argtype = c_char_p
        self._dll.setDistributedGeometryMaxWidth.restype = c_int
        self._dll.getDistributedGeometryMaxWidth.argtypes = [c_char_p, c_int]
        self._dll.getDistributedGeometryMaxWidth.restype = c_int

        self._dll.setDistributedGeometryMinWidth.argtype = c_char_p
        self._dll.setDistributedGeometryMinWidth.restype = c_int
        self._dll.getDistributedGeometryMinWidth.argtypes = [c_char_p, c_int]
        self._dll.getDistributedGeometryMinWidth.restype = c_int

        self._dll.setDistributedGeometryMaxGap.argtype = c_char_p
        self._dll.setDistributedGeometryMaxGap.restype = c_int
        self._dll.getDistributedGeometryMaxGap.argtypes = [c_char_p, c_int]
        self._dll.getDistributedGeometryMaxGap.restype = c_int

        self._dll.setDistributedGeometryMinGap.argtype = c_char_p
        self._dll.setDistributedGeometryMinGap.restype = c_int
        self._dll.getDistributedGeometryMinGap.argtypes = [c_char_p, c_int]
        self._dll.getDistributedGeometryMinGap.restype = c_int

        self._dll.setDistributedApplyLimits.argtype = c_bool
        self._dll.setDistributedApplyLimits.restype = c_int
        self._dll.getDistributedApplyLimits.argtype = POINTER(c_bool)
        self._dll.getDistributedApplyLimits.restype = c_int

        self._dll.setDistributedAdjustLengthOnLimit.argtype = c_bool
        self._dll.setDistributedAdjustLengthOnLimit.restype = c_int
        self._dll.getDistributedAdjustLengthOnLimit.argtype = POINTER(c_bool)
        self._dll.getDistributedAdjustLengthOnLimit.restype = c_int

    @property
    def fixed_width_to_height_ratio_capacitor_sections_enabled(self) -> bool:
        """Flag indicating if the fixed width-to-substrate height ratios for all segments and stubs in the
        translated lumped capacitor sections are enabled.

        Returns
        -------
        bool
        """
        fixed_width_to_height_ratio_capacitor_sections_enabled = c_bool()
        status = self._dll.getEnableDistributedCapacitorSections(
            byref(fixed_width_to_height_ratio_capacitor_sections_enabled)
        )
        self._dll_interface.raise_error(status)
        return bool(fixed_width_to_height_ratio_capacitor_sections_enabled.value)

    @fixed_width_to_height_ratio_capacitor_sections_enabled.setter
    def fixed_width_to_height_ratio_capacitor_sections_enabled(
        self, fixed_width_to_height_ratio_capacitor_sections_enabled: bool
    ):
        status = self._dll.setEnableDistributedCapacitorSections(fixed_width_to_height_ratio_capacitor_sections_enabled)
        self._dll_interface.raise_error(status)

    @property
    def fixed_width_to_height_ratio_capacitor_sections(self) -> str:
        """Fixed width-to-substrate height ratios for all segments and stubs in the
        translated lumped capacitor sections.
        All sections are set to the same width. The default is ``4``.

        Returns
        -------
        str
        """
        fixed_width_to_height_ratio_capacitor_sections_string = self._dll_interface.get_string(
            self._dll.getDistributedCapacitorSections
        )
        return fixed_width_to_height_ratio_capacitor_sections_string

    @fixed_width_to_height_ratio_capacitor_sections.setter
    def fixed_width_to_height_ratio_capacitor_sections(self, fixed_width_to_height_ratio_capacitor_sections_string):
        self._dll_interface.set_string(
            self._dll.setDistributedCapacitorSections, fixed_width_to_height_ratio_capacitor_sections_string
        )

    @property
    def fixed_width_to_height_ratio_inductor_sections_enabled(self) -> bool:
        """Flag indicating if the fixed width-to-substrate height ratios for all segments and stubs in the
        translated lumped inductor sections are enabled.

        Returns
        -------
        bool
        """
        fixed_width_to_height_ratio_inductor_sections_enabled = c_bool()
        status = self._dll.getEnableDistributedInductorSections(
            byref(fixed_width_to_height_ratio_inductor_sections_enabled)
        )
        self._dll_interface.raise_error(status)
        return bool(fixed_width_to_height_ratio_inductor_sections_enabled.value)

    @fixed_width_to_height_ratio_inductor_sections_enabled.setter
    def fixed_width_to_height_ratio_inductor_sections_enabled(
        self, fixed_width_to_height_ratio_inductor_sections_enabled: bool
    ):
        status = self._dll.setEnableDistributedInductorSections(fixed_width_to_height_ratio_inductor_sections_enabled)
        self._dll_interface.raise_error(status)

    @property
    def fixed_width_to_height_ratio_inductor_sections(self) -> str:
        """Fixed width-to-substrate height ratios for all segments and stubs in the
        translated lumped inductor sections.
        All sections are set to the same width. The default is ``0.25``.

        Returns
        -------
        str
        """
        fixed_width_to_height_ratio_inductor_sections_string = self._dll_interface.get_string(
            self._dll.getDistributedInductorSections
        )
        return fixed_width_to_height_ratio_inductor_sections_string

    @fixed_width_to_height_ratio_inductor_sections.setter
    def fixed_width_to_height_ratio_inductor_sections(self, fixed_width_to_height_ratio_inductor_sections_string):
        self._dll_interface.set_string(
            self._dll.setDistributedInductorSections, fixed_width_to_height_ratio_inductor_sections_string
        )

    @property
    def split_wide_stubs_enabled(self) -> bool:
        """Flag indicating if the wide stubs width into two thinner parallel stubs is enabled.

        Returns
        -------
        bool
        """
        split_wide_stubs_enabled = c_bool()
        status = self._dll.getEnableDistributedSplitHeightRatio(byref(split_wide_stubs_enabled))
        self._dll_interface.raise_error(status)
        return bool(split_wide_stubs_enabled.value)

    @split_wide_stubs_enabled.setter
    def split_wide_stubs_enabled(self, split_wide_stubs_enabled: bool):
        status = self._dll.setEnableDistributedSplitHeightRatio(split_wide_stubs_enabled)
        self._dll_interface.raise_error(status)

    @property
    def wide_stubs_width_to_substrate_height_ratio(self) -> str:
        """Stub width to substrate height ratio of stubs to be split into thinner stubs.
        All stubs wider than this ratio will be split.
        This property is not effective for radial and delta stubs. The default is ``0``.

        Returns
        -------
        str
        """
        wide_stubs_width_to_substrate_height_ratio_string = self._dll_interface.get_string(
            self._dll.getDistributedSplitHeightRatio
        )
        return wide_stubs_width_to_substrate_height_ratio_string

    @wide_stubs_width_to_substrate_height_ratio.setter
    def wide_stubs_width_to_substrate_height_ratio(self, wide_stubs_width_to_substrate_height_ratio_string):
        self._dll_interface.set_string(
            self._dll.setDistributedSplitHeightRatio, wide_stubs_width_to_substrate_height_ratio_string
        )

    @property
    def alternate_stub_orientation(self) -> bool:
        """Flag indicating if the alternate vertical orientation of stubs is enabled.
        The orientation alternates between up and down to minimize interference between adjacent stubs.

        Returns
        -------
        bool
        """
        alternate_stub_orientation = c_bool()
        status = self._dll.getDistributedAlternateStubOrientation(byref(alternate_stub_orientation))
        self._dll_interface.raise_error(status)
        return bool(alternate_stub_orientation.value)

    @alternate_stub_orientation.setter
    def alternate_stub_orientation(self, alternate_stub_orientation: bool):
        status = self._dll.setDistributedAlternateStubOrientation(alternate_stub_orientation)
        self._dll_interface.raise_error(status)

    @property
    def max_width(self) -> str:
        """Maximum conductor width of the geometry. The default is ``6.35 mm``.

        Returns
        -------
        str
        """
        max_width_string = self._dll_interface.get_string(self._dll.getDistributedGeometryMaxWidth)
        return max_width_string

    @max_width.setter
    def max_width(self, max_width_string):
        self._dll_interface.set_string(self._dll.setDistributedGeometryMaxWidth, max_width_string)

    @property
    def min_width(self) -> str:
        """Minimum conductor width of the geometry. The default is ``50 um``.

        Returns
        -------
        str
        """
        min_width_string = self._dll_interface.get_string(self._dll.getDistributedGeometryMinWidth)
        return min_width_string

    @min_width.setter
    def min_width(self, min_width_string):
        self._dll_interface.set_string(self._dll.setDistributedGeometryMinWidth, min_width_string)

    @property
    def max_gap(self) -> str:
        """Maximum conductor gap width between conductors of the geometry. The default is ``6.35 mm``.

        Returns
        -------
        str
        """
        max_gap_string = self._dll_interface.get_string(self._dll.getDistributedGeometryMaxGap)
        return max_gap_string

    @max_gap.setter
    def max_gap(self, max_gap_string):
        self._dll_interface.set_string(self._dll.setDistributedGeometryMaxGap, max_gap_string)

    @property
    def min_gap(self) -> str:
        """Minimum conductor gap width between conductors of the geometry. The default is ``50 um``.

        Returns
        -------
        str
        """
        min_gap_string = self._dll_interface.get_string(self._dll.getDistributedGeometryMinGap)
        return min_gap_string

    @min_gap.setter
    def min_gap(self, min_gap_string):
        self._dll_interface.set_string(self._dll.setDistributedGeometryMinGap, min_gap_string)

    @property
    def apply_limits(self) -> bool:
        """Flag indicating if the given geometry minimum and maximum widths and gaps limits are applied.

        Returns
        -------
        bool
        """
        apply_limits = c_bool()
        status = self._dll.getDistributedApplyLimits(byref(apply_limits))
        self._dll_interface.raise_error(status)
        return bool(apply_limits.value)

    @apply_limits.setter
    def apply_limits(self, apply_limits: bool):
        status = self._dll.setDistributedApplyLimits(apply_limits)
        self._dll_interface.raise_error(status)

    @property
    def adjust_length_on_limit(self) -> bool:
        """Flag indicating if the length of all limited stubs and segments are adjusted to maintain
        the desired lumped element impedance. This adjustment is effective for sections simulating
        translated lumped elements.

        Returns
        -------
        bool
        """
        adjust_length_on_limit = c_bool()
        status = self._dll.getDistributedAdjustLengthOnLimit(byref(adjust_length_on_limit))
        self._dll_interface.raise_error(status)
        return bool(adjust_length_on_limit.value)

    @adjust_length_on_limit.setter
    def adjust_length_on_limit(self, adjust_length_on_limit: bool):
        status = self._dll.setDistributedAdjustLengthOnLimit(adjust_length_on_limit)
        self._dll_interface.raise_error(status)
