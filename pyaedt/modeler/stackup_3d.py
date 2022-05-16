from collections import OrderedDict
from math import exp
from math import log
from math import pi
from math import sqrt

from pyaedt import constants

LAYERS = {"s": "signal", "g": "ground", "d": "dielectric"}


class NamedVariable(object):
    def __init__(self, application, name, expression):
        self._application = application
        self._name = name
        self._expression = expression
        application[name] = expression
        self._variable = application.variable_manager.variables[name]

    @property
    def name(self):
        return self._name

    @property
    def expression(self):
        return self._expression

    @expression.setter
    def expression(self, expression):
        if isinstance(expression, str):
            self._expression = expression
            self._application[self.name] = expression
        else:
            self._application.logger.error("Expression must be a string")

    @property
    def unit_system(self):
        """Unit system of the expression as a string."""
        return self._variable.unit_system

    @property
    def units(self):
        """Units."""
        return self._variable.units

    @property
    def value(self):
        """Value."""
        return self._variable.value

    @property
    def numeric_value(self):
        """Numeric part of the expression as a float value."""
        return self._variable.numeric_value

    @property
    def string_value(self):
        return self._variable.string_value


class Layer3D(object):
    def __init__(
        self,
        stackup,
        app,
        name,
        layer_type="S",
        material="copper",
        thickness=0.035,
        fill_material="FR4_epoxy",
        index=1,
    ):
        self._stackup = stackup
        # I think is better to call it just 'position'
        # I delete the position in argument I think it is not needed, if we forced user to the Stackup3D method
        self._index = index
        self._app = app
        self._name = name
        layer_position = "layer_" + name + "_position"
        self._position = NamedVariable(app, layer_position, "0mm")
        self._thickness = None
        layer_type = LAYERS.get(layer_type.lower())
        if not layer_type:
            raise ValueError("Layer Type has to be one of the S, D, G strins.")
        self._obj_3d = []
        obj_3d = None
        self._material_name = self.duplicate_parametrize_material(material).name
        if layer_type != "dielectric" and thickness > 0:
            self._fill_material = self.duplicate_parametrize_material(fill_material).name
        self._thickness_variable = self._name + "_thickness"
        if thickness:
            self._thickness = NamedVariable(self._app, self._thickness_variable, str(thickness) + "mm")
        if layer_type == "dielectric":
            cloned_material = self.duplicate_parametrize_material(material)
            if cloned_material:

                obj_3d = self._app.modeler.primitives.create_box(
                    ["dielectric_x_position", "dielectric_y_position", layer_position],
                    ["dielectric_length", "dielectric_width", self._thickness_variable],
                    name=self._name,
                    matname=cloned_material.name,
                )
        elif layer_type == "ground":
            if thickness:
                obj_3d = self._app.modeler.primitives.create_box(
                    ["dielectric_x_position", "dielectric_y_position", layer_position],
                    ["dielectric_length", "dielectric_width", self._thickness_variable],
                    name=self._name,
                    matname=self._material_name,
                )

            else:
                obj_3d = self._app.modeler.primitives.create_rectangle(
                    "Z",
                    ["dielectric_x_position", "dielectric_y_position", layer_position],
                    ["dielectric_length", "dielectric_width"],
                    name=self._name,
                    matname=self._material_name,
                )
        elif layer_type == "signal":
            if thickness:
                obj_3d = self._app.modeler.primitives.create_box(
                    ["dielectric_x_position", "dielectric_y_position", layer_position],
                    ["dielectric_length", "dielectric_width", self._thickness_variable],
                    name=self._name,
                    matname=self._fill_material,
                )
            else:
                obj_3d = self._app.modeler.primitives.create_rectangle(
                    "Z",
                    ["dielectric_x_position", "dielectric_y_position", layer_position],
                    ["dielectric_length", "dielectric_width"],
                    name=self._name,
                    matname=self._fill_material,
                )

        if obj_3d:
            self._obj_3d.append(obj_3d)
        else:
            self._app.logger.error("Generation of the ground layer does not work.")

    @property
    def material_name(self):
        return self._material_name

    @property
    def filling_material_name(self):
        return self._fill_material

    @property
    def thickness(self):
        return self._thickness

    @property
    def thickness_value(self):
        return self._thickness.value

    @thickness.setter
    def thickness(self, value):
        self._thickness.expression = value

    @property
    def position(self):
        return self._position

    @property
    def elevation_value(self):
        return self._app.variable_manager[self._position.name].value

    @property
    def elevation(self):
        try:
            return self._app.variable_manager[self._position.name].expression
        except:
            return self._app.variable_manager[self._position.name].string_value

    def duplicate_parametrize_material(self, material_name, cloned_material_name=None, list_of_properties=None):
        application = self._app
        if self._app.materials.checkifmaterialexists(material_name):
            if not cloned_material_name:
                cloned_material_name = "cloned_" + material_name
            if not self._app.materials.checkifmaterialexists(cloned_material_name):
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

    def patch(
        self,
        frequency,
        patch_width,
        patch_length=None,
        patch_position_x=0,
        patch_position_y=0,
        patch_name="patch",
        metric_unit="mm",
    ):
        substrate_thickness = 0
        for k, v in self._stackup._stackup.items():
            if v._index == self._index - 1:
                substrate_thickness = v.thickness_value
                break
        created_patch = Patch(
            self._app,
            frequency,
            substrate_thickness,
            patch_width,
            self._name,
            patch_length=patch_length,
            patch_thickness=self.thickness,
            patch_material=self.material_name,
            patch_position_x=patch_position_x,
            patch_position_y=patch_position_y,
            patch_position_z=self.elevation,
            patch_name=patch_name,
            metric_unit=metric_unit,
            below_material=self.filling_material_name,
        )
        self._obj_3d.append(created_patch)
        return created_patch

    def line(
        self,
        frequency,
        line_length,
        line_impedance,
        line_width=None,
        line_electrical_length=None,
        line_position_x=0,
        line_position_y=0,
        line_name="line",
        metric_unit="mm",
    ):
        substrate_thickness = 0
        for k, v in self._stackup._stackup.items():
            if v._index == self._index - 1:
                substrate_thickness = v.thickness_value
                break

        created_line = Line(
            self._app,
            frequency,
            substrate_thickness,
            line_impedance,
            line_width,
            self._name,
            line_length=line_length,
            line_electrical_length=line_electrical_length,
            line_thickness=self.thickness,
            line_material=self.material_name,
            line_position_x=line_position_x,
            line_position_y=line_position_y,
            line_position_z=self.elevation,
            line_name=line_name,
            metric_unit=metric_unit,
            below_material=self.filling_material_name,
        )
        self._obj_3d.append(created_line)
        return created_line


