import xml.etree.cElementTree as ET


class Characteristics(object):
    def __init__(self):
        self.category = "ELECTRICAL"
        self.device_type = ""
        self.component_class = ""
        self.value = ""

    def write_xml(self, bom_item):
        if bom_item:
            characteristic = ET.SubElement(bom_item, "Characteristics")
            characteristic.set("category", self.category)
            component_type = ET.SubElement(characteristic, "Textual")
            component_type.set("definitionSource", "ANSYS")
            component_type.set("textualCharacteristicName", "DEVICE_TYPE")
            component_type.set("textualCharacteristicValue", "{}_{}".format(self.device_type, self.value))
            component_class = ET.SubElement(characteristic, "Textual")
            component_class.set("definitionSource", "ANSYS")
            component_class.set("textualCharacteristicName", "COMP_CLASS")
            component_class.set("textualCharacteristicValue", "{}".format(self.component_class))
            component_value = ET.SubElement(characteristic, "Textual")
            component_value.set("definitionSource", "ANSYS")
            component_value.set("textualCharacteristicName", "VALUE")
            component_value.set("textualCharacteristicValue", "{}".format(self.value))
            component_parent_type = ET.SubElement(characteristic, "Textual")
            component_parent_type.set("definitionSource", "ANSYS")
            component_parent_type.set("textualCharacteristicName", "PARENT_PPT_PART")
            component_parent_type.set("textualCharacteristicValue", "{}_{}".format(self.device_type, self.value))
            component_parent = ET.SubElement(characteristic, "Textual")
            component_parent.set("definitionSource", "ANSYS")
            component_parent.set("textualCharacteristicName", "PARENT_PPT")
            component_parent.set("textualCharacteristicValue", "{}".format(self.device_type))
            component_parent2 = ET.SubElement(characteristic, "Textual")
            component_parent2.set("definitionSource", "ANSYS")
            component_parent2.set("textualCharacteristicName", "PARENT_PART_TYPE")
            component_parent2.set("textualCharacteristicValue", "{}".format(self.device_type))
