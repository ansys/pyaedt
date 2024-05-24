import os.path

# import filedialog module
from tkinter import filedialog

from pyaedt import Desktop
from pyaedt import get_pyaedt_app
from pyaedt.workflows.misc import get_aedt_version
from pyaedt.workflows.misc import get_port
from pyaedt.workflows.misc import get_process_id


# Function for opening the
# file explorer window
def browseFiles():
    filename = filedialog.askopenfilename(
        initialdir="/", title="Select a File", filetypes=(("Nastran files", "*.nas*"), ("all files", "*.*"))
    )

    # Change label contents
    return filename


nas_input = browseFiles()

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
        app.modeler.import_nastran(nas_input)
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
