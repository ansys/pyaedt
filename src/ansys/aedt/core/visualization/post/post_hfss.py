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
This module contains the `PostProcessor3D` class.

It contains all advanced postprocessing functionalities for creating and editing plots in the 3D tools.
"""

from ansys.aedt.core.base import PyAedtBase
from ansys.aedt.core.generic.general_methods import pyaedt_function_handler
from ansys.aedt.core.visualization.post.post_3dlayout import PostProcessor3DLayout
from ansys.aedt.core.visualization.post.post_common_3d import PostProcessor3D
from ansys.aedt.core.visualization.post.vrt_data import VRTFieldPlot


class PostProcessorHFSS(PostProcessor3D, PyAedtBase):
    """Manages the specific HFSS postprocessing functions.

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

    @pyaedt_function_handler(expression="expressions", families_dict="sweeps")
    def get_far_field_data(self, expressions="GainTotal", setup_sweep_name="", domain="Infinite Sphere1", sweeps=None):
        """Generate far field data using the ``GetSolutionDataPerVariation()`` method.

        This method returns the data ``solData``, ``ThetaVals``,
        ``PhiVals``, ``ScanPhiVals``, ``ScanThetaVals``, and
        ``FreqVals``.

        Parameters
        ----------
        expressions : str or list, optional
            One or more formulas to add to the report. The default is ``"GainTotal"``.
        setup_sweep_name : str, optional
            Name of the setup for computing the report. The default is ``""``,
            in which case the nominal sweep is used.
        domain : str, dict, optional
            Context type (sweep or time). The default is ``"Infinite Sphere1"``.
        sweeps : dict, optional
            Dictionary of variables and values. The default is ``{"Freq": ["All"]}``.

        Returns
        -------
        :class:`ansys.aedt.core.modules.solutions.SolutionData`

        References
        ----------
        >>> oModule.GetSolutionDataPerVariation
        """
        if not isinstance(expressions, list):
            expressions = [expressions]
        if not setup_sweep_name:
            setup_sweep_name = self._app.nominal_adaptive
        if sweeps is None:
            sweeps = {"Theta": ["All"], "Phi": ["All"], "Freq": ["All"]}
        context = ["Context:=", domain]
        if isinstance(domain, dict):
            if "Context" in domain.keys() and "SourceContext" in domain.keys():
                context = ["Context:=", domain["Context"], "Context:=", domain["SourceContext"]]

        solution_data = self.get_solution_data_per_variation(
            "Far Fields", setup_sweep_name, context, sweeps, expressions
        )
        if not solution_data:
            print("No Data Available. Check inputs")
            return False
        return solution_data

    @pyaedt_function_handler()
    def create_creeping_plane_visual_ray_tracing(
        self,
        max_frequency="1GHz",
        ray_density=1,
        sample_density=10,
        ray_cutoff=40,
        irregular_surface_tolerance=50,
        incident_theta=0,
        incident_phi=0,
        is_vertical_polarization=False,
    ):
        """Create a Creeping Wave Plane Wave Visual Ray Tracing and return the class object.

        Parameters
        ----------
        max_frequency : str, optional
            Maximum Frequency. Default is ``"1GHz"``.
        ray_density : int, optional
            Ray Density. Default is ``2``.
        sample_density : int, optional
            Sample density. Default is ``10``.
        ray_cutoff : int, optional
            Ray Cutoff number. Default is ``40``.
        irregular_surface_tolerance : int, optional
            Irregular Surface Tolerance value. Default is ``50``.
        incident_theta : str, optional
            Incident plane wave theta. Default is ``"0deg"``.
        incident_phi : str, optional
            Incident plane wave phi. Default is ``"0deg"``.
        is_vertical_polarization : bool, optional
            Whether if enable or Vertical Polarization or not. Default is ``False``.

        Returns
        -------
        :class:` from ansys.aedt.core.modules.solutions.VRTFieldPlot`
        """
        vrt = VRTFieldPlot(self, is_creeping_wave=True)
        vrt.max_frequency = max_frequency
        vrt.sample_density = sample_density
        vrt.ray_density = ray_density
        vrt.ray_cutoff = ray_cutoff
        vrt.irregular_surface_tolerance = irregular_surface_tolerance
        vrt.is_plane_wave = True
        vrt.incident_theta = incident_theta
        vrt.incident_phi = incident_phi
        vrt.vertical_polarization = is_vertical_polarization
        vrt.create()
        return vrt

    @pyaedt_function_handler()
    def create_creeping_point_visual_ray_tracing(
        self,
        max_frequency="1GHz",
        ray_density=1,
        sample_density=10,
        ray_cutoff=40,
        irregular_surface_tolerance=50,
        custom_location=None,
    ):
        """Create a Creeping Wave Point Source Visual Ray Tracing and return the class object.

        Parameters
        ----------
        max_frequency : str, optional
            Maximum Frequency. Default is ``"1GHz"``.
        ray_density : int, optional
            Ray Density. Default is ``2``.
        sample_density : int, optional
            Sample density. Default is ``10``.
        ray_cutoff : int, optional
            Ray Cutoff number. Default is ``40``.
        irregular_surface_tolerance : int, optional
            Irregular Surface Tolerance value. Default is ``50``.
        custom_location : list, optional
            List of x, y,z position of point source. Default is ``None``.

        Returns
        -------
        :class:` from ansys.aedt.core.modules.solutions.VRTFieldPlot`
        """
        if custom_location is None:
            custom_location = [0, 0, 0]
        vrt = VRTFieldPlot(self, is_creeping_wave=True)
        vrt.max_frequency = max_frequency
        vrt.sample_density = sample_density
        vrt.ray_density = ray_density
        vrt.ray_cutoff = ray_cutoff
        vrt.irregular_surface_tolerance = irregular_surface_tolerance
        vrt.is_plane_wave = False
        vrt.custom_location = custom_location
        vrt.create()
        return vrt

    @pyaedt_function_handler()
    def create_sbr_plane_visual_ray_tracing(
        self,
        max_frequency="1GHz",
        ray_density=2,
        number_of_bounces=5,
        multi_bounce=False,
        mbrd_max_sub_division=2,
        shoot_utd=False,
        incident_theta=0,
        incident_phi=0,
        is_vertical_polarization=False,
        shoot_filter_type="All Rays",
        ray_index_start=0,
        ray_index_stop=1,
        ray_index_step=1,
        ray_box=None,
    ):
        """Create an SBR Plane Wave Visual Ray Tracing and return the class object.

        Parameters
        ----------
        max_frequency : str, optional
            Maximum Frequency. Default is ``"1GHz"``.
        ray_density : int, optional
            Ray Density. Default is ``2``.
        number_of_bounces : int, optional
            Maximum number of bounces. Default is ``5``.
        multi_bounce : bool, optional
            Whether if enable or not Multi-Bounce ray density control. Default is ``False``.
        mbrd_max_sub_division : int, optional
            Maximum number of MBRD subdivisions. Default is ``2``.
        shoot_utd : bool, optional
            Whether if enable or UTD Rays shooting or not. Default is ``False``.
        incident_theta : str, optional
            Incident plane wave theta. Default is ``"0deg"``.
        incident_phi : str, optional
            Incident plane wave phi. Default is ``"0deg"``.
        is_vertical_polarization : bool, optional
            Whether if enable or Vertical Polarization or not. Default is ``False``.
        shoot_filter_type : str, optional
            Shooter Type. Default is ``"All Rays"``. Options are  ``"Rays by index"``,  ``"Rays in box"``.
        ray_index_start : int, optional
            Ray index start. Valid only if ``"Rays by index"`` is chosen.  Default is ``0``.
        ray_index_stop : int, optional
            Ray index stop. Valid only if ``"Rays by index"`` is chosen.  Default is ``1``.
        ray_index_step : int, optional
            Ray index step. Valid only if ``"Rays by index"`` is chosen.  Default is ``1``.
        ray_box : int or str optional
            Ray box name or id. Valid only if ``"Rays by box"`` is chosen.  Default is ``None``.

        Returns
        -------
        :class:` from ansys.aedt.core.modules.solutions.VRTFieldPlot`
        """
        vrt = VRTFieldPlot(self, is_creeping_wave=False)
        vrt.max_frequency = max_frequency
        vrt.ray_density = ray_density
        vrt.number_of_bounces = number_of_bounces
        vrt.multi_bounce_ray_density_control = multi_bounce
        vrt.mbrd_max_subdivision = mbrd_max_sub_division
        vrt.shoot_utd_rays = shoot_utd
        vrt.shoot_type = shoot_filter_type
        vrt.is_plane_wave = True
        vrt.incident_theta = incident_theta
        vrt.incident_phi = incident_phi
        vrt.vertical_polarization = is_vertical_polarization
        vrt.start_index = ray_index_start
        vrt.stop_index = ray_index_stop
        vrt.step_index = ray_index_step
        vrt.ray_box = ray_box
        vrt.create()
        return vrt

    @pyaedt_function_handler()
    def create_sbr_point_visual_ray_tracing(
        self,
        max_frequency="1GHz",
        ray_density=2,
        number_of_bounces=5,
        multi_bounce=False,
        mbrd_max_sub_division=2,
        shoot_utd=False,
        custom_location=None,
        shoot_filter_type="All Rays",
        ray_index_start=0,
        ray_index_stop=1,
        ray_index_step=1,
        ray_box=None,
    ):
        """Create an SBR Point Source Visual Ray Tracing and return the class object.

        Parameters
        ----------
        max_frequency : str, optional
            Maximum Frequency. Default is ``1GHz``.
        ray_density : int, optional
            Ray Density. Default is ``2``.
        number_of_bounces : int, optional
            Maximum number of bounces. Default is ``5``.
        multi_bounce : bool, optional
            Whether if enable or not Multi-Bounce ray density control. Default is ``False``.
        mbrd_max_sub_division : int, optional
            Maximum number of MBRD subdivisions. Default is ``2``.
        shoot_utd : bool, optional
            Whether if enable or UTD Rays shooting or not. Default is ``False``.
        custom_location : list, optional
            List of x, y,z position of point source. Default is ``None``.
        shoot_filter_type : str, optional
            Shooter Type. Default is ``"All Rays"``. Options are ``Rays by index``, ``Rays in box``.
        ray_index_start : int, optional
            Ray index start. Valid only if ``Rays by index`` is chosen.  Default is ``0``.
        ray_index_stop : int, optional
            Ray index stop. Valid only if ``Rays by index`` is chosen.  Default is ``1``.
        ray_index_step : int, optional
            Ray index step. Valid only if ``Rays by index`` is chosen.  Default is ``1``.
        ray_box : int or str optional
            Ray box name or id. Valid only if ``Rays by box`` is chosen.  Default is ``None``.

        Returns
        -------
        :class:` from ansys.aedt.core.modules.solutions.VRTFieldPlot`

        """
        if custom_location is None:
            custom_location = [0, 0, 0]
        vrt = VRTFieldPlot(self, is_creeping_wave=False)
        vrt.max_frequency = max_frequency
        vrt.ray_density = ray_density
        vrt.number_of_bounces = number_of_bounces
        vrt.multi_bounce_ray_density_control = multi_bounce
        vrt.mbrd_max_subdivision = mbrd_max_sub_division
        vrt.shoot_utd_rays = shoot_utd
        vrt.shoot_type = shoot_filter_type
        vrt.is_plane_wave = False
        vrt.custom_location = custom_location
        vrt.start_index = ray_index_start
        vrt.stop_index = ray_index_stop
        vrt.step_index = ray_index_step
        vrt.ray_box = ray_box
        vrt.create()
        return vrt

    @pyaedt_function_handler()
    def set_tuning_offset(self, setup, offsets):
        """Set derivative variable to a specific offset value.

        Parameters
        ----------
        setup : str
            Setup name.
        offsets : dict
            Dictionary containing the variable name and it's offset value.

        Returns
        -------
        bool
        """
        setup_obj = self._app.get_setup(setup)
        if setup_obj and "set_tuning_offset" in dir(setup_obj):
            return setup_obj.set_tuning_offset(offsets)
        self.logger.error("Tuning offset applies only to solved setup with derivatives enabled.")
        return False

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
