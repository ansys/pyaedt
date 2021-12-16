"""
This module contains these classes: `CoordinateSystem`, `Modeler`,
`Position`, and `SweepOptions`.

This modules provides functionalities for the 3D Modeler, 2D Modeler,
3D Layout Modeler, and Circuit Modeler.
"""
from __future__ import absolute_import
import os

from collections import OrderedDict
from pyaedt.modeler.GeometryOperators import GeometryOperators
from pyaedt.generic.constants import AEDT_UNITS
from pyaedt.generic.general_methods import generate_unique_name, _retry_ntimes, aedt_exception_handler, _pythonver
import math
from pyaedt.generic.DataHandlers import _dict2arg
from pyaedt.modeler.Object3d import EdgePrimitive, FacePrimitive, VertexPrimitive, Object3d


class CoordinateSystem(object):
    """Manages coordinate system data and execution.

    Parameters
    ----------
    modeler :
        Inherited parent object.
    props : dict, optional
        Dictionary of properties. The default is ``None``.
    name : optional
        The default is ``None``.

    """

    def __init__(self, modeler, props=None, name=None):
        self._modeler = modeler
        self.model_units = self._modeler.model_units
        self.name = name
        self.props = props
        self.ref_cs = None
        self._quaternion = None
        self.mode = None
        try:
            if "KernelVersion" in self.props:
                del self.props["KernelVersion"]
        except:
            pass

    @aedt_exception_handler
    def _dim_arg(self, Value, sUnits=None):
        """Dimension argument.

        Parameters
        ----------
        Value :

        sUnits : optional
             The default is ``None``.

        Returns
        -------

        """
        if sUnits is None:
            sUnits = self.model_units
        if type(Value) is str:
            try:
                float(Value)
                val = "{0}{1}".format(Value, sUnits)
            except:
                val = Value
        else:
            val = "{0}{1}".format(Value, sUnits)
        return val

    @aedt_exception_handler
    def _change_property(self, name, arg):
        """Update properties of the coordinate system.

        Parameters
        ----------
        name : str
            Name of the coordinate system.
        arg : list
            List of the properties to update. For example,
            ``["NAME:ChangedProps", ["NAME:Mode", "Value:=", "Axis/Position"]]``.

        Returns
        -------
        list
            List of changed properties of the coordinate system.

        """
        arguments = ["NAME:AllTabs", ["NAME:Geometry3DCSTab", ["NAME:PropServers", name], arg]]
        _retry_ntimes(10, self._modeler.oeditor.ChangeProperty, arguments)

    @aedt_exception_handler
    def rename(self, newname):
        """Rename the coordinate system.

        Parameters
        ----------
        newname : str
            New name for the coordinate system.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        """
        self._change_property(self.name, ["NAME:ChangedProps", ["NAME:Name", "Value:=", newname]])
        self.name = newname
        return True

    @aedt_exception_handler
    def update(self):
        """Update the coordinate system.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        """
        self._change_property(self.name, ["NAME:ChangedProps", ["NAME:Reference CS", "Value:=", self.ref_cs]])

        try:
            self._change_property(self.name, ["NAME:ChangedProps", ["NAME:Mode", "Value:=", self.props["Mode"]]])
        except:
            raise ValueError(
                "Mode must be 'Axis/Position', 'Euler Angle ZYZ' or 'Euler Angle ZXZ', not {}.".format(
                    self.props["Mode"]
                )
            )

        props = ["NAME:ChangedProps"]

        props.append(
            [
                "NAME:Origin",
                "X:=",
                self._dim_arg(self.props["OriginX"]),
                "Y:=",
                self._dim_arg(self.props["OriginY"]),
                "Z:=",
                self._dim_arg(self.props["OriginZ"]),
            ]
        )

        if self.props["Mode"] == "Axis/Position":
            props.append(
                [
                    "NAME:X Axis",
                    "X:=",
                    self._dim_arg(self.props["XAxisXvec"]),
                    "Y:=",
                    self._dim_arg(self.props["XAxisYvec"]),
                    "Z:=",
                    self._dim_arg(self.props["XAxisZvec"]),
                ]
            )
            props.append(
                [
                    "NAME:Y Point",
                    "X:=",
                    self._dim_arg(self.props["YAxisXvec"]),
                    "Y:=",
                    self._dim_arg(self.props["YAxisYvec"]),
                    "Z:=",
                    self._dim_arg(self.props["YAxisZvec"]),
                ]
            )
        else:
            props.append(["NAME:Phi", "Value:=", self._dim_arg(self.props["Phi"], "deg")])

            props.append(["NAME:Theta", "Value:=", self._dim_arg(self.props["Theta"], "deg")])

            props.append(["NAME:Psi", "Value:=", self._dim_arg(self.props["Psi"], "deg")])

        self._change_property(self.name, props)
        return True

    @aedt_exception_handler
    def change_cs_mode(self, mode_type=0):
        """Change the mode of the coordinate system.

        Parameters
        ----------
        mode_type : int, optional
            Type of the mode. Options are:

            * ``0`` - Axis/Position
            * ``1`` - Euler Angle ZXZ
            * ``2`` - Euler Angle ZYZ

            The default is ``0``.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        """
        if mode_type == 0:  # "Axis/Position"
            if self.props and (self.props["Mode"] == "Euler Angle ZXZ" or self.props["Mode"] == "Euler Angle ZYZ"):
                self.props["Mode"] = "Axis/Position"
                x, y, z = GeometryOperators.quaternion_to_axis(self.quaternion)
                xaxis = x
                ypoint = y
                self.props["XAxisXvec"] = xaxis[0]
                self.props["XAxisYvec"] = xaxis[1]
                self.props["XAxisZvec"] = xaxis[2]
                self.props["YAxisXvec"] = ypoint[0]
                self.props["YAxisYvec"] = ypoint[1]
                self.props["YAxisZvec"] = ypoint[2]
                del self.props["Phi"]
                del self.props["Theta"]
                del self.props["Psi"]
                self.mode = "axis"
                self.update()
        elif mode_type == 1:  # "Euler Angle ZXZ"
            if self.props and self.props["Mode"] == "Euler Angle ZYZ":
                self.props["Mode"] = "Euler Angle ZXZ"
                a, b, g = GeometryOperators.quaternion_to_euler_zxz(self.quaternion)
                phi = GeometryOperators.rad2deg(a)
                theta = GeometryOperators.rad2deg(b)
                psi = GeometryOperators.rad2deg(g)
                self.props["Phi"] = "{}deg".format(phi)
                self.props["Theta"] = "{}deg".format(theta)
                self.props["Psi"] = "{}deg".format(psi)
                self.mode = "zxz"
                self.update()
            elif self.props and self.props["Mode"] == "Axis/Position":
                self.props["Mode"] = "Euler Angle ZXZ"
                a, b, g = GeometryOperators.quaternion_to_euler_zxz(self.quaternion)
                phi = GeometryOperators.rad2deg(a)
                theta = GeometryOperators.rad2deg(b)
                psi = GeometryOperators.rad2deg(g)
                self.props["Phi"] = "{}deg".format(phi)
                self.props["Theta"] = "{}deg".format(theta)
                self.props["Psi"] = "{}deg".format(psi)
                del self.props["XAxisXvec"]
                del self.props["XAxisYvec"]
                del self.props["XAxisZvec"]
                del self.props["YAxisXvec"]
                del self.props["YAxisYvec"]
                del self.props["YAxisZvec"]
                self.mode = "zxz"
                self.update()
        elif mode_type == 2:  # "Euler Angle ZYZ"
            if self.props and self.props["Mode"] == "Euler Angle ZXZ":
                self.props["Mode"] = "Euler Angle ZYZ"
                a, b, g = GeometryOperators.quaternion_to_euler_zyz(self.quaternion)
                phi = GeometryOperators.rad2deg(a)
                theta = GeometryOperators.rad2deg(b)
                psi = GeometryOperators.rad2deg(g)
                self.props["Phi"] = "{}deg".format(phi)
                self.props["Theta"] = "{}deg".format(theta)
                self.props["Psi"] = "{}deg".format(psi)
                self.mode = "zyz"
                self.update()
            elif self.props and self.props["Mode"] == "Axis/Position":
                self.props["Mode"] = "Euler Angle ZYZ"
                a, b, g = GeometryOperators.quaternion_to_euler_zyz(self.quaternion)
                phi = GeometryOperators.rad2deg(a)
                theta = GeometryOperators.rad2deg(b)
                psi = GeometryOperators.rad2deg(g)
                self.props["Phi"] = "{}deg".format(phi)
                self.props["Theta"] = "{}deg".format(theta)
                self.props["Psi"] = "{}deg".format(psi)
                del self.props["XAxisXvec"]
                del self.props["XAxisYvec"]
                del self.props["XAxisZvec"]
                del self.props["YAxisXvec"]
                del self.props["YAxisYvec"]
                del self.props["YAxisZvec"]
                self.mode = "zyz"
                self.update()
        else:
            raise ValueError('mode_type=0 for "Axis/Position", =1 for "Euler Angle ZXZ", =2 for "Euler Angle ZYZ"')
        return True

    @aedt_exception_handler
    def create(
        self,
        origin=None,
        reference_cs="Global",
        name=None,
        mode="axis",
        view="iso",
        x_pointing=None,
        y_pointing=None,
        phi=0,
        theta=0,
        psi=0,
        u=None,
    ):
        """Create a coordinate system.

        Parameters
        ----------
        origin : list
            List of ``[x, y, z]`` coordinates for the origin of the coordinate system.
            The default is ``None``, in which case ``[0, 0, 0]`` is used.
        reference_cs : str, optional
            Name of the reference coordinate system. The default is ``"Global"``.
        name : str
            Name of the coordinate system. The default is ``None``.
        mode : str, optional
            Definition mode. Options are ``"view"``, ``"axis"``, ``"zxz"``, ``"zyz"``,
            and ``"axisrotation"``. The default is ``"axis"``.

            * If ``mode="view"``, specify ``view``.
            * If ``mode="axis"``, specify ``x_pointing`` and ``y_pointing``.
            * If ``mode="zxz"`` or ``mode="zyz"``, specify ``phi``, ``theta``, and ``psi``.
            * If ``mode="axisrotation"``, specify ``theta`` and ``u``.

            Parameters not needed by the specified mode are ignored.
            For back compatibility, ``view="rotate"`` is the same as ``mode="axis"``.
            The mode ``"axisrotation"`` is a coordinate system parallel
            to the global coordinate system centered in the global origin.

        view : str, optional
            View for the coordinate system if ``mode="view"``. Options are
            ``"XY"``, ``"XZ"``, ``"XY"``, ``"iso"``, ``None``, and ``"rotate"``
            (obsolete). The default is ``"iso"``.

            .. note::
               Because the ``"rotate"`` option is obsolete, use ``mode="axis"`` instead.

        x_pointing : list, optional
            List of the ``[x, y, z]`` coordinates specifying the X axis
            pointing in the local coordinate system if ``mode="axis"``.
            The default is ``[1, 0, 0]``.
        y_pointing : list, optional
            List of the ``[x, y, z]`` coordinates specifying the Y axis
            pointing in the local coordinate system if ``mode="axis"``.
            The default is ``[0, 1, 0]``.
        phi : float, optional
            Euler angle phi in degrees if ``mode="zxz"`` or ``mode="zyz"``.
            The default is ``0``.
        theta : float, optional
            Euler angle theta or rotation angle in degrees if ``mode="zxz"``,
            ``mode="zyz"``, or ``mode="axisrotation"``. The default is ``0``.
        psi : float, optional
            Euler angle psi in degrees if ``mode="zxz"`` or ``mode="zyz"``.
            The default is ``0``.
        u : list
            List of the ``[ux, uy, uz]`` coordinates for the rotation axis
            if ``mode="zxz"``. The default is ``[1, 0, 0]``.

        Returns
        -------
        :class:`pyaedt.modeler.Modeler.CoordinateSystem`

        """
        if not origin:
            origin = [0, 0, 0]
        if not x_pointing:
            x_pointing = [1, 0, 0]
        if not y_pointing:
            y_pointing = [0, 1, 0]
        if not u:
            u = [1, 0, 0]
        if view == "rotate":
            # legacy compatibility
            mode = "axis"

        if name:
            self.name = name
        else:
            self.name = generate_unique_name("CS")

        originX = self._dim_arg(origin[0], self.model_units)
        originY = self._dim_arg(origin[1], self.model_units)
        originZ = self._dim_arg(origin[2], self.model_units)
        orientationParameters = OrderedDict({"OriginX": originX, "OriginY": originY, "OriginZ": originZ})
        self.mode = mode
        if mode == "view":
            orientationParameters["Mode"] = "Axis/Position"
            if view == "YZ":
                orientationParameters["XAxisXvec"] = "0mm"
                orientationParameters["XAxisYvec"] = "0mm"
                orientationParameters["XAxisZvec"] = "-1mm"
                orientationParameters["YAxisXvec"] = "0mm"
                orientationParameters["YAxisYvec"] = "1mm"
                orientationParameters["YAxisZvec"] = "0mm"
            elif view == "XZ":
                orientationParameters["XAxisXvec"] = "1mm"
                orientationParameters["XAxisYvec"] = "0mm"
                orientationParameters["XAxisZvec"] = "0mm"
                orientationParameters["YAxisXvec"] = "0mm"
                orientationParameters["YAxisYvec"] = "-1mm"
                orientationParameters["YAxisZvec"] = "0mm"
            elif view == "XY":
                orientationParameters["XAxisXvec"] = "1mm"
                orientationParameters["XAxisYvec"] = "0mm"
                orientationParameters["XAxisZvec"] = "0mm"
                orientationParameters["YAxisXvec"] = "0mm"
                orientationParameters["YAxisYvec"] = "1mm"
                orientationParameters["YAxisZvec"] = "0mm"
            elif view == "iso":
                orientationParameters["XAxisXvec"] = "1mm"
                orientationParameters["XAxisYvec"] = "1mm"
                orientationParameters["XAxisZvec"] = "-2mm"
                orientationParameters["YAxisXvec"] = "-1mm"
                orientationParameters["YAxisYvec"] = "1mm"
                orientationParameters["YAxisZvec"] = "0mm"
            else:
                raise ValueError("With mode = 'view', specify view = 'XY', 'XZ', 'XY', 'iso' ")

        elif mode == "axis":
            orientationParameters["Mode"] = "Axis/Position"
            orientationParameters["XAxisXvec"] = self._dim_arg((x_pointing[0]), self.model_units)
            orientationParameters["XAxisYvec"] = self._dim_arg((x_pointing[1]), self.model_units)
            orientationParameters["XAxisZvec"] = self._dim_arg((x_pointing[2]), self.model_units)
            orientationParameters["YAxisXvec"] = self._dim_arg((y_pointing[0]), self.model_units)
            orientationParameters["YAxisYvec"] = self._dim_arg((y_pointing[1]), self.model_units)
            orientationParameters["YAxisZvec"] = self._dim_arg((y_pointing[2]), self.model_units)

        elif mode == "zxz":
            orientationParameters["Mode"] = "Euler Angle ZXZ"
            orientationParameters["Phi"] = self._dim_arg(phi, "deg")
            orientationParameters["Theta"] = self._dim_arg(theta, "deg")
            orientationParameters["Psi"] = self._dim_arg(psi, "deg")

        elif mode == "zyz":
            orientationParameters["Mode"] = "Euler Angle ZYZ"
            orientationParameters["Phi"] = self._dim_arg(phi, "deg")
            orientationParameters["Theta"] = self._dim_arg(theta, "deg")
            orientationParameters["Psi"] = self._dim_arg(psi, "deg")

        elif mode == "axisrotation":
            th = GeometryOperators.deg2rad(theta)
            q = GeometryOperators.axis_angle_to_quaternion(u, th)
            a, b, c = GeometryOperators.quaternion_to_euler_zyz(q)
            phi = GeometryOperators.rad2deg(a)
            theta = GeometryOperators.rad2deg(b)
            psi = GeometryOperators.rad2deg(c)
            orientationParameters["Mode"] = "Euler Angle ZYZ"
            orientationParameters["Phi"] = self._dim_arg(phi, "deg")
            orientationParameters["Theta"] = self._dim_arg(theta, "deg")
            orientationParameters["Psi"] = self._dim_arg(psi, "deg")
        else:
            raise ValueError("Specify the mode = 'view', 'axis', 'zxz', 'zyz', 'axisrotation' ")

        self.props = orientationParameters
        self._modeler.oeditor.CreateRelativeCS(self.orientation, self.attributes)
        self.ref_cs = reference_cs
        self.update()

        return True

    @property
    def quaternion(self):
        """Quaternion computed based on specific axis mode.

        Returns
        -------
        list
        """
        self._modeler._app.variable_manager["temp_var"] = 0
        if self.mode == "axis" or self.mode == "view":
            x1 = self.props["XAxisXvec"]
            x2 = self.props["XAxisYvec"]
            x3 = self.props["XAxisZvec"]
            y1 = self.props["YAxisXvec"]
            y2 = self.props["YAxisYvec"]
            y3 = self.props["YAxisZvec"]
            self._modeler._app.variable_manager["temp_var"] = x1
            x_pointing_num = [self._modeler._app.variable_manager["temp_var"].numeric_value]
            self._modeler._app.variable_manager["temp_var"] = x2
            x_pointing_num.append(self._modeler._app.variable_manager["temp_var"].numeric_value)
            self._modeler._app.variable_manager["temp_var"] = x3
            x_pointing_num.append(self._modeler._app.variable_manager["temp_var"].numeric_value)
            self._modeler._app.variable_manager["temp_var"] = y1
            y_pointing_num = [self._modeler._app.variable_manager["temp_var"].numeric_value]
            self._modeler._app.variable_manager["temp_var"] = y2
            y_pointing_num.append(self._modeler._app.variable_manager["temp_var"].numeric_value)
            self._modeler._app.variable_manager["temp_var"] = y3
            y_pointing_num.append(self._modeler._app.variable_manager["temp_var"].numeric_value)
            x, y, z = GeometryOperators.pointing_to_axis(x_pointing_num, y_pointing_num)
            a, b, g = GeometryOperators.axis_to_euler_zyz(x, y, z)
            self._quaternion = GeometryOperators.euler_zyz_to_quaternion(a, b, g)
            del self._modeler._app.variable_manager["temp_var"]
        elif self.mode == "zxz":
            self._modeler._app.variable_manager["temp_var"] = self.props["Phi"]
            a = GeometryOperators.deg2rad(self._modeler._app.variable_manager["temp_var"].numeric_value)
            self._modeler._app.variable_manager["temp_var"] = self.props["Theta"]
            b = GeometryOperators.deg2rad(self._modeler._app.variable_manager["temp_var"].numeric_value)
            self._modeler._app.variable_manager["temp_var"] = self.props["Psi"]
            g = GeometryOperators.deg2rad(self._modeler._app.variable_manager["temp_var"].numeric_value)
            self._quaternion = GeometryOperators.euler_zxz_to_quaternion(a, b, g)
            del self._modeler._app.variable_manager["temp_var"]
        elif self.mode == "zyz" or self.mode == "axisrotation":
            self._modeler._app.variable_manager["temp_var"] = self.props["Phi"]
            a = GeometryOperators.deg2rad(self._modeler._app.variable_manager["temp_var"].numeric_value)
            self._modeler._app.variable_manager["temp_var"] = self.props["Theta"]
            b = GeometryOperators.deg2rad(self._modeler._app.variable_manager["temp_var"].numeric_value)
            self._modeler._app.variable_manager["temp_var"] = self.props["Psi"]
            g = GeometryOperators.deg2rad(self._modeler._app.variable_manager["temp_var"].numeric_value)
            self._quaternion = GeometryOperators.euler_zyz_to_quaternion(a, b, g)
            del self._modeler._app.variable_manager["temp_var"]
        return self._quaternion

    @property
    def orientation(self):
        """Internal named array for orientation of the coordinate system."""
        arg = ["Name:RelativeCSParameters"]
        _dict2arg(self.props, arg)
        return arg

    @property
    def attributes(self):
        """Internal named array for attributes of the coordinate system."""
        coordinateSystemAttributes = ["NAME:Attributes", "Name:=", self.name]
        return coordinateSystemAttributes

    @aedt_exception_handler
    def delete(self):
        """Delete the coordinate system.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        """
        self._modeler.oeditor.Delete(["NAME:Selections", "Selections:=", self.name])
        self._modeler.coordinate_systems.remove(self)
        return True

    @aedt_exception_handler
    def set_as_working_cs(self):
        """Set the coordinate system as the working coordinate system.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        """
        self._modeler.oeditor.SetWCS(
            ["NAME:SetWCS Parameter", "Working Coordinate System:=", self.name, "RegionDepCSOk:=", False]
        )
        return True


