import os
from tkinter import Button
from tkinter import Entry
from tkinter import Label
from tkinter import RAISED
from tkinter import StringVar
from tkinter import Tk
from tkinter import mainloop

from pyaedt import Desktop
from pyaedt import Hfss
from pyaedt import Hfss3dLayout
from pyaedt import Icepak
from pyaedt import Maxwell3d
from pyaedt import Q3d

master = Tk()
var = StringVar()
label = Label(master, textvariable=var, relief=RAISED)
var.set("1 - Export to HFSS\n2 - Export to Q3D\n3 - Export to Maxwell 3D\n4 - Export to Icepak")
label.pack()
e = Entry(master)
e.pack()

e.focus_set()
choice = "1"


def callback():
    global choice
    choice = e.get()  # This is the text you may want to use later
    master.destroy()
    return True


b = Button(master, text="OK", width=10, command=callback)
b.pack()

mainloop()
if choice not in ["1", "2", "3", "4"]:
    raise Exception("Wrong input.")
suffixes = {"1": "HFSS", "2": "Q3D", "3": "M3D", "4": "IPK"}

if "PYAEDT_SCRIPT_PORT" in os.environ and "PYAEDT_SCRIPT_VERSION" in os.environ:
    port = os.environ["PYAEDT_SCRIPT_PORT"]
    version = os.environ["PYAEDT_SCRIPT_VERSION"]
else:
    port = 0
    version = "2024.1"

with Desktop(new_desktop_session=False, close_on_exit=False, specified_version=version, port=port) as d:
    proj = d.active_project()
    des = d.active_design()
    projname = proj.GetName()
    if des.GetDesignType() in ["HFSS 3D Layout Design"]:
        desname = des.GetName().split(";")[1]
    else:
        d.odesktop.AddMessage("", "", 3, "Hfss 3D Layout project is needed.")
        d.release_desktop(False, False)
        raise Exception("Hfss 3D Layout project is needed.")
    h3d = Hfss3dLayout(projectname=projname, designname=desname)
    setup = h3d.create_setup()
    suffix = suffixes[choice]

    if choice == "2":
        setup.export_to_q3d(h3d.project_file[:-5] + f"_{suffix}.aedt", keep_net_name=True)
    else:
        setup.export_to_hfss(h3d.project_file[:-5] + f"_{suffix}.aedt", keep_net_name=True)
    h3d.delete_setup(setup.name)
    if choice == "2":
        app = Q3d(projectname=h3d.project_file[:-5] + f"_{suffix}.aedt")
    else:
        app = Hfss(projectname=h3d.project_file[:-5] + f"_{suffix}.aedt")
        app2 = None
        if choice == "3":
            app2 = Maxwell3d(projectname=app.project_name)
        elif choice == "4":
            app2 = Icepak(projectname=app.project_name)
        if app2:
            app2.copy_solid_bodies_from(
                app,
                no_vacuum=False,
                no_pec=False,
                include_sheets=True,
            )
            app2.delete_design(app.design_name)
            app2.save_project()
    d.logger.info("Project generated correctly.")
