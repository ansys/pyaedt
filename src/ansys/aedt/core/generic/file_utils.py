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

import codecs
import csv
import fnmatch
import json
import math
import os
from pathlib import Path
import re
import string
import tempfile
from typing import Dict
from typing import List
from typing import TextIO
from typing import Union

from ansys.aedt.core.aedt_logger import pyaedt_logger
from ansys.aedt.core.generic.constants import CSS4_COLORS
from ansys.aedt.core.generic.general_methods import pyaedt_function_handler
from ansys.aedt.core.generic.numbers_utils import Quantity
from ansys.aedt.core.generic.settings import settings
from ansys.aedt.core.internal.aedt_versions import aedt_versions
from ansys.aedt.core.internal.errors import AEDTRuntimeError

is_linux = os.name == "posix"
is_windows = not is_linux


# Path processing
@pyaedt_function_handler(path_in="input_dir")
def normalize_path(input_dir: Union[str, Path], sep: str = None) -> str:
    """Normalize path separators.

    Parameters
    ----------
    input_dir : str or :class:`pathlib.Path`
        Path to normalize.
    sep : str, optional
        Separator.

    Returns
    -------
    str
        Path normalized to new separator.
    """
    path = Path(input_dir)
    if sep:
        return str(path).replace(path.anchor, sep)
    return str(path)


@pyaedt_function_handler(path="input_file")
def get_filename_without_extension(input_file: Union[str, Path]) -> str:
    """Get the filename without its extension.

    Parameters
    ----------
    input_file : str or :class:`pathlib.Path`
        Path of the file.

    Returns
    -------
    str
       Name of the file without extension.
    """
    path = Path(input_file)
    return str(path.stem)


@pyaedt_function_handler(project_path="input_file")
def is_project_locked(input_file: Union[str, Path]) -> bool:
    """Check if the AEDT project lock file exists.

    Parameters
    ----------
    input_file : str or :class:`pathlib.Path`
        Path for the AEDT project.

    Returns
    -------
    bool
        ``True`` when successful, ``False`` when failed.
    """
    input_file = Path(input_file)
    if settings.remote_rpc_session:
        if settings.remote_rpc_session.filemanager.pathexists(str(input_file) + ".lock"):
            return True
        else:
            return False
    return check_if_path_exists(str(input_file) + ".lock")


@pyaedt_function_handler(project_path="input_file")
def remove_project_lock(input_file: Union[str, Path]) -> bool:
    """Check if the AEDT project exists and try to remove the lock file.

    .. note::
       This operation is risky because the file could be opened in another AEDT instance.

    Parameters
    ----------
    input_file : str or :class:`pathlib.Path`
        Path for the AEDT project.

    Returns
    -------
    bool
        ``True`` when successful, ``False`` when failed.
    """
    input_file = Path(input_file)
    input_file_locked = Path(str(input_file) + ".lock")
    if settings.remote_rpc_session and settings.remote_rpc_session.filemanager.pathexists(str(input_file_locked)):
        settings.remote_rpc_session.filemanager.unlink(str(input_file_locked))
        return True
    if input_file_locked.exists():
        input_file_locked.unlink()
    return True


@pyaedt_function_handler()
def check_and_download_file(remote_path: Union[str, Path], overwrite: bool = True) -> str:
    """Check if a file is remote. Download it or return the path.

    Parameters
    ----------
    remote_path : str or :class:`pathlib.Path`
        Path to the remote file.
    overwrite : bool, optional
        Whether to overwrite the file if it already exists locally.
        The default is ``True``.

    Returns
    -------
    str
        Path to the remote file.
    """
    remote_path = Path(remote_path)
    if settings.remote_rpc_session:
        remote_path = _check_path(remote_path)
        local_path = Path(settings.remote_rpc_session_temp_folder) / Path(remote_path).name
        if settings.remote_rpc_session.filemanager.pathexists(remote_path):
            settings.remote_rpc_session.filemanager.download_file(str(remote_path), local_path, overwrite=overwrite)
            return str(local_path)
    return str(remote_path)


