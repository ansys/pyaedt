import os

from pyaedt.generic.general_methods import pyaedt_function_handler


class CommonAntenna(object):
    """Base methods common to antennas toolkit."""

    def __init__(self, *args, **kwargs):
        self._app = args[0]
        self.parameters = []
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
        self._old_antenna_name = None
        self.antenna_name = kwargs["antenna_name"]
        self.position = kwargs["position"]
        super(CommonAntenna, self).__init__(*args, **kwargs)

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
        if self.object_list:
            parameters = self._synthesis()
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
        if self.object_list:
            parameters = self._synthesis()
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
        if self.object_list:
            parameters = self._synthesis()
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
        self._antenna_name = value
        old_name = None
        if value != self._old_antenna_name:
            old_name = self._old_antenna_name
            self._old_antenna_name = self._antenna_name
        if old_name and self.object_list:
            for antenna_obj in self.object_list:
                self.object_list[antenna_obj].group_name = self._antenna_name

            if len(list(self._app.modeler.oeditor.GetObjectsInGroup(old_name))) == 0:
                self._app.modeler.oeditor.Delete(["NAME:Selections", "Selections:=", old_name])

    @property
    def position(self):
        """Antenna position.

        Returns
        -------
        list
        """
        return self._position

    @position.setter
    def position(self, value):
        self._position = value
        if self.object_list:
            parameters = self._synthesis()
            parameters_map = {}
            cont = 0
            for param in parameters:
                if param[0:4] == "pos_":
                    parameters_map[self.parameters[cont]] = parameters[param]
                cont += 1
            if parameters_map:
                self._update_parameters(parameters_map, self._length_unit)
            else:
                self._app.logger.error("Variable with suffix 'pos' not found.")

    @pyaedt_function_handler()
    def create_3dcomponent(self, component_file=None, component_name=None, replace=False):
        """Create 3DComponent of the antenna.

        Parameters
        ----------
        component_file : str, optional
            Full path to the A3DCOMP file. The default is the pyaedt folder.
        component_name : str, optional
            Name of the component. The default is the antenna name.
        replace : bool, optional
            Whether to replace antenna with a 3DComponent. The default is ``False``.

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

        self._app.modeler.create_3dcomponent(
            component_file=component_file,
            component_name=component_name,
            variables_to_include=self.parameters,
            object_list=list(self.object_list.keys()),
            boundaries_list=list(self.boundaries.keys()),
            excitation_list=list(self.excitations.keys()),
            included_cs=[self.coordinate_system],
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
                included_cs=[self.coordinate_system],
                reference_cs=self.coordinate_system,
            )
            if self._app.modeler.oeditor.GetObjectsInGroup(self.antenna_name).count == 0:
                self._app.modeler.oeditor.Delete(["NAME:Selections", "Selections:=", self.antenna_name])

            self._app.modeler.add_new_user_defined_component()

        return True

    @pyaedt_function_handler()
    def duplicate_along_line(self, vector, num_clones=2):
        """Duplicate the object along a line.

        Parameters
        ----------
        vector : list
            List of ``[x1 ,y1, z1]`` coordinates for the vector.
        num_clones : int, optional
            Number of clones. The default is ``2``.

        Returns
        -------
        dict
            Dictionary with the list of new objects.

        Examples
        --------
        >>> from pyaedt import Hfss
        >>> hfss = Hfss()
        >>> patch = hfss.antennas.rectangular_patch_w_probe()
        >>> new_patch = patch.duplicate_along_line([10, 0, 0], 2)
        """
        new_objects = {}
        for i in range(0, num_clones - 1):
            new_objects["antenna" + str(i)] = []
        for component in self.object_list:
            _, output = self._app.modeler.duplicate_along_line(component, vector, num_clones)
            for i in range(0, num_clones - 1):
                new_objects["antenna" + str(i)].append(output[i])

        return new_objects

    @pyaedt_function_handler()
    def _update_parameters(self, parameters, length_unit):
        for param in parameters:
            self._app[param] = str(parameters[param]) + length_unit
        return True

    @pyaedt_function_handler()
    def _synthesis(self):
        pass
