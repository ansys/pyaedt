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

"""
This module contains the ``MaterialWorkbench`` class.

It includes a method to import materials from a Workbench Engineering Data XML file.
"""

from collections import defaultdict
import copy
import re

import defusedxml
from defusedxml.ElementTree import ParseError

from ansys.aedt.core.aedt_logger import pyaedt_logger as logger
from ansys.aedt.core.base import PyAedtBase
from ansys.aedt.core.generic.data_handlers import normalize_string_format
from ansys.aedt.core.modules.material import MatProperties

defusedxml.defuse_stdlib()


class MaterialWorkbench(PyAedtBase):
    """Manages the import of materials from a Workbench Engineering Data XML file.

    Parameters
    ----------
    app : :class:`ansys.aedt.core`
        Inherited parent object.
    """

    def __init__(self, app):
        self._app = app
        self._mat_name_suffix = "_wb"

    @property
    def mat_name_suffix(self):
        return self._mat_name_suffix

    @mat_name_suffix.setter
    def mat_name_suffix(self, suffix):
        self._mat_name_suffix = str(suffix)

    @staticmethod
    def _etree_to_dict(t):
        """Recursively convert an ElementTree element into a dictionary."""
        d = {t.tag: {} if t.attrib else None}
        children = list(t)
        if children:
            dd = defaultdict(list)
            for dc in map(MaterialWorkbench._etree_to_dict, children):
                for k, v in dc.items():
                    dd[k].append(v)
            d = {t.tag: {k: v[0] if len(v) == 1 else v for k, v in dd.items()}}
        if t.attrib:
            d[t.tag].update(("@" + k, v) for k, v in t.attrib.items())
        if t.text:
            text = t.text.strip()
            if children or t.attrib:
                if text:
                    d[t.tag]["#text"] = text
            else:
                d[t.tag] = text
        return d

    @staticmethod
    def _parse_xml(file_path):
        """Parse an XML file and convert it into a dictionary."""
        # Load the XML file
        try:
            tree = defusedxml.ElementTree.parse(file_path)
        except ParseError:  # pragma: no cover
            logger.error(f"Unable to parse {file_path}.")
            return

        root = tree.getroot()
        return MaterialWorkbench._etree_to_dict(root)

    @staticmethod
    def _to_float(string):
        try:
            return float(string)
        except ValueError:
            return string

    @staticmethod
    def _is_tabular_data(string):
        pattern = r"^([+-]?(\d+(\.\d*)?|\.\d+)([eE][+-]?\d+)?)(,([+-]?(\d+(\.\d*)?|\.\d+)([eE][+-]?\d+)?))*$"
        if re.match(pattern, string):
            return True
        else:
            return False

    def _dataset_name(self, material_name, property_name):
        name = f"TM_{self._aedt_material_name(material_name)}_{MatProperties.wb_to_aedt_name(property_name)}"
        return name

    def _aedt_material_name(self, wb_material_name):
        return f"{normalize_string_format(wb_material_name)}{self.mat_name_suffix}"

    def import_materials_from_workbench(self, filename):
        """Import materials from Workbench Engineering Data XML file.

        Parameters
        ----------
        filename : str
            Full path of the XML file. It must be in the format of the Workbench Engineering Data.

        Returns
        -------
        list
            List of imported materials.

        """
        # Parse the XML
        xml_dict = MaterialWorkbench._parse_xml(filename)

        # creating the materials dict holding all info in a more readable way
        parameters = {}
        for p in xml_dict["EngineeringData"]["Materials"]["MatML_Doc"]["Metadata"]["ParameterDetails"]:
            parameters[p["@id"]] = p["Name"]

        properties = {}
        for p in xml_dict["EngineeringData"]["Materials"]["MatML_Doc"]["Metadata"]["PropertyDetails"]:
            properties[p["@id"]] = p["Name"]

        materials = {}
        for m in xml_dict["EngineeringData"]["Materials"]["MatML_Doc"]["Material"]:
            mat = m["BulkDetails"]
            materials[mat["Name"]] = {}
            material = materials[mat["Name"]]
            if "Description" in mat:
                # material["Description"] = mat["Description"]
                pass
            for p in mat["PropertyData"]:
                prop = properties[p["@property"]]
                if "ParameterValue" in p and isinstance(p["ParameterValue"], list):
                    material[prop] = []
                    for v in p["ParameterValue"]:
                        material[prop].append(
                            {"parameter": parameters[v["@parameter"]], "data": MaterialWorkbench._to_float(v["Data"])}
                        )
                elif "ParameterValue" in p:
                    material[prop] = {
                        "parameter": parameters[p["ParameterValue"]["@parameter"]],
                        "data": MaterialWorkbench._to_float(p["ParameterValue"]["Data"]),
                    }

        # If data is not a number, but a string, check if it is tabular data. If not, it will be removed.
        for mat_name in materials:
            for prop_name, prop_data in materials[mat_name].items():
                if isinstance(prop_data, list):
                    for i, p in enumerate(prop_data[:]):
                        if isinstance(p["data"], str) and not MaterialWorkbench._is_tabular_data(p["data"]):
                            # remove the entry
                            del prop_data[i]

        # Check for thermal modifiers and rewrite them in a more usable format.
        # Also check for anisotropic material and rewrite them in a more usable format.
        for mat_name in materials:
            for prop_name, prop_data in materials[mat_name].items():
                # check for tabular data
                if isinstance(prop_data, list):
                    if (
                        len(prop_data) == 2
                        and all([isinstance(i["data"], str) for i in prop_data])
                        and any([i["parameter"] == "Temperature" for i in prop_data])
                        and all([MaterialWorkbench._is_tabular_data(i["data"]) for i in prop_data])
                    ):
                        # thermal modifier is found, reconstruct the property
                        parameter_name = None
                        data_array = None
                        temp_array = None
                        for p in prop_data:
                            if p["parameter"] == "Temperature":
                                temp_array = [float(i) for i in p["data"].split(",")]
                            elif p["parameter"] != "Temperature":
                                data_array = [float(i) for i in p["data"].split(",")]
                                parameter_name = p["parameter"]
                        materials[mat_name][prop_name] = {
                            "parameter": parameter_name,
                            "data": data_array[0],
                            "dataset": [data_array, temp_array],
                        }
                    if (
                        (len(prop_data) == 3 or len(prop_data) == 4)
                        and any([i["parameter"] == f"{prop_name} X direction" for i in prop_data])
                        and any([i["parameter"] == f"{prop_name} Y direction" for i in prop_data])
                        and any([i["parameter"] == f"{prop_name} Z direction" for i in prop_data])
                        and all([isinstance(i["data"], float) for i in prop_data])
                    ):
                        # Anisotropic material founded
                        anisotropic_data = [
                            [i["data"] for i in prop_data if i["parameter"] == f"{prop_name} X direction"][0],
                            [i["data"] for i in prop_data if i["parameter"] == f"{prop_name} Y direction"][0],
                            [i["data"] for i in prop_data if i["parameter"] == f"{prop_name} Z direction"][0],
                        ]
                        materials[mat_name][prop_name] = {
                            "parameter": prop_name,
                            "data": None,
                            "anisotropic": anisotropic_data,
                        }

        # Expand the Elasticity property into the individual properties
        materials2 = copy.deepcopy(materials)
        for mat_name in materials2:
            for prop_name, prop_data in materials2[mat_name].items():
                if isinstance(prop_data, list):
                    if prop_name == "Elasticity":
                        if (
                            all([isinstance(i["data"], str) for i in prop_data])
                            and any([i["parameter"] == "Temperature" for i in prop_data])
                            and all([MaterialWorkbench._is_tabular_data(i["data"]) for i in prop_data])
                        ):
                            for p in prop_data:
                                if p["parameter"] == "Temperature":
                                    temp_array = [float(i) for i in p["data"].split(",")]
                            for p in prop_data:
                                if p["parameter"] != "Temperature":
                                    data_array = [float(i) for i in p["data"].split(",")]
                                    parameter_name = p["parameter"]
                                    materials[mat_name][parameter_name] = {
                                        "parameter": parameter_name,
                                        "data": data_array[0],
                                        "dataset": [data_array, temp_array],
                                    }
                        else:
                            for p in prop_data:
                                materials[mat_name][p["parameter"]] = {"parameter": p["parameter"], "data": p["data"]}
                        del materials[mat_name]["Elasticity"]

        # Performs other simplifications to the properties
        materials2 = copy.deepcopy(materials)
        for mat_name in materials2:
            for prop_name, prop_data in materials2[mat_name].items():
                if isinstance(prop_data, list):
                    # Properties with a single element list are saved without the list
                    if len(prop_data) == 1:
                        materials[mat_name][prop_name] = {
                            "parameter": prop_data[0]["parameter"],
                            "data": prop_data[0]["data"],
                        }
                    # Properties with a table specified but with a single raw (a single temperature entry) are converted
                    if (
                        len(prop_data) == 2
                        and any([i["parameter"] == "Temperature" for i in prop_data])
                        and not all(isinstance(i["data"], list) for i in prop_data)
                    ):
                        prop = [i for i in prop_data if i["parameter"] != "Temperature"][0]
                        materials[mat_name][prop_name] = {"parameter": prop["parameter"], "data": prop["data"]}
                    if prop_name == "Color":
                        r = [i["data"] for i in prop_data if i["parameter"] == "Red"]
                        g = [i["data"] for i in prop_data if i["parameter"] == "Green"]
                        b = [i["data"] for i in prop_data if i["parameter"] == "Blue"]
                        if r and g and b:
                            materials[mat_name][prop_name] = {
                                "parameter": "Color",
                                "data": [int(r[0]), int(g[0]), int(b[0])],
                            }
                        else:
                            del materials[mat_name]["Color"]

        # material props creation in AEDT format and also other auxiliary dictionaries (thermal_modifier and colors)
        mat_props = {}
        thermal_modifiers = {}
        colors = {}
        for m_name, m_props in materials.items():
            mat_props[m_name] = {}
            thermal_modifiers[m_name] = {}
            props = mat_props[m_name]

            for wb_prop_name in MatProperties.workbench_name:
                if wb_prop_name is None:
                    continue
                aedt_prop_name = MatProperties.wb_to_aedt_name(wb_prop_name)
                if wb_prop_name in m_props:
                    if "anisotropic" in m_props[wb_prop_name]:
                        props[aedt_prop_name] = {
                            "property_type": "AnisoProperty",
                            "unit": "",
                            "component1": m_props[wb_prop_name]["anisotropic"][0],
                            "component2": m_props[wb_prop_name]["anisotropic"][1],
                            "component3": m_props[wb_prop_name]["anisotropic"][2],
                        }
                    else:
                        props[aedt_prop_name] = m_props[wb_prop_name]["data"]

            if "Resistivity" in m_props and "Electrical Conductivity" not in m_props:
                if "anisotropic" in m_props["Resistivity"]:
                    props["conductivity"] = {
                        "property_type": "AnisoProperty",
                        "unit": "",
                        "component1": 1 / m_props["Resistivity"]["anisotropic"][0],
                        "component2": 1 / m_props["Resistivity"]["anisotropic"][1],
                        "component3": 1 / m_props["Resistivity"]["anisotropic"][2],
                    }
                else:
                    props["conductivity"] = 1 / m_props["Resistivity"]["data"]
            if "Color" in m_props:
                colors[m_name] = m_props["Color"]["data"]
                colors[m_name].append(0.0)  # transparency information required by AEDT
            for p_name, p in m_props.items():
                if p_name in MatProperties.workbench_name and "dataset" in p:
                    thermal_modifiers[m_name][MatProperties.wb_to_aedt_name(p_name)] = {
                        "dataset": p["dataset"],
                        "dataset_name": self._dataset_name(m_name, p_name),
                    }

        # Creating the material in Hfss
        imported_materials = []
        for material_name, props in mat_props.items():
            mat = self._app.materials.add_material(self._aedt_material_name(material_name), props)
            if not mat:
                continue  # if the material is not created continues with the next one
            imported_materials.append(mat)
            if thermal_modifiers[material_name]:
                for prop, data in thermal_modifiers[material_name].items():
                    self._app.create_dataset(name=data["dataset_name"], x=data["dataset"][0], y=data["dataset"][1])
                    x = getattr(mat, prop)
                    x.add_thermal_modifier_dataset(f"${data['dataset_name']}")
            if material_name in colors:
                mat.material_appearance = colors[material_name]
        return imported_materials
