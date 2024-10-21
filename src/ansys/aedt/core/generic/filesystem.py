# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 - 2024 ANSYS, Inc. and/or its affiliates.
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
import random
import shutil
import string
import sys
import tempfile

from ansys.aedt.core.generic.constants import CSS4_COLORS
from ansys.aedt.core.generic.data_handlers import compute_fft
from ansys.aedt.core.generic.data_handlers import generate_unique_name
from ansys.aedt.core.generic.general_methods import pyaedt_function_handler
from ansys.aedt.core.generic.settings import settings


def search_files(dirname, pattern="*"):
    """Search for files inside a directory given a specific pattern.

    Parameters
    ----------
    dirname : str
    pattern :str, optional

    Returns
    -------
    list
    """
    from ansys.aedt.core.generic.general_methods import is_ironpython

    if is_ironpython:
        import glob

        return list(glob.glob(os.path.join(dirname, pattern)))
    else:
        import pathlib

        return [os.path.abspath(i) for i in pathlib.Path(dirname).glob(pattern)]


def my_location():
    """ """
    return os.path.normpath(os.path.dirname(__file__))


class Scratch:
    """ """

    @property
    def path(self):
        """ """
        return self._scratch_path

    @property
    def is_empty(self):
        """ """
        return self._cleaned

    def __init__(self, local_path, permission=0o777, volatile=False):
        self._volatile = volatile
        self._cleaned = True
        char_set = string.ascii_uppercase + string.digits
        self._scratch_path = os.path.normpath(os.path.join(local_path, "scratch" + "".join(random.sample(char_set, 6))))
        if os.path.exists(self._scratch_path):
            try:
                self.remove()
            except Exception:
                self._cleaned = False
        if self._cleaned:
            try:
                os.mkdir(self.path)
                os.chmod(self.path, permission)
            except FileNotFoundError as fnf_error:  # Raise error if folder doesn't exist.
                print(fnf_error)

    def remove(self):
        """ """
        try:
            # TODO check why on Anaconda 3.7 get errors with os.path.exists
            shutil.rmtree(self._scratch_path, ignore_errors=True)
        except Exception:
            settings.logger.error("An error occurred while removing {}".format(self._scratch_path))

    def copyfile(self, src_file, dst_filename=None):
        """
        Copy a file to the scratch directory. The target filename is optional.
        If omitted, the target file name is identical to the source file name.

        Parameters
        ----------
        src_file : str
            Source file with fullpath.
        dst_filename : str, optional
            Destination filename with the extension. The default is ``None``,
            in which case the destination file is given the same name as the
            source file.


        Returns
        -------
        dst_file : str
            Full path and file name of the copied file.

        """
        if dst_filename:
            dst_file = os.path.join(self.path, dst_filename)
        else:
            dst_file = os.path.join(self.path, os.path.basename(src_file))
        if os.path.exists(dst_file):
            try:
                os.unlink(dst_file)
            except OSError:  # pragma: no cover
                pass
        try:
            shutil.copy2(src_file, dst_file)
        except FileNotFoundError as fnf_error:
            print(fnf_error)

        return dst_file

    def copyfolder(self, src_folder, destfolder):
        """

        Parameters
        ----------
        src_folder :

        destfolder :


        Returns
        -------

        """
        shutil.copytree(src_folder, destfolder, dirs_exist_ok=True)
        return True

    def __enter__(self):
        return self

    def __exit__(self, ex_type, ex_value, ex_traceback):
        if ex_type or self._volatile:
            self.remove()


def get_json_files(start_folder):
    """
    Get the absolute path to all *.json files in start_folder.

    Parameters
    ----------
    start_folder : str
        Path to the folder where the json files are located.

    Returns
    -------
    """
    return [y for x in os.walk(start_folder) for y in search_files(x[0], "*.json")]


def is_safe_path(path, allowed_extensions=None):
    """Validate if a path is safe to use."""
    # Ensure that path is an existing file or directory
    if not os.path.exists(path) or not os.path.isfile(path):
        return False

    # Restrict to allowed file extensions:
    if allowed_extensions:
        if not any(path.endswith(extension) for extension in allowed_extensions):
            return False

    # Ensure path does not contain dangerous characters
    if any(char in path for char in (";", "|", "&", "$", "<", ">", "`")):
        return False

    return True


def normalize_path(path_in, sep=None):
    """Normalize path separators.

    Parameters
    ----------
    path_in : str
        Path to normalize.
    sep : str, optional
        Separator.

    Returns
    -------
    str
        Path normalized to new separator.
    """
    if sep is None:
        sep = os.sep
    return path_in.replace("\\", sep).replace("/", sep)


@pyaedt_function_handler()
def _check_path(path_to_check):
    return path_to_check.replace("\\", "/") if path_to_check[0] != "\\" else path_to_check


