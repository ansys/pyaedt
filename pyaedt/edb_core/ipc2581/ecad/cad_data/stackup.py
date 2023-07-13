from pyaedt.edb_core.ipc2581.ecad.cad_data.stackup_group import StackupGroup
from pyaedt.generic.general_methods import ET


class Stackup(object):
    def __init__(self):
        self.name = "PRIMARY"
        self.total_thickness = 0.0
        self.tol_plus = 0.0
        self.tol_min = 0.0
        self.where_measured = "METAL"
        self._stackup_group = StackupGroup()

    @property
    def stackup_group(self):
        return self._stackup_group

    @stackup_group.setter
    def stackup_group(self, value):  # pragma no cover
        if isinstance(value, list):
            if len([stack_grp for stack_grp in value if isinstance(stack_grp, StackupGroup)]):
                self._stackup_group = value

    def write_xml(self, cad_data):  # pragma no cover
        stackup = ET.SubElement(cad_data, "Stackup")
        stackup.set("name", self.name)
        stackup.set("overallThickness", str(self.total_thickness))
        stackup.set("tolPlus", str(self.tol_plus))
        stackup.set("tolMinus", str(self.tol_min))
        stackup.set("whereMeasured", self.where_measured)
        self.stackup_group.write_xml(stackup)
