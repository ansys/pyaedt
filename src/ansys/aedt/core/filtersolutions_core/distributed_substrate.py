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
from ctypes import create_string_buffer
from typing import Union

import ansys.aedt.core
from ansys.aedt.core.filtersolutions_core.export_to_aedt import SubstrateEr
from ansys.aedt.core.filtersolutions_core.export_to_aedt import SubstrateResistivity
from ansys.aedt.core.filtersolutions_core.export_to_aedt import SubstrateType


class DistributedSubstrate:
    """Defines substrate parameters of distributed filters.

    This class allows you to define and modify the substrate parameters of distributed filters.
    """

    def __init__(self):
        self._dll = ansys.aedt.core.filtersolutions_core._dll_interface()._dll
        self._dll_interface = ansys.aedt.core.filtersolutions_core._dll_interface()
        self._define_substrate_dll_functions()

    def _define_substrate_dll_functions(self):
        """Define C++ API DLL functions."""
        self._dll.setDistributedSubstrateType.argtype = c_int
        self._dll.setDistributedSubstrateType.restype = int
        self._dll.getDistributedSubstrateType.argtype = POINTER(c_int)
        self._dll.getDistributedSubstrateType.restype = int

        self._dll.setDistributedEr.argtype = [c_char_p, c_int]
        self._dll.setDistributedEr.restype = c_int
        self._dll.getDistributedEr.argtype = [c_char_p, POINTER(c_int), c_int]
        self._dll.getDistributedEr.restype = c_int

        self._dll.setDistributedResistivity.argtype = [c_char_p, c_int]
        self._dll.setDistributedResistivity.restype = c_int
        self._dll.getDistributedResistivity.argtype = [c_char_p, POINTER(c_int), c_int]
        self._dll.getDistributedResistivity.restype = c_int

        self._dll.setDistributedLossTangent.argtype = [c_char_p, c_int]
        self._dll.setDistributedLossTangent.restype = c_int
        self._dll.getDistributedLossTangent.argtype = [c_char_p, POINTER(c_int), c_int]
        self._dll.getDistributedLossTangent.restype = c_int

        self._dll.setDistributedConductorThickness.argtype = c_char_p
        self._dll.setDistributedConductorThickness.restype = c_int
        self._dll.getDistributedConductorThickness.argtypes = [c_char_p, c_int]
        self._dll.getDistributedConductorThickness.restype = c_int

        self._dll.setDistributedDielectricHeight.argtype = c_char_p
        self._dll.setDistributedDielectricHeight.restype = c_int
        self._dll.getDistributedDielectricHeight.argtypes = [c_char_p, c_int]
        self._dll.getDistributedDielectricHeight.restype = c_int

        self._dll.setDistributedLowerDielectricHeight.argtype = c_char_p
        self._dll.setDistributedLowerDielectricHeight.restype = c_int
        self._dll.getDistributedLowerDielectricHeight.argtypes = [c_char_p, c_int]
        self._dll.getDistributedLowerDielectricHeight.restype = c_int

        self._dll.setDistributedSuspendDielectricHeight.argtype = c_char_p
        self._dll.setDistributedSuspendDielectricHeight.restype = c_int
        self._dll.getDistributedSuspendDielectricHeight.argtypes = [c_char_p, c_int]
        self._dll.getDistributedSuspendDielectricHeight.restype = c_int

        self._dll.setDistributedCoverHeight.argtype = c_char_p
        self._dll.setDistributedCoverHeight.restype = c_int
        self._dll.getDistributedCoverHeight.argtypes = [c_char_p, c_int]
        self._dll.getDistributedCoverHeight.restype = c_int

        self._dll.setDistributedUnbalancedStripLine.argtype = c_bool
        self._dll.setDistributedUnbalancedStripLine.restype = c_int
        self._dll.getDistributedUnbalancedStripLine.argtype = POINTER(c_bool)
        self._dll.getDistributedUnbalancedStripLine.restype = c_int

        self._dll.setDistributedGroundedCoverAboveLine.argtype = c_bool
        self._dll.setDistributedGroundedCoverAboveLine.restype = c_int
        self._dll.getDistributedGroundedCoverAboveLine.argtype = POINTER(c_bool)
        self._dll.getDistributedGroundedCoverAboveLine.restype = c_int

    @property
    def substrate_type(self) -> SubstrateType:
        """Substrate type of the filter.

        The ``SubstrateType`` enum provides a list of all substrate types.

        Returns
        -------
        :enum:`SubstrateType`
        """
        index = c_int()
        substrate_type_list = list(SubstrateType)
        status = self._dll.getDistributedSubstrateType(byref(index))
        self._dll_interface.raise_error(status)
        substrate_type = substrate_type_list[index.value]
        return substrate_type

    @substrate_type.setter
    def substrate_type(self, substrate_type: SubstrateType):
        status = self._dll.setDistributedSubstrateType(substrate_type.value)
        self._dll_interface.raise_error(status)

    @property
    def substrate_er(self) -> Union[SubstrateType, str]:
        """Substrate's relative permittivity ``Er``.

        The value can be either a string or an instance of the ``SubstrateEr`` enum.
        The default is ``9.8`` for ``SubstrateEr.ALUMINA``.

        Returns
        -------
        Union[SubstrateEr, str]

        """
        substrate_er_index = c_int()
        substrate_er_value_str = create_string_buffer(100)
        status = self._dll.getDistributedEr(substrate_er_value_str, byref(substrate_er_index), 100)
        self._dll_interface.raise_error(status)
        if substrate_er_index.value in [e.value for e in SubstrateEr]:
            return SubstrateEr(substrate_er_index.value)
        else:
            return substrate_er_value_str.value.decode("ascii")

    @substrate_er.setter
    def substrate_er(self, substrate_input):
        if substrate_input in list(SubstrateEr):
            substrate_er_index = SubstrateEr(substrate_input).value
            substrate_er_value = ""
        elif isinstance(substrate_input, str):
            substrate_er_value = substrate_input
            substrate_er_index = -1
        else:
            raise ValueError("Invalid substrate input. Must be a SubstrateEr enum member or a string")

        substrate_er_value_bytes = bytes(substrate_er_value, "ascii")
        status = self._dll.setDistributedEr(substrate_er_value_bytes, substrate_er_index)
        self._dll_interface.raise_error(status)

    @property
    def substrate_resistivity(self) -> Union[SubstrateResistivity, str]:
        """Substrate's resistivity.

        The value can be either a string or an instance of the ``SubstrateResistivity`` enum.
        The default is ``1.43`` for ``SubstrateResistivity.GOLD``.

        Returns
        -------
        Union[SubstrateResistivity, str]
        """
        substrate_resistivity_index = c_int()
        substrate_resistivity_value_str = create_string_buffer(100)
        status = self._dll.getDistributedResistivity(
            substrate_resistivity_value_str, byref(substrate_resistivity_index), 100
        )
        self._dll_interface.raise_error(status)
        if substrate_resistivity_index.value in [e.value for e in SubstrateResistivity]:
            return SubstrateResistivity(substrate_resistivity_index.value)
        else:
            return substrate_resistivity_value_str.value.decode("ascii")

    @substrate_resistivity.setter
    def substrate_resistivity(self, substrate_input):
        if substrate_input in list(SubstrateResistivity):
            substrate_resistivity_index = SubstrateResistivity(substrate_input).value
            substrate_resistivity_value = ""
        elif isinstance(substrate_input, str):
            substrate_resistivity_value = substrate_input
            substrate_resistivity_index = -1
        else:
            raise ValueError("Invalid substrate input. Must be a SubstrateResistivity enum member or a string")
        substrate_resistivity_value_bytes = bytes(substrate_resistivity_value, "ascii")
        status = self._dll.setDistributedResistivity(substrate_resistivity_value_bytes, substrate_resistivity_index)
        self._dll_interface.raise_error(status)

    @property
    def substrate_loss_tangent(self) -> Union[SubstrateEr, str]:
        """Substrate's loss tangent.

        The value can be either a string or an instance of the ``SubstrateEr`` enum.
        The default is ``0.0005`` for ``SubstrateEr.ALUMINA``.

        Returns
        -------
        Union[SubstrateEr, str]
        """
        substrate_loss_tangent_index = c_int()
        substrate_loss_tangent_value_str = create_string_buffer(100)
        status = self._dll.getDistributedLossTangent(
            substrate_loss_tangent_value_str, byref(substrate_loss_tangent_index), 100
        )
        self._dll_interface.raise_error(status)
        if substrate_loss_tangent_index.value in [e.value for e in SubstrateEr]:
            return SubstrateEr(substrate_loss_tangent_index.value)
        else:
            return substrate_loss_tangent_value_str.value.decode("ascii")

    @substrate_loss_tangent.setter
    def substrate_loss_tangent(self, substrate_input):
        if substrate_input in list(SubstrateEr):
            substrate_loss_tangent_index = SubstrateEr(substrate_input).value
            substrate_loss_tangent_value = ""
        elif isinstance(substrate_input, str):
            substrate_loss_tangent_value = substrate_input
            substrate_loss_tangent_index = -1
        else:
            raise ValueError("Invalid substrate input. Must be a SubstrateEr enum member or a string")
        substrate_loss_tangent_value_bytes = bytes(substrate_loss_tangent_value, "ascii")
        status = self._dll.setDistributedLossTangent(substrate_loss_tangent_value_bytes, substrate_loss_tangent_index)
        self._dll_interface.raise_error(status)

    @property
    def substrate_conductor_thickness(self) -> str:
        """Substrate's conductor thickness.

        The default is ``2.54 um``.

        Returns
        -------
        str
        """
        substrate_conductor_thickness_string = self._dll_interface.get_string(
            self._dll.getDistributedConductorThickness
        )
        return substrate_conductor_thickness_string

    @substrate_conductor_thickness.setter
    def substrate_conductor_thickness(self, substrate_conductor_thickness_string):
        self._dll_interface.set_string(self._dll.setDistributedConductorThickness, substrate_conductor_thickness_string)

    @property
    def substrate_dielectric_height(self) -> str:
        """Substrate's dielectric height.

        The default is ``1.27 mm``.

        Returns
        -------
        str
        """
        substrate_dielectric_height_string = self._dll_interface.get_string(self._dll.getDistributedDielectricHeight)
        return substrate_dielectric_height_string

    @substrate_dielectric_height.setter
    def substrate_dielectric_height(self, substrate_dielectric_height_string):
        self._dll_interface.set_string(self._dll.setDistributedDielectricHeight, substrate_dielectric_height_string)

    @property
    def substrate_unbalanced_lower_dielectric_height(self) -> str:
        """Substrate's lower dielectric height for unbalanced stripline substrate type.

        The default is ``1.27 mm``.

        Returns
        -------
        str
        """
        substrate_unbalanced_lower_dielectric_height_string = self._dll_interface.get_string(
            self._dll.getDistributedLowerDielectricHeight
        )
        return substrate_unbalanced_lower_dielectric_height_string

    @substrate_unbalanced_lower_dielectric_height.setter
    def substrate_unbalanced_lower_dielectric_height(self, substrate_unbalanced_lower_dielectric_height_string):
        self._dll_interface.set_string(
            self._dll.setDistributedLowerDielectricHeight, substrate_unbalanced_lower_dielectric_height_string
        )

    @property
    def substrate_suspend_dielectric_height(self) -> str:
        """Substrate's suspend dielectric height above ground plane for suspend and inverted substrate types.

        The default is ``1.27 mm``.

        Returns
        -------
        str
        """
        substrate_suspend_dielectric_height_string = self._dll_interface.get_string(
            self._dll.getDistributedSuspendDielectricHeight
        )
        return substrate_suspend_dielectric_height_string

    @substrate_suspend_dielectric_height.setter
    def substrate_suspend_dielectric_height(self, substrate_suspend_dielectric_height_string):
        self._dll_interface.set_string(
            self._dll.setDistributedSuspendDielectricHeight, substrate_suspend_dielectric_height_string
        )

    @property
    def substrate_cover_height(self) -> str:
        """Substrate's cover height for microstrip, suspend, and inverted substrate types.
        The default is ``6.35 mm``.

        Returns
        -------
        str
        """
        substrate_cover_height_string = self._dll_interface.get_string(self._dll.getDistributedCoverHeight)
        return substrate_cover_height_string

    @substrate_cover_height.setter
    def substrate_cover_height(self, substrate_cover_height_string):
        self._dll_interface.set_string(self._dll.setDistributedCoverHeight, substrate_cover_height_string)

    @property
    def substrate_unbalanced_stripline_enabled(self) -> bool:
        """Flag indicating if the substrate unbalanced stripline is enabled.

        Returns
        -------
        bool
        """
        substrate_unbalanced_stripline_enabled = c_bool()
        status = self._dll.getDistributedUnbalancedStripLine(byref(substrate_unbalanced_stripline_enabled))
        self._dll_interface.raise_error(status)
        return bool(substrate_unbalanced_stripline_enabled.value)

    @substrate_unbalanced_stripline_enabled.setter
    def substrate_unbalanced_stripline_enabled(self, substrate_unbalanced_stripline_enabled: bool):
        status = self._dll.setDistributedUnbalancedStripLine(substrate_unbalanced_stripline_enabled)
        self._dll_interface.raise_error(status)

    @property
    def substrate_cover_height_enabled(self) -> bool:
        """Flag indicating if the substrate cover height is enabled.

        Returns
        -------
        bool
        """
        substrate_cover_height_enabled = c_bool()
        status = self._dll.getDistributedGroundedCoverAboveLine(byref(substrate_cover_height_enabled))
        self._dll_interface.raise_error(status)
        return bool(substrate_cover_height_enabled.value)

    @substrate_cover_height_enabled.setter
    def substrate_cover_height_enabled(self, substrate_cover_height_enabled: bool):
        status = self._dll.setDistributedGroundedCoverAboveLine(substrate_cover_height_enabled)
        self._dll_interface.raise_error(status)
