import os

from ..generic.DataHandlers import json_to_dict
from ..generic.filesystem import get_json_files
from ..generic.general_methods import aedt_exception_handler
from .GeometryOperators import GeometryOperators


def read_actors(fn, actor_lib):
    """
    Read and map actors in fn to a list of actor objects.

    Parameters
    ----------
    fn: str, required
        JSON file describing actors
    actor_lib: str, required
        Full path to the library containing the actors definitions.

    :return: list of Actor
        List of actor objects
    """
    a = {}
    actor_dict = json_to_dict(fn)
    for name in actor_dict:
        a[name] = Actor(actor_dict[name], actor_lib, name)
    return a


class Part(object):
    """
    Class to help manage 3d components. Component placement and definition.
    """

    # List of known keys for a Part and default values:
    allowed_keys = {
        "comp_name": None,  # *.a3dcomp file name
        "offset": None,
        "rotation_cs": None,
        "rotation": 0.0,
        "compensation_angle": None,
        "rotation_axis": "Z",
        "tire_radius": None,
        "duplicate_number": None,
        "duplicate_vector": None,
        "antenna_type": None,  # Antenna only
        "mode": None,  # Antenna only
        "aedt_name": None,
        "beamwidth_elevation": None,  # Antenna only
        "beamwidth_azimuth": None,  # Antenna only
        "polarization": None,
    }  # Antenna only

    def __init__(self, part_folder, part_dict, parent=None, name=None):
        """

        Parameters
        ----------
        part_folder : str, required
            Folder where *.a3dcomp files is located
        part_dict : dict, required
             Defines relevant properties of the class with the following keywords:
             'comp_name': str,  *.a3dcomp file name
             'offset': list or str, Offset coordinate system definition relative to parent.
             'rotation_cs': list or str, Rotation coordinate system relative to parent.
             'rotation': str or numeric, Rotation angle
             'compensation_angle': str or numeric, initial angle
             'rotation_axis': char, "X", "Y" or "Z. Rotation axis
             'duplicate_number': str or int, Number of instances for linear duplication.
             'duplicate_vector': list, Vector for duplication relative to parent CS

        name : str, required
            name of the 3d comp file without extension.

        """
        # Default values:
        self._compdef = dict()
        self._parent = parent

        # Extract the 3d component name and part folder
        # from the file name.
        # Use this as the default value for comp_name.  Ensure that the correct extension is used.
        self._compdef["part_folder"] = part_folder
        for k in Part.allowed_keys:
            if k in part_dict:
                self._compdef[k] = part_dict[k]
            else:
                self._compdef[k] = Part.allowed_keys[k]

        self._motion = False
        if parent:  # Inherit _motion directly from parent.
            self._motion = self._parent.motion

        # make sure self._name is unique if it is not passed as an argument.
        if name:
            self._name = name  # Part name should be unique. No checking here.
        elif "name" in part_dict:
            self._name = part_dict["name"]
        else:
            self._name = "radar"  # TODO: Need to fix this!

        # Update self._compdef from the library definition in the *.json file.

        for kw, val in part_dict.items():
            if kw in self._compdef:
                self._compdef[kw] = val
            else:
                raise KeyError("Key " + kw + " not allowed.")

        # Instantiate yaw, pitch and roll.  Might want to change
        # how this is handled. Make "rotation" a list instead of
        # using .yaw, .pitch, .roll properties?
        self.rot_axis = [False, False, False]  # [X, Y, Z] rotation Boolean
        if self._compdef["rotation_axis"]:
            a = self._compdef["rotation"]
            if self._compdef["rotation_axis"].lower() == "x":  # roll
                [y, p, r] = ["0", "0", a]
                self.rot_axis[2] = True
            elif self._compdef["rotation_axis"].lower() == "y":  # pitch
                [y, p, r] = ["0", a, "0"]
                self.rot_axis[1] = True
            elif self._compdef["rotation_axis"].lower() == "z":  # yaw
                [y, p, r] = [a, "0", "0"]
                self.rot_axis[0] = True
            else:
                [y, p, r] = ["0", "0", "0"]  # Exception? invalid value for 'rotation_axis'.
            if not self._compdef["rotation"]:  # rotation may be None. Catch this:
                self._compdef["rotation"] = ["0", "0", "0"]
            self._yaw = y
            self._pitch = p
            self._roll = r
        else:
            self._yaw = "0"
            self._pitch = "0"
            self._roll = "0"

    def __setitem__(self, key, value):
        self._compdef[key] = value

    def __getitem__(self, key):
        if key == "rotation_cs":
            cs = self._compdef[key]
            if cs == "Global" or cs is None:
                self._compdef[key] = ["0", "0", "0"]
            else:
                self._compdef[key] = [str(i) if not i is str else i for i in cs]
        return self._compdef[key]

    @aedt_exception_handler
    def zero_offset(self, kw):  # Returns True if cs at kw is at [0, 0, 0]
        """Return zero if the coordinate system defined by kw is [0, 0, 0].

        Parameters
        ----------
        kw : str, required
             'offset' or 'rotation_cs'

        Returns
        -------
        True if the coordinate system is [0, 0, 0] or None

        """
        if kw in ["offset", "rotation_cs"]:
            s = []
            if self[kw]:
                s = [GeometryOperators.is_small(c) for c in self[kw]]
            if len(s) > 0:
                return all(s)
            else:
                return True
        return False

    @property
    def file_name(self):
        """Antenna File Name.

        Returns
        -------
        str
            full file name for *.a3dcomp file.
        """
        return os.path.join(self._compdef["part_folder"], self["comp_name"])

    # Create a unique coordinate system name for the part.
    @property
    def cs_name(self):
        """Coordinate System Name.

        Returns
        -------
        str
        """
        if self._motion or not self.zero_offset("offset") or not self.zero_offset("rotation_cs"):
            return self.name + "_cs"
        else:
            return self._parent.cs_name

    # Define the variable names for angles in the app:
    @property
    def yaw_name(self):
        """Yaw Name.

        Returns
        -------
        str
        """
        return self.name + "_yaw"

    @property
    def pitch_name(self):
        """Pitch Name.

        Returns
        -------
        str
        """
        return self.name + "_pitch"

    @property
    def roll_name(self):
        """Roll Name.

        Returns
        -------
        str
        """
        return self.name + "_roll"

    # Always return the local origin as a list:
    @property
    def local_origin(self):
        """Local Part Offset.

        Returns
        -------
        list
        """
        if self["offset"]:
            if self.zero_offset("offset") or self["offset"] == "Global":
                return [0, 0, 0]
            else:
                if self._parent._local_units:
                    units = self._parent._local_units
                else:
                    units = self._parent.modeler_units
                offset = [str(i) + units for i in self["offset"]]

                return offset
        else:
            return [0, 0, 0]

    @property
    def rotate_origin(self):
        """Origin Rotation Liste.

        Returns
        -------
        list
        """
        if self["rotation_cs"]:
            if self.zero_offset("rotation_cs") or self["rotation_cs"] == "Global":
                return self.local_origin()
            else:
                return self["rotation_cs"]
        else:
            return [0, 0, 0]

    @property
    def _do_rotate(self):  # True if any rotation angles are non-zero or 'rotation_cs' is defined.
        return any(self.rot_axis)

    @property
    def _do_offset(self):  # True if any rotation angles are non-zero.
        return any(GeometryOperators.numeric_cs(self.local_origin))

    # Allow expressions should be valid angle as either string
    # or numerical value.
    @property
    def yaw(self):
        """Yaw Value.

        Returns
        -------
        str
        """
        return self._yaw

    @yaw.setter
    def yaw(self, yaw):
        self._yaw = yaw

    @property
    def pitch(self):
        """Pitch Value.

        Returns
        -------
        str
        """
        return self._pitch

    @pitch.setter
    def pitch(self, pitch):
        self._pitch = pitch

    @property
    def roll(self):
        """Roll Value.

        Returns
        -------
        str
        """
        return self._roll

    @roll.setter
    def roll(self, roll):
        self._roll = roll

    @property
    def name(self):
        """Part Name.

        Returns
        -------
        str
        """
        return self._parent.name + "_" + self._name

    @aedt_exception_handler
    def set_relative_cs(self, app):
        """Create a new, parametric Coordinate System.

        Returns
        -------
        bool
        """
        # Set x,y,z offset variables in app. But check first to see if the CS
        # has already been defined.
        if self.cs_name not in app.modeler.oeditor.GetCoordinateSystems() and self.cs_name != "Global":
            x_pointing = [1, 0, 0]
            y_pointing = [0, 1, 0]
            app.modeler.create_coordinate_system(
                origin=self.local_origin,
                x_pointing=x_pointing,
                y_pointing=y_pointing,
                reference_cs=self._parent.cs_name,
                mode="axis",
                name=self.cs_name,
            )
        return True

    @property
    def rot_cs_name(self):
        """Rotation Coordinate System Name.

        Returns
        -------
        str
        """
        return self.name + "_rot_cs"

    @aedt_exception_handler
    def do_rotate(self, app, aedt_object):
        """
        Set the rotation coordinate system relative to the parent CS.
        This function should only be called if
        there is rotation in the component. The rotation cs is offset from
        the parent CS.

        Parameters
        ----------
        app : pyaedt.Hfss
            Instance of the Ansys AEDT application.

        aedt_object : str
            Name of the design in AEDT.

        """

        x_pointing = [1, 0, 0]
        y_pointing = [0, 1, 0]
        app.modeler.create_coordinate_system(
            origin=self.rotate_origin,
            x_pointing=x_pointing,
            y_pointing=y_pointing,
            reference_cs=self._parent.cs_name,
            mode="axis",
            name=self.rot_cs_name,
        )
        if self.rot_axis[0]:
            app[self.yaw_name] = self.yaw
            app.modeler.rotate(aedt_object, "Z", angle=self.yaw_name)
        if self.rot_axis[1]:
            app[self.pitch_name] = self.pitch
            app.modeler.rotate(aedt_object, "Y", angle=self.pitch_name)
        if self.rot_axis[2]:
            app[self.roll_name] = self.roll
            app.modeler.rotate(aedt_object, "X", angle=self.roll_name)

        return True

    @aedt_exception_handler
    def insert(self, app):
        """Insert 3D Component into app.

        Parameters
        ----------
        app : class:`pyaedt.hfss.Hfss`
            HFSS application instance.

        Returns
        -------
        name of inserted object.
        """
        aedt_objects = []
        # TODO: Why the inconsistent syntax for cs commands?
        if self._do_offset:
            self.set_relative_cs(app)  # Create coordinate system, if needed.
            aedt_objects.append(app.modeler.primitives.insert_3d_component(self.file_name, targetCS=self.cs_name))
        else:
            aedt_objects.append(
                app.modeler.primitives.insert_3d_component(self.file_name, targetCS=self._parent.cs_name)
            )
        if self._do_rotate:
            self.do_rotate(app, aedt_objects[0])

        # Duplication occurs in parent coordinate system.
        app.modeler.set_working_coordinate_system(self._parent.cs_name)
        if self["duplicate_vector"]:
            d_vect = [float(i) for i in self["duplicate_vector"]]
            duplicate_result = app.modeler.duplicate_along_line(
                aedt_objects[0], d_vect, nclones=int(self["duplicate_number"]), is_3d_comp=True
            )
            if duplicate_result[0]:
                for d in duplicate_result[1]:
                    aedt_objects.append(d)
        return aedt_objects


