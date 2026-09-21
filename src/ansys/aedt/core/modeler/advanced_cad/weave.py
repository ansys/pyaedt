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
from typing import Any
from typing import cast

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
    from ansys.aedt.core.modeler.modeler_3d import Modeler3D

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

    Examples
    --------
    >>> from ansys.aedt.core.modeler.advanced_cad.weave import Weave
    >>> from ansys.aedt.core import Hfss
    >>> hfss = Hfss()
    >>> obj = Weave()
    >>> sub = hfss.modeler.create_box([0, 0, 0], [5, 10, 2])
    >>> w1 = weave.create_weave(hfss, sub)
    """

    def __init__(self) -> None:
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
        self._rotation = 0.0
        self._facet_ellipse_segs = 8
        self._facet_path_segs_per_half = 6
        self._subtract_from_substrate = False
        self._sectors_per_pitch = 1

    @property
    def yarn_material(self) -> str:
        """Yarn material name.

        Returns
        -------
        str
            Name of the yarn material.

        Examples
        --------
        >>> from ansys.aedt.core.modeler.advanced_cad.weave import Weave
        >>> obj = Weave()
        >>> mat = obj.yarn_material

        """
        return self._yarn_material

    @yarn_material.setter
    def yarn_material(self, value: str) -> None:
        self._yarn_material = str(value)

    @property
    def yarn_permittivity(self) -> float:
        """Yarn relative permittivity (Dk).

        Returns
        -------
        float
            Relative permittivity used for yarn material.

        Examples
        --------
        >>> from ansys.aedt.core.modeler.advanced_cad.weave import Weave
        >>> obj = Weave()
        >>> dk = obj.yarn_permittivity

        """
        return self._yarn_permittivity

    @yarn_permittivity.setter
    def yarn_permittivity(self, value: float) -> None:
        if value <= 0:
            raise ValueError("yarn_permittivity must be positive.")
        self._yarn_permittivity = float(value)

    @property
    def yarn_loss_tangent(self) -> float:
        """Yarn dielectric loss tangent.

        Returns
        -------
        float
            Dielectric loss tangent for yarn material.

        Examples
        --------
        >>> from ansys.aedt.core.modeler.advanced_cad.weave import Weave
        >>> obj = Weave()
        >>> lt = obj.yarn_loss_tangent

        """
        return self._yarn_loss_tangent

    @yarn_loss_tangent.setter
    def yarn_loss_tangent(self, value: float) -> None:
        self._yarn_loss_tangent = float(value)

    @property
    def target_pitch_x(self) -> float:
        """Target pitch in the X direction in millimeters.

        Returns
        -------
        float
            Target weave pitch along X in millimeters.

        Examples
        --------
        >>> from ansys.aedt.core.modeler.advanced_cad.weave import Weave
        >>> obj = Weave()
        >>> px = obj.target_pitch_x

        """
        return self._target_pitch_x

    @target_pitch_x.setter
    def target_pitch_x(self, value: float) -> None:
        if value <= 0:
            raise ValueError("target_pitch_x must be positive")
        self._target_pitch_x = float(value)

    @property
    def target_pitch_y(self) -> float:
        """Target pitch in the Y direction in millimeters.

        Returns
        -------
        float
            Target weave pitch along Y in millimeters.

        Examples
        --------
        >>> from ansys.aedt.core.modeler.advanced_cad.weave import Weave
        >>> obj = Weave()
        >>> py = obj.target_pitch_y

        """
        return self._target_pitch_y

    @target_pitch_y.setter
    def target_pitch_y(self, value: float) -> None:
        if value <= 0:
            raise ValueError("target_pitch_y must be positive")
        self._target_pitch_y = float(value)

    @property
    def target_amplitude(self) -> float:
        """Target amplitude of yarn undulation in millimeters.

        Returns
        -------
        float
            Undulation amplitude in millimeters.

        Examples
        --------
        >>> from ansys.aedt.core.modeler.advanced_cad.weave import Weave
        >>> obj = Weave()
        >>> a = obj.target_amplitude

        """
        return self._target_amplitude

    @target_amplitude.setter
    def target_amplitude(self, value: float) -> None:
        self._target_amplitude = float(value)

    @property
    def warp_width(self) -> float:
        """Warp yarn width in millimeters.

        Returns
        -------
        float
            Width of warp yarn cross-section in millimeters.

        Examples
        --------
        >>> from ansys.aedt.core.modeler.advanced_cad.weave import Weave
        >>> obj = Weave()
        >>> w = obj.warp_width

        """
        return self._warp_width

    @warp_width.setter
    def warp_width(self, value: float) -> None:
        self._warp_width = float(value)

    @property
    def fill_width(self) -> float:
        """Fill yarn width in millimeters.

        Returns
        -------
        float
            Width of fill yarn cross-section in millimeters.

        Examples
        --------
        >>> from ansys.aedt.core.modeler.advanced_cad.weave import Weave
        >>> obj = Weave()
        >>> f = obj.fill_width

        """
        return self._fill_width

    @fill_width.setter
    def fill_width(self, value: float) -> None:
        self._fill_width = float(value)

    @property
    def ratio_warp(self) -> float:
        """Warp height ratio (relative factor used to compute yarn height).

        Returns
        -------
        float
            Ratio applied to `warp_width` to compute vertical yarn height.

        Examples
        --------
        >>> from ansys.aedt.core.modeler.advanced_cad.weave import Weave
        >>> obj = Weave()
        >>> r = obj.ratio_warp

        """
        return self._ratio_warp

    @ratio_warp.setter
    def ratio_warp(self, value: float) -> None:
        self._ratio_warp = float(value)

    @property
    def ratio_fill(self) -> float:
        """Fill height ratio (relative factor used to compute yarn height).

        Returns
        -------
        float
            Ratio applied to `fill_width` to compute vertical yarn height.

        Examples
        --------
        >>> from ansys.aedt.core.modeler.advanced_cad.weave import Weave
        >>> obj = Weave()
        >>> r = obj.ratio_fill

        """
        return self._ratio_fill

    @ratio_fill.setter
    def ratio_fill(self, value: float) -> None:
        self._ratio_fill = float(value)

    @property
    def shift_y(self) -> float:
        """Y-shift applied to the weave coordinate system in millimeters.

        Returns
        -------
        float
            Offset applied along Y when creating the weave.

        Examples
        --------
        >>> from ansys.aedt.core.modeler.advanced_cad.weave import Weave
        >>> obj = Weave()
        >>> s = obj.shift_y
        """
        return self._weave_shift_y

    @shift_y.setter
    def shift_y(self, value: float) -> None:
        self._weave_shift_y = float(value)

    @property
    def rotation(self) -> float:
        """Rotation applied to the weave coordinate system in degrees.

        Returns
        -------
        float
            Rotation angle in degrees.

        Examples
        --------
        >>> from ansys.aedt.core.modeler.advanced_cad.weave import Weave
        >>> obj = Weave()
        >>> r = obj.rotation

        """
        return self._rotation

    @rotation.setter
    def rotation(self, value: float) -> None:
        self._rotation = float(value)

    @property
    def facet_ellipse_segments(self) -> int:
        """Number of segments used to approximate yarn ellipse profiles.

        Returns
        -------
        int
            Number of segments for ellipse approximations.

        Examples
        --------
        >>> from ansys.aedt.core.modeler.advanced_cad.weave import Weave
        >>> obj = Weave()
        >>> n = obj.facet_ellipse_segments

        """
        return self._facet_ellipse_segs

    @facet_ellipse_segments.setter
    def facet_ellipse_segments(self, value: int) -> None:
        self._facet_ellipse_segs = int(value)

    @property
    def facet_path_segments_per_half(self) -> int:
        """Path segmentation per half-period used to discretize yarn paths.

        Returns
        -------
        int
            Number of path segments per half-period.

        Examples
        --------
        >>> from ansys.aedt.core.modeler.advanced_cad.weave import Weave
        >>> obj = Weave()
        >>> n = obj.facet_path_segments_per_half

        """
        return self._facet_path_segs_per_half

    @facet_path_segments_per_half.setter
    def facet_path_segments_per_half(self, value: int) -> None:
        self._facet_path_segs_per_half = int(value)

    @property
    def subtract_from_substrate(self) -> bool:
        """Whether the created weave bodies should be subtracted from the substrate.

        Returns
        -------
        bool
            If True, weave bodies are subtracted from the substrate.

        Examples
        --------
        >>> from ansys.aedt.core.modeler.advanced_cad.weave import Weave
        >>> obj = Weave()
        >>> flag = obj.subtract_from_substrate

        """
        return self._subtract_from_substrate

    @subtract_from_substrate.setter
    def subtract_from_substrate(self, value: bool) -> None:
        self._subtract_from_substrate = bool(value)

    @property
    def sectors_per_pitch(self) -> int:
        """Number of homogenized sectors per weave pitch.

        Returns
        -------
        int
            Number of sectors used when creating homogenized regions per pitch.

        Examples
        --------
        >>> from ansys.aedt.core.modeler.advanced_cad.weave import Weave
        >>> obj = Weave()
        >>> s = obj.sectors_per_pitch

        """
        return self._sectors_per_pitch

    @sectors_per_pitch.setter
    def sectors_per_pitch(self, value: int) -> None:
        if int(value) < 1:
            raise ValueError("sectors_per_pitch must be >= 1")
        self._sectors_per_pitch = int(value)

    @property
    def weave_parameters(self) -> dict:
        """Current weave parameters as a dictionary.

        Returns
        -------
        dict

        Examples
        --------
        >>> from ansys.aedt.core.modeler.advanced_cad.weave import Weave
        >>> obj = Weave()
        >>> param = obj.weave_parameters

        """
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
            "shift_y": self.shift_y,
            "rotation": self.rotation,
            "facet_ellipse_segments": self.facet_ellipse_segments,
            "facet_path_segments_per_half": self.facet_path_segments_per_half,
            "subtract_from_substrate": self.subtract_from_substrate,
            "sectors_per_pitch": self.sectors_per_pitch,
        }

    @classmethod
    def from_dict(cls, data: dict) -> Weave:
        """Create a `Weave` instance from a dictionary.

        Parameters
        ----------
        data: dict
            Dictionary with parameter keys matching `weave_parameters`.

        Returns
        -------
        Weave
            Configured Weave instance.

        Examples
        --------
        >>> from ansys.aedt.core.modeler.advanced_cad.weave import Weave
        >>> weave1 = Weave()
        >>> param = weave1.weave_parameters
        >>> weave2 = Weave.from_dict(param)

        """
        w = cls()
        for k, v in data.items():
            if hasattr(w, k):
                setattr(w, k, v)
        return w

    def export_to_json(self, output_file: str | Path) -> bool:
        """Export current weave parameters to a JSON file.

        Parameters
        ----------
        output_file: str or :class:`pathlib.Path`
            Full path to the file, including its extension.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        Examples
        --------
        >>> from ansys.aedt.core.modeler.advanced_cad.weave import Weave
        >>> weave = Weave()
        >>> weave.export_to_json(r"C:\\Temp\\parameters.json")

        """
        return write_configuration_file(self.weave_parameters, str(output_file))

    @classmethod
    def load_from_json(cls, input_file: str | Path) -> Weave:
        """Load weave parameters from a JSON or TOML file and return a configured Weave.

        Parameters
        ----------
        input_file: str or :class:`pathlib.Path`
            Full path to the file, including its extension.

        Returns
        -------
        Weave
            Configured Weave instance.

        Examples
        --------
        >>> from ansys.aedt.core.modeler.advanced_cad.weave import Weave
        >>> weave1 = Weave()
        >>> weave1.export_to_json(r"C:\\Temp\\parameters.json")
        >>> weave2 = Weave.load_from_json(r"C:\\Temp\\parameters.json")

        """
        data = read_configuration_file(str(input_file))
        return cls.from_dict(data)

    @pyaedt_function_handler()
    def set_weave_style(self, style: str) -> None:
        """Resolve weave preset values from `WEAVE_STYLES`.

        Parameters
        ----------
        style: str
            Weave style. Styles are available in WEAVE_STYLES constant.

        Examples
        --------
        >>> from ansys.aedt.core.modeler.advanced_cad.weave import Weave
        >>> from ansys.aedt.core.modeler.advanced_cad.weave import WEAVE_STYLES
        >>> weave1 = Weave()
        >>> style1 = list(WEAVE_STYLES.keys())[0]
        >>> weave1.set_weave_style(style1)

        """
        if style not in WEAVE_STYLES:
            msg = f"Unknown weave style '{style}'. Available options are: {list(WEAVE_STYLES.keys())}"
            raise ValueError(msg)
        preset = WEAVE_STYLES[style]
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
        app: Hfss | Maxwell3d | Q3d | Icepak,
        assignment: int | str | Object3d,
        weave_style: str | None = None,
        name: str | None = None,
    ) -> Object3d:
        """Create a woven yarn geometry (warp and fill) clipped to the provided reference object.

        Parameters
        ----------
        app:
            AEDT application instance used by the `Weave` object.
        assignment : int, str, or :class:`ansys.aedt.core.modeler.cad.object_3d.Object3d`
            Reference body used to create the weave.
        weave_style: str, optional
            Weave style. Styles are available in WEAVE_STYLES constant.
        name: str, optional
            Name prefix for the created weave bodies. The default is ``None``, in which case the
            default name is assigned.

        Returns
        -------
        Object3d
            The created weave object.

        Examples
        --------
        >>> from ansys.aedt.core.modeler.advanced_cad.weave import Weave
        >>> from ansys.aedt.core import Hfss
        >>> hfss = Hfss()
        >>> sub = hfss.modeler.create_box([0, 0, 0], [5, 10, 2])
        >>> weave = Weave()
        >>> weave.create_weave(hfss, sub)

        """
        m = cast("Modeler3D", app.modeler)
        logger = app.logger

        if not name:
            name = "Weave"

        substrate = m._resolve_object(assignment)

        bbox = substrate.bounding_box
        xmin, ymin, zmin = bbox[0], bbox[1], bbox[2]
        xmax, ymax, zmax = bbox[3], bbox[4], bbox[5]
        sub_w = xmax - xmin
        sub_hy = ymax - ymin

        if weave_style is not None and weave_style in WEAVE_STYLES:
            self.set_weave_style(weave_style)

        if self.yarn_material not in app.materials.material_keys:
            mat = app.materials.add_material(self.yarn_material)
            mat.permittivity = self.yarn_permittivity
            mat.dielectric_loss_tangent = self.yarn_loss_tangent

        diag = math.sqrt(sub_w**2 + sub_hy**2)

        n_cell_x = max(1, round(diag / (2 * self.target_pitch_x)))
        n_cell_y = max(1, round(diag / (2 * self.target_pitch_y)))
        pitch_x = diag / (2 * n_cell_x)
        pitch_y = diag / (2 * n_cell_y)
        max_amplitude = (zmax - zmin) / 2.0 * 0.80
        amplitude = min(self.target_amplitude, max_amplitude)

        app[f"{name}_pitch_x"] = f"{pitch_x}mm"
        app[f"{name}_pitch_y"] = f"{pitch_y}mm"
        app[f"{name}_warp_width"] = f"{self.warp_width}mm"
        app[f"{name}_fill_width"] = f"{self.fill_width}mm"
        app[f"{name}_amplitude"] = f"{amplitude}mm"
        app[f"{name}_span_x"] = f"{diag / 2}mm"
        app[f"{name}_span_y"] = f"{diag / 2}mm"

        n_pts_warp = self.facet_path_segments_per_half * 2 * n_cell_x
        n_pts_fill = self.facet_path_segments_per_half * 2 * n_cell_y

        cs_name = f"{name}_CS"
        existing_cs_names = [cs.name for cs in m.coordinate_systems]
        if cs_name in existing_cs_names:
            cs_to_delete = next(cs for cs in m.coordinate_systems if cs.name == cs_name)
            cs_to_delete.delete()
            logger.info(f"Weave '{name}': deleted existing coordinate system '{cs_name}'.")

        z_mid = (zmin + zmax) / 2.0

        r = math.radians(self.rotation)
        cx, sx = math.cos(r), math.sin(r)
        m.create_coordinate_system(
            origin=[xmin + sub_w / 2, ymin + sub_hy / 2 + self.shift_y, z_mid],
            x_pointing=[cx, sx, 0],
            y_pointing=[-sx, cx, 0],
            name=cs_name,
        )
        m.set_working_coordinate_system(cs_name)

        def _warp_yarn(name_with_prefix, phase):
            sign = "" if phase == "+" else "-"
            z0_expr = f"{name}_amplitude" if phase == "+" else f"-{name}_amplitude"
            m.create_equationbased_curve(
                x_t="_t",
                y_t="0",
                z_t=f"{sign}{name}_amplitude*cos(pi*_t/{name}_pitch_x)",
                t_start=f"-{name}_span_x",
                t_end=f"{name}_span_x",
                num_points=n_pts_warp,
                name=name_with_prefix + "_path",
            )
            m.create_ellipse(
                orientation="YZ",
                origin=["0mm", "0mm", z0_expr],
                major_radius=f"{name}_warp_width/2",
                ratio=self.ratio_warp,
                is_covered=True,
                segments=self.facet_ellipse_segments,
                name=name_with_prefix + "_prof",
            )
            m.sweep_along_path(name_with_prefix + "_prof", name_with_prefix + "_path")
            obj = m[name_with_prefix + "_prof"]
            obj.name = name_with_prefix
            obj.material_name = self.yarn_material
            return m[name_with_prefix]

        def _fill_yarn(name_with_prefix, phase):
            sign = "" if phase == "+" else "-"
            z0_expr = f"{name}_amplitude" if phase == "+" else f"-{name}_amplitude"
            m.create_equationbased_curve(
                x_t="0",
                y_t="_t",
                z_t=f"{sign}{name}_amplitude*cos(pi*_t/{name}_pitch_y)",
                t_start=f"-{name}_span_y",
                t_end=f"{name}_span_y",
                num_points=n_pts_fill,
                name=name_with_prefix + "_path",
            )
            m.create_ellipse(
                orientation="XY",
                origin=["0mm", "0mm", "0mm"],
                major_radius=f"{name}_fill_width/2",
                ratio=self.ratio_fill,
                is_covered=True,
                segments=self.facet_ellipse_segments,
                name=name_with_prefix + "_prof",
            )
            m.rotate(name_with_prefix + "_prof", axis="X", angle="90deg")
            m.move(name_with_prefix + "_prof", ["0mm", "0mm", z0_expr])
            m.sweep_along_path(name_with_prefix + "_prof", name_with_prefix + "_path")
            obj = m[name_with_prefix + "_prof"]
            obj.name = name_with_prefix
            obj.material_name = self.yarn_material
            return m[name_with_prefix]

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

        m.unite(weave_names)
        m[weave_names[0]].name = name

        weave_obj = m[name]

        clip_name = f"WeaveClip_{name}"
        m.create_box(
            origin=[xmin, ymin, zmin],
            sizes=[sub_w, sub_hy, zmax - zmin],
            name=clip_name,
        )
        m.intersect(assignment=[weave_obj.name, clip_name], keep_originals=False)

        if self.subtract_from_substrate:
            m.subtract(
                blank_list=[substrate.name],
                tool_list=weave_obj.name,
                keep_originals=True,
            )

        m.set_working_coordinate_system("Global")
        return weave_obj

    @pyaedt_function_handler()
    def create_weave_homogenized(
        self,
        app: Hfss | Maxwell3d | Q3d | Icepak,
        assignment: int | str | Object3d,
        weave_style: str | None = None,
        name: str | None = None,
    ) -> list[Object3d]:
        """Create a homogenized approximation of the weave as material sectors covering the reference object.

        Parameters
        ----------
        app:
            AEDT application instance used by the `Weave` object.
        assignment : int, str, or :class:`ansys.aedt.core.modeler.cad.object_3d.Object3d`
            Reference body used to create the weave.
        weave_style: str, optional
            Weave style. Styles are available in WEAVE_STYLES constant.
        name: str, optional
            Name prefix for the created weave bodies. The default is ``None``, in which case the
            default name is assigned.

        Returns
        -------
        list
            List of created objects.

        Examples
        --------
        >>> from ansys.aedt.core.modeler.advanced_cad.weave import Weave
        >>> from ansys.aedt.core import Hfss
        >>> hfss = Hfss()
        >>> sub = hfss.modeler.create_box([0, 0, 0], [5, 10, 2])
        >>> weave = Weave()
        >>> weave.create_weave(hfss, sub)

        """
        m = cast("Modeler3D", app.modeler)

        substrate = m._resolve_object(assignment)

        if not name:
            name = "Fiber"

        if weave_style is not None and weave_style in WEAVE_STYLES:
            self.set_weave_style(weave_style)

        self.shift_y = 0.0

        if self.sectors_per_pitch < 1:
            msg = f"sectors_per_pitch must be >= 1, got {self.sectors_per_pitch}."
            raise ValueError(msg)

        bbox = substrate.bounding_box
        xmin, ymin, zmin = bbox[0], bbox[1], bbox[2]
        xmax, ymax, zmax = bbox[3], bbox[4], bbox[5]
        sub_w = xmax - xmin
        sub_hy = ymax - ymin
        thickness = zmax - zmin

        resin_mat = app.materials[substrate.material_name]

        resin_permittivity = self._extract_numeric_scalar(resin_mat.permittivity.value)
        resin_loss_tangent = self._extract_numeric_scalar(resin_mat.dielectric_loss_tangent.value)

        h_warp = min(thickness, self.warp_width * self.ratio_warp)
        h_fill = min(thickness, self.fill_width * self.ratio_fill)

        n_sectors_x = max(1, round((sub_w / self.target_pitch_x) * self.sectors_per_pitch))
        n_sectors_y = max(1, round((sub_hy / self.target_pitch_y) * self.sectors_per_pitch))
        sector_w = sub_w / n_sectors_x
        sector_h = sub_hy / n_sectors_y

        pitch_x = sub_w / max(1, round(sub_w / self.target_pitch_x))
        pitch_y = sub_hy / max(1, round(sub_hy / self.target_pitch_y))

        dk_cache = {}
        sector_objs = []
        for i in range(n_sectors_x):
            x_center = (i + 0.5) * sector_w
            x_mod = x_center % pitch_x
            fill_present = abs(x_mod - pitch_x / 2.0) <= (self.fill_width / 2.0)

            for j in range(n_sectors_y):
                y_center = (j + 0.5) * sector_h
                y_mod = y_center % pitch_y
                warp_present = abs(y_mod - pitch_y / 2.0) <= (self.warp_width / 2.0)

                f_yarn = 0.0
                if warp_present:
                    f_yarn += h_warp / thickness
                if fill_present:
                    f_yarn += h_fill / thickness
                f_yarn = min(1.0, f_yarn)

                key = round(f_yarn, 6)
                if key not in dk_cache:
                    dk_eff = f_yarn * self.yarn_permittivity + (1 - f_yarn) * resin_permittivity
                    tand_eff = f_yarn * self.yarn_loss_tangent + (1 - f_yarn) * resin_loss_tangent
                    mat_name = f"{name}_HomogMat_{len(dk_cache)}"
                    if mat_name not in app.materials.material_keys:
                        mat = app.materials.add_material(mat_name)
                    else:
                        mat = app.materials[mat_name]
                    mat.permittivity = dk_eff
                    mat.dielectric_loss_tangent = tand_eff
                    dk_cache[key] = (mat_name, dk_eff, tand_eff)

                mat_name, dk_eff, tand_eff = dk_cache[key]
                new_name = f"{name}_Sector_{i}_{j}"
                new_sector_obj = m.create_box(
                    origin=[xmin + i * sector_w, ymin + j * sector_h, zmin],
                    sizes=[sector_w, sector_h, thickness],
                    name=new_name,
                    material=mat_name,
                )
                sector_objs.append(new_sector_obj)

        return sector_objs

    @staticmethod
    def _extract_numeric_scalar(val: Any) -> float:  # pragma: no cover
        """Return a scalar numeric value from possibly nested sequences.

        Walks into lists taking the first element until an int/float/str
        is found, then converts it to float. Raises TypeError if no numeric
        scalar can be extracted.
        """
        if isinstance(val, (int, float, str)):
            return float(val)
        if isinstance(val, (list, tuple)):
            if not val:
                raise TypeError("Material property is an empty sequence")
            elem: Any = val[0]
            while isinstance(elem, (list, tuple)):
                if not elem:
                    raise TypeError("Material property contains an empty sequence")
                elem = elem[0]
            if isinstance(elem, (int, float, str)):
                return float(elem)
        raise TypeError("Cannot extract numeric value from material property")
