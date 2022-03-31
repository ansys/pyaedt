"""
This module contains the `PostProcessor` class.

It contains all advanced postprocessing functionalities that require Python 3.x packages like NumPy and Matplotlib.
"""
from __future__ import absolute_import  # noreorder

import math
import os
import time
import warnings

from pyaedt.generic.general_methods import is_ironpython
from pyaedt.generic.general_methods import pyaedt_function_handler
from pyaedt.generic.plot import ModelPlotter
from pyaedt.modules.PostProcessor import PostProcessor as Post

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
        warnings.warn(
            "The Ipython module is required to run some functionalities of PostProcess.\n"
            "Install with \n\npip install ipython\n\nRequires CPython."
        )

    try:
        import matplotlib.pyplot as plt
    except ImportError:
        warnings.warn(
            "The Matplotlib module is required to run some functionalities of PostProcess.\n"
            "Install with \n\npip install matplotlib\n\nRequires CPython."
        )
    except:
        pass


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
        file_name = self.export_model_picture(show_axis=show_axis, show_grid=show_grid, show_ruler=show_ruler)
        return Image(file_name, width=500)

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
            numpy array containing ``[theta_range, phi_range, Etheta, Ephi]``.
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

            ctxt = ["Context:=", ff_setup]

            sweeps = ["Theta:=", ["All"], "Phi:=", ["All"], "Freq:=", [freq]]

            trace_name = "rETheta"
            solnData = self.get_far_field_data(
                setup_sweep_name=setup_sweep_name, domain=ff_setup, expression=trace_name
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
                setup_sweep_name=setup_sweep_name, domain=ff_setup, expression=trace_name
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
    def ff_sum_with_delta_phase(self, ff_data, xphase=0, yphase=0):
        """Generate a far field sum with a delta phase.

        Parameters
        ----------
        ff_data :

        xphase : float, optional
            Phase in the X-axis direction. The default is ``0``.
        yphase : float, optional
            Phase in the Y-axis direction. The default is ``0``.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.
        """
        array_size = [4, 4]
        loc_offset = 2

        rETheta = ff_data[2]
        rEPhi = ff_data[3]
        weight = np.zeros((array_size[0], array_size[0]))
        mag = np.ones((array_size[0], array_size[0]))
        for m in range(array_size[0]):
            for n in range(array_size[1]):
                mag = mag[m][n]
                ang = np.radians(xphase * m) + np.radians(yphase * n)
                weight[m][n] = np.sqrt(mag) * np.exp(1 * ang)
        return True

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

        Returns
        -------
        :class:`pyaedt.generic.plot.ModelPlotter`
            Model Object.
        """
        assert self._app._aedt_version >= "2021.2", self.logger.error("Object is supported from AEDT 2021 R2.")
        files = self.export_model_obj(
            obj_list=objects,
            export_as_single_objects=plot_as_separate_objects,
            air_objects=plot_air_objects,
        )
        if not files:
            self.logger.warning("No Objects exported. Try other options or include Air objects.")
            return False

        model = ModelPlotter()

        for file in files:
            if force_opacity_value:
                model.add_object(file[0], file[1], force_opacity_value, self.modeler.model_units)
            else:
                model.add_object(file[0], file[1], file[2], self.modeler.model_units)
        if not show:
            model.off_screen = True
        if export_path:
            model.plot(export_path)
        elif show:
            model.plot()
        if clean_files:
            model.clean_cache_and_files(clean_cache=False)
        return model

    @pyaedt_function_handler()
    def plot_field_from_fieldplot(
        self,
        plotname,
        project_path="",
        meshplot=False,
        imageformat="jpg",
        view="isometric",
        plot_label="Temperature",
        plot_folder=None,
        show=True,
        scale_min=None,
        scale_max=None,
    ):
        """Export a field plot to an image file (JPG or PNG) using Python Plotly.

        .. note::
           The Plotly module rebuilds the mesh and the overlap fields on the mesh.

        Parameters
        ----------
        plotname : str
            Name of the field plot to export.
        project_path : str, optional
            Path for saving the image file. The default is ``""``.
        meshplot : bool, optional
            Whether to create and plot the mesh over the fields. The
            default is ``False``.
        imageformat : str, optional
            Format of the image file. Options are ``"jpg"``,
            ``"png"``, ``"svg"``, and ``"webp"``. The default is
            ``"jpg"``.
        view : str, optional
            View to export. Options are ``isometric``, ``top``, ``front``,
             ``left``, ``all``.. The default is ``"iso"``. If ``"all"``, all views are exported.
        plot_label : str, optional
            Type of the plot. The default is ``"Temperature"``.
        plot_folder : str, optional
            Plot folder to update before exporting the field.
            The default is ``None``, in which case all plot
            folders are updated.
        show : bool, optional
            Export Image without plotting on UI.
        scale_min : float, optional
            Fix the Scale Minimum value.
        scale_max : float, optional
            Fix the Scale Maximum value.

        Returns
        -------
        :class:`pyaedt.generic.plot.ModelPlotter`
            Model Object.
        """
        if not plot_folder:
            self.ofieldsreporter.UpdateAllFieldsPlots()
        else:
            self.ofieldsreporter.UpdateQuantityFieldsPlots(plot_folder)

        start = time.time()
        file_to_add = self.export_field_plot(plotname, self._app.working_directory)
        models = None
        if not file_to_add:
            return False
        else:
            if self._app._aedt_version >= "2021.2":
                models = self.export_model_obj(export_as_single_objects=True, air_objects=False)

        model = ModelPlotter()
        model.off_screen = not show

        if file_to_add:
            model.add_field_from_file(file_to_add, coordinate_units=self.modeler.model_units, show_edges=meshplot)
            if plot_label:
                model.fields[0].label = plot_label
        if models:
            for m in models:
                model.add_object(m[0], m[1], m[2])
        model.view = view

        if scale_min and scale_max:
            model.range_min = scale_min
            model.range_max = scale_max
        if show or project_path:
            model.plot(os.path.join(project_path, self._app.project_name + "." + imageformat))
            model.clean_cache_and_files(clean_cache=False)

        return model

    @pyaedt_function_handler()
    def animate_fields_from_aedtplt(
        self,
        plotname,
        plot_folder=None,
        meshplot=False,
        variation_variable="Phi",
        variation_list=["0deg"],
        project_path="",
        export_gif=False,
        show=True,
    ):
        """Generate a field plot to an image file (JPG or PNG) using PyVista.

        .. note::
           The PyVista module rebuilds the mesh and the overlap fields on the mesh.

        Parameters
        ----------
        plotname : str
            Name of the plot or the name of the object.
        plot_folder : str, optional
            Name of the folder in which the plot resides. The default
            is ``None``.
        variation_variable : str, optional
            Variable to vary. The default is ``"Phi"``.
        variation_list : list, optional
            List of variation values with units. The default is
            ``["0deg"]``.
        project_path : str, optional
            Path for the export. The default is ``""`` which export file in working_directory.
        meshplot : bool, optional
             The default is ``False``. Valid from Version 2021.2.
        export_gif : bool, optional
             The default is ``False``.
                show=False,
        show : bool, optional
             Generate the animation without showing an interactive plot.  The default is ``True``.

        Returns
        -------
        :class:`pyaedt.generic.plot.ModelPlotter`
            Model Object.
        """
        if not plot_folder:
            self.ofieldsreporter.UpdateAllFieldsPlots()
        else:
            self.ofieldsreporter.UpdateQuantityFieldsPlots(plot_folder)
        models_to_add = []
        if meshplot:
            if self._app._aedt_version >= "2021.2":
                models_to_add = self.export_model_obj(export_as_single_objects=True, air_objects=False)
        fields_to_add = []
        if not project_path:
            project_path = self._app.working_directory
        for el in variation_list:
            self._app._odesign.ChangeProperty(
                [
                    "NAME:AllTabs",
                    [
                        "NAME:FieldsPostProcessorTab",
                        ["NAME:PropServers", "FieldsReporter:" + plotname],
                        ["NAME:ChangedProps", ["NAME:" + variation_variable, "Value:=", el]],
                    ],
                ]
            )
            fields_to_add.append(
                self.export_field_plot(plotname, project_path, plotname + variation_variable + str(el))
            )

        model = ModelPlotter()
        model.off_screen = not show
        if models_to_add:
            for m in models_to_add:
                model.add_object(m[0], cad_color=m[1], opacity=m[2])
        if fields_to_add:
            model.add_frames_from_file(fields_to_add)
        if export_gif:
            model.gif_file = os.path.join(self._app.working_directory, self._app.project_name + ".gif")

        if show or export_gif:
            model.animate()
            model.clean_cache_and_files(clean_cache=False)
        return model

    @pyaedt_function_handler()
    def animate_fields_from_aedtplt_2(
        self,
        quantityname,
        object_list,
        plottype,
        meshplot=False,
        setup_name=None,
        intrinsic_dict={},
        variation_variable="Phi",
        variation_list=["0deg"],
        project_path="",
        export_gif=False,
        show=True,
        zoom=None,
    ):
        """Generate a field plot to an animated gif file using PyVista.

         .. note::
            The PyVista module rebuilds the mesh and the overlap fields on the mesh.

        This method creates the plot and exports it.
        It is an alternative to the method :func:`animate_fields_from_aedtplt`,
        which uses an existing plot.

        Parameters
        ----------
        quantityname : str
            Name of the plot or the name of the object.
        object_list : list, optional
            Name of the ``folderplot`` folder.
        plottype : str
            Type of the plot. Options are ``"Surface"``, ``"Volume"``, and
            ``"CutPlane"``.
        meshplot : bool, optional
            The default is ``False``.
        setup_name : str, optional
            Name of the setup (sweep) to use for the export. The default is
            ``None``.
        intrinsic_dict : dict, optional
            Intrinsic dictionary that is needed for the export.
            The default is ``{}``.
        variation_variable : str, optional
            Variable to vary. The default is ``"Phi"``.
        variation_list : list, option
            List of variation values with units. The default is
            ``["0deg"]``.
        project_path : str, optional
            Path for the export. The default is ``""`` which export file in working_directory.
        export_gif : bool, optional
            Whether to export to a GIF file. The default is ``False``,
            in which case the plot is exported to a JPG file.
        show : bool, optional
            Generate the animation without showing an interactive plot.  The default is ``True``.
        zoom : float, optional
            Zoom factor.

        Returns
        -------
        :class:`pyaedt.generic.plot.ModelPlotter`
            Model Object.
        """
        if not project_path:
            project_path = self._app.working_directory
        models_to_add = []
        if meshplot:
            if self._app._aedt_version >= "2021.2":
                models_to_add = self.export_model_obj(export_as_single_objects=True, air_objects=False)
        v = 0
        fields_to_add = []
        for el in variation_list:
            intrinsic_dict[variation_variable] = el
            if plottype == "Surface":
                plotf = self.create_fieldplot_surface(object_list, quantityname, setup_name, intrinsic_dict)
            elif plottype == "Volume":
                plotf = self.create_fieldplot_volume(object_list, quantityname, setup_name, intrinsic_dict)
            else:
                plotf = self.create_fieldplot_cutplane(object_list, quantityname, setup_name, intrinsic_dict)
            if plotf:
                file_to_add = self.export_field_plot(plotf.name, project_path, plotf.name + str(v))
                if file_to_add:
                    fields_to_add.append(file_to_add)
                plotf.delete()
            v += 1
        model = ModelPlotter()
        model.off_screen = not show
        if models_to_add:
            for m in models_to_add:
                model.add_object(m[0], cad_color=m[1], opacity=m[2])
        if fields_to_add:
            model.add_frames_from_file(fields_to_add)
        if export_gif:
            model.gif_file = os.path.join(self._app.working_directory, self._app.project_name + ".gif")
        if zoom:
            model.zoom = zoom
        if show or export_gif:
            model.animate()
            model.clean_cache_and_files(clean_cache=False)

        return model

    @pyaedt_function_handler()
    def far_field_plot(self, ff_data, x=0, y=0, qty="rETotal", dB=True, array_size=[4, 4]):
        """Generate a far field plot.

        Parameters
        ----------
        ff_data :

        x : float, optional
            The default is ``0``.
        y : float, optional
            The default is ``0``.
        qty : str, optional
            The default is ``"rETotal"``.
        dB : bool, optional
            The default is ``True``.
        array_size : list
            List for the array size. The default is ``[4, 4]``.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.
        """
        loc_offset = 2  # if array index is not starting at [1,1]
        xphase = float(y)
        yphase = float(x)
        array_shape = (array_size[0], array_size[1])
        weight = np.zeros(array_shape, dtype=complex)
        mag = np.ones(array_shape, dtype="object")
        port_names_arranged = np.chararray(array_shape)
        all_ports = ff_data.keys()
        w_dict = {}
        # calculate weights based off of progressive phase shift
        port_name = []
        for m in range(array_shape[0]):
            for n in range(array_shape[1]):
                mag_val = mag[m][n]
                ang = np.radians(xphase * m) + np.radians(yphase * n)
                weight[m][n] = np.sqrt(mag_val) * np.exp(1j * ang)
                current_index_str = "[" + str(m + 1 + loc_offset) + "," + str(n + 1 + loc_offset) + "]"
                port_name = [y for y in all_ports if current_index_str in y]
                w_dict[port_name[0]] = weight[m][n]

        length_of_ff_data = len(ff_data[port_name[0]][2])

        array_shape = (len(w_dict), length_of_ff_data)
        rEtheta_fields = np.zeros(array_shape, dtype=complex)
        rEphi_fields = np.zeros(array_shape, dtype=complex)
        w = np.zeros((1, array_shape[0]), dtype=complex)
        # create port mapping
        Ntheta = 0
        Nphi = 0
        for n, port in enumerate(ff_data.keys()):
            re_theta = ff_data[port][2]
            re_phi = ff_data[port][3]
            re_theta = re_theta * w_dict[port]

            w[0][n] = w_dict[port]
            re_phi = re_phi * w_dict[port]

            rEtheta_fields[n] = re_theta
            rEphi_fields[n] = re_phi

            theta_range = ff_data[port][0]
            phi_range = ff_data[port][1]
            theta = [int(np.min(theta_range)), int(np.max(theta_range)), np.size(theta_range)]
            phi = [int(np.min(phi_range)), int(np.max(phi_range)), np.size(phi_range)]
            Ntheta = len(theta_range)
            Nphi = len(phi_range)

        rEtheta_fields = np.dot(w, rEtheta_fields)
        rEtheta_fields = np.reshape(rEtheta_fields, (Ntheta, Nphi))

        rEphi_fields = np.dot(w, rEphi_fields)
        rEphi_fields = np.reshape(rEphi_fields, (Ntheta, Nphi))

        all_qtys = {}
        all_qtys["rEPhi"] = rEphi_fields
        all_qtys["rETheta"] = rEtheta_fields
        all_qtys["rETotal"] = np.sqrt(np.power(np.abs(rEphi_fields), 2) + np.power(np.abs(rEtheta_fields), 2))

        pin = np.sum(w)
        print(str(pin))
        real_gain = 2 * np.pi * np.abs(np.power(all_qtys["rETotal"], 2)) / pin / 377
        all_qtys["RealizedGain"] = real_gain

        if dB:
            if "Gain" in qty:
                qty_to_plot = 10 * np.log10(np.abs(all_qtys[qty]))
            else:
                qty_to_plot = 20 * np.log10(np.abs(all_qtys[qty]))
            qty_str = qty + " (dB)"
        else:
            qty_to_plot = np.abs(all_qtys[qty])
            qty_str = qty + " (mag)"

        plt.figure(figsize=(15, 10))
        plt.title(qty_str)
        plt.xlabel("Theta (degree)")
        plt.ylabel("Phi (degree)")

        plt.imshow(qty_to_plot, cmap="jet")
        plt.colorbar()

        np.max(qty_to_plot)

    @pyaedt_function_handler()
    def create_3d_plot(
        self, solution_data, nominal_sweep="Freq", nominal_value=1, primary_sweep="Theta", secondary_sweep="Phi"
    ):
        """Create a 3D plot using Matplotlib.

        Parameters
        ----------
        solution_data :
            Input data for the solution.
        nominal_sweep : str, optional
            Name of the nominal sweep. The default is ``"Freq"``.
        nominal_value : str, optional
            Value for the nominal sweep. The default is ``1``.
        primary_sweep : str, optional
            Primary sweep. The default is ``"Theta"``.
        secondary_sweep : str, optional
            Secondary sweep. The default is ``"Phi"``.

        Returns
        -------
         bool
             ``True`` when successful, ``False`` when failed.
        """
        legend = []
        Freq = nominal_value
        solution_data.nominal_sweeps[nominal_sweep] = Freq
        solution_data.primary_sweep = primary_sweep
        solution_data.nominal_sweeps[primary_sweep] = 45
        theta = np.array((solution_data.sweeps[primary_sweep]))
        phi = np.array((solution_data.sweeps[secondary_sweep]))
        r = []
        i = 0
        phi1 = []
        theta1 = [i * math.pi / 180 for i in theta]
        for el in solution_data.sweeps[secondary_sweep]:
            solution_data.nominal_sweeps[secondary_sweep] = el
            phi1.append(el * math.pi / 180)
            r.append(solution_data.data_magnitude())
        THETA, PHI = np.meshgrid(theta1, phi1)

        R = np.array(r)
        X = R * np.sin(THETA) * np.cos(PHI)
        Y = R * np.sin(THETA) * np.sin(PHI)

        Z = R * np.cos(THETA)
        fig1 = plt.figure()
        ax1 = fig1.add_subplot(1, 1, 1, projection="3d")
        plot = ax1.plot_surface(
            X, Y, Z, rstride=1, cstride=1, cmap=plt.get_cmap("jet"), linewidth=0, antialiased=True, alpha=0.5
        )
        fig1.set_size_inches(10, 10)

    @pyaedt_function_handler()
    def plot_scene(self, frames_list, output_gif_path, norm_index=0, dy_rng=0, fps=30, show=True):
        """Plot the current model 3D scene with overlapping animation coming from a file list and save the gif.


        Parameters
        ----------
        frames_list : list or str
            File list containing animation frames to plot in csv format or
            path to a txt index file containing full path to csv files.
        output_gif_path : str
            Full path to output gif file.
        norm_index : int, optional
            Pick the frame to use to normalize your images.
            Data is already saved as dB : 100 for usual traffic scenes.
        dy_rng : int, optional
            Specify how many dB below you would like to specify the range_min.
            Tweak this a couple of times with small number of frames.
        fps : int, optional
            Frames per Second.
        show : bool, optional
            Either if show or only export gif.

        Returns
        -------

        """
        if isinstance(frames_list, str) and os.path.exists(frames_list):
            with open(frames_list, "r") as f:
                lines = f.read()
                temp_list = lines.splitlines()
            frames_paths_list = [i for i in temp_list]
        elif isinstance(frames_list, str):
            self.logger.error("Path doesn't exists")
            return False
        else:
            frames_paths_list = frames_list
        scene = self.plot_model_obj(show=False)

        norm_data = np.loadtxt(frames_paths_list[norm_index], skiprows=1, delimiter=",")
        norm_val = norm_data[:, -1]
        v_max = np.max(norm_val)
        v_min = v_max - dy_rng
        scene.add_frames_from_file(frames_paths_list, log_scale=False, color_map="jet", header_lines=1, opacity=0.8)

        # Specifying the attributes of the scene through the ModelPlotter object
        scene.off_screen = not show
        scene.isometric_view = False
        scene.range_min = v_min
        scene.range_max = v_max
        scene.show_grid = False
        scene.windows_size = [1920, 1080]
        scene.show_legend = False
        scene.show_bounding_box = False
        scene.legend = False
        scene.frame_per_seconds = fps
        scene.camera_position = "yz"
        scene.zoom = 2
        scene.bounding_box = False
        scene.color_bar = False
        scene.gif_file = output_gif_path  # This gif may be a bit slower so we can speed it up a bit
        scene.animate()
