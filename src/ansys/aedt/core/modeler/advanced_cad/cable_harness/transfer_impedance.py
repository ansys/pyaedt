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

"""Closed-form transfer impedance models for cable shields.

This module provides analytic frequency-domain transfer impedance (Z_t) models
for foil and braided-wire cable shields. All models operate on plain NumPy
arrays and require no AEDT session.

The two primary classes are :class:`FoilShield` and :class:`BraidShield`.
Both expose a ``transfer_impedance(freqs_hz)`` method returning complex
impedance in ohm/m.
"""

from __future__ import annotations

from dataclasses import dataclass
import math

import numpy as np

MU0 = 4.0e-7 * math.pi  # H/m
EPS = 1.0e-30  # numerical floor


def _diffusion_impedance(
    sigma: float,
    thickness_m: float,
    freqs_hz: np.ndarray,
) -> np.ndarray:
    """Compute the Schelkunoff diffusion impedance of a thin conducting sheet.

    Evaluates ``Z_d(f) = R_dc * (gamma*t) / sinh(gamma*t)`` where
    ``gamma = (1 + j) / delta`` and ``delta = 1 / sqrt(pi * f * mu0 * sigma)``.
    The DC limit ``Z_d -> R_dc`` is enforced when ``f = 0``.

    Parameters
    ----------
    sigma : float
        Electrical conductivity of the sheet material, in S/m.
    thickness_m : float
        Sheet thickness, in metres.
    freqs_hz : numpy.ndarray
        Frequency array, in Hz.

    Returns
    -------
    numpy.ndarray
        Complex diffusion impedance per square, in ohm/square.

    References
    ----------
    Schelkunoff, S. A., "The Electromagnetic Theory of Coaxial Transmission
    Lines and Cylindrical Shields," Bell System Technical Journal, 13(4),
    1934.
    """
    f = np.asarray(freqs_hz, dtype=float)
    r_dc = 1.0 / (sigma * thickness_m)  # ohm/square at DC

    # At f = 0 the formula is indeterminate; force the DC limit.
    safe_f = np.where(f > 0, f, EPS)
    delta = 1.0 / np.sqrt(np.pi * safe_f * MU0 * sigma)  # skin depth, m
    gamma_t = (1.0 + 1.0j) * thickness_m / delta

    # sinh small-argument limit -> gamma_t, so Z_d -> R_dc.
    sinh_gt = np.sinh(gamma_t)
    z_d = r_dc * np.where(
        np.abs(gamma_t) < 1e-6,
        1.0 + 0.0j,
        gamma_t / sinh_gt,
    )
    return z_d


@dataclass
class FoilShield:
    """Foil-tape shield (for example, aluminium-polyester) with a longitudinal seam.

    Parameters
    ----------
    sigma : float
        Electrical conductivity of the foil material, in S/m.
    thickness_m : float
        Foil thickness, in metres.
    cable_radius_m : float
        Radius of the foil tube, in metres.
    seam_inductance_h_per_m : float, optional
        Per-unit-length seam inductance, in H/m. Heuristic range is 0.5–2 nH/m
        for a typical 1 mm longitudinal overlap. Set to ``0`` for a perfectly
        seamless tube (idealised reference).
    """

    sigma: float
    thickness_m: float
    cable_radius_m: float
    seam_inductance_h_per_m: float = 1.0e-9

    def transfer_impedance(self, freqs_hz: np.ndarray) -> np.ndarray:
        """Return the transfer impedance of the foil shield.

        Evaluates ``Z_t(f) = Z_d(f) / (2*pi*r) + j*omega*L_seam`` where
        ``Z_d`` is the Schelkunoff diffusion impedance per square and the
        geometric factor ``1 / (2*pi*r)`` converts ohm/square to ohm/m for a
        closed tube of radius *r*.

        Parameters
        ----------
        freqs_hz : numpy.ndarray
            Frequency array, in Hz.

        Returns
        -------
        numpy.ndarray
            Complex transfer impedance, in ohm/m.

        References
        ----------
        Schelkunoff, S. A., "The Electromagnetic Theory of Coaxial Transmission
        Lines and Cylindrical Shields," Bell System Technical Journal, 13(4),
        1934.
        """
        f = np.asarray(freqs_hz, dtype=float)
        omega = 2.0 * np.pi * f

        z_d = _diffusion_impedance(self.sigma, self.thickness_m, f)
        circumference = 2.0 * np.pi * self.cable_radius_m
        z_diffusion = z_d / circumference

        z_seam = 1.0j * omega * self.seam_inductance_h_per_m
        return z_diffusion + z_seam