@pyaedt_function_handler()
def check_if_path_exists(path: Union[str, Path]) -> bool:
    """Check whether a path exists on a local or on a remote machine (for remote sessions only).

    Parameters
    ----------
    path : str or :class:`pathlib.Path`
        Local or remote path to check.

    Returns
    -------
    bool
        ``True`` when exist, ``False`` when fails.
    """
    path = Path(path)
    if settings.remote_rpc_session:
        return settings.remote_rpc_session.filemanager.pathexists(str(path))
    return path.exists()


@pyaedt_function_handler()
def check_and_download_folder(
    local_path: Union[str, Path], remote_path: Union[str, Path], overwrite: bool = True
) -> str:
    """Download remote folder.

    Parameters
    ----------
    local_path : str or :class:`pathlib.Path`
        Local path to save the folder to.
    remote_path : str or :class:`pathlib.Path`
        Path to the remote folder.
    overwrite : bool, optional
        Whether to overwrite the folder if it already exists locally.
        The default is ``True``.

    Returns
    -------
    str
        Path to the local folder if downloaded, otherwise the remote path.
    """
    local_path = str(local_path)
    remote_path = str(remote_path)

    if settings.remote_rpc_session:
        remote_path = remote_path.replace("\\", "/") if remote_path[0] != "\\" else remote_path
        settings.remote_rpc_session.filemanager.download_folder(remote_path, local_path, overwrite=overwrite)
        return local_path
    return remote_path


@pyaedt_function_handler(rootname="root_name")
def generate_unique_name(root_name: str, suffix: str = "", n: int = 6) -> str:
    """Generate a new name given a root name and optional suffix.

    Parameters
    ----------
    root_name : str
        Root name to add random characters to.
    suffix : string, optional
        Suffix to add. The default is ``''``.
    n : int, optional
        Number of random characters to add to the name. The default value is ``6``.

    Returns
    -------
    str
        Newly generated name.
    """
    alphabet = string.ascii_uppercase + string.digits

    import secrets

    name = "".join(secrets.choice(alphabet) for _ in range(n))

    unique_name = root_name + "_" + name
    if suffix:
        unique_name += "_" + suffix
    return unique_name


@pyaedt_function_handler(rootname="root_name")
def generate_unique_folder_name(root_name: str = None, folder_name: str = None) -> str:
    """Generate a new AEDT folder name given a root name.

    Parameters
    ----------
    root_name : str, optional
        Root name for the new folder. The default is ``None``.
    folder_name : str, optional
        Name for the new AEDT folder if one must be created.

    Returns
    -------
    str
        Newly generated name.
    """
    if not root_name:
        if settings.remote_rpc_session:
            root_name = settings.remote_rpc_session_temp_folder
        else:
            root_name = tempfile.gettempdir()
    if folder_name is None:
        folder_name = generate_unique_name("pyaedt_prj", n=3)
    temp_folder = Path(root_name) / folder_name
    if settings.remote_rpc_session and not settings.remote_rpc_session.filemanager.pathexists(str(temp_folder)):
        settings.remote_rpc_session.filemanager.makedirs(str(temp_folder))
    elif not temp_folder.exists():
        temp_folder.mkdir(parents=True)
    return str(temp_folder)


@pyaedt_function_handler(rootname="root_name")
def generate_unique_project_name(
    root_name: str = None, folder_name: str = None, project_name: str = None, project_format: str = "aedt"
):
    """Generate a new AEDT project name given a root name.

    Parameters
    ----------
    root_name : str, optional
        Root name where the new project is to be created.
    folder_name : str, optional
        Name of the folder to create. The default is ``None``, in which case a random folder
        is created. Use ``""`` if you do not want to create a subfolder.
    project_name : str, optional
        Name for the project. The default is ``None``, in which case a random project is
        created. If a project with this name already exists, a new suffix is added.
    project_format : str, optional
        Project format. The default is ``"aedt"``. Options are ``"aedt"`` and ``"aedb"``.

    Returns
    -------
    str
        Newly generated name.
    """
    if not project_name:
        project_name = generate_unique_name("Project", n=3)
    name_with_ext = project_name + "." + project_format
    folder_path = generate_unique_folder_name(root_name, folder_name=folder_name)
    folder_path = Path(folder_path)
    prj = folder_path / name_with_ext
    while check_if_path_exists(prj):
        name_with_ext = generate_unique_name(project_name, n=3) + "." + project_format
        prj = folder_path / name_with_ext
    return str(prj)


