#
# Copyright (C) 2021 - 2026 Synopsys, Inc. and ANSYS, Inc. All rights reserved.
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

"""Typed, validated configuration model for a routed cable bundle.

The YAML/JSON/TOML schema used by the CAT6A S/STP example is parsed into a small
tree of frozen-ish dataclasses.  The goal is threefold:

1. **Fail fast.**  Structural mistakes (missing radii, empty routes, a differential
   pair that references an unknown conductor) are caught in
   :meth:`CableBundleConfig.validate` *before* any AEDT object is created.
2. **Discoverability.**  IDEs and ``mypy``/``ty`` can autocomplete
   ``cfg.geometry.pair_shield_radius`` instead of
   ``cfg["simulation"]["geometry"][...]``.
3. **Forward compatibility.**  Every node keeps the original mapping in ``.raw``
   so "under construction" YAML keys (drain wires, overlap widths, separators)
   remain accessible without a schema bump.

Only fields that the builder actually consumes are promoted to typed attributes;
everything else stays reachable through ``.raw``.
"""

from __future__ import annotations

from dataclasses import dataclass
from dataclasses import field
import json
import pathlib
from typing import Any

import numpy as np

import ansys.aedt.core
from ansys.aedt.core.generic.file_utils import read_configuration_file
from ansys.aedt.core.internal.errors import AEDTRuntimeError

__all__ = [
    "Bundle",
    "CableBundleConfig",
    "Conductor",
    "CrossSection",
    "GeometrySettings",
    "GroundPlane",
    "Insulation",
    "Material",
    "Pair",
    "PortSettings",
    "Route",
    "Shield",
    "Simulation",
    "Terminations",
    "Transient",
    "TransientSource",
]


@dataclass
class Material:
    """Represent a single material entry from the ``materials`` mapping.

    Parameters
    ----------
    name : str
        Unique material name.
    conductivity : float or None, optional
        Electrical conductivity in S/m.
    relative_permittivity : float or None, optional
        Relative permittivity (dielectric constant).
    loss_tangent : float or None, optional
        Dielectric loss tangent.
    raw : dict, optional
        Original mapping for forward-compatibility access.
    """

    name: str
    conductivity: float | None = None
    relative_permittivity: float | None = None
    loss_tangent: float | None = None
    raw: dict[str, Any] = field(default_factory=dict)


@dataclass
class Conductor:
    """Represent a single wire in the ``conductors`` mapping.

    Parameters
    ----------
    name : str
        Unique conductor name.
    equivalent_radius : float
        Equivalent solid-wire radius.
    awg : int or None, optional
        American Wire Gauge specification.
    strand_count : int or None, optional
        Number of strands for a stranded conductor.
    raw : dict, optional
        Original mapping for forward-compatibility access.
    """

    name: str
    equivalent_radius: float
    awg: int | None = None
    strand_count: int | None = None
    raw: dict[str, Any] = field(default_factory=dict)


@dataclass
class Insulation:
    """Represent a per-wire dielectric jacket.

    Parameters
    ----------
    material : str
        Name of the insulation material (must be declared in ``materials``).
    outer_radius : float
        Outer radius of the insulation jacket.
    raw : dict, optional
        Original mapping for forward-compatibility access.
    """

    material: str
    outer_radius: float
    raw: dict[str, Any] = field(default_factory=dict)


@dataclass
class Shield:
    """Represent a foil or braid shield, either per-pair or bundle-wide.

    Parameters
    ----------
    kind : str
        Shield type: ``'foil'``, ``'braid'``, or ``'none'``.
    material : str or None, optional
        Material name of the shield conductor.
    thickness : float or None, optional
        Foil or tape thickness.
    construction : dict, optional
        Shield construction details (seam type, wire diameter, etc.).
    raw : dict, optional
        Original mapping for forward-compatibility access.
    """

    kind: str
    material: str | None = None
    thickness: float | None = None
    construction: dict[str, Any] = field(default_factory=dict)
    raw: dict[str, Any] = field(default_factory=dict)

    @property
    def is_braid(self) -> bool:
        """Return ``True`` when the shield kind is ``'braid'``."""
        return self.kind == "braid"

    @property
    def is_foil(self) -> bool:
        """Return ``True`` when the shield kind is ``'foil'``."""
        return self.kind == "foil"


