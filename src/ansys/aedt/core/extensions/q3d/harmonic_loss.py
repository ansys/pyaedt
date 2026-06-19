# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 - 2026 Synopsys, Inc. and ANSYS, Inc. All rights reserved.
# SPDX-License-Identifier: MIT
#
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

from dataclasses import asdict
from dataclasses import dataclass
import os
from pathlib import Path
import tkinter as tk
from tkinter import filedialog
from tkinter import ttk

import pandas as pd

import ansys.aedt.core
from ansys.aedt.core.extensions.misc import ExtensionCommonData
from ansys.aedt.core.extensions.misc import ExtensionProjectCommon
from ansys.aedt.core.extensions.misc import ExtensionQ3DCommon
from ansys.aedt.core.extensions.misc import get_aedt_version
from ansys.aedt.core.extensions.misc import get_arguments
from ansys.aedt.core.extensions.misc import get_port
from ansys.aedt.core.extensions.misc import get_process_id
from ansys.aedt.core.extensions.misc import is_student
from ansys.aedt.core.generic.design_types import get_pyaedt_app
from ansys.aedt.core.internal.errors import AEDTRuntimeError

PORT = get_port()
VERSION = get_aedt_version()
AEDT_PROCESS_ID = get_process_id()
IS_STUDENT = is_student()

EXTENSION_DEFAULT_ARGUMENTS = {"csv_path": "", "threshold": 0.0}
EXTENSION_TITLE = "Excitations setup for Harmonic Loss in Q3D"

result = None


@dataclass
class ExtensionData(ExtensionCommonData):
    """Data class containing user input."""

    csv_path: str = EXTENSION_DEFAULT_ARGUMENTS["csv_path"]
    threshold: float = EXTENSION_DEFAULT_ARGUMENTS["threshold"]


class HarmonicLossExtension(ExtensionQ3DCommon):
    """Extension to configure source excitations for harmonic loss analysis in Q3D."""

    def __init__(self, withdraw: bool = False) -> None:
        super().__init__(
            EXTENSION_TITLE,
            withdraw=withdraw,
            add_custom_content=True,
            toggle_row=6,
            toggle_column=2,
        )

    def show_pictures_popup(self) -> None:
        popup = tk.Toplevel(self.root)
        popup.title("Coil Parameters")
        popup.configure(bg=self.theme.light["pane_bg"])

        container = ttk.Frame(popup, padding=12)
        container.pack(fill="both", expand=True)

        explanation = (
            "Use these reference images to check the format of the CSV file.\n"
            "Match your CSV file with the reference images before applying the filter."
        )
        ttk.Label(
            container,
            text=explanation,
            style="PyAEDT.TLabel",
            justify="left",
            wraplength=700,
        ).pack(anchor="w", pady=(0, 10))

        images_dir = Path(__file__).parent / "images" / "large"
        image_files = ["[...].png", "[...].png"]

        popup._images = []
        for image_name in image_files:
            image_path = images_dir / image_name
            if image_path.exists():
                tk_image = tk.PhotoImage(file=image_path)
                popup._images.append(tk_image)
                tk.Label(
                    container,
                    image=tk_image,
                    background=self.theme.light["pane_bg"],
                ).pack(anchor="w", pady=5)
            else:
                ttk.Label(
                    container,
                    text=f"Image not found: {image_name}",
                    style="PyAEDT.TLabel",
                ).pack(anchor="w", pady=2)

    def add_extension_content(self) -> None:
        """Add custom content to the extension UI."""
        # Browse file entry - CSV file path
        browse_file_label = ttk.Label(self.root, text="Browse CSV File:", width=20, style="PyAEDT.TLabel")
        browse_file_label.grid(row=0, column=0, pady=10)
        browse_file_entry = tk.Text(self.root, width=40, height=1, name="browse_file_entry")
        browse_file_entry.grid(row=0, column=1, pady=15, padx=10)
        browse_file_entry.configure(
            background=self.theme.light["pane_bg"], foreground=self.theme.light["text"], font=self.theme.default_font
        )

        # Threshold entry
        threshold_label = ttk.Label(self.root, text="Current Threshold:", width=20, style="PyAEDT.TLabel")
        threshold_label.grid(row=1, column=0, padx=15, pady=10)
        threshold_entry = tk.Text(self.root, width=40, height=1, name="threshold_entry")
        threshold_entry.grid(row=1, column=1, pady=15, padx=10)
        threshold_entry.configure(
            background=self.theme.light["pane_bg"], foreground=self.theme.light["text"], font=self.theme.default_font
        )

        def callback(extension: HarmonicLossExtension) -> None:
            data = ExtensionData(
                csv_path=browse_file_entry.get("1.0", tk.END).strip(),
                threshold=float(threshold_entry.get("1.0", tk.END).strip() or 0.0),
            )
            extension.data = data
            self.root.destroy()

        def browse_files() -> None:
            global result
            filename = filedialog.askopenfilename(
                initialdir="/",
                title="Select a CSV File",
                filetypes=(("CSV", ".csv"), ("all files", "*.*")),
            )
            browse_file_entry.insert(tk.END, filename)
            result = ExtensionData(csv_path=browse_file_entry.get("1.0", tk.END).strip())

        # Create button to browse an AEDT file
        browse_button = ttk.Button(
            self.root, text="...", command=browse_files, width=10, style="PyAEDT.TButton", name="browse_button"
        )
        browse_button.grid(row=0, column=2, pady=10, padx=15)

        # Filter button, generate dataset and edit sources
        filter_button = ttk.Button(
            self.root, text="Edit Sources", command=lambda: callback(self), style="PyAEDT.TButton", name="create_button"
        )
        filter_button.grid(row=1, column=2, padx=15, pady=10)

        info_button = ttk.Button(
            self.root, text="Requirements", command=self.show_pictures_popup, style="PyAEDT.TButton"
        )
        info_button.grid(row=2, column=1, padx=15, pady=10)