@pyaedt_function_handler()
def available_file_name(full_file_name: Union[str, Path]) -> Path:
    """Provide a file name that doesn't exist.

    If the input file name exists, increment the base
    name and return a valid ``Path`` object with an updated name.

    Parameters
    ----------
    full_file_name : str or :class:`pathlib.Path`
        File to be saved.

    Returns
    -------
    class:`pathlib.Path`
        Valid file name with increment suffix `"_n.ext"`.  If the file doesn't
        exist, the original file name will be returned as a ``Path`` object.
    """
    p = Path(full_file_name)
    candidate = p
    n = 1
    while candidate.exists():
        candidate = candidate.with_name(f"{p.stem}_{n}{p.suffix}")
        n += 1
    return candidate


@pyaedt_function_handler(startpath="path", filepattern="file_pattern")
def recursive_glob(path: Union[str, Path], file_pattern: str):
    """Get a list of files matching a pattern, searching recursively from a start path.

    Parameters
    ----------
    path : str or :class:`pathlib.Path`
        Starting path.
    file_pattern : str
        File pattern to match.

    Returns
    -------
    list
        List of files matching the given pattern.
    """
    path = Path(path)
    if settings.remote_rpc_session:
        files = []
        for i in settings.remote_rpc_session.filemanager.listdir(str(path)):
            input_file = path / i
            if settings.remote_rpc_session.filemanager.isdir(str(input_file)):
                files.extend(recursive_glob(input_file, file_pattern))
            elif fnmatch.fnmatch(i, file_pattern):
                files.append(str(input_file))
        return files
    else:
        return [str(file) for file in Path(path).rglob("*") if fnmatch.fnmatch(file.name, file_pattern)]


@pyaedt_function_handler()
def open_file(
    file_path: Union[str, Path], file_options: str = "r", encoding: str = None, override_existing: bool = True
) -> Union[TextIO, None]:
    """Open a file and return the object.

    Parameters
    ----------
    file_path : str or :class:`pathlib.Path`
        Full absolute path to the file (either local or remote).
    file_options : str, optional
        Options for opening the file.
    encoding : str, optional
        Name of the encoding used to decode or encode the file.
        The default is ``None``, which means a platform-dependent encoding is used. You can
        specify any encoding supported by Python.
    override_existing : bool, optional
        Whether to override an existing file if opening a file in write mode on a remote
        machine. The default is ``True``.

    Returns
    -------
    Union[TextIO, None]
        Opened file object or ``None`` if the file or folder does not exist.
    """
    file_path = Path(file_path)
    dir_name = file_path.parent

    if "r" in file_options:
        if file_path.exists():
            return open(str(file_path), file_options, encoding=encoding)
        elif settings.remote_rpc_session and settings.remote_rpc_session.filemanager.pathexists(
            str(file_path)
        ):  # pragma: no cover
            local_file = Path(tempfile.gettempdir()) / file_path.name
            settings.remote_rpc_session.filemanager.download_file(str(file_path), str(local_file))
            return open(str(local_file), file_options, encoding=encoding)
    elif dir_name.exists():
        return open(str(file_path), file_options, encoding=encoding)
    elif settings.remote_rpc_session and settings.remote_rpc_session.filemanager.pathexists(str(dir_name)):
        if "w" in file_options:
            return settings.remote_rpc_session.create_file(
                str(file_path), file_options, encoding=encoding, override=override_existing
            )
        else:
            return settings.remote_rpc_session.open_file(str(file_path), file_options, encoding=encoding)
    else:
        pyaedt_logger.error("The file or folder %s does not exist", dir_name)
        return None


@pyaedt_function_handler(fn="input_file")
def read_json(input_file: Union[str, Path]) -> dict:
    """Load a JSON file to a dictionary.

    Parameters
    ----------
    input_file : str or :class:`pathlib.Path`
        Full path to the JSON file.

    Returns
    -------
    dict
        Parsed JSON file as a dictionary.
    """
    json_data = {}
    with open_file(input_file) as json_file:
        try:
            json_data = json.load(json_file)
        except json.JSONDecodeError as e:  # pragma: no cover
            error = f"Error reading json: {e.msg} at line {e.lineno}"
            pyaedt_logger.error(error)
    return json_data


