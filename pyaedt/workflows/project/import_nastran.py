import os.path
from tkinter import Button
from tkinter import Checkbutton

# import filedialog module
from tkinter import END
from tkinter import IntVar
from tkinter import Label
from tkinter import StringVar
from tkinter import Text
from tkinter import Tk
from tkinter import filedialog
from tkinter import mainloop
from tkinter import ttk

import PIL.Image
import PIL.ImageTk

from pyaedt import Desktop
from pyaedt import get_pyaedt_app
import pyaedt.workflows
from pyaedt.workflows.misc import get_aedt_version
from pyaedt.workflows.misc import get_port
from pyaedt.workflows.misc import get_process_id

decimate = 0.0

lightweight = False
file_path = ""


def browse_nastran():
    # Function for opening the
    # file explorer window

    master = Tk()

    master.geometry("700x200")

    master.title("Import Nastran or STL file")

    # Load the logo for the main window
    icon_path = os.path.join(pyaedt.workflows.__path__[0], "images", "large", "logo.png")
    im = PIL.Image.open(icon_path)
    photo = PIL.ImageTk.PhotoImage(im)

    # Set the icon for the main window
    master.iconphoto(True, photo)

    # Configure style for ttk buttons
    style = ttk.Style()
    style.configure("Toolbutton.TButton", padding=6, font=("Helvetica", 8))

    var = StringVar()
    label = Label(master, textvariable=var)
    var.set("Decimation factor (0-0.9). It may affect results:")
    label.grid(row=0, column=0, pady=10)
    check = Text(master, width=20, height=1)  # Set the width of the combobox
    check.insert(END, "0.0")
    check.grid(row=0, column=1, pady=10, padx=5)
    var = StringVar()
    label = Label(master, textvariable=var)
    var.set("Import as lightweight (only HFSS):")
    label.grid(row=1, column=0, pady=10)
    light = IntVar()
    check2 = Checkbutton(master, width=30, variable=light)  # Set the width of the combobox
    check2.grid(row=1, column=1, pady=10, padx=5)
    var2 = StringVar()
    label2 = Label(master, textvariable=var2)
    var2.set("Browse file:")
    label2.grid(row=2, column=0, pady=10)
    text = Text(master, width=40, height=1)
    text.grid(row=2, column=1, pady=10, padx=5)

    def browseFiles():
        filename = filedialog.askopenfilename(
            initialdir="/",
            title="Select a Nastran or stl File",
            filetypes=(("Nastran", "*.nas"), ("STL", "*.stl"), ("all files", "*.*")),
        )
        text.insert(END, filename)
        # # Change label contents
        # return filename

    b1 = Button(master, text="...", width=10, command=browseFiles)
    b1.grid(row=3, column=0)
    # b1.pack(pady=10)
    b1.grid(row=2, column=2, pady=10)

    def callback():
        global lightweight, decimate, file_path
        decimate = float(check.get("1.0", END).strip())
        lightweight = True if light.get() == 1 else False
        file_path = text.get("1.0", END).strip()
        master.destroy()
        return True

    b = Button(master, text="Ok", width=40, command=callback)
    # b.pack(pady=10)
    b.grid(row=3, column=1, pady=10)

    mainloop()


browse_nastran()

port = get_port()
version = get_aedt_version()
aedt_process_id = get_process_id()

if os.path.exists(nas_input):
    with Desktop(
        new_desktop_session=False,
        close_on_exit=False,
        specified_version=version,
        port=port,
        aedt_process_id=aedt_process_id,
    ) as d:
        proj = d.active_project()
        des = d.active_design()
        projname = proj.GetName()
        desname = des.GetName()
        app = get_pyaedt_app(projname, desname)
        if file_path.endswith(".nas"):
            app.modeler.import_nastran(file_path, import_as_light_weight=lightweight, decimation=decimate)
        else:
            from pyaedt.modules.solutions import simplify_stl

            outfile = simplify_stl(file_path, decimation=decimate, aggressiveness=5)
            app.modeler.import_3d_cad(outfile, healing=False, create_lightweigth_part=lightweight)
        d.logger.info("Nastran imported correctly.")
else:
    with Desktop(
        new_desktop_session=False,
        close_on_exit=False,
        specified_version=version,
        port=port,
        aedt_process_id=aedt_process_id,
    ) as d:
        d.odesktop.AddMessage("", "", 3, "Wrong file selected. Select a .nas file")
