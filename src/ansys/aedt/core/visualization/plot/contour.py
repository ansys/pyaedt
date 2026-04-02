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
import warnings

from ansys.aedt.core.internal.checks import GRAPHICS_REQUIRED

try:
    import matplotlib.pyplot as plt
    import numpy as np
except ImportError:
    warnings.warn(GRAPHICS_REQUIRED)
from ansys.aedt.core.generic.settings import settings


def bin_to_grid(
    xc: np.ndarray,
    yc: np.ndarray,
    zc: np.ndarray,
    xlim: "tuple[float, float] | None" = None,
    ylim: "tuple[float, float] | None" = None,
) -> "tuple[np.ndarray, np.ndarray, np.ndarray]":
    """Convert scattered (x, y, z) sample data to a regular 2-D grid.

    Parameters
    ----------
    xc : numpy.ndarray
        Array of x-coordinates for each sample.
    yc : numpy.ndarray
        Array of y-coordinates for each sample.
        Must have the same length as ``xc``.
    zc : numpy.ndarray
        Array of scalar values at each ``(xc, yc)``
        sample point.  Must have the same length as ``xc``.
    xlim : tuple[float, float] or None, optional
        ``(x_min, x_max)`` clipping range.  Samples outside this range
        are discarded before gridding. The default is ``None``, in which case the
        full extent of ``xc`` is used.
    ylim : tuple[float, float] or None, optional
        ``(y_min, y_max)`` clipping range.  Samples outside this range
        are discarded before gridding. The default is ``None``, in which case the
        full extent of ``yc`` is used.

    Returns
    -------
    Xc : numpy.ndarray
        Sorted unique x-coordinates of the output grid.
    Yc : numpy.ndarray
        Sorted unique y-coordinates of the output grid.
    Z : numpy.ndarray
        Averaged *zc* values on the ``(Yc, Xc)`` grid.  Grid cells
        that contain no sample are left as ``0``.
    """
    xc = np.asarray(xc).ravel()
    yc = np.asarray(yc).ravel()
    zc = np.asarray(zc).ravel()

    if not (xc.size == yc.size == zc.size):
        raise ValueError("xc, yc, zc must have same length")

    # Optional clipping to limits
    if xlim is None:
        xlim = (np.min(xc), np.max(xc))
    if ylim is None:
        ylim = (np.min(yc), np.max(yc))

    mask = (xc >= xlim[0]) & (xc <= xlim[1]) & (yc >= ylim[0]) & (yc <= ylim[1])
    xc, yc, zc = xc[mask], yc[mask], zc[mask]

    # Unique grid coordinates = full data resolution
    Xc = np.unique(xc)
    Yc = np.unique(yc)

    nx = Xc.size
    ny = Yc.size

    # Map each sample to its grid index
    ix = np.searchsorted(Xc, xc)
    iy = np.searchsorted(Yc, yc)

    # Prepare output arrays
    Z = np.zeros((ny, nx))
    counts = np.zeros((ny, nx))

    # Accumulate using numpy-only operations
    np.add.at(Z, (iy, ix), zc)
    np.add.at(counts, (iy, ix), 1)

    # Avoid division by zero
    counts[counts == 0] = 1
    Z = Z / counts

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
    Xc: np.ndarray,
    Yc: np.ndarray,
    Z: np.ndarray,
    center: "tuple[float, float]",
    prefer_contains: bool = True,
    connectivity: int = 4,
) -> np.ndarray:
    """Extract the eye-opening contour closest to a reference center point.

    Identifies connected zero-valued regions in the density grid ``Z``
    (which correspond to eye openings), selects the region that best
    matches ``center``, and returns its boundary as an (x, y) polygon.

    Parameters
    ----------
    Xc : numpy.ndarray
        1-D array of shape ``(nx,)`` containing the sorted unique
        x-coordinates of the grid.
    Yc : numpy.ndarray
        1-D array of shape ``(ny,)`` containing the sorted unique
        y-coordinates of the grid.
    Z : numpy.ndarray
        2-D density array of shape ``(ny, nx)``.  Cells equal to ``0``
        represent the eye-opening; cells greater than ``0`` represent
        signal traces.
    center : tuple[float, float]
        ``(cx, cy)`` reference point used to disambiguate between
        multiple zero regions (upper, middle, or lower PAM4 eyes).
    prefer_contains : bool, optional
        When ``True`` (default), the zero region that directly contains
        ``center`` is preferred over the nearest-centroid region.
    connectivity : int, optional
        Pixel connectivity used when labelling zero regions.
        Use ``4`` (default) for edge-connected or ``8`` for
        corner-connected regions.

    Returns
    -------
    numpy.ndarray
        Array of shape ``(N, 2)`` with the ``(x, y)`` vertices of the
        eye-opening contour polygon.  Returns an empty array when no
        zero region or contour is found.
    """
    Xc = np.asarray(Xc).ravel()
    Yc = np.asarray(Yc).ravel()
    Z = np.asarray(Z)
    if not (Z.ndim == 2 and Z.shape == (len(Yc), len(Xc))):
        settings.logger.error(f"Z must be 2D with shape (len(Yc), len(Xc)); got {Z.shape}")
        return np.array([])

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


def prepare_and_extract(
    xc: np.ndarray,
    yc: np.ndarray,
    zc: np.ndarray,
    center: "tuple[float, float]",
    prefer_contains: bool = True,
    connectivity: int = 4,
) -> np.ndarray:
    """Convert scattered sample arrays to a grid and extract the eye-opening contour.

    This is a convenience wrapper that calls :func:`bin_to_grid` followed by
    :func:`extract_eye_opening_contour_by_center`.

    Parameters
    ----------
    xc : numpy.ndarray
        1-D array of x-coordinates for each sample.
    yc : numpy.ndarray
        1-D array of y-coordinates for each sample.
        Must have the same length as ``xc``.
    zc : numpy.ndarray
        1-D array of scalar (hit-count or density) values at each
        ``(xc, yc)`` sample point.  Must have the same length as ``xc``.
    center : tuple[float, float]
        ``(cx, cy)`` reference point used to select the eye opening of
        interest when multiple zero regions are present (e.g. PAM4 eyes).
    prefer_contains : bool, optional
        When ``True`` (default), prefer the zero region that directly
        contains ``center`` over the nearest-centroid region.
    connectivity : int, optional
        Pixel connectivity used for labelling zero regions.
        Use ``4`` (default) for edge-connected or ``8`` for
        corner-connected regions.

    Returns
    -------
    numpy.ndarray
        Array of shape ``(N, 2)`` containing the ``(x, y)`` vertices of
        the eye-opening contour polygon.  Returns an empty array when no
        opening is found.
    """
    Xc, Yc, Z = bin_to_grid(
        xc,
        yc,
        zc,
    )
    # Optional: sanity print to avoid shape confusion
    # print("Xc", Xc.shape, "Yc", Yc.shape, "Z", Z.shape, "Z.ndim", Z.ndim)
    return extract_eye_opening_contour_by_center(
        Xc, Yc, Z, center=center, prefer_contains=prefer_contains, connectivity=connectivity
    )
