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

"""Explicit HFSS model of a routed, twisted, shielded cable bundle.

:class:`RoutedCableBundle` turns a validated
:class:`~ansys.aedt.core.modeler.advanced_cad.cable_harness.configuration.CableBundleConfig` into a
fully explicit HFSS geometry made of twisted solid conductors, faceted insulation, faceted foil and
braid shield sheets, and a jacket. It then assigns a frequency-dependent transfer-impedance boundary
to every shield surface, creates a port at both ends of every conductor, and registers the
differential pairs declared in the configuration.

The builder receives an already-open :class:`~ansys.aedt.core.hfss.Hfss` design rather than launching
Electronics Desktop itself, so it composes into larger workflows and is straightforward to unit test.
Every swept profile is a regular polygon of ``geometry.facets`` sides rather than a true surface, and
every created object, boundary, port, and dataset name is recorded in
:attr:`RoutedCableBundle.created` so that downstream steps can consume them.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from dataclasses import field
import math
from typing import TYPE_CHECKING
from typing import Any

import numpy as np

from ansys.aedt.core.base import PyAedtBase
from ansys.aedt.core.generic.general_methods import pyaedt_function_handler
from ansys.aedt.core.internal.errors import AEDTRuntimeError
from ansys.aedt.core.modeler.advanced_cad.cable_harness import geometry as geo
from ansys.aedt.core.modeler.advanced_cad.cable_harness.configuration import CableBundleConfig
from ansys.aedt.core.modeler.advanced_cad.cable_harness.shield_models import ShieldModel
from ansys.aedt.core.modeler.advanced_cad.cable_harness.shield_models import build_shield_model

if TYPE_CHECKING:  # pragma: no cover - typing only
    from pathlib import Path

__all__ = ["BuildArtifacts", "RoutedCableBundle"]

_LIGHT_GREY = (200, 200, 200)


@dataclass
class BuildArtifacts(PyAedtBase):
    """Store the names of every entity created by :class:`RoutedCableBundle`, grouped by role.

    Attributes
    ----------
    conductors : list of str
        Names of the solid conductor objects.
    insulation : list of str
        Names of the insulation objects surrounding each conductor.
    pair_shields : list of str
        Names of the per-pair shield sheets.
    overall_shield : list of str
        Names of the overall shield sheets.
    jacket : list of str
        Names of the jacket objects.
    boundaries : list of str
        Names of the impedance boundaries assigned to the shield sheets.
    ports : list of str
        Names of the ports created at the conductor ends.
    datasets : list of str
        Names of the transfer-impedance datasets created in the design.
    """

    conductors: list[str] = field(default_factory=list)
    insulation: list[str] = field(default_factory=list)
    pair_shields: list[str] = field(default_factory=list)
    overall_shield: list[str] = field(default_factory=list)
    jacket: list[str] = field(default_factory=list)
    boundaries: list[str] = field(default_factory=list)
    ports: list[str] = field(default_factory=list)
    datasets: list[str] = field(default_factory=list)

    @pyaedt_function_handler()
    def as_dict(self) -> dict[str, list[str]]:
        """Return the artifacts as a plain dictionary keyed by role.

        Returns
        -------
        dict
            Mapping of role name to the list of created entity names.
        """
        return {
            "conductors": self.conductors,
            "insulation": self.insulation,
            "pair_shields": self.pair_shields,
            "overall_shield": self.overall_shield,
            "jacket": self.jacket,
            "boundaries": self.boundaries,
            "ports": self.ports,
            "datasets": self.datasets,
        }


class RoutedCableBundle(PyAedtBase):
    """Build an explicit HFSS model of a routed, twisted, shielded cable bundle.

    Parameters
    ----------
    configuration : :class:`CableBundleConfig`
        Validated cable bundle configuration.
    hfss : :class:`ansys.aedt.core.hfss.Hfss`
        Open HFSS design using a ``"DrivenTerminal"`` or ``"DrivenModal"`` solution type. The caller
        owns the lifecycle of this object.
    name_prefix : str, optional
        Prefix applied to **every** created entity — modeler objects, impedance-boundary names,
        transfer-impedance dataset names, port names, and differential-mode names — so that several
        bundles with different prefixes can coexist in one design without name collisions.
        The default is ``"cbl"``.
    frequencies : numpy.ndarray, optional
        Frequency grid in Hz on which the transfer impedance is evaluated for the boundary datasets.
        The default is ``None``, in which case 71 logarithmically spaced points from 1 kHz to 10 GHz
        are used.
    shield_model_factory : callable, optional
        Override for how a shield definition becomes a shield model. The signature must match
        :func:`~ansys.aedt.core.modeler.advanced_cad.cable_harness.shield_models.build_shield_model`.
        The default is ``None``, in which case ``build_shield_model`` is used. Provide a custom
        factory to inject measured transfer-impedance data.

    Examples
    --------
    >>> from ansys.aedt.core import Hfss
    >>> from ansys.aedt.core.modeler.advanced_cad.cable_harness import RoutedCableBundle
    >>> hfss = Hfss(solution_type="Terminal")  # doctest: +SKIP
    >>> bundle = RoutedCableBundle.from_file("cat6a_sstp_awg25.yaml", hfss)  # doctest: +SKIP
    >>> artifacts = bundle.build()  # doctest: +SKIP
    >>> bundle.create_setup()  # doctest: +SKIP
    """

    def __init__(
        self,
        configuration: CableBundleConfig,
        hfss: Any,
        *,
        name_prefix: str = "cbl",
        frequencies: np.ndarray | None = None,
        shield_model_factory: Callable[..., ShieldModel] | None = None,
    ) -> None:
        self.configuration = configuration
        self.hfss = hfss
        self.name_prefix = name_prefix
        self.frequencies = np.logspace(3, 10, 71) if frequencies is None else np.asarray(frequencies, dtype=float)
        self._shield_factory = shield_model_factory or build_shield_model

        self.created = BuildArtifacts()
        self.conductor_paths: dict[str, np.ndarray] = {}
        self.port_pairs: dict[str, tuple[str, str]] = {}

        route = self.configuration.active_route
        self._route_points = route.points
        _, self._normal_1, self._normal_2 = geo.route_point_frames(self._route_points)
        self._extended_route = geo.extend_route_ends(self._route_points, self.configuration.end_extension())

    @property
    def logger(self) -> Any:
        """Logger of the HFSS design used to report build progress.

        Returns
        -------
        :class:`ansys.aedt.core.aedt_logger.AedtLogger`
            Logger of the associated HFSS design.
        """
        return self.hfss.logger

    @classmethod
    @pyaedt_function_handler()
    def from_file(cls, input_file: str | Path, hfss: Any, **kwargs: Any) -> RoutedCableBundle:
        """Create a bundle builder from a configuration file and an open HFSS design.

        Parameters
        ----------
        input_file : str or :class:`pathlib.Path`
            Path to the cable bundle configuration file. Supported formats are those accepted by
            :func:`~ansys.aedt.core.generic.file_utils.read_configuration_file`, typically YAML or
            JSON.
        hfss : :class:`ansys.aedt.core.hfss.Hfss`
            Open HFSS design in which the bundle is created.
        **kwargs : dict, optional
            Additional keyword arguments forwarded to the class constructor.

        Returns
        -------
        :class:`RoutedCableBundle`
            Builder ready to create the explicit model.
        """
        return cls(CableBundleConfig.from_file(input_file), hfss, **kwargs)

    @pyaedt_function_handler()
    def build(
        self,
        *,
        create_ports: bool = True,
        assign_shield_boundaries: bool = True,
        define_differential_pairs: bool = True,
    ) -> BuildArtifacts:
        """Build the complete explicit model in a single call.

        Parameters
        ----------
        create_ports : bool, optional
            Whether to create ports at both ends of every conductor. The default is ``True``.
        assign_shield_boundaries : bool, optional
            Whether to compute the transfer impedance and assign it to every shield surface. The
            default is ``True``.
        define_differential_pairs : bool, optional
            Whether to register the differential pairs listed in the configuration. The default is
            ``True``.

        Returns
        -------
        :class:`BuildArtifacts`
            Names of every entity created, for use by downstream steps.

        Raises
        ------
        AEDTRuntimeError
            If geometry has already been built on this instance. Create a new
            :class:`RoutedCableBundle` instance, or use a different ``name_prefix``, to build again.
        """
        if self.created.conductors:
            raise AEDTRuntimeError(
                f"This RoutedCableBundle (prefix='{self.name_prefix}') has already been built. "
                "Geometry objects already exist in the design. "
                "Create a new RoutedCableBundle instance or use a different name_prefix to build again."
            )
        self.ensure_materials()
        self.build_geometry()
        if assign_shield_boundaries:
            self.assign_shield_boundaries()
        if create_ports:
            self.create_ports()
        if define_differential_pairs:
            self.define_differential_pairs()
        return self.created

    @pyaedt_function_handler()
    def ensure_materials(self) -> bool:
        """Create or update every material referenced by the configuration.

        Returns
        -------
        bool
            ``True`` when the materials are created or updated.
        """
        materials = self.hfss.materials
        for name, spec in self.configuration.materials.items():
            material = materials[name] if name in materials.material_keys else materials.add_material(name)
            if spec.conductivity is not None:
                material.conductivity = spec.conductivity
            if spec.relative_permittivity is not None:
                material.permittivity = spec.relative_permittivity
            if spec.loss_tangent is not None:
                material.dielectric_loss_tangent = spec.loss_tangent
        return True

    @pyaedt_function_handler()
    def build_geometry(self) -> bool:
        """Create the conductors, insulation, pair shields, overall shield, and jacket.

        Returns
        -------
        bool
            ``True`` when the geometry is created.

        Raises
        ------
        AEDTRuntimeError
            If geometry has already been built on this instance. Create a new
            :class:`RoutedCableBundle` instance, or use a different ``name_prefix``, to build again.
        """
        if self.created.conductors:
            raise AEDTRuntimeError(
                f"Geometry for RoutedCableBundle (prefix='{self.name_prefix}') already exists in the design. "
                "Create a new RoutedCableBundle instance or use a different name_prefix to build again."
            )
        self._build_pairs()
        self._build_overall_shield_and_jacket()
        return True

    @pyaedt_function_handler()
    def assign_shield_boundaries(self) -> bool:
        """Assign a frequency-dependent transfer impedance to every shield sheet.

        Returns
        -------
        bool
            ``True`` when the boundaries are assigned.
        """
        geometry_settings = self.configuration.simulation.geometry

        for pair in self.configuration.pairs.values():
            if not pair.shield or pair.shield.kind == "none":
                continue
            model = self._shield_factory(
                pair.shield,
                radius_mm=geometry_settings.pair_shield_radius,
                materials=self.configuration.materials,
            )
            transfer_impedance = model.transfer_impedance(self.frequencies)
            sheet = f"{self.name_prefix}_{pair.name}_foil_shield"
            self._assign_transfer_impedance(
                sheet,
                f"{self.name_prefix}_ZT_{pair.name}",
                transfer_impedance,
                f"{self.name_prefix}_Zt_{pair.name}",
                geometry_settings.pair_shield_radius,
            )

        overall = self.configuration.bundle.overall_shield
        if overall and overall.kind != "none":
            model = self._shield_factory(
                overall,
                radius_mm=geometry_settings.overall_shield_radius,
                materials=self.configuration.materials,
            )
            self._log_braid_metrics(model)
            transfer_impedance = model.transfer_impedance(self.frequencies)
            self._assign_transfer_impedance(
                f"{self.name_prefix}_overall_braid",
                f"{self.name_prefix}_ZT_overall_braid",
                transfer_impedance,
                f"{self.name_prefix}_Zt_overall_braid",
                geometry_settings.overall_shield_radius,
            )
        return True

    @pyaedt_function_handler()
    def create_ports(self) -> bool:
        """Create a circuit port between each conductor end face and the port reference.

        Only circuit ports are currently implemented. Lumped and wave ports on faceted 3-D
        conductors require an explicit rectangular cap sheet between the conductor end and the
        reference plane, which this builder does not create. If the configuration requests a
        different port type, a warning is emitted once and circuit ports are created instead.

        Returns
        -------
        bool
            ``True`` when the ports are created.

        Raises
        ------
        AEDTRuntimeError
            If the geometry has not been built yet, or if no end face or reference edge can be found
            for a conductor.
        """
        if not self.conductor_paths:
            raise AEDTRuntimeError("Ports cannot be created before the geometry is built.")

        port_kind = self.configuration.simulation.ports.kind
        if port_kind != "circuit":
            self.logger.warning(
                f"Port type '{port_kind}' was requested but only 'circuit' ports are currently "
                "implemented. Faceted conductor ends require an explicit cap sheet for lumped or "
                "wave ports, which this builder does not create. Creating circuit ports instead."
            )

        impedance = self.configuration.simulation.ports.impedance
        reference_object = self._reference_object()

        for conductor_name, centerline in self.conductor_paths.items():
            conductor_object = self.hfss.modeler[f"{self.name_prefix}_{conductor_name}_cu"]
            if conductor_object is None:
                raise AEDTRuntimeError(f"Conductor object '{self.name_prefix}_{conductor_name}_cu' was not found.")
            for end_index, label in ((0, "in"), (-1, "out")):
                target = np.asarray(centerline[end_index], dtype=float)
                conductor_face = self._end_face_of(conductor_object, target)
                if not conductor_face.edges:
                    raise AEDTRuntimeError(
                        f"No edge was found on the end face of conductor '{conductor_name}'. "
                        "The port cap sheet cannot be created.",
                    )
                conductor_edge = conductor_face.edges[0]
                reference_edge = self._nearest_edge(reference_object.edges, target)

                port_name = f"{self.name_prefix}_P_{conductor_name}_{label}"
                self.hfss.circuit_port(
                    assignment=conductor_edge,
                    reference=reference_edge,
                    impedance=impedance,
                    name=port_name,
                    renormalize=True,
                    renorm_impedance=str(impedance),
                )
                self.created.ports.append(port_name)
            self.port_pairs[conductor_name] = (
                f"{self.name_prefix}_P_{conductor_name}_in",
                f"{self.name_prefix}_P_{conductor_name}_out",
            )
        return True

    @pyaedt_function_handler()
    def define_differential_pairs(self) -> bool:
        """Register the differential pairs listed in the simulation settings.

        Ports must already exist. Each differential pair ties together the two ``_in`` ports and the
        two ``_out`` ports of a wire pair.

        Returns
        -------
        bool
            ``True`` when the differential pairs are registered, ``False`` when the configuration
            declares none or when no ports exist.
        """
        differential_pairs = self.configuration.simulation.differential_pairs
        if not differential_pairs or not self.port_pairs:
            return False

        differential_impedance = self.configuration.simulation.characteristic_impedance_diff or 100.0
        index = 0
        for positive, negative in differential_pairs:
            if positive not in self.port_pairs or negative not in self.port_pairs:
                self.logger.warning(
                    f"Differential pair ('{positive}', '{negative}') is skipped because at least one "
                    "of its conductors has no port.",
                )
                continue
            for end in ("in", "out"):
                pos_port = self.port_pairs[positive][0 if end == "in" else 1]
                neg_port = self.port_pairs[negative][0 if end == "in" else 1]
                self.hfss.set_differential_pair(
                    assignment=pos_port,
                    reference=neg_port,
                    common_mode=f"{self.name_prefix}_CM{index}",
                    differential_mode=f"{self.name_prefix}_DM{index}",
                    common_reference=differential_impedance / 4.0,
                    differential_reference=differential_impedance,
                    active=True,
                )
                index += 1
        return True

    @pyaedt_function_handler()
    def create_setup(
        self,
        *,
        name: str = "Sparam",
        maximum_passes: int = 8,
        delta_s: float = 0.02,
        num_points: int = 401,
        sweep_name: str = "Broadband",
    ) -> Any:
        """Create a broadband interpolating S-parameter setup and frequency sweep.

        Parameters
        ----------
        name : str, optional
            Name of the setup. The default is ``"Sparam"``.
        maximum_passes : int, optional
            Maximum number of adaptive passes. The default is ``8``.
        delta_s : float, optional
            Convergence criterion on the scattering parameters. The default is ``0.02``.
        num_points : int, optional
            Number of frequency points in the sweep. The default is ``401``.
        sweep_name : str, optional
            Name of the frequency sweep. The default is ``"Broadband"``.

        Returns
        -------
        :class:`ansys.aedt.core.modules.solve_setup.SetupHFSS`
            Setup that was created.

        Raises
        ------
        AEDTRuntimeError
            If HFSS fails to create the setup.
        """
        frequency_start = self.configuration.simulation.frequency_start
        frequency_stop = self.configuration.simulation.frequency_stop
        setup = self.hfss.create_setup(
            name=name,
            Frequency=f"{frequency_stop / 2:.3e}Hz",
            MaximumPasses=maximum_passes,
            MinimumConvergedPasses=1,
            DeltaS=delta_s,
        )
        if not setup:
            raise AEDTRuntimeError(f"Failed to create the HFSS setup '{name}'.")
        setup.create_frequency_sweep(
            unit="Hz",
            name=sweep_name,
            start_frequency=frequency_start,
            stop_frequency=frequency_stop,
            num_of_freq_points=num_points,
            sweep_type="Interpolating",
        )
        return setup

    def _build_pairs(self) -> None:
        """Create the conductors, insulation, and per-pair shields of every twisted pair."""
        configuration = self.configuration
        geometry_settings = configuration.simulation.geometry
        insulation = configuration.insulation
        facets = geometry_settings.facets

        for pair in configuration.pairs.values():
            center_x, center_y = configuration.cross_section.pair_locations[pair.name]
            pair_center = np.array([center_x, center_y], dtype=float)

            for index, conductor_name in enumerate(pair.members):
                phase = 0.0 if index == 0 else math.pi
                centerline = geo.twisted_centerline(
                    self._route_points,
                    pair_center,
                    self._normal_1,
                    self._normal_2,
                    radius=geometry_settings.pair_wire_center_offset,
                    pitch=pair.twist_pitch,
                    phase=phase,
                    samples_per_pitch=geometry_settings.samples_per_pitch,
                )
                self.conductor_paths[conductor_name] = centerline

                conductor = self._faceted_sweep(
                    centerline,
                    configuration.conductors[conductor_name].equivalent_radius,
                    facets,
                    name=f"{self.name_prefix}_{conductor_name}_cu",
                    material="copper",
                    closed_solid=True,
                )
                self.created.conductors.append(conductor.name)

                insulation_object = self._faceted_sweep(
                    centerline,
                    insulation.outer_radius,
                    facets,
                    name=f"{self.name_prefix}_{conductor_name}_ins",
                    material=insulation.material,
                    closed_solid=True,
                )
                self.created.insulation.append(insulation_object.name)

            shield_path = geo.offset_route_points(self._route_points, pair_center, self._normal_1, self._normal_2)
            shield = self._faceted_sweep(
                shield_path,
                geometry_settings.pair_shield_radius,
                facets,
                name=f"{self.name_prefix}_{pair.name}_foil_shield",
                material=None,
                closed_solid=False,
            )
            self.created.pair_shields.append(shield.name)

    def _build_overall_shield_and_jacket(self) -> None:
        """Create the overall shield sheet and the outer jacket along the extended route."""
        configuration = self.configuration
        geometry_settings = configuration.simulation.geometry
        facets = geometry_settings.facets

        braid = self._faceted_sweep(
            self._extended_route,
            geometry_settings.overall_shield_radius,
            facets,
            name=f"{self.name_prefix}_overall_braid",
            material=None,
            closed_solid=False,
        )
        self.created.overall_shield.append(braid.name)

        jacket = self._faceted_sweep(
            self._extended_route,
            configuration.bundle.jacket_outer_radius,
            facets,
            name=f"{self.name_prefix}_pvc_jacket",
            material=configuration.bundle.jacket_material,
            closed_solid=True,
        )
        self.created.jacket.append(jacket.name)

        for obj in (braid, jacket):
            obj.transparency = 0.8
            obj.color = _LIGHT_GREY

    def _faceted_sweep(
        self,
        path_points: np.ndarray,
        radius: float,
        facets: int,
        *,
        name: str,
        material: str | None,
        closed_solid: bool,
    ) -> Any:
        """Sweep a regular polygon profile along a 3D polyline and return the resulting object."""
        start = path_points[0]
        tangent = geo.unit(path_points[1] - path_points[0])
        profile_points = geo.faceted_profile_points(start, tangent, radius, facets)

        profile = self.hfss.modeler.create_polyline(
            points=profile_points + [profile_points[0]],
            name=f"{name}_profile",
            close_surface=closed_solid,
            cover_surface=closed_solid,
            material=material if closed_solid else None,
        )
        path = self.hfss.modeler.create_polyline(points=path_points.tolist(), name=f"{name}_path")
        self.hfss.modeler.sweep_along_path(profile, path)
        profile.name = name
        if material and closed_solid:
            profile.material_name = material
        return profile

    def _assign_transfer_impedance(
        self,
        sheet_name: str,
        dataset_name: str,
        transfer_impedance: np.ndarray,
        boundary_name: str,
        radius_mm: float,
    ) -> None:
        """Create transfer-impedance datasets and assign them as an impedance boundary.

        Parameters
        ----------
        sheet_name : str
            Name of the shield sheet object in the modeler.
        dataset_name : str
            Base name for the two frequency-domain datasets. Two datasets are created:
            ``<dataset_name>_re`` for the real (resistive) part and ``<dataset_name>_im`` for the
            imaginary (reactive) part of the surface impedance.
        transfer_impedance : numpy.ndarray
            Complex transfer impedance in **ohm per metre** of cable, evaluated at
            ``self.frequencies``. This is the quantity returned by
            ``ShieldModel.transfer_impedance()``.
        boundary_name : str
            Name for the HFSS impedance boundary.
        radius_mm : float
            Shield mid-surface radius in **millimetres**. Used to convert from ohm/m to
            ohm/square before writing to HFSS.

        Notes
        -----
        HFSS ``assign_impedance_to_sheet`` expects a **surface impedance** in ohm/square, whereas
        ``ShieldModel.transfer_impedance()`` returns a **transfer impedance** in ohm/m (it has
        already divided the per-square resistance by the shield circumference so that it represents
        the coupling per unit cable length).

        The conversion back to ohm/square is:

        .. math::

            Z_{\\text{surface}}\\,[\\Omega/\\square] =
                Z_{\\text{transfer}}\\,[\\Omega/\\mathrm{m}] \\times 2\\pi r

        where ``r`` is the shield radius in metres.  The real and imaginary parts are converted
        independently and stored in separate design datasets (``_re`` / ``_im``) so that the
        reactive aperture/seam term is correctly represented as reactance in the boundary condition
        rather than folded into the resistance.
        """
        radius_m = radius_mm * 1e-3
        circumference_m = 2.0 * math.pi * radius_m
        zt_sq = transfer_impedance * circumference_m

        name_re = f"{dataset_name}_re"
        name_im = f"{dataset_name}_im"

        result_re = self.hfss.create_dataset(
            name_re,
            self.frequencies.tolist(),
            zt_sq.real.tolist(),
            is_project_dataset=False,
            x_unit="Hz",
            y_unit="ohm",
        )
        if result_re is False:
            raise AEDTRuntimeError(f"Failed to create transfer-impedance dataset '{name_re}'.")
        self.created.datasets.append(name_re)

        result_im = self.hfss.create_dataset(
            name_im,
            self.frequencies.tolist(),
            zt_sq.imag.tolist(),
            is_project_dataset=False,
            x_unit="Hz",
            y_unit="ohm",
        )
        if result_im is False:
            raise AEDTRuntimeError(f"Failed to create transfer-impedance dataset '{name_im}'.")
        self.created.datasets.append(name_im)

        boundary = self.hfss.assign_impedance_to_sheet(
            sheet_name,
            name=boundary_name,
            resistance=f"pwl({name_re}, Freq)",
            reactance=f"pwl({name_im}, Freq)",
        )
        if not boundary:
            raise AEDTRuntimeError(f"The impedance boundary could not be assigned to sheet '{sheet_name}'.")
        self.created.boundaries.append(boundary.name)

    def _reference_object(self) -> Any:
        """Return the modeler object used as the electrical reference for the ports."""
        reference = self.configuration.simulation.ports.reference
        if reference != "overall_shield":
            raise AEDTRuntimeError(
                f"Port reference '{reference}' is not supported. Only 'overall_shield' is available "
                "because no ground plane is created by this builder.",
            )
        reference_name = f"{self.name_prefix}_overall_braid"
        reference_object = self.hfss.modeler[reference_name]
        if reference_object is None:
            raise AEDTRuntimeError(f"The port reference object '{reference_name}' was not found.")
        return reference_object

    @staticmethod
    def _end_face_of(assignment: Any, target_point: np.ndarray) -> Any:
        """Return the face of an object whose center is closest to a target point."""
        target = np.asarray(target_point, dtype=float)
        faces = assignment.faces
        if not faces:
            raise AEDTRuntimeError(f"Object '{assignment.name}' has no face to place a port on.")
        return min(faces, key=lambda f: float(np.linalg.norm(np.array(f.center) - target)))

    @staticmethod
    def _nearest_edge(edges: Any, target_point: np.ndarray) -> Any:
        """Return the edge whose midpoint is closest to a target point."""
        target = np.asarray(target_point, dtype=float)
        candidates = list(edges)
        if not candidates:
            raise AEDTRuntimeError("The port reference object has no edge to connect the port to.")
        return min(candidates, key=lambda e: float(np.linalg.norm(np.array(e.midpoint) - target)))

    def _log_braid_metrics(self, model: ShieldModel) -> None:
        """Report the derived braid metrics of a shield model through the design logger."""
        coverage = getattr(model, "optical_coverage", None)
        resistance = getattr(model, "dc_resistance_per_m", None)
        if coverage is not None:
            self.logger.info(f"Computed optical coverage: {coverage:.3f}")
        if resistance is not None:
            self.logger.info(f"Computed DC resistance: {resistance * 1e3:.3f} mOhm/m")
