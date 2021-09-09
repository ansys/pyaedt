import os

from pyaedt import aedt_exception_handler
from pyaedt.modeler.GeometryOperators import GeometryOperators


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
        # Default values:
        self._compdef = dict()
        self._parent = parent

        # Extract the 3d component name and part folder
        # from the file name.
        # Use this as the default value for comp_name.  Ensure that the correct extension is used.
        self._compdef['part_folder'] = part_folder
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
        if kw in ['offset', 'rotation_cs']:
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
        return os.path.join(self._compdef['part_folder'], self['comp_name'])

    # Create a unique coordinate system name for the part.
    @property
    def cs_name(self):
        """Coordinate System Name.

        Returns
        -------
        str
        """
        if self._motion or not self.zero_offset('offset') or not self.zero_offset('rotation_cs'):
            return self.name + '_cs'
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
        return self.name + '_yaw'

    @property
    def pitch_name(self):
        """Pitch Name.

        Returns
        -------
        str
        """
        return self.name + '_pitch'

    @property
    def roll_name(self):
        """Roll Name.

        Returns
        -------
        str
        """
        return self.name + '_roll'

    # Always return the local origin as a list:
    @property
    def local_origin(self):
        """Local Part Offset.

        Returns
        -------
        list
        """
        if self['offset']:
            if self.zero_offset('offset') or self['offset'] == 'Global':
                return [0, 0, 0]
            else:
                if self._parent._local_units:
                    units = self._parent._local_units
                else:
                    units = self._parent.modeler_units
                offset = [str(i)+units for i in self['offset']]

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
        # return any(GeometryOperators.numeric_cs([self._yaw, self._pitch, self._roll])) or not self.zero_offset('rotation_cs')

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
        return self._parent.name + '_' + self._name

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
            app.modeler.create_coordinate_system(origin=self.local_origin,
                                                 x_pointing=x_pointing,
                                                 y_pointing=y_pointing,
                                                 reference_cs=self._parent.cs_name,
                                                 mode="axis",
                                                 name=self.cs_name)
        return True

    @property
    def rot_cs_name(self):
        """Rotation Coordinate System Name.

        Returns
        -------
        str
        """
        return self.name + '_rot_cs'

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
                app.modeler.primitives.insert_3d_component(self.file_name, targetCS=self._parent.cs_name))
        if self._do_rotate:
            self.do_rotate(app, aedt_objects[0])

        # Duplication occurs in parent coordinate system.
        app.modeler.set_working_coordinate_system(self._parent.cs_name)
        if self['duplicate_vector']:
            d_vect = [float(i) for i in self['duplicate_vector']]
            duplicate_result = app.modeler.duplicate_along_line(aedt_objects[0], d_vect,
                                                                nclones=int(self['duplicate_number']), is_3d_comp=True)
            if duplicate_result[0]:
                for d in duplicate_result[1]:
                    aedt_objects.append(d)
        return aedt_objects


class Antenna(Part, object):
    """Antenna class derived from Part.
    """
    def __init__(self, root_folder, ant_dict, parent=None, name=None):
        super(Antenna, self).__init__(root_folder, ant_dict, parent=parent, name=name)

    def _antenna_type(self, app):
        if self._compdef['antenna_type'] == 'parametric':
            return app.SbrAntennas.ParametricBeam

    @property
    def params(self):
        """Multipart Parameters.

        Returns
        -------
        dict
        """
        p = {}
        if self._compdef['antenna_type'] == 'parametric':
            p['Vertical BeamWidth'] = self._compdef['beamwidth_elevation']
            p['Horizontal BeamWidth'] = self._compdef['beamwidth_azimuth']
            p['Polarization'] = self._compdef['polarization']
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
        a = app.create_sbr_antenna(self._antenna_type(app),
                                   model_units=units,
                                   parameters_dict=self.params,
                                   target_cs=target_cs,
                                   antenna_name=self.name)
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