@dataclass
class Pair:
    """Represent a twisted pair: two member conductors plus an optional foil shield.

    Parameters
    ----------
    name : str
        Unique pair name.
    members : list of str
        Names of the two conductors forming this pair.
    twist_pitch : float
        Twist pitch length.
    shield : Shield or None, optional
        Per-pair foil shield, if present.
    raw : dict, optional
        Original mapping for forward-compatibility access.
    """

    name: str
    members: list[str]
    twist_pitch: float
    shield: Shield | None = None
    raw: dict[str, Any] = field(default_factory=dict)


@dataclass
class Bundle:
    """Represent the overall bundle: member pairs, overall shield and jacket.

    Parameters
    ----------
    name : str
        Unique bundle name.
    members : list of str
        Names of the pairs that form this bundle.
    jacket_material : str
        Name of the jacket material.
    jacket_outer_radius : float
        Outer radius of the cable jacket.
    overall_shield : Shield or None, optional
        Bundle-level shield (e.g. a braid), if present.
    separator : dict, optional
        Separator definition (under construction).
    raw : dict, optional
        Original mapping for forward-compatibility access.
    """

    name: str
    members: list[str]
    jacket_material: str
    jacket_outer_radius: float
    overall_shield: Shield | None = None
    separator: dict[str, Any] = field(default_factory=dict)
    raw: dict[str, Any] = field(default_factory=dict)


@dataclass
class CrossSection:
    """Represent nominal 2-D placement of each pair centre in the bundle cross-section.

    Parameters
    ----------
    layout : str
        Cross-section layout algorithm name (e.g. ``'quad'``).
    pair_locations : dict of str to tuple of float
        Mapping from pair name to ``(x, y)`` centre coordinates.
    raw : dict, optional
        Original mapping for forward-compatibility access.
    """

    layout: str
    pair_locations: dict[str, tuple[float, float]]
    raw: dict[str, Any] = field(default_factory=dict)


@dataclass
class Route:
    """Represent a named piecewise-linear route through 3-D space.

    Parameters
    ----------
    name : str
        Unique route name.
    points : numpy.ndarray
        Array of shape ``(N, 3)`` containing the route waypoints.
    """

    name: str
    points: np.ndarray

    def __post_init__(self) -> None:
        """Convert points to a float64 numpy array."""
        self.points = np.asarray(self.points, dtype=float)


@dataclass
class GroundPlane:
    """Represent an optional reference plane used for lumped ports.

    Parameters
    ----------
    enabled : bool, optional
        Whether the ground plane is active.
    distance_below_route : float, optional
        Distance from the route to the reference plane.
    size_margin : float, optional
        Amount by which the plane extends past the route bounding box.
    """

    enabled: bool = False
    distance_below_route: float = 10.0
    size_margin: float = 20.0


@dataclass
class GeometrySettings:
    """Represent faceting and radii that drive the explicit 3-D geometry.

    Parameters
    ----------
    facets : int, optional
        Number of polygon facets for circular cross-sections.
    samples_per_pitch : int, optional
        Number of helix samples per twist pitch.
    pair_wire_center_offset : float, optional
        Half-distance between the two wires of a pair.
    pair_shield_radius : float, optional
        Outer radius of the foil shield around each pair.
    overall_shield_radius : float, optional
        Radius of the braid/overall shield inside the jacket.
    tube_end_extension : float or None, optional
        Extension past the wire ends at both extremities.
    ground_plane : GroundPlane, optional
        Ground-plane settings for lumped-port reference.
    raw : dict, optional
        Original mapping for forward-compatibility access.
    """

    facets: int = 8
    samples_per_pitch: int = 8
    pair_wire_center_offset: float = 0.58
    pair_shield_radius: float = 1.15
    overall_shield_radius: float = 3.60
    tube_end_extension: float | None = None
    ground_plane: GroundPlane = field(default_factory=GroundPlane)
    raw: dict[str, Any] = field(default_factory=dict)


