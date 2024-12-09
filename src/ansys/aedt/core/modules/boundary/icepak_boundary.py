# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 - 2024 ANSYS, Inc. and/or its affiliates.
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

from abc import abstractmethod

from ansys.aedt.core.generic.general_methods import pyaedt_function_handler


class BoundaryDictionary:
    """
    Handles Icepak transient and temperature-dependent boundary condition assignments.

    Parameters
    ----------
    assignment_type : str
        Type of assignment represented by the class. Options are `"Temp Dep"``
        and ``"Transient"``.
    function_type : str
        Variation function to assign. If ``assignment_type=="Temp Dep"``,
        the function can only be ``"Piecewise Linear"``. Otherwise, the function can be
        ``"Exponential"``, ``"Linear"``, ``"Piecewise Linear"``, ``"Power Law"``,
        ``"Sinusoidal"``, and ``"Square Wave"``.
    """

    def __init__(self, assignment_type, function_type):
        if assignment_type not in ["Temp Dep", "Transient"]:  # pragma : no cover
            raise AttributeError(f"The argument {assignment_type} for ``assignment_type`` is not valid.")
        if assignment_type == "Temp Dep" and function_type != "Piecewise Linear":  # pragma : no cover
            raise AttributeError(
                "Temperature dependent assignments only support"
                ' ``"Piecewise Linear"`` as ``function_type`` argument.'
            )
        self.assignment_type = assignment_type
        self.function_type = function_type

    @property
    def props(self):
        """Dictionary that defines all the boundary condition properties."""
        return {
            "Type": self.assignment_type,
            "Function": self.function_type,
            "Values": self._parse_value(),
        }

    @abstractmethod
    def _parse_value(self):
        pass  # pragma : no cover

    @pyaedt_function_handler()
    def __getitem__(self, k):
        return self.props.get(k)


class LinearDictionary(BoundaryDictionary):
    """
    Manages linear conditions assignments, which are children of the ``BoundaryDictionary`` class.

    This class applies a condition ``y`` dependent on the time ``t``:
        ``y=a+b*t``

    Parameters
    ----------
    intercept : str
        Value of the assignment condition at the initial time, which
        corresponds to the coefficient ``a`` in the formula.
    slope : str
        Slope of the assignment condition, which
        corresponds to the coefficient ``b`` in the formula.
    """

    def __init__(self, intercept, slope):
        super().__init__("Transient", "Linear")
        self.intercept = intercept
        self.slope = slope

    @pyaedt_function_handler()
    def _parse_value(self):
        return [self.slope, self.intercept]


class PowerLawDictionary(BoundaryDictionary):
    """
    Manages power law condition assignments, which are children of the ``BoundaryDictionary`` class.

     This class applies a condition ``y`` dependent on the time ``t``:
         ``y=a+b*t^c``

     Parameters
     ----------
     intercept : str
         Value of the assignment condition at the initial time, which
         corresponds to the coefficient ``a`` in the formula.
     coefficient : str
         Coefficient that multiplies the power term, which
         corresponds to the coefficient ``b`` in the formula.
     scaling_exponent : str
         Exponent of the power term, which
         corresponds to the coefficient ``c`` in the formula.
    """

    def __init__(self, intercept, coefficient, scaling_exponent):
        super().__init__("Transient", "Power Law")
        self.intercept = intercept
        self.coefficient = coefficient
        self.scaling_exponent = scaling_exponent

    @pyaedt_function_handler()
    def _parse_value(self):
        return [self.intercept, self.coefficient, self.scaling_exponent]


