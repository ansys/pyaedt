from ansys.aedt.core import Hfss

hfss = Hfss(
    project="test_define_weave",
    design="WeaveTest",
    solution_type="DrivenModal",
    new_desktop=True,
    non_graphical=False,
    # set True for headless
)
hfss.modeler.model_units = "mm"

# Create a simple resin substrate box
if "resin336" not in hfss.materials.material_keys:
    r = hfss.materials.add_material("resin336")
    r.permittivity = 3.36
    r.dielectric_loss_tangent = 0.004

sub = hfss.modeler.create_box(
    origin=[0, 0, 0],
    sizes=[10, 4, 0.127],
    name="Substrate",
    material="resin336",
)


# yarn_names = hfss.modeler.define_weave(sub)

# Override one thing from the preset
yarn_names = hfss.modeler.define_weave(sub, weave_style="7628", weave_rotate_deg=0)

# Fully manual (existing behaviour, no change)
# hfss.modeler.define_weave(sub, bw_warp=0.25, target_pitch_x=0.6, ...))

# Basic checks
print("Yarns created:", yarn_names)
assert len(yarn_names) > 0, "No yarns were created!"
for name in yarn_names:
    assert name in hfss.modeler.solid_names, f"{name} not found in solids!"

print("All assertions passed.")
hfss.modeler.fit_all()
hfss.save_project()