class MultiPartComponent(object):
    """
    Class to support multi-part 3d components for Electronics
    Desktop - SBR+.
    """

    _component_classes = ["environment", "rcs_standard", "vehicle", "person", "bike", "bird", "radar"]

    # Keep track of all assigned names to the class.  Use the
    # properties '.name' and '.index' to ensure unique instance names.
    _names = []
    # for c in _component_classes:
    #     _count[c] = 0

    # Initialization variables and values for the app using
    # the MultiPartComponent
    _t = "time_var"
    _t_value = "0s"
    modeler_units = "meter"

    @staticmethod
    def start(app):
        """Initialize app for SBR+ Simulation.

        Parameters
        ----------
        app : class:`pyaedt.Hfss`
            Application instance.

        Returns
        -------
        bool
            True on success
        """
        app[MultiPartComponent._t] = MultiPartComponent._t_value
        app.modeler.model_units = "meter"  # Set units.

        return True

    def __init__(
        self,
        comp_folder,
        name=None,
        use_relative_cs=False,
        relative_cs_name=None,
        motion=False,
        offset=("0", "0", "0"),
        yaw="0deg",
        pitch="0deg",
        roll="0deg",
    ):
        """
        MultiPartComponent class. Forward motion is in the x-direction (if motion is set)

        Parameters
        ----------

        comp_folder : str, required
            Folder where the component definition resides.
            This folder must contain a *.json file with the
            same name as the folder.
        use_relative_cs : Bool, optional
            Default: False
            Set to True if this component should use
            a relative Coordinate System. This is
            necessary if the component moves relative to the global
            CS. Set to False if the multi-part component doesn't move.
        relative_cs_name : str, optional
            Default: None
            Set to a specific name on which the multipart relative system will be connected.
        motion : Bool, optional
            Set to true if expressions should be used to define the
            position and orientation of the MultiPartComponent.
            Default value is False
        name : str, optional
            Name of the multipart component. If this value is set, the
            component will be selected from the corresponding json file in
            comp_folder. Default=None (read name from the first .json file
            found in comp_folder.
        offset : list, optional
            List of [x,y,z] defining the component offset.
            Default is ["0", "0", "0"]
        yaw : str or float, optional
            Yaw angle. Rotation about the component z-axis
        pitch: str or float, optional
            Pitch angle. Rotation about the component y-axis
        roll: str or float, optional
            Roll angle. Rotation about the component x-axis.

        """

        self.comp_folder = comp_folder  # Folder where the component is defined.
        # self._name = os.path.split(comp_folder)[-1]  # Base name of multipart component.
        self._index = None  # Counter used to assign unique name.
        self._yaw = yaw  # Yaw is the rotation about the z-axis
        self._pitch = pitch  # Pitch is tilt toward the sky (i.e. rotation about y)
        self._roll = roll  # Roll is rotation about the x-axis (x is the direction of movement)
        self._relative_cs_name = relative_cs_name
        if relative_cs_name:
            self._reference_cs_name = relative_cs_name
        else:
            self._reference_cs_name = "Global"

        # If the component moves, then expressions must be used for position and orientation
        self.motion = motion

        self.aedt_components = []  # List of components

        # Find the json file that defines this part.
        json_files = get_json_files(self.comp_folder)
        if name:
            self._name = name  # Define name from the passed parameter.
            f = None
            for fn in json_files:
                if os.path.split(fn)[1].split(".")[0] == name:
                    f = fn
        else:
            f = json_files[0]
            self._name = os.path.split(f)[1].split(".")[0]  # Define name from the json file name.

        compdef = json_to_dict(f)  # dict defining the 3d component

        if "class" in compdef.keys():
            self._component_class = compdef["class"]
        elif self._component_class:  # already defined by subclass. Do nothing.
            pass
        else:
            self._component_class = None

        #  Allow for different units in the multipart component. For example with radar.
        if "units" in compdef.keys():
            self._local_units = compdef["units"]
        else:
            self._local_units = None  # Default to global units.

        # Used to offset the multipart component.
        # These are the variable names in HFSS.
        # self.name is a unique name (see the @property definition for name)
        xyz = ["x", "y", "z"]
        self._offset_var_names = [self.name + "_" + s for s in xyz]

        # Instantiate parts with the Part class.
        self.parts = {}
        if "parts" in compdef.keys():
            for pn, part_def in compdef["parts"].items():
                self.parts[pn] = Part(self.comp_folder, part_def, parent=self, name=pn)
        if "antennas" in compdef.keys():
            for a, a_def in compdef["antennas"].items():
                self.parts[a] = Antenna(self.comp_folder, a_def, parent=self, name=a)

        self.use_relative_cs = use_relative_cs
        if use_relative_cs:
            self._use_global_cs = False
            self._offset_values = list(offset)

        else:
            self._use_global_cs = True
            self._offset_values = list(offset)

    @property
    def cs_name(self):
        """Coordinate System Name.

        Returns
        -------
        str
        """
        if self.use_global_cs:
            self._relative_cs_name = "Global"
        elif not self._relative_cs_name:
            self._relative_cs_name = self.name + "_cs"
        return self._relative_cs_name

    @property
    def index(self):
        """Track number of self._name using MultiPartComponent._names.

        Returns
        -------
        int
        """
        if self._index is None:  # Only increment one time.
            self._index = MultiPartComponent._names.count(self._name)
            MultiPartComponent._names.append(self._name)
        return self._index

    # The following read-only properties are used to
    # set the x,y,z offset variable name for this
    # multi-part 3d component instance in the app.
    @property
    def offset_x_name(self):
        """X Axis Offset Name.

        Returns
        -------
        str
        """
        return self._offset_var_names[0]

    @property
    def offset_y_name(self):
        """Y Axis Offset Name.

        Returns
        -------
        str
        """
        return self._offset_var_names[1]

    @property
    def offset_z_name(self):
        """Z Axis Offset Name.

        Returns
        -------
        str
        """
        return self._offset_var_names[2]

    @property
    def offset_names(self):
        """X, Y, Z Axis Offset Name.

        Returns
        -------
        list
        """
        return [self.offset_x_name, self.offset_y_name, self.offset_z_name]

    @property
    def yaw_name(self):
        """Yaw variable name.

        Returns
        -------
        str
        """
        return self.name + "_yaw"

    @property
    def yaw(self):
        """Yaw variable value.

        Returns
        -------
        str
        """
        return self._yaw

    @yaw.setter
    def yaw(self, yaw_str):
        # TODO: Need variable checking for yaw angle.
        # yaw is the rotation about the object z-axis.
        self._use_global_cs = False
        self._yaw = yaw_str

    @property
    # This is the name of the variable for pitch in the app.
    def pitch_name(self):
        """Pitch variable name.

        Returns
        -------
        str
        """
        return self.name + "_pitch"

    @property
    def pitch(self):
        """Pitch variable value.

        Returns
        -------
        str
        """
        return self._pitch

    @pitch.setter
    def pitch(self, pitch_str):
        # TODO: Need variable checking for pitch angle.
        # pitch is the rotation about the object y-axis.
        self._use_global_cs = False
        self._pitch = pitch_str

    @property
    # This is the name of the variable for roll in the app.
    def roll_name(self):
        """Roll variable name.

        Returns
        -------
        str
        """
        return self.name + "_roll"

    @property
    def roll(self):
        """Roll variable value.

        Returns
        -------
        str
        """
        return self._roll

    @roll.setter
    def roll(self, roll_str):
        # TODO: Need variable checking for pitch angle.
        # roll is the rotation about the object x-axis.
        self._use_global_cs = False
        self._roll = roll_str

    @property
    def _cs_pointing(self):
        if self.motion:  # Pass expressions to the app variable.
            yaw_str = self.yaw_name
            pitch_str = self.pitch_name
            roll_str = self.roll_name
        else:  # Pass values to the app variable.
            yaw_str = self.yaw
            pitch_str = self.pitch
            roll_str = self.roll

        return GeometryOperators.cs_xy_pointing_expression(yaw_str, pitch_str, roll_str)

    @property
    def name(self):
        """Unique instance name.

        Returns
        -------
        str
        """
        suffix = "_" + str(self.index)
        return self._name + suffix  # unique instance name

    @property
    def use_global_cs(self):
        """Use Global CS.

        Returns
        -------
        bool
        """
        return self._use_global_cs

    @property
    def offset(self):
        """Offset for Multipart.

        Returns
        -------
        list
        """
        return self._offset_values

    @offset.setter
    def offset(self, o):
        # TODO: Add check for validity
        self._use_global_cs = False
        self._offset_values = o  # Expect tuple or list of strings

    @aedt_exception_handler
    def position_in_app(self, app):
        """
        Set up design variables and values to enable motion for
        the multi-part 3d component in the application.

        Parameters
        ----------
        app : pyaedt.Hfss, required
            Application instance.

        Returns
        -------
        Coordinate system.
        """
        if self.motion:
            xyz = ["x", "y", "z"]
            for m in range(3):
                # app[self.offset_names[m]] = self.offset[m]
                app.variable_manager.set_variable(
                    variable_name=self.offset_names[m],
                    expression=self.offset[m],
                    description=self.name + " " + xyz[m] + "-position",
                )

            app.variable_manager.set_variable(
                variable_name=self.yaw_name, expression=self.yaw, description=self.name + " yaw"
            )

            app.variable_manager.set_variable(
                variable_name=self.pitch_name, expression=self.pitch, description=self.name + " pitch"
            )

            app.variable_manager.set_variable(
                variable_name=self.roll_name, expression=self.roll, description=self.name + " roll"
            )

            cs_origin = self.offset_names
        else:
            cs_origin = self.offset
        if self.use_relative_cs:
            return app.modeler.create_coordinate_system(
                origin=cs_origin,
                reference_cs=self._reference_cs_name,
                x_pointing=self._cs_pointing[0],
                y_pointing=self._cs_pointing[1],
                mode="axis",
                name=self.cs_name,
            )

    @aedt_exception_handler
    def _insert(self, app, motion=False):
        """Insert the multipart 3d component.

        Parameters
        ----------
        app : :class:`pyaedt.hfss.Hfss`
            Application where Mutipart3DComponent will be inserted.
        motion : Bool, optional
            Set to true if variables should be created in the
            app to set position, yaw, pitch, roll

        Returns
        -------
        bool
        """
        self.motion = True if motion else self.motion

        if self.use_global_cs or self.cs_name in app.modeler.oeditor.GetCoordinateSystems():
            app.modeler.set_working_coordinate_system(self.cs_name)
            if self.use_relative_cs:
                self._relative_cs_name = self.name + "_cs"
        self.position_in_app(app)

        for p in self.parts:
            inserted = self.parts[p].insert(app)  # index ensures unique CS names.
            if len(inserted) > 0:
                for i in inserted:
                    self.aedt_components.append(i)
        app.modeler.create_group(components=self.aedt_components, group_name=self.name)
        return True

    @aedt_exception_handler
    def insert(self, app, motion=False):
        """Insert object into App.

        Returns
        -------
        bool
        """
        return self._insert(app, motion=motion)


