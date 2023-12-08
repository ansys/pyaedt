from pyaedt.edb_core.ipc2581.ecad.cad_data.layer_feature import LayerFeature
from pyaedt.generic.general_methods import ET


class Profile(object):
    def __init__(self, ipc):
        self._profile = []
        self._ipc = ipc

    @property
    def profile(self):
        return self._profile

    @profile.setter
    def profile(self, value):  # pragma no cover
        if isinstance(value, list):
            if len([poly for poly in value if isinstance(poly, LayerFeature)]) == len(value):
                self._profile = value

    def add_polygon(self, polygon):  # pragma no cover
        if isinstance(polygon, LayerFeature):
            self._profile.append(polygon)

    def xml_writer(self, step):  # pragma no cover
        profile = ET.SubElement(step, "Profile")
        for poly in self.profile:
            for feature in poly.features:
                if feature.feature_type == 0:
                    polygon = ET.SubElement(profile, "Polygon")
                    polygon_begin = ET.SubElement(polygon, "PolyBegin")
                    polygon_begin.set(
                        "x", str(self._ipc.from_meter_to_units(feature.polygon.poly_steps[0].x, self._ipc.units))
                    )
                    polygon_begin.set(
                        "y", str(self._ipc.from_meter_to_units(feature.polygon.poly_steps[0].y, self._ipc.units))
                    )
                    for poly_step in feature.polygon.poly_steps[1:]:
                        poly_step.write_xml(polygon, self._ipc)
                    for cutout in feature.polygon.cutout:
                        cutout.write_xml(profile, self._ipc)
