# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 - 2026 ANSYS, Inc. and/or its affiliates.
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
from ansys.aedt.core.internal.errors import AEDTRuntimeError


class EmitSchematic:
    """Represents the EMIT schematic and provides methods to interact with it."""

    always_excluded = ["Name", "NodeID"]

    def __init__(self, emit_project) -> None:
        """Initialize the EmitSchematic class.

        Parameters
        ----------
        emit_project : Emit
            Instance of the Emit class.
        """
        self.emit_project = emit_project

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
            matching_components = []
            matching_components = self.emit_project.modeler.components.components_catalog[component_type]

            if not matching_components:
                # couldn't find a component match, try looking at all component names
                catalog_comps = self.emit_project.modeler.components.components_catalog.components
                for value in catalog_comps.values():
                    if value.name == component_type:
                        matching_components.append(value)

                if not matching_components:
                    self.emit_project.logger.error(f"No component found for type '{component_type}'.")
                    raise ValueError(f"No component found for type '{component_type}'.")

            if len(matching_components) == 1:
                # Use the single matching component
                component = matching_components[0]
                self.emit_project.logger.info(
                    f"Using component '{component.name}' from library '{component.component_library}"
                    f"' for type '{component_type}'."
                )
            else:
                # Attempt to find an exact match
                component = next((comp for comp in matching_components if comp.name == component_type), None)
                if not component:
                    self.emit_project.logger.error(
                        f"Multiple components found for type '{component_type}', but no exact match."
                        "  Please specify a unique component."
                    )
                    raise ValueError(f"Multiple components found for type '{component_type}', but no exact match.")
                self.emit_project.logger.info(
                    f"Using exact match component '{component.name}' from library '{component.component_library}"
                    "' for type '{component_type}'."
                )
            revision = self.emit_project.results.get_revision()

            # Create the component using the EmitCom module
            component.name = component.name.strip("'")
            new_component_id = self.emit_project._emit_com_module.CreateEmitComponent(
                name, component.name, component.component_library
            )
            component_node = revision._get_node(node_id=new_component_id)
            return component_node
        except Exception as e:
            self.emit_project.logger.error(f"Failed to create component '{name}' of type '{component_type}': {e}")
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
                self.connect_components(new_antenna.name, new_radio.name)  # Connect antenna to radio
                return new_radio, new_antenna
            raise RuntimeError(f"Failed to create radio of type '{radio_type}' or antenna.")
        except Exception as e:
            self.emit_project.logger.error(f"Failed to create radio of type '{radio_type}' or antenna: {e}")
            raise RuntimeError(f"Failed to create radio of type '{radio_type}' or antenna: {e}")

    @pyaedt_function_handler
    def connect_components(self, component_name_1: str, component_name_2: str):
        """Connect two components in the schematic.

        Parameters
        ----------
        component_1 : str
            Name of the first component.
        component_2 : str
            Name of the second component.

        Raises
        ------
        RuntimeError
            If the connection fails.
        """
        try:
            self.emit_project._oeditor.PlaceComponent(component_name_1, component_name_2)
            self.emit_project.logger.info(
                f"Successfully connected components '{component_name_1}' and '{component_name_2}'."
            )
        except Exception as e:
            self.emit_project.logger.error(
                f"Failed to connect components '{component_name_1}' and '{component_name_2}': {e}"
            )
            raise RuntimeError(f"Failed to connect components '{component_name_1}' and '{component_name_2}': {e}")

    @pyaedt_function_handler
    def delete_component(self, name: str):
        """Delete a component from the schematic.

        Parameters
        ----------
        name : str
            Name of the component.

        Raises
        ------
        RuntimeError
            If the deletion fails.
        """
        try:
            self.emit_project._emit_com_module.DeleteEmitComponent(name)
            self.emit_project.logger.info(f"Successfully deleted component '{name}'.")
        except Exception as e:
            self.emit_project.logger.error(f"Failed to delete component '{name}': {e}")
            raise AEDTRuntimeError(f"Failed to delete component '{name}': {e}")

    @pyaedt_function_handler
    def compare_nodes(
        self, node_1: EmitNode, node_2: EmitNode, exclude_props: list[str] = None
    ) -> tuple[bool, dict]:
        """Compare two EMIT nodes.

        Parameters
        ----------
        node_1 : EmitNode
            First node.
        node_2 : EmitNode
            Second node.
        exclude_props : list[str], optional
            Additional properties to exclude from the comparison. ``Name`` and
            ``NodeID`` are always excluded.

        Returns
        -------
        tuple[bool, dict]
            A tuple containing a boolean indicating if the nodes are the same type and a dictionary of non-matching properties.
            The dictionary contains the differences between the nodes.
        """
        if node_1._node_type != node_2._node_type:
            return False, {}

        excluded_props = set(self.always_excluded)
        if exclude_props:
            excluded_props.update(exclude_props)

        non_matching_properties = {}
        props_1 = node_1.properties
        props_2 = node_2.properties
        for key in sorted(props_1.keys() | props_2.keys()):
            if key == "Children" or key in excluded_props:
                continue

            value_1 = props_1.get(key)
            value_2 = props_2.get(key)
            if value_1 != value_2:
                non_matching_properties[key] = {
                    "from": {
                        "component": node_2.name,
                        "value": value_2,
                    },
                    "to": {
                        "component": node_1.name,
                        "value": value_1,
                    },
                }
        return True, non_matching_properties

    @pyaedt_function_handler
    def compare_components(
        self, component_1: EmitNode, component_2: EmitNode, exclude_props: list[str] = None
    ) -> tuple[bool, dict]:
        """Compare two EMIT schematic components.

        For single-node components (Filters, Amplifiers, Antennas, etc.), this
        returns the same result as :func:`compare_nodes`. For multi-node
        components (Radios, Emitters, Multiplexers), the root node is compared
        and differences from matching child nodes are merged recursively.

        Parameters
        ----------
        component_1 : EmitNode
            First component.
        component_2 : EmitNode
            Second component.
        exclude_props : list[str], optional
            Additional properties to exclude from the comparison. ``Name`` and
            ``NodeID`` are always excluded.

        Returns
        -------
        tuple[bool, dict]
            A tuple containing a boolean indicating if the components are the same type and a dictionary of differences.
            The dictionary contains the differences between the components.
        """
        if component_1.node_type != component_2.node_type:
            return False, {}

        differences = {}
        same_type, node_diffs = self.compare_nodes(
            component_1, component_2, exclude_props=exclude_props
        )
        if not same_type:
            return False, {}

        for key, value in node_diffs.items():
            if key != "Children":
                differences[key] = value

        children_1 = component_1.children
        children_2 = component_2.children
        if not children_1 and not children_2:
            return True, differences

        children_1_by_name = {child.name: child for child in children_1}
        children_2_by_name = {child.name: child for child in children_2}
        child_diffs = {}

        for child_name in sorted(children_1_by_name.keys() | children_2_by_name.keys()):
            child_1 = children_1_by_name.get(child_name)
            child_2 = children_2_by_name.get(child_name)
            if child_1 is None:
                child_diffs[child_name] = {
                    "only_in": component_2.name,
                    "value": child_2.name,
                }
            elif child_2 is None:
                child_diffs[child_name] = {
                    "only_in": component_1.name,
                    "value": child_1.name,
                }
            else:
                same_child_type, nested_diffs = self.compare_components(
                    child_1, child_2, exclude_props=exclude_props
                )
                if not same_child_type:
                    child_diffs[child_name] = {
                        "from": {
                            "component": component_2.name,
                            "value": child_2.node_type,
                        },
                        "to": {
                            "component": component_1.name,
                            "value": child_1.node_type,
                        },
                    }
                elif nested_diffs:
                    child_diffs[child_name] = nested_diffs

        if child_diffs:
            differences.update({"children": child_diffs})

        return True, differences
