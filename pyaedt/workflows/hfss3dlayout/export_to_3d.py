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
from pyaedt.workflows.misc import is_test

choice = "Export to HFSS"

port = get_port()
version = get_aedt_version()
aedt_process_id = get_process_id()
test_dict = is_test()

if not test_dict["is_test"]:  # pragma: no cover
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

else:
    choice = test_dict["choice"]

suffixes = {"Export to HFSS": "HFSS", "Export to Q3D": "Q3D", "Export to Maxwell 3D": "M3D", "Export to Icepak": "IPK"}


def main():
    app = pyaedt.Desktop(new_desktop_session=False, specified_version=version, port=port)

    active_project = app.active_project()
    active_design = app.active_design()

    project_name = active_project.GetName()

    if active_design.GetDesignType() in ["HFSS 3D Layout Design"]:
        design_name = active_design.GetName().split(";")[1]
    else:  # pragma: no cover
        app.logger.debug("Hfss 3D Layout project is needed.")
        app.release_desktop(False, False)
        raise Exception("Hfss 3D Layout project is needed.")

    h3d = pyaedt.Hfss3dLayout(projectname=project_name, designname=design_name)
    setup = h3d.create_setup()
    suffix = suffixes[choice]

    if choice == "Export to Q3D":
        setup.export_to_q3d(h3d.project_file[:-5] + f"_{suffix}.aedt", keep_net_name=True)
    else:
        setup.export_to_hfss(h3d.project_file[:-5] + f"_{suffix}.aedt", keep_net_name=True)

    h3d.delete_setup(setup.name)

    if choice == "Export to Q3D":
        _ = pyaedt.Q3d(projectname=h3d.project_file[:-5] + f"_{suffix}.aedt")
    else:
        aedtapp = pyaedt.Hfss(projectname=h3d.project_file[:-5] + f"_{suffix}.aedt")
        aedtapp2 = None
        if choice == "Export to Maxwell 3D":
            aedtapp2 = pyaedt.Maxwell3d(projectname=aedtapp.project_name)
        elif choice == "Export to Icepak":
            aedtapp2 = pyaedt.Icepak(projectname=aedtapp.project_name)
        if aedtapp2:
            aedtapp2.copy_solid_bodies_from(
                aedtapp,
                no_vacuum=False,
                no_pec=False,
                include_sheets=True,
            )
            aedtapp2.delete_design(app.design_name)
            aedtapp2.save_project()
    app.logger.info("Project generated correctly.")

    if not test_dict["is_test"]:  # pragma: no cover
        app.release_desktop(False, False)


if __name__ == "__main__":
    main()
