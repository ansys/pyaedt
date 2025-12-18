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

from pydantic import BaseModel

from ansys.aedt.core.generic.numbers_utils import Quantity


def convert_to_meter(value):
    """Convert numbers automatically to mils.

    It is rounded to the nearest 100 mil which is minimum schematic snap unit.
    """
    value = Quantity(value, "mil")

    value = value.to("mil")
    value.value = round(value.value, -2)
    value = value.to("meter")
    return value.value


class ComponentProps(BaseModel):
    name: str

    @classmethod
    def create(cls, **kwargs):
        return cls.model_validate(kwargs)

    def to_aedt_args(self):
        args = ["NAME:ComponentProps"]
        if self.name is not None:
            args.extend(["Name:=", self.name])
        return args


class Attributes(BaseModel):
    page: int = 1
    x: float
    y: float
    angle: float = 0.0
    flip: bool = False

    @classmethod
    def create(cls, **kwargs):
        kwargs["x"] = convert_to_meter(kwargs.pop("x"))
        kwargs["y"] = convert_to_meter(kwargs.pop("y"))
        return cls.model_validate(kwargs)

    def to_aedt_args(self):
        args = ["NAME:Attributes"]
        if self.page is not None:
            args.extend(["Page:=", self.page])
        if self.x is not None:
            args.extend(["X:=", self.x])
        if self.y is not None:
            args.extend(["Y:=", self.y])
        if self.angle is not None:
            args.extend(["Angle:=", self.angle])
        if self.flip is not None:
            args.extend(["Flip:=", self.flip])
        return args