@pyaedt_function_handler()
def check_and_download_file(remote_path, overwrite=True):
    """Check if a file is remote and either download it or return the path.

    Parameters
    ----------
    remote_path : str
        Path to the remote file.
    overwrite : bool, optional
        Whether to overwrite the file if it already exists locally.
        The default is ``True``.

    Returns
    -------
    str
        Path to the remote file.
    """
    if settings.remote_rpc_session:
        remote_path = _check_path(remote_path)
        local_path = os.path.join(settings.remote_rpc_session_temp_folder, os.path.split(remote_path)[-1])
        if settings.remote_rpc_session.filemanager.pathexists(remote_path):
            settings.remote_rpc_session.filemanager.download_file(remote_path, local_path, overwrite=overwrite)
            return local_path
    return remote_path


@pyaedt_function_handler(filename="file_name")
def read_csv(file_name, encoding="utf-8"):
    """Read information from a CSV file and return a list.

    Parameters
    ----------
    file_name : str
            Full path and name for the CSV file.
    encoding : str, optional
            File encoding for the CSV file. The default is ``"utf-8"``.

    Returns
    -------
    list
        Content of the CSV file.
    """
    file_name = check_and_download_file(file_name)

    lines = []
    with codecs.open(file_name, "rb", encoding) as csvfile:
        reader = csv.reader(csvfile, delimiter=",")
        for row in reader:
            lines.append(row)
    return lines


@pyaedt_function_handler(filename="input_file")
def read_csv_pandas(input_file, encoding="utf-8"):
    """Read information from a CSV file and return a list.

    Parameters
    ----------
    input_file : str
            Full path and name for the CSV file.
    encoding : str, optional
            File encoding for the CSV file. The default is ``"utf-8"``.

    Returns
    -------
    :class:`pandas.DataFrame`
        CSV file content.
    """
    input_file = check_and_download_file(input_file)
    try:
        import pandas as pd

        return pd.read_csv(input_file, encoding=encoding, header=0, na_values=".")
    except ImportError:
        settings.logger.error("Pandas is not available. Install it.")
        return None


@pyaedt_function_handler(filename="file_name")
def read_tab(file_name):
    """Read information from a TAB file and return a list.

    Parameters
    ----------
    file_name : str
            Full path and name for the TAB file.

    Returns
    -------
    list
        TAB file content.
    """
    with open_file(file_name) as my_file:
        lines = my_file.readlines()
    return lines


@pyaedt_function_handler(filename="file_name")
def read_xlsx(file_name):
    """Read information from an XLSX file and return a list.

    Parameters
    ----------
    file_name : str
            Full path and name for the XLSX file.

    Returns
    -------
    list
        XLSX file content.
    """
    file_name = check_and_download_file(file_name)
    try:
        import pandas as pd

        lines = pd.read_excel(file_name)
        return lines
    except ImportError:
        lines = []
        return lines


