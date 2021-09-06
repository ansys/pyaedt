import json
from glob import glob
import os
import math
import sys
from pyaedt.generic.general_methods import aedt_exception_handler


def get_numeric(s):  # TODO: add validation
    """ Convert a string to a numeric value. Discard the suffix."""
    if type(s) == str:
        if s == 'Global':
            return 0.0
        else:
            return float(''.join(c for c in s if c.isdigit() or c == '.'))
    elif s is None:
        return 0.0
    else:
        return float(s)


def get_suffix(s):
    return ''.join(c for c in s if not (c.isdigit() or c == '.'))

def get_duplicated_object_names(start_name, n):
    """
    This function is a workaround for the duplicate_along_line method in hfss.modeler
    which returns only the names of objects (and sheets) inside the 3D component after
    duplication. There is no way to get the names of the objects in the group.

    Parameters
    ----------
    start_name : str, required
        Name of the object. Should end with a numeric index.
    n : int , required
        Number of repetitions.

    Returns
    -------
    list of object names
    """
    suffix = ''
    base_name_reverse = ''
    done = False
    for c in start_name[::-1]:
        if c.isdigit() and not done:
            suffix = c + suffix
        elif not c.isdigit() and not done:
            done = True
            base_name_reverse += c
        else:
            base_name_reverse += c
    base_name = base_name_reverse[::-1]
    names = []
    if len(suffix) > 0:
        d = int(suffix)  # Need to again reverse order
        for m in range(n-1):
            names.append(base_name + str(m+d+1))
    return names


def is_small(s):
    """
    Return True if the number represented by s is zero (i.e very small).

    Parameters
    ----------
    s, numeric or str
        Variable value.

    Returns
    -------

    """
    n = get_numeric(s)
    return True if math.fabs(n) < 2.0 * abs(sys.float_info.epsilon) else False


def numeric_cs(cs_in):
    """
    Return a list of [x,y,z] numeric values
    given a coordinate system as input:

    cs_in could be a list of strings, ["x", "y", "z"]
    or "Global"
    """

    # TODO: Improve error handling and conversion robustness.
    if type(cs_in) is str:
        if cs_in == "Global":
            return [0.0, 0.0, 0.0]
        else:
            return None
    elif type(cs_in) is list:
        if len(cs_in) == 3:
            return [get_numeric(s) if type(s) is str else s for s in cs_in]
        else:
            return [0, 0, 0]


def json_to_dict(fn):
    with open(fn) as json_file:
        try:
            data = json.load(json_file)
        except Exception as e:
            print("Error: ", e.__class__)
            raise e

        # Print the type of data variable
    return data


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


def get_json_files(start_folder):
    """
    Get the absolute path to all *.json files in start_folder.

    Parameters
    ----------
    start_folder, str
        Path to the folder where the json files are located.

    Returns
    -------
    """
    return [y for x in os.walk(start_folder) for y in glob(os.path.join(x[0], '*.json'))]


def read_environment_lib(env_lib):
    """
    Read an environment library.

    Parameters
    ----------
    env_lib : str, required
        Full name of the environment library path.
    """
    try:
        env_files = get_json_files(env_lib)  # Get all json files in the library and read
        # data into a dict()
        environments = {}  # List of environment objects
        for fn in env_files:
            e = Environment(fn)
            environments[e.instance_name] = e
    except FileNotFoundError as fn_error:
        raise fn_error
    return environments


def cs_xy_pointing_expression(yaw, pitch, roll):
    """
    return x_pointing and y_pointing vectors as expressions from
    the yaw, ptich, and roll input (as strings).

    Parameters
    ----------
    yaw : str, required
        String expression for the yaw angle (rotation about Z-axis)
    pitch : str
        String expression for the pitch angle (rotation about Y-axis)
    roll : str
        String expression for the roll angle (rotation about X-axis)

    Returns
    -------
    [x_pointing, y_pointing] vector expressions.
    """
    # X-Pointing
    xx = "cos(" + yaw + ")*cos(" + pitch + ")"
    xy = "sin(" + yaw + ")*cos(" + pitch + ")"
    xz = "sin(" + pitch + ")"

    # Y-Pointing
    yx = "sin(" + roll + ")*sin(" + pitch + ")*cos(" + yaw + ") - "
    yx += "sin(" + yaw + ")*cos(" + roll + ")"

    yy = "sin(" + roll + ")*sin(" + yaw + ")*sin(" + pitch + ") + "
    yy += "cos(" + roll + ")*cos(" + yaw + ")"

    yz = "sin(" + roll + " + pi)*cos(" + pitch + ")"  # use pi to avoid negative sign.

    # x, y pointing vectors for CS
    x_pointing = [xx, xy, xz]
    y_pointing = [yx, yy, yz]

    return [x_pointing, y_pointing]