class Modeler(object):
    """Provides the `Modeler` application class that other `Modeler` classes inherit.

    This class is inherited in the caller application and is accessible through the modeler variable
    object( eg. ``hfss.modeler``).

    Parameters
    ----------
    app :
        Inherited parent object.

    Examples
    --------
    >>> from pyaedt import Maxwell2d
    >>> app = Maxwell2d()
    >>> my_modeler = app.modeler
    """

    def __init__(self, app):
        self._app = app

    # Properties derived from internal parent data
    @property
    def _desktop(self):
        """Desktop."""
        return self._app._desktop

    @property
    def logger(self):
        """Logger."""
        return self._app.logger

    @property
    def _odesign(self):
        """Design."""
        return self._app._odesign

    @property
    def _oimportexport(self):
        """Import/Export."""
        return self._app.oimport_export

    @property
    def projdir(self):
        """Project directory."""
        return self._app.project_path


class GeometryModeler(Modeler, object):
    """Manages the main AEDT Modeler functionalities for geometry-based designs.

    Parameters
    ----------
    app :
        Inherited parent object.
    is3d : bool, optional
        Whether the model is 3D. The default is ``True``.
    """

    def __init__(self, app, is3d=True):
        self._app = app
        self._oeditor = self._odesign.SetActiveEditor("3D Modeler")
        self._odefinition_manager = self._app.odefinition_manager
        self._omaterial_manager = self._app._oproject.GetDefinitionManager().GetManager("Material")
        Modeler.__init__(self, app)
        # TODO Refactor this as a dictionary with names as key
        self.coordinate_systems = self._get_coordinates_data()
        self._is3d = is3d

    @property
    def oeditor(self):
        """Aedt oEditor Module.

        References
        ----------

        >>> oEditor = oDesign.SetActiveEditor("3D Modeler")"""

        return self._oeditor

    @property
    def materials(self):
        """Material library used in the project.

        Returns
        -------
        :class:`pyaedt.modules.MaterialLib.Materials`

        """
        return self._app.materials

    @aedt_exception_handler
    def _convert_list_to_ids(self, input_list, convert_objects_ids_to_name=True):
        """Convert a list to IDs.

        Parameters
        ----------
        input_list : list
           List of object IDs.
        convert_objects_ids_to_name : bool, optional
             Whether to convert the object IDs to object names.
             The default is ``True``.

        Returns
        -------
        list
            List of object names.

        """
        output_list = []
        if type(input_list) is not list:
            input_list = [input_list]
        for el in input_list:
            if type(el) is Object3d:
                output_list = [i.name for i in input_list]
            elif type(el) is EdgePrimitive or type(el) is FacePrimitive or type(el) is VertexPrimitive:
                output_list = [i.id for i in input_list]
            elif type(el) is int and convert_objects_ids_to_name:
                if el in list(self.primitives.objects.keys()):
                    output_list.append(self.primitives.objects[el].name)
                else:
                    output_list.append(el)
            else:
                output_list.append(el)
        return output_list

    def _get_coordinates_data(self):
        coord = []
        id2name = {1: "Global"}
        name2refid = {}
        if self._app.design_properties and "ModelSetup" in self._app.design_properties:
            cs = self._app.design_properties["ModelSetup"]["GeometryCore"]["GeometryOperations"]["CoordinateSystems"]
            for ds in cs:
                try:
                    if isinstance(cs[ds], (OrderedDict, dict)):
                        props = cs[ds]["RelativeCSParameters"]
                        name = cs[ds]["Attributes"]["Name"]
                        cs_id = cs[ds]["ID"]
                        id2name[cs_id] = name
                        name2refid[name] = cs[ds]["ReferenceCoordSystemID"]
                        coord.append(CoordinateSystem(self, props, name))
                    elif type(cs[ds]) is list:
                        for el in cs[ds]:
                            props = el["RelativeCSParameters"]
                            name = el["Attributes"]["Name"]
                            cs_id = el["ID"]
                            id2name[cs_id] = name
                            name2refid[name] = el["ReferenceCoordSystemID"]
                            coord.append(CoordinateSystem(self, props, name))
                except:
                    pass
            for cs in coord:
                try:
                    cs.ref_cs = id2name[name2refid[cs.name]]
                    if cs.props["Mode"] == "Axis/Position":
                        x1 = GeometryOperators.parse_dim_arg(
                            cs.props["XAxisXvec"], variable_manager=self._app.variable_manager
                        )
                        x2 = GeometryOperators.parse_dim_arg(
                            cs.props["XAxisYvec"], variable_manager=self._app.variable_manager
                        )
                        x3 = GeometryOperators.parse_dim_arg(
                            cs.props["XAxisZvec"], variable_manager=self._app.variable_manager
                        )
                        y1 = GeometryOperators.parse_dim_arg(
                            cs.props["YAxisXvec"], variable_manager=self._app.variable_manager
                        )
                        y2 = GeometryOperators.parse_dim_arg(
                            cs.props["YAxisYvec"], variable_manager=self._app.variable_manager
                        )
                        y3 = GeometryOperators.parse_dim_arg(
                            cs.props["YAxisZvec"], variable_manager=self._app.variable_manager
                        )
                        x, y, z = GeometryOperators.pointing_to_axis([x1, x2, x3], [y1, y2, y3])
                        a, b, g = GeometryOperators.axis_to_euler_zyz(x, y, z)
                        cs.quaternion = GeometryOperators.euler_zyz_to_quaternion(a, b, g)
                    elif cs.props["Mode"] == "Euler Angle ZXZ":
                        a = GeometryOperators.parse_dim_arg(
                            cs.props["Phi"], variable_manager=self._app.variable_manager
                        )
                        b = GeometryOperators.parse_dim_arg(
                            cs.props["Theta"], variable_manager=self._app.variable_manager
                        )
                        g = GeometryOperators.parse_dim_arg(
                            cs.props["Psi"], variable_manager=self._app.variable_manager
                        )
                        cs.quaternion = GeometryOperators.euler_zxz_to_quaternion(a, b, g)
                    elif cs.props["Mode"] == "Euler Angle ZYZ":
                        a = GeometryOperators.parse_dim_arg(
                            cs.props["Phi"], variable_manager=self._app.variable_manager
                        )
                        b = GeometryOperators.parse_dim_arg(
                            cs.props["Theta"], variable_manager=self._app.variable_manager
                        )
                        g = GeometryOperators.parse_dim_arg(
                            cs.props["Psi"], variable_manager=self._app.variable_manager
                        )
                        cs.quaternion = GeometryOperators.euler_zyz_to_quaternion(a, b, g)
                except:
                    pass
        return coord

    def __get__(self, instance, owner):
        self._app = instance
        return self

    @property
    def model_units(self):
        """Model units as a string. For example ``"mm"``.

        References
        ----------

        >>> oEditor.GetModelUnits
        >>> oEditor.SetModelUnits
        """
        return _retry_ntimes(10, self.oeditor.GetModelUnits)

    @model_units.setter
    def model_units(self, units):
        assert units in AEDT_UNITS["Length"], "Invalid units string {0}.".format(units)
        self.oeditor.SetModelUnits(["NAME:Units Parameter", "Units:=", units, "Rescale:=", False])

    @property
    def selections(self):
        """Selections.

        References
        ----------

        >>> oEditor.GetSelections
        """
        return self.oeditor.GetSelections()

    @property
    def obounding_box(self):
        """Bounding box.

        References
        ----------

        >>> oEditor.GetModelBoundingBox
        """
        return self.oeditor.GetModelBoundingBox()

    @aedt_exception_handler
    def fit_all(self):
        """Fit all.

        References
        ----------

        >>> oEditor.FitAll
        """
        self.oeditor.FitAll()

    @property
    def dimension(self):
        """Dimensions.

        Returns
        -------
        str
            Dimensionality, which is either ``"2D"`` or ``"3D"``.

        References
        ----------

        >>> oDesign.Is2D
        """
        try:
            if self._odesign.Is2D():
                return "2D"
            else:
                return "3D"
        except Exception:
            if self.design_type == "2D Extractor":
                return "2D"
            else:
                return "3D"

    @property
    def design_type(self):
        """Design type.

        References
        ----------

        >>> oDesign.GetDesignType
        """
        return self._odesign.GetDesignType()

    @property
    def geometry_mode(self):
        """Geometry mode.

        References
        ----------

        >>> oDesign.GetGeometryMode"""
        return self._odesign.GetGeometryMode()

    @property
    def solid_bodies(self):
        """List of Object Names.

        .. note::
            Non-model objects are also returned.

        Returns
        -------
        list os str
            List of object names with the object name as the key.

        References
        ----------

        >>> oEditor.GetObjectsInGroup
        """
        if self.dimension == "3D":
            objects = self.oeditor.GetObjectsInGroup("Solids")
        else:
            objects = self.oeditor.GetObjectsInGroup("Sheets")
        return list(objects)

    @aedt_exception_handler
    def _find_perpendicular_points(self, face):

        if isinstance(face, str):
            vertices = [i.position for i in self.primitives[face].vertices]
        else:
            vertices = []
            for vertex in list(self.oeditor.GetVertexIDsFromFace(face)):
                vertices.append([float(i) for i in list(self.oeditor.GetVertexPosition(vertex))])
        assert len(vertices) > 2, "Automatic A-B Assignment can be done only on face with more than 2 vertices."
        origin = vertices[0]
        a_end = []
        b_end = []
        tol = 1e-10
        for v in vertices[1:]:
            edge1 = GeometryOperators.v_points(origin, v)
            for v2 in vertices[1:]:
                if v2 != v:
                    edge2 = GeometryOperators.v_points(origin, v2)
                    if abs(GeometryOperators.v_dot(edge1, edge2)) < tol:
                        a_end = v
                        b_end = v2
                        break
            if a_end:
                break
        if not a_end:
            a_end = vertices[1]
            b_end = vertices[2]
            return False, (origin, a_end, b_end)
        return True, (origin, a_end, b_end)

    @aedt_exception_handler
    def cover_lines(self, selection):
        """Cover a closed line and transform it to sheet.

        Parameters
        ----------
        selection : str, int
            Polyline object to cover.
        Returns
        -------
        bool

        References
        ----------

        >>> oEditor.CoverLines
        """
        obj_to_cover = self.convert_to_selections(selection, False)
        self.oeditor.CoverLines(["NAME:Selections", "Selections:=", obj_to_cover, "NewPartsModelFlag:=", "Model"])
        return True

    @aedt_exception_handler
    def create_coordinate_system(
        self,
        origin=None,
        reference_cs="Global",
        name=None,
        mode="axis",
        view="iso",
        x_pointing=None,
        y_pointing=None,
        psi=0,
        theta=0,
        phi=0,
        u=None,
    ):
        """Create a coordinate system.

        Parameters
        ----------
        origin : list
            List of ``[x, y, z]`` coordinates for the origin of the
            coordinate system.  The default is ``None``, in which case
            ``[0, 0, 0]`` is used.
        reference_cs : str, optional
            Name of the reference coordinate system. The default is
            ``"Global"``.
        name : str
            Name of the coordinate system. The default is ``None``.
        mode : str, optional
            Definition mode. Options are ``"view"``, ``"axis"``,
            ``"zxz"``, ``"zyz"``, and ``"axisrotation"``. The default
            is ``"axis"``.  Enumerator ``pyaedt.generic.constants.CSMODE`` can be used.

            * If ``mode="view"``, specify ``view``.
            * If ``mode="axis"``, specify ``x_pointing`` and ``y_pointing``.
            * If ``mode="zxz"`` or ``mode="zyz"``, specify ``phi``, ``theta``, and ``psi``.
            * If ``mode="axisrotation"``, specify ``theta`` and ``u``.

            Parameters not needed by the specified mode are ignored.
            For back compatibility, ``view="rotate"`` is the same as
            ``mode="axis"``.  The default mode, ``"axisrotation"``, is
            a coordinate system parallel to the global coordinate
            system centered in the global origin.

        view : str, int optional
            View for the coordinate system if ``mode="view"``. Options
            are ``"XY"``, ``"XZ"``, ``"XY"``, ``"iso"``, ``None``, and
            ``"rotate"`` (obsolete). The default is ``"iso"``.
            Enumerator ``pyaedt.generic.constants.VIEW`` can be used.

            .. note::
               Because the ``"rotate"`` option is obsolete, use
               ``mode="axis"`` instead.

        x_pointing : list, optional
            List of the ``[x, y, z]`` coordinates specifying the X axis
            pointing in the global coordinate system if ``mode="axis"``.
            The default is ``[1, 0, 0]``.
        y_pointing : list, optional
            List of the ``[x, y, z]`` coordinates specifying the Y axis
            pointing in the global coordinate system if ``mode="axis"``.
            The default is ``[0, 1, 0]``.
        phi : float, optional
            Euler angle phi in degrees if ``mode="zxz"`` or ``mode="zyz"``.
            The default is ``0``.
        theta : float, optional
            Euler angle theta or rotation angle in degrees if ``mode="zxz"``,
            ``mode="zyz"``, or ``mode="axisrotation"``. The default is ``0``.
        psi : float, optional
            Euler angle psi in degrees if ``mode="zxz"`` or ``mode="zyz"``.
            The default is ``0``.
        u : list
            List of the ``[ux, uy, uz]`` coordinates for the rotation axis
            if ``mode="zxz"``. The default is ``[1, 0, 0]``.

        Returns
        -------
        :class:`pyaedt.modeler.Modeler.CoordinateSystem`
            Coordinate System Object.

        References
        ----------

        >>> oEditor.CreateRelativeCS
        """
        if name:
            cs_names = [i.name for i in self.coordinate_systems]
            if name in cs_names:
                raise AttributeError("A coordinate system with the specified name already exists!")

        cs = CoordinateSystem(self)
        if cs:
            result = cs.create(
                origin=origin,
                reference_cs=reference_cs,
                name=name,
                mode=mode,
                view=view,
                x_pointing=x_pointing,
                y_pointing=y_pointing,
                phi=phi,
                theta=theta,
                psi=psi,
                u=u,
            )
            if result:
                self.coordinate_systems.append(cs)
                return cs
        return False

    @aedt_exception_handler
    def global_to_cs(self, point, ref_cs):
        """Transform a point from the global coordinate system to another coordinate system.

        Parameters
        ----------
        point : list
            List of the ``[x, y, z]`` coordinates to transform.
        ref_cs : str
            Name of the destination reference system.

        Returns
        -------
        list
            List of the transformed ``[x, y, z]`` coordinates.

        """
        if type(point) is not list or len(point) != 3:
            raise AttributeError("Point must be in format [x, y, z].")
        try:
            point = [float(i) for i in point]
        except:
            raise AttributeError("Point must be in format [x, y, z].")
        if ref_cs == "Global":
            return point
        cs_names = [i.name for i in self.coordinate_systems]
        if ref_cs not in cs_names:
            raise AttributeError("Specified coordinate system does not exist in the design.")

        def get_total_transformation(p, cs):
            idx = cs_names.index(cs)
            q = self.coordinate_systems[idx].quaternion
            ox = GeometryOperators.parse_dim_arg(
                self.coordinate_systems[idx].props["OriginX"],
                self.model_units,
                variable_manager=self._app.variable_manager,
            )
            oy = GeometryOperators.parse_dim_arg(
                self.coordinate_systems[idx].props["OriginY"],
                self.model_units,
                variable_manager=self._app.variable_manager,
            )
            oz = GeometryOperators.parse_dim_arg(
                self.coordinate_systems[idx].props["OriginZ"],
                self.model_units,
                variable_manager=self._app.variable_manager,
            )
            o = [ox, oy, oz]
            refcs = self.coordinate_systems[idx].ref_cs
            if refcs == "Global":
                p1 = p
            else:
                p1 = get_total_transformation(p, refcs)
            p2 = GeometryOperators.q_rotation_inv(GeometryOperators.v_sub(p1, o), q)
            return p2

        return get_total_transformation(point, ref_cs)

    @aedt_exception_handler
    def set_working_coordinate_system(self, name):
        """Set the working coordinate system to another coordinate system.

        Parameters
        ----------
        name : str
            Name of the coordinate system to set as the working coordinate system.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        References
        ----------

        >>> oEditor.SetWCS
        """
        self.oeditor.SetWCS(["NAME:SetWCS Parameter", "Working Coordinate System:=", name, "RegionDepCSOk:=", False])
        return True

    @aedt_exception_handler
    def set_objects_deformation(self, objects):
        """Assign deformation objects to a Workbench link.

        Parameters
        ----------
        objects : list
            List of the deformation objects to assign to the Workbench link.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        References
        ----------

        >>> oDesign.SetObjectDeformation
        """
        self.logger.info("Enabling deformation feedback")
        try:
            self._odesign.SetObjectDeformation(["EnabledObjects:=", objects])
        except:
            self.logger.error("Failed to enable the deformation dependence")
            return False
        else:
            self.logger.info("Successfully enabled deformation feedback")
            return True

    @aedt_exception_handler
    def set_objects_temperature(self, objects, ambient_temp=22, create_project_var=False):
        """Assign temperatures to objects.

        The materials assigned to the objects must have a thermal modifier.

        Parameters
        ----------
        objects : list
            List of objects.
        ambient_temp : float, optional
            Ambient temperature. The default is ``22``.
        create_project_var : bool, optional
            Whether to create a project variable for the ambient temperature.
            The default is ``False``. If ``True,`` ``$AmbientTemp`` is created.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        References
        ----------

        >>> oDesign.SetObjectTemperature
        """
        self.logger.info("Set model temperature and enabling Thermal Feedback")
        if create_project_var:
            self._app.variable_manager["$AmbientTemp"] = str(ambient_temp) + "cel"
            var = "$AmbientTemp"
        else:
            var = str(ambient_temp) + "cel"
        vargs1 = [
            "NAME:TemperatureSettings",
            "IncludeTemperatureDependence:=",
            True,
            "EnableFeedback:=",
            True,
            "Temperatures:=",
        ]
        vargs2 = []
        for obj in objects:
            mat = self.primitives[obj].material_name
            th = self._app.materials.check_thermal_modifier(mat)
            if th:
                vargs2.append(obj)
                vargs2.append(var)
        if not vargs2:
            return False
        else:
            vargs1.append(vargs2)
        try:
            self._odesign.SetObjectTemperature(vargs1)
        except:
            self.logger.error("Failed to enable the temperature dependence")
            return False
        else:
            self.logger.info("Assigned Objects Temperature")
            return True

    @aedt_exception_handler
    def _create_sheet_from_object_closest_edge(self, startobj, endobject, axisdir, portonplane):
        """Create a sheet from the edge closest to the object.

        Parameters
        ----------
        startobj : str
            Name of the starting object.
        endobject : str
            Name of the ending object.
        axisdir : int
           Axis direction. Options are ``0`` through ``5``.
        portonplane : bool
            Whether edges are to be on the plane orthogonal to the axis
            direction.

        Returns
        -------
        str
            Name of the sheet.
        list
            List of the points.

        """
        out, parallel = self.primitives.find_closest_edges(startobj, endobject, axisdir)
        port_edges = self.primitives.get_equivalent_parallel_edges(out, portonplane, axisdir, startobj, endobject)
        if port_edges is None or port_edges is False:
            port_edges = []
            for e in out:
                edge = self.primitives.create_object_from_edge(e)
                port_edges.append(edge)
        edge_0 = port_edges[0].edges[0]
        edge_1 = port_edges[1].edges[0]
        sheet_name = port_edges[0].name
        point0 = edge_0.midpoint
        point1 = edge_1.midpoint
        self.connect(port_edges)
        return sheet_name, point0, point1

    @aedt_exception_handler
    def find_point_around(self, objectname, startposition, offset, plane):
        """Find the point around an object.

        Parameters
        ----------
        objectname : str
            Name of the object.
        startposition : list
            List of the ``[x, y, z]`` coordinates for the starting
            position of the object.
        offset :
            Offset to apply.
        plane : str
            Coordinate plane of the arc. Choices are ``"YZ"``,
            ``"ZX"``, and ``"XY"``.


        Returns
        -------
        list
            List of the ``[x, y, z]`` coordinates for the point.

        """
        position = [0, 0, 0]
        angle = 0
        if plane == 0:
            while angle <= 360:
                position[0] = startposition[0] + offset * math.cos(math.pi * angle / 180)
                position[1] = startposition[1] + offset * math.sin(math.pi * angle / 180)
                if objectname in self.primitives.get_bodynames_from_position(startposition):
                    angle = 400
                else:
                    angle += 90
        elif plane == 1:
            while angle <= 360:
                position[1] = startposition[1] + offset * math.cos(math.pi * angle / 180)
                position[2] = startposition[2] + offset * math.sin(math.pi * angle / 180)
                if objectname in self.primitives.get_bodynames_from_position(startposition):
                    angle = 400
                else:
                    angle += 90
        elif plane == 2:
            while angle <= 360:
                position[0] = startposition[0] + offset * math.cos(math.pi * angle / 180)
                position[2] = startposition[2] + offset * math.sin(math.pi * angle / 180)
                if objectname in self.primitives.get_bodynames_from_position(startposition):
                    angle = 400
                else:
                    angle += 90
        return position

    @aedt_exception_handler
    def create_sheet_to_ground(self, objectname, groundname=None, axisdir=0, sheet_dim=1):
        """Create a sheet between an object and a ground plane.

        The ground plane must be bigger than the object and perpendicular
        to one of the three axes.

        Parameters
        ----------
        objectname : str
            Name of the object.
        groundname : str, optional
            Name of the ground. The default is ``None``, in which case the
            bounding box is used.
        axisdir : int, optional
            Axis direction. Options are ``0`` through ``5``. The default is ``0``.
        sheet_dim : optional
            Sheet dimension in millimeters. The default is ``1``.

        Returns
        -------
        int
            ID of the sheet created.

        References
        ----------

        >>> oEditor.CreatePolyline
        """
        if axisdir > 2:
            obj_cent = [-1e6, -1e6, -1e6]
        else:
            obj_cent = [1e6, 1e6, 1e6]
        face_ob = None
        for face in self.primitives[objectname].faces:
            center = face.center
            if not center:
                continue
            if axisdir > 2 and center[axisdir - 3] > obj_cent[axisdir - 3]:
                obj_cent = center
                face_ob = face
            elif axisdir <= 2 and center[axisdir] < obj_cent[axisdir]:
                obj_cent = center
                face_ob = face
        vertx = face_ob.vertices
        start = vertx[0].position

        if not groundname:
            gnd_cent = []
            bounding = self.primitives.get_model_bounding_box()
            if axisdir < 3:
                for i in bounding[0:3]:
                    gnd_cent.append(float(i))
            else:
                for i in bounding[3:]:
                    gnd_cent.append(float(i))
        else:
            ground_plate = self.primitives[groundname]
            if axisdir > 2:
                gnd_cent = [1e6, 1e6, 1e6]
            else:
                gnd_cent = [-1e6, -1e6, -1e6]
            face_gnd = ground_plate.faces
            for face in face_gnd:
                center = face.center
                if not center:
                    continue
                if axisdir > 2 and center[axisdir - 3] < gnd_cent[axisdir - 3]:
                    gnd_cent = center
                elif axisdir <= 2 and center[axisdir] > gnd_cent[axisdir]:
                    gnd_cent = center

        axisdist = obj_cent[divmod(axisdir, 3)[1]] - gnd_cent[divmod(axisdir, 3)[1]]
        if axisdir < 3:
            axisdist = -axisdist

        if divmod(axisdir, 3)[1] == 0:
            cs = self._app.PLANE.YZ
            vector = [axisdist, 0, 0]
        elif divmod(axisdir, 3)[1] == 1:
            cs = self._app.PLANE.ZX
            vector = [0, axisdist, 0]
        elif divmod(axisdir, 3)[1] == 2:
            cs = self._app.PLANE.XY
            vector = [0, 0, axisdist]

        offset = self.find_point_around(objectname, start, sheet_dim, cs)
        p1 = self.primitives.create_polyline([start, offset])
        p2 = p1.clone().translate(vector)
        self.connect([p1, p2])

        return p1

    @aedt_exception_handler
    def _get_faceid_on_axis(self, objname, axisdir):
        """Get the ID of the face on the axis.

        Parameters
        ----------
        objname : str
            Name of the object.
        axisdir : int
            Axis direction. Options are ``1`` through ``5``.

        Returns
        -------
        int
            ID of the face.

        """
        faces = self.primitives.get_object_faces(objname)
        face = None
        center = None
        for f in faces:
            try:
                c = self.primitives.get_face_center(f)
                if not face and c:
                    face = f
                    center = c
                elif axisdir < 3 and c[axisdir] < center[axisdir]:
                    face = f
                    center = c
                elif axisdir > 2 and c[axisdir - 3] > center[axisdir - 3]:
                    face = f
                    center = c
            except:
                pass
        return face

    @aedt_exception_handler
    def _create_microstrip_sheet_from_object_closest_edge(self, startobj, endobject, axisdir, vfactor=3, hfactor=5):
        def duplicate_and_unite(sheet_name, array1, array2, dup_factor):
            status, list = self.duplicate_along_line(sheet_name, array1, dup_factor + 1)
            status, list2 = self.duplicate_along_line(sheet_name, array2, dup_factor + 1)
            list_unite.extend(list)
            list_unite.extend(list2)
            self.unite(list_unite)

        tol = 1e-6
        out, parallel = self.primitives.find_closest_edges(startobj, endobject, axisdir)
        port_edges = self.primitives.get_equivalent_parallel_edges(out, True, axisdir, startobj, endobject)
        if port_edges is None:
            return False
        sheet_name = port_edges[0].name
        point0 = port_edges[0].edges[0].midpoint
        point1 = port_edges[1].edges[0].midpoint
        len = port_edges[0].edges[0].length
        vect = GeometryOperators.v_points(point1, point0)
        l1 = out[0].length
        l2 = out[1].length
        if l1 < l2:
            vect_t = [i * (vfactor - 1) for i in vect]
            self.translate(port_edges[0], vect_t)
        else:
            vect_t = [i * (1 - vfactor) for i in vect]
            self.translate(port_edges[1], vect_t)

        self.connect(port_edges)
        list_unite = [sheet_name]
        dup_factor = divmod((hfactor + 1), 2)[0]
        coeff = float(hfactor - 1) / 2 / dup_factor

        if divmod(axisdir, 3)[1] == 0 and abs(vect[1]) < tol:
            duplicate_and_unite(sheet_name, [0, len * coeff, 0], [0, -len * coeff, 0], dup_factor)
        elif divmod(axisdir, 3)[1] == 0 and abs(vect[2]) < tol:
            duplicate_and_unite(sheet_name, [0, 0, len * coeff], [0, 0, -len * coeff], dup_factor)
        elif divmod(axisdir, 3)[1] == 1 and abs(vect[0]) < tol:
            duplicate_and_unite(sheet_name, [len * coeff, 0, 0], [-len * coeff, 0, 0], dup_factor)
        elif divmod(axisdir, 3)[1] == 1 and abs(vect[2]) < tol:
            duplicate_and_unite(sheet_name, [0, 0, len * coeff], [0, 0, -len * coeff], dup_factor)
        elif divmod(axisdir, 3)[1] == 2 and abs(vect[0]) < tol:
            duplicate_and_unite(sheet_name, [len * coeff, 0, 0], [-len * coeff, 0, 0], dup_factor)
        elif divmod(axisdir, 3)[1] == 2 and abs(vect[1]) < tol:
            duplicate_and_unite(sheet_name, [0, len * coeff, 0], [0, -len * coeff, 0], dup_factor)

        return sheet_name, point0, point1

    @aedt_exception_handler
    def get_excitations_name(self):
        """Get all excitation names.

        Returns
        -------
        list
            List of excitation names. Excitations with multiple modes will return one
            excitation for each mode.

        References
        ----------

        >>> oModule.GetExcitations
        """
        try:
            list_names = list(self._app.oboundary.GetExcitations())
            del list_names[1::2]
            return list_names
        except:
            return []

    @aedt_exception_handler
    def get_boundaries_name(self):
        """Retrieve all boundary names.

        Returns
        -------
        list
            List of boundary names. Boundaries with multiple modes will return one
            boundary for each mode.

        References
        ----------

        >>> oModule.GetBoundaries
        """
        list_names = list(self._app.oboundary.GetBoundaries())
        del list_names[1::2]
        return list_names

    @aedt_exception_handler
    def set_object_model_state(self, obj_list, model=True):
        """Set a list of objects to either models or non-models.

        Parameters
        ----------
        obj_list : list
            List of objects IDs or names.
        model : bool, optional
            Whether to set the objects as models. The default is ``True``.
            If ``False``, the objects are set as non-models.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        References
        ----------

        >>> oEditor.ChangeProperty
        """
        selections = self.convert_to_selections(obj_list, True)
        for obj in selections:
            self.primitives[obj].model = model
        return True

    @aedt_exception_handler
    def get_objects_in_group(self, group):
        """Retrieve a list of objects belonging to a group.

        Parameters
        ----------
        group : str
            Name of the group.

        Returns
        -------
        list
            List of objects belonging to the group.

        References
        ----------

        >>> oEditor.GetObjectsInGroup
        """
        if type(group) is not str:
            raise ValueError("Group name must be a string")
        group_objs = list(self.oeditor.GetObjectsInGroup(group))
        if not group_objs:
            return None
        return group_objs

    @aedt_exception_handler
    def get_group_bounding_box(self, group):
        """Retrieve the bounding box of a group.

        Parameters
        ----------
        group : str
            Name of the group.

        Returns
        -------
        list
            List of six float values representing the bounding box
            in the form ``[min_x, min_y, min_z, max_x, max_y, max_z]``.

        References
        ----------

        >>> oEditor.GetObjectsInGroup
        >>> oEditor.GetModelBoundingBox
        """
        if type(group) is not str:
            raise ValueError("Group name must be a string")
        group_objs = list(self.oeditor.GetObjectsInGroup(group))
        if not group_objs:
            return None
        all_objs = self.primitives.object_names
        objs_to_unmodel = [i for i in all_objs if i not in group_objs]
        if objs_to_unmodel:
            vArg1 = ["NAME:Model", "Value:=", False]
            self.primitives._change_geometry_property(vArg1, objs_to_unmodel)
            bounding = self.get_model_bounding_box()
            self._odesign.Undo()
        else:
            bounding = self.get_model_bounding_box()
        return bounding

    @aedt_exception_handler
    def convert_to_selections(self, objtosplit, return_list=False):
        """Convert one or more object to selections.

        Parameters
        ----------
        objtosplit : str, int, list
            One or more objects to convert to selections. A list can contain
            both strings (object names) and integers (object IDs).
        return_list : bool, option
            Whether to return a list of the selections. The default is
            ``False``, in which case a string of the selections is returned.
            If ``True``, a list of the selections is returned.

        Returns
        -------
        str or list
           String or list of the selections.

        """
        if "netref.builtins.list" in str(type(objtosplit)):
            list_new = []
            for i in range(len(objtosplit)):
                list_new.append(objtosplit[i])
        elif not isinstance(objtosplit, list):
            objtosplit = [objtosplit]
        objnames = []
        for el in objtosplit:
            if isinstance(el, int) and el in list(self.primitives.objects.keys()):
                objnames.append(self.primitives.objects[el].name)
            elif isinstance(el, int):
                objnames.append(el)
            elif isinstance(el, Object3d):
                objnames.append(el.name)
            elif isinstance(el, FacePrimitive):
                objnames.append(el.id)
            elif isinstance(el, str):
                objnames.append(el)
            else:
                return False
        if return_list:
            return objnames
        else:
            return ",".join(objnames)

    @aedt_exception_handler
    def split(self, objects, plane, sides="Both"):
        """Split a list of objects.

        Parameters
        ----------
        objects : str, int, or list
            One or more objects to split. A list can contain
            both strings (object names) and integers (object IDs).
        plane : str
            Coordinate plane of the cut or the Application.PLANE object.
            Choices for the coordinate plane are ``"XY"``, ``"YZ"``, and ``"ZX"``.
        sides : str
            Which side to keep. Options are ``"Both"``, ``"PositiveOnly"``,
            and ``"NegativeOnly"``. The default is ``"Both"``, in which case
            all objects are kept after the split.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        References
        ----------

        >>> oEditor.Split
        """
        planes = GeometryOperators.cs_plane_to_plane_str(plane)
        selections = self.convert_to_selections(objects)
        self.oeditor.Split(
            ["NAME:Selections", "Selections:=", selections, "NewPartsModelFlag:=", "Model"],
            [
                "NAME:SplitToParameters",
                "SplitPlane:=",
                planes,
                "WhichSide:=",
                sides,
                "ToolType:=",
                "PlaneTool",
                "ToolEntityID:=",
                -1,
                "SplitCrossingObjectsOnly:=",
                False,
                "DeleteInvalidObjects:=",
                True,
            ],
        )
        self.primitives.refresh_all_ids()
        return True

    @aedt_exception_handler
    def duplicate_and_mirror(self, objid, position, vector, is_3d_comp=False):
        """Duplicate and mirror a selection.

        Parameters
        ----------
        bjid : str, int, or  Object3d
            Name or ID of the object.
        position : float
            List of the ``[x, y, z]`` coordinates or
            Application.Position object for the selection.
        vector : float
            List of the ``[x1, y1, z1]`` coordinates or
            Application.Position object for the vector.
        is_3d_comp : bool, optional
            If ``True``, the method will try to return the duplicated list of 3dcomponents. The default is ``False``.

        Returns
        -------
        list
            List of objects created or an empty list.

        References
        ----------

        >>> oEditor.DuplicateMirror
        """
        selections = self.convert_to_selections(objid)
        Xpos, Ypos, Zpos = self.primitives._pos_with_arg(position)
        Xnorm, Ynorm, Znorm = self.primitives._pos_with_arg(vector)

        vArg1 = ["NAME:Selections", "Selections:=", selections, "NewPartsModelFlag:=", "Model"]
        vArg2 = ["NAME:DuplicateToMirrorParameters"]
        vArg2.append("DuplicateMirrorBaseX:="), vArg2.append(Xpos)
        vArg2.append("DuplicateMirrorBaseY:="), vArg2.append(Ypos)
        vArg2.append("DuplicateMirrorBaseZ:="), vArg2.append(Zpos)
        vArg2.append("DuplicateMirrorNormalX:="), vArg2.append(Xnorm)
        vArg2.append("DuplicateMirrorNormalY:="), vArg2.append(Ynorm)
        vArg2.append("DuplicateMirrorNormalZ:="), vArg2.append(Znorm)
        vArg3 = ["NAME:Options", "DuplicateAssignments:=", False]
        if is_3d_comp:
            orig_3d = [i for i in self.primitives.components_3d_names]
        added_objs = self.oeditor.DuplicateMirror(vArg1, vArg2, vArg3)
        self.primitives.add_new_objects()
        if is_3d_comp:
            added_3d_comps = [i for i in self.primitives.components_3d_names if i not in orig_3d]
            if added_3d_comps:
                self.logger.info("Found 3D Components Duplication")
                return True, added_3d_comps
        return True, added_objs

    @aedt_exception_handler
    def mirror(self, objid, position, vector):
        """Mirror a selection.

        Parameters
        ----------
        objid : str, int, or Object3d
            Name or ID of the object.
        position : float
            List of the ``[x, y, z]`` coordinates or the
            Application.Position object for the selection.
        vector : float
            List of the ``[x1, y1, z1]`` coordinates or
            the Application.Position object for the vector.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        References
        ----------

        >>> oEditor.Mirror
        """
        selections = self.convert_to_selections(objid)
        Xpos, Ypos, Zpos = self.primitives._pos_with_arg(position)
        Xnorm, Ynorm, Znorm = self.primitives._pos_with_arg(vector)

        vArg1 = ["NAME:Selections", "Selections:=", selections, "NewPartsModelFlag:=", "Model"]
        vArg2 = ["NAME:MirrorParameters"]
        vArg2.append("MirrorBaseX:="), vArg2.append(Xpos)
        vArg2.append("MirrorBaseY:="), vArg2.append(Ypos)
        vArg2.append("MirrorBaseZ:="), vArg2.append(Zpos)
        vArg2.append("MirrorNormalX:="), vArg2.append(Xnorm)
        vArg2.append("MirrorNormalY:="), vArg2.append(Ynorm)
        vArg2.append("MirrorNormalZ:="), vArg2.append(Znorm)

        self.oeditor.Mirror(vArg1, vArg2)

        return True

    @aedt_exception_handler
    def duplicate_around_axis(self, objid, cs_axis, angle=90, nclones=2, create_new_objects=True, is_3d_comp=False):
        """Duplicate a selection around an axis.

        Parameters
        ----------
        objid : str, int, or Object3d
            Name or ID of the object.
        cs_axis :
            Coordinate system axis or the Application.CoordinateSystemAxis object.
        angle : float, optional
            Angle rotation in degees. The default is ``90``.
        nclones : int, optional
            Number of clones. The default is ``2``.
        create_new_objects :
            Whether to create the copies as new objects. The
            default is ``True``.
        is_3d_comp : bool, optional
            If ``True``, the method will try to return the duplicated list of 3dcomponents. The default is ``False``.

        Returns
        -------
        tuple

        References
        ----------

        >>> oEditor.DuplicateAroundAxis
        """
        selections = self.convert_to_selections(objid)

        vArg1 = ["NAME:Selections", "Selections:=", selections, "NewPartsModelFlag:=", "Model"]
        vArg2 = [
            "NAME:DuplicateAroundAxisParameters",
            "CreateNewObjects:=",
            create_new_objects,
            "WhichAxis:=",
            GeometryOperators.cs_axis_str(cs_axis),
            "AngleStr:=",
            self.primitives._arg_with_dim(angle, "deg"),
            "Numclones:=",
            str(nclones),
        ]
        vArg3 = ["NAME:Options", "DuplicateBoundaries:=", "true"]
        if is_3d_comp:
            orig_3d = [i for i in self.primitives.components_3d_names]
        added_objs = self.oeditor.DuplicateAroundAxis(vArg1, vArg2, vArg3)
        self._duplicate_added_objects_tuple()
        if is_3d_comp:
            added_3d_comps = [i for i in self.primitives.components_3d_names if i not in orig_3d]
            if added_3d_comps:
                self.logger.info("Found 3D Components Duplication")
                return True, added_3d_comps

        return True, list(added_objs)

    def _duplicate_added_objects_tuple(self):
        added_objects = self.primitives.add_new_objects()
        if added_objects:
            return True, added_objects
        else:
            return False, []

    @aedt_exception_handler
    def duplicate_along_line(self, objid, vector, nclones=2, attachObject=False, is_3d_comp=False):
        """Duplicate a selection along a line.

        Parameters
        ----------
        objid : str, int, or Object3d
            Name or ID of the object.
        vector : list
            List of ``[x1,y1,z1]`` coordinates or the Application.Position object for
            the vector.
        attachObject : bool, optional
            The default is ``False``.
        nclones : int, optional
            Number of clones. The default is ``2``.
        is_3d_comp : bool, optional
            If True, the method will try to return the duplicated list of 3dcomponents. The default is ``False``.
        Returns
        -------
        tuple

        References
        ----------

        >>> oEditor.DuplicateAlongLine
        """
        selections = self.convert_to_selections(objid)
        Xpos, Ypos, Zpos = self.primitives._pos_with_arg(vector)

        vArg1 = ["NAME:Selections", "Selections:=", selections, "NewPartsModelFlag:=", "Model"]
        vArg2 = ["NAME:DuplicateToAlongLineParameters"]
        vArg2.append("CreateNewObjects:="), vArg2.append(not attachObject)
        vArg2.append("XComponent:="), vArg2.append(Xpos)
        vArg2.append("YComponent:="), vArg2.append(Ypos)
        vArg2.append("ZComponent:="), vArg2.append(Zpos)
        vArg2.append("Numclones:="), vArg2.append(str(nclones))
        vArg3 = ["NAME:Options", "DuplicateBoundaries:=", "true"]
        if is_3d_comp:
            orig_3d = [i for i in self.primitives.components_3d_names]
        added_objs = self.oeditor.DuplicateAlongLine(vArg1, vArg2, vArg3)
        self._duplicate_added_objects_tuple()
        if is_3d_comp:
            added_3d_comps = [i for i in self.primitives.components_3d_names if i not in orig_3d]
            if added_3d_comps:
                self.logger.info("Found 3D Components Duplication")
                return True, added_3d_comps
        return True, list(added_objs)
        # return self._duplicate_added_objects_tuple()

    @aedt_exception_handler
    def thicken_sheet(self, objid, thickness, bBothSides=False):
        """Thicken the sheet of the selection.

        Parameters
        ----------
        objid :
            Name or ID of the object.
        thickness : float, str
            Amount to thicken the sheet by.
        bBothSides : bool, optional
            Whether to thicken the sheet on both side. The default is ``False``.

        Returns
        -------
        pyaedt.modeler.Object3d.Object3d

        References
        ----------

        >>> oEditor.ThickenSheet
        """
        selections = self.convert_to_selections(objid)

        vArg1 = ["NAME:Selections", "Selections:=", selections, "NewPartsModelFlag:=", "Model"]
        vArg2 = ["NAME:SheetThickenParameters"]
        vArg2.append("Thickness:="), vArg2.append(self.primitives._arg_with_dim(thickness))
        vArg2.append("BothSides:="), vArg2.append(bBothSides)

        self.oeditor.ThickenSheet(vArg1, vArg2)
        return self.primitives.update_object(objid)

    @aedt_exception_handler
    def sweep_along_normal(self, obj_name, face_id, sweep_value=0.1):
        """Sweep the selection along the vector.

        Parameters
        ----------
        obj_name : str, int
            Name or ID of the object.
        face_id : int
            Face to sweep.
        sweep_value : float, optional
            Sweep value. The default is ``0.1``.

        Returns
        -------
        pyaedt.modeler.Object3d.Object3d

        References
        ----------

        >>> oEditor.SweepFacesAlongNormal
        """
        selections = self.convert_to_selections(obj_name)
        vArg1 = ["NAME:Selections", "Selections:=", selections, "NewPartsModelFlag:=", "Model"]
        vArg2 = ["NAME:Parameters"]
        vArg2.append(
            [
                "NAME:SweepFaceAlongNormalToParameters",
                "FacesToDetach:=",
                [face_id],
                "LengthOfSweep:=",
                self.primitives._arg_with_dim(sweep_value),
            ]
        )

        objs = self.primitives._all_object_names
        self.oeditor.SweepFacesAlongNormal(vArg1, vArg2)
        self.primitives.cleanup_objects()
        objs2 = self.primitives._all_object_names
        obj = [i for i in objs2 if i not in objs]
        for el in obj:
            self.primitives._create_object(el)
        if obj:
            return self.primitives.update_object(self.primitives[obj[0]])
        return False

    @aedt_exception_handler
    def sweep_along_vector(self, objid, sweep_vector, draft_angle=0, draft_type="Round"):
        """Sweep the selection along a vector.

        Parameters
        ----------
        objid : str, int
            Name or ID of the object.
        sweep_vector : float
            List of ``[x1, y1, z1]`` coordinates or Application.Position object for
            the vector.
        draft_angle : float, optional
            Draft angle in degrees. The default is ``0``.
        draft_type : str
            Type of the draft. Options are ``"Round"``, ``"Natural"``,
            and ``"Extended"``. The default is ``"Round"``.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        References
        ----------

        >>> oEditor.SweepAlongVector
        """
        selections = self.convert_to_selections(objid)
        vectorx, vectory, vectorz = self.primitives._pos_with_arg(sweep_vector)
        vArg1 = ["NAME:Selections", "Selections:=", selections, "NewPartsModelFlag:=", "Model"]
        vArg2 = ["NAME:VectorSweepParameters"]
        vArg2.append("DraftAngle:="), vArg2.append(self.primitives._arg_with_dim(draft_angle, "deg"))
        vArg2.append("DraftType:="), vArg2.append(GeometryOperators.draft_type_str(draft_type))
        vArg2.append("SweepVectorX:="), vArg2.append(vectorx)
        vArg2.append("SweepVectorY:="), vArg2.append(vectory)
        vArg2.append("SweepVectorZ:="), vArg2.append(vectorz)

        self.oeditor.SweepAlongVector(vArg1, vArg2)

        return self.primitives.update_object(objid)

    @aedt_exception_handler
    def sweep_along_path(
        self, objid, sweep_object, draft_angle=0, draft_type="Round", is_check_face_intersection=False, twist_angle=0
    ):
        """Sweep the selection along a path.

        Parameters
        ----------
        objid : str, int
            Name or ID of the object.
        sweep_object : str, int
            Name or ID of the sweep.
        draft_angle : float, optional
            Draft angle in degrees. The default is ``0``.
        draft_type : str
            Type of the draft. Options are ``"Round"``, ``"Natural"``,
            and ``"Extended"``. The default is ``"Round"``.
        is_check_face_intersection : bool, optional
            The default is ``False``.
        twist_angle : float, optional
           Twist angle in degrees. The default is ``0``.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        References
        ----------

        >>> oEditor.SweepAlongPath
        """
        selections = self.convert_to_selections(objid) + "," + self.convert_to_selections(sweep_object)
        vArg1 = ["NAME:Selections", "Selections:=", selections, "NewPartsModelFlag:=", "Model"]
        vArg2 = ["NAME:PathSweepParameters"]
        vArg2.append("DraftAngle:="), vArg2.append(self.primitives._arg_with_dim(draft_angle, "deg"))
        vArg2.append("DraftType:="), vArg2.append(GeometryOperators.draft_type_str(draft_type))
        vArg2.append("CheckFaceFaceIntersection:="), vArg2.append(is_check_face_intersection)
        vArg2.append("TwistAngle:="), vArg2.append(str(twist_angle) + "deg")

        self.oeditor.SweepAlongPath(vArg1, vArg2)

        return self.primitives.update_object(objid)

    @aedt_exception_handler
    def sweep_around_axis(self, objid, cs_axis, sweep_angle=360, draft_angle=0):
        """Sweep the selection around the axis.

        Parameters
        ----------
        objid : str, int
            Name or ID of the object.
        cs_axis :
            Coordinate system axis or the Application.CoordinateSystemAxis object.
        sweep_angle : float
            Sweep angle in degrees. The default is ``360``.
        draft_angle : float
            Draft angle in degrees. The default is ``0``.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        References
        ----------

        >>> oEditor.SweepAroundAxis
        """
        selections = self.convert_to_selections(objid)

        vArg1 = ["NAME:Selections", "Selections:=", selections, "NewPartsModelFlag:=", "Model"]
        vArg2 = [
            "NAME:AxisSweepParameters",
            "DraftAngle:=",
            self.primitives._arg_with_dim(draft_angle, "deg"),
            "DraftType:=",
            "Round",
            "CheckFaceFaceIntersection:=",
            False,
            "SweepAxis:=",
            GeometryOperators.cs_axis_str(cs_axis),
            "SweepAngle:=",
            self.primitives._arg_with_dim(sweep_angle, "deg"),
            "NumOfSegments:=",
            "0",
        ]

        self.oeditor.SweepAroundAxis(vArg1, vArg2)

        return self.primitives.update_object(objid)

    @aedt_exception_handler
    def section(self, object_list, plane, create_new=True, section_cross_object=False):
        """Section the selection.

        Parameters
        ----------
        object_list : str, int, or Object3d
            One or more objects to section.
        plane : str
            Coordinate plane or Application.PLANE object.
            Choices for the coordinate plane are ``"XY"``, ``"YZ"``, and ``"ZX"``.'
        create_new : bool, optional
            The default is ``True``, but this parameter has no effect.
        section_cross_object : bool, optional
            The default is ``False``, but this parameter has no effect.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        References
        ----------

        >>> oEditor.Section
        """
        plane_ids = [0, 1, 2]
        plane_str = ["XY", "YZ", "ZX"]
        if plane in plane_ids:
            section_plane = plane_str[plane]
        elif plane in plane_str:
            section_plane = plane
        else:
            return False

        selections = self.convert_to_selections(object_list)

        self.oeditor.Section(
            ["NAME:Selections", "Selections:=", selections, "NewPartsModelFlag:=", "Model"],
            [
                "NAME:SectionToParameters",
                "CreateNewObjects:=",
                create_new,
                "SectionPlane:=",
                section_plane,
                "SectionCrossObject:=",
                section_cross_object,
            ],
        )
        self.primitives.refresh_all_ids()
        return True

    @aedt_exception_handler
    def separate_bodies(self, object_list, create_group=False):
        """Separate bodies of the selection.

        Parameters
        ----------
        object_list : list
            List of objects to separate.
        create_group : bool, optional
            Whether to create a group. The default is ``False``.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        References
        ----------

        >>> oEditor.SeparateBody
        """
        selections = self.convert_to_selections(object_list)
        self.oeditor.SeparateBody(
            ["NAME:Selections", "Selections:=", selections, "NewPartsModelFlag:=", "Model"],
            ["CreateGroupsForNewObjects:=", create_group],
        )
        self.primitives.refresh_all_ids()
        return True

    @aedt_exception_handler
    def rotate(self, objid, cs_axis, angle=90.0, unit="deg"):
        """Rotate the selection.

        Parameters
        ----------
        objid : int
             ID of the object.
        cs_axis
            Coordinate system axis or the Application.CoordinateSystemAxis object.
        angle : float
            Angle of rotation. The units, defined by ``unit``, can be either
            degrees or radians. The default is ``90.0``.
        unit : text, optional
             Units for the angle. Options are ``"deg"`` or ``"rad"``.
             The default is ``"deg"``.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        References
        ----------

        >>> oEditor.Rotate
        """
        selections = self.convert_to_selections(objid)
        vArg1 = ["NAME:Selections", "Selections:=", selections, "NewPartsModelFlag:=", "Model"]
        vArg2 = ["NAME:RotateParameters"]
        vArg2.append("RotateAxis:="), vArg2.append(GeometryOperators.cs_axis_str(cs_axis))
        vArg2.append("RotateAngle:="), vArg2.append(self.primitives._arg_with_dim(angle, unit))

        if self.oeditor is not None:
            self.oeditor.Rotate(vArg1, vArg2)

        return True

    @aedt_exception_handler
    def subtract(self, blank_list, tool_list, keepOriginals=True):
        """Subtract objects.

        Parameters
        ----------
        blank_list : list of Object3d or list of int
            List of objects to subtract from. The list can be of
            either :class:`pyaedt.modeler.Object3d.Object3d` objects or object IDs.
        tool_list : list
            List of objects to subtract. The list can be of
            either Object3d objects or object IDs.
        keepOriginals : bool, optional
            Whether to keep the original objects. The default is ``True``.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        References
        ----------

        >>> oEditor.Subtract
        """
        szList = self.convert_to_selections(blank_list)
        szList1 = self.convert_to_selections(tool_list)

        vArg1 = ["NAME:Selections", "Blank Parts:=", szList, "Tool Parts:=", szList1]
        vArg2 = ["NAME:SubtractParameters", "KeepOriginals:=", keepOriginals]

        self.oeditor.Subtract(vArg1, vArg2)
        if not keepOriginals:
            self.primitives.cleanup_objects()

        return True

    @aedt_exception_handler
    def purge_history(self, theList):
        """Purge history objects from object names.

        Parameters
        ----------
        theList : list
            List of object names to purge.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        References
        ----------

        >>> oEditor.PurgeHistory
        """
        szList = self.convert_to_selections(theList)

        vArg1 = ["NAME:Selections", "Selections:=", szList, "NewPartsModelFlag:=", "Model"]

        self.oeditor.PurgeHistory(vArg1)
        return True

    @aedt_exception_handler
    def get_model_bounding_box(self):
        """Retrieve the model bounding box.


        Returns
        -------
        list
            List of six float values representing the bounding box
            in the form ``[min_x, min_y, min_z, max_x, max_y, max_z]``.

        References
        ----------

        >>> oEditor.GetModelBoundingBox
        """
        bb = list(self.oeditor.GetModelBoundingBox())
        bound = [float(b) for b in bb]
        return bound

    @aedt_exception_handler
    def unite(self, theList):
        """Unite objects from a list.

        Parameters
        ----------
        theList : list
            List of objects.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        References
        ----------

        >>> oEditor.Unite
        """
        slice = min(20, len(theList))
        num_objects = len(theList)
        remaining = num_objects
        objs_groups = []
        while remaining > 0:
            objs = theList[:slice]
            szSelections = self.convert_to_selections(objs)
            vArg1 = ["NAME:Selections", "Selections:=", szSelections]
            vArg2 = ["NAME:UniteParameters", "KeepOriginals:=", False]
            self.oeditor.Unite(vArg1, vArg2)
            objs_groups.append(objs[0])
            remaining -= slice
            if remaining > 0:
                theList = theList[slice:]
        self.primitives.cleanup_objects()
        if len(objs_groups) > 1:
            return self.unite(objs_groups)
        self.logger.info("Union of {} objects has been executed.".format(num_objects))
        return True

    @aedt_exception_handler
    def clone(self, objid):
        """Clone objects from a list of object IDs.

        Parameters
        ----------
        objid : list
            List of object IDs.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.
        str
            Name of objects cloned when successful.

        References
        ----------

        >>> oEditor.Copy
        >>> oEditor.Paste
        """

        szSelections = self.convert_to_selections(objid)
        vArg1 = ["NAME:Selections", "Selections:=", szSelections]

        self.oeditor.Copy(vArg1)
        self.oeditor.Paste()
        new_objects = self.primitives.add_new_objects()
        return True, new_objects

    @aedt_exception_handler
    def intersect(self, theList, keeporiginal=False):
        """Intersect objects from a list.

        Parameters
        ----------
        theList : list
            List of objects.
        keeporiginal : bool, optional
            Whether to keep the original object. The default is ``False``.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        References
        ----------

        >>> oEditor.Intersect
        """
        unclassified = list(self.oeditor.GetObjectsInGroup("Unclassified"))
        szSelections = self.convert_to_selections(theList)

        vArg1 = ["NAME:Selections", "Selections:=", szSelections]
        vArg2 = ["NAME:IntersectParameters", "KeepOriginals:=", keeporiginal]

        self.oeditor.Intersect(vArg1, vArg2)
        unclassified1 = list(self.oeditor.GetObjectsInGroup("Unclassified"))
        if unclassified != unclassified1:
            self._odesign.Undo()
            self.logger.error("Error in intersection. Reverting Operation")
            return False
        self.primitives.cleanup_objects()
        self.logger.info("Intersection Succeeded")
        return True

    @aedt_exception_handler
    def connect(self, theList):
        """Connect objects from a list.

        Parameters
        ----------
        theList : list
            List of objects.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        References
        ----------

        >>> oEditor.Connect
        """
        unclassified_before = list(self.primitives.unclassified_names)
        szSelections = self.convert_to_selections(theList)

        vArg1 = ["NAME:Selections", "Selections:=", szSelections]

        self.oeditor.Connect(vArg1)
        if unclassified_before != self.primitives.unclassified_names:
            self._odesign.Undo()
            self.logger.error("Error in connection. Reverting Operation")
            return False

        self.primitives.cleanup_objects()
        self.logger.info("Connection Correctly created")
        return True

    @aedt_exception_handler
    def translate(self, objid, vector):
        """Translate objects from a list.

        Parameters
        ----------
        objid : list, Position object
            List of object IDs.
        vector : list
            Vector of the direction move. It can be a list of the ``[x, y, z]``
            coordinates or a Position object.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        References
        ----------

        >>> oEditor.Move
        """
        Xvec, Yvec, Zvec = self.primitives._pos_with_arg(vector)
        szSelections = self.convert_to_selections(objid)

        vArg1 = ["NAME:Selections", "Selections:=", szSelections, "NewPartsModelFlag:=", "Model"]
        vArg2 = ["NAME:TranslateParameters"]
        vArg2.append("TranslateVectorX:="), vArg2.append(Xvec)
        vArg2.append("TranslateVectorY:="), vArg2.append(Yvec)
        vArg2.append("TranslateVectorZ:="), vArg2.append(Zvec)

        if self.oeditor is not None:
            self.oeditor.Move(vArg1, vArg2)
        return True

    @aedt_exception_handler
    def chassis_subtraction(self, chassis_part):
        """Subtract all non-vacuum objects from the main chassis object.

        Parameters
        ----------
        chassis_part : str
            Name of the main chassis object.

        References
        ----------

        >>> oEditor.Subtract
        """
        self.logger.info("Subtract all objects from Chassis object - exclude vacuum objs")
        mat_names = self._omaterial_manager.GetNames()
        num_obj_start = self.oeditor.GetNumObjects()
        blank_part = chassis_part
        # in main code this object will need to be determined automatically eg by name such as chassis or sheer size
        self.logger.info("Blank Part in Subtraction = " + str(blank_part))
        """
        check if blank part exists, if not, skip subtraction
        """
        tool_parts = list(self.oeditor.GetObjectsInGroup("Solids"))
        tool_parts.remove(blank_part)
        for mat in mat_names:
            if str(mat).lower() == "vacuum":
                objnames = self.oeditor.GetObjectsByMaterial(mat)
                for obj in objnames:
                    tool_parts.remove(obj)
                # tool_parts_final=list(set(tool_parts).difference(set(objnames)))
        tool_parts = ",".join(tool_parts)
        num_obj_end = self.oeditor.GetNumObjects()
        self.subtract(blank_part, tool_parts, True)

        self.logger.info("Subtraction Objs - Initial: " + str(num_obj_start) + "  ,  Final: " + str(num_obj_end))

    @aedt_exception_handler
    def _offset_on_plane(self, i, offset):
        """Offset the object on a plane.

        Parameters
        ----------
        i :

        offset :
            Offset to apply.

        Returns
        -------
        tuple
           Position of object after offset is applied.

        """
        if i > 7:
            off1 = 0
        elif i % 4 == 0 or i % 4 == 1:
            off1 = offset
        else:
            off1 = -offset
        if 3 < i < 8:
            off2 = 0
        elif i % 2 == 0:
            off2 = offset
        else:
            off2 = -offset
        if i < 4:
            off3 = 0
        elif i != 4 and i != 7 and i != 8 and i != 11:
            off3 = -offset
        else:
            off3 = +offset
        return off1, off2, off3

    @aedt_exception_handler
    def check_plane(self, obj, faceposition, offset=1):
        """Check for the plane that is defined as the face for an object.

        Parameters
        ----------
        obj : str
            Name of the object.
        faceposition : list
            List of the ``[x, y, z]`` coordinates for the position of the face.
        offset : optional
            Offset to apply. The default is ``1``.

        Returns
        -------
        type
            Plane string

        """

        Xvec, Yvec, Zvec = self.primitives._pos_with_arg(faceposition)

        if isinstance(obj, int):
            obj = self.primitives.objects[obj].name
        plane = None
        found = False
        i = 0
        while not found:
            off1, off2, off3 = self._offset_on_plane(i, offset)
            vArg1 = ["NAME:FaceParameters"]
            vArg1.append("BodyName:="), vArg1.append(obj)
            vArg1.append("XPosition:="), vArg1.append(Xvec + "+" + self.primitives._arg_with_dim(off1))
            vArg1.append("YPosition:="), vArg1.append(Yvec + "+" + self.primitives._arg_with_dim(off2))
            vArg1.append("ZPosition:="), vArg1.append(Zvec + "+" + self.primitives._arg_with_dim(off3))
            try:
                face_id = self.oeditor.GetFaceByPosition(vArg1)
                if i < 4:
                    plane = "XY"
                elif i < 8:
                    plane = "XZ"
                else:
                    plane = "YZ"
                found = True
            except:
                i = i + 1
                if i > 11:
                    found = True

        return plane

    @aedt_exception_handler
    def get_matched_object_name(self, search_string):
        """Retrieve the name of the matched object.

        Parameters
        ----------
        search_string : str
            Text string to search for.


        Returns
        -------
        str
            Name of the matched object.

        References
        ----------

        >>> oEditor.GetMatchedObjectName
        """
        return self.oeditor.GetMatchedObjectName(search_string)

    @aedt_exception_handler
    def clean_objects_name(self, main_part_name):
        """Clean the names of the objects for a main part.

        Parameters
        ----------
        main_part_name : str
            Name of the main part.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        References
        ----------

        >>> oEditor.RenamePart
        """
        # import os.path
        # (CADPath, CADFilename) = os.path.split(CADFile)
        # (CADName, CADExt) = os.path.splitext(CADFilename)
        CADSuffix = main_part_name + "_"
        objNames = self.oeditor.GetMatchedObjectName(CADSuffix + "*")
        for name in objNames:
            RenameArgs = {}
            RenameArgs["NAME"] = "Rename Data"
            RenameArgs["Old Name"] = name
            RenameArgs["New Name"] = name.replace(CADSuffix, "")
            self.oeditor.RenamePart(RenameArgs)
        return True

    @aedt_exception_handler
    def create_airbox(self, offset=0, offset_type="Absolute", defname="AirBox_Auto"):
        """Create an airbox that is as big as the bounding extension of the project.

        Parameters
        ----------
        offset :
            Double offset value to apply on the airbox faces versus the bounding box.
            The default is ``0``.
        offset_type : str
            Type of the offset. Options are ``"Absolute"`` and ``"Relative"``.
            The default is ``"Absolute"``. If ``"Relative"``, the offset input
            is between 0 and 100.
        defname : str, optional
            Name of the airbox. The default is ``"AirBox_Auto"``.

        Returns
        -------
        int
            ID of the airbox created.

        References
        ----------

        >>> oEditor.CreateBox
        """
        self.logger.info("Adding Airbox to the Bounding ")

        bound = self.get_model_bounding_box()
        if offset_type == "Absolute":
            offset1 = offset2 = offset3 = offset
        else:
            offset1 = (bound[3] - bound[0]) * offset / 100
            offset2 = (bound[4] - bound[1]) * offset / 100
            offset3 = (bound[5] - bound[2]) * offset / 100
        startpos = self.Position(bound[0] - offset1, bound[1] - offset2, bound[2] - offset3)

        dim = []
        dim.append(bound[3] - bound[0] + 2 * offset1)
        dim.append(bound[4] - bound[1] + 2 * offset2)
        dim.append(bound[5] - bound[2] + 2 * offset3)
        airid = self.primitives.create_box(startpos, dim, defname)
        return airid

    @aedt_exception_handler
    def create_air_region(self, x_pos=0, y_pos=0, z_pos=0, x_neg=0, y_neg=0, z_neg=0):
        """Create an air region.

        Parameters
        ----------
        x_pos : float, optional
            Padding in percent in the +X direction (+R for 2D RZ).
            The default is ``0``.
        y_pos : float, optional
            Padding in percent in the +Y direction. The default is ``0``.
        z_pos : float, optional
            Padding in percent in the +Z direction. The default is ``0``.
        x_neg : float, optional
            Padding in percent in the -X direction (-R for 2D RZ).
            The default is ``0``.
        y_neg : float, optional
            Padding in percent in the -Y direction. The default is ``0``.
        z_neg : float, optional
            Padding in percent in the -Z direction. The default is ``0``.

        Returns
        -------
        list
            List of ``[x_pos, y_pos, z_pos, x_neg, y_neg, z_neg]``
            coordinates for the region created.

        References
        ----------

        >>> oEditor.CreateRegion
        """
        return self.primitives.create_region([x_pos, y_pos, z_pos, x_neg, y_neg, z_neg])

    @aedt_exception_handler
    def create_coaxial(
        self,
        startingposition,
        axis,
        innerradius=1,
        outerradius=2,
        dielradius=1.8,
        length=10,
        matinner="copper",
        matouter="copper",
        matdiel="teflon_based",
    ):
        """Create a coaxial.

        Parameters
        ----------
        startingposition : list
            List of ``[x, y, z]`` coordinates for the starting position.
        axis : int
            Coordinate system AXIS (integer ``0`` for X, ``1`` for Y, ``2`` for Z) or
            the :class:`Application.CoordinateSystemAxis` enumerator.
        innerradius : float, optional
            Inner coax radius. The default is ``1``.
        outerradius : float, optional
            Outer coax radius. The default is ``2``.
        dielradius : float, optional
            Dielectric coax radius. The default is ``1.8``.
        length : float, optional
            Coaxial length. The default is ``10``.
        matinner : str, optional
            Material for the inner coaxial. The default is ``"copper"``.
        matouter : str, optional
            Material for the outer coaxial. The default is ``"copper"``.
        matdiel : str, optional
            Material for the dielectric. The default is ``"teflon_based"``.

        Returns
        -------
        tuple
            Contains the inner, outer, and dielectric coax as
            :class:`pyaedt.modeler.Object3d.Object3d` objects.

        References
        ----------

        >>> oEditor.CreateCylinder
        >>> oEditor.AssignMaterial


        Examples
        --------

        This example shows how to create a Coaxial Along X Axis waveguide.

        >>> from pyaedt import Hfss
        >>> app = Hfss()
        >>> position = [0,0,0]
        >>> coax = app.modeler.create_coaxial(
        ...    position, app.AXIS.X, innerradius=0.5, outerradius=0.8, dielradius=0.78, length=50
        ... )

        """
        if not (outerradius > dielradius and dielradius > innerradius):
            raise ValueError("Error in coaxial radius.")
        inner = self.primitives.create_cylinder(axis, startingposition, innerradius, length, 0)
        outer = self.primitives.create_cylinder(axis, startingposition, outerradius, length, 0)
        diel = self.primitives.create_cylinder(axis, startingposition, dielradius, length, 0)
        self.subtract(outer, inner)
        self.subtract(outer, diel)
        inner.material_name = matinner
        outer.material_name = matouter
        diel.material_name = matdiel

        return inner, outer, diel

    @aedt_exception_handler
    def create_waveguide(
        self,
        origin,
        wg_direction_axis,
        wgmodel="WG0",
        wg_length=100,
        wg_thickness=None,
        wg_material="aluminum",
        parametrize_w=False,
        parametrize_h=False,
        create_sheets_on_openings=False,
        name=None,
    ):
        """Create a standard waveguide and optionally parametrize `W` and `H`.

        Available models are WG0.0, WG0, WG1, WG2, WG3, WG4, WG5, WG6,
        WG7, WG8, WG9, WG9A, WG10, WG11, WG11A, WG12, WG13, WG14,
        WG15, WR102, WG16, WG17, WG18, WG19, WG20, WG21, WG22, WG24,
        WG25, WG26, WG27, WG28, WG29, WG29, WG30, WG31, and WG32.

        Parameters
        ----------
        origin : list
            List of ``[x, y, z]`` coordinates for the original position.
        wg_direction_axis : int
            Coordinate system axis (integer ``0`` for X, ``1`` for Y, ``2`` for Z) or
            the :class:`Application.CoordinateSystemAxis` enumerator.
        wgmodel : str, optional
            Waveguide model. The default is ``"WG0"``.
        wg_length : float, optional
            Waveguide length. The default is ``100``.
        wg_thickness : float, optional
            Waveguide thickness. The default is ``None``, in which case the
            thickness is `wg_height/20`.
        wg_material : str, optional
            Waveguide material. The default is ``"aluminum"``.
        parametrize_w : bool, optional
            Whether to parametrize `W`. The default is ``False``.
        parametrize_h : bool, optional
            Whether to parametrize `H`. The default is ``False``.
        create_sheets_on_openings : bool, optional
            Whether to create sheets on both openings. The default is ``False``.
        name : str, optional
            Name of the waveguide. The default is ``None``.

        Returns
        -------
        tuple
            Tuple of :class:`Object3d <pyaedt.modeler.Object3d.Object3d>`
            objects created by the waveguide.

        References
        ----------

        >>> oEditor.CreateBox
        >>> oEditor.AssignMaterial


        Examples
        --------

        This example shows how to create a WG9 waveguide.

        >>> from pyaedt import Hfss
        >>> app = Hfss()
        >>> position = [0, 0, 0]
        >>> wg1 = app.modeler.create_waveguide(position, app.AXIS.,
        ...                                    wgmodel="WG9", wg_length=2000)


        """
        p1 = -1
        p2 = -1
        WG = {
            "WG0.0": [584.2, 292.1],
            "WG0": [533.4, 266.7],
            "WG1": [457.2, 228.6],
            "WG2": [381, 190.5],
            "WG3": [292.1, 146.05],
            "WG4": [247.65, 123.825],
            "WG5": [195.58, 97.79],
            "WG6": [165.1, 82.55],
            "WG7": [129.54, 64.77],
            "WG8": [109.22, 54.61],
            "WG9": [88.9, 44.45],
            "WG9A": [86.36, 43.18],
            "WG10": [72.136, 34.036],
            "WG11": [60.2488, 28.4988],
            "WG11A": [58.166, 29.083],
            "WG12": [47.5488, 22.1488],
            "WG13": [40.386, 20.193],
            "WG14": [34.8488, 15.7988],
            "WG15": [28.4988, 12.6238],
            "WR102": [25.908, 12.954],
            "WG16": [22.86, 10.16],
            "WG17": [19.05, 9.525],
            "WG18": [15.7988, 7.8994],
            "WG19": [12.954, 6.477],
            "WG20": [0.668, 4.318],
            "WG21": [8.636, 4.318],
            "WG22": [7.112, 3.556],
            "WG23": [5.6896, 2.8448],
            "WG24": [4.7752, 2.3876],
            "WG25": [3.7592, 1.8796],
            "WG26": [3.0988, 1.5494],
            "WG27": [2.54, 1.27],
            "WG28": [2.032, 1.016],
            "WG29": [1.651, 0.8255],
            "WG30": [1.2954, 0.6477],
            "WG31": [1.0922, 0.5461],
            "WG32": [0.8636, 0.4318],
        }

        if wgmodel in WG:
            wgwidth = WG[wgmodel][0]
            wgheight = WG[wgmodel][1]
            if not wg_thickness:
                wg_thickness = wgheight / 20
            if parametrize_h:
                self._app[wgmodel + "_H"] = self.primitives._arg_with_dim(wgheight)
                h = wgmodel + "_H"
                hb = wgmodel + "_H + 2*" + self.primitives._arg_with_dim(wg_thickness)
            else:
                h = self.primitives._arg_with_dim(wgheight)
                hb = self.primitives._arg_with_dim(wgheight) + " + 2*" + self.primitives._arg_with_dim(wg_thickness)

            if parametrize_w:
                self._app[wgmodel + "_W"] = self.primitives._arg_with_dim(wgwidth)
                w = wgmodel + "_W"
                wb = wgmodel + "_W + " + self.primitives._arg_with_dim(2 * wg_thickness)
            else:
                w = self.primitives._arg_with_dim(wgwidth)
                wb = self.primitives._arg_with_dim(wgwidth) + " + 2*" + self.primitives._arg_with_dim(wg_thickness)
            if wg_direction_axis == self._app.AXIS.Z:
                airbox = self.primitives.create_box(origin, [w, h, wg_length])

                if type(wg_thickness) is str:
                    origin[0] = str(origin[0]) + "-" + wg_thickness
                    origin[1] = str(origin[1]) + "-" + wg_thickness
                else:
                    origin[0] -= wg_thickness
                    origin[1] -= wg_thickness

            elif wg_direction_axis == self._app.AXIS.Y:
                airbox = self.primitives.create_box(origin, [w, wg_length, h])

                if type(wg_thickness) is str:
                    origin[0] = str(origin[0]) + "-" + wg_thickness
                    origin[2] = str(origin[2]) + "-" + wg_thickness
                else:
                    origin[0] -= wg_thickness
                    origin[2] -= wg_thickness
            else:
                airbox = self.primitives.create_box(origin, [wg_length, w, h])

                if type(wg_thickness) is str:
                    origin[2] = str(origin[2]) + "-" + wg_thickness
                    origin[1] = str(origin[1]) + "-" + wg_thickness
                else:
                    origin[2] -= wg_thickness
                    origin[1] -= wg_thickness
            centers = [f.center for f in airbox.faces]
            posx = [i[wg_direction_axis] for i in centers]
            mini = posx.index(min(posx))
            maxi = posx.index(max(posx))
            if create_sheets_on_openings:
                p1 = self.primitives.create_object_from_face(airbox.faces[mini].id)
                p2 = self.primitives.create_object_from_face(airbox.faces[maxi].id)
            if not name:
                name = generate_unique_name(wgmodel)
            if wg_direction_axis == self._app.AXIS.Z:
                wgbox = self.primitives.create_box(origin, [wb, hb, wg_length], name=name)
            elif wg_direction_axis == self._app.AXIS.Y:
                wgbox = self.primitives.create_box(origin, [wb, wg_length, hb], name=name)
            else:
                wgbox = self.primitives.create_box(origin, [wg_length, wb, hb], name=name)
            self.subtract(wgbox, airbox, False)
            wgbox.material_name = wg_material

            return wgbox, p1, p2
        else:
            return None

    @aedt_exception_handler
    def edit_region_dimensions(self, listvalues):
        """Modify the dimensions of the region.

        Parameters
        ----------
        listvalues : list
            List of the padding percentages along all six directions in
            the form ``[+X, -X, +Y, -Y, +Z, -Z]``.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        References
        ----------

        >>> oEditor.ChangeProperty
        """
        arg = ["NAME:AllTabs"]
        arg2 = ["NAME:Geometry3DCmdTab", ["NAME:PropServers", "Region:CreateRegion:1"]]
        arg3 = ["NAME:ChangedProps"]
        p = ["+X", "-X", "+Y", "-Y", "+Z", "-Z"]
        for label, value in zip(p, listvalues):
            padding = []
            padding.append("NAME:" + label + " Padding Data")
            padding.append("Value:=")
            padding.append(str(value))
            arg3.append(padding)
        arg2.append(arg3)
        arg.append(arg2)
        self.oeditor.ChangeProperty(arg)
        return True

    @aedt_exception_handler
    def create_face_list(self, fl, name):
        """Create a list of faces given a list of face names.

        Parameters
        ----------
        fl : list
            List of face names.

        name : str
           Name of the new list.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        References
        ----------

        >>> oEditor.CreateEntityList
        """
        self.oeditor.CreateEntityList(
            ["NAME:GeometryEntityListParameters", "EntityType:=", "Face", "EntityList:=", fl],
            ["NAME:Attributes", "Name:=", name],
        )
        self.logger.info("Face List " + name + " created")
        return True

    @aedt_exception_handler
    def create_object_list(self, fl, name):
        """Create an object list given a list of object names.

        Parameters
        ----------
        fl : list
            List of object names.
        name : str
            Name of the new object list.

        Returns
        -------
        int
            ID of the new object list.

        References
        ----------

        >>> oEditor.CreateEntityList
        """
        listf = ",".join(fl)
        self.oeditor.CreateEntityList(
            ["NAME:GeometryEntityListParameters", "EntityType:=", "Object", "EntityList:=", listf],
            ["NAME:Attributes", "Name:=", name],
        )
        self.logger.info("Object List " + name + " created")

        return self.get_entitylist_id(name)

    @aedt_exception_handler
    def generate_object_history(self, objectname):
        """Generate history for the object.

        Parameters
        ----------
        objectname : str
            Name of the history object.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        References
        ----------

        >>> oEditor.GenerateHistory
        """
        objectname = self.convert_to_selections(objectname)
        self.oeditor.GenerateHistory(
            ["NAME:Selections", "Selections:=", objectname, "NewPartsModelFlag:=", "Model", "UseCurrentCS:=", True]
        )
        self.primitives.cleanup_objects()
        return True

    @aedt_exception_handler
    def create_faceted_bondwire_from_true_surface(self, bondname, bond_direction, min_size=0.2, numberofsegments=8):
        """Create a faceted bondwire from an existing true surface bondwire.

        Parameters
        ----------
        bondname : str
            Name of the bondwire to replace.
        bond_direction : list
            List of the ``[x, y, z]`` coordinates for the axis direction
            of the bondwire. For example, ``[0, 1, 2]``.
        min_size : float
            Minimum size of the subsegment of the new polyline. The default is ``0.2``.
        numberofsegments : int, optional
            Number of segments. The default is ``8``.

        Returns
        -------
        str
            Name of the bondwire created.
        """
        old_bondwire = self.primitives.get_object_from_name(bondname)
        if not old_bondwire:
            return False
        edges = old_bondwire.edges
        faces = old_bondwire.faces
        centers = []
        for el in faces:
            center = el.center
            if center:
                centers.append(center)
        edgelist = []
        verlist = []
        for el in edges:
            ver = el.vertices
            if len(ver) < 2:
                continue
            p1 = ver[0].position
            p2 = ver[1].position
            p3 = [abs(i - j) for i, j in zip(p1, p2)]

            dir = p3.index(max(p3))
            if dir == bond_direction:
                edgelist.append(el)
                verlist.append([p1, p2])
        if not edgelist:
            self.logger.error("No edges found specified direction. Check again")
            return False
        connected = [edgelist[0]]
        tol = 1e-6
        for edge in edgelist[1:]:
            ver = edge.vertices
            p1 = ver[0].position
            p2 = ver[1].position
            for el in connected:
                ver1 = el.vertices
                p3 = ver1[0].position
                p4 = ver1[1].position
                dist = GeometryOperators.points_distance(p1, p3)
                if dist < tol:
                    connected.append(edge)
                    break
                dist = GeometryOperators.points_distance(p1, p4)
                if dist < tol:
                    connected.append(edge)
                    break
                dist = GeometryOperators.points_distance(p2, p3)
                if dist < tol:
                    connected.append(edge)
                    break
                dist = GeometryOperators.points_distance(p2, p4)
                if dist < tol:
                    connected.append(edge)
                    break
        new_edges = []
        for edge in connected:
            edge_object = self.primitives.create_object_from_edge(edge)
            new_edges.append(edge_object)

        self.unite(new_edges)
        self.generate_object_history(new_edges[0])
        self.primitives.convert_segments_to_line(new_edges[0].name)

        edges = new_edges[0].edges
        i = 0
        edge_to_delete = []
        first_vert = None
        for edge in edges:
            ver = edge.vertices
            p1 = ver[0].position
            p2 = ver[1].position
            if not first_vert:
                first_vert = p1
            dist = GeometryOperators.points_distance(p1, p2)
            if dist < min_size:
                edge_to_delete.append(i)
            i += 1

        rad = 1e6
        move_vector = None
        for fc in centers:
            dist = GeometryOperators.points_distance(fc, first_vert)
            if dist < rad:
                rad = dist
                move_vector = GeometryOperators.v_sub(fc, first_vert)

        P = self.primitives.get_existing_polyline(object=new_edges[0])

        if edge_to_delete:
            P.remove_edges(edge_to_delete)

        angle = math.pi * (180 - 360 / numberofsegments) / 360

        status = P.set_crosssection_properties(
            type="Circle", num_seg=numberofsegments, width=(rad * (2 - math.sin(angle))) * 2
        )
        if status:
            self.translate(new_edges[0], move_vector)
            old_bondwire.model = False
            return new_edges[0]
        else:
            return False

    @aedt_exception_handler
    def get_entitylist_id(self, name):
        """Retrieve the ID of an entity list.

        Parameters
        ----------
        name : str
            Name of the entity list.

        Returns
        -------
        int
            ID of the entity list.

        References
        ----------

        >>> oEditor.GetEntityListIDByName
        """
        id = self.oeditor.GetEntityListIDByName(name)
        return id

    @aedt_exception_handler
    def create_outer_facelist(self, externalobjects, name="outer_faces"):
        """Create a face list from a list of outer objects.

        Parameters
        ----------
        externalobjects : list
            List of outer objects.
        name : str, optional
            Name of the new list. The default is ``"outer_faces"``.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        """
        list2 = self.select_allfaces_fromobjects(externalobjects)  # find ALL faces of outer objects
        self.create_face_list(list2, name)
        self.logger.info("Extfaces of thermal model = " + str(len(list2)))
        return True

    @aedt_exception_handler
    def explicitly_subtract(self, diellist, metallist):
        """Explicitly subtract all elements in a SolveInside list and a SolveSurface list.

        Parameters
        ----------
        diellist : list
            List of dielectrics.
        metallist : list
            List of metals.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        References
        ----------

        >>> oEditor.Subtract
        >>> oEditor.PurgeHistory
        """
        self.logger.info("Creating explicit subtraction between objects.")
        for el in diellist:
            list1 = el
            list2 = ""
            for el1 in metallist:
                list2 = list2 + el1 + ","
            for el1 in diellist:
                if el1 is not el:
                    list2 = list2 + el1 + ","
            if list2:
                list2 = list2[:-1]
                self.subtract(list1, list2, True)
                self.purge_history(list1)
                self.purge_history(list2)
        for el in metallist:
            list1 = el
            list2 = ""
            for el1 in metallist:
                if el1 is not el:
                    list2 = list2 + el1 + ","
            if list2:
                list2 = list2[:-1]
                self.subtract(list1, list2, True)
                self.purge_history(list1)
                self.purge_history(list2)
        self.logger.info("Explicit subtraction is completed.")
        return True

    @aedt_exception_handler
    def find_port_faces(self, objs):
        """Find the vaccums given a list of input sheets.

        Starting from a list of input sheets, this method creates a list of output sheets
        that represent the blank parts (vacuums) and the tool parts of all the intersections
        of solids on the sheets. After a vacuum on a sheet is found, a port can be
        created on it.

        Parameters
        ----------
        objs : list
            List of input sheets.

        Returns
        -------
        List
            List of output sheets (`2x len(objs)`).

        """
        faces = []
        id = 1
        for obj in objs:
            self.oeditor.Copy(["NAME:Selections", "Selections:=", obj])
            originals = self.primitives.object_names
            self.oeditor.Paste()
            self.primitives.refresh_all_ids()
            added = self.primitives.object_names
            cloned = [i for i in added if i not in originals]
            solids = self.primitives.get_all_solids_names()
            self.subtract(cloned[0], ",".join(solids))
            self.subtract(obj, cloned[0])
            air = self.primitives.get_obj_id(cloned[0])
            air.change_name(obj + "_Face1Vacuum")
            faces.append(obj)
            faces.append(obj + "_Face1Vacuum")
            id += 1
        return faces

    @aedt_exception_handler
    def load_objects_bytype(self, type):
        """Load all objects of a specified type.

        Parameters
        ----------
        type : str
            Type of the objects to load. Options are
            ``"Solids"`` and ``"Sheets"``.

        Returns
        -------
        list
            List of the object names for the specified type.

        References
        ----------

        >>> oEditor.GetObjectsInGroup
        """
        objNames = list(self.oeditor.GetObjectsInGroup(type))
        return objNames

    @aedt_exception_handler
    def get_line_ids(self):
        """Create a dictionary of object IDs for the lines in the design with the line name as the key."""
        line_ids = {}
        line_list = list(self.oeditor.GetObjectsInGroup("Lines"))
        for line_object in line_list:
            # TODO Problem with GetObjectIDByName
            try:
                line_ids[line_object] = str(self.oeditor.GetObjectIDByName(line_object))
            except:
                self.logger.warning("Line {} has an invalid ID!".format(line_object))
        return line_ids

    @aedt_exception_handler
    def get_bounding_dimension(self):
        """Retrieve the dimension array of the bounding box.

        Returns
        -------
        list
            List of six float values representing the bounding box
            in the form ``[min_x, min_y, min_z, max_x, max_y, max_z]``.

        References
        ----------

        >>> oEditor.GetModelBoundingBox
        """
        oBoundingBox = list(self.oeditor.GetModelBoundingBox())
        dimensions = []
        dimensions.append(abs(float(oBoundingBox[0]) - float(oBoundingBox[3])))
        dimensions.append(abs(float(oBoundingBox[1]) - float(oBoundingBox[4])))
        dimensions.append(abs(float(oBoundingBox[2]) - float(oBoundingBox[5])))
        return dimensions

    @aedt_exception_handler
    def get_object_name_from_edge_id(self, edge_id):
        """Retrieve the object name for a predefined edge ID.

        Parameters
        ----------
        edge_id : int
            ID of the edge.

        Returns
        -------
        str
            Name of the edge if it exists, ``False`` otherwise.

        References
        ----------

        >>> oEditor.GetEdgeIDsFromObject
        """
        for object in list(self.primitives.object_id_dict.keys()):
            try:
                oEdgeIDs = self.oeditor.GetEdgeIDsFromObject(object)
                if str(edge_id) in oEdgeIDs:
                    return object
            except:
                return False
        return False

    @aedt_exception_handler
    def get_solving_volume(self):
        """Generate a mesh for a setup.

        Returns
        -------
        int
            ``1`` when successful, ``0`` when failed.

        References
        ----------

        >>> oEditor.GetModelBoundingBox
        """
        bound = self.get_model_bounding_box()
        volume = abs(bound[3] - bound[0]) * abs(bound[4] - bound[1]) * abs(bound[5] - bound[2])
        volume = str(round(volume, 0))
        return volume

    @aedt_exception_handler
    def vertex_data_of_lines(self, txtfilter=None):
        """Generate a dictionary of line vertex data for all lines contained within the design.

        Parameters
        ----------
        txtfilter : str, optional
            Text string for filtering. The default is ``None``. When a text string is specified,
            line data is generated only if this text string is contained within the line name.

        Returns
        -------
        dict
            Dictionary of the line name with a list of vertex positions in either 2D or 3D.

        """
        line_data = {}
        lines = self.get_line_ids()
        if txtfilter is not None:
            lines = [n for n in lines if txtfilter in n]
        for x in lines:
            line_data[x] = self.get_vertices_of_line(x)

        return line_data

    @aedt_exception_handler
    def get_vertices_of_line(self, sLineName):
        """Generate a list of vertex positions for a line object from AEDT in model units.

        Parameters
        ----------
        sLineName : str
            Name of the line object in AEDT.

        Returns
        -------
        list
            List of the ``[x, y, (z)]`` coordinates for the 2D or 3D line object.

        References
        ----------

        >>> oEditor.GetVertexIDsFromObject
        """
        position_list = []

        # Get all vertices in the line
        vertices_on_line = self.oeditor.GetVertexIDsFromObject(sLineName)

        for x in vertices_on_line:
            pos = self.oeditor.GetVertexPosition(x)
            if self.design_type == "Maxwell 2D":
                if self.geometry_mode == "XY":
                    position_list.append([float(pos[0]), float(pos[1])])
                else:
                    position_list.append([float(pos[0]), float(pos[2])])
            else:
                position_list.append([float(pos[0]), float(pos[1]), float(pos[2])])

        return position_list

    @aedt_exception_handler
    def import_3d_cad(self, filename, healing=0, refresh_all_ids=True):
        """Import a CAD model.

        Parameters
        ----------
        filename : str
            Full path and name of the CAD file.
        healing : bool, optional
            Whether to perform healing. The default is ``0``, in which
            case healing is not performed.
        refresh_all_ids : bool, optional
            Whether to refresh all IDs after the CAD file is loaded. The
            default is ``True``. Refreshing IDs can take a lot of time in
            a big project.

        Returns
        -------
         bool
            ``True`` when successful, ``False`` when failed.

        References
        ----------

        >>> oEditor.Import
        """
        vArg1 = ["NAME:NativeBodyParameters"]
        vArg1.append("HealOption:="), vArg1.append(healing)
        vArg1.append("Options:="), vArg1.append("-1")
        vArg1.append("FileType:="), vArg1.append("UnRecognized")
        vArg1.append("MaxStitchTol:="), vArg1.append(-1)
        vArg1.append("ImportFreeSurfaces:="), vArg1.append(False)
        vArg1.append("GroupByAssembly:="), vArg1.append(False)
        vArg1.append("CreateGroup:="), vArg1.append(True)
        vArg1.append("STLFileUnit:="), vArg1.append(self.model_units)
        vArg1.append("MergeFacesAngle:="), vArg1.append(-1)
        vArg1.append("PointCoincidenceTol:="), vArg1.append(1e-06)
        vArg1.append("CreateLightweightPart:="), vArg1.append(False)
        vArg1.append("ImportMaterialNames:="), vArg1.append(False)
        vArg1.append("SeparateDisjointLumps:="), vArg1.append(False)
        vArg1.append("SourceFile:="), vArg1.append(filename)
        self.oeditor.Import(vArg1)
        if refresh_all_ids:
            self.primitives.refresh_all_ids()
        self.logger.info("Step file {} imported".format(filename))
        return True

    @aedt_exception_handler
    def import_spaceclaim_document(self, SCFile):
        """Import a SpaceClaim document.

        Parameters
        ----------
        SCFile :
            Full path and name of the SpaceClaim file.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        References
        ----------

        >>> oEditor.CreateUserDefinedModel
        """
        environlist = os.environ
        latestversion = ""
        for l in environlist:
            if "AWP_ROOT" in l:
                if l > latestversion:
                    latestversion = l
        if not latestversion:
            self.logger.error("SpaceClaim is not found.")
        else:
            scdm_path = os.path.join(os.environ[latestversion], "scdm")
        self.oeditor.CreateUserDefinedModel(
            [
                "NAME:UserDefinedModelParameters",
                [
                    "NAME:Definition",
                    [
                        "NAME:UDMParam",
                        "Name:=",
                        "GeometryFilePath",
                        "Value:=",
                        '"' + SCFile + '"',
                        "DataType:=",
                        "String",
                        "PropType2:=",
                        0,
                        "PropFlag2:=",
                        1,
                    ],
                    [
                        "NAME:UDMParam",
                        "Name:=",
                        "IsSpaceClaimLinkUDM",
                        "Value:=",
                        "1",
                        "DataType:=",
                        "Int",
                        "PropType2:=",
                        5,
                        "PropFlag2:=",
                        8,
                    ],
                ],
                [
                    "NAME:Options",
                    [
                        "NAME:UDMParam",
                        "Name:=",
                        "Solid Bodies",
                        "Value:=",
                        "1",
                        "DataType:=",
                        "Int",
                        "PropType2:=",
                        5,
                        "PropFlag2:=",
                        0,
                    ],
                    [
                        "NAME:UDMParam",
                        "Name:=",
                        "Surface Bodies",
                        "Value:=",
                        "1",
                        "DataType:=",
                        "Int",
                        "PropType2:=",
                        5,
                        "PropFlag2:=",
                        0,
                    ],
                    [
                        "NAME:UDMParam",
                        "Name:=",
                        "Parameters",
                        "Value:=",
                        "1",
                        "DataType:=",
                        "Int",
                        "PropType2:=",
                        5,
                        "PropFlag2:=",
                        0,
                    ],
                    [
                        "NAME:UDMParam",
                        "Name:=",
                        "Parameter Key",
                        "Value:=",
                        '""',
                        "DataType:=",
                        "String",
                        "PropType2:=",
                        0,
                        "PropFlag2:=",
                        0,
                    ],
                    [
                        "NAME:UDMParam",
                        "Name:=",
                        "Named Selections",
                        "Value:=",
                        "1",
                        "DataType:=",
                        "Int",
                        "PropType2:=",
                        5,
                        "PropFlag2:=",
                        8,
                    ],
                    [
                        "NAME:UDMParam",
                        "Name:=",
                        "Rendering Attributes",
                        "Value:=",
                        "1",
                        "DataType:=",
                        "Int",
                        "PropType2:=",
                        5,
                        "PropFlag2:=",
                        0,
                    ],
                    [
                        "NAME:UDMParam",
                        "Name:=",
                        "Material Assignment",
                        "Value:=",
                        "1",
                        "DataType:=",
                        "Int",
                        "PropType2:=",
                        5,
                        "PropFlag2:=",
                        0,
                    ],
                    [
                        "NAME:UDMParam",
                        "Name:=",
                        "Import suppressed for physics objects",
                        "Value:=",
                        "0",
                        "DataType:=",
                        "Int",
                        "PropType2:=",
                        5,
                        "PropFlag2:=",
                        0,
                    ],
                    [
                        "NAME:UDMParam",
                        "Name:=",
                        "Explode Multi-Body Parts",
                        "Value:=",
                        "1",
                        "DataType:=",
                        "Int",
                        "PropType2:=",
                        5,
                        "PropFlag2:=",
                        8,
                    ],
                    [
                        "NAME:UDMParam",
                        "Name:=",
                        "SpaceClaim Installation Path",
                        "Value:=",
                        '"' + scdm_path + '"',
                        "DataType:=",
                        "String",
                        "PropType2:=",
                        0,
                        "PropFlag2:=",
                        8,
                    ],
                    [
                        "NAME:UDMParam",
                        "Name:=",
                        "Smart CAD Update",
                        "Value:=",
                        "1",
                        "DataType:=",
                        "Int",
                        "PropType2:=",
                        5,
                        "PropFlag2:=",
                        8,
                    ],
                ],
                ["NAME:GeometryParams"],
                "DllName:=",
                "SCIntegUDM",
                "Library:=",
                "installLib",
                "Version:=",
                "2.0",
                "ConnectionID:=",
                "",
            ]
        )
        self.primitives.refresh_all_ids()
        return True

    @aedt_exception_handler
    def modeler_variable(self, value):
        """Modeler variable.

        Parameters
        ----------
        value :


        Returns
        -------

        """
        if isinstance(value, str if _pythonver >= 3 else basestring):
            return value
        else:
            return str(value) + self.model_units

    @aedt_exception_handler
    def break_spaceclaim_connection(self):
        """Break the connection with SpaceClaim.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        References
        ----------

        >>> oEditor.BreakUDMConnection
        """
        args = ["NAME:Selections", "Selections:=", "SpaceClaim1"]
        self.oeditor.BreakUDMConnection(args)
        return True

    @aedt_exception_handler
    def load_scdm_in_hfss(self, SpaceClaimFile):
        """Load a SpaceClaim file in HFSS.

        Parameters
        ----------
        SpaceClaimFile : str
            Full path and name of the SpaceClaim file.


        Returns
        -------
         bool
            ``True`` when successful, ``False`` when failed.

        References
        ----------

        >>> oEditor.CreateUserDefinedModel
        >>> oEditor.BreakUDMConnection
        """
        self.import_spaceclaim_document(SpaceClaimFile)
        self.break_spaceclaim_connection()
        return True

    @aedt_exception_handler
    def load_hfss(self, cadfile):
        """Load HFSS.

        Parameters
        ----------
        cadfile : str
            Name of the CAD file to load in HFSS.


        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        References
        ----------

        >>> oEditor.Import
        """
        self.import_3d_cad(cadfile, 1)
        return True

    @aedt_exception_handler
    def get_faces_from_materials(self, mats):
        """Select all outer faces given a list of materials.

        Parameters
        ----------
        mats : list
            List of materials to include in the search for outer
            faces.

        Returns
        -------
        list
            List of all outer faces of the specified materials.

        References
        ----------

        >>> oEditor.GetObjectsByMaterial
        >>> oEditor.GetFaceIDs
        """
        self.logger.info("Selecting outer faces.")

        sel = []
        if type(mats) is str:
            mats = [mats]
        for mat in mats:
            objs = list(self.oeditor.GetObjectsByMaterial(mat))
            objs.extend(list(self.oeditor.GetObjectsByMaterial(mat.lower())))

            for i in objs:

                oFaceIDs = self.oeditor.GetFaceIDs(i)

                for facce in oFaceIDs:
                    sel.append(int(facce))
        return sel

    @aedt_exception_handler
    def select_allfaces_fromobjects(self, elements):
        """Select all outer faces given a list of objects.

        Parameters
        ----------
        elements : list
            List of objects to include in the search for outer faces.

        Returns
        -------
        list
            List of outer faces in the given list of objects.

        References
        ----------

        >>> oEditor.GetFaceIDs
        """
        self.logger.info("Selecting outer faces.")

        sel = []

        for i in elements:

            oFaceIDs = self.oeditor.GetFaceIDs(i)

            for facce in oFaceIDs:
                sel.append(int(facce))
        return sel

    @aedt_exception_handler
    def setunassigned_mats(self):
        """Find unassagned objects and set them to non-model.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        References
        ----------

        >>> oEditor.SetPropertyValue
        """
        oObjects = list(self.oeditor.GetObjectsInGroup("Solids"))
        for obj in oObjects:
            pro = self.oeditor.GetPropertyValue("Geometry3DAttributeTab", obj, "Material")
            if pro == '""':
                self.oeditor.SetPropertyValue("Geometry3DAttributeTab", obj, "Model", False)
        return True

    @aedt_exception_handler
    def automatic_thicken_sheets(self, inputlist, value, internalExtr=True, internalvalue=1):
        """Create thickened sheets for a list of input faces.

        This method automatically checks the direction in which to thicken the sheets.

        Parameters
        ----------
        inputlist : list
            List of faces.
        value : float
            Value in millimeters to thicken the sheets.
        internalExtr : bool, optional
            Whether to extrude sheets internally. The default is ``True``.
        internalvalue : float, optional
            Value in millimeters to thicken the sheets internally (vgoing into the model).
            The default is ``1``.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        References
        ----------

        >>> oEditor.ThickenSheet
        """
        aedt_bounding_box = self.get_model_bounding_box()
        directions = {}
        inputlist = self.convert_to_selections(inputlist, True)
        for el in inputlist:
            objID = self.oeditor.GetFaceIDs(el)
            faceCenter = self.oeditor.GetFaceCenter(int(objID[0]))
            directionfound = False
            l = 10
            while not directionfound:
                self.oeditor.ThickenSheet(
                    ["NAME:Selections", "Selections:=", el, "NewPartsModelFlag:=", "Model"],
                    ["NAME:SheetThickenParameters", "Thickness:=", str(l) + "mm", "BothSides:=", False],
                )
                aedt_bounding_box2 = self.get_model_bounding_box()
                self._odesign.Undo()
                if aedt_bounding_box != aedt_bounding_box2:
                    directions[el] = "External"
                    directionfound = True
                self.oeditor.ThickenSheet(
                    ["NAME:Selections", "Selections:=", el, "NewPartsModelFlag:=", "Model"],
                    ["NAME:SheetThickenParameters", "Thickness:=", "-" + str(l) + "mm", "BothSides:=", False],
                )
                aedt_bounding_box2 = self.get_model_bounding_box()

                self._odesign.Undo()

                if aedt_bounding_box != aedt_bounding_box2:
                    directions[el] = "Internal"
                    directionfound = True
                else:
                    l = l + 10
        for el in inputlist:
            objID = self.oeditor.GetFaceIDs(el)
            faceCenter = self.oeditor.GetFaceCenter(int(objID[0]))
            if directions[el] == "Internal":
                self.oeditor.ThickenSheet(
                    ["NAME:Selections", "Selections:=", el, "NewPartsModelFlag:=", "Model"],
                    ["NAME:SheetThickenParameters", "Thickness:=", "-" + str(value) + "mm", "BothSides:=", False],
                )
            else:
                self.oeditor.ThickenSheet(
                    ["NAME:Selections", "Selections:=", el, "NewPartsModelFlag:=", "Model"],
                    ["NAME:SheetThickenParameters", "Thickness:=", str(value) + "mm", "BothSides:=", False],
                )
            if internalExtr:
                objID2 = self.oeditor.GetFaceIDs(el)
                for fid in objID2:
                    try:
                        faceCenter2 = self.oeditor.GetFaceCenter(int(fid))
                        if faceCenter2 == faceCenter:
                            self.oeditor.MoveFaces(
                                ["NAME:Selections", "Selections:=", el, "NewPartsModelFlag:=", "Model"],
                                [
                                    "NAME:Parameters",
                                    [
                                        "NAME:MoveFacesParameters",
                                        "MoveAlongNormalFlag:=",
                                        True,
                                        "OffsetDistance:=",
                                        str(internalvalue) + "mm",
                                        "MoveVectorX:=",
                                        "0mm",
                                        "MoveVectorY:=",
                                        "0mm",
                                        "MoveVectorZ:=",
                                        "0mm",
                                        "FacesToMove:=",
                                        [int(fid)],
                                    ],
                                ],
                            )
                    except:
                        self.logger.info("done")
                        # self.modeler_oproject.ClearMessages()
        return True

    def __get__(self, instance, owner):
        self._app = instance
        return self

    class Position:
        """Position.

        Parameters
        ----------
        args : list or int
            Position of the item as either a list of the ``[x, y, z]`` coordinates
            or three separate values. If no or insufficient arguments
            are specified, ``0`` is applied.

        """

        @aedt_exception_handler
        def __getitem__(self, item):
            if item == 0:
                return self.X
            elif item == 1:
                return self.Y
            elif item == 2:
                return self.Z

        @aedt_exception_handler
        def __setitem__(self, item, value):
            if item == 0:
                self.X = value
            elif item == 1:
                self.Y = value
            elif item == 2:
                self.Z = value

        def __iter__(self):
            return self

        def __len__(self):
            return 3

        def __init__(self, *args):
            if len(args) == 1 and type(args[0]) is list:
                try:
                    self.X = args[0][0]
                except:
                    self.X = 0
                try:
                    self.Y = args[0][1]
                except:
                    self.Y = 0
                try:
                    self.Z = args[0][2]
                except:
                    self.Z = 0
            else:
                try:
                    self.X = args[0]
                except:
                    self.X = 0
                try:
                    self.Y = args[1]
                except:
                    self.Y = 0
                try:
                    self.Z = args[2]
                except:
                    self.Z = 0

    class SweepOptions(object):
        """Manages sweep options.

        Parameters
        ----------
        draftType : str, optional
            Type of the draft. Options are ``"Round"``, ``"Natural"``,
            and ``"Extended"``. The default is ``"Round"``.
        draftAngle : str, optional
            Draft angle with units. The default is ``"0deg"``.
        twistAngle : str, optional
            Twist angle with units. The default is ``"0deg"``.

        """

        @aedt_exception_handler
        def __init__(self, draftType="Round", draftAngle="0deg", twistAngle="0deg"):
            self.DraftType = draftType
            self.DraftAngle = draftAngle
            self.TwistAngle = twistAngle

    @aedt_exception_handler
    def create_group(self, objects=None, components=None, groups=None, group_name=None):
        """Group objects or groups into one group.

        At least one between ``objects``, ``components``, ``groups`` has to be defined.

        Parameters
        ----------
        objects : list, optional
            List of objects. The default is ``None``, in which case a group
            with all objects is created.
        components : list, optional
            List of 3d components to group. The default is ``None``.
        groups : list, optional
            List of groups. The default is ``None``.
        group_name : str, optional
            Name of the new group. The default is ``None``.
            It is not possible to choose the name but a name is
            assigned automatically.

        Returns
        -------
        str
           Name assigned to the new group.

        References
        ----------

        >>> oEditor.CreateGroup
        """
        if components is None and groups is None and objects is None:
            raise AttributeError("At least one between ``objects``, ``components``, ``groups`` has to be defined.")

        all_objects = self.primitives.object_names
        if objects:
            object_selection = self.convert_to_selections(objects, return_list=False)
        else:
            object_selection = ""
        if groups:
            group_selection = self.convert_to_selections(groups, return_list=False)
        else:
            group_selection = ""
        if components:
            component_selection = self.convert_to_selections(components, return_list=False)
        else:
            component_selection = ""

        arg = [
            "NAME:GroupParameter",
            "ParentGroupID:=",
            "Model",
            "Parts:=",
            object_selection,
            "SubmodelInstances:=",
            component_selection,
            "Groups:=",
            group_selection,
        ]
        assigned_name = self.oeditor.CreateGroup(arg)
        if group_name and group_name not in all_objects:
            self.oeditor.ChangeProperty(
                [
                    "NAME:AllTabs",
                    [
                        "NAME:Attributes",
                        ["NAME:PropServers", assigned_name],
                        ["NAME:ChangedProps", ["NAME:Name", "Value:=", group_name]],
                    ],
                ]
            )
            return group_name
        else:
            return assigned_name

    @aedt_exception_handler
    def ungroup(self, groups):
        """Ungroup one or more groups.

        Parameters
        ----------
        groups : list
            List of group names.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        References
        ----------

        >>> oEditor.Ungroup
        """
        group_list = self.convert_to_selections(groups, return_list=True)
        arg = ["Groups:=", group_list]
        self.oeditor.Ungroup(arg)
        return True

    @aedt_exception_handler
    def flatten_assembly(self):
        """Flatten the assembly, removing all group trees.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        References
        ----------

        >>> oEditor.FlattenGroup
        """
        self.oeditor.FlattenGroup(["Groups:=", ["Model"]])
        return True