class Environment(MultiPartComponent, object):
    """
    Environment class is derived from MultiPartComponent.
    The call signature is identical to the parent class except
    motion is always False.
    """

    def __init__(self, env_folder, relative_cs_name=None):
        super(Environment, self).__init__(env_folder, motion=False)

    @property
    def cs_name(self):
        """Coordinate System Name.

        Returns
        -------
        str
        """
        return "Global"

    @property
    def yaw(self):
        """Yaw variable value.

        Returns
        -------
        str
        """
        return self._yaw

    @yaw.setter
    def yaw(self, yaw_str):
        # TODO: Need variable checking for yaw angle.
        self._yaw = yaw_str

    @property
    def pitch(self):
        """Pitch variable value.

        Returns
        -------
        str
        """
        return self._pitch

    @pitch.setter
    def pitch(self, pitch_str):
        self._pitch = pitch_str

    @property
    def roll(self):
        """Roll variable value.

        Returns
        -------
        str
        """
        return self._roll

    @roll.setter
    def roll(self, roll_str):
        # TODO: Need variable checking for pitch angle.
        # roll is the rotation about the object x-axis.
        self._roll = roll_str

    @property
    def offset(self):
        """Offset for Multipart.

        Returns
        -------
        list
        """
        return self._offset_values

    @offset.setter
    def offset(self, o):
        self._offset_values = o  # Expect tuple or list of strings


