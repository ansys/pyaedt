import xml.etree.cElementTree as ET

from pyaedt.edb_core.IPC2581.BOM.bom import Bom
from pyaedt.edb_core.IPC2581.BOM.bom_item import BomItem
from pyaedt.edb_core.IPC2581.content.content import Content
from pyaedt.edb_core.IPC2581.ecad.cad_data.padstack_def.padstack_def import PadstackDef
from pyaedt.edb_core.IPC2581.ecad.ecad import Ecad
from pyaedt.edb_core.IPC2581.history_record import HistoryRecord
from pyaedt.edb_core.IPC2581.logistic_header import LogisticHeader
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
        self.ecad = Ecad(self, pedb, units)
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
        self.ecad.design_name = self.design_name
        self.ecad.cad_header.units = self.units
        self.ecad.cad_data.stackup.name = self.design_name
        self.from_meter_to_units(self._pedb.get_statistics().stackup_thickness, self.units)
        layers_name = list(self._pedb.stackup.signal_layers.keys())
        top_bottom_layers = [layers_name[0], layers_name[-1]]

        for layer_name in list(self._pedb.stackup.layers.keys()):
            self.content.add_layer_ref(layer_name)
            layer_color = self._pedb.stackup.layers[layer_name].color
            self.content.dict_colors.add_color(
                "COLOR_{}".format(layer_name), str(layer_color[0]), str(layer_color[1]), str(layer_color[2])
            )
            # Ecad layers

            layer_type = "CONDUCTOR"
            conductivity = 5e6
            permitivity = 1.0
            loss_tg = 0.0
            try:
                material_name = self._pedb.stackup.layers[layer_name]._edb_layer.GetMaterial()
                edb_material = self._pedb.edb.Definition.MaterialDef.FindByName(self._pedb.db, material_name)
                if self._pedb.stackup.layers[layer_name].type == "dielectric":
                    layer_type = "DIELECTRIC"
                    permitivity = edb_material.GetProperty(self._pedb.edb.Definition.MaterialPropertyId.Permittivity)[
                        1
                    ].ToDouble()
                    loss_tg = edb_material.GetProperty(
                        self._pedb.edb.Definition.MaterialPropertyId.DielectricLossTangent
                    )[1].ToDouble()
                if layer_type == "CONDUCTOR":
                    conductivity = edb_material.GetProperty(self._pedb.edb.Definition.MaterialPropertyId.Conductivity)[
                        1
                    ].ToDouble()
                self.ecad.cad_header.add_spec(
                    name=layer_name,
                    material=self._pedb.stackup.layers[layer_name]._edb_layer.GetMaterial(),
                    layer_type=layer_type,
                    conductivity=str(conductivity),
                    dielectric_constant=str(permitivity),
                    loss_tg=str(loss_tg),
                )
                self.ecad.cad_data.add_layer(layer_name=layer_name, layer_side="internal", polarity="positive")
                self.ecad.cad_data.stackup.stackup_group.add_stackup_layer(
                    layer_name=layer_name,
                    thickness=self._pedb.stackup.layers[layer_name].thickness,
                )
            except:
                pass

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

        # step
        # padstackdef
        for padstack_name, padstackdef in self._pedb.core_padstack.padstacks.items():
            padstack_def = PadstackDef()
            padstack_def.name = padstack_name
            padstack_def.padstack_hole_def.name = padstack_name
            if padstackdef.hole_properties:
                padstack_def.padstack_hole_def.diameter = str(padstackdef.hole_properties[0])
            for layer, pad in padstackdef.pad_by_layer.items():
                try:
                    self.content.standard_geometries_dict.add_circle(pad.parameters_value)
                except:
                    pass
                if pad.parameters_values:
                    if pad.geometry_type == 1:
                        primitive_ref = "CIRCLE_{}".format(
                            self.from_meter_to_units(pad.parameters_values[0], self.units)
                        )
                    elif pad.geometry_type == 2:
                        primitive_ref = "RECT_{}_{}".format(
                            self.from_meter_to_units(pad.parameters_values[0], self.units),
                            self.from_meter_to_units(pad.parameters_values[0], self.units),
                        )
                    elif pad.geometry_type == 3:
                        primitive_ref = "RECT_{}_{}".format(
                            self.from_meter_to_units(pad.parameters_values[0], self.units),
                            self.from_meter_to_units(pad.parameters_values[1], self.units),
                        )
                    elif pad.geometry_type == 4:
                        primitive_ref = "OVAL_{}_{}_{}".format(
                            self.from_meter_to_units(pad.parameters_values[0], self.units),
                            self.from_meter_to_units(pad.parameters_values[1], self.units),
                            self.from_meter_to_units(pad.parameters_values[2], self.units),
                        )
                    else:
                        primitive_ref = "Default"
                    padstack_def.add_padstack_pad_def(layer=layer, pad_use="REGULAR", primitive_ref=primitive_ref)
            for layer, antipad in padstackdef.antipad_by_layer.items():
                try:
                    self.content.standard_geometries_dict.add_circle(antipad.parameters_value)
                except:
                    pass
                if antipad.parameters_values:
                    if antipad.geometry_type == 1:
                        primitive_ref = "CIRCLE_{}".format(
                            self.from_meter_to_units(pad.parameters_values[0], self.units)
                        )
                    elif antipad.geometry_type == 2:
                        primitive_ref = "RECT_{}_{}".format(
                            self.from_meter_to_units(pad.parameters_values[0], self.units),
                            self.from_meter_to_units(pad.parameters_values[0], self.units),
                        )
                    elif antipad.geometry_type == 3:
                        primitive_ref = "RECT_{}_{}".format(
                            self.from_meter_to_units(pad.parameters_values[0], self.units),
                            self.from_meter_to_units(pad.parameters_values[1]),
                            self.units,
                        )
                    elif antipad.geometry_type == 4:
                        primitive_ref = "OVAL_{}_{}_{}".format(
                            self.from_meter_to_units(pad.parameters_values[0], self.units),
                            self.from_meter_to_units(pad.parameters_values[1], self.units),
                            self.from_meter_to_units(pad.parameters_values[2], self.units),
                        )
                    else:
                        primitive_ref = "Default"
                    padstack_def.add_padstack_pad_def(layer=layer, pad_use="ANTIPAD", primitive_ref=primitive_ref)
            for layer, thermalpad in padstackdef.thermalpad_by_layer.items():
                try:
                    self.content.standard_geometries_dict.add_circle(thermalpad.parameters_value)
                except:
                    pass
                if thermalpad.parameters_values:
                    if thermalpad.geometry_type == 1:
                        primitive_ref = "CIRCLE_{}".format(
                            self.from_meter_to_units(pad.parameters_values[0], self.units)
                        )
                    elif thermalpad.geometry_type == 2:
                        primitive_ref = "RECT_{}_{}".format(
                            self.from_meter_to_units(pad.parameters_values[0], self.units),
                            self.from_meter_to_units(pad.parameters_values[0], self.units),
                        )
                    elif thermalpad.geometry_type == 3:
                        primitive_ref = "RECT_{}_{}".format(
                            self.from_meter_to_units(pad.parameters_values[0], self.units),
                            self.from_meter_to_units(pad.parameters_values[1], self.units),
                        )
                    elif thermalpad.geometry_type == 4:
                        primitive_ref = "OVAL_{}_{}_{}".format(
                            self.from_meter_to_units(pad.parameters_values[0], self.units),
                            self.from_meter_to_units(pad.parameters_values[1], self.units),
                            self.from_meter_to_units(pad.parameters_values[2], self.units),
                        )
                    else:
                        primitive_ref = "Default"
                    padstack_def.add_padstack_pad_def(layer=layer, pad_use="THERMAL", primitive_ref=primitive_ref)
            if not padstack_def.name in self.ecad.cad_data.cad_data_step.padstack_defs:
                self.ecad.cad_data.cad_data_step.padstack_defs[padstack_def.name] = padstack_def
        # component def
        for refdes, component in self._pedb.core_components.components.items():
            self.ecad.cad_data.cad_data_step.add_component(component=component)
        # component pads
        for _, layer in self._pedb.stackup.layers.items():
            self.ecad.cad_data.cad_data_step.add_layer_feature(layer, top_bottom_layers)
            # viadef
        # adding drill layer feature
        via_list = [
            obj
            for obj in list(self._pedb.core_padstack.padstack_instances.values())
            if not obj.start_layer == obj.stop_layer
        ]
        self.ecad.cad_data.cad_data_step.add_drill_layer_feature(
            via_list, "DRILL_1-{}".format(len(list(self._pedb.stackup.layers.keys())))
        )

    @pyaedt_function_handler()
    def from_meter_to_units(self, value, units):
        if units.lower() == "mm":
            return round(value * 1000, 4)
        if units.lower() == "um":
            return round(value * 1e6, 4)
        if units.lower() == "mils":
            return round(value * 39370.079, 4)
        if units.lower() == "inch":
            return round(value * 39.370079, 4)
        if units.lower() == "cm":
            return round(value * 100, 4)
