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

from typing import Dict
from typing import List
from typing import Optional
from typing import Union

from pydantic import BaseModel
from pydantic import Field
from pyedb.configuration.cfg_stackup import CfgLayer


class BaseDataClass(BaseModel, validate_assignment=True):
    model_config = {"populate_by_name": True, "populate_by_alias": True}


class ConnectionTrace(BaseDataClass):
    width: str
    clearance: str


class StitchingVias(BaseDataClass):
    start_angle: int
    step_angle: int
    number_of_vias: int
    distance: str


class SolderBallParameters(BaseDataClass):
    shape: str
    diameter: str
    mid_diameter: str
    placement: str
    material: str


class PadstackDef(BaseDataClass):
    name: str
    shape: str
    pad_diameter: str
    hole_diameter: str
    hole_range: str
    solder_ball_parameters: Optional[SolderBallParameters] = None


class General(BaseDataClass):
    version: str
    output_dir: str


class Port(BaseDataClass):
    horizontal_extent_factor: int
    vertical_extent_factor: int


class FanoutTrace(BaseDataClass):
    via_index: int
    layer: str
    width: str
    separation: str
    clearance: str
    incremental_path_dy: List[str]
    end_cap_style: str
    flip_dx: bool
    flip_dy: bool
    port: Port


class ViaDefinition(BaseDataClass):
    padstack_def: str
    start_layer: str
    stop_layer: str
    dx: Union[str, int]
    dy: Union[str, int]
    flip_dx: bool
    flip_dy: bool
    anti_pad_diameter: str
    connection_trace: Union[ConnectionTrace, bool]
    with_solder_ball: bool
    backdrill_parameters: Union[bool, Dict]  # can be expanded later
    stitching_vias: Union[StitchingVias, bool]


class Technology(BaseDataClass):
    stacked_via: List[ViaDefinition]

    def validation(self):
        # todo
        return


class DifferentialSignal(BaseDataClass):
    signals: List[str]
    fanout_trace: List[FanoutTrace]
    technology: str


class Signals(BaseDataClass):
    fanout_trace: Dict = Field(default_factory=dict)
    technology: str


class Placement(BaseDataClass):
    pin_map: List[List[str]]
    pitch: str
    outline_extent: str


class ConfigModel(BaseDataClass):
    title: str
    general: General
    stackup: List[CfgLayer]  # Todo replace with CfgStackup
    padstack_defs: List[PadstackDef]
    placement: Placement
    signals: Dict[str, Signals]
    differential_signals: Dict[str, DifferentialSignal]
    technologies: Dict[str, Technology]

    def add_layer_at_bottom(self, name, **kwargs):
        self.stackup.append(CfgLayer(name=name, **kwargs))
