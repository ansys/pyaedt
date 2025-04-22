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


class LumpedTopology:
    """Defines topology parameters of lumped filters.

    This class allows you to define and modify the topology parameters of lumped filters.
    """

    def __init__(self):
        self._dll = ansys.aedt.core.filtersolutions_core._dll_interface()._dll
        self._dll_interface = ansys.aedt.core.filtersolutions_core._dll_interface()
        self._define_topology_dll_functions()
        if self._dll_interface.api_version() >= "2025.2":
            self._set_lump_implementation()

    def _define_topology_dll_functions(self):
        """Define C++ API DLL functions."""
        if self._dll_interface.api_version() >= "2025.2":
            self._dll.setLumpedSourceResistance.argtype = c_char_p
            self._dll.setLumpedSourceResistance.restype = c_int
            self._dll.getLumpedSourceResistance.argtypes = [c_char_p, c_int]
            self._dll.getLumpedSourceResistance.restype = c_int

            self._dll.setLumpedLoadResistance.argtype = c_char_p
            self._dll.setLumpedLoadResistance.restype = c_int
            self._dll.getLumpedLoadResistance.argtypes = [c_char_p, c_int]
            self._dll.getLumpedLoadResistance.restype = c_int
        else:
            self._dll.setLumpedGeneratorResistor.argtype = c_char_p
            self._dll.setLumpedGeneratorResistor.restype = c_int
            self._dll.getLumpedGeneratorResistor.argtypes = [c_char_p, c_int]
            self._dll.getLumpedGeneratorResistor.restype = c_int

            self._dll.setLumpedLoadResistor.argtype = c_char_p
            self._dll.setLumpedLoadResistor.restype = c_int
            self._dll.getLumpedLoadResistor.argtypes = [c_char_p, c_int]
            self._dll.getLumpedLoadResistor.restype = c_int

        self._dll.setLumpedCurrentSource.argtype = c_bool
        self._dll.setLumpedCurrentSource.restype = c_int
        self._dll.getLumpedCurrentSource.argtype = POINTER(c_bool)
        self._dll.getLumpedCurrentSource.restype = c_int

        self._dll.setLumpedFirstElementShunt.argtype = c_bool
        self._dll.setLumpedFirstElementShunt.restype = c_int
        self._dll.getLumpedFirstElementShunt.argtype = POINTER(c_bool)
        self._dll.getLumpedFirstElementShunt.restype = c_int

        self._dll.setLumpedBridgeT.argtype = c_bool
        self._dll.setLumpedBridgeT.restype = c_int
        self._dll.getLumpedBridgeT.argtype = POINTER(c_bool)
        self._dll.getLumpedBridgeT.restype = c_int

        self._dll.setLumpedBridgeTLow.argtype = c_bool
        self._dll.setLumpedBridgeTLow.restype = c_int
        self._dll.getLumpedBridgeTLow.argtype = POINTER(c_bool)
        self._dll.getLumpedBridgeTLow.restype = c_int

        self._dll.setLumpedBridgeTHigh.argtype = c_bool
        self._dll.setLumpedBridgeTHigh.restype = c_int
        self._dll.getLumpedBridgeTHigh.argtype = POINTER(c_bool)
        self._dll.getLumpedBridgeTHigh.restype = c_int

        self._dll.setLumpedEqualInductors.argtype = c_bool
        self._dll.setLumpedEqualInductors.restype = c_int
        self._dll.getLumpedEqualInductors.argtype = POINTER(c_bool)
        self._dll.getLumpedEqualInductors.restype = c_int

        self._dll.setLumpedEqualCapacitors.argtype = c_bool
        self._dll.setLumpedEqualCapacitors.restype = c_int
        self._dll.getLumpedEqualCapacitors.argtype = POINTER(c_bool)
        self._dll.getLumpedEqualCapacitors.restype = c_int

        self._dll.setLumpedEqualLegs.argtype = c_bool
        self._dll.setLumpedEqualLegs.restype = c_int
        self._dll.getLumpedEqualLegs.argtype = POINTER(c_bool)
        self._dll.getLumpedEqualLegs.restype = c_int

        self._dll.setLumpedHighLowPass.argtype = c_bool
        self._dll.setLumpedHighLowPass.restype = c_int
        self._dll.getLumpedHighLowPass.argtype = POINTER(c_bool)
        self._dll.getLumpedHighLowPass.restype = c_int

        self._dll.setLumpedHighLowPassMinInd.argtype = c_bool
        self._dll.setLumpedHighLowPassMinInd.restype = c_int
        self._dll.getLumpedHighLowPassMinInd.argtype = POINTER(c_bool)
        self._dll.getLumpedHighLowPassMinInd.restype = c_int

        self._dll.setLumpedZigZag.argtype = c_bool
        self._dll.setLumpedZigZag.restype = c_int
        self._dll.getLumpedZigZag.argtype = POINTER(c_bool)
        self._dll.getLumpedZigZag.restype = c_int

        self._dll.setLumpedMinInd.argtype = c_bool
        self._dll.setLumpedMinInd.restype = c_int
        self._dll.getLumpedMinInd.argtype = POINTER(c_bool)
        self._dll.getLumpedMinInd.restype = c_int

        self._dll.setLumpedMinCap.argtype = c_bool
        self._dll.setLumpedMinCap.restype = c_int
        self._dll.getLumpedMinCap.argtype = POINTER(c_bool)
        self._dll.getLumpedMinCap.restype = c_int

        self._dll.setLumpedSourceRes.argtype = c_bool
        self._dll.setLumpedSourceRes.restype = c_int
        self._dll.getLumpedSourceRes.argtype = POINTER(c_bool)
        self._dll.getLumpedSourceRes.restype = c_int

        self._dll.setLumpedTrapTopology.argtype = c_bool
        self._dll.setLumpedTrapTopology.restype = c_int
        self._dll.getLumpedTrapTopology.argtype = POINTER(c_bool)
        self._dll.getLumpedTrapTopology.restype = c_int

        self._dll.setLumpedNodeCapGround.argtype = c_bool
        self._dll.setLumpedNodeCapGround.restype = c_int
        self._dll.getLumpedNodeCapGround.argtype = POINTER(c_bool)
        self._dll.getLumpedNodeCapGround.restype = c_int

        self._dll.setLumpedMatchImpedance.argtype = c_bool
        self._dll.setLumpedMatchImpedance.restype = c_int
        self._dll.getLumpedMatchImpedance.argtype = POINTER(c_bool)
        self._dll.getLumpedMatchImpedance.restype = c_int

        self._dll.setLumpedComplexTermination.argtype = c_bool
        self._dll.setLumpedComplexTermination.restype = c_int
        self._dll.getLumpedComplexTermination.argtype = POINTER(c_bool)
        self._dll.getLumpedComplexTermination.restype = c_int

        self._dll.setLumpedComplexElementTuneEnabled.argtype = c_bool
        self._dll.setLumpedComplexElementTuneEnabled.restype = c_int
        self._dll.getLumpedComplexElementTuneEnabled.argtype = POINTER(c_bool)
        self._dll.getLumpedComplexElementTuneEnabled.restype = c_int

        if self._dll_interface.api_version() >= "2025.2":
            self._dll.getLumpedNetlistSize.argtype = POINTER(c_int)
            self._dll.getLumpedNetlistSize.restype = c_int
            self._dll.getLumpedNetlist.argtypes = [c_char_p, c_int]
            self._dll.getLumpedNetlist.restype = c_int
        else:
            self._dll.getLumpedCircuitResponseSize.argtype = POINTER(c_int)
            self._dll.getLumpedCircuitResponseSize.restype = c_int
            self._dll.getLumpedCircuitResponse.argtypes = [c_char_p, c_int]
            self._dll.getLumpedCircuitResponse.restype = c_int

    def _set_lump_implementation(self):
        """Set ``FilterSolutions`` attributes to lump design."""
        filter_implementation_status = self._dll.setFilterImplementation(0)
        self._dll_interface.raise_error(filter_implementation_status)

    @property
    def source_resistance(self) -> str:
        """Generator resistor. The default is ``50``.

        Returns
        -------
        str
        """
        if self._dll_interface.api_version() >= "2025.2":
            source_resistance_string = self._dll_interface.get_string(self._dll.getLumpedSourceResistance)
        else:
            source_resistance_string = self._dll_interface.get_string(self._dll.getLumpedGeneratorResistor)
        return source_resistance_string

    @source_resistance.setter
    def source_resistance(self, source_resistance_string):
        if self._dll_interface.api_version() >= "2025.2":
            self._dll_interface.set_string(self._dll.setLumpedSourceResistance, source_resistance_string)
        else:
            self._dll_interface.set_string(self._dll.setLumpedGeneratorResistor, source_resistance_string)

    @property
    def load_resistance(self) -> str:
        """Load resistor. The default is ``50``.

        Returns
        -------
        str
        """
        if self._dll_interface.api_version() >= "2025.2":
            load_resistance_string = self._dll_interface.get_string(self._dll.getLumpedLoadResistance)
        else:
            load_resistance_string = self._dll_interface.get_string(self._dll.getLumpedLoadResistor)
        return load_resistance_string

    @load_resistance.setter
    def load_resistance(self, load_resistance_string):
        if self._dll_interface.api_version() >= "2025.2":
            self._dll_interface.set_string(self._dll.setLumpedLoadResistance, load_resistance_string)
        else:
            self._dll_interface.set_string(self._dll.setLumpedLoadResistor, load_resistance_string)

    @property
    def current_source(self) -> bool:
        """Flag indicating if the current source in the synthesized circuit is enabled.

        Returns
        -------
        bool
        """
        current_source = c_bool()
        status = self._dll.getLumpedCurrentSource(byref(current_source))
        self._dll_interface.raise_error(status)
        return bool(current_source.value)

    @current_source.setter
    def current_source(self, current_source: bool):
        status = self._dll.setLumpedCurrentSource(current_source)
        self._dll_interface.raise_error(status)

    @property
    def first_shunt(self) -> bool:
        """Flag indicating if shunt elements are first in the synthesized circuit.

        If ``False``, series elements are first.

        Returns
        -------
        bool
        """
        first_shunt = c_bool()
        status = self._dll.getLumpedFirstElementShunt(byref(first_shunt))
        self._dll_interface.raise_error(status)
        return bool(first_shunt.value)

    @first_shunt.setter
    def first_shunt(self, first_shunt: bool):
        status = self._dll.setLumpedFirstElementShunt(first_shunt)
        self._dll_interface.raise_error(status)

    @property
    def bridge_t(self) -> bool:
        """Flag indicating if the bridgeT topology in the synthesized circuit is enabled.

        Returns
        -------
        bool
        """
        bridge_t = c_bool()
        status = self._dll.getLumpedBridgeT(byref(bridge_t))
        self._dll_interface.raise_error(status)
        return bool(bridge_t.value)

    @bridge_t.setter
    def bridge_t(self, bridge_t: bool):
        status = self._dll.setLumpedBridgeT(bridge_t)
        self._dll_interface.raise_error(status)

    @property
    def bridge_t_low(self) -> bool:
        """Flag indicating if the bridgeT topology for the lower frequency band in the synthesized circuit is enabled.

        Returns
        -------
        bool
        """
        bridge_t_low = c_bool()
        status = self._dll.getLumpedBridgeTLow(byref(bridge_t_low))
        self._dll_interface.raise_error(status)
        return bool(bridge_t_low.value)

    @bridge_t_low.setter
    def bridge_t_low(self, bridge_t_low: bool):
        status = self._dll.setLumpedBridgeTLow(bridge_t_low)
        self._dll_interface.raise_error(status)

    @property
    def bridge_t_high(self) -> bool:
        """Flag indicating if the bridgeT topology for the higher frequency band in the synthesized circuit is enabled.

        Returns
        -------
        bool
        """
        bridge_t_high = c_bool()
        status = self._dll.getLumpedBridgeTHigh(byref(bridge_t_high))
        self._dll_interface.raise_error(status)
        return bool(bridge_t_high.value)

    @bridge_t_high.setter
    def bridge_t_high(self, bridge_t_high: bool):
        status = self._dll.setLumpedBridgeTHigh(bridge_t_high)
        self._dll_interface.raise_error(status)

    @property
    def equal_inductors(self) -> bool:
        """Flag indicating if the equal inductors topology in the synthesized circuit is enabled.

        Returns
        -------
        bool
        """
        equal_inductors = c_bool()
        status = self._dll.getLumpedEqualInductors(byref(equal_inductors))
        self._dll_interface.raise_error(status)
        return bool(equal_inductors.value)

    @equal_inductors.setter
    def equal_inductors(self, equal_inductors: bool):
        status = self._dll.setLumpedEqualInductors(equal_inductors)
        self._dll_interface.raise_error(status)

    @property
    def equal_capacitors(self) -> bool:
        """Flag indicating if the equal capacitors topology in the synthesized circuit is enabled.

        Returns
        -------
        bool
        """
        equal_capacitors = c_bool()
        status = self._dll.getLumpedEqualCapacitors(byref(equal_capacitors))
        self._dll_interface.raise_error(status)
        return bool(equal_capacitors.value)

    @equal_capacitors.setter
    def equal_capacitors(self, equal_capacitors: bool):
        status = self._dll.setLumpedEqualCapacitors(equal_capacitors)
        self._dll_interface.raise_error(status)

    @property
    def equal_legs(self) -> bool:
        """Flag indicating if the equal pairs shunt or series legs topology in the synthesized circuit is enabled.

        Returns
        -------
        bool
        """
        equal_legs = c_bool()
        status = self._dll.getLumpedEqualLegs(byref(equal_legs))
        self._dll_interface.raise_error(status)
        return bool(equal_legs.value)

    @equal_legs.setter
    def equal_legs(self, equal_legs: bool):
        status = self._dll.setLumpedEqualLegs(equal_legs)
        self._dll_interface.raise_error(status)

    @property
    def high_low_pass(self) -> bool:
        """Flag indicating if the high and low pass topology in the synthesized circuit is enabled.

        Returns
        -------
        bool
        """
        high_low_pass = c_bool()
        status = self._dll.getLumpedHighLowPass(byref(high_low_pass))
        self._dll_interface.raise_error(status)
        return bool(high_low_pass.value)

    @high_low_pass.setter
    def high_low_pass(self, high_low_pass: bool):
        status = self._dll.setLumpedHighLowPass(high_low_pass)
        self._dll_interface.raise_error(status)

    @property
    def high_low_pass_min_ind(self) -> bool:
        """Flag indicating if the high and low pass topology with minimum inductors
        in the synthesized circuit is enabled.

        Returns
        -------
        bool
        """
        high_low_pass_min_ind = c_bool()
        status = self._dll.getLumpedHighLowPassMinInd(byref(high_low_pass_min_ind))
        self._dll_interface.raise_error(status)
        return bool(high_low_pass_min_ind.value)

    @high_low_pass_min_ind.setter
    def high_low_pass_min_ind(self, high_low_pass_min_ind: bool):
        status = self._dll.setLumpedHighLowPassMinInd(high_low_pass_min_ind)
        self._dll_interface.raise_error(status)

    @property
    def zig_zag(self) -> bool:
        """Flag indicating if the zig-zag topology with minimum inductors in the synthesized circuit is enabled.

        Returns
        -------
        bool
        """
        zig_zag = c_bool()
        status = self._dll.getLumpedZigZag(byref(zig_zag))
        self._dll_interface.raise_error(status)
        return bool(zig_zag.value)

    @zig_zag.setter
    def zig_zag(self, zig_zag: bool):
        status = self._dll.setLumpedZigZag(zig_zag)
        self._dll_interface.raise_error(status)

    @property
    def min_ind(self) -> bool:
        """Flag indicating if the minimum inductors topology in the synthesized circuit is enabled.

        Returns
        -------
        bool
        """
        min_ind = c_bool()
        status = self._dll.getLumpedMinInd(byref(min_ind))
        self._dll_interface.raise_error(status)
        return bool(min_ind.value)

    @min_ind.setter
    def min_ind(self, min_ind: bool):
        status = self._dll.setLumpedMinInd(min_ind)
        self._dll_interface.raise_error(status)

    @property
    def min_cap(self) -> bool:
        """Flag indicating if the minimum capacitors topology in the synthesized circuit is enabled.

        Returns
        -------
        bool
        """
        min_cap = c_bool()
        status = self._dll.getLumpedMinCap(byref(min_cap))
        self._dll_interface.raise_error(status)
        return bool(min_cap.value)

    @min_cap.setter
    def min_cap(self, min_cap: bool):
        status = self._dll.setLumpedMinCap(min_cap)
        self._dll_interface.raise_error(status)

    @property
    def set_source_res(self) -> bool:
        """Flag indicating if the matched source resistor for zig-zag topology in the synthesized circuit is enabled.

        Returns
        -------
        bool
        """
        set_source_res = c_bool()
        status = self._dll.getLumpedSourceRes(byref(set_source_res))
        self._dll_interface.raise_error(status)
        return bool(set_source_res.value)

    @set_source_res.setter
    def set_source_res(self, set_source_res: bool):
        status = self._dll.setLumpedSourceRes(set_source_res)
        self._dll_interface.raise_error(status)

    @property
    def trap_topology(self) -> bool:
        """Flag indicating if the trap topology in the synthesized circuit is enabled.

        Returns
        -------
        bool
        """
        trap_topology = c_bool()
        status = self._dll.getLumpedTrapTopology(byref(trap_topology))
        self._dll_interface.raise_error(status)
        return bool(trap_topology.value)

    @trap_topology.setter
    def trap_topology(self, trap_topology: bool):
        status = self._dll.setLumpedTrapTopology(trap_topology)
        self._dll_interface.raise_error(status)

    @property
    def node_cap_ground(self) -> bool:
        """Flag indicating if the parasitic capacitors to ground topology in the synthesized circuit is enabled.

        Returns
        -------
        bool
        """
        node_cap_ground = c_bool()
        status = self._dll.getLumpedNodeCapGround(byref(node_cap_ground))
        self._dll_interface.raise_error(status)
        return bool(node_cap_ground.value)

    @node_cap_ground.setter
    def node_cap_ground(self, node_cap_ground: bool):
        status = self._dll.setLumpedNodeCapGround(node_cap_ground)
        self._dll_interface.raise_error(status)

    @property
    def match_impedance(self) -> bool:
        """Flag indicating if the automatic matched impedance topology in the synthesized circuit is enabled.

        Returns
        -------
        bool
        """
        match_impedance = c_bool()
        status = self._dll.getLumpedMatchImpedance(byref(match_impedance))
        self._dll_interface.raise_error(status)
        return bool(match_impedance.value)

    @match_impedance.setter
    def match_impedance(self, match_impedance: bool):
        status = self._dll.setLumpedMatchImpedance(match_impedance)
        self._dll_interface.raise_error(status)

    @property
    def complex_termination(self) -> bool:
        """Flag indicating if the lumped filter complex termination is enabled.

        Returns
        -------
        bool
        """
        complex_termination = c_bool()
        status = self._dll.getLumpedComplexTermination(byref(complex_termination))
        self._dll_interface.raise_error(status)
        return bool(complex_termination.value)

    @complex_termination.setter
    def complex_termination(self, complex_termination: bool):
        status = self._dll.setLumpedComplexTermination(complex_termination)
        self._dll_interface.raise_error(status)

    @property
    def complex_element_tune_enabled(self) -> bool:
        """Flag indicating if the element tune option is enabled.

        Returns
        -------
        bool
        """
        complex_element_tune_enabled = c_bool()
        status = self._dll.getLumpedComplexElementTuneEnabled(byref(complex_element_tune_enabled))
        self._dll_interface.raise_error(status)
        return bool(complex_element_tune_enabled.value)

    @complex_element_tune_enabled.setter
    def complex_element_tune_enabled(self, complex_element_tune_enabled: bool):
        status = self._dll.setLumpedComplexElementTuneEnabled(complex_element_tune_enabled)
        self._dll_interface.raise_error(status)

    def netlist(self):
        """Execute real filter synthesis"""
        size = c_int()
        if self._dll_interface.api_version() >= "2025.2":
            status = self._dll.getLumpedNetlistSize(byref(size))
        else:
            status = self._dll.getLumpedCircuitResponseSize(byref(size))
        self._dll_interface.raise_error(status)
        if self._dll_interface.api_version() >= "2025.2":
            netlist_string = self._dll_interface.get_string(self._dll.getLumpedNetlist, max_size=size.value)
        else:
            netlist_string = self._dll_interface.get_string(self._dll.getLumpedCircuitResponse, max_size=size.value)
        return netlist_string
