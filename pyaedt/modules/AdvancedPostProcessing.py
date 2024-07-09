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

"""
This module contains the `PostProcessor` class.

It contains all advanced postprocessing functionalities that require Python 3.x packages like NumPy and Matplotlib.
"""

from __future__ import absolute_import  # noreorder

import csv
import os
import re
import warnings

from pyaedt import generate_unique_name
from pyaedt.generic.general_methods import is_ironpython
from pyaedt.generic.general_methods import open_file
from pyaedt.generic.general_methods import pyaedt_function_handler
from pyaedt.generic.plot import ModelPlotter
from pyaedt.generic.settings import settings
from pyaedt.modules.PostProcessor import FieldSummary
from pyaedt.modules.PostProcessor import PostProcessor as Post
from pyaedt.modules.PostProcessor import TOTAL_QUANTITIES
from pyaedt.modules.fields_calculator import FieldsCalculator

if not is_ironpython:
    try:
        import numpy as np
    except ImportError:
        warnings.warn(
            "The NumPy module is required to run some functionalities of PostProcess.\n"
            "Install with \n\npip install numpy\n\nRequires CPython."
        )

    try:
        from IPython.display import Image

        ipython_available = True
    except ImportError:
        ipython_available = False


class PostProcessor(Post):
    """Contains advanced postprocessing functionalities that require Python 3.x packages like NumPy and Matplotlib.

    Parameters
    ----------
    app :
        Inherited parent object.

    Examples
    --------
    Basic usage demonstrated with an HFSS, Maxwell, or any other design:

    >>> from pyaedt import Hfss
    >>> aedtapp = Hfss()
    >>> post = aedtapp.post
    """

    def __init__(self, app):
        Post.__init__(self, app)
        self.fields_calculator = FieldsCalculator(app)

    @pyaedt_function_handler()
    def nb_display(self, show_axis=True, show_grid=True, show_ruler=True):
        """Show the Jupyter Notebook display.

          .. note::
              .assign_curvature_extraction Jupyter Notebook is not supported by IronPython.

         Parameters
         ----------
         show_axis : bool, optional
             Whether to show the axes. The default is ``True``.
         show_grid : bool, optional
             Whether to show the grid. The default is ``True``.
         show_ruler : bool, optional
             Whether to show the ruler. The default is ``True``.

        Returns
        -------
        :class:`IPython.core.display.Image`
            Jupyter notebook image.

        """
        if ipython_available:
            file_name = self.export_model_picture(show_axis=show_axis, show_grid=show_grid, show_ruler=show_ruler)
            return Image(file_name, width=500)
        else:
            warnings.warn("The Ipython package is missing and must be installed.")

    @pyaedt_function_handler()
    def get_efields_data(self, setup_sweep_name="", ff_setup="Infinite Sphere1", freq="All"):
        """Compute Etheta and EPhi.

        .. warning::
           This method requires NumPy to be installed on your machine.


        Parameters
        ----------
        setup_sweep_name : str, optional
            Name of the setup for computing the report. The default is ``""``, in
            which case the nominal adaptive is applied.
        ff_setup : str, optional
            Far field setup. The default is ``"Infinite Sphere1"``.
        freq : str, optional
            The default is ``"All"``.

        Returns
        -------
        np.ndarray
            Numpy array containing ``[theta_range, phi_range, Etheta, Ephi]``.
        """
        if not setup_sweep_name:
            setup_sweep_name = self._app.nominal_adaptive
        results_dict = {}
        all_sources = self.post_osolution.GetAllSources()
        # assuming only 1 mode
        all_sources_with_modes = [s + ":1" for s in all_sources]

        for n, source in enumerate(all_sources_with_modes):
            edit_sources_ctxt = [["IncludePortPostProcessing:=", False, "SpecifySystemPower:=", False]]
            for m, each in enumerate(all_sources_with_modes):
                if n == m:  # set only 1 source to 1W, all the rest to 0
                    mag = 1
                else:
                    mag = 0
                phase = 0
                edit_sources_ctxt.append(
                    ["Name:=", "{}".format(each), "Magnitude:=", "{}W".format(mag), "Phase:=", "{}deg".format(phase)]
                )
            self.post_osolution.EditSources(edit_sources_ctxt)

            trace_name = "rETheta"
            solnData = self.get_far_field_data(
                expressions=trace_name, setup_sweep_name=setup_sweep_name, domain=ff_setup
            )

            data = solnData.nominal_variation

            theta_vals = np.degrees(np.array(data.GetSweepValues("Theta")))
            phi_vals = np.degrees(np.array(data.GetSweepValues("Phi")))
            # phi is outer loop
            theta_unique = np.unique(theta_vals)
            phi_unique = np.unique(phi_vals)
            theta_range = np.linspace(np.min(theta_vals), np.max(theta_vals), np.size(theta_unique))
            phi_range = np.linspace(np.min(phi_vals), np.max(phi_vals), np.size(phi_unique))
            real_theta = np.array(data.GetRealDataValues(trace_name))
            imag_theta = np.array(data.GetImagDataValues(trace_name))

            trace_name = "rEPhi"
            solnData = self.get_far_field_data(
                expressions=trace_name, setup_sweep_name=setup_sweep_name, domain=ff_setup
            )
            data = solnData.nominal_variation

            real_phi = np.array(data.GetRealDataValues(trace_name))
            imag_phi = np.array(data.GetImagDataValues(trace_name))

            Etheta = np.vectorize(complex)(real_theta, imag_theta)
            Ephi = np.vectorize(complex)(real_phi, imag_phi)
            source_name_without_mode = source.replace(":1", "")
            results_dict[source_name_without_mode] = [theta_range, phi_range, Etheta, Ephi]
        return results_dict

    @pyaedt_function_handler()
    def get_model_plotter_geometries(
        self,
        objects=None,
        plot_as_separate_objects=True,
        plot_air_objects=False,
        force_opacity_value=None,
        array_coordinates=None,
        generate_mesh=True,
        get_objects_from_aedt=True,
    ):
        """Initialize the Model Plotter object with actual modeler objects and return it.

        Parameters
        ----------
        objects : list, optional
            Optional list of objects to plot. If `None` all objects will be exported.
        plot_as_separate_objects : bool, optional
            Plot each object separately. It may require more time to export from AEDT.
        plot_air_objects : bool, optional
            Plot also air and vacuum objects.
        force_opacity_value : float, optional
            Opacity value between 0 and 1 to be applied to all model.
            If `None` aedt opacity will be applied to each object.
        array_coordinates : list of list
            List of array element centers. The modeler objects will be duplicated and translated.
            List of [[x1,y1,z1], [x2,y2,z2]...].
        generate_mesh : bool, optional
            Whether to generate the mesh after importing objects. The default is ``True``.
        get_objects_from_aedt : bool, optional
            Whether to export objects from AEDT and initialize them. The default is ``True``.

        Returns
        -------
        :class:`pyaedt.generic.plot.ModelPlotter`
            Model Object.
        """

        assert self._app._aedt_version >= "2021.2", self.logger.error("Object is supported from AEDT 2021 R2.")

        files = []
        if get_objects_from_aedt and self._app.solution_type not in ["HFSS3DLayout", "HFSS 3D Layout Design"]:
            files = self.export_model_obj(
                assignment=objects, export_as_single_objects=plot_as_separate_objects, air_objects=plot_air_objects
            )

        model = ModelPlotter()
        model.off_screen = True
        units = self.modeler.model_units
        for file in files:
            if force_opacity_value:
                model.add_object(file[0], file[1], force_opacity_value, units)
            else:
                model.add_object(file[0], file[1], file[2], units)
        model.array_coordinates = array_coordinates
        if generate_mesh:
            model.generate_geometry_mesh()
        return model

    @pyaedt_function_handler()
    def plot_model_obj(
        self,
        objects=None,
        show=True,
        export_path=None,
        plot_as_separate_objects=True,
        plot_air_objects=False,
        force_opacity_value=None,
        clean_files=False,
        array_coordinates=None,
        view="isometric",
        show_legend=True,
        dark_mode=False,
        show_bounding=False,
        show_grid=False,
    ):
        """Plot the model or a substet of objects.

        Parameters
        ----------
        objects : list, optional
            Optional list of objects to plot. If `None` all objects will be exported.
        show : bool, optional
            Show the plot after generation or simply return the
            generated Class for more customization before plot.
        export_path : str, optional
            If available, an image is saved to file. If `None` no image will be saved.
        plot_as_separate_objects : bool, optional
            Plot each object separately. It may require more time to export from AEDT.
        plot_air_objects : bool, optional
            Plot also air and vacuum objects.
        force_opacity_value : float, optional
            Opacity value between 0 and 1 to be applied to all model.
            If `None` aedt opacity will be applied to each object.
        clean_files : bool, optional
            Clean created files after plot. Cache is mainteined into the model object returned.
        array_coordinates : list of list
            List of array element centers. The modeler objects will be duplicated and translated.
            List of [[x1,y1,z1], [x2,y2,z2]...].
        view : str, optional
           View to export. Options are ``"isometric"``, ``"xy"``, ``"xz"``, ``"yz"``.
            The default is ``"isometric"``.
        show_legend : bool, optional
            Whether to display the legend or not. The default is ``True``.
        dark_mode : bool, optional
            Whether to display the model in dark mode or not. The default is ``False``.
        show_grid : bool, optional
            Whether to display the axes grid or not. The default is ``False``.
        show_bounding : bool, optional
            Whether to display the axes bounding box or not. The default is ``False``.

        Returns
        -------
        :class:`pyaedt.generic.plot.ModelPlotter`
            Model Object.
        """
        model = self.get_model_plotter_geometries(
            objects=objects,
            plot_as_separate_objects=plot_as_separate_objects,
            plot_air_objects=plot_air_objects,
            force_opacity_value=force_opacity_value,
            array_coordinates=array_coordinates,
            generate_mesh=False,
        )

        model.show_legend = show_legend
        model.off_screen = not show
        if dark_mode:
            model.background_color = [40, 40, 40]
        model.bounding_box = show_bounding
        model.show_grid = show_grid
        if view != "isometric" and view in ["xy", "xz", "yz"]:
            model.camera_position = view
        elif view != "isometric":
            self.logger.warning("Wrong view setup. It has to be one of xy, xz, yz, isometric.")
        if export_path:
            model.plot(export_path)
        elif show:
            model.plot()
        if clean_files:
            model.clean_cache_and_files(clean_cache=False)
        return model

    @pyaedt_function_handler(plotname="plot_name", meshplot="mesh_plot", imageformat="image_format")
    def plot_field_from_fieldplot(
        self,
        plot_name,
        project_path="",
        mesh_plot=False,
        image_format="jpg",
        view="isometric",
        plot_label="Temperature",
        plot_folder=None,
        show=True,
        scale_min=None,
        scale_max=None,
        plot_cad_objs=True,
        log_scale=True,
        dark_mode=False,
        show_grid=False,
        show_bounding=False,
        show_legend=True,
        plot_as_separate_objects=True,
        file_format="case",
    ):
        """Export a field plot to an image file (JPG or PNG) using Python PyVista.

        This method does not support streamlines plot.

        .. note::
           The PyVista module rebuilds the mesh and the overlap fields on the mesh.

        Parameters
        ----------
        plot_name : str
            Name of the field plot to export.
        project_path : str, optional
            Path for saving the image file. The default is ``""``.
        mesh_plot : bool, optional
            Whether to create and plot the mesh over the fields. The default is ``False``.
        image_format : str, optional
            Format of the image file. Options are ``"jpg"``, ``"png"``, ``"svg"``, and ``"webp"``.
            The default is ``"jpg"``.
        view : str, optional
           View to export. Options are ``"isometric"``, ``"xy"``, ``"xz"``, ``"yz"``.
        plot_label : str, optional
            Type of the plot. The default is ``"Temperature"``.
        plot_folder : str, optional
            Plot folder to update before exporting the field.
            The default is ``None``, in which case all plot folders are updated.
        show : bool, optional
            Export Image without plotting on UI.
        scale_min : float, optional
            Fix the Scale Minimum value.
        scale_max : float, optional
            Fix the Scale Maximum value.
        plot_cad_objs : bool, optional
            Whether to include objects in the plot. The default is ``True``.
        log_scale : bool, optional
            Whether to plot fields in log scale. The default is ``True``.
        dark_mode : bool, optional
            Whether to display the model in dark mode or not. The default is ``False``.
        show_grid : bool, optional
            Whether to display the axes grid or not. The default is ``False``.
        show_bounding : bool, optional
            Whether to display the axes bounding box or not. The default is ``False``.
        show_legend : bool, optional
            Whether to display the legend. The default is ``True``.
        plot_as_separate_objects : bool, optional
            Whether to plot each object separately, which can require
            more time to export from AEDT. The default is ``True``.
        file_format : str, optional
            File format to export the plot to. The default is ``"case".
            Options are ``"aedtplt"`` and ``"case"``.
            If the active design is a Q3D design, the file format is automatically
            set to ``"fldplt"``.

        Returns
        -------
        :class:`pyaedt.generic.plot.ModelPlotter`
            Model Object.
        """
        is_pcb = False
        if self._app.solution_type in ["HFSS3DLayout", "HFSS 3D Layout Design"]:
            is_pcb = True
        if not plot_folder:
            self.ofieldsreporter.UpdateAllFieldsPlots()
        else:
            self.ofieldsreporter.UpdateQuantityFieldsPlots(plot_folder)

        file_to_add = self.export_field_plot(plot_name, self._app.working_directory, file_format=file_format)
        model = self.get_model_plotter_geometries(
            generate_mesh=False,
            get_objects_from_aedt=plot_cad_objs,
            plot_as_separate_objects=plot_as_separate_objects,
        )
        model.show_legend = show_legend
        model.off_screen = not show
        if dark_mode:
            model.background_color = [40, 40, 40]
        model.bounding_box = show_bounding
        model.show_grid = show_grid
        if file_to_add:
            model.add_field_from_file(
                file_to_add,
                coordinate_units=self.modeler.model_units,
                show_edges=mesh_plot,
                log_scale=log_scale,
            )
            if plot_label:
                model.fields[0].label = plot_label

        if view != "isometric" and view in ["xy", "xz", "yz"]:
            model.camera_position = view
        elif view != "isometric":
            self.logger.warning("Wrong view setup. It has to be one of xy, xz, yz, isometric.")
        if is_pcb:
            model.z_scale = 5

        if scale_min and scale_max:
            model.range_min = scale_min
            model.range_max = scale_max
        if project_path:
            model.plot(os.path.join(project_path, plot_name + "." + image_format))
        elif show:
            model.plot()
        return model

    @pyaedt_function_handler(object_list="assignment", imageformat="image_format", setup_name="setup")
    def plot_field(
        self,
        quantity,
        assignment,
        plot_type="Surface",
        setup=None,
        intrinsics=None,
        mesh_on_fields=False,
        view="isometric",
        plot_label=None,
        show=True,
        scale_min=None,
        scale_max=None,
        plot_cad_objs=True,
        log_scale=False,
        export_path="",
        image_format="jpg",
        keep_plot_after_generation=False,
        dark_mode=False,
        show_bounding=False,
        show_grid=False,
        show_legend=True,
        filter_objects=None,
        plot_as_separate_objects=True,
    ):
        """Create a field plot  using Python PyVista and export to an image file (JPG or PNG).

        .. note::
           The PyVista module rebuilds the mesh and the overlap fields on the mesh.

        Parameters
        ----------
        quantity : str
            Quantity to plot. For example, ``"Mag_E"``.
        assignment : str, list
            One or more objects or faces to apply the field plot to.
        plot_type  : str, optional
            Plot type. The default is ``Surface``. Options are
            ``"CutPlane"``, ``"Surface"``, and ``"Volume"``.
        setup : str, optional
            Setup and sweep name on which create the field plot. Default is None for nominal setup usage.
        intrinsics : dict, optional.
            Intrinsic dictionary that is needed for the export.
            The default is ``None`` which try to retrieve intrinsics from setup.
        mesh_on_fields : bool, optional
            Whether to create and plot the mesh over the fields. The
            default is ``False``.
        view : str, optional
           View to export. Options are ``"isometric"``, ``"xy"``, ``"xz"``, ``"yz"``.
        plot_label : str, optional
            Type of the plot. The default is ``"Temperature"``.
        show : bool, optional
            Export Image without plotting on UI.
        scale_min : float, optional
            Fix the Scale Minimum value.
        scale_max : float, optional
            Fix the Scale Maximum value.
        plot_cad_objs : bool, optional
            Whether to include objects in the plot. The default is ``True``.
        log_scale : bool, optional
            Whether to plot fields in log scale. The default is ``False``.
        export_path : str, optional
            Image export path. Default is ``None`` to not export the image.
        image_format : str, optional
            Format of the image file. Options are ``"jpg"``, ``"png"``, ``"svg"``, and ``"webp"``.
            The default is ``"jpg"``.
        keep_plot_after_generation : bool, optional
            Either to keep the Field Plot in AEDT after the generation is completed. Default is ``False``.
        dark_mode : bool, optional
            Whether to display the model in dark mode or not. The default is ``False``.
        show_grid : bool, optional
            Whether to display the axes grid or not. The default is ``False``.
        show_bounding : bool, optional
            Whether to display the axes bounding box or not. The default is ``False``.
        show_legend : bool, optional
            Whether to display the legend or not. The default is ``True``.
        filter_objects : list, optional
            Objects list for filtering the ``CutPlane`` plots.
        plot_as_separate_objects : bool, optional
            Plot each object separately. It may require more time to export from AEDT.

        Returns
        -------
        :class:`pyaedt.generic.plot.ModelPlotter`
            Model Object.
        """
        if filter_objects is None:
            filter_objects = []
        if os.getenv("PYAEDT_DOC_GENERATION", "False").lower() in ("true", "1", "t"):  # pragma: no cover
            show = False
        if not setup:
            setup = self._app.existing_analysis_sweeps[0]
        if not intrinsics:
            for i in self._app.setups:
                if i.name == setup.split(" : ")[0]:
                    intrinsics = i.default_intrinsics

        # file_to_add = []
        if plot_type == "Surface":
            plotf = self.create_fieldplot_surface(assignment, quantity, setup, intrinsics)
        elif plot_type == "Volume":
            plotf = self.create_fieldplot_volume(assignment, quantity, setup, intrinsics)
        else:
            plotf = self.create_fieldplot_cutplane(
                assignment, quantity, setup, intrinsics, filter_objects=filter_objects
            )
        # if plotf:
        #     file_to_add = self.export_field_plot(plotf.name, self._app.working_directory, plotf.name)

        model = self.plot_field_from_fieldplot(
            plotf.name,
            export_path,
            mesh_on_fields,
            image_format,
            view,
            plot_label if plot_label else quantity,
            None,
            show,
            scale_min,
            scale_max,
            plot_cad_objs,
            log_scale,
            dark_mode=dark_mode,
            show_grid=show_grid,
            show_bounding=show_bounding,
            show_legend=show_legend,
            plot_as_separate_objects=plot_as_separate_objects,
        )
        if not keep_plot_after_generation:
            plotf.delete()
        return model

    @pyaedt_function_handler(object_list="assignment", variation_list="variations", setup_name="setup")
    def plot_animated_field(
        self,
        quantity,
        assignment,
        plot_type="Surface",
        setup=None,
        intrinsics=None,
        variation_variable="Phi",
        variations=None,
        view="isometric",
        show=True,
        scale_min=None,
        scale_max=None,
        plot_cad_objs=True,
        log_scale=True,
        zoom=None,
        export_gif=False,
        export_path="",
        force_opacity_value=0.1,
        dark_mode=False,
        show_grid=False,
        show_bounding=False,
        show_legend=True,
        filter_objects=None,
    ):
        """Create an animated field plot using Python PyVista and export to a gif file.

        .. note::
           The PyVista module rebuilds the mesh and the overlap fields on the mesh.

        Parameters
        ----------
        quantity : str
            Quantity to plot (for example, ``"Mag_E"``).
        assignment : list, str
            One or more objects or faces to apply the field plot to.
        plot_type  : str, optional
            Plot type. The default is ``Surface``. Options are
            ``"CutPlane"``, ``"Surface"``, and ``"Volume"``.
        setup : str, optional
            Setup and sweep name on which create the field plot. Default is None for nominal setup usage.
        intrinsics : dict, optional.
            Intrinsic dictionary that is needed for the export.
            The default is ``None`` which try to retrieve intrinsics from setup.
        variation_variable : str, optional
            Variable to vary. The default is ``"Phi"``.
        variations : list, optional
            List of variation values with units. The default is ``["0deg"]``.
        view : str, optional
           View to export. Options are ``"isometric"``, ``"xy"``, ``"xz"``, ``"yz"``.
        show : bool, optional
            Export Image without plotting on UI.
        scale_min : float, optional
            Fix the Scale Minimum value.
        scale_max : float, optional
            Fix the Scale Maximum value.
        plot_cad_objs : bool, optional
            Whether to include objects in the plot. The default is ``True``.
        log_scale : bool, optional
            Whether to plot fields in log scale. The default is ``True``.
        zoom : float, optional
            Zoom factor.
        export_gif : bool, optional
             Whether to export an animated gif or not. The default is ``False``.
        export_path : str, optional
            Image export path. Default is ``None`` to not ``working_directory`` will be used to save the image.
        force_opacity_value : float, optional
            Opacity value between 0 and 1 to be applied to all model.
            If `None` aedt opacity will be applied to each object.
        dark_mode : bool, optional
            Whether to display the model in dark mode or not. The default is ``False``.
        show_grid : bool, optional
            Whether to display the axes grid or not. The default is ``False``.
        show_bounding : bool, optional
            Whether to display the axes bounding box or not. The default is ``False``.
        show_legend : bool, optional
            Whether to display the legend or not. The default is ``True``.
        filter_objects : list, optional
            Objects list for filtering the ``CutPlane`` plots.
            The default is ``None`` in which case an empty list is passed.

        Returns
        -------
        :class:`pyaedt.generic.plot.ModelPlotter`
            Model Object.
        """
        if variations is None:
            variations = ["0deg"]
        if os.getenv("PYAEDT_DOC_GENERATION", "False").lower() in ("true", "1", "t"):  # pragma: no cover
            show = False
        if intrinsics is None:
            intrinsics = {}
        if not export_path:
            export_path = self._app.working_directory
        if not filter_objects:
            filter_objects = []

        v = 0
        fields_to_add = []
        is_intrinsics = True
        if variation_variable in self._app.variable_manager.independent_variables:
            is_intrinsics = False
        for el in variations:
            if is_intrinsics:
                intrinsics[variation_variable] = el
            else:
                self._app[variation_variable] = el
            if plot_type == "Surface":
                plotf = self.create_fieldplot_surface(assignment, quantity, setup, intrinsics)
            elif plot_type == "Volume":
                plotf = self.create_fieldplot_volume(assignment, quantity, setup, intrinsics)
            else:
                plotf = self.create_fieldplot_cutplane(
                    assignment, quantity, setup, intrinsics, filter_objects=filter_objects
                )
            if plotf:
                file_to_add = self.export_field_plot(plotf.name, export_path, plotf.name + str(v))
                if file_to_add:
                    fields_to_add.append(file_to_add)
                plotf.delete()
            v += 1
        model = self.get_model_plotter_geometries(
            generate_mesh=False, get_objects_from_aedt=plot_cad_objs, force_opacity_value=force_opacity_value
        )
        model.off_screen = not show
        if dark_mode:
            model.background_color = [40, 40, 40]
        model.bounding_box = show_bounding
        model.show_grid = show_grid
        model.show_legend = show_legend
        if fields_to_add:
            model.add_frames_from_file(fields_to_add, log_scale=log_scale)
        if export_gif:
            model.gif_file = os.path.join(self._app.working_directory, self._app.project_name + ".gif")
        if view != "isometric" and view in ["xy", "xz", "yz"]:
            model.camera_position = view
        elif view != "isometric":
            self.logger.warning("Wrong view setup. It has to be one of xy, xz, yz, isometric.")

        if scale_min and scale_max:
            model.range_min = scale_min
            model.range_max = scale_max
        if zoom:
            model.zoom = zoom
        if show or export_gif:
            model.animate()
        return model

    @pyaedt_function_handler(plotname="plot_name", variation_list="variations")
    def animate_fields_from_aedtplt(
        self,
        plot_name,
        plot_folder=None,
        variation_variable="Phase",
        variations=["0deg"],
        project_path="",
        export_gif=False,
        show=True,
        dark_mode=False,
        show_bounding=False,
        show_grid=False,
    ):
        """Generate a field plot to an image file (JPG or PNG) using PyVista.

        .. note::
           The PyVista module rebuilds the mesh and the overlap fields on the mesh.

        Parameters
        ----------
        plot_name : str
            Name of the plot or the name of the object.
        plot_folder : str, optional
            Name of the folder in which the plot resides. The default
            is ``None``.
        variation_variable : str, optional
            Variable to vary. The default is ``"Phase"``.
        variations : list, optional
            List of variation values with units. The default is
            ``["0deg"]``.
        project_path : str, optional
            Path for the export. The default is ``""``, in which case the file is exported
            to the working directory.
        export_gif : bool, optional
             Whether to export the GIF file. The default is ``False``.
        show : bool, optional
             Generate the animation without showing an interactive plot.  The default is ``True``.
        dark_mode : bool, optional
            Whether to display the model in dark mode or not. The default is ``False``.
        show_grid : bool, optional
            Whether to display the axes grid or not. The default is ``False``.
        show_bounding : bool, optional
            Whether to display the axes bounding box or not. The default is ``False``.

        Returns
        -------
        :class:`pyaedt.generic.plot.ModelPlotter`
            Model Object.
        """
        if not plot_folder:
            self.ofieldsreporter.UpdateAllFieldsPlots()
        else:
            self.ofieldsreporter.UpdateQuantityFieldsPlots(plot_folder)

        fields_to_add = []
        if not project_path:
            project_path = self._app.working_directory
        for el in variations:
            if plot_name in self.field_plots and variation_variable in self.field_plots[plot_name].intrinsics:
                self.field_plots[plot_name].intrinsics[variation_variable] = el
                self.field_plots[plot_name].update()
            else:
                self._app._odesign.ChangeProperty(
                    [
                        "NAME:AllTabs",
                        [
                            "NAME:FieldsPostProcessorTab",
                            ["NAME:PropServers", "FieldsReporter:" + plot_name],
                            ["NAME:ChangedProps", ["NAME:" + variation_variable, "Value:=", el]],
                        ],
                    ]
                )
            fields_to_add.append(
                self.export_field_plot(
                    plot_name, project_path, plot_name + variation_variable + str(el), file_format="case"
                )
            )

        model = self.get_model_plotter_geometries(generate_mesh=False)
        model.off_screen = not show
        if dark_mode:
            model.background_color = [40, 40, 40]
        model.bounding_box = show_bounding
        model.show_grid = show_grid
        if fields_to_add:
            model.add_frames_from_file(fields_to_add)
        if export_gif:
            model.gif_file = os.path.join(self._app.working_directory, self._app.project_name + ".gif")

        if show or export_gif:
            model.animate()
        return model

    @pyaedt_function_handler()
    def create_3d_plot(
        self,
        solution_data,
        nominal_sweep=None,
        nominal_value=None,
        primary_sweep="Theta",
        secondary_sweep="Phi",
        snapshot_path=None,
        show=True,
    ):
        """Create a 3D plot using Matplotlib.

        Parameters
        ----------
        solution_data : :class:`pyaedt.modules.solutions.SolutionData`
            Input data for the solution.
        nominal_sweep : str, optional
            Name of the nominal sweep. The default is ``None``.
        nominal_value : str, optional
            Value for the nominal sweep. The default is ``None``.
        primary_sweep : str, optional
            Primary sweep. The default is ``"Theta"``.
        secondary_sweep : str, optional
            Secondary sweep. The default is ``"Phi"``.
        snapshot_path : str, optional
            Full path to image file if a snapshot is needed.
            The default is ``None``.
        show : bool, optional
            Whether if show the plot or not. Default is set to `True`.

        Returns
        -------
         bool
             ``True`` when successful, ``False`` when failed.
        """
        if nominal_value:
            solution_data.intrinsics[nominal_sweep] = nominal_value
        if nominal_value:
            solution_data.primary_sweep = primary_sweep
        return solution_data.plot_3d(
            x_axis=primary_sweep, y_axis=secondary_sweep, snapshot_path=snapshot_path, show=show
        )

    @pyaedt_function_handler(frames_list="frames", output_gif_path="gif_path")
    def plot_scene(
        self,
        frames,
        gif_path,
        norm_index=0,
        dy_rng=0,
        fps=30,
        show=True,
        view="yz",
        zoom=2.0,
        convert_fields_in_db=False,
        log_multiplier=10.0,
    ):
        """Plot the current model 3D scene with overlapping animation coming from a file list and save the gif.


        Parameters
        ----------
        frames : list or str
            File list containing animation frames to plot in CSV format or
            path to a text index file containing the full path to CSV files.
        gif_path : str
            Full path for outputting the GIF file.
        norm_index : int, optional
            Frame to use to normalize your images.
            Data is already saved as dB : 100 for usual traffic scenes.
        dy_rng : int, optional
            Specify how many dB below you would like to specify the range_min.
            Tweak this a couple of times with small number of frames.
        fps : int, optional
            Frames per Second.
        show : bool, optional
            Either if show or only export gif.
        view : str, optional
           View to export. Options are ``"isometric"``, ``"xy"``, ``"xz"``, and ``"yz"``.
           The default is ``"isometric"``.
        zoom : float, optional
            Default zoom. Default Value is `2`.
        convert_fields_in_db : bool, optional
            Either if convert the fields before plotting in dB. Default Value is `False`.
        log_multiplier : float, optional
            Field multiplier if field in dB. Default Value is `10.0`.

        Returns
        -------

        """
        if isinstance(frames, str) and os.path.exists(frames):
            with open_file(frames, "r") as f:
                lines = f.read()
                temp_list = lines.splitlines()
            frames_paths_list = [i for i in temp_list]
        elif isinstance(frames, str):
            self.logger.error("Path doesn't exists")
            return False
        else:
            frames_paths_list = frames
        scene = self.get_model_plotter_geometries(generate_mesh=False)

        norm_data = np.loadtxt(frames_paths_list[norm_index], skiprows=1, delimiter=",")
        norm_val = norm_data[:, -1]
        v_max = np.max(norm_val)
        v_min = v_max - dy_rng
        scene.add_frames_from_file(frames_paths_list, log_scale=False, color_map="jet", header_lines=1, opacity=0.8)

        # Specifying the attributes of the scene through the ModelPlotter object
        scene.off_screen = not show
        if view != "isometric" and view in ["xy", "xz", "yz"]:
            scene.camera_position = view
        scene.range_min = v_min
        scene.range_max = v_max
        scene.show_grid = False
        scene.windows_size = [1920, 1080]
        scene.show_legend = False
        scene.show_boundingbox = False
        scene.legend = False
        scene.frame_per_seconds = fps
        scene.zoom = zoom
        scene.bounding_box = False
        scene.color_bar = False
        scene.gif_file = gif_path  # This GIF file may be a bit slower so it can be speed it up a bit
        scene.convert_fields_in_db = convert_fields_in_db
        scene.log_multiplier = log_multiplier
        scene.animate()


