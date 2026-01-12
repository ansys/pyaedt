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

import copy


def extract_boundary_data(data):
    boundary_data = []
    object_mapping = data.get("general", {}).get("object_mapping", {})
    read_only_cols = []
    selection_dict = {}
    headings = ["Boundary Name", "Boundary Type", "Selected Objects", "BC Name 1", "Value 1", "BC Name 2", "Value 2"]
    type_list = ["text", "text", "multiple_text", "text", "text", "text", "text"]

    # Convert mapping to ensure all values are names (some are lists)
    id_to_name = {}
    for obj_id, value in object_mapping.items():
        if isinstance(value, list):  # Some entries have extra data in a list
            id_to_name[obj_id] = value[0]  # Extract the name
        else:
            id_to_name[obj_id] = value  # Direct mapping

    all_objects = [obj_name for obj_name, obj_details in data.get("objects", {}).items()]
    selection_dict["Selected Objects"] = all_objects

    for boundary_name, boundary_details in data.get("boundaries", {}).items():
        cols = [1, 2, 4, 6]
        boundary_type = boundary_details.get("BoundType", "")
        if boundary_type == "Block":
            use_total_power = boundary_details.get("Use Total Power", "")
            use_external_conditions = boundary_details.get("Use External Conditions", "")
            if use_total_power:
                bc_name1 = "Total Power"
                bc_name2 = "N/A"
                value2 = "0.0"
                value1 = boundary_details.get("Total Power", "0W")  # Default to "0W" if missing
                object_ids = boundary_details.get("Objects", [])  # Default to empty list if missing
                selected_objects = [id_to_name[str(obj_id)] for obj_id in object_ids]
                boundary_data.append(
                    [boundary_name, boundary_type, selected_objects, bc_name1, value1, bc_name2, value2]
                )
                cols.append(7)
                read_only_cols.append(cols)
            elif use_external_conditions:
                bc_name1 = "Heat Transfer Coefficient"
                bc_name2 = "Temperature"
                value1 = boundary_details.get("Heat Transfer Coefficient", "0w_per_m2k")
                value2 = boundary_details.get("Temperature", "0cel")
                object_ids = boundary_details.get("Objects", [])  # Default to empty list if missing
                selected_objects = [id_to_name[str(obj_id)] for obj_id in object_ids]
                boundary_data.append(
                    [boundary_name, boundary_type, selected_objects, bc_name1, value1, bc_name2, value2]
                )
                read_only_cols.append(cols)
            else:
                bc_name1 = "Power Density"
                bc_name2 = "N/A"
                value2 = "0.0"
                value1 = boundary_details.get("Power Density", "0w_per_m3")
                object_ids = boundary_details.get("Objects", [])  # Default to empty list if missing
                selected_objects = [id_to_name[str(obj_id)] for obj_id in object_ids]
                boundary_data.append(
                    [boundary_name, boundary_type, selected_objects, bc_name1, value1, bc_name2, value2]
                )
                cols.append(7)
                read_only_cols.append(cols)

        if boundary_type == "Source":
            thermal_condition = boundary_details.get("Thermal Condition", "")
            if thermal_condition == "Surface Flux":
                bc_name1 = "Surface Heat"
                bc_name2 = "N/A"
                value1 = boundary_details.get("Surface Heat", "0kW_per_m2")
                value2 = "0.0"
                object_ids = boundary_details.get("Faces", [])  # Default to empty list if missing
                selected_objects = [str(ids) for ids in object_ids]
                boundary_data.append(
                    [boundary_name, boundary_type, selected_objects, bc_name1, value1, bc_name2, value2]
                )
                cols.append(3)
                cols.append(7)
                read_only_cols.append(cols)
            if thermal_condition == "Total Power":
                bc_name1 = "Total Power"
                bc_name2 = "N/A"
                value1 = boundary_details.get("Total Power", "0W")
                value2 = "0.0"
                object_ids = boundary_details.get("Faces", [])  # Default to empty list if missing
                selected_objects = [str(ids) for ids in object_ids]
                boundary_data.append(
                    [boundary_name, boundary_type, selected_objects, bc_name1, value1, bc_name2, value2]
                )
                cols.append(3)
                cols.append(7)
                read_only_cols.append(cols)
            if thermal_condition == "Fixed Temperature":
                bc_name1 = "Fixed Temperature"
                bc_name2 = "N/A"
                value1 = boundary_details.get("Temperature", "0cel")
                value2 = "0.0"
                object_ids = boundary_details.get("Faces", [])  # Default to empty list if missing
                selected_objects = [str(ids) for ids in object_ids]
                boundary_data.append(
                    [boundary_name, boundary_type, selected_objects, bc_name1, value1, bc_name2, value2]
                )
                cols.append(3)
                cols.append(7)
                read_only_cols.append(cols)
    return headings, type_list, selection_dict, boundary_data, read_only_cols


