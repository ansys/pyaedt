from subprocess import call
import tkinter as tk


def uninstall_library(library_name):
    call(["pip", "uninstall", library_name])


def create_library_buttons(frame, libraries):
    for library in libraries:
        button = tk.Button(frame, text=library)

        button.pack(side=tk.TOP, pady=5)


def project_window():
    project_window = tk.Toplevel(root)
    project_window.title("Project Libraries")


libraries = ["library1", "library2", "library3"]

create_library_buttons(project_window, libraries)

back_button = tk.Button(project_window, text="Back", command=project_window.destroy)

back_button.pack(side=tk.BOTTOM, pady=10)


def hfss_window():
    hfss_window = tk.Toplevel(root)
    hfss_window.title("HFSS Libraries")


libraries = ["hfss_library1", "hfss_library2", "hfss_library3"]

create_library_buttons(hfss_window, libraries)

back_button.pack(side=tk.BOTTOM, pady=10)

root = tk.Tk()
root.title("Main Menu")

project_button = tk.Button(root, text="Project", command=project_window)

project_button.pack(side=tk.LEFT, padx=10)

hfss_button = tk.Button(root, text="HFSS", command=hfss_window)

hfss_button.pack.pack(side=tk.RIGHT, padx=10)

root.mainloop()
