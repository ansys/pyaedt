import json
from pathlib import Path
from typing import Union, Optional, List, Dict

from pyaedt import Hfss
from ansys.aedt.core.generic.constants import Axis
from pydantic import BaseModel, Field


class Arrange(BaseModel):
    operation: str
    axis: Optional[str] = "X"
    angle: Optional[str] = "0deg"
    vector: Optional[list[Union[str]]] = ["0mm", "0mm", "0mm"]


class Component(BaseModel):
    component_type: str
    name: str
    file_path: str
    reference_coordinate_system: str = "Global"
    target_coordinate_system: str
    layout_coordinate_systems : Optional[ List[str]] = Field(default_factory=list)
    arranges: List[Arrange] = Field(default_factory=list)
    sub_components: Optional[Dict] = Field(default_factory=dict)

    @classmethod
    def load(cls, name, data):
        sub_components = {name:cls.load(name, comp) for name, comp in data.get("sub_components", {}).items()}
        data_ = data.copy()
        data_["sub_components"] = sub_components
        data_["name"] = name
        return cls(**data_)


    def assemble_sub_components(self, hfss, cs_prefix=""):
        for name, comp in self.sub_components.items():
            comp.assemble(hfss, cs_prefix)

    def apply_arrange(self, hfss):
        for i in self.arranges:
            if i.operation == "rotate":
                hfss.modeler.rotate(self.name, getattr(Axis, i.axis), i.angle)
            elif i.operation == "move":
                hfss.modeler.move(self.name, i.vector)

    def assemble(self, hfss, cs_prefix=None):
        """
        Parameters
        ----------
         cs_prefix : str
            This is the name of the component definition.
        """
        if cs_prefix:
            self.target_coordinate_system = f"{cs_prefix}_{self.target_coordinate_system}"

        if self.component_type == "mcad":
            comp = hfss.modeler.insert_3d_component(
                name=self.name,
                input_file=self.file_path,
                coordinate_system=self.target_coordinate_system,
            )
            temp = None
        else:
            comp = hfss.modeler.insert_layout_component(
                input_file=self.file_path,
                coordinate_system=self.target_coordinate_system,
                reference_coordinate_system=self.reference_coordinate_system,
                layout_coordinate_systems=self.layout_coordinate_systems,
                name=self.name,
            )
            temp = comp.definition_name

        if comp is False:
            raise ValueError(self.name, self.file_path, self.target_coordinate_system)

        self.apply_arrange(hfss)
        if self.sub_components:
            self.assemble_sub_components(hfss, cs_prefix=temp)

Component.model_rebuild()


class MCADAssemblyBackend(BaseModel):

    coordinate_system : Dict[str, Dict[str, Union[str, List[str]]]] = Field(default_factory=dict)
    sub_components : Dict[str, Component] = Field(default_factory=dict)
    component_models: Optional[Dict[str, str]] = Field(default_factory=dict)

    @classmethod
    def load(cls, data):

        return cls(coordinate_system=data.get("coordinate_system", {}),
                   sub_components={name: Component.load(name, comp) for name, comp in data.get("assembly", {}).items()})

    def run(self, hfss):
        for name, value in self.coordinate_system.items():
            hfss.modeler.create_coordinate_system(name=name, **value)

        for name, comp in self.sub_components.items():
            comp.assemble(hfss)


if __name__ == '__main__':
    from ansys.aedt.core.extensions.hfss.mcad_assembly.template import DATA

    app = MCADAssemblyBackend.load(data=DATA)

    app_hfss = Hfss(specified_version="2025.1", new_desktop_session=False, solution_type="DrivenTerminal")
    app.run(app_hfss)
    app_hfss.release_desktop(False, False)
