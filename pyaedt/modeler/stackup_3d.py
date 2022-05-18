from collections import OrderedDict

from pyaedt.generic.general_methods import generate_unique_name
from pyaedt.generic.general_methods import pyaedt_function_handler
from pyaedt.modules.MaterialLib import Material

LAYERS = {"s": "signal", "g": "ground", "d": "dielectric"}


class NamedVariable(object):
    """Cast Pyaedt Variable object to simplify getter and setters in Stackup3D."""

    def __init__(self, application, name, expression):
        self._application = application
        self._name = name
        self._expression = expression
        application[name] = expression

    @property
    def _variable(self):
        return self._application.variable_manager.variables[self._name]

    @property
    def name(self):
        """

        Returns
        -------

        """
        return self._name

    @property
    def expression(self):
        """

        Returns
        -------

        """
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
        """

        Returns
        -------

        """
        return self._variable.string_value

    @pyaedt_function_handler()
    def hide_variable(self, value=True):
        """

        Parameters
        ----------
        value

        Returns
        -------

        """
        self._application.hidden_variable(self.name, value)

    @pyaedt_function_handler()
    def read_only_variable(self, value=True):
        """

        Parameters
        ----------
        value

        Returns
        -------

        """
        self._application.read_only_variable(self.name, value)


class Layer3D(object):
    """ """

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
        self._layer_type = LAYERS.get(layer_type.lower())

        self._obj_3d = []
        obj_3d = None
        self._material = self.duplicate_parametrize_material(material)
        self._material_name = self._material.name
        if self._layer_type != "dielectric":
            self._fill_material = self.duplicate_parametrize_material(fill_material)
            self._fill_material_name = self._fill_material.name
        self._thickness_variable = self._name + "_thickness"
        if thickness:
            self._thickness = NamedVariable(self._app, self._thickness_variable, str(thickness) + "mm")
        if self._layer_type == "dielectric":
            obj_3d = self._app.modeler.primitives.create_box(
                ["dielectric_x_position", "dielectric_y_position", layer_position],
                ["dielectric_length", "dielectric_width", self._thickness_variable],
                name=self._name,
                matname=self._material_name,
            )
        elif self._layer_type == "ground":
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
        elif self._layer_type == "signal":
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
        obj_3d.group_name = "Layer_{}".format(self._name)
        if obj_3d:
            self._obj_3d.append(obj_3d)
        else:
            self._app.logger.error("Generation of the ground layer does not work.")

    @property
    def name(self):
        """

        Returns
        -------

        """
        return self._name

    @property
    def number(self):
        """

        Returns
        -------

        """
        return self._index

    @property
    def material_name(self):
        """

        Returns
        -------

        """
        return self._material_name

    @property
    def material(self):
        """

        Returns
        -------

        """
        return self._material

    @property
    def filling_material(self):
        """

        Returns
        -------

        """
        return self._fill_material

    @property
    def filling_material_name(self):
        """

        Returns
        -------

        """
        return self._fill_material_name

    @property
    def thickness(self):
        """

        Returns
        -------

        """
        return self._thickness

    @property
    def thickness_value(self):
        """

        Returns
        -------

        """
        return self._thickness.value

    @thickness.setter
    def thickness(self, value):
        self._thickness.expression = value

    @property
    def position(self):
        """

        Returns
        -------

        """
        return self._position

    @property
    def elevation_value(self):
        """

        Returns
        -------

        """
        return self._app.variable_manager[self._position.name].value

    @property
    def elevation(self):
        """

        Returns
        -------

        """
        try:
            return self._app.variable_manager[self._position.name].expression
        except:
            return self._app.variable_manager[self._position.name].string_value

    @pyaedt_function_handler()
    def duplicate_parametrize_material(self, material_name, cloned_material_name=None, list_of_properties=None):
        """

        Parameters
        ----------
        material_name
        cloned_material_name
        list_of_properties

        Returns
        -------

        """
        application = self._app
        if isinstance(material_name, Material):
            return material_name
        if isinstance(cloned_material_name, Material):
            return cloned_material_name
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
                # application.logger.warning(
                #     "The material %s has been already cloned,"
                #     " if you want to clone it again pass in argument"
                #     " the named of the clone" % material_name
                # )
                return application.materials[cloned_material_name]
        else:
            application.logger.error("The material name %s doesn't exist" % material_name)
            return None

    @pyaedt_function_handler()
    def patch(
        self,
        frequency,
        patch_width,
        patch_length=None,
        patch_position_x=0,
        patch_position_y=0,
        patch_name=None,
        metric_unit="mm",
        axis="X",
    ):
        """

        Parameters
        ----------
        frequency
        patch_width
        patch_length
        patch_position_x
        patch_position_y
        patch_name
        metric_unit
        axis

        Returns
        -------

        """
        if not patch_name:
            patch_name = generate_unique_name("{}_patch".format(self._name), n=3)
        lst = self._stackup._layer_name
        for i in range(len(lst)):
            if lst[i] == self._name:
                if self._stackup.stackup_layers[lst[i - 1]]._layer_type == "dielectric":
                    below_layer = self._stackup.stackup_layers[lst[i - 1]]
                    break
                else:
                    self._app.logger.error("The layer below the selected one must be of dielectric type")
                    return False
        created_patch = Patch(
            self._app,
            frequency,
            patch_width,
            signal_layer=self,
            dielectric_layer=below_layer,
            patch_length=patch_length,
            patch_position_x=patch_position_x,
            patch_position_y=patch_position_y,
            patch_name=patch_name,
            metric_unit=metric_unit,
            axis=axis,
        )
        self._obj_3d.append(created_patch.aedt_object)
        self._stackup._object_list.append(created_patch)
        created_patch.aedt_object.group_name = "Layer_{}".format(self._name)
        return created_patch

    @pyaedt_function_handler()
    def line(
        self,
        line_width=None,
        line_length=None,
        is_electrical_length=False,
        line_position_x=0,
        line_position_y=0,
        line_name=None,
        metric_unit="mm",
        axis="X",
        reference_system=None,
        frequency="1GHz",
    ):
        """

        Parameters
        ----------
        line_width
        line_length
        is_electrical_length
        line_position_x
        line_position_y
        line_name
        metric_unit
        axis
        reference_system
        frequency

        Returns
        -------
        :class:`pyaedt.modeler.stackup_3d.Line`
        """
        if not line_name:
            line_name = generate_unique_name("{0}_line".format(self._name), n=3)
        dielectric_layer = None
        for k, v in self._stackup._stackup.items():
            if v._index == self._index - 1:
                dielectric_layer = v
                break
        if dielectric_layer is None:
            self._app.logger.error("There is no layer under this layer")

        created_line = Line(
            self._app,
            frequency,
            None,
            line_width,
            self,
            dielectric_layer,
            line_length=line_length if not is_electrical_length else None,
            line_electrical_length=line_length if is_electrical_length else None,
            line_position_x=line_position_x,
            line_position_y=line_position_y,
            line_name=line_name,
            metric_unit=metric_unit,
            reference_system=reference_system,
            axis=axis,
        )
        created_line.aedt_object.group_name = "Layer_{}".format(self._name)
        self._obj_3d.append(created_line.aedt_object)
        self._stackup._object_list.append(created_line)
        return created_line

    @pyaedt_function_handler()
    def polygon(self, points, material="copper", is_void=False, units="mm", poly_name=None):
        """

        Parameters
        ----------
        points
        material
        is_void
        units
        poly_name

        Returns
        -------

        """
        if not poly_name:
            poly_name = generate_unique_name("{0}_poly".format(self._name), n=3)
        polygon = Polygon(
            self._app,
            points,
            thickness=self._thickness,
            metric_unit=units,
            signal_layer_name=self._name,
            mat_name=material,
            is_void=is_void,
            poly_name=poly_name,
        )
        polygon.aedt_object.group_name = "Layer_{}".format(self._name)

        if self._layer_type == "ground":
            if not is_void:
                self._app.modeler[self._name].subtract(polygon.aedt_object, False)
                return True
        elif is_void:
            self._app.modeler.subtract(self._obj_3d, polygon.aedt_object, True)
            polygon.aedt_object.material_name = self.filling_material_name
            return True
        else:
            self._app.modeler.subtract(self._obj_3d[0], polygon.aedt_object, True)
            self._obj_3d.append(polygon.aedt_object)
            self._stackup._object_list.append(polygon)
            return polygon


