from pyaedt.generic.general_methods import ET


class PhyNet(object):
    """Class describing an IPC2581 physical net."""

    def __init__(self):
        self._name = ""
        self._phy_net_points = []

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):  # pragma no cover
        if isinstance(value, str):
            self._name = value

    @property
    def phy_net_points(self):
        return self._phy_net_points

    @phy_net_points.setter
    def phy_net_points(self, value):  # pragma no cover
        if isinstance(value, list):
            if len([net for net in value if isinstance(net, PhyNetPoint)]) == len(value):
                self._phy_net_points = value

    def add_phy_net_point(self, point=None):  # pragma no cover
        if isinstance(point, PhyNetPoint):
            self._phy_net_points.append(point)

    def write_xml(self, step):  # pragma no cover
        if step:
            phy_net = ET.SubElement(step, "PhyNet")
            for phy_net_point in self.phy_net_points:
                phy_net_point.write_xml(phy_net)


class PhyNetPoint(object):
    """Class describing an IPC2581 physical net point."""

    def __init__(self):
        self.x = 0.0
        self.y = 0.0
        self.layer_ref = ""
        self.net_node_type = ""
        self._exposure = ExposureType().Exposed
        self.via = ""
        self.standard_primitive_id = ""

    @property
    def exposure(self):
        if self._exposure == ExposureType.Exposed:
            return "EXPOSED"
        elif self._exposure == ExposureType.CoveredPrimary:
            return "COVERED_PRIMARY"
        elif self._exposure == ExposureType.CoveredSecondary:
            return "COVERED_SECONDARY"

    def write_xml(self, phynet):  # pragma no cover
        if phynet:
            phynet_point = ET.SubElement(phynet, "PhyNetPoint")
            phynet_point.set("x", self.x)
            phynet_point.set("y", self.y)
            phynet_point.set("layerRef", self.layer_ref)
            phynet_point.set("netNode", self.net_node_type)
            phynet_point.set("exposure", self.exposure)
            phynet_point.set("via", self.via)
            primitive_ref = ET.SubElement(phynet_point, "StandardPrimitiveRef")
            primitive_ref.set("id", self.standard_primitive_id)


class NetNodeType(object):
    (Middle, End) = range(0, 2)


class ExposureType(object):
    (CoveredPrimary, CoveredSecondary, Exposed) = range(0, 3)
