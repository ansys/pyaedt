from pyaedt import aedt_exception_handler
from pyaedt.generic.DataHandlers import json_to_dict
from pyaedt.modeler.MultiParts import MultiPartComponent, Actor


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


class Generic(Actor, object):
    """
    One instance of an actor. Derived class from MultiPartComponent.
    """

    def __init__(self, actor_folder, speed="0", relative_cs_name=None):
        """Generic class, derived from Actor.

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
        super(Generic, self).__init__(actor_folder, speed=speed, relative_cs_name=relative_cs_name)


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
                    app[p.pitch_name] = p.pitch + "*sin(2*pi*(" + self.speed_name + \
                                           "/" + self.stride + ") " \
                                           + "*" + MultiPartComponent._t + ") + " + \
                                           "(" + p['compensation_angle'] + ")rad"

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
    """One instance of an actor. Derived class from MultiPartComponent.
    """

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
                    app[p.roll_name] = p['rotation'] + '* sin(2*pi*' + str(self._flapping_rate) + '*' \
                                        + MultiPartComponent._t + ")"

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
    """One instance of an actor. Derived class from MultiPartComponent.
    """

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
                    app[p.pitch_name] = "(" + MultiPartComponent._t + "*" + \
                                        self.speed_name + "/" + p['tire_radius'] \
                                        + "meter)*(180/pi)*1deg"

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


class Radar(MultiPartComponent, object):
    """
    Radar class manages the radar definition and placement in the HFSS design.

    """

    def __init__(self, radar_folder, name=None, motion=False,
                 use_relative_cs=False, offset=("0", "0", "0"), speed=0, relative_cs_name=None):

        self.aedt_antenna_names = []  # List of Antenna Names
        name = name.split('.')[0] if name else name  # remove suffix if any
        self._component_class = 'radar'
        super(Radar, self).__init__(radar_folder, name=name, use_relative_cs=use_relative_cs, motion=motion,
                                    offset=offset, relative_cs_name=relative_cs_name)
        self._speed_expression = str(speed) + 'm_per_sec'
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
        return self.name + '_speed'

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
        app.variable_manager.set_variable(variable_name=self.speed_name,
                                          expression=self.speed_expression,
                                          description="radar speed")
        # Update expressions for x and y position in app:
        app[self.offset_names[0]] = str(self.offset[0]) + '+' \
                                    + self.speed_name + ' * ' + MultiPartComponent._t \
                                    + '* cos(' + self.yaw_name + ')'

        app[self.offset_names[1]] = str(self.offset[1]) + '+' \
                                    + self.speed_name + ' * ' + MultiPartComponent._t \
                                    + '* sin(' + self.yaw_name + ')'

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
                self._relative_cs_name = self.name + '_cs'
        self.position_in_app(app)
        tx_names = []
        rx_names = []
        for p in self.parts:
            antenna_object = self.parts[p].insert(app, units=self._local_units)
            self.aedt_components.append(antenna_object.antennaname)
            self.aedt_antenna_names.append(antenna_object.excitation_name)
            if p.startswith('tx'):
                tx_names.append(antenna_object.excitation_name)
            elif p.startswith('rx'):
                rx_names.append(antenna_object.excitation_name)

        # Define tx/rx pairs:
        self.pair = {}
        for tx in tx_names:
            rx_string = ''
            for rx in rx_names:
                rx_string += rx + ','
            self.pair[tx] = rx_string.strip(',')

        app.set_sbr_txrx_settings(self.pair)

        app.modeler.create_group(components=self.aedt_components,
                                 group_name=self.name)
        app.add_info_message("Group Created:  " + self.name)
        if motion:
            self._add_speed(app)
        return self.aedt_antenna_names