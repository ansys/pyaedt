# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 - 2025 ANSYS, Inc. and/or its affiliates.
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

import warnings

from ansys.aedt.core.base import PyAedtBase
from ansys.aedt.core.generic.constants import CATEGORIESQ3D
from ansys.aedt.core.generic.constants import PlotCategoriesQ3D
from ansys.aedt.core.generic.file_utils import generate_unique_name
from ansys.aedt.core.generic.general_methods import filter_tuple
from ansys.aedt.core.generic.general_methods import pyaedt_function_handler


class Matrix(PyAedtBase):
    """Manages Matrix in Q3d and Q2d Projects.

    Examples
    --------


    """

    def __init__(self, app, name, operations=None):
        self._app = app
        self.omatrix = self._app.omatrix
        self.name = name
        self._sources = []
        if operations:
            if isinstance(operations, list):
                self._operations = operations
            else:
                self._operations = [operations]

    # TODO: Remove for release 1.0.0
    @property
    def CATEGORIES(self):
        """Deprecated: Use a plot category from ``ansys.aedt.core.generic.constants`` instead."""
        warnings.warn(
            "Usage of CATEGORIES is deprecated. "
            "Use a plot category defined in ansys.aedt.core.generic.constants instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        return CATEGORIESQ3D

    @pyaedt_function_handler()
    def sources(self, is_gc_sources=True):
        """List of matrix sources.

        Parameters
        ----------
        is_gc_sources : bool,
            In Q3d, define if to return GC sources or RL sources. Default `True`.

        Returns
        -------
        List
        """
        if self.name in list(self._app.omatrix.ListReduceMatrixes()):
            if self._app.design_type == "Q3D Extractor":
                self._sources = list(self._app.omatrix.ListReduceMatrixReducedSources(self.name, is_gc_sources))
            else:
                self._sources = list(self._app.omatrix.ListReduceMatrixReducedSources(self.name))
        return self._sources

    @pyaedt_function_handler()
    def get_sources_for_plot(
        self,
        get_self_terms=True,
        get_mutual_terms=True,
        first_element_filter=None,
        second_element_filter=None,
        category="C",
    ):
        """Return a list of source of specified matrix ready to be used in plot reports.

        Parameters
        ----------
        get_self_terms : bool
            Either if self terms have to be returned or not.
        get_mutual_terms : bool
            Either if mutual terms have to be returned or not.
        first_element_filter : str, optional
            Filter to apply to first element of equation. It accepts `*` and `?` as special characters.
        second_element_filter : str, optional
            Filter to apply to second element of equation. It accepts `*` and `?` as special characters.
        category : str
            Plot category name as in the report. Eg. "C" is category Capacitance.
            Matrix `CATEGORIES` property can be used to map available categories.

        Returns
        -------
        list

        Examples
        --------
        >>> from ansys.aedt.core import Q3d
        >>> q3d = Q3d(project_path)
        >>> q3d.matrices[0].get_sources_for_plot(
        ...     first_element_filter="Bo?1", second_element_filter="GND*", category="DCL"
        ... )
        """
        if not first_element_filter:
            first_element_filter = "*"
        if not second_element_filter:
            second_element_filter = "*"
        is_cg = False
        if category in [PlotCategoriesQ3D.C, PlotCategoriesQ3D.G]:
            is_cg = True
        list_output = []
        if get_self_terms:
            for el in self.sources(is_gc_sources=is_cg):
                value = f"{category}({el},{el})"
                if filter_tuple(value, first_element_filter, second_element_filter):
                    list_output.append(value)
        if get_mutual_terms:
            for el1 in self.sources(is_gc_sources=is_cg):
                for el2 in self.sources(is_gc_sources=is_cg):
                    if el1 != el2:
                        value = f"{category}({el1},{el2})"
                        if filter_tuple(value, first_element_filter, second_element_filter):
                            list_output.append(value)
        return list_output

    @property
    def operations(self):
        """List of matrix operations.

        Returns
        -------
        List
        """
        if self.name in list(self._app.omatrix.ListReduceMatrixes()):
            self._operations = self._app.omatrix.ListReduceMatrixOperations(self.name)
        return self._operations

    @pyaedt_function_handler()
    def create(
        self,
        source_names=None,
        new_net_name=None,
        new_source_name=None,
        new_sink_name=None,
    ):
        """Create a new matrix.

        Parameters
        ----------
        source_names : str, list
            List or str containing the content of the matrix reduction (eg. source name).
        new_net_name : str, optional
            Name of the new net. The default is ``None``.
        new_source_name : str, optional
            Name of the new source. The default is ``None``.
        new_sink_name : str, optional
            Name of the new sink. The default is ``None``.

        Returns
        -------
        bool
            `True` if succeeded.
        """
        if not isinstance(source_names, list) and source_names:
            source_names = [source_names]

        command = self._write_command(source_names, new_net_name, new_source_name, new_sink_name)
        self.omatrix.InsertRM(self.name, command)
        return True

    @pyaedt_function_handler()
    def delete(self):
        """Delete current matrix.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.
        """
        self.omatrix.DeleteRM(self.name)
        for el in self._app.matrices:
            if el.name == self.name:
                self._app.matrices.remove(el)
        return True

    @pyaedt_function_handler()
    def add_operation(
        self,
        operation_type,
        source_names=None,
        new_net_name=None,
        new_source_name=None,
        new_sink_name=None,
    ):
        """Add a new operation to existing matrix.

        Parameters
        ----------
        operation_type : str
            Operation to perform
        source_names : str, list
            List or str containing the content of the matrix reduction (eg. source name).
        new_net_name : str, optional
            Name of the new net. The default is ``None``.
        new_source_name : str, optional
            Name of the new source. The default is ``None``.
        new_sink_name : str, optional
            Name of the new sink. The default is ``None``.

        Returns
        -------
        bool
            `True` if succeeded.
        """
        self._operations.append(operation_type)
        if not isinstance(source_names, list) and source_names:
            source_names = [source_names]

        if not new_net_name:
            new_net_name = generate_unique_name("Net")

        if not new_source_name:
            new_source_name = generate_unique_name("Source")

        if not new_sink_name:
            new_sink_name = generate_unique_name("Sink")

        command = self._write_command(source_names, new_net_name, new_source_name, new_sink_name)
        self.omatrix.RMAddOp(self.name, command)
        return True

    @pyaedt_function_handler()
    def _write_command(self, source_names, new_name, new_source, new_sink):
        if self._operations[-1] == "JoinSeries":
            command = f"""{self._operations[-1]}('{new_name}', '{"', '".join(source_names)}')"""
        elif self._operations[-1] == "JoinParallel":
            command = (
                f"""{self._operations[-1]}('{new_name}', '{new_source}', '{new_sink}', '{"', '".join(source_names)}')"""
            )
        elif self._operations[-1] == "JoinSelectedTerminals":
            command = f"""{self._operations[-1]}('', '{"', '".join(source_names)}')"""
        elif self._operations[-1] == "FloatInfinity":
            command = "FloatInfinity()"
        elif self._operations[-1] == "AddGround":
            command = f"""{self._operations[-1]}(SelectionArray[{len(source_names)}: '{"', '".join(source_names)}'],
            OverrideInfo())"""
        elif (
            self._operations[-1] == "SetReferenceGround"
            or self._operations[-1] == "SetReferenceGround"
            or self._operations[-1] == "Float"
        ):
            command = f"""{self._operations[-1]}(SelectionArray[{len(source_names)}: '{"', '".join(source_names)}'],
            OverrideInfo())"""
        elif self._operations[-1] == "Parallel" or self._operations[-1] == "DiffPair":
            id_ = 0
            for el in self._app.boundaries:
                if el.name == source_names[0]:
                    id_ = self._app.modeler[el.props["Objects"][0]].id
            command = f"""{self._operations[-1]}(SelectionArray[{len(source_names)}: '{"', '".join(source_names)}'],
            OverrideInfo({id_}, '{new_name}'))"""
        else:
            command = f"""{self._operations[-1]}('{"', '".join(source_names)}')"""
        return command
