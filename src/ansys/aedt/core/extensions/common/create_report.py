# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 - 2025 ANSYS, Inc. and/or its affiliates.
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

from dataclasses import dataclass
import os
from pathlib import Path
import tkinter
from tkinter import filedialog
from tkinter import ttk
import webbrowser

import ansys.aedt.core
from ansys.aedt.core import get_pyaedt_app
from ansys.aedt.core.extensions.misc import DEFAULT_PADDING
from ansys.aedt.core.extensions.misc import ExtensionCommonData
from ansys.aedt.core.extensions.misc import ExtensionProjectCommon
from ansys.aedt.core.extensions.misc import get_aedt_version
from ansys.aedt.core.extensions.misc import get_port
from ansys.aedt.core.extensions.misc import get_process_id
from ansys.aedt.core.extensions.misc import is_student
from ansys.aedt.core.generic.general_methods import is_windows
from ansys.aedt.core.internal.errors import AEDTRuntimeError
from ansys.aedt.core.visualization.plot.pdf import AnsysReport

PORT = get_port()
VERSION = get_aedt_version()
AEDT_PROCESS_ID = get_process_id()
IS_STUDENT = is_student()

# Extension batch arguments
EXTENSION_DEFAULT_ARGUMENTS = {
    "report_name": "CustomReport",
    "open_report": True,
    "save_path": "",
}
EXTENSION_TITLE = "Create Report"


@dataclass
class CreateReportExtensionData(ExtensionCommonData):
    """Data class containing user input and computed data."""

    report_name: str = EXTENSION_DEFAULT_ARGUMENTS["report_name"]
    open_report: bool = EXTENSION_DEFAULT_ARGUMENTS["open_report"]
    save_path: str = EXTENSION_DEFAULT_ARGUMENTS["save_path"]


class CreateReportExtension(ExtensionProjectCommon):
    """Extension for creating PDF reports in AEDT."""

    def __init__(self, withdraw: bool = False):
        # Initialize the common extension class with title and
        # theme color
        super().__init__(
            EXTENSION_TITLE,
            theme_color="light",
            withdraw=withdraw,
            add_custom_content=True,
            toggle_row=3,
            toggle_column=1,
        )

        # Initialize widget storage
        self._widgets["report_name_entry"] = None
        self._widgets["open_report_var"] = None
        self._widgets["save_path_entry"] = None
        self.data: CreateReportExtensionData = CreateReportExtensionData()
        self.generate_clicked = False  # Track if generate button was clicked
        self.add_extension_content()

    def add_extension_content(self):
        """Add custom content to the extension UI."""
        # Report name entry
        report_name_label = ttk.Label(
            self.root,
            text="Report name:",
            width=30,
            style="PyAEDT.TLabel",
        )
        report_name_label.grid(row=0, column=0)
        self._widgets["report_name_entry"] = tkinter.Text(self.root, width=30, height=1)
        self._widgets["report_name_entry"].insert(tkinter.END, "CustomReport")
        self._widgets["report_name_entry"].grid(row=0, column=1, **DEFAULT_PADDING)

        # Save path selection
        save_path_label = ttk.Label(
            self.root,
            text="Save location:",
            width=30,
            style="PyAEDT.TLabel",
        )
        save_path_label.grid(row=1, column=0, **DEFAULT_PADDING)

        save_path_frame = ttk.Frame(self.root, style="PyAEDT.TFrame")
        save_path_frame.grid(
            row=1,
            column=1,
            pady=10,
            padx=10,
            sticky="ew",
        )

        self._widgets["save_path_entry"] = tkinter.Text(save_path_frame, width=24, height=1)
        self._widgets["save_path_entry"].insert(tkinter.END, "")
        self._widgets["save_path_entry"].grid(row=0, column=0, padx=(0, 5))

        def browse_folder():
            folder_path = filedialog.askdirectory(title="Select folder to save report")
            if folder_path:
                self._widgets["save_path_entry"].delete("1.0", tkinter.END)
                self._widgets["save_path_entry"].insert(tkinter.END, folder_path)

        browse_button = ttk.Button(
            save_path_frame,
            text="Browse",
            width=8,
            command=browse_folder,
            style="PyAEDT.TButton",
        )
        browse_button.grid(row=0, column=1)

        # Open report checkbox
        self._widgets["open_report_var"] = tkinter.BooleanVar(value=True)
        open_report_checkbox = ttk.Checkbutton(
            self.root,
            text="Open report after generation",
            variable=self._widgets["open_report_var"],
            style="PyAEDT.TCheckbutton",
        )
        open_report_checkbox.grid(row=2, column=0, columnspan=2, **DEFAULT_PADDING)

        def callback(extension: CreateReportExtension):
            extension.data = CreateReportExtensionData(
                report_name=self._widgets["report_name_entry"].get("1.0", tkinter.END).strip(),
                open_report=self._widgets["open_report_var"].get(),
                save_path=self._widgets["save_path_entry"].get("1.0", tkinter.END).strip(),
            )
            extension.generate_clicked = True
            extension.root.destroy()

        ok_button = ttk.Button(
            self.root,
            text="Generate Report",
            width=20,
            command=lambda: callback(self),
            style="PyAEDT.TButton",
            name="generate",
        )
        ok_button.grid(row=3, column=0, **DEFAULT_PADDING)


