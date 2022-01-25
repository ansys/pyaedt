"""
This module contains the `PostProcessor` class.

It contains all advanced postprocessing functionalities that require Python 3.x packages like NumPy and Matplotlib.
"""
from __future__ import absolute_import

import math
import os
import time
import warnings
import csv

from pyaedt.generic.general_methods import aedt_exception_handler
from pyaedt.modules.PostProcessor import PostProcessor as Post
from pyaedt.generic.constants import CSS4_COLORS, AEDT_UNITS

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
except:
    pass


def is_notebook():
    """Check if pyaedt is running in Jupyter or not.

    Returns
    -------
    bool
    """
    try:
        shell = get_ipython().__class__.__name__
        if shell == "ZMQInteractiveShell":
            return True  # Jupyter notebook or qtconsole
        else:
            return False
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


class ObjClass(object):
    """Class that manages mesh files to be plotted in pyvista.

    Parameters
    ----------
    path : str
        Full path to the file.
    color : str or tuple
        Can be a string with color name or a tuple with (r,g,b) values.
    opacity : float
        Value between 0 to 1 of opacity.
    units : str
        Model units.

    """

    def __init__(self, path, color, opacity, units):
        self.path = path
        self._color = (0, 0, 0)
        self.color = color
        self.opacity = opacity
        self.units = units
        self._cached_mesh = None
        self._cached_polydata = None
        self.name = os.path.splitext(os.path.basename(self.path))[0]

    @property
    def color(self):
        return self._color

    @color.setter
    def color(self, value):
        if isinstance(value, (tuple, list)):
            self._color = value
        elif value in CSS4_COLORS:
            h = CSS4_COLORS[value].lstrip("#")
            self._color = tuple(int(h[i : i + 2], 16) for i in (0, 2, 4))


class FieldClass(object):
    """Class to manage Field data to be plotted in pyvista.

    Parameters
    ----------
    path : str
        Full path to the file.
    log_scale : bool, optional
        Either if the field has to be plotted log or not. The default value is ``True``.
    coordinate_units : str, optional
        Fields coordinates units. The default value is ``"meter"``.
    opacity : float, optional
        Value between 0 to 1 of opacity. The default value is ``1``.
    color_map : str, optional
        Color map of field plot. The default value is ``"rainbow"``.
    label : str, optional
        Name of the field. The default value is ``"Field"``.
    tolerance : float, optional
        Delauny tolerance value used for interpolating points. The default value is ``1e-3``.
    headers : int, optional
        Number of lines to of the file containing header info that has to be removed.
        The default value is ``2``.
    """

    def __init__(
        self,
        path,
        log_scale=True,
        coordinate_units="meter",
        opacity=1,
        color_map="rainbow",
        label="Field",
        tolerance=1e-3,
        headers=2,
        show_edge=True,
    ):
        self.path = path
        self.log_scale = log_scale
        self.units = coordinate_units
        self.opacity = opacity
        self.color_map = color_map
        self._cached_mesh = None
        self._cached_polydata = None
        self.label = label
        self.name = os.path.splitext(os.path.basename(self.path))[0]
        self.color = (255, 0, 0)
        self.surface_mapping_tolerance = tolerance
        self.header_lines = headers
        self.show_edge = show_edge
        self._is_frame = False


