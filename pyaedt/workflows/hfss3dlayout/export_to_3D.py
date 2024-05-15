import os
from tkinter import Button
from tkinter import Label
from tkinter import RAISED
from tkinter import StringVar
from tkinter import Tk
from tkinter import mainloop
from tkinter import ttk
from tkinter.ttk import Combobox

import PIL.Image
import PIL.ImageTk

from pyaedt import Desktop
from pyaedt import Hfss
from pyaedt import Hfss3dLayout
from pyaedt import Icepak
from pyaedt import Maxwell3d
from pyaedt import Q3d
import pyaedt.workflows.hfss3dlayout

master = Tk()

master.geometry("400x150")

master.title("Export to 3D")

# Load the logo for the main window
icon_path = os.path.join(os.path.dirname(pyaedt.workflows.__file__), "images", "large", "logo.png")
im = PIL.Image.open(icon_path)
photo = PIL.ImageTk.PhotoImage(im)

# Set the icon for the main window
master.iconphoto(True, photo)

# Configure style for ttk buttons
style = ttk.Style()
style.configure("Toolbutton.TButton", padding=6, font=("Helvetica", 10))

var = StringVar()
label = Label(master, textvariable=var, relief=RAISED)
var.set("Choose an option:")
label.pack(pady=10)
combo = Combobox(master, width=40)  # Set the width of the combobox
combo["values"] = ("Export to HFSS", "Export to Q3D", "Export to Maxwell 3D", "Export to Icepak")
combo.current(0)
combo.pack(pady=10)

combo.focus_set()
choice = "Export to HFSS"


def callback():
    global choice
    choice = combo.get()
    master.destroy()
    return True


b = Button(master, text="Export", width=40, command=callback)
b.pack(pady=10)

mainloop()

suffixes = {"Export to HFSS": "HFSS", "Export to Q3D": "Q3D", "Export to Maxwell 3D": "M3D", "Export to Icepak": "IPK"}

if "PYAEDT_SCRIPT_PORT" in os.environ and "PYAEDT_SCRIPT_VERSION" in os.environ:
    port = int(os.environ["PYAEDT_SCRIPT_PORT"])
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

    if choice == "Export to Q3D":
        setup.export_to_q3d(h3d.project_file[:-5] + f"_{suffix}.aedt", keep_net_name=True)
    else:
        setup.export_to_hfss(h3d.project_file[:-5] + f"_{suffix}.aedt", keep_net_name=True)
    h3d.delete_setup(setup.name)
    if choice == "Export to Q3D":
        app = Q3d(projectname=h3d.project_file[:-5] + f"_{suffix}.aedt")
    else:
        app = Hfss(projectname=h3d.project_file[:-5] + f"_{suffix}.aedt")
        app2 = None
        if choice == "Export to Maxwell 3D":
            app2 = Maxwell3d(projectname=app.project_name)
        elif choice == "Export to Icepak":
            app2 = Icepak(projectname=app.project_name)
        if app2:
            app2.copy_solid_bodies_from(app, vacuum=False, pec=False, include_sheets=True)
            app2.delete_design(app.design_name)
            app2.save_project()
    d.logger.info("Project generated correctly.")