class PadstackLayer(object):
    """ """

    def __init__(self, padstack, layer_name, elevation):
        self._padstack = padstack
        self._layer_name = layer_name
        self._layer_elevation = elevation
        self._pad_radius = 1
        self._antipad_radius = 2
        self._units = "mm"


class Padstack(object):
    """ """

    def __init__(self, app, stackup, name, material="copper"):
        self._app = app
        self._stackup = stackup
        self.name = name
        self._padstacks_by_layer = OrderedDict({})
        self._vias_objects = []
        self._num_sides = 16
        self._plating_ratio = 1
        v = None
        k = None
        for k, v in self._stackup.stackup_layers.items():
            if not self._padstacks_by_layer and v._layer_type == "dielectric":
                continue
            self._padstacks_by_layer[k] = PadstackLayer(self, k, v.position)
        if v and v._layer_type == "dielectric":
            del self._padstacks_by_layer[k]
        self._padstacks_material = material

    @property
    def plating_ratio(self):
        """

        Returns
        -------

        """
        return self._plating_ratio

    @plating_ratio.setter
    def plating_ratio(self, val):
        if isinstance(val, (float, int)) and val > 0 and val <= 1:
            self._plating_ratio = val
        elif isinstance(val, str):
            self._plating_ratio = val
        else:
            self._app.logger.error("Plating has to be between 0 and 1")

    @property
    def num_sides(self):
        """

        Returns
        -------

        """
        return self._num_sides

    @num_sides.setter
    def num_sides(self, val):
        self._num_sides = val

    @pyaedt_function_handler()
    def set_all_pad_value(self, value):
        """

        Parameters
        ----------
        value

        Returns
        -------

        """
        for v in list(self._padstacks_by_layer.values()):
            self._pad_radius = value

    @pyaedt_function_handler()
    def set_all_antipad_value(self, value):
        """

        Parameters
        ----------
        value

        Returns
        -------

        """
        for v in list(self._padstacks_by_layer.values()):
            self._antipad_radius = value

    @pyaedt_function_handler()
    def set_start_layer(self, layer):
        """

        Parameters
        ----------
        layer

        Returns
        -------

        """
        found = False
        new_stackup = OrderedDict({})
        for k, v in self._stackup.stackup_layers.items():
            if k == layer:
                found = True
            if found and layer not in self._padstacks_by_layer:
                new_stackup[k] = PadstackLayer(self, k, v.position)
            elif found:
                new_stackup[k] = self._padstacks_by_layer[k]
        self._padstacks_by_layer = new_stackup

    @pyaedt_function_handler()
    def set_stop_layer(self, layer):
        """

        Parameters
        ----------
        layer

        Returns
        -------

        """
        found = False
        new_stackup = OrderedDict({})
        for k, v in self._stackup.stackup_layers.items():
            if k == layer:
                found = True
            if not found and k in list(self._padstacks_by_layer.keys()):
                new_stackup[k] = self._padstacks_by_layer[k]
        self._padstacks_by_layer = new_stackup

    @pyaedt_function_handler()
    def insert(self, position_x=0, position_y=0, instance_name=None, reference_system=None):
        """

        Parameters
        ----------
        position_x
        position_y
        instance_name
        reference_system

        Returns
        -------

        """
        if not instance_name:
            instance_name = generate_unique_name("{}_".format(self.name), n=3)
            if reference_system:
                self._app.modeler.set_working_coordinate_system(reference_system)
                self._reference_system = reference_system
            else:
                self._app.modeler.create_coordinate_system(
                    origin=[0, 0, 0], reference_cs="Global", name=instance_name + "_CS"
                )
                self._app.modeler.set_working_coordinate_system(instance_name + "_CS")
                self._reference_system = instance_name + "_CS"

            first_el = None
            cyls = []
            for k, v in self._padstacks_by_layer.items():
                if not first_el:
                    first_el = v._layer_elevation
                else:
                    position_x = self._app.modeler._arg_with_dim(position_x)
                    position_y = self._app.modeler._arg_with_dim(position_y)
                    cyls.append(
                        self._app.modeler.create_cylinder(
                            "Z",
                            [position_x, position_y, first_el.name],
                            v._pad_radius,
                            v._layer_elevation.name,
                            matname=self._padstacks_material,
                            name=instance_name,
                            numSides=self._num_sides,
                        )
                    )
                    if self.plating_ratio < 1:
                        hole = self._app.modeler.create_cylinder(
                            "Z",
                            [position_x, position_y, first_el.name],
                            "{}*{}".format(self._app.modeler._arg_with_dim(v._pad_radius), 1 - self.plating_ratio),
                            v._layer_elevation.name,
                            matname=self._padstacks_material,
                            name=instance_name,
                            numSides=self._num_sides,
                        )
                        cyls[-1].subtract(hole, False)
                    anti = self._app.modeler.create_cylinder(
                        "Z",
                        [position_x, position_y, first_el.name],
                        v._antipad_radius,
                        v._layer_elevation.name,
                        matname="air",
                        name=instance_name + "_antipad",
                    )
                    self._app.modeler.subtract(
                        self._stackup._signal_list + self._stackup._ground_list + self._stackup._dielectric_list,
                        anti,
                        False,
                    )
                    first_el = v._layer_elevation
            if len(cyls) > 1:
                self._app.modeler.unite(cyls)
            self._vias_objects.append(cyls[0])
            cyls[0].group_name = "Vias"
            self._stackup._vias.append(self)
            return cyls[0]


