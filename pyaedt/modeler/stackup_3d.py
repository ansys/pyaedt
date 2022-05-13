from math import exp
from math import log
from math import pi
from math import sqrt

from pyaedt import constants


class Layers:
    def __init__(
        self,
        application,
        layer_list=[
            ["G", "Ground", "copper", 0.035, "air"],
            ["D", "Dielectric", "Duroid (tm)", 1.54],
            ["S", "Top", "copper", 0.035, "air"],
        ],
    ):
        self.__application = application
        self.__layer_name = []
        self.__layer_position = []
        self.__layer_values = layer_list
        self.__dielectric_list = []
        self.__dielectric_name_list = []
        self.__ground_list = []
        self.__ground_name_list = []
        self.__ground_fill_material = []
        self.__signal_list = []
        self.__signal_name_list = []
        self.__signal_material = []
        self.__object_list = []
        z_position_offset = 0
        first_layer_position = "layer_1_position"
        application[first_layer_position] = "0mm"
        application["dielectric_x_position"] = "0mm"
        application["dielectric_y_position"] = "0mm"
        application["dielectric_length"] = "1000mm"
        application["dielectric_width"] = "1000mm"
        for layer in layer_list:
            index = layer_list.index(layer)
            shifted_index = index + 1
            if layer[0] == "S":
                layer_type = "signal"
                if isinstance(layer[1], str):
                    layer[1] = layer[1] + "_S"
                else:
                    raise TypeError("The %i layer name must be a string" % shifted_index)
            elif layer[0] == "G":
                layer_type = "ground"
                if isinstance(layer[1], str):
                    layer[1] = layer[1] + "_G"
                else:
                    raise TypeError("The %i layer name must be a string" % shifted_index)
            elif layer[0] == "D":
                layer_type = "dielectric"
                if isinstance(layer[1], str):
                    layer[1] = layer[1] + "_D"
                else:
                    raise TypeError("The %i layer name must be a string" % shifted_index)
            else:
                raise TypeError(
                    "The 0 index element of the %i layer is incorrect,"
                    " it must only be a string: S, G, D" % shifted_index
                )

            self.__layer_name.append(layer[1])
            self.__layer_position.append(z_position_offset)
            if layer_type == "dielectric":
                if isinstance(layer[2], str):
                    cloned_material = self.duplicate_parametrize_material(layer[2])
                    if cloned_material:
                        if isinstance(layer[3], float) or isinstance(layer[3], int):
                            thickness_variable = layer[1] + "_thickness"
                            application[thickness_variable] = str(layer[3]) + "mm"
                            layer_position = "layer_" + str(shifted_index) + "_position"
                            dielectric_layer = application.modeler.primitives.create_box(
                                ["dielectric_x_position", "dielectric_y_position", layer_position],
                                ["dielectric_length", "dielectric_width", thickness_variable],
                                name=layer[1],
                                matname=cloned_material.name,
                            )
                            if dielectric_layer:
                                self.__dielectric_list.append(dielectric_layer)
                                self.__dielectric_name_list.append(layer[1])
                                z_position_offset = z_position_offset + layer[3]
                                next_layer_position = "layer_" + str(shifted_index + 1) + "_position"
                                application[next_layer_position] = layer_position + "+" + thickness_variable
                            else:
                                application.logger.error("Generation of the dielectric layer does not work.")
                        else:
                            raise TypeError("The %i layer thickness must be an int or a float" % shifted_index)
                else:
                    raise TypeError("The %i layer material name must be a string" % shifted_index)
            elif layer_type == "ground":
                if len(layer) == 2:
                    layer_position = "layer_" + str(shifted_index) + "_position"
                    ground_layer = application.modeler.primitives.create_rectangle(
                        "Z",
                        ["dielectric_x_position", "dielectric_y_position", layer_position],
                        ["dielectric_length", "dielectric_width"],
                        name=layer[1],
                        matname="copper",
                    )
                    if ground_layer:
                        self.__ground_list.append(ground_layer)
                        self.__ground_name_list.append(layer[1])
                        self.__ground_fill_material.append("FR4_epoxy")
                        next_layer_position = "layer_" + str(shifted_index + 1) + "_position"
                        application[next_layer_position] = layer_position
                    else:
                        application.logger.error("Generation of the ground layer does not work.")
                else:
                    if isinstance(layer[2], str):
                        material_name = self.duplicate_parametrize_material(layer[2]).name
                    elif layer[2] is None:
                        material_name = "copper"
                    else:
                        raise TypeError("The %i layer material name must be a string" % index + 1)
                    if isinstance(layer[4], str):
                        fill_material = self.duplicate_parametrize_material(layer[4]).name
                    elif layer[4] is None:
                        fill_material = "FR4_epoxy"
                    else:
                        raise TypeError("The %i layer thickness must be a string" % index + 1)
                    if isinstance(layer[3], float) or isinstance(layer[3], int):
                        thickness_variable = layer[1] + "_thickness"
                        application[thickness_variable] = str(layer[3]) + "mm"
                        layer_position = "layer_" + str(shifted_index) + "_position"
                        ground_layer = application.modeler.primitives.create_box(
                            ["dielectric_x_position", "dielectric_y_position", layer_position],
                            ["dielectric_length", "dielectric_width", thickness_variable],
                            name=layer[1],
                            matname=material_name,
                        )
                        if ground_layer:
                            self.__ground_list.append(ground_layer)
                            self.__ground_name_list.append(layer[1])
                            self.__ground_fill_material.append(fill_material)
                            z_position_offset = z_position_offset + layer[3]
                            next_layer_position = "layer_" + str(shifted_index + 1) + "_position"
                            application[next_layer_position] = layer_position + "+" + thickness_variable
                        else:
                            application.logger.error("Generation of the ground layer does not work.")
                    elif layer[3] is None:
                        layer_position = "layer_" + str(shifted_index) + "_position"
                        ground_layer = application.modeler.primitives.create_rectangle(
                            "Z",
                            ["dielectric_x_position", "dielectric_y_position", layer_position],
                            ["dielectric_length", "dielectric_width"],
                            name=layer[1],
                            matname=material_name,
                        )
                        if ground_layer:
                            self.__ground_list.append(ground_layer)
                            self.__ground_name_list.append(layer[1])
                            self.__ground_fill_material.append("fill_material")
                            next_layer_position = "layer_" + str(shifted_index + 1) + "_position"
                            application[next_layer_position] = layer_position
                        else:
                            application.logger.error("Generation of the ground layer does not work.")
                    else:
                        application.logger.error("The %i layer thickness must be a string" % index + 1)
            elif layer_type == "signal":
                if len(layer) == 2:
                    layer_position = "layer_" + str(shifted_index) + "_position"
                    signal_layer = application.modeler.primitives.create_rectangle(
                        "Z",
                        ["dielectric_x_position", "dielectric_y_position", layer_position],
                        ["dielectric_length", "dielectric_width"],
                        name=layer[1],
                        matname="FR4_epoxy",
                    )
                    if signal_layer:
                        self.__signal_list.append(signal_layer)
                        self.__signal_name_list.append(layer[1])
                        self.__signal_material.append("copper")
                        next_layer_position = "layer_" + str(shifted_index + 1) + "_position"
                        application[next_layer_position] = layer_position
                    else:
                        application.logger.error("Generation of the ground layer does not work.")
                else:
                    if isinstance(layer[2], str):
                        material_name = self.duplicate_parametrize_material(layer[2]).name
                    elif layer[2] is None:
                        material_name = "copper"
                    else:
                        raise TypeError("The %i layer material name must be a string" % index + 1)
                    if isinstance(layer[4], str):
                        fill_material = self.duplicate_parametrize_material(layer[4]).name
                    elif layer[4] is None:
                        fill_material = "FR4_epoxy"
                    else:
                        raise TypeError("The %i layer thickness must be a string" % index + 1)
                    if isinstance(layer[3], float) or isinstance(layer[3], int):
                        thickness_variable = layer[1] + "_thickness"
                        application[thickness_variable] = str(layer[3]) + "mm"
                        layer_position = "layer_" + str(shifted_index) + "_position"
                        signal_layer = application.modeler.primitives.create_box(
                            ["dielectric_x_position", "dielectric_y_position", layer_position],
                            ["dielectric_length", "dielectric_width", thickness_variable],
                            name=layer[1],
                            matname=fill_material,
                        )
                        if signal_layer:
                            self.__signal_list.append(signal_layer)
                            self.__signal_name_list.append(layer[1])
                            self.__signal_material.append(material_name)
                            z_position_offset = z_position_offset + layer[3]
                            next_layer_position = "layer_" + str(shifted_index + 1) + "_position"
                            application[next_layer_position] = layer_position + "+" + thickness_variable
                        else:
                            application.logger.error("Generation of the ground layer does not work.")
                    elif layer[3] is None:
                        layer_position = "layer_" + str(shifted_index) + "_position"
                        signal_layer = application.modeler.primitives.create_rectangle(
                            "Z",
                            ["dielectric_x_position", "dielectric_y_position", layer_position],
                            ["dielectric_length", "dielectric_width"],
                            name=layer[1],
                            matname=fill_material,
                        )
                        if signal_layer:
                            self.__signal_list.append(signal_layer)
                            self.__signal_name_list.append(layer[1])
                            self.__signal_material.append(material_name)
                            next_layer_position = "layer_" + str(shifted_index + 1) + "_position"
                            application[next_layer_position] = layer_position
                        else:
                            application.logger.error("Generation of the ground layer does not work.")
                    else:
                        application.logger.error("The %i layer thickness must be a string" % index + 1)

    def duplicate_parametrize_material(self, material_name, cloned_material_name=None, list_of_properties=None):
        application = self.__application
        if self.__application.materials.checkifmaterialexists(material_name):
            if not cloned_material_name:
                cloned_material_name = "cloned_" + material_name
            if not self.__application.materials.checkifmaterialexists(cloned_material_name):
                if not list_of_properties:
                    cloned_material = application.materials.duplicate_material(material_name, cloned_material_name)
                    permittivity = cloned_material.permittivity.value
                    permeability = cloned_material.permeability.value
                    conductivity = cloned_material.conductivity.value
                    dielectric_loss_tan = cloned_material.dielectric_loss_tangent.value
                    magnetic_loss_tan = cloned_material.magnetic_loss_tangent.value
                    reformat_name = _replace_by_underscore(" ", cloned_material_name)
                    reformat_name = _replace_by_underscore("(", reformat_name)
                    reformat_name = _replace_by_underscore(")", reformat_name)
                    reformat_name = _replace_by_underscore("/", reformat_name)
                    reformat_name = _replace_by_underscore("-", reformat_name)
                    reformat_name = _replace_by_underscore(".", reformat_name)
                    reformat_name = _replace_by_underscore(",", reformat_name)
                    permittivity_variable = "$" + reformat_name + "_permittivity"
                    permeability_variable = "$" + reformat_name + "_permeability"
                    conductivity_variable = "$" + reformat_name + "_conductivity"
                    dielectric_loss_variable = "$" + reformat_name + "_dielectric_loss"
                    magnetic_loss_variable = "$" + reformat_name + "_magnetic_loss"
                    application[permittivity_variable] = str(permittivity)
                    application[permeability_variable] = str(permeability)
                    application[conductivity_variable] = str(conductivity)
                    application[dielectric_loss_variable] = str(dielectric_loss_tan)
                    application[magnetic_loss_variable] = str(magnetic_loss_tan)
                    cloned_material.permittivity = permittivity_variable
                    cloned_material.permeability = permeability_variable
                    cloned_material.conductivity = conductivity_variable
                    cloned_material.dielectric_loss_tangent = dielectric_loss_variable
                    cloned_material.magnetic_loss_tangent = magnetic_loss_variable
                    return cloned_material
            else:
                application.logger.warning(
                    "The material %s has been already cloned,"
                    " if you want to clone it again pass in argument"
                    " the named of the clone" % material_name
                )
                return application.materials[cloned_material_name]
        else:
            application.logger.error("The material name %s doesn't exist" % material_name)
            return None

    def resize(self, percentage_offset):
        list_of_2d_points = []
        list_of_x_coordinates = []
        list_of_y_coordinates = []
        for object in self.__object_list:
            points_list_by_object = object.points_on_layer
            list_of_2d_points = points_list_by_object + list_of_2d_points
        for point in list_of_2d_points:
            list_of_x_coordinates.append(point[0])
            list_of_y_coordinates.append(point[1])
        maximum_x = max(list_of_x_coordinates)
        minimum_x = min(list_of_x_coordinates)
        maximum_y = max(list_of_y_coordinates)
        minimum_y = min(list_of_y_coordinates)
        variation_x = maximum_x - minimum_x
        variation_y = maximum_y - minimum_y
        self.__application["dielectric_x_position"] = str(minimum_x - variation_x / 2 * percentage_offset / 100) + "mm"
        self.__application["dielectric_y_position"] = str(minimum_y - variation_y / 2 * percentage_offset / 100) + "mm"
        self.__application["dielectric_length"] = str(maximum_x + variation_x * percentage_offset / 100) + "mm"
        self.__application["dielectric_width"] = str(maximum_y + variation_y * percentage_offset / 100) + "mm"

    def resize_around_patch(self):
        self.__application["dielectric_x_position"] = "patch_position_x - patch_length * 50 / 100"
        self.__application["dielectric_y_position"] = "patch_position_y - patch_width * 50 / 100"
        self.__application["dielectric_length"] = (
            "abs(patch_position_x + patch_length * (1 + 50 / 100)) +" " abs(dielectric_x_position)"
        )
        self.__application["dielectric_width"] = (
            "abs(patch_position_y + patch_width * (1 + 50 / 100)) +" " abs(dielectric_y_position)"
        )

    def create_region(self, pad_percent=None):
        if pad_percent is None:
            pad_percent = [50, 50, 5000, 50, 50, 100]
        return self.__application.modeler.primitives.create_region(pad_percent)

    def patch(
        self,
        frequency,
        patch_width,
        signal_layer_name,
        patch_length=None,
        patch_position_x=0,
        patch_position_y=0,
        patch_name="patch",
        metric_unit="mm",
    ):
        application = self.__application
        if isinstance(signal_layer_name, str):
            for i in range(len(self.__layer_name)):
                if self.__layer_name[i] == signal_layer_name or self.__layer_name[i] == signal_layer_name + "_S":
                    signal_layer_name = self.__layer_name[i]
                    signal_layer_number = i + 1
                    index = self.__signal_name_list.index(signal_layer_name)
                    patch_material = self.__signal_material[index]
                    patch_position_z = self.__layer_position[i]
                    if len(self.__layer_values[i]) == 2:
                        patch_thickness = None
                    else:
                        patch_thickness = self.__layer_values[i][3]
                    if self.__layer_values[i - 1][1].split("_")[-1] == "D":
                        try:
                            below_material = self.__layer_values[i - 1][2]
                            substrat_thickness = self.__layer_values[i - 1][3]
                            break
                        except:
                            self.__application.logger.error("The dielectric thickness or material name are incorrect")
                    else:
                        self.__application.logger.error("The layer below the selected one must be of dielectric type")
                        return False
        created_patch = Patch(
            application,
            frequency,
            substrat_thickness,
            patch_width,
            signal_layer_name,
            signal_layer_number,
            patch_length=patch_length,
            patch_thickness=patch_thickness,
            patch_material=patch_material,
            patch_position_x=patch_position_x,
            patch_position_y=patch_position_y,
            patch_position_z=patch_position_z,
            patch_name=patch_name,
            metric_unit=metric_unit,
            below_material=below_material,
        )
        self.__object_list.append(created_patch)
        return created_patch

    def line(
        self,
        frequency,
        line_length,
        line_impedance,
        signal_layer_name,
        line_width=None,
        line_electrical_length=None,
        line_position_x=0,
        line_position_y=0,
        line_name="line",
        metric_unit="mm",
    ):
        application = self.__application
        if isinstance(signal_layer_name, str):
            for i in range(len(self.__layer_name)):
                if self.__layer_name[i] == signal_layer_name or self.__layer_name[i] == signal_layer_name + "_S":
                    signal_layer_name = self.__layer_name[i]
                    signal_layer_number = i + 1
                    index = self.__signal_name_list.index(signal_layer_name)
                    line_material = self.__signal_material[index]
                    line_position_z = self.__layer_position[i]
                    if len(self.__layer_values[i]) == 2:
                        line_thickness = None
                    else:
                        line_thickness = self.__layer_values[i][3]
                    if self.__layer_values[i - 1][1].split("_")[-1] == "D":
                        try:
                            below_material = self.__layer_values[i - 1][2]
                            substrat_thickness = self.__layer_values[i - 1][3]
                            break
                        except:
                            self.__application.logger.error("The dielectric thickness or material name are incorrect")
                    else:
                        self.__application.logger.error("The layer below the selected one must be of dielectric type")
                        return False
        created_line = Line(
            application,
            frequency,
            substrat_thickness,
            line_impedance,
            line_width,
            signal_layer_name,
            signal_layer_number,
            line_length=line_length,
            line_electrical_length=line_electrical_length,
            line_thickness=line_thickness,
            line_material=line_material,
            line_position_x=line_position_x,
            line_position_y=line_position_y,
            line_position_z=line_position_z,
            line_name=line_name,
            metric_unit=metric_unit,
            below_material=below_material,
        )
        self.__object_list.append(created_line)
        return created_line


