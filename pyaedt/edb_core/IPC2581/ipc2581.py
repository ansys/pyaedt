import xml.etree.cElementTree as ET

from pyaedt.edb_core.IPC2581.content.content import Content
from pyaedt.edb_core.IPC2581.ecad.ecad import Ecad
from pyaedt.edb_core.IPC2581.history_record import HistoryRecord
from pyaedt.edb_core.IPC2581.logistic_header import LogisticHeader
from pyaedt.edb_core.IPC2581.BOM.bom import Bom
from pyaedt.edb_core.IPC2581.BOM.bom_item import BomItem
from pyaedt.generic.general_methods import pyaedt_function_handler



class IPC2581(object):
    def __init__(self, pedb, units):
        self.revision = "C"
        self._pedb = pedb
        self.units = units
        self.content = Content(self)
        self.logistic_header = LogisticHeader()
        self.history_record = HistoryRecord()
        self.bom = Bom()
        self.ecad = Ecad(self)
        self.file_path = ""
        self.design_name = ""
        self_datum = ""

    def write_xml(self):
        if self.file_path:
            ipc = ET.Element("IPC-2581")
            ipc.set("revision", self.revision)
            ipc.set("xmlns", "http://webstds.ipc.org/2581")
            ipc.set("xmlns:xsi", "http://www.w3.org/2001/XMLSchema-instance")
            ipc.set("xmlns:xsd", "http://www.w3.org/2001/XMLSchema")
            self.content.write_wml(ipc)
            self.logistic_header.write_xml(ipc)
            self.history_record.write_xml(ipc)
            self.bom.write_xml(ipc)
            self.ecad.write_xml(ipc)

    @pyaedt_function_handler()
    def load_ipc_model(self):
        self.design_name = self._pedb._active_layout.GetCell().GetName()

        for layer_name in list(self._pedb.stackup.layer.keys()):
            self.content.add_layer_ref(layer_name)
            layer_color = self._pedb.stackup.layer[layer_name].color
            self.content.dict_colors.add_color("COLOR_{}".format(layer_name), str(layer_color[0]), str(layer_color[1]),
                                               str(layer_color[2]))

        for path_width in list(set([path.GetWidth() for path in self._pedb.core_primitives.paths])):
            if self.units == "mm":
                converted_width = path_width / 1000
            self.content.dict_line.add_line(str(converted_width))

        # Bom
        for part_name, components in self._pedb.core_components.components_by_partname.items():
            bom_item = BomItem()
            bom_item.part_name = part_name
            bom_item.quantity = len(components)
            bom_item.pin_count = components[0].numpins
            bom_item.category = "ELECTRICAL"
            bom_item.charactistics.device_type = components[0].type
            bom_item.charactistics.category = "ELECTRICAL"
            bom_item.charactistics.component_class = "DISCRETE"
            if components[0].type == "Resistor":
                bom_item.charactistics.value = components[0].res_value
            elif components[0].type == "Capacitor":
                bom_item.charactistics.value = components[0].cap_value
            elif components[0].type == "Inductor":
                bom_item.charactistics.value = components[0].ind_value
            for cmp in components:
                bom_item.add_refdes(cmp.refdes, cmp.placement_layer)

