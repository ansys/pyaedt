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

"""Substrate data block classes for Circuit designs."""

from __future__ import annotations

from ansys.aedt.core.base import PyAedtBase
from ansys.aedt.core.generic.constants import SubstrateType
from ansys.aedt.core.generic.file_utils import generate_unique_name
from ansys.aedt.core.generic.general_methods import pyaedt_function_handler


class SubstrateManager:
    """Manages substrate data blocks for a Circuit design.

    Provides methods to add, query, and delete substrate data blocks.
    Access this object via :attr:`ansys.aedt.core.Circuit.substrate`.

    Parameters
    ----------
    app : :class:`ansys.aedt.core.circuit.Circuit`
        Circuit application instance.

    Examples
    --------
    >>> from ansys.aedt.core import Circuit
    >>> cir = Circuit()
    >>> sub = cir.substrate.add_microstrip("10mil", 4.4, 0.02, "25mm", name="MySub")
    >>> cir.substrate.names
    ['MySub']
    >>> cir.substrate.delete("MySub")

    """

    def __init__(self, app) -> None:
        """
        Initialize SubstrateManager.

        Parameters
        ----------
        app : :class:`ansys.aedt.core.circuit.Circuit`
            Circuit application instance.

        """
        self._app = app

    @property
    def names(self) -> list[str]:
        """
        Return the names of all substrate data blocks in the active Circuit design.

        Returns
        -------
        list of str
            Names of every substrate data block currently defined in the design.

        Examples
        --------
        >>> cir.substrate.names
        ['Sub1']

        """
        result = self._app.odata_block.GetAllSubstrateDataBlocks()
        return list(result) if result else []

    @property
    def all(self) -> dict[str, "SubstrateDataBlock"]:
        """
        Get all substrates.

        Returns
        -------
        dict[str, SubstrateDataBlock]
            Dictionary mapping substrate name to :class:`SubstrateDataBlock` object.

        """
        if not self._app._substrates:
            props = self._app.design_properties
            if not props or "ControlBlocks" not in props or "SubstrateData" not in props["ControlBlocks"]:
                return self._app._substrates
            for entry in props["ControlBlocks"]["SubstrateData"]:
                try:
                    obj = SubstrateDataBlock.from_dict(self._app, entry)
                    self._app._substrates[obj.name] = obj
                except Exception:  # pragma: no cover
                    self._app.logger.warning(f"Failed to reconstruct substrate object from: {entry}")
        return self._app._substrates

    @pyaedt_function_handler()
    def delete(self, name: str) -> bool:
        """
        Delete a substrate data block.

        Parameters
        ----------
        name : str
            Name of the substrate to delete.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        References
        ----------
        >>> oModule.Remove

        """
        if name in self.names:
            self._app.odata_block.Remove(name)
            if name in self._app._substrates:
                del self._app._substrates[name]
            return True
        return False

    @pyaedt_function_handler()
    def add_microstrip(
        self,
        dielectric_height: str,
        dielectric_constant: float | int,
        dielectric_loss_tangent: float | int,
        air_height: str,
        roughness: str = "",
        metal_material: str = "copper",
        metal_thickness: str = "0.7mil",
        name: str | None = None,
    ) -> "SubstrateDataBlock":
        """
        Add a microstrip substrate data block to the circuit design.

        Parameters
        ----------
        dielectric_height : str
            Height of the dielectric layer, including units (for example, ``"10mil"``).
        dielectric_constant : float or int
            Relative permittivity (epsilon-r) of the dielectric.
        dielectric_loss_tangent : float or int
            Loss tangent of the dielectric.
        air_height : str
            Height of the air region above the substrate, including units.
        roughness : str, optional
            Conductor surface roughness value, including units. The default is ``""``.
        metal_material : str, optional
            Conductor material name. The default is ``"copper"``.
        metal_thickness : str, optional
            Conductor thickness, including units. The default is ``"0.7mil"``.
        name : str, optional
            Name of the substrate data block. If ``None``, a unique name is generated
            automatically. The default is ``None``.

        Returns
        -------
        :class:`ansys.aedt.core.modules.substrate_circuit.SubstrateDataBlock`
            Substrate data block object.

        Examples
        --------
        >>> sub = cir.substrate.add_microstrip("10mil", 4.4, 0.02, "25mm", roughness="1pm")

        """
        return SubstrateDataBlock.microstrip(
            self._app,
            dielectric_height=dielectric_height,
            dielectric_constant=dielectric_constant,
            loss_tangent=dielectric_loss_tangent,
            air_height=air_height,
            roughness=roughness,
            metal_material=metal_material,
            metal_thickness=metal_thickness,
            name=name,
        ).create()

    @pyaedt_function_handler()
    def add_stripline(
        self,
        dielectric_height: str,
        dielectric_constant: float | int,
        dielectric_loss_tangent: float | int,
        roughness: str = "",
        name: str | None = None,
        metal_material: str = "copper",
        metal_thickness: str = "0.7mil",
        bottom_metal_material: str = "",
        bottom_metal_thickness: str = "",
    ) -> "SubstrateDataBlock":
        """
        Add a stripline substrate data block to the circuit design.

        Parameters
        ----------
        dielectric_height : str
            Height of the dielectric layer between the conductor and the ground plane,
            including units (for example, ``"10mil"``).
        dielectric_constant : float or int
            Relative permittivity (epsilon-r) of the dielectric.
        dielectric_loss_tangent : float or int
            Loss tangent of the dielectric.
        roughness : str, optional
            Conductor surface roughness, including units. The default is ``""``.
        name : str, optional
            Name of the substrate data block. If ``None``, a unique name is generated
            automatically. The default is ``None``.
        metal_material : str, optional
            Top conductor material name. The default is ``"copper"``.
        metal_thickness : str, optional
            Top conductor thickness, including units. The default is ``"0.7mil"``.
        bottom_metal_material : str, optional
            Bottom conductor material name. The default is ``""``.
        bottom_metal_thickness : str, optional
            Bottom conductor thickness, including units. The default is ``""``.

        Returns
        -------
        :class:`ansys.aedt.core.modules.substrate_circuit.SubstrateDataBlock`
            Substrate data block object.

        Examples
        --------
        >>> sub = cir.substrate.add_stripline("20mil", 4.4, 0.02)

        """
        return SubstrateDataBlock.stripline(
            self._app,
            name=name,
            dielectric_height=dielectric_height,
            dielectric_constant=dielectric_constant,
            loss_tangent=dielectric_loss_tangent,
            roughness=roughness,
            metal_material=metal_material,
            metal_thickness=metal_thickness,
            bottom_metal_material=bottom_metal_material,
            bottom_metal_thickness=bottom_metal_thickness,
        ).create()

    @pyaedt_function_handler()
    def add_suspended_stripline(
        self,
        dielectric_height: str,
        air_height: str,
        dielectric_constant: float | int,
        dielectric_loss_tangent: float | int,
        roughness: str = "",
        name: str | None = None,
        metal_material: str = "copper",
        metal_thickness: str = "0.7mil",
    ) -> "SubstrateDataBlock":
        """
        Add a suspended stripline substrate data block to the circuit design.

        Parameters
        ----------
        dielectric_height : str
            Dielectric slab height, including units.
        air_height : str
            Air-gap height between the conductor and the dielectric slab, including units.
        dielectric_constant : float or int
            Relative permittivity (epsilon-r) of the dielectric.
        dielectric_loss_tangent : float or int
            Loss tangent of the dielectric.
        roughness : str, optional
            Conductor surface roughness, including units. The default is ``""``.
        name : str, optional
            Name of the substrate data block. If ``None``, a unique name is generated
            automatically. The default is ``None``.
        metal_material : str, optional
            Conductor material name. The default is ``"copper"``.
        metal_thickness : str, optional
            Conductor thickness, including units. The default is ``"0.7mil"``.

        Returns
        -------
        :class:`ansys.aedt.core.modules.substrate_circuit.SubstrateDataBlock`
            Substrate data block object.

        Examples
        --------
        >>> sub = cir.substrate.add_suspended_stripline("1mm", "0.5mm", 2.2, 0.0)

        """
        return SubstrateDataBlock.suspended_stripline(
            self._app,
            name=name,
            dielectric_height=dielectric_height,
            air_height=air_height,
            dielectric_constant=dielectric_constant,
            loss_tangent=dielectric_loss_tangent,
            roughness=roughness,
            metal_material=metal_material,
            metal_thickness=metal_thickness,
        ).create()

    @pyaedt_function_handler()
    def add_offset_stripline(
        self,
        dielectric_height: str,
        dielectric_constant: float | int,
        dielectric_loss_tangent: float | int,
        enclosure_width: str,
        enclosure_height: str,
        roughness: str = "",
        name: str | None = None,
        metal_material: str = "copper",
        metal_thickness: str = "0.7mil",
    ) -> "SubstrateDataBlock":
        """
        Add an offset stripline substrate data block to the circuit design.

        Parameters
        ----------
        dielectric_height : str
            Dielectric layer height, including units.
        dielectric_constant : float or int
            Relative permittivity (epsilon-r) of the dielectric.
        dielectric_loss_tangent : float or int
            Loss tangent of the dielectric.
        enclosure_width : str
            Enclosure width, including units.
        enclosure_height : str
            Enclosure height, including units.
        roughness : str, optional
            Conductor surface roughness, including units. The default is ``""``.
        name : str, optional
            Name of the substrate data block. If ``None``, a unique name is generated
            automatically. The default is ``None``.
        metal_material : str, optional
            Conductor material name. The default is ``"copper"``.
        metal_thickness : str, optional
            Conductor thickness, including units. The default is ``"0.7mil"``.

        Returns
        -------
        :class:`ansys.aedt.core.modules.substrate_circuit.SubstrateDataBlock`
            Substrate data block object.

        Examples
        --------
        >>> sub = cir.substrate.add_offset_stripline("1mm", 2.2, 0.0, "25mm", "25mm")

        """
        return SubstrateDataBlock.offset_stripline(
            self._app,
            name=name,
            dielectric_height=dielectric_height,
            dielectric_constant=dielectric_constant,
            loss_tangent=dielectric_loss_tangent,
            enclosure_width=enclosure_width,
            enclosure_height=enclosure_height,
            roughness=roughness,
            metal_material=metal_material,
            metal_thickness=metal_thickness,
        ).create()

    @pyaedt_function_handler()
    def add_coplanar_waveguide(
        self,
        dielectric_height: str,
        dielectric_constant: float | int,
        dielectric_loss_tangent: float | int,
        cover_height: str,
        roughness: str = "",
        name: str | None = None,
        metal_material: str = "copper",
        metal_thickness: str = "0.7mil",
        cover_metal_material: str = "",
        cover_metal_thickness: str = "",
    ) -> "SubstrateDataBlock":
        """
        Add a coplanar waveguide (CPW) substrate data block to the circuit design.

        Parameters
        ----------
        dielectric_height : str
            Dielectric layer height, including units.
        dielectric_constant : float or int
            Relative permittivity (epsilon-r) of the dielectric.
        dielectric_loss_tangent : float or int
            Loss tangent of the dielectric.
        cover_height : str
            Height from the conductor to the metallic cover, including units.
        roughness : str, optional
            Conductor surface roughness, including units. The default is ``""``.
        name : str, optional
            Name of the substrate data block. If ``None``, a unique name is generated
            automatically. The default is ``None``.
        metal_material : str, optional
            Strip conductor material. The default is ``"copper"``.
        metal_thickness : str, optional
            Strip conductor thickness, including units. The default is ``"0.7mil"``.
        cover_metal_material : str, optional
            Cover conductor material. The default is ``""``.
        cover_metal_thickness : str, optional
            Cover conductor thickness, including units. The default is ``""``.

        Returns
        -------
        :class:`ansys.aedt.core.modules.substrate_circuit.SubstrateDataBlock`
            Substrate data block object.

        Examples
        --------
        >>> sub = cir.substrate.add_coplanar_waveguide("1mm", 2.2, 0.0, "25mm")

        """
        return SubstrateDataBlock.coplanar_waveguide(
            self._app,
            name=name,
            dielectric_height=dielectric_height,
            dielectric_constant=dielectric_constant,
            loss_tangent=dielectric_loss_tangent,
            cover_height=cover_height,
            roughness=roughness,
            metal_material=metal_material,
            metal_thickness=metal_thickness,
            cover_metal_material=cover_metal_material,
            cover_metal_thickness=cover_metal_thickness,
        ).create()

    @pyaedt_function_handler()
    def add_grounded_coplanar_waveguide(
        self,
        dielectric_height: str,
        dielectric_constant: float | int,
        dielectric_loss_tangent: float | int,
        bottom_air_height: str,
        top_air_height: str,
        roughness: str = "",
        name: str | None = None,
        metal_material: str = "copper",
        metal_thickness: str = "0.7mil",
    ) -> "SubstrateDataBlock":
        """
        Add a grounded coplanar waveguide (GCPW) substrate data block to the circuit design.

        Parameters
        ----------
        dielectric_height : str
            Dielectric slab height, including units.
        dielectric_constant : float or int
            Relative permittivity (epsilon-r) of the dielectric.
        dielectric_loss_tangent : float or int
            Loss tangent of the dielectric.
        bottom_air_height : str
            Air gap below the dielectric slab, including units.
        top_air_height : str
            Air gap above the dielectric slab, including units.
        roughness : str, optional
            Conductor surface roughness, including units. The default is ``""``.
        name : str, optional
            Name of the substrate data block. If ``None``, a unique name is generated
            automatically. The default is ``None``.
        metal_material : str, optional
            Conductor material. The default is ``"copper"``.
        metal_thickness : str, optional
            Conductor thickness, including units. The default is ``"0.7mil"``.

        Returns
        -------
        :class:`ansys.aedt.core.modules.substrate_circuit.SubstrateDataBlock`
            Substrate data block object.

        Examples
        --------
        >>> sub = cir.substrate.add_grounded_coplanar_waveguide("1mm", 2.2, 0.0, "5mm", "5mm")

        """
        return SubstrateDataBlock.grounded_coplanar_waveguide(
            self._app,
            name=name,
            dielectric_height=dielectric_height,
            dielectric_constant=dielectric_constant,
            loss_tangent=dielectric_loss_tangent,
            bottom_air_height=bottom_air_height,
            top_air_height=top_air_height,
            roughness=roughness,
            metal_material=metal_material,
            metal_thickness=metal_thickness,
        ).create()

    @pyaedt_function_handler()
    def add_slotline(
        self,
        dielectric_height: str,
        dielectric_constant: float | int,
        dielectric_loss_tangent: float | int,
        bottom_air_height: str,
        top_air_height: str,
        roughness: str = "",
        name: str | None = None,
        metal_material: str = "copper",
        metal_thickness: str = "0.7mil",
    ) -> "SubstrateDataBlock":
        """
        Add a slotline substrate data block to the circuit design.

        Parameters
        ----------
        dielectric_height : str
            Dielectric slab height, including units.
        dielectric_constant : float or int
            Relative permittivity (epsilon-r) of the dielectric.
        dielectric_loss_tangent : float or int
            Loss tangent of the dielectric.
        bottom_air_height : str
            Air gap below the dielectric slab, including units.
        top_air_height : str
            Air gap above the dielectric slab, including units.
        roughness : str, optional
            Conductor surface roughness, including units. The default is ``""``.
        name : str, optional
            Name of the substrate data block. If ``None``, a unique name is generated
            automatically. The default is ``None``.
        metal_material : str, optional
            Conductor material. The default is ``"copper"``.
        metal_thickness : str, optional
            Conductor thickness, including units. The default is ``"0.7mil"``.

        Returns
        -------
        :class:`ansys.aedt.core.modules.substrate_circuit.SubstrateDataBlock`
            Substrate data block object.

        Examples
        --------
        >>> sub = cir.substrate.add_slotline("1mm", 2.2, 0.0, "5mm", "5mm")

        """
        return SubstrateDataBlock.slotline(
            self._app,
            name=name,
            dielectric_height=dielectric_height,
            dielectric_constant=dielectric_constant,
            loss_tangent=dielectric_loss_tangent,
            bottom_air_height=bottom_air_height,
            top_air_height=top_air_height,
            roughness=roughness,
            metal_material=metal_material,
            metal_thickness=metal_thickness,
        ).create()

    @pyaedt_function_handler()
    def add_rectangular_waveguide(
        self,
        num_layers: int,
        roughness: str = "",
        name: str | None = None,
        metal_material: str = "copper",
        metal_thickness: str = "0.7mil",
    ) -> "SubstrateDataBlock":
        """
        Add a rectangular waveguide substrate data block to the circuit design.

        Parameters
        ----------
        num_layers : int
            Number of dielectric layers in the stack.
        roughness : str, optional
            Conductor surface roughness, including units. The default is ``""``.
        name : str, optional
            Name of the substrate data block. If ``None``, a unique name is generated
            automatically. The default is ``None``.
        metal_material : str, optional
            Conductor material. The default is ``"copper"``.
        metal_thickness : str, optional
            Conductor thickness, including units. The default is ``"0.7mil"``.

        Returns
        -------
        :class:`ansys.aedt.core.modules.substrate_circuit.SubstrateDataBlock`
            Substrate data block object.

        Examples
        --------
        >>> sub = cir.substrate.add_rectangular_waveguide(num_layers=3)

        """
        return SubstrateDataBlock.rectangular_waveguide(
            self._app,
            name=name,
            num_layers=num_layers,
            roughness=roughness,
            metal_material=metal_material,
            metal_thickness=metal_thickness,
        ).create()

    @pyaedt_function_handler()
    def add_substrate_reference(
        self,
        dielectric_height: str,
        dielectric_constant: float | int,
        dielectric_loss_tangent: float | int,
        air_height: str,
        roughness: str = "",
        name: str | None = None,
        metal_material: str = "copper",
        metal_thickness: str = "0.7mil",
    ) -> "SubstrateDataBlock":
        """
        Add a substrate reference data block to the circuit design.

        A substrate reference is a named substrate used as a reference by
        transmission-line models in the schematic.

        Parameters
        ----------
        dielectric_height : str
            Dielectric layer height, including units.
        dielectric_constant : float or int
            Relative permittivity (epsilon-r) of the dielectric.
        dielectric_loss_tangent : float or int
            Loss tangent of the dielectric.
        air_height : str
            Air-region height, including units.
        roughness : str, optional
            Conductor surface roughness, including units. The default is ``""``.
        name : str, optional
            Name of the substrate data block. If ``None``, a unique name is generated
            automatically. The default is ``None``.
        metal_material : str, optional
            Conductor material. The default is ``"copper"``.
        metal_thickness : str, optional
            Conductor thickness, including units. The default is ``"0.7mil"``.

        Returns
        -------
        :class:`ansys.aedt.core.modules.substrate_circuit.SubstrateDataBlock`
            Substrate data block object.

        Examples
        --------
        >>> sub = cir.substrate.add_substrate_reference("1mm", 2.2, 0.0, "25mm")

        """
        return SubstrateDataBlock.substrate_reference(
            self._app,
            name=name,
            dielectric_height=dielectric_height,
            dielectric_constant=dielectric_constant,
            loss_tangent=dielectric_loss_tangent,
            air_height=air_height,
            roughness=roughness,
            metal_material=metal_material,
            metal_thickness=metal_thickness,
        ).create()


