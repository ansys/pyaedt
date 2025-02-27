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
import json
from pathlib import Path
from typing import Dict
from typing import List
from typing import TextIO
from typing import Union

from ansys.aedt.core.generic.general_methods import pyaedt_function_handler
from ansys.aedt.core.generic.settings import settings


# Path processing
@pyaedt_function_handler()
def normalize_path(path_in: Union[str, Path], sep: str = None) -> str:
    """Normalize path separators.

    Parameters
    ----------
    path_in : str or :class:`pathlib.Path`
        Path to normalize.
    sep : str, optional
        Separator.

    Returns
    -------
    str
        Path normalized to new separator.
    """
    path = Path(path_in)
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
    """Check if an AEDT project lock file exists.

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
    """Check if an AEDT project exists and try to remove the lock file.

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
    input_file_locked = str(input_file) + ".lock"
    if settings.remote_rpc_session and settings.remote_rpc_session.filemanager.pathexists(input_file_locked):
        settings.remote_rpc_session.filemanager.unlink(input_file_locked)
        return True
    if os.path.exists(input_file_locked):
        os.remove(input_file_locked)
    return True


@pyaedt_function_handler()
def check_and_download_file(remote_path: Union[str, Path], overwrite: bool = True) -> str:
    """Check if a file is remote and either download it or return the path.

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
    """Check whether a path exists or not local or remote machine (for remote sessions only).

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
    """Check if a folder is remote and either download it or return the path.

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
    file_path = file_path.as_posix() if file_path.drive else file_path

    dir_name = file_path.parent
    if "r" in file_options:
        if file_path.exists():
            return open(file_path, file_options, encoding=encoding)
        elif settings.remote_rpc_session and settings.remote_rpc_session.filemanager.pathexists(
            str(file_path)
        ):  # pragma: no cover
            local_file = Path(tempfile.gettempdir()) / file_path.name
            settings.remote_rpc_session.filemanager.download_file(str(file_path), str(local_file))
            return open(local_file, file_options, encoding=encoding)
    elif dir_name.exists():
        return open(file_path, file_options, encoding=encoding)
    elif settings.remote_rpc_session and settings.remote_rpc_session.filemanager.pathexists(str(dir_name)):
        if "w" in file_options:
            return settings.remote_rpc_session.create_file(
                str(file_path), file_options, encoding=encoding, override=override_existing
            )
        else:
            return settings.remote_rpc_session.open_file(str(file_path), file_options, encoding=encoding)
    else:
        settings.logger.error("The file or folder %s does not exist", dir_name)
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
            settings.logger.error(error)
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
        writer.writerow(data)
    f.close()
    return True


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


@pyaedt_function_handler()
def _create_json_file(json_dict, full_json_path):
    full_json_path = Path(full_json_path)
    if not full_json_path.parent.exists():
        full_json_path.parent.mkdir(parents=True)

    with open_file(full_json_path, "w") as fp:
        json.dump(json_dict, fp, indent=4)
    settings.logger.info(f"{full_json_path} correctly created.")
    return True
