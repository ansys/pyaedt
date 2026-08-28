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

"""Adapter layer between shield configuration and transfer-impedance models.

This module defines a small :class:`ShieldModel` structural protocol describing
what the builder requires from any shield model (a frequency-dependent transfer
impedance, and — for braids — optical coverage and DC resistance for logging),
provides :func:`build_shield_model`, a factory that constructs
:class:`~ansys.aedt.core.modeler.advanced_cad.cable_harness.transfer_impedance.FoilShield`
and
:class:`~ansys.aedt.core.modeler.advanced_cad.cable_harness.transfer_impedance.BraidShield`
from a :class:`~ansys.aedt.core.modeler.advanced_cad.cable_harness.configuration.Shield`, and
exposes a ``shield_model_factory`` hook that lets callers inject an alternative
provider (measured :math:`Z_t(f)` data, a vendor model, a unit-test stub)
without modifying the builder.
"""

from __future__ import annotations

from typing import TYPE_CHECKING
from typing import Any
from typing import Protocol
from typing import runtime_checkable

import numpy as np

from ansys.aedt.core.internal.errors import AEDTRuntimeError
from ansys.aedt.core.modeler.advanced_cad.cable_harness import transfer_impedance as _ti

if TYPE_CHECKING:  # pragma: no cover - typing only
    from ansys.aedt.core.modeler.advanced_cad.cable_harness.configuration import Material
    from ansys.aedt.core.modeler.advanced_cad.cable_harness.configuration import Shield

__all__ = ["MeasuredShield", "ShieldModel", "ShieldModelError", "build_shield_model"]


class ShieldModelError(AEDTRuntimeError):
    """Raised when a shield model cannot be constructed from the supplied configuration."""


@runtime_checkable
class ShieldModel(Protocol):
    """Minimal interface the builder relies on for any shield model.

    Any object exposing a ``transfer_impedance(freqs_hz) -> np.ndarray`` method
    satisfies this protocol. Braid-style models may additionally expose
    ``optical_coverage`` and ``dc_resistance_per_m`` for reporting purposes.
    """

    def transfer_impedance(self, freqs_hz: np.ndarray) -> np.ndarray:
        """Return complex transfer impedance in ohm/m at each requested frequency.

        Parameters
        ----------
        freqs_hz : numpy.ndarray
            Frequency array, in Hz.

        Returns
        -------
        numpy.ndarray
            Complex transfer impedance, in ohm/m.
        """
        ...


def build_shield_model(
    shield: Shield,
    *,
    radius_mm: float,
    materials: dict[str, Material],
    provider: Any | None = None,
) -> ShieldModel:
    """Construct a :class:`ShieldModel` from a shield definition.

    Parameters
    ----------
    shield : Shield
        Parsed shield configuration describing either a foil or braid shield.
    radius_mm : float
        Outer radius of the shield tube, in millimetres. Converted to metres
        internally because the physics models use SI units.
    materials : dict[str, Material]
        Material table used to resolve the shield conductivity.
    provider : module or object, optional
        An object or module exposing ``FoilShield`` and ``BraidShield`` classes
        compatible with the
        :mod:`ansys.aedt.core.modeler.advanced_cad.cable_harness.transfer_impedance`
        API. When ``None``, the sibling ``transfer_impedance`` module is used
        directly.

    Returns
    -------
    ShieldModel
        A ready-to-query model whose ``transfer_impedance`` method returns
        ohm/m.

    Raises
    ------
    ShieldModelError
        If the shield material is missing from *materials*, has no conductivity,
        lacks required construction parameters, or uses an unsupported shield
        type.
    """
    if shield.material is None or shield.material not in materials:
        raise ShieldModelError(f"Shield material {shield.material!r} is not defined in 'materials'.")
    sigma = materials[shield.material].conductivity
    if sigma is None:
        raise ShieldModelError(f"Shield material {shield.material!r} has no 'conductivity'.")

    ti = provider if provider is not None else _ti
    radius_m = radius_mm * 1e-3

    if shield.is_foil:
        if shield.thickness is None:
            raise ShieldModelError("Foil shield requires a 'thickness'.")
        construction = shield.construction or {}
        return ti.FoilShield(
            sigma=float(sigma),
            thickness_m=float(shield.thickness) * 1e-3,
            cable_radius_m=radius_m,
            seam_inductance_h_per_m=float(construction.get("seam_inductance", 1.0e-9)),
        )

    if shield.is_braid:
        c = shield.construction or {}
        required = ("wire_diameter", "carriers", "wires_per_carrier", "weave_angle")
        missing = [k for k in required if k not in c]
        if missing:
            raise ShieldModelError(f"Braid shield construction block is missing required key(s): {missing!r}.")
        return ti.BraidShield(
            sigma=float(sigma),
            wire_diameter_m=float(c["wire_diameter"]) * 1e-3,
            carriers=int(c["carriers"]),
            wires_per_carrier=int(c["wires_per_carrier"]),
            weave_angle_deg=float(c["weave_angle"]),
            cable_radius_m=radius_m,
        )

    raise ShieldModelError(f"Unsupported shield type {shield.kind!r}.")


class MeasuredShield:
    """A :class:`ShieldModel` backed by tabulated measured :math:`Z_t(f)` data.

    Useful for validation studies where a datasheet or bench measurement should
    override the analytic model. Values are interpolated (log-frequency,
    complex) onto whatever frequency grid the builder requests.

    Parameters
    ----------
    freqs_hz : numpy.ndarray
        Reference frequency points at which measurements were taken, in Hz.
    zt_ohm_per_m : numpy.ndarray
        Complex transfer impedance measured at each point in *freqs_hz*, in
        ohm/m.

    Raises
    ------
    ValueError
        If *freqs_hz* and *zt_ohm_per_m* do not have equal length.
    """

    def __init__(self, freqs_hz: np.ndarray, zt_ohm_per_m: np.ndarray) -> None:
        self._f = np.asarray(freqs_hz, dtype=float)
        self._zt = np.asarray(zt_ohm_per_m, dtype=complex)
        if self._f.shape != self._zt.shape:
            raise ValueError("freqs_hz and zt_ohm_per_m must have equal length.")

    def transfer_impedance(self, freqs_hz: np.ndarray) -> np.ndarray:
        """Return interpolated transfer impedance at the requested frequencies.

        Real and imaginary parts are interpolated independently on a
        log-frequency axis.

        Parameters
        ----------
        freqs_hz : numpy.ndarray
            Query frequency array, in Hz.

        Returns
        -------
        numpy.ndarray
            Complex transfer impedance at each query frequency, in ohm/m.
        """
        f = np.asarray(freqs_hz, dtype=float)
        lf, lgrid = np.log10(self._f), np.log10(f)
        re = np.interp(lgrid, lf, self._zt.real)
        im = np.interp(lgrid, lf, self._zt.imag)
        return re + 1j * im
