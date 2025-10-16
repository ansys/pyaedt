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
import re

from ansys.aedt.core.base import PyAedtBase
from ansys.aedt.core.generic.general_methods import pyaedt_function_handler
from ansys.aedt.core.generic.settings import settings
from ansys.aedt.core.visualization.post.post_common_3d import PostProcessor3D


class PostProcessor3DLayout(PostProcessor3D, PyAedtBase):
    """Manages the main schematic postprocessing functions.

    .. note::
       Some functionalities are available only when AEDT is running in the graphical mode.

    Parameters
    ----------
    app : :class:`ansys.aedt.core.application.analysis_nexxim.FieldAnalysisCircuit`
        Inherited parent object. The parent object must provide the members
        `_modeler`, `_desktop`, `_odesign`, and `logger`.

    """

    def __init__(self, app):
        PostProcessor3D.__init__(self, app)

    @pyaedt_function_handler
    def _compute_power_loss(self, net_filter=None, layer_filter=None, solution=None):
        if solution is None:
            for setup in self._app.setups:
                if setup.solver_type == "SIwaveDCIR":
                    solution = setup.name
                    break
            if solution is None:  # pragma: no cover
                self._app.logger.error("No SIwave DC IR setup exist.")
                return
        else:
            solution_obj = [i for i in self._app.setups if i.name == solution]
            if len(solution_obj):
                if solution_obj[0].solver_type != "SIwaveDCIR":  # pragma: no cover
                    self._app.logger.error(f"Solution {solution} is not a SIwave DC IR setup.")
                    return
            else:  # pragma: no cover
                self._app.logger.error(f"Solution {solution} doesn't exist.")
                return

        aedt_results = Path(self._app.project_file).with_suffix(".aedtresults")
        solution_data_dir = aedt_results / "main"
        if not solution_data_dir.exists():  # pragma: no cover
            solution_data_dir = aedt_results / self._app.design_name
        subfolders = [f for f in solution_data_dir.iterdir() if f.is_dir()]
        dcir_solution_folder = None
        for folder in subfolders:
            file_exec = folder / "SIwave.exec"
            if not file_exec.exists():
                continue  # pragma: no cover
            with open(file_exec, "r") as f:
                siwave_exec = f.read()
                match = re.search(r'SetupName\s+"(.*?)"', siwave_exec)
                if match.group(1) == solution:
                    dcir_solution_folder = folder
                    break
        if dcir_solution_folder is None:  # pragma: no cover
            self._app.logger.error(f"Solution {solution} has no result.")
            return
        else:
            file_net = None
            for i in dcir_solution_folder.iterdir():
                if i.suffix == ".net":
                    file_net = i
                    break
            with open(file_net, "r") as f:
                file_net_text = f.read()
                match = re.search(r"B_NET_CLASSIFICATION\s+(.*?)\s+E_NET_CLASSIFICATION", file_net_text, re.DOTALL)
                nets = []
                for i in match.group(1).split("\n"):
                    net_name = i.lstrip(" ").split(" ")[1]
                    nets.append(net_name)

        if net_filter is not None:
            nets = [i for i in nets if i in net_filter]

        edbapp = self._app.modeler.edb

        if layer_filter is None:
            net_per_layer_names = {i: [] for i in edbapp.stackup.signal_layers.keys()}
        else:
            net_per_layer_names = {i: [] for i in edbapp.stackup.signal_layers.keys() if i in layer_filter}

        for net_name in nets:
            net_obj = edbapp.nets[net_name]
            layer_names = [i.layer_name for i in net_obj.primitives]
            layer_names = list(set(layer_names))
            for i in layer_names:
                if i in net_per_layer_names:
                    net_per_layer_names[i].append(net_name)

        power_loss_per_layer = []
        operations = []
        for layer_name, net_names in net_per_layer_names.items():
            if not net_names:
                continue
            thickness = edbapp.stackup[layer_name].thickness
            for net_name in net_names:
                assignment = f"{layer_name}_{net_name}"
                operations.extend(
                    [
                        "Fundamental_Quantity('P')",
                        f"EnterSurface('{assignment}')",
                        "Operation('SurfaceValue')",
                        "Operation('Integrate')",
                    ]
                )

                operations.extend([f"Scalar_Constant({thickness})", "Operation('*')"])

                solution_type = ["DC Fields"] if settings.aedt_version < "2025.1" else ["DCIR Fields"]
                my_expression = {
                    "name": f"Power_{layer_name}",
                    "description": "Power Density",
                    "design_type": ["HFSS 3D Layout Design"],
                    "fields_type": solution_type,
                    "solution_type": "",
                    "primary_sweep": "",
                    "assignment": "",
                    "assignment_type": ["Surface"],
                    "operations": operations,
                    "report": ["Data Table", "Rectangular Plot"],
                }
                if self._app.post.fields_calculator.is_expression_defined(my_expression["name"]):
                    self._app.post.fields_calculator.delete_expression(my_expression["name"])
                self._app.post.fields_calculator.add_expression(my_expression, "")

                loss = self._app.post.fields_calculator.evaluate(my_expression["name"], solution, intrinsics={})

                power_loss_per_layer.append({"layer": layer_name, "net": net_name, "loss": float(loss)})

        return power_loss_per_layer

    @pyaedt_function_handler()
    def compute_power_by_layer(self, layers=None, solution=None):
        """Compute the power by layer.

        This applies only to SIwave DC Analysis.

        Parameters
        ----------
        layers : list, optional
            Layers to include in power calculation.
        solution : str, optional
            SIwave DCIR solution.

        Returns
        -------
        dict
            Power by layer.
        """
        power_by_layers = {}
        power_loss = self._compute_power_loss(layer_filter=layers, solution=solution)
        for i in power_loss:
            layer_name = i["layer"]
            loss = i["loss"]
            if layer_name not in power_by_layers:
                power_by_layers[layer_name] = loss
            else:
                power_by_layers[layer_name] += loss
        return power_by_layers

    @pyaedt_function_handler()
    def compute_power_by_net(self, nets=None, solution=None):
        """Compute the power by nets. This applies only to SIwave DC Analysis.

        Parameters
        ----------
        nets : list, optional
            Layers to include in power calculation.
        solution : str, optional
            SIwave DCIR solution.

        Returns
        -------
        dict
            Power by nets.
        """
        power_by_nets = {}
        power_loss = self._compute_power_loss(net_filter=nets, solution=solution)
        for i in power_loss:
            net_name = i["net"]
            loss = i["loss"]
            if net_name not in power_by_nets:
                power_by_nets[net_name] = loss
            else:
                power_by_nets[net_name] += loss
        return power_by_nets

    @pyaedt_function_handler()
    def _get_all_3dl_layers_nets(self, setup):
        try:
            get_ids = self._odesign.GetGeometryIdsForAllNetLayerCombinations(setup)
        except Exception:  # pragma no cover
            get_ids = []
        k = 0
        get_ids_dict = {}
        key = ""
        list_to_add = []
        while k < len(get_ids):
            if get_ids[k].startswith("PlotGeomInfo"):
                if key:
                    get_ids_dict[key] = list_to_add
                key = get_ids[k].replace("PlotGeomInfo for ", "").replace(" (net/layer combination):", "")
                list_to_add = []
            else:
                try:
                    list_to_add.append(int(get_ids[k]))
                except ValueError:
                    pass
            k = k + 1
        return get_ids_dict

    @pyaedt_function_handler()
    def _get_3dl_layers_nets(self, layers, nets, setup, include_dielectrics):
        lst_faces = []
        new_layers = []
        ids_dict = self._get_all_3dl_layers_nets(setup)
        if not layers:
            if include_dielectrics:
                new_layers.extend([f"{i}" for i in self._app.modeler.edb.stackup.dielectric_layers.keys()])
            for layer in self._app.modeler.edb.stackup.signal_layers.keys():
                if not nets:
                    nets = list(self._app.modeler.edb.nets.nets.keys())
                for el in nets:
                    if f"{el}/{layer}" in ids_dict:
                        lst_faces.extend(ids_dict[f"{el}/{layer}"])
        else:
            for layer in layers:
                if layer in self._app.modeler.edb.stackup.dielectric_layers and include_dielectrics:
                    new_layers.append(f"{layer}")
                elif layer in self._app.modeler.edb.stackup.signal_layers:
                    if not nets:
                        nets = list(self._app.modeler.edb.nets.nets.keys())
                    for el in nets:
                        if f"{el}/{layer}" in ids_dict:
                            lst_faces.extend(ids_dict[f"{el}/{layer}"])
        return lst_faces, new_layers

    @pyaedt_function_handler()
    def _get_3d_layers_nets(self, layers, nets):
        dielectrics = []
        new_layers = []
        for k, v in self._app.modeler.user_defined_components.items():
            if v.layout_component:
                if not layers:
                    layers = [i for i in v.layout_component.edb_object.stackup.stackup_layers.keys()]
                if not nets:
                    nets = [""] + [i for i in v.layout_component.edb_object.nets.nets.keys()]
                for layer in layers:
                    if layer in v.layout_component.edb_object.stackup.signal_layers:
                        new_layers.append([layer] + nets)
                    elif layer in v.layout_component.edb_object.stackup.dielectric_layers:
                        dielectrics.append(f"{k}:{layer}")
        return dielectrics, new_layers

    @pyaedt_function_handler()
    def create_fieldplot_layers(
        self, layers, quantity, setup=None, nets=None, plot_on_surface=True, intrinsics=None, name=None
    ):
        # type: (list, str, str, list, bool, dict, str) -> FieldPlot
        """Create a field plot of stacked layer plot.

        This plot is valid from AEDT 2023 R2 and later in HFSS 3D Layout. Nets can be used as a filter.
        Dielectrics will be included into the plot.
        It works when a layout components in 3d modeler is used.

        Parameters
        ----------
        layers : list
            List of layers to plot. For example:
            ``["Layer1","Layer2"]``. If empty list is provided
            all layers are considered.
        quantity : str
            Name of the quantity to plot.
        setup : str, optional
            Name of the setup. The default is ``None``, in which case the ``nominal_adaptive``
            setup is used. Make sure to build a setup string in the form of
            ``"SetupName : SetupSweep"``, where ``SetupSweep`` is the sweep name to
            use in the export or ``LastAdaptive``.
        nets : list, optional
            List of nets to filter the field plot. Optional.
        plot_on_surface : bool, optional
            Whether if the plot has to be on surfaces or inside the objects.
            It is applicable only to layout components. Default is ``True``.
        intrinsics : dict, str, optional
            Intrinsic variables required to compute the field before the export.
            These are typically: frequency, time and phase.
            It can be provided either as a dictionary or as a string.
            If it is a dictionary, keys depend on the solution type and can be expressed in lower or camel case as:

            - ``"Freq"`` or ``"Frequency"``.
            - ``"Time"``.
            - ``"Phase"``.

            If it is a string, it can either be ``"Freq"`` or ``"Time"`` depending on the solution type.
            The default is ``None`` in which case the intrinsics value is automatically computed based on the setup.
        name : str, optional
            Name of the field plot to create.

        Returns
        -------
        :class:``ansys.aedt.core.modules.solutions.FieldPlot`` or bool
            Plot object.

        References
        ----------
        >>> oModule.CreateFieldPlot
        """
        intrinsics = self._check_intrinsics(intrinsics, setup=setup)
        if not setup:
            setup = self._app.existing_analysis_sweeps[0]
        if nets is None:
            nets = []
        if not (
            "APhi" in self.post_solution_type and settings.aedt_version >= "2023.2"
        ) and self._app.design_type not in ["HFSS", "HFSS 3D Layout Design"]:
            self.logger.error("This method requires AEDT 2023 R2 and Maxwell 3D Transient APhi Formulation.")
            return False
        if name and name in list(self.field_plots.keys()):
            self.logger.info(f"Plot {name} exists. returning the object.")
            return self.field_plots[name]

        if self._app.design_type in ["HFSS 3D Layout Design"]:
            lst_faces, new_layers = self._get_3dl_layers_nets(layers, nets, setup, include_dielectrics=True)
            if new_layers:
                plt = self._create_fieldplot(
                    new_layers, quantity, setup, intrinsics, "ObjList", name, create_plot=False
                )
                plt.surfaces = lst_faces
                out = plt.create()
                if out:
                    return plt
                return False
            else:
                return self._create_fieldplot(lst_faces, quantity, setup, intrinsics, "FacesList", name)
        else:
            dielectrics, new_layers = self._get_3d_layers_nets(layers, nets)
            if plot_on_surface:
                plot_type = "LayerNetsExtFace"
            else:
                plot_type = "LayerNets"
            if new_layers:
                plt = self._create_fieldplot(
                    new_layers, quantity, setup, intrinsics, plot_type, name, create_plot=False
                )
                if dielectrics:
                    plt.volumes = dielectrics
                out = plt.create()
                if out:
                    return plt
            elif dielectrics:
                return self._create_fieldplot(dielectrics, quantity, setup, intrinsics, "ObjList", name)
            return False

    @pyaedt_function_handler()
    def create_fieldplot_nets(
        self, nets, quantity, setup=None, layers=None, plot_on_surface=True, intrinsics=None, name=None
    ):
        # type: (list, str, str, list, bool, dict, str) -> FieldPlot
        """Create a field plot of stacked layer plot based on a net selections.

        Layers can be used as a filter.
        Dielectrics will be excluded from the plot.
        This plot is valid from AEDT 2023 R2 and later in HFSS 3D Layout.
        It works when a layout components in 3d modeler is used.

        Parameters
        ----------
        nets : list, optional
            List of nets to filter the field plot.
        quantity : str
            Name of the quantity to plot.
        setup : str, optional
            Name of the setup. The default is ``None``, in which case the ``nominal_adaptive``
            setup is used. Make sure to build a setup string in the form of
            ``"SetupName : SetupSweep"``, where ``SetupSweep`` is the sweep name to
            use in the export or ``LastAdaptive``.
        layers : list, optional
            List of layers to plot. For example:
            ``["Layer1","Layer2"]``. If empty list is provided
            all layers are considered.
        intrinsics : dict, str, optional
            Intrinsic variables required to compute the field before the export.
            These are typically: frequency, time and phase.
            It can be provided either as a dictionary or as a string.
            If it is a dictionary, keys depend on the solution type and can be expressed in lower or camel case as:

            - ``"Freq"`` or ``"Frequency"``.
            - ``"Time"``.
            - ``"Phase"``.

            If it is a string, it can either be ``"Freq"`` or ``"Time"`` depending on the solution type.
            The default is ``None`` in which case the intrinsics value is automatically computed based on the setup.
        plot_on_surface : bool, optional
            Whether if the plot has to be on surfaces or inside the objects.
            It is applicable only to layout components. Default is ``True``.
        name : str, optional
            Name of the field plot to create.

        Returns
        -------
        :class:``ansys.aedt.core.modules.solutions.FieldPlot`` or bool
            Plot object.

        References
        ----------
        >>> oModule.CreateFieldPlot
        """
        intrinsics = self._check_intrinsics(intrinsics, setup=setup)
        if not setup:
            setup = self._app.existing_analysis_sweeps[0]
        if nets is None:
            nets = []
        if not (
            "APhi" in self.post_solution_type and settings.aedt_version >= "2023.2"
        ) and self._app.design_type not in ["HFSS", "HFSS 3D Layout Design"]:
            self.logger.error("This method requires AEDT 2023 R2 and Maxwell 3D Transient APhi Formulation.")
            return False
        if name and name in list(self.field_plots.keys()):
            self.logger.info(f"Plot {name} exists. returning the object.")
            return self.field_plots[name]

        if self._app.design_type in ["HFSS 3D Layout Design"]:
            lst_faces, new_layers = self._get_3dl_layers_nets(layers, nets, setup, include_dielectrics=False)
            return self._create_fieldplot(lst_faces, quantity, setup, intrinsics, "FacesList", name)
        else:
            _, new_layers = self._get_3d_layers_nets(layers, nets)
            if plot_on_surface:
                plot_type = "LayerNetsExtFace"
            else:
                plot_type = "LayerNets"
            return self._create_fieldplot(new_layers, quantity, setup, intrinsics, plot_type, name)

    @pyaedt_function_handler(quantity_name="quantity", setup_name="setup")
    def create_fieldplot_layers_nets(
        self, layers_nets, quantity, setup=None, intrinsics=None, plot_on_surface=True, plot_name=None
    ):
        # type: (list, str, str, dict, bool, str) -> FieldPlot
        """Create a field plot of stacked layer plot on specified matrix of layers and nets.

        This plot is valid from AEDT 2023 R2 and later in HFSS 3D Layout
        and any modeler where a layout component is used.

        Parameters
        ----------
        layers_nets : list
            List of layers and nets to plot. For example:
            ``[["Layer1", "GND", "PWR"], ["Layer2", "VCC"], ...]``. If ``"no-layer"`` is provided as first argument,
            all layers are considered. If ``"no-net"`` is provided or the list contains only layer name, all the
            nets are automatically considered.
        quantity : str
            Name of the quantity to plot.
        setup : str, optional
            Name of the setup. The default is ``None``, in which case the ``nominal_adaptive``
            setup is used. Make sure to build a setup string in the form of
            ``"SetupName : SetupSweep"``, where ``SetupSweep`` is the sweep name to
            use in the export or ``LastAdaptive``.
        intrinsics : dict, str, optional
            Intrinsic variables required to compute the field before the export.
            These are typically: frequency, time and phase.
            It can be provided either as a dictionary or as a string.
            If it is a dictionary, keys depend on the solution type and can be expressed in lower or camel case as:

            - ``"Freq"`` or ``"Frequency"``.
            - ``"Time"``.
            - ``"Phase"``.

            If it is a string, it can either be ``"Freq"`` or ``"Time"`` depending on the solution type.
            The default is ``None`` in which case the intrinsics value is automatically computed based on the setup.
        plot_on_surface : bool, optional
            Whether if the plot has to be on surfaces or inside the objects.
            It is applicable only to layout components. Default is ``True``.
        plot_name : str, optional
            Name of the field plot to create.

        Returns
        -------
        :class:``ansys.aedt.core.modules.solutions.FieldPlot``
            Plot object.

        References
        ----------
        >>> oModule.CreateFieldPlot
        """
        intrinsics = self._check_intrinsics(intrinsics, setup=setup)
        if not (
            "APhi" in self.post_solution_type and settings.aedt_version >= "2023.2"
        ) and self._app.design_type not in ["HFSS", "HFSS 3D Layout Design"]:
            self.logger.error("This method requires AEDT 2023 R2 and Maxwell 3D Transient APhi Formulation.")
            return False
        if intrinsics is None:
            intrinsics = {}
        if plot_name and plot_name in list(self.field_plots.keys()):
            self.logger.info(f"Plot {plot_name} exists. returning the object.")
            return self.field_plots[plot_name]
        if self._app.design_type == "HFSS 3D Layout Design":
            if not setup:
                setup = self._app.existing_analysis_sweeps[0]
            lst = []
            if len(layers_nets) == 0:
                dicts_in = self._get_all_3dl_layers_nets(setup)
                for _, v in dicts_in.items():
                    lst.extend(v)
            for layer in layers_nets:
                if len(layer) == 1:
                    dicts_in = self._get_all_3dl_layers_nets(setup)
                    for v, i in dicts_in.items():
                        if v.split("/")[1] == layer[0] or v.split("/")[0] == layer[0]:
                            lst.extend(i)
                for el in layer[1:]:
                    el = "<no-net>" if el == "no-net" else el
                    try:
                        get_ids = self._odesign.GetGeometryIdsForNetLayerCombination(el, layer[0], setup)
                    except Exception:  # pragma no cover
                        get_ids = []
                    if isinstance(get_ids, (tuple, list)) and len(get_ids) > 2:
                        lst.extend([int(i) for i in get_ids[2:]])
            return self._create_fieldplot(lst, quantity, setup, intrinsics, "FacesList", plot_name)
        else:
            new_list = []
            for layer in layers_nets:
                if "no-layer" in layer[0]:
                    for v in self._app.modeler.user_defined_components.values():
                        new_list.extend(
                            [[i] + layer[1:] for i in v.layout_component.edb_object.stackup.signal_layers.keys()]
                        )
                else:
                    new_list.append(layer)
            layers_nets = new_list
            for layer in layers_nets:
                if len(layer) == 1 or "no-net" in layer[1]:
                    for v in self._app.modeler.user_defined_components.values():
                        if layer[0] in v.layout_component.edb_object.stackup.stackup_layers:
                            layer.extend(list(v.layout_component.edb_object.nets.nets.keys()))
            if plot_on_surface:
                plot_type = "LayerNetsExtFace"
            else:
                plot_type = "LayerNets"
            return self._create_fieldplot(layers_nets, quantity, setup, intrinsics, plot_type, plot_name)