def main(data: CreateReportExtensionData):
    """Main function to run the create report extension."""
    if not data.report_name:
        raise AEDTRuntimeError("Report name cannot be empty.")

    app = ansys.aedt.core.Desktop(
        new_desktop=False,
        version=VERSION,
        port=PORT,
        aedt_process_id=AEDT_PROCESS_ID,
        student_version=IS_STUDENT,
    )

    active_project = app.active_project()
    active_design = app.active_design()

    project_name = active_project.GetName()
    design_name = active_design.GetName()

    if active_design.GetDesignType() in [
        "HFSS 3D Layout Design",
        "Circuit Design",
    ]:
        design_name = None
    aedtapp = get_pyaedt_app(project_name, design_name)

    report = AnsysReport(
        version=app.aedt_version_id,
        design_name=aedtapp.design_name,
        project_name=aedtapp.project_name,
    )
    report.create()
    report.add_section()
    report.add_chapter(f"{aedtapp.solution_type} Results")
    report.add_sub_chapter("Plots")
    report.add_text("This section contains all reports results.")

    for plot in aedtapp.post.plots:
        aedtapp.post.export_report_to_jpg(aedtapp.working_directory, plot.plot_name)
        image_path = Path(aedtapp.working_directory) / f"{plot.plot_name}.jpg"
        report.add_image(image_path, plot.plot_name)
        report.add_page_break()

    report.add_toc()

    # Determine the save directory
    save_directory = data.save_path if data.save_path else aedtapp.working_directory

    pdf_path = report.save_pdf(save_directory, f"{data.report_name}.pdf")
    aedtapp.logger.info(f"Report Generated. {pdf_path}")

    if is_windows and data.open_report:
        try:
            pdf_file = Path(pdf_path)
            if (
                pdf_file.is_file() and pdf_file.suffix == ".pdf" and "PYTEST_CURRENT_TEST" not in os.environ
            ):  # pragma: no cover:
                webbrowser.open(pdf_path)  # nosec
        except Exception:
            aedtapp.logger.warning(f"Failed to open {pdf_path}")

    if "PYTEST_CURRENT_TEST" not in os.environ:  # pragma: no cover
        app.release_desktop(False, False)
    return True


if __name__ == "__main__":  # pragma: no cover
    # Open UI
    extension = CreateReportExtension()
    tkinter.mainloop()
    if extension.data and extension.generate_clicked:
        main(extension.data)
