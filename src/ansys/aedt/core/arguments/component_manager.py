from pydantic import BaseModel, Field


class Files(BaseModel):
    files: List[str] = Field(..., min_length=1)

    @classmethod
    def create(cls, **kwargs):
        return cls.model_validate(kwargs)

    def to_aedt_args(self):
        args = ["NAME:Files"]
        if self.files is not None: args.extend(["Files:=", self.files])
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
        if self.num_ports_or_lines is not None: args.extend(["NumPortsOrLines:=", self.num_ports_or_lines])
        args.extend(["CreateArray:=", True])
        if self.array_name is not None: args.extend(["ArrayName:=", self.array_name])
        if self.array_id_name is not None: args.extend(["ArrayIdName:=", self.array_id_name])
        args.extend(["CompType:=", 2])
        if self.comp_name is not None: args.extend(["CompName:=", self.comp_name])
        return args