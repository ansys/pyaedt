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

from typing import Optional
from typing import Union

from ansys.aedt.core.application.analysis_3d import FieldAnalysis3D
from ansys.aedt.core.application.design import DesignSettingsManipulation
from ansys.aedt.core.base import PyAedtBase
from ansys.aedt.core.generic.configurations import ConfigurationsIcepak
from ansys.aedt.core.generic.settings import settings
from ansys.aedt.core.modules.boundary.icepak_boundary import BoundaryDictionary


class FieldAnalysisIcepak(FieldAnalysis3D, PyAedtBase):
    """Manages Icepak field analysis setup.

    This class is automatically initialized by an application call from one Icepak.
    See the application function for parameter definitions.

    Parameters
    ----------
    application : str
        3D application that is to initialize the call.
    project : str, optional
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
    aedt_process_id : int, optional
        Only used when ``new_desktop = False``, specifies by process ID which instance
        of Electronics Desktop to point PyAEDT at.
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
        setup: Optional[str] = None,
        version: Optional[Union[str, int, float]] = None,
        non_graphical: bool = False,
        new_desktop: bool = False,
        close_on_exit: bool = False,
        student_version=False,
        machine: str = "",
        port: int = 0,
        aedt_process_id: Optional[int] = None,
        remove_lock: bool = False,
    ):
        FieldAnalysis3D.__init__(
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

        self.design_settings.manipulate_inputs = IcepakDesignSettingsManipulation(self)
        self._mesh = None
        self._post = None
        self._monitor = None
        self._configurations = ConfigurationsIcepak(self)
        if not settings.lazy_load:
            self._mesh = self.mesh
            self._post = self.post
            self._monitor = self.monitor

    @property
    def post(self):
        """Icepak post processor.

        Returns
        -------
        :class:`ansys.aedt.core.visualization.post.post_icepak.PostProcessorIcepak`
            PostProcessor object.
        """
        if self._post is None and self._odesign:
            from ansys.aedt.core.visualization.post import post_processor

            self._post = post_processor(self)
        return self._post

    @property
    def mesh(self):
        """Mesh.

        Returns
        -------
        :class:`ansys.aedt.core.modules.mesh_icepak.IcepakMesh`
            Mesh object.
        """
        if self._mesh is None and self._odesign:
            self.logger.reset_timer()

            from ansys.aedt.core.modules.mesh_icepak import IcepakMesh

            self._mesh = IcepakMesh(self)
            self.logger.info_timer("Mesh class has been initialized!")
        return self._mesh

    @property
    def monitor(self):
        """Property to handle monitor objects.

        Returns
        -------
        :class:`ansys.aedt.core.modules.monitor_icepak.Monitor`
        """
        if self._monitor is None:
            from ansys.aedt.core.visualization.post.monitor_icepak import Monitor

            self._monitor = Monitor(self)

        self._monitor._delete_removed_monitors()  # force update. some operations may delete monitors
        return self._monitor


class IcepakDesignSettingsManipulation(DesignSettingsManipulation, PyAedtBase):
    """Manages Icepak design settings.

    This class provides methods to modify specific design settings like ambient temperature,
    gauge pressure, and gravity vector. The settings are managed through key-value pairs
    and validated based on specific rules for each key.

    Parameters
    ----------
    app : FieldAnalysisIcepak
        Icepak application that is to initialize the call.
    """

    def __init__(self, app):
        self.app = app

    def execute(self, k, v) -> str:
        """
        Modify the design settings for the given key with the specified value.

        Handles specific keys like ``"AmbTemp"``, ``"AmbRadTemp"``, ``"AmbGaugePressure"``, and ``"GravityVec"``,
        applying custom logic to validate and format the values before assignment.

        Parameters
        ----------
            k : str
                The design setting key to modify.
            v: float, int, str
                The value to assign to the setting. The expected type and format depend on the key.

        Returns
        -------
        str
             Updated value after processing, or an error message if the operation fails.
        """
        if k in ["AmbTemp", "AmbRadTemp"]:
            if k == "AmbTemp" and isinstance(v, (dict, BoundaryDictionary)):
                self.app.logger.error("Failed. Use `edit_design_settings` function.")
                return self.app.design_settings["AmbTemp"]
                # TODO: Bug in native API. Uncomment when fixed
                # if not self.solution_type == "Transient":
                #     self.logger.error("Transient assignment is supported only in transient designs.")
                #     return False
                # ambtemp = getattr(self, "_parse_variation_data")(
                #     "AmbientTemperature",
                #     "Transient",
                #     variation_value=v["Values"],
                #     function=v["Function"],
                # )
                # if ambtemp is not None:
                #     return ambtemp
                # else:
                #     self.logger.error("Transient dictionary is not valid.")
                #     return False
            else:
                return self.app.value_with_units(v, "cel")
        elif k == "AmbGaugePressure":
            return self.app.value_with_units(v, "n_per_meter_sq")
        elif k == "GravityVec":
            if isinstance(v, (float, int)):
                self.app.design_settings["GravityDir"] = ["Positive", "Negative"][v // 3]
                v = f"Global::{['X', 'Y', 'Z'][v - v // 3 * 3]}"
                return v
            else:
                if len(v.split("::")) == 1 and len(v) < 3:
                    if v.startswith("+") or v.startswith("-"):
                        self.app.design_settings["GravityDir"] = ["Positive", "Negative"][int(v.startswith("-"))]
                        v = v[-1]
                    return f"Global::{v}"
                else:
                    return v
        else:
            return v