class SubstrateDataBlock(PyAedtBase):
    """Represents a substrate data block and provides the API to create it.

    Use the class-level factory methods (``microstrip``, ``stripline``, ...) to
    instantiate a correctly configured object, then call :meth:`create` to push it
    to AEDT.  Alternatively, pass *all* raw keyword arguments directly to the
    constructor for full control.

    Parameters
    ----------
    app : :class:`ansys.aedt.core.circuit.Circuit`
        Circuit application instance.
    name : str
        Unique name for the substrate data block.
    substrate_type : int
        One of the integer constants defined in :class:`SubstrateType`.
    dielectric : list of str
        List of dielectric parameters whose content depends on *substrate_type*.
    metal_material : str, optional
        Name of the primary conductor material. The default is ``"copper"``.
    metal_thickness : str, optional
        Primary conductor thickness including units.  The default is ``"0.7mil"``.
    bottom_metal_material : str, optional
        Name of the second (bottom) conductor material.
        The default is ``""`` (not specified).
    bottom_metal_thickness : str, optional
        Second conductor thickness. The default is ``""`` (not specified).
    cover_metal_material : str, optional
        Name of the third (cover) conductor material. The default is ``""`` (not specified).
    cover_metal_thickness : str, optional
        Third conductor thickness. The default is ``""`` (not specified).
    roughness : str, optional
        Surface roughness of the conductor including units. The default is ``""`` (not specified).
    metal_specify_type : int, optional
        Metal specification type flag used by AEDT. The default is ``0``.
    metal_temp_material : str, optional
        Temporary metal material name used by AEDT during parameter sweeps.
        The default is ``""`` (not specified).
    dielectric_temp_materials : list of str, optional
        List of up to five temporary dielectric material names used by AEDT
        during parameter sweeps. The default is five empty strings.

    Examples
    --------
    Create a microstrip substrate via the factory method:

    >>> from ansys.aedt.core import Circuit
    >>> cir = Circuit()
    >>> sub = SubstrateDataBlock.microstrip(
    ...     cir,
    ...     name="MySub",
    ...     dielectric_height="10mil",
    ...     dielectric_constant=4.4,
    ...     loss_tangent=0.02,
    ...     air_height="25mm",
    ...     roughness="1pm",
    ... )
    >>> sub.create()

    Create a stripline substrate:

    >>> sub = SubstrateDataBlock.stripline(
    ...     cir,
    ...     name="MyStripline",
    ...     dielectric_height="20mil",
    ...     dielectric_constant=4.4,
    ...     loss_tangent=0.02,
    ...     roughness="",
    ... )
    >>> sub.create()

    """

    def __init__(
        self,
        app,
        name: str | None,
        substrate_type: "SubstrateType",
        dielectric: list,
        metal_material: str = "copper",
        metal_thickness: str = "0.7mil",
        bottom_metal_material: str = "",
        bottom_metal_thickness: str = "",
        cover_metal_material: str = "",
        cover_metal_thickness: str = "",
        roughness: str = "",
        metal_specify_type: int = 0,
        metal_temp_material: str = "",
        dielectric_temp_materials: list | None = None,
    ) -> None:
        """Initialize SubstrateDataBlock."""
        self._app = app
        # Disable during construction to avoid triggering updates before the object is fully initialized
        self._auto_update = False

        # Handle name assignment and uniqueness
        if not name:
            self._name = generate_unique_name("Substrate")
        elif name in self._app.substrates:
            new_name = generate_unique_name(name)
            app.logger.warning(
                f"Substrate data block '{name}' already exists in the design. Using '{new_name}' instead."
            )
            self._name = new_name
        else:
            self._name = name
        self._substrate_type = substrate_type
        self._dielectric = dielectric
        self._metal_material = metal_material
        self._metal_thickness = metal_thickness
        self._bottom_metal_material = bottom_metal_material
        self._bottom_metal_thickness = bottom_metal_thickness
        self._cover_metal_material = cover_metal_material
        self._cover_metal_thickness = cover_metal_thickness
        self._roughness = roughness
        self._metal_specify_type = metal_specify_type
        self._metal_temp_material = metal_temp_material
        self._dielectric_temp_materials = (
            dielectric_temp_materials if dielectric_temp_materials is not None else ["", "", "", "", ""]
        )

        # Ensure exactly 5 entries
        while len(self._dielectric_temp_materials) < 5:
            self._dielectric_temp_materials.append("")

        # Enable after construction
        self._auto_update = True

    @property
    def auto_update(self) -> bool:
        """Whether to push changes to AEDT immediately when a property is set."""
        return self._auto_update

    @auto_update.setter
    def auto_update(self, value: bool) -> None:
        self._auto_update = bool(value)

    @property
    def name(self) -> str:
        """Substrate name."""
        return self._name

    @name.setter
    def name(self, new_name: str) -> None:
        if new_name == self.name:
            return

        if new_name in self._app.substrate.names:
            old_name = new_name
            new_name = generate_unique_name(new_name)
            self._app.logger.warning(
                f"Substrate data block '{old_name}' already exists in the design. Using '{new_name}' instead."
            )
        self._app.odata_block.Rename(self._name, new_name)

        # Update substrates dictionary
        self._app._substrates[new_name] = self._app._substrates[self._name]
        del self._app._substrates[self._name]

        self._name = new_name

    @property
    def substrate_type(self):
        """Substrate type."""
        return self._substrate_type

    @substrate_type.setter
    def substrate_type(self, value) -> None:
        self._substrate_type = value
        if self.auto_update:
            self.update()

    @property
    def dielectric(self) -> list:
        """Dielectric parameters."""
        return self._dielectric

    @dielectric.setter
    def dielectric(self, value: list) -> None:
        self._dielectric = value
        if self.auto_update:
            self.update()

    @property
    def metal_material(self) -> str:
        """Primary conductor material name."""
        return self._metal_material

    @metal_material.setter
    def metal_material(self, value: str) -> None:
        self._metal_material = value
        if self.auto_update:
            self.update()

    @property
    def metal_thickness(self) -> str:
        """Primary conductor thickness."""
        return self._metal_thickness

    @metal_thickness.setter
    def metal_thickness(self, value: str) -> None:
        self._metal_thickness = value
        if self.auto_update:
            self.update()

    @property
    def bottom_metal_material(self) -> str:
        """Bottom conductor material name."""
        return self._bottom_metal_material

    @bottom_metal_material.setter
    def bottom_metal_material(self, value: str) -> None:
        self._bottom_metal_material = value
        if self.auto_update:
            self.update()

    @property
    def bottom_metal_thickness(self) -> str:
        """Bottom conductor thickness."""
        return self._bottom_metal_thickness

    @bottom_metal_thickness.setter
    def bottom_metal_thickness(self, value: str) -> None:
        self._bottom_metal_thickness = value
        if self.auto_update:
            self.update()

    @property
    def cover_metal_material(self) -> str:
        """Cover conductor material name."""
        return self._cover_metal_material

    @cover_metal_material.setter
    def cover_metal_material(self, value: str) -> None:
        self._cover_metal_material = value
        if self.auto_update:
            self.update()

    @property
    def cover_metal_thickness(self) -> str:
        """Cover conductor thickness."""
        return self._cover_metal_thickness

    @cover_metal_thickness.setter
    def cover_metal_thickness(self, value: str) -> None:
        self._cover_metal_thickness = value
        if self.auto_update:
            self.update()

    @property
    def roughness(self) -> str:
        """Conductor surface roughness."""
        return self._roughness

    @roughness.setter
    def roughness(self, value: str) -> None:
        self._roughness = value
        if self.auto_update:
            self.update()

    @property
    def metal_specify_type(self) -> int:
        """Metal specification type flag."""
        return self._metal_specify_type

    @metal_specify_type.setter
    def metal_specify_type(self, value: int) -> None:
        self._metal_specify_type = value
        if self.auto_update:
            self.update()

    @property
    def metal_temp_material(self) -> str:
        """Temporary metal material name."""
        return self._metal_temp_material

    @metal_temp_material.setter
    def metal_temp_material(self, value: str) -> None:
        self._metal_temp_material = value
        if self.auto_update:
            self.update()

    @property
    def dielectric_temp_materials(self) -> list:
        """Temporary dielectric material names (list of 5)."""
        return self._dielectric_temp_materials

    @dielectric_temp_materials.setter
    def dielectric_temp_materials(self, value: list) -> None:
        self._dielectric_temp_materials = value
        if self.auto_update:
            self.update()

    @classmethod
    def microstrip(
        cls,
        app,
        dielectric_height: str = "1mm",
        dielectric_constant: float = 2.2,
        loss_tangent: float = 0.0,
        air_height: str = "25mm",
        roughness: str = "",
        metal_material: str = "copper",
        metal_thickness: str = "0.7mil",
        name: str | None = None,
    ) -> "SubstrateDataBlock":
        """
        Create a microstrip substrate.

        Parameters
        ----------
        app : :class:`ansys.aedt.core.circuit.Circuit`
            Circuit application instance.
        dielectric_height : str, optional
            Dielectric layer height with units.  The default is ``"1mm"``.
        dielectric_constant : float, optional
            Relative permittivity (εr).  The default is ``2.2``.
        loss_tangent : float, optional
            Dielectric loss tangent.  The default is ``0.0``.
        air_height : str, optional
            Air-region height above the substrate with units.  The default is ``"25mm"``.
        roughness : str, optional
            Conductor surface roughness with units.  The default is ``""``.
        name : str, optional
            Substrate name.  A unique name is generated when ``None``.
        metal_material : str, optional
            Conductor material name.  The default is ``"copper"``.
        metal_thickness : str, optional
            Conductor thickness with units.  The default is ``"0.7mil"``.

        Returns
        -------
        SubstrateDataBlock

        """
        dielectric = [
            dielectric_height,
            str(dielectric_constant),
            str(loss_tangent),
            air_height,
            "0",
            "0",
            "0",
        ]
        return cls(
            app,
            name=name,
            substrate_type=SubstrateType.Microstrip,
            dielectric=dielectric,
            metal_material=metal_material,
            metal_thickness=metal_thickness,
            roughness=roughness,
        )

    @classmethod
    def stripline(
        cls,
        app,
        dielectric_height: str = "1mm",
        dielectric_constant: float = 2.2,
        loss_tangent: float = 0.0,
        roughness: str = "",
        metal_material: str = "copper",
        metal_thickness: str = "0.7mil",
        name: str | None = None,
        bottom_metal_material: str = "",
        bottom_metal_thickness: str = "",
    ) -> "SubstrateDataBlock":
        """
        Create a stripline substrate (Type 1).

        Parameters
        ----------
        app : :class:`ansys.aedt.core.circuit.Circuit`
            Circuit application instance.
        dielectric_height : str, optional
            Dielectric height between the conductor and the ground plane with units.
            The default is ``"1mm"``.
        dielectric_constant : float, optional
            Relative permittivity (εr).  The default is ``2.2``.
        loss_tangent : float, optional
            Dielectric loss tangent.  The default is ``0.0``.
        roughness : str, optional
            Conductor roughness with units.  The default is ``""``.
        name : str, optional
            Substrate name.  A unique name is generated when ``None``.
        metal_material : str, optional
            Top conductor material.  The default is ``"copper"``.
        metal_thickness : str, optional
            Top conductor thickness with units.  The default is ``"0.7mil"``.
        bottom_metal_material : str, optional
            Bottom conductor material.  The default is ``""``.
        bottom_metal_thickness : str, optional
            Bottom conductor thickness with units.  The default is ``""``.

        Returns
        -------
        SubstrateDataBlock

        """
        dielectric = [dielectric_height, str(dielectric_constant), str(loss_tangent)]
        return cls(
            app,
            name=name,
            substrate_type=SubstrateType.Stripline,
            dielectric=dielectric,
            metal_material=metal_material,
            metal_thickness=metal_thickness,
            bottom_metal_material=bottom_metal_material,
            bottom_metal_thickness=bottom_metal_thickness,
            roughness=roughness,
        )

    @classmethod
    def suspended_stripline(
        cls,
        app,
        dielectric_height: str = "1mm",
        air_height: str = "0.5mm",
        dielectric_constant: float = 2.2,
        loss_tangent: float = 0.0,
        roughness: str = "",
        metal_material: str = "copper",
        metal_thickness: str = "0.7mil",
        name: str | None = None,
    ) -> "SubstrateDataBlock":
        """
        Create a suspended stripline substrate (Type 2).

        Parameters
        ----------
        app : :class:`ansys.aedt.core.circuit.Circuit`
            Circuit application instance.
        dielectric_height : str, optional
            Dielectric slab height with units.  The default is ``"1mm"``.
        air_height : str, optional
            Air-gap height between the conductor and the dielectric with units.
            The default is ``"0.5mm"``.
        dielectric_constant : float, optional
            Relative permittivity (εr).  The default is ``2.2``.
        loss_tangent : float, optional
            Dielectric loss tangent.  The default is ``0.0``.
        roughness : str, optional
            Conductor roughness with units.  The default is ``""``.
        name : str, optional
            Substrate name.  A unique name is generated when ``None``.
        metal_material : str, optional
            Conductor material.  The default is ``"copper"``.
        metal_thickness : str, optional
            Conductor thickness with units.  The default is ``"0.7mil"``.

        Returns
        -------
        SubstrateDataBlock

        """
        dielectric = [dielectric_height, air_height, str(dielectric_constant), str(loss_tangent)]
        return cls(
            app,
            name=name,
            substrate_type=SubstrateType.SuspendedStripline,
            dielectric=dielectric,
            metal_material=metal_material,
            metal_thickness=metal_thickness,
            roughness=roughness,
        )

    @classmethod
    def offset_stripline(
        cls,
        app,
        dielectric_height: str = "1mm",
        dielectric_constant: float = 2.2,
        loss_tangent: float = 0.0,
        enclosure_width: str = "25mm",
        enclosure_height: str = "25mm",
        roughness: str = "",
        metal_material: str = "copper",
        metal_thickness: str = "0.7mil",
        name: str | None = None,
    ) -> "SubstrateDataBlock":
        """
        Create an offset stripline substrate (Type 3).

        Parameters
        ----------
        app : :class:`ansys.aedt.core.circuit.Circuit`
            Circuit application instance.
        dielectric_height : str, optional
            Dielectric layer height with units.  The default is ``"1mm"``.
        dielectric_constant : float, optional
            Relative permittivity (εr).  The default is ``2.2``.
        loss_tangent : float, optional
            Dielectric loss tangent.  The default is ``0.0``.
        enclosure_width : str, optional
            Enclosure width with units.  The default is ``"25mm"``.
        enclosure_height : str, optional
            Enclosure height with units.  The default is ``"25mm"``.
        roughness : str, optional
            Conductor roughness with units.  The default is ``""``.
        name : str, optional
            Substrate name.  A unique name is generated when ``None``.
        metal_material : str, optional
            Conductor material.  The default is ``"copper"``.
        metal_thickness : str, optional
            Conductor thickness with units.  The default is ``"0.7mil"``.

        Returns
        -------
        SubstrateDataBlock

        """
        dielectric = [
            dielectric_height,
            str(dielectric_constant),
            str(loss_tangent),
            enclosure_width,
            enclosure_height,
        ]
        return cls(
            app,
            name=name,
            substrate_type=SubstrateType.OffsetStripline,
            dielectric=dielectric,
            metal_material=metal_material,
            metal_thickness=metal_thickness,
            roughness=roughness,
        )

    @classmethod
    def coplanar_waveguide(
        cls,
        app,
        dielectric_height: str = "1mm",
        dielectric_constant: float = 2.2,
        loss_tangent: float = 0.0,
        cover_height: str = "25mm",
        roughness: str = "",
        metal_material: str = "copper",
        metal_thickness: str = "0.7mil",
        name: str | None = None,
        cover_metal_material: str = "",
        cover_metal_thickness: str = "",
    ) -> "SubstrateDataBlock":
        """
        Create a coplanar waveguide (CPW) substrate (Type 4).

        Parameters
        ----------
        app : :class:`ansys.aedt.core.circuit.Circuit`
            Circuit application instance.
        dielectric_height : str, optional
            Dielectric layer height with units.  The default is ``"1mm"``.
        dielectric_constant : float, optional
            Relative permittivity (εr).  The default is ``2.2``.
        loss_tangent : float, optional
            Dielectric loss tangent.  The default is ``0.0``.
        cover_height : str, optional
            Height from the conductor to the metallic cover with units.
            The default is ``"25mm"``.
        roughness : str, optional
            Conductor roughness with units.  The default is ``""``.
        name : str, optional
            Substrate name.  A unique name is generated when ``None``.
        metal_material : str, optional
            Strip conductor material.  The default is ``"copper"``.
        metal_thickness : str, optional
            Strip conductor thickness with units.  The default is ``"0.7mil"``.
        cover_metal_material : str, optional
            Cover conductor material.  The default is ``""``.
        cover_metal_thickness : str, optional
            Cover conductor thickness with units.  The default is ``""``.

        Returns
        -------
        SubstrateDataBlock

        """
        dielectric = [dielectric_height, str(dielectric_constant), str(loss_tangent), cover_height]
        return cls(
            app,
            name=name,
            substrate_type=SubstrateType.CoplanarWaveguide,
            dielectric=dielectric,
            metal_material=metal_material,
            metal_thickness=metal_thickness,
            cover_metal_material=cover_metal_material,
            cover_metal_thickness=cover_metal_thickness,
            roughness=roughness,
        )

    @classmethod
    def grounded_coplanar_waveguide(
        cls,
        app,
        dielectric_height: str = "1mm",
        dielectric_constant: float = 2.2,
        loss_tangent: float = 0.0,
        bottom_air_height: str = "5mm",
        top_air_height: str = "5mm",
        roughness: str = "",
        metal_material: str = "copper",
        metal_thickness: str = "0.7mil",
        name: str | None = None,
    ) -> "SubstrateDataBlock":
        """
        Create a grounded coplanar waveguide (GCPW) substrate (Type 5).

        Parameters
        ----------
        app : :class:`ansys.aedt.core.circuit.Circuit`
            Circuit application instance.
        dielectric_height : str, optional
            Dielectric slab height with units.  The default is ``"1mm"``.
        dielectric_constant : float, optional
            Relative permittivity (εr).  The default is ``2.2``.
        loss_tangent : float, optional
            Dielectric loss tangent.  The default is ``0.0``.
        bottom_air_height : str, optional
            Air gap below the dielectric slab with units.  The default is ``"5mm"``.
        top_air_height : str, optional
            Air gap above the dielectric slab with units.  The default is ``"5mm"``.
        roughness : str, optional
            Conductor roughness with units.  The default is ``""``.
        name : str, optional
            Substrate name.  A unique name is generated when ``None``.
        metal_material : str, optional
            Conductor material.  The default is ``"copper"``.
        metal_thickness : str, optional
            Conductor thickness with units.  The default is ``"0.7mil"``.

        Returns
        -------
        SubstrateDataBlock

        """
        dielectric = [
            dielectric_height,
            str(dielectric_constant),
            str(loss_tangent),
            bottom_air_height,
            top_air_height,
        ]
        return cls(
            app,
            name=name,
            substrate_type=SubstrateType.GroundedCoplanarWaveguide,
            dielectric=dielectric,
            metal_material=metal_material,
            metal_thickness=metal_thickness,
            roughness=roughness,
        )

    @classmethod
    def slotline(
        cls,
        app,
        dielectric_height: str = "1mm",
        dielectric_constant: float = 2.2,
        loss_tangent: float = 0.0,
        bottom_air_height: str = "5mm",
        top_air_height: str = "5mm",
        roughness: str = "",
        metal_material: str = "copper",
        metal_thickness: str = "0.7mil",
        name: str | None = None,
    ) -> "SubstrateDataBlock":
        """
        Create a slotline substrate (Type 6).

        Parameters
        ----------
        app : :class:`ansys.aedt.core.circuit.Circuit`
            Circuit application instance.
        dielectric_height : str, optional
            Dielectric slab height with units.  The default is ``"1mm"``.
        dielectric_constant : float, optional
            Relative permittivity (εr).  The default is ``2.2``.
        loss_tangent : float, optional
            Dielectric loss tangent.  The default is ``0.0``.
        bottom_air_height : str, optional
            Air gap below the dielectric slab with units.  The default is ``"5mm"``.
        top_air_height : str, optional
            Air gap above the dielectric slab with units.  The default is ``"5mm"``.
        roughness : str, optional
            Conductor roughness with units.  The default is ``""``.
        name : str, optional
            Substrate name.  A unique name is generated when ``None``.
        metal_material : str, optional
            Conductor material.  The default is ``"copper"``.
        metal_thickness : str, optional
            Conductor thickness with units.  The default is ``"0.7mil"``.

        Returns
        -------
        SubstrateDataBlock

        """
        dielectric = [
            dielectric_height,
            str(dielectric_constant),
            str(loss_tangent),
            bottom_air_height,
            top_air_height,
        ]
        return cls(
            app,
            name=name,
            substrate_type=SubstrateType.Slotline,
            dielectric=dielectric,
            metal_material=metal_material,
            metal_thickness=metal_thickness,
            roughness=roughness,
        )

    @classmethod
    def rectangular_waveguide(
        cls,
        app,
        num_layers: int = 1,
        roughness: str = "",
        metal_material: str = "copper",
        metal_thickness: str = "0.7mil",
        name: str | None = None,
    ) -> "SubstrateDataBlock":
        """
        Create a rectangular waveguide substrate (Type 9).

        Parameters
        ----------
        app : :class:`ansys.aedt.core.circuit.Circuit`
            Circuit application instance.
        num_layers : int, optional
            Number of dielectric layers in the stack.  The default is ``1``.
        roughness : str, optional
            Conductor roughness with units.  The default is ``""``.
        name : str, optional
            Substrate name.  A unique name is generated when ``None``.
        metal_material : str, optional
            Conductor material.  The default is ``"copper"``.
        metal_thickness : str, optional
            Conductor thickness with units.  The default is ``"0.7mil"``.

        Returns
        -------
        SubstrateDataBlock

        """
        dielectric = [str(num_layers), "0", str(num_layers)]
        return cls(
            app,
            name=name,
            substrate_type=SubstrateType.RectangularWaveguide,
            dielectric=dielectric,
            metal_material=metal_material,
            metal_thickness=metal_thickness,
            roughness=roughness,
        )

    @classmethod
    def substrate_reference(
        cls,
        app,
        dielectric_height: str = "1mm",
        dielectric_constant: float = 2.2,
        loss_tangent: float = 0.0,
        air_height: str = "25mm",
        roughness: str = "",
        metal_material: str = "copper",
        metal_thickness: str = "0.7mil",
        name: str | None = None,
    ) -> "SubstrateDataBlock":
        """
        Create a substrate reference (Type 10).

        A substrate reference is a named substrate used as a reference by
        transmission-line models in the schematic.

        Parameters
        ----------
        app : :class:`ansys.aedt.core.circuit.Circuit`
            Circuit application instance.
        name : str, optional
            Substrate name.  A unique name is generated when ``None``.
        dielectric_height : str, optional
            Dielectric layer height with units.  The default is ``"1mm"``.
        dielectric_constant : float, optional
            Relative permittivity (εr).  The default is ``2.2``.
        loss_tangent : float, optional
            Dielectric loss tangent.  The default is ``0.0``.
        air_height : str, optional
            Air-region height with units.  The default is ``"25mm"``.
        roughness : str, optional
            Conductor roughness with units.  The default is ``""``.
        metal_material : str, optional
            Conductor material.  The default is ``"copper"``.
        metal_thickness : str, optional
            Conductor thickness with units.  The default is ``"0.7mil"``.

        Returns
        -------
        SubstrateDataBlock

        """
        dielectric = [
            dielectric_height,
            str(dielectric_constant),
            str(loss_tangent),
            air_height,
            "0.0",
            "0.0",
            "0.0",
        ]
        return cls(
            app,
            name=name,
            substrate_type=SubstrateType.SubstrateReference,
            dielectric=dielectric,
            metal_material=metal_material,
            metal_thickness=metal_thickness,
            roughness=roughness,
        )

    @classmethod
    def from_dict(cls, app, data: dict) -> "SubstrateDataBlock":
        """
        Build `SubstrateDataBlock` from ``design_properties`` dict entry.

        Parameters
        ----------
        app : :class:`ansys.aedt.core.circuit.Circuit`
            Circuit application instance.
        data : dict
            One entry from ``app.design_properties['SubstrateData']``.

        Returns
        -------
        SubstrateDataBlock
            Reconstructed substrate object.

        """
        import re as _re

        name = data.get("Name", "")
        substrate_type = SubstrateType(int(data.get("Type", 0)))
        dielectric = list(data.get("Dielectric", []))
        metal_specify_type = int(data.get("MetalSpecifyType", 0))
        metal_temp_material = data.get("MetalTempMaterial", "")
        dielectric_temp_materials = [
            data.get("DielecTempMaterial0", ""),
            data.get("DielecTempMaterial1", ""),
            data.get("DielecTempMaterial2", ""),
            data.get("DielecTempMaterial3", ""),
            data.get("DielecTempMaterial4", ""),
        ]

        # Parse Metalization list:
        # Format: ["Metal('mat'", "res", "'thick')", "Metal('mat2'", ...], "Roughness('val')"]
        metals: list[list[str]] = []
        roughness = ""
        met_list = data.get("Metalization", [])
        i = 0
        while i < len(met_list):
            entry = str(met_list[i])
            if entry.startswith("Metal("):
                mat_raw = entry  # e.g. "Metal('copper'"
                mat_match = _re.search(r"Metal\('([^']*)'\s*$|Metal\('([^']*)'", mat_raw)
                metal_mat = ""
                if mat_match:
                    metal_mat = mat_match.group(1) or mat_match.group(2) or ""
                res_raw = str(met_list[i + 1]) if i + 1 < len(met_list) else ""
                try:
                    res_val = float(res_raw) if res_raw else ""
                except ValueError:
                    res_val = res_raw
                thick_raw = str(met_list[i + 2]) if i + 2 < len(met_list) else ""
                thick_match = _re.search(r"'([^']*)'", thick_raw)
                metal_thick = thick_match.group(1) if thick_match else thick_raw
                metals.append([metal_mat, res_val, metal_thick])
                i += 3
            elif entry.startswith("Roughness("):
                rough_match = _re.search(r"Roughness\('([^']*)'\)", entry)
                roughness = rough_match.group(1) if rough_match else ""
                i += 1
            else:
                i += 1

        def _get_metal(idx):
            if idx < len(metals):
                return metals[idx]
            return ["", "", ""]

        m0 = _get_metal(0)
        m1 = _get_metal(1)
        m2 = _get_metal(2)

        # Bypass name uniqueness check and auto_update during reconstruction
        obj = object.__new__(cls)
        obj._app = app
        obj._auto_update = False
        obj._name = name
        obj._substrate_type = substrate_type
        obj._dielectric = dielectric
        obj._metal_material = m0[0]
        obj._metal_thickness = m0[2]
        obj._bottom_metal_material = m1[0]
        obj._bottom_metal_thickness = m1[2]
        obj._cover_metal_material = m2[0]
        obj._cover_metal_thickness = m2[2]
        obj._roughness = roughness
        obj._metal_specify_type = metal_specify_type
        obj._metal_temp_material = metal_temp_material
        obj._dielectric_temp_materials = dielectric_temp_materials
        obj._auto_update = True
        return obj

    def _build_args(self) -> list:
        """Build the argument list for ``AddSubstrateDataBlock``."""
        dielec_temps = self.dielectric_temp_materials[:5]
        metalization = [
            "Metal:=",
            [self.metal_material, "", self.metal_thickness],
            "Metal:=",
            [self.bottom_metal_material, "", self.bottom_metal_thickness],
            "Metal:=",
            [self.cover_metal_material, "", self.cover_metal_thickness],
            "Roughness:=",
            [self.roughness],
        ]
        return [
            "NAME:DataBlock",
            "Name:=",
            self.name,
            "Type:=",
            int(self.substrate_type),
            "MetalSpecifyType:=",
            self.metal_specify_type,
            "DielecTempMaterial0:=",
            dielec_temps[0],
            "DielecTempMaterial1:=",
            dielec_temps[1],
            "DielecTempMaterial2:=",
            dielec_temps[2],
            "DielecTempMaterial3:=",
            dielec_temps[3],
            "DielecTempMaterial4:=",
            dielec_temps[4],
            "MetalTempMaterial:=",
            self.metal_temp_material,
            "Dielectric:=",
            self.dielectric,
            "DielectricRef:=",
            [0, ""],
            "Metalization:=",
            metalization,
        ]

    @pyaedt_function_handler()
    def create(self) -> "SubstrateDataBlock":
        """
        Push the substrate data block to the active Circuit design.

        Returns
        -------
        SubstrateDataBlock
            The current instance (``self``) so the call can be chained.

        Examples
        --------
        >>> from ansys.aedt.core import Circuit
        >>> from ansys.aedt.core.modules.substrate_circuit import SubstrateDataBlock
        >>> cir = Circuit()
        >>> sub = SubstrateDataBlock.microstrip(cir, "MySub", "10mil", 4.4, 0.02, "25mm")
        >>> sub.create()

        """
        from ansys.aedt.core.internal.errors import AEDTRuntimeError

        try:
            self._app.odata_block.AddSubstrateDataBlock(self._build_args())
            self._app._substrates[self.name] = self
        except Exception as e:  # pragma: no cover
            raise AEDTRuntimeError(f"Failed to create substrate data block '{self.name}': {e}") from e
        return self

    @pyaedt_function_handler()
    def update(self) -> bool:
        """
        Push the current state of this substrate data block to AEDT.

        Use this method to apply changes after setting one or more properties
        with :attr:`auto_update` set to ``False``, or to force a refresh at
        any time.

        Returns
        -------
        bool
            ``True`` when successful.

        References
        ----------
        >>> oModule.EditSubstrateDataBlock

        Examples
        --------
        Batch update several parameters at once:

        >>> sub = cir.substrate.all["MySub"]
        >>> sub.auto_update = False
        >>> sub.metal_material = "aluminum"
        >>> sub.metal_thickness = "1mil"
        >>> sub.roughness = "2pm"
        >>> sub.auto_update = True
        >>> sub.update()

        """
        from ansys.aedt.core.internal.errors import AEDTRuntimeError

        try:
            self._app.odata_block.EditSubstrateDataBlock(self.name, self._build_args())
        except Exception as e:  # pragma: no cover
            raise AEDTRuntimeError(f"Failed to update substrate data block '{self.name}': {e}") from e
        return True