@pyaedt_function_handler(file_path="input_file")
def read_toml(input_file: Union[str, Path]) -> dict:
    """Read a TOML file and return as a dictionary.

    Parameters
    ----------
    input_file : str or :class:`pathlib.Path`
        Full path to the TOML file.

    Returns
    -------
    dict
        Parsed TOML file as a dictionary.
    """
    try:
        import tomllib
    except (ImportError, ModuleNotFoundError):
        import tomli as tomllib

    with open_file(input_file, "rb") as fb:
        return tomllib.load(fb)


@pyaedt_function_handler(file_name="input_file")
def read_csv(input_file: Union[str, Path], encoding: str = "utf-8") -> list:
    """Read information from a CSV file and return a list.

    Parameters
    ----------
    input_file : str or :class:`pathlib.Path`
            Full path and name for the CSV file.
    encoding : str, optional
            File encoding for the CSV file. The default is ``"utf-8"``.

    Returns
    -------
    list
        Content of the CSV file.
    """
    file_name = check_and_download_file(input_file)

    lines = []
    with codecs.open(file_name, "rb", encoding) as csvfile:
        reader = csv.reader(csvfile, delimiter=",")
        for row in reader:
            lines.append(row)
    return lines


@pyaedt_function_handler(filename="input_file")
def read_csv_pandas(input_file: Union[str, Path], encoding: str = "utf-8"):
    """Read information from a CSV file and return a list.

    Parameters
    ----------
    input_file : str or :class:`pathlib.Path`
            Full path and name for the CSV file.
    encoding : str, optional
            File encoding for the CSV file. The default is ``"utf-8"``.

    Returns
    -------
    :class:`pandas.DataFrame`
        CSV file content.
    """
    input_file = Path(input_file)
    input_file = check_and_download_file(input_file)
    try:
        import pandas as pd

        return pd.read_csv(str(input_file), encoding=encoding, header=0, na_values=".")
    except ImportError:
        pyaedt_logger.error("Pandas is not available. Install it.")
        return None


@pyaedt_function_handler(output="output_file", quotechar="quote_char")
def write_csv(
    output_file: str, list_data: list, delimiter: str = ",", quote_char: str = "|", quoting: int = csv.QUOTE_MINIMAL
) -> bool:
    """Write data to a CSV .

    Parameters
    ----------
    output_file : str
        Full path and name of the file to write the data to.
    list_data : list
        Data to be written to the specified output file.
    delimiter : str
        Delimiter. The default value is ``"|"``.
    quote_char : str
        Quote character. The default value is ``"|"``
    quoting : int
        Quoting character. The default value is ``"csv.QUOTE_MINIMAL"``.
        It can take one any of the following module constants:

        - ``"csv.QUOTE_MINIMAL"`` means only when required, for example, when a
            field contains either the quote char or the delimiter
        - ``"csv.QUOTE_ALL"`` means that quotes are always placed around fields.
        - ``"csv.QUOTE_NONNUMERIC"`` means that quotes are always placed around
            fields which do not parse as integers or floating point
            numbers.
        - ``"csv.QUOTE_NONE"`` means that quotes are never placed around fields.

    Return
    ------
    bool
        ``True`` when successful, ``False`` when failed.
    """
    f = open(output_file, "w", newline="")
    writer = csv.writer(f, delimiter=delimiter, quotechar=quote_char, quoting=quoting)
    for data in list_data:
        writer.writerow([float(i) if isinstance(i, Quantity) else i for i in data])
    f.close()
    return True


@pyaedt_function_handler(file_name="input_file")
def read_tab(input_file: Union[str, Path]) -> list:
    """Read information from a TAB file and return a list.

    Parameters
    ----------
    input_file : str or :class:`pathlib.Path`
        Full path and name for the TAB file.

    Returns
    -------
    list
        TAB file content.
    """
    with open_file(input_file) as my_file:
        lines = my_file.readlines()
    return lines


@pyaedt_function_handler(file_name="input_file")
def read_xlsx(input_file: Union[str, Path]):
    """Read information from an XLSX file and return a list.

    Parameters
    ----------
    input_file : str or :class:`pathlib.Path`
        Full path and name for the XLSX file.

    Returns
    -------
    list
        XLSX file content.
    """
    file_name = check_and_download_file(input_file)
    try:
        import pandas as pd

        lines = pd.read_excel(file_name)
    except ImportError:  # pragma: no cover
        pyaedt_logger.error("Pandas and openpyxl are required to read the XLSX file.")
        lines = []
    return lines


