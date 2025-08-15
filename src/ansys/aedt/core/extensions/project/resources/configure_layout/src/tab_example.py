import json
import os
import tempfile


from pathlib import Path
from tkinter import ttk, filedialog, messagebox

from ansys.aedt.core.extensions.project.resources.configure_layout.src.template import SERDES_CONFIG
from ansys.aedt.core.examples.downloads import download_file


def create_tab_example(tab_frame, master):
    ttk.Button(
        tab_frame,
        name="load_example_board",
        text="Load Example Board",
        command=lambda :call_back_load_example_board(master),
        style="PyAEDT.TButton",
        width=30,
    ).pack(expand=True, padx=5, pady=5, side="left", anchor="nw")

    ttk.Button(
        tab_frame,
        name="export_example_config",
        text="Export Example Config",
        command=call_back_export_template,
        style="PyAEDT.TButton",
        width=30,
    ).pack(expand=True, padx=5, pady=5, side="right", anchor="ne")


def call_back_load_example_board(master, test_folder=None):
    temp_dir = tempfile.TemporaryDirectory(suffix=".ansys", dir=test_folder).name
    Path(temp_dir).mkdir()
    example_edb = download_file(source="edb/ANSYS_SVP_V1_1.aedb", local_path=temp_dir)
    master.load_edb_into_hfss3dlayout(example_edb)


def call_back_export_template():
    file = filedialog.asksaveasfilename(
        initialfile="serdes_config.json",
        defaultextension=".json", filetypes=[("JSON files", "*.json")]
    )
    if not file:  # pragma: no cover
        return
    file = Path(file)
    with open(file, "w", encoding="utf-8") as f:
        json.dump(SERDES_CONFIG, f, indent=2)
    if "PYTEST_CURRENT_TEST" not in os.environ:  # pragma: no cover
        messagebox.showinfo("Message", "Template file exported successfully.")