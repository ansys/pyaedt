from pyaedt.edb_core.ipc2581.ecad.cad_data.padstack_hole_def import PadstackHoleDef
from pyaedt.edb_core.ipc2581.ecad.cad_data.padstack_pad_def import PadstackPadDef
from pyaedt.generic.general_methods import ET


class PadstackDef(object):
    """Class describing an IPC2581 padstack definition."""

    def __init__(self):
        self.name = ""
        self.padstack_hole_def = PadstackHoleDef()
        self._padstack_pad_def = []

    @property
    def padstack_pad_def(self):
        return self._padstack_pad_def

    @padstack_pad_def.setter
    def padstack_pad_def(self, value):  # pragma no cover
        if isinstance(value, list):
            if len([pad for pad in value if isinstance(pad, PadstackPadDef)]) == len(value):
                self._padstack_pad_def = value

    def add_padstack_pad_def(self, layer="", pad_use="REGULAR", x="0", y="0", primitive_ref=""):  # pragma no cover
        pad = PadstackPadDef()
        pad.layer_ref = layer
        pad.pad_use = pad_use
        pad.x = x
        pad.y = y
        pad.primitive_ref = primitive_ref
        self.padstack_pad_def.append(pad)

    def write_xml(self, step):  # pragma no cover
        padstack_def = ET.SubElement(step, "PadStackDef")
        padstack_def.set("name", self.name)
        self.padstack_hole_def.write_xml(padstack_def)
        for pad in self.padstack_pad_def:
            pad.write_xml(padstack_def)
