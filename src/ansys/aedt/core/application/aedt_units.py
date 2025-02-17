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

from ansys.aedt.core.generic.constants import AEDT_UNITS
from ansys.aedt.core.generic.desktop_sessions import _desktop_sessions


class AedtUnits(object):
    def __init__(self, desktop=None):
        if desktop:
            self._odesktop = desktop.odesktop
        elif _desktop_sessions:
            self._odesktop = list(_desktop_sessions.values())[-1].odesktop
        else:
            self._odesktop = None
        self._frequencies = None
        self._lengths = None
        self._resistance = None
        self._angle = None
        self._power = None
        self._inductance = None
        self._time = None
        self._voltage = None
        self._capacitance = None
        self._temperature = None
        self._current = None
        self._force = None
        self._torque = None
        self._speed = None
        self._angular_speed = None
        self._mag_flux = None
        self._mass = None
        self._mag_field = None
        self._pressure = None
        self._conductance = None
        self._datarate = None

    @property
    def frequencies(self):
        """Default frequency unit to be used in active design.
        The setter doesn't change AEDT default units.


        Returns
        -------
        str
            Unit value.
        """
        if self._frequencies is None and self._odesktop:
            self._frequencies = self._odesktop.GetDefaultUnit("Frequency")
        return self._frequencies

    @frequencies.setter
    def frequencies(self, value):
        if value in AEDT_UNITS["Frequencies"]:
            self._frequencies = value
        else:
            raise AttributeError(f"Unit {value} is incorrect.")
