from __future__ import absolute_import

from collections import OrderedDict
import os

from pyaedt import pyaedt_function_handler
from pyaedt.generic.general_methods import _uname
from pyaedt.generic.general_methods import read_csv
from pyaedt.modeler.geometry_operators import GeometryOperators as go


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

    def __init__(self, app, name=None, props=None):
        if name:
            self._m_name = name
        else:
            self._m_name = _uname("Array_")

        self._app = app

        self._logger = app.logger

        self._omodel = self._app.get_oo_object(self._app.odesign, "Model")

        self._oarray = self._app.get_oo_object(self._omodel, name)

        # Data that can not be obtained from CSV

        self._cs_id = props["ReferenceCSID"]

        self._array_info_path = None
        self._array_props = None
        if self._app.settings.aedt_version > "2023.2":
            self.export_array_info(array_path=None)
            self._array_info_path = os.path.join(self._app.toolkit_directory, "array_info.csv")

        if self._array_info_path and os.path.exists(self._array_info_path):
            self._array_props = self.array_info_parser(self._array_info_path)

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
           Name of the array.
        """
        return self._m_name

    @name.setter
    def name(self, array_name):
        if array_name not in self._app.component_array_names:
            if array_name != self._m_name:
                if self._app.settings.aedt_version < "2024.2":
                    self._logger.warning("Array rename it is not possible on this AEDT version.")
                else:  # pragma: no cover
                    self._oarray.SetPropValue("Name", array_name)
                    # self._change_array_property("Name", array_name)
                    self._app.component_array.update({array_name: self})
                    self._app.component_array_names = list(self._app.omodelsetup.GetArrayNames())
                    self._m_name = array_name
        else:  # pragma: no cover
            self._logger.warning("Name %s already assigned in the design", array_name)

    @property
    def visible(self):
        """Array visibility.

        Returns
        -------
        bool
           ``True`` if property is checked.
        """
        return self._app.get_oo_property_value(self._omodel, self.name, "Visible")

    @visible.setter
    def visible(self, val):
        self._oarray.SetPropValue("Visible", val)

    @property
    def show_cell_number(self):
        """Show array cell number.

        Returns
        -------
        bool
           ``True`` if property is checked.
        """
        return self._app.get_oo_property_value(self._omodel, self.name, "Show Cell Number")

    @show_cell_number.setter
    def show_cell_number(self, val):
        self._oarray.SetPropValue("Show Cell Number", val)

    @property
    def render_choices(self):
        """Render name choices.

        Returns
        -------
        list
           Render names.
        """
        return list(self._oarray.GetPropValue("Render/Choices"))

    @property
    def render(self):
        """Array rendering.

        Returns
        -------
        str
           Rendering type.
        """
        return self._app.get_oo_property_value(self._omodel, self.name, "Render")

    @render.setter
    def render(self, val):
        if val not in self.render_choices:
            self._logger.warning("Render value not available")
        else:
            self._oarray.SetPropValue("Render", val)

    @property
    def a_vector_choices(self):
        """A vector name choices.

        Returns
        -------
        list
           Lattice vector names.
        """
        return list(self._app.get_oo_property_value(self._omodel, self.name, "A Vector/Choices"))

    @property
    def b_vector_choices(self):
        """B vector name choices.

        Returns
        -------
        list
           Lattice vector names.
        """
        return list(self._app.get_oo_property_value(self._omodel, self.name, "B Vector/Choices"))

    @property
    def a_vector_name(self):
        """A vector name.

        Returns
        -------
        str
           Lattice vector name.
        """
        return self._app.get_oo_property_value(self._omodel, self.name, "A Vector")

    @a_vector_name.setter
    def a_vector_name(self, val):
        if val in self.a_vector_choices:
            self._oarray.SetPropValue("A Vector", val)
        else:
            self._logger.warning("A vector name not available")

    @property
    def b_vector_name(self):
        """B vector name.

        Returns
        -------
        str
           Lattice vector name.
        """
        return self._oarray.GetPropValue("B Vector")

    @b_vector_name.setter
    def b_vector_name(self, val):
        if val in self.b_vector_choices:
            self._oarray.SetPropValue("B Vector", val)
        else:
            self._logger.warning("B vector name not available")

    @property
    def a_size(self):
        """A cell count.

        Returns
        -------
        int
           Number of cells in A direction.
        """
        return int(self._app.get_oo_property_value(self._omodel, self.name, "A Cell Count"))

    @a_size.setter
    def a_size(self, val):
        # self._oarray.SetPropValue("A Cell Count", val)
        pass

    @property
    def b_size(self):
        """B cell count.

        Returns
        -------
        int
           Number of cells in B direction.
        """
        return int(self._app.get_oo_property_value(self._omodel, self.name, "B Cell Count"))

    @b_size.setter
    def b_size(self, val):
        # self._oarray.SetPropValue("B Cell Count", val)
        pass

    @property
    def padding_cells(self):
        """Number of padding cells.

        Returns
        -------
        int
           Number of padding cells.
        """
        return int(self._app.get_oo_property_value(self._omodel, self.name, "Padding"))

    @padding_cells.setter
    def padding_cells(self, val):
        self._oarray.SetPropValue("Padding", val)

    @property
    def coordinate_system(self):
        """Coordinate system.

        Returns
        -------
        str
           Coordinate system name.
        """
        cs_dict = self._get_coordinate_system_id()
        if self._cs_id not in cs_dict.values():
            self._logger.warning("Coordinate system is not loaded, please save the project.")
            return "Global"
        else:
            return [cs for cs in cs_dict if cs_dict[cs] == self._cs_id][0]

    @coordinate_system.setter
    def coordinate_system(self, name):
        cs_dict = self._get_coordinate_system_id()
        if name not in cs_dict.keys():
            self._logger.warning("Coordinate system is not loaded, please save the project.")
        else:
            self._cs_id = cs_dict[name]

    @pyaedt_function_handler()
    def delete(self):
        """Delete the object.

        References
        ----------

        >>> oModule.DeleteArray

        """
        self._app.omodelsetup.DeleteArray()
        del self._app.component_array[self.name]
        self._app.component_array_names = list(self._app.get_oo_name(self._app.odesign, "Model"))

    @pyaedt_function_handler()
    def export_array_info(self, array_path=None):
        """Export array information to CSV file.

        References
        ----------

        >>> oModule.ExportArray

        """
        if not array_path:
            array_path = os.path.join(self._app.toolkit_directory, "array_info.csv")
        self._app.omodelsetup.ExportArray(self.name, array_path)
        return True

    @pyaedt_function_handler()
    def array_info_parser(self, array_path):
        """Parse array information CSV file.

        References
        ----------

        >>> oModule.ExportArray

        """
        info = read_csv(array_path)
        if not info:
            self._logger.error("Data from CSV not loaded.")
            return False

        array_info = OrderedDict()
        components = []
        array_matrix = []
        array_matrix_rotation = []
        array_matrix_active = []

        # Components
        start_str = ["Component Index", "Component Name"]
        end_str = ["Source Row", "Source Column", "Source Name", "Magnitude", "Phase"]

        capture_data = False
        line_cont = 0
        for el in info:
            if el == end_str:
                break
            if capture_data:
                components.append(el[1])
            if el == start_str:
                capture_data = True
            line_cont += 1
        array_info["components"] = components

        # Array matrix
        start_str = ["Array", "Format: Component_index:Rotation_angle:Active_or_Passive"]
        capture_data = False
        row = []
        for el in info[line_cont + 1 :]:
            if el == end_str:
                break
            if capture_data:
                component_index = []
                rotation = []
                active_passive = []

                for element in el:
                    split_elements = element.split(":")

                    # Check for non-empty strings
                    if split_elements[0]:
                        component_index.append(int(split_elements[0]))

                    # Some elements might not have the rotation and active/passive status, so we check for their
                    # existence
                    if len(split_elements) > 1:
                        rot = go.parse_dim_arg(split_elements[1])
                        rotation.append(int(rot))
                    else:
                        rotation.append(0)

                    if len(split_elements) > 2:
                        if split_elements[2] == 0:
                            active_passive.append(True)
                        else:
                            active_passive.append(False)
                    else:
                        active_passive.append(True)

                array_matrix.append(component_index)
                array_matrix_rotation.append(rotation)
                array_matrix_active.append(active_passive)

            if el == start_str:
                capture_data = True
        return True

    @pyaedt_function_handler()
    def _get_coordinate_system_id(self):
        id2name = {1: "Global"}
        name2id = id2name
        if self._app.design_properties and "ModelSetup" in self._app.design_properties:
            cs = self._app.design_properties["ModelSetup"]["GeometryCore"]["GeometryOperations"]["CoordinateSystems"]
            for ds in cs:
                try:
                    if isinstance(cs[ds], (OrderedDict, dict)):
                        name = cs[ds]["Attributes"]["Name"]
                        cs_id = cs[ds]["ID"]
                        id2name[cs_id] = name
                    elif isinstance(cs[ds], list):
                        for el in cs[ds]:
                            name = el["Attributes"]["Name"]
                            cs_id = el["ID"]
                            id2name[cs_id] = name
                except:
                    pass
            name2id = {v: k for k, v in id2name.items()}
        return name2id

    # @pyaedt_function_handler()
    # def _change_array_property(self, prop_name, value):
    #     # names = self._app.modeler.convert_to_selections(value, True)
    #     vChangedProp = ["NAME:ChangedProps", ["NAME:" + prop_name, "Value:=", value]]
    #     vPropServer = ["NAME:PropServers", "ModelSetup:" + self.name]
    #
    #     vGeo3d = ["NAME:HfssTab", vPropServer, vChangedProp]
    #     vOut = ["NAME:AllTabs", vGeo3d]
    #
    #     self._app.odesign.ChangeProperty(vOut)
    #     return True

    # @pyaedt_function_handler()
    # def _get_args(self, props=None):
    #     if props is None:
    #         props = self.props
    #     arg = ["NAME:" + self.name]
    #     _dict2arg(props, arg)
    #     return arg

    # @pyaedt_function_handler()
    # def _update_props(self, d, u):
    #     for k, v in u.items():
    #         if isinstance(v, (dict, OrderedDict)):
    #             if k not in d:
    #                 d[k] = OrderedDict({})
    #             d[k] = self._update_props(d[k], v)
    #         else:
    #             d[k] = v
    #     return d
