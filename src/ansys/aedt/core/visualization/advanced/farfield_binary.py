# -*- coding: utf-8 -*-
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

"""Far field directly from the binary radiation-surface data in ``.aedtresults``.

When HFSS solves a radiating structure it stores the tangential ``E``/``H`` on the
radiation boundary in three companion files inside a per-frequency results folder
(``<design>.results/DV*_S*_V*_F*/``):

* ``current.sf_mshhdr`` -- ASCII header (vertex/triangle counts, precision).
* ``current.sf_msh`` -- binary surface mesh (vertices in metres + triangles).
* ``fields.sf_fld_<k>`` -- binary tangential complex ``E``/``H`` for source ``k``.

This module decodes those files and reconstructs the far field with a
near-field-to-far-field (NF2FF) transform, so the antenna pattern can be obtained
**without re-exporting an** ``.ffd`` **file through the solver**. The result is
written as a standard ``.ffd`` plus a ``pyaedt_antenna_metadata.json`` so the
existing
:class:`ansys.aedt.core.visualization.advanced.farfield_visualization.FfdSolutionData`
consumes it unchanged.

.. note::
   Only designs that persist the surface fields are supported -- single antennas,
   explicit (multi-port) arrays, and finite-array domain-decomposition (FA-DDM)
   solves. Component-array DDM (CA-DDM / 3D-component) designs keep the currents
   inside the component domains and write no ``sf_fld``; for those the caller must
   fall back to the regular far-field export.
"""

from __future__ import annotations

import json
from pathlib import Path
import re
import struct

import numpy as np

from ansys.aedt.core.aedt_logger import pyaedt_logger as logger
from ansys.aedt.core.base import PyAedtBase
from ansys.aedt.core.generic.constants import SpeedOfLight
from ansys.aedt.core.generic.general_methods import pyaedt_function_handler
from ansys.aedt.core.visualization.advanced.farfield_visualization import FfdSolutionData

ETA0 = 376.730313668  # free-space wave impedance (ohms)

# on-disk record sizes (little-endian)
_VERTEX_REC = 28  # int32 id + 3 * float64 (x, y, z in metres)
_TRI_REC = 28  # int32 id + 3 * int32 vertices (1-based) + 3 * int32 (-1)
_FIELD_HDR = 8  # int32 id + int32 ndof


@pyaedt_function_handler()
def parse_surface_mesh_header(file_name) -> dict:
    """Parse the ASCII ``current.sf_mshhdr`` surface-mesh header.

    Parameters
    ----------
    file_name : str or :class:`pathlib.Path`
        Path to the ``current.sf_mshhdr`` (or ``..._D0``) file.

    Returns
    -------
    dict
        Keys ``num_vertices``, ``num_triangles``, ``num_midpoints``,
        ``data_precision`` and ``big_endian``.
    """
    text = Path(file_name).read_text(errors="replace")

    def _get(key, default=""):
        match = re.search(rf"{key}\s*=\s*'?([^'\n\r]+)'?", text)
        return match.group(1).strip() if match else default

    return {
        "num_vertices": int(_get("NumVertices", "0")),
        "num_triangles": int(_get("NumTriangles", "0")),
        "num_midpoints": int(_get("NumMidPoints", "0")),
        "data_precision": _get("DataPrecision", "Double"),
        "big_endian": _get("BigEndian", "false").lower() == "true",
    }