class ModelPlotter(object):
    """Class that manage the plot data.

    Examples
    --------
    This Class can be instantiated within Pyaedt (with plot_model_object or different field plots
    and standalone.
    Here an example of standalone project

    >>> model = ModelPlotter()
    >>> model.add_object(r'D:\Simulation\antenna.obj', (200,20,255), 0.6, "in")
    >>> model.add_object(r'D:\Simulation\helix.obj', (0,255,0), 0.5, "in")
    >>> model.add_field_from_file(r'D:\Simulation\helic_antenna.csv', True, "meter", 1)
    >>> model.background_color = (0,0,0)
    >>> model.plot()

    And here an example of animation:

    >>> model = ModelPlotter()
    >>> model.add_object(r'D:\Simulation\antenna.obj', (200,20,255), 0.6, "in")
    >>> model.add_object(r'D:\Simulation\helix.obj', (0,255,0), 0.5, "in")
    >>> frames = [r'D:\Simulation\helic_antenna.csv', r'D:\Simulation\helic_antenna_10.fld',
    >>>           r'D:\Simulation\helic_antenna_20.fld', r'D:\Simulation\helic_antenna_30.fld',
    >>>           r'D:\Simulation\helic_antenna_40.fld']
    >>> model.gif_file = r"D:\Simulation\animation.gif"
    >>> model.animate()
    """

    def __init__(self):
        self._objects = []
        self._fields = []
        self._frames = []
        self.show_axes = True
        self.show_legend = True
        self.show_grid = True
        self.is_notebook = is_notebook()
        self.gif_file = None
        self._background_color = (255, 255, 255)
        self.off_screen = False
        self.windows_size = [1024, 768]
        self.pv = None
        self._orientation = ["xy", 0, 0, 0]
        self.units = "meter"
        self.frame_per_seconds = 3
        self._plot_meshes = []
        self.range_min = None
        self.range_max = None
        self.image_file = None
        self._camera_position = "yz"
        self._roll_angle = 0
        self._azimuth_angle = 45
        self._elevation_angle = 20
        self._zoom = 1
        self._isometric_view = True
        self.bounding_box = True
        self.color_bar = True

    @property
    def isometric_view(self):
        """Enable or disable the default iso view.

        Parameters
        ----------
        value : bool
            Either if iso view is enabled or disabled.

        Returns
        -------
        bool
        """
        return self._isometric_view

    @isometric_view.setter
    def isometric_view(self, value=True):
        self._isometric_view = value

    @property
    def camera_position(self):
        """Get/Set the camera position value. It disables the default iso view.

        Parameters
        ----------
        value : str
            Value of camera position. One of `"xy"`, `"xz"`,`"yz"`.

        Returns
        -------
        str
        """
        return self._camera_position

    @camera_position.setter
    def camera_position(self, value):
        self._camera_position = value
        self.isometric_view = False

    @property
    def roll_angle(self):
        """Get/Set the roll angle value. It disables the default iso view.

        Parameters
        ----------
        value : float
            Value of roll angle in degrees.

        Returns
        -------
        float
        """
        return self._roll_angle

    @roll_angle.setter
    def roll_angle(self, value=20):
        self._roll_angle = value
        self.isometric_view = False

    @property
    def azimuth_angle(self):
        """Get/Set the azimuth angle value. It disables the default iso view.

        Parameters
        ----------
        value : float
            Value of azimuth angle in degrees.

        Returns
        -------
        float
        """
        return self._azimuth_angle

    @azimuth_angle.setter
    def azimuth_angle(self, value=45):
        self._azimuth_angle = value
        self.use_default_iso_view = False

    @property
    def elevation_angle(self):
        """Get/Set the elevation angle value. It disables the default iso view.

        Parameters
        ----------
        value : float
            Value of elevation angle in degrees.

        Returns
        -------
        float
        """
        return self._elevation_angle

    @elevation_angle.setter
    def elevation_angle(self, value=45):
        self._elevation_angle = value
        self.use_default_iso_view = False

    @property
    def zoom(self):
        """Get/Set the zoom value.

        Parameters
        ----------
        value : float
            Value of zoom in degrees.

        Returns
        -------
        float
        """
        return self._zoom

    @zoom.setter
    def zoom(self, value=1):
        self._zoom = value

    @aedt_exception_handler
    def set_orientation(self, camera_position="xy", roll_angle=0, azimuth_angle=45, elevation_angle=20):
        """Change the plot default orientation.

        Parameters
        ----------
        camera_position : str
            Camera view. Default is `"xy"`. Options are `"xz"` and `"yz"`.
        roll_angle : int, float
            Roll camera angle on the specified the camera_position.
        azimuth_angle : int, float
            Azimuth angle of camera on the specified the camera_position.
        elevation_angle : int, float
            Elevation camera angle on the specified the camera_position.

        Returns
        -------
        bool
        """
        if camera_position in ["xy", "yz", "xz"]:
            self.camera_position = camera_position
        else:
            warnings.warn("Plane has to be one of xy, xz, yz.")
        self.roll_angle = roll_angle
        self.azimuth_angle = azimuth_angle
        self.elevation_angle = elevation_angle
        self.use_default_iso_view = False
        return True

    @property
    def background_color(self):
        """Get/Set Backgroun Color.
        It can be a tuple of (r,g,b)  or color name."""
        return self._background_color

    @background_color.setter
    def background_color(self, value):
        if isinstance(value, (tuple, list)):
            self._background_color = value
        elif value in CSS4_COLORS:
            h = CSS4_COLORS[value].lstrip("#")
            self._background_color = tuple(int(h[i : i + 2], 16) for i in (0, 2, 4))

    @property
    def fields(self):
        """List of fields object.

        Returns
        -------
        list of :class:`pyaedt.modules.AdvancedPostProcessing.FieldClass`
        """
        return self._fields

    @property
    def frames(self):
        """Frames list for animation.

        Returns
        -------
        list of :class:`pyaedt.modules.AdvancedPostProcessing.FieldClass`
        """
        return self._frames

    @property
    def objects(self):
        """List of class objects.

        Returns
        -------
        list of :class:`pyaedt.modules.AdvancedPostProcessing.ObjClass`
        """
        return self._objects

    @aedt_exception_handler
    def add_object(self, cad_path, cad_color="dodgerblue", opacity=1, units="mm"):
        """Add an mesh file to the scenario. It can be obj or any of pyvista supported files.

        Parameters
        ----------
        cad_path : str
            Full path to the file.
        cad_color : str or tuple
            Can be a string with color name or a tuple with (r,g,b) values.
            The default value is ``"dodgerblue"``.
        opacity : float
            Value between 0 to 1 of opacity. The default value is ``1``.
        units : str
            Model units. The default value is ``"mm"``.

        Returns
        -------
        bool
        """
        self._objects.append(ObjClass(cad_path, cad_color, opacity, units))
        self.units = units
        return True

    @aedt_exception_handler
    def add_field_from_file(
        self,
        field_path,
        log_scale=True,
        coordinate_units="meter",
        opacity=1,
        color_map="rainbow",
        label_name="Field",
        surface_mapping_tolerance=1e-3,
        header_lines=2,
        show_edges=True,
    ):
        """Add a field file to the scenario.
        It can be aedtplt, fld or csv file or any txt file with 4 column [x,y,z,field].
        If text file they have to be space separated column.

        Parameters
        ----------
        field_path : str
            Full path to the file.
        log_scale : bool
            Either if the field has to be plotted log or not.
        coordinate_units : str
            Fields coordinates units.
        opacity : float
            Value between 0 to 1 of opacity.
        color_map : str
            Color map of field plot. Default rainbow.
        label_name : str, optional
            Name of the field.
        surface_mapping_tolerance : float, optional
            Delauny tolerance value used for interpolating points.
        header_lines : int
            Number of lines to of the file containing header info that has to be removed.

        Returns
        -------
        bool
        """
        self._fields.append(
            FieldClass(
                field_path,
                log_scale,
                coordinate_units,
                opacity,
                color_map,
                label_name,
                surface_mapping_tolerance,
                header_lines,
                show_edges,
            )
        )

    @aedt_exception_handler
    def add_frames_from_file(
        self,
        field_files,
        log_scale=True,
        coordinate_units="meter",
        opacity=1,
        color_map="rainbow",
        label_name="Field",
        surface_mapping_tolerance=1e-3,
        header_lines=2,
    ):
        """Add a field file to the scenario. It can be aedtplt, fld or csv file.

        Parameters
        ----------
        field_files : list
            List of full path to frame file.
        log_scale : bool
            Either if the field has to be plotted log or not.
        coordinate_units : str
            Fields coordinates units.
        opacity : float
            Value between 0 to 1 of opacity.
        color_map : str
            Color map of field plot. Default rainbow.
        label_name : str, optional
            Name of the field.
        surface_mapping_tolerance : float, optional
            Delauny tolerance value used for interpolating points.
        header_lines : int
            Number of lines to of the file containing header info that has to be removed.
        Returns
        -------
        bool
        """
        for field in field_files:
            self._frames.append(
                FieldClass(
                    field,
                    log_scale,
                    coordinate_units,
                    opacity,
                    color_map,
                    label_name,
                    surface_mapping_tolerance,
                    header_lines,
                    False,
                )
            )
            self._frames[-1]._is_frame = True

    @aedt_exception_handler
    def add_field_from_data(
        self,
        coordinates,
        fields_data,
        log_scale=True,
        coordinate_units="meter",
        opacity=1,
        color_map="rainbow",
        label_name="Field",
        surface_mapping_tolerance=1e-3,
        show_edges=True,
    ):
        """Add field data to the scenario.

        Parameters
        ----------
        coordinates : list of list
            List of list [x,y,z] coordinates.
        fields_data : list
            List of list Fields Value.
        log_scale : bool
            Either if the field has to be plotted log or not.
        coordinate_units : str
            Fields coordinates units.
        opacity : float
            Value between 0 to 1 of opacity.
        color_map : str
            Color map of field plot. Default rainbow.
        label_name : str, optional
            Name of the field.
        surface_mapping_tolerance : float, optional
            Delauny tolerance value used for interpolating points.

        Returns
        -------
        bool
        """
        self._fields.append(
            FieldClass(
                None, log_scale, coordinate_units, opacity, color_map, label_name, surface_mapping_tolerance, show_edges
            )
        )
        vertices = np.array(coordinates)
        filedata = pv.PolyData(vertices)
        filedata = filedata.delaunay_2d(tol=surface_mapping_tolerance)
        filedata.point_data[self.fields[-1].label] = np.array(fields_data)
        self.fields[-1]._cached_polydata = filedata

    @aedt_exception_handler
    def _triangle_vertex(self, elements_nodes, num_nodes_per_element, take_all_nodes=True):
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
    def _read_mesh_files(self, read_frames=False):
        for cad in self.objects:
            if not cad._cached_polydata:
                filedata = pv.read(cad.path)
                cad._cached_polydata = filedata
            color_cad = [i / 255 for i in cad.color]
            cad._cached_mesh = self.pv.add_mesh(cad._cached_polydata, color=color_cad, opacity=cad.opacity)
        obj_to_iterate = [i for i in self._fields]
        if read_frames:
            for i in self.frames:
                obj_to_iterate.append(i)
        for field in obj_to_iterate:
            if field.path and not field._cached_polydata:
                if ".aedtplt" in field.path:
                    lines = []
                    with open(field.path, "r") as f:
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
                    surf = None
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
                                    sols[i : i + num_solution_per_element]
                                    for i in range(0, len(sols), num_solution_per_element)
                                ]
                                solution = [sum(i) / num_solution_per_element for i in sols]

                        nodes = [
                            [nodes_list[i], nodes_list[i + 1], nodes_list[i + 2]] for i in range(0, len(nodes_list), 3)
                        ]
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
                            surf.point_data[field.label] = temps
                    field.log = log
                    field._cached_polydata = surf
                else:
                    points = []
                    nodes = []
                    values = []
                    with open(field.path, "r") as f:
                        try:
                            lines = f.read().splitlines()[field.header_lines :]
                            if ".csv" in field.path:
                                sniffer = csv.Sniffer()
                                delimiter = sniffer.sniff(lines[0]).delimiter
                            else:
                                delimiter = " "
                            if len(lines) > 2000 and not field._is_frame:
                                lines = list(dict.fromkeys(lines))
                                # decimate = 2
                                # del lines[decimate - 1 :: decimate]
                        except:
                            lines = []
                        for line in lines:
                            tmp = line.split(delimiter)
                            nodes.append([float(tmp[0]), float(tmp[1]), float(tmp[2])])
                            values.append(float(tmp[3]))
                    if nodes:
                        try:
                            conv = 1 / AEDT_UNITS["Length"][self.units]
                        except:
                            conv = 1
                        vertices = np.array(nodes) * conv
                        filedata = pv.PolyData(vertices)
                        filedata = filedata.delaunay_2d(tol=field.surface_mapping_tolerance)
                        filedata.point_data[field.label] = np.array(values)
                        field._cached_polydata = filedata

    @aedt_exception_handler
    def _add_buttons(self):
        size = int(self.pv.window_size[1] / 40)
        startpos = self.pv.window_size[1] - 2 * size
        endpos = 100
        color = self.pv.background_color
        axes_color = [0 if i >= 0.5 else 1 for i in color]
        buttons = []
        texts = []
        max_elements = (startpos - endpos) // (size + (size // 10))

        class SetVisibilityCallback:
            """Helper callback to keep a reference to the actor being modified."""

            def __init__(self, actor):
                self.actor = actor

            def __call__(self, state):
                self.actor.SetVisibility(state)

        class ChangePageCallback:
            """Helper callback to keep a reference to the actor being modified."""

            def __init__(self, plot, actor, axes_color):
                self.plot = plot
                self.actors = actor
                self.id = 0
                self.endpos = 100
                self.size = int(plot.window_size[1] / 40)
                self.startpos = plot.window_size[1] - 2 * self.size
                self.max_elements = (self.startpos - self.endpos) // (self.size + (self.size // 10))
                self.i = self.max_elements
                self.axes_color = axes_color

            def __call__(self, state):
                self.plot.button_widgets = [self.plot.button_widgets[0]]
                self.id += 1
                k = 0
                startpos = self.startpos
                while k < self.max_elements:
                    if len(self.text) > k:
                        self.plot.remove_actor(self.text[k])
                    k += 1
                self.text = []
                k = 0

                while k < self.max_elements:
                    if self.i >= len(self.actors):
                        self.i = 0
                        self.id = 0
                    callback = SetVisibilityCallback(self.actors[self.i])
                    self.plot.add_checkbox_button_widget(
                        callback,
                        value=self.actors[self.i]._cached_mesh.GetVisibility() == 1,
                        position=(5.0, startpos),
                        size=self.size,
                        border_size=1,
                        color_on=[i / 255 for i in self.actors[self.i].color],
                        color_off="grey",
                        background_color=None,
                    )
                    self.text.append(
                        self.plot.add_text(
                            self.actors[self.i].name,
                            position=(25.0, startpos),
                            font_size=self.size // 3,
                            color=self.axes_color,
                        )
                    )
                    startpos = startpos - self.size - (self.size // 10)
                    k += 1
                    self.i += 1

        el = 1
        for actor in self.objects:
            if el < max_elements:
                callback = SetVisibilityCallback(actor._cached_mesh)
                buttons.append(
                    self.pv.add_checkbox_button_widget(
                        callback,
                        value=True,
                        position=(5.0, startpos + 50),
                        size=size,
                        border_size=1,
                        color_on=[i / 255 for i in actor.color],
                        color_off="grey",
                        background_color=None,
                    )
                )
                texts.append(
                    self.pv.add_text(actor.name, position=(50.0, startpos + 50), font_size=size // 3, color=axes_color)
                )
                startpos = startpos - size - (size // 10)
                el += 1
        for actor in self.fields:
            if actor._cached_mesh and el < max_elements:
                callback = SetVisibilityCallback(actor._cached_mesh)
                buttons.append(
                    self.pv.add_checkbox_button_widget(
                        callback,
                        value=True,
                        position=(5.0, startpos + 50),
                        size=size,
                        border_size=1,
                        color_on="blue",
                        color_off="grey",
                        background_color=None,
                    )
                )
                texts.append(
                    self.pv.add_text(actor.name, position=(50.0, startpos + 50), font_size=size // 3, color=axes_color)
                )
                startpos = startpos - size - (size // 10)
                el += 1
        actors = [i for i in self._fields if i._cached_mesh] + self._objects
        if texts and len(texts) >= max_elements:
            callback = ChangePageCallback(self.pv, actors, axes_color)
            self.pv.add_checkbox_button_widget(
                callback,
                value=True,
                position=(5.0, self.pv.window_size[1]),
                size=int(1.5 * size),
                border_size=2,
                color_on=axes_color,
                color_off=axes_color,
            )
            self.pv.add_text("Next", position=(50.0, self.pv.window_size[1]), font_size=size // 3, color="grey")
            self.pv.button_widgets.insert(
                0, self.pv.button_widgets.pop(self.pv.button_widgets.index(self.pv.button_widgets[-1]))
            )

    @aedt_exception_handler
    def plot(self, export_image_path=None):
        """Plot the current available Data.

        Parameters
        ----------

        export_image_path : str
            Path to image to save.

        Returns
        -------
        bool
        """
        start = time.time()
        self.pv = pv.Plotter(notebook=self.is_notebook, off_screen=self.off_screen, window_size=self.windows_size)
        self.pv.background_color = [i / 255 for i in self.background_color]
        self._read_mesh_files()

        axes_color = [0 if i >= 128 else 1 for i in self.background_color]
        if self.color_bar:
            sargs = dict(
                title_font_size=10,
                label_font_size=10,
                shadow=True,
                n_labels=9,
                italic=True,
                fmt="%.1f",
                font_family="arial",
                interactive=True,
                color=axes_color,
                vertical=False,
            )
        else:
            sargs = dict(
                position_x=2,
                position_y=2,
            )
        for field in self._fields:
            if self.range_max is not None and self.range_min is not None:
                field._cached_mesh = self.pv.add_mesh(
                    field._cached_polydata,
                    scalars=field.label,
                    log_scale=field.log_scale,
                    scalar_bar_args=sargs,
                    cmap=field.color_map,
                    clim=[self.range_min, self.range_max],
                    opacity=field.opacity,
                    show_edges=field.show_edge,
                )
            else:
                field._cached_mesh = self.pv.add_mesh(
                    field._cached_polydata,
                    scalars=field.label,
                    log_scale=field.log_scale,
                    scalar_bar_args=sargs,
                    cmap=field.color_map,
                    opacity=field.opacity,
                    show_edges=field.show_edge,
                )
        if self.show_legend:
            self._add_buttons()
        end = time.time() - start
        files_list = []
        if self.show_axes:
            self.pv.show_axes()
        if self.show_grid and not self.is_notebook:
            self.pv.show_grid(color=tuple(axes_color))
        if self.bounding_box:
            self.pv.add_bounding_box(color=tuple(axes_color))
        self.pv.set_focus(self.pv.mesh.center)

        if not self.isometric_view:
            self.pv.camera_position = self.camera_position
            self.pv.camera.azimuth += self.azimuth_angle
            self.pv.camera.roll += self.roll_angle
            self.pv.camera.elevation += self.elevation_angle
        else:
            self.pv.isometric_view()
        self.pv.camera.zoom(self.zoom)
        if export_image_path:
            self.pv.show(screenshot=export_image_path, full_screen=True)
        elif self.is_notebook:
            self.pv.show()
        else:
            self.pv.show(full_screen=True)
        self.image_file = export_image_path
        return True

    @aedt_exception_handler
    def clean_cache_and_files(self, remove_objs=True, remove_fields=True, clean_cache=False):
        """Clean downloaded files, and, on demand, also the cached meshes.

        Parameters
        ----------
        remove_objs : bool
        remove_fields : bool
        clean_cache : bool

        Returns
        -------
        bool
        """
        if remove_objs:
            for el in self.objects:
                if os.path.exists(el.path):
                    os.remove(el.path)
                if clean_cache:
                    el._cached_mesh = None
                    el._cached_polydata = None
        if remove_fields:
            for el in self.fields:
                if os.path.exists(el.path):
                    os.remove(el.path)
                if clean_cache:
                    el._cached_mesh = None
                    el._cached_polydata = None
        return True

    @aedt_exception_handler
    def animate(self):
        """Animate the current field plot.

        Returns
        -------
        bool
        """
        start = time.time()
        assert len(self.frames) > 0, "Number of Fields have to be greater than 1 to do an animation."
        if self.is_notebook:
            self.pv = pv.Plotter(notebook=self.is_notebook, off_screen=True, window_size=self.windows_size)
        else:
            self.pv = pv.Plotter(notebook=self.is_notebook, off_screen=self.off_screen, window_size=self.windows_size)

        self.pv.background_color = [i / 255 for i in self.background_color]
        self._read_mesh_files(read_frames=True)
        end = time.time() - start
        files_list = []
        axes_color = [0 if i >= 128 else 1 for i in self.background_color]

        if self.show_axes:
            self.pv.show_axes()
        if self.show_grid and not self.is_notebook:
            self.pv.show_grid(color=tuple(axes_color))
        if self.bounding_box:
            self.pv.add_bounding_box(color=tuple(axes_color))
        if self.show_legend:
            labels = []
            for m in self.objects:
                labels.append([m.name, [i / 255 for i in m.color]])
            for m in self.fields:
                labels.append([m.name, "red"])
            self.pv.add_legend(labels=labels, bcolor=None, face="circle", size=[0.15, 0.15])
        if not self.isometric_view:
            self.pv.camera_position = self.camera_position
            self.pv.camera.azimuth += self.azimuth_angle
            self.pv.camera.roll += self.roll_angle
            self.pv.camera.elevation += self.elevation_angle
        else:
            self.pv.isometric_view()
        self.pv.zoom = self.zoom
        self._animating = True

        if self.gif_file:
            self.pv.open_gif(self.gif_file)

        def q_callback():
            """exit when user wants to leave"""
            self._animating = False

        self._pause = False

        def p_callback():
            """exit when user wants to leave"""
            self._pause = not self._pause

        self.pv.add_text(
            "Press p for Play/Pause, Press q to exit ", font_size=8, position="upper_left", color=tuple(axes_color)
        )
        self.pv.add_text(" ", font_size=10, position=[0, 0], color=tuple(axes_color))
        self.pv.add_key_event("q", q_callback)
        self.pv.add_key_event("p", p_callback)
        if self.color_bar:
            sargs = dict(
                title_font_size=10,
                label_font_size=10,
                shadow=True,
                n_labels=9,
                italic=True,
                fmt="%.1f",
                font_family="arial",
            )
        else:
            sargs = dict(
                position_x=2,
                position_y=2,
            )

        for field in self._fields:
            field._cached_mesh = self.pv.add_mesh(
                field._cached_polydata,
                scalars=field.label,
                log_scale=field.log_scale,
                scalar_bar_args=sargs,
                cmap=field.color_map,
                opacity=field.opacity,
            )
        # run until q is pressed
        if self.pv.mesh:
            self.pv.set_focus(self.pv.mesh.center)

        cpos = self.pv.show(interactive=False, auto_close=False, interactive_update=not self.off_screen)

        if self.range_min is not None and self.range_max is not None:
            mins = self.range_min
            maxs = self.range_max
        else:
            mins = 1e20
            maxs = -1e20
            for el in self.frames:
                if np.min(el._cached_polydata.point_data[el.label]) < mins:
                    mins = np.min(el._cached_polydata.point_data[el.label])
                if np.max(el._cached_polydata.point_data[el.label]) > maxs:
                    maxs = np.max(el._cached_polydata.point_data[el.label])

        self.frames[0]._cached_mesh = self.pv.add_mesh(
            self.frames[0]._cached_polydata,
            scalars=self.frames[0].label,
            log_scale=self.frames[0].log_scale,
            scalar_bar_args=sargs,
            cmap=self.frames[0].color_map,
            clim=[mins, maxs],
            show_edges=False,
            pickable=True,
            smooth_shading=True,
            name="FieldPlot",
            opacity=self.frames[0].opacity,
        )
        start = time.time()

        self.pv.update(1, force_redraw=True)
        if self.gif_file:
            first_loop = True
            self.pv.write_frame()
        else:
            first_loop = False
        i = 1
        while self._animating:
            if self._pause:
                time.sleep(1)
                self.pv.update(1, force_redraw=True)
                continue
            # p.remove_actor("FieldPlot")
            if i >= len(self.frames):
                if self.off_screen or self.is_notebook:
                    break
                i = 0
                first_loop = False
            scalars = self.frames[i]._cached_polydata.point_data[self.frames[i].label]
            self.pv.update_scalars(scalars, render=False)
            if not hasattr(self.pv, "ren_win"):
                break
            time.sleep(max(0, (1 / self.frame_per_seconds) - (time.time() - start)))
            start = time.time()
            if self.off_screen:
                self.pv.render()
            else:
                self.pv.update(1, force_redraw=True)
            if first_loop:
                self.pv.write_frame()
            i += 1
        self.pv.close()
        if self.gif_file:
            return self.gif_file
        else:
            return True


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
        :class:`pyaedt.modules.AdvancedPostProcessing.ModelPlotter`
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

    @aedt_exception_handler
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
        :class:`pyaedt.modules.AdvancedPostProcessing.ModelPlotter`
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
            if meshplot:
                if self._app._aedt_version >= "2021.2":
                    models = self.export_model_obj(export_as_single_objects=True, air_objects=False)

        model = ModelPlotter()
        model.off_screen = not show

        if file_to_add:
            model.add_field_from_file(file_to_add, coordinate_units=self.modeler.model_units)
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

    @aedt_exception_handler
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
        :class:`pyaedt.modules.AdvancedPostProcessing.ModelPlotter`
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
        show=True,
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

        Returns
        -------
        :class:`pyaedt.modules.AdvancedPostProcessing.ModelPlotter`
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
        if show or export_gif:
            model.animate()
            model.clean_cache_and_files(clean_cache=False)

        return model

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