class Stackup3D(object):
    """ """

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
        self._vias = []
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
        self._padstacks = []

    @property
    def padstacks(self):
        """

        Returns
        -------

        """
        return self._padstacks

    @property
    def dielectrics(self):
        """

        Returns
        -------

        """
        return self._dielectric_list

    @property
    def grounds(self):
        """

        Returns
        -------

        """
        return self._ground_list

    @property
    def signals(self):
        """

        Returns
        -------

        """
        return self._signal_list

    @property
    def objects(self):
        """

        Returns
        -------

        """
        return self._object_list

    @property
    def objects_by_layer(self):
        """

        Returns
        -------

        """
        objs = {}
        for obj in self.objects:
            if objs.get(obj.layer_name, None):
                objs[obj.layer_name].append(obj)
            else:
                objs[obj.layer_name] = [obj]
        return objs

    @property
    def start_position(self):
        """

        Returns
        -------

        """
        return self._start_position

    @start_position.setter
    def start_position(self, expression):
        self._start_position.expression = expression

    @property
    def dielectric_x_position(self):
        """

        Returns
        -------

        """
        return self._dielectric_x_position

    @dielectric_x_position.setter
    def dielectric_x_position(self, expression):
        self._dielectric_x_position.expression = expression

    @property
    def dielectric_y_position(self):
        """

        Returns
        -------

        """
        return self._dielectric_x_position

    @dielectric_y_position.setter
    def dielectric_y_position(self, expression):
        self._dielectric_y_position.expression = expression

    @property
    def dielectric_width(self):
        """

        Returns
        -------

        """
        return self._dielectric_width

    @dielectric_width.setter
    def dielectric_width(self, expression):
        self._dielectric_width.expression = expression

    @property
    def dielectric_length(self):
        """

        Returns
        -------

        """
        return self._dielectric_length

    @dielectric_length.setter
    def dielectric_length(self, expression):
        self._dielectric_length.expression = expression

    @property
    def layer_names(self):
        """

        Returns
        -------

        """
        return self._layer_name

    @property
    def layer_positions(self):
        """

        Returns
        -------

        """
        return self._layer_position

    @property
    def layer_values(self):
        """

        Returns
        -------

        """
        return self._layer_values

    @property
    def stackup_layers(self):
        """

        Returns
        -------

        """
        return self._stackup

    @property
    def z_position_offset(self):
        """

        Returns
        -------

        """
        return self._z_position_offset

    @pyaedt_function_handler()
    def add_padstack(self, name, material="copper"):
        """

        Parameters
        ----------
        name
        material

        Returns
        -------

        """
        p = Padstack(self._app, self, name, material)
        self._padstacks.append(p)
        return p

    @pyaedt_function_handler()
    def add_layer(self, name, layer_type="S", material="copper", thickness=0.035, fill_material="FR4_epoxy"):
        """

        Parameters
        ----------
        name
        layer_type
        material
        thickness
        fill_material

        Returns
        -------

        """
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
            lay._obj_3d[-1].transparency = "0.8"
        elif layer_type == "G":
            self._ground_list.extend(lay._obj_3d)
            self._ground_name_list.append(lay._name)
            self._ground_fill_material.append(lay._fill_material)
            lay._obj_3d[-1].transparency = "0.6"
            lay._obj_3d[-1].color = (255, 0, 0)

        elif layer_type == "S":
            self._signal_list.extend(lay._obj_3d)
            self._signal_name_list.append(lay._name)
            self._signal_material.append(lay._material_name)
            # With the function _layer_position_manager i think this part is not needed anymore or has to be reworked
            lay._obj_3d[-1].transparency = "0.8"
        self._stackup[lay._name] = lay
        return lay

    @pyaedt_function_handler()
    def add_signal_layer(self, name, material="copper", thickness=0.035, fill_material="FR4_epoxy"):
        """

        Parameters
        ----------
        name
        material
        thickness
        fill_material

        Returns
        -------

        """
        return self.add_layer(
            name=name, layer_type="S", material=material, thickness=thickness, fill_material=fill_material
        )

    @pyaedt_function_handler()
    def add_dielectric_layer(
        self,
        name,
        material="FR4_epoxy",
        thickness=0.035,
    ):
        """

        Parameters
        ----------
        name
        material
        thickness

        Returns
        -------

        """
        return self.add_layer(name=name, layer_type="D", material=material, thickness=thickness, fill_material=None)

    @pyaedt_function_handler()
    def add_ground_layer(self, name, material="copper", thickness=0.035, fill_material="air"):
        """

        Parameters
        ----------
        name
        material
        thickness
        fill_material

        Returns
        -------

        """
        return self.add_layer(
            name=name, layer_type="G", material=material, thickness=thickness, fill_material=fill_material
        )

    @pyaedt_function_handler()
    def _layer_position_manager(self, layer):
        """

        Parameters
        ----------
        layer

        Returns
        -------

        """
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

    @pyaedt_function_handler()
    def resize(self, percentage_offset):
        """

        Parameters
        ----------
        percentage_offset

        Returns
        -------

        """
        list_of_2d_points = []
        list_of_x_coordinates = []
        list_of_y_coordinates = []
        for object in self._object_list:
            points_list_by_object = object.points_on_layer
            list_of_2d_points = points_list_by_object + list_of_2d_points
        for via in self._vias:
            for v in via._vias_objects:
                list_of_x_coordinates.append(v.bounding_box[0])
                list_of_x_coordinates.append(v.bounding_box[2])
                list_of_y_coordinates.append(v.bounding_box[1])
                list_of_y_coordinates.append(v.bounding_box[3])
                list_of_x_coordinates.append(v.bounding_box[0])
                list_of_x_coordinates.append(v.bounding_box[2])
                list_of_y_coordinates.append(v.bounding_box[3])
                list_of_y_coordinates.append(v.bounding_box[1])
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
        return True

    @pyaedt_function_handler()
    def resize_around_patch(self):
        """

        Returns
        -------

        """
        self._app["dielectric_x_position"] = "patch_position_x - patch_length * 50 / 100"
        self._app["dielectric_y_position"] = "patch_position_y - patch_width * 50 / 100"
        self._app["dielectric_length"] = (
            "abs(patch_position_x + patch_length * (1 + 50 / 100)) +" " abs(dielectric_x_position)"
        )
        self._app["dielectric_width"] = (
            "abs(patch_position_y + patch_width * (1 + 50 / 100)) +" " abs(dielectric_y_position)"
        )

    @pyaedt_function_handler()
    def create_region(self, pad_percent=None):
        """

        Parameters
        ----------
        pad_percent

        Returns
        -------

        """
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