class RadiationSurface(PyAedtBase):
    """Radiation-surface mesh and tangential fields decoded from ``.aedtresults``.

    Reads the ``current.sf_msh`` triangle mesh and one ``fields.sf_fld_<k>`` per
    driven source, exposing the triangle centroids, outward unit normals, areas
    and per-source complex ``E``/``H`` needed for the NF2FF transform.

    Parameters
    ----------
    folder : str or :class:`pathlib.Path`
        Results folder holding ``current.sf_mshhdr``/``current.sf_msh`` and the
        ``fields.sf_fld_<k>`` files. The FA-DDM ``_D0`` (unit-cell domain) suffix
        is detected automatically.

    Examples
    --------
    >>> from ansys.aedt.core.visualization.advanced.farfield_binary import RadiationSurface
    >>> surface = RadiationSurface(results_folder)  # doctest: +SKIP
    >>> e_theta, e_phi = surface.far_field(frequency=10e9)  # doctest: +SKIP
    """

    def __init__(self, folder) -> None:
        folder = Path(folder)
        self.folder = folder

        if (folder / "current.sf_mshhdr").is_file():
            suffix = ""
        elif (folder / "current.sf_mshhdr_D0").is_file():
            suffix = "_D0"
        else:
            raise FileNotFoundError(f"No 'current.sf_mshhdr[_D0]' surface mesh in {folder}.")
        self.domain = suffix.lstrip("_")

        header = parse_surface_mesh_header(folder / f"current.sf_mshhdr{suffix}")
        if header["big_endian"]:
            raise NotImplementedError("Big-endian surface mesh is not supported.")
        n_vertices = header["num_vertices"]
        n_triangles = header["num_triangles"]

        self.vertices, self.triangles = _read_mesh(folder / f"current.sf_msh{suffix}", n_vertices, n_triangles)

        pattern = re.compile(rf"fields\.sf_fld_(\d+){re.escape(suffix)}$")
        source_files = sorted(
            (p for p in folder.glob(f"fields.sf_fld_*{suffix}") if pattern.fullmatch(p.name)),
            key=lambda p: int(pattern.fullmatch(p.name).group(1)),
        )
        if not source_files:
            raise FileNotFoundError(f"No 'fields.sf_fld_<k>{suffix}' field files in {folder}.")

        e_sources, h_sources = [], []
        for source_file in source_files:
            e_field, h_field = _read_field(source_file, n_triangles)
            e_sources.append(e_field)
            h_sources.append(h_field)
        #: Per-source complex tangential E, shape ``(n_sources, n_triangles, 3)`` (V/m).
        self.e_sources = np.array(e_sources)
        #: Per-source complex tangential H, shape ``(n_sources, n_triangles, 3)`` (A/m).
        self.h_sources = np.array(h_sources)

        #: Antenna frequency in Hz, read from the ``fields.evtrs`` header when present.
        self.frequency = _read_frequency(folder / "fields.evtrs")

    @property
    def n_sources(self) -> int:
        """Number of driven sources (ports or active array elements)."""
        return self.e_sources.shape[0]

    @property
    def n_triangles(self) -> int:
        """Number of radiation-surface triangles."""
        return self.triangles.shape[0]

    @property
    def centroids(self) -> np.ndarray:
        """Triangle centroids ``(n_triangles, 3)`` in metres."""
        return self.vertices[self.triangles].mean(axis=1)

    @property
    def areas(self) -> np.ndarray:
        """Triangle areas ``(n_triangles,)`` in square metres."""
        return 0.5 * np.linalg.norm(self._face_normals, axis=1)

    @property
    def normals(self) -> np.ndarray:
        """Outward unit normals ``(n_triangles, 3)`` (oriented away from the centre)."""
        unit = self._face_normals / np.linalg.norm(self._face_normals, axis=1, keepdims=True)
        sign = np.sign(np.einsum("ij,ij->i", unit, self.centroids - self.vertices.mean(0)))
        sign[sign == 0] = 1.0
        return unit * sign[:, None]

    @property
    def _face_normals(self) -> np.ndarray:
        points = self.vertices[self.triangles]
        return np.cross(points[:, 1] - points[:, 0], points[:, 2] - points[:, 0])

    @pyaedt_function_handler()
    def element_positions(self) -> np.ndarray:
        """Per-source element position ``(n_sources, 3)`` from the field energy centroid.

        For an array whose elements sit at distinct lattice sites on a shared
        radiation surface, this recovers each element location -- used to build a
        scan taper with :meth:`steering_weights`.
        """
        weight = (np.abs(self.e_sources) ** 2).sum(-1)
        return np.einsum("sn,nd->sd", weight, self.centroids) / weight.sum(1, keepdims=True)

    @pyaedt_function_handler()
    def steering_weights(self, theta_scan: float, phi_scan: float, frequency: float | None = None) -> np.ndarray:
        """Phase weights ``exp(-j k r_s . r_e)`` that steer the beam to ``(theta, phi)`` in degrees."""
        frequency = self.frequency if frequency is None else frequency
        k = 2 * np.pi * frequency / SpeedOfLight
        theta, phi = np.deg2rad(theta_scan), np.deg2rad(phi_scan)
        scan = np.array([np.sin(theta) * np.cos(phi), np.sin(theta) * np.sin(phi), np.cos(theta)])
        return np.exp(-1j * k * (self.element_positions() @ scan))

    @pyaedt_function_handler()
    def combined_field(self, weights=None):
        """Superpose the sources into a single tangential ``(E, H)`` per triangle."""
        if weights is None:
            weights = np.ones(self.n_sources, dtype=complex)
        weights = np.asarray(weights, dtype=complex)
        if weights.shape != (self.n_sources,):
            raise ValueError(f"'weights' must have length {self.n_sources}.")
        e_field = np.tensordot(weights, self.e_sources, axes=(0, 0))
        h_field = np.tensordot(weights, self.h_sources, axes=(0, 0))
        return e_field, h_field

    @pyaedt_function_handler()
    def far_field(self, frequency: float | None = None, theta=None, phi=None, weights=None):
        """Reconstruct the far field with the NF2FF transform.

        Parameters
        ----------
        frequency : float, optional
            Frequency in Hz. Defaults to the value read from ``fields.evtrs``.
        theta : numpy.ndarray, optional
            Theta angles in degrees. Defaults to ``0:180`` in 2 degree steps.
        phi : numpy.ndarray, optional
            Phi angles in degrees. Defaults to ``-180:180`` in 2 degree steps.
        weights : numpy.ndarray, optional
            Complex excitation weight per source. Defaults to uniform.

        Returns
        -------
        tuple of numpy.ndarray
            ``(rEtheta, rEphi)``, each shaped ``(len(theta), len(phi))`` and complex.
        """
        frequency = self.frequency if frequency is None else frequency
        if frequency is None:
            raise ValueError("Frequency is unknown; pass 'frequency'.")
        theta = np.linspace(0, 180, 91) if theta is None else np.asarray(theta, dtype=float)
        phi = np.linspace(-180, 180, 181) if phi is None else np.asarray(phi, dtype=float)
        e_field, h_field = self.combined_field(weights)
        return _near_to_far_field(self.centroids, e_field, h_field, frequency, theta, phi, self.normals, self.areas)


