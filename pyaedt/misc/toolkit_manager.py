import os
import tkinter as tk
from tkinter import ttk

from pyaedt import Desktop
from pyaedt import is_windows
from pyaedt.misc.install_extra_toolkits import available_toolkits


def create_library_buttons(frame, libraries):
    buttons = []

    # Create the option menu at the top
    option_action = tk.StringVar(value="Install")
    install_radio = tk.Radiobutton(frame, text="Install", variable=option_action, value="Install")
    uninstall_radio = tk.Radiobutton(frame, text="Uninstall", variable=option_action, value="Uninstall")
    install_radio.grid(row=0, column=0, padx=5, pady=5)
    uninstall_radio.grid(row=0, column=2, padx=5, pady=5)

    buttons.append(option_action)

    row = 1
    for library in libraries:
        if is_windows:
            venv_dir = os.path.join(os.environ["APPDATA"], "{}_env_ide".format(library))
            python_exe = os.path.join(venv_dir, "Scripts", "python.exe")

        else:
            venv_dir = os.path.join(os.environ["HOME"], "{}_env_ide".format(library))
            python_exe = os.path.join(venv_dir, "bin", "python")

        # Set the initial button color
        button_bg_color = "green" if os.path.isfile(python_exe) else "red"

        button = tk.Button(frame, text=library, bg=button_bg_color, fg="white")
        button.grid(row=row, column=1, padx=5, pady=5)

        buttons.append(button)
        row += 1

    return buttons


def open_window(window, window_name, libraries):
    if not hasattr(window, "opened"):
        window.opened = True
        window.title(window_name)
        buttons = create_library_buttons(window, libraries)
        root.minsize(500, 250)
        return buttons
    else:
        window.deiconify()


def toolkit_window(toolkit_level="Project"):
    toolkit_window_var = tk.Toplevel(root)
    specific_toolkits = []
    for toolkit_name, toolkit_info in available_toolkits.items():
        if toolkit_info["installation_path"].lower() == toolkit_level.lower():
            specific_toolkits.append(toolkit_name)
    toolkit_window_var.minsize(300, 200)
    buttons = open_window(toolkit_window_var, toolkit_level, specific_toolkits)

    option_action = buttons[0]
    library_buttons = buttons[1:]
    for button in library_buttons:
        # Attach event handlers or perform other actions
        button.configure(command=lambda b=button, o=option_action: on_button_click(b, o))


def on_button_click(button, option_action):
    if is_windows:
        venv_dir = os.path.join(os.environ["APPDATA"], "{}_env_ide".format(button["text"]))
        python_exe = os.path.join(venv_dir, "Scripts", "python.exe")

    else:
        venv_dir = os.path.join(os.environ["HOME"], "{}_env_ide".format(button["text"]))
        python_exe = os.path.join(venv_dir, "bin", "python")

    student_version = False
    if (
        "PYAEDT_SCRIPT_VERSION" in os.environ
        and "PYAEDT_SCRIPT_PORT" in os.environ
        and "PYAEDT_STUDENT_VERSION" in os.environ
    ):

        version = os.environ["PYAEDT_SCRIPT_VERSION"]
        port = int(os.environ["PYAEDT_SCRIPT_PORT"])
        student_version = False if os.environ["PYAEDT_STUDENT_VERSION"] == "False" else True

        desktop = Desktop(
            specified_version=version,
            port=port,
            new_desktop_session=False,
            non_graphical=False,
            close_on_exit=False,
            student_version=student_version,
        )
    else:
        desktop = Desktop(
            new_desktop_session=True,
            non_graphical=False,
            close_on_exit=False,
            student_version=student_version,
        )

    action = option_action.get()

    if os.path.isfile(python_exe) and action == "Install":
        desktop.logger.info(f"Updating {button['text']} toolkit.")
        desktop.add_custom_toolkit(button["text"])
    elif action == "Install":
        desktop.logger.info(f"Installing {button['text']} toolkit.")
        desktop.add_custom_toolkit(button["text"])
    elif os.path.isfile(python_exe) and action == "Uninstall":
        desktop.logger.info(f"Uninstalling {button['text']} toolkit.")
        desktop.delete_custom_toolkit(button["text"])
    else:
        desktop.logger.info(f"{button['text']} not installed.")

    if os.path.isfile(python_exe):
        button.configure(text=button["text"], bg="green", fg="white")
    else:
        button.configure(text=button["text"], bg="red", fg="white")

    desktop.odesktop.RefreshToolkitUI()
    desktop.release_desktop(False, False)


root = tk.Tk()
root.title("AEDT Toolkit Manager")

# Load the logo for the main window
icon_path = r"images\large\logo.png"
icon = tk.PhotoImage(file=icon_path)

# Set the icon for the main window
root.iconphoto(True, icon)

# Configure style for ttk buttons
style = ttk.Style()
style.configure("Toolbutton.TButton", padding=6, font=("Helvetica", 10))

toolkit_levels = [
    "Project",
    "",
    "",
    "",
    "HFSS",
    "Maxwell3D",
    "Icepak",
    "Q3D",
    "Maxwell2D",
    "Q2D",
    "HFSS3DLayout",
    "Mechanical",
    "Circuit",
    "EMIT",
    "Simplorer",
    "",
]

window_width, window_height = 500, 250
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()
x_position = (screen_width - window_width) // 2
y_position = (screen_height - window_height) // 2

root.geometry(f"{window_width}x{window_height}+{x_position}+{y_position}")

# Create buttons in a 4x4 grid, centered
for i, level in enumerate(toolkit_levels):
    row_num = i // 4
    col_num = i % 4
    if level:
        toolkit_button = ttk.Button(
            root, text=level, command=lambda l=level: toolkit_window(l), style="Toolbutton.TButton"
        )
        toolkit_button.grid(row=row_num, column=col_num, padx=10, pady=10)

root.minsize(window_width, window_height)

root.mainloop()