def cs_xy_pointing_value(yaw, pitch, roll):
    """
    return x_pointing and y_pointing vectors as expressions from
    the yaw, ptich, and roll input (as strings).

    Parameters
    ----------
    yaw : str or float, required
        String expression for the yaw angle (rotation about Z-axis)
    pitch : str or float, required
        String expression for the pitch angle (rotation about Y-axis)
    roll : str or float, required
        String expression for the roll angle (rotation about X-axis)

    Returns
    -------
    [x_pointing, y_pointing] vector expressions.
    """
    ang = [yaw, pitch, roll]
    angles = []

    # TODO: This needs improved input validation.
    # Convert angle values to float:
    for v in ang:
        if type(v) == str:
            if v.strip().endswith("deg"):
                angles.append(float(v.strip().strip("deg")) * math.pi / 180.0)
            else:
                angles.append(float(v))
        else:
            angles.append(float(v))
    [yaw, pitch, roll] = angles

    # X-Pointing
    xx = math.cos(yaw) * math.cos(pitch)
    xy = math.sin(yaw) * math.cos(pitch)
    xz = math.sin(pitch)

    # Y-Pointing
    yx = math.sin(roll) * math.sin(pitch) * math.cos(yaw) - math.sin(yaw) * math.cos(roll)

    yy = math.sin(roll) * math.sin(yaw) * math.sin(pitch) + math.cos(roll) * math.cos(yaw)

    yz = -math.sin(roll) * math.cos(pitch)

    # x, y pointing vectors for CS
    x_pointing = [xx, xy, xz]
    y_pointing = [yx, yy, yz]

    return [x_pointing, y_pointing]