def _replace_by_underscore(character, string):
    if not isinstance(character, str):
        raise TypeError("character must be str")
    if not isinstance(character, str):
        raise TypeError("string must be str")
    reformat_name = list(string)
    while character in reformat_name:
        index = reformat_name.index(character)
        reformat_name[index] = "_"
    return "".join(reformat_name)


class Patch:
    def __init__(
        self,
        application,
        frequency,
        substrat_thickness,
        patch_width,
        signal_layer_name,
        signal_layer_number,
        patch_length=None,
        patch_thickness=None,
        patch_material="copper",
        patch_position_x=0,
        patch_position_y=0,
        patch_position_z=0,
        patch_name="patch",
        metric_unit="mm",
        below_material="Duroid (tm)",
    ):
        self.__frequency = frequency
        self.__substrat_thickness = substrat_thickness
        self.__width = patch_width
        self.__position_x = patch_position_x
        self.__position_y = patch_position_y
        self.__position_z = patch_position_z
        self.__metric_unit = metric_unit
        self.__material_name = below_material
        self.__signal_material = patch_material
        self.__layer_name = signal_layer_name
        self.__patch_name = patch_name
        self.__layer_number = signal_layer_number
        self.__patch_thickness = patch_thickness
        self.__application = application
        self.__aedt_object = None
        if application.materials.checkifmaterialexists(below_material):
            self.__material = application.materials[below_material]
            self.__permittivity = float(self.__material.permittivity.value)
        else:
            application.logger.error("Material doesn't exist, you must create it in using: import_materials_from_file")
        if isinstance(patch_length, float) or isinstance(patch_length, int):
            self.__length = patch_length
            self.__effective_permittivity = self.effective_permittivity_calcul
            self.__wave_length = self.wave_length_calcul
        elif patch_length is None:
            self.__effective_permittivity = self.effective_permittivity_calcul
            self.__added_length = self.added_length_calcul
            self.__wave_length = self.wave_length_calcul
            self.__length = self.length_calcul
        self.__impedance = self.impedance_calcul
        self.make_design_variable(patch_length)
        if patch_thickness:
            self.__aedt_object = application.modeler.primitives.create_box(
                position=["patch_position_x", "patch_position_y", "layer_" + str(signal_layer_number) + "_position"],
                dimensions_list=["patch_length", "patch_width", signal_layer_name + "_thickness"],
                name=patch_name,
                matname=patch_material,
            )
        else:
            self.__aedt_object = application.modeler.primitives.create_rectangle(
                position=["patch_position_x", "patch_position_y", "layer_" + str(signal_layer_number) + "_position"],
                dimension_list=["patch_length", "patch_width"],
                name=patch_name,
                matname=patch_material,
            )
        application.modeler.subtract(blank_list=[signal_layer_name], tool_list=[patch_name], keepOriginals=True)

    def make_design_variable(self, length):
        self.application["patch_frequency"] = str(self.__frequency) + "Hz"
        self.application["substrat_thickness"] = str(self.__substrat_thickness) + "mm"
        self.application["patch_width"] = str(self.__width) + "mm"
        self.application["patch_position_x"] = str(self.__position_x) + "mm"
        self.application["patch_position_y"] = str(self.__position_y) + "mm"
        self.application["substrat_permittivity"] = str(self.__permittivity)
        patch_eff_permittivity_formula = (
            "(substrat_permittivity + 1)/2 + (substrat_permittivity - 1)/"
            "(2 * sqrt(1 + 10 * substrat_thickness/patch_width))"
        )
        self.application["patch_eff_permittivity"] = patch_eff_permittivity_formula
        patch_wave_length_formula = "c0 * 1000/(patch_frequency * sqrt(patch_eff_permittivity))"
        self.application["patch_wave_length"] = patch_wave_length_formula + "mm"
        if isinstance(length, float) or isinstance(length, int):
            self.application["patch_length"] = str(self.__length) + "mm"
        elif length is None:
            patch_added_length_formula = (
                "0.412 * substrat_thickness * (patch_eff_permittivity + 0.3)"
                " * (patch_width/substrat_thickness + 0.264)"
                " / ((patch_eff_permittivity - 0.258)"
                " * (patch_width/substrat_thickness + 0.813)) "
            )
            self.application["patch_added_length"] = patch_added_length_formula
            patch_length_formula = "patch_wave_length / 2 - 2 * patch_added_length"
            self.application["patch_length"] = patch_length_formula
        if self.__wave_length > self.__width:
            patch_impedance_formula = "45 * (patch_wave_length/patch_width * sqrt(patch_eff_permittivity)) ** 2"
        else:
            patch_impedance_formula = "60 * patch_wave_length/patch_width * sqrt(patch_eff_permittivity)"
        self.application["patch_impedance"] = patch_impedance_formula

    @property
    def frequency(self):
        return self.__frequency

    @frequency.setter
    def frequency(self, value):
        self.__frequency = value
        self.wave_length_calcul
        self.length_calcul

    @property
    def substrat_thickness(self):
        return self.__substrat_thickness

    @substrat_thickness.setter
    def substrat_thickness(self, value):
        if isinstance(value, float):
            self.__substrat_thickness = abs(value)
            self.effective_permittivity_calcul
            self.added_length_calcul
            self.wave_length_calcul
            self.length_calcul
        else:
            self.application.logger.error("substrat_thickness must be a positive float")

    @property
    def width(self):
        return self.__width

    @width.setter
    def width(self, value):
        self.__width = value
        self.effective_permittivity_calcul
        self.added_length_calcul
        self.wave_length_calcul
        self.length_calcul

    @property
    def position_x(self):
        return self.__position_x

    @position_x.setter
    def position_x(self, value):
        self.__position_x = value

    @property
    def position_y(self):
        return self.__position_y

    @position_y.setter
    def position_y(self, value):
        self.__position_y = value

    @property
    def metric_unit(self):
        return self.__metric_unit

    @metric_unit.setter
    def metric_unit(self, value):
        self.__metric_unit = value

    @property
    def material(self):
        return self.__material

    @material.setter
    def material(self, value):
        # TODO no sens, it is a material, not a material name.
        if self.application.materials.checkifmaterialexists(value):
            self.__material = self.application.materials[value]
            self.permittivity = float(self.__material.permittivity.value)

    @property
    def material_name(self):
        return self.__material_name

    @material_name.setter
    def material_name(self, value):
        if self.application.materials.checkifmaterialexists(value):
            self.__material = self.application.materials[value]
            self.permittivity = float(self.__material.permittivity.value)

    @property
    def permittivity(self):
        return self.__permittivity

    @permittivity.setter
    def permittivity(self, value):
        self.__permittivity = value
        self.effective_permittivity_calcul
        self.added_length_calcul
        self.wave_length_calcul
        self.length_calcul

    @property
    def permittivity_calcul(self):
        self.__permittivity = self.application.materials[self._material].permittivity
        return self.__permittivity

    @property
    def effective_permittivity(self):
        return self.__effective_permittivity

    @effective_permittivity.setter
    def effective_permittivity(self, value):
        self.__effective_permittivity = value
        self.added_length_calcul
        self.wave_length_calcul
        self.length_calcul

    @property
    def effective_permittivity_calcul(self):
        er = self.__permittivity
        h = self.__substrat_thickness
        h_w = h / self.__width
        self.__effective_permittivity = (er + 1) / 2 + (er - 1) / (2 * sqrt(1 + 10 * h_w))
        return self.__effective_permittivity

    @property
    def added_length(self):
        return self.__added_length

    @added_length.setter
    def added_length(self, value):
        self.__added_length = value
        self.wave_length_calcul
        self.length_calcul

    @property
    def added_length_calcul(self):
        er_e = self.__effective_permittivity
        h = self.__substrat_thickness
        h_w = h / self.__width
        w_h = 1 / h_w
        self.__added_length = 0.412 * h * (er_e + 0.3) * (w_h + 0.264) / ((er_e - 0.258) * (w_h + 0.813))
        return self.__added_length

    @property
    def wave_length(self):
        return self.__wave_length

    @wave_length.setter
    def wave_length(self, value):
        if isinstance(value, float):
            self.__wave_length = abs(value)
            self.length_calcul
        else:
            self.application.logger.error("wave_length must be a positive float")

    @property
    def wave_length_calcul(self):
        if isinstance(self.__metric_unit, int):
            converter = 1 * 10 ** (-self.__metric_unit)
        elif self.__metric_unit == "mm":
            converter = 1e3
        elif self.__metric_unit == "cm":
            converter = 1e2
        elif self.__metric_unit == "m":
            converter = 1
        elif self.__metric_unit == "mil":
            converter = 0.00062137119223732773833
        else:
            self.application.logger.error("metric_unit must be a string mm or cm or m or mil or an integer")
        c = 2.99792458e8 * converter
        f = self.__frequency
        er_e = self.__effective_permittivity
        self.__wave_length = c / (f * sqrt(er_e))
        return self.__wave_length

    @property
    def length(self):
        return self.__length

    @length.setter
    def length(self, value):
        if isinstance(value, float):
            self.__length = abs(value)
        else:
            self.application.logger.error("Patch length must be a positive float")

    @property
    def length_calcul(self):
        d_l = self.added_length
        lbd = self.__wave_length
        self.__length = lbd / 2 - 2 * d_l
        return self.__length

    @property
    def impedance(self):
        return self.__impedance

    @impedance.setter
    def impedance(self, value):
        if isinstance(value, float):
            self.__impedance = value
        else:
            self.application.logger.error("Patch impedance must be a positive float")

    @property
    def impedance_calcul(self):
        er_e = self.__effective_permittivity
        lbd = self.__wave_length
        lbd_w = lbd / self.__width
        if lbd > self.__width:
            self.__impedance = 0.5 * 90 * (lbd_w * sqrt(er_e)) ** 2
        else:
            self.__impedance = 0.5 * 120 * lbd_w * sqrt(er_e)
        self.application.logger.warning(
            "The closer the ratio between wave length and the width is to 1,"
            " the less correct the impedance calculation is"
        )
        return self.__impedance

    @property
    def layer_name(self):
        return self.__layer_name

    @layer_name.setter
    def layer_name(self, value):
        if isinstance(value, str):
            self.__layer_name = value
        else:
            self.application.logger.error("Patch layer name must be a string")

    @property
    def layer_number(self):
        return self.__layer_number

    @property
    def application(self):
        return self.__application

    @application.setter
    def application(self, value):
        self.__application = value

    @property
    def aedt_object(self):
        return self.__aedt_object

    @property
    def points_on_layer(self):
        return [
            [self.__position_x, self.__position_y],
            [self.__position_x + self.__length, self.__position_y],
            [self.__position_x + self.__length, self.__position_y + self.__width],
            [self.__position_x, self.__position_y + self.__width],
        ]

    def create_lumped_port(self, reference_layer_number, opposite_side=False, port_name=None):
        string_position_x = str(self.__patch_name) + "_port_position_x"
        string_position_y = str(self.__patch_name) + "_port_position_y"
        string_width = str(self.__patch_name) + "_port_width"
        string_length = str(self.__patch_name) + "_port_length"
        self.__application[string_position_x] = "patch_position_x + patch_length"
        self.__application[string_width] = "patch_width"
        self.__application[string_position_y] = "patch_position_y"
        layer_reference_position = "layer_" + str(reference_layer_number) + "_position"
        patch_layer_position = "(layer_" + str(self.__layer_number) + "_position + " + self.__layer_name + "_thickness)"
        self.__application[string_length] = "abs(" + layer_reference_position + " - " + patch_layer_position + ")"
        port = self.__application.modeler.primitives.create_rectangle(
            csPlane=constants.PLANE.YZ,
            position=[string_position_x, string_position_y, patch_layer_position],
            dimension_list=[string_width, "-" + string_length],
            name=self.__patch_name + "_port",
            matname=None,
        )
        self.__application.create_lumped_port_to_sheet(
            port.name, portname=port_name, reference_object_list=["Ground_G"]
        )

    def line(self, line_impedance, line_length, line_name, line_electrical_length=None, line_width=None):
        patch_line = Line(
            application=self.application,
            frequency=self.frequency,
            substrat_thickness=self.substrat_thickness,
            line_impedance=line_impedance,
            line_width=line_width,
            signal_layer_name=self.layer_name,
            signal_layer_number=self.layer_number,
            line_length=line_length,
            line_electrical_length=line_electrical_length,
            line_thickness=self.__patch_thickness,
            line_material=self.__signal_material,
            line_position_x=0,
            line_position_y=0,
            line_position_z=0,
            line_name=line_name,
            metric_unit="mm",
            below_material=self.material_name,
        )

        self.application["line_position_x"] = "patch_position_x + patch_length"
        self.application["line_position_y"] = "patch_position_y + patch_width/2 - line_width/2"
        return patch_line