@pyaedt_function_handler()
def _check_path(path_to_check: Union[str, Path]) -> str:
    path_to_check = str(path_to_check)
    return path_to_check.replace("\\", "/") if path_to_check[0] != "\\" else path_to_check


# AEDT files parsing
@pyaedt_function_handler()
def read_component_file(input_file: Union[str, Path]) -> dict:
    """Read the component file and extract variables.

    Parameters
    ----------
    input_file : str or :class:`pathlib.Path`
        Path to the component file.

    Returns
    -------
    dict
        Dictionary of variables in the component file.
    """
    variables = {}
    file_path = Path(input_file)

    if not file_path.is_file():
        return variables

    with open_file(str(file_path), "rb") as aedt_fh:
        temp = aedt_fh.read().splitlines()

    _all_lines = []
    for line in temp:
        try:
            _all_lines.append(line.decode("utf-8").lstrip("\t"))
        except UnicodeDecodeError:
            continue

    for line in _all_lines:
        if "VariableProp(" in line:
            line_list = line.split("'")
            if not any(c in line_list[-2] for c in ["+", "-", "*", ",", "/", "(", ")"]):
                variables[line_list[1]] = line_list[-2]

    return variables


@pyaedt_function_handler(file_name="input_file")
def parse_excitation_file(
    input_file: Union[str, Path],
    is_time_domain: bool = True,
    x_scale: float = 1.0,
    y_scale: float = 1,
    impedance: float = 50.0,
    data_format: str = "Power",
    encoding: str = "utf-8",
    out_mag: str = "Voltage",
    window: str = "hamming",
) -> Union[tuple, bool]:
    """Parse a csv file and convert data in list that can be applied to Hfss and Hfss3dLayout sources.

    Parameters
    ----------
    input_file : str or :class:`pathlib.Path`
        Full name of the input file.
    is_time_domain : bool, optional
        Either if the input data is Time based or Frequency Based. Frequency based data are Mag/Phase (deg).
    x_scale : float, optional
        Scaling factor for x axis.
    y_scale : float, optional
        Scaling factor for y axis.
    data_format : str, optional
        Either `"Power"`, `"Current"` or `"Voltage"`.
    impedance : float, optional
        Excitation impedance. Default is `50`.
    encoding : str, optional
        Csv file encoding.
    out_mag : str, optional
        Output magnitude format. It can be `"Voltage"` or `"Power"` depending on Hfss solution.
    window : str, optional
        Fft window. Options are ``"hamming"``, ``"hanning"``, ``"blackman"``, ``"bartlett"`` or ``None``.

    Returns
    -------
    tuple or bool
        Frequency, magnitude and phase.
    """
    import numpy as np

    try:
        import pandas
    except ImportError:  # pragma: no cover
        pyaedt_logger.error("Pandas is not available. Install it.")
        return False

    input_file = Path(input_file)
    df = read_csv_pandas(input_file, encoding=encoding)
    if is_time_domain and isinstance(df, pandas.DataFrame):
        time = df[df.keys()[0]].values * x_scale
        val = df[df.keys()[1]].values * y_scale
        freq, fval = compute_fft(time, val, window)

        if data_format.lower() == "current":
            if out_mag == "Voltage":
                fval = fval * impedance
            else:
                fval = fval * fval * impedance
        elif data_format.lower() == "voltage":
            if out_mag == "Power":
                fval = fval * fval / impedance
        else:
            if out_mag == "Voltage":
                fval = np.sqrt(fval * impedance)
        mag = list(np.abs(fval))
        phase = [math.atan2(j, i) * 180 / math.pi for i, j in zip(list(fval.real), list(fval.imag))]

    elif isinstance(df, pandas.DataFrame):
        freq = list(df[df.keys()[0]].values * x_scale)
        if data_format.lower() == "current":
            mag = df[df.keys()[1]].values * df[df.keys()[1]].values * impedance * y_scale * y_scale
        elif data_format.lower() == "voltage":
            mag = df[df.keys()[1]].values * df[df.keys()[1]].values / impedance * y_scale * y_scale
        else:
            mag = df[df.keys()[1]].values * y_scale
        mag = list(mag)
        phase = list(df[df.keys()[2]].values)
    return freq, mag, phase


