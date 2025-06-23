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


from ansys.aedt.core.emit_core.nodes.emit_node import EmitNode
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
    def create_component(self, component_type: str, name: str = None, library: str = None) -> EmitNode:
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
        EmitNode
            The EmitNode of the created component.

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
                    f"' for type '{component_type}'."
                )
            stripped_component_name = component.name.strip("'")
            revision = self.emit_instance.results.get_revision()
            # Create the component using the EmitCom module
            new_component_id = self._emit_com_module.CreateEmitComponent(
                name, stripped_component_name, component.component_library
            )

            component_node = revision._get_node(node_id=new_component_id)
            return component_node
        except Exception as e:
            self.emit_instance.logger.error(f"Failed to create component '{name}' of type '{component_type}': {e}")
            raise RuntimeError(f"Failed to create component of type '{component_type}': {e}")

    @pyaedt_function_handler
    def create_radio_antenna(
        self, radio_type: str, radio_name: str = None, antenna_name: str = None, library: str = None
    ) -> tuple[EmitNode, EmitNode]:
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
        tuple[EmitNode, EmitNode]
            A tuple containing the EmitNode of the created radio and antenna.

        Raises
        ------
        RuntimeError
            If the radio or antenna creation fails.
        """
        radio_name = radio_name or ""
        antenna_name = antenna_name or ""
        library = library or ""

        try:
            new_radio = self.create_component(radio_type, radio_name, library)
            new_antenna = self.create_component("Antenna", antenna_name, "Antennas")
            if new_radio and new_antenna:
                self.connect_components(new_antenna, new_radio, "in", "n1")  # Connect antenna to radio
            return new_radio, new_antenna
        except Exception as e:
            self.emit_instance.logger.error(f"Failed to create radio of type '{radio_type}' or antenna: {e}")
            raise RuntimeError(f"Failed to create radio of type '{radio_type}' or antenna: {e}")

    @pyaedt_function_handler
    def connect_components(
        self, component_1: EmitNode, component_2: EmitNode, component_port_1: str = None, component_port_2: str = None
    ) -> None:
        """Connect two components in the schematic.

        Parameters
        ----------
        component_1 : EmitNode
            First component to connect.
        component_2 : EmitNode
            Second component to connect.
        component_port_1 : str, optional
            Port of the first component to connect. If ``None``, the default port is used.
        component_port_2 : str, optional
            Port of the second component to connect. If ``None``, the default port is used.

        Raises
        ------
        RuntimeError
            If the connection fails.
        """
        try:
            component_port_1 = component_port_1 or "n1"
            component_port_2 = component_port_2 or "n2"
            # Update the component ports to match the emit definition
            component_port_1 = self._component_port_update(component_port_1)
            component_port_2 = self._component_port_update(component_port_2)
            # Get the ports and their locations for both components
            ports_1 = self.emit_instance._oeditor.GetComponentPorts(component_1.name)
            port_locs_1 = {
                port: self.emit_instance._oeditor.GetComponentPortLocation(component_1.name, port) for port in ports_1
            }
            if len(ports_1) == 1:
                component_port_1 = ports_1[0]
            if component_1.properties["Type"] == "Multiplexer":
                component_port_1 = component_port_1.strip("n")

            ports_2 = self.emit_instance._oeditor.GetComponentPorts(component_2.name)
            port_locs_2 = {
                port: self.emit_instance._oeditor.GetComponentPortLocation(component_2.name, port) for port in ports_2
            }
            if len(ports_2) == 1:
                component_port_2 = ports_2[0]
            if component_2.properties["Type"] == "Multiplexer":
                component_port_2 = component_port_2.strip("n")

            # Validate that the specified ports exist in their respective components
            if component_port_1 not in port_locs_1:
                raise ValueError(f"Port '{component_port_1}' does not exist in component '{component_1.name}'.")
            if component_port_2 not in port_locs_2:
                raise ValueError(f"Port '{component_port_2}' does not exist in component '{component_2.name}'.")
            # Check if the ports are on the same side of the components
            component_1_antenna_pors_list = [x for x in component_1.properties["AntennaSidePorts"].split("|")]
            component_1_radio_ports_list = [x for x in component_1.properties["RadioSidePorts"].split("|")]
            if component_1.properties["Type"] == "AntennaNode":
                component_1_radio_ports_list = ["n"]
            component_2_antenna_ports_list = [x for x in component_2.properties["AntennaSidePorts"].split("|")]
            component_2_radio_ports_list = [x for x in component_2.properties["RadioSidePorts"].split("|")]
            if component_2.properties["Type"] == "AntennaNode":
                component_2_radio_ports_list = ["n"]
            if (
                component_port_1[-1] in component_1_antenna_pors_list
                and component_port_2[-1] in component_2_antenna_ports_list
            ) or (
                component_port_1[-1] in component_1_radio_ports_list
                and component_port_2[-1] in component_2_radio_ports_list
            ):
                raise RuntimeError("Both ports are on the same side. Connection cannot be established.")
            # Move the first component to align with the second component's port
            delta_x = port_locs_2[component_port_2][0] - port_locs_1[component_port_1][0]
            delta_y = port_locs_2[component_port_2][1] - port_locs_1[component_port_1][1]
            self.emit_instance._oeditor.Move(component_1.name, delta_x, delta_y)
            self.emit_instance.logger.info(
                f"Successfully connected components '{component_1.name}' and '{component_2.name}'."
            )
        except Exception as e:
            self.emit_instance.logger.error(
                f"Failed to connect components '{component_1.name}' and '{component_2.name}' with the given ports: {e}"
            )
            raise RuntimeError(
                f"Failed to connect components '{component_1.name}' and '{component_2.name}' with the given ports: {e}"
            )

    @pyaedt_function_handler
    def _component_port_update(self, input_port: str) -> str:
        """Update the component port properties as emit definition.

        Parameters
        ----------
        input_port : str
            Name of the input port to update.

        Returns
        -------
        updated_port: int
            The updated port number after the update.
        """

        port_number = input_port[-1]
        if port_number in ["2", "3", "4", "5", "6"]:
            updated_port = "n" + port_number
        elif port_number in ["1", "n"]:
            updated_port = "n1"
        else:
            raise ValueError(f"Invalid port format: '{input_port}'")
        return updated_port
