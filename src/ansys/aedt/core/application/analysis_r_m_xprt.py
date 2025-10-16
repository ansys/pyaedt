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

from ansys.aedt.core.application.analysis import Analysis
from ansys.aedt.core.base import PyAedtBase
from ansys.aedt.core.generic.general_methods import pyaedt_function_handler
from ansys.aedt.core.generic.settings import settings


class FieldAnalysisRMxprt(Analysis, PyAedtBase):
    """Manages RMXprt field analysis setup. (To be implemented.)

    This class is automatically initialized by an application call (like HFSS,
    Q3D...). Refer to the application function for inputs definition.

    Parameters
    ----------

    Returns
    -------

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
    def post(self):
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
    def modeler(self):
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
    def disable_modelcreation(self, solution_type=None):
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
        self.design_type = "RMxprtSolution"
        self.solution_type = solution_type
        return True

    @pyaedt_function_handler()
    def enable_modelcreation(self, solution_type=None):
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
    def create_maxwell_design(self, setup_name, variation="", maxwell_2d=True):
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
                from ansys.aedt.core.maxwell import Maxwell2d

                app = Maxwell2d(design=new_des_list[0])
                return app
            else:
                from ansys.aedt.core import Maxwell3d

                app = Maxwell3d(design=new_des_list[0])
                return app
        self.logger.error("Failed to generate the Maxwell project.")
        return False

    @pyaedt_function_handler()
    def set_material_threshold(self, conductivity=100000, permeability=100):
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
    def _check_solution_consistency(self):
        """Check solution consistency."""
        if self.design_solutions:
            return self._odesign.GetSolutionType() == self.design_solutions._solution_type
        else:
            return True

    @pyaedt_function_handler()
    def _check_design_consistency(self):
        """Check design consistency."""
        consistent = False
        destype = self._odesign.GetDesignType()
        if destype == "RMxprt":
            consistent = self._check_solution_consistency()
        return consistent
