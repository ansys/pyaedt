from __future__ import absolute_import

from collections import OrderedDict
import os
import re

from pyaedt import pyaedt_function_handler
from pyaedt.generic.general_methods import _uname
from pyaedt.generic.general_methods import read_csv


class ComponentArray(object):
    """Manages object attributes for a 3D component array.

    Parameters
    ----------
    app : :class:`pyaedt.Hfss`
        HFSS PyAEDT object.
    name : str, optional
        Array name. The default value is ``None``.
    props : dict, optional
        Dictionary of properties. The default value is ``None``.

    Examples
    --------
    Basic usage demonstrated with an HFSS design with an existing array:

    >>> from pyaedt import Hfss
    >>> aedtapp = Hfss(projectname="Array.aedt")
    >>> array_names = aedtapp.component_array_names[0]
    >>> array = aedtapp.component_array[array_names[0]]
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

        # Data that cannot be obtained from CSV
        try:
            self._cs_id = props["ArrayDefinition"]["ArrayObject"]["ReferenceCSID"]
        except AttributeError:  # pragma: no cover
            self._cs_id = 1

        self._array_info_path = None

        self._update_cells = True

        if self._app.settings.aedt_version > "2023.2":  # pragma: no cover
            self._array_info_path = self.export_array_info(array_path=None)

        self._cells = None

        self._post_processing_cells = {}

    @property
    def component_names(self):
        """List of component names.

        Returns
        -------
        list
        """
        return self._array_props["component"]

    @property
    def cells(self):
        """List of cell objects.

        Returns
        -------
        list
            List of :class:`pyaedt.modeler.cad.component_array.CellArray`
        """

        if not self._update_cells:
            return self._cells

        if self._app.settings.aedt_version > "2023.2":  # pragma: no cover
            self._array_info_path = self.export_array_info(array_path=None)

        self._cells = [[None for _ in range(self.b_size)] for _ in range(self.a_size)]
        array_props = self._array_props
        component_names = self.component_names
        for row_cell in range(0, self.a_size):
            for col_cell in range(0, self.b_size):
                self._cells[row_cell][col_cell] = CellArray(row_cell, col_cell, array_props, component_names, self)
        return self._cells

    @property
    def name(self):
        """Name of the array.

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
                self._oarray.SetPropValue("Name", array_name)
                self._app.component_array.update({array_name: self})
                self._app.component_array_names = list(self._app.omodelsetup.GetArrayNames())
                del self._app.component_array[self._m_name]
                self._m_name = array_name

        else:  # pragma: no cover
            self._logger.warning("Name %s already assigned in the design", array_name)

    @property
    def post_processing_cells(self):
        """Postprocessing cells.

        Returns
        -------
        dict
           Postprocessing cells of each component.
        """
        if not self._post_processing_cells:
            self._post_processing_cells = {}
            component_info = {}
            row = 1
            for row_info in self.cells[:]:
                col = 1
                for col_info in row_info:
                    name = col_info.component
                    if name not in component_info:
                        component_info[name] = [[row, col]]
                    else:
                        component_info[name].append([row, col])
                    col += 1
                row += 1

            for component_name, component_cells in component_info.items():
                if component_name not in self._post_processing_cells.keys() and component_name is not None:
                    self._post_processing_cells[component_name] = component_cells[0]

        return self._post_processing_cells

    @post_processing_cells.setter
    def post_processing_cells(self, val):
        if isinstance(val, dict):
            self._post_processing_cells = val
            self._edit_array()

        else:  # pragma: no cover
            self._logger.error("Dictionary with component names and cell not correct")

    @property
    def visible(self):
        """Array visibility.

        Returns
        -------
        bool
           Array visibility.
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
           Cell number visibility.
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

    def _render_id(self):
        """Array rendering index.

        Returns
        -------
        int
           Rendering ID.
        """
        render_choices = self.render_choices
        rendex_index = 0
        for choice in render_choices:
            if self.render == choice:
                break
            rendex_index += 1
        return rendex_index

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
    def a_size(self, val):  # pragma: no cover
        # Bug in 2024.1, not possible to change cell count.
        # self._oarray.SetPropValue("A Cell Count", val)
        pass

    @property
    def b_size(self):
        """Number of cells in the vector B direction.

        Returns
        -------
        int
           Number of cells in B direction.
        """
        return int(self._app.get_oo_property_value(self._omodel, self.name, "B Cell Count"))

    @b_size.setter
    def b_size(self, val):  # pragma: no cover
        # Bug in 2024.1, not possible to change cell count.
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
        """Coordinate system name.

        Returns
        -------
        str
           Coordinate system name.
        """
        cs_dict = self._get_coordinate_system_id()
        if self._cs_id not in cs_dict.values():
            self._logger.warning("Coordinate system is not loaded. Save the project.")
            return "Global"
        else:
            return [cs for cs in cs_dict if cs_dict[cs] == self._cs_id][0]

    @coordinate_system.setter
    def coordinate_system(self, name):
        cs_dict = self._get_coordinate_system_id()
        if name not in cs_dict.keys():
            self._logger.warning("Coordinate system is not loaded. Save the project.")
        else:
            self._cs_id = cs_dict[name]
            self._edit_array()

    @property
    def _array_props(self):
        """Ordered dictionary of the properties of the component array.

        Returns
        -------
        dict
           An ordered dictionary of the properties of the component array.
        """
        return self.get_array_props()

    @pyaedt_function_handler()
    def delete(self):
        """Delete the component array.

        References
        ----------

        >>> oModule.DeleteArray

        """
        self._app.omodelsetup.DeleteArray()
        del self._app.component_array[self.name]
        self._app.component_array_names = list(self._app.get_oo_name(self._app.odesign, "Model"))

    @pyaedt_function_handler()
    def export_array_info(self, array_path=None):
        """Export array information to a CSV file.

        Returns
        -------
        str
           Path of the CSV file.

        References
        ----------

        >>> oModule.ExportArray

        """
        if self._app.settings.aedt_version < "2024.1":  # pragma: no cover
            self._logger.warning("This feature is not available in {}.".format(str(self._app.settings.aedt_version)))
            return False

        if not array_path:  # pragma: no cover
            array_path = os.path.join(self._app.toolkit_directory, "array_info.csv")
        self._app.omodelsetup.ExportArray(self.name, array_path)
        return array_path

    @pyaedt_function_handler()
    def get_array_props(self):
        """Retrieve the properties of the component array.

        Returns
        -------
        dict
           Ordered dictionary of the properties of the component array.
        """
        # From 2024R1, array information can be loaded from a CSV
        if self._array_info_path and os.path.exists(self._array_info_path):  # pragma: no cover
            array_props = self.array_info_parser(self._array_info_path)
        else:
            self._app.save_project()
            array_props = self._get_array_info_from_aedt()
        return array_props

    @pyaedt_function_handler()
    def array_info_parser(self, array_path):  # pragma: no cover
        """Parse component array information from the CSV file.

        Parameters
        ----------
        array_path : str
             Name of the CSV file.

        Returns
        -------
        dict
           Ordered dictionary of the properties of the component array.

        Examples
        --------
        >>> from pyaedt import Hfss
        >>> aedtapp = Hfss(projectname="Array.aedt")
        >>> array_names = aedtapp.component_array_names[0]
        >>> array = aedtapp.component_array[array_names[0]]
        >>> array_csv = array.export_array_info()
        >>> array_info = array.array_info_parser(array_csv)
        """

        info = read_csv(array_path)
        if not info:
            self._logger.error("Data from CSV file is not loaded.")
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

        # Array matrix
        start_str = ["Array", "Format: Component_index:Rotation_angle:Active_or_Passive"]
        capture_data = False

        for el in info[line_cont + 1 :]:
            if capture_data:
                el = el[:-1]
                component_index = []
                rotation = []
                active_passive = []

                for row in el:
                    split_elements = row.split(":")

                    # Check for non-empty strings
                    if split_elements[0]:
                        component_index.append(int(split_elements[0]))
                    else:
                        component_index.append(-1)

                    # Some elements might not have the rotation and active/passive status, so we check for their
                    # existence
                    if split_elements[0] and len(split_elements) > 1:
                        string_part = re.findall("[a-zA-Z]+", split_elements[1])
                        if string_part and string_part[0] == "deg":
                            rot = re.findall(r"[+-]?\d+\.\d+", split_elements[1])
                            rotation.append(int(float(rot[0])))
                            if len(split_elements) > 2:
                                if split_elements[2] == "0":
                                    active_passive.append(False)
                                else:
                                    active_passive.append(True)
                            else:
                                active_passive.append(True)
                        else:
                            active_passive.append(False)
                            rotation.append(0)
                    elif split_elements[0]:
                        active_passive.append(True)
                        rotation.append(0)
                    else:
                        active_passive.append(False)
                        rotation.append(0)

                array_matrix.append(component_index)
                array_matrix_rotation.append(rotation)
                array_matrix_active.append(active_passive)
            if el == start_str:
                capture_data = True

        array_info["component"] = components
        array_info["active"] = array_matrix_active
        array_info["rotation"] = array_matrix_rotation
        array_info["cells"] = array_matrix
        return array_info

    @pyaedt_function_handler()
    def _edit_array(self):
        """Edit component array.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed

        References
        ----------

        >>> oModule.EditArray
        """

        args = [
            "NAME:" + self.name,
            "Name:=",
            self.name,
            "UseAirObjects:=",
            True,
            "RowPrimaryBnd:=",
            self.a_vector_name,
            "ColumnPrimaryBnd:=",
            self.b_vector_name,
            "RowDimension:=",
            self.a_size,
            "ColumnDimension:=",
            self.b_size,
            "Visible:=",
            self.visible,
            "ShowCellNumber:=",
            self.show_cell_number,
            "RenderType:=",
            self._render_id(),
            "Padding:=",
            self.padding_cells,
            "ReferenceCSID:=",
            self._cs_id,
        ]

        cells = ["NAME:Cells"]
        component_info = {}
        row = 1
        for row_info in self.cells[:]:
            col = 1
            for col_info in row_info:
                name = col_info.component
                if name not in component_info:
                    component_info[name] = [[row, col]]
                else:
                    component_info[name].append([row, col])
                col += 1
            row += 1

        for component_name, component_cells in component_info.items():
            if component_name:
                cells.append(component_name + ":=")
                component_cells_str = [str(item) for item in component_cells]
                component_cells_str = ", ".join(component_cells_str)
                cells.append([component_cells_str])

        rotations = ["NAME:Rotation"]
        component_rotation = {}
        row = 1
        for row_info in self.cells[:]:
            col = 1
            for col_info in row_info:
                if float(col_info.rotation) != 0.0:
                    if col_info.rotation not in component_rotation:
                        component_rotation[col_info.rotation] = [[row, col]]
                    else:
                        component_rotation[col_info.rotation].append([row, col])
                col += 1
            row += 1

        for rotation, rotation_cells in component_rotation.items():
            rotations.append(str(rotation) + " deg:=")
            component_cells_str = [str(item) for item in rotation_cells]
            component_cells_str = ", ".join(component_cells_str)
            rotations.append([component_cells_str])

        args.append(cells)
        args.append(rotations)

        args.append("Active:=")

        component_active = []
        row = 1
        for row_info in self.cells[:]:
            col = 1
            for col_info in row_info:
                if col_info.is_active:
                    component_active.append([row, col])
                col += 1
            row += 1

        if component_active:
            component_active_str = [str(item) for item in component_active]
            args.append(", ".join(component_active_str))
        else:
            args.append("All")

        post = ["NAME:PostProcessingCells"]
        for post_processing_cell in self.post_processing_cells:
            post.append(post_processing_cell + ":=")
            row = self.post_processing_cells[post_processing_cell][0]
            col = self.post_processing_cells[post_processing_cell][1]
            post.append([str(row), str(col)])
        args.append(post)
        args.append("Colors:=")
        col = []
        args.append(col)
        self._app.omodelsetup.EditArray(args)

        return True

    @pyaedt_function_handler()
    def get_cell(self, row, col):
        """Get cell object corresponding to a row and column.

        Returns
        -------
        :class:`pyaedt.modeler.cad.component_array.CellArray`

        """
        if row > self.a_size or col > self.b_size:
            self._logger.error("Specified cell does not exist.")
            return False
        if row <= 0 or col <= 0:
            self._logger.error("Row and column index start with ``1``.")
            return False
        return self.cells[row - 1][col - 1]

    @pyaedt_function_handler()
    def lattice_vector(self):
        """Get model lattice vector.

        Returns
        -------
        list
            List of starting point coordinates paired with ending point coordinates.
        References
        ----------
        >>> oModule.GetLatticeVectors()

        """
        return self._app.omodelsetup.GetLatticeVectors()

    @pyaedt_function_handler()
    def _get_array_info_from_aedt(self):
        """Get array properties from an AEDT file.

        Returns
        -------
        dict
            Ordered dictionary of the properties of the component array.

        """
        props = self._app.design_properties
        component_id = {}
        user_defined_models = props["ModelSetup"]["GeometryCore"]["GeometryOperations"]["UserDefinedModels"][
            "UserDefinedModel"
        ]
        if not isinstance(user_defined_models, list):
            user_defined_models = [user_defined_models]
        for component_defined in user_defined_models:
            component_id[component_defined["ID"]] = component_defined["Attributes"]["Name"]

        components_map = props["ArrayDefinition"]["ArrayObject"]["ComponentMap"]
        components = [None] * len(components_map)
        for comp in props["ArrayDefinition"]["ArrayObject"]["ComponentMap"]:
            key, value = comp.split("=")
            key = int(key.strip("'"))
            value = int(value)
            components[key - 1] = component_id[value]
        array_props = OrderedDict()
        array_props["component"] = components
        array_props["active"] = props["ArrayDefinition"]["ArrayObject"]["Active"]["matrix"]
        array_props["rotation"] = props["ArrayDefinition"]["ArrayObject"]["Rotation"]["matrix"]
        array_props["cells"] = props["ArrayDefinition"]["ArrayObject"]["Cells"]["matrix"]
        return array_props

    @pyaedt_function_handler()
    def _get_coordinate_system_id(self):
        """Get the coordinate system ID.

        Returns
        -------
        int
            Coordinate system ID.
        """
        id2name = {1: "Global"}
        name2id = id2name
        if self._app.design_properties and "ModelSetup" in self._app.design_properties:  # pragma: no cover
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
                except AttributeError:
                    pass
            name2id = {v: k for k, v in id2name.items()}
        return name2id


class CellArray(object):
    """Manages object attributes for a 3D component and a user-defined model.

    Parameters
    ----------
    row : int
        Row index of the cell.
    col : int
        Column index of the cell.
    array_props : dict
        Dictionary containing the properties of the array.
    component_names : list
        List of component names in the array.
    array_obj : class:`pyaedt.modeler.cad.component_array.ComponentArray`
        Instance of the array containing the cell.

    """

    def __init__(self, row, col, array_props, component_names, array_obj):
        self.row = row + 1
        self.col = col + 1
        self._array_obj = array_obj
        self._cell_props = OrderedDict(
            {
                "component": array_props["cells"][row][col],
                "active": array_props["active"][row][col],
                "rotation": array_props["rotation"][row][col],
            }
        )
        self._rotation = self._cell_props["rotation"]
        self._is_active = self._cell_props["active"]

        component_index = self._cell_props["component"]
        if component_index == -1:
            self._component = None
        else:
            self._component = component_names[component_index - 1]

    @property
    def rotation(self):
        """Rotation value of the cell object.

        Returns
        -------
        int
        """
        return self._rotation

    @rotation.setter
    def rotation(self, val):
        if val in [0, 90, 180, 270]:
            self._rotation = val
            self._array_obj._update_cells = False
            self._array_obj._edit_array()
            self._array_obj._update_cells = True
        else:
            self._array_obj._logger.error("Rotation must be an integer. 0, 90, 180, and 270 degrees are available.")

    @property
    def component(self):
        """Component name of the cell object.

        Returns
        -------
        str
        """
        return self._component

    @component.setter
    def component(self, val):
        self._array_obj._update_cells = False
        if val in self._array_obj.component_names or val is None:
            if val is None:
                for post_processing_cell in self._array_obj.post_processing_cells:
                    if (
                        self._array_obj.post_processing_cells[post_processing_cell][0] == self.row
                        and self._array_obj.post_processing_cells[post_processing_cell][1] == self.col
                    ):
                        flat_cell_list = [item for sublist in self._array_obj.cells for item in sublist]
                        for cell in flat_cell_list:
                            if cell.component == self.component and cell.col != self.col or cell.row != self.row:
                                self._array_obj.post_processing_cells[self.component] = [cell.row, cell.col]
                                break
                        break
            self._component = val
            self._array_obj._edit_array()
            self._array_obj._update_cells = True
        else:  # pragma: no cover
            self._array_obj._logger.error("Component must be defined.")

    @property
    def is_active(self):
        """Flag indicating if the cell object is active or passive.

        Returns
        -------
        bool
        """
        return self._is_active

    @is_active.setter
    def is_active(self, val):
        if isinstance(val, bool):
            self._is_active = val
            self._array_obj._update_cells = False
            self._array_obj._edit_array()
            self._array_obj._update_cells = True
        else:
            self._array_obj._logger.error("Only Boolean type is allowed.")
