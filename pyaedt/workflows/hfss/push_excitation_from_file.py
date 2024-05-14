import os.path
from tkinter import Button
from tkinter import Label

# import filedialog module
from tkinter import RAISED
from tkinter import StringVar
from tkinter import Tk
from tkinter import filedialog
from tkinter import mainloop
from tkinter import ttk
from tkinter.ttk import Combobox

import PIL.Image
import PIL.ImageTk

import pyaedt
from pyaedt import Desktop
from pyaedt import Hfss

choice = ""


def browse_port(port_selection):
    master = Tk()

    master.geometry("500x150")

    master.title("Assign push excitation to port from transient data")

    # Load the logo for the main window
    icon_path = os.path.join(pyaedt.__path__[0], "workflows", "images", "large", "logo.png")
    im = PIL.Image.open(icon_path)
    photo = PIL.ImageTk.PhotoImage(im)

    # Set the icon for the main window
    master.iconphoto(True, photo)

    # Configure style for ttk buttons
    style = ttk.Style()
    style.configure("Toolbutton.TButton", padding=6, font=("Helvetica", 10))

    var = StringVar()
    label = Label(master, textvariable=var, relief=RAISED)
    var.set("Choose a port:")
    label.pack(pady=10)
    combo = Combobox(master, width=40)  # Set the width of the combobox
    combo["values"] = port_selection
    combo.current(0)
    combo.pack(pady=10)

    combo.focus_set()

    def callback():
        global choice
        choice = combo.get()
        master.destroy()
        return True

    b = Button(master, text="Ok", width=40, command=callback)
    b.pack(pady=10)

    mainloop()


# Function for opening the
# file explorer window
def browseFiles():
    filename = filedialog.askopenfilename(
        initialdir="/", title="Select a Transient File", filetypes=(("Transient curve", "*.csv*"), ("all files", "*.*"))
    )

    # Change label contents
    return filename


if "PYAEDT_SCRIPT_PORT" in os.environ and "PYAEDT_SCRIPT_VERSION" in os.environ:
    port = os.environ["PYAEDT_SCRIPT_PORT"]
    version = os.environ["PYAEDT_SCRIPT_VERSION"]
else:
    port = 0
    version = "2023.2"
with Desktop(new_desktop_session=False, close_on_exit=False, specified_version=version, port=port) as d:
    proj = d.active_project()
    des = d.active_design()
    projname = proj.GetName()
    desname = des.GetName()
    app = Hfss(projname, desname)
    if len(app.excitations) == 1:
        choice = app.excitations[0]
    else:
        browse_port(app.excitations)
    if choice:
        curve_info = browseFiles()
        app.edit_source_from_file(
            choice,
            curve_info,
            is_time_domain=True,
        )
        d.logger.info("Excitation assigned correctly.")
    else:
        d.logger.error("Failed to select a port.")
