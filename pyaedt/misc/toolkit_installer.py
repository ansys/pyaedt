import tkinter as tk
from tkinter import ttk

# from pyaedt.misc.install_extra_toolkits import available_toolkits


def create_library_buttons(frame, libraries):
    for library in libraries:
        button = ttk.Button(frame, text=library, style="Toolbutton.TButton")
        button.pack(side=tk.TOP, pady=5)


def open_window(window, window_name, libraries):
    if not hasattr(window, "opened"):
        window.opened = True
        window.title(window_name)
        create_library_buttons(window, libraries)
        root.minsize(550, 250)
    else:
        window.deiconify()


def toolkit_window(toolkit_level="Project"):
    toolkit_window_var = tk.Toplevel(root)
    open_window(toolkit_window_var, toolkit_level, ["library1", "library2", "library3"])


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

window_width, window_height = 550, 250
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
