"""
This module contains the `PostProcessor` class.

It contains all advanced postprocessing functionalities that require Python 3.x packages like NumPy and Matplotlib.
"""
from __future__ import absolute_import

import math
import os
import time
import warnings

from pyaedt.generic.general_methods import aedt_exception_handler
from pyaedt.modules.PostProcessor import PostProcessor as Post
from pyaedt.generic.constants import CSS4_COLORS

try:
    import numpy as np
except ImportError:
    warnings.warn(
        "The NumPy module is required to run some functionalities of PostProcess.\n"
        "Install with \n\npip install numpy\n\nRequires CPython."
    )

try:
    import pyvista as pv

    pyvista_available = True
except ImportError:
    warnings.warn(
        "The PyVista module is required to run some functionalities of PostProcess.\n"
        "Install with \n\npip install pyvista\n\nRequires CPython."
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


def isnotebook():
    try:
        shell = get_ipython().__class__.__name__
        if shell == "ZMQInteractiveShell":
            return True  # Jupyter notebook or qtconsole
        elif shell == "TerminalInteractiveShell":
            return False  # Terminal running IPython
        else:
            return False  # Other type (?)
    except NameError:
        return False  # Probably standard Python interpreter


def is_float(istring):
    """Convert a string to a float.

    Parameters
    ----------
    istring : str
        String to convert to a float.

    Returns
    -------
    float
        Converted float when successful, ``0`` when when failed.
    """
    try:
        return float(istring.strip())
    except Exception:
        return 0


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

    @aedt_exception_handler
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

    @aedt_exception_handler
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

    @aedt_exception_handler
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

    @aedt_exception_handler
    def _triangle_vertex(self, elements_nodes, num_nodes_per_element, take_all_nodes=True):
        """

        Parameters
        ----------
        elements_nodes :

        num_nodes_per_element :

        take_all_nodes : bool, optional
            The default is ``True``.

        Returns
        -------

        """
        trg_vertex = []
        if num_nodes_per_element == 10 and take_all_nodes:
            for e in elements_nodes:
                trg_vertex.append([e[0], e[1], e[3]])
                trg_vertex.append([e[1], e[2], e[4]])
                trg_vertex.append([e[1], e[4], e[3]])
                trg_vertex.append([e[3], e[4], e[5]])

                trg_vertex.append([e[9], e[6], e[8]])
                trg_vertex.append([e[6], e[0], e[3]])
                trg_vertex.append([e[6], e[3], e[8]])
                trg_vertex.append([e[8], e[3], e[5]])

                trg_vertex.append([e[9], e[7], e[8]])
                trg_vertex.append([e[7], e[2], e[4]])
                trg_vertex.append([e[7], e[4], e[8]])
                trg_vertex.append([e[8], e[4], e[5]])

                trg_vertex.append([e[9], e[7], e[6]])
                trg_vertex.append([e[7], e[2], e[1]])
                trg_vertex.append([e[7], e[1], e[6]])
                trg_vertex.append([e[6], e[1], e[0]])
        elif num_nodes_per_element == 10 and not take_all_nodes:
            for e in elements_nodes:
                trg_vertex.append([e[0], e[2], e[5]])
                trg_vertex.append([e[9], e[0], e[5]])
                trg_vertex.append([e[9], e[2], e[0]])
                trg_vertex.append([e[9], e[2], e[5]])

        elif num_nodes_per_element == 6 and not take_all_nodes:
            for e in elements_nodes:
                trg_vertex.append([e[0], e[2], e[5]])

        elif num_nodes_per_element == 6 and take_all_nodes:
            for e in elements_nodes:
                trg_vertex.append([e[0], e[1], e[3]])
                trg_vertex.append([e[1], e[2], e[4]])
                trg_vertex.append([e[1], e[4], e[3]])
                trg_vertex.append([e[3], e[4], e[5]])

        elif num_nodes_per_element == 4 and take_all_nodes:
            for e in elements_nodes:
                trg_vertex.append([e[0], e[1], e[3]])
                trg_vertex.append([e[1], e[2], e[3]])
                trg_vertex.append([e[0], e[1], e[2]])
                trg_vertex.append([e[0], e[2], e[3]])

        elif num_nodes_per_element == 3:
            trg_vertex = elements_nodes

        return trg_vertex

    @aedt_exception_handler
    def _read_mesh_files(
        self, aedtplt_files, model_color, lines, meshes, model_colors, model_opacity, materials, objects
    ):
        id = 0
        colors = list(CSS4_COLORS.keys())
        for file in aedtplt_files:
            if ".aedtplt" in file:
                with open(file, "r") as f:
                    drawing_found = False
                    for line in f:
                        if "$begin Drawing" in line:
                            drawing_found = True
                            l_tmp = []
                            continue
                        if "$end Drawing" in line:
                            lines.append(l_tmp)
                            drawing_found = False
                            continue
                        if drawing_found:
                            l_tmp.append(line)
                            continue
                        if "Number of drawing:" in line:
                            n_drawings = int(line[18:])
                            continue
            elif ".obj" in file:
                meshes.append(pv.read(file))
                file_split = file.split("_")
                objects.append(os.path.splitext(os.path.basename(file))[0].replace("Model_", "").split(".")[0])
                if len(file_split) >= 3:
                    model_opacity.append(0.6)
                    if "air.obj" in file or "vacuum.obj" in file:
                        materials[file_split[-1]] = "dodgerblue"
                        model_colors.append(materials[file_split[-1]])
                    else:
                        if file_split[-1] in materials:
                            model_colors.append(materials[file_split[-1]])
                        else:
                            materials[file_split[-1]] = colors[id % len(colors)]
                            id += 1
                            model_colors.append(materials[file_split[-1]])
                else:
                    model_colors.append(colors[id % len(colors)])
                    id += 1
                if model_color:
                    model_colors[-1] = model_color

    @aedt_exception_handler
    def _add_model_meshes_to_plot(
        self,
        plot,
        meshes,
        model_colors,
        model_opacity,
        objects,
        show_model_edge,
        fields_exists=False,
        object_selector=True,
    ):

        mesh = plot.add_mesh

        class SetVisibilityCallback:
            """Helper callback to keep a reference to the actor being modified."""

            def __init__(self, actor):
                self.actor = actor

            def __call__(self, state):
                self.actor.SetVisibility(state)

        class ChangePageCallback:
            """Helper callback to keep a reference to the actor being modified."""

            def __init__(self, plot, actor, text, names, colors):
                self.plot = plot
                self.actor = actor
                self.text = text
                self.names = names
                self.colors = colors
                self.id = 0
                self.endpos = 100
                self.size = int(plot.window_size[1] / 40)
                self.startpos = plot.window_size[1] - 2 * self.size
                self.max_elements = (self.startpos - self.endpos) // (self.size + (self.size // 10))
                self.i = self.max_elements

            def __call__(self, state):
                self.plot.button_widgets = [self.plot.button_widgets[0]]
                self.id += 1
                k = 0
                startpos = self.startpos
                while k < max_elements:
                    if len(self.text) > k:
                        self.plot.remove_actor(self.text[k])
                    k += 1
                self.text = []
                k = 0

                while k < self.max_elements:
                    if self.i >= len(self.actor):
                        self.i = 0
                        self.id = 0
                    callback = SetVisibilityCallback(self.actor[self.i])
                    plot.add_checkbox_button_widget(
                        callback,
                        value=self.actor[self.i].GetVisibility() == 1,
                        position=(5.0, startpos),
                        size=self.size,
                        border_size=1,
                        color_on=self.colors[self.i],
                        color_off="grey",
                        background_color=None,
                    )
                    self.text.append(
                        plot.add_text(
                            self.names[self.i], position=(25.0, startpos), font_size=self.size // 3, color=axes_color
                        )
                    )
                    startpos = startpos - self.size - (self.size // 10)
                    k += 1
                    self.i += 1

        if meshes and len(meshes) == 1:

            def _create_object_mesh(opacity):
                try:
                    plot.remove_actor("Volumes")
                except:
                    pass
                mesh(
                    meshes[0],
                    show_scalar_bar=False,
                    opacity=opacity,
                    color=model_colors[0],
                    name="3D Model",
                    show_edges=show_model_edge,
                    edge_color=model_colors[0],
                )

            plot.add_slider_widget(
                _create_object_mesh,
                [0, 1],
                style="modern",
                value=0.75,
                pointa=[0.81, 0.98],
                pointb=[0.95, 0.98],
                title="Opacity",
            )
        elif meshes:

            size = int(plot.window_size[1] / 40)
            startpos = plot.window_size[1] - 2 * size
            endpos = 100
            color = plot.background_color
            axes_color = [0 if i >= 0.5 else 1 for i in color]
            buttons = []
            texts = []
            max_elements = (startpos - endpos) // (size + (size // 10))
            actors = []
            el = 0
            if fields_exists:
                for m, c, n in zip(meshes, model_colors, objects):
                    actor = mesh(m, show_scalar_bar=False, opacity=0.3, color="#8faf8f")
                    if object_selector:
                        actors.append(actor)
                        if el < max_elements:
                            callback = SetVisibilityCallback(actor)
                            buttons.append(
                                plot.add_checkbox_button_widget(
                                    callback,
                                    value=True,
                                    position=(5.0, startpos + 50),
                                    size=size,
                                    border_size=1,
                                    color_on=c,
                                    color_off="grey",
                                    background_color=None,
                                )
                            )
                            texts.append(
                                plot.add_text(n, position=(50.0, startpos + 50), font_size=size // 3, color=axes_color)
                            )

                            startpos = startpos - size - (size // 10)
                            el += 1

            else:
                for m, c, o, n in zip(meshes, model_colors, model_opacity, objects):
                    actor = mesh(
                        m,
                        show_scalar_bar=False,
                        opacity=o,
                        color=c,
                    )
                    if object_selector:
                        actors.append(actor)

                        if el < max_elements:
                            callback = SetVisibilityCallback(actor)
                            buttons.append(
                                plot.add_checkbox_button_widget(
                                    callback,
                                    value=True,
                                    position=(5.0, startpos),
                                    size=size,
                                    border_size=1,
                                    color_on=c,
                                    color_off="grey",
                                    background_color=None,
                                )
                            )
                            texts.append(
                                plot.add_text(n, position=(25.0, startpos), font_size=size // 3, color=axes_color)
                            )
                            startpos = startpos - size - (size // 10)
                            el += 1
            if object_selector and texts and len(texts) >= max_elements:
                callback = ChangePageCallback(plot, actors, texts, objects, model_colors)
                plot.add_checkbox_button_widget(
                    callback,
                    value=True,
                    position=(5.0, plot.window_size[1]),
                    size=int(1.5 * size),
                    border_size=2,
                    color_on=axes_color,
                    color_off=axes_color,
                )
                plot.add_text("Next", position=(50.0, plot.window_size[1]), font_size=size // 3, color="grey")
                plot.button_widgets.insert(
                    0, plot.button_widgets.pop(plot.button_widgets.index(plot.button_widgets[-1]))
                )

    @aedt_exception_handler
    def _add_fields_to_plot(self, plot, plot_label, plot_type, scale_min, scale_max, off_screen, lines):
        for drawing_lines in lines:
            bounding = []
            elements = []
            nodes_list = []
            solution = []
            for l in drawing_lines:
                if "BoundingBox(" in l:
                    bounding = l[l.find("(") + 1 : -2].split(",")
                    bounding = [i.strip() for i in bounding]
                if "Elements(" in l:
                    elements = l[l.find("(") + 1 : -2].split(",")
                    elements = [int(i.strip()) for i in elements]
                if "Nodes(" in l:
                    nodes_list = l[l.find("(") + 1 : -2].split(",")
                    nodes_list = [float(i.strip()) for i in nodes_list]
                if "ElemSolution(" in l:
                    # convert list of strings to list of floats
                    sols = l[l.find("(") + 1 : -2].split(",")
                    sols = [is_float(value) for value in sols]

                    # sols = [float(i.strip()) for i in sols]
                    num_solution_per_element = int(sols[2])
                    sols = sols[3:]
                    sols = [
                        sols[i : i + num_solution_per_element] for i in range(0, len(sols), num_solution_per_element)
                    ]
                    solution = [sum(i) / num_solution_per_element for i in sols]

            nodes = [[nodes_list[i], nodes_list[i + 1], nodes_list[i + 2]] for i in range(0, len(nodes_list), 3)]
            num_nodes = elements[0]
            num_elements = elements[1]
            elements = elements[2:]
            element_type = elements[0]
            num_nodes_per_element = elements[4]
            hl = 5  # header length
            elements_nodes = []
            for i in range(0, len(elements), num_nodes_per_element + hl):
                elements_nodes.append([elements[i + hl + n] for n in range(num_nodes_per_element)])
            if solution:
                take_all_nodes = True  # solution case
            else:
                take_all_nodes = False  # mesh case
            trg_vertex = self._triangle_vertex(elements_nodes, num_nodes_per_element, take_all_nodes)
            # remove duplicates
            nodup_list = [list(i) for i in list(set([frozenset(t) for t in trg_vertex]))]
            sols_vertex = []
            if solution:
                sv = {}
                for els, s in zip(elements_nodes, solution):
                    for el in els:
                        if el in sv:
                            sv[el] = (sv[el] + s) / 2
                        else:
                            sv[el] = s
                sols_vertex = [sv[v] for v in sorted(sv.keys())]
            array = [[3] + [j - 1 for j in i] for i in nodup_list]
            faces = np.hstack(array)
            vertices = np.array(nodes)
            surf = pv.PolyData(vertices, faces)
            if sols_vertex:
                temps = np.array(sols_vertex)
                mean = np.mean(temps)
                std = np.std(temps)
                if np.min(temps) > 0:
                    log = True
                else:
                    log = False
                surf.point_data[plot_label] = temps

            sargs = dict(
                title_font_size=10,
                label_font_size=10,
                shadow=True,
                n_labels=9,
                italic=True,
                fmt="%.1f",
                font_family="arial",
            )
            if plot_type == "Clip":
                plot.add_text("Full Plot", font_size=15)
                if solution:

                    class MyCustomRoutine:
                        """ """

                        def __init__(self, mesh):
                            self.output = mesh  # Expected PyVista mesh type
                            # default parameters
                            self.kwargs = {
                                "min_val": 0.5,
                                "max_val": 30,
                            }

                        def __call__(self, param, value):
                            self.kwargs[param] = value
                            self.update()

                        def update(self):
                            """ """
                            # This is where you call your simulation
                            try:
                                plot.remove_actor("FieldPlot")
                            except:
                                pass
                            plot.add_mesh(
                                surf,
                                scalars=plot_label,
                                log_scale=log,
                                scalar_bar_args=sargs,
                                cmap="rainbow",
                                show_edges=False,
                                clim=[self.kwargs["min_val"], self.kwargs["max_val"]],
                                pickable=True,
                                smooth_shading=True,
                                name="FieldPlot",
                            )
                            return

                    engine = MyCustomRoutine(surf)
                    plot.add_box_widget(
                        surf,
                        show_edges=False,
                        scalars=plot_label,
                        log_scale=log,
                        scalar_bar_args=sargs,
                        cmap="rainbow",
                        pickable=True,
                        smooth_shading=True,
                        name="FieldPlot",
                    )
                    if not off_screen:
                        plot.add_slider_widget(
                            callback=lambda value: engine("min_val", value),
                            rng=[np.min(temps), np.max(temps)],
                            title="Lower",
                            style="modern",
                            value=np.min(temps),
                            pointa=(0.5, 0.98),
                            pointb=(0.65, 0.98),
                        )

                        plot.add_slider_widget(
                            callback=lambda value: engine("max_val", value),
                            rng=[np.min(temps), np.max(temps)],
                            title="Upper",
                            style="modern",
                            value=np.max(temps),
                            pointa=(0.66, 0.98),
                            pointb=(0.8, 0.98),
                        )
                    else:
                        if isinstance(scale_max, float):
                            engine("max_val", scale_max)
                        if isinstance(scale_min, float):
                            engine("min_val", scale_min)
                else:
                    plot.add_box_widget(
                        surf, show_edges=True, line_width=0.1, color="grey", pickable=True, smooth_shading=True
                    )
            else:
                plot.add_text("Full Plot", font_size=15)
                if solution:

                    class MyCustomRoutine:
                        """ """

                        def __init__(self, mesh):
                            self.output = mesh  # Expected PyVista mesh type
                            # default parameters
                            self.kwargs = {
                                "min_val": 0.5,
                                "max_val": 30,
                            }

                        def __call__(self, param, value):
                            self.kwargs[param] = value
                            self.update()

                        def update(self):
                            """ """
                            # This is where you call your simulation
                            try:
                                plot.remove_actor("FieldPlot")
                            except:
                                pass
                            plot.add_mesh(
                                surf,
                                scalars=plot_label,
                                log_scale=log,
                                scalar_bar_args=sargs,
                                cmap="rainbow",
                                show_edges=False,
                                clim=[self.kwargs["min_val"], self.kwargs["max_val"]],
                                pickable=True,
                                smooth_shading=True,
                                name="FieldPlot",
                            )
                            return

                    engine = MyCustomRoutine(surf)
                    plot.add_mesh(
                        surf,
                        show_edges=False,
                        scalars=plot_label,
                        log_scale=log,
                        scalar_bar_args=sargs,
                        cmap="rainbow",
                        pickable=True,
                        smooth_shading=True,
                        name="FieldPlot",
                    )
                    if not off_screen:
                        plot.add_slider_widget(
                            callback=lambda value: engine("min_val", value),
                            rng=[np.min(temps), np.max(temps)],
                            title="Lower",
                            style="modern",
                            value=np.min(temps),
                            pointa=(0.5, 0.98),
                            pointb=(0.65, 0.98),
                        )

                        plot.add_slider_widget(
                            callback=lambda value: engine("max_val", value),
                            rng=[np.min(temps), np.max(temps)],
                            title="Upper",
                            style="modern",
                            value=np.max(temps),
                            pointa=(0.66, 0.98),
                            pointb=(0.8, 0.98),
                        )
                    else:
                        if isinstance(scale_max, (int, float)):
                            engine("max_val", scale_max)
                        if isinstance(scale_min, (int, float)):
                            engine("min_val", scale_min)
                else:
                    plot.add_mesh(
                        surf, show_edges=True, line_width=0.1, color="grey", pickable=True, smooth_shading=True
                    )

    @aedt_exception_handler
    def _plot_on_pyvista(
        self,
        plot,
        meshes,
        model_color,
        materials,
        view,
        imageformat,
        aedtplt_files,
        show_axes=True,
        show_grid=True,
        show_legend=True,
        export_path=None,
    ):
        files_list = []
        color = plot.background_color
        axes_color = [0 if i >= 0.5 else 1 for i in color]
        if show_axes:
            plot.show_axes()
        if show_grid and not isnotebook():
            plot.show_grid(color=tuple(axes_color))
        plot.add_bounding_box(color=tuple(axes_color))
        if show_legend and meshes and len(meshes) > 1 and not model_color:
            labels = []
            for m in list(materials.keys()):
                labels.append([m[:-4], materials[m]])
            plot.add_legend(labels=labels, bcolor=None, size=[0.1, 0.1])
        if view == "isometric":
            plot.view_isometric()
        elif view == "top":
            plot.view_yz()
        elif view == "front":
            plot.view_xz()
        elif view == "top":
            plot.view_xy()
        if imageformat:
            if export_path:
                filename = export_path
            else:
                filename = os.path.splitext(aedtplt_files[0])[0] + "." + imageformat
            plot.show(screenshot=filename, full_screen=True)
            files_list.append(filename)
        else:
            plot.show()
        if aedtplt_files:
            for f in aedtplt_files:
                if os.path.exists(f):
                    os.remove(f)
                if "obj" in f and os.path.exists(f[:-3] + "mtl"):
                    os.remove(f[:-3] + "mtl")
        return files_list

    @aedt_exception_handler
    def _plot_from_aedtplt(
        self,
        aedtplt_files=None,
        imageformat="jpg",
        view="isometric",
        plot_type="Full",
        plot_label="Temperature",
        model_color="#8faf8f",
        show_model_edge=False,
        off_screen=False,
        scale_min=None,
        scale_max=None,
        show_axes=True,
        show_grid=True,
        show_legend=True,
        background_color=[0.6, 0.6, 0.6],
        windows_size=None,
        object_selector=True,
        export_path=None,
    ):
        """Export the 3D field solver mesh, fields, or both mesh and fields as images using Python Plotly.

        .. note::
           This method is currently supported only on Windows using CPython.

        Parameters
        ----------
        aedtplt_files : str or list, optional
            Names of the one or more AEDTPLT files generated by AEDT. The default is ``None``.
        imageformat : str, optional
            Format of the image file. Options are ``"jpg"``, ``"png"``, ``"svg"``, and
            ``"webp"``. The default is ``"jpg"``.
        view : str, optional
            View to export. Options are `Options are ``isometric``,
            ``top``, ``front``, ``left``, ``all``.
            The ``"all"`` option exports all views.
        plot_type : str, optional
            Type of the plot. The default is ``"Full"``.
        plot_label : str, optional
            Label for the plot. The default is ``"Temperature"``.
        model_color : str, optional
            Color scheme for the 3D model. The default is ``"#8faf8f"``, which is silver.
        show_model_edge : bool, optional
            Whether to return a list of the files that are generated. The default
            is ``False``.
        off_screen : bool, optional
             The default is ``False``.
        scale_min : float, optional
            Fix the Scale Minimum value.
        scale_max : float, optional
            Fix the Scale Maximum value.

        Returns
        -------
        list
            List of exported files.
        """
        start = time.time()
        if type(aedtplt_files) is str:
            aedtplt_files = [aedtplt_files]
        if not windows_size:
            windows_size = [1024, 768]

        plot = pv.Plotter(notebook=isnotebook(), off_screen=off_screen, window_size=windows_size)
        plot.background_color = background_color
        lines = []
        meshes = []
        model_colors = []
        model_opacity = []
        materials = {}
        objects = []
        self._read_mesh_files(
            aedtplt_files, model_color, lines, meshes, model_colors, model_opacity, materials, objects
        )
        if lines:
            fields_exists = True
        else:
            fields_exists = False
        self._add_model_meshes_to_plot(
            plot,
            meshes,
            model_colors,
            model_opacity,
            objects,
            object_selector=object_selector,
            show_model_edge=show_model_edge,
            fields_exists=fields_exists,
        )
        if lines:
            self._add_fields_to_plot(plot, plot_label, plot_type, scale_min, scale_max, off_screen, lines)

        end = time.time() - start
        self.logger.info("PyVista plot generation took {} seconds.".format(end))
        print(plot.background_color)
        files_list = self._plot_on_pyvista(
            plot,
            meshes,
            model_color,
            materials,
            view,
            imageformat,
            aedtplt_files,
            show_axes=show_axes,
            show_grid=show_grid,
            show_legend=show_legend,
            export_path=export_path,
        )

        return files_list

    @aedt_exception_handler
    def _animation_from_aedtflt(
        self,
        aedtplt_files=None,
        variation_var="Time",
        variation_list=[],
        plot_label="Temperature",
        model_color="#8faf8f",
        export_gif=False,
        off_screen=False,
    ):
        """Export the 3D field solver mesh, fields, or both mesh and fields as images using Python Plotly.

          .. note::
           This method is currently supported only on Windows using CPython.

        Parameters
        ----------
        aedtplt_files : str or list, optional
            Names of the one or more AEDTPLT files generated by AEDT. The default is ``None``.
        variation_var : str, optional
             Variable to vary. The default is ``"Time"``.
        variation_list : list, optional
             List of variation values. The default is ``[]``.
        plot_label : str, optional
            Label for the plot. The default is ``"Temperature"``.
        model_color : str, optional
            Color scheme for the 3D model. The default is ``"#8faf8f"``, which is silver.
        export_gif : bool, optional
             Whether to export the animation as a GIF file. The default is ``False``.
        off_screen : bool, optional
             The default is ``False``.

        Returns
        -------
        str
            Name of the GIF file.
        """
        frame_per_seconds = 0.5
        start = time.time()
        if type(aedtplt_files) is str:
            aedtplt_files = [aedtplt_files]
        plot = pv.Plotter(notebook=False, off_screen=off_screen)
        if not off_screen:
            plot.enable_anti_aliasing()
        plot.enable_fly_to_right_click()
        lines = []
        for file in aedtplt_files:
            if ".aedtplt" in file:
                with open(file, "r") as f:
                    drawing_found = False
                    for line in f:
                        if "$begin Drawing" in line:
                            drawing_found = True
                            l_tmp = []
                            continue
                        if "$end Drawing" in line:
                            lines.append(l_tmp)
                            drawing_found = False
                            continue
                        if drawing_found:
                            l_tmp.append(line)
                            continue
                        if "Number of drawing:" in line:
                            n_drawings = int(line[18:])
                            continue
            elif ".obj" in file:
                mesh = pv.read(file)
                plot.add_mesh(
                    mesh,
                    show_scalar_bar=False,
                    opacity=0.75,
                    cmap=[model_color],
                    name="3D Model",
                    show_edges=False,
                    edge_color=model_color,
                )
                # def create_object_mesh(opacity):
                #     try:
                #         p.remove_actor("Volumes")
                #     except:
                #         pass
                #     p.add_mesh(mesh, show_scalar_bar=False, opacity=opacity, cmap=[model_color], name="3D Model",
                #                show_edges=False, edge_color=model_color)
                # p.add_slider_widget(
                #   create_object_mesh,
                #   [0,1], style='modern',
                #   value=0.75,pointa=[0.81,0.98],
                #   pointb=[0.95,0.98],title="Opacity"
                # )
        filename = os.path.splitext(aedtplt_files[0])[0]
        print(filename)
        surfs = []
        log = False
        mins = 1e12
        maxs = -1e12
        log = True
        for drawing_lines in lines:
            bounding = []
            elements = []
            nodes_list = []
            solution = []
            for l in drawing_lines:
                if "BoundingBox(" in l:
                    bounding = l[l.find("(") + 1 : -2].split(",")
                    bounding = [i.strip() for i in bounding]
                if "Elements(" in l:
                    elements = l[l.find("(") + 1 : -2].split(",")
                    elements = [int(i.strip()) for i in elements]
                if "Nodes(" in l:
                    nodes_list = l[l.find("(") + 1 : -2].split(",")
                    nodes_list = [float(i.strip()) for i in nodes_list]
                if "ElemSolution(" in l:
                    # convert list of strings to list of floats
                    sols = l[l.find("(") + 1 : -2].split(",")
                    sols = [is_float(value) for value in sols]

                    num_solution_per_element = int(sols[2])
                    sols = sols[3:]
                    sols = [
                        sols[i : i + num_solution_per_element] for i in range(0, len(sols), num_solution_per_element)
                    ]
                    solution = [sum(i) / num_solution_per_element for i in sols]

            nodes = [[nodes_list[i], nodes_list[i + 1], nodes_list[i + 2]] for i in range(0, len(nodes_list), 3)]
            num_nodes = elements[0]
            num_elements = elements[1]
            elements = elements[2:]
            element_type = elements[0]
            num_nodes_per_element = elements[4]
            hl = 5  # header length
            elements_nodes = []
            for i in range(0, len(elements), num_nodes_per_element + hl):
                elements_nodes.append([elements[i + hl + n] for n in range(num_nodes_per_element)])
            if solution:
                take_all_nodes = True  # solution case
            else:
                take_all_nodes = False  # mesh case
            trg_vertex = self._triangle_vertex(elements_nodes, num_nodes_per_element, take_all_nodes)
            # remove duplicates
            nodup_list = [list(i) for i in list(set([frozenset(t) for t in trg_vertex]))]
            sols_vertex = []
            if solution:
                sv = {}
                for els, s in zip(elements_nodes, solution):
                    for el in els:
                        if el in sv:
                            sv[el] = (sv[el] + s) / 2
                        else:
                            sv[el] = s
                sols_vertex = [sv[v] for v in sorted(sv.keys())]
            array = [[3] + [j - 1 for j in i] for i in nodup_list]
            faces = np.hstack(array)
            vertices = np.array(nodes)
            surf = pv.PolyData(vertices, faces)

            if sols_vertex:
                temps = np.array(sols_vertex)
                mean = np.mean(temps)
                std = np.std(temps)
                if np.min(temps) <= 0:
                    log = False
                surf.point_data[plot_label] = temps
            if solution:
                surfs.append(surf)
                if np.min(temps) < mins:
                    mins = np.min(temps)
                if np.max(temps) > maxs:
                    maxs = np.max(temps)

        self._animating = True
        gifname = None
        if export_gif:
            gifname = os.path.splitext(aedtplt_files[0])[0] + ".gif"
            plot.open_gif(gifname)

        def q_callback():
            """exit when user wants to leave"""
            self._animating = False

        self._pause = False

        def p_callback():
            """exit when user wants to leave"""
            self._pause = not self._pause

        plot.add_text("Press p for Play/Pause, Press q to exit ", font_size=8, position="upper_left")
        plot.add_text(" ", font_size=10, position=[0, 0])
        plot.add_key_event("q", q_callback)
        plot.add_key_event("p", p_callback)

        # run until q is pressed
        plot.show_axes()
        plot.show_grid()
        cpos = plot.show(interactive=False, auto_close=False, interactive_update=not off_screen)

        sargs = dict(
            title_font_size=10,
            label_font_size=10,
            shadow=True,
            n_labels=9,
            italic=True,
            fmt="%.1f",
            font_family="arial",
        )
        plot.add_mesh(
            surfs[0],
            scalars=plot_label,
            log_scale=log,
            scalar_bar_args=sargs,
            cmap="rainbow",
            clim=[mins, maxs],
            show_edges=False,
            pickable=True,
            smooth_shading=True,
            name="FieldPlot",
        )
        plot.isometric_view()
        start = time.time()

        plot.update(1, force_redraw=True)
        first_loop = True
        if export_gif:
            first_loop = True
            plot.write_frame()
        else:
            first_loop = False
        i = 1
        while self._animating:
            if self._pause:
                time.sleep(1)
                plot.update(1, force_redraw=True)
                continue
            # p.remove_actor("FieldPlot")
            if i >= len(surfs):
                if off_screen:
                    break
                i = 0
                first_loop = False
            scalars = surfs[i].point_data[plot_label]
            plot.update_scalars(scalars, render=False)
            # p.add_mesh(surfs[i], scalars=plot_label, log_scale=log, scalar_bar_args=sargs, cmap='rainbow',
            #            show_edges=False, pickable=True, smooth_shading=True, name="FieldPlot")
            plot.textActor.SetInput(variation_var + " = " + variation_list[i])
            if not hasattr(plot, "ren_win"):
                break
            # p.update(1, force_redraw=True)
            time.sleep(max(0, frame_per_seconds - (time.time() - start)))
            start = time.time()
            if off_screen:
                plot.render()
            else:
                plot.update(1, force_redraw=True)
            if first_loop:
                plot.write_frame()

            time.sleep(0.2)
            i += 1
        plot.close()
        for el in aedtplt_files:
            os.remove(el)
        return gifname

    @aedt_exception_handler
    def export_model_obj(self, obj_list=None, export_path=None, export_as_single_objects=False, air_objects=False):
        """Export the model.

        Parameters
        ----------
        obj_list : list, optional
            List of objects to export. Export every model object except 3D ones, vacuum and air objects.
        export_path : str, optional
            Full path to the export obj file.
        export_as_single_objects : bool, optional
            Define if the model will be exported as single obj or list of objs for each object.
        air_objects : bool, optional
            Define if air and vacuum objects will be exported.

        Returns
        -------
        list
            Files obj path.
        """

        assert self._app._aedt_version >= "2021.2", self.logger.error("Object is supported from AEDT 2021 R2.")
        if not export_path:
            export_path = self._app.project_path
        if not obj_list:
            obj_list = self._app.modeler.primitives.object_names
            if not air_objects:
                obj_list = [
                    i
                    for i in obj_list
                    if not self._app.modeler[i].is3d
                    or (
                        self._app.modeler[i].material_name.lower() != "vacuum"
                        and self._app.modeler[i].material_name.lower() != "air"
                    )
                ]
        if export_as_single_objects:
            files_exported = []
            for el in obj_list:
                fname = os.path.join(
                    export_path, "Model_{}_{}.obj".format(el, self._app.modeler[el].material_name.lower())
                )
                self._app.modeler.oeditor.ExportModelMeshToFile(fname, [el])
                files_exported.append(fname)
            return files_exported
        else:
            fname = os.path.join(export_path, "Model_AllObjs_AllMats.obj")
            self._app.modeler.oeditor.ExportModelMeshToFile(fname, obj_list)
            return [fname]

    @aedt_exception_handler
    def export_mesh_obj(self, setup_name=None, intrinsic_dict={}):
        """Export the mesh.

        Parameters
        ----------
        setup_name : str, optional
            Name of the setup. The default is ``None``.
        intrinsic_dict : dict, optipnal.
            Intrinsic dictionary that is needed for the export.
            The default is ``{}``.

        Returns
        -------

        """
        project_path = self._app.project_path

        if not setup_name:
            setup_name = self._app.nominal_adaptive
        face_lists = []
        obj_list = self._app.modeler.primitives.object_names
        for el in obj_list:
            obj_id = self._app.modeler.primitives.get_obj_id(el)
            if not self._app.modeler.primitives.objects[obj_id].is3d or (
                self._app.modeler.primitives.objects[obj_id].material_name != "vacuum"
                and self._app.modeler.primitives.objects[obj_id].material_name != "air"
            ):
                face_lists += self._app.modeler.primitives.get_object_faces(obj_id)
        plot = self.create_fieldplot_surface(face_lists, "Mesh", setup_name, intrinsic_dict)
        if plot:
            file_to_add = self.export_field_plot(plot.name, project_path)
            plot.delete()
            return file_to_add
        return None

    @aedt_exception_handler
    def plot_model_obj(
        self,
        objects=None,
        export_afterplot=True,
        export_path=None,
        plot_separate_objects=True,
        air_objects=False,
        show_axes=True,
        show_grid=True,
        show_legend=True,
        background_color="white",
        object_selector=True,
        windows_size=None,
        off_screen=False,
        color=None,
    ):
        """Plot the model or a substet of objects.

        Parameters
        ----------
        objects : list
            Optional list of objects to plot. If `None` all objects will be exported.
        export_afterplot : bool
            Set to True if the image has to be exported after the plot is completed.
        export_path : str
            File name with full path. If `None` Project directory will be used.
        plot_separate_objects : bool
            Plot each object separately. It may require more time to export from AEDT.
        air_objects : bool
            Plot also air and vacuum objects.
        show_axes : bool
            Define if axis will be visible or not.
        show_grid : bool
            Define if grid will be visible or not.
        show_legend : bool
            Define if legend is visible or not.
        background_color : str, list
            Define the plot background color. Default is `"white"`.
            One of the keys of `pyaedt.generic.constants.CSS4_COLORS` can be used.
        object_selector : bool
            Enable the list of object to hide show objects.
        windows_size : list
            Windows Plot size.
        off_screen : bool
            Off Screen plot
        color : str, list
            Color of the object. Can be color name or list of RGB. If None automatic color.

        Returns
        -------
        list
            List of plot files.
        """
        assert self._app._aedt_version >= "2021.2", self.logger.error("Object is supported from AEDT 2021 R2.")
        files = self.export_model_obj(
            obj_list=objects, export_as_single_objects=plot_separate_objects, air_objects=air_objects
        )
        if export_afterplot:
            imageformat = "png"
        else:
            imageformat = None

        file_list = self._plot_from_aedtplt(
            files,
            imageformat=imageformat,
            export_path=export_path,
            plot_label="3D Model",
            model_color=color,
            show_model_edge=False,
            off_screen=off_screen,
            show_axes=show_axes,
            show_grid=show_grid,
            show_legend=show_legend,
            background_color=background_color,
            windows_size=windows_size,
            object_selector=object_selector,
        )
        return file_list

    @aedt_exception_handler
    def plot_field_from_fieldplot(
        self,
        plotname,
        project_path="",
        meshplot=False,
        setup_name=None,
        intrinsic_dict={},
        imageformat="jpg",
        view="isometric",
        plot_label="Temperature",
        plot_folder=None,
        off_screen=False,
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
        setup_name : str, optional
            Name of the setup or sweep to use for the export. The default is ``None``.
        intrinsic_dict : dict, optional
            Intrinsic dictionary that is needed for the export when ``meshplot="True"``.
            The default is ``{}``.
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
        off_screen : bool, optional
            Export Image without plotting on UI.
        scale_min : float, optional
            Fix the Scale Minimum value.
        scale_max : float, optional
            Fix the Scale Maximum value.

        Returns
        -------
        type
            List of exported files.
        """
        if not plot_folder:
            self.ofieldsreporter.UpdateAllFieldsPlots()
        else:
            self.ofieldsreporter.UpdateQuantityFieldsPlots(plot_folder)

        start = time.time()
        files_to_add = []
        if not project_path:
            project_path = self._app.project_path
        file_to_add = self.export_field_plot(plotname, project_path)
        file_list = None
        if not file_to_add:
            return False
        else:
            files_to_add.append(file_to_add)
            if meshplot:
                if self._app._aedt_version >= "2021.2":
                    files_to_add.extend(self.export_model_obj())
                else:
                    file_to_add = self.export_mesh_obj(setup_name, intrinsic_dict)
                    if file_to_add:
                        files_to_add.append(file_to_add)
            file_list = self._plot_from_aedtplt(
                files_to_add,
                imageformat=imageformat,
                view=view,
                plot_label=plot_label,
                off_screen=off_screen,
                scale_min=scale_min,
                scale_max=scale_max,
            )
            endt = time.time() - start
            print("Field Generation, export and plot time: ", endt)
        return file_list

    @aedt_exception_handler
    def animate_fields_from_aedtplt(
        self,
        plotname,
        plot_folder=None,
        meshplot=False,
        setup_name=None,
        intrinsic_dict={},
        variation_variable="Phi",
        variation_list=["0deg"],
        project_path="",
        export_gif=False,
        off_screen=False,
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
        setup_name : str, optional
            Name of the setup (sweep) to use for the export. The
            default is ``None``.
        intrinsic_dict : dict, optional
            Intrinsic dictionary that is needed for the export. The default
            is ``{}``.
        variation_variable : str, optional
            Variable to vary. The default is ``"Phi"``.
        variation_list : list, optional
            List of variation values with units. The default is
            ``["0deg"]``.
        project_path : str, optional
            Path for the export. The default is ``""``.
        meshplot : bool, optional
             The default is ``False``.
        export_gif : bool, optional
             The default is ``False``.
        off_screen : bool, optional
             Generate the animation without showing an interactive plot.  The default is ``False``.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.
        """
        if not plot_folder:
            self.ofieldsreporter.UpdateAllFieldsPlots()
        else:
            self.ofieldsreporter.UpdateQuantityFieldsPlots(plot_folder)
        files_to_add = []
        if meshplot:
            if self._app._aedt_version >= "2021.2":
                files_to_add.extend(self.export_model_obj())
            else:
                file_to_add = self.export_mesh_obj(setup_name, intrinsic_dict)
                if file_to_add:
                    files_to_add.append(file_to_add)
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
            files_to_add.append(self.export_field_plot(plotname, project_path, plotname + variation_variable + str(el)))

        self._animation_from_aedtflt(
            files_to_add, variation_variable, variation_list, export_gif=export_gif, off_screen=off_screen
        )
        return True

    @aedt_exception_handler
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
        off_screen=False,
    ):
        """Generate a field plot to an image file (JPG or PNG) using PyVista.

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
            Path for the export. The default is ``""``.
        export_gif : bool, optional
             Whether to export to a GIF file. The default is ``False``,
             in which case the plot is exported to a JPG file.
        off_screen : bool, optional
             The default is ``False``.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.
        """
        if not project_path:
            project_path = self._app.project_path
        files_to_add = []
        if meshplot:
            if self._app._aedt_version >= "2021.2":
                files_to_add.extend(self.export_model_obj())
            else:
                file_to_add = self.export_mesh_obj(setup_name, intrinsic_dict)
                if file_to_add:
                    files_to_add.append(file_to_add)
        v = 0
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
                    files_to_add.append(file_to_add)
                plotf.delete()
            v += 1

        return self._animation_from_aedtflt(
            files_to_add, variation_variable, variation_list, export_gif=export_gif, off_screen=off_screen
        )

    @aedt_exception_handler
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

    @aedt_exception_handler
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
