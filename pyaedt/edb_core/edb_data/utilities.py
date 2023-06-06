class EDBStatistics(object):
    """Statistics object

    Object properties example.
    >>> stat_model = EDBStatistics()
    >>> stat_model.num_capacitors
    >>> stat_model.num_resistors
    >>> stat_model.num_inductors
    >>> stat_model.layout_size
    >>> stat_model.num_discrete_components
    >>> stat_model.num_inductors
    >>> stat_model.num_resistors
    >>> stat_model.num_capacitors
    >>> stat_model.num_nets
    >>> stat_model.num_traces
    >>> stat_model.num_polygons
    >>> stat_model.num_vias
    >>> stat_model.stackup_thickness
    >>> stat_model.occupying_surface
    >>> stat_model.occupying_ratio
    """

    def __init__(self):
        self._nb_layer = 0
        self._stackup_thickness = 0.0
        self._nb_vias = 0
        self._occupying_ratio = 0.0
        self._occupying_surface = 0.0
        self._layout_size = [0.0, 0.0, 0.0, 0.0]
        self._nb_polygons = 0
        self._nb_traces = 0
        self._nb_nets = 0
        self._nb_discrete_components = 0
        self._nb_inductors = 0
        self._nb_capacitors = 0
        self._nb_resistors = 0

    @property
    def num_layers(self):
        return self._nb_layer

    @num_layers.setter
    def num_layers(self, value):
        if isinstance(value, int):
            self._nb_layer = value

    @property
    def stackup_thickness(self):
        return self._stackup_thickness

    @stackup_thickness.setter
    def stackup_thickness(self, value):
        if isinstance(value, float):
            self._stackup_thickness = value

    @property
    def num_vias(self):
        return self._nb_vias

    @num_vias.setter
    def num_vias(self, value):
        if isinstance(value, int):
            self._nb_vias = value

    @property
    def occupying_ratio(self):
        return self._occupying_ratio

    @occupying_ratio.setter
    def occupying_ratio(self, value):
        if isinstance(value, float):
            self._occupying_ratio = value

    @property
    def occupying_surface(self):
        return self._occupying_surface

    @occupying_surface.setter
    def occupying_surface(self, value):
        if isinstance(value, float):
            self._occupying_surface = value

    @property
    def layout_size(self):
        return self._layout_size

    @property
    def num_polygons(self):
        return self._nb_polygons

    @num_polygons.setter
    def num_polygons(self, value):
        if isinstance(value, int):
            self._nb_polygons = value

    @property
    def num_traces(self):
        return self._nb_traces

    @num_traces.setter
    def num_traces(self, value):
        if isinstance(value, int):
            self._nb_traces = value

    @property
    def num_nets(self):
        return self._nb_nets

    @num_nets.setter
    def num_nets(self, value):
        if isinstance(value, int):
            self._nb_nets = value

    @property
    def num_discrete_components(self):
        return self._nb_discrete_components

    @num_discrete_components.setter
    def num_discrete_components(self, value):
        if isinstance(value, int):
            self._nb_discrete_components = value

    @property
    def num_inductors(self):
        return self._nb_inductors

    @num_inductors.setter
    def num_inductors(self, value):
        if isinstance(value, int):
            self._nb_inductors = value

    @property
    def num_capacitors(self):
        return self._nb_capacitors

    @num_capacitors.setter
    def num_capacitors(self, value):
        if isinstance(value, int):
            self._nb_capacitors = value

    @property
    def num_resistors(self):
        return self._nb_resistors

    @num_resistors.setter
    def num_resistors(self, value):
        if isinstance(value, int):
            self._nb_resistors = value
