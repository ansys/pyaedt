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

from __future__ import annotations

import math
from typing import TYPE_CHECKING

from ansys.aedt.core.base import PyAedtBase
from ansys.aedt.core.generic.file_utils import read_configuration_file
from ansys.aedt.core.generic.file_utils import write_configuration_file
from ansys.aedt.core.generic.general_methods import pyaedt_function_handler

if TYPE_CHECKING:
    from pathlib import Path

    from ansys.aedt.core import Hfss
    from ansys.aedt.core import Icepak
    from ansys.aedt.core import Maxwell3d
    from ansys.aedt.core import Q3d
    from ansys.aedt.core.modeler.cad.object_3d import Object3d

WEAVE_STYLES = {
    "1067": dict(
        target_pitch_x=0.28,
        target_pitch_y=0.28,
        warp_width=0.13,
        fill_width=0.13,
        ratio_warp=0.077,
        ratio_fill=0.077,
        target_amplitude=0.025,
        yarn_permittivity=6.0,
        yarn_loss_tangent=0.004,
    ),
    "1080": dict(
        target_pitch_x=0.40,
        target_pitch_y=0.40,
        warp_width=0.18,
        fill_width=0.18,
        ratio_warp=0.067,
        ratio_fill=0.067,
        target_amplitude=0.035,
        yarn_permittivity=6.0,
        yarn_loss_tangent=0.004,
    ),
    "2116": dict(
        target_pitch_x=0.50,
        target_pitch_y=0.50,
        warp_width=0.20,
        fill_width=0.20,
        ratio_warp=0.057,
        ratio_fill=0.057,
        target_amplitude=0.050,
        yarn_permittivity=6.0,
        yarn_loss_tangent=0.004,
    ),
    "7628": dict(
        target_pitch_x=0.80,
        target_pitch_y=0.80,
        warp_width=0.35,
        fill_width=0.28,
        ratio_warp=0.057,
        ratio_fill=0.057,
        target_amplitude=0.080,
        yarn_permittivity=6.0,
        yarn_loss_tangent=0.004,
    ),
}