class ExponentialDictionary(BoundaryDictionary):
    """
    Manages exponential condition assignments, which are children of the ``BoundaryDictionary`` class.

    This class applies a condition ``y`` dependent on the time ``t``:
        ``y=a+b*exp(c*t)``

    Parameters
    ----------
    vertical_offset : str
        Vertical offset summed to the exponential law, which
        corresponds to the coefficient ``a`` in the formula.
    coefficient : str
        Coefficient that multiplies the exponential term, which
        corresponds to the coefficient ``b`` in the formula.
    exponent_coefficient : str
        Coefficient in the exponential term, which
        corresponds to the coefficient ``c`` in the formula.
    """

    def __init__(self, vertical_offset, coefficient, exponent_coefficient):
        super().__init__("Transient", "Exponential")
        self.vertical_offset = vertical_offset
        self.coefficient = coefficient
        self.exponent_coefficient = exponent_coefficient

    @pyaedt_function_handler()
    def _parse_value(self):
        return [self.vertical_offset, self.coefficient, self.exponent_coefficient]


class SinusoidalDictionary(BoundaryDictionary):
    """
    Manages sinusoidal condition assignments, which are children of the ``BoundaryDictionary`` class.

    This class applies a condition ``y`` dependent on the time ``t``:
        ``y=a+b*sin(2*pi(t-t0)/T)``

    Parameters
    ----------
    vertical_offset : str
        Vertical offset summed to the sinusoidal law, which
        corresponds to the coefficient ``a`` in the formula.
    vertical_scaling : str
        Coefficient that multiplies the sinusoidal term, which
        corresponds to the coefficient ``b`` in the formula.
    period : str
        Period of the sinusoid, which
        corresponds to the coefficient ``T`` in the formula.
    period_offset : str
        Offset of the sinusoid, which
        corresponds to the coefficient ``t0`` in the formula.
    """

    def __init__(self, vertical_offset, vertical_scaling, period, period_offset):
        super().__init__("Transient", "Sinusoidal")
        self.vertical_offset = vertical_offset
        self.vertical_scaling = vertical_scaling
        self.period = period
        self.period_offset = period_offset

    @pyaedt_function_handler()
    def _parse_value(self):
        return [self.vertical_offset, self.vertical_scaling, self.period, self.period_offset]


class SquareWaveDictionary(BoundaryDictionary):
    """
    Manages square wave condition assignments, which are children of the ``BoundaryDictionary`` class.

    Parameters
    ----------
    on_value : str
        Maximum value of the square wave.
    initial_time_off : str
        Time after which the square wave assignment starts.
    on_time : str
        Time for which the square wave keeps the maximum value during one period.
    off_time : str
        Time for which the square wave keeps the minimum value during one period.
    off_value : str
        Minimum value of the square wave.
    """

    def __init__(self, on_value, initial_time_off, on_time, off_time, off_value):
        super().__init__("Transient", "Square Wave")
        self.on_value = on_value
        self.initial_time_off = initial_time_off
        self.on_time = on_time
        self.off_time = off_time
        self.off_value = off_value

    @pyaedt_function_handler()
    def _parse_value(self):
        return [self.on_value, self.initial_time_off, self.on_time, self.off_time, self.off_value]


class PieceWiseLinearDictionary(BoundaryDictionary):
    """
    Manages dataset condition assignments, which are children of the ``BoundaryDictionary`` class.

    Parameters
    ----------
    assignment_type : str
        Type of assignment represented by the class.
        Options are ``"Temp Dep"`` and ``"Transient"``.
    ds : str
        Dataset name to assign.
    scale : str
        Scaling factor for the y values of the dataset.
    """

    def __init__(self, assignment_type, ds, scale):
        super().__init__(assignment_type, "Piecewise Linear")
        self.scale = scale
        self._assignment_type = assignment_type
        self.dataset = ds

    @pyaedt_function_handler()
    def _parse_value(self):
        return [self.scale, self.dataset.name]

    @property
    def dataset_name(self):
        """Dataset name that defines the piecewise assignment."""
        return self.dataset.name


def _create_boundary(bound):
    try:
        if bound.create():
            bound._app._boundaries[bound.name] = bound
            return bound
        else:  # pragma : no cover
            raise Exception
    except Exception:  # pragma: no cover
        return None