class Part(object):
    """
    Class to help manage 3d components. Component placement and definition.
    """

    # List of known keys for a Part and default values:
    allowed_keys = {'comp_name': None,  # *.a3dcomp file name
                     'offset': None,
                     'rotation_cs': None,
                     'rotation': 0.0,
                     'compensation_angle': None,
                     'rotation_axis': 'Z',
                     'tire_radius': None,
                     'duplicate_number': None,
                     'duplicate_vector': None,
                     'antenna_type': None,  # Antenna only
                     'mode': None,  # Antenna only
                     'aedt_name': None,
                     'beamwidth_elevation': None,  # Antenna only
                     'beamwidth_azimuth': None,  # Antenna only
                     'polarization': None}  # Antenna only

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
        # TODO: Add exception handling
        # Default values:
        self._compdef = dict()
        self._parent = parent

        # Extract the 3d component name and part folder
        # from the file name.
        # Use this as the default value for comp_name.  Ensure that the correct extension is used.
        # self._compdef['comp_name'] = part_dict['comp_name'].split('.')[0] + '.a3dcomp'
        self._compdef['part_folder'] = part_folder
        for k in Part.allowed_keys:
            if k in part_dict:
                self._compdef[k] = part_dict[k]
            else:
                self._compdef[k] = Part.allowed_keys[k]
        #self._compdef['rotation_cs'] = None
        #self._compdef['rotation'] = 0.0
        #self._compdef['rotation_axis'] = "Z"
        #self._compdef['offset'] = None
        #self._compdef['compensation_angle'] = None
        #self._compdef['tire_radius'] = None
        #self._compdef['duplicate_number'] = None
        #self._compdef['duplicate_vector'] = None
        #self._compdef['aedt_name'] = None

        if parent:  # Inherit _motion directly from parent.
            self._motion = self._parent.motion
        else:
            self._motion = False  # Default is static part.

        # make sure self._name is unique if it is not passed as an argument.
        if name:
            self._name = name  # Part name should be unique. No checking here.
        elif 'name' in part_dict:
            self._name = part_dict['name']
        else:
            self._name = 'radar'  # TODO: Need to fix this!

        # Update self._compdef from the library definition in the *.json file.

        for kw, val in part_dict.items():
            if kw in self._compdef:
                self._compdef[kw] = val
            else:
                raise KeyError('Key ' + kw + ' not allowed.')

        # Instantiate yaw, pitch and roll.  Might want to change
        # how this is handled. Make "rotation" a list instead of
        # using .yaw, .pitch, .roll properties?
        self.rot_axis = [False, False, False]  # [X, Y, Z] rotation Boolean
        if self._compdef['rotation_axis']:
            a = self._compdef['rotation']
            if self._compdef['rotation_axis'].lower() == 'x':  # roll
                [y, p, r] = ["0", "0", a]
                self.rot_axis[2] = True
            elif self._compdef['rotation_axis'].lower() == 'y':  # pitch
                [y, p, r] = ["0", a, "0"]
                self.rot_axis[1] = True
            elif self._compdef['rotation_axis'].lower() == 'z':  # yaw
                [y, p, r] = [a, "0", "0"]
                self.rot_axis[0] = True
            else:
                [y, p, r] = ["0", "0", "0"]  # Exception? invalid value for 'rotation_axis'.
            if not self._compdef['rotation']:  # rotation may be None. Catch this:
                self._compdef['rotation'] = ["0", "0", "0"]
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
        if key == 'rotation_cs':
            cs = self._compdef[key]
            if cs == "Global" or cs is None:
                self._compdef[key] = ["0", "0", "0"]
            else:
                self._compdef[key] = [str(i) if not i is str else i for i in cs]
        return self._compdef[key]

    def zero_offset(self, kw):  # Returns True if cs at kw is at [0, 0, 0]
        """
        Return zero if the coordinate system defined by kw is [0, 0, 0]

        Parameters
        ----------
        kw : str, required
             'offset' or 'rotation_cs'

        Returns
        -------
        True if the coordinate system is [0, 0, 0] or None

        """
        if kw in ['offset', 'rotation_cs']:
            s = []
            if self[kw]:
                s = [is_small(c) for c in self[kw]]
            if len(s) > 0:
                return all(s)
            else:
                return True
        else:
            return False

    @property
    def file_name(self):
        """

        Returns
        -------
        str, full file name for *.a3dcomp file.

        """
        return os.path.join(self._compdef['part_folder'], self['comp_name'])

    # Create a unique coordinate system name for the part.
    @property
    def cs_name(self):
        if self._motion or not self.zero_offset('offset') or not self.zero_offset('rotation_cs'):
            return self.name + '_cs'
        else:
            return self._parent.cs_name

    # Define the variable names for angles in the app:
    @property
    def yaw_name(self):
        return self.name + '_yaw'

    @property
    def pitch_name(self):
        return self.name + '_pitch'

    @property
    def roll_name(self):
        return self.name + '_roll'

    # Always return the local origin as a list:
    @property
    def local_origin(self):
        if self['offset']:
            if self.zero_offset('offset') or self['offset'] == 'Global':
                return [0, 0, 0]
            else:
                return self['offset']
        else:
            return [0, 0, 0]

    @property
    def rotate_origin(self):
        if self['rotation_cs']:
            if self.zero_offset('rotation_cs') or self['rotation_cs'] == 'Global':
                return self.local_origin()
            else:
                return self['rotation_cs']
        else:
            return [0, 0, 0]

    @property
    def _do_rotate(self):  # True if any rotation angles are non-zero or 'rotation_cs' is defined.
        return any(self.rot_axis)
        # return any(numeric_cs([self._yaw, self._pitch, self._roll])) or not self.zero_offset('rotation_cs')

    @property
    def _do_offset(self):  # True if any rotation angles are non-zero.
        return any(numeric_cs(self.local_origin))

    # Allow expressions should be valid angle as either string
    # or numerical value.
    @property
    def yaw(self):
        return self._yaw

    @yaw.setter
    def yaw(self, yaw):
        self._yaw = yaw

    @property
    def pitch(self):
        return self._pitch

    @pitch.setter
    def pitch(self, pitch):
        self._pitch = pitch

    @property
    def roll(self):
        return self._roll

    @roll.setter
    def roll(self, roll):
        self._roll = roll

    @property
    def name(self):
        return self._parent.name + '_' + self._name

    def set_relative_cs(self, app):

        # Set x,y,z offset variables in app. But check first to see if the CS
        # has already been defined.
        if self.cs_name not in app.modeler.oeditor.GetCoordinateSystems() and self.cs_name != "Global":
            x_pointing = [1, 0, 0]
            y_pointing = [0, 1, 0]
            app.modeler.create_coordinate_system(origin=self.local_origin,
                                                 x_pointing=x_pointing,
                                                 y_pointing=y_pointing,
                                                 reference_cs=self._parent.cs_name,
                                                 mode="axis",
                                                 name=self.cs_name)
        return True

    @property
    def rot_cs_name(self):
        return self.name + '_rot_cs'

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
        app.modeler.create_coordinate_system(origin=self.rotate_origin,
                                             x_pointing=x_pointing,
                                             y_pointing=y_pointing,
                                             reference_cs=self._parent.cs_name,
                                             mode="axis",
                                             name=self.rot_cs_name)
        if self.rot_axis[0]:
            app[self.yaw_name] = self.yaw
            app.modeler.rotate(aedt_object, 'Z', angle=self.yaw_name)
        if self.rot_axis[1]:
            app[self.pitch_name] = self.pitch
            app.modeler.rotate(aedt_object, 'Y', angle=self.pitch_name)
        if self.rot_axis[2]:
            app[self.roll_name] = self.roll
            app.modeler.rotate(aedt_object, 'X', angle=self.roll_name)

        return True

    def insert(self, app, verbose=False):
        """
        Insert 3D Component into app
        Parameters
        ----------
        app : pyaedt.Hfss, required
            HFSS application instance.

        Returns
        -------
        name of inserted object.

        """
        aedt_objects = []
        # TODO: Why the inconsistent syntax for cs commands?
        if self._do_offset:
            self.set_relative_cs(app)  # Create coordinate system, if needed.
            aedt_objects.append(app.modeler.primitives.insert_3d_component(self.file_name,
                                                                     targetCS=self.cs_name))
        else:
            aedt_objects.append(app.modeler.primitives.insert_3d_component(self.file_name,
                                                                     targetCS=self._parent.cs_name))
        if self._do_rotate:
            self.do_rotate(app, aedt_objects[0])

        # Duplication occurs in parent coordinate system.
        app.modeler.set_working_coordinate_system(self._parent.cs_name)
        if self['duplicate_vector']:  # TODO: There is a bug in oeditor.DuplicateAlongLine. Doesn't return correct values.
            d_vect = [float(i) for i in self['duplicate_vector']]
            duplicate_result = app.modeler.duplicate_along_line(aedt_objects[0],
                                                           d_vect,
                                                           nclones=int(self['duplicate_number']), is_3d_comp=True)
            if duplicate_result[0]:
                # dup_objects = duplicate_result[1]
                # dup_objects = get_duplicated_object_names(aedt_objects[0], int(self['duplicate_number']))
                # for d in dup_objects:
                #     aedt_objects.append(d)
                for d in duplicate_result[1]:
                    aedt_objects.append(d)
        return aedt_objects