def extract_model_data(data):
    object_data = []
    bulk_materials = set()
    surface_materials = set()
    headings = ["Object Name", "Bulk Material", "Surface Material", "Solve Inside", "Modeling"]
    type_list = ["text", "combo", "combo", "combo", "combo"]
    selection_dict = {"Solve Inside": ["True", "False"], "Modeling": ["Model", "Non-Model"]}
    read_only_cols = []

    for obj_name, obj_details in data.get("objects", {}).items():
        cols = [1]
        component_name = obj_name
        bulk_material = obj_details.get("Material", "")
        surface_material = obj_details.get("SurfaceMaterial", "")
        solve = obj_details.get("SolveInside", "")
        if solve:
            solve_inside = "True"
        else:
            solve_inside = "False"

        model = obj_details.get("Model", "")

        if model:
            modelling = "Model"
        else:
            modelling = "Non-Model"

        if bulk_material == '""' or bulk_material == "":
            bulk_material = "Not Specified"
            bulk_materials.add(bulk_material)
        else:
            bulk_materials.add(bulk_material)

        if surface_material == '""':
            surface_material = surface_material.strip('"')
            data["objects"][obj_name]["SurfaceMaterial"] = surface_material
            surface_material = "Not Specified"
            surface_materials.add(surface_material)
        elif surface_material == "":
            surface_material = "Not Specified"
            surface_materials.add(surface_material)
        elif surface_material is None:
            surface_material = "Not Specified"
            surface_materials.add(surface_material)
        else:
            surface_material = surface_material.strip('"')
            data["objects"][obj_name]["SurfaceMaterial"] = surface_material  # removing "" in the source
            surface_materials.add(surface_material)

        object_data.append([component_name, bulk_material, surface_material, solve_inside, modelling])
        read_only_cols.append(cols)
    selection_dict["Bulk Material"] = list(bulk_materials)
    selection_dict["Surface Material"] = list(surface_materials)
    return headings, type_list, selection_dict, object_data, read_only_cols


def extract_material_data(data):
    materials = data.get("materials", {})
    extracted_data = []
    read_only_cols = []
    headings = [
        "Material Name",
        "Material Type",
        "Thermal Conductivity",
        "Mass Density",
        "Specific Heat",
        "Thermal Expansion Coefficient",
        "Diffusivity",
        "Viscosity",
    ]
    type_list = ["text", "text", "text", "text", "text", "text", "text", "text"]
    selection_dict = {}

    for mat_name, mat_details in materials.items():
        cols = [1]
        material_type = mat_details.get("thermal_material_type", {}).get("Choice", "N/A")
        # make material type read only
        cols.append(2)
        if material_type == "Solid" or material_type == "N/A":
            cols.append(8)
        thermal_conductivity = mat_details.get("thermal_conductivity", "N/A")
        # Handle anisotropic thermal conductivity case
        if isinstance(thermal_conductivity, dict):
            thermal_conductivity = thermal_conductivity["property_type"]
            cols.append(3)
        mass_density = mat_details.get("mass_density", "N/A")
        specific_heat = mat_details.get("specific_heat", "N/A")
        thermal_expansion_coefficient = mat_details.get("thermal_expansion_coefficient", "N/A")

        diffusivity = mat_details.get("diffusivity", "N/A")
        viscosity = mat_details.get("viscosity", "N/A")

        extracted_data.append(
            [
                mat_name,
                material_type,
                thermal_conductivity,
                mass_density,
                specific_heat,
                thermal_expansion_coefficient,
                diffusivity,
                viscosity,
            ]
        )
        read_only_cols.append(cols)
    return headings, type_list, selection_dict, extracted_data, read_only_cols


