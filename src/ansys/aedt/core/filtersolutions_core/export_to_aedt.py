# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 - 2024 ANSYS, Inc. and/or its affiliates.
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

from ctypes import POINTER
from ctypes import byref
from ctypes import c_bool
from ctypes import c_char_p
from ctypes import c_int
from enum import Enum
import os

import ansys.aedt.core


class ExportFormat(Enum):
    """Provides an enum of export format types.

    **Attributes:**

    - DIRECT_TO_AEDT: Represents a direct export to ``AEDT``.
    - PYTHON: Represents a Python scripted export.
    """

    DIRECT_TO_AEDT = 0
    PYTHON_SCRIPT = 1


class ExportCreationMode(Enum):
    """Provides an enum of export creation modes.

    **Attributes:**

    - OVERWRITE: Represents export to ``AEDT`` and overwrite to existing design.
    - APPEND: Represents export to ``AEDT`` and append to existing design.
    """

    OVERWRITE = 0
    APPEND = 1


class ExportToAedt:
    """Defines attributes and parameters for exporting filter .

    This class lets you construct all the necessary attributes for the ``ExportToAedt`` class.
    """

    def __init__(self):
        self._dll = ansys.aedt.core.filtersolutions_core._dll_interface()._dll
        self._dll_interface = ansys.aedt.core.filtersolutions_core._dll_interface()
        self._define_export_to_desktop_dll_functions()

    def _define_export_to_desktop_dll_functions(self):
        """Define C++ API DLL functions."""

        self._dll.setSchematicName.argtype = c_char_p
        self._dll.setSchematicName.restype = c_int
        self._dll.getSchematicName.argtypes = [c_char_p, c_int]
        self._dll.getSchematicName.restype = c_int

        self._dll.setSimulateAfterExport.argtype = c_bool
        self._dll.setSimulateAfterExport.restype = c_int
        self._dll.getSimulateAfterExport.argtype = POINTER(c_bool)
        self._dll.getSimulateAfterExport.restype = c_int

        self._dll.setGroupDelay.argtype = c_bool
        self._dll.setGroupDelay.restype = c_int
        self._dll.getGroupDelay.argtype = POINTER(c_bool)
        self._dll.getGroupDelay.restype = c_int

        self._dll.setGTGain.argtype = c_bool
        self._dll.setGTGain.restype = c_int
        self._dll.getGTGain.argtype = POINTER(c_bool)
        self._dll.getGTGain.restype = c_int

        self._dll.setVGSL.argtype = c_bool
        self._dll.setVGSL.restype = c_int
        self._dll.getVGSL.argtype = POINTER(c_bool)
        self._dll.getVGSL.restype = c_int

        self._dll.setVGIN.argtype = c_bool
        self._dll.setVGIN.restype = c_int
        self._dll.getVGIN.argtype = POINTER(c_bool)
        self._dll.getVGIN.restype = c_int

        self._dll.setS11.argtype = c_bool
        self._dll.setS11.restype = c_int
        self._dll.getS11.argtype = POINTER(c_bool)
        self._dll.getS11.restype = c_int

        self._dll.setS21.argtype = c_bool
        self._dll.setS21.restype = c_int
        self._dll.getS21.argtype = POINTER(c_bool)
        self._dll.getS21.restype = c_int

        self._dll.setS12.argtype = c_bool
        self._dll.setS12.restype = c_int
        self._dll.getS12.argtype = POINTER(c_bool)
        self._dll.getS12.restype = c_int

        self._dll.setS22.argtype = c_bool
        self._dll.setS22.restype = c_int
        self._dll.getS22.argtype = POINTER(c_bool)
        self._dll.getS22.restype = c_int

        self._dll.setDbFormat.argtype = c_bool
        self._dll.setDbFormat.restype = c_int
        self._dll.getDbFormat.argtype = POINTER(c_bool)
        self._dll.getDbFormat.restype = c_int

        self._dll.setRectPlot.argtype = c_bool
        self._dll.setRectPlot.restype = c_int
        self._dll.getRectPlot.argtype = POINTER(c_bool)
        self._dll.getRectPlot.restype = c_int

        self._dll.setSmithPlot.argtype = c_bool
        self._dll.setSmithPlot.restype = c_int
        self._dll.getSmithPlot.argtype = POINTER(c_bool)
        self._dll.getSmithPlot.restype = c_int

        self._dll.setPolarPlot.argtype = c_bool
        self._dll.setPolarPlot.restype = c_int
        self._dll.getPolarPlot.argtype = POINTER(c_bool)
        self._dll.getPolarPlot.restype = c_int

        self._dll.setTableData.argtype = c_bool
        self._dll.setTableData.restype = c_int
        self._dll.getTableData.argtype = POINTER(c_bool)
        self._dll.getTableData.restype = c_int

        self._dll.setOptimetrics.argtype = c_bool
        self._dll.setOptimetrics.restype = c_int
        self._dll.getOptimetrics.argtype = POINTER(c_bool)
        self._dll.getOptimetrics.restype = c_int

        self._dll.setOptimizeAfterExport.argtype = c_bool
        self._dll.setOptimizeAfterExport.restype = c_int
        self._dll.getOptimizeAfterExport.argtype = POINTER(c_bool)
        self._dll.getOptimizeAfterExport.restype = c_int

    def _open_aedt_export(self):
        """Open export page to accept manipulate export parameters"""
        status = self._dll.openLumpedExportPage()
        ansys.aedt.core.filtersolutions_core._dll_interface().raise_error(status)



    @property
    def schematic_name(self) -> str:
        """Name of the exported schematic in ``AEDT``, displayed as the project and design names.
        The default name is ``FilterSolutions`` if not specified.

        Returns
        -------
        str
        """
        schematic_name_string = self._dll_interface.get_string(self._dll.getSchematicName)
        return schematic_name_string

    @schematic_name.setter
    def schematic_name(self, schematic_name_string):
        self._dll_interface.set_string(self._dll.setSchematicName, schematic_name_string)

    @property
    def simulate_after_export_enabled(self) -> bool:
        """Flag indicating if the simulation will be initiated upon export to ``AEDT``.

        Returns
        -------
        bool
        """
        simulate_after_export_enabled = c_bool()
        status = self._dll.getSimulateAfterExport(byref(simulate_after_export_enabled))
        ansys.aedt.core.filtersolutions_core._dll_interface().raise_error(status)
        return bool(simulate_after_export_enabled.value)

    @simulate_after_export_enabled.setter
    def simulate_after_export_enabled(self, simulate_after_export_enabled: bool):
        status = self._dll.setSimulateAfterExport(simulate_after_export_enabled)
        ansys.aedt.core.filtersolutions_core._dll_interface().raise_error(status)

    @property
    def include_group_delay_enabled(self) -> bool:
        """Flag indicating if the group delay report will be created upon export to ``AEDT``.

        Returns
        -------
        bool
        """
        include_group_delay_enabled = c_bool()
        status = self._dll.getGroupDelay(byref(include_group_delay_enabled))
        ansys.aedt.core.filtersolutions_core._dll_interface().raise_error(status)
        return bool(include_group_delay_enabled.value)

    @include_group_delay_enabled.setter
    def include_group_delay_enabled(self, include_group_delay_enabled: bool):
        status = self._dll.setGroupDelay(include_group_delay_enabled)
        ansys.aedt.core.filtersolutions_core._dll_interface().raise_error(status)

    @property
    def include_gt_gain_enabled(self) -> bool:
        """Flag indicating if the total voltage gain report will be created upon
        export to ``AEDT``.

        Returns
        -------
        bool
        """
        include_gt_gain_enabled = c_bool()
        status = self._dll.getGTGain(byref(include_gt_gain_enabled))
        ansys.aedt.core.filtersolutions_core._dll_interface().raise_error(status)
        return bool(include_gt_gain_enabled.value)

    @include_gt_gain_enabled.setter
    def include_gt_gain_enabled(self, include_gt_gain_enabled: bool):
        status = self._dll.setGTGain(include_gt_gain_enabled)
        ansys.aedt.core.filtersolutions_core._dll_interface().raise_error(status)

    @property
    def include_vgsl_enabled(self) -> bool:
        """Flag indicating if the voltage gain source load report will be created upon
         export to ``AEDT``.

        Returns
        -------
        bool
        """
        include_vgsl_enabled = c_bool()
        status = self._dll.getVGSL(byref(include_vgsl_enabled))
        ansys.aedt.core.filtersolutions_core._dll_interface().raise_error(status)
        return bool(include_vgsl_enabled.value)

    @include_vgsl_enabled.setter
    def include_vgsl_enabled(self, include_vgsl_enabled: bool):
        status = self._dll.setVGSL(include_vgsl_enabled)
        ansys.aedt.core.filtersolutions_core._dll_interface().raise_error(status)

    @property
    def include_vgin_enabled(self) -> bool:
        """Flag indicating if the voltage gain insertion report will be created upon
        export to ``AEDT``.

        Returns
        -------
        bool
        """
        include_vgin_enabled = c_bool()
        status = self._dll.getVGIN(byref(include_vgin_enabled))
        ansys.aedt.core.filtersolutions_core._dll_interface().raise_error(status)
        return bool(include_vgin_enabled.value)

    @include_vgin_enabled.setter
    def include_vgin_enabled(self, include_vgin_enabled: bool):
        status = self._dll.setVGIN(include_vgin_enabled)
        ansys.aedt.core.filtersolutions_core._dll_interface().raise_error(status)

    @property
    def include_input_return_loss_s11_enabled(self) -> bool:
        """Flag indicating if the input return loss report will be created upon
        export to ``AEDT``.

        Returns
        -------
        bool
        """
        include_input_return_loss_s11_enabled = c_bool()
        status = self._dll.getS11(byref(include_input_return_loss_s11_enabled))
        ansys.aedt.core.filtersolutions_core._dll_interface().raise_error(status)
        return bool(include_input_return_loss_s11_enabled.value)

    @include_input_return_loss_s11_enabled.setter
    def include_input_return_loss_s11_enabled(self, include_input_return_loss_s11_enabled: bool):
        status = self._dll.setS11(include_input_return_loss_s11_enabled)
        ansys.aedt.core.filtersolutions_core._dll_interface().raise_error(status)

    @property
    def include_forward_transfer_s21_enabled(self) -> bool:
        """Flag indicating if the forward transfer gain report will be created upon
        export to ``AEDT``.

        Returns
        -------
        bool
        """
        include_forward_transfer_s21_enabled = c_bool()
        status = self._dll.getS21(byref(include_forward_transfer_s21_enabled))
        ansys.aedt.core.filtersolutions_core._dll_interface().raise_error(status)
        return bool(include_forward_transfer_s21_enabled.value)

    @include_forward_transfer_s21_enabled.setter
    def include_forward_transfer_s21_enabled(self, include_forward_transfer_s21_enabled: bool):
        status = self._dll.setS21(include_forward_transfer_s21_enabled)
        ansys.aedt.core.filtersolutions_core._dll_interface().raise_error(status)

    @property
    def include_reverse_transfer_s12_enabled(self) -> bool:
        """Flag indicating if the reverse transfer gain report will be created upon
        export to ``AEDT``.

        Returns
        -------
        bool
        """
        include_reverse_transfer_s12_enabled = c_bool()
        status = self._dll.getS12(byref(include_reverse_transfer_s12_enabled))
        ansys.aedt.core.filtersolutions_core._dll_interface().raise_error(status)
        return bool(include_reverse_transfer_s12_enabled.value)

    @include_reverse_transfer_s12_enabled.setter
    def include_reverse_transfer_s12_enabled(self, include_reverse_transfer_s12_enabled: bool):
        status = self._dll.setS12(include_reverse_transfer_s12_enabled)
        ansys.aedt.core.filtersolutions_core._dll_interface().raise_error(status)

    @property
    def include_output_return_loss_s22_enabled(self) -> bool:
        """Flag indicating if the output return loss report will be created upon
        export to ``AEDT``.

        Returns
        -------
        bool
        """
        include_output_return_loss_s22_enabled = c_bool()
        status = self._dll.getS22(byref(include_output_return_loss_s22_enabled))
        ansys.aedt.core.filtersolutions_core._dll_interface().raise_error(status)
        return bool(include_output_return_loss_s22_enabled.value)

    @include_output_return_loss_s22_enabled.setter
    def include_output_return_loss_s22_enabled(self, include_output_return_loss_s22_enabled: bool):
        status = self._dll.setS22(include_output_return_loss_s22_enabled)
        ansys.aedt.core.filtersolutions_core._dll_interface().raise_error(status)

    @property
    def db_format_enabled(self) -> bool:
        """Flag indicating if the report format in dB in the
        exported filter to ``AEDT`` is enabled.

        Returns
        -------
        bool
        """
        db_format_enabled = c_bool()
        status = self._dll.getDbFormat(byref(db_format_enabled))
        ansys.aedt.core.filtersolutions_core._dll_interface().raise_error(status)
        return bool(db_format_enabled.value)

    @db_format_enabled.setter
    def db_format_enabled(self, db_format_enabled: bool):
        status = self._dll.setDbFormat(db_format_enabled)
        ansys.aedt.core.filtersolutions_core._dll_interface().raise_error(status)

    @property
    def rectangular_plot_enabled(self) -> bool:
        """Flag indicating if the rectangular report format in the
         exported filter to ``AEDT`` is enabled.

        Returns
        -------
        bool
        """
        rectangular_plot_enabled = c_bool()
        status = self._dll.getRectPlot(byref(rectangular_plot_enabled))
        ansys.aedt.core.filtersolutions_core._dll_interface().raise_error(status)
        return bool(rectangular_plot_enabled.value)

    @rectangular_plot_enabled.setter
    def rectangular_plot_enabled(self, rectangular_plot_enabled: bool):
        status = self._dll.setRectPlot(rectangular_plot_enabled)
        ansys.aedt.core.filtersolutions_core._dll_interface().raise_error(status)

    @property
    def smith_plot_enabled(self) -> bool:
        """Flag indicating if the ``Smith Chart`` report format in the
         exported filter to ``AEDT`` is enabled.

        Returns
        -------
        bool
        """
        smith_plot_enabled = c_bool()
        status = self._dll.getSmithPlot(byref(smith_plot_enabled))
        ansys.aedt.core.filtersolutions_core._dll_interface().raise_error(status)
        return bool(smith_plot_enabled.value)

    @smith_plot_enabled.setter
    def smith_plot_enabled(self, smith_plot_enabled: bool):
        status = self._dll.setSmithPlot(smith_plot_enabled)
        ansys.aedt.core.filtersolutions_core._dll_interface().raise_error(status)

    @property
    def polar_plot_enabled(self) -> bool:
        """Flag indicating if the polar report format in the
         exported filter to ``AEDT`` is enabled.

        Returns
        -------
        bool
        """
        polar_plot_enabled = c_bool()
        status = self._dll.getPolarPlot(byref(polar_plot_enabled))
        ansys.aedt.core.filtersolutions_core._dll_interface().raise_error(status)
        return bool(polar_plot_enabled.value)

    @polar_plot_enabled.setter
    def polar_plot_enabled(self, polar_plot_enabled: bool):
        status = self._dll.setPolarPlot(polar_plot_enabled)
        ansys.aedt.core.filtersolutions_core._dll_interface().raise_error(status)

    @property
    def table_data_enabled(self) -> bool:
        """Flag indicating if the table data format in the
         exported filter to ``AEDT`` is enabled.

        Returns
        -------
        bool
        """
        table_data_enabled = c_bool()
        status = self._dll.getTableData(byref(table_data_enabled))
        ansys.aedt.core.filtersolutions_core._dll_interface().raise_error(status)
        return bool(table_data_enabled.value)

    @table_data_enabled.setter
    def table_data_enabled(self, table_data_enabled: bool):
        status = self._dll.setTableData(table_data_enabled)
        ansys.aedt.core.filtersolutions_core._dll_interface().raise_error(status)

    @property
    def optimitrics_enabled(self) -> bool:
        """Flag indicating if the optimitric parameters in the
         exported filter to ``AEDT`` is enabled.

        Returns
        -------
        bool
        """
        optimitrics_enabled = c_bool()
        status = self._dll.getOptimetrics(byref(optimitrics_enabled))
        ansys.aedt.core.filtersolutions_core._dll_interface().raise_error(status)
        return bool(optimitrics_enabled.value)

    @optimitrics_enabled.setter
    def optimitrics_enabled(self, optimitrics_enabled: bool):
        status = self._dll.setOptimetrics(optimitrics_enabled)
        ansys.aedt.core.filtersolutions_core._dll_interface().raise_error(status)

    @property
    def optimize_after_export_enabled(self) -> bool:
        """Flag indicating if the optimization option after exporting to ``AEDT`` is enabled.

        Returns
        -------
        bool
        """
        optimize_after_export_enabled = c_bool()
        status = self._dll.getOptimizeAfterExport(byref(optimize_after_export_enabled))
        ansys.aedt.core.filtersolutions_core._dll_interface().raise_error(status)
        return bool(optimize_after_export_enabled.value)

    @optimize_after_export_enabled.setter
    def optimize_after_export_enabled(self, optimize_after_export_enabled: bool):
        status = self._dll.setOptimizeAfterExport(optimize_after_export_enabled)
        ansys.aedt.core.filtersolutions_core._dll_interface().raise_error(status)

    def export_design(self, export_format: ExportFormat.DIRECT_TO_AEDT, export_creation_mode=None, export_path=None):
        """Export the design directly to ``AEDT` or generate a ``Python`` script for exporting.
        When exporting to ``AEDT``, the design can either be appended to an existing project or overwrite it.
        When generating a Python script, the script is created and saved to the specified file location.

        Parameters
        ----------
        export_format : `ExportFormat`
            The export format type.
            The default is ``DIRECT_TO_AEDT``.
        design_creation_mode : `ExportCreationMode`
            The design creation mode.
            The default is ``None``.
        export_path : str
            The export path for Python script.
            The default is ``None``.
        """
        if export_creation_mode is None:
            export_creation_mode = ExportCreationMode.OVERWRITE
        if export_path is None:
            export_path = ""
        else:
            directory_path = os.path.dirname(export_path)
            if not os.path.exists(directory_path):
                os.makedirs(directory_path)
        export_path_bytes = bytes(export_path, "ascii")
        status = self._dll.exportDesign(export_format.value, export_creation_mode.value, export_path_bytes)
        ansys.aedt.core.filtersolutions_core._dll_interface().raise_error(status)

    def import_tuned_variables(self):
        """Imported ``AEDT`` tuned parameter variables back into the ``FilterSolutions`` project."""
        status = self._dll.importTunedVariables()
        ansys.aedt.core.filtersolutions_core._dll_interface().raise_error(status)
