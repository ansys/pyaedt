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

import copy
from pathlib import Path

import numpy as np

from ansys.aedt.core.generic.file_utils import read_json
from ansys.aedt.core.perceive_em import MISC_PATH
from ansys.aedt.core.perceive_em.core.general_methods import perceive_em_function_handler
from ansys.aedt.core.perceive_em.modules.material_properties import MaterialProperties


class MaterialManager:
    """
    Manages material definitions for a radar simulation scenario.

    This class loads, tracks, and manages electromagnetic material properties,
    including loading them into the simulation environment and assigning coating indices.

    Parameters
    ----------
    app : :class:`ansys.aedt.core.perceive_em.core.api_interface.APIInterface`
        Perceive EM object.
    material_library : str, :class:'pathlib.Path', or list, optional
        Path(s) to JSON file(s) containing material definitions. If not provided,
        the default material library is used.
    """

    def __init__(self, app, material_library=None):
        # Internal properties
        self._rss = app.radar_sensor_scenario
        self._api = app.api

        # Private properties
        self.__available_materials = {}
        self.__materials = {}

        # Public properties
        self._logger = app._logger

        all_materials_libraries = {}

        if material_library is not None:
            if isinstance(material_library, str) or isinstance(material_library, Path):
                material_library = [material_library]

                for mat_library in material_library:
                    material_library = Path(mat_library)
                    if not material_library.is_file():
                        raise FileNotFoundError(f"Material library {material_library} not found.")
                    materials_dict = read_json(mat_library)
                    if materials_dict is None or materials_dict.get("materials", None) is None:  # pragma: no cover
                        raise KeyError("Wrong library loaded. Materials are not available.")
                    all_materials_libraries.update(materials_dict["materials"])
            elif isinstance(material_library, dict):
                for mat_name, mat_library in material_library.items():
                    all_materials_libraries.update({mat_name: mat_library.to_dict()})
        else:
            mat_library = MISC_PATH / "default_material_library.json"
            materials_dict = read_json(mat_library)
            all_materials_libraries.update(materials_dict["materials"])

        # Assign coating indices
        for n, each in enumerate(all_materials_libraries):
            all_materials_libraries[each]["coating_idx"] = n + 1
        if "pec" in all_materials_libraries:
            all_materials_libraries["pec"]["coating_idx"] = 0

        for name, data in all_materials_libraries.items():
            self.__available_materials[name.lower()] = MaterialProperties.from_dict(data)

    @property
    def available_materials(self):
        """Available materials.

        Returns
        -------
        dict
           Dictionary of available materials keyed by name.
        """
        return self.__available_materials

    @property
    def available_material_names(self):
        """Available materials names.

        Returns
        -------
        list
           Names of all available materials.
        """
        return list(self.available_materials.keys())

    @property
    def available_material_names_by_coating_index(self):
        """Available materials by coating index.

        Returns
        -------
        dict
           Mapping from coating index to material name for available materials.
        """
        material_names_by_coating_idx = {
            material.coating_idx: name for name, material in self.available_materials.items()
        }
        return material_names_by_coating_idx

    @property
    def materials(self):
        """Added materials.

        Returns
        -------
        dict
           Dictionary of materials loaded into the simulation.
        """
        return self.__materials

    @property
    def material_names(self):
        """Added materials names.

        Returns
        -------
        list
           Names of materials loaded into the simulation.
        """
        return list(self.materials.keys())

    @property
    def material_names_by_coating_index(self):
        """Added materials by coating index.

        Returns
        -------
        dict
           Mapping from coating index to material name for loaded materials.
        """
        material_names_by_coating_idx = {material.coating_idx: name for name, material in self.materials.items()}
        return material_names_by_coating_idx

    def load_material(self, material: str) -> bool:
        """
        Load a material into the simulation scenario.

        Parameters
        ----------
        material : str
            The name of the material to load.

        Returns
        -------
        bool
            ``True`` if material was loaded successfully.

        Raises
        ------
        ValueError
            If the material is not found in the available materials.
        """
        material = material.lower()

        if material == "pec":
            self._logger.info("PEC is already added by default.")
            return True

        if material in self.available_materials:
            self._logger.warning("You are using PyAEDT materials, verify its properties using 'available materials'.")
            t = self.available_materials[material].thickness
            er_real = self.available_materials[material].rel_eps_real
            er_im = self.available_materials[material].rel_eps_imag
            mu_real = self.available_materials[material].rel_mu_real
            mu_imag = self.available_materials[material].rel_mu_imag
            cond = self.available_materials[material].conductivity
            mat_idx = self.available_materials[material].coating_idx
            material_is_rough = False
            height_standard_dev = self.available_materials[material].height_standard_dev
            roughness = self.available_materials[material].roughness

            if isinstance(t, list):
                material_str = "DielectricLayers " + " ".join(
                    f"{t[i]},{er_real[i]},{er_im[i]},{mu_real[i]},{mu_imag[i]},{cond[i]}" for i in range(len(t))
                )
            else:
                material_str = f"DielectricLayers {t},{er_real},{er_im},{mu_real},{mu_imag},{cond}"

            if material == "absorber":
                mat_idx = self.available_materials[material].coating_idx
                material_str = "Absorber"
            else:
                if self.available_materials[material].backing:
                    backing_mat = self.available_materials[material].backing
                    material_str = f"{material_str}  {backing_mat}"
                if roughness and height_standard_dev:
                    material_is_rough = True
                    roughness = self.available_materials[material].roughness
                    height_standard_dev = self.available_materials[material].height_standard_dev

            if mat_idx not in self.material_names_by_coating_index:
                material_name = self.available_material_names_by_coating_index[mat_idx]
                material_properties = self.available_materials[material_name]
                material_properties_copy = copy.deepcopy(material_properties)

                material_dict = {material_name: material_properties_copy}

                self.__materials.update(material_dict.copy())
                self.__materials[material_name].coating_idx = len(self.materials)

                self.add_coating(
                    material_name=material_str,
                    material_index=mat_idx,
                    is_rough=material_is_rough,
                    height_standard_dev=height_standard_dev,
                    roughness=roughness,
                )

            return True
        else:
            raise ValueError(f"{material} not found in the material library.")

    def add_material(
        self, name: str, properties: MaterialProperties, load: bool = True, overwrite: bool = False
    ) -> bool:
        """
        Add a new material to the available material library.

        Parameters
        ----------
        name : str
            Name of the material to add.
        properties : MaterialProperties
            The properties of the material.
        load : bool, optional
            Whether to immediately load the material into the scene. Default is True.
        overwrite : bool, optional
            Whether to overwrite an existing material with the same name. Default is False.

        Returns
        -------
        bool
            ``True`` if the material is added successfully.

        Examples
        --------
        >>> from ansys.aedt.core.perceive_em.core.api_interface import PerceiveEM
        >>> from ansys.aedt.core.perceive_em.modules.material_properties import MaterialProperties
        >>> default_material = MaterialProperties(thickness=1.0, rel_eps_real=2.5, rel_eps_imag=0.1)
        >>> perceive_em = PerceiveEM()
        >>> perceive_em.material_manager.add_material("my_mat", default_material)
        """
        name = name.lower()
        if name in self.available_materials and not overwrite:
            raise ValueError(f"{name} already exists in the material library.")

        if not isinstance(properties, MaterialProperties):
            raise TypeError("Properties must be a MaterialProperties object.")

        self.__available_materials[name] = properties
        # Set last coating index
        self.__available_materials[name].coating_idx = len(self.available_materials.keys())

        if load:
            self.load_material(name)

        return True

    def add_coating(
        self,
        material_name: str,
        material_index: int,
        is_rough: bool = False,
        height_standard_dev: float = None,
        roughness: float = None,
    ) -> bool:
        """
        Add a coating material and optionally define its roughness.

        This method creates a new coating, assigns it a material name and maps it
        to a specific material index. Optionally, it can apply surface roughness parameters.

        Parameters
        ----------
        material_name : str
            Name of the coating material.
        material_index : int
            Index of the material in the simulation environment.
        is_rough : bool, optional
            Whether the coating has roughness applied. The default is ``False``.
        height_standard_dev : float, optional
            Standard deviation of height for roughness modeling. Required if `is_rough` is ``True``.
        roughness : float, optional
            Roughness parameter of the coating. Required if `is_rough` is ``True``.

        Returns
        -------
        bool
            True if the coating is successfully created and configured.

        Examples
        --------
        >>> from ansys.aedt.core.perceive_em.core.api_interface import PerceiveEM
        >>> perceive_em = PerceiveEM()
        >>> perceive_em.material_manager.add_coating("Aluminum", 3)
        """
        h_mat = self._coating()
        self._add_coating(h_mat, material_name)
        self._map_coating_to_index(h_mat, material_index)
        if is_rough:
            self._set_coating_roughness(h_mat, height_standard_dev, roughness)
        return True

    # Internal Perceive EM API objects
    # Perceive EM API objects should be hidden to the final user, it makes more user-friendly API
    @perceive_em_function_handler
    def _coating(self):
        """
        Create a new coating object instance.

        Returns
        -------
        Coating
            A new coating handle from the radar sensor scenario API.
        """
        return self._rss.Coating()

    @perceive_em_function_handler
    def _add_coating(self, coating, material_name):
        """
        Add a coating to the simulation environment.

        Parameters
        ----------
        coating : Coating
            Coating object handle created from the API.
        material_name : str
            Name of the material to assign to the coating.
        """
        return self._api.addCoating(coating, material_name)

    @perceive_em_function_handler
    def _map_coating_to_index(self, coating, material_index):
        """
        Map a coating to a specific material index.

        Parameters
        ----------
        coating : Coating
            Coating object handle.
        material_index : int
            Index of the material to map the coating to.
        """
        return self._api.mapCoatingToIndex(coating, material_index)

    @perceive_em_function_handler
    def _set_coating_roughness(self, coating, height_standard_dev=None, roughness=None):
        """
        Set roughness parameters for a coating.

        Parameters
        ----------
        coating : Coating
            Coating object handle.
        height_standard_dev : float, optional
            Standard deviation of surface height.
        roughness : float, optional
            Roughness value to apply.
        """
        return self._api.setCoatingRoughness(coating, height_standard_dev, roughness)


