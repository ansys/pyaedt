# -*- coding: utf-8 -*-
"""
Advanced PostProcessing Class
================================


**Description**

This class contains all the advanced post processing functionalities which requires python 3.x packages like numpy or matplotlib



"""
from __future__ import absolute_import
import os

from .PostProcessor import PostProcessor as Post
from ..generic.general_methods import aedt_exception_handler
import time
import math
import warnings

try:
    import numpy as np
except ImportError:
    warnings.warn("The numpy module required to run some functionalities of PostProcess.\n"
                  "Install with \n\npip install numpy\n\nRequires CPython")

try:
    import pyvista as pv
    pyvista_available = True
except ImportError:
    warnings.warn("The pyvista module required to run some functionalities of PostProcess.\n"
                  "Install with \n\npip install pyvista\n\nRequires CPython")

try:
    import matplotlib.pyplot as plt
except ImportError:
    warnings.warn("The matplotlib module required to run some functionalities of PostProcess.\n"
                  "Install with \n\npip install matplotlib\n\nRequires CPython")


class PostProcessor(Post):
    """ """
    def __init__(self, parent):
        Post.__init__(self, parent)

    @aedt_exception_handler
    def get_efields_data(self, setup_sweep_name='', ff_setup="Infinite Sphere1", freq='All'):
        """WARNING this functions requires Numpy installed on your machine
        this function compute Etheta and EPhi and return and returns an array of [theta_range, phi_range, Etheta, Ephi]

        Parameters
        ----------
        setup_sweep_name :
            Name of setup to compute report. if None, nominal adaptive will be applied (Default value = '')
        ff_setup :
            Far Field Setup (Default value = "Infinite Sphere1")
        freq :
            return: [theta_range, phi_range, Etheta, Ephi] (Default value = 'All')

        Returns
        -------
        type
            theta_range, phi_range, Etheta, Ephi]

        """
        if not setup_sweep_name:
            setup_sweep_name = self._parent.nominal_adaptive
        results_dict = {}
        all_sources = self.post_osolution.GetAllSources()
        # assuming only 1 mode
        all_sources_with_modes = [s + ':1' for s in all_sources]

        for n, source in enumerate(all_sources_with_modes):
            edit_sources_ctxt = [["IncludePortPostProcessing:=", False, "SpecifySystemPower:=", False]]
            for m, each in enumerate(all_sources_with_modes):
                if n == m:  # set only 1 source to 1W, all the rest to 0
                    mag = 1
                else:
                    mag = 0
                phase = 0
                edit_sources_ctxt.append(
                    ["Name:=", "{}".format(each), "Magnitude:=", "{}W".format(mag), "Phase:=", "{}deg".format(phase)])
            self.post_osolution.EditSources(edit_sources_ctxt)

            ctxt = ['Context:=', ff_setup]

            sweeps = ['Theta:=', ['All'], 'Phi:=', ['All'], 'Freq:=', [freq]]

            trace_name = "rETheta"
            solnData = self.get_far_field_data(setup_sweep_name=setup_sweep_name, domain=ff_setup,
                                               expression=trace_name)

            data = solnData.nominal_variation

            theta_vals = np.degrees(np.array(data.GetSweepValues('Theta')))
            phi_vals = np.degrees(np.array(data.GetSweepValues('Phi')))
            # phi is outer loop
            theta_unique = np.unique(theta_vals)
            phi_unique = np.unique(phi_vals)
            theta_range = np.linspace(np.min(theta_vals), np.max(theta_vals), np.size(theta_unique))
            phi_range = np.linspace(np.min(phi_vals), np.max(phi_vals), np.size(phi_unique))
            real_theta = np.array(data.GetRealDataValues(trace_name))
            imag_theta = np.array(data.GetImagDataValues(trace_name))

            trace_name = "rEPhi"
            solnData = self.get_far_field_data(setup_sweep_name=setup_sweep_name, domain=ff_setup,
                                               expression=trace_name)
            data = solnData.nominal_variation

            real_phi = np.array(data.GetRealDataValues(trace_name))
            imag_phi = np.array(data.GetImagDataValues(trace_name))

            Etheta = np.vectorize(complex)(real_theta, imag_theta)
            Ephi = np.vectorize(complex)(real_phi, imag_phi)
            source_name_without_mode = source.replace(':1', '')
            results_dict[source_name_without_mode] = [theta_range, phi_range, Etheta, Ephi]
        return results_dict

    @aedt_exception_handler
    def ff_sum_with_delta_phase(self, ff_data, xphase=0, yphase=0):
        """

        Parameters
        ----------
        ff_data :
            
        xphase :
             (Default value = 0)
        yphase :
             (Default value = 0)

        Returns
        -------

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
            
        take_all_nodes :
             (Default value = True)

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
    def _plot_from_aedtplt(self, aedtplt_files=None, imageformat="jpg", view="iso", plot_type="Full",
                           plot_label="Temperature", model_color="#8faf8f", show_model_edge=False, jupyter=False):
        """This function exports the 3D Field Solver Mesh &/or fields as images using Python Plotly. This is currently
        supported only on Windows using CPython

        Parameters
        ----------
        aedtplt_files :
            str or list of aedtplt files generated by AEDT (Default value = None)
        imageformat :
            str default output format (jpg, png, svg, webp)
        view :
            str default output view ( iso, x , y, z, all). all option export all the views files
        plot_type :
            Full" (Default value = "Full")
        plot_label :
            Plot Color Label (Default value = "Temperature")
        model_color :
            3D Model Color. Default "silver"
        show_model_edge :
            boolean
            return: list of files generated (Default value = False)
        jupyter :
             (Default value = False)

        Returns
        -------

        """

        start = time.time()
        if type(aedtplt_files) is str:
            aedtplt_files = [aedtplt_files]

        plot = pv.Plotter()
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

                def create_object_mesh(opacity):
                    """

                    Parameters
                    ----------
                    opacity :
                        

                    Returns
                    -------

                    """
                    try:
                        plot.remove_actor("Volumes")
                    except:
                        pass
                    plot.add_mesh(mesh, show_scalar_bar=False, opacity=opacity, cmap=[model_color], name="3D Model",
                                  show_edges=show_model_edge, edge_color=model_color)
                plot.add_slider_widget(create_object_mesh, [0, 1], style='modern', value=0.75, pointa=[0.81, 0.98], pointb=[0.95, 0.98], title="Opacity")
        filename = os.path.splitext(aedtplt_files[0])[0]
        print(filename)
        for drawing_lines in lines:
            bounding = []
            elements = []
            nodes_list = []
            solution = []
            for l in drawing_lines:
                if "BoundingBox(" in l:
                    bounding = l[l.find("(") + 1:-2].split(",")
                    bounding = [i.strip() for i in bounding]
                if "Elements(" in l:
                    elements = l[l.find("(") + 1:-2].split(",")
                    elements = [int(i.strip()) for i in elements]
                if "Nodes(" in l:
                    nodes_list = l[l.find("(") + 1:-2].split(",")
                    nodes_list = [float(i.strip()) for i in nodes_list]
                if "ElemSolution(" in l:
                    sols = l[l.find("(") + 1:-2].split(",")
                    s = []
                    for i in sols:
                        s.append(self.is_float(i))
                    sols = s
                    # sols = [float(i.strip()) for i in sols]
                    num_solution_per_element = int(sols[2])
                    sols = sols[3:]
                    sols = [sols[i:i + num_solution_per_element] for i in range(0, len(sols), num_solution_per_element)]
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
                surf.point_arrays[plot_label] = temps

            sargs = dict(title_font_size=10, label_font_size=10, shadow=True, n_labels=9, italic=True, fmt="%.1f",
                         font_family="arial")
            if plot_type == "Clip":
                plot.add_text("Full Plot", font_size=15)
                if solution:
                    class MyCustomRoutine():
                        """ """
                        def __init__(self, mesh):
                            self.output = mesh  # Expected PyVista mesh type
                            # default parameters
                            self.kwargs = {
                                'min_val': 0.5,
                                'max_val': 30,
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
                            plot.add_mesh(surf, scalars=plot_label, log_scale=log, scalar_bar_args=sargs, cmap='rainbow',
                                          show_edges=False, clim=[self.kwargs['min_val'], self.kwargs['max_val']],
                                          pickable=True, smooth_shading=True, name="FieldPlot")
                            return

                    engine = MyCustomRoutine(surf)

                    plot.add_box_widget(surf, show_edges=False, scalars=plot_label, log_scale=log, scalar_bar_args=sargs,
                                        cmap='rainbow', pickable=True, smooth_shading=True, name="FieldPlot")

                    plot.add_slider_widget(callback=lambda value: engine('min_val', value),
                                           rng=[np.min(temps), np.max(temps)], title='Lower', style='modern',
                                           value=np.min(temps), pointa=(.5, .98), pointb=(.65, .98))

                    plot.add_slider_widget(callback=lambda value: engine('max_val', value),
                                           rng=[np.min(temps), np.max(temps)], title='Upper', style='modern',
                                           value=np.max(temps), pointa=(.66, .98), pointb=(.8, .98))
                else:
                    plot.add_box_widget(surf, show_edges=True, line_width=0.1, color="grey", pickable=True, smooth_shading=True)
            else:
                plot.add_text("Full Plot", font_size=15)
                if solution:
                    class MyCustomRoutine():
                        """ """
                        def __init__(self, mesh):
                            self.output = mesh  # Expected PyVista mesh type
                            # default parameters
                            self.kwargs = {
                                'min_val': 0.5,
                                'max_val': 30,
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
                            plot.add_mesh(surf, scalars=plot_label, log_scale=log, scalar_bar_args=sargs, cmap='rainbow',
                                          show_edges=False, clim=[self.kwargs['min_val'], self.kwargs['max_val']],
                                          pickable=True, smooth_shading=True, name="FieldPlot")
                            return

                    engine = MyCustomRoutine(surf)

                    plot.add_mesh(surf, show_edges=False, scalars=plot_label, log_scale=log, scalar_bar_args=sargs,
                                  cmap='rainbow', pickable=True, smooth_shading=True, name="FieldPlot")

                    plot.add_slider_widget(callback=lambda value: engine('min_val', value),
                                           rng=[np.min(temps), np.max(temps)], title='Lower', style='modern',
                                           value=np.min(temps), pointa=(.5, .98), pointb=(.65, .98))

                    plot.add_slider_widget(callback=lambda value: engine('max_val', value),
                                           rng=[np.min(temps), np.max(temps)], title='Upper', style='modern',
                                           value=np.max(temps), pointa=(.66, .98), pointb=(.8, .98))
                else:
                    plot.add_mesh(surf, show_edges=True, line_width=0.1, color="grey", pickable=True, smooth_shading=True)
            plot.show_axes()
            plot.show_grid()
            if view == "iso":
                plot.view_isometric()
            elif view == "x":
                plot.view_yz()
            elif view == "y":
                plot.view_xz()
            elif view == "z":
                plot.view_xy()
        files_list = []

        if plot:
            end = time.time() - start
            self.messenger.add_info_message("PyVista Generation tooks {} secs".format(end))
            if jupyter:
                if imageformat:
                    plot.show(screenshot=filename + "." + imageformat)
                    files_list.append(filename + "." + imageformat)
                else:
                    plot.show()
            else:
                def show(screen=None, interactive=True):
                    """

                    Parameters
                    ----------
                    screen :
                         (Default value = None)
                    interactive :
                         (Default value = True)

                    Returns
                    -------

                    """
                    if screen:
                        plot.show(screenshot=screen, interactive=interactive, full_screen=True)
                    else:
                        plot.show(interactive=interactive)

                if imageformat:
                    show(filename + "." + imageformat, True)
                    files_list.append(filename + "." + imageformat)
                else:
                    show(filename + "." + imageformat, False)
            for f in aedtplt_files:
                os.remove(os.path.join(f))
        return files_list


    @aedt_exception_handler
    def _animation_from_aedtflt(self, aedtplt_files=None, variation_var="Time", variation_list=[],
                                plot_label="Temperature", model_color="#8faf8f", export_gif=False, off_screen=False):
        """This function exports the 3D Field Solver Mesh &/or fields as images using Python Plotly. This is currently
        supported only on Windows using CPython

        Parameters
        ----------
        aedtplt_files :
            str or list of aedtplt files generated by AEDT (Default value = None)
        plot_label :
            Plot Color Label (Default value = "Temperature")
        model_color :
            3D Model Color. Default "silver"
            return: list of files generated
        variation_var :
             (Default value = "Time")
        variation_list :
             (Default value = [])
        export_gif :
             (Default value = False)
        off_screen :
             (Default value = False)
        autoclose :
             (Default value = False)

        Returns
        -------

        """
        frame_per_seconds = 0.5
        start = time.time()
        if type(aedtplt_files) is str:
            aedtplt_files = [aedtplt_files]
        plot = pv.Plotter(notebook=False, off_screen=off_screen)
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
                plot.add_mesh(mesh, show_scalar_bar=False, opacity=0.75, cmap=[model_color], name="3D Model",
                              show_edges=False, edge_color=model_color)
                # def create_object_mesh(opacity):
                #     try:
                #         p.remove_actor("Volumes")
                #     except:
                #         pass
                #     p.add_mesh(mesh, show_scalar_bar=False, opacity=opacity, cmap=[model_color], name="3D Model",
                #                show_edges=False, edge_color=model_color)
                # p.add_slider_widget(create_object_mesh, [0,1], style='modern', value=0.75,pointa=[0.81,0.98], pointb=[0.95,0.98],title="Opacity")
        filename = os.path.splitext(aedtplt_files[0])[0]
        print(filename)
        surfs=[]
        log = False
        mins=1e12
        maxs=-1e12
        log = True
        for drawing_lines in lines:
            bounding = []
            elements = []
            nodes_list = []
            solution = []
            for l in drawing_lines:
                if "BoundingBox(" in l:
                    bounding = l[l.find("(") + 1:-2].split(",")
                    bounding = [i.strip() for i in bounding]
                if "Elements(" in l:
                    elements = l[l.find("(") + 1:-2].split(",")
                    elements = [int(i.strip()) for i in elements]
                if "Nodes(" in l:
                    nodes_list = l[l.find("(") + 1:-2].split(",")
                    nodes_list = [float(i.strip()) for i in nodes_list]
                if "ElemSolution(" in l:
                    sols = l[l.find("(") + 1:-2].split(",")
                    s = []
                    for i in sols:
                        s.append(self.is_float(i))
                    sols = s
                    # sols = [float(i.strip()) for i in sols]
                    num_solution_per_element = int(sols[2])
                    sols = sols[3:]
                    sols = [sols[i:i + num_solution_per_element] for i in range(0, len(sols), num_solution_per_element)]
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
                if np.min(temps) <=0:
                    log = False
                surf.point_arrays[plot_label] = temps
            if solution:
                surfs.append(surf)
                if np.min(temps)<mins:
                    mins=np.min(temps)
                if np.max(temps) > maxs:
                    maxs = np.max(temps)

        self._animating = True
        gifname=None
        if export_gif:
            gifname= os.path.splitext(aedtplt_files[0])[0]+".gif"
            plot.open_gif(gifname)
        def q_callback():
            """exit when user wants to leave"""
            self._animating = False
        self._pause=False
        def p_callback():
            """exit when user wants to leave"""
            self._pause = not self._pause
        plot.add_text('Press p for Play/Pause, Press q to exit ', font_size=8, position='upper_left')
        plot.add_text(' ', font_size=10, position=[0, 0])
        plot.add_key_event("q", q_callback)
        plot.add_key_event("p", p_callback)

        # run until q is pressed
        plot.show_axes()
        plot.show_grid()
        cpos = plot.show(interactive=False, auto_close=False,
                  interactive_update=not off_screen)


        sargs = dict(title_font_size=10, label_font_size=10, shadow=True, n_labels=9, italic=True, fmt="%.1f",
                     font_family="arial")
        plot.add_mesh(surfs[0], scalars=plot_label, log_scale=log, scalar_bar_args=sargs, cmap='rainbow', clim=[mins, maxs],
                      show_edges=False, pickable=True, smooth_shading=True, name="FieldPlot")
        plot.isometric_view()
        start = time.time()
        plot.update(1, force_redraw=True)
        first_loop = True
        if export_gif:
            first_loop = True
            plot.write_frame()
        else:
            first_loop = False
        i=1
        while self._animating:
            if self._pause:
                time.sleep(1)
                plot.update(1, force_redraw=True)
                continue
            #p.remove_actor("FieldPlot")
            if i>=len(surfs):
                if off_screen:
                    break
                i=0
                first_loop = False
            scalars = surfs[i].point_arrays[plot_label]
            plot.update_scalars(scalars, render=False)
            # p.add_mesh(surfs[i], scalars=plot_label, log_scale=log, scalar_bar_args=sargs, cmap='rainbow',
            #            show_edges=False, pickable=True, smooth_shading=True, name="FieldPlot")
            plot.textActor.SetInput(variation_var + " = " + variation_list[i])
            if not hasattr(plot, 'ren_win'):
                break
            #p.update(1, force_redraw=True)
            time.sleep(max(0, frame_per_seconds - (time.time() - start)))
            start = time.time()
            if off_screen:
                plot.render()
            else:
                plot.update(1, force_redraw=True)
            if first_loop:
                plot.write_frame()

            time.sleep(0.2)
            i+=1
        plot.close()
        for el in  aedtplt_files:
            os.remove(el)
        return gifname


    @aedt_exception_handler
    def export_model_obj(self):
        """ """
        assert self._parent._aedt_version >= "2021.2", self.messenger.add_error_message("Obj supported from AEDT 2021R2")
        project_path = self._parent.project_path
        obj_list = self._parent.modeler.primitives.get_all_objects_names()
        obj_list = [i for i in obj_list if not self._parent.modeler.primitives.objects[
            self._parent.modeler.primitives.get_obj_id(i)].is3d or (
                            self._parent.modeler.primitives.objects[
                                self._parent.modeler.primitives.get_obj_id(i)].material_name.lower() != "vacuum" and
                            self._parent.modeler.primitives.objects[
                                self._parent.modeler.primitives.get_obj_id(i)].material_name.lower() != "air")]
        self._parent.modeler.oeditor.ExportModelMeshToFile(os.path.join(project_path, "Model.obj"),
                                                           obj_list)
        return os.path.join(project_path, "Model.obj")

    @aedt_exception_handler
    def export_mesh_obj(self, setup_name=None, intrinsic_dict={}):
        """

        Parameters
        ----------
        setup_name :
             (Default value = None)
        intrinsic_dict :
             (Default value = {})

        Returns
        -------

        """
        project_path = self._parent.project_path

        if not setup_name:
            setup_name = self._parent.nominal_adaptive
        face_lists = []
        obj_list = self._parent.modeler.primitives.get_all_objects_names()
        for el in obj_list:
            obj_id = self._parent.modeler.primitives.get_obj_id(el)
            if not self._parent.modeler.primitives.objects[obj_id].is3d or (
                    self._parent.modeler.primitives.objects[obj_id].material_name != "vacuum" and
                    self._parent.modeler.primitives.objects[obj_id].material_name != "air"):
                face_lists += self._parent.modeler.primitives.get_object_faces(obj_id)
        plot = self.create_fieldplot_surface(face_lists, "Mesh", setup_name, intrinsic_dict)
        if plot:
            file_to_add = self.export_field_plot(plot.name, project_path)
            plot.delete()
            return file_to_add
        return None

    @aedt_exception_handler
    def plot_model_obj(self, export_afterplot=True, jupyter=False):
        """

        Parameters
        ----------
        export_afterplot :
             (Default value = True)
        jupyter :
             (Default value = False)

        Returns
        -------

        """
        assert self._parent._aedt_version >= "2021.2", self.messenger.add_error_message("Obj supported from AEDT 2021R2")
        files = [self.export_model_obj()]
        if export_afterplot:
            imageformat='jpg'
        else:
            imageformat=None
        file_list = self._plot_from_aedtplt(files, imageformat=imageformat, plot_label="3D Model", model_color="#8faf8f", show_model_edge=False, jupyter=jupyter)
        return file_list

    @aedt_exception_handler
    def plot_field_from_fieldplot(self, plotname, project_path="", meshplot=False, setup_name=None,
                                  intrinsic_dict={}, imageformat="jpg", view="iso", plot_label="Temperature", plot_folder=None):
        """Export Field Plot to picture format (jpg, png) using PLOTLY method which rebuilds the mesh and overlap fields on it

        Parameters
        ----------
        plotname :
            name of the plot to export
        project_path :
            path where to save the image (Default value = "")
        meshplot :
            create and plot the mesh over the fields (Default value = False)
        setup_name :
            name of the setup - sweep to use for the export (Default value = None)
        intrinsic_dict :
            intrinsic dictionary needed for export of the mesh. Valid only if meshplot is True (Default value = {})
        imageformat :
            image format. Defalult jpg (Default value = "jpg")
        view :
            image view. Default iso
        plot_label :
            Plot Type. Default Temperature
        plot_folder :
            Plot Folder to force update before export the field. If none all the plots will be updated (Default value = None)

        Returns
        -------
        type
            list of the files exported

        """
        if not plot_folder:
            self.ofieldsreporter.UpdateAllFieldsPlots()
        else:
            self.ofieldsreporter.UpdateQuantityFieldsPlots(plot_folder)

        start = time.time()
        files_to_add = []
        if not project_path:
            project_path = self._parent.project_path
        file_to_add = self.export_field_plot(plotname, project_path)
        file_list=None
        if not file_to_add:
            return False
        else:
            files_to_add.append(file_to_add)
            if meshplot:
                if self._parent._aedt_version >= "2021.2":
                    files_to_add.append(self.export_model_obj())
                else:
                    file_to_add = self.export_mesh_obj(setup_name, intrinsic_dict)
                    if file_to_add:
                        files_to_add.append(file_to_add)
            file_list = self._plot_from_aedtplt(files_to_add, imageformat=imageformat, view=view,
                                                plot_label=plot_label)
            endt = time.time() - start
            print("Field Generation, export and plot time: ", endt)
        return file_list

    @staticmethod
    def is_float(istring):
        """

        Parameters
        ----------
        istring :
            

        Returns
        -------

        """
        try:
            return float(istring.strip())
        except Exception:
            return 0


    @aedt_exception_handler
    def animate_fields_from_aedtplt(self, plotname, plot_folder=None, meshplot=False, setup_name=None,
                                    intrinsic_dict={}, variation_variable="Phi", variation_list=['0deg'],
                                    project_path="", export_gif=False, off_screen=False):
        """Generate  Field Plot to picture format (jpg, png) using PYVISTA method which rebuilds the mesh and overlap fields on it

        Parameters
        ----------
        plotname :
            name of the plot to use or name o
        plot_folder :
            optional name of the plot_folder (Default value = None)
        setup_name :
            name of the setup - sweep to use for the export (Default value = None)
        intrinsic_dict :
            intrinsic dictionary needed for export (Default value = {})
        variation_variable :
            variation variable. Default "Phi"
        variation_list :
            list of variation values (Default value = ['0deg'])
        project_path :
            path for the export (Default value = "")
        meshplot :
             (Default value = False)
        export_gif :
             (Default value = False)
        off_screen :
             (Default value = False)

        Returns
        -------
        type
            Boolean

        """
        if not plot_folder:
            self.ofieldsreporter.UpdateAllFieldsPlots()
        else:
            self.ofieldsreporter.UpdateQuantityFieldsPlots(plot_folder)
        files_to_add = []
        if meshplot:
            if self._parent._aedt_version >= "2021.2":
                files_to_add.append(self.export_model_obj())
            else:
                file_to_add = self.export_mesh_obj(setup_name, intrinsic_dict)
                if file_to_add:
                    files_to_add.append(file_to_add)
        for el in variation_list:
            self._parent.odesign.ChangeProperty(
                [
                    "NAME:AllTabs",
                    [
                        "NAME:FieldsPostProcessorTab",
                        [
                            "NAME:PropServers",
                            "FieldsReporter:"+plotname
                        ],
                        [
                            "NAME:ChangedProps",
                            [
                                "NAME:"+variation_variable,
                                "Value:="	, el
                            ]
                        ]
                    ]
                ])
            files_to_add.append(self.export_field_plot(plotname, project_path,plotname+variation_variable+str(el)))

        self._animation_from_aedtflt(files_to_add, variation_variable, variation_list, export_gif=export_gif, off_screen=off_screen)
        return True

    @aedt_exception_handler
    def animate_fields_from_aedtplt_2(self, quantityname, object_list, plottype, meshplot=False, setup_name=None,
                                    intrinsic_dict={}, variation_variable="Phi", variation_list=['0deg'],
                                    project_path="", export_gif=False, off_screen=False):
        """Generate  Field Plot to picture format (jpg, png) using PYVISTA method which rebuilds the mesh and overlap fields on it.
        This method creates the plot and export it. is alternative to animate_fields_from_aedtplt which uses existing plot

        Parameters
        ----------
        quantityname :
            name of the plot to use or name o
        object_list :
            optional name of the plot_folder
        plottype :
            Plot Type. "Surface", "Volume" or "CutPlane"
        setup_name :
            name of the setup - sweep to use for the export (Default value = None)
        intrinsic_dict :
            intrinsic dictionary needed for export (Default value = {})
        variation_variable :
            variation variable. Default "Phi"
        variation_list :
            list of variation values (Default value = ['0deg'])
        project_path :
            path for the export (Default value = "")
        meshplot :
             (Default value = False)
        export_gif :
             (Default value = False)
        off_screen :
             (Default value = False)

        Returns
        -------
        type
            Boolean

        """
        if not project_path:
            project_path = self._parent.project_path
        files_to_add = []
        if meshplot:
            if self._parent._aedt_version >= "2021.2":
                files_to_add.append(self.export_model_obj())
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

        return self._animation_from_aedtflt(files_to_add, variation_variable, variation_list, export_gif=export_gif, off_screen=off_screen)


    @aedt_exception_handler
    def far_field_plot(self, ff_data, x=0, y=0, qty='rETotal', dB=True, array_size=[4, 4]):
        """

        Parameters
        ----------
        ff_data :
            
        x :
             (Default value = 0)
        y :
             (Default value = 0)
        qty :
             (Default value = 'rETotal')
        dB :
             (Default value = True)
        array_size :
             (Default value = [4)
        4] :
            

        Returns
        -------

        """

        loc_offset = 2  # if array index is not starting at [1,1]
        xphase = float(y)
        yphase = float(x)
        array_shape = (array_size[0], array_size[1])
        weight = np.zeros(array_shape, dtype=complex)
        mag = np.ones(array_shape, dtype='object')
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
                current_index_str = '[' + str(m + 1 + loc_offset) + ',' + str(n + 1 + loc_offset) + ']'
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
        all_qtys['rEPhi'] = rEphi_fields
        all_qtys['rETheta'] = rEtheta_fields
        all_qtys['rETotal'] = np.sqrt(np.power(np.abs(rEphi_fields), 2) + np.power(np.abs(rEtheta_fields), 2))

        pin = np.sum(w)
        print(str(pin))
        real_gain = 2 * np.pi * np.abs(np.power(all_qtys['rETotal'], 2)) / pin / 377
        all_qtys['RealizedGain'] = real_gain

        if dB:
            if 'Gain' in qty:
                qty_to_plot = 10 * np.log10(np.abs(all_qtys[qty]))
            else:
                qty_to_plot = 20 * np.log10(np.abs(all_qtys[qty]))
            qty_str = qty + ' (dB)'
        else:
            qty_to_plot = np.abs(all_qtys[qty])
            qty_str = qty + ' (mag)'

        plt.figure(figsize=(15, 10))
        plt.title(qty_str)
        plt.xlabel('Theta (degree)')
        plt.ylabel('Phi (degree)')

        plt.imshow(qty_to_plot, cmap='jet')
        plt.colorbar()

        np.max(qty_to_plot)

    @aedt_exception_handler
    def create_3d_plot(self, solution_data, nominal_sweep="Freq", nominal_value=1, primary_sweep="Theta",
                       secondary_sweep="Phi"):
        """Create 3D Plot with matplotlib.

        Parameters
        ----------
        solution_data :
            Solution Data Input
        nominal_sweep :
            Nominal Sweep Name (Default value = "Freq")
        nominal_value :
            Nominal Sweep Value (Default value = 1)
        primary_sweep :
            Primary Sweep. Default Theta
        secondary_sweep :
            Secondary Sweep. Default Phi

        Returns
        -------

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
        ax1 = fig1.add_subplot(1, 1, 1, projection='3d')
        plot = ax1.plot_surface(
            X, Y, Z, rstride=1, cstride=1, cmap=plt.get_cmap('jet'),
            linewidth=0, antialiased=True, alpha=0.5)
        fig1.set_size_inches(10, 10)