class MultiPartComponent(object):
    """
    Class to support multi-part 3d components for Electronics
    Desktop - SBR+.
    """
    _component_classes = ['environment',
                          'rcs_standard',
                          'vehicle',
                          'person',
                          'bike',
                          'bird',
                          'radar']

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
    # @aedt_exception_handler #  TODO: Get help catching errors.
    def start(app):
        """
        Initialize app for SBR+ Simulation
        Parameters
        ----------
        app : pyaedt.Hfss, required
            Application instance.

        Returns
        -------
        True on success
        """
        app[MultiPartComponent._t] = MultiPartComponent._t_value
        app.modeler.model_units = "meter"  # Set units.

        return True

    def __init__(self, comp_folder, name=None, use_relative_cs=False, motion=False,
                  offset=("0", "0", "0"), yaw="0deg", pitch="0deg", roll="0deg"):
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

        # If the component moves, then expressions must be used for position and orientation
        self.motion = motion

        self.aedt_components = []  # List of components

        # Find the json file that defines this part.
        json_files = get_json_files(self.comp_folder)
        if name:
            self._name = name  # Define name from the passed parameter.
            f = None
            for fn in json_files:
                if os.path.split(fn)[1].split('.')[0] == name:
                    f = fn
        else:
            f = json_files[0]
            self._name = os.path.split(f)[1].split('.')[0]  # Define name from the json file name.

        compdef = json_to_dict(f)  # dict defining the 3d component

        if 'class' in compdef.keys():
            self._component_class = compdef['class']
        elif self._component_class:  # already defined by subclass. Do nothing.
            pass
        else:
            self._component_class = None

        #  Allow for different units in the multipart component. For example with radar.
        if 'units' in compdef.keys():
            self._local_units = compdef['units']
        else:
            self._local_units = None  # Default to global units.

        #self.index = MultiPartComponent._count[self._component_class]

        # Used to offset the multipart component.
        # These are the variable names in HFSS.
        # self.name is a unique name (see the @property definition for name)
        xyz = ['x', 'y', 'z']
        self._offset_var_names = [self.name + '_' + s for s in xyz]

        # Instantiate parts with the Part class.
        self.parts = {}
        if 'parts' in compdef.keys():
            for pn, part_def in compdef['parts'].items():
                self.parts[pn] = Part(self.comp_folder, part_def, parent=self, name=pn)
        if 'antennas' in compdef.keys():
            for a, a_def in compdef['antennas'].items():
                self.parts[a] = Antenna(self.comp_folder, a_def, parent=self, name=a)

        if use_relative_cs:
            self._use_global_cs = False
            self._offset_values = list(offset)

        else:
            self._use_global_cs = True
            self._offset_values = list(offset)

    @property
    def cs_name(self):
        if self.use_global_cs:
            return "Global"
        else:
            return self.name + '_cs'  # name is uniquely indexed so cs will be unique

    @property
    def index(self):  # Track number of self._name using MultiPartComponent._names
        if self._index is None:  # Only increment one time.
            self._index = MultiPartComponent._names.count(self._name)
            MultiPartComponent._names.append(self._name)
        return self._index