@pyaedt_function_handler(file_path="input_file", unit="units", control_path="output_file")
def tech_to_control_file(input_file: Union[str, Path], units: str = "nm", output_file: Union[str, Path] = None):
    """Convert a TECH file to an XML file for use in a GDS or DXF import.

    Parameters
    ----------
    input_file : str or :class:`pathlib.Path`
        Full path to the TECH file.
    units : str, optional
        Tech units. If specified in tech file this parameter will not be used. Default is ``"nm"``.
    output_file : str or :class:`pathlib.Path`, optional
        Path for outputting the XML file.

    Returns
    -------
    str
        Output file path.
    """
    result = []
    input_file = Path(input_file)
    with open_file(input_file) as f:
        vals = list(CSS4_COLORS.values())
        id_layer = 0
        for line in f:
            line_split = line.split()
            if len(line_split) == 5:
                layerID, layer_name, _, _, layer_height = line.split()
                x = (
                    f'      <Layer Color="{vals[id_layer]}" '
                    f'GDSIIVia="{"true" if layer_name.lower().startswith("v") else "false"}" '
                    f'Name="{layerID}" TargetLayer="{layer_name}" Thickness="{layer_height}"'
                )
                x += ' Type="conductor"/>'
                result.append(x)
                id_layer += 1
            elif len(line_split) > 1 and "UNIT" in line_split[0]:
                units = line_split[1]
    if not output_file:
        output_file = input_file.with_suffix(".xml")
    else:
        output_file = Path(output_file)
    with open_file(output_file, "w") as f:
        f.write('<?xml version="1.0" encoding="UTF-8" standalone="no" ?>\n')
        f.write('    <c:Control xmlns:c="http://www.ansys.com/control" schemaVersion="1.0">\n')
        f.write("\n")
        f.write('      <Stackup schemaVersion="1.0">\n')
        f.write(f'        <Layers LengthUnit="{units}">\n')
        for res in result:
            f.write(res + "\n")

        f.write("    </Layers>\n")
        f.write("  </Stackup>\n")
        f.write("\n")
        f.write('  <ImportOptions Flatten="true" GDSIIConvertPolygonToCircles="false" ImportDummyNet="true"/>\n')
        f.write("\n")
        f.write("</c:Control>\n")
    return str(output_file)


# CAD parsing
@pyaedt_function_handler()
def get_dxf_layers(input_file: Union[str, Path]) -> List[str]:
    """Read a DXF file and return all layer names.

    Parameters
    ----------
    input_file : str or :class:`pathlib.Path`
        Full path to the DXF file.

    Returns
    -------
    list
        List of layers in the DXF file.
    """
    file_path = Path(input_file)

    def find_indices(list_to_check, item_to_find):
        return [element for element, value in enumerate(list_to_check) if value == item_to_find]

    layer_names = []
    with open_file(str(file_path), encoding="utf8") as f:
        lines = f.readlines()
        indices = find_indices(lines, "AcDbLayerTableRecord\n")
        index_offset = 1
        if not indices:
            indices = find_indices(lines, "LAYER\n")
            index_offset = 3
        for idx in indices:
            if "2" in lines[idx + index_offset]:
                layer_names.append(lines[idx + index_offset + 1].replace("\n", ""))
        return layer_names


# Configuration file
@pyaedt_function_handler(file_path="input_file")
def read_configuration_file(input_file: Union[str, Path]) -> Union[Dict, List]:
    """Parse a file and return the information in a list or dictionary.

    Parameters
    ----------
    input_file : str or :class:`pathlib.Path`
        Full path to the file. Supported formats are ``"csv"``, ``"json"``, ``"tab"``, ``"toml"``, and ``"xlsx"``.

    Returns
    -------
    Union[Dict, List]
        Dictionary if configuration file is ``"toml"`` or ``"json"``, List is ``"csv"``, ``"tab"`` or ``"xlsx"``.
    """
    file_path = Path(input_file)
    ext = Path(file_path).suffix
    if ext == ".toml":
        return read_toml(file_path)
    elif ext == ".tab":
        return read_tab(file_path)
    elif ext == ".csv":
        return read_csv(file_path)
    elif ext == ".xlsx":
        return read_xlsx(file_path)
    else:
        return read_json(file_path)


