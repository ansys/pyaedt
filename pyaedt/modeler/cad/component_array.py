from __future__ import absolute_import

from collections import OrderedDict

from pyaedt import pyaedt_function_handler
from pyaedt.generic.general_methods import _uname
from pyaedt.modeler.cad.elements3d import _dict2arg


class ComponentArrayProps(OrderedDict):
    """User Defined Component Internal Parameters."""

    def __setitem__(self, key, value):
        OrderedDict.__setitem__(self, key, value)
        if self._pyaedt_user_defined_component.auto_update:
            res = self._pyaedt_user_defined_component.update_native()
            if not res:
                self._pyaedt_user_defined_component._logger.warning("Update of %s failed. Check needed arguments", key)

    def __init__(self, user_defined_components, props):
        OrderedDict.__init__(self)
        if props:
            for key, value in props.items():
                if isinstance(value, (dict, OrderedDict)):
                    OrderedDict.__setitem__(self, key, ComponentArrayProps(user_defined_components, value))
                else:
                    OrderedDict.__setitem__(self, key, value)
        self._pyaedt_user_defined_component = user_defined_components

    def _setitem_without_update(self, key, value):
        OrderedDict.__setitem__(self, key, value)


class ComponentArray(object):
    """Manages object attributes for 3DComponent and User Defined Model.

    Parameters
    ----------
    primitives : :class:`pyaedt.modeler.Primitives3D.Primitives3D`
        Inherited parent object.
    name : str, optional
        Name of the component. The default value is ``None``.
    props : dict, optional
        Dictionary of properties. The default value is ``None``.
    component_type : str, optional
        Type of the component. The default value is ``None``.

    Examples
    --------
    Basic usage demonstrated with an HFSS design:

    >>> from pyaedt import Hfss
    >>> aedtapp = Hfss()
    >>> prim = aedtapp.modeler.user_defined_components

    Obtain user defined component names, to return a :class:`pyaedt.modeler.cad.components_3d.UserDefinedComponent`.

    >>> component_names = aedtapp.modeler.user_defined_components
    >>> component = aedtapp.modeler[component_names["3DC_Cell_Radome_In1"]]
    """

    def __init__(self, name=None, props=None):
        if name:
            self._m_name = name
        else:
            self._m_name = _uname("Array_")

        self._visible = None

        self._show_cell_number = None

        self._render = None

        self._a_vector_name = None

        self._b_vector_name = None

        self._a_size = None

        self._b_size = None

        self._padding_cells = None

        self._coordinate_system = None

        # Everything inside components ?
        self._component_names = None

        self.components = None

        self._component_colors = None

        # Each component should also has the list of cells

        self.cells = []
        # self.cells[0][0] = {"component": x,
        #                     "rotation": False,
        #                     "active": True,
        #                     }

        self.postprocessing_cell = {}

        # Methods

        # Create array airbox and update  array airbox
        # Delete array
        # GetLatticeVector

    @property
    def name(self):
        """Name of the object.

        Returns
        -------
        str
           Name of the object.

        References
        ----------

        >>> oEditor.GetPropertyValue
        >>> oEditor.ChangeProperty

        """
        return self._m_name

    @name.setter
    def name(self, component_name):
        if component_name not in self._primitives.user_defined_component_names + self._primitives.object_names + list(
            self._primitives.oeditor.Get3DComponentDefinitionNames()
        ):
            if component_name != self._m_name:
                pcs = ["NAME:Name", "Value:=", component_name]
                self._change_property(pcs)
                self._primitives.user_defined_components.update({component_name: self})
                del self._primitives.user_defined_components[self._m_name]
                self._project_dictionary = None
                self._m_name = component_name
        else:  # pragma: no cover
            self._logger.warning("Name %s already assigned in the design", component_name)

    @property
    def target_coordinate_system(self):
        """Target coordinate system.

        Returns
        -------
        str
            Name of the target coordinate system.

        References
        ----------

        >>> oEditor.GetPropertyValue
        >>> oEditor.ChangeProperty

        """
        self._target_coordinate_system = None
        if "Target Coordinate System" in self._primitives.oeditor.GetChildObject(self.name).GetPropNames():
            tCS = self._primitives.oeditor.GetChildObject(self.name).GetPropValue("Target Coordinate System")
            self._target_coordinate_system = tCS
        return self._target_coordinate_system

    @target_coordinate_system.setter
    def target_coordinate_system(self, tCS):
        if (
            "Target Coordinate System" in self._primitives.oeditor.GetChildObject(self.name).GetPropNames()
            and "Target Coordinate System/Choices" in self._primitives.oeditor.GetChildObject(self.name).GetPropNames()
        ):
            tCS_options = list(
                self._primitives.oeditor.GetChildObject(self.name).GetPropValue("Target Coordinate System/Choices")
            )
            if tCS in tCS_options:
                pcs = ["NAME:Target Coordinate System", "Value:=", tCS]
                self._change_property(pcs)
                self._target_coordinate_system = tCS

    @pyaedt_function_handler()
    def delete(self):
        """Delete the object. The project must be saved after the operation to update the list
        of names for user-defined components.

        References
        ----------

        >>> oEditor.Delete

        Examples
        --------

        >>> from pyaedt import hfss
        >>> hfss = Hfss()
        >>> hfss.modeler["UDM"].delete()
        >>> hfss.save_project()
        >>> hfss._project_dictionary = None
        >>> udc = hfss.modeler.user_defined_component_names

        """
        arg = ["NAME:Selections", "Selections:=", self._m_name]
        self._m_Editor.Delete(arg)
        del self._primitives.modeler.user_defined_components[self.name]
        self._primitives.cleanup_objects()
        self.__dict__ = {}

    @property
    def bounding_box(self):
        """Get bounding dimension of a user defined model.

        Returns
        -------
        list
            List of floats containing [x_min, y_min, z_min, x_max, y_max, z_max].

        """
        bb = [float("inf")] * 3 + [float("-inf")] * 3
        for _, obj in self.parts.items():
            bbox = obj.bounding_box
            bb = [min(bb[i], bbox[i]) for i in range(3)] + [max(bb[i + 3], bbox[i + 3]) for i in range(3)]
        return bb

    @property
    def center(self):
        """Get center coordinates of a user defined model.

        Returns
        -------
        list
            List of floats containing [x_center, y_center, z_center].

        """
        x_min, y_min, z_min, x_max, y_max, z_max = self.bounding_box
        x_center = (x_min + x_max) / 2
        y_center = (y_min + y_max) / 2
        z_center = (z_min + z_max) / 2
        return [x_center, y_center, z_center]

    @property
    def _logger(self):
        """Logger."""
        return self._primitives.logger

    @pyaedt_function_handler()
    def _get_args(self, props=None):
        if props is None:
            props = self.props
        arg = ["NAME:" + self.name]
        _dict2arg(props, arg)
        return arg

    @pyaedt_function_handler()
    def _update_props(self, d, u):
        for k, v in u.items():
            if isinstance(v, (dict, OrderedDict)):
                if k not in d:
                    d[k] = OrderedDict({})
                d[k] = self._update_props(d[k], v)
            else:
                d[k] = v
        return d

    @property
    def _m_Editor(self):
        """Pointer to the oEditor object in the AEDT API. This property is
        intended primarily to be used by FacePrimitive, EdgePrimitive, and
        VertexPrimitive child objects.

        Returns
        -------
        oEditor COM Object

        """
        return self._primitives.oeditor

    @pyaedt_function_handler()
    def get_component_filepath(self):
        """Get 3d component file path.

        Returns
        -------
        str
            Path of the 3d component file.
        """

        return self._primitives._app.get_oo_object(self._primitives._app.oeditor, self.definition_name).GetPropValue(
            "3D Component File Path"
        )

    @pyaedt_function_handler()
    def update_definition(self, password="", new_filepath=""):
        """Update 3d component definition.

        Parameters
        ----------
        password : str, optional
            Password for encrypted models. The default value is ``""``.
        new_filepath : str, optional
            New path containing the 3d component file. The default value is ``""``, which means
            that the 3d component file has not changed.

        Returns
        -------
        bool
            True if successful.
        """

        self._primitives._app.oeditor.UpdateComponentDefinition(
            [
                "NAME:UpdateDefinitionData",
                "ForLocalEdit:=",
                False,
                "DefinitionNames:=",
                self.definition_name,
                "Passwords:=",
                [password],
                "NewFilePath:=",
                new_filepath,
            ]
        )
        self._primitives._app.modeler.refresh_all_ids()
        return True