class CommonObject(object):
    """ """

    def __init__(self, application, metric_unit="mm"):
        self._application = application
        self._metric_unit = metric_unit
        self._name = None
        self._dielectric_layer = None
        self._signal_layer = None
        self._aedt_object = None
        self._layer_name = None
        self._layer_number = None
        self._material_name = None
        self._reference_system = None

    @property
    def reference_system(self):
        """

        Returns
        -------

        """
        return self._reference_system

    @property
    def metric_unit(self):
        """

        Returns
        -------

        """
        return self._metric_unit

    @metric_unit.setter
    def metric_unit(self, value):
        self._metric_unit = value

    @property
    def dielectric_layer(self):
        """

        Returns
        -------

        """
        return self._dielectric_layer

    @property
    def signal_layer(self):
        """

        Returns
        -------

        """
        return self._signal_layer

    @property
    def name(self):
        """

        Returns
        -------

        """
        return self._name

    # TODO name@setter

    @property
    def application(self):
        """

        Returns
        -------

        """
        return self._application

    @property
    def aedt_object(self):
        """

        Returns
        -------

        """
        return self._aedt_object

    @property
    def layer_name(self):
        """

        Returns
        -------

        """
        return self._layer_name

    @property
    def layer_number(self):
        """

        Returns
        -------

        """
        return self._layer_number

    @property
    def material_name(self):
        """

        Returns
        -------

        """
        return self._material_name

    @property
    def points_on_layer(self):
        """

        Returns
        -------

        """
        bb = self._aedt_object.bounding_box
        return [[bb[0], bb[1]], [bb[0], bb[4]], [bb[3], bb[4]], [bb[3], bb[1]]]

    @property
    def get_maximum_in_x(self):
        """

        Returns
        -------

        """
        bb = self._aedt_object.bounding_box
        return max(bb[0], bb[3])

    @property
    def get_minimum_in_x(self):
        """

        Returns
        -------

        """
        bb = self._aedt_object.bounding_box
        return min(bb[0], bb[3])

    @property
    def get_maximum_in_y(self):
        """

        Returns
        -------

        """
        bb = self._aedt_object.bounding_box
        return max(bb[1], bb[4])

    @property
    def get_minimum_in_y(self):
        """

        Returns
        -------

        """
        bb = self._aedt_object.bounding_box
        return min(bb[1], bb[4])


