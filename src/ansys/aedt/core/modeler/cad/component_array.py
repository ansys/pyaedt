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
import sys
from typing import TYPE_CHECKING
from typing import cast

from ansys.aedt.core.internal.checks import deprecated_doc

if sys.version_info >= (3, 13):
    from warnings import deprecated
else:
    from typing_extensions import deprecated
from ansys.aedt.core.base import PyAedtBase
from ansys.aedt.core.generic.constants import AEDT_UNITS
from ansys.aedt.core.generic.data_handlers import _dict2arg
from ansys.aedt.core.generic.file_utils import _uname
from ansys.aedt.core.generic.file_utils import generate_unique_name
from ansys.aedt.core.generic.file_utils import read_csv
from ansys.aedt.core.generic.general_methods import pyaedt_function_handler

if TYPE_CHECKING:
    from ansys.aedt.core.generic.protocols import _OModelSetup
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

        if self._app.desktop_class.aedt_version < "2026.1":  # pragma: no cover
            # Data that cannot be obtained from CSV
            array_definition = app.design_properties.get("ArrayDefinition", {})
            array_object = array_definition.get("ArrayObject", {}) or array_definition.get("ArrayObjects", {})
            if array_object and isinstance(array_object, dict):
                array_object = array_object.get(name, {})
            references_csid = array_object.get("ReferenceCSID") or array_object.get("ReferenceCS")
            self.__cs_id = 1
            if references_csid:
                self.__cs_id = references_csid

        self.__cells = None
        self.__post_processing_cells = self._saved_post_processing_cells() if not self._has_getobject else None

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
    def _omodelsetup(self) -> _OModelSetup:
        """Return the model setup required by component operations."""
        model_setup = self._app.omodelsetup
        if model_setup is None:
            raise AEDTRuntimeError("Component operations require an active AEDT model setup.")
        return model_setup

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
        """Properties of the component array.

        Assigning a property updates the array in AEDT.

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

    @props.setter
    @min_aedt_version("2026.1")
    def props(self, value: dict) -> None:
        self.update(value)

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
        component indices are assigned in reverse of the ``Cells`` order.

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
            if not isinstance(res, dict):
                raise AEDTRuntimeError("Component array information could not be read from the CSV file.")
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

        for index, (name, positions) in enumerate(reversed(list(props["Cells"].items())), start=1):
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
    def component_names(self) -> dict:
        """Dictionary mapping component indices to names.

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
    def cells(self) -> list[list[CellArray]]:
        """List of :class:`ansys.aedt.core.modeler.cad.component_array.CellArray` objects.

        Examples
        --------
        >>> from ansys.aedt.core import Hfss
        >>> aedtapp = Hfss()
        >>> array_names = aedtapp.component_array_names[0]
        >>> array_comp = aedtapp.component_array[array_names[0]]
        >>> array_comp.cells

        """
        if not self.update_cells and self.__cells is not None:
            return self.__cells

        if self._app.desktop_class.aedt_version > "2023.2" and not self._has_getobject:  # pragma: no cover
            self.export_array_info(output_file=None)
        elif not self._has_getobject:  # pragma: no cover
            self._app.save_project()

        array_props = self.properties

        a_size = self.a_size
        b_size = self.b_size
        if a_size is None or b_size is None:
            raise AEDTRuntimeError("Component array dimensions are unavailable.")

        component_names = self.component_names
        self.__cells = [
            [CellArray(row, col, array_props, component_names, self) for col in range(b_size)] for row in range(a_size)
        ]
        return self.__cells

    @property
    def post_processing_cells(self) -> dict:
        """Dictionary of each component's postprocessing cells.

        The returned dictionary is a copy. Assign it back to this property
        after making changes to apply them to AEDT. AEDT 2026 R1 and later
        provide the selections through object data. Otherwise, initial
        selections are read from the last saved project when available.

        Examples
        --------
        >>> from ansys.aedt.core import Hfss
        >>> aedtapp = Hfss()
        >>> array_names = aedtapp.component_array_names[0]
        >>> array_comp = aedtapp.component_array[array_names[0]]
        >>> array_comp.post_processing_cells

        """
        selections = self._current_post_processing_cells()
        return self._reconcile_post_processing_cells(self.cells, selections)

    @post_processing_cells.setter
    def post_processing_cells(self, val: dict) -> None:
        try:
            selections = self._reconcile_post_processing_cells(self.cells, val, strict=True)
        except (ValueError, SyntaxError, TypeError) as error:
            self._app.logger.error("Invalid postprocessing cells: %s", error)
            return
        if not self._edit_array(post_processing_cells=selections):
            self._app.logger.error("Failed to update postprocessing cells.")

    @staticmethod
    def _component_cell_positions(cells):
        component_info = {}
        for row, row_info in enumerate(cells, start=1):
            for col, cell in enumerate(row_info, start=1):
                if cell.component is not None:
                    component_info.setdefault(cell.component, []).append([row, col])
        return component_info

    @classmethod
    def _reconcile_post_processing_cells(cls, cells, selections, strict=False):
        component_info = cls._component_cell_positions(cells)
        if not isinstance(selections, dict):
            raise ValueError("Postprocessing cells must be a dictionary.")
        normalized = {}
        for name, position in selections.items():
            if isinstance(position, str):
                position = ast.literal_eval(position)
            if not isinstance(position, (list, tuple)) or len(position) != 2:
                raise ValueError(f"Invalid postprocessing cell for {name!r}.")
            if any(not str(value).isdigit() for value in position):
                raise ValueError(f"Invalid postprocessing cell for {name!r}.")
            position = [int(value) for value in position]
            if strict and position not in component_info.get(name, []):
                raise ValueError(f"Postprocessing cell for {name!r} must belong to that component.")
            normalized[name] = position
        return {
            name: list(normalized[name]) if normalized.get(name) in positions else positions[0]
            for name, positions in component_info.items()
        }

    def _current_post_processing_cells(self, props=None):
        if self._has_getobject:
            if props is None:
                props = self.props.to_dict()
            if "PostProcessingCells" not in props:
                raise ValueError(f"Postprocessing cells for array {self.name} are unavailable in object data.")
            return props["PostProcessingCells"]
        return self.__post_processing_cells

    def _saved_post_processing_cells(self):
        """Read selections from the last saved project, without saving it."""
        design = self._app.design_properties or {}
        definition = design.get("ArrayDefinition", {})
        arrays = definition.get("ArrayObject") or definition.get("ArrayObjects") or {}
        if isinstance(arrays, dict):
            if "Name" in arrays:
                arrays = [arrays]
            elif self.name in arrays:
                array = arrays[self.name]
                arrays = [dict(array, Name=self.name)]
            else:
                arrays = list(arrays.values())
        array = next((item for item in arrays if isinstance(item, dict) and item.get("Name") == self.name), None)
        if not array or "PostProcessingCells" not in array:
            self._app.logger.warning(
                "Postprocessing cells for array %s are unavailable in the saved project; using the first cell.",
                self.name,
            )
            return {}

        models = (
            design.get("ModelSetup", {})
            .get("GeometryCore", {})
            .get("GeometryOperations", {})
            .get("UserDefinedModels", {})
            .get("UserDefinedModel", [])
        )
        if isinstance(models, dict):
            models = [models]
        names = {model["ID"]: model["Attributes"]["Name"] for model in models}
        if any(component_id not in names for component_id in array["PostProcessingCells"]):
            self._app.logger.warning(
                "Some postprocessing components for array %s could not be resolved from the saved project.", self.name
            )
        post_processing_cells = array["PostProcessingCells"]
        if not isinstance(post_processing_cells, dict):
            raise ValueError(f"Invalid postprocessing cells for array {self.name}.")
        return {
            names[component_id]: list(position)
            for component_id, position in post_processing_cells.items()
            if component_id in names
        }

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
    def visible(self, val: bool) -> None:  # pragma: no cover
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
        render_choices = self.render_choices
        if render_choices is None or val not in render_choices:
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
        render_choices = self.render_choices
        render = self.render
        if render_choices is None or render is None or render not in render_choices:
            raise AEDTRuntimeError("Array rendering choices are unavailable.")
        res = render_choices.index(render)
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
        vector_choices = self.a_vector_choices
        if vector_choices is None or val not in vector_choices:
            self._app.logger.warning("A vector name not available.")
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
        vector_choices = self.b_vector_choices
        if vector_choices is None or val not in vector_choices:
            self._app.logger.warning("B vector name not available.")
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
                def_names = app.modeler.component_names + app.modeler.component_definition_names
                if v["name"] not in def_names:
                    if v["name"] not in json_dict:
                        raise AEDTRuntimeError(
                            "3D component array is not present in design and not defined correctly in the JSON file."
                        )
                    geometryparams = app.get_component_variables(json_dict[v["name"]])
                    ref = "Global"
                    if json_dict.get("referencecs", None):
                        ref = json_dict["referencecs"]
                    insert_3d_component = getattr(app.modeler, "insert_3d_component", None)
                    if not callable(insert_3d_component):
                        raise AEDTRuntimeError("3D components can only be inserted in a 3D design.")
                    insert_3d_component(json_dict[v["name"]], geometryparams, coordinate_system=ref, name=v["name"])
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

        names = app.component_array_names

        model_setup = app.omodelsetup
        if model_setup is None:
            raise AEDTRuntimeError("Component operations require an active AEDT model setup.")

        if name in names:
            # Save project, because coordinate system information can not be obtained from AEDT API
            app.save_project()
            model_setup.EditArray(args)
        else:
            model_setup.AssignArray(args)
            if app.desktop_class.aedt_version < "2026.1":
                # Save project, because coordinate system information can not be obtained from AEDT API
                app.save_project()
            app._register_component_array(ComponentArray(app, name))

        array = app.component_array[name]
        if not array._has_getobject:
            array.__post_processing_cells = {
                component: ast.literal_eval(cell) for component, cell in cells_post.items()
            }
        return array

    @pyaedt_function_handler()
    @deprecated_doc(version="2.0.0")
    @deprecated("Properties are dynamically updated from 2026R1.")
    def update_properties(self) -> dict:  # pragma: no cover
        """Update component array properties.

        Returns
        -------
        dict or bool
            Ordered properties dictionary, or ``False`` when the CSV contains no data.

        Examples
        --------
        >>> from ansys.aedt.core import Hfss
        >>> aedtapp = Hfss()
        >>> array_names = aedtapp.component_array_names[0]
        >>> array_comp = aedtapp.component_array[array_names[0]]
        >>> array_comp.update_properties()

        """
        if self._has_getobject:
            return self.properties

        # From 2024R1, array information can be loaded from a CSV, and this method is not needed.
        aedt_version = self._app.settings.aedt_version
        if aedt_version is not None and aedt_version > "2023.2":
            self.export_array_info(output_file=None)
        else:
            self._app.save_project()
        new_properties = self.properties
        self.post_processing_cells
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
        old_name = self.name
        self._omodelsetup.DeleteArray()
        self._app._unregister_component_array(old_name)

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
        self._omodelsetup.ExportArray(self.name, output_file)
        return output_file

    @pyaedt_function_handler()
    def parse_array_info_from_csv(self, input_file: str) -> dict | bool:  # pragma: no cover
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
    def update(self, props: dict | None = None) -> bool:
        """Update the array using its property dictionary.

        Parameters
        ----------
        props : dict, optional
            Complete property dictionary to apply. If omitted, current AEDT
            properties are used.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.
        """
        if not self._has_getobject:
            self._app.logger.error("Updating array properties requires GetObjData.")
            return False
        current = self.props.to_dict()
        if props is None:
            props = current
        else:
            props = dict(props)
        supported = {
            "Name",
            "UseAirObjects",
            "RowPrimaryBnd",
            "ColumnPrimaryBnd",
            "RowDimension",
            "ColumnDimension",
            "Visible",
            "ShowCellNumber",
            "RenderType",
            "Padding",
            "ReferenceCS",
            "ReferenceCSID",
            "Cells",
            "Rotation",
            "Active",
            "PostProcessingCells",
            "Colors",
        }
        for key in props.keys() | current.keys():
            if key not in supported and props.get(key) != current.get(key):
                raise ValueError(f"Array property {key!r} cannot be updated.")
        if props.get("Name", self.name) != self.name:
            raise ValueError("Rename the array using its name property.")
        return self._edit_array(props, current_props=current)

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
        return self._edit_array()

    def _edit_array(
        self, props: dict | None = None, post_processing_cells: dict | None = None, current_props: dict | None = None
    ) -> bool:
        if current_props is None:
            current_props = self.props.to_dict() if self._has_getobject else {}
        args = [
            "NAME:" + self.name,
            "Name:=",
            self.name,
            "UseAirObjects:=",
            current_props.get("UseAirObjects", True),
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
        ]
        if self._app.desktop_class.aedt_version >= "2026.1":
            args.append("ReferenceCS:=")
            args.append(self.coordinate_system)
        else:
            args.append("ReferenceCSID:=")
            args.append(self.__cs_id)

        cells_obj = self.cells[:]
        if props is not None and "Cells" in props:
            array_props = self._parse_array_info_from_props(props)
            cells_obj = [
                [
                    CellArray(row, col, array_props, array_props["component"], self)
                    for col in range(int(props["ColumnDimension"]))
                ]
                for row in range(int(props["RowDimension"]))
            ]
        selections = post_processing_cells
        if selections is None:
            selections = self._current_post_processing_cells(current_props)
        selections = self._reconcile_post_processing_cells(
            cells_obj, selections, strict=post_processing_cells is not None
        )
        if props is not None and "PostProcessingCells" in props:
            overrides = props["PostProcessingCells"]
            current = current_props.get("PostProcessingCells", {})
            if not isinstance(overrides, dict):
                raise ValueError("Postprocessing cells must be a dictionary.")
            changed = {name: value for name, value in overrides.items() if current.get(name) != value}
            validated = self._reconcile_post_processing_cells(cells_obj, changed, strict=True)
            selections.update({name: validated[name] for name in changed})
        cells = ["NAME:Cells"]
        component_info = self._component_cell_positions(cells_obj)

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
        for component_name, values in selections.items():
            post.append(component_name + ":=")
            post.append([str(values[0]), str(values[1])])
        args.append(post)
        args.append("Colors:=")
        col = current_props.get("Colors", [])
        args.append(col)
        if props is not None:
            scalar_keys = {
                "Name",
                "UseAirObjects",
                "RowPrimaryBnd",
                "ColumnPrimaryBnd",
                "RowDimension",
                "ColumnDimension",
                "Visible",
                "ShowCellNumber",
                "RenderType",
                "Padding",
                "ReferenceCS",
                "ReferenceCSID",
                "Active",
                "Colors",
            }
            for key in scalar_keys:
                if key in props and key + ":=" in args:
                    args[args.index(key + ":=") + 1] = props[key]
            for key in ("Cells", "Rotation"):
                if key in props:
                    section = []
                    _dict2arg({key: props[key]}, section)
                    index = next(
                        i for i, item in enumerate(args) if isinstance(item, list) and item[0] == "NAME:" + key
                    )
                    args[index] = section[0]
        self._omodelsetup.EditArray(args)
        if not self._has_getobject:
            self.__post_processing_cells = selections
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
        lattice_vectors = self._omodelsetup.GetLatticeVectors()

        unit_factor = cast(float, AEDT_UNITS["Length"][self._app.modeler.model_units])
        lattice_vectors = [float(vec) * unit_factor for vec in lattice_vectors]
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
            if component_object.definition_type == "3d_component":
                part_names = [part.name for part in component_object.parts.values()]
            else:
                part_names = list(self._app.get_oo_name(self._app.modeler.oeditor, component_object.name))

            for part_name in part_names:
                if component not in component_info:
                    center = component_object.center
                    unit_factor = cast(float, AEDT_UNITS["Length"][self._app.modeler.model_units])
                    scaled_center = [float(cen) * unit_factor for cen in center]
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
        a_size = self.a_size
        b_size = self.b_size
        if a_size is None or b_size is None:
            raise AEDTRuntimeError("Component array dimensions are unavailable.")
        cell_info = [[None for _ in range(b_size)] for _ in range(a_size)]
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
        for row_cell in range(a_size):
            for col_cell in range(b_size):
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
            if m is None:
                raise ValueError(f"Invalid component map entry: {c!r}")
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
            self.__array_obj._app.logger.error(
                "Rotation must be an integer. 0, 90, 180, and 270 degrees are available."
            )

    @property
    def component(self) -> str | None:
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
    def component(self, val: str | None) -> None:
        component_names = self.__array_obj.component_names
        if val in component_names.values() or val is None:
            self.__array_obj.update_cells = False
            try:
                self.__array_obj.post_processing_cells
                self.__component = val
                self.__array_obj.edit_array()
            finally:
                self.__array_obj.update_cells = True
        else:  # pragma: no cover
            self.__array_obj._app.logger.error("Component must be defined.")

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
            self.__array_obj._app.logger.error("Only Boolean type is allowed.")
