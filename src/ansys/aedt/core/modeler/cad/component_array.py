# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 - 2026 Synopsys, Inc. and ANSYS, Inc. All rights reserved.
# SPDX-License-Identifier: MIT
#
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

from __future__ import annotations

import ast
import os
import re
from typing import TYPE_CHECKING

from ansys.aedt.core.base import PyAedtBase
from ansys.aedt.core.generic.constants import AEDT_UNITS
from ansys.aedt.core.generic.file_utils import _uname
from ansys.aedt.core.generic.file_utils import generate_unique_name
from ansys.aedt.core.generic.file_utils import read_csv
from ansys.aedt.core.generic.general_methods import pyaedt_function_handler

if TYPE_CHECKING:
    from ansys.aedt.core.hfss import Hfss
from ansys.aedt.core.application import _get_obj_data
from ansys.aedt.core.application import _has_get_obj_data
from ansys.aedt.core.generic.props import Props as ComponentArrayProps
from ansys.aedt.core.internal.checks import min_aedt_version
from ansys.aedt.core.internal.errors import AEDTRuntimeError


class ComponentArray(PyAedtBase):
    """Manages object attributes for a 3D component array.

    Parameters
    ----------
    app : :class:`ansys.aedt.core.Hfss`
        HFSS PyAEDT object.
    name : str, optional
        Array name. The default is ``None``, in which case a random name is assigned.

    Examples
    --------
    >>> from ansys.aedt.core import Hfss
    >>> aedtapp = Hfss(project="Array.aedt")
    >>> array_names = aedtapp.component_array_names[0]
    >>> array_comp = aedtapp.component_array[array_names[0]]

    """

    def __init__(self, app: Hfss, name: str | None = None) -> None:
        # Public attributes
        self.update_cells = True

        # Private attributes
        self._app = app
        if name is None:
            name = _uname("Array_")
        self._name = name

        self._legacy_props = {}

        self.__child_object = None

        # GetObjData is available for some objects in 2026R1
        self._has_getobject = _has_get_obj_data(self.child_object)

        if self._app.desktop_class.aedt_version > "2023.2" and not self._has_getobject:  # pragma: no cover
            # Leverage csv file if possible
            self.export_array_info(output_file=None)
            self._array_info_path = os.path.join(self._app.toolkit_directory, "array_info.csv")
        elif not self._has_getobject:  # pragma: no cover
            self._app.save_project()
            self._array_info_path = None

        if "Coordinate_System" not in dir(self.child_object):  # pragma: no cover
            # Data that cannot be obtained from CSV
            array_definition = app.design_properties.get("ArrayDefinition", {})
            array_object = array_definition.get("ArrayObject", {}) or array_definition.get("ArrayObjects", {})
            if array_object and isinstance(array_object, dict):
                array_object = array_object.get(name, {})
            references_csid = array_object.get("ReferenceCSID") or array_object.get("ReferenceCS")
            if references_csid:
                self.__cs_id = references_csid
            else:
                self.__cs_id = 1

        self.__cells = None
        self.__post_processing_cells = {}

    def __getitem__(self, key):
        """Get cell object corresponding to a key (row, column).

        Parameters
        ----------
        key : tuple(int,int)
            Row and column associated to the cell.

        Returns
        -------
        :class:`ansys.aedt.core.modeler.cad.component_array.CellArray`
        """
        if key[0] > self.a_size or key[1] > self.b_size:
            self._app.logger.error("Specified cell does not exist.")
            return False

        if key[0] <= 0 or key[1] <= 0:
            self._app.logger.error("Row and column index start with ``1``.")
            return False

        return self.cells[key[0] - 1][key[1] - 1]

    @property
    def child_object(self):
        """Object-oriented properties.

        Returns
        -------
        AEDT object if any or `None`.

        Examples
        --------
        >>> from ansys.aedt.core import Hfss
        >>> aedtapp = Hfss()
        >>> array_names = aedtapp.component_array_names[0]
        >>> array_comp = aedtapp.component_array[array_names[0]]
        >>> array_comp.child_object.GetChildNames()

        """
        if not self.__child_object:
            design_childs = self._app.get_oo_name(self._app.odesign)

            if "Model" in design_childs:
                cc = self._app.get_oo_object(self._app.odesign, "Model")
                cc_names = self._app.get_oo_name(cc)
                if self._name in cc_names:
                    self.__child_object = self._app.get_oo_object(cc, self._name)
        return self.__child_object

    @property
    @min_aedt_version("2026.1")
    def props(self) -> ComponentArrayProps:
        """Properties of the setup.

        Examples
        --------
        >>> from ansys.aedt.core import Hfss
        >>> aedtapp = Hfss()
        >>> array_names = aedtapp.component_array_names[0]
        >>> array_comp = aedtapp.component_array[array_names[0]]
        >>> array_comp.props

        """
        if self._has_getobject:
            self._legacy_props = _get_obj_data(self.child_object)
        return ComponentArrayProps(self, self._legacy_props)

    @property
    def name(self) -> str:
        """Name of the array.

        Examples
        --------
        >>> from ansys.aedt.core import Hfss
        >>> aedtapp = Hfss()
        >>> array_names = aedtapp.component_array_names[0]
        >>> array_comp = aedtapp.component_array[array_names[0]]
        >>> array_comp.name

        """
        child_object = self.child_object
        if child_object is not None and "Name" in dir(child_object):
            self._name = child_object.Name
        return self._name

    @name.setter
    def name(self, array_name: str) -> None:
        if array_name not in self._app.component_array_names:
            old_name = self._name
            self.child_object.SetPropValue("Name", array_name)
            self._app._rename_component_array(old_name, array_name, self)
            # Reset object
            self.__child_object = None
            object.__setattr__(self, "_name", array_name)
        else:
            self._app.logger.warning("Name %s already assigned in the design", array_name)

    @property
    def properties(self) -> dict:
        """Ordered dictionary of the properties of the component array.

        The ``component`` dictionary maps component indices to names. The
        ``cells``, ``active``, and ``rotation`` entries are row-by-column
        matrices. Empty cells have an index of ``-1``. When using object data,
        component indices are assigned in the order returned by AEDT.

        Examples
        --------
        >>> from ansys.aedt.core import Hfss
        >>> aedtapp = Hfss()
        >>> array_names = aedtapp.component_array_names[0]
        >>> array_comp = aedtapp.component_array[array_names[0]]
        >>> array_comp.properties

        """
        if self._has_getobject:
            res = self._parse_array_info_from_props(self.props)
        elif self._array_info_path and os.path.exists(self._array_info_path):  # pragma: no cover
            # From 2024R1, array information can be loaded from a CSV
            res = self.parse_array_info_from_csv(self._array_info_path)
        else:  # pragma: no cover
            res = self.__get_properties_from_aedt()
        return res

    @staticmethod
    def _parse_array_info_from_props(props: dict) -> dict:
        """Parse component array object data into component and cell matrices."""
        rows = int(props["RowDimension"])
        columns = int(props["ColumnDimension"])
        res = {
            "component": {},
            "active": [[False for _ in range(columns)] for _ in range(rows)],
            "rotation": [[0 for _ in range(columns)] for _ in range(rows)],
            "cells": [[-1 for _ in range(columns)] for _ in range(rows)],
        }

        def cell_positions(values):
            if isinstance(values, str):
                values = [values]
            position = r"\[\s*(\d+)\s*,\s*(\d+)\s*\]"
            for value in values:
                if not re.fullmatch(rf"\s*{position}(?:\s*,\s*{position})*\s*", value):
                    raise ValueError(f"Invalid component array cell positions: {value!r}")
                for row, column in re.findall(position, value):
                    row, column = int(row) - 1, int(column) - 1
                    if not (0 <= row < rows and 0 <= column < columns):
                        raise ValueError(f"Component array cell position out of range: [{row + 1},{column + 1}]")
                    yield row, column

        for index, (name, positions) in enumerate(props["Cells"].items(), start=1):
            res["component"][index] = name
            for row, column in cell_positions(positions):
                res["cells"][row][column] = index

        active = props["Active"]
        if active == "All":
            res["active"] = [[cell != -1 for cell in row] for row in res["cells"]]
        else:
            for row, column in cell_positions(active):
                res["active"][row][column] = True

        for angle, positions in props["Rotation"].items():
            if not angle.endswith(" deg"):
                raise ValueError(f"Invalid component array rotation: {angle!r}")
            rotation = int(float(angle[:-4]))
            for row, column in cell_positions(positions):
                res["rotation"][row][column] = rotation
        return res

    @property
    def component_names(self) -> list:
        """List of component names.

        Examples
        --------
        >>> from ansys.aedt.core import Hfss
        >>> aedtapp = Hfss()
        >>> array_names = aedtapp.component_array_names[0]
        >>> array_comp = aedtapp.component_array[array_names[0]]
        >>> array_comp.component_names

        """
        return self.properties["component"]

    @property
    def cells(self) -> list:
        """List of :class:`ansys.aedt.core.modeler.cad.component_array.CellArray` objects.

        Examples
        --------
        >>> from ansys.aedt.core import Hfss
        >>> aedtapp = Hfss()
        >>> array_names = aedtapp.component_array_names[0]
        >>> array_comp = aedtapp.component_array[array_names[0]]
        >>> array_comp.cells

        """
        if not self.update_cells:
            return self.__cells

        if self._app.desktop_class.aedt_version > "2023.2" and not self._has_getobject:  # pragma: no cover
            self.export_array_info(output_file=None)
        elif not self._has_getobject:  # pragma: no cover
            self._app.save_project()

        array_props = self.properties

        self.__cells = [[None for _ in range(self.b_size)] for _ in range(self.a_size)]

        component_names = self.component_names
        for row_cell in range(0, self.a_size):
            for col_cell in range(0, self.b_size):
                self.__cells[row_cell][col_cell] = CellArray(row_cell, col_cell, array_props, component_names, self)
        return self.__cells

    @property
    def post_processing_cells(self) -> dict:
        """Dictionary of each component's postprocessing cells.

        Examples
        --------
        >>> from ansys.aedt.core import Hfss
        >>> aedtapp = Hfss()
        >>> array_names = aedtapp.component_array_names[0]
        >>> array_comp = aedtapp.component_array[array_names[0]]
        >>> array_comp.post_processing_cells

        """
        if not self.__post_processing_cells or self._has_getobject:
            self.__post_processing_cells = {}
            component_info = {}
            for row, row_info in enumerate(self.cells, start=1):
                for col, col_info in enumerate(row_info, start=1):
                    name = col_info.component
                    component_info.setdefault(name, []).append([row, col])

            for component_name, component_cells in component_info.items():
                if component_name not in self.__post_processing_cells.keys() and component_name is not None:
                    self.__post_processing_cells[component_name] = component_cells[0]

        return self.__post_processing_cells

    @post_processing_cells.setter
    def post_processing_cells(self, val: dict) -> None:
        if isinstance(val, dict):
            self.__post_processing_cells = val
            self.edit_array()
        else:  # pragma: no cover
            self._app.logger.error("Dictionary with component names and cell is not correct.")

    @property
    def visible(self) -> bool | None:
        """Flag indicating if the array is visible.

        Examples
        --------
        >>> from ansys.aedt.core import Hfss
        >>> aedtapp = Hfss()
        >>> array_names = aedtapp.component_array_names[0]
        >>> array_comp = aedtapp.component_array[array_names[0]]
        >>> array_comp.visible

        """
        visible = None
        if "Visible" in dir(self.child_object):
            visible = self.child_object.Visible
        return visible

    @visible.setter
    def visible(self, val: bool) -> None:
        if "Visible" in dir(self.child_object):
            self.child_object.Visible = val

    @property
    def show_cell_number(self) -> bool | None:
        """Flag indicating if the array cell number is shown.

        Examples
        --------
        >>> from ansys.aedt.core import Hfss
        >>> aedtapp = Hfss()
        >>> array_names = aedtapp.component_array_names[0]
        >>> array_comp = aedtapp.component_array[array_names[0]]
        >>> array_comp.show_cell_number

        """
        show_cell_number = None
        if "Show_Cell_Number" in dir(self.child_object):
            show_cell_number = self.child_object.Show_Cell_Number
        return show_cell_number

    @show_cell_number.setter
    def show_cell_number(self, val: bool) -> None:
        if "Show_Cell_Number" in dir(self.child_object):
            self.child_object.Show_Cell_Number = val

    @property
    def render_choices(self) -> list | None:
        """List of rendered name choices.

        Examples
        --------
        >>> from ansys.aedt.core import Hfss
        >>> aedtapp = Hfss()
        >>> array_names = aedtapp.component_array_names[0]
        >>> array_comp = aedtapp.component_array[array_names[0]]
        >>> array_comp.render_choices

        """
        render_choices = None
        if "Render_Choices" in dir(self.child_object):
            render_choices = self.child_object.Render_Choices
        return render_choices

    @property
    def render(self) -> str | None:
        """Array rendering.

        Examples
        --------
        >>> from ansys.aedt.core import Hfss
        >>> aedtapp = Hfss()
        >>> array_names = aedtapp.component_array_names[0]
        >>> array_comp = aedtapp.component_array[array_names[0]]
        >>> array_comp.render

        """
        render = None
        if "Render" in dir(self.child_object):
            render = self.child_object.Render
        return render

    @render.setter
    def render(self, val: str) -> None:
        if val not in self.render_choices:
            self._app.logger.warning("Render value is not available.")
        if "Render" in dir(self.child_object):
            self.child_object.Render = val

    @property
    def render_id(self) -> int:
        """Array rendering ID.

        Examples
        --------
        >>> from ansys.aedt.core import Hfss
        >>> aedtapp = Hfss()
        >>> array_names = aedtapp.component_array_names[0]
        >>> array_comp = aedtapp.component_array[array_names[0]]
        >>> array_comp.render_id

        """
        res = self.render_choices.index(self.render)
        return res

    @property
    def a_vector_choices(self) -> list | None:
        """List of name choices for vector A.

        Examples
        --------
        >>> from ansys.aedt.core import Hfss
        >>> aedtapp = Hfss()
        >>> array_names = aedtapp.component_array_names[0]
        >>> array_comp = aedtapp.component_array[array_names[0]]
        >>> array_comp.a_vector_choices

        """
        a_vector_choices = None
        if "A_Vector_Choices" in dir(self.child_object):
            a_vector_choices = self.child_object.A_Vector_Choices
        return a_vector_choices

    @property
    def b_vector_choices(self) -> list | None:
        """List of name choices for vector B.

        Examples
        --------
        >>> from ansys.aedt.core import Hfss
        >>> aedtapp = Hfss()
        >>> array_names = aedtapp.component_array_names[0]
        >>> array_comp = aedtapp.component_array[array_names[0]]
        >>> array_comp.b_vector_choices

        """
        b_vector_choices = None
        if "B_Vector_Choices" in dir(self.child_object):
            b_vector_choices = self.child_object.B_Vector_Choices
        return b_vector_choices

    @property
    def a_vector_name(self) -> str | None:
        """Name of vector A.

        Examples
        --------
        >>> from ansys.aedt.core import Hfss
        >>> aedtapp = Hfss()
        >>> array_names = aedtapp.component_array_names[0]
        >>> array_comp = aedtapp.component_array[array_names[0]]
        >>> array_comp.a_vector_name

        """
        a_vector_name = None
        if "A_Vector" in dir(self.child_object):
            a_vector_name = self.child_object.A_Vector
        return a_vector_name

    @a_vector_name.setter
    def a_vector_name(self, val: str) -> None:
        if val not in self.a_vector_choices:
            self._app.logger.warning("A vector name not available.")
            self.child_object.SetPropValue("A Vector", val)
        elif "A_Vector" in dir(self.child_object):
            self.child_object.A_Vector = val

    @property
    def b_vector_name(self) -> str | None:
        """Name of vector B.

        Examples
        --------
        >>> from ansys.aedt.core import Hfss
        >>> aedtapp = Hfss()
        >>> array_names = aedtapp.component_array_names[0]
        >>> array_comp = aedtapp.component_array[array_names[0]]
        >>> array_comp.b_vector_name

        """
        b_vector_name = None
        if "B_Vector" in dir(self.child_object):
            b_vector_name = self.child_object.B_Vector
        return b_vector_name

    @b_vector_name.setter
    def b_vector_name(self, val: str) -> None:
        if val not in self.b_vector_choices:
            self._app.logger.warning("B vector name not available.")
            self.child_object.SetPropValue("B Vector", val)
        elif "B_Vector" in dir(self.child_object):
            self.child_object.B_Vector = val

    @property
    def a_size(self) -> int | None:
        """Number of cells in the vector A direction.

        Examples
        --------
        >>> from ansys.aedt.core import Hfss
        >>> aedtapp = Hfss()
        >>> array_names = aedtapp.component_array_names[0]
        >>> array_comp = aedtapp.component_array[array_names[0]]
        >>> array_comp.a_size

        """
        cell_count = None
        if "A_Cell_Count" in dir(self.child_object):
            cell_count = int(self.child_object.A_Cell_Count)
        return cell_count

    @a_size.setter
    @min_aedt_version("2026.1")
    def a_size(self, val: int) -> None:
        if "A_Cell_Count" in dir(self.child_object):
            self.child_object.A_Cell_Count = str(val)

    @property
    def b_size(self) -> int | None:
        """Number of cells in the vector B direction.

        Examples
        --------
        >>> from ansys.aedt.core import Hfss
        >>> aedtapp = Hfss()
        >>> array_names = aedtapp.component_array_names[0]
        >>> array_comp = aedtapp.component_array[array_names[0]]
        >>> array_comp.b_size

        """
        cell_count = None
        if "B_Cell_Count" in dir(self.child_object):
            cell_count = int(self.child_object.B_Cell_Count)
        return cell_count

    @b_size.setter
    @min_aedt_version("2026.1")
    def b_size(self, val: int) -> None:
        if "B_Cell_Count" in dir(self.child_object):
            self.child_object.B_Cell_Count = str(val)

    @property
    def a_length(self) -> float | None:
        """Length of the array in A direction.

        Examples
        --------
        >>> from ansys.aedt.core import Hfss
        >>> aedtapp = Hfss()
        >>> array_names = aedtapp.component_array_names[0]
        >>> array_comp = aedtapp.component_array[array_names[0]]
        >>> array_comp.a_length

        """
        if self.a_size is None:  # pragma: no cover
            return None
        a_size = float(self.a_size)
        lattice_vector = self.lattice_vector()
        if lattice_vector[0] != 0:  # pragma: no cover
            x_spacing = float(lattice_vector[0])
        else:
            x_spacing = float(lattice_vector[3])

        return x_spacing * a_size

    @property
    def b_length(self) -> float | None:
        """Length of the array in B direction.

        Examples
        --------
        >>> from ansys.aedt.core import Hfss
        >>> aedtapp = Hfss()
        >>> array_names = aedtapp.component_array_names[0]
        >>> array_comp = aedtapp.component_array[array_names[0]]
        >>> array_comp.b_length

        """
        if self.b_size is None:  # pragma: no cover
            return None
        b_size = float(self.b_size)
        lattice_vector = self.lattice_vector()
        if lattice_vector[1] != 0:
            y_spacing = lattice_vector[1]
        else:  # pragma: no cover
            y_spacing = lattice_vector[4]

        return y_spacing * b_size

    @property
    def padding_cells(self) -> int | None:
        """Number of padding cells.

        Examples
        --------
        >>> from ansys.aedt.core import Hfss
        >>> aedtapp = Hfss()
        >>> array_names = aedtapp.component_array_names[0]
        >>> array_comp = aedtapp.component_array[array_names[0]]
        >>> array_comp.padding_cells

        """
        padding = None
        if "Padding" in dir(self.child_object):
            padding = int(self.child_object.Padding)
        return padding

    @padding_cells.setter
    def padding_cells(self, val: int) -> None:
        if "Padding" in dir(self.child_object):
            self.child_object.Padding = val

    @property
    def coordinate_system(self) -> str:
        """Coordinate system name.

        Examples
        --------
        >>> from ansys.aedt.core import Hfss
        >>> aedtapp = Hfss()
        >>> array_names = aedtapp.component_array_names[0]
        >>> array_comp = aedtapp.component_array[array_names[0]]
        >>> array_comp.coordinate_system

        """
        if "Coordinate_System" in dir(self.child_object):
            return self.child_object.Coordinate_System
        else:  # pragma: no cover
            cs_dict = self.__map_coordinate_system_to_id()
            res = "Global"
            for name, cs_id in cs_dict.items():
                if cs_id == self.__cs_id:
                    res = name
            if res == "Global":
                self._app.logger.warning("Coordinate system is not loaded. Save the project.")
            return res

    @coordinate_system.setter
    def coordinate_system(self, name: str) -> None:
        if "Coordinate_System" in dir(self.child_object):
            self.child_object.Coordinate_System = name
        else:  # pragma: no cover
            cs_dict = self.__map_coordinate_system_to_id()
            if name not in cs_dict:
                self._app.logger.warning("Coordinate system is not loaded. Save the project.")
            else:
                self.__cs_id = cs_dict[name]
                self.edit_array()

    @classmethod
    def create(cls, app: Hfss, input_data: dict, name: str | None = None) -> ComponentArray:
        """Create a component array.

        Parameters
        ----------
        app : :class:`ansys.aedt.core.Hfss`
            HFSS PyAEDT object.
        input_data : dict
            Properties of the component array.
        name : str, optional
            Name of the component array. The default is ``None``, in which case a random name is assigned.

        Returns
        -------
        :class:`ansys.aedt.core.modeler.cad.component_array.ComponentArray`
            Component array object.

        Examples
        --------
        >>> from ansys.aedt.core import Hfss
        >>> aedtapp = Hfss()
        >>> array_names = aedtapp.component_array_names[0]
        >>> array_comp = aedtapp.component_array[array_names[0]]
        >>> array_comp.create(app=aedtapp, input_data={"Name": "Value"})

        """
        app.hybrid = True

        json_dict = input_data

        if not name:
            name = generate_unique_name("Array")

        cells_names = {}
        cells_color = {}
        cells_active = []
        cells_rotation = {}
        cells_post = {}
        for k, v in json_dict["cells"].items():
            if isinstance(k, (list, tuple)):
                k1 = str(list(k))
            else:
                k1 = str(list(ast.literal_eval(k)))
            if v["name"] in cells_names:
                cells_names[v["name"]].append(k1)
            else:
                def_names = app.modeler.user_defined_component_names + app.oeditor.Get3DComponentDefinitionNames()
                if v["name"] not in def_names:
                    if v["name"] not in json_dict:
                        raise AEDTRuntimeError(
                            "3D component array is not present in design and not defined correctly in the JSON file."
                        )

                    geometryparams = app.get_component_variables(json_dict[v["name"]])
                    ref = "Global"
                    if json_dict.get("referencecs", None):
                        ref = json_dict["referencecs"]
                    app.modeler.insert_3d_component(
                        json_dict[v["name"]], geometryparams, coordinate_system=ref, name=v["name"]
                    )
                cells_names[v["name"]] = [k1]
            if v.get("color", None):
                cells_color[v["name"]] = v.get("color", None)
            if str(v.get("rotation", "0.0")) in cells_rotation:
                cells_rotation[str(v.get("rotation", "0.0"))].append(k1)
            else:
                cells_rotation[str(v.get("rotation", "0.0"))] = [k1]

            # By default, cell is active
            if v.get("active", True):
                cells_active.append(k1)

            if v.get("postprocessing", False):
                cells_post[v["name"]] = k1

        primary_lattice = json_dict.get("primarylattice", None)
        secondary_lattice = json_dict.get("secondarylattice", None)

        # TODO: Obtain lattice pair names from 3D Component
        if not primary_lattice:
            raise AEDTRuntimeError("The primary lattice is not defined.")
        if not secondary_lattice:
            raise AEDTRuntimeError("The secondary lattice is not defined.")

        args = [
            "NAME:" + name,
            "Name:=",
            name,
            "RowPrimaryBnd:=",
            primary_lattice,
            "ColumnPrimaryBnd:=",
            secondary_lattice,
            "RowDimension:=",
            json_dict.get("rowdimension", 4),
            "ColumnDimension:=",
            json_dict.get("columndimension", 4),
            "Visible:=",
            json_dict.get("visible", True),
            "ShowCellNumber:=",
            json_dict.get("showcellnumber", True),
            "RenderType:=",
            0,
            "Padding:=",
            json_dict.get("paddingcells", 0),
        ]
        if "referencecs" in json_dict:
            args.append("ReferenceCS:=")
            args.append(json_dict["referencecs"])
        else:
            args.append("ReferenceCSID:=")
            args.append(json_dict.get("referencecsid", 1))

        cells = ["NAME:Cells"]
        for k, v in cells_names.items():
            cells.append(k + ":=")
            cells.append([", ".join(v)])
        rotations = ["NAME:Rotation"]
        for k, v in cells_rotation.items():
            if float(k) != 0.0:
                rotations.append(k + " deg:=")
                rotations.append([", ".join(v)])
        args.append(cells)
        args.append(rotations)
        args.append("Active:=")
        if cells_active:
            args.append(", ".join(cells_active))
        else:
            args.append("All")
        post = ["NAME:PostProcessingCells"]
        for k, v in cells_post.items():
            post.append(k + ":=")
            post.append(str(ast.literal_eval(v)))
        args.append(post)
        args.append("Colors:=")
        col = []
        for k, v in cells_color.items():
            col.append(k)
            col.append(str(v).replace(",", " "))
        args.append(col)
        try:
            names = app.omodelsetup.GetArrayNames()
        except Exception:
            names = []

        if name in names:
            # Save project, because coordinate system information can not be obtained from AEDT API
            app.save_project()
            app.omodelsetup.EditArray(args)
        else:
            app.omodelsetup.AssignArray(args)
            # Save project, because coordinate system information can not be obtained from AEDT API
            app.save_project()
            app.component_array[name] = ComponentArray(app, name)
        app.component_array_names.append(name)
        return app.component_array[name]

    @pyaedt_function_handler()
    def update_properties(self) -> dict:
        """Update component array properties.

        Returns
        -------
        dict
           Ordered dictionary of the properties of the component array.

        Examples
        --------
        >>> from ansys.aedt.core import Hfss
        >>> aedtapp = Hfss()
        >>> array_names = aedtapp.component_array_names[0]
        >>> array_comp = aedtapp.component_array[array_names[0]]
        >>> array_comp.update_properties()

        """
        # From 2024R1, array information can be loaded from a CSV, and this method is not needed.
        if self._app.settings.aedt_version > "2023.2":  # pragma: no cover
            self.export_array_info(output_file=None)
        else:
            self._app.save_project()
        new_properties = self.properties
        # TODO : post_processing_cells property can not be retrieved, so if the length of the components and the
        #  property is different, the method will reset the property.
        if len(new_properties["component"]) != len(self.post_processing_cells):
            self.__post_processing_cells = {}
            new_properties = self.properties
        return new_properties

    @pyaedt_function_handler()
    def delete(self) -> None:
        """Delete the component array.

        References
        ----------
        >>> oModule.DeleteArray

        Examples
        --------
        >>> from ansys.aedt.core import Hfss
        >>> aedtapp = Hfss()
        >>> array_names = aedtapp.component_array_names[0]
        >>> array_comp = aedtapp.component_array[array_names[0]]
        >>> array_comp.delete()

        """
        self._app.omodelsetup.DeleteArray()
        del self._app.component_array[self.name]
        self._app.component_array_names = list(self._app.get_oo_name(self._app.odesign, "Model"))

    @pyaedt_function_handler()
    @min_aedt_version("2024.1")
    def export_array_info(self, output_file: str | None = None) -> str:  # pragma: no cover
        """Export array information to a CSV file.

        Returns
        -------
        str
           Path of the CSV file.

        References
        ----------
        >>> oModule.ExportArray

        Examples
        --------
        >>> from ansys.aedt.core import Hfss
        >>> aedtapp = Hfss()
        >>> array_names = aedtapp.component_array_names[0]
        >>> array_comp = aedtapp.component_array[array_names[0]]
        >>> array_comp.export_array_info(output_file="example.txt")

        """
        if not output_file:  # pragma: no cover
            output_file = os.path.join(self._app.toolkit_directory, "array_info.csv")
        self._app.omodelsetup.ExportArray(self.name, output_file)
        return output_file

    @pyaedt_function_handler()
    def parse_array_info_from_csv(self, input_file: str) -> dict:  # pragma: no cover
        """Parse component array information from the CSV file.

        Parameters
        ----------
        input_file : str
             Name of the CSV file.

        Returns
        -------
        dict
           Ordered dictionary of the properties of the component array.

        Examples
        --------
        >>> from ansys.aedt.core import Hfss
        >>> aedtapp = Hfss(project="Array.aedt")
        >>> array_names = aedtapp.component_array_names[0]
        >>> array = aedtapp.component_array[array_names[0]]
        >>> array_csv = array.export_array_info()
        >>> array_info = array.array_info_parser(array_csv)

        """
        info = read_csv(input_file)
        if not info:
            self._app.logger.error("Data from CSV file is not loaded.")
            return False

        components = {}
        array_matrix = []
        array_matrix_rotation = []
        array_matrix_active = []

        # Components
        start_str = ["Component Index", "Component Name"]
        end_str = ["Source Row", "Source Column", "Source Name", "Magnitude", "Phase"]

        capture_data = False
        line_cont = 0
        for element_data in info:
            if element_data == start_str:
                capture_data = True
            elif element_data == end_str:
                break
            elif capture_data:
                components[int(float(element_data[0]))] = element_data[1]
            line_cont += 1

        # Array matrix
        start_str = ["Array", "Format: Component_index:Rotation_angle:Active_or_Passive"]
        capture_data = False

        for element_data in info[line_cont + 1 :]:
            if capture_data:
                rows = element_data[:-1]
                component_index = []
                rotation = []
                active_passive = []

                for row in rows:
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
                                active_passive.append(bool(int(split_elements[2])))
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
            elif element_data == start_str:
                capture_data = True
        res = {}
        res["component"] = components
        res["active"] = array_matrix_active
        res["rotation"] = array_matrix_rotation
        res["cells"] = array_matrix
        return res

    @pyaedt_function_handler()
    def edit_array(self) -> bool:
        """Edit component array.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        References
        ----------
        >>> oModule.EditArray

        Examples
        --------
        >>> from ansys.aedt.core.modeler.cad.component_array import ComponentArray
        >>> obj = ComponentArray()
        >>> obj.edit_array()

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
            self.render_id,
            "Padding:=",
            self.padding_cells,
            "ReferenceCSID:=",
            self.__cs_id,
        ]

        cells = ["NAME:Cells"]
        component_info = {}
        cells_obj = self.cells[:]
        for row, row_info in enumerate(cells_obj, start=1):
            for col, col_info in enumerate(row_info, start=1):
                name = col_info.component
                component_info.setdefault(name, []).append([row, col])

        for component_name, component_cells in component_info.items():
            if component_name:
                cells.append(component_name + ":=")
                component_cells_str = ", ".join(str(item) for item in component_cells)
                cells.append([component_cells_str])

        rotations = ["NAME:Rotation"]
        component_rotation = {}
        for row, row_info in enumerate(cells_obj, start=1):
            for col, col_info in enumerate(row_info, start=1):
                component_rotation.setdefault(col_info.rotation, []).append([row, col])

        for rotation, rotation_cells in component_rotation.items():
            rotations.append(str(rotation) + " deg:=")
            component_cells_str = ", ".join(str(item) for item in rotation_cells)
            rotations.append([component_cells_str])

        args.append(cells)
        args.append(rotations)

        args.append("Active:=")

        component_active = []
        for row, row_info in enumerate(cells_obj, start=1):
            for col, col_info in enumerate(row_info, start=1):
                if col_info.is_active:
                    component_active.append([row, col])

        if component_active:
            args.append(", ".join(str(item) for item in component_active))
        else:  # pragma: no cover
            args.append("All")

        post = ["NAME:PostProcessingCells"]
        for component_name, values in self.post_processing_cells.items():
            post.append(component_name + ":=")
            post.append([str(values[0]), str(values[1])])
        args.append(post)
        args.append("Colors:=")
        col = []
        args.append(col)
        self._app.omodelsetup.EditArray(args)
        return True

    @pyaedt_function_handler()
    def get_cell(self, row: int, col: int) -> CellArray:
        """Get cell object corresponding to a row and column.

        Returns
        -------
        :class:`ansys.aedt.core.modeler.cad.component_array.CellArray`

        Examples
        --------
        >>> from ansys.aedt.core import Hfss
        >>> aedtapp = Hfss()
        >>> array_names = aedtapp.component_array_names[0]
        >>> array_comp = aedtapp.component_array[array_names[0]]
        >>> array_comp.get_cell(row=1, col=1)

        """
        return self[row, col]

    @pyaedt_function_handler()
    def lattice_vector(self) -> list:
        """Get model lattice vector.

        Returns
        -------
        list
            List of starting point coordinates paired with ending point coordinates.

        References
        ----------
        >>> oModule.GetLatticeVectors()

        Examples
        --------
        >>> from ansys.aedt.core import Hfss
        >>> aedtapp = Hfss()
        >>> array_names = aedtapp.component_array_names[0]
        >>> array_comp = aedtapp.component_array[array_names[0]]
        >>> array_comp.lattice_vector()

        """
        lattice_vectors = self._app.omodelsetup.GetLatticeVectors()

        lattice_vectors = [float(vec) * AEDT_UNITS["Length"][self._app.modeler.model_units] for vec in lattice_vectors]
        return lattice_vectors

    @pyaedt_function_handler()
    def get_component_objects(self) -> dict:
        """Get 3D component center.

        Returns
        -------
        dict
            Dictionary of the center position and part name for all 3D components.

        Examples
        --------
        >>> from ansys.aedt.core import Hfss
        >>> aedtapp = Hfss()
        >>> array_names = aedtapp.component_array_names[0]
        >>> array_comp = aedtapp.component_array[array_names[0]]
        >>> array_comp.get_component_objects()

        """
        component_info = {}
        component_names = self.component_names
        for component in component_names.values():
            component_object = self._app.modeler.components[component]
            if component_object.is_3d_component:
                part_names = [part.name for part in component_object.parts.values()]
            else:
                part_names = list(self._app.get_oo_name(self._app.modeler.oeditor, component_object.name))

            for part_name in part_names:
                if component not in component_info:
                    center = component_object.center
                    scaled_center = [float(cen) * AEDT_UNITS["Length"][self._app.modeler.model_units] for cen in center]
                    component_info[component] = (scaled_center, part_name)
                else:
                    component_info[component] = component_info[component] + (part_name,)

        return component_info

    @pyaedt_function_handler()
    def get_cell_position(self) -> list:
        """Get cell position.

        Returns
        -------
        list
            List of the center position and part name for all cells.

        Examples
        --------
        >>> from ansys.aedt.core import Hfss
        >>> aedtapp = Hfss()
        >>> array_names = aedtapp.component_array_names[0]
        >>> array_comp = aedtapp.component_array[array_names[0]]
        >>> array_comp.get_cell_position()

        """
        cell_info = [[None for _ in range(self.b_size)] for _ in range(self.a_size)]
        lattice_vector = self.lattice_vector()
        # Perpendicular lattice vector
        a_x_dir = True
        if lattice_vector[0] != 0:  # pragma: no cover
            x_spacing = lattice_vector[0]
        else:
            a_x_dir = False
            x_spacing = lattice_vector[3]

        if lattice_vector[1] != 0:
            y_spacing = lattice_vector[1]
        else:  # pragma: no cover
            y_spacing = lattice_vector[4]

        cells = self.cells
        for row_cell in range(0, self.a_size):
            for col_cell in range(0, self.b_size):
                if a_x_dir:  # pragma: no cover
                    y_position = col_cell * y_spacing
                    x_position = row_cell * x_spacing

                else:
                    y_position = row_cell * y_spacing
                    x_position = col_cell * x_spacing

                cell_info[row_cell][col_cell] = (
                    cells[row_cell][col_cell].component,
                    [x_position, y_position, 0.0],
                    cells[row_cell][col_cell].rotation,
                    [row_cell + 1, col_cell + 1],
                )
        return cell_info

    @pyaedt_function_handler()
    def __get_properties_from_aedt(self):
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
        components = {}
        for c in components_map:
            m = re.search(r"'(\d+)'=(\d+)", c)
            components[int(m.group(1))] = component_id[int(m.group(2))]
        res = {}
        res["component"] = components
        res["active"] = props["ArrayDefinition"]["ArrayObject"]["Active"]["matrix"]
        res["rotation"] = props["ArrayDefinition"]["ArrayObject"]["Rotation"]["matrix"]
        res["cells"] = props["ArrayDefinition"]["ArrayObject"]["Cells"]["matrix"]
        return res

    @pyaedt_function_handler()
    def __map_coordinate_system_to_id(self):
        """Map coordinate system to ID.

        Returns
        -------
        dict
            Coordinate system ID.
        """
        res = {"Global": 1}
        if self._app.design_properties and "ModelSetup" in self._app.design_properties:  # pragma: no cover
            cs = self._app.design_properties["ModelSetup"]["GeometryCore"]["GeometryOperations"]["CoordinateSystems"]
            for _, val in cs.items():
                try:
                    if isinstance(val, dict):
                        val = [val]
                    for ite in val:
                        name = ite["Attributes"]["Name"]
                        cs_id = ite["ID"]
                        res[name] = cs_id
                except AttributeError:
                    pass
        return res


class CellArray(PyAedtBase):
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
    array_obj : class:`ansys.aedt.core.modeler.cad.component_array.ComponentArray`
        Instance of the array containing the cell.

    Examples
    --------
    >>> from ansys.aedt.core import Hfss
    >>> aedtapp = Hfss()
    >>> array_names = aedtapp.component_array_names[0]
    >>> array_comp = aedtapp.component_array[array_names[0]]
    >>> cell = array_comp.get_cell(row=1, col=1)

    """

    def __init__(self, row, col, array_props, component_names, array_obj) -> None:
        self.__row = row + 1
        self.__col = col + 1
        self.__array_obj = array_obj
        self.__cell_props = {
            "component": array_props["cells"][row][col],
            "active": array_props["active"][row][col],
            "rotation": array_props["rotation"][row][col],
        }

        self.__rotation = self.__cell_props["rotation"]
        self.__is_active = self.__cell_props["active"]

        component_index = self.__cell_props["component"]
        if component_index == -1:
            self.__component = None
        else:
            self.__component = component_names[component_index]

    @property
    def rotation(self) -> int:
        """Rotation value of the cell object.

        Examples
        --------
        >>> from ansys.aedt.core import Hfss
        >>> aedtapp = Hfss()
        >>> array_names = aedtapp.component_array_names[0]
        >>> array_comp = aedtapp.component_array[array_names[0]]
        >>> cell = array_comp.get_cell(row=1, col=1)
        >>> cell.rotation

        """
        return self.__rotation

    @rotation.setter
    def rotation(self, val: int) -> None:
        if val in [0, 90, 180, 270]:
            self.__rotation = val
            self.__array_obj.update_cells = False
            self.__array_obj.edit_array()
            self.__array_obj.update_cells = True
        else:
            self.__array_obj.logger.error("Rotation must be an integer. 0, 90, 180, and 270 degrees are available.")

    @property
    def component(self):
        """Component name of the cell object.

        Examples
        --------
        >>> from ansys.aedt.core import Hfss
        >>> aedtapp = Hfss()
        >>> array_names = aedtapp.component_array_names[0]
        >>> array_comp = aedtapp.component_array[array_names[0]]
        >>> cell = array_comp.get_cell(row=1, col=1)
        >>> cell.component

        """
        return self.__component

    @component.setter
    def component(self, val: str) -> None:
        component_names = self.__array_obj.component_names
        if val in component_names.values() or val is None:
            self.__array_obj.update_cells = False
            if val is None:
                post_processing_cells = self.__array_obj.post_processing_cells
                for values in post_processing_cells:
                    if (values[0], values[1]) == (self.__row, self.__col):
                        flat_cell_list = [item for sublist in self.__array_obj.cells for item in sublist]
                        for cell in flat_cell_list:
                            if cell.component == self.component and cell.col != self.__col or cell.row != self.__row:
                                self.__array_obj.post_processing_cells[self.component] = [cell.row, cell.col]
                                break
                        break
            self.__component = val
            self.__array_obj.edit_array()
            self.__array_obj.update_cells = True
        else:  # pragma: no cover
            self.__array_obj.logger.error("Component must be defined.")

    @property
    def is_active(self) -> bool:
        """Flag indicating if the cell object is active or passive.

        Examples
        --------
        >>> from ansys.aedt.core import Hfss
        >>> aedtapp = Hfss()
        >>> array_names = aedtapp.component_array_names[0]
        >>> array_comp = aedtapp.component_array[array_names[0]]
        >>> cell = array_comp.get_cell(row=1, col=1)
        >>> cell.is_active

        """
        return self.__is_active

    @is_active.setter
    def is_active(self, val: bool) -> None:
        if isinstance(val, bool):
            self.__is_active = val
            self.__array_obj.update_cells = False
            self.__array_obj.edit_array()
            self.__array_obj.update_cells = True
        else:
            self.__array_obj.logger.error("Only Boolean type is allowed.")
