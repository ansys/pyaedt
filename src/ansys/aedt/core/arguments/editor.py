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
        if self.name is not None: args.extend(["Name:=", self.name])
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
        if self.page is not None: args.extend(["Page:=", self.page])
        if self.x is not None: args.extend(["X:=", self.x])
        if self.y is not None: args.extend(["Y:=", self.y])
        if self.angle is not None: args.extend(["Angle:=", self.angle])
        if self.flip is not None: args.extend(["Flip:=", self.flip])
        return args