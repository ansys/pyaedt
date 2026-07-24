from ansys.aedt.core import Hfss

hfss = Hfss(
    project="test_define_weave",
    design="WeaveTest",
    new_desktop=False,
)

sub = hfss.modeler["Substrate"]


yarn_names = hfss.modeler.define_weave(
    sub,
    weave_style="1067",
    weave_rotate_deg=0,
)

hfss.save_project()