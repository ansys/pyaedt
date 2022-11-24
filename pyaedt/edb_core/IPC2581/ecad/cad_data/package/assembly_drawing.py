from pyaedt.edb_core.IPC2581.ecad.cad_data.primitives.polygon import Polygon


class AssemblyDrawing(object):
    """Class describing IPC2581 assembly drawing."""

    def __init__(self, ipc):
        self._ipc = ipc
        self.polygon = Polygon(self._ipc)

    def write_xml(self, step):  # pragma no cover
        pass
