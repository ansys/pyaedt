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

import logging
from pathlib import Path
import re
import shutil
from typing import Union
import warnings

from ansys.aedt.core.generic.file_utils import read_csv
from ansys.aedt.core.generic.general_methods import pyaedt_function_handler
from ansys.aedt.core.internal.errors import AEDTRuntimeError


@pyaedt_function_handler()
def read_info_fromcsv(projdir, name):  # pragma: no cover
    """Read information from a CSV file and return a list.

    .. deprecated:: 0.15.1
        This method is deprecated. Use the ``ansys.aedt.core.generic.file_utils.read_csv`` method instead.

    Parameters
    ----------
    projdir : str
        Full path to the file.
    name : str
        Name of the file.

    Returns
    -------
    list

    """
    warnings.warn(
        "`read_info_fromcsv` is deprecated. Use `ansys.aedt.core.generic.file_utils.read_csv` instead.",
        DeprecationWarning,
    )
    # Construct the filename using pathlib.
    filename = str(Path(projdir) / name)
    return read_csv(filename)


@pyaedt_function_handler(dir="input_dir")
def clean_proj_folder(input_dir):  # pragma: no cover
    """Delete all project name-related folders.

    .. deprecated:: 0.15.1
        This method is deprecated. Use the ``ansys.aedt.core.application.clean_proj_folder`` method instead.

    Parameters
    ----------
    input_dir : str or :class:`pathlib.Path`
        Full path to the project directory.

    Returns
    -------
    bool
        ``True`` when successful, ``False`` when failed.
    """
    warnings.warn(
        "`clean_proj_folder` is deprecated. Use `ansys.aedt.core.application.clean_proj_folder` instead.",
        DeprecationWarning,
    )
    input_dir_path = Path(input_dir)
    if input_dir_path.exists():
        shutil.rmtree(input_dir_path, True)
    input_dir_path.mkdir()
    return True


@pyaedt_function_handler(ProjectDir="input_dir")
def create_output_folder(input_dir: Union[str, Path]) -> tuple:
    """Create the output folders starting from the project directory.

    Parameters
    ----------
    input_dir : str or :class:`pathlib.Path`
        Name of the project directory.

    Returns
    -------
    tuple
        Picture path, Results path

    """
    warnings.warn(
        "`create_output_folder` is deprecated.",
        DeprecationWarning,
    )
    npath = Path(input_dir)
    base = npath.name

    # Set pathnames for the output folders.
    output_path = npath / base
    picture_path = output_path / "Pictures"
    results_path = output_path / "Results"

    # Create directories using a loop.
    for directory in [output_path, picture_path, results_path]:
        directory.mkdir(parents=True, exist_ok=True)
    return str(picture_path), str(results_path)


@pyaedt_function_handler(origfile="input_file", solid_list="assignment")
def change_objects_visibility(input_file: Union[str, Path], assignment: list) -> bool:
    """Edit the project file to make only the solids that are specified visible.

    Parameters
    ----------
    input_file : str or :class:`pathlib.Path`
        Full path to the project file, which has an ``.aedt`` extension.
    assignment : list
        List of names for the solid to make visible. All other solids are hidden.

    Returns
    -------
    bool
        ``True`` when successful, ``False`` when failed.
    """
    path = Path(input_file).parent
    newfile = path / "aedttmp.tmp"

    if not (Path(input_file).with_suffix(".lock")).is_file():  # check if the project is closed
        try:
            # Using text mode with explicit encoding instead of binary mode.
            with open(str(input_file), "rb") as f, open(str(newfile), "wb") as n:
                # Reading file content
                content = f.read()
                # Searching file content for pattern
                search_str = r"(\$begin 'EditorWindow'\n.+)(Drawings\[.+\])(.+\n\s*\$end 'EditorWindow')"
                # Replacing string
                view_str = "Drawings[" + str(len(assignment)) + ": " + str(assignment).strip("[")
                sub_str = r"\1" + view_str + r"\3"
                s = re.sub(search_str.encode("utf-8"), sub_str.encode("utf-8"), content)
                # Writing file content
                n.write(s)
            # Renaming files and deleting temporary file
            Path(input_file).unlink()
            newfile.rename(input_file)
            return True
        except Exception:  # pragma: no cover
            # Cleanup temporary file if exists.
            newfile.unlink(missing_ok=True)
            raise AEDTRuntimeError("Failed to restrict visibility to specified solids.")

    else:  # pragma: no cover
        logging.error("change_objects_visibility: Project %s is still locked.", str(input_file))
        return False


