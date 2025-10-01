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

"""
Defines the `PostProcessor3D` class.

It contains all advanced postprocessing functionalities for creating and editing plots in the 3D tools.
"""

import secrets
import string

from ansys.aedt.core.base import PyAedtBase
from ansys.aedt.core.generic.general_methods import pyaedt_function_handler
from ansys.aedt.core.visualization.post.field_data import FieldPlot
from ansys.aedt.core.visualization.post.post_3dlayout import PostProcessor3DLayout
from ansys.aedt.core.visualization.post.post_common_3d import PostProcessor3D


class PostProcessorMaxwell(PostProcessor3D, PyAedtBase):
    """Manages the specific Maxwell postprocessing functions.

    .. note::
       Some functionalities are available only when AEDT is running in the graphical mode.

    Parameters
    ----------
    app : :class:`ansys.aedt.core.application.analysis_3d.FieldAnalysis3D`
        Inherited parent object. The parent object must provide the members
        `_modeler`, `_desktop`, `_odesign`, and `logger`.

    """

    def __init__(self, app):
        PostProcessor3D.__init__(self, app)
        self.post_3dlayout = PostProcessor3DLayout(app)

    @pyaedt_function_handler(quantityName="quantity", setup_name="setup")
    def _create_fieldplot_line_traces(
        self,
        seeding_faces_ids,
        in_volume_tracing_ids,
        surface_tracing_ids,
        quantity,
        setup,
        intrinsics,
        plot_name=None,
        field_type="",
    ):
        if not setup:
            setup = self._app.existing_analysis_sweeps[0]
        if not intrinsics:
            for i in self._app.setups:
                if i.name == setup.split(" : ")[0]:
                    intrinsics = i.default_intrinsics
        self._app.desktop_class.close_windows()
        try:
            self._app.modeler.fit_all()
        except Exception:  # pragma: no cover
            self.logger.debug("Something went wrong with `fit_all` while creating field plot with line traces.")
        self._desktop.TileWindows(0)
        self._app.desktop_class.active_design(self._oproject, self._app.design_name)

        char_set = string.ascii_uppercase + string.digits
        if not plot_name:
            plot_name = quantity + "_" + "".join(secrets.choice(char_set) for _ in range(6))
        plot = FieldPlot(
            self,
            objects=in_volume_tracing_ids,
            surfaces=surface_tracing_ids,
            solution=setup,
            quantity=quantity,
            intrinsics=intrinsics,
            seeding_faces=seeding_faces_ids,
        )
        if field_type:
            plot.field_type = field_type
        plot.name = plot_name
        plot.plot_folder = plot_name

        plt = plot.create()
        if plt:
            self.field_plots[plot_name] = plot
            return plot
        else:
            return False

    @pyaedt_function_handler(IntrinsincDict="intrinsics", setup_name="setup")
    def create_fieldplot_line_traces(
        self,
        seeding_faces,
        in_volume_tracing_objs=None,
        surface_tracing_objs=None,
        setup=None,
        intrinsics=None,
        plot_name=None,
        field_type="DC R/L Fields",
    ):
        """
        Create a field plot of the line.

        Parameters
        ----------
        seeding_faces : list
            List of seeding faces.
        in_volume_tracing_objs : list
            List of the in-volume tracing objects.
        surface_tracing_objs : list
            List of the surface tracing objects.
        setup : str, optional
            Name of the setup in the format ``"setupName : sweepName"``. The default
            is ``None``.
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
        plot_name : str, optional
            Name of the field plot to create. The default is ``None``.
        field_type : str, optional
            Field type to plot. Valid only for Q3D Field plots.

        Returns
        -------
        type
            Plot object.

        References
        ----------
        >>> oModule.CreateFieldPlot

        Examples
        --------
        >>> from ansys.aedt.core import Maxwell2d
        >>> aedtapp = Maxwell2d()
        >>> # Intrinsics is provided as a dictionary.
        >>> intrinsics = {"Freq": "5GHz", "Phase": "180deg"}
        >>> min_value = aedtapp.post.get_scalar_field_value(quantity_name, "Minimum", setup_name, intrinsics=intrinsics)
        >>> plot1 = aedtapp.post.create_fieldplot_line_traces(seeding_faces=["Ground", "Electrode", "Region"],
        >>>                                                   in_volume_tracing_objs="Region",
        >>>                                                   plot_name="LineTracesTest",
        >>>                                                   intrinsics=intrinsics)
        >>> # Intrinsics is provided as a string. Phase is automatically assigned to 0deg.
        >>> min_value = aedtapp.post.get_scalar_field_value(quantity_name, "Minimum", setup_name, intrinsics="5GHz")
        >>> plot1 = aedtapp.post.create_fieldplot_line_traces(seeding_faces=["Ground", "Electrode", "Region"],
        >>>                                                   in_volume_tracing_objs="Region",
        >>>                                                   plot_name="LineTracesTest",
        >>>                                                   intrinsics="200Hz")
        """
        intrinsics = self._check_intrinsics(intrinsics, setup=setup)
        if self._app.solution_type != "Electrostatic":
            self.logger.error("Field line traces is valid only for electrostatic solution")
            return False
        if plot_name and plot_name in list(self.field_plots.keys()):
            self.logger.info(f"Plot {plot_name} exists. returning the object.")
            return self.field_plots[plot_name]
        if not isinstance(seeding_faces, list):
            seeding_faces = [seeding_faces]
        seeding_faces_ids = []
        for face in seeding_faces:
            if self._app.modeler[face]:
                seeding_faces_ids.append(self._app.modeler[face].id)
            else:
                self.logger.error(f"Object {face} doesn't exist in current design")
                return False
        in_volume_tracing_ids = []
        if not in_volume_tracing_objs:
            in_volume_tracing_ids.append(0)
        elif not isinstance(in_volume_tracing_objs, list):
            in_volume_tracing_objs = [in_volume_tracing_objs]
            for obj in in_volume_tracing_objs:
                if self._app.modeler[obj]:
                    in_volume_tracing_ids.append(self._app.modeler[obj].id)
                else:
                    self.logger.error(f"Object {obj} doesn't exist in current design")
                    return False
        elif isinstance(in_volume_tracing_objs, list):
            for obj in in_volume_tracing_objs:
                if not self._app.modeler[obj]:
                    self.logger.error(f"Object {obj} doesn't exist in current design")
                    return False
        surface_tracing_ids = []
        if not surface_tracing_objs:
            surface_tracing_ids.append(0)
        elif not isinstance(surface_tracing_objs, list):
            surface_tracing_objs = [surface_tracing_objs]
            for obj in surface_tracing_objs:
                if self._app.modeler[obj]:
                    surface_tracing_ids.append(self._app.modeler[obj].id)
                else:
                    self.logger.error(f"Object {obj} doesn't exist in current design")
                    return False
        elif isinstance(surface_tracing_objs, list):
            for obj in surface_tracing_objs:
                if not self._app.modeler[obj]:
                    self.logger.error(f"Object {obj} doesn't exist in current design")
                    return False
        seeding_faces_ids.insert(0, len(seeding_faces_ids))
        if in_volume_tracing_ids != [0]:
            in_volume_tracing_ids.insert(0, len(in_volume_tracing_ids))
        if surface_tracing_ids != [0]:
            surface_tracing_ids.insert(0, len(surface_tracing_ids))
        return self._create_fieldplot_line_traces(
            seeding_faces_ids,
            in_volume_tracing_ids,
            surface_tracing_ids,
            "FieldLineTrace",
            setup,
            intrinsics,
            plot_name,
            field_type=field_type,
        )

    @pyaedt_function_handler()
    def create_fieldplot_layers(
        self, layers, quantity, setup=None, nets=None, plot_on_surface=True, intrinsics=None, name=None
    ):
        # type: (list, str, str, list, bool, dict, str) -> FieldPlot
        """Create a field plot of stacked layer plot.

        This plot is valid from AEDT 2023 R2 and later. Nets can be used as a filter.
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
        return self.post_3dlayout.create_fieldplot_layers(
            layers, quantity, setup, nets, plot_on_surface, intrinsics, name
        )

    @pyaedt_function_handler()
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
        return self.post_3dlayout.create_fieldplot_layers_nets(
            layers_nets, quantity, setup, intrinsics, plot_on_surface, plot_name
        )