def calculate_itu_properties(frequency: float) -> dict:
    """
    Calculate the ITU material properties for a given frequency based on data from a material library.

    Parameters
    ----------
    frequency : float
        The frequency in Hz at which to calculate the material properties.

    Returns
    -------
    dict
        Dictionary with MaterialProperties object with the ITU material properties.

    Example
    -------
    >>> from ansys.aedt.core.perceive_em.core.api_interface import PerceiveEM
    >>> from ansys.aedt.core.perceive_em.modules.material import calculate_itu_properties
    >>> from ansys.aedt.core.perceive_em.modules.material import MaterialManager
    >>> perceive_em = PerceiveEM()
    >>> properties = calculate_itu_properties(1000)
    >>> material_manager_new = MaterialManager(perceive_em, new_itu_library)

    """
    material_table = read_json(MISC_PATH / "material_itu_library.json")
    material_dict = {}

    # Iterate through table data to find the closest frequency value
    for n, entry in enumerate(material_table):
        a = material_table[entry]["a"]
        b = material_table[entry]["b"]
        c = material_table[entry]["c"]
        d = material_table[entry]["d"]
        er = a * np.power(frequency, b)
        sigma = c * np.power(frequency, d)
        er_imag = 17.98 * sigma / frequency * -1

        new_material = MaterialProperties()

        new_material.thickness = -1
        new_material.rel_eps_real = er
        new_material.rel_eps_imag = er_imag
        new_material.rel_mu_real = 1.0
        new_material.rel_mu_imag = 0.0
        new_material.conductivity = sigma
        new_material.coating_idx = n + 1

        material_dict[entry] = new_material

    return material_dict
