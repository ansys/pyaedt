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

import csv
from dataclasses import dataclass
from dataclasses import field
import os
from pathlib import Path
import tkinter
from tkinter import filedialog
from tkinter import ttk
from typing import Optional

import ansys.aedt.core
from ansys.aedt.core import Icepak
import ansys.aedt.core.extensions
from ansys.aedt.core.extensions.misc import DEFAULT_PADDING
from ansys.aedt.core.extensions.misc import ExtensionCommonData
from ansys.aedt.core.extensions.misc import ExtensionIcepakCommon
from ansys.aedt.core.extensions.misc import get_aedt_version
from ansys.aedt.core.extensions.misc import get_arguments
from ansys.aedt.core.extensions.misc import get_port
from ansys.aedt.core.extensions.misc import get_process_id
from ansys.aedt.core.extensions.misc import is_student
from ansys.aedt.core.internal.errors import AEDTRuntimeError

PORT = get_port()
VERSION = get_aedt_version()
AEDT_PROCESS_ID = get_process_id()
IS_STUDENT = is_student()
EXTENSION_DEFAULT_ARGUMENTS = {
    "file_path": "",
    "geometric_info": [],
    "source_value_info": {},
    "source_unit_info": {},
}
EXTENSION_TITLE = "Power map from file"
EXTENSION_NB_ROW = 2
EXTENSION_NB_COLUMN = 3
FILE_PATH_ERROR_MSG = "Please select an existing CSV file before creating a power map."
DESIGN_TYPE_ERROR_MSG = "An Icepak design is needed for this extension."
PARSING_ERROR_MSG = "Missing information in the CSV file. Please provide both geometric and source data."


class IcepakCSVFormatError(AEDTRuntimeError):
    """Raised when the CSV file does not follow the expected Icepak classic format."""


@dataclass
class PowerMapFromCSVExtensionData(ExtensionCommonData):
    """Data class containing user input and computed data."""

    file_path: Optional[Path] = None
    geometric_info: list = field(default_factory=list)
    source_value_info: dict = field(default_factory=dict)
    source_unit_info: dict = field(default_factory=dict)


class PowerMapFromCSVExtension(ExtensionIcepakCommon):
    """Class to create a cutout in an HFSS 3D Layout design."""

    def __init__(self, withdraw: bool = False):
        # Initialize the common extension class with the title and theme color
        super().__init__(
            EXTENSION_TITLE,
            theme_color="light",
            withdraw=withdraw,
            add_custom_content=False,
        )
        self.data: PowerMapFromCSVExtensionData = PowerMapFromCSVExtensionData()
        self.add_extension_content()

    def browse_file(self):
        filename = filedialog.askopenfilename(
            initialdir="/",
            title="Select CSV file",
            filetypes=(("Power map", "*.csv*"), ("all files", "*.*")),
        )
        entry = self._widgets["browse_file_entry"]
        entry.config(state="normal")
        entry.delete(0, tkinter.END)
        entry.insert(0, filename)
        entry.config(state="readonly")
        self.data.file_path = Path(filename)

    def add_extension_content(self):
        """Add custom content to the extension UI."""
        upper_frame = ttk.Frame(self.root, style="PyAEDT.TFrame")
        upper_frame.grid(row=0, column=0, columnspan=EXTENSION_NB_COLUMN)

        label = ttk.Label(upper_frame, text="Selected file:", style="PyAEDT.TLabel")
        label.grid(row=0, column=0, **DEFAULT_PADDING)

        entry = tkinter.Entry(upper_frame, width=50, state="readonly")
        entry.grid(row=0, column=1, **DEFAULT_PADDING)
        self._widgets["browse_file_entry"] = entry

        lower_frame = ttk.Frame(self.root, style="PyAEDT.TFrame")
        lower_frame.grid(row=1, column=0, columnspan=EXTENSION_NB_COLUMN)

        browse_button = ttk.Button(
            lower_frame, text="Browse", command=lambda: self.browse_file(), style="PyAEDT.TButton"
        )
        browse_button.grid(row=0, column=0, **DEFAULT_PADDING)
        self._widgets["browse_file_button"] = browse_button

        create_button = ttk.Button(
            lower_frame, text="Create", command=lambda: self.__parse_data(), style="PyAEDT.TButton"
        )
        create_button.grid(row=0, column=1, **DEFAULT_PADDING)
        self._widgets["create_button"] = create_button

        self.add_toggle_theme_button(lower_frame, 0, 2)

    def __parse_data(self):
        """Parse source and geometric data from the CSV file."""
        if self.data.file_path is None or not self.data.file_path.is_file():
            raise AEDTRuntimeError(FILE_PATH_ERROR_MSG)
        geometric_info, source_value_info, source_unit_info = extract_info(self.data.file_path)
        self.data.geometric_info = geometric_info
        self.data.source_value_info = source_value_info
        self.data.source_unit_info = source_unit_info
        self.root.destroy()


