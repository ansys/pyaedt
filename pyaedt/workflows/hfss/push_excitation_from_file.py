import os.path
from tkinter import Button

# import filedialog module
from tkinter import END
from tkinter import Label
from tkinter import StringVar
from tkinter import Text
from tkinter import Tk
from tkinter import filedialog
from tkinter import mainloop
from tkinter import ttk
from tkinter.ttk import Combobox

import PIL.Image
import PIL.ImageTk

import pyaedt
from pyaedt import Hfss
import pyaedt.workflows
from pyaedt.workflows.misc import get_aedt_version
from pyaedt.workflows.misc import get_port
from pyaedt.workflows.misc import get_process_id
from pyaedt.workflows.misc import is_test

choice = ""
file_path = ""


def browse_port(port_selection):  # pragma: no cover
    # Function for opening the
    # file explorer window

    master = Tk()

    master.geometry("700x150")

    master.title("Assign push excitation to port from transient data")

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
    var.set("Choose a port:")
    label.grid(row=0, column=0, pady=10)
    combo = Combobox(master, width=30)  # Set the width of the combobox
    combo["values"] = port_selection
    combo.current(0)
    combo.grid(row=0, column=1, pady=10, padx=5)
    combo.focus_set()
    var2 = StringVar()
    label2 = Label(master, textvariable=var2)
    var2.set("Browse file:")
    label2.grid(row=1, column=0, pady=10)
    text = Text(master, width=50, height=1)
    text.grid(row=1, column=1, pady=10, padx=5)

    def browseFiles():
        filename = filedialog.askopenfilename(
            initialdir="/",
            title="Select a Transient File",
            filetypes=(("Transient curve", "*.csv*"), ("all files", "*.*")),
        )
        text.insert(END, filename)
        # # Change label contents
        # return filename

    b1 = Button(master, text="...", width=10, command=browseFiles)
    b1.grid(row=3, column=0)
    # b1.pack(pady=10)
    b1.grid(row=1, column=2, pady=10)

    def callback():
        global choice, file_path
        choice = combo.get()
        file_path = text.get("1.0", END).strip()
        master.destroy()
        return True

    b = Button(master, text="Ok", width=40, command=callback)
    b.grid(row=2, column=1, pady=10)

    mainloop()


port = get_port()
version = get_aedt_version()
aedt_process_id = get_process_id()
test_dict = is_test()


def main():
    d = pyaedt.Desktop(new_desktop_session=False, specified_version=version, port=port, aedt_process_id=aedt_process_id)

    proj = d.active_project()
    des = d.active_design()

    projname = proj.GetName()
    desname = des.GetName()

    app = Hfss(projname, desname)

    if not test_dict["is_test"]:
        browse_port(port_selection=app.excitations)
    else:
        choice = test_dict["choice"]
        file_path = test_dict["file_path"]

    if choice:
        app.edit_source_from_file(
            choice,
            file_path,
            is_time_domain=True,
        )
        d.logger.info("Excitation assigned correctly.")
    else:
        d.logger.error("Failed to select a port.")

    if not is_test:  # pragma: no cover
        d.release_desktop(False, False)


if __name__ == "__main__":
    main()