#    @index.setter
#    def index(self, i):
#        self._index = i
#        MultiPartComponent._count[self._component_class] += 1  # Increment class index

    # The following read-only properties are used to
    # set the x,y,z offset variable name for this
    # multi-part 3d component instance in the app.
    @property
    def offset_x_name(self):
        return self._offset_var_names[0]

    @property
    def offset_y_name(self):
        return self._offset_var_names[1]

    @property
    def offset_z_name(self):
        return self._offset_var_names[2]

    @property
    def offset_names(self):
        return [self.offset_x_name,
                self.offset_y_name,
                self.offset_z_name]

    @property
    # This is the name of the variable for yaw in the app.
    def yaw_name(self):
        return self.name + '_yaw'

    @property
    def yaw(self):
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
        return self.name + '_pitch'

    @property
    def pitch(self):
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
        return self.name + '_roll'

    @property
    def roll(self):
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

        return cs_xy_pointing_expression(yaw_str, pitch_str, roll_str)

    @property
    def name(self):
        suffix = '_' + str(self.index)
        return self._name + suffix  # unique instance name

    @property
    def use_global_cs(self):
        return self._use_global_cs

    @property
    def offset(self):
        return self._offset_values

    @offset.setter
    def offset(self, o):
        # TODO: Add check for validity
        self._use_global_cs = False
        self._offset_values = o  # Expect tuple or list of strings

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
        # Set x,y,z offset variables in app
        if self.motion:
            xyz = ['x', 'y', 'z']
            for m in range(3):
                # app[self.offset_names[m]] = self.offset[m]
                app.variable_manager.set_variable(
                    variable_name=self.offset_names[m],
                    expression=self.offset[m],
                    description=self.name + ' ' + xyz[m] + "-position")

            #            app[self.yaw_name] = self.yaw  # TODO: Need an app Variable class in pyaedt to simplify syntax.
            #            app[self.pitch_name] = self.pitch
            #            app[self.roll_name] = self.roll
            app.variable_manager.set_variable(
                variable_name=self.yaw_name,
                expression=self.yaw,
                description=self.name + ' yaw')

            app.variable_manager.set_variable(
                variable_name=self.pitch_name,
                expression=self.pitch,
                description=self.name + ' pitch')

            app.variable_manager.set_variable(
                variable_name=self.roll_name,
                expression=self.roll,
                description=self.name + ' roll')

            cs_origin = self.offset_names
        else:
            cs_origin = self.offset
        if self.use_global_cs:
            return app.modeler.set_working_coordinate_system("Global")
        else:
            return app.modeler.create_coordinate_system(origin=cs_origin,
                                                        x_pointing=self._cs_pointing[0],
                                                        y_pointing=self._cs_pointing[1],
                                                        mode="axis",
                                                        name=self.cs_name)

    def _insert(self, app, verbose=False, motion=False):
        """
        Insert the multipart 3d component
        Parameters
        ----------
        app : pyaedt.hfss.Hfss, required
            Application where Mutipart3DComponent will be inserted.
        verbose : Bool, optional
            Placeholder variable to turn on verbose message
            reporting. Default False
        motion : Bool, optional
            Set to true if variables should be created in the
            app to set position, yaw, pitch, roll

        Returns
        -------

        """
        self.motion = True if motion else self.motion

        if self.use_global_cs:
            app.modeler.set_working_coordinate_system("Global")
        else:
            self.position_in_app(app)
            # TODO: fix create_coordinate_system as it does not allow expressions.
            # cs = app.modeler.create_coordinate_system(origin=self.offset_names,
            #                                          x_pointing=[1, 0, 0],
            #                                          y_pointing=[0, 1, 0],
            #                                          name=self.cs_name + '_good')

        for p in self.parts:
            inserted = self.parts[p].insert(app, verbose=verbose)  # index ensures unique CS names.
            if len(inserted) > 0:
                for i in inserted:
                    self.aedt_components.append(i)
        app.modeler.create_group(components=self.aedt_components,
                                 group_name=self.name)

    def insert(self, app, verbose=False, motion=False):
        return self._insert(app, verbose=verbose, motion=motion)


