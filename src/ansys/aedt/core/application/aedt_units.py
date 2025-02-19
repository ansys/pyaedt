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


class AedtUnits:
    def __init__(self, aedt_object=None):
        self._aedt_object = aedt_object
        self._frequency = self._get_model_unit("Frequency")
        self._length = None
        self._resistance = self._get_model_unit("Resistance")
        self._angle = self._get_model_unit("Angle")
        self._power = self._get_model_unit("Power")
        self._inductance = self._get_model_unit("Inductance")
        self._time = self._get_model_unit("Time")
        self._voltage = self._get_model_unit("Voltage")
        self._capacitance = self._get_model_unit("Capacitance")
        self._temperature = self._get_model_unit("Temperature")
        self._current = self._get_model_unit("Current")
        self._force = self._get_model_unit("Force")
        self._speed = self._get_model_unit("Speed")
        self._angular_speed = self._get_model_unit("AngularSpeed")
        self._mass = self._get_model_unit("Mass")
        self._conductance = self._get_model_unit("Conductance")
        self._rescale_model = False

    @property
    def rescale_model(self):
        """Whether if rescale model on model unit change or not.

        Returns
        -------
        bool
        """
        return self._rescale_model

    @rescale_model.setter
    def rescale_model(self, value):
        self._rescale_model = value

    def _get_model_unit(self, unit_system):
        if self._aedt_object:
            return self._aedt_object._odesktop.GetDefaultUnit(unit_system)

    def _set_model_unit(self, prop, value, unit_system):
        if value in AEDT_UNITS[unit_system]:
            setattr(self, prop, value)
        else:
            raise AttributeError(f"Unit {value} is incorrect.")

    @property
    def frequency(self):
        """Default frequency unit to be used in active design.
        The setter doesn't change AEDT default units.


        Returns
        -------
        str
            Unit value.
        """
        return self._frequency

    @frequency.setter
    def frequency(self, value):
        self._set_model_unit("_frequency", value, "Frequency")

    @property
    def length(self):
        """Default length unit to be used in active design.
        The setter changes AEDT default units.


        Returns
        -------
        str
            Unit value.
        """
        if self._length is None and self._aedt_object:
            self._length = self._aedt_object.oeditor.GetModelUnits()
        return self._length

    @length.setter
    def length(self, value):
        if value in AEDT_UNITS["Lengths"]:
            self._length = value
            if "SetModelUnits" in dir(self._aedt_object.oeditor):
                self._aedt_object.oeditor.SetModelUnits(
                    ["NAME:Units Parameter", "Units:=", value, "Rescale:=", self.rescale_model]
                )
            elif "SetActiveUnits" in dir(self._aedt_object.oeditor):
                self._aedt_object.oeditor.SetActiveUnits(value)
        else:
            raise AttributeError(f"Unit {value} is incorrect.")

    @property
    def angle(self):
        """Default angle unit to be used in active design.
        The setter doesn't change AEDT default units.


        Returns
        -------
        str
            Unit value.
        """
        return self._angle

    @angle.setter
    def angle(self, value):
        self._set_model_unit("_angle", value, "Angle")

    @property
    def resistance(self):
        """Default resistance unit to be used in active design.
        The setter doesn't change AEDT default units.


        Returns
        -------
        str
            Unit value.
        """
        return self._resistance

    @resistance.setter
    def resistance(self, value):
        self._set_model_unit("_resistance", value, "Resistance")

    @property
    def power(self):
        """Default power unit to be used in active design.
        The setter doesn't change AEDT default units.


        Returns
        -------
        str
            Unit value.
        """
        return self._power

    @power.setter
    def power(self, value):
        self._set_model_unit("_power", value, "Power")

    @property
    def time(self):
        """Default time unit to be used in active design.
        The setter doesn't change AEDT default units.


        Returns
        -------
        str
            Unit value.
        """
        return self._time

    @time.setter
    def time(self, value):
        self._set_model_unit("_time", value, "Time")

    @property
    def temperature(self):
        """Default temperature unit to be used in active design.
        The setter doesn't change AEDT default units.


        Returns
        -------
        str
            Unit value.
        """
        return self._temperature

    @temperature.setter
    def temperature(self, value):
        self._set_model_unit("_temperature", value, "Temperature")

    @property
    def inductance(self):
        """Default inductance unit to be used in active design.
        The setter doesn't change AEDT default units.


        Returns
        -------
        str
            Unit value.
        """
        return self._inductance

    @inductance.setter
    def inductance(self, value):
        self._set_model_unit("_inductance", value, "Inductance")

    @property
    def voltage(self):
        """Default voltage unit to be used in active design.
        The setter doesn't change AEDT default units.


        Returns
        -------
        str
            Unit value.
        """
        return self._voltage

    @voltage.setter
    def voltage(self, value):
        self._set_model_unit("_voltage", value, "Voltage")

    @property
    def current(self):
        """Default current unit to be used in active design.
        The setter doesn't change AEDT default units.


        Returns
        -------
        str
            Unit value.
        """
        return self._current

    @current.setter
    def current(self, value):
        self._set_model_unit("_current", value, "Current")

    @property
    def angular_speed(self):
        """Default angular speed unit to be used in active design.
        The setter doesn't change AEDT default units.


        Returns
        -------
        str
            Unit value.
        """
        return self._angular_speed

    @angular_speed.setter
    def angular_speed(self, value):
        self._set_model_unit("_angular_speed", value, "AngularSpeed")

    @property
    def capacitance(self):
        """Default capacitance unit to be used in active design.
        The setter doesn't change AEDT default units.


        Returns
        -------
        str
            Unit value.
        """
        return self._capacitance

    @capacitance.setter
    def capacitance(self, value):
        self._set_model_unit("_capacitance", value, "Capacitance")

    @property
    def conductance(self):
        """Default conductance unit to be used in active design.
        The setter doesn't change AEDT default units.


        Returns
        -------
        str
            Unit value.
        """
        return self._conductance

    @conductance.setter
    def conductance(self, value):
        self._set_model_unit("_conductance", value, "Conductance")

    @property
    def mass(self):
        """Default mass unit to be used in active design.
        The setter doesn't change AEDT default units.


        Returns
        -------
        str
            Unit value.
        """
        return self._mass

    @mass.setter
    def mass(self, value):
        self._set_model_unit("_mass", value, "Mass")

    @property
    def speed(self):
        """Default speed unit to be used in active design.
        The setter doesn't change AEDT default units.


        Returns
        -------
        str
            Unit value.
        """
        return self._speed

    @speed.setter
    def speed(self, value):
        self._set_model_unit("_speed", value, "Speed")