def compare_and_update_boundary_data(original_data, modified_object_data, object_mapping):
    """
    Compares modified object data with the original data and identifies differences.
    Also returns the updated original data with the modifications applied.
    """
    # updated_data = copy.deepcopy(original_data)  # Make a copy to avoid modifying original
    differences = []
    inverse_mapping = {str(v): k for k, v in object_mapping.items()}

    updated_data = {"boundaries": {}, "general": {}}
    updated_data["general"]["object_mapping"] = {**original_data["general"]["object_mapping"], **inverse_mapping}
    modified_boundary = set()
    for row in modified_object_data:
        (boundary_name, boundary_type, selected_objects, bc_name1, value1, bc_name2, value2) = row

        original_obj = original_data["boundaries"][boundary_name]
        updated_data["boundaries"][boundary_name] = copy.deepcopy(original_data["boundaries"][boundary_name])

        # Convert string values back to boolean where necessary

        # Check for differences and update
        if isinstance(selected_objects, list):
            selected_object_ids = [int(i) if str(i).isdigit() else object_mapping[i] for i in selected_objects]

        if isinstance(selected_objects, str):
            selected_object_ids = [
                int(i.strip()) if str(i.strip()).isdigit() else object_mapping[i.strip()]
                for i in selected_objects.split(",")
            ]

        original_obj_ids = original_obj.get("Objects", [])
        if original_obj_ids:
            if set(original_obj_ids) != set(selected_object_ids):
                differences.append(f"{boundary_name}: {bc_name1} selected objects changed  to '{selected_objects}'")
                updated_data["boundaries"][boundary_name]["Objects"] = selected_object_ids
                modified_boundary.add(boundary_name)

        if original_obj.get(bc_name1, "") != value1:
            differences.append(
                f"{boundary_name}: {bc_name1} changed from '{original_obj.get(bc_name1, '')}' to '{value1}'"
            )
            updated_data["boundaries"][boundary_name][bc_name1] = value1
            modified_boundary.add(boundary_name)

        if bc_name2 != "N/A":
            if original_obj.get(bc_name2, "") != value2:
                differences.append(
                    f"{boundary_name}: {bc_name1} changed from '{original_obj.get(bc_name1, '')}' to '{value1}'"
                )
            updated_data["boundaries"][boundary_name][bc_name2] = value2
            modified_boundary.add(boundary_name)

    modified_data = {"boundaries": {}, "general": {}}
    modified_data["general"]["object_mapping"] = {**original_data["general"]["object_mapping"], **inverse_mapping}
    for boundary_name in modified_boundary:
        modified_data["boundaries"][boundary_name] = copy.deepcopy(updated_data["boundaries"][boundary_name])

    return differences, modified_data


def compare_and_update_model_data(original_data, modified_object_data):
    """
    Compares modified object data with the original data and identifies differences.
    Also returns the updated original data with the modifications applied.
    """
    updated_data = {"objects": {}}
    differences = []
    modified_objects = set()

    for row in modified_object_data:
        obj_name, bulk_material, surface_material, solve_inside, modelling = row

        original_obj = original_data["objects"][obj_name]
        updated_data["objects"][obj_name] = copy.deepcopy(original_data["objects"][obj_name])

        # Convert string values back to boolean where necessary
        solve_inside_bool = solve_inside == "True"
        modelling_bool = modelling == "Model"

        # Check for differences and update
        if not bulk_material == "Not Specified":
            if original_obj.get("Material", "") != bulk_material:
                differences.append(
                    f"{obj_name}: Bulk Material changed from '{original_obj.get('Material', '')}' to '{bulk_material}'"
                )
                updated_data["objects"][obj_name]["Material"] = bulk_material
                modified_objects.add(obj_name)

        if not surface_material == "Not Specified":
            if original_obj.get("SurfaceMaterial", "") != surface_material:
                differences.append(
                    f"""{obj_name}: Surface Material changed from '{original_obj.get("SurfaceMaterial", "")}' to
                    '{surface_material}'"""
                )
                updated_data["objects"][obj_name]["SurfaceMaterial"] = surface_material
                modified_objects.add(obj_name)

        if original_obj.get("SolveInside", "") != solve_inside_bool:
            differences.append(
                f"""{obj_name}: Solve Inside changed from '{original_obj.get("SolveInside", "")}'
                to '{solve_inside_bool}'"""
            )
            updated_data["objects"][obj_name]["SolveInside"] = str(solve_inside_bool)
            modified_objects.add(obj_name)

        if original_obj.get("Model", "") != modelling_bool:
            differences.append(
                f"{obj_name}: Modeling changed from '{original_obj.get('Model', '')}' to '{modelling_bool}'"
            )
            updated_data["objects"][obj_name]["Model"] = str(modelling_bool)
            updated_data["objects"][obj_name]["SurfaceMaterial"] = None
            modified_objects.add(obj_name)

    modified_data = {"objects": {}}
    for obj_name in modified_objects:
        modified_data["objects"][obj_name] = copy.deepcopy(updated_data["objects"][obj_name])

    return differences, modified_data