class Environment(MultiPartComponent, object):
    """
    Environment class is derived from MultiPartComponent.
    The call signature is identical to the parent class except
    motion is always False.
    """

    def __init__(self, env_folder):
        super(Environment, self).__init__(env_folder, motion=False)


class Actor(MultiPartComponent, object):
    """
    One instance of an actor. Derived class from MultiPartComponent
    """

    def __init__(self, actor_folder, speed="0"):
        """
        Actor class
            Derived from MultiPartComponent.
            Note: Forward motion is always forward in the +x-direction.

        Properties
        ----------
        speed : float or str
            Speed of the person in the x-direction.

        Parameters
        ----------
        actor_folder : str, required
            Folder pointing to the folder containing the definition
            of the Person.  This can be changed later in the Person class
            definition.
        """

        super(Actor, self).__init__(actor_folder, use_relative_cs=True, motion=True)

        self._speed_expression = str(speed) + 'm_per_sec'  # TODO: Need error checking here.

    @property
    def speed_name(self):
        return self.name + '_speed'

    @property
    def speed_expression(self):
        return self._speed_expression

    @speed_expression.setter
    def speed_expression(self, s):  # TODO: Add validation of the expression.
        self._speed_expression = s

    def _add_speed(self, app):
        app.variable_manager.set_variable(variable_name=self.speed_name,
                                          expression=self.speed_expression,
                                          description="object speed")
        # Update expressions for x and y position in app:
        app[self.offset_names[0]] = str(self.offset[0]) + '+' \
                                    + self.speed_name + ' * ' + MultiPartComponent._t \
                                    + '* cos(' + self.yaw_name + ')'

        app[self.offset_names[1]] = str(self.offset[1]) + '+' \
                                    + self.speed_name + ' * ' + MultiPartComponent._t \
                                    + '* sin(' + self.yaw_name + ')'

    def insert(self, app):
        """
        Insert the Bike into the AEDT app.

        """
        app.add_info_message("Adding Bike: " + self.name, "Design")
        self._insert(app, motion=True)  # Place the Person in the app.
        self._add_speed(self, app)


