from collections import OrderedDict

from pyaedt.generic.general_methods import generate_unique_name
from pyaedt.generic.general_methods import pyaedt_function_handler
from pyaedt.modules.MaterialLib import Material

LAYERS = {"s": "signal", "g": "ground", "d": "dielectric"}


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


class NamedVariable(object):
    """Cast PyAEDT variable object to simplify getters and setters in Stackup3D.

    The returned Polyline object exposes the methods for manipulating the polyline.

    Parameters
    ----------
    application : :class:`pyaedt.hfss.Hfss
        HFSS design or project where the variable is to be created.
    name : str
        The name of the variable. If the the name begins with an '$', the variable will be a project variable.
        Otherwise, it will be a design variable.
    expression : str
        Expression of the value.

    Examples
    --------

    >>> from pyaedt import Hfss
    >>> from pyaedt.modeler.stackup_3d import Stackup3D
    >>> hfss = Hfss()
    >>> my_frequency = NamedVariable(hfss, "my_frequency", "900000Hz")
    >>> wave_length_formula = "c0/" + my_frequency.name
    >>> my_wave_length = NamedVariable(hfss, "my_wave_length", wave_length_formula)
    >>> my_permittivity = NamedVariable(hfss, "my_permittivity", "2.2")
    >>> my_wave_length.expression = my_wave_length.expression + "/" + my_permittivity.name

    """

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
        """Name of the variable as a string."""
        return self._name

    @property
    def expression(self):
        """Expression of the variable as a string."""
        return self._expression

    @expression.setter
    def expression(self, expression):
        """Set the expression of the variable.

        Parameters
        ----------
        expression: str
            Value expression of the variable."""
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
    def evaluated_value(self):
        """String that combines the numeric value and the units."""
        return self._variable.evaluated_value

    @pyaedt_function_handler()
    def hide_variable(self, value=True):
        """Set the variable to a hidden variable.

        Parameters
        ----------
        value : bool, optional
            Whether the variable is a hidden variable. The default is ``True``.

        Returns
        bool
        """
        self._application.variable_manager[self._name].hidden = value
        return True

    @pyaedt_function_handler()
    def read_only_variable(self, value=True):
        """Set the variable to a read-only variable.

        Parameters
        ----------
        value : bool, optional
            Whether the variable is a read-only variable. The default is ``True``.

        Returns
        -------
        bool
        """
        self._application.variable_manager[self._name].read_only = value
        return True