class Patch(CommonObject, object):
    """ """

    def __init__(
        self,
        application,
        frequency,
        patch_width,
        signal_layer,
        dielectric_layer,
        patch_length=None,
        patch_position_x=0,
        patch_position_y=0,
        patch_name="patch",
        metric_unit="mm",
        reference_system=None,
        axis="X",
    ):
        CommonObject.__init__(self, application, metric_unit)
        self._frequency = NamedVariable(application, patch_name + "_frequency", str(frequency) + "Hz")
        self._signal_layer = signal_layer
        self._dielectric_layer = dielectric_layer
        self._substrate_thickness = dielectric_layer.thickness
        self._width = NamedVariable(application, patch_name + "_width", str(patch_width) + metric_unit)
        self._position_x = NamedVariable(application, patch_name + "_position_x", str(patch_position_x) + metric_unit)
        self._position_y = NamedVariable(application, patch_name + "_position_y", str(patch_position_y) + metric_unit)
        self._position_z = signal_layer.position
        self._metric_unit = metric_unit
        self._dielectric_layer = dielectric_layer
        self._signal_layer = signal_layer
        self._dielectric_material = dielectric_layer.material
        self._material_name = signal_layer.material_name
        self._layer_name = signal_layer.name
        self._layer_number = signal_layer.number
        self._name = patch_name
        self._patch_thickness = signal_layer.thickness
        self._application = application
        self._aedt_object = None
        try:
            self._permittivity = NamedVariable(
                application, patch_name + "_permittivity", float(self._dielectric_material.permittivity.value)
            )
        except:
            self._permittivity = NamedVariable(
                application,
                patch_name + "_permittivity",
                float(application.variable_manager[self._dielectric_material.permittivity.value].value),
            )
        if isinstance(patch_length, float) or isinstance(patch_length, int):
            self._length = NamedVariable(application, patch_name + "_length", str(patch_length) + metric_unit)
            self._effective_permittivity = self.effective_permittivity_calcul
            self._wave_length = self.wave_length_calcul
        elif patch_length is None:
            self._effective_permittivity = self.effective_permittivity_calcul
            self._added_length = self.added_length_calcul
            self._wave_length = self.wave_length_calcul
            self._length = self.length_calcul
        self._impedance_l_w, self._impedance_w_l = self.impedance_calcul
        if reference_system:
            application.modeler.set_working_coordinate_system(reference_system)
            if axis == "X":
                start_point = [
                    "{0}_position_x".format(self._name),
                    "{0}_position_y-{0}_width/2".format(self._name),
                    0,
                ]
            else:
                start_point = [
                    "{0}_position_x-{0}_width/2".format(self._name),
                    "{}_position_y".format(self._name),
                    0,
                ]
            self._reference_system = reference_system
        else:
            application.modeler.create_coordinate_system(
                origin=[
                    "{0}_position_x".format(patch_name),
                    "{}_position_y".format(patch_name),
                    signal_layer.position.name,
                ],
                reference_cs="Global",
                name=patch_name + "_CS",
            )
            if axis == "X":
                start_point = [0, "-{}_width/2".format(patch_name), 0]

            else:
                start_point = ["-{}_width/2".format(patch_name), 0, 0]
            application.modeler.set_working_coordinate_system(patch_name + "_CS")

            self._reference_system = patch_name + "_CS"
        if signal_layer.thickness:
            self._aedt_object = application.modeler.primitives.create_box(
                position=start_point,
                dimensions_list=[
                    "{}_length".format(patch_name),
                    "{}_width".format(patch_name),
                    signal_layer.thickness.name,
                ],
                name=patch_name,
                matname=signal_layer.material_name,
            )
        else:
            self._aedt_object = application.modeler.primitives.create_rectangle(
                position=start_point,
                dimension_list=[self.length.name, self.width.name],
                name=patch_name,
                matname=signal_layer.material_name,
            )
            application.assign_coating(self._aedt_object.name, signal_layer.material)
        application.modeler.set_working_coordinate_system("Global")
        application.modeler.subtract(blank_list=[signal_layer.name], tool_list=[patch_name], keepOriginals=True)

    @property
    def frequency(self):
        """

        Returns
        -------

        """
        return self._frequency

    @property
    def substrate_thickness(self):
        """

        Returns
        -------

        """
        return self._substrate_thickness

    @property
    def width(self):
        """

        Returns
        -------

        """
        return self._width

    @property
    def position_x(self):
        """

        Returns
        -------

        """
        return self._position_x

    @property
    def position_y(self):
        """

        Returns
        -------

        """
        return self._position_y

    @property
    def permittivity(self):
        """

        Returns
        -------

        """
        return self._permittivity

    @property
    def permittivity_calcul(self):
        """

        Returns
        -------

        """
        self._permittivity = self.application.materials[self._dielectric_material].permittivity
        return self._permittivity

    @property
    def effective_permittivity(self):
        """

        Returns
        -------

        """
        return self._effective_permittivity

    @property
    def effective_permittivity_calcul(self):
        """

        Returns
        -------

        """
        # "(substrat_permittivity + 1)/2 + (substrat_permittivity -
        # 1)/(2 * sqrt(1 + 10 * substrate_thickness/patch_width))"
        er = self._permittivity.name
        h = self._substrate_thickness.name
        w = self._width.name
        patch_eff_permittivity_formula = "(" + er + "+ 1)/2 + (" + er + "- 1)/(2 * sqrt(1 + 10 * " + h + "/" + w + "))"
        self._effective_permittivity = NamedVariable(
            self.application, self._name + "_eff_permittivity", patch_eff_permittivity_formula
        )
        return self._effective_permittivity

    @property
    def added_length(self):
        """

        Returns
        -------

        """
        return self._added_length

    @property
    def added_length_calcul(self):
        """

        Returns
        -------

        """
        # "0.412 * substrate_thickness * (patch_eff_permittivity + 0.3) * (patch_width/substrate_thickness + 0.264)"
        # " / ((patch_eff_permittivity - 0.258) * (patch_width/substrate_thickness + 0.813)) "

        er_e = self._effective_permittivity.name
        h = self._substrate_thickness.name
        w = self._width.name
        patch_added_length_formula = (
            "0.412 * " + h + " * (" + er_e + " + 0.3) * (" + w + "/" + h + " + 0.264)/"
            "((" + er_e + " - 0.258) * (" + w + "/" + h + " + 0.813))"
        )
        self._added_length = NamedVariable(self.application, self._name + "_added_length", patch_added_length_formula)
        return self._added_length

    @property
    def wave_length(self):
        """

        Returns
        -------

        """
        return self._wave_length

    @property
    def wave_length_calcul(self):
        """

        Returns
        -------

        """
        # "c0 * 1000/(patch_frequency * sqrt(patch_eff_permittivity))"
        # TODO it is currently only available for mm
        f = self._frequency.name
        er_e = self._effective_permittivity.name
        patch_wave_length_formula = "c0 * 1000/(" + f + "* sqrt(" + er_e + "))"
        self._wave_length = NamedVariable(
            self.application, self._name + "_wave_length", patch_wave_length_formula + self._metric_unit
        )
        return self._wave_length

    @property
    def length(self):
        """

        Returns
        -------

        """
        return self._length

    @property
    def length_calcul(self):
        """

        Returns
        -------

        """
        # "patch_wave_length / 2 - 2 * patch_added_length"
        d_l = self._added_length.name
        lbd = self._wave_length.name
        patch_length_formula = lbd + "/2" + " - 2 * " + d_l
        self._length = NamedVariable(self.application, self._name + "_length", patch_length_formula)
        return self._length

    @property
    def impedance(self):
        """

        Returns
        -------

        """
        return self._impedance_l_w, self._impedance_w_l

    @property
    def impedance_calcul(self):
        """

        Returns
        -------

        """
        # "45 * (patch_wave_length/patch_width * sqrt(patch_eff_permittivity)) ** 2"
        # "60 * patch_wave_length/patch_width * sqrt(patch_eff_permittivity)"
        er_e = self._effective_permittivity.name
        lbd = self._wave_length.name
        w = self._width.name
        patch_impedance_formula_l_w = "45 * (" + lbd + "/" + w + "* sqrt(" + er_e + ")) ** 2"
        patch_impedance_formula_w_l = "60 * " + lbd + "/" + w + "* sqrt(" + er_e + ")"
        self._impedance_l_w = NamedVariable(
            self.application, self._name + "_impedance_l_w", patch_impedance_formula_l_w
        )
        self._impedance_w_l = NamedVariable(
            self.application, self._name + "_impedance_w_l", patch_impedance_formula_w_l
        )
        self.application.logger.warning(
            "The closer the ratio between wave length and the width is to 1,"
            " the less correct the impedance calculation is"
        )
        return self._impedance_l_w, self._impedance_w_l


