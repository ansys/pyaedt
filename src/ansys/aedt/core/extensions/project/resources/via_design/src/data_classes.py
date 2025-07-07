from pathlib import Path

import toml
from pydantic import BaseModel, Field
from typing import List, Union, Optional, Dict


class BaseDataClass(BaseModel):
    @classmethod
    def create_from_toml(cls, path_toml):
        data = toml.load(path_toml)
        return cls(**data)


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


class Layer(BaseDataClass):
    name: str
    type: str
    material: str
    fill_material: Optional[str] = None
    thickness: str


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


class StackedVia(BaseDataClass):
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


class DifferentialSignal(BaseDataClass):
    signals: List[str]
    fanout_trace: List[FanoutTrace]
    stacked_vias: str


class Signals(BaseDataClass):
    fanout_trace: Dict = Field(default_factory=dict)
    stacked_vias: str


class ConfigModel(BaseDataClass):
    title: str
    general: General
    stackup: List[Layer]
    padstack_defs: List[PadstackDef]
    pin_map: List[List[str]]
    signals: Dict[str, Signals]
    differential_signals: Dict[str, DifferentialSignal]
    stacked_vias: Dict[str, List[StackedVia]]


if __name__ == '__main__':
    ConfigModel.create_from_toml(Path(__file__).parent.parent / 'package_diff.toml')