class Layer3D(object):
    """Provides a class for a management of a parametric layer in 3D Modeler."""

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
            obj_3d = self._app.modeler.create_box(
                ["dielectric_x_position", "dielectric_y_position", layer_position],
                ["dielectric_length", "dielectric_width", self._thickness_variable],
                name=self._name,
                matname=self._material_name,
            )
        elif self._layer_type == "ground":
            if thickness:
                obj_3d = self._app.modeler.create_box(
                    ["dielectric_x_position", "dielectric_y_position", layer_position],
                    ["dielectric_length", "dielectric_width", self._thickness_variable],
                    name=self._name,
                    matname=self._material_name,
                )

            else:
                obj_3d = self._app.modeler.create_rectangle(
                    "Z",
                    ["dielectric_x_position", "dielectric_y_position", layer_position],
                    ["dielectric_length", "dielectric_width"],
                    name=self._name,
                    matname=self._material_name,
                )
        elif self._layer_type == "signal":
            if thickness:
                obj_3d = self._app.modeler.create_box(
                    ["dielectric_x_position", "dielectric_y_position", layer_position],
                    ["dielectric_length", "dielectric_width", self._thickness_variable],
                    name=self._name,
                    matname=self._fill_material,
                )
            else:
                obj_3d = self._app.modeler.create_rectangle(
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
        """Layer name.

        Returns
        -------
        str
        """
        return self._name

    @property
    def number(self):
        """Layer ID.

        Returns
        -------
        int
        """
        return self._index

    @property
    def material_name(self):
        """Material name.

        Returns
        -------
        str
        """
        return self._material_name

    @property
    def material(self):
        """Material.

        Returns
        -------
        :class:`pyaedt.modules.Material.Material`
            Material.
        """
        return self._material

    @property
    def filling_material(self):
        """Fill material.

        Returns
        -------
        :class:`pyaedt.modules.Material.Material`
            Material.
        """
        return self._fill_material

    @property
    def filling_material_name(self):
        """Fill material name.

        Returns
        -------
        str
        """
        return self._fill_material_name

    @property
    def thickness(self):
        """Thickness variable.

        Returns
        -------
        :class:`pyaedt.modeler.stackup_3d.NamedVariable`
            Variable Object.
        """
        return self._thickness

    @property
    def thickness_value(self):
        """Thickness value.


        Returns
        -------
        float, str
        """
        return self._thickness.value

    @thickness.setter
    def thickness(self, value):
        self._thickness.expression = value

    @property
    def elevation(self):
        """Layer elevation.

        Returns
        -------
        :class:`pyaedt.modeler.stackup_3d.NamedVariable`
            Variable object.
        """
        return self._position

    @property
    def elevation_value(self):
        """Layer elevation value.

        Returns
        -------
        str, float
        """
        return self._app.variable_manager[self._position.name].value

    @pyaedt_function_handler()
    def duplicate_parametrize_material(self, material_name, cloned_material_name=None, list_of_properties=None):
        """Duplicate a material and parametrize all properties.

        Parameters
        ----------
        material_name : str
            Name of origin material
        cloned_material_name : str, optional
            Name of destination material. The default is ``None``.
        list_of_properties : list, optional
            Properties to parametrize. The default is ``None``.

        Returns
        -------
        :class:`pyaedt.modules.Material.Material`
            Material object.
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
                return application.materials[cloned_material_name]
        else:
            application.logger.error("The material name %s doesn't exist" % material_name)
            return None

    @pyaedt_function_handler()
    def add_patch(
        self,
        frequency,
        patch_width,
        patch_length=None,
        patch_position_x=0,
        patch_position_y=0,
        patch_name=None,
        axis="X",
    ):
        """Create a parametric patch.

        Parameters
        ----------
        frequency : float
            Frequency value for the patch calculation in Hz.
        patch_width : float
            Patch width.
        patch_length : float, optional
            Patch length. The default is ``None``.
        patch_position_x : float, optional
            Patch start x position.
        patch_position_y : float, optional
            Patch start y position. The default is ``0.``
        patch_name : str, optional
            Patch name. The default is ``None``.
        axis : str, optional
            Line orientation axis. The default is ``"X"``.

        Returns
        -------
        :class:`pyaedt.modeler.stackup_3d.Patch`
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
            axis=axis,
        )
        self._obj_3d.append(created_patch.aedt_object)
        self._stackup._object_list.append(created_patch)
        created_patch.aedt_object.group_name = "Layer_{}".format(self._name)
        return created_patch

    @pyaedt_function_handler()
    def add_trace(
        self,
        line_width,
        line_length,
        is_electrical_length=False,
        is_impedance=False,
        line_position_x=0,
        line_position_y=0,
        line_name=None,
        axis="X",
        reference_system=None,
        frequency=1e9,
    ):
        """Create a line.

        Parameters
        ----------
        line_width : float
            Line width. It can be the physical width or the line impedance.
        line_length : float
            Line length. It can be the physical length or the electrical length.
        is_electrical_length : bool, optional
            Whether the line length is an electrical length or a physical length. The default
            is ``False``, which means it is a physical length.
        is_impedance : bool, optional
            Whether the line width is an impedance. The default is ``False``, in which case
            the line width is a geometrical value.
        line_position_x : float, optional
            Line center start x position. The default is ``0``.
        line_position_y : float, optional
            Line center start y position. The default is ``0``.
        line_name : str, optional
            Line name. The default is ``None``.
        axis : str, optional
            Line orientation axis. The default is ``"X"``.
        reference_system : str, optional
            Line reference system. The default is ``None``, in which case a new coordinate
            system is created.
        frequency : float, optional
            Frequency value for the line calculation in Hz. The default is ``1e9``.

        Returns
        -------
        :class:`pyaedt.modeler.stackup_3d.Line`
        """
        if not line_name:
            line_name = generate_unique_name("{0}_line".format(self._name), n=3)
        dielectric_layer = None
        for v in list(self._stackup._stackup.values()):
            if v._index == self._index - 1:
                dielectric_layer = v
                break
        if dielectric_layer is None:
            self._app.logger.error("There is no layer under this layer.")

        created_line = Trace(
            self._app,
            frequency,
            line_width if is_impedance else None,
            line_width if not is_impedance else None,
            self,
            dielectric_layer,
            line_length=line_length if not is_electrical_length else None,
            line_electrical_length=line_length if is_electrical_length else None,
            line_position_x=line_position_x,
            line_position_y=line_position_y,
            line_name=line_name,
            reference_system=reference_system,
            axis=axis,
        )
        created_line.aedt_object.group_name = "Layer_{}".format(self._name)
        self._obj_3d.append(created_line.aedt_object)
        self._stackup._object_list.append(created_line)
        return created_line

    @pyaedt_function_handler()
    def add_polygon(self, points, material="copper", is_void=False, poly_name=None):
        """Create a polygon.

        Parameters
        ----------
        points : list
            Points list of [x,y] coordinates.
        material : str, optional
            Material name. The default is ``"copper"``.
        is_void : bool, optional
            Whether the polygon is a void. The default is ``False``.
            On ground layers, it will act opposite of the Boolean value because the ground
            is negative.
        poly_name : str, optional
            Polygon name. The default is ``None``.

        Returns
        -------

        """
        if not poly_name:
            poly_name = generate_unique_name("{0}_poly".format(self._name), n=3)
        polygon = Polygon(
            self._app,
            points,
            thickness=self._thickness,
            signal_layer_name=self._name,
            mat_name=material,
            is_void=is_void,
            poly_name=poly_name,
        )
        polygon.aedt_object.group_name = "Layer_{}".format(self._name)

        if self._layer_type == "ground":
            if not is_void:
                if polygon.aedt_object.is3d:
                    self._app.modeler[self._name].subtract(polygon.aedt_object, True)
                    polygon.aedt_object.material_name = self.filling_material_name
                else:
                    self._app.modeler[self._name].subtract(polygon.aedt_object, False)
                    return True
        elif is_void:
            if polygon.aedt_object.is3d:
                self._app.modeler.subtract(self._obj_3d, polygon.aedt_object, True)
                polygon.aedt_object.material_name = self.filling_material_name
            else:
                self._app.modeler[self._name].subtract(polygon.aedt_object, False)
                return True
        else:
            self._app.modeler.subtract(self._obj_3d[0], polygon.aedt_object, True)
            self._obj_3d.append(polygon.aedt_object)
            self._stackup._object_list.append(polygon)
        return polygon


