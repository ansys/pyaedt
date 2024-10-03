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

from ansys.aedt.core.application.analysis import Analysis
from ansys.aedt.core.generic.settings import settings


class AnalysisCircuitNetlist(Analysis, object):
    """Provides the Circuit Netlist (CircuitNetlist) interface.
    Circuit Netlist Editor has no setup, solution, analysis or postprocessor
    It is automatically initialized by Application call.
    Refer to Application function for inputs definition

    Parameters
    ----------
    project : str, optional
        Name of the project to select or the full path to the project
        or AEDTZ archive to open.  The default is ``None``, in which
        case an attempt is made to get an active project. If no
        projects are present, an empty project is created.
    design : str, optional
        Name of the design to select. The default is ``None``, in
        which case an attempt is made to get an active design. If no
        designs are present, an empty design is created.
    version : str, int, float, optional
        Version of AEDT to use. The default is ``None``. If ``None``,
        the active setup is used or the latest installed version is
        used.
    non_graphical : bool, optional
        Whether to launch AEDT in the non-graphical mode. The default
        is ``False``, in which case AEDT is launched in the graphical mode.
    new_desktop : bool, optional
        Whether to launch an instance of AEDT in a new thread, even if
        another instance of the ``specified_version`` is active on the
        machine.  The default is ``False``.
    close_on_exit : bool, optional
        Whether to release AEDT on exit. The default is ``False``.
    student_version : bool, optional
        Whether to open the AEDT student version. The default is ``False``.
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
        project,
        design,
        version,
        non_graphical,
        new_desktop,
        close_on_exit,
        student_version,
        machine,
        port,
        aedt_process_id,
        remove_lock,
    ):
        Analysis.__init__(
            self,
            "Circuit Netlist",
            project,
            design,
            None,
            None,
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
            self._post = self.post

    @property
    def post(self):
        """PostProcessor.

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
        """Modeler object."""
        return self._modeler