class Actor(MultiPartComponent, object):
    """One instance of an actor. Derived class from MultiPartComponent."""

    def __init__(self, actor_folder, speed="0", relative_cs_name=None):
        """
        Actor class
            Derived from MultiPartComponent.
            Note: Forward motion is always forward in the +x-direction.

        Parameters
        ----------
        actor_folder : str, required
            Folder pointing to the folder containing the definition
            of the Person.  This can be changed later in the Person class
            definition.
        speed : float or str
            Speed of the person in the x-direction.
        relative_cs_name : str
            Relative CS Name of the actor. ``None`` for Global CS.
        """

        super(Actor, self).__init__(actor_folder, use_relative_cs=True, motion=True, relative_cs_name=relative_cs_name)

        self._speed_expression = str(speed) + "m_per_sec"  # TODO: Need error checking here.

    @property
    def speed_name(self):
        """Speed Name.

        Returns
        -------
        str
        """
        return self.name + "_speed"

    @property
    def speed_expression(self):
        """Speed Expression.

        Returns
        -------
        str
        """
        return self._speed_expression

    @speed_expression.setter
    def speed_expression(self, s):  # TODO: Add validation of the expression.
        self._speed_expression = s

    @aedt_exception_handler
    def _add_speed(self, app):
        app.variable_manager.set_variable(
            variable_name=self.speed_name, expression=self.speed_expression, description="object speed"
        )
        # Update expressions for x and y position in app:
        app[self.offset_names[0]] = (
            str(self.offset[0]) + "+" + self.speed_name + " * " + MultiPartComponent._t + "* cos(" + self.yaw_name + ")"
        )

        app[self.offset_names[1]] = (
            str(self.offset[1]) + "+" + self.speed_name + " * " + MultiPartComponent._t + "* sin(" + self.yaw_name + ")"
        )