class Stackup3D(object):
    def __init__(self, application):
        self._app = application
        self._layer_name = []
        self._layer_position = []
        self._layer_values = []
        self._dielectric_list = []
        self._dielectric_name_list = []
        self._ground_list = []
        self._ground_name_list = []
        self._ground_fill_material = []
        self._signal_list = []
        self._signal_name_list = []
        self._signal_material = []
        self._object_list = []
        self._end_of_stackup3D = NamedVariable(self._app, "StackUp_End", "0mm")
        self._z_position_offset = 0
        self._first_layer_position = "layer_1_position"
        self._shifted_index = 0
        self._stackup = OrderedDict({})
        self._start_position = NamedVariable(self._app, self._first_layer_position, "0mm")
        self._dielectric_x_position = NamedVariable(self._app, "dielectric_x_position", "0mm")
        self._dielectric_y_position = NamedVariable(self._app, "dielectric_y_position", "0mm")
        self._dielectric_width = NamedVariable(self._app, "dielectric_width", "1000mm")
        self._dielectric_length = NamedVariable(self._app, "dielectric_length", "1000mm")

    @property
    def start_position(self):
        return self._start_position

    @start_position.setter
    def start_position(self, expression):
        self._start_position.expression = expression

    @property
    def dielectric_x_position(self):
        return self._dielectric_x_position

    @dielectric_x_position.setter
    def dielectric_x_position(self, expression):
        self._dielectric_x_position.expression = expression

    @property
    def dielectric_y_position(self):
        return self._dielectric_x_position

    @dielectric_y_position.setter
    def dielectric_y_position(self, expression):
        self._dielectric_y_position.expression = expression

    @property
    def dielectric_width(self):
        return self._dielectric_width

    @dielectric_width.setter
    def dielectric_width(self, expression):
        self._dielectric_width.expression = expression

    @property
    def dielectric_length(self):
        return self._dielectric_length

    @dielectric_length.setter
    def dielectric_length(self, expression):
        self._dielectric_length.expression = expression

    @property
    def layer_names(self):
        return self._layer_name

    @property
    def layer_positions(self):
        return self._layer_position

    @property
    def layer_values(self):
        return self._layer_values

    @property
    def stackup_layers(self):
        return self._stackup

    @property
    def z_position_offset(self):
        return self._z_position_offset

    def add_layer(self, name, layer_type="S", material="copper", thickness=0.035, fill_material="FR4_epoxy"):
        self._shifted_index += 1
        if not layer_type:
            raise ValueError("Layer Type has to be one of the S, D, G strins.")
        self._layer_name.append(name)

        lay = Layer3D(
            stackup=self,
            app=self._app,
            name=name,
            layer_type=layer_type,
            material=material,
            thickness=thickness,
            fill_material=fill_material,
            index=self._shifted_index,
        )
        self._layer_position_manager(lay)
        if layer_type == "D":
            self._dielectric_list.extend(lay._obj_3d)
            self._dielectric_name_list.append(lay._name)
        elif layer_type == "G":
            self._ground_list.extend(lay._obj_3d)
            self._ground_name_list.append(lay._name)
            self._ground_fill_material.append(lay._fill_material)
        elif layer_type == "S":
            self._signal_list.extend(lay._obj_3d)
            self._signal_name_list.append(lay._name)
            self._signal_material.append(lay._material_name)
        # With the function _layer_position_manager i think this part is not needed anymore or has to be reworked

        self._stackup[lay._name] = lay
        return lay

    def add_signal_layer(self, name, material="copper", thickness=0.035, fill_material="FR4_epoxy"):
        return self.add_layer(
            name=name, layer_type="S", material=material, thickness=thickness, fill_material=fill_material
        )

    def add_dielectric_layer(
        self,
        name,
        material="FR4_epoxy",
        thickness=0.035,
    ):
        return self.add_layer(name=name, layer_type="D", material=material, thickness=thickness, fill_material=None)

    def add_ground_layer(self, name, material="copper", thickness=0.035, fill_material="air"):
        return self.add_layer(
            name=name, layer_type="G", material=material, thickness=thickness, fill_material=fill_material
        )

    def _layer_position_manager(self, layer):
        previous_layer_end = self._end_of_stackup3D.expression

        layer.position.expression = previous_layer_end
        if layer.thickness:
            self._end_of_stackup3D.expression = layer.position.name + " + " + layer.thickness.name
        else:
            self._end_of_stackup3D.expression = layer.position.name

    # if we call this function instantiation of the Layer, the first call, previous_layer_end is "0mm", and
    # layer.position.expression is also "0mm" and self._end_of_stackup becomes the first layer.position + thickness
    # if it has thickness, and so the second call, previous_layer_end is the previous layer position + thickness
    # so the current layer position is the previous_layer_end and the end_of_stackup is the current layer position +
    # thickness, and we just need to call this function after the construction of a layer3D.

    def resize(self, percentage_offset):
        # TODO A really correct resize function can be create because 'hfss variable' allows to use max(myvar, myvar2)
        list_of_2d_points = []
        list_of_x_coordinates = []
        list_of_y_coordinates = []
        for object in self._object_list:
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
        self._app["dielectric_x_position"] = str(minimum_x - variation_x / 2 * percentage_offset / 100) + "mm"
        self._app["dielectric_y_position"] = str(minimum_y - variation_y / 2 * percentage_offset / 100) + "mm"
        self._app["dielectric_length"] = str(maximum_x + variation_x * percentage_offset / 100) + "mm"
        self._app["dielectric_width"] = str(maximum_y + variation_y * percentage_offset / 100) + "mm"

    def resize_around_patch(self):
        self._app["dielectric_x_position"] = "patch_position_x - patch_length * 50 / 100"
        self._app["dielectric_y_position"] = "patch_position_y - patch_width * 50 / 100"
        self._app["dielectric_length"] = (
            "abs(patch_position_x + patch_length * (1 + 50 / 100)) +" " abs(dielectric_x_position)"
        )
        self._app["dielectric_width"] = (
            "abs(patch_position_y + patch_width * (1 + 50 / 100)) +" " abs(dielectric_y_position)"
        )

    def create_region(self, pad_percent=None):
        if pad_percent is None:
            pad_percent = [50, 50, 5000, 50, 50, 100]
        return self._app.modeler.primitives.create_region(pad_percent)


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
        self._signal_material = patch_material
        self._layer_name = signal_layer_name
        self.__patch_name = patch_name
        self.__patch_thickness = patch_thickness
        self._app = application
        self.__aedt_object = None
        if application.materials.checkifmaterialexists(below_material):
            self.__material = application.materials[below_material]
            try:
                self.__permittivity = float(self.__material.permittivity.value)
            except:
                self.__permittivity = application.variable_manager[self.__material.permittivity.value].value
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
                position=["patch_position_x", "patch_position_y", "layer_" + str(signal_layer_name) + "_position"],
                dimensions_list=["patch_length", "patch_width", signal_layer_name + "_thickness"],
                name=patch_name,
                matname=patch_material,
            )
        else:
            self.__aedt_object = application.modeler.primitives.create_rectangle(
                position=["patch_position_x", "patch_position_y", "layer_" + str(signal_layer_name) + "_position"],
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
        return self._layer_name

    @layer_name.setter
    def layer_name(self, value):
        if isinstance(value, str):
            self._layer_name = value
        else:
            self.application.logger.error("Patch layer name must be a string")

    @property
    def layer_number(self):
        return self.__layer_number

    @property
    def application(self):
        return self._app

    @application.setter
    def application(self, value):
        self._app = value

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
        self._app[string_position_x] = "patch_position_x + patch_length"
        self._app[string_width] = "patch_width"
        self._app[string_position_y] = "patch_position_y"
        layer_reference_position = "layer_" + str(reference_layer_number) + "_position"
        patch_layer_position = "(layer_" + str(self.__layer_number) + "_position + " + self._layer_name + "_thickness)"
        self._app[string_length] = "abs(" + layer_reference_position + " - " + patch_layer_position + ")"
        port = self._app.modeler.primitives.create_rectangle(
            csPlane=constants.PLANE.YZ,
            position=[string_position_x, string_position_y, patch_layer_position],
            dimension_list=[string_width, "-" + string_length],
            name=self.__patch_name + "_port",
            matname=None,
        )
        self._app.create_lumped_port_to_sheet(port.name, portname=port_name, reference_object_list=["Ground_G"])

    def line(self, line_impedance, line_length, line_name, line_electrical_length=None, line_width=None):
        patch_line = Line(
            application=self.application,
            frequency=self.frequency,
            substrat_thickness=self.substrat_thickness,
            line_impedance=line_impedance,
            line_width=line_width,
            signal_layer_name=self.layer_name,
            line_length=line_length,
            line_electrical_length=line_electrical_length,
            line_thickness=self.__patch_thickness,
            line_material=self._signal_material,
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
        self._layer_name = signal_layer_name
        self._app = application
        if application.materials.checkifmaterialexists(below_material):
            self.__material = application.materials[below_material]
            try:
                self.__permittivity = float(self.__material.permittivity.value)
            except:
                self.__permittivity = application.variable_manager[self.__material.permittivity.value].value
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
                position=["line_position_x", "line_position_y", "layer_" + str(signal_layer_name) + "_position"],
                dimensions_list=["line_length", "line_width", signal_layer_name + "_thickness"],
                name=line_name,
                matname=line_material,
            )
        else:
            self.__aedt_object = application.modeler.primitives.create_rectangle(
                position=["line_position_x", "line_position_y", "layer_" + str(signal_layer_name) + "_position"],
                dimension_list=["line_length", "line_width"],
                name=line_name,
                matname=line_material,
            )
        application.modeler.subtract(blank_list=[signal_layer_name], tool_list=[line_name], keepOriginals=True)

    def make_design_variable(self, width):
        self.application["line_frequency"] = self.application.modeler._arg_with_dim(self.__frequency, "Hz")
        self.application["substrat_thickness"] = self.application.modeler._arg_with_dim(self.__substrat_thickness, "mm")
        self.application["line_position_x"] = self.application.modeler._arg_with_dim(self.__position_x, "mm")
        self.application["line_position_y"] = self.application.modeler._arg_with_dim(self.__position_y, "mm")
        self.application["line_length"] = self.application.modeler._arg_with_dim(self.__length, "mm")
        self.application["substrat_permittivity"] = str(self.__permittivity)
        if isinstance(width, float) or isinstance(width, int):
            self.application["line_width"] = self.application.modeler._arg_with_dim(self.__width, "mm")
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
                    self._app.logger.error(
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
            self._app.logger.error("frequency must be a positive float")

    @property
    def substrat_thickness(self):
        return self.__substrat_thickness

    @substrat_thickness.setter
    def substrat_thickness(self, value):
        if isinstance(value, float):
            self.__substrat_thickness = abs(value)
        else:
            self._app.logger.error("substrat_thickness must be a positive float")

    @property
    def width(self):
        return self.__width

    @width.setter
    def width(self, value):
        if isinstance(value, float):
            self.__width = abs(value)
        else:
            self._app.logger.error("line_width must be a positive float")

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
                self._app.logger.error(
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
            self._app.logger.error("line_length must be a positive float")

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
            self._app.logger.error("line_position must be a positive float")

    @property
    def metric_unit(self):
        return self.__metric_unit

    @metric_unit.setter
    def metric_unit(self, value):
        if isinstance(value, str):
            self.__metric_unit = value
        else:
            self._app.logger.error("metric_unit must be a string")

    @property
    def material_name(self):
        return self.__material_name

    @material_name.setter
    def material_name(self, value):
        if isinstance(value, str):
            self.__material_name = value
        else:
            self._app.logger.error("material_name must be a string")

    @property
    def layer_name(self):
        return self._layer_name

    @layer_name.setter
    def layer_name(self, value):
        if isinstance(value, str):
            self._layer_name = value
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
        w = self.__width
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
            self._app.logger.error("metric_unit must be a string mm or cm or m or mil or an integer")
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
        return self._app

    @application.setter
    def application(self, value):
        self._app = value

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