@pyaedt_function_handler()
def far_field_data_from_aedtresults(
    folder,
    frequency: float | None = None,
    output_dir=None,
    theta=None,
    phi=None,
    weights=None,
) -> FfdSolutionData:
    """Build a :class:`FfdSolutionData` from the binary surface fields in ``.aedtresults``.

    Decodes the radiation-surface mesh and tangential fields, reconstructs the far
    field through NF2FF, writes a standard ``.ffd`` plus a
    ``pyaedt_antenna_metadata.json``, and returns the resulting ``FfdSolutionData``
    -- avoiding a solver round-trip to re-export the ``.ffd``.

    Parameters
    ----------
    folder : str or :class:`pathlib.Path`
        Results folder with ``current.sf_msh`` and ``fields.sf_fld_<k>``.
    frequency : float, optional
        Frequency in Hz. Defaults to the value stored in ``fields.evtrs``.
    output_dir : str or :class:`pathlib.Path`, optional
        Folder for the generated ``.ffd`` and metadata. Defaults to ``folder``.
    theta, phi : numpy.ndarray, optional
        Far-field angle grids in degrees.
    weights : numpy.ndarray, optional
        Complex excitation weight per source (for arrays). Defaults to uniform.

    Returns
    -------
    :class:`ansys.aedt.core.visualization.advanced.farfield_visualization.FfdSolutionData`

    Examples
    --------
    >>> from ansys.aedt.core.visualization.advanced.farfield_binary import (
    ...     far_field_data_from_aedtresults,
    ... )
    >>> data = far_field_data_from_aedtresults(results_folder)  # doctest: +SKIP
    >>> data.plot_cut()  # doctest: +SKIP
    """
    surface = RadiationSurface(folder)
    frequency = surface.frequency if frequency is None else frequency
    if frequency is None:
        raise ValueError("Frequency is unknown; pass 'frequency'.")

    theta = np.linspace(0, 180, 91) if theta is None else np.asarray(theta, dtype=float)
    phi = np.linspace(-180, 180, 181) if phi is None else np.asarray(phi, dtype=float)
    e_theta, e_phi = surface.far_field(frequency, theta, phi, weights)

    output_dir = Path(folder if output_dir is None else output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    ffd_file = output_dir / "farfield.ffd"
    _write_ffd(ffd_file, frequency, theta, phi, e_theta, e_phi)

    metadata = {
        "variation": "Nominal",
        "touchstone_file": "",
        "element_pattern": {
            "antenna": {
                "file_name": ffd_file.name,
                "location": [0.0, 0.0, 0.0],
                "incident_power": {frequency: 1.0},
                "radiated_power": {frequency: 1.0},
                "accepted_power": {frequency: 1.0},
            }
        },
    }
    metadata_file = output_dir / "pyaedt_antenna_metadata.json"
    with open(metadata_file, "w") as handle:
        json.dump(metadata, handle, indent=4)

    logger.info(f"Far field reconstructed from binary surface fields: {ffd_file}")
    return FfdSolutionData(str(metadata_file))


@pyaedt_function_handler()
def _read_mesh(file_name, n_vertices: int, n_triangles: int):
    """Decode ``current.sf_msh`` into vertices (m) and 0-based triangle connectivity."""
    data = Path(file_name).read_bytes()
    vertices = np.empty((n_vertices, 3))
    for i in range(n_vertices):
        vertices[i] = struct.unpack_from("<3d", data, i * _VERTEX_REC + 4)
    base = n_vertices * _VERTEX_REC
    triangles = np.empty((n_triangles, 3), dtype=int)
    for i in range(n_triangles):
        triangles[i] = struct.unpack_from("<4i", data, base + i * _TRI_REC)[1:4]
    return vertices, triangles - 1  # connectivity is 1-based on disk


@pyaedt_function_handler()
def _read_field(file_name, n_triangles: int):
    """Decode one ``fields.sf_fld_<k>`` into node-averaged complex (E, H) per triangle."""
    data = Path(file_name).read_bytes()
    e_field = np.empty((n_triangles, 3), dtype=complex)
    h_field = np.empty((n_triangles, 3), dtype=complex)
    # fixed record stride derived from the first record's node count
    _, ndof = struct.unpack_from("<2i", data, 4)
    stride = _FIELD_HDR + ndof * 12 * 4
    for t in range(n_triangles):
        offset = 4 + t * stride + _FIELD_HDR
        floats = np.frombuffer(data, dtype="<f4", count=ndof * 12, offset=offset)
        e_block = floats[: ndof * 6].reshape(ndof, 6)
        h_block = floats[ndof * 6 :].reshape(ndof, 6)
        e_field[t] = (e_block[:, 0::2] + 1j * e_block[:, 1::2]).mean(0)
        h_field[t] = (h_block[:, 0::2] + 1j * h_block[:, 1::2]).mean(0)
    return e_field, h_field


@pyaedt_function_handler()
def _read_frequency(file_name):
    """Read the solution frequency (Hz) from the ASCII ``fields.evtrs`` header, if present."""
    file_name = Path(file_name)
    if not file_name.is_file():
        return None
    text = file_name.read_bytes()[:4096].decode("latin1", "replace")
    match = re.search(r"Frequency=([0-9.eE+\-]+)", text)
    return float(match.group(1)) if match else None


def _near_to_far_field(points, e_field, h_field, frequency, theta, phi, normals, areas):
    """Stratton-Chu / Love NF2FF over a closed surface.

    Equivalent currents ``J = n x H`` and ``M = -n x E`` are integrated against the
    radiation phase factor over every far-field direction. The common
    ``j k exp(-j k r) / (4 pi r)`` factor is dropped (it cancels in the pattern).
    """
    points = np.asarray(points, dtype=float)
    k = 2 * np.pi * frequency / SpeedOfLight

    j_current = np.cross(normals, h_field) * areas[:, None]
    m_current = -np.cross(normals, e_field) * areas[:, None]

    theta_rad = np.deg2rad(theta)[:, None]
    phi_rad = np.deg2rad(phi)[None, :]
    sin_t, cos_t = np.sin(theta_rad), np.cos(theta_rad)
    sin_p, cos_p = np.sin(phi_rad), np.cos(phi_rad)
    ones = np.ones_like(sin_p)
    r_hat = np.stack([sin_t * cos_p, sin_t * sin_p, cos_t * ones], -1)
    theta_hat = np.stack([cos_t * cos_p, cos_t * sin_p, -sin_t * ones], -1)
    phi_hat = np.stack([-sin_p * np.ones_like(cos_t), cos_p * np.ones_like(cos_t), np.zeros_like(cos_t * sin_p)], -1)

    e_theta = np.zeros(r_hat.shape[:2], dtype=complex)
    e_phi = np.zeros(r_hat.shape[:2], dtype=complex)
    for i in range(r_hat.shape[0]):
        for j_idx in range(r_hat.shape[1]):
            phase = np.exp(1j * k * (points @ r_hat[i, j_idx]))
            n_vec = (j_current * phase[:, None]).sum(0)
            l_vec = (m_current * phase[:, None]).sum(0)
            e_theta[i, j_idx] = -(l_vec @ phi_hat[i, j_idx] + ETA0 * (n_vec @ theta_hat[i, j_idx]))
            e_phi[i, j_idx] = l_vec @ theta_hat[i, j_idx] - ETA0 * (n_vec @ phi_hat[i, j_idx])
    return e_theta, e_phi


def _write_ffd(file_name, frequency, theta, phi, e_theta, e_phi) -> Path:
    """Write a standard ``.ffd`` that :class:`FfdSolutionData` reads."""
    header = f"{theta[0]:g} {theta[-1]:g} {len(theta)}\n{phi[0]:g} {phi[-1]:g} {len(phi)}\nFrequency {frequency:g}\n"
    rows = np.column_stack(
        [e_theta.reshape(-1).real, e_theta.reshape(-1).imag, e_phi.reshape(-1).real, e_phi.reshape(-1).imag]
    )
    with open(file_name, "w") as handle:
        handle.write(header)
        np.savetxt(handle, rows, fmt="%.8e")
    return Path(file_name)