class Person(Actor, object):
    """
    One instance of an actor. Derived class from MultiPartComponent.
    """

    def __init__(self, actor_folder, speed="0", stride="0.8meters", relative_cs_name=None):
        """Person class, derived from Actor.

         .. note::  Motion is always forward in the x-direction of the Person coordinate system.

        Parameters
        ----------
        actor_folder : str, required
            Folder pointing to the folder containing the definition
            of the Person.  This can be changed later in the Person class
            definition.
                speed : float or str
            Speed of the person in the x-direction.
        stride: float or str
            Stride length of the person. Default = "0.8meters"
        relative_cs_name : str
            Relative CS Name of the actor. ``None`` for Global CS.

        """

        super(Person, self).__init__(actor_folder, speed=speed, relative_cs_name=relative_cs_name)

        self._stride = stride

    @property
    def stride(self):
        """Stride in meters.

        Returns
        -------
        str
        """
        return self._stride

    @stride.setter
    def stride(self, s):
        self._stride = s  # TODO: Add validation to allow expressions.

    @aedt_exception_handler
    def _add_walking(self, app):
        # Update expressions for oscillation of limbs. At this point
        # we could parse p.name to handle motion (arm, leg, ...).
        for k, p in self.parts.items():
            if any(p.rot_axis):  # use this key to determine if there is motion of the part.
                if p.rot_axis[1]:  # Make sure pitch rotation is True
                    app[p.pitch_name] = (
                        p.pitch
                        + "*sin(2*pi*("
                        + self.speed_name
                        + "/"
                        + self.stride
                        + ") "
                        + "*"
                        + MultiPartComponent._t
                        + ") + "
                        + "("
                        + p["compensation_angle"]
                        + ")rad"
                    )

    @aedt_exception_handler
    def insert(self, app, motion=True):
        """Insert the Person into the AEDT app.

        Parameters
        ----------
        app : :class:`pyaedt.hfss.Hfss`
        motion : bool

        Returns
        -------
        bool
        """
        app.add_info_message("Adding Person: " + self.name, "Design")

        # Insert the component first, then set variables.
        self._insert(app)  # Place the Person in the app.
        if motion:
            self._add_speed(app)
            self._add_walking(app)