@pyaedt_function_handler(dict_in="input_data", full_path="output_file")
def write_configuration_file(input_data: dict, output_file: Union[str, Path]) -> bool:
    """Create a configuration file in JSON or TOML format from a dictionary.

    Parameters
    ----------
    input_data : dict
        Dictionary to write the file to.
    output_file : str or :class:`pathlib.Path`
        Full path to the file, including its extension.

    Returns
    -------
    bool
        ``True`` when successful, ``False`` when failed.
    """
    ext = Path(output_file).suffix
    if ext == ".json":
        return _create_json_file(input_data, output_file)
    elif ext == ".toml":
        return _create_toml_file(input_data, output_file)


# Operators
@pyaedt_function_handler(time_vals="time_values", value="data_values")
def compute_fft(time_values, data_values, window=None) -> Union[tuple, bool]:  # pragma: no cover
    """Compute FFT of input transient data.

    Parameters
    ----------
    time_values : `pandas.Series`
        Time points corresponding to the x-axis of the input transient data.
    data_values : `pandas.Series`
        Points corresponding to the y-axis.
    window : str, optional
        Fft window. Options are "hamming", "hanning", "blackman", "bartlett".

    Returns
    -------
    tuple or bool
        Frequency and values.
    """
    import numpy as np

    deltaT = time_values[-1] - time_values[0]
    num_points = len(time_values)
    win = None
    if window:
        if window == "hamming":
            win = np.hamming(num_points)
        elif window == "hanning":
            win = np.hanning(num_points)
        elif window == "bartlett":
            win = np.bartlett(num_points)
        elif window == "blackman":
            win = np.blackman(num_points)
    if win is not None:
        valueFFT = np.fft.fft(data_values * win, num_points)
    else:
        valueFFT = np.fft.fft(data_values, num_points)
    Npoints = int(len(valueFFT) / 2)
    valueFFT = valueFFT[:Npoints]
    valueFFT = 2 * valueFFT / len(valueFFT)
    n = np.arange(num_points)
    freq = n / deltaT
    return freq, valueFFT


# License


@pyaedt_function_handler()
def available_license_feature(
    feature: str = "electronics_desktop", input_dir: Union[str, Path] = None, port: int = 1055, name: str = "127.0.0.1"
) -> int:  # pragma: no cover
    """Check available license feature.

    .. warning::

        Do not execute this function with untrusted function argument, environment
        variables or pyaedt global settings.
        See the :ref:`security guide<ref_security_consideration>` for details.

    The method retrieves the port and name values from the ``ANSYSLMD_LICENSE_FILE`` environment variable if available.
    If not, the default values are applied.

    Parameters
    ----------
    feature : str
        Feature increment name. The default is the ``"electronics_desktop"``.
    input_dir: str or :class:`pathlib.Path`, optional
        AEDT installation path. The default is ``None``, in which case the first identified AEDT
        installation from :func:`ansys.aedt.core.internal.aedt_versions.installed_versions`
        method is taken.
    port : int, optional
        Server port number. The default is ``1055``.
    name : str, optional
        License server name. The default is ``"127.0.0.1"``.

    Returns
    -------
    int
        Number of available license features, ``False`` when license server is down.
    """
    import subprocess  # nosec

    if os.getenv("ANSYSLMD_LICENSE_FILE", None):
        name_env = os.getenv("ANSYSLMD_LICENSE_FILE")
        name_env = name_env.split(",")[0].split("@")
        if len(name_env) == 2:
            port = name_env[0]
            name = name_env[1]

    if not input_dir and aedt_versions.current_version:
        input_dir = Path(aedt_versions.installed_versions[aedt_versions.current_version])
    elif not input_dir:
        input_dir = Path(aedt_versions.installed_versions[aedt_versions.latest_version])
    else:
        input_dir = Path(input_dir)

    # Starting with 25R2, the licensingclient directory is located one level higher in the installation
    # path. If the folder isn't found in the legacy location, use the parent directory.
    if not check_if_path_exists(os.path.join(input_dir, "licensingclient")):
        input_dir = Path(os.path.dirname(input_dir))

    if is_linux:
        ansysli_util_path = input_dir / "licensingclient" / "linx64" / "lmutil"
    else:
        ansysli_util_path = input_dir / "licensingclient" / "winx64" / "lmutil"

    my_env = os.environ.copy()

    tempfile_checkout = tempfile.NamedTemporaryFile(suffix=".txt", delete=False).name
    tempfile_checkout = Path(tempfile_checkout)

    cmd = [str(ansysli_util_path), "lmstat", "-f", feature, "-c", str(port) + "@" + str(name)]

    try:
        with tempfile_checkout.open("w") as f:
            subprocess.run(cmd, stdout=f, stderr=f, env=my_env, check=True)  # nosec
    except Exception as e:
        raise AEDTRuntimeError("Failed to check available licenses") from e

    available_licenses = 0
    pattern_license = r"Total of\s+(\d+)\s+licenses? issued;\s+Total of\s+(\d+)\s+licenses? in use"
    pattern_error = r"Error getting status"
    with open_file(tempfile_checkout, "r") as f:
        for line in f:
            line = line.strip()
            match_license = re.search(pattern_license, line)
            if match_license:
                total_licenses_issued = int(match_license.group(1))
                total_licenses_in_use = int(match_license.group(2))
                available_licenses = total_licenses_issued - total_licenses_in_use
                break
            match_error = re.search(pattern_error, line)
            if match_error:
                pyaedt_logger.error(line)
                return False

    # Clean up temp file after processing
    tempfile_checkout.unlink()

    return available_licenses