@dataclass
class PortSettings:
    """Represent port creation options.

    Parameters
    ----------
    kind : str, optional
        Port type: ``'lumped'``, ``'circuit'``, or ``'wave'``.
    reference : str, optional
        Port reference: ``'overall_shield'`` or ``'ground_plane'``.
    impedance : float, optional
        Renormalization impedance for S-parameters.
    raw : dict, optional
        Original mapping for forward-compatibility access.
    """

    kind: str = "lumped"
    reference: str = "overall_shield"
    impedance: float = 50.0
    raw: dict[str, Any] = field(default_factory=dict)


@dataclass
class TransientSource:
    """Represent a PWL excitation for the Circuit/Nexxim transient run.

    Parameters
    ----------
    kind : str
        Source waveform kind (e.g. ``'pwl'``).
    time : list of float
        Time breakpoints of the piecewise-linear waveform.
    amplitude : list of float
        Amplitude breakpoints of the piecewise-linear waveform.
    source_impedance : float
        Generator source impedance in ohms.
    raw : dict, optional
        Original mapping for forward-compatibility access.
    """

    kind: str
    time: list[float]
    amplitude: list[float]
    source_impedance: float
    raw: dict[str, Any] = field(default_factory=dict)


@dataclass
class Transient:
    """Represent Nexxim transient timing plus its source.

    Parameters
    ----------
    stop_time : float
        Simulation stop time in seconds.
    time_step : float
        Maximum time step in seconds.
    initial_step : float
        Initial time step in seconds.
    source : TransientSource
        Excitation source definition.
    raw : dict, optional
        Original mapping for forward-compatibility access.
    """

    stop_time: float
    time_step: float
    initial_step: float
    source: TransientSource
    raw: dict[str, Any] = field(default_factory=dict)


@dataclass
class Terminations:
    """Represent per-end resistive terminations for the transient schematic.

    Parameters
    ----------
    driven_conductor : str or None, optional
        Name of the conductor carrying the excitation.
    load_end : dict of str to float, optional
        Per-conductor load resistances at the far end.
    other_conductors_default : float, optional
        Default termination resistance for non-driven conductors.
    raw : dict, optional
        Original mapping for forward-compatibility access.
    """

    driven_conductor: str | None = None
    load_end: dict[str, float] = field(default_factory=dict)
    other_conductors_default: float = 50.0
    raw: dict[str, Any] = field(default_factory=dict)


@dataclass
class Simulation:
    """Represent the ``simulation`` block: sweep, ports, geometry, terminations, transient.

    Parameters
    ----------
    differential_pairs : list of tuple of str
        List of ``(conductorA, conductorB)`` pairs for differential excitation.
    frequency_start : float
        Start frequency of the sweep in Hz.
    frequency_stop : float
        Stop frequency of the sweep in Hz.
    geometry : GeometrySettings
        3-D geometry faceting and dimension settings.
    ports : PortSettings
        Port type and reference settings.
    terminations : Terminations
        Resistive termination settings.
    transient : Transient or None
        Transient simulation settings, or ``None`` if not used.
    characteristic_impedance_diff : float or None, optional
        Differential characteristic impedance target in ohms.
    raw : dict, optional
        Original mapping for forward-compatibility access.
    """

    differential_pairs: list[tuple[str, str]]
    frequency_start: float
    frequency_stop: float
    geometry: GeometrySettings
    ports: PortSettings
    terminations: Terminations
    transient: Transient | None
    characteristic_impedance_diff: float | None = None
    raw: dict[str, Any] = field(default_factory=dict)