class Bird(Actor, object):
    """One instance of an actor. Derived class from MultiPartComponent."""

    def __init__(self, bird_folder, speed="2.0", flapping_rate="50Hz", relative_cs_name=None):
        """
        Bike class
            Derived from MultiPartComponent.
            Note: Motion is always forward in the x-direction.

        Parameters
        ----------
        speed : float or str
            Speed of the vehicle.
        relative_cs_name : str
            Relative CS Name of the actor. ``None`` for Global CS.

        """

        super(Bird, self).__init__(bird_folder, speed=speed, relative_cs_name=relative_cs_name)
        self._flapping_rate = flapping_rate

    def _add_flying(self, app):
        # Update expressions for wheel motion:

        for k, p in self.parts.items():
            if any(p.rot_axis):  # use this key to verify that there is local motion.
                if p.rot_axis[2]:  # Flapping is roll
                    app[p.roll_name] = (
                        p["rotation"] + "* sin(2*pi*" + str(self._flapping_rate) + "*" + MultiPartComponent._t + ")"
                    )

    @aedt_exception_handler
    def insert(self, app, motion=True):
        """Insert the Bird into the AEDT app.

        Parameters
        ----------
        app : :class:`pyaedt.hfss.Hfss`
        motion : bool

        Returns
        -------
        bool
        """
        app.add_info_message("Adding Vehicle: " + self.name, "Design")

        self._insert(app)  # Place the multipart component in the app.
        if motion:
            self._add_speed(app)
            self._add_flying(app)