class Line:
    def __init__(
        self,
        application,
        frequency,
        substrat_thickness,
        line_impedance,
        line_width,
        signal_layer_name,
        signal_layer_number,
        line_length,
        line_electrical_length=None,
        line_thickness=None,
        line_material="copper",
        line_position_x=0,
        line_position_y=0,
        line_position_z=0,
        line_name="line",
        metric_unit="mm",
        below_material="Duroid (tm)",
    ):
        self.__frequency = frequency
        self.__substrat_thickness = substrat_thickness
        self.__position_x = line_position_x
        self.__position_y = line_position_y
        self.__position_z = line_position_z
        self.__metric_unit = metric_unit
        self.__material_name = below_material
        self.__layer_name = signal_layer_name
        self.__layer_number = signal_layer_number
        self.__application = application
        if application.materials.checkifmaterialexists(below_material):
            self.__material = application.materials[below_material]
            self.__permittivity = float(self.__material.permittivity.value)
        else:
            application.logger.error("Material doesn't exist, you must create it in using: import_materials_from_file")
        if isinstance(line_width, float) or isinstance(line_width, int):
            self.__width = line_width
            self.__effective_permittivity = self.effective_permittivity_calcul
            self.__wave_length = self.wave_length_calcul
            if isinstance(line_electrical_length, float) or isinstance(line_electrical_length, int):
                self.__electrical_length = line_electrical_length
                self.__length = self.length_calcul

            elif isinstance(line_length, float) or isinstance(line_length, int):
                self.__length = line_length
                self.__electrical_length = self.electrical_length_calcul
            else:
                application.logger.error("line_length must be a float.")
            self.__charac_impedance = self.charac_impedance_calcul
        elif line_width is None:
            self.__charac_impedance = line_impedance
            self.__width = self.width_calcul
            self.__effective_permittivity = self.effective_permittivity_calcul
            self.__wave_length = self.wave_length_calcul
            if isinstance(line_electrical_length, float) or isinstance(line_electrical_length, int):
                self.__electrical_length = line_electrical_length
                self.__length = self.length_calcul

            elif isinstance(line_length, float) or isinstance(line_length, int):
                self.__length = line_length
                self.__electrical_length = self.electrical_length_calcul
            else:
                application.logger.error("line_length must be a float.")
        self.make_design_variable(line_width)
        if line_thickness:
            self.__aedt_object = application.modeler.primitives.create_box(
                position=["line_position_x", "line_position_y", "layer_" + str(signal_layer_number) + "_position"],
                dimensions_list=["line_length", "line_width", signal_layer_name + "_thickness"],
                name=line_name,
                matname=line_material,
            )
        else:
            self.__aedt_object = application.modeler.primitives.create_rectangle(
                position=["line_position_x", "line_position_y", "layer_" + str(signal_layer_number) + "_position"],
                dimension_list=["line_length", "line_width"],
                name=line_name,
                matname=line_material,
            )
        application.modeler.subtract(blank_list=[signal_layer_name], tool_list=[line_name], keepOriginals=True)

    def make_design_variable(self, width):
        self.application["line_frequency"] = str(self.__frequency) + "Hz"
        self.application["substrat_thickness"] = str(self.__substrat_thickness) + "mm"
        self.application["line_position_x"] = str(self.__position_x) + "mm"
        self.application["line_position_y"] = str(self.__position_y) + "mm"
        self.application["line_length"] = str(self.__length) + "mm"
        self.application["substrat_permittivity"] = str(self.__permittivity)
        if isinstance(width, float) or isinstance(width, int):
            self.application["line_width"] = str(self.__width) + "mm"
        elif width is None:
            self.application["line_impedance"] = self.__charac_impedance
            z = self.__charac_impedance
            er = self.__permittivity
            a = z * sqrt((er + 1) / 2) / 60 + (0.23 + 0.11 / er) * (er - 1) / (er + 1)
            string_a = (
                "(line_impedance * sqrt((substrat_permittivity + 1)/2) / 60 +"
                " (0.23 + 0.11 / substrat_permittivity) * "
                "(substrat_permittivity - 1) / (substrat_permittivity + 1))"
            )
            w_h = 8 * exp(a) / (exp(2 * a) - 2)
            string_w_h = "(8 * exp(" + string_a + ")/ (exp(2 * " + string_a + ") -2))"
            if w_h < 2:
                line_width_formula = "substrat_thickness * " + string_w_h
                self.application["line_width"] = line_width_formula
            else:
                b = 377 * pi / (2 * z * sqrt(er))
                string_b = "(377 * pi / (2 * line_impedance * sqrt(substrat_permittivity))"
                w_h = 2 * (b - 1 - log(2 * b - 1) * (er - 1) * (log(b - 1) + 0.39 - 0.61 / er) / (2 * er)) / pi
                string_w_h = (
                    "(2 * (" + string_b + " - 1 - log(2 * " + string_b + "- 1) * (substrat_permittivity -1) * "
                    "(log(" + string_b + " - 1) + 0.39 - 0.61 / substrat_permittivity) /"
                    " (2 * substrat_permittivity)) / pi "
                )
                if w_h > 2:
                    line_width_formula = "substrat_thickness * " + string_w_h
                    self.application["line_width"] = line_width_formula
                else:
                    self.__application.logger.error(
                        "No value of the theoretical width can be determined with this substrate"
                        " thickness and this characteristic impedance."
                    )
        line_eff_permittivity_formula = (
            "(substrat_permittivity + 1)/2 + (substrat_permittivity - 1)/"
            "(2 * sqrt(1 + 10 * substrat_thickness/line_width))"
        )
        self.application["line_eff_permittivity"] = line_eff_permittivity_formula
        line_wave_length_formula = "c0 * 1000/(line_frequency * sqrt(line_eff_permittivity))"
        self.application["line_wave_length"] = line_wave_length_formula + "mm"

    @property
    def frequency(self):
        return self.__frequency

    @frequency.setter
    def frequency(self, value):
        if isinstance(value, float):
            self.__frequency = abs(value)
        else:
            self.__application.logger.error("frequency must be a positive float")

    @property
    def substrat_thickness(self):
        return self.__substrat_thickness

    @substrat_thickness.setter
    def substrat_thickness(self, value):
        if isinstance(value, float):
            self.__substrat_thickness = abs(value)
        else:
            self.__application.logger.error("substrat_thickness must be a positive float")

    @property
    def width(self):
        return self.__width

    @width.setter
    def width(self, value):
        if isinstance(value, float):
            self.__width = abs(value)
        else:
            self.__application.logger.error("line_width must be a positive float")

    @property
    def width_calcul(self):
        h = self.__substrat_thickness
        z = self.__charac_impedance
        er = self.__permittivity
        a = z * sqrt((er + 1) / 2) / 60 + (0.23 + 0.11 / er) * (er - 1) / (er + 1)
        w_h = 8 * exp(a) / (exp(2 * a) - 2)
        if w_h < 2:
            self.__width = w_h * h
            return self.__width
        else:
            b = 377 * pi / (2 * z * sqrt(er))
            w_h = 2 * (b - 1 - log(2 * b - 1) * (er - 1) * (log(b - 1) + 0.39 - 0.61 / er) / (2 * er)) / pi
            if w_h > 2:
                self.__width = w_h * h
                return self.__width
            else:
                self.__application.logger.error(
                    "No value of the theoretical width can be determined with this substrate"
                    " thickness and this characteristic impedance."
                )

    @property
    def length(self):
        return self.__length

    @length.setter
    def length(self, value):
        if isinstance(value, float):
            self.__length = abs(value)
        else:
            self.__application.logger.error("line_length must be a positive float")

    @property
    def length_calcul(self):
        lbd = self.__wave_length
        e_length = self.__electrical_length
        self.__length = e_length * lbd / 360
        return self.__length

    @property
    def position_x(self):
        return self.__position_x

    @position_x.setter
    def position_x(self, value):
        if isinstance(value, float):
            self.__position_x = abs(value)
        else:
            self.__application.logger.error("line_position must be a positive float")

    @property
    def metric_unit(self):
        return self.__metric_unit

    @metric_unit.setter
    def metric_unit(self, value):
        if isinstance(value, str):
            self.__metric_unit = value
        else:
            self.__application.logger.error("metric_unit must be a string")

    @property
    def material_name(self):
        return self.__material_name

    @material_name.setter
    def material_name(self, value):
        if isinstance(value, str):
            self.__material_name = value
        else:
            self.__application.logger.error("material_name must be a string")

    @property
    def layer_name(self):
        return self.__layer_name

    @layer_name.setter
    def layer_name(self, value):
        if isinstance(value, str):
            self.__layer_name = value
        else:
            print("signal_layer_name must be a string")

    @property
    def charac_impedance(self):
        return self.__charac_impedance

    @charac_impedance.setter
    def charac_impedance(self, value):
        if isinstance(value, float):
            self.__charac_impedance = abs(value)
        else:
            print("line_impedance must be a string")

    @property
    def charac_impedance_calcul(self):
        w = self.line_width
        h = self.substrat_thickness
        er_e = self.effective_permittivity
        if w / h > 1:
            self.__charac_impedance = 60 * log(8 * h / w + w / (4 * h)) / sqrt(er_e)
        elif w / h < 1:
            self.__charac_impedance = 120 * pi / (sqrt(er_e) * (w / h + 1.393 + 0.667 * log(w / h + 1.444)))
        else:
            self.__charac_impedance = (
                60 * log(8 * h / w + w / (4 * h)) / sqrt(er_e) / 2
                + 120 * pi / (sqrt(er_e) * (w / h + 1.393 + 0.667 * log(w / h + 1.444))) / 2
            )
        return self.__charac_impedance

    @property
    def effective_permittivity(self):
        return self.__effective_permittivity

    @effective_permittivity.setter
    def effective_permittivity(self, value):
        self.__effective_permittivity = value
        self.added_length_calcul
        self.wave_length_calcul
        self.length_calcul

    @property
    def effective_permittivity_calcul(self):
        er = self.__permittivity
        h = self.__substrat_thickness
        h_w = h / self.__width
        self.__effective_permittivity = (er + 1) / 2 + (er - 1) / (2 * sqrt(1 + 10 * h_w))
        return self.__effective_permittivity

    @property
    def wave_length(self):
        return self.__wave_length

    @wave_length.setter
    def wave_length(self, value):
        self.__wave_length = value

    @property
    def wave_length_calcul(self):
        if isinstance(self.__metric_unit, int):
            converter = 1 * 10 ** (-self.__metric_unit)
        elif self.__metric_unit == "mm":
            converter = 1e3
        elif self.__metric_unit == "cm":
            converter = 1e2
        elif self.__metric_unit == "m":
            converter = 1
        elif self.__metric_unit == "mil":
            converter = 0.00062137119223732773833
        else:
            self.__application.logger.error("metric_unit must be a string mm or cm or m or mil or an integer")
        c = 2.99792458e8 * converter
        f = self.__frequency
        er_e = self.__effective_permittivity
        self.__wave_length = c / (f * sqrt(er_e))
        return self.__wave_length

    @property
    def electrical_length(self):
        return self.__electrical_length

    @electrical_length.setter
    def electrical_length(self, value):
        self.__electrical_length = value
        self.__length = self.line_length_calcul

    @property
    def electrical_length_calcul(self):
        lbd = self.__wave_length
        length = self.__length
        self.__electrical_length = 360 * length / lbd
        return self.__electrical_length

    @property
    def application(self):
        return self.__application

    @application.setter
    def application(self, value):
        self.__application = value

    @property
    def aedt_object(self):
        return self.__aedt_object

    @property
    def set_length_to_quarter_wave(self):
        self.__length = self.__wave_length / 4

    @property
    def points_on_layer(self):
        return [
            [self.__position_x, self.__position_y],
            [self.__position_x + self.__length, self.__position_y],
            [self.__position_x + self.__length, self.__position_y + self.__width],
            [self.__position_x, self.__position_y + self.__width],
        ]

    def create_lumped_port(self, reference_layer_name, change_side=False):
        if not change_side:
            self.application.create_lumped_port_between_objects(
                reference_layer_name, self.aedt_object.name, axisdir=self.application.AxisDir.XPos
            )
        else:
            self.application.create_lumped_port_between_objects(
                reference_layer_name, self.aedt_object.name, axisdir=self.application.AxisDir.XNeg
            )