class PadstackLayer(object):
    """Provides a data class for the definition of a padstack layer and relative pad and antipad values."""

    def __init__(self, padstack, layer_name, elevation, thickness):
        self._padstack = padstack
        self._layer_name = layer_name
        self._layer_elevation = elevation
        self._layer_thickness = thickness
        self._pad_radius = 1
        self._antipad_radius = 2
        self._units = "mm"


class Padstack(object):
    """Padstack Class member of Stackup3D."""

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
            self._padstacks_by_layer[k] = PadstackLayer(self, k, v.elevation, v.thickness)
        if v and v._layer_type == "dielectric":
            del self._padstacks_by_layer[k]
        self._padstacks_material = material

    @property
    def plating_ratio(self):
        """Plating ratio between 0 and 1.

        Returns
        -------
        float
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
        """Number of sides on the circle, which is 0 for a true circle.

        Returns
        -------
        int
        """
        return self._num_sides

    @num_sides.setter
    def num_sides(self, val):
        self._num_sides = val

    @pyaedt_function_handler()
    def set_all_pad_value(self, value):
        """Set all pads in all layers to a specified value.

        Parameters
        ----------
        value : float
            Pad radius.

        Returns
        -------
        bool
            "True`` when successful, ``False`` when failed.
        """
        for v in list(self._padstacks_by_layer.values()):
            v._pad_radius = value
        return True

    @pyaedt_function_handler()
    def set_all_antipad_value(self, value):
        """Set all antipads in all layers to a specified value.

        Parameters
        ----------
        value : float
            Pad radius.

        Returns
        -------
        bool
             "True`` when successful, ``False`` when failed.
        """
        for v in list(self._padstacks_by_layer.values()):
            v._antipad_radius = value
        return True

    @pyaedt_function_handler()
    def set_start_layer(self, layer):
        """Set the start layer to a specified value.

        Parameters
        ----------
        layer : str
            Layer name.

        Returns
        -------
        bool
             "True`` when successful, ``False`` when failed.

        """
        found = False
        new_stackup = OrderedDict({})
        for k, v in self._stackup.stackup_layers.items():
            if k == layer:
                found = True
            if found and layer not in self._padstacks_by_layer:
                new_stackup[k] = PadstackLayer(self, k, v.elevation)
            elif found:
                new_stackup[k] = self._padstacks_by_layer[k]
        self._padstacks_by_layer = new_stackup
        return True

    @pyaedt_function_handler()
    def set_stop_layer(self, layer):
        """Set the stop layer to a specified value.

        Parameters
        ----------
        layer : str
            Layer name.

        Returns
        -------
        bool
             "True`` when successful, ``False`` when failed.

        """
        found = False
        new_stackup = OrderedDict({})
        for k in list(self._stackup.stackup_layers.keys()):
            if k == layer:
                found = True
            if not found and k in list(self._padstacks_by_layer.keys()):
                new_stackup[k] = self._padstacks_by_layer[k]
        self._padstacks_by_layer = new_stackup

    @pyaedt_function_handler()
    def add_via(self, position_x=0, position_y=0, instance_name=None, reference_system=None):
        """Insert a new via on this padstack.

        Parameters
        ----------
        position_x : float, optional
            Center x position. The default is ``0``.
        position_y : float, optional
            Center y position. The default is ``0``.
        instance_name : str, optional
            Via name. The default is ``None``.
        reference_system : str, optional
            Whether to use an existing reference system or create a new one. The default
            is ``None``, in which case a new reference system is created.

        Returns
        -------
        :class:`pyaedt.modeler.Object3d.Object3d`
            Object created.
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
            for v in list(self._padstacks_by_layer.values()):
                if not first_el:
                    first_el = v._layer_elevation
                else:
                    position_x = self._app.modeler._arg_with_dim(position_x)
                    position_y = self._app.modeler._arg_with_dim(position_y)
                    cyls.append(
                        self._app.modeler.create_cylinder(
                            "Z",
                            [position_x, position_y, v._layer_elevation.name],
                            v._pad_radius,
                            v._layer_thickness.name,
                            matname=self._padstacks_material,
                            name=instance_name,
                            numSides=self._num_sides,
                        )
                    )
                    if self.plating_ratio < 1:
                        hole = self._app.modeler.create_cylinder(
                            "Z",
                            [position_x, position_y, v._layer_elevation.name],
                            "{}*{}".format(self._app.modeler._arg_with_dim(v._pad_radius), 1 - self.plating_ratio),
                            v._layer_thickness.name,
                            matname=self._padstacks_material,
                            name=instance_name,
                            numSides=self._num_sides,
                        )
                        cyls[-1].subtract(hole, False)
                    anti = self._app.modeler.create_cylinder(
                        "Z",
                        [position_x, position_y, v._layer_elevation.name],
                        v._antipad_radius,
                        v._layer_thickness.name,
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
    """Main Stackup3D Class."""

    def __init__(self, application):
        self._app = application
        self._layer_name = []
        self._layer_position = []
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
        """List of padstacks created.

        Returns
        -------
        List
        """
        return self._padstacks

    @property
    def dielectrics(self):
        """List of dielectrics created.

        Returns
        -------
        List
        """
        return self._dielectric_list

    @property
    def grounds(self):
        """List of grounds created.

        Returns
        -------
        List
        """
        return self._ground_list

    @property
    def signals(self):
        """List of signals created.

        Returns
        -------
        List
        """
        return self._signal_list

    @property
    def objects(self):
        """List of obects created.

        Returns
        -------
        List
        """
        return self._object_list

    @property
    def objects_by_layer(self):
        """List of padstacks created.

        Returns
        -------
        List
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
        """Variable containing the start position.

        Returns
        -------
        :class:`pyaedt.modeler.stackup_3d.NamedVariable`
        """
        return self._start_position

    @start_position.setter
    def start_position(self, expression):
        self._start_position.expression = expression

    @property
    def dielectric_x_position(self):
        """Stackup x origin.

        Returns
        -------
        :class:`pyaedt.modeler.stackup_3d.NamedVariable`
            Variable object.
        """
        return self._dielectric_x_position

    @dielectric_x_position.setter
    def dielectric_x_position(self, expression):
        self._dielectric_x_position.expression = expression

    @property
    def dielectric_y_position(self):
        """Stackup y origin.

        Returns
        -------
        :class:`pyaedt.modeler.stackup_3d.NamedVariable`
            Variable object.
        """
        return self._dielectric_x_position

    @dielectric_y_position.setter
    def dielectric_y_position(self, expression):
        self._dielectric_y_position.expression = expression

    @property
    def dielectric_width(self):
        """Stackup width.

        Returns
        -------
        :class:`pyaedt.modeler.stackup_3d.NamedVariable`
            Variable object.
        """
        return self._dielectric_width

    @dielectric_width.setter
    def dielectric_width(self, expression):
        self._dielectric_width.expression = expression

    @property
    def dielectric_length(self):
        """Stackup length.

        Returns
        -------
        :class:`pyaedt.modeler.stackup_3d.NamedVariable`
            Variable object.
        """
        return self._dielectric_length

    @dielectric_length.setter
    def dielectric_length(self, expression):
        self._dielectric_length.expression = expression

    @property
    def layer_names(self):
        """List of all layer names.

        Returns
        -------
        list
        """
        return self._layer_name

    @property
    def layer_positions(self):
        """List of all layer positions.

        Returns
        -------
        List
        """
        return self._layer_position

    @property
    def stackup_layers(self):
        """Dictionary of all stackup layers.

        Returns
        -------
        dict
        """
        return self._stackup

    @property
    def z_position_offset(self):
        """Elevation.

        Returns
        -------

        """
        return self._z_position_offset

    @pyaedt_function_handler()
    def add_padstack(self, name, material="copper"):
        """Add a new padstack definition.

        Parameters
        ----------
        name : str
            padstack name
        material : str, optional
            Padstack material. The default is ``"copper"``.

        Returns
        -------
        :class:`pyaedt.modeler.stackup_3d.Padstack`
        """
        p = Padstack(self._app, self, name, material)
        self._padstacks.append(p)
        return p

    @pyaedt_function_handler()
    def add_layer(self, name, layer_type="S", material="copper", thickness=0.035, fill_material="FR4_epoxy"):
        """Add a new layer to the stackup.
        The new layer can be a signal (S), ground (G), or dielectric (D).
        The layer is entirely filled with the specified fill material. Anything will be drawn
        wmaterial.

        Parameters
        ----------
        name : str
            Layer name.
        layer_type : str, optional
            Layer type. Options are ``"S"``, ``"D"``, and ``"G"``. The default is ``"S"``.
        material : str, optional
            Material name. The default is ``"copper"``. The material will be parametrized.
        thickness : float, optional
            Thickness value. The default is ``0.035``. The thickness will be parametrized.
        fill_material : str, optional
            Fill material name. The default is ``"FR4_epoxy"``. The fill material will be
            parametrized. This parameter is not valid for dielectrics.

        Returns
        -------
        :class:`pyaedt.modeler.stackup_3d.Layer3D`
            Layer object.
        """
        self._shifted_index += 1
        if not layer_type:
            raise ValueError("Layer type has to be an S, D, or G string.")
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
        """Add a new ground layer to the stackup.
        A signal layer is positive. The layer is entirely filled with the fill material.
        Anything will be drawn wmaterial.

        Parameters
        ----------
        name : str
            Layer name.
        material : str, optional
            Material name. Material will be parametrized. Default value is `"copper"`.
        thickness : float, optional
            Thickness value. Thickness will be parametrized. Default value is `0.035`.
        fill_material : str, optional
            Fill material name. Material will be parametrized. Default value is `"FR4_epoxy"`.

        Returns
        -------
        :class:`pyaedt.modeler.stackup_3d.Layer3D`
            Layer object.
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
        """Add a new dielectric layer to the stackup.

        Parameters
        ----------
        name : str
            Layer name.
        material : str
            Material name. The default is ``"FR4_epoxy"``. The material will be parametrized.
        thickness : float, optional
            Thickness value. The default is ``0.035``. The thickness will be parametrized.


        Returns
        -------
        :class:`pyaedt.modeler.stackup_3d.Layer3D`
            Layer 0bject.
        """
        return self.add_layer(name=name, layer_type="D", material=material, thickness=thickness, fill_material=None)

    @pyaedt_function_handler()
    def add_ground_layer(self, name, material="copper", thickness=0.035, fill_material="air"):
        """Add a new ground layer to the stackup. A ground layer is negative.
        The layer is entirely filled with  metal. Any polygon will draw a void in it.

        Parameters
        ----------
        name : str
            Layer name.
        material : str
            Material name. Material will be parametrized.
        thickness : float
            Thickness value. Thickness will be parametrized.
        fill_material : str
            Fill Material name. Material will be parametrized.

        Returns
        -------
        :class:`pyaedt.modeler.stackup_3d.Layer3D`
            Layer Object.
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

        layer.elevation.expression = previous_layer_end
        if layer.thickness:
            self._end_of_stackup3D.expression = layer.elevation.name + " + " + layer.thickness.name
        else:
            self._end_of_stackup3D.expression = layer.elevation.name

    # if we call this function instantiation of the Layer, the first call, previous_layer_end is "0mm", and
    # layer.position.expression is also "0mm" and self._end_of_stackup becomes the first layer.position + thickness
    # if it has thickness, and so the second call, previous_layer_end is the previous layer position + thickness
    # so the current layer position is the previous_layer_end and the end_of_stackup is the current layer position +
    # thickness, and we just need to call this function after the construction of a layer3D.

    @pyaedt_function_handler()
    def resize(self, percentage_offset):
        """Resize the stackup around objects created by a percentage offset.

        Parameters
        ----------
        percentage_offset : float
            Offset of resize. The value must be greater than 0.

        Returns
        -------
        bool
        """
        list_of_2d_points = []
        list_of_x_coordinates = []
        list_of_y_coordinates = []
        for obj3d in self._object_list:
            points_list_by_object = obj3d.points_on_layer
            list_of_2d_points = points_list_by_object + list_of_2d_points
        for via in self._vias:
            for v in via._vias_objects:
                list_of_x_coordinates.append(v.bounding_box[0] - v.bounding_dimension[0])
                list_of_x_coordinates.append(v.bounding_box[3] - v.bounding_dimension[0])
                list_of_y_coordinates.append(v.bounding_box[1] - v.bounding_dimension[1])
                list_of_y_coordinates.append(v.bounding_box[4] - v.bounding_dimension[1])
                list_of_x_coordinates.append(v.bounding_box[0] + v.bounding_dimension[0])
                list_of_x_coordinates.append(v.bounding_box[4] + v.bounding_dimension[0])
                list_of_y_coordinates.append(v.bounding_box[4] + v.bounding_dimension[1])
                list_of_y_coordinates.append(v.bounding_box[1] + v.bounding_dimension[1])
        for point in list_of_2d_points:
            list_of_x_coordinates.append(point[0])
            list_of_y_coordinates.append(point[1])
        maximum_x = max(list_of_x_coordinates)
        minimum_x = min(list_of_x_coordinates)
        maximum_y = max(list_of_y_coordinates)
        minimum_y = min(list_of_y_coordinates)
        variation_x = abs(maximum_x - minimum_x)
        variation_y = abs(maximum_y - minimum_y)
        self._app["dielectric_x_position"] = str(minimum_x - variation_x * percentage_offset / 100) + "mm"
        self._app["dielectric_y_position"] = str(minimum_y - variation_y * percentage_offset / 100) + "mm"
        self._app["dielectric_length"] = str(maximum_x - minimum_x + 2 * variation_x * percentage_offset / 100) + "mm"
        self._app["dielectric_width"] = str(maximum_y - minimum_y + 2 * variation_y * percentage_offset / 100) + "mm"
        return True


class CommonObject(object):
    """CommonObject Class in Stackup3D."""

    def __init__(self, application):
        self._application = application
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
        """Coordinate system of the object.

        Returns
        -------
        str
        """
        return self._reference_system

    @property
    def dielectric_layer(self):
        """Dielectric layer that the object belongs to.

        Returns
        -------
        :class:`pyaedt.modeler.stackup_3d.Layer3D`
        """
        return self._dielectric_layer

    @property
    def signal_layer(self):
        """Signal layer that the object belongs to.

        Returns
        -------
        :class:`pyaedt.modeler.stackup_3d.Layer3D`
        """
        return self._signal_layer

    @property
    def name(self):
        """Object name.

        Returns
        -------
        str
        """
        return self._name

    @property
    def application(self):
        """App object."""
        return self._application

    @property
    def aedt_object(self):
        """PyAEDT object 3D.

        Returns
        -------
        :class:`pyaedt.modeler.Object3d.Object3d`
        """
        return self._aedt_object

    @property
    def layer_name(self):
        """Layer name.

        Returns
        -------
        str
        """
        return self._layer_name

    @property
    def layer_number(self):
        """Layer ID.

        Returns
        -------
        int
        """
        return self._layer_number

    @property
    def material_name(self):
        """Material name.

        Returns
        -------
        str
        """
        return self._material_name

    @property
    def points_on_layer(self):
        """Object bounding box.

        Returns
        -------
        List
            List of [x,y] coordinate of the bounding box.
        """
        bb = self._aedt_object.bounding_box
        return [[bb[0], bb[1]], [bb[0], bb[4]], [bb[3], bb[4]], [bb[3], bb[1]]]


class Patch(CommonObject, object):
    """Patch Class in Stackup3D."""

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
        reference_system=None,
        axis="X",
    ):
        CommonObject.__init__(self, application)
        self._frequency = NamedVariable(application, patch_name + "_frequency", str(frequency) + "Hz")
        self._signal_layer = signal_layer
        self._dielectric_layer = dielectric_layer
        self._substrate_thickness = dielectric_layer.thickness
        self._width = NamedVariable(application, patch_name + "_width", application.modeler._arg_with_dim(patch_width))
        self._position_x = NamedVariable(
            application, patch_name + "_position_x", application.modeler._arg_with_dim(patch_position_x)
        )
        self._position_y = NamedVariable(
            application, patch_name + "_position_y", application.modeler._arg_with_dim(patch_position_y)
        )
        self._position_z = signal_layer.elevation
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
        except ValueError:
            self._permittivity = NamedVariable(
                application,
                patch_name + "_permittivity",
                float(application.variable_manager[self._dielectric_material.permittivity.value].value),
            )
        if isinstance(patch_length, float) or isinstance(patch_length, int):
            self._length = NamedVariable(
                application, patch_name + "_length", application.modeler._arg_with_dim(patch_length)
            )
            self._effective_permittivity = self._effective_permittivity_calcul
            self._wave_length = self._wave_length_calcul
        elif patch_length is None:
            self._effective_permittivity = self._effective_permittivity_calcul
            self._added_length = self._added_length_calcul
            self._wave_length = self._wave_length_calcul
            self._length = self._length_calcul
        self._impedance_l_w, self._impedance_w_l = self._impedance_calcul
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
                    signal_layer.elevation.name,
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
            self._aedt_object = application.modeler.create_box(
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
            self._aedt_object = application.modeler.create_rectangle(
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
        """Model frequency.

        Returns
        -------
        :class:`pyaedt.modeler.stackup_3d.NamedVariable`
            Variable Object.
        """
        return self._frequency

    @property
    def substrate_thickness(self):
        """Substrate thickness.

        Returns
        -------
        :class:`pyaedt.modeler.stackup_3d.NamedVariable`
            Variable Object.
        """
        return self._substrate_thickness

    @property
    def width(self):
        """Width.

        Returns
        -------
        :class:`pyaedt.modeler.stackup_3d.NamedVariable`
            Variable object.
        """
        return self._width

    @property
    def position_x(self):
        """Starting position X.

        Returns
        -------
        :class:`pyaedt.modeler.stackup_3d.NamedVariable`
            Variable object.
        """
        return self._position_x

    @property
    def position_y(self):
        """Starting position Y.

        Returns
        -------
        :class:`pyaedt.modeler.stackup_3d.NamedVariable`
            Variable object.
        """
        return self._position_y

    @property
    def permittivity(self):
        """Permittivity.

        Returns
        -------
        :class:`pyaedt.modeler.stackup_3d.NamedVariable`
            Variable object.
        """
        return self._permittivity

    @property
    def _permittivity_calcul(self):
        """Permittivity calculation.

        Returns
        -------
        :class:`pyaedt.modeler.stackup_3d.NamedVariable`
            Variable object.
        """
        self._permittivity = self.application.materials[self._dielectric_material].permittivity
        return self._permittivity

    @property
    def effective_permittivity(self):
        """Effective permittivity.

        Returns
        -------
        :class:`pyaedt.modeler.stackup_3d.NamedVariable`
            Variable object.
        """
        return self._effective_permittivity

    @property
    def _effective_permittivity_calcul(self):
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
        """Added length calculation.

        Returns
        -------
        :class:`pyaedt.modeler.stackup_3d.NamedVariable`
            Variable object.
        """
        return self._added_length

    @property
    def _added_length_calcul(self):
        """Added length calculation.

        Returns
        -------
        :class:`pyaedt.modeler.stackup_3d.NamedVariable`
            Variable object.
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
        """Wave length.

        Returns
        -------
        :class:`pyaedt.modeler.stackup_3d.NamedVariable`
            Variable Object.
        """
        return self._wave_length

    @property
    def _wave_length_calcul(self):
        """Wave Length Calutation.

        Returns
        -------
        :class:`pyaedt.modeler.stackup_3d.NamedVariable`
            Variable Object.
        """
        # "c0 * 1000/(patch_frequency * sqrt(patch_eff_permittivity))"
        f = self._frequency.name
        er_e = self._effective_permittivity.name
        patch_wave_length_formula = "c0 * 1000/(" + f + "* sqrt(" + er_e + "))"
        self._wave_length = NamedVariable(
            self.application,
            self._name + "_wave_length",
            self.application.modeler._arg_with_dim(patch_wave_length_formula),
        )
        return self._wave_length

    @property
    def length(self):
        """Length.

        Returns
        -------
        :class:`pyaedt.modeler.stackup_3d.NamedVariable`
            Variable Object.
        """
        return self._length

    @property
    def _length_calcul(self):
        """Length Calutation.

        Returns
        -------
        :class:`pyaedt.modeler.stackup_3d.NamedVariable`
            Variable Object.
        """
        # "patch_wave_length / 2 - 2 * patch_added_length"
        d_l = self._added_length.name
        lbd = self._wave_length.name
        patch_length_formula = lbd + "/2" + " - 2 * " + d_l
        self._length = NamedVariable(self.application, self._name + "_length", patch_length_formula)
        return self._length

    @property
    def impedance(self):
        """Impedance.

        Returns
        -------
        :class:`pyaedt.modeler.stackup_3d.NamedVariable`
            Variable Object.
        """
        return self._impedance_l_w, self._impedance_w_l

    @property
    def _impedance_calcul(self):
        """Impedance Calculation.

        Returns
        -------
        :class:`pyaedt.modeler.stackup_3d.NamedVariable`
            Variable Object.
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


class Trace(CommonObject, object):
    """Provides a class to create a trace in stackup."""

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
        reference_system=None,
        axis="X",
    ):
        CommonObject.__init__(self, application)
        self._frequency = NamedVariable(application, line_name + "_frequency", str(frequency) + "Hz")
        self._signal_layer = signal_layer
        self._dielectric_layer = dielectric_layer
        self._substrate_thickness = dielectric_layer.thickness
        self._position_x = NamedVariable(
            application, line_name + "_position_x", application.modeler._arg_with_dim(line_position_x)
        )
        self._position_y = NamedVariable(
            application, line_name + "_position_y", application.modeler._arg_with_dim(line_position_y)
        )
        self._position_z = signal_layer.elevation
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
        except ValueError:
            self._permittivity = NamedVariable(
                application,
                line_name + "_permittivity",
                float(application.variable_manager[self._dielectric_material.permittivity.value].value),
            )
        if isinstance(line_width, float) or isinstance(line_width, int):
            self._width = NamedVariable(
                application, line_name + "_width", application.modeler._arg_with_dim(line_width)
            )
            self._effective_permittivity = self._effective_permittivity_calcul
            self._wave_length = self._wave_length_calcul
            self._added_length = self._added_length_calcul
            if isinstance(line_electrical_length, float) or isinstance(line_electrical_length, int):
                self._electrical_length = NamedVariable(
                    application, line_name + "_elec_length", str(line_electrical_length)
                )
                self._length = self._length_calcul
            elif isinstance(line_length, float) or isinstance(line_length, int):
                self._length = NamedVariable(
                    application, line_name + "_length", application.modeler._arg_with_dim(line_length)
                )
                self._electrical_length = self._electrical_length_calcul
            else:
                application.logger.error("line_length must be a float.")
            self._charac_impedance_w_h, self._charac_impedance_h_w = self._charac_impedance_calcul
        elif line_width is None:
            self._charac_impedance = NamedVariable(
                self.application, line_name + "_charac_impedance_h_w", str(line_impedance)
            )
            self._width, self._width_h_w = self._width_calcul
            self._effective_permittivity = self._effective_permittivity_calcul
            self._wave_length = self._wave_length_calcul
            self._added_length = self._added_length_calcul
            if isinstance(line_electrical_length, float) or isinstance(line_electrical_length, int):
                self._electrical_length = NamedVariable(
                    application, line_name + "_elec_length", str(line_electrical_length)
                )
                self._length = self._length_calcul
            elif isinstance(line_length, float) or isinstance(line_length, int):
                self._length = NamedVariable(
                    application, line_name + "_length", application.modeler._arg_with_dim(line_length)
                )
                self._electrical_length = self._electrical_length_calcul
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
                    signal_layer.elevation.name,
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
            self._aedt_object = application.modeler.create_box(
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
            self._aedt_object = application.modeler.create_rectangle(
                position=start_point,
                dimension_list=["{}_length".format(self._name), "{}_width".format(self._name)],
                name=line_name,
                matname=signal_layer.material_name,
            )
        application.modeler.set_working_coordinate_system("Global")
        application.modeler.subtract(blank_list=[signal_layer.name], tool_list=[line_name], keepOriginals=True)

    @property
    def frequency(self):
        """Frequency.

        Returns
        -------
        :class:`pyaedt.modeler.stackup_3d.NamedVariable`
            Variable Object.
        """
        return self._frequency

    @property
    def substrate_thickness(self):
        """Substrate Thickness.

        Returns
        -------
        :class:`pyaedt.modeler.stackup_3d.NamedVariable`
            Variable Object.
        """
        return self._substrate_thickness

    @property
    def width(self):
        """Width.

        Returns
        -------
        :class:`pyaedt.modeler.stackup_3d.NamedVariable`
            Variable Object.
        """
        return self._width

    @property
    def width_h_w(self):
        """Width H W.

        Returns
        -------
        :class:`pyaedt.modeler.stackup_3d.NamedVariable`
            Variable Object.
        """
        if self._width_h_w is not None:
            return self._width_h_w

    @property
    def _width_calcul(self):
        """Width calculation.

        Returns
        -------
        :class:`pyaedt.modeler.stackup_3d.NamedVariable`
            Variable Object.
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
        """Starting Position X.

        Returns
        -------
        :class:`pyaedt.modeler.stackup_3d.NamedVariable`
            Variable Object.
        """
        return self._position_x

    @property
    def position_y(self):
        """Starting Position Y.

        Returns
        -------
        :class:`pyaedt.modeler.stackup_3d.NamedVariable`
            Variable Object.
        """
        return self._position_y

    @property
    def permittivity(self):
        """Permittivity.

        Returns
        -------
        :class:`pyaedt.modeler.stackup_3d.NamedVariable`
            Variable Object.
        """
        return self._permittivity

    @property
    def _permittivity_calcul(self):
        """Permittivity Calutation.

        Returns
        -------
        :class:`pyaedt.modeler.stackup_3d.NamedVariable`
            Variable Object.
        """
        self._permittivity = self.application.materials[self._dielectric_material].permittivity
        return self._permittivity

    @property
    def added_length(self):
        """Added Length Calutation.

        Returns
        -------
        :class:`pyaedt.modeler.stackup_3d.NamedVariable`
            Variable Object.
        """
        return self._added_length

    @property
    def _added_length_calcul(self):
        """Added Length Calutation.

        Returns
        -------
        :class:`pyaedt.modeler.stackup_3d.NamedVariable`
            Variable Object.
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
        """Length.

        Returns
        -------
        :class:`pyaedt.modeler.stackup_3d.NamedVariable`
            Variable Object.
        """
        return self._length

    @property
    def _length_calcul(self):
        """Length Calutation.

        Returns
        -------
        :class:`pyaedt.modeler.stackup_3d.NamedVariable`
            Variable Object.
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
        """Characteristic Impedance.

        Returns
        -------
        :class:`pyaedt.modeler.stackup_3d.NamedVariable`
            Variable Object.
        """
        return self._charac_impedance

    @property
    def _charac_impedance_calcul(self):
        """Characteristic Impedance Calutation.

        Returns
        -------
        :class:`pyaedt.modeler.stackup_3d.NamedVariable`
            Variable Object.
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
        """Effective Permittivity.

        Returns
        -------
        :class:`pyaedt.modeler.stackup_3d.NamedVariable`
            Variable Object.
        """
        return self._effective_permittivity

    @property
    def _effective_permittivity_calcul(self):
        """Effective Permittivity Calutation.

        Returns
        -------
        :class:`pyaedt.modeler.stackup_3d.NamedVariable`
            Variable Object.
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
        """Wave Length.

        Returns
        -------
        :class:`pyaedt.modeler.stackup_3d.NamedVariable`
            Variable Object.
        """
        return self._wave_length

    @property
    def _wave_length_calcul(self):
        """Wave Length Calutation.

        Returns
        -------
        :class:`pyaedt.modeler.stackup_3d.NamedVariable`
            Variable Object.
        """
        # "c0 * 1000/(patch_frequency * sqrt(patch_eff_permittivity))"
        # TODO it is currently only available for mm
        f = self._frequency.name
        er_e = self._effective_permittivity.name
        patch_wave_length_formula = "c0 * 1000/(" + f + "* sqrt(" + er_e + "))"
        self._wave_length = NamedVariable(
            self.application,
            self._name + "_wave_length",
            self.application.modeler._arg_with_dim(patch_wave_length_formula),
        )
        return self._wave_length

    @property
    def electrical_length(self):
        """Electrical Length.

        Returns
        -------
        :class:`pyaedt.modeler.stackup_3d.NamedVariable`
            Variable Object.
        """
        return self._electrical_length

    @property
    def _electrical_length_calcul(self):
        """Electrical Length calculation.

        Returns
        -------
        :class:`pyaedt.modeler.stackup_3d.NamedVariable`
            Variable Object.
        """
        lbd = self._wave_length.name
        length = self._length.name
        d_l = self._added_length.name
        elec_length_formula = "360 * (" + length + " + 2 * " + d_l + ")/" + lbd
        self._electrical_length = NamedVariable(self.application, self._name + "_elec_length", elec_length_formula)
        return self._electrical_length

    @pyaedt_function_handler()
    def create_lumped_port(self, reference_layer_name, change_side=False):
        """Create a lumped port on the specified line.

        Parameters
        ----------
        reference_layer_name : str
            Name of the layer on which attach the reference.
        change_side : bool, optional
            Either if apply the port on one direction or the opposite. Default it is on Positive side.

        Returns
        -------
        :class:`pyaedt.modules.Boundary.BoundaryObject`
            Boundary object.
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
        p1 = self.application.create_lumped_port_between_objects(
            reference_layer_name, self.aedt_object.name, axisdir=axisdir
        )
        z_elev = ""
        start_count = False
        for k, v in self._signal_layer._stackup.stackup_layers.items():
            if k == reference_layer_name or k == self._signal_layer.name:
                if not start_count:
                    start_count = True
                else:
                    start_count = False
            elif start_count:
                z_elev += "-" + v.thickness.name
        self.application.modeler.oeditor.ChangeProperty(
            [
                "NAME:AllTabs",
                [
                    "NAME:Geometry3DCmdTab",
                    ["NAME:PropServers", self._name + ":Move:1"],
                    ["NAME:ChangedProps", ["NAME:Move Vector", "X:=", "0mm", "Y:=", "0mm", "Z:=", z_elev]],
                ],
            ]
        )
        return p1


class Polygon(CommonObject, object):
    """Polygon Class in Stackup3D."""

    def __init__(
        self,
        application,
        point_list,
        thickness,
        signal_layer_name,
        poly_name="poly",
        mat_name="copper",
        is_void=False,
        reference_system=None,
    ):
        CommonObject.__init__(self, application)

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
        """Object Bounding Box.

        Returns
        -------
        List
            List of [x,y] coordinate of bounding box.
        """
        bb = self._aedt_object.bounding_box
        return [[bb[0], bb[1]], [bb[0], bb[4]], [bb[3], bb[4]], [bb[3], bb[1]]]
