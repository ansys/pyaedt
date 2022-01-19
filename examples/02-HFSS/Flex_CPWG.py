"""
Flex Coplanar Waveguid Example
------------------------------
This example shows how you can use PyAEDT to create a flex cable coplanar waveguide.
"""
from math import radians, sin, cos, pi, sqrt
from pyaedt import Hfss

hfss = Hfss(specified_version='2021.2', solution_type="DrivenTerminal")
hfss.change_material_override(True)
hfss.change_automatically_use_causal_materials(True)
hfss.create_open_region('100GHz')
hfss.modeler.model_units = 'mil'
hfss.mesh.assign_initial_mesh_from_slider(applycurvilinear=True)

setup = hfss.create_setup('setup1')
setup.props['Frequency'] = '2GHz'
setup.props['MaximumPasses'] = 10
setup.props['MinimumConvergedPasses'] = 2
setup.update()

total_length = 300
theta = 120
r = 100
width = 3
height = 0.1
spacing = 1.53
gnd_width = 10
gnd_thickness = 2

xt = (total_length - r * radians(theta)) / 2


def create_bending(radius, extension=0):
    position_list = [(-xt, 0, -radius), (0, 0, -radius)]

    for i in [radians(i) for i in range(theta)] + [radians(theta + 0.000000001)]:
        position_list.append((radius * sin(i), 0, -radius * cos(i)))

    x1, y1, z1 = position_list[-1]
    x0, y0, z0 = position_list[-2]

    scale = (xt + extension) / sqrt((x1 - x0) ** 2 + (z1 - z0) ** 2)
    x, y, z = (x1 - x0) * scale + x0, 0, (z1 - z0) * scale + z0

    position_list[-1] = (x, y, z)
    return position_list


# %% Draw Signal
position_list = create_bending(r, 1)
line = hfss.modeler.create_polyline(position_list=position_list,
                                    xsection_type='Rectangle',
                                    xsection_width=height,
                                    xsection_height=width,
                                    matname='copper')
line.color = (255, 0, 0)

# %% Draw Ground
gnd_r = [(x, spacing + width / 2 + gnd_width / 2, z) for x, y, z in position_list]
gnd_l = [(x, -y, z) for x, y, z in gnd_r]

gnd_objs = []
for gnd in [gnd_r, gnd_l]:
    x = hfss.modeler.create_polyline(position_list=gnd,
                                     xsection_type='Rectangle',
                                     xsection_width=height,
                                     xsection_height=gnd_width,
                                     matname='copper')
    x.color = (255, 0, 0)
    gnd_objs.append(x)

# %% Create FR4
position_list = create_bending(r + (height + gnd_thickness) / 2)

fr4 = hfss.modeler.create_polyline(position_list=position_list,
                                   xsection_type='Rectangle',
                                   xsection_width=gnd_thickness,
                                   xsection_height=width + 2 * spacing + 2 * gnd_width,
                                   matname='FR4_epoxy')

fr4.color = (0, 255, 0)

# %% bottome metal
position_list = create_bending(r + height + gnd_thickness, 1)

bot = hfss.modeler.create_polyline(position_list=position_list,
                                   xsection_type='Rectangle',
                                   xsection_width=height,
                                   xsection_height=width + 2 * spacing + 2 * gnd_width,
                                   matname='copper')

bot.color = (255, 0, 0)

# %%
port_faces = []
for face, blockname in zip(fr4.faces[-2:], ['b1', 'b2']):
    xc, yc, zc = face.center
    positions = [i.position for i in face.vertices]

    port_sheet_list = [((x - xc) * 10 + xc, (y - yc) + yc, (z - zc) * 10 + zc) for x, y, z in positions]
    s = hfss.modeler.create_polyline(port_sheet_list, close_surface=True, cover_surface=True)
    center = [round(i, 6) for i in s.faces[0].center]

    port_block = hfss.modeler.thicken_sheet(s.name, 5)
    port_block.name = blockname
    for f in port_block.faces:

        if [round(i, 6) for i in f.center] == center:
            port_faces.append(f)

    port_block.material_name = 'PEC'

    for i in [line, bot] + gnd_objs:
        i.subtract([port_block], True)

    print(port_faces)
# %%
boundary = []
for face in [fr4.top_face_y, fr4.bottom_face_y]:
    s = hfss.modeler.create_object_from_face(face)
    boundary.append(s)
    hfss.assign_perfecte_to_sheets(s)

# %%
for s, port_name in zip(port_faces, ["1", "2"]):
    reference = [i.name for i in gnd_objs + boundary + [bot]] + ['b1', 'b2']

    hfss.create_wave_port_from_sheet(s.id, portname=port_name, terminal_references=reference)

hfss.create_linear_count_sweep(setupname='setup1',
                               unit='GHz',
                               freqstart=1e-1,
                               freqstop=4,
                               num_of_freq_points=101,
                               sweepname='sweep1',
                               save_fields=False,
                               sweep_type='Interpolating')

# hfss.analyze_nominal(num_cores=4)