class Person(Actor, object):
    """
    One instance of an actor. Derived class from MultiPartComponent
    """

    def __init__(self, actor_folder, speed="0", stride="0.8meters"):
        """
        Person class
            Derived from Actor.
            Note: Motion is always forward in the x-direction of
            the Person coordinate system.

        Properties
        ----------
        speed : float or str
            Speed of the person in the x-direction.
        stride: float or str
            Stride length of the person. Default = "0.8meters"

        Parameters
        ----------
        actor_folder : str, required
            Folder pointing to the folder containing the definition
            of the Person.  This can be changed later in the Person class
            definition.
        """

        super(Person, self).__init__(actor_folder, speed=speed)

        self._stride = stride

    @property
    def stride(self):
        return self._stride

    @stride.setter
    def stride(self, s):
        self._stride = s  # TODO: Add validation to allow expressions.

    def _add_walking(self, app):
        # Update expressions for oscillation of limbs. At this point
        # we could parse p.name to handle motion (arm, leg, ...).
        for k, p in self.parts.items():
            if any(p.rot_axis):  # use this key to determine if there is motion of the part.
                if p.rot_axis[1]:  # Make sure pitch rotation is True
                    app[p.pitch_name] = p.pitch + "*sin(2*pi*(" + self.speed_name + \
                                           "/" + self.stride + ") " \
                                           + "*" + MultiPartComponent._t + ") + " + \
                                           "(" + p['compensation_angle'] + ")rad"

    def insert(self, app):
        """
        Insert the Person into the AEDT app.

        """

        app.add_info_message("Adding Person: " + self.name, "Design")

        # Insert the component first, then set variables.
        self._insert(app)  # Place the Person in the app.
        self._add_speed(app)
        self._add_walking(app)


class Bird(Actor, object):
    """
    One instance of an actor. Derived class from MultiPartComponent
    """

    def __init__(self, bird_folder, speed="2.0", flapping_rate="50Hz"):
        """
        Bike class
            Derived from MultiPartComponent.
            Note: Motion is always forward in the x-direction.

        Properties
        ----------
        speed : float or str
            Speed of the vehicle.

        """

        super(Bird, self).__init__(bird_folder, speed=speed)
        self._flapping_rate = flapping_rate

    def _add_flying(self, app):
        # Update expressions for wheel motion:

        for k, p in self.parts.items():
            if any(p.rot_axis):  # use this key to verify that there is local motion.
                if p.rot_axis[2]:  # Flapping is roll
                    app[p.roll_name] = p['rotation'] + '* sin(2*pi*' + str(self._flapping_rate) + '*' \
                                        + MultiPartComponent._t + ")"

    def insert(self, app):
        """
        Insert the Vehicle into the AEDT app.

        """

        app.add_info_message("Adding Vehicle: " + self.name, "Design")

        self._insert(app)  # Place the multipart component in the app.
        self._add_speed(app)
        self._add_flying(app)


class Vehicle(Actor, object):
    """
    One instance of an actor. Derived class from MultiPartComponent
    """

    def __init__(self, car_folder, speed="10.0"):
        """
        Vehicle class
            Derived from MultiPartComponent.
            Note: Motion is always forward in the x-direction.

        Properties
        ----------
        speed : float or str
            Speed of the vehicle.

        """

        super(Vehicle, self).__init__(car_folder, speed=speed)

    def _add_driving(self, app):
        # Update expressions for wheel motion:
        for k, p in self.parts.items():
            if any(p.rot_axis):  # use this key to determine if there is motion of the wheel.
                if p.rot_axis[1]:  # Make sure pitch rotation is True
                    app[p.pitch_name] = "(" + MultiPartComponent._t + "*" + \
                                        self.speed_name + "/" + p['tire_radius'] \
                                        + "meter)*(180/pi)*1deg"

    def insert(self, app):
        """
        Insert the Vehicle into the AEDT app.

        """

        app.add_info_message("Adding Vehicle: " + self.name, "Design")

        self._insert(app)  # Place the multipart component in the app.
        self._add_speed(app)
        self._add_driving(app)

        # Update Modeler line 137 to accept numerical values for the CS.

    def materials_dict(self):
        """
        all user defined material should be defined as dictionaries
        here. any material that is defined in the enviroment
        should be created here, otherwise PEC will be used by default
        """
        mat_dict = {}
        mat_dict['human_77GHz'] = {
            'er': 30,
            'tand': 0.01,
            'cond': 0
        }
        mat_dict['concrete'] = {
            'er': 2.5,
            'tand': 0.01,
            'cond': 0
        }
        mat_dict['earth'] = {
            'er': 4.5,
            'tand': 0.09,
            'cond': 0
        }
        mat_dict['steel'] = {
            'er': 1,
            'tand': 0,
            'cond': 6e8
        }

        return mat_dict


