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

from pathlib import Path
import warnings

from ansys.aedt.core.internal.checks import ERROR_GRAPHICS_REQUIRED
from ansys.aedt.core.internal.checks import check_graphics_available
from ansys.aedt.core.internal.checks import graphics_required

# Check that graphics are available
try:
    check_graphics_available()

    import pyvista as pv

    from ansys.tools.visualization_interface import MeshObjectPlot
    from ansys.tools.visualization_interface import Plotter
    from ansys.tools.visualization_interface.backends.pyvista import PyVistaBackend
except ImportError:
    warnings.warn(ERROR_GRAPHICS_REQUIRED)


class MeshLoader:
    def __init__(self, app):
        # Private properties
        self.__rss = app.radar_sensor_scenario
        self.__api = app.api
        self.__material_manager = app.material_manager
        self.logger = app.logger

        # used to preserve previous settings when update_mesh is used. Not all features can be used right now,
        # for example, scaling and textures will not be preserved on a generator mesh update. That is because
        # we are assuming what is coming from the generator is the mesh and it does not need to be changed
        self.mesh_memory_mat_idx = 0
        self.mesh_memory_clip_at_bounds = None
        self.mesh_memory_center_geometry = False
        self.h_mesh = None

    def update_mesh(self, h_node=None, mesh=None, delete_old_scene_element=True):
        if delete_old_scene_element:
            if self.h_mesh is not None:
                try:
                    self.api.deleteSceneElement(self.h_mesh)
                except Exception:
                    print("INFO: Could not delete old scene element on update_mesh() for generator object")
        (h_mesh, _) = self.loadMesh(
            mesh=mesh,
            material=self.mesh_memory_mat_idx,
            clip_at_bounds=self.mesh_memory_clip_at_bounds,
            center_geometry=self.mesh_memory_center_geometry,
        )

        # this will update a node with a new scene element. I think using replace triangles will eventually be faster
        # but until 25R1 I will just use setSceneElement() which will replace the scene element on the node.
        # there might be some overhead if we don't delete previous scene_elements for large models with lots of updates
        api_core.isOK(self.api.setSceneElement(h_node, h_mesh))

    def load_mesh(self, input_file=None, mesh=None, material_index=0, use_curved_physics=False):
        h_mesh = None

        if input_file is not None:
            input_file = Path(input_file)
            if input_file.is_file():
                base_dir = input_file.parent
                filename_only = input_file.name
                ext = input_file.suffix

                # Load pyvista mesh which will be used for visualization
                mesh = pv.read(input_file)

                # helper function to load stl or obj file, but ultimately we just need triangles
                perceive_mesh = self.__api.loadTriangleMesh(str(input_file))
                triangles = perceive_mesh.triangles
                vertices = perceive_mesh.vertices

                # Coating be default will be 0 with this approach, increment to mat_idx
                perceive_mesh.coatings += material_index

                if vertices.shape[0] == 0:
                    self.logger.info(f"Mesh is empty: {input_file}")
                    return None, None

                h_mesh = self.__rss.SceneElement()
                self.__api.addSceneElement(h_mesh)

                if not use_curved_physics or perceive_mesh is None:
                    self.__api.setTriangles(h_mesh, vertices, triangles, material_index)
                    if use_curved_physics:
                        self.logger.warning(
                            "Using Curved Physics Failed, "
                            "check file type and support for surface normals (currently only obj and stl "
                            "supported)"
                        )
                else:
                    self.logger.info("Using curved physics")
                    # this is currently disabled, but we could enable it if we want to use the normals from cad
                    # file to include curvature extraction. cad file must have enormals
                    self.__api.setTriangles(h_mesh, perceive_mesh)
                    self.__api.setDoCurvedSurfPhysics(True)
                    mesh = mesh.compute_normals()
                    normals = mesh.active_normals
                    self.__api.setVertexNormals(h_mesh, self.__rss.VertexNormalFormat.BY_VERTEX_LIST, normals)
            else:
                raise FileNotFoundError(f"File not found: {input_file}")

        self.h_mesh = h_mesh

        return h_mesh, mesh

    def map_material_based_on_color_SUMS(self, mesh):
        # ToDo, using default material idx mappings. This should be updated to use the material names
        print("Mapping material based on default material_library.json. Please verify this is correct")

        # swap the below dictionary key and values to get the material names

        material_idx = {
            -1: "unlabelled",
            0: "unclassified",
            1: "terrain",
            2: "high_vegetation",
            3: "building",
            4: "water",
            5: "car",
            6: "boat",
        }

        # index values for pec, earth, veg, water, concrete aluminum...etc.
        material_map = {
            "unlabelled": 0,
            "unclassified": 0,
            "terrain": 4,
            "high_vegetation": 9,
            "building": 6,
            "water": 16,
            "car": 11,
            "boat": 0,
        }

        idx_mapping = {-1: 0, 0: 0, 1: 4, 2: 9, 3: 6, 4: 16, 5: 11, 6: 0}
        # load the material into the API
        for mat in idx_mapping.keys():
            self.material_manager.load_material(idx_mapping[mat])

        # map mesh.cell_data['material'] to new material index using idx_mapping. If the material index is not in the
        # idx_mapping, then it is unlabelled and will be assigned to 0
        mesh.cell_data["material"] = np.array(
            [idx_mapping.get(x, 0) for x in mesh.cell_data["material"]], dtype=np.int32
        )
        return mesh
        # return np.asarray(mesh.cell_data['material'], dtype=np.int32)

    def map_material_based_on_color(self, mesh, texture):
        texture = texture.to_array()
        # ToDo I am not sure if I have these backwards
        x_size = texture.shape[0]
        y_size = texture.shape[1]
        color_per_cell_idx = []

        print("Mapping material based on texture map... (slow)")
        for n in tqdm(range(mesh.n_cells)):
            cell = mesh.get_cell(n)
            pnt_ids = cell.point_ids
            colors_avg = []
            for pnt_id in pnt_ids:
                uv_coord = mesh.active_texture_coordinates[pnt_id]
                closest_idx_x = int(np.abs(uv_coord[0]) * x_size)
                closest_idx_y = int(np.abs(uv_coord[1]) * y_size)
                colors_avg.append(np.array(texture[closest_idx_y, closest_idx_x][:3]))  # only first three values
            rgb = self.average_rgb_colors(colors_avg)
            hsv = self.convert_rgb_to_hsb(rgb)
            # ToDo, assign meaningful index value. Right now just 1 for green, 0 for everything else
            if hsv[0] > 40 and hsv[0] < 160 and hsv[1] > 5 and hsv[1] < 250 and hsv[2] > 1 and hsv[2] < 250:  # green
                color_per_cell_idx.append(1)
            else:
                color_per_cell_idx.append(0)
            colors_avg = []
        return np.asarray(color_per_cell_idx, dtype=np.int32)

    def average_rgb_colors(self, rgb_list):
        r = 0
        b = 0
        g = 0
        num = len(rgb_list)
        rgb_list = np.array(rgb_list, dtype=float)
        for rgb in rgb_list:
            r += rgb[0] * rgb[0]
            g += rgb[1] * rgb[1]
            b += rgb[2] * rgb[2]
        rgb_avg = [int(np.sqrt(r / num)), int(np.sqrt(g / num)), int(np.sqrt(b / num))]
        return rgb_avg

    def convert_rgb_to_hsb(self, rgb):
        r, g, b = rgb
        r, g, b = r / 255.0, g / 255.0, b / 255.0
        mx = max(r, g, b)
        mn = min(r, g, b)
        df = mx - mn
        if mx == mn:
            h = 0
        elif mx == r:
            h = (60 * ((g - b) / df) + 360) % 360
        elif mx == g:
            h = (60 * ((b - r) / df) + 120) % 360
        elif mx == b:
            h = (60 * ((r - g) / df) + 240) % 360
        if mx == 0:
            s = 0
        else:
            s = (df / mx) * 100
        v = mx * 100
        return [h, s, v]

    def facet_to_stl(self, filename, outfile=None):
        base_dir = os.path.dirname(filename)
        filename_only = os.path.basename(filename)
        ext = os.path.splitext(filename_only)[1]

        if outfile is None:
            outfile = filename_only + ".stl"
            outfile = os.path.join(base_dir, outfile)

        # Read the FACET file
        with open(filename, "r") as f:
            lines = f.readlines()

        # Parse header information
        n_points = int(lines[4].strip())

        # Read points
        points = np.loadtxt(lines[5 : 5 + n_points])

        # Find the start of facets data
        facet_start = 5 + n_points + 3
        n_facets, n_sides = map(int, lines[facet_start - 1].strip().split())

        # Read facets
        facets = np.loadtxt(lines[facet_start:], dtype=int)[:, :3] - 1  # Subtract 1 to convert to 0-based indexing

        # Write STL file
        with open(outfile, "w") as f:
            f.write('solid "design<stl unit=M>"\n')

            for facet in facets:
                # Calculate normal (assuming counter-clockwise vertex order)
                v1 = points[facet[1]] - points[facet[0]]
                v2 = points[facet[2]] - points[facet[0]]
                normal = np.cross(v1, v2)
                normal = normal / np.linalg.norm(normal)

                f.write(f"  facet normal {normal[0]:.6f} {normal[1]:.6f} {normal[2]:.6f}\n")
                f.write("    outer loop\n")
                for vertex in facet:
                    point = points[vertex]
                    f.write(f"      vertex {point[0]:.6f} {point[1]:.6f} {point[2]:.6f}\n")
                f.write("    endloop\n")
                f.write("  endfacet\n")

            f.write("endsolid\n")

        # Load the STL file as a PyVista mesh to convert ascii to binary
        mesh = pv.read(outfile)
        mesh.save(outfile, binary=True)
        print(f"STL file '{outfile}' has been created successfully.")
        return outfile

    def ply_to_obj(self, filename, outfile=None):
        base_dir = os.path.dirname(filename)
        filename_only = os.path.basename(filename)
        ext = os.path.splitext(filename_only)[1]
        filename_only = os.path.splitext(filename_only)[0]

        if outfile is None:
            outfile = filename_only + ".obj"
            outfile = os.path.join(base_dir, outfile)

        # Load the STL file as a PyVista mesh to convert ascii to binary
        mesh = pv.read(filename)
        mesh.save(outfile, binary=True)
        print(f"OBJ file '{outfile}' has been created successfully.")
        return outfile

    def vtp_to_obj(self, filename, outfile=None):
        base_dir = os.path.dirname(filename)
        filename_only = os.path.basename(filename)
        ext = os.path.splitext(filename_only)[1]
        filename_only = os.path.splitext(filename_only)[0]

        if outfile is None:
            outfile = filename_only + ".obj"
            outfile = os.path.join(base_dir, outfile)

        # Load the STL file as a PyVista mesh to convert ascii to binary
        mesh = pv.read(filename)
        mesh.save(outfile, binary=True)
        print(f"OBJ file '{outfile}' has been created successfully.")
        return outfile