def main(data: ExtensionData) -> bool:
    app = ansys.aedt.core.Desktop(
        new_desktop=False,
        version=VERSION,
        port=PORT,
        aedt_process_id=AEDT_PROCESS_ID,
        student_version=IS_STUDENT,
    )
    active_project = app.active_project()
    active_design = app.active_design()

    if active_project is None:
        raise AEDTRuntimeError(
            "No active project found. Please open or create a project before running this extension."
        )

    project_name = active_project.GetName()
    if active_design.GetDesignType() == "HFSS 3D Layout Design":
        design_name = active_design.GetDesignName()
    else:
        design_name = active_design.GetName()
    aedtapp = get_pyaedt_app(project_name, design_name)

    if not aedtapp.boundaries_by_type["Source"]:
        raise AEDTRuntimeError("No sources in the active design.")

    sources = [source.name for source in aedtapp.boundaries_by_type["Source"]]

    q3d_sources_unfiltered = pd.read_csv(data.csv_path, sep=",")

    # Delete a row if and only if both re and im are below the threshold value for all sources at that frequency.
    # Build per-source masks where True indicates that both parts of the source are below the threshold for that row.

    df = q3d_sources_unfiltered.copy()
    src_masks = []
    for source in sources:
        col_re = f"re({source}.I) [A]"
        col_im = f"im({source}.I) [A]"
        re_vals = pd.to_numeric(df[col_re], errors="coerce").abs()
        im_vals = pd.to_numeric(df[col_im], errors="coerce").abs()
        src_masks.append((re_vals < data.threshold) & (im_vals < data.threshold))

    # A row is removed only if every source mask is True for that row
    rows_all_small = pd.concat(src_masks, axis=1).all(axis=1) if src_masks else pd.Series(False, index=df.index)
    q3d_sources_filtered = df[~rows_all_small]

    # Save filtered data back to a new CSV file

    q3d_sources_filtered_path = Path(aedtapp.working_directory) / "Q3D_sources_filtered.csv"
    q3d_sources_filtered.to_csv(q3d_sources_filtered_path, sep=",", index=False)

    # Save real and imaginary part in separate tab-separated files
    # Each .tab file will contain two columns: frequency and the corresponding part (real or imaginary)
    # After exporting, import each .tab file as a dataset 1D in Q3D

    freq_column = q3d_sources_filtered.columns[0]

    for col in q3d_sources_filtered.columns[1:]:
        # Save the DataFrame as a tab-separated file
        new_file_name = Path(aedtapp.working_directory) / f"{col}.tab"
        q3d_sources_filtered[[freq_column, col]].to_csv(new_file_name, sep="\t", index=False)

        # Determine dataset name and import it
        if col.split("(")[0] == "re":
            dataset_name = f"re_{col.split('(')[1].split('.')[0]}"
        elif col.split("(")[0] == "im":
            dataset_name = f"im_{col.split('(')[1].split('.')[0]}"
        aedtapp.import_dataset1d(str(new_file_name), name=dataset_name, is_project_dataset=False)

    # ## Q3D: Harmonic loss setup
    #
    # Specify real and imaginary currents for each source to compute harmonic loss.

    harmonic_loss = {}
    for source in sources:
        re_dataset_name = next(d for d in list(aedtapp.design_datasets.keys()) if source in d and "re" in d.lower())
        im_dataset_name = next(d for d in list(aedtapp.design_datasets.keys()) if source in d and "im" in d.lower())
        harmonic_loss[source] = (re_dataset_name, im_dataset_name)
    aedtapp.edit_sources(harmonic_loss=harmonic_loss)

    if "PYTEST_CURRENT_TEST" not in os.environ:
        app.release_desktop(False, False)
    return True


if __name__ == "__main__":
    args = get_arguments(EXTENSION_DEFAULT_ARGUMENTS, EXTENSION_TITLE)

    # Open UI
    if not args["is_batch"]:  # pragma: no cover
        extension: ExtensionProjectCommon = HarmonicLossExtension(withdraw=False)

        tk.mainloop()

        if result:
            args.update(asdict(result))
            main(args)
    else:
        main(args)