class Vehicle(Actor, object):
    """One instance of an actor. Derived class from MultiPartComponent."""

    def __init__(self, car_folder, speed=10.0, relative_cs_name=None):
        """
        Vehicle class
            Derived from MultiPartComponent.
            Note: Motion is always forward in the x-direction.

        Properties
        ----------
        speed : float or str
            Speed of the vehicle.
        relative_cs_name : str
            Relative CS Name of the actor. ``None`` for Global CS.
        """

        super(Vehicle, self).__init__(car_folder, speed=speed, relative_cs_name=relative_cs_name)

    @aedt_exception_handler
    def _add_driving(self, app):
        # Update expressions for wheel motion:
        for k, p in self.parts.items():
            if any(p.rot_axis):  # use this key to determine if there is motion of the wheel.
                if p.rot_axis[1]:  # Make sure pitch rotation is True
                    app[p.pitch_name] = (
                        "("
                        + MultiPartComponent._t
                        + "*"
                        + self.speed_name
                        + "/"
                        + p["tire_radius"]
                        + "meter)*(180/pi)*1deg"
                    )

    @aedt_exception_handler
    def insert(self, app, motion=True):
        """Insert the Vehicle into the AEDT app.

        Parameters
        ----------
        app : :class:`pyaedt.hfss.Hfss`
        motion : bool

        Returns
        -------
        bool
        """
        app.add_info_message("Adding Vehicle: " + self.name, "Design")

        self._insert(app)  # Place the multipart component in the app.
        if motion:
            self._add_speed(app)
            self._add_driving(app)
        return True


