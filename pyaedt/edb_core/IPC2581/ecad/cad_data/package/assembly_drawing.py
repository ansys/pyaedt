from pyaedt.edb_core.IPC2581.ecad.cad_data.primitives.polygon import Polygon


class AssemblyDrawing(object):
    def __init__(self):
        self.polygon = Polygon()

    def write_xml(self, step):
        pass