def create_powermaps_from_csv(ipk, csv_path: Path):
    """Create powermap from an Icepak classic CSV file.

    Parameters
    ----------
    csv_path : Path
        The file path to the CSV file to be processed.
    """
    geometric_info, source_value_info, source_unit_info = extract_info(csv_path)
    data = PowerMapFromCSVExtensionData(
        file_path=csv_path,
        geometric_info=geometric_info,
        source_value_info=source_value_info,
        source_unit_info=source_unit_info,
    )
    create_powermaps_from_data(ipk, data)


def create_powermaps_from_data(ipk, data: PowerMapFromCSVExtensionData):
    """Create power maps from geometric and source information.

    Parameters
    ----------
    ipk : Icepak
    data : PowerMapFromCSVExtensionData
        The data containing the file path and other information.
    """
    for info in data.geometric_info:
        name = info["name"]
        points = []
        for vertex in info["vertices"]:
            if not vertex == "":
                x = vertex.split()[0] + "m"
                y = vertex.split()[1] + "m"
                z = vertex.split()[2] + "m"
                points.append([x, y, z])
        # Add first point at the end of list
        points.append(points[0])
        sanitized_name = name.replace(".", "_")
        ipk.logger.info(f"Creating 2d object {sanitized_name}.")
        polygon = ipk.modeler.create_polyline(points, name=sanitized_name)
        ipk.logger.info("Polygon created.")
        ipk.modeler.cover_lines(polygon)
        power = data.source_value_info[name] + data.source_unit_info[name]
        ipk.logger.info(f"Assigning power value {power}")
        ipk.assign_source(polygon.name, "Total Power", power)
        ipk.logger.info("Power value assigned.")


def extract_info(csv_file: Path) -> tuple[list, dict, dict]:
    """Extract source and geometric information from an Icepak classic CSV file.

    Parameters
    ----------
    csv_file: Path
        The path to the CSV file to be processed.

    Returns
    -------
    geometric_info : list
        A list of dictionaries, each containing:
            - "name": The name of the geometric object.
            - "vertices": A list of vertex coordinates.
    source_value_info: dict
        A dictionary mapping geometric object to its power value.
    source_unit_info: dict
        A dictionary mapping geometric object to its power unit.

    """

    def safe_skip(reader, n):
        """Skip up to n lines, ignoring StopIteration."""
        for _ in range(n):
            try:
                next(reader)
            except StopIteration:
                break

    # Initialize lists to store the extracted information
    geometric_info = []
    source_value_info = {}
    source_unit_info = {}

    with csv_file.open("r") as file:
        reader = csv.reader(file)

        # Skip the first three header lines
        safe_skip(reader, 3)

        # Read the source information lines until an empty line
        try:
            for line in reader:
                if not line or line[0] == "":
                    break
                source_value_info[line[0]] = line[1]
                source_unit_info[line[0]] = line[2]
        except IndexError as e:
            raise IcepakCSVFormatError("CSV file does not follow the expected Icepak classic format.") from e

        if not source_value_info and not source_unit_info:
            raise IcepakCSVFormatError(PARSING_ERROR_MSG)

        # Skip the next three lines
        safe_skip(reader, 3)

        # Read the geometric information
        for line in reader:
            if line and line[0]:
                geometric_info.append({"name": line[0], "vertices": line[10:]})

        if not geometric_info:
            raise IcepakCSVFormatError(PARSING_ERROR_MSG)

        return geometric_info, source_value_info, source_unit_info


def main(data: PowerMapFromCSVExtensionData):
    """Main function to execute the cutout operation."""
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

    if active_design.GetDesignType() == "Icepak":
        design_name = active_design.GetName()
    else:  # pragma: no cover
        raise AEDTRuntimeError(DESIGN_TYPE_ERROR_MSG)

    ipk = Icepak(project_name, design_name)

    if data.source_value_info and data.source_unit_info and data.geometric_info:
        create_powermaps_from_data(ipk, data)
    # NOTE: This is mainly used for direct call from the command line.
    elif data.file_path and data.file_path.is_file():
        create_powermaps_from_csv(ipk, data.file_path)
    else:
        raise AEDTRuntimeError(FILE_PATH_ERROR_MSG)

    if "PYTEST_CURRENT_TEST" not in os.environ:
        app.logger.info("Power maps created successfully.")
        app.release_desktop(False, False)
    return True


if __name__ == "__main__":  # pragma: no cover
    args = get_arguments(EXTENSION_DEFAULT_ARGUMENTS, EXTENSION_TITLE)

    # Open UI
    if not args["is_batch"]:
        extension = PowerMapFromCSVExtension(withdraw=False)

        tkinter.mainloop()

        main(extension.data)
    else:
        data = PowerMapFromCSVExtensionData()
        for key, value in args.items():
            setattr(data, key, value)
        main(data)