@pyaedt_function_handler(output="output_file", quotechar="quote_char")
def write_csv(output_file, list_data, delimiter=",", quote_char="|", quoting=csv.QUOTE_MINIMAL):
    """Write data to a CSV.

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
def check_if_path_exists(path):
    """Check whether a path exists or not local or remote machine (for remote sessions only).

    Parameters
    ----------
    path : str
        Local or remote path to check.

    Returns
    -------
    bool
        ``True`` when successful, ``False`` when fails.
    """
    if settings.remote_rpc_session:
        return settings.remote_rpc_session.filemanager.pathexists(path)
    return os.path.exists(path)


@pyaedt_function_handler()
def check_and_download_folder(local_path, remote_path, overwrite=True):
    """Check if a folder is remote and either download it or return the path.

    Parameters
    ----------
    local_path : str
        Local path to save the folder to.
    remote_path : str
        Path to the remote folder.
    overwrite : bool, optional
        Whether to overwrite the folder if it already exists locally.
        The default is ``True``.

    Returns
    -------
    str
    """
    if settings.remote_rpc_session:
        remote_path = remote_path.replace("\\", "/") if remote_path[0] != "\\" else remote_path
        settings.remote_rpc_session.filemanager.download_folder(remote_path, local_path, overwrite=overwrite)
        return local_path
    return remote_path


@pyaedt_function_handler()
def open_file(file_path, file_options="r", encoding=None, override_existing=True):
    """Open a file and return the object.

    Parameters
    ----------
    file_path : str
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
    object
        Opened file.
    """
    file_path = str(file_path)
    file_path = file_path.replace("\\", "/") if file_path[0] != "\\" else file_path

    dir_name = os.path.dirname(file_path)
    if "r" in file_options:
        if os.path.exists(file_path):
            return open(file_path, file_options, encoding=encoding)
        elif settings.remote_rpc_session and settings.remote_rpc_session.filemanager.pathexists(
            file_path
        ):  # pragma: no cover
            local_file = os.path.join(tempfile.gettempdir(), os.path.split(file_path)[-1])
            settings.remote_rpc_session.filemanager.download_file(file_path, local_file)
            return open(local_file, file_options, encoding=encoding)
    elif os.path.exists(dir_name):
        return open(file_path, file_options, encoding=encoding)
    elif settings.remote_rpc_session and settings.remote_rpc_session.filemanager.pathexists(dir_name):
        if "w" in file_options:
            return settings.remote_rpc_session.create_file(
                file_path, file_options, encoding=encoding, override=override_existing
            )
        else:
            return settings.remote_rpc_session.open_file(file_path, file_options, encoding=encoding)
    else:
        settings.logger.error("The file or folder %s does not exist", dir_name)


@pyaedt_function_handler()
def read_configuration_file(file_path):
    """Parse a file and return the information in a list or dictionary.

    Parameters
    ----------
    file_path : str
        Full path to the file. Supported formats are ``"csv"``, ``"json"``, ``"tab"``, ``"toml"``, and ``"xlsx"``.

    Returns
    -------
    dict or list
        Dictionary if configuration file is ``"toml"`` or ``"json"``, List is ``"csv"``, ``"tab"`` or ``"xlsx"``.
    """
    ext = os.path.splitext(file_path)[1]
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


@pyaedt_function_handler()
def read_json(fn):
    """Load a JSON file to a dictionary.

    Parameters
    ----------
    fn : str
        Full path to the JSON file.

    Returns
    -------
    dict
        Parsed JSON file as a dictionary.
    """
    json_data = {}
    with open_file(fn) as json_file:
        try:
            json_data = json.load(json_file)
        except json.JSONDecodeError as e:  # pragma: no cover
            error = "Error reading json: {} at line {}".format(e.msg, e.lineno)
            settings.logger.error(error)
    return json_data


@pyaedt_function_handler()
def read_toml(file_path):  # pragma: no cover
    """Read a TOML file and return as a dictionary.

    Parameters
    ----------
    file_path : str
        Full path to the TOML file.

    Returns
    -------
    dict
        Parsed TOML file as a dictionary.
    """
    current_python_version = sys.version_info[:2]
    if current_python_version < (3, 12):
        import pytomlpp as tomllib
    else:
        import tomllib

    with open_file(file_path, "rb") as fb:
        return tomllib.load(fb)


@pyaedt_function_handler()
def get_filename_without_extension(path):
    """Get the filename without its extension.

    Parameters
    ----------
    path : str
        Path of the file.

    Returns
    -------
    str
       Name of the file without extension.
    """
    return os.path.splitext(os.path.split(path)[1])[0]


@pyaedt_function_handler(rootname="root_name")
def generate_unique_folder_name(root_name=None, folder_name=None):
    """Generate a new AEDT folder name given a rootname.

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
    temp_folder = os.path.join(root_name, folder_name)
    if settings.remote_rpc_session and not settings.remote_rpc_session.filemanager.pathexists(temp_folder):
        settings.remote_rpc_session.filemanager.makedirs(temp_folder)
    elif not os.path.exists(temp_folder):
        os.makedirs(temp_folder)
    return temp_folder


