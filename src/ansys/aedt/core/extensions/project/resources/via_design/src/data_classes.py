from pathlib import Path

import toml
from pydantic import BaseModel, Field
from typing import List, Union, Optional, Dict

from pyedb.configuration.cfg_stackup import CfgStackup, CfgLayer


class BaseDataClass(BaseModel):
    @classmethod
    def create_from_toml(cls, path_toml):
        data = toml.load(path_toml)
        return cls(**data)

    model_config = {
        "populate_by_name": True,
        "populate_by_alias": True
    }

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
    outline_extent: str
    pitch: str


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
    stacked_via = List[ViaDefinition]

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


class ConfigModel(BaseDataClass):
    title: str
    general: General
    stackup: List[CfgLayer] # Todo replace with CfgStackup
    padstack_defs: List[PadstackDef]
    pin_map: List[List[str]]
    signals: Dict[str, Signals]
    differential_signals: Dict[str, DifferentialSignal]
    technologies: Dict[str, Technology]

    def add_layer_at_bottom(self, name, **kwargs):
        self.stackup.append(CfgLayer(name=name, **kwargs))
