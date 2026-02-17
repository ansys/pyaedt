# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 - 2026 ANSYS, Inc. and/or its affiliates.
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

from typing import TYPE_CHECKING

from ansys.aedt.core.application.analysis import Analysis
from ansys.aedt.core.base import PyAedtBase
from ansys.aedt.core.generic.general_methods import pyaedt_function_handler
from ansys.aedt.core.generic.settings import settings
from ansys.aedt.core.modules.setup_templates import SetupKeys
from ansys.aedt.core.modules.solve_setup import SetupCircuit

if TYPE_CHECKING:
    from ansys.aedt.core.modeler.schematic import ModelerTwinBuilder
    from ansys.aedt.core.visualization.post.post_circuit import PostProcessorCircuit


class AnalysisTwinBuilder(Analysis, PyAedtBase):
    """Provides the Twin Builder Analysis Setup (TwinBuilder).

    It is automatically initialized by Application call (Twin Builder).
    Refer to Application function for inputs definition

    Parameters
    ----------
    application : str
        3D application that is to initialize the call.
    project : str or :class:`pathlib.Path`, optional
        Name of the project to select or the full path to the project
        or AEDTZ archive to open. The default is ``None``, in which
        case an attempt is made to get an active project. If no
        projects are present, an empty project is created.
    design : str, optional
        Name of the design to select. The default is ``None``, in
        which case an attempt is made to get an active design. If no
        designs are present, an empty design is created.
    solution_type : str, optional
        Solution type to apply to the design. The default is
        ``None``, in which case the default type is applied.
    setup : str, optional
        Name of the setup to use as the nominal. The default is
        ``None``, in which case the active setup is used or
        nothing is used.
    version : str, int, float, optional
        Version of AEDT  to use. The default is ``None``, in which case
        the active version or latest installed version is used.
    non_graphical : bool, optional
        Whether to run AEDT in non-graphical mode. The default
        is ``False``, in which case AEDT is launched in the graphical mode.
    new_desktop : bool, optional
        Whether to launch an instance of AEDT in a new thread, even if
        another instance of the ``specified_version`` is active on the
        machine. The default is ``False``.
    close_on_exit : bool, optional
        Whether to release AEDT on exit. The default is ``False``.
    student_version : bool, optional
        Whether to enable the student version of AEDT. The default
        is ``False``.
    port : int, optional
        Port number to use for the AEDT instance. The default is ``0``.
    aedt_process_id : int, optional
        Only used when ``new_desktop = False``, specifies by process ID which instance
        of Electronics Desktop to point PyAEDT at.
    remove_lock : bool, optional
        Whether to remove lock to project before opening it or not.
        The default is ``False``, which means to not unlock
        the existing project if needed and raise an exception.
    """

    @property
    def setups(self) -> list[str]:
        """Setup names.

        References
        ----------
        >>> oModule.GetAllSolutionSetups
        """
        return [i.split(" : ")[0] for i in self.oanalysis.GetAllSolutionSetups()]

    def __init__(
        self,
        application: str,
        project: str,
        design: str,
        solution_type: str,
        setup: str = None,
        version: str = None,
        non_graphical: bool = False,
        new_desktop: bool = False,
        close_on_exit: bool = False,
        student_version: bool = False,
        machine: str = "",
        port: int = 0,
        aedt_process_id: int = None,
        remove_lock: bool = False,
    ):
        Analysis.__init__(
            self,
            application,
            project,
            design,
            solution_type,
            setup,
            version,
            non_graphical,
            new_desktop,
            close_on_exit,
            student_version,
            machine,
            port,
            aedt_process_id,
            remove_lock=remove_lock,
        )
        self._modeler = None
        self._post = None
        if not settings.lazy_load:
            self._modeler = self.modeler
            self._post = self.post

    @property
    def modeler(self) -> ModelerTwinBuilder:
        """Design Modeler.

        Returns
        -------
        :class:`ansys.aedt.core.modeler.schematic.ModelerTwinBuilder`
        """
        if self._modeler is None and self._odesign:
            from ansys.aedt.core.modeler.schematic import ModelerTwinBuilder

            self._modeler = ModelerTwinBuilder(self)
        return self._modeler

    @property
    def post(self) -> PostProcessorCircuit:
        """Design Postprocessor.

        Returns
        -------
        :class:`ansys.aedt.core.visualization.post.post_circuit.PostProcessorCircuit`
            PostProcessor object.
        """
        if self._post is None and self._odesign:
            from ansys.aedt.core.visualization.post import post_processor

            self._post = post_processor(self)
        return self._post

    @pyaedt_function_handler()
    def create_setup(self, name: str = "MySetupAuto", setup_type: str = None, **kwargs) -> SetupCircuit:
        """Create a setup.

        Parameters
        ----------
        name : str, optional
            Name of the setup. The default is ``"MySetupAuto"``.
        setup_type : str
            Type of the setup. The default is ``None``, in which case the default
            type is applied.
        **kwargs : dict, optional
            Extra arguments to set up the circuit.
            Available keys depend on the setup chosen.
            For more information, see
            :doc:`../SetupTemplatesCircuit`.

        Returns
        -------
        :class:`ansys.aedt.core.modules.solve_setup.SetupCircuit`
            Setup object.
        """
        if setup_type is None:
            setup_type = self.design_solutions.default_setup
        elif setup_type in SetupKeys.SetupNames:
            setup_type = SetupKeys.SetupNames.index(setup_type)
        name = self.generate_unique_setup(name)
        setup = SetupCircuit(self, setup_type, name)
        tmp_setups = self.setups
        setup.create()
        setup.auto_update = False

        if "props" in kwargs:
            for el in kwargs["props"]:
                setup.props[el] = kwargs["props"][el]
        for arg_name, arg_value in kwargs.items():
            if arg_name == "props":
                continue
            if setup[arg_name] is not None:
                setup[arg_name] = arg_value
        setup.auto_update = True
        setup.update()
        self._setups = tmp_setups + [setup]
        return setup
