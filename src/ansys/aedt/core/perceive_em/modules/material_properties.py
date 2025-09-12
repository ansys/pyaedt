# ruff: noqa: E402

# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 - 2025 ANSYS, Inc. and/or its affiliates.
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

from dataclasses import dataclass


@dataclass
class MaterialProperties:
    """
    A data class that represents the properties of a material.

    Attributes
    ----------
    thickness : float
        The thickness of the material. Defaults to -1.0.
    rel_eps_real : float
        The real part of the relative permittivity. Defaults to 1.0.
    rel_eps_imag : float
        The imaginary part of the relative permittivity. Defaults to 0.0.
    rel_mu_real : float
        The real part of the relative permeability. Defaults to 1.0.
    rel_mu_imag : float
        The imaginary part of the relative permeability. Defaults to 0.0.
    conductivity : float
        The conductivity of the material. Defaults to 0.0.
    height_standard_dev : float
        The standard deviation of the height. Defaults to None.
    roughness : float
        The roughness of the material. Defaults to None.
    backing : str
        The backing of the material. Defaults to None.
    coating_idx : int
        The index of the coating. Defaults to 1.
    """

    thickness: float = -1.0
    rel_eps_real: float = 1.0
    rel_eps_imag: float = 0.0
    rel_mu_real: float = 1.0
    rel_mu_imag: float = 0.0
    conductivity: float = 0.0
    height_standard_dev: float or None = None
    roughness: float or None = None
    backing: str or None = None
    coating_idx: int = 1

    @classmethod
    def from_dict(cls, data):
        """
        A class method that creates a MaterialProperties instance from a dictionary.

        Parameters
        ----------
        data : dict
            The dictionary containing the material data.

        Returns
        -------
        MaterialProperties
            The created MaterialProperties instance.

        Examples
        --------
        >>> from ansys.aedt.core.generic.file_utils import read_json
        >>> from ansys.aedt.core.perceive_em.modules.material_properties import MaterialProperties
        >>> material_dict = read_json("material_lib.json")
        >>> mat_props = MaterialProperties.from_dict(material_dict)
        """
        return cls(
            thickness=data.get("thickness", -1.0),
            rel_eps_real=data.get("relEpsReal", 1.0),
            rel_eps_imag=data.get("relEpsImag", 0.0),
            rel_mu_real=data.get("relMuReal", 1.0),
            rel_mu_imag=data.get("relMuImag", 0.0),
            conductivity=data.get("conductivity", 0.0),
            height_standard_dev=data.get("height_standard_dev", None),
            roughness=data.get("roughness", None),
            backing=data.get("backing", None),
            coating_idx=data.get("coating_idx", 1),
        )

    def to_dict(self) -> dict:
        """
        Convert object to a dictionary.

        Returns
        -------
        dict
            Dictionary containing the material properties.
        """
        return {
            "thickness": self.thickness,
            "relEpsReal": self.rel_eps_real,
            "relEpsImag": self.rel_eps_imag,
            "relMuReal": self.rel_mu_real,
            "relMuImag": self.rel_mu_imag,
            "conductivity": self.conductivity,
            "height_standard_dev": self.height_standard_dev,
            "roughness": self.roughness,
            "backing": self.backing,
            "coating_idx": self.coating_idx,
        }
