import os
import tkinter as tk
from tkinter import ttk

import PIL.Image
import PIL.ImageTk

from pyaedt import Desktop
from pyaedt import is_windows
from pyaedt.misc.install_extra_toolkits import available_toolkits

env_vars = ["PYAEDT_SCRIPT_VERSION", "PYAEDT_SCRIPT_PORT", "PYAEDT_STUDENT_VERSION"]
if all(var in os.environ for var in env_vars):
    version = os.environ["PYAEDT_SCRIPT_VERSION"]
    version = version[2:6].replace(".", "")
    port = int(os.environ["PYAEDT_SCRIPT_PORT"])
    student_version = False if os.environ["PYAEDT_STUDENT_VERSION"] == "False" else True
else:
    version = "2024.1"
    port = 0
    student_version = False

if is_windows:
    venv_dir = os.path.join(os.environ["APPDATA"], "pyaedt_env_ide", "toolkits_v{}".format(version))
    python_exe = os.path.join(venv_dir, "Scripts", "python.exe")
    package_dir = os.path.join(venv_dir, "Lib", "site-packages")

else:
    venv_dir = os.path.join(os.environ["HOME"], "pyaedt_env_ide", "toolkits_v{}".format(version))
    python_exe = os.path.join(venv_dir, "bin", "python")
    package_dir = os.path.join(venv_dir, "Lib", "site-packages")


def create_toolkit_page(frame, open_source_toolkits):
    """Create page to display toolkit on."""
    # Available toolkits
    toolkits = ["Custom"] + open_source_toolkits
    max_length = max(len(item) for item in toolkits)

    # Pip or Offline radio options
    installation_option_action = tk.StringVar(value="Offline")
    pip_installation_radio = tk.Radiobutton(frame, text="Pip", variable=installation_option_action, value="Pip")
    offline_installation_radio = tk.Radiobutton(
        frame, text="Offline", variable=installation_option_action, value="Offline"
    )
    pip_installation_radio.grid(row=1, column=0, padx=5, pady=5)
    offline_installation_radio.grid(row=1, column=1, padx=5, pady=5)

    # Combobox with available toolkit options
    toolkits_combo_label = tk.Label(frame, text="Toolkit:", width=max_length)
    toolkits_combo_label.grid(row=2, column=0, padx=5, pady=5)

    toolkits_combo = ttk.Combobox(
        frame, values=list(filter(lambda x: x != "", toolkits)), state="readonly", width=max_length
    )
    toolkits_combo.set("Custom")
    toolkits_combo.grid(row=2, column=1, padx=5, pady=5)

    # Create entry box for directory path
    input_file_label = tk.Label(frame, text="Enter script path:")
    input_file_label.grid(row=3, column=0, padx=5, pady=5)
    input_file = tk.Entry(frame)
    input_file.grid(row=3, column=1, padx=5, pady=5)

    toolkit_name_label = tk.Label(frame, text="Enter toolkit name:")
    toolkit_name_label.grid(row=4, column=0, padx=5, pady=5)
    toolkit_name = tk.Entry(frame)
    toolkit_name.grid(row=4, column=1, padx=5, pady=5)

    # Install button
    install_button = tk.Button(frame, text="Install", bg="green", fg="white", padx=20, pady=5)
    install_button.grid(row=5, column=0, padx=5, pady=5, sticky="nsew")
    uninstall_button = tk.Button(frame, text="Uninstall", bg="red", fg="white", padx=20, pady=5)
    uninstall_button.grid(row=5, column=1, padx=5, pady=5, sticky="nsew")

    def update_page(event=None):
        selected_toolkit = toolkits_combo.get()
        if selected_toolkit == "Custom":
            install_button.config(text="Install")
            uninstall_button.config(state="normal")
        else:
            if is_toolkit_installed(selected_toolkit):
                install_button.config(text="Update")
                uninstall_button.config(state="normal")
            else:
                install_button.config(text="Install")
                uninstall_button.config(state="disabled")

        if installation_option_action.get() == "Pip" and selected_toolkit != "Custom":
            toolkit_name.config(state="disabled")
            input_file_label.config(text="Enter wheelhouse path:")
            input_file.config(state="disabled")
        elif (installation_option_action.get() == "Pip" and selected_toolkit == "Custom") or (
            installation_option_action.get() == "Offline" and selected_toolkit == "Custom"
        ):
            toolkit_name.config(state="normal")
            input_file_label.config(text="Enter script path:")
            input_file.config(state="normal")
            installation_option_action.set("Offline")
        else:
            toolkit_name.config(state="disabled")
            input_file_label.config(text="Enter wheelhouse path:")
            input_file.config(state="normal")

    toolkits_combo.bind("<<ComboboxSelected>>", update_page)

    update_page()

    return install_button, uninstall_button, input_file, toolkits_combo, toolkit_name


def is_toolkit_installed(toolkit_name):
    """Check if toolkit is installed."""
    if toolkit_name == "Custom":
        return False
    script_file = os.path.normpath(os.path.join(package_dir, available_toolkits[toolkit_name]["toolkit_script"]))
    return True if os.path.isfile(script_file) else False


