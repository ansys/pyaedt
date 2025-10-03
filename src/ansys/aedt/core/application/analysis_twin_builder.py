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

from ansys.aedt.core.application.analysis import Analysis
from ansys.aedt.core.base import PyAedtBase
from ansys.aedt.core.generic.general_methods import pyaedt_function_handler
from ansys.aedt.core.generic.settings import settings
from ansys.aedt.core.modules.setup_templates import SetupKeys
from ansys.aedt.core.modules.solve_setup import SetupCircuit


class AnalysisTwinBuilder(Analysis, PyAedtBase):
    """Provides the Twin Builder Analysis Setup (TwinBuilder).

    It is automatically initialized by Application call (Twin Builder).
    Refer to Application function for inputs definition

    Parameters
    ----------
    """

    @property
    def existing_analysis_setups(self):
        """Existing analysis setups.

        .. deprecated:: 0.15.0
            Use :func:`setup_names` from setup object instead.

        Returns
        -------
        list of str
            List of all analysis setups in the design.
        """
        msg = "`existing_analysis_setups` is deprecated. Use `setup_names` method from setup object instead."
        warnings.warn(msg, DeprecationWarning)
        return self.setup_names

    @property
    def setup_names(self):
        """Setup names.

        References
        ----------
        >>> oModule.GetAllSolutionSetups
        """
        return [i.split(" : ")[0] for i in self.oanalysis.GetAllSolutionSetups()]

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
            remove_lock=remove_lock,
        )
        self._modeler = None
        self._post = None
        if not settings.lazy_load:
            self._modeler = self.modeler
            self._post = self.post

    @property
    def modeler(self):
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
    def post(self):
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

    @pyaedt_function_handler(setupname="name", setuptype="setup_type")
    def create_setup(self, name="MySetupAuto", setup_type=None, **kwargs):
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
        name = self.generate_unique_setup_name(name)
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
