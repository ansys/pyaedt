from pyaedt.edb_core.ipc2581.ecad.cad_data.polygon import Polygon


class Profile(object):
    def __init__(self):
        self._profile = []

    @property
    def profile(self):
        return self._profile

    @profile.setter
    def profile(self, value):  # pragma no cover
        if isinstance(value, list):
            if len([poly for poly in value if isinstance(poly, Polygon)]) == len(value):
                self._profile = value

    def add_polygon(self, polygon):  # pragma no cover
        if isinstance(polygon, Polygon):
            self._profile.append(polygon)

    def xml_writer(self):  # pragma no cover
        pass