class Line(CommonObject, object):
    """ """

    def __init__(
        self,
        application,
        frequency,
        line_impedance,
        line_width,
        signal_layer,
        dielectric_layer,
        line_length=None,
        line_electrical_length=90,
        line_position_x=0,
        line_position_y=0,
        line_name="line",
        metric_unit="mm",
        reference_system=None,
        axis="X",
    ):
        CommonObject.__init__(self, application, metric_unit)
        self._frequency = NamedVariable(application, line_name + "_frequency", str(frequency) + "Hz")
        self._signal_layer = signal_layer
        self._dielectric_layer = dielectric_layer
        self._substrate_thickness = dielectric_layer.thickness
        self._position_x = NamedVariable(application, line_name + "_position_x", str(line_position_x) + metric_unit)
        self._position_y = NamedVariable(application, line_name + "_position_y", str(line_position_y) + metric_unit)
        self._position_z = signal_layer.position
        self._dielectric_material = dielectric_layer.material
        self._material_name = signal_layer.material_name
        self._layer_name = signal_layer.name
        self._layer_number = signal_layer.number
        self._name = line_name
        self._line_thickness = signal_layer.thickness
        self._width = None
        self._width_h_w = None
        self._axis = axis
        try:
            self._permittivity = NamedVariable(
                application, line_name + "_permittivity", float(self._dielectric_material.permittivity.value)
            )
        except:
            self._permittivity = NamedVariable(
                application,
                line_name + "_permittivity",
                float(application.variable_manager[self._dielectric_material.permittivity.value].value),
            )
        if isinstance(line_width, float) or isinstance(line_width, int):
            self._width = NamedVariable(application, line_name + "_width", str(line_width) + metric_unit)
            self._effective_permittivity = self.effective_permittivity_calcul
            self._wave_length = self.wave_length_calcul
            self._added_length = self.added_length_calcul
            if isinstance(line_electrical_length, float) or isinstance(line_electrical_length, int):
                self._electrical_length = NamedVariable(
                    application, line_name + "_elec_length", str(line_electrical_length)
                )
                self._length = self.length_calcul
            elif isinstance(line_length, float) or isinstance(line_length, int):
                self._length = NamedVariable(application, line_name + "_length", str(line_length) + metric_unit)
                self._electrical_length = self.electrical_length_calcul
            else:
                application.logger.error("line_length must be a float.")
            self._charac_impedance_w_h, self._charac_impedance_h_w = self.charac_impedance_calcul
        elif line_width is None:
            self._charac_impedance = NamedVariable(
                self.application, line_name + "_charac_impedance_h_w", str(line_impedance)
            )
            self._width, self._width_h_w = self.width_calcul
            self._effective_permittivity = self.effective_permittivity_calcul
            self._wave_length = self.wave_length_calcul
            self._added_length = self.added_length_calcul
            if isinstance(line_electrical_length, float) or isinstance(line_electrical_length, int):
                self._electrical_length = NamedVariable(
                    application, line_name + "_elec_length", str(line_electrical_length)
                )
                self._length = self.length_calcul
            elif isinstance(line_length, float) or isinstance(line_length, int):
                self._length = NamedVariable(application, line_name + "_length", str(line_length) + metric_unit)
                self._electrical_length = self.electrical_length_calcul
            else:
                application.logger.error("line_length must be a float.")
        if reference_system:
            application.modeler.set_working_coordinate_system(reference_system)
            if axis == "X":
                start_point = [
                    "{0}_position_x".format(self._name),
                    "{0}_position_y-{0}_width/2".format(self._name),
                    0,
                ]
            else:

                start_point = [
                    "{0}_position_x-{0}_width/2".format(self._name),
                    "{}_position_y".format(self._name),
                    0,
                ]
            self._reference_system = reference_system
        else:
            application.modeler.create_coordinate_system(
                origin=[
                    "{}_position_x".format(self._name),
                    "{}_position_y".format(self._name),
                    signal_layer.position.name,
                ],
                reference_cs="Global",
                name=line_name + "_CS",
            )
            application.modeler.set_working_coordinate_system(line_name + "_CS")
            if axis == "X":
                start_point = [0, "-{0}_width/2".format(self._name), 0]
            else:
                start_point = ["-{0}_width/2".format(self._name), 0, 0]
            self._reference_system = line_name + "_CS"
        if signal_layer.thickness:
            self._aedt_object = application.modeler.primitives.create_box(
                position=start_point,
                dimensions_list=[
                    "{}_length".format(self._name),
                    "{}_width".format(self._name),
                    signal_layer.thickness.name,
                ],
                name=line_name,
                matname=signal_layer.material_name,
            )
        else:
            self._aedt_object = application.modeler.primitives.create_rectangle(
                position=start_point,
                dimension_list=["{}_length".format(self._name), "{}_width".format(self._name)],
                name=line_name,
                matname=signal_layer.material_name,
            )
        application.modeler.set_working_coordinate_system("Global")
        application.modeler.subtract(blank_list=[signal_layer.name], tool_list=[line_name], keepOriginals=True)

    @property
    def frequency(self):
        """

        Returns
        -------

        """
        return self._frequency

    @property
    def substrate_thickness(self):
        """

        Returns
        -------

        """
        return self._substrate_thickness

    @property
    def width(self):
        """

        Returns
        -------

        """
        return self._width

    @property
    def width_h_w(self):
        """

        Returns
        -------

        """
        if self._width_h_w is not None:
            return self._width_h_w

    @property
    def width_calcul(self):
        """

        Returns
        -------

        """
        # if w/h < 2 :
        # a = z * sqrt((er + 1) / 2) / 60 + (0.23 + 0.11 / er) * (er - 1) / (er + 1)
        # w/h = 8 * exp(a) / (exp(2 * a) - 2)
        # else w/h > 2 :
        # b = 377 * pi / (2 * z * sqrt(er))
        # w/h = 2 * (b - 1 - log(2 * b - 1) * (er - 1) * (log(b - 1) + 0.39 - 0.61 / er) / (2 * er)) / pi
        h = self._substrate_thickness.name
        z = self._charac_impedance.name
        er = self._permittivity.name
        a_formula = (
            "("
            + z
            + " * sqrt(("
            + er
            + " + 1)/2)/60 + (0.23 + 0.11/"
            + er
            + ")"
            + " * ("
            + er
            + "- 1)/("
            + er
            + "+ 1))"
        )
        w_div_by_h_inf_2 = "(8 * exp(" + a_formula + ")/(exp(2 * " + a_formula + ") - 2))"

        b_formula = "(377 * pi/(2 * " + z + " * " + "sqrt(" + er + ")))"
        w_div_by_h_sup_2 = (
            "(2 * ("
            + b_formula
            + " - 1 - log(2 * "
            + b_formula
            + " - 1) * ("
            + er
            + " - 1) * (log("
            + b_formula
            + " - 1) + 0.39 - 0.61/"
            + er
            + ")/(2 * "
            + er
            + "))/pi)"
        )

        w_formula_inf = w_div_by_h_inf_2 + " * " + h
        w_formula_sup = w_div_by_h_sup_2 + " * " + h

        self._width_h_w = NamedVariable(self.application, self._name + "_width_h_w", w_formula_inf)
        self._width = NamedVariable(self.application, self._name + "_width", w_formula_sup)

        return self._width, self._width_h_w

    @property
    def position_x(self):
        """

        Returns
        -------

        """
        return self._position_x

    @property
    def position_y(self):
        """

        Returns
        -------

        """
        return self._position_y

    @property
    def permittivity(self):
        """

        Returns
        -------

        """
        return self._permittivity

    @property
    def permittivity_calcul(self):
        """

        Returns
        -------

        """
        self._permittivity = self.application.materials[self._dielectric_material].permittivity
        return self._permittivity

    @property
    def added_length(self):
        """

        Returns
        -------

        """
        return self._added_length

    @property
    def added_length_calcul(self):
        """

        Returns
        -------

        """
        # "0.412 * substrate_thickness * (patch_eff_permittivity + 0.3) * (patch_width/substrate_thickness + 0.264)"
        # " / ((patch_eff_permittivity - 0.258) * (patch_width/substrate_thickness + 0.813)) "

        er_e = self._effective_permittivity.name
        h = self._substrate_thickness.name
        w = self._width.name
        patch_added_length_formula = (
            "0.412 * " + h + " * (" + er_e + " + 0.3) * (" + w + "/" + h + " + 0.264)/"
            "((" + er_e + " - 0.258) * (" + w + "/" + h + " + 0.813))"
        )
        self._added_length = NamedVariable(self.application, self._name + "_added_length", patch_added_length_formula)
        return self._added_length

    @property
    def length(self):
        """

        Returns
        -------

        """
        return self._length

    @property
    def length_calcul(self):
        """

        Returns
        -------

        """
        # "patch_wave_length / 2 - 2 * patch_added_length"
        d_l = self._added_length.name
        lbd = self._wave_length.name
        e_l = self._electrical_length.name
        line_length_formula = lbd + "* (" + e_l + "/360)" + " - 2 * " + d_l
        self._length = NamedVariable(self.application, self._name + "_length", line_length_formula)
        return self._length

    @property
    def charac_impedance(self):
        """

        Returns
        -------

        """
        return self._charac_impedance

    @property
    def charac_impedance_calcul(self):
        """

        Returns
        -------

        """
        # if w / h > 1: 60 * log(8 * h / w + w / (4 * h)) / sqrt(er_e)
        # if w / h < 1: 120 * pi / (sqrt(er_e) * (w / h + 1.393 + 0.667 * log(w / h + 1.444)))
        w = self._width.name
        h = self._dielectric_layer.thickness.name
        er_e = self.effective_permittivity.name
        charac_impedance_formula_w_h = (
            "60 * log(8 * " + h + "/" + w + " + " + w + "/(4 * " + h + "))/sqrt(" + er_e + ")"
        )
        charac_impedance_formula_h_w = (
            "120 * pi / (sqrt(" + er_e + ") * (" + w + "/" + h + "+ 1.393 + 0.667 * log(" + w + "/" + h + " + 1.444)))"
        )
        self._charac_impedance_w_h = NamedVariable(
            self.application, self._name + "_charac_impedance_w_h", charac_impedance_formula_w_h
        )
        self._charac_impedance_h_w = NamedVariable(
            self.application, self._name + "_charac_impedance_h_w", charac_impedance_formula_h_w
        )
        return self._charac_impedance_w_h, self._charac_impedance_h_w

    @property
    def effective_permittivity(self):
        """

        Returns
        -------

        """
        return self._effective_permittivity

    @property
    def effective_permittivity_calcul(self):
        """

        Returns
        -------

        """
        # "(substrat_permittivity + 1)/2 +
        # (substrat_permittivity - 1)/(2 * sqrt(1 + 10 * substrate_thickness/patch_width))"
        er = self._permittivity.name
        h = self._substrate_thickness.name
        w = self._width.name
        patch_eff_permittivity_formula = (
            "(" + er + " + 1)/2 + (" + er + " - 1)/(2 * sqrt(1 + 10 * " + h + "/" + w + "))"
        )
        self._effective_permittivity = NamedVariable(
            self.application, self._name + "_eff_permittivity", patch_eff_permittivity_formula
        )
        return self._effective_permittivity

    @property
    def wave_length(self):
        """

        Returns
        -------

        """
        return self._wave_length

    @property
    def wave_length_calcul(self):
        """

        Returns
        -------

        """
        # "c0 * 1000/(patch_frequency * sqrt(patch_eff_permittivity))"
        # TODO it is currently only available for mm
        f = self._frequency.name
        er_e = self._effective_permittivity.name
        patch_wave_length_formula = "c0 * 1000/(" + f + "* sqrt(" + er_e + "))"
        self._wave_length = NamedVariable(
            self.application, self._name + "_wave_length", patch_wave_length_formula + self.metric_unit
        )
        return self._wave_length

    @property
    def electrical_length(self):
        """

        Returns
        -------

        """
        return self._electrical_length

    @property
    def electrical_length_calcul(self):
        """

        Returns
        -------

        """
        lbd = self._wave_length.name
        length = self._length.name
        d_l = self._added_length.name
        elec_length_formula = "360 * (" + length + " + 2 * " + d_l + ")/" + lbd
        self._electrical_length = NamedVariable(self.application, self._name + "_elec_length", elec_length_formula)
        return self._electrical_length

    @pyaedt_function_handler()
    def create_lumped_port(self, reference_layer_name, change_side=False):
        """

        Parameters
        ----------
        reference_layer_name
        change_side

        Returns
        -------

        """
        if self._axis == "X":
            if change_side:
                axisdir = self.application.AxisDir.XNeg
            else:
                axisdir = self.application.AxisDir.XPos
        else:
            if change_side:
                axisdir = self.application.AxisDir.YNeg
            else:
                axisdir = self.application.AxisDir.YPos
        return self.application.create_lumped_port_between_objects(
            reference_layer_name, self.aedt_object.name, axisdir=axisdir
        )


