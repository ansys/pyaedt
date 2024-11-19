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
import os

from ansys.aedt.core.visualization.post.post_common_3d import PostProcessor3D
from build.lib.ansys.aedt.core.generic.general_methods import pyaedt_function_handler


class PostProcessor3DLayout(PostProcessor3D):
    """Manages the main 3d layout postprocessing functions.

    Parameters
    ----------
    app : :class:`ansys.aedt.core.analysis_3d_layout.FieldAnalysis3DLayout`
        Inherited parent object. The parent object must provide the members
        `_modeler`, `_desktop`, `_odesign`, and `logger`.

    """

    def __init__(self, app):
        PostProcessor3D.__init__(self, app)

    def _check_inputs(self, layers=None, nets=None, solution=None):
        if layers is None:
            layers = list(self._app.modeler.edb.stackup.signal_layers.keys())
        if nets is None:
            nets = []
            for k in self._app.modeler.edb.sources.values():
                nets.append(k.net_name)
                try:
                    nets.append(k.ref_terminal.net_name)
                except AttributeError:  # pragma no cover
                    pass
        if solution is None:
            for setup in self._app.setups:
                if setup.solver_type == "SIwaveDCIR":
                    solution = setup.name
        else:
            for setup in self._app.setups:  # pragma no cover
                if setup.name == solution and setup.solver_type != "SIwaveDCIR":
                    self._app.logger.error("Wrong Setup. It has to be an SIwave DCIR solution.")
                    solution = None
        return layers, nets, solution

    @pyaedt_function_handler()
    def compute_power_by_layer(self, layers=None, nets=None, solution=None):
        """Computes the power by layer. This applies only to Siwave DC Analysis.

        Parameters
        ----------
        layers : list
            List of layers to include in power calculation.
        nets : list
            List of nets to include in power calculation.
        solution : str
            SIwave DCIR solution.

        Returns
        -------
        dict
            Power by layer.
        """
        layers, nets, solution = self._check_inputs(layers, nets, solution)
        if self._app.desktop_class.aedt_version_id >= "2025.1":
            solution_type = "DCIR Fields"
        else:
            solution_type = "DC Fields"
        if layers is None or nets is None or solution is None:  # pragma no cover
            self._app.logger.error("Check inputs.")
            return False
        power_by_layers = {}
        for layer in layers:
            thickness = self._app.modeler.edb.stackup[layer].thickness
            operations = []
            idx = 0
            for net in nets:
                try:
                    get_ids = self._app.odesign.GetGeometryIdsForNetLayerCombination(net, layer, solution)
                except Exception:  # pragma no cover
                    get_ids = []
                if not get_ids:
                    continue  # pragma no cover
                assignment = f"{layer}_{net}"
                operations.extend(
                    [
                        "Fundamental_Quantity('P')",
                        f"EnterSurface('{assignment}')",
                        "Operation('SurfaceValue')",
                        "Operation('Integrate')",
                    ]
                )
                idx += 1
                if idx > 1:
                    operations.append("Operation('+')")
            operations.extend([f"Scalar_Constant({thickness})", "Operation('*')"])
            if idx == 0:
                continue
            my_expression = {
                "name": f"Power_{layer}",
                "description": "Power Density",
                "design_type": ["HFSS 3D Layout Design"],
                "fields_type": [solution_type],
                "solution_type": "",
                "primary_sweep": "",
                "assignment": "",
                "assignment_type": ["Surface"],
                "operations": operations,
                "report": ["Data Table", "Rectangular Plot"],
            }

            self._app.post.fields_calculator.add_expression(my_expression, "")
            self._app.ofieldsreporter.CopyNamedExprToStack(f"Power_{layer}")
            self._app.ofieldsreporter.ClcEval(solution, [], solution_type)
            self._app.ofieldsreporter.CalculatorWrite(
                os.path.join(self._app.working_directory, f"Power_{layer}.txt"), ["Solution:=", solution], []
            )
            self._app.ofieldsreporter.CalcStack("clear")
            if os.path.exists(os.path.join(self._app.working_directory, f"Power_{layer}.txt")):
                with open(os.path.join(self._app.working_directory, f"Power_{layer}.txt"), "r") as f:
                    lines = f.readlines()
                    print(f"Power for layer {layer} is {lines[-1]}")
                    power_by_layers[layer] = float(lines[-1])
        return power_by_layers

    @pyaedt_function_handler()
    def compute_power_by_nets(self, nets=None, layers=None, solution=None):
        """Computes the power by nets. This applies only to Siwave DC Analysis.

        Parameters
        ----------
        layers : list
            List of layers to include in power calculation.
        nets : list
            List of nets to include in power calculation.
        solution : str
            SIwave DCIR solution.

        Returns
        -------
        dict
            Power by nets.
        """
        layers, nets, solution = self._check_inputs(layers, nets, solution)
        if layers is None or nets is None or solution is None:  # pragma no cover
            self._app.logger.error("Check inputs.")
            return False
        power_by_nets = {}
        if self._app.desktop_class.aedt_version_id >= "2025.1":
            solution_type = "DCIR Fields"
        else:
            solution_type = "DC Fields"
        for net in nets:
            operations = []
            idx = 0
            for layer in layers:
                thickness = self._app.modeler.edb.stackup[layer].thickness
                try:
                    get_ids = self._app.odesign.GetGeometryIdsForNetLayerCombination(net, layer, solution)
                except:  # pragma no cover
                    get_ids = []
                if not get_ids:
                    continue
                assignment = f"{layer}_{net}"
                operations.extend(
                    [
                        "Fundamental_Quantity('P')",
                        f"EnterSurface('{assignment}')",
                        "Operation('SurfaceValue')",
                        "Operation('Integrate')",
                    ]
                )
                idx += 1
                if idx > 1:
                    operations.append("Operation('+')")
            operations.extend([f"Scalar_Constant({thickness})", "Operation('*')"])
            if idx == 0:
                continue  # pragma no cover
            my_expression = {
                "name": f"Power_{net}",
                "description": "Power Density",
                "design_type": ["HFSS 3D Layout Design"],
                "fields_type": [solution_type],
                "solution_type": "",
                "primary_sweep": "",
                "assignment": "",
                "assignment_type": ["Surface"],
                "operations": operations,
                "report": ["Data Table", "Rectangular Plot"],
            }

            self._app.post.fields_calculator.add_expression(my_expression, "")
            self._app.ofieldsreporter.CopyNamedExprToStack(f"Power_{net}")
            self._app.ofieldsreporter.ClcEval(solution, [], solution_type)
            self._app.ofieldsreporter.CalculatorWrite(
                os.path.join(self._app.working_directory, f"Power_{net}.txt"), ["Solution:=", solution], []
            )
            self._app.ofieldsreporter.CalcStack("clear")
            if os.path.exists(os.path.join(self._app.working_directory, f"Power_{net}.txt")):
                with open(os.path.join(self._app.working_directory, f"Power_{net}.txt"), "r") as f:
                    lines = f.readlines()
                    print(f"Power for net {net} is {lines[-1]}")
                    power_by_nets[net] = float(lines[-1])
        return power_by_nets