@pyaedt_function_handler(origfile="input_file")
def change_model_orientation(input_file: Union[str, Path], bottom_dir: str) -> bool:
    """Edit the project file to change the model orientation.

    Parameters
    ----------
    input_file : str or :class:`pathlib.Path`
        Full path to the project file, which has an ``.aedt`` extension.
    bottom_dir : str
        Bottom direction as specified in the properties file.

    Returns
    -------
    bool
        ``True`` when successful, ``False`` when failed.
    """
    input_path = Path(input_file)
    newfile = input_path.parent / "aedttmp.tmp"
    lock_file = input_path.with_suffix(".aedt.lock")

    # Directory of u, v vectors for view orientation
    orientation = {
        "+X": "OrientationMatrix(0, -0.816496610641479, -0.577350318431854, 0, 0.70710676908493, -0.40824830532074, "
        "0.577350318431854, 0, -0.70710676908493, -0.40824830532074, 0.577350318431854, 0, 0, 0, 0, 1, 0, -100, "
        "100, -100, 100, -100, 100)",
        "+Y": "OrientationMatrix(-0.70710688829422, -0.408248245716095, 0.577350199222565, 0, 1.04308128356934e-07, "
        "-0.816496670246124, -0.577350199222565, 0, 0.707106709480286, -0.408248245716095, 0.577350437641144, "
        "0, 0, 0, 0, 1, 0, -100, 100, -100, 100, -100, 100)",
        "+Z": "OrientationMatrix(0.70710676908493, -0.408248394727707, 0.577350199222565, 0, -0.70710676908493, "
        "-0.408248394727707, 0.577350199222565, 0, 0, -0.81649649143219, -0.577350437641144, 0, 0, 0, 0, 1, 0, "
        "-100, 100, -100, 100, -100, 100)",
        "-X": "OrientationMatrix(0, 0.816496610641479, 0.577350318431854, 0, -0.70710676908493, -0.40824830532074, "
        "0.577350318431854, 0, 0.70710676908493, -0.40824830532074, 0.577350318431854, 0, 0, 0, -0, 1, 0, -100, "
        "100, -100, 100, -100, 100)",
        "-Y": "OrientationMatrix(0.70710688829422, -0.408248245716095, 0.577350199222565, 0, 1.04308128356934e-07, "
        "0.816496670246124, 0.577350199222565, 0, -0.707106709480286, -0.408248245716095, 0.577350437641144, 0, "
        "0, 0, -0, 1, 0, -100, 100, -100, 100, -100, 100)",
        "-Z": "OrientationMatrix(-0.70710676908493, -0.408248394727707, 0.577350199222565, 0, 0.70710676908493, "
        "-0.408248394727707, 0.577350199222565, 0, 0, 0.81649649143219, 0.577350437641144, 0, 0, 0, -0, 1, 0, "
        "-100, 100, -100, 100, -100, 100) ",
    }

    if lock_file.exists():  # pragma: no cover
        logging.error(f"change_model_orientation: Project {input_file} is still locked.")
        return False

    try:
        with input_path.open("rb") as f, newfile.open("wb") as n:
            content = f.read()
            search_str = r"(\\$begin 'EditorWindow'\\n.+?)(OrientationMatrix\\(.+?\\))(.+\\n\\s*\\$end 'EditorWindow')"
            # Replacing string
            orientation_str = orientation[bottom_dir]
            sub_str = r"\1" + orientation_str + r"\3"
            s = re.sub(search_str.encode("utf-8"), sub_str.encode("utf-8"), content)
            # Writing file content
            n.write(s)
        input_path.unlink()
        newfile.rename(input_path)
        return True
    except Exception as e:  # pragma: no cover
        newfile.unlink(missing_ok=True)
        raise AEDTRuntimeError(f"change_model_orientation: Error encountered - {e}")