@dataclass
class CableBundleConfig:
    """Represent the top-level, validated view of a cable-bundle configuration file.

    This class parses a YAML, JSON, or TOML file describing a routed explicit
    cable bundle into a typed dataclass tree and runs semantic cross-reference
    validation before returning.

    Parameters
    ----------
    units : str
        Dimensional unit for all lengths (e.g. ``'mm'``).
    materials : dict of str to Material
        Named material definitions.
    conductors : dict of str to Conductor
        Named conductor definitions.
    insulation : Insulation
        Wire insulation jacket definition.
    pairs : dict of str to Pair
        Named twisted-pair definitions.
    bundle : Bundle
        Cable-bundle definition (pairs, shield, jacket).
    cross_section : CrossSection
        2-D placement of pair centres in the bundle cross-section.
    routes : dict of str to Route
        Named piecewise-linear routes through 3-D space.
    simulation : Simulation
        Simulation sweep, geometry, port, and transient settings.
    harnesses : dict, optional
        Named harness instances mapping bundles to routes.
    raw : dict, optional
        Original top-level mapping for forward-compatibility access.

    Raises
    ------
    AEDTRuntimeError
        If schema validation fails or semantic cross-references are invalid.

    Examples
    --------
    >>> cfg = CableBundleConfig.from_file("bundle.yaml")
    >>> cfg.bundle.jacket_outer_radius
    4.0
    """

    units: str
    materials: dict[str, Material]
    conductors: dict[str, Conductor]
    insulation: Insulation
    pairs: dict[str, Pair]
    bundle: Bundle
    cross_section: CrossSection
    routes: dict[str, Route]
    simulation: Simulation
    harnesses: dict[str, Any] = field(default_factory=dict)
    raw: dict[str, Any] = field(default_factory=dict)

    # -- Construction ----------------------------------------------------------

    @classmethod
    def from_file(cls, path: str | pathlib.Path) -> CableBundleConfig:
        """Load and validate a configuration from a YAML, JSON, or TOML file.

        Parameters
        ----------
        path : str or pathlib.Path
            Path to the configuration file.  Supported extensions are
            ``.yaml``, ``.yml``, ``.json``, and ``.toml``.

        Returns
        -------
        CableBundleConfig
            Validated configuration object.

        Raises
        ------
        AEDTRuntimeError
            If the file cannot be parsed, fails JSON-schema structural
            validation, or fails semantic cross-reference validation.
        """
        data = read_configuration_file(pathlib.Path(path))
        return cls._from_dict_with_schema_check(data)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> CableBundleConfig:
        """Build and validate a configuration from an already-parsed mapping.

        Parameters
        ----------
        data : dict
            Top-level configuration mapping as produced by YAML/JSON/TOML parsing.

        Returns
        -------
        CableBundleConfig
            Validated configuration object.

        Raises
        ------
        AEDTRuntimeError
            If JSON-schema structural validation or semantic cross-reference
            validation fails.
        """
        return cls._from_dict_with_schema_check(data)

    @classmethod
    def _from_dict_with_schema_check(cls, data: dict[str, Any]) -> CableBundleConfig:
        """Validate *data* against the JSON schema, then construct the dataclass tree.

        Parameters
        ----------
        data : dict
            Raw configuration mapping.

        Returns
        -------
        CableBundleConfig
            Validated configuration object.

        Raises
        ------
        AEDTRuntimeError
            If schema or semantic validation fails.
        """
        cls._validate_schema(data)
        return cls._build(data)

    # -- Schema validation -----------------------------------------------------

    @staticmethod
    def _validate_schema(data: dict[str, Any]) -> None:
        """Run JSON-schema structural validation on *data*.

        Parameters
        ----------
        data : dict
            Raw configuration mapping to validate.

        Raises
        ------
        AEDTRuntimeError
            If the data does not conform to the JSON schema.
        """
        from jsonschema import ValidationError
        from jsonschema import validate

        schema_path = pathlib.Path(ansys.aedt.core.__file__).parent / "misc" / "cable_harness.schema.json"
        with open(schema_path, encoding="utf-8") as fh:
            schema = json.load(fh)

        try:
            validate(instance=data, schema=schema)
        except ValidationError as exc:
            raise AEDTRuntimeError(f"Cable-bundle configuration does not conform to schema: {exc.message}") from exc

    # -- Build -----------------------------------------------------------------

    @classmethod
    def _build(cls, data: dict[str, Any]) -> CableBundleConfig:
        """Construct the dataclass tree from a validated raw mapping.

        Parameters
        ----------
        data : dict
            Validated raw configuration mapping.

        Returns
        -------
        CableBundleConfig
            Constructed and semantically validated configuration.

        Raises
        ------
        AEDTRuntimeError
            If semantic cross-reference validation fails.
        """
        units = data.get("units", "mm")

        materials = {
            name: Material(
                name=name,
                conductivity=props.get("conductivity"),
                relative_permittivity=props.get("relative_permittivity"),
                loss_tangent=props.get("loss_tangent"),
                raw=props,
            )
            for name, props in (data.get("materials", {}) or {}).items()
        }

        conductors = {
            name: Conductor(
                name=name,
                equivalent_radius=float(
                    props.get("conductor_equivalent_radius") or props.get("conductor_radius", 0.227),
                ),
                awg=props.get("awg"),
                strand_count=props.get("strand_count"),
                raw=props,
            )
            for name, props in (data.get("conductors", {}) or {}).items()
        }

        ins_def = (data.get("insulation", {}) or {}).get("wire_insulation", {})
        insulation = Insulation(
            material=ins_def.get("material", "pe_foam"),
            outer_radius=float(ins_def.get("outer_radius", 0.55)),
            raw=ins_def,
        )

        pairs = {
            name: Pair(
                name=name,
                members=list(props["members"]),
                twist_pitch=float(props["twist_pitch"]),
                shield=cls._parse_shield(props.get("shield")),
                raw=props,
            )
            for name, props in (data.get("pairs", {}) or {}).items()
        }

        bundle = cls._parse_bundle(data.get("bundle", {}) or {})
        cross_section = cls._parse_cross_section(data.get("cross_section", {}) or {})

        routes = {
            name: Route(name=name, points=props["points"]) for name, props in (data.get("routes", {}) or {}).items()
        }

        simulation = cls._parse_simulation(data.get("simulation", {}) or {})

        cfg = cls(
            units=units,
            materials=materials,
            conductors=conductors,
            insulation=insulation,
            pairs=pairs,
            bundle=bundle,
            cross_section=cross_section,
            routes=routes,
            simulation=simulation,
            harnesses=data.get("harnesses", {}) or {},
            raw=data,
        )
        cfg.validate()
        return cfg

    # -- Sub-parsers -----------------------------------------------------------

    @staticmethod
    def _parse_shield(props: dict[str, Any] | None) -> Shield | None:
        """Parse a shield sub-mapping into a :class:`Shield` instance.

        Parameters
        ----------
        props : dict or None
            Raw shield mapping, or ``None`` if no shield is defined.

        Returns
        -------
        Shield or None
            Parsed shield, or ``None`` when *props* is falsy.
        """
        if not props:
            return None
        kind = props.get("type", "none")
        if kind == "none":
            return Shield(kind="none", raw=props)
        thickness = props.get("thickness")
        return Shield(
            kind=kind,
            material=props.get("material"),
            thickness=float(thickness) if thickness is not None else None,
            construction=props.get("construction", {}) or {},
            raw=props,
        )

    @classmethod
    def _parse_bundle(cls, block: dict[str, Any]) -> Bundle:
        """Parse the ``bundle`` block into a :class:`Bundle` instance.

        Parameters
        ----------
        block : dict
            Raw bundle mapping (the outer dict keyed by bundle name).

        Returns
        -------
        Bundle
            Parsed bundle.

        Raises
        ------
        AEDTRuntimeError
            If the block is empty.
        """
        if not block:
            raise AEDTRuntimeError("Configuration is missing a 'bundle' section.")
        name = next(iter(block))
        b = block[name]
        jacket = b.get("jacket", {}) or {}
        return Bundle(
            name=name,
            members=list(b.get("members", [])),
            jacket_material=jacket.get("material", "pvc"),
            jacket_outer_radius=float(jacket.get("outer_radius", 4.0)),
            overall_shield=cls._parse_shield(b.get("overall_shield")),
            separator=b.get("separator", {}) or {},
            raw=b,
        )

    @staticmethod
    def _parse_cross_section(block: dict[str, Any]) -> CrossSection:
        """Parse the ``cross_section`` block into a :class:`CrossSection` instance.

        Parameters
        ----------
        block : dict
            Raw cross-section mapping.

        Returns
        -------
        CrossSection
            Parsed cross-section.
        """
        locations = {
            pname: (
                float(pdef["center"][0]),
                float(pdef["center"][1]),
            )
            for pname, pdef in (block.get("pair_locations", {}) or {}).items()
        }
        return CrossSection(
            layout=block.get("layout", "quad"),
            pair_locations=locations,
            raw=block,
        )

    @classmethod
    def _parse_simulation(cls, sim: dict[str, Any]) -> Simulation:
        """Parse the ``simulation`` block into a :class:`Simulation` instance.

        Parameters
        ----------
        sim : dict
            Raw simulation mapping.

        Returns
        -------
        Simulation
            Parsed simulation settings.
        """
        geom_raw = sim.get("geometry", {}) or {}
        gp_raw = geom_raw.get("ground_plane", {}) or {}
        geometry = GeometrySettings(
            facets=int(geom_raw.get("facets", 8)),
            samples_per_pitch=int(geom_raw.get("samples_per_pitch", 8)),
            pair_wire_center_offset=float(geom_raw.get("pair_wire_center_offset", 0.58)),
            pair_shield_radius=float(geom_raw.get("pair_shield_radius", 1.15)),
            overall_shield_radius=float(geom_raw.get("overall_shield_radius", 3.60)),
            tube_end_extension=(float(geom_raw["tube_end_extension"]) if "tube_end_extension" in geom_raw else None),
            ground_plane=GroundPlane(
                enabled=bool(gp_raw.get("enabled", False)),
                distance_below_route=float(gp_raw.get("distance_below_route", 10.0)),
                size_margin=float(gp_raw.get("size_margin", 20.0)),
            ),
            raw=geom_raw,
        )

        ports_raw = sim.get("ports", {}) or {}
        ports = PortSettings(
            kind=ports_raw.get("type", "lumped"),
            reference=ports_raw.get("reference", "overall_shield"),
            impedance=float(ports_raw.get("impedance", 50.0)),
            raw=ports_raw,
        )

        term_raw = sim.get("terminations", {}) or {}
        terminations = Terminations(
            driven_conductor=term_raw.get("driven_conductor"),
            load_end={k: float(v) for k, v in (term_raw.get("load_end", {}) or {}).items()},
            other_conductors_default=float(term_raw.get("other_conductors_default", 50.0)),
            raw=term_raw,
        )

        transient: Transient | None = None
        tran_raw = sim.get("transient")
        if tran_raw:
            src_raw = tran_raw.get("source", {}) or {}
            transient = Transient(
                stop_time=float(tran_raw["stop_time"]),
                time_step=float(tran_raw["time_step"]),
                initial_step=float(tran_raw["initial_step"]),
                source=TransientSource(
                    kind=src_raw.get("type", "pwl"),
                    time=list(src_raw.get("time", [])),
                    amplitude=list(src_raw.get("amplitude", [])),
                    source_impedance=float(src_raw.get("source_impedance", 50.0)),
                    raw=src_raw,
                ),
                raw=tran_raw,
            )

        diff = [(str(a), str(b)) for a, b in (sim.get("differential_pairs", []) or [])]
        freq = sim.get("frequency_range", {}) or {}
        z0 = (sim.get("characteristic_impedance", {}) or {}).get("differential")

        return Simulation(
            differential_pairs=diff,
            frequency_start=float(freq.get("start", 1e6)),
            frequency_stop=float(freq.get("stop", 10e9)),
            geometry=geometry,
            ports=ports,
            terminations=terminations,
            transient=transient,
            characteristic_impedance_diff=float(z0) if z0 is not None else None,
            raw=sim,
        )

    # -- Validation ------------------------------------------------------------

    def validate(self) -> None:
        """Run cross-reference and sanity checks, raising on any problem found.

        All discovered problems are accumulated before raising so the caller
        receives a complete list of issues in a single exception.

        Raises
        ------
        AEDTRuntimeError
            If any cross-reference or geometry interference check fails.
            The message lists every problem found.
        """
        errors: list[str] = []

        for pair in self.pairs.values():
            for member in pair.members:
                if member not in self.conductors:
                    errors.append(f"Pair {pair.name!r} references unknown conductor {member!r}.")
            if pair.name not in self.cross_section.pair_locations:
                errors.append(f"Pair {pair.name!r} has no entry in cross_section.pair_locations.")

        for member in self.bundle.members:
            if member not in self.pairs:
                errors.append(f"Bundle {self.bundle.name!r} references unknown pair {member!r}.")

        for a, b in self.simulation.differential_pairs:
            for c in (a, b):
                if c not in self.conductors:
                    errors.append(f"Differential pair references unknown conductor {c!r}.")

        referenced = {self.insulation.material, self.bundle.jacket_material}
        for pair in self.pairs.values():
            if pair.shield and pair.shield.material:
                referenced.add(pair.shield.material)
        if self.bundle.overall_shield and self.bundle.overall_shield.material:
            referenced.add(self.bundle.overall_shield.material)
        for mat in referenced:
            if mat not in self.materials:
                errors.append(f"Material {mat!r} is used but not defined.")

        if not self.routes:
            errors.append("At least one route is required.")
        for route in self.routes.values():
            if route.points.shape[0] < 2 or route.points.shape[1] != 3:
                errors.append(f"Route {route.name!r} must be an (N>=2, 3) point list.")

        errors.extend(self._pair_shield_interference_errors())

        if errors:
            raise AEDTRuntimeError("Invalid cable-bundle configuration:\n  - " + "\n  - ".join(errors))

    def _pair_shield_interference_errors(self, tol: float = 1e-6) -> list[str]:
        """Return geometry interference errors for pair-shield overlaps.

        Parameters
        ----------
        tol : float, optional
            Tolerance in the same units as the configuration.

        Returns
        -------
        list of str
            Error messages for each pair of interfering pair shields.
        """
        r = self.simulation.geometry.pair_shield_radius
        locs = {name: np.array(center, dtype=float) for name, center in self.cross_section.pair_locations.items()}
        names = list(locs)
        out: list[str] = []
        for i, a in enumerate(names):
            for b in names[i + 1 :]:
                d = float(np.linalg.norm(locs[a] - locs[b]))
                min_d = 2.0 * r
                if d + tol < min_d:
                    out.append(
                        f"Pair shields {a!r} and {b!r} overlap: "
                        f"distance={d:.3f} mm < required {min_d:.3f} mm. "
                        f"Reduce geometry.pair_shield_radius or spread "
                        f"cross_section.pair_locations.",
                    )
        return out

    # -- Convenience -----------------------------------------------------------

    @property
    def active_route(self) -> Route:
        """Return the first declared route (the one the builder uses by default)."""
        return next(iter(self.routes.values()))

    def end_extension(self) -> float:
        """Return the end extension, falling back to a radius-based default.

        Returns
        -------
        float
            The ``tube_end_extension`` value when set, otherwise ``5 * max(gap, 1)``.
        """
        g = self.simulation.geometry
        if g.tube_end_extension is not None:
            return g.tube_end_extension
        gap = g.overall_shield_radius - self.insulation.outer_radius
        return 5.0 * max(gap, 1.0)
