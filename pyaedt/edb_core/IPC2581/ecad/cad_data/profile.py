from pyaedt.edb_core.IPC2581.ecad.cad_data.primitives.polygon import Polygon


class Profile(object):
    def __init__(self):
        self._profile = []

    @property
    def profile(self):
        return self._profile

    @profile.setter
    def profile(self, value):
        if isinstance(value, list):
            if len([poly for poly in value if isinstance(poly, Polygon)]) == len(value):
                self._profile = value

    def add_polygon(self, polygon):
        if isinstance(polygon, Polygon):
            self._profile.append(polygon)

    def xml_writer(self):
        pass