class IcepakPostProcessor(PostProcessor, object):
    def __init__(self, app):
        PostProcessor.__init__(self, app)

    @pyaedt_function_handler()
    def create_field_summary(self):
        return FieldSummary(self._app)

    @pyaedt_function_handler(timestep="time_step", design_variation="variation")
    def get_fans_operating_point(self, export_file=None, setup_name=None, time_step=None, variation=None):
        """
        Get the operating point of the fans in the design.

        Parameters
        ----------
        export_file : str, optional
            Name of the file to save the operating point of the fans to. The default is
            ``None``, in which case the filename is automatically generated.
        setup_name : str, optional
            Setup name to determine the operating point of the fans. The default is
            ``None``, in which case the first available setup is used.
        time_step : str, optional
            Time, with units, at which to determine the operating point of the fans. The default
            is ``None``, in which case the first available timestep is used. This parameter is
            only relevant in transient simulations.
        variation : str, optional
            Design variation to determine the operating point of the fans from. The default is
            ``None``, in which case the nominal variation is used.

        Returns
        -------
        list
            First element of the list is the CSV filename. The second and third elements
            are the quantities with units describing the operating point of the fans.
            The fourth element is a dictionary with the names of the fan instances
            as keys and lists with volumetric flow rates and pressure rise floats associated
            with the operating point as values.

        References
        ----------

        >>> oModule.ExportFanOperatingPoint

        Examples
        --------
        >>> from pyaedt import Icepak
        >>> ipk = Icepak()
        >>> ipk.create_fan()
        >>> filename, vol_flow_name, p_rise_name, op_dict= ipk.get_fans_operating_point()
        """

        if export_file is None:
            path = self._app.temp_directory
            base_name = "{}_{}_FanOpPoint".format(self._app.project_name, self._app.design_name)
            export_file = os.path.join(path, base_name + ".csv")
            while os.path.exists(export_file):
                file_name = generate_unique_name(base_name)
                export_file = os.path.join(path, file_name + ".csv")
        if setup_name is None:
            setup_name = "{} : {}".format(self._app.get_setups()[0], self._app.solution_type)
        if time_step is None:
            time_step = ""
            if self._app.solution_type == "Transient":
                self._app.logger.warning("No timestep is specified. First timestep is exported.")
        else:
            if not self._app.solution_type == "Transient":
                self._app.logger.warning("Simulation is steady-state. Timestep argument is ignored.")
                time_step = ""
        if variation is None:
            variation = ""
        self._app.osolution.ExportFanOperatingPoint(
            [
                "SolutionName:=",
                setup_name,
                "DesignVariationKey:=",
                variation,
                "ExportFilePath:=",
                export_file,
                "Overwrite:=",
                True,
                "TimeStep:=",
                time_step,
            ]
        )
        with open_file(export_file, "r") as f:
            reader = csv.reader(f)
            for line in reader:
                if "Fan Instances" in line:
                    vol_flow = line[1]
                    p_rise = line[2]
                    break
            var = {line[0]: [float(line[1]), float(line[2])] for line in reader}
        return [export_file, vol_flow, p_rise, var]

    @pyaedt_function_handler
    def _parse_field_summary_content(self, fs, setup_name, design_variation, quantity_name):
        content = fs.get_field_summary_data(setup=setup_name, variation=design_variation)
        pattern = r"\[([^]]*)\]"
        match = re.search(pattern, content["Quantity"][0])
        if match:
            content["Unit"] = [match.group(1)]
        else:  # pragma: no cover
            content["Unit"] = [None]

        if quantity_name in TOTAL_QUANTITIES:
            return {i: content[i][0] for i in ["Total", "Unit"]}
        return {i: content[i][0] for i in ["Min", "Max", "Mean", "Stdev", "Unit"]}

    @pyaedt_function_handler(faces_list="faces", quantity_name="quantity", design_variation="variation")
    def evaluate_faces_quantity(
        self,
        faces,
        quantity,
        side="Default",
        setup_name=None,
        variations=None,
        ref_temperature="",
    ):
        """Export the field surface output.

        Parameters
        ----------
        faces : list
            List of faces to apply.
        quantity : str
            Name of the quantity to export.
        side : str, optional
            Which side of the mesh face to use. The default is ``Default``.
            Options are ``"Adjacent"``, ``"Combined"``, and ``"Default"``.
        setup_name : str, optional
            Name of the setup and name of the sweep. For example, ``"IcepakSetup1 : SteatyState"``.
            The default is ``None``, in which case the active setup and active sweep are used.
        variations : dict, optional
            Dictionary of parameters defined for the specific setup with values. The default is ``{}``.
        ref_temperature: str, optional
            Reference temperature to use for heat transfer coefficient computation. The default is ``""``.

        Returns
        -------
        dict
            Output dictionary, which depending on the quantity chosen, contains one
            of these sets of keys:

            - ``"Min"``, ``"Max"``, ``"Mean"``, ``"Stdev"``, and ``"Unit"``
            - ``"Total"`` and ``"Unit"``

        References
        ----------

        >>> oModule.ExportFieldsSummary
        """
        if variations is None:
            variations = {}
        facelist_name = generate_unique_name(quantity)
        self._app.modeler.create_face_list(faces, facelist_name)
        fs = self.create_field_summary()
        fs.add_calculation("Object", "Surface", facelist_name, quantity, side=side, ref_temperature=ref_temperature)
        out = self._parse_field_summary_content(fs, setup_name, variations, quantity)
        self._app.oeditor.Delete(["NAME:Selections", "Selections:=", facelist_name])
        return out

    @pyaedt_function_handler(boundary_name="boundary", quantity_name="quantity", design_variation="variations")
    def evaluate_boundary_quantity(
        self,
        boundary,
        quantity,
        side="Default",
        volume=False,
        setup_name=None,
        variations=None,
        ref_temperature="",
    ):
        """Export the field output on a boundary.

        Parameters
        ----------
        boundary : str
            Name of boundary to perform the computation on.
        quantity : str
            Name of the quantity to export.
        side : str, optional
            Side of the mesh face to use. The default is ``"Default"``.
            Options are ``"Adjacent"``, ``"Combined"``, and ``"Default"``.
        volume : bool, optional
            Whether to compute the quantity on the volume or on the surface.
            The default is ``False``, in which case the quantity will be evaluated
            only on the surface .
        setup_name : str, optional
            Name of the setup and name of the sweep. For example, ``"IcepakSetup1 : SteatyState"``.
            The default is ``None``, in which case the active setup and active sweep are used.
        variations : dict, optional
            Dictionary of parameters defined for the specific setup with values. The default is ``{}``.
        ref_temperature: str, optional
            Reference temperature to use for heat transfer coefficient computation. The default is ``""``.

        Returns
        -------
        dict
            Output dictionary, which depending on the quantity chosen, contains one
            of these sets of keys:
            - ``"Min"``, ``"Max"``, ``"Mean"``, ``"Stdev"``, and ``"Unit"``
            - ``"Total"`` and ``"Unit"``

        References
        ----------

        >>> oModule.ExportFieldsSummary
        """
        if variations is None:
            variations = {}
        fs = self.create_field_summary()
        fs.add_calculation(
            "Boundary",
            ["Surface", "Volume"][int(volume)],
            boundary,
            quantity,
            side=side,
            ref_temperature=ref_temperature,
        )
        return self._parse_field_summary_content(fs, setup_name, variations, quantity)

    @pyaedt_function_handler(monitor_name="monitor", quantity_name="quantity", design_variation="variations")
    def evaluate_monitor_quantity(
        self,
        monitor,
        quantity,
        side="Default",
        setup_name=None,
        variations=None,
        ref_temperature="",
    ):
        """Export monitor field output.

        Parameters
        ----------
        monitor : str
            Name of monitor to perform the computation on.
        quantity : str
            Name of the quantity to export.
        side : str, optional
            Side of the mesh face to use. The default is ``"Default"``.
            Options are ``"Adjacent"``, ``"Combined"``, and ``"Default"``.
        setup_name : str, optional
            Name of the setup and name of the sweep. For example, ``"IcepakSetup1 : SteatyState"``.
            The default is ``None``, in which case the active setup and active sweep are used.
        variations : dict, optional
            Dictionary of parameters defined for the specific setup with values. The default is ``{}``.
        ref_temperature: str, optional
            Reference temperature to use for heat transfer coefficient computation. The default is ``""``.

        Returns
        -------
        dict
            Output dictionary, which depending on the quantity chosen, contains one
            of these sets of keys:

            - ``"Min"``, ``"Max"``, ``"Mean"``, ``"Stdev"``, and ``"Unit"``
            - ``"Total"`` and ``"Unit"``

        References
        ----------

        >>> oModule.ExportFieldsSummary
        """
        if variations is None:
            variations = {}
        if settings.aedt_version < "2024.1":
            raise NotImplementedError("Monitors are not supported in field summary in versions earlier than 2024 R1.")
        else:  # pragma: no cover
            if self._app.monitor.face_monitors.get(monitor, None):
                field_type = "Surface"
            elif self._app.monitor.point_monitors.get(monitor, None):
                field_type = "Volume"
            else:
                raise AttributeError("Monitor {} is not found in the design.".format(monitor))
            fs = self.create_field_summary()
            fs.add_calculation("Monitor", field_type, monitor, quantity, side=side, ref_temperature=ref_temperature)
            return self._parse_field_summary_content(fs, setup_name, variations, quantity)

    @pyaedt_function_handler(design_variation="variations")
    def evaluate_object_quantity(
        self,
        object_name,
        quantity_name,
        side="Default",
        volume=False,
        setup_name=None,
        variations=None,
        ref_temperature="",
    ):
        """Export the field output on or in an object.

        Parameters
        ----------
        object_name : str
            Name of object to perform the computation on.
        quantity_name : str
            Name of the quantity to export.
        side : str, optional
            Side of the mesh face to use. The default is ``"Default"``.
            Options are ``"Adjacent"``, ``"Combined"``, and ``"Default"``.
        volume : bool, optional
            Whether to compute the quantity on the volume or on the surface. The default is ``False``.
        setup_name : str, optional
            Name of the setup and name of the sweep. For example, ``"IcepakSetup1 : SteatyState"``.
            The default is ``None``, in which case the active setup and active sweep are used.
        variations : dict, optional
            Dictionary of parameters defined for the specific setup with values. The default is ``{}``.
        ref_temperature: str, optional
            Reference temperature to use for heat transfer coefficient computation. The default is ``""``.

        Returns
        -------
        dict
            Output dictionary, which depending on the quantity chosen, contains one
            of these sets of keys:

            - ``"Min"``, ``"Max"``, ``"Mean"``, ``"Stdev"``, and ``"Unit"``
            - ``"Total"`` and ``"Unit"``

        References
        ----------

        >>> oModule.ExportFieldsSummary
        """
        if variations is None:
            variations = {}
        fs = self.create_field_summary()
        fs.add_calculation(
            "Boundary",
            ["Surface", "Volume"][int(volume)],
            object_name,
            quantity_name,
            side=side,
            ref_temperature=ref_temperature,
        )
        return self._parse_field_summary_content(fs, setup_name, variations, quantity_name)
