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


class DistributedRadial:
    """Defines radial parameters of distributed filters.

    This class allows you to define and modify the radial and delta stub parameters of distributed filters.
    These parameter changes are applicable exclusively to low-pass filters that include stub resonators.
    """

    def __init__(self):
        self._dll = ansys.aedt.core.filtersolutions_core._dll_interface()._dll
        self._dll_interface = ansys.aedt.core.filtersolutions_core._dll_interface()
        self._define_radial_dll_functions()

    def _define_radial_dll_functions(self):
        """Define C++ API DLL functions."""
        self._dll.setDistributedRadialStubs.argtype = c_bool
        self._dll.setDistributedRadialStubs.restype = c_int
        self._dll.getDistributedRadialStubs.argtype = POINTER(c_bool)
        self._dll.getDistributedRadialStubs.restype = c_int

        self._dll.setEnableDistributedFixedAngle.argtype = c_bool
        self._dll.setEnableDistributedFixedAngle.restype = c_int
        self._dll.getEnableDistributedFixedAngle.argtype = POINTER(c_bool)
        self._dll.getEnableDistributedFixedAngle.restype = c_int

        self._dll.setDistributedFixedAngle.argtype = c_char_p
        self._dll.setDistributedFixedAngle.restype = int
        self._dll.getDistributedFixedAngle.argtypes = [c_char_p, c_int]
        self._dll.getDistributedFixedAngle.restype = int

        self._dll.setDistributedDeltaStubs.argtype = c_bool
        self._dll.setDistributedDeltaStubs.restype = c_int
        self._dll.getDistributedDeltaStubs.argtype = POINTER(c_bool)
        self._dll.getDistributedDeltaStubs.restype = c_int

        self._dll.setEnableDistributedSplitWideAngle.argtype = c_bool
        self._dll.setEnableDistributedSplitWideAngle.restype = c_int
        self._dll.getEnableDistributedSplitWideAngle.argtype = POINTER(c_bool)
        self._dll.getEnableDistributedSplitWideAngle.restype = c_int

        self._dll.setDistributedSplitWideAngle.argtype = c_char_p
        self._dll.setDistributedSplitWideAngle.restype = c_int
        self._dll.getDistributedSplitWideAngle.argtypes = [c_char_p, c_int]
        self._dll.getDistributedSplitWideAngle.restype = c_int

        self._dll.setEnableDistributedOffsetFromFeedline.argtype = c_bool
        self._dll.setEnableDistributedOffsetFromFeedline.restype = c_int
        self._dll.getEnableDistributedOffsetFromFeedline.argtype = POINTER(c_bool)
        self._dll.getEnableDistributedOffsetFromFeedline.restype = c_int

        self._dll.setDistributedOffsetFromFeedline.argtype = c_char_p
        self._dll.setDistributedOffsetFromFeedline.restype = c_int
        self._dll.getDistributedOffsetFromFeedline.argtypes = [c_char_p, c_int]
        self._dll.getDistributedOffsetFromFeedline.restype = c_int

        self._dll.setDistributedAlternateRadialDeltaOrientation.argtype = c_bool
        self._dll.setDistributedAlternateRadialDeltaOrientation.restype = c_int
        self._dll.getDistributedAlternateRadialDeltaOrientation.argtype = POINTER(c_bool)
        self._dll.getDistributedAlternateRadialDeltaOrientation.restype = c_int

        self._dll.setDistributedAdjustWidthMax.argtype = c_bool
        self._dll.setDistributedAdjustWidthMax.restype = c_int
        self._dll.getDistributedAdjustWidthMax.argtype = POINTER(c_bool)
        self._dll.getDistributedAdjustWidthMax.restype = c_int

        self._dll.setDistributedMaxRadialDeltaAngle.argtype = c_char_p
        self._dll.setDistributedMaxRadialDeltaAngle.restype = c_int
        self._dll.getDistributedMaxRadialDeltaAngle.argtypes = [c_char_p, c_int]
        self._dll.getDistributedMaxRadialDeltaAngle.restype = c_int

        self._dll.setDistributedAdjustLengthMax.argtype = c_bool
        self._dll.setDistributedAdjustLengthMax.restype = c_int
        self._dll.getDistributedAdjustLengthMax.argtype = POINTER(c_bool)
        self._dll.getDistributedAdjustLengthMax.restype = c_int

        self._dll.setDistributedMinRadialDeltaAngle.argtype = c_char_p
        self._dll.setDistributedMinRadialDeltaAngle.restype = c_int
        self._dll.getDistributedMinRadialDeltaAngle.argtypes = [c_char_p, c_int]
        self._dll.getDistributedMinRadialDeltaAngle.restype = c_int

        self._dll.setDistributedApplyLimitsRadialDelta.argtype = c_bool
        self._dll.setDistributedApplyLimitsRadialDelta.restype = c_int
        self._dll.getDistributedApplyLimitsRadialDelta.argtype = POINTER(c_bool)
        self._dll.getDistributedApplyLimitsRadialDelta.restype = c_int

    @property
    def radial_stubs(self) -> bool:
        """Flag indicating if the distributed radial stubs is enabled.
        If true, radial stubs are used for open lines.

        Returns
        -------
        bool
        """
        radial_stubs = c_bool()
        status = self._dll.getDistributedRadialStubs(byref(radial_stubs))
        self._dll_interface.raise_error(status)
        return radial_stubs.value

    @radial_stubs.setter
    def radial_stubs(self, radial_stubs: bool):
        status = self._dll.setDistributedRadialStubs(radial_stubs)
        self._dll_interface.raise_error(status)

    @property
    def fixed_angle_enabled(self) -> bool:
        """Flag indicating if the fixed angle for all radial or delta stubs is enabled.

        Returns
        -------
        bool
        """
        fixed_angle_enabled = c_bool()
        status = self._dll.getEnableDistributedFixedAngle(byref(fixed_angle_enabled))
        self._dll_interface.raise_error(status)
        return fixed_angle_enabled.value

    @fixed_angle_enabled.setter
    def fixed_angle_enabled(self, fixed_angle_enabled: bool):
        status = self._dll.setEnableDistributedFixedAngle(fixed_angle_enabled)
        self._dll_interface.raise_error(status)

    @property
    def fixed_angle(self) -> str:
        """Fixed angle in degrees for all radial or delta stubs. The default is ``90``.

        Returns
        -------
        str
        """
        fixed_angle_string = self._dll_interface.get_string(self._dll.getDistributedFixedAngle)
        return fixed_angle_string

    @fixed_angle.setter
    def fixed_angle(self, fixed_angle_string: str):
        self._dll_interface.set_string(self._dll.setDistributedFixedAngle, fixed_angle_string)

    @property
    def delta_stubs(self) -> bool:
        """Flag indicating if the distributed delta stubs is enabled.
        If true, delta stubs are used for open lines.

        Returns
        -------
        bool
        """
        delta_stubs = c_bool()
        status = self._dll.getDistributedDeltaStubs(byref(delta_stubs))
        self._dll_interface.raise_error(status)
        return delta_stubs.value

    @delta_stubs.setter
    def delta_stubs(self, delta_stubs: bool):
        status = self._dll.setDistributedDeltaStubs(delta_stubs)
        self._dll_interface.raise_error(status)

    @property
    def split_wide_angle_enabled(self) -> bool:
        """Flag indicating if the splitting of the wide radial or delta stubs is enabled.

        Returns
        -------
        bool
        """
        split_wide_angle_enabled = c_bool()
        status = self._dll.getEnableDistributedSplitWideAngle(byref(split_wide_angle_enabled))
        self._dll_interface.raise_error(status)
        return split_wide_angle_enabled.value

    @split_wide_angle_enabled.setter
    def split_wide_angle_enabled(self, split_wide_angle_enabled: bool):
        status = self._dll.setEnableDistributedSplitWideAngle(split_wide_angle_enabled)
        self._dll_interface.raise_error(status)

    @property
    def split_wide_angle(self) -> str:
        """Angle in degrees that triggers the splitting of the wide radial or delta stubs.

        This parameter controls the splitting of wide stubs into upper and lower sections,
        which helps reduce the overall stub thickness.
        Stubs wider than the specified angle will be split.
        A default value of ``0`` ensures that all stubs are split.

        Returns
        -------
        str
        """
        split_wide_angle_string = self._dll_interface.get_string(self._dll.getDistributedSplitWideAngle)
        return split_wide_angle_string

    @split_wide_angle.setter
    def split_wide_angle(self, split_wide_angle_string: str):
        self._dll_interface.set_string(self._dll.setDistributedSplitWideAngle, split_wide_angle_string)

    @property
    def offset_from_feedline_enabled(self) -> bool:
        """Flag indicating if the distance from the radial or delta stub base to the feedline is enabled.

        Returns
        -------
        bool
        """
        offset_from_feedline_enabled = c_bool()
        status = self._dll.getEnableDistributedOffsetFromFeedline(byref(offset_from_feedline_enabled))
        self._dll_interface.raise_error(status)
        return offset_from_feedline_enabled.value

    @offset_from_feedline_enabled.setter
    def offset_from_feedline_enabled(self, offset_from_feedline_enabled: bool):
        status = self._dll.setEnableDistributedOffsetFromFeedline(offset_from_feedline_enabled)
        self._dll_interface.raise_error(status)

    @property
    def offset_from_feedline(self) -> str:
        """Distance from radial or delta stub base to feedline. The default is ``200 um``.

        Returns
        -------
        str
        """
        offset_from_feedline_string = self._dll_interface.get_string(self._dll.getDistributedOffsetFromFeedline)
        return offset_from_feedline_string

    @offset_from_feedline.setter
    def offset_from_feedline(self, offset_from_feedline_string: str):
        self._dll_interface.set_string(self._dll.setDistributedOffsetFromFeedline, offset_from_feedline_string)

    @property
    def alternate_radial_delta_orientation(self) -> bool:
        """Flag indicating if the alternate vertical orientation of radial or delta stubs is enabled.
        The orintation alternates between up and down to minimize interference between adjacent stubs.

        Returns
        -------
        bool
        """
        alternate_radial_delta_orientation = c_bool()
        status = self._dll.getDistributedAlternateRadialDeltaOrientation(byref(alternate_radial_delta_orientation))
        self._dll_interface.raise_error(status)
        return alternate_radial_delta_orientation.value

    @alternate_radial_delta_orientation.setter
    def alternate_radial_delta_orientation(self, alternate_radial_delta_orientation: bool):
        status = self._dll.setDistributedAlternateRadialDeltaOrientation(alternate_radial_delta_orientation)
        self._dll_interface.raise_error(status)

    @property
    def adjust_width_max(self) -> bool:
        """Flag indicating if the adjustment of radial or delta width to the upper angle limit is enabled.

        Returns
        -------
        bool
        """
        adjust_width_max = c_bool()
        status = self._dll.getDistributedAdjustWidthMax(byref(adjust_width_max))
        self._dll_interface.raise_error(status)
        return adjust_width_max.value

    @adjust_width_max.setter
    def adjust_width_max(self, adjust_width_max: bool):
        status = self._dll.setDistributedAdjustWidthMax(adjust_width_max)
        self._dll_interface.raise_error(status)

    @property
    def max_radial_delta_angle(self) -> str:
        """Maximum angle of radial or delta stubs.

        Returns
        -------
        str
        """
        max_radial_delta_angle_string = self._dll_interface.get_string(self._dll.getDistributedMaxRadialDeltaAngle)
        return max_radial_delta_angle_string

    @max_radial_delta_angle.setter
    def max_radial_delta_angle(self, max_radial_delta_angle_string: str):
        self._dll_interface.set_string(self._dll.setDistributedMaxRadialDeltaAngle, max_radial_delta_angle_string)

    @property
    def adjust_length_max(self) -> bool:
        """Flag indicating if the adjustment of radial or delta length to the upper angle limit is enabled.

        Returns
        -------
        bool
        """
        adjust_length_max = c_bool()
        status = self._dll.getDistributedAdjustLengthMax(byref(adjust_length_max))
        self._dll_interface.raise_error(status)
        return adjust_length_max.value

    @adjust_length_max.setter
    def adjust_length_max(self, adjust_length_max: bool):
        status = self._dll.setDistributedAdjustLengthMax(adjust_length_max)
        self._dll_interface.raise_error(status)

    @property
    def min_radial_delta_angle(self) -> str:
        """Minimum angle of radial or delta stubs.

        Returns
        -------
        str
        """
        min_radial_delta_angle_string = self._dll_interface.get_string(self._dll.getDistributedMinRadialDeltaAngle)
        return min_radial_delta_angle_string

    @min_radial_delta_angle.setter
    def min_radial_delta_angle(self, min_radial_delta_angle_string: str):
        self._dll_interface.set_string(self._dll.setDistributedMinRadialDeltaAngle, min_radial_delta_angle_string)

    @property
    def apply_limits_radial_delta(self) -> bool:
        """Flag indicating if the radial or delta minimum and maximum angle limits are applied.

        Returns
        -------
        bool
        """
        apply_limits_radial_delta = c_bool()
        status = self._dll.getDistributedApplyLimitsRadialDelta(byref(apply_limits_radial_delta))
        self._dll_interface.raise_error(status)
        return apply_limits_radial_delta.value

    @apply_limits_radial_delta.setter
    def apply_limits_radial_delta(self, apply_limits_radial_delta: bool):
        status = self._dll.setDistributedApplyLimitsRadialDelta(apply_limits_radial_delta)
        self._dll_interface.raise_error(status)
