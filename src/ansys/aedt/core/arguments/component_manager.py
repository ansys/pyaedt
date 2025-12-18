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
from pydantic import Field


class Files(BaseModel):
    files: List[str] = Field(..., min_length=1)

    @classmethod
    def create(cls, **kwargs):
        return cls.model_validate(kwargs)

    def to_aedt_args(self):
        args = ["NAME:Files"]
        if self.files is not None:
            args.extend(["Files:=", self.files])
        return args


class Options(BaseModel):
    num_ports_or_lines: int = Field(..., ge=1)
    array_name: str
    array_id_name: str
    comp_name: str

    @classmethod
    def create(cls, **kwargs):
        return cls.model_validate(kwargs)

    def to_aedt_args(self):
        args = ["NAME:Options"]
        if self.num_ports_or_lines is not None:
            args.extend(["NumPortsOrLines:=", self.num_ports_or_lines])
        args.extend(["CreateArray:=", True])
        if self.array_name is not None:
            args.extend(["ArrayName:=", self.array_name])
        if self.array_id_name is not None:
            args.extend(["ArrayIdName:=", self.array_id_name])
        args.extend(["CompType:=", 2])
        if self.comp_name is not None:
            args.extend(["CompName:=", self.comp_name])
        return args
