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

from pathlib import Path
import warnings

from ansys.aedt.core.application.analysis import Analysis
from ansys.aedt.core.base import PyAedtBase
from ansys.aedt.core.generic.configurations import Configurations3DLayout
from ansys.aedt.core.generic.general_methods import pyaedt_function_handler
from ansys.aedt.core.generic.settings import settings
from ansys.aedt.core.modules.setup_templates import SetupKeys
from ansys.aedt.core.modules.solve_setup import Setup3DLayout


class FieldAnalysis3DLayout(Analysis, PyAedtBase):
    """Manages 3D field analysis setup in HFSS 3D Layout.

    This class is automatically initialized by an application call from this
    3D tool. See the application function for parameter definitions.

    Parameters
    ----------
    application : str
        3D application that is to initialize the call.
    projectname : str, optional
        Name of the project to select or the full path to the project
        or AEDTZ archive to open. The default is ``None``, in which
        case an attempt is made to get an active project. If no
        projects are present, an empty project is created.
    designname : str, optional
        Name of the design to select. The default is ``None``, in
        which case an attempt is made to get an active design. If no
        designs are present, an empty design is created.
    solution_type : str, optional
        Solution type to apply to the design. The default is
        ``None``, in which case the default type is applied.
    setup_name : str, optional
        Name of the setup to use as the nominal. The default is
        ``None``, in which case the active setup is used or
        nothing is used.
    version : str, int, float, optional
        Version of AEDT  to use. The default is ``None``, in which case
        the active version or latest installed version is used.
    non_graphical : bool, optional
        Whether to run AEDT in the non-graphical mode. The default
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
        Specifies by process ID the instance of AEDT to point PyAEDT at.
        This parameter is only used when ``new_desktop=False``.
    ic_mode : bool, optional
        Whether to set the design to IC mode. The default is ``None``, which means to retain the
        existing setting.
    remove_lock : bool, optional
        Whether to remove lock to project before opening it or not.
        The default is ``False``, which means to not unlock
        the existing project if needed and raise an exception.

    """

    def __init__(
        self,
        application,
        projectname,
        designname,
        solution_type,
        setup_name=None,
        version=None,
        non_graphical=False,
        new_desktop=False,
        close_on_exit=False,
        student_version=False,
        machine="",
        port=0,
        aedt_process_id=None,
        ic_mode=None,
        remove_lock=False,
    ):
        Analysis.__init__(
            self,
            application,
            projectname,
            designname,
            solution_type,
            setup_name,
            version,
            non_graphical,
            new_desktop,
            close_on_exit,
            student_version,
            machine,
            port,
            aedt_process_id,
            ic_mode,
            remove_lock=remove_lock,
        )
        self._modeler = None
        self._mesh = None
        self._post = None
        self._configurations = Configurations3DLayout(self)
        if not settings.lazy_load:
            self._modeler = self.modeler
            self._mesh = self.mesh
            self._post = self.post

    @property
    def configurations(self):
        """Property to import and export configuration files.

        Returns
        -------
        :class:`ansys.aedt.core.generic.configurations.Configurations`
        """
        return self._configurations

    @property
    def post(self):
        """PostProcessor.

        Returns
        -------
        :class:`ansys.aedt.core.visualization.post.post_3dlayout.PostProcessor3DLayout`
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
        :class:`ansys.aedt.core.modules.mesh_3d_layout.Mesh3d`
        """
        if self._mesh is None and self._odesign:
            from ansys.aedt.core.modules.mesh_3d_layout import Mesh3d

            self._mesh = Mesh3d(self)
        return self._mesh

    @property
    def excitations(self):
        """Get all excitation names.

        .. deprecated:: 0.15.0
           Use :func:`excitation_names` property instead.

        Returns
        -------
        list
            List of excitation names. Excitations with multiple modes will return one
            excitation for each mode.

        References
        ----------
        >>> oModule.GetExcitations
        """
        mess = "The property `excitations` is deprecated.\n"
        mess += " Use `app.excitation_names` directly."
        warnings.warn(mess, DeprecationWarning)
        return self.excitation_names

    @property
    def excitation_names(self):
        """Get all excitation names.

        Returns
        -------
        list
            List of excitation names. Excitations with multiple modes will return one
            excitation for each mode.

        References
        ----------
        >>> oModule.GetAllPortsList
        """
        return list(self.oboundary.GetAllPortsList())

    @pyaedt_function_handler()
    def change_design_settings(self, settings):
        """Set HFSS 3D Layout Design Settings.

        Parameters
        ----------
        settings : dict
            Dictionary of settings with value to apply.

        Returns
        -------
        bool
        """
        arg = ["NAME:options"]
        for key, value in settings.items():
            arg.append(key + ":=")
            arg.append(value)
        self.odesign.DesignOptions(arg)
        return True

    @pyaedt_function_handler(setup_name="setup", variation_string="variations", mesh_path="output_file")
    def export_mesh_stats(self, setup, variations="", output_file=None):
        """Export mesh statistics to a file.

        Parameters
        ----------
        setup : str
            Setup name.
        variations : str, optional
            Variation List.
        output_file : str, optional
            Full path to mesh statistics file. If `None` working_directory will be used.

        Returns
        -------
        str
            Path to the mesh statistics file.

        References
        ----------
        >>> oModule.ExportMeshStats
        """
        if not output_file:
            output_file = str(Path(self.working_directory) / "meshstats.ms")
        self.odesign.ExportMeshStats(setup, variations, output_file)
        return output_file

    @property
    def modeler(self):
        """Modeler object.

        Returns
        -------
        :class:`ansys.aedt.core.modeler.modeler_pcb.Modeler3DLayout`
        """
        if self._modeler is None and self._odesign:
            self.logger.reset_timer()
            from ansys.aedt.core.modeler.modeler_pcb import Modeler3DLayout

            self._modeler = Modeler3DLayout(self)
            self.logger.info_timer("Modeler class has been initialized!")

        return self._modeler

    @property
    def port_list(self):
        """Port list.

        References
        ----------
        >>> oModule.GetAllPorts
        """
        return self.oexcitation.GetAllPortsList()

    @property
    def existing_analysis_setups(self):
        """Existing analysis setups.

        .. deprecated:: 0.15.0
            Use :func:`setup_names` from setup object instead.

        Returns
        -------
        list of str
            List of all analysis setups in the design.

        References
        ----------
        >>> oModule.GetSetups
        """
        msg = "`existing_analysis_setups` is deprecated. Use `setup_names` method from setup object instead."
        warnings.warn(msg, DeprecationWarning)
        return self.setup_names

    @pyaedt_function_handler(setupname="name", setuptype="setup_type")
    def create_setup(self, name="MySetupAuto", setup_type=None, **kwargs):
        """Create a setup.

        Parameters
        ----------
        name : str, optional
            Name of the new setup. The default is ``"MySetupAuto"``.
        setup_type : str, optional
            Type of the setup. The default is ``None``, in which case
            the default type is applied.
        **kwargs : dict, optional
            Extra arguments for setup settings.
            Available keys depend on the setup chosen. For more
            information, see :doc:`../SetupTemplates3DLayout`.

        Returns
        -------
        :class:`ansys.aedt.core.modules.solve_setup.Setup3DLayout`

        References
        ----------
        >>> oModule.Add

        Examples
        --------
        >>> from ansys.aedt.core import Hfss3dLayout
        >>> app = Hfss3dLayout()
        >>> app.create_setup(name="Setup1", MeshSizeFactor=2, SingleFrequencyDataList__AdaptiveFrequency="5GHZ")
        """
        if setup_type is None:
            setup_type = self.design_solutions.default_setup
        elif setup_type in SetupKeys.SetupNames:
            setup_type = SetupKeys.SetupNames.index(setup_type)
        name = self.generate_unique_setup_name(name)
        setup = Setup3DLayout(self, setup_type, name)
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

    @pyaedt_function_handler(setupname="name")
    def delete_setup(self, name):
        """Delete a setup.

        Parameters
        ----------
        name : str
            Name of the setup.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        References
        ----------
        >>> oModule.Delete

        Examples
        --------
        Create a setup and then delete it.

        >>> import ansys.aedt.core
        >>> hfss3dlayout = ansys.aedt.core.Hfss3dLayout()
        >>> setup1 = hfss3dlayout.create_setup(name="Setup1")
        >>> hfss3dlayout.delete_setup()
        PyAEDT INFO: Sweep was deleted correctly.
        """
        if name in self.setup_names:
            self.osolution.Delete(name)
            for s in self.setups:
                if s.name == name:
                    self.setups.remove(s)
            return True
        return False