@pyaedt_function_handler()
def _check_installed_version(install_path, long_version):
    """Check installation folder to determine if it is for specified Ansys EM version.

    Parameters
    ----------
    install_path: str
        Installation folder to check.  For example, ``"C:\\Program Files\\AnsysEM\\v231\\Win64"``.
    long_version: str
        Long form of version number.  For example, ``"2023.1"``.

    Returns
    -------
    bool
    """
    install_path = Path(install_path)
    product_list_path = install_path / "config" / "ProductList.txt"
    if product_list_path.is_file():
        try:
            with open_file(product_list_path, "r") as f:
                install_version = f.readline().strip()[-6:]
                if install_version == long_version:
                    return True
        except Exception:
            pyaedt_logger.debug("An error occurred while parsing installation version")
    return False


@pyaedt_function_handler()
def _create_json_file(json_dict, full_json_path):
    full_json_path = Path(full_json_path)
    if not full_json_path.parent.exists():
        full_json_path.parent.mkdir(parents=True)

    with open_file(full_json_path, "w") as fp:
        json.dump(json_dict, fp, indent=4)
    pyaedt_logger.info(f"{full_json_path} correctly created.")
    return True


@pyaedt_function_handler()
def _create_toml_file(input_dict, full_toml_path):
    import tomli_w

    full_toml_path = Path(full_toml_path)

    if not full_toml_path.parent.exists():
        full_toml_path.parent.mkdir(parents=True)

    def _dict_toml(d):
        new_dict_toml = {}
        for k, v in d.items():
            new_k = k
            if not isinstance(k, str):
                new_k = str(k)
            new_v = v
            if isinstance(v, dict):
                new_v = _dict_toml(v)
            elif isinstance(v, tuple):
                new_v = list(v)
            new_dict_toml[new_k] = new_v
        return new_dict_toml

    new_dict = _dict_toml(input_dict)
    with open_file(full_toml_path, "wb") as fp:
        tomli_w.dump(new_dict, fp)
    pyaedt_logger.info(f"{full_toml_path} correctly created.")
    return True


def _uname(name: str = None) -> str:
    """Append a 6-digit hash code to a specified name.

    Parameters
    ----------
    name : str
        Name to append the hash code to. The default is ``"NewObject_"``.

    Returns
    -------
    str

    """
    alphabet = string.ascii_uppercase + string.digits

    import secrets

    generator = secrets.SystemRandom()
    unique_name = "".join(secrets.SystemRandom.sample(generator, alphabet, 6))

    if name:
        return name + unique_name
    else:
        return "NewObject_" + unique_name