class Antenna(Part, object):
    """Antenna class derived from Part."""

    def __init__(self, root_folder, ant_dict, parent=None, name=None):
        super(Antenna, self).__init__(root_folder, ant_dict, parent=parent, name=name)

    def _antenna_type(self, app):
        if self._compdef["antenna_type"] == "parametric":
            return app.SbrAntennas.ParametricBeam

    @property
    def params(self):
        """Multipart Parameters.

        Returns
        -------
        dict
        """
        p = {}
        if self._compdef["antenna_type"] == "parametric":
            p["Vertical BeamWidth"] = self._compdef["beamwidth_elevation"]
            p["Horizontal BeamWidth"] = self._compdef["beamwidth_azimuth"]
            p["Polarization"] = self._compdef["polarization"]
        return p

    @aedt_exception_handler
    def _insert(self, app, target_cs=None, units=None):
        if not target_cs:
            target_cs = self._parent.cs_name
        if not units:
            if self._parent._local_units:
                units = self._parent._local_units
            else:
                units = self._parent.units
        a = app.create_sbr_antenna(
            self._antenna_type(app),
            model_units=units,
            parameters_dict=self.params,
            target_cs=target_cs,
            antenna_name=self.name,
        )
        return a

    @aedt_exception_handler
    def insert(self, app, units=None):
        """Insert antenna into app.

        Parameters
        ----------
        app : :class:`pyaedt.hfss.Hfss`, required HFSS application instance.

        Returns
        -------
        name of inserted object.
        """

        if self._do_offset:
            self.set_relative_cs(app)
            antenna_object = self._insert(app, units=units)  # Create coordinate system, if needed.
        else:
            antenna_object = self._insert(app, target_cs=self._parent.cs_name, units=units)
        if self._do_rotate:
            self.do_rotate(app, antenna_object.name)

        return antenna_object


class Radar(MultiPartComponent, object):
    """
    Radar class manages the radar definition and placement in the HFSS design.

    """

    def __init__(
        self,
        radar_folder,
        name=None,
        motion=False,
        use_relative_cs=False,
        offset=("0", "0", "0"),
        speed=0,
        relative_cs_name=None,
    ):

        self.aedt_antenna_names = []  # List of Antenna Names
        name = name.split(".")[0] if name else name  # remove suffix if any
        self._component_class = "radar"
        super(Radar, self).__init__(
            radar_folder,
            name=name,
            use_relative_cs=use_relative_cs,
            motion=motion,
            offset=offset,
            relative_cs_name=relative_cs_name,
        )
        self._speed_expression = str(speed) + "m_per_sec"
        self.pair = []

    @property
    def units(self):
        """Multipart Units.

        Returns
        -------
        str
        """
        return self._local_units

    @property
    def speed_name(self):
        """Speed Variable Name.

        Returns
        -------
        str
        """
        return self.name + "_speed"

    @property
    def speed_expression(self):
        """Speed Variable Expression.

        Returns
        -------
        str
        """
        return self._speed_expression

    @speed_expression.setter
    def speed_expression(self, s):
        self._speed_expression = s

    @aedt_exception_handler
    def _add_speed(self, app):
        app.variable_manager.set_variable(
            variable_name=self.speed_name, expression=self.speed_expression, description="radar speed"
        )
        # Update expressions for x and y position in app:
        app[self.offset_names[0]] = (
            str(self.offset[0]) + "+" + self.speed_name + " * " + MultiPartComponent._t + "* cos(" + self.yaw_name + ")"
        )

        app[self.offset_names[1]] = (
            str(self.offset[1]) + "+" + self.speed_name + " * " + MultiPartComponent._t + "* sin(" + self.yaw_name + ")"
        )

    @aedt_exception_handler
    def insert(self, app, motion=False):
        """Insert radar into app (app is the HFSS application instance).

        Parameters
        ----------
        app: class: `pyaedt.hfss.Hfss`

        Returns
        -------
        list
            list of Antenna Placed.
        """
        app.add_info_message("Adding Radar Module:  " + self.name)
        if self.use_global_cs or self.cs_name in app.modeler.oeditor.GetCoordinateSystems():
            app.modeler.set_working_coordinate_system(self.cs_name)
            if self.use_relative_cs:
                self._relative_cs_name = self.name + "_cs"
        self.position_in_app(app)
        tx_names = []
        rx_names = []
        for p in self.parts:
            antenna_object = self.parts[p].insert(app, units=self._local_units)
            self.aedt_components.append(antenna_object.antennaname)
            self.aedt_antenna_names.append(antenna_object.excitation_name)
            if p.startswith("tx"):
                tx_names.append(antenna_object.excitation_name)
            elif p.startswith("rx"):
                rx_names.append(antenna_object.excitation_name)

        # Define tx/rx pairs:
        self.pair = {}
        for tx in tx_names:
            rx_string = ""
            for rx in rx_names:
                rx_string += rx + ","
            self.pair[tx] = rx_string.strip(",")

        app.set_sbr_txrx_settings(self.pair)

        app.modeler.create_group(components=self.aedt_components, group_name=self.name)
        app.add_info_message("Group Created:  " + self.name)
        if motion:
            self._add_speed(app)
        return self.aedt_antenna_names