def open_window(window, window_name, open_source_toolkits):
    """Open a window."""
    if not hasattr(window, "opened"):
        window.opened = True
        window.title(window_name)
        install_button, uninstall_button, input_file, toolkits_combo, toolkit_name = create_toolkit_page(
            window, open_source_toolkits
        )
        root.minsize(500, 250)
        return install_button, uninstall_button, input_file, toolkits_combo, toolkit_name
    else:
        window.deiconify()


def __get_command_function(
    is_install, toolkit_level, input_file, toolkits_combo, toolkit_name, install_button, uninstall_button
):
    return lambda: button_is_clicked(
        is_install, toolkit_level, input_file, toolkits_combo, toolkit_name, install_button, uninstall_button
    )


def toolkit_window(toolkit_level="Project"):
    """Create interactive toolkit window."""
    toolkit_window_var = tk.Toplevel(root)
    open_source_toolkits = []
    for toolkit_name, toolkit_info in available_toolkits.items():
        if toolkit_info["installation_path"].lower() == toolkit_level.lower():
            open_source_toolkits.append(toolkit_name)
    toolkit_window_var.minsize(250, 150)
    install_button, uninstall_button, input_file, toolkits_combo, toolkit_name = open_window(
        toolkit_window_var, toolkit_level, open_source_toolkits
    )

    install_command = __get_command_function(
        True, toolkit_level, input_file, toolkits_combo, toolkit_name, install_button, uninstall_button
    )
    uninstall_command = __get_command_function(
        False, toolkit_level, input_file, toolkits_combo, toolkit_name, install_button, uninstall_button
    )

    install_button.configure(command=install_command)
    uninstall_button.configure(command=uninstall_command)


def button_is_clicked(
    install_action, toolkit_level, input_file, combo_toolkits, toolkit_name, install_button, uninstall_button
):
    """Set up a button for installing and uninstalling the toolkit."""
    file = input_file.get()
    selected_toolkit_name = combo_toolkits.get()
    name = toolkit_name.get()

    desktop = Desktop(
        specified_version=version,
        port=port,
        new_desktop_session=False,
        non_graphical=False,
        close_on_exit=False,
        student_version=student_version,
    )

    desktop.odesktop.CloseAllWindows()

    if selected_toolkit_name != "Custom":
        desktop.logger.info("TEST: VENV {}".format(venv_dir))
        if is_toolkit_installed(selected_toolkit_name) and install_action:
            desktop.logger.info("Updating {}".format(selected_toolkit_name))
            desktop.add_custom_toolkit(selected_toolkit_name, file)
            install_button.config(text="Update")
            uninstall_button.config(state="normal")
            desktop.logger.info("{} updated".format(selected_toolkit_name))
        elif install_action:
            desktop.logger.info("Installing {}".format(selected_toolkit_name))
            desktop.add_custom_toolkit(selected_toolkit_name, file)
            install_button.config(text="Update")
            uninstall_button.config(state="normal")
        elif is_toolkit_installed(selected_toolkit_name) and not install_action:
            desktop.logger.info("Uninstalling {}".format(selected_toolkit_name))
            desktop.add_custom_toolkit(selected_toolkit_name, install=False)
            install_button.config(text="Install")
            uninstall_button.config(state="disabled")
            desktop.logger.info("{} uninstalled".format(selected_toolkit_name))
        else:
            desktop.logger.info("{} not installed".format(selected_toolkit_name))

    else:
        if install_action:
            desktop.logger.info("Install {}".format(name))
            if is_windows:
                pyaedt_venv_dir = os.path.join(os.environ["APPDATA"], "pyaedt_env_ide", "v{}".format(version))
                executable_interpreter = os.path.join(pyaedt_venv_dir, "Scripts", "python.exe")
            else:
                pyaedt_venv_dir = os.path.join(os.environ["HOME"], "pyaedt_env_ide", "v{}".format(version))
                executable_interpreter = os.path.join(pyaedt_venv_dir, "bin", "python")
            if os.path.isfile(executable_interpreter):
                desktop.add_script_to_menu(
                    toolkit_name=name,
                    script_path=file,
                    product=toolkit_level,
                    executable_interpreter=executable_interpreter,
                )
            else:
                desktop.logger.info("PyAEDT environment is not installed.")
        else:
            desktop.logger.info("Uninstall {}.".format(name))
            desktop.remove_script_from_menu(name, product=toolkit_level)

    desktop.odesktop.CloseAllWindows()
    desktop.odesktop.RefreshToolkitUI()
    desktop.release_desktop(False, False)


root = tk.Tk()
root.title("AEDT Toolkit Manager")

# Load the logo for the main window
icon_path = os.path.join(os.path.dirname(__file__), "images", "large", "logo.png")
im = PIL.Image.open(icon_path)
photo = PIL.ImageTk.PhotoImage(im)

# Set the icon for the main window
root.iconphoto(True, photo)

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