@pyaedt_function_handler(rootname="root_name")
def generate_unique_project_name(root_name=None, folder_name=None, project_name=None, project_format="aedt"):
    """Generate a new AEDT project name given a rootname.

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
    prj = os.path.join(folder_path, name_with_ext)
    if check_if_path_exists(prj):
        name_with_ext = generate_unique_name(project_name, n=3) + "." + project_format
        prj = os.path.join(folder_path, name_with_ext)
    return prj


@pyaedt_function_handler(startpath="path", filepattern="file_pattern")
def recursive_glob(path, file_pattern):
    """Get a list of files matching a pattern, searching recursively from a start path.

    Parameters
    ----------
    path : str
        Starting path.
    file_pattern : str
        File pattern to match.

    Returns
    -------
    list
        List of files matching the given pattern.
    """
    if settings.remote_rpc_session:
        files = []
        for i in settings.remote_rpc_session.filemanager.listdir(path):
            if settings.remote_rpc_session.filemanager.isdir(os.path.join(path, i)):
                files.extend(recursive_glob(os.path.join(path, i), file_pattern))
            elif fnmatch.fnmatch(i, file_pattern):
                files.append(os.path.join(path, i))
        return files
    else:
        return [
            os.path.join(dirpath, filename)
            for dirpath, _, filenames in os.walk(path)
            for filename in filenames
            if fnmatch.fnmatch(filename, file_pattern)
        ]


@pyaedt_function_handler()
def _create_toml_file(input_dict, full_toml_path):
    current_python_version = sys.version_info[:2]
    if current_python_version < (3, 12):
        import pytomlpp as tomllib
    else:
        import tomllib

    if not os.path.exists(os.path.dirname(full_toml_path)):
        os.makedirs(os.path.dirname(full_toml_path))

    def _dict_toml(d):
        new_dict = {}
        for k, v in d.items():
            new_k = k
            if not isinstance(k, str):
                new_k = str(k)
            new_v = v
            if isinstance(v, dict):
                new_v = _dict_toml(v)
            elif isinstance(v, tuple):
                new_v = list(v)
            new_dict[new_k] = new_v
        return new_dict

    new_dict = _dict_toml(input_dict)
    with open_file(full_toml_path, "w") as fp:
        tomllib.dump(new_dict, fp)
    settings.logger.info(f"{full_toml_path} correctly created.")
    return True


@pyaedt_function_handler()
def _create_json_file(json_dict, full_json_path):
    if not os.path.exists(os.path.dirname(full_json_path)):
        os.makedirs(os.path.dirname(full_json_path))
    with open_file(full_json_path, "w") as fp:
        json.dump(json_dict, fp, indent=4)
    settings.logger.info(f"{full_json_path} correctly created.")
    return True


@pyaedt_function_handler(dict_in="input_data", full_path="output_file")
def write_configuration_file(input_data, output_file):
    """Create a configuration file in JSON or TOML format from a dictionary.

    Parameters
    ----------
    input_data : dict
        Dictionary to write the file to.
    output_file : str
        Full path to the file, including its extension.

    Returns
    -------
    bool
        ``True`` when successful, ``False`` when failed.
    """
    ext = os.path.splitext(output_file)[1]
    if ext == ".json":
        return _create_json_file(input_data, output_file)
    elif ext == ".toml":
        return _create_toml_file(input_data, output_file)


@pyaedt_function_handler(file_name="input_file")
def parse_excitation_file(
    input_file,
    is_time_domain=True,
    x_scale=1,
    y_scale=1,
    impedance=50,
    data_format="Power",
    encoding="utf-8",
    out_mag="Voltage",
    window="hamming",
):
    """Parse a csv file and convert data in list that can be applied to Hfss and Hfss3dLayout sources.

    Parameters
    ----------
    input_file : str
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
    tuple
        Frequency, magnitude and phase.
    """
    try:
        import numpy as np
    except ImportError:
        settings.logger.error("NumPy is not available. Install it.")
        return False
    df = read_csv_pandas(input_file, encoding=encoding)
    if is_time_domain:
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

    else:
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


@pyaedt_function_handler(tech_path="file_path", unit="units", control_path="output_file")
def tech_to_control_file(file_path, units="nm", output_file=None):
    """Convert a TECH file to an XML file for use in a GDS or DXF import.

    Parameters
    ----------
    file_path : str
        Full path to the TECH file.
    units : str, optional
        Tech units. If specified in tech file this parameter will not be used. Default is ``"nm"``.
    output_file : str, optional
        Path for outputting the XML file.

    Returns
    -------
    str
        Output file path.
    """
    result = []
    with open_file(file_path) as f:
        vals = list(CSS4_COLORS.values())
        id_layer = 0
        for line in f:
            line_split = line.split()
            if len(line_split) == 5:
                layerID, layer_name, _, elevation, layer_height = line.split()
                x = '      <Layer Color="{}" GDSIIVia="{}" Name="{}" TargetLayer="{}" Thickness="{}"'.format(
                    vals[id_layer],
                    "true" if layer_name.lower().startswith("v") else "false",
                    layerID,
                    layer_name,
                    layer_height,
                )
                x += ' Type="conductor"/>'
                result.append(x)
                id_layer += 1
            elif len(line_split) > 1 and "UNIT" in line_split[0]:
                units = line_split[1]
    if not output_file:
        output_file = os.path.splitext(file_path)[0] + ".xml"
    with open_file(output_file, "w") as f:
        f.write('<?xml version="1.0" encoding="UTF-8" standalone="no" ?>\n')
        f.write('    <c:Control xmlns:c="http://www.ansys.com/control" schemaVersion="1.0">\n')
        f.write("\n")
        f.write('      <Stackup schemaVersion="1.0">\n')
        f.write('        <Layers LengthUnit="{}">\n'.format(units))
        for res in result:
            f.write(res + "\n")

        f.write("    </Layers>\n")
        f.write("  </Stackup>\n")
        f.write("\n")
        f.write('  <ImportOptions Flatten="true" GDSIIConvertPolygonToCircles="false" ImportDummyNet="true"/>\n')
        f.write("\n")
        f.write("</c:Control>\n")

    return output_file