def compare_and_update_material_data(original_data, modified_object_data):
    """
    Compares modified object data with the original data and identifies differences.
    Also returns the updated original data with the modifications applied.
    """
    differences = []
    updated_data = {"materials": {}}

    modified_materials = set()
    for row in modified_object_data:
        (
            mat_name,
            material_type,
            thermal_conductivity,
            mass_density,
            specific_heat,
            thermal_expansion_coefficient,
            diffusivity,
            viscosity,
        ) = row

        original_obj = original_data["materials"][mat_name]
        updated_data["materials"][mat_name] = copy.deepcopy(original_data["materials"][mat_name])

        # Check for differences and update
        if not isinstance(original_obj.get("thermal_conductivity"), dict):
            if original_obj.get("thermal_conductivity", "") != thermal_conductivity:
                differences.append(
                    f"""{mat_name}: Thermal Conductivity changed from '{original_obj.get("thermal_conductivity", "")}'
                     to '{thermal_conductivity}'"""
                )
                updated_data["materials"][mat_name]["thermal_conductivity"] = thermal_conductivity
                modified_materials.add(mat_name)

        if original_obj.get("mass_density", "") != mass_density:
            differences.append(
                f"{mat_name}: Mass density changed from '{original_obj.get('mass_density', '')}' to '{mass_density}'"
            )
            updated_data["materials"][mat_name]["mass_density"] = mass_density
            modified_materials.add(mat_name)

        if original_obj.get("specific_heat", "") != specific_heat:
            differences.append(
                f"{mat_name}: specific heat changed from '{original_obj.get('specific_heat', '')}' to '{specific_heat}'"
            )
            updated_data["materials"][mat_name]["specific_heat"] = specific_heat
            modified_materials.add(mat_name)

        if original_obj.get("thermal_expansion_coefficient", "") != thermal_expansion_coefficient:
            differences.append(
                f"{mat_name}: Thermal expansion coefficient changed "
                f"from '{original_obj.get('thermal_expansion_coefficient', '')}' to '{thermal_expansion_coefficient}'"
            )
            updated_data["materials"][mat_name]["thermal_expansion_coefficient"] = thermal_expansion_coefficient
            modified_materials.add(mat_name)

        if original_obj.get("diffusivity", "") != diffusivity:
            differences.append(
                f"{mat_name}: diffusivity changed from '{original_obj.get('diffusivity', '')}' to '{diffusivity}'"
            )
            updated_data["materials"][mat_name]["diffusivity"] = diffusivity
            modified_materials.add(mat_name)

        if original_obj.get("viscosity", "") != viscosity:
            differences.append(
                f"{mat_name}: viscosity changed from '{original_obj.get('diffusivity', '')}' to '{diffusivity}'"
            )
            updated_data["materials"][mat_name]["viscosity"] = viscosity
            modified_materials.add(mat_name)

    modified_data = {"materials": {}}
    for mat_name in modified_materials:
        modified_data["materials"][mat_name] = copy.deepcopy(updated_data["materials"][mat_name])
    return differences, modified_data
