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

if TYPE_CHECKING:
    from ansys.aedt.core.maxwell import Maxwell2d
    from ansys.aedt.core.maxwell import Maxwell3d
    from ansys.aedt.core.modeler.modeler_2d import ModelerRMxprt
    from ansys.aedt.core.visualization.post.post_circuit import PostProcessorCircuit


class FieldAnalysisRMxprt(Analysis, PyAedtBase):
    """Provides the RMxprt field analysis interface.

    This class is for RMxprt analysis setup. It is automatically
    initialized by a call from the Rmxprt application.

    Parameters
    ----------
    application : str
        Name of the application. The value should be ``"RMxprtSolution"``.
    project : str
        Name of the project to select or the full path to the project
        or AEDTZ archive to open.
    design : str
        Name of the design to select.
    solution_type : str
        Solution type to apply to the design.
    setup : str, optional
        Name of the setup to use as the nominal. The default is
        ``None``, in which case the active setup is used or
        nothing is used.
    version : str, optional
        Version of AEDT to use. The default is ``None``, in which case
        the active version or latest installed version is used.
        This parameter is ignored when a script is launched within AEDT.
    non_graphical : bool, optional
        Whether to launch AEDT in non-graphical mode. The default
        is ``False``, in which case AEDT is launched in graphical mode.
        This parameter is ignored when a script is launched within AEDT.
    new_desktop : bool, optional
        Whether to launch an instance of AEDT in a new thread, even if
        another instance of the ``specified_version`` is active on the
        machine. The default is ``False``. This parameter is ignored when
        a script is launched within AEDT.
    close_on_exit : bool, optional
        Whether to release AEDT on exit. The default is ``False``.
    student_version : bool, optional
        Whether to open the AEDT student version. The default is
        ``False``. This parameter is ignored when a script is launched
        within AEDT.
    machine : str, optional
        Machine name to connect the oDesktop session to. This parameter works only on
        2022 R2 or later. The remote server must be up and running with the command
        `"ansysedt.exe -grpcsrv portnum"`. If the machine is `"localhost"`, the server
        starts if it is not present. The default is ``""``.
    port : int, optional
        Port number on which to start the oDesktop communication on an already existing server.
        This parameter is ignored when creating a new server. It works only in 2022 R2 or later.
        The remote server must be up and running with the command `"ansysedt.exe -grpcsrv portnum"`.
        The default is ``0``.
    aedt_process_id : int, optional
        Process ID for the instance of AEDT to point PyAEDT at. The default is
        ``None``. This parameter is only used when ``new_desktop = False``.
    remove_lock : bool, optional
        Whether to remove lock to project before opening it or not.
        The default is ``False``, which means to not unlock
        the existing project if needed and raise an exception.

    """

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
    def post(self) -> PostProcessorCircuit:
        """Post Object.

        Returns
        -------
        :class:`ansys.aedt.core.visualization.post.post_circuit.PostProcessorCircuit`
            PostProcessor object.
        """
        if self._post is None and self._odesign:
            from ansys.aedt.core.visualization.post import post_processor

            self._post = post_processor(self)
        return self._post

    @property
    def modeler(self) -> ModelerRMxprt:
        """Modeler.

        Returns
        -------
        :class:`ansys.aedt.core.modules.modeler_2d.ModelerRMxprt`

        """
        if self._modeler is None and self._odesign:
            from ansys.aedt.core.modeler.modeler_2d import ModelerRMxprt

            self._modeler = ModelerRMxprt(self)

        return self._modeler

    @pyaedt_function_handler()
    def disable_modelcreation(self, solution_type: str | None = None) -> bool:
        """Enable the RMxprt solution.

        Parameters
        ----------
        solution_type :
            Type of the solution. The default is ``None``.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        """
        self.design_type = "RMxprt"
        self.solution_type = solution_type
        return True

    @pyaedt_function_handler()
    def enable_modelcreation(self, solution_type: str | None = None) -> bool:
        """Enable model creation for the Maxwell model wizard.

        Parameters
        ----------
        solution_type : str
            Type of the solution. The default is ``None``.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        """
        self.design_type = "ModelCreation"
        self.solution_type = solution_type
        return True

    @pyaedt_function_handler()
    def create_maxwell_design(
        self, setup_name: str, variation: str = "", maxwell_2d: bool = True
    ) -> bool | Maxwell2d | Maxwell3d:
        """Create a Maxwell design from Rmxprt project. Setup has to be solved to run this method.

        Parameters
        ----------
        setup_name : str
            Name of setup.
        variation : str, optional
            Variation string to be applied.
        maxwell_2d : bool, optional
            Whether if the model has to be exported in Maxwell 2D or Maxwell 3D. Default is ``True``.

        Returns
        -------
        :class:`ansys.aedt.core.maxwell.Maxwell2d` or :class:`ansys.aedt.core.maxwell.Maxwell3d`
            Maxwell object.
        """
        des_list = self.design_list[::]
        self.oanalysis.CreateMaxwellDesign(0 if maxwell_2d else 1, setup_name, variation)
        new_des_list = [i for i in self.design_list[::] if i not in des_list and "Maxwell" in i]
        if new_des_list:
            if maxwell_2d:
                from ansys.aedt.core.maxwell import Maxwell2d as App
            else:  # pragma: no cover
                from ansys.aedt.core import Maxwell3d as App
            app = App(design=new_des_list[0])
            return app
        self.logger.error("Failed to generate the Maxwell project.")
        return False

    @pyaedt_function_handler()
    def set_material_threshold(self, conductivity: float = 100000, permeability: float = 100) -> bool:
        """Set material threshold.

        Parameters
        ----------
        conductivity : float, optional
            Conductivity threshold.
            The default value is 100000.
        permeability : float, optional
            Permeability threshold.
            The default value is 100.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.
        """
        try:
            self.odesign.SetThreshold(conductivity, permeability)
            return True
        except Exception:
            return False

    @pyaedt_function_handler()
    def _check_solution_consistency(self) -> bool:
        """Check solution consistency."""
        if self.design_solutions:
            return self._odesign.GetSolutionType() == self.design_solutions._solution_type
        else:
            return True

    @pyaedt_function_handler()
    def _check_design_consistency(self) -> bool:
        """Check design consistency."""
        consistent = False
        destype = self._odesign.GetDesignType()
        if destype == "RMxprt":
            consistent = self._check_solution_consistency()
        return consistent