@dataclass
class BraidShield:
    """Single-layer braided wire shield.

    Geometry follows the standard braid convention.

    Parameters
    ----------
    sigma : float
        Electrical conductivity of the wire material, in S/m.
    wire_diameter_m : float
        Diameter of a single strand, in metres.
    carriers : int
        Number of carrier groups around the braid.
    wires_per_carrier : int
        Number of strands within one carrier.
    weave_angle_deg : float
        Angle of carriers measured from the cable axis, in degrees.
    cable_radius_m : float
        Mean braid radius, in metres.
    """

    sigma: float
    wire_diameter_m: float
    carriers: int
    wires_per_carrier: int
    weave_angle_deg: float
    cable_radius_m: float

    @property
    def fill_factor(self) -> float:
        """Return the fraction of one half-shell covered by carriers in one direction.

        Returns
        -------
        float
            Dimensionless fill factor ``f = N*n*d / (2*pi*r*cos(alpha))``.
        """
        alpha = math.radians(self.weave_angle_deg)
        n_c = self.carriers
        n_w = self.wires_per_carrier
        d = self.wire_diameter_m
        r = self.cable_radius_m
        return (n_c * n_w * d) / (2.0 * math.pi * r * math.cos(alpha))

    @property
    def optical_coverage(self) -> float:
        """Return the optical coverage ``K = 2f - f**2``, clipped to ``[0, 1]``.

        Returns
        -------
        float
            Dimensionless optical coverage in the range ``[0, 1]``.
        """
        f = self.fill_factor
        return max(0.0, min(1.0, 2.0 * f - f * f))

    @property
    def dc_resistance_per_m(self) -> float:
        """Return the DC resistance per metre of the braid as a whole.

        Treats all carrier wires as parallel conductors of length
        ``L / cos(alpha)``.

        Returns
        -------
        float
            DC resistance, in ohm/m.
        """
        alpha = math.radians(self.weave_angle_deg)
        a_wire = math.pi * (self.wire_diameter_m / 2.0) ** 2
        n_total = self.carriers * self.wires_per_carrier
        r_per_wire = 1.0 / (self.sigma * a_wire * math.cos(alpha))
        return r_per_wire / n_total

    def _diffusion_term(self, freqs_hz: np.ndarray) -> np.ndarray:
        """Compute the diffusion contribution to braid transfer impedance.

        Uses the Schelkunoff form with an effective wall thickness equal to the
        wire diameter, normalised to per-metre cable length using the braid DC
        resistance. At ``f -> 0`` this returns exactly ``R_dc``.

        Parameters
        ----------
        freqs_hz : numpy.ndarray
            Frequency array, in Hz.

        Returns
        -------
        numpy.ndarray
            Complex diffusion term of the transfer impedance, in ohm/m.
        """
        z_d_per_sq = _diffusion_impedance(self.sigma, self.wire_diameter_m, freqs_hz)
        # Normalise to per-metre using the braid DC resistance: at f -> 0
        # this returns exactly R_dc, then rolls off with skin effect.
        return self.dc_resistance_per_m * (z_d_per_sq / z_d_per_sq[0].real)

    def _aperture_inductance(self) -> float:
        """Compute the Vance aperture mutual inductance per metre.

        Evaluates ``M_12 ~ (mu0 / (pi * N_c)) * (1 - K)**(3/2) * tan(alpha)``.

        Returns
        -------
        float
            Aperture mutual inductance, in H/m.

        References
        ----------
        Vance, E. F., "Shielding Effectiveness of Braided-Wire Shields," IEEE
        Transactions on Electromagnetic Compatibility, 17(2), 1975.

        Kley, T., "Optimized Single-Braided Cable Shields," IEEE Transactions on
        Electromagnetic Compatibility, 35(1), 1993.
        """
        alpha = math.radians(self.weave_angle_deg)
        k = self.optical_coverage
        leakage = (1.0 - k) ** 1.5
        return (MU0 / (math.pi * self.carriers)) * leakage * math.tan(alpha)

    def transfer_impedance(self, freqs_hz: np.ndarray) -> np.ndarray:
        """Return the transfer impedance of the braid shield.

        Evaluates ``Z_t(f) = Z_diffusion(f) + j*omega*M_12`` where
        ``Z_diffusion`` captures skin-effect roll-off and ``M_12`` is the Vance
        aperture inductance.

        Parameters
        ----------
        freqs_hz : numpy.ndarray
            Frequency array, in Hz.

        Returns
        -------
        numpy.ndarray
            Complex transfer impedance, in ohm/m.

        References
        ----------
        Vance, E. F., "Shielding Effectiveness of Braided-Wire Shields," IEEE
        Transactions on Electromagnetic Compatibility, 17(2), 1975.

        Kley, T., "Optimized Single-Braided Cable Shields," IEEE Transactions on
        Electromagnetic Compatibility, 35(1), 1993.
        """
        f = np.asarray(freqs_hz, dtype=float)
        omega = 2.0 * np.pi * f
        return self._diffusion_term(f) + 1.0j * omega * self._aperture_inductance()


def report_zt(
    name: str,
    zt: np.ndarray,
    freqs_hz: np.ndarray,
    checkpoints_hz: tuple[float, ...] = (1e3, 1e6, 1e8, 1e9),
) -> None:
    """Log ``|Z_t|`` in mΩ/m at a set of canonical spot frequencies.

    Parameters
    ----------
    name : str
        Label for the shield model, used in the log output.
    zt : numpy.ndarray
        Complex transfer impedance array, in ohm/m, evaluated at *freqs_hz*.
    freqs_hz : numpy.ndarray
        Frequency array corresponding to *zt*, in Hz.
    checkpoints_hz : tuple[float, ...], optional
        Spot frequencies at which to report, in Hz.
    """
    from ansys.aedt.core.aedt_logger import pyaedt_logger

    pyaedt_logger.info("Transfer impedance: %s", name)
    for fc in checkpoints_hz:
        idx = int(np.argmin(np.abs(freqs_hz - fc)))
        f_actual = freqs_hz[idx]
        mag = abs(zt[idx]) * 1e3  # mΩ/m
        pyaedt_logger.info("  f = %8.2e Hz   |Z_t| = %8.3f mOhm/m", f_actual, mag)
