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

from ctypes import c_char_p
from ctypes import c_int

import ansys.aedt.core


class DistributedParasitics:
    """Defines parasitic parameters of distributed filters.

    This class allows you to define and modify the layout parasitics parameters of distributed filters.
    """

    def __init__(self):
        self._dll = ansys.aedt.core.filtersolutions_core._dll_interface()._dll
        self._dll_interface = ansys.aedt.core.filtersolutions_core._dll_interface()
        self._define_parasitics_dll_functions()

    def _define_parasitics_dll_functions(self):
        """Define C++ API DLL functions."""
        self._dll.setDistributedCapacitorQ.argtype = c_char_p
        self._dll.setDistributedCapacitorQ.restype = c_int
        self._dll.getDistributedCapacitorQ.argtypes = [c_char_p, c_int]
        self._dll.getDistributedCapacitorQ.restype = c_int

        self._dll.setDistributedCapacitorRs.argtype = c_char_p
        self._dll.setDistributedCapacitorRs.restype = c_int
        self._dll.getDistributedCapacitorRs.argtypes = [c_char_p, c_int]
        self._dll.getDistributedCapacitorRs.restype = c_int

        self._dll.setDistributedCapacitorRp.argtype = c_char_p
        self._dll.setDistributedCapacitorRp.restype = c_int
        self._dll.getDistributedCapacitorRp.argtypes = [c_char_p, c_int]
        self._dll.getDistributedCapacitorRp.restype = c_int

        self._dll.setDistributedCapacitorLs.argtype = c_char_p
        self._dll.setDistributedCapacitorLs.restype = c_int
        self._dll.getDistributedCapacitorLs.argtypes = [c_char_p, c_int]
        self._dll.getDistributedCapacitorLs.restype = c_int

        self._dll.setDistributedInductorQ.argtype = c_char_p
        self._dll.setDistributedInductorQ.restype = c_int
        self._dll.getDistributedInductorQ.argtypes = [c_char_p, c_int]
        self._dll.getDistributedInductorQ.restype = c_int

        self._dll.setDistributedInductorRs.argtype = c_char_p
        self._dll.setDistributedInductorRs.restype = c_int
        self._dll.getDistributedInductorRs.argtypes = [c_char_p, c_int]
        self._dll.getDistributedInductorRs.restype = c_int

        self._dll.setDistributedInductorRp.argtype = c_char_p
        self._dll.setDistributedInductorRp.restype = c_int
        self._dll.getDistributedInductorRp.argtypes = [c_char_p, c_int]
        self._dll.getDistributedInductorRp.restype = c_int

        self._dll.setDistributedInductorCp.argtype = c_char_p
        self._dll.setDistributedInductorCp.restype = c_int
        self._dll.getDistributedInductorCp.argtypes = [c_char_p, c_int]
        self._dll.getDistributedInductorCp.restype = c_int

        self._dll.setDistributedOddResistance.argtype = c_char_p
        self._dll.setDistributedOddResistance.restype = c_int
        self._dll.getDistributedOddResistance.argtypes = [c_char_p, c_int]
        self._dll.getDistributedOddResistance.restype = c_int

        self._dll.setDistributedEvenResistance.argtype = c_char_p
        self._dll.setDistributedEvenResistance.restype = c_int
        self._dll.getDistributedEvenResistance.argtypes = [c_char_p, c_int]
        self._dll.getDistributedEvenResistance.restype = c_int

        self._dll.setDistributedOddConductance.argtype = c_char_p
        self._dll.setDistributedOddConductance.restype = c_int
        self._dll.getDistributedOddConductance.argtypes = [c_char_p, c_int]
        self._dll.getDistributedOddConductance.restype = c_int

        self._dll.setDistributedEvenConductance.argtype = c_char_p
        self._dll.setDistributedEvenConductance.restype = c_int
        self._dll.getDistributedEvenConductance.argtypes = [c_char_p, c_int]
        self._dll.getDistributedEvenConductance.restype = c_int

        self._dll.setDistributedMinSegmentLength.argtype = c_char_p
        self._dll.setDistributedMinSegmentLength.restype = c_int
        self._dll.getDistributedMinSegmentLength.argtypes = [c_char_p, c_int]
        self._dll.getDistributedMinSegmentLength.restype = c_int

    @property
    def capacitor_q(self) -> str:
        """Q factor value of non-ideal capacitors in the synthesized circuit.
        The default is ``infinite``.

        Returns
        -------
        str
        """
        capacitor_q_string = self._dll_interface.get_string(self._dll.getDistributedCapacitorQ)
        return capacitor_q_string

    @capacitor_q.setter
    def capacitor_q(self, capacitor_q_string):
        self._dll_interface.set_string(self._dll.setDistributedCapacitorQ, capacitor_q_string)

    @property
    def capacitor_rs(self) -> str:
        """Series resistor value of non-ideal capacitors in the synthesized circuit.
        The default is ``0``.

        Returns
        -------
        str
        """
        capacitor_rs_string = self._dll_interface.get_string(self._dll.getDistributedCapacitorRs)
        return capacitor_rs_string

    @capacitor_rs.setter
    def capacitor_rs(self, capacitor_rs_string):
        self._dll_interface.set_string(self._dll.setDistributedCapacitorRs, capacitor_rs_string)

    @property
    def capacitor_rp(self) -> str:
        """Shunt resistor value of non-ideal capacitors in the synthesized circuit.
        The default is ``infinite``.

        Returns
        -------
        str
        """
        capacitor_rp_string = self._dll_interface.get_string(self._dll.getDistributedCapacitorRp)
        return capacitor_rp_string

    @capacitor_rp.setter
    def capacitor_rp(self, capacitor_rp_string):
        self._dll_interface.set_string(self._dll.setDistributedCapacitorRp, capacitor_rp_string)

    @property
    def capacitor_ls(self) -> str:
        """Series inductance value of non-ideal capacitors in the synthesized circuit.
        The default is ``0``.

        Returns
        -------
        str
        """
        capacitor_ls_string = self._dll_interface.get_string(self._dll.getDistributedCapacitorLs)
        return capacitor_ls_string

    @capacitor_ls.setter
    def capacitor_ls(self, capacitor_ls_string):
        self._dll_interface.set_string(self._dll.setDistributedCapacitorLs, capacitor_ls_string)

    @property
    def inductor_q(self) -> str:
        """Q factor value of non-ideal inductors in the synthesized circuit.
        The default is ``infinite``.

        Returns
        -------
        str
        """
        inductor_q_string = self._dll_interface.get_string(self._dll.getDistributedInductorQ)
        return inductor_q_string

    @inductor_q.setter
    def inductor_q(self, inductor_q_string):
        self._dll_interface.set_string(self._dll.setDistributedInductorQ, inductor_q_string)

    @property
    def inductor_rs(self) -> str:
        """Series resistor value of non-ideal inductors in the synthesized circuit.
        The default is` ``0``.

        Returns
        -------
        str
        """
        inductor_rs_string = self._dll_interface.get_string(self._dll.getDistributedInductorRs)
        return inductor_rs_string

    @inductor_rs.setter
    def inductor_rs(self, inductor_rs_string):
        self._dll_interface.set_string(self._dll.setDistributedInductorRs, inductor_rs_string)

    @property
    def inductor_rp(self) -> str:
        """Shunt resistor value of non-ideal inductors in the synthesized circuit.
        The default is ``infinite``.

        Returns
        -------
        str
        """
        inductor_rp_string = self._dll_interface.get_string(self._dll.getDistributedInductorRp)
        return inductor_rp_string

    @inductor_rp.setter
    def inductor_rp(self, inductor_rp_string):
        self._dll_interface.set_string(self._dll.setDistributedInductorRp, inductor_rp_string)

    @property
    def inductor_cp(self) -> str:
        """Shunt capacitor value of non-ideal inductors in the synthesized circuit.
        The default is ``0``.

        Returns
        -------
        str
        """
        inductor_cp_string = self._dll_interface.get_string(self._dll.getDistributedInductorCp)
        return inductor_cp_string

    @inductor_cp.setter
    def inductor_cp(self, inductor_cp_string):
        self._dll_interface.set_string(self._dll.setDistributedInductorCp, inductor_cp_string)

    @property
    def line_odd_resistance(self) -> str:
        """Odd-mode conductor resistance value of the line per unit length.
        This parameter is defined for standard ``RLGC`` transmission line model substrate types.
        The default is ``0``.

        Returns
        -------
        str
        """
        odd_resistance_string = self._dll_interface.get_string(self._dll.getDistributedOddResistance)
        return odd_resistance_string

    @line_odd_resistance.setter
    def line_odd_resistance(self, odd_resistance_string):
        self._dll_interface.set_string(self._dll.setDistributedOddResistance, odd_resistance_string)

    @property
    def line_even_resistance(self) -> str:
        """Even-mode conductor resistance value of the line per unit length.
        This parameter is defined for standard ``RLGC`` transmission line model substrate types.
        The default is ``0``.

        Returns
        -------
        str
        """
        even_resistance_string = self._dll_interface.get_string(self._dll.getDistributedEvenResistance)
        return even_resistance_string

    @line_even_resistance.setter
    def line_even_resistance(self, even_resistance_string):
        self._dll_interface.set_string(self._dll.setDistributedEvenResistance, even_resistance_string)

    @property
    def line_odd_conductance(self) -> str:
        """Odd-mode dielectric conductance of the line per unit length.
        This parameter is defined for standard ``RLGC`` transmission line model substrate types.
        The default is ``0``.

        Returns
        -------
        str
        """
        odd_conductance_string = self._dll_interface.get_string(self._dll.getDistributedOddConductance)
        return odd_conductance_string

    @line_odd_conductance.setter
    def line_odd_conductance(self, odd_conductance_string):
        self._dll_interface.set_string(self._dll.setDistributedOddConductance, odd_conductance_string)

    @property
    def line_even_conductance(self) -> str:
        """Even-mode dielectric conductance of the line per unit length.
        This parameter is defined for standard ``RLGC`` transmission line model substrate types.
        The default is ``0``.

        Returns
        -------
        str
        """
        even_conductance_string = self._dll_interface.get_string(self._dll.getDistributedEvenConductance)
        return even_conductance_string

    @line_even_conductance.setter
    def line_even_conductance(self, even_conductance_string):
        self._dll_interface.set_string(self._dll.setDistributedEvenConductance, even_conductance_string)

    @property
    def line_min_segment_lengths(self) -> str:
        """Default value for the minimum segment lengths between stubs.
        This parameter is defined for standard ``RLGC`` transmission line model substrate types.
        The default is ``0``.

        Returns
        -------
        str
        """
        line_min_segment_length_string = self._dll_interface.get_string(self._dll.getDistributedMinSegmentLength)
        return line_min_segment_length_string

    @line_min_segment_lengths.setter
    def line_min_segment_lengths(self, line_min_segment_length_string):
        self._dll_interface.set_string(self._dll.setDistributedMinSegmentLength, line_min_segment_length_string)