class Polygon(CommonObject, object):
    """ """

    def __init__(
        self,
        application,
        point_list,
        thickness,
        signal_layer_name,
        poly_name="poly",
        metric_unit="mm",
        mat_name="copper",
        is_void=False,
        reference_system=None,
    ):
        CommonObject.__init__(self, application, metric_unit)

        self._metric_unit = metric_unit
        self._is_void = is_void
        self._layer_name = signal_layer_name
        self._app = application
        pts = []
        for el in point_list:
            pts.append(
                [
                    application.modeler._arg_with_dim(el[0]),
                    application.modeler._arg_with_dim(el[1]),
                    "layer_" + str(signal_layer_name) + "_position",
                ]
            )
        if reference_system:
            application.modeler.set_working_coordinate_system(reference_system)
            self._reference_system = reference_system
        else:
            application.modeler.create_coordinate_system(
                origin=[0, 0, 0], reference_cs="Global", name=poly_name + "_CS"
            )
            application.modeler.set_working_coordinate_system(poly_name + "_CS")

            self._reference_system = poly_name + "_CS"
        self._aedt_object = application.modeler.create_polyline(
            position_list=pts, name=poly_name, matname=mat_name, cover_surface=True
        )
        if thickness:
            if isinstance(thickness, (float, int)):
                application.modeler.sweep_along_vector(self._aedt_object, [0, 0, thickness], draft_type="Natural")
            else:
                application.modeler.sweep_along_vector(self._aedt_object, [0, 0, thickness.name], draft_type="Natural")
        application.modeler.set_working_coordinate_system("Global")

    @property
    def points_on_layer(self):
        """

        Returns
        -------

        """
        bb = self._aedt_object.bounding_box
        return [[bb[0], bb[1]], [bb[0], bb[4]], [bb[3], bb[4]], [bb[3], bb[1]]]