class Weave(PyAedtBase):
    """Class to create weaves in AEDT.

    Parameters
    ----------
    app:
        AEDT application object.

    Examples
    --------
    >>> from ansys.aedt.core.modeler.advanced_cad.weave import Weave
    >>> from ansys.aedt.core import Hfss
    >>> hfss = Hfss()
    >>> obj = Weave(hfss)

    """

    def __init__(self, app: "Hfss | Maxwell3d | Q3d | Icepak") -> None:
        """Constructor for Weave."""
        self._app = app
        self.logger = self._app.logger

        # Instance-configurable parameters with sensible defaults
        self._yarn_material = "eglass"
        self._yarn_permittivity = 6.0
        self._yarn_loss_tangent = 0.004
        self._target_pitch_x = 0.5
        self._target_pitch_y = 0.5
        self._target_amplitude = 0.05
        self._warp_width = 0.20
        self._fill_width = 0.20
        self._ratio_warp = 0.057
        self._ratio_fill = 0.057
        self._weave_shift_y = 0.0
        self._weave_rotate_deg = 0.0
        self._facet_ellipse_segs = 8
        self._facet_path_segs_per_half = 6
        self._subtract_from_substrate = False
        self._sectors_per_pitch = 1

    @property
    def yarn_material(self) -> str:
        return self._yarn_material

    @yarn_material.setter
    def yarn_material(self, value: str) -> None:
        self._yarn_material = str(value)

    @property
    def yarn_permittivity(self) -> float:
        return self._yarn_permittivity

    @yarn_permittivity.setter
    def yarn_permittivity(self, value: float) -> None:
        if value <= 0:
            raise ValueError("yarn_permittivity must be positive")
        self._yarn_permittivity = float(value)

    @property
    def yarn_loss_tangent(self) -> float:
        return self._yarn_loss_tangent

    @yarn_loss_tangent.setter
    def yarn_loss_tangent(self, value: float) -> None:
        self._yarn_loss_tangent = float(value)

    @property
    def target_pitch_x(self) -> float:
        return self._target_pitch_x

    @target_pitch_x.setter
    def target_pitch_x(self, value: float) -> None:
        if value <= 0:
            raise ValueError("target_pitch_x must be positive")
        self._target_pitch_x = float(value)

    @property
    def target_pitch_y(self) -> float:
        return self._target_pitch_y

    @target_pitch_y.setter
    def target_pitch_y(self, value: float) -> None:
        if value <= 0:
            raise ValueError("target_pitch_y must be positive")
        self._target_pitch_y = float(value)

    @property
    def target_amplitude(self) -> float:
        return self._target_amplitude

    @target_amplitude.setter
    def target_amplitude(self, value: float) -> None:
        self._target_amplitude = float(value)

    @property
    def warp_width(self) -> float:
        return self._warp_width

    @warp_width.setter
    def warp_width(self, value: float) -> None:
        self._warp_width = float(value)

    @property
    def fill_width(self) -> float:
        return self._fill_width

    @fill_width.setter
    def fill_width(self, value: float) -> None:
        self._fill_width = float(value)

    @property
    def ratio_warp(self) -> float:
        return self._ratio_warp

    @ratio_warp.setter
    def ratio_warp(self, value: float) -> None:
        self._ratio_warp = float(value)

    @property
    def ratio_fill(self) -> float:
        return self._ratio_fill

    @ratio_fill.setter
    def ratio_fill(self, value: float) -> None:
        self._ratio_fill = float(value)

    @property
    def weave_shift_y(self) -> float:
        return self._weave_shift_y

    @weave_shift_y.setter
    def weave_shift_y(self, value: float) -> None:
        self._weave_shift_y = float(value)

    @property
    def weave_rotate_deg(self) -> float:
        return self._weave_rotate_deg

    @weave_rotate_deg.setter
    def weave_rotate_deg(self, value: float) -> None:
        self._weave_rotate_deg = float(value)

    @property
    def facet_ellipse_segs(self) -> int:
        return self._facet_ellipse_segs

    @facet_ellipse_segs.setter
    def facet_ellipse_segs(self, value: int) -> None:
        self._facet_ellipse_segs = int(value)

    @property
    def facet_path_segs_per_half(self) -> int:
        return self._facet_path_segs_per_half

    @facet_path_segs_per_half.setter
    def facet_path_segs_per_half(self, value: int) -> None:
        self._facet_path_segs_per_half = int(value)

    @property
    def subtract_from_substrate(self) -> bool:
        return self._subtract_from_substrate

    @subtract_from_substrate.setter
    def subtract_from_substrate(self, value: bool) -> None:
        self._subtract_from_substrate = bool(value)

    @property
    def sectors_per_pitch(self) -> int:
        return self._sectors_per_pitch

    @sectors_per_pitch.setter
    def sectors_per_pitch(self, value: int) -> None:
        if int(value) < 1:
            raise ValueError("sectors_per_pitch must be >= 1")

    @property
    def weave_parameters(self) -> dict:
        """Return current weave parameters as a dictionary."""
        return {
            "yarn_material": self.yarn_material,
            "yarn_permittivity": self.yarn_permittivity,
            "yarn_loss_tangent": self.yarn_loss_tangent,
            "target_pitch_x": self.target_pitch_x,
            "target_pitch_y": self.target_pitch_y,
            "target_amplitude": self.target_amplitude,
            "warp_width": self.warp_width,
            "fill_width": self.fill_width,
            "ratio_warp": self.ratio_warp,
            "ratio_fill": self.ratio_fill,
            "weave_shift_y": self.weave_shift_y,
            "weave_rotate_deg": self.weave_rotate_deg,
            "facet_ellipse_segs": self.facet_ellipse_segs,
            "facet_path_segs_per_half": self.facet_path_segs_per_half,
            "subtract_from_substrate": self.subtract_from_substrate,
            "sectors_per_pitch": self.sectors_per_pitch,
        }

    @classmethod
    def from_dict(cls, app: Hfss | Maxwell3d | Q3d | Icepak, data: dict) -> Weave:
        """Create a `Weave` instance from a parameters dictionary.

        Parameters
        ----------
        app:
            AEDT application instance used by the `Weave` object.
        data: dict
            Dictionary with parameter keys matching `weave_parameters`.

        Returns
        -------
        Weave
            Configured Weave instance.
        """
        w = cls(app)
        for k, v in data.items():
            if hasattr(w, k):
                try:
                    setattr(w, k, v)
                except Exception:
                    # best-effort: skip invalid assignments
                    w.logger.debug(f"Weave.from_dict: skipped setting {k}={v}")
        return w

    def export_to_json(self, output_file: str | Path) -> bool:
        """Export current weave parameters to a JSON file.

        Parameters
        ----------
        output_file : str or :class:`pathlib.Path`
            Full path to the file, including its extension.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        Examples
        --------
        >>> from ansys.aedt.core.generic.file_utils import write_configuration_file
        >>> write_configuration_file({"units": "mm"}, r"C:\\Temp\\settings.json")
        """
        return write_configuration_file(self.weave_parameters, str(output_file))

    @classmethod
    def load_from_json(cls, app: Hfss | Maxwell3d | Q3d | Icepak, json_path: str | Path) -> Weave:
        """Load weave parameters from a JSON or TOML file and return a configured Weave."""
        data = read_configuration_file(str(json_path))
        if not isinstance(data, dict):
            raise ValueError("Configuration file did not contain a dictionary")
        return cls.from_dict(app, data)

    @pyaedt_function_handler()
    def set_weave_style(self, weave_style: str):
        """Resolve weave preset values from `WEAVE_STYLES`."""
        if weave_style not in WEAVE_STYLES:
            msg = f"Unknown weave style '{weave_style}'. Available options are: {list(WEAVE_STYLES.keys())}"
            raise ValueError(msg)
        preset = WEAVE_STYLES[weave_style]
        self.target_pitch_x = preset["target_pitch_x"]
        self.target_pitch_y = preset["target_pitch_y"]
        self.warp_width = preset["warp_width"]
        self.fill_width = preset["fill_width"]
        self.ratio_warp = preset["ratio_warp"]
        self.ratio_fill = preset["ratio_fill"]
        self.target_amplitude = preset["target_amplitude"]
        self.yarn_permittivity = preset["yarn_permittivity"]
        self.yarn_loss_tangent = preset["yarn_loss_tangent"]

    @pyaedt_function_handler()
    def create_weave(
        self,
        substrate: Object3d,
        weave_style: str | None = None,
        name: str | None = None,
    ) -> list:
        # Delegate heavy implementation to the modeler while adapting names
        m = self._app.modeler

        bbox = substrate.bounding_box
        xmin, ymin, zmin = bbox[0], bbox[1], bbox[2]
        xmax, ymax, zmax = bbox[3], bbox[4], bbox[5]
        sub_w = xmax - xmin
        sub_hy = ymax - ymin

        if weave_style is not None and weave_style in WEAVE_STYLES:
            self.set_weave_style(weave_style)

        if self.yarn_material not in self._app.materials.material_keys:
            mat = self._app.materials.add_material(self.yarn_material)
            mat.permittivity = self.yarn_permittivity
            mat.dielectric_loss_tangent = self.yarn_loss_tangent

        diag = math.sqrt(sub_w**2 + sub_hy**2)

        n_cell_x = max(1, round(diag / (2 * self.target_pitch_x)))
        n_cell_y = max(1, round(diag / (2 * self.target_pitch_y)))
        pitch_x = diag / (2 * n_cell_x)
        pitch_y = diag / (2 * n_cell_y)
        max_amplitude = (zmax - zmin) / 2.0 * 0.80
        amplitude = min(self.target_amplitude, max_amplitude)
        if self.target_amplitude > max_amplitude:
            self.logger.warning(
                f"Weave '{name}': requested amplitude {self.target_amplitude}mm exceeds the safe "
                f"limit for the substrate thickness. Clamped to {amplitude:.4f}mm."
            )

        self._app[f"{name}_pitch_x"] = f"{pitch_x}mm"
        self._app[f"{name}_pitch_y"] = f"{pitch_y}mm"
        self._app[f"{name}_warp_width"] = f"{self.warp_width}mm"
        self._app[f"{name}_fill_width"] = f"{self.fill_width}mm"
        self._app[f"{name}_amplitude"] = f"{amplitude}mm"
        self._app[f"{name}_span_x"] = f"{diag / 2}mm"
        self._app[f"{name}_span_y"] = f"{diag / 2}mm"

        n_pts_warp = self.facet_path_segs_per_half * 2 * n_cell_x
        n_pts_fill = self.facet_path_segs_per_half * 2 * n_cell_y

        cs_name = f"{name}_CS"
        existing_cs_names = [cs.name for cs in m.coordinate_systems]
        if cs_name in existing_cs_names:
            cs_to_delete = next(cs for cs in m.coordinate_systems if cs.name == cs_name)
            cs_to_delete.delete()
            self.logger.info(f"Weave '{name}': deleted existing coordinate system '{cs_name}'.")

        weave_prefixes = (
            f"{name}_WarpA",
            f"{name}_WarpB",
            f"{name}_FillA",
            f"{name}_FillB",
        )
        stale = [n for n in m.solid_names if n.startswith(weave_prefixes)]
        if stale:
            m.delete(stale)
            self.logger.info(f"Weave '{name}': removed {len(stale)} stale yarn bodies.")

        z_mid = (zmin + zmax) / 2.0

        r = math.radians(self.weave_rotate_deg)
        cx, sx = math.cos(r), math.sin(r)
        m.create_coordinate_system(
            origin=[xmin + sub_w / 2, ymin + sub_hy / 2 + self.weave_shift_y, z_mid],
            x_pointing=[cx, sx, 0],
            y_pointing=[-sx, cx, 0],
            name=cs_name,
        )
        m.set_working_coordinate_system(cs_name)

        def _warp_yarn(name, phase):
            sign = "" if phase == "+" else "-"
            z0_expr = f"{name}_amplitude" if phase == "+" else f"-{name}_amplitude"
            m.create_equationbased_curve(
                x_t="_t",
                y_t="0",
                z_t=f"{sign}{name}amplitude*cos(pi*_t/{name}_pitch_x)",
                t_start=f"-{name}_span_x",
                t_end=f"{name}_span_x",
                num_points=n_pts_warp,
                name=name + "_path",
            )
            m.create_ellipse(
                orientation="YZ",
                origin=["0mm", "0mm", z0_expr],
                major_radius=f"{name}_warp_width/2",
                ratio=self.ratio_warp,
                is_covered=True,
                segments=self.facet_ellipse_segs,
                name=name + "_prof",
            )
            m.sweep_along_path(name + "_prof", name + "_path")
            obj = m[name + "_prof"]
            obj.name = name
            obj.material_name = self.yarn_material
            return m[name]

        def _fill_yarn(name, phase):
            sign = "" if phase == "+" else "-"
            z0_expr = f"{name}amplitude" if phase == "+" else f"-{name}amplitude"
            m.create_equationbased_curve(
                x_t="0",
                y_t="_t",
                z_t=f"{sign}{name}amplitude*cos(pi*_t/{name}_pitch_y)",
                t_start=f"-{name}_span_y",
                t_end=f"{name}_span_y",
                num_points=n_pts_fill,
                name=name + "_path",
            )
            m.create_ellipse(
                orientation="XY",
                origin=["0mm", "0mm", "0mm"],
                major_radius=f"{name}_fill_width/2",
                ratio=self.ratio_fill,
                is_covered=True,
                segments=self.facet_ellipse_segs,
                name=name + "_prof",
            )
            m.rotate(name + "_prof", axis="X", angle="90deg")
            m.move(name + "_prof", ["0mm", "0mm", z0_expr])
            m.sweep_along_path(name + "_prof", name + "_path")
            obj = m[name + "_prof"]
            obj.name = name
            obj.material_name = self.yarn_material
            return m[name]

        _warp_yarn(f"{name}_WarpA", "+")
        _warp_yarn(f"{name}_WarpB", "-")
        _fill_yarn(f"{name}_FillA", "-")
        _fill_yarn(f"{name}_FillB", "+")

        m.move(f"{name}_WarpB", ["0mm", f"{name}_pitch_y", "0mm"])
        m.move(f"{name}_FillB", [f"{name}_pitch_x", "0mm", "0mm"])

        half_diag = diag / 2
        n_offset_y = math.ceil(half_diag / (2 * pitch_y))
        n_offset_x = math.ceil(half_diag / (2 * pitch_x))
        offset_y = f"-{2 * n_offset_y}*{name}_pitch_y"
        offset_x = f"-{2 * n_offset_x}*{name}_pitch_x"

        for name_warp in [f"{name}_WarpA", f"{name}_WarpB"]:
            m.move(name_warp, ["0mm", offset_y, "0mm"])
        for name_fill in [f"{name}_FillA", f"{name}_FillB"]:
            m.move(name_fill, [offset_x, "0mm", "0mm"])

        weave_names = [
            f"{name}_WarpA",
            f"{name}_WarpB",
            f"{name}_FillA",
            f"{name}_FillB",
        ]

        for base, vec, n in [
            (f"{name}_WarpA", ["0mm", f"2*{name}_pitch_y", "0mm"], n_cell_y + n_offset_y),
            (f"{name}_WarpB", ["0mm", f"2*{name}_pitch_y", "0mm"], n_cell_y + n_offset_y),
            (f"{name}_FillA", [f"2*{name}_pitch_x", "0mm", "0mm"], n_cell_x + n_offset_x),
            (f"{name}_FillB", [f"2*{name}_pitch_x", "0mm", "0mm"], n_cell_x + n_offset_x),
        ]:
            if n < 2:
                continue
            result = m.duplicate_along_line(base, vec, clones=n)
            if isinstance(result, (list, tuple)) and len(result) == 2 and isinstance(result[0], bool):
                _, clone_names = result
            else:
                clone_names = result
            if clone_names:
                weave_names.extend(clone_names)

        m.set_working_coordinate_system("Global")

        unified_name = f"{name}_Weave"
        m.unite(weave_names)
        m[weave_names[0]].name = unified_name

        clip_name = f"_WeaveClip_{name}"
        m.create_box(
            origin=[xmin, ymin, zmin],
            sizes=[sub_w, sub_hy, zmax - zmin],
            name=clip_name,
        )
        m.intersect(assignment=[unified_name, clip_name], keep_originals=False)

        weave_names = [unified_name]

        if self.subtract_from_substrate:
            m.subtract(
                blank_list=[substrate.name],
                tool_list=weave_names,
                keep_originals=True,
            )

        m.set_working_coordinate_system("Global")
        self.logger.info(f"Weave '{name}' created: {len(weave_names)} yarn body/bodies.")
        return weave_names

    @pyaedt_function_handler()
    def create_weave_homogenized(
        self,
        substrate: "Object3d",
        weave_style: str | None = None,
        sectors_per_pitch: int | None = None,
        name_prefix: str | None = None,
        yarn_permittivity: float | None = None,
        yarn_loss_tangent: float | None = None,
        target_pitch_x: float | None = None,
        target_pitch_y: float | None = None,
        warp_width: float | None = None,
        fill_width: float | None = None,
        ratio_warp: float | None = None,
        ratio_fill: float | None = None,
    ) -> list:
        # Prefer instance value when caller omits the argument
        sectors_per_pitch = self.sectors_per_pitch if sectors_per_pitch is None else sectors_per_pitch
        name_prefix = self.name_prefix if name_prefix is None else name_prefix
        yarn_permittivity = self.yarn_permittivity if yarn_permittivity is None else yarn_permittivity
        yarn_loss_tangent = self.yarn_loss_tangent if yarn_loss_tangent is None else yarn_loss_tangent
        target_pitch_x = self.target_pitch_x if target_pitch_x is None else target_pitch_x
        target_pitch_y = self.target_pitch_y if target_pitch_y is None else target_pitch_y
        warp_width = self.warp_width if warp_width is None else warp_width
        fill_width = self.fill_width if fill_width is None else fill_width
        ratio_warp = self.ratio_warp if ratio_warp is None else ratio_warp
        ratio_fill = self.ratio_fill if ratio_fill is None else ratio_fill

        if sectors_per_pitch < 1:
            msg = f"sectors_per_pitch must be >= 1, got {sectors_per_pitch}."
            self.logger.error(msg)
            raise ValueError(msg)

        (
            target_pitch_x,
            target_pitch_y,
            warp_width,
            fill_width,
            ratio_warp,
            ratio_fill,
            _target_amplitude_unused,
            yarn_permittivity,
            yarn_loss_tangent,
        ) = Weave._resolve_weave_style(
            weave_style,
            target_pitch_x,
            target_pitch_y,
            warp_width,
            fill_width,
            ratio_warp,
            ratio_fill,
            0.0,
            yarn_permittivity,
            yarn_loss_tangent,
            self.logger,
            name_prefix,
        )

        return self._create_weave_homogenized(
            substrate=substrate,
            name_prefix=name_prefix,
            sectors_per_pitch=sectors_per_pitch,
            target_pitch_x=target_pitch_x,
            target_pitch_y=target_pitch_y,
            warp_width=warp_width,
            fill_width=fill_width,
            ratio_warp=ratio_warp,
            ratio_fill=ratio_fill,
            yarn_permittivity=yarn_permittivity,
            yarn_loss_tangent=yarn_loss_tangent,
        )

    @pyaedt_function_handler()
    def _create_weave_homogenized(
        self,
        substrate: "Object3d",
        name_prefix: str,
        sectors_per_pitch: int,
        target_pitch_x: float,
        target_pitch_y: float,
        warp_width: float,
        fill_width: float,
        ratio_warp: float,
        ratio_fill: float,
        yarn_permittivity: float,
        yarn_loss_tangent: float,
    ) -> list:
        m = self._app.modeler
        bbox = substrate.bounding_box
        xmin, ymin, zmin = bbox[0], bbox[1], bbox[2]
        xmax, ymax, zmax = bbox[3], bbox[4], bbox[5]
        sub_w = xmax - xmin
        sub_hy = ymax - ymin
        thickness = zmax - zmin

        resin_mat = self._app.materials[substrate.material_name]
        resin_permittivity = resin_mat.permittivity.value
        resin_loss_tangent = resin_mat.dielectric_loss_tangent.value

        h_warp = min(thickness, warp_width * ratio_warp)
        h_fill = min(thickness, fill_width * ratio_fill)

        n_sectors_x = max(1, round((sub_w / target_pitch_x) * sectors_per_pitch))
        n_sectors_y = max(1, round((sub_hy / target_pitch_y) * sectors_per_pitch))
        sector_w = sub_w / n_sectors_x
        sector_h = sub_hy / n_sectors_y

        pitch_x = sub_w / max(1, round(sub_w / target_pitch_x))
        pitch_y = sub_hy / max(1, round(sub_hy / target_pitch_y))

        stale = [n for n in m.solid_names if n.startswith(f"{name_prefix}_Sector_")]
        if stale:
            m.delete(stale)
            self.logger.info(f"Weave '{name_prefix}' (homogenized): removed {len(stale)} stale sector bodies.")

        dk_cache = {}
        sector_names = []
        for i in range(n_sectors_x):
            x_center = (i + 0.5) * sector_w
            x_mod = x_center % pitch_x
            fill_present = abs(x_mod - pitch_x / 2.0) <= (fill_width / 2.0)

            for j in range(n_sectors_y):
                y_center = (j + 0.5) * sector_h
                y_mod = y_center % pitch_y
                warp_present = abs(y_mod - pitch_y / 2.0) <= (warp_width / 2.0)

                f_yarn = 0.0
                if warp_present:
                    f_yarn += h_warp / thickness
                if fill_present:
                    f_yarn += h_fill / thickness
                f_yarn = min(1.0, f_yarn)

                key = round(f_yarn, 6)
                if key not in dk_cache:
                    dk_eff = f_yarn * yarn_permittivity + (1 - f_yarn) * resin_permittivity
                    tand_eff = f_yarn * yarn_loss_tangent + (1 - f_yarn) * resin_loss_tangent
                    mat_name = f"{name_prefix}_HomogMat_{len(dk_cache)}"
                    if mat_name not in self._app.materials.material_keys:
                        mat = self._app.materials.add_material(mat_name)
                    else:
                        mat = self._app.materials[mat_name]
                    mat.permittivity = dk_eff
                    mat.dielectric_loss_tangent = tand_eff
                    dk_cache[key] = (mat_name, dk_eff, tand_eff)

                mat_name, dk_eff, tand_eff = dk_cache[key]
                name = f"{name_prefix}_Sector_{i}_{j}"
                m.create_box(
                    origin=[xmin + i * sector_w, ymin + j * sector_h, zmin],
                    sizes=[sector_w, sector_h, thickness],
                    name=name,
                    material=mat_name,
                )
                sector_names.append(name)

        self.logger.info(
            f"Weave '{name_prefix}' (homogenized): {len(sector_names)} sectors created "
            f"({n_sectors_x}x{n_sectors_y} grid), {len(dk_cache)} distinct Dk_eff region(s): "
            + ", ".join(f"{v[1]:.3f}" for v in dk_cache.values())
        )
        return sector_names
