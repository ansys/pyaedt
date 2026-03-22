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

import matplotlib.pyplot as plt
import numpy as np

from ansys.aedt.core.generic.settings import settings


# --- 1) Bin your 1D samples (xc, yc, zc) to a regular grid (Xc, Yc, Z) ---
def bin_to_grid(xc, yc, zc, nx=2000, ny=2000, xlim=None, ylim=None):
    """
    Convert scattered or per-sample arrays to a regular grid for contouring.

    xc, yc, zc: 1D arrays (length N)

    Returns
    -------
      Xc: (nx,) grid centers along X (monotonic)
      Yc: (ny,) grid centers along Y (monotonic)
      Z : (ny, nx) aggregated values per cell
    """
    xc = np.asarray(xc).ravel()
    yc = np.asarray(yc).ravel()
    zc = np.asarray(zc).ravel()
    if not xc.size == yc.size == zc.size:
        settings.logger.error("xc, yc, zc must have the same length")
        return

    if xlim is None:
        xlim = (float(np.nanmin(xc)), float(np.nanmax(xc)))
    if ylim is None:
        ylim = (float(np.nanmin(yc)), float(np.nanmax(yc)))

    xedges = np.linspace(xlim[0], xlim[1], nx + 1)
    yedges = np.linspace(ylim[0], ylim[1], ny + 1)

    H, _, _ = np.histogram2d(yc, xc, bins=[yedges, xedges], weights=zc)  # (ny, nx)

    Xc = 0.5 * (xedges[:-1] + xedges[1:])
    Yc = 0.5 * (yedges[:-1] + yedges[1:])
    Z = H.astype(float)
    return Xc, Yc, Z


def _label_connected_components(mask, connectivity=4):
    from scipy.ndimage import label as _scipy_label

    if connectivity == 8:
        structure = np.ones((3, 3), dtype=int)
    else:
        structure = np.array([[0, 1, 0], [1, 1, 1], [0, 1, 0]], dtype=int)
    labels, num = _scipy_label(mask, structure=structure)
    return labels.astype(np.int32, copy=False), int(num)


def _nearest_index(sorted_1d, value):
    arr = np.asarray(sorted_1d)
    i = int(np.clip(np.searchsorted(arr, value), 1, len(arr) - 1))
    return i if abs(arr[i] - value) < abs(arr[i - 1] - value) else i - 1


# --- 3) Robust contour extraction (version-agnostic using .allsegs) ---
def _extract_contours_xy(Xc, Yc, mask_float, level=0.5):
    """
    Returns list of polygons (each Nx2) via marching squares on a binary mask.
    Works across Matplotlib versions using QuadContourSet.allsegs.
    """
    fig, ax = plt.subplots()
    try:
        cs = ax.contour(Xc, Yc, mask_float, levels=[level])
        polys = []
        if hasattr(cs, "allsegs") and len(cs.allsegs) > 0 and len(cs.allsegs[0]) > 0:
            for seg in cs.allsegs[0]:
                polys.append(seg.copy())
        else:
            # Fallback to collections if available
            if hasattr(cs, "collections") and cs.collections:
                paths = cs.collections[0].get_paths() or []
                for p in paths:
                    polys.append(p.vertices.copy())
        return polys
    finally:
        plt.close(fig)


def _polygon_area(poly_xy):
    x, y = poly_xy[:, 0], poly_xy[:, 1]
    return 0.5 * abs(np.dot(x, np.roll(y, -1)) - np.dot(y, np.roll(x, -1)))


# --- 4) Main: select eye opening by center and return its contour ---
def extract_eye_opening_contour_by_center(
    Xc,
    Yc,
    Z,
    center,
    prefer_contains=True,
    connectivity=4,
):
    """
    Xc: (nx,), Yc: (ny,), Z: (ny, nx) with 0 in opening/background, >0 on traces.
    center: (cx, cy) to disambiguate (e.g., upper/middle/lower PAM4 eye).
    """
    Xc = np.asarray(Xc).ravel()
    Yc = np.asarray(Yc).ravel()
    Z = np.asarray(Z)
    if not (Z.ndim == 2 and Z.shape == (len(Yc), len(Xc))):
        settings.logger.error(f"Z must be 2D with shape (len(Yc), len(Xc)); got {Z.shape}")
        return

    zero_mask = Z == 0
    labels, num = _label_connected_components(zero_mask, connectivity=connectivity)
    if num == 0:
        settings.logger.warning("No zero regions found in Z.")
        return np.array([])

    cx_t, cy_t = float(center[0]), float(center[1])
    ix = _nearest_index(Xc, cx_t)
    iy = _nearest_index(Yc, cy_t)
    contains_label = int(labels[iy, ix]) if zero_mask[iy, ix] else 0

    # Region stats
    regions = []
    for k in range(1, num + 1):
        sel = labels == k
        if not sel.any():
            continue
        r, c = np.where(sel)
        cx = float(Xc[c].mean()) if c.size else np.nan
        cy = float(Yc[r].mean()) if r.size else np.nan
        regions.append(
            {"label": k, "contains_center": (k == contains_label), "centroid": (cx, cy), "area_pixels": int(sel.sum())}
        )

    # Choose region
    if prefer_contains and contains_label > 0:
        chosen = next(r for r in regions if r["label"] == contains_label)
    else:
        chosen = min(regions, key=lambda r: (r["centroid"][0] - cx_t) ** 2 + (r["centroid"][1] - cy_t) ** 2)

    opening_mask = labels == chosen["label"]
    polys = _extract_contours_xy(Xc, Yc, opening_mask.astype(float), level=0.5)
    if not polys:
        settings.logger.warning("Contour extraction failed (no polygons returned).")
        return np.array([])

    contour = max(polys, key=_polygon_area)

    return contour


def prepare_and_extract(xc, yc, zc, center, nx=400, ny=300, prefer_contains=True, connectivity=4):
    """
    Convert 1D sample arrays to a grid and extract the eye opening contour.
    Returns (contour, info) if return_meta=True else contour.
    """
    Xc, Yc, Z = bin_to_grid(
        xc,
        yc,
        zc,
        nx=nx,
        ny=ny,
    )
    # Optional: sanity print to avoid shape confusion
    # print("Xc", Xc.shape, "Yc", Yc.shape, "Z", Z.shape, "Z.ndim", Z.ndim)
    return extract_eye_opening_contour_by_center(
        Xc, Yc, Z, center=center, prefer_contains=prefer_contains, connectivity=connectivity
    )
