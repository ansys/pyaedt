# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 - 2025 ANSYS, Inc. and/or its affiliates.
# SPDX-License-Identifier: MIT
#
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.


from ansys.aedt.core.generic.general_methods import pyaedt_function_handler


class EmitSchematic:
    """Represents the EMIT schematic and provides methods to interact with it."""

    def __init__(self, emit_instance):
        """Initialize the EmitSchematic class.

        Parameters
        ----------
        emit_instance : Emit
            Instance of the Emit class.
        """
        self.emit_instance = emit_instance

    @property
    def _emit_com_module(self):
        """Retrieve the EmitCom module from the Emit instance.

        Returns
        -------
        object
            The EmitCom module.

        Raises
        ------
        RuntimeError
            If the EmitCom module cannot be retrieved.
        """
        if not hasattr(self.emit_instance, "_odesign"):
            raise RuntimeError("Emit instance does not have a valid '_odesign' attribute.")
        try:
            return self.emit_instance._odesign.GetModule("EmitCom")
        except Exception as e:
            raise RuntimeError(f"Failed to retrieve EmitCom module: {e}")

    @pyaedt_function_handler
    def create_component(self, component_type: str, name: str = None, library: str = None) -> int:
        """Create a component.

        Parameters
        ----------
        component_type : str
            Type of the component to create.
        name : str, optional
            Name of the component to create. AEDT defaults used if not provided.
        library : str, optional
            Name of the component library. Defaults to an empty string if not provided.

        Returns
        -------
        int
            The ID of the created component.

        Raises
        ------
        ValueError
            If the component type is empty or no matching component is found.
        RuntimeError
            If the component creation fails.
        """
        if not component_type:
            raise ValueError("The 'component_type' argument is required.")

        name = name or ""
        library = library or ""

        try:
            # Retrieve matching components from the catalog
            matching_components = self.emit_instance.modeler.components.components_catalog[component_type]

            if not matching_components:
                self.emit_instance.logger.error(f"No component found for type '{component_type}'.")
                raise ValueError(f"No component found for type '{component_type}'.")

            if len(matching_components) == 1:
                # Use the single matching component
                component = matching_components[0]
                self.emit_instance.logger.info(
                    f"Using component '{component.name}' from library '{component.component_library}"
                    f"' for type '{component_type}'."
                )
            else:
                # Attempt to find an exact match
                component = next((comp for comp in matching_components if comp.name == component_type), None)
                if not component:
                    self.emit_instance.logger.error(
                        f"Multiple components found for type '{component_type}', but no exact match."
                        "  Please specify a unique component."
                    )
                    raise ValueError(f"Multiple components found for type '{component_type}', but no exact match.")
                self.emit_instance.logger.info(
                    f"Using exact match component '{component.name}' from library '{component.component_library}"
                    "' for type '{component_type}'."
                )

            # Create the component using the EmitCom module
            new_component_id = self._emit_com_module.CreateEmitComponent(
                name, component.name, component.component_library
            )
            return new_component_id
        except Exception as e:
            self.emit_instance.logger.error(f"Failed to create component '{name}' of type '{component_type}': {e}")
            raise RuntimeError(f"Failed to create component of type '{component_type}': {e}")

    @pyaedt_function_handler
    def create_radio_antenna(
        self, radio_type: str, radio_name: str = None, antenna_name: str = None, library: str = None
    ) -> tuple[int, int]:
        """Create a new radio and antenna and connect them.

        Parameters
        ----------
        radio_type : str
            Type of radio to create. For example, "Bluetooth". Must match
            a radio name in the specified library.
        radio_name : str, optional
            Name to assign to the new radio. If ``None``, then an instance
            name is assigned automatically. The default is ``None``.
        antenna_name : str, optional
            Name to assign to the new antenna. If ``None``, then an instance
            name is assigned automatically. The default is ``None``.
        library : str, optional
            Name of the component library. If ``None``, then the default
            library is used. The default is ``None``.

        Returns
        -------
        tuple
            A tuple containing the IDs of the created radio and antenna.

        Raises
        ------
        RuntimeError
            If the radio or antenna creation fails.
        """
        radio_name = radio_name or ""
        antenna_name = antenna_name or ""
        library = library or ""

        try:
            new_radio_id = self.create_component(radio_type, radio_name, library)
            new_antenna_id = self.create_component("Antenna", antenna_name, "Antennas")
            if new_radio_id and new_antenna_id:
                self.connect_components(new_antenna_id, new_radio_id)  # Connect antenna to radio
            return new_radio_id, new_antenna_id
        except Exception as e:
            self.emit_instance.logger.error(f"Failed to create radio of type '{radio_type}' or antenna: {e}")
            raise RuntimeError(f"Failed to create radio of type '{radio_type}' or antenna: {e}")

    @pyaedt_function_handler
    def connect_components(self, component_id_1: int, component_id_2: int):
        """Connect two components in the schematic.

        Parameters
        ----------
        component_id_1 : str
            ID of the first component.
        component_id_2 : str
            ID of the second component.

        Raises
        ------
        RuntimeError
            If the connection fails.
        """
        try:
            component_name_1 = self.get_component_properties(component_id_1, "Name")
            component_name_2 = self.get_component_properties(component_id_2, "Name")
            self.emit_instance._oeditor.PlaceComponent(component_name_1, component_name_2)
            self.emit_instance.logger.info(
                f"Successfully connected components '{component_name_1}' and '{component_name_2}'."
            )
        except Exception as e:
            self.emit_instance.logger.error(
                f"Failed to connect components '{component_id_1}' and '{component_id_2}': {e}"
            )
            raise RuntimeError(f"Failed to connect components '{component_id_1}' and '{component_id_2}': {e}")

    @pyaedt_function_handler
    def get_component_properties(self, component_id: int, property_key: str = None) -> dict:
        """Get properties of a component.

        Parameters
        ----------
        component_id : int
            ID of the component.
        property_key : str, optional
            Specific property key to retrieve. If ``None``, all properties are returned.

        Returns
        -------
        dict or str
            Dictionary containing all properties of the component if `property_key` is ``None``.
            Otherwise, the value of the specified property key.

        Raises
        ------
        KeyError
            If the specified property key is not found.
        """
        try:
            props = self._emit_com_module.GetEmitNodeProperties(0, component_id, True)
            props_dict = {prop.split("=", 1)[0]: prop.split("=", 1)[1] for prop in props}
            if property_key is None:
                return props_dict
            if property_key in props_dict:
                return props_dict[property_key]
            raise KeyError(f"Property key '{property_key}' not found.")
        except Exception as e:
            self.emit_instance.logger.error(f"Failed to retrieve properties for component '{component_id}': {e}")
            raise RuntimeError(f"Failed to retrieve properties for component '{component_id}': {e}")
