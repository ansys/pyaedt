import os

from pyaedt.generic.general_methods import pyaedt_function_handler


class CommonAntenna(object):
    """Base methods common to antennas toolkit."""

    def __init__(self, *args, **kwargs):
        self._app = args[0]
        self.object_list = {}
        self.boundaries = {}
        self.excitations = {}
        self.mesh_operations = {}
        self.frequency = kwargs["frequency"]
        self.frequency_unit = kwargs["frequency_unit"]
        self.outer_boundary = kwargs["outer_boundary"]
        self.huygens_box = kwargs["huygens_box"]
        self.length_unit = kwargs["length_unit"]
        self.coordinate_system = kwargs["coordinate_system"]
        self.antenna_name = kwargs["antenna_name"]
        self.position = kwargs["position"]

    @property
    def frequency(self):
        """Center Frequency.

        Returns
        -------
        float
        """
        return self._frequency

    @frequency.setter
    def frequency(self, value):
        self._frequency = value
        parameters = self._rectangular_patch_w_probe_synthesis()
        if "object_list" in set(list(self.__dict__.keys())) and self.object_list:
            parameters_map = {}
            cont = 0
            for param in parameters:
                parameters_map[self.parameters[cont]] = parameters[param]
                cont += 1
            self._update_parameters(parameters_map, self._length_unit)

    @property
    def frequency_unit(self):
        """Frequency units.

        Returns
        -------
        str
        """
        return self._frequency_unit

    @frequency_unit.setter
    def frequency_unit(self, value):
        self._frequency_unit = value
        parameters = self._rectangular_patch_w_probe_synthesis()
        if "object_list" in set(list(self.__dict__.keys())) and self.object_list:
            parameters_map = {}
            cont = 0
            for param in parameters:
                parameters_map[self.parameters[cont]] = parameters[param]
                cont += 1
            self._update_parameters(parameters_map, self._length_unit)

    @property
    def outer_boundary(self):
        """Outer boundary.

        Returns
        -------
        str
        """
        return self._outer_boundary

    @outer_boundary.setter
    def outer_boundary(self, value):
        self._outer_boundary = value

    @property
    def huygens_box(self):
        """Enable Huygens box.

        Returns
        -------
        bool
        """
        return self._huygens_box

    @huygens_box.setter
    def huygens_box(self, value):
        self._huygens_box = value

    @property
    def length_unit(self):
        """Length unit.

        Returns
        -------
        str
        """
        return self._length_unit

    @length_unit.setter
    def length_unit(self, value):
        self._length_unit = value
        parameters = self._rectangular_patch_w_probe_synthesis()
        if "object_list" in set(list(self.__dict__.keys())) and self.object_list:
            parameters_map = {}
            cont = 0
            for param in parameters:
                parameters_map[self.parameters[cont]] = parameters[param]
                cont += 1
            self._update_parameters(parameters_map, self._length_unit)

    @property
    def coordinate_system(self):
        """Reference Coordinate system.

        Returns
        -------
        str
        """
        return self._coordinate_system

    @coordinate_system.setter
    def coordinate_system(self, value):
        self._coordinate_system = value
        for antenna_obj in self.object_list:
            self.object_list[antenna_obj].history.props["Coordinate System"] = self._coordinate_system

    @property
    def antenna_name(self):
        """Antenna name.

        Returns
        -------
        str
        """
        return self._antenna_name

    @antenna_name.setter
    def antenna_name(self, value):
        old_name = None
        if "_antenna_name" in set(list(self.__dict__.keys())):
            old_name = self._antenna_name
        self._antenna_name = value
        if old_name:
            for antenna_obj in self.object_list:
                self.object_list[antenna_obj].group_name = self._antenna_name
            self._app.modeler.oeditor.Delete(["NAME:Selections", "Selections:=", old_name])

    @property
    def position(self):
        """Antenna position.

        Returns
        -------
        lst
        """
        return self._position

    @position.setter
    def position(self, value):
        self._position = value
        parameters = self._rectangular_patch_w_probe_synthesis()
        if "object_list" in set(list(self.__dict__.keys())) and self.object_list:
            parameters_map = {}
            cont = 0
            for param in parameters:
                parameters_map[self.parameters[cont]] = parameters[param]
                cont += 1
            self._update_parameters(parameters_map, self._length_unit)

    @pyaedt_function_handler()
    def create_3dcomponent(self, component_file=None, component_name=None, replace=False):
        """Create 3DComponent of the antenna.

        Parameters
        ----------
        component_file : str
            Full path to the A3DCOMP file. The default is the pyaedt folder.
        component_name : str, optional
            Name of the component. The default is the antenna name.
        replace : bool, optional
            Replace antenna with a 3DComponent. The default is ``False``.

        Returns
        -------
        str
            Path of the 3DComponent file.

        Examples
        --------
        >>> from pyaedt import Hfss
        >>> hfss = Hfss()
        >>> patch = hfss.antennas.rectangular_patch_w_probe()
        >>> path = patch.create_3dcomponent()
        """
        if not component_file:
            component_file = os.path.join(self._app.working_directory, self.antenna_name + ".a3dcomp")
        if not component_name:
            component_name = self.antenna_name

        included_cs = None
        if self.coordinate_system != "Global":
            included_cs = self.coordinate_system

        # # Check independent variables
        # variables_to_add = []
        # dependent_variables = []
        # ind_variables = self._app._variable_manager.independent_variable_names
        # dep_variables = self._app._variable_manager.dependent_variable_names
        # for param in self.parameters:
        #     if self._app[param] in ind_variables:
        #         variables_to_add.append(self._app[param])
        #         dependent_variables.append(param)
        #     elif self._app[param] not in dep_variables:
        #         variables_to_add.append(param)

        self._app.modeler.create_3dcomponent(
            component_file=component_file,
            component_name=component_name,
            variables_to_include=self.parameters,
            object_list=list(self.object_list.keys()),
            boundaries_list=list(self.boundaries.keys()),
            excitation_list=list(self.excitations.keys()),
            included_cs=[included_cs],
            reference_cs=self.coordinate_system,
            component_outline="None",
        )

        if replace:
            self._app.modeler.replace_3dcomponent(
                component_name=component_name,
                variables_to_include=self.parameters,
                object_list=list(self.object_list.keys()),
                boundaries_list=list(self.boundaries.keys()),
                excitation_list=list(self.excitations.keys()),
                included_cs=[included_cs],
                reference_cs=self.coordinate_system,
            )
            self._app.modeler.oeditor.Delete(["NAME:Selections", "Selections:=", self.antenna_name])
        return True

    @pyaedt_function_handler()
    def _update_parameters(self, parameters, length_unit):
        for param in parameters:
            self._app[param] = str(parameters[param]) + length_unit
        return True