class Antenna(Part, object):
    """
    Antenna class derived from Part
    """
    def __init__(self, root_folder, ant_dict, parent=None, name=None):
        super(Antenna, self).__init__(root_folder, ant_dict, parent=parent, name=name)

    def _antenna_type(self, app):
        if self._compdef['antenna_type'] == 'parametric':
            return app.SbrAntennas.ParametricBeam

    @property
    def params(self):
        p = {}
        if self._compdef['antenna_type'] == 'parametric':
            p['Vertical BeamWidth'] = self._compdef['beamwidth_elevation']
            p['Horizontal BeamWidth'] = self._compdef['beamwidth_azimuth']
            p['Polarization'] = self._compdef['polarization']
        return p

    def _insert(self, app, target_cs=None):
        if not target_cs:
            target_cs = self._parent.cs_name
        a = app.create_sbr_antenna(self._antenna_type(app),
                                   model_units=self._parent.units,
                                   parameters_dict=self.params,
                                   target_cs=target_cs,
                                   antenna_name=self.name)
        return a

    def insert(self, app):

        """
        Insert antenna into app
        Parameters
        ----------
        app : pyaedt.Hfss, required
            HFSS application instance.

        Returns
        -------
        name of inserted object.

        """

        if self._do_offset:
            self.set_relative_cs(app)
            antenna_object = self._insert(app)  # Create coordinate system, if needed.
        else:
            antenna_object = self._insert(app, target_cs=self._parent.cs_name)
        if self._do_rotate:
            self.do_rotate(app, antenna_object.name)

        return antenna_object


class Radar(MultiPartComponent, object):
    """
    Radar class manages the radar definition and placement in the HFSS design.

    """

    def __init__(self, radar_folder, name=None, motion=False,
                 use_relative_cs=False, offset=("0", "0", "0")):

        name = name.split('.')[0] if name else name  # remove suffix if any
        self._component_class = 'radar'
        super(Radar, self).__init__(radar_folder, name=name,
                         use_relative_cs=use_relative_cs,
                         motion=motion, offset=offset)
        self.pair = []

    @property
    def units(self):
        return self._local_units

    def insert(self, app, verbose=False):
        """
        Insert radar into app (app is the HFSS application instance)
        Parameters
        ----------
        app, pyaedt.Hfss

        Returns
        -------

        """
        if verbose:
            app.add_info_message("Adding Radar Module:  " + self.name, "Design")

        tx_names = []
        rx_names = []
        for p in self.parts:
            antenna_object = self.parts[p].insert(app)
            self.aedt_components.append(antenna_object.antennaname)
            if p.startswith('tx'):
                tx_names.append(antenna_object.antennaname + '_p1')
                tx_names.append(antenna_object.antennaname + '_p1')
            elif p.startswith('rx'):
                rx_names.append(antenna_object.antennaname + '_p1')

        # Define tx/rx pairs:
        # TODO: How to get the name of the antenna? Always with '_p1' suffix??
        self.pair = {}
        for tx in tx_names:
            rx_string = ''
            for rx in rx_names:
                rx_string += rx + ','
            self.pair[tx] = rx_string.strip(',')

        app.set_sbr_txrx_settings(self.pair)

        app.modeler.create_group(components=self.aedt_components,
                                 group_name=self.name)


