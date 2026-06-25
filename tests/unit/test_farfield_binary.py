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

"""Unit tests for the binary radiation-surface far-field reader (no live AEDT)."""

import struct

import numpy as np

from ansys.aedt.core.visualization.advanced.farfield_binary import RadiationSurface
from ansys.aedt.core.visualization.advanced.farfield_binary import far_field_data_from_aedtresults
from ansys.aedt.core.visualization.advanced.farfield_binary import parse_surface_mesh_header


def _write_surface(folder, frequency=1.8e9, element_x=(0.0,), suffix=""):
    """Write a synthetic ``current.sf_msh``/``fields.sf_fld_<k>`` results folder.

    A flat strip of two triangles per element; each element's field is planted on
    its own two triangles (localized at ``x = element_x[k]``).
    """
    vertices, triangles, owner = [], [], []
    for k, x in enumerate(element_x):
        base = len(vertices)
        vertices += [(x - 0.01, -0.01, 0.0), (x + 0.01, -0.01, 0.0), (x + 0.01, 0.01, 0.0), (x - 0.01, 0.01, 0.0)]
        triangles += [(base + 1, base + 2, base + 3), (base + 1, base + 3, base + 4)]  # 1-based
        owner += [k, k]
    vertices = np.array(vertices, dtype=float)
    n_vertices, n_triangles = len(vertices), len(triangles)

    (folder / f"current.sf_mshhdr{suffix}").write_text(
        "$begin 'Surface Mesh Header'\n\tBigEndian=false\n\tDataFormat='BINARY'\n"
        f"\tDataPrecision='Double'\n\tNumVertices={n_vertices}\n\tNumMidPoints=0\n"
        f"\tNumTriangles={n_triangles}\n$end 'Surface Mesh Header'\n"
    )
    mesh = bytearray()
    for i, vertex in enumerate(vertices):
        mesh += struct.pack("<i3d", i + 1, *vertex)
    for i, triangle in enumerate(triangles):
        mesh += struct.pack("<7i", 100 + i, triangle[0], triangle[1], triangle[2], -1, -1, -1)
    (folder / f"current.sf_msh{suffix}").write_bytes(mesh)

    for k in range(len(element_x)):
        buffer = bytearray(struct.pack("<i", 0))
        for ti in range(n_triangles):
            buffer += struct.pack("<2i", 100 + ti, 6)
            e_vec = (0.0, 0.0, 1.0) if owner[ti] == k else (0.0, 0.0, 0.0)
            h_vec = (0.01, 0.0, 0.0) if owner[ti] == k else (0.0, 0.0, 0.0)
            node_e = [e_vec[0], 0.0, e_vec[1], 0.0, e_vec[2], 0.0]
            node_h = [h_vec[0], 0.0, h_vec[1], 0.0, h_vec[2], 0.0]
            buffer += struct.pack("<36f", *(node_e * 6))
            buffer += struct.pack("<36f", *(node_h * 6))
        (folder / f"fields.sf_fld_{k}{suffix}").write_bytes(buffer)

    (folder / "fields.evtrs").write_text(
        f"$begin 'Header'\n\tNumSources={len(element_x)}\n\tFrequency={frequency:g}\n$end 'Header'\n"
    )


def test_parse_surface_mesh_header(tmp_path):
    _write_surface(tmp_path)
    header = parse_surface_mesh_header(tmp_path / "current.sf_mshhdr")
    assert header["num_vertices"] == 4
    assert header["num_triangles"] == 2
    assert header["data_precision"] == "Double"
    assert header["big_endian"] is False


def test_radiation_surface_decode(tmp_path):
    _write_surface(tmp_path, frequency=10e9)
    surface = RadiationSurface(tmp_path)
    assert surface.n_sources == 1
    assert surface.n_triangles == 2
    assert surface.frequency == 10e9
    assert surface.e_sources.shape == (1, 2, 3)
    assert np.iscomplexobj(surface.e_sources)
    assert surface.centroids.shape == (2, 3)
    assert np.allclose(np.linalg.norm(surface.normals, axis=1), 1.0)
    assert np.all(surface.areas > 0)


def test_far_field_shape_and_finite(tmp_path):
    _write_surface(tmp_path)
    surface = RadiationSurface(tmp_path)
    theta = np.linspace(0, 180, 19)
    phi = np.linspace(-180, 180, 13)
    e_theta, e_phi = surface.far_field(theta=theta, phi=phi)  # frequency from header
    assert e_theta.shape == (len(theta), len(phi))
    assert np.all(np.isfinite(e_theta)) and np.all(np.isfinite(e_phi))


def test_ffd_solution_data_round_trip(tmp_path):
    _write_surface(tmp_path, frequency=10e9)
    data = far_field_data_from_aedtresults(tmp_path, theta=np.linspace(0, 180, 19), phi=np.linspace(-180, 180, 13))
    assert (tmp_path / "farfield.ffd").is_file()
    assert (tmp_path / "pyaedt_antenna_metadata.json").is_file()
    assert data.all_element_names == ["antenna"]
    assert data.frequencies == [10e9]


def test_multi_source_array_helpers(tmp_path):
    _write_surface(tmp_path, element_x=[-0.05, 0.05])
    surface = RadiationSurface(tmp_path)
    assert surface.n_sources == 2
    # element positions recover the planted x-locations
    assert np.allclose(surface.element_positions()[:, 0], [-0.05, 0.05], atol=1e-3)
    # selecting one source via weights returns that raw source field
    e_field, _ = surface.combined_field(np.array([0.0, 1.0]))
    assert np.allclose(e_field, surface.e_sources[1])
    # steering weights are a pure phase taper
    weights = surface.steering_weights(30.0, 0.0)
    assert np.allclose(np.abs(weights), 1.0)


def test_faddm_domain_suffix_detected(tmp_path):
    _write_surface(tmp_path, element_x=[-0.05, 0.05], suffix="_D0")
    surface = RadiationSurface(tmp_path)
    assert surface.domain == "D0"
    assert surface.n_sources == 2
