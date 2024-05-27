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

import pyaedt
import pyaedt.workflows.hfss3dlayout
from pyaedt.workflows.misc import get_aedt_version
from pyaedt.workflows.misc import get_port
from pyaedt.workflows.misc import get_process_id

choice = "Export to HFSS"

is_test = False
if "PYAEDT_TEST_CONFIG" in os.environ:
    is_test = True
    extra_vars = json.loads(os.environ["PYAEDT_TEST_CONFIG"])
    choice = extra_vars["choice"]

if not is_test:
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

    def callback():
        global choice
        choice = combo.get()
        master.destroy()
        return True

    b = Button(master, text="Export", width=40, command=callback)
    b.pack(pady=10)

    mainloop()

suffixes = {"Export to HFSS": "HFSS", "Export to Q3D": "Q3D", "Export to Maxwell 3D": "M3D", "Export to Icepak": "IPK"}

port = get_port()
version = get_aedt_version()
aedt_process_id = get_process_id()

d = pyaedt.Desktop(new_desktop_session=False, specified_version=version, port=port)

active_project = d.active_project()
active_design = d.active_design()

projname = active_project.GetName()

if active_design.GetDesignType() in ["HFSS 3D Layout Design"]:
    desname = active_design.GetName().split(";")[1]
else:  # pragma: no cover
    d.odesktop.AddMessage("", "", 3, "Hfss 3D Layout project is needed.")
    d.release_desktop(False, False)
    raise Exception("Hfss 3D Layout project is needed.")

h3d = pyaedt.Hfss3dLayout(projectname=projname, designname=desname)
setup = h3d.create_setup()
suffix = suffixes[choice]

if choice == "Export to Q3D":
    setup.export_to_q3d(h3d.project_file[:-5] + f"_{suffix}.aedt", keep_net_name=True)
else:
    setup.export_to_hfss(h3d.project_file[:-5] + f"_{suffix}.aedt", keep_net_name=True)

h3d.delete_setup(setup.name)

if choice == "Export to Q3D":
    app = pyaedt.Q3d(projectname=h3d.project_file[:-5] + f"_{suffix}.aedt")
else:
    app = pyaedt.Hfss(projectname=h3d.project_file[:-5] + f"_{suffix}.aedt")
    app2 = None
    if choice == "Export to Maxwell 3D":
        app2 = pyaedt.Maxwell3d(projectname=app.project_name)
    elif choice == "Export to Icepak":
        app2 = pyaedt.Icepak(projectname=app.project_name)
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
