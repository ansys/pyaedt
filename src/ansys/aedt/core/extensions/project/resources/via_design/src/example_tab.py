from dataclasses import dataclass

from ansys.aedt.core.extensions.misc import DEFAULT_PADDING
from ansys.aedt.core.extensions.misc import SUN
from pathlib import Path
from tkinter import filedialog, ttk
from functools import partial

import PIL


@dataclass
class ExportExampleData:
    """"""

    picture_path: Path
    toml_file_path: Path


def create_example_ui(frame, app_instance, EXTENSION_NB_COLUMN):
    def save_example(toml_file_path: Path):
        file_path = filedialog.asksaveasfilename(
            initialfile=toml_file_path.name,
            defaultextension=".toml",
            filetypes=[("TOML File", "*.toml"), ("All Files", "*.*")],
            title="Save example as",
        )
        if file_path:
            with open(toml_file_path, "r", encoding="utf-8") as file:
                config_string = file.read()

            with open(file_path, "w", encoding="utf-8") as f:
                f.write(config_string)

    export_exmaples = [
        ExportExampleData(app_instance.EXTENSION_RESOURCES_PATH / "via_design_rf.png", app_instance.EXTENSION_RESOURCES_PATH / "pcb_rf.toml"),
        ExportExampleData(app_instance.EXTENSION_RESOURCES_PATH / "via_design_pcb_diff.png",
                          app_instance.EXTENSION_RESOURCES_PATH / "pcb_diff.toml"),
        ExportExampleData(
            app_instance.EXTENSION_RESOURCES_PATH / "via_design_pkg_diff.png", app_instance.EXTENSION_RESOURCES_PATH / "package_diff.toml"
        ),
    ]

    row = 0
    column = 0
    for example in export_exmaples:
        img = PIL.Image.open(example.picture_path)
        img = img.resize((100, 100))
        photo = PIL.ImageTk.PhotoImage(img, master=frame)

        example_name = example.toml_file_path.stem
        button = ttk.Button(
            frame,
            command=partial(save_example, example.toml_file_path),
            style="PyAEDT.TButton",
            image=photo,
            width=20,
            name=f"button_{example_name}",
        )
        # NOTE: Setting button.image ensures that a reference to the photo is kept and that
        # the picture is correctly rendered in the tkinter window
        button.image = photo
        button.grid(row=row, column=column, **DEFAULT_PADDING)

        if column > EXTENSION_NB_COLUMN:
            row += 1
            column = 0
        else:
            column += 1

    lower_frame = ttk.Frame(app_instance.root, style="PyAEDT.TFrame")
    lower_frame.grid(row=2, column=0, columnspan=EXTENSION_NB_COLUMN)

    create_design_button = ttk.Button(
        lower_frame,
        text="Create Design",
        command=app_instance.create_design,
        style="PyAEDT.TButton",
        width=20,
        name="button_create_design",
    )
    create_design_button.grid(row=0, column=0, sticky="w", **DEFAULT_PADDING)
    change_theme_button = ttk.Button(
        lower_frame,
        width=20,
        text=SUN,
        command=app_instance.toggle_theme,
        style="PyAEDT.TButton",
        name="theme_toggle_button",
    )
    change_theme_button.grid(row=0, column=1)