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

"""Download example datasets from https://github.com/ansys/example-data"""

import os
from pathlib import Path
import shutil
import tempfile
from typing import Optional
from typing import Union
from urllib.parse import urljoin
import urllib.request
import zipfile

from ansys.aedt.core.aedt_logger import pyaedt_logger
from ansys.aedt.core.generic.general_methods import pyaedt_function_handler
from ansys.aedt.core.internal.errors import AEDTRuntimeError

EXAMPLES_DATA_REPO = "https://github.com/ansys/example-data/raw/main"
EXAMPLES_PATH = Path(tempfile.gettempdir()) / "PyAEDTExamples"


def delete_downloads():
    """Delete all downloaded examples to free space or update the files."""
    shutil.rmtree(EXAMPLES_PATH, ignore_errors=True)


def _download_file(relative_path: str, local_path: Optional[Union[str, Path]] = None) -> Path:
    """Download a file from a URL."""
    url = urljoin(EXAMPLES_DATA_REPO + "/", relative_path + "/")
    relative_path = Path(relative_path.strip("/"))

    if not local_path:
        local_path = EXAMPLES_PATH / relative_path
    else:
        local_path = Path(local_path) / relative_path
    local_path.parent.mkdir(parents=True, exist_ok=True)

    try:
        if not local_path.exists():
            pyaedt_logger.debug(f"Downloading file from URL {url}")
            urllib.request.urlretrieve(url, local_path)
        else:
            pyaedt_logger.debug(f"File already exists in {local_path}. Skipping download.")
    except Exception as e:
        raise AEDTRuntimeError(f"Failed to download file from URL {url}.") from e

    return local_path.resolve()


def _download_folder(relative_path: str, local_path: Optional[Union[str, Path]] = None) -> Path:
    """Download a folder from the example data repository."""
    import json
    import re

    url = urljoin(EXAMPLES_DATA_REPO + "/", relative_path + "/")
    relative_path = Path(relative_path.strip("/"))

    if not local_path:
        local_path = EXAMPLES_PATH
    else:
        local_path = Path(local_path)
    local_path.mkdir(parents=True, exist_ok=True)

    with urllib.request.urlopen(url) as response:
        data = response.read().decode("utf-8").splitlines()

    try:
        tree = [i for i in data if '"payload"' in i][0]
        match = re.search(r'>({"payload".+)</script>', tree)
        json_data = json.loads(match.group(1))
        items = json_data["payload"]["tree"]["items"]
        for item in items:
            if item["contentType"] == "directory":
                pyaedt_logger.info(f"Calling download folder {item['path']} into {local_path}")
                _download_folder(item["path"], local_path)
            else:
                pyaedt_logger.info(f"Calling download file {item['path']} into {local_path}")
                _download_file(item["path"], local_path)
    except Exception as e:
        raise AEDTRuntimeError(f"Failed to download {relative_path}.") from e

    return local_path / relative_path


###############################################################################


def download_aedb(local_path: Optional[Union[str, Path]] = None):
    """Download an example of AEDB File and return the def path.

    Examples files are downloaded to a persistent cache to avoid
    re-downloading the same file twice.

    Parameters
    ----------
    local_path : str or :class:`pathlib.Path`, optional
        Path for downloading files. The default is the user's temp folder.

    Returns
    -------
    str
        Path to the example file.

    Examples
    --------
    Download an example result file and return the path of the file.
    >>> import ansys.aedt.core
    >>> path = ansys.aedt.core.downloads.download_aedb()

    """
    from ansys.aedt.core.examples.downloads import _download_file

    local_path = _download_file("pyaedt/edb/Galileo.aedb/GRM32ER72A225KA35_25C_0V.sp", local_path)
    local_path = local_path.parent.parent.parent.parent
    local_path = _download_file("pyaedt/edb/Galileo.aedb/edb.def", local_path)
    local_path = local_path.parent
    return local_path


def download_edb_merge_utility(force_download=False, destination=None):
    """Download an example of WPF Project which allows to merge 2aedb files.

    Examples files are downloaded to a persistent cache to avoid
    re-downloading the same file twice.

    Parameters
    ----------
    force_download : bool
        Force to delete cache and download files again.
    destination : str, optional
        Path for downloading files. The default is the user's temp folder.

    Returns
    -------
    str
        Path to the example file.

    Examples
    --------
    Download an example result file and return the path of the file.
    >>> import ansys.aedt.core
    >>> path = ansys.aedt.core.downloads.download_edb_merge_utility(force_download=True)
    >>> path
    'C:/Users/user/AppData/local/temp/wpf_edb_merge/merge_wizard.py'
    """
    if not destination:
        destination = EXAMPLES_PATH
    if force_download:
        local_path = os.path.join(destination, "wpf_edb_merge")
        if os.path.exists(local_path):
            shutil.rmtree(local_path, ignore_errors=True)
    local_paths = []
    _download_file("pyaedt/wpf_edb_merge/board.aedb", "edb.def", destination, local_paths)
    _download_file("pyaedt/wpf_edb_merge/package.aedb", "edb.def", destination, local_paths)
    _download_file("pyaedt/wpf_edb_merge", "merge_wizard_settings.json", destination, local_paths)

    _download_file("pyaedt/wpf_edb_merge", "merge_wizard.py", destination, local_paths)
    return local_paths[0]


def download_netlist(destination=None):
    """Download an example of netlist File and return the def path.

    Examples files are downloaded to a persistent cache to avoid
    re-downloading the same file twice.

    Parameters
    ----------
    destination : str, optional
        Path for downloading files. The default is the user's temp folder.

    Returns
    -------
    str
        Path to the example file.

    Examples
    --------
    Download an example result file and return the path of the file.

    >>> import ansys.aedt.core
    >>> path = ansys.aedt.core.downloads.download_netlist()
    >>> path
    'C:/Users/user/AppData/local/temp/pyaedtexamples/netlist_small.cir'
    """
    local_paths = []
    _download_file("pyaedt/netlist", "netlist_small.cir", destination, local_paths)
    return local_paths[0]


def download_antenna_array(destination=None):
    """Download an example of Antenna Array and return the def path.

    Examples files are downloaded to a persistent cache to avoid
    re-downloading the same file twice.

    Parameters
    ----------
    destination : str, optional
        Path for downloading files. The default is the user's temp folder.

    Returns
    -------
    str
        Path to the example file.

    Examples
    --------

    Download an example result file and return the path of the file.

    >>> import ansys.aedt.core
    >>> path = ansys.aedt.core.downloads.download_antenna_array()
    >>> path
    'C:/Users/user/AppData/local/temp/pyaedtexamples/FiniteArray_Radome_77GHz_3D_CADDM.aedt'
    """

    local_paths = []
    _download_file("pyaedt/array_antenna", "FiniteArray_Radome_77GHz_3D_CADDM.aedt", destination, local_paths)
    return local_paths[0]


def download_sbr(destination=None):
    """Download an example of SBR+ Array and return the def path.

    Examples files are downloaded to a persistent cache to avoid
    re-downloading the same file twice.

    Parameters
    ----------
    destination : str, optional
        Path for downloading files. The default is the user's temp folder.

    Returns
    -------
    str
        Path to the example file.

    Examples
    --------
    Download an example result file and return the path of the file.

    >>> import ansys.aedt.core
    >>> path = ansys.aedt.core.downloads.download_antenna_array()
    >>> path
    'C:/Users/user/AppData/local/temp/pyaedtexamples/FiniteArray_Radome_77GHz_3D_CADDM.aedt'
    """

    local_paths = []
    _download_file("pyaedt/sbr", "Cassegrain.aedt", destination, local_paths)
    return local_paths[0]


def download_sbr_time(destination=None):
    """Download an example of SBR+ Time domain animation and return the def path.

    Examples files are downloaded to a persistent cache to avoid
    re-downloading the same file twice.

    Parameters
    ----------
    destination : str, optional
        Path for downloading files. The default is the user's temp folder.

    Returns
    -------
    str
        Path to the example file.

    Examples
    --------
    Download an example result file and return the path of the file.

    >>> import ansys.aedt.core
    >>> path = ansys.aedt.core.downloads.download_sbr_time()
    >>> path
    'C:/Users/user/AppData/local/temp/pyaedtexamples/sbr/poc_scat_small.aedt'
    """

    return _download_file("pyaedt/sbr", "poc_scat_small.aedt", destination)


def download_icepak(destination=None):
    """Download an example of Icepak Array and return the def path.

    Examples files are downloaded to a persistent cache to avoid
    re-downloading the same file twice.

    Parameters
    ----------
    destination : str, optional
        Path for downloading files. The default is the user's temp folder.

    Returns
    -------
    str
        Path to the example file.

    Examples
    --------
    Download an example result file and return the path of the file.

    >>> import ansys.aedt.core
    >>> path = ansys.aedt.core.downloads.download_icepak()
    >>> pathavoid
    'C:/Users/user/AppData/local/temp/pyaedtexamples/Graphic_Card.aedt'
    """
    _download_file("pyaedt/icepak", "Graphics_card.aedt", destination)
    return _download_file("pyaedt/icepak", "Graphics_card.aedt", destination)


def download_icepak_3d_component(destination=None):  # pragma: no cover
    """Download an example of Icepak Array and return the def pathsw.

    Examples files are downloaded to a persistent cache to avoid
    re-downloading the same file twice.

    Parameters
    ----------
    destination : str, optional
        Path for downloading files. The default is the user's temp folder.

    Returns
    -------
    str
        Path to PCBAssembly the example file.
    str
        Path to QFP2 the example file.

    Examples
    --------
    Download an example result file and return the path of the file.

    >>> import ansys.aedt.core
    >>> path1, path2 = ansys.aedt.core.downloads.download_icepak_3d_component()
    >>> path1
    'C:/Users/user/AppData/local/temp/pyaedtexamples/PCBAssembly.aedt',
    """
    local_paths = []
    _download_file("pyaedt/icepak_3dcomp//PCBAssembly.aedb", destination=destination)
    _download_file("pyaedt/icepak_3dcomp", "PCBAssembly.aedt", destination, local_paths)
    _download_file("icepak_3dcomp", "QFP2.aedt", destination, local_paths)
    return local_paths


def download_via_wizard(destination=None):
    """Download an example of Hfss Via Wizard and return the def path.

    Examples files are downloaded to a persistent cache to avoid
    re-downloading the same file twice.

    Parameters
    ----------
    destination : str, optional
        Path for downloading files. The default is the user's temp folder.

    Returns
    -------
    str
        Path to the example file.

    Examples
    --------
    Download an example result file and return the path of the file.

    >>> import ansys.aedt.core
    >>> path = ansys.aedt.core.downloads.download_via_wizard()
    >>> path
    'C:/Users/user/AppData/local/temp/pyaedtexamples/Graphic_Card.aedt'
    """

    return _download_file("pyaedt/via_wizard", "viawizard_vacuum_FR4.aedt", destination)


def download_touchstone(destination=None):
    """Download an example of touchstone File and return the def path.

    Examples files are downloaded to a persistent cache to avoid
    re-downloading the same file twice.

    Parameters
    ----------
    destination : str, optional
        Path for downloading files. The default is the user's temp folder.

    Returns
    -------
    str
        Path to the example file.

    Examples
    --------
    Download an example result file and return the path of the file.
    >>> import ansys.aedt.core
    >>> path = ansys.aedt.core.downloads.download_touchstone()
    >>> path
    'C:/Users/user/AppData/local/temp/pyaedtexamples/ssn_ssn.s6p'
    """
    local_paths = []
    _download_file("pyaedt/touchstone", "SSN_ssn.s6p", destination, local_paths)
    return local_paths[0]


def download_sherlock(destination=None):
    """Download an example of sherlock needed files and return the def path.

    Examples files are downloaded to a persistent cache to avoid
    re-downloading the same file twice.

    Parameters
    ----------
    destination : str, optional
        Path for downloading files. The default is the user's temp folder.

    Returns
    -------
    str
        Path to the example file.

    Examples
    --------
    Download an example result file and return the path of the file.

    >>> import ansys.aedt.core
    >>> path = ansys.aedt.core.downloads.download_sherlock()
    """
    if not destination:
        destination = EXAMPLES_PATH
    local_paths = []
    _download_file("pyaedt/sherlock", "MaterialExport.csv", destination, local_paths)
    _download_file("pyaedt/sherlock", "TutorialBoardPartsList.csv", destination, local_paths)
    _download_file("pyaedt/sherlock", "SherlockTutorial.aedt", destination, local_paths)
    _download_file("pyaedt/sherlock", "TutorialBoard.stp", destination, local_paths)
    _download_file("pyaedt/sherlock/SherlockTutorial.aedb", "edb.def", destination, local_paths)

    return os.path.join(destination, "sherlock")


def download_leaf(destination=None):
    """Download an example of Nissan leaf files and return the def path.

    Examples files are downloaded to a persistent cache to avoid
    re-downloading the same file twice.

    Parameters
    ----------
    destination : str, optional
        Path for downloading files. The default is the user's temp folder.

    Returns
    -------
    (str, str)
        Path to the 30DH_20C_smooth and BH_Arnold_Magnetics_N30UH_80C tabular material data file file.

    Examples
    --------
    Download an example result file and return the path of the file.

    >>> import ansys.aedt.core
    >>> path = ansys.aedt.core.downloads.download_leaf(r"c:\temp")
    >>> path
    ('C:/temp/BH_Arnold_Magnetics_N30UH_80C.tab', 'C:/temp/BH_Arnold_Magnetics_N30UH_80C.tab')
    """
    if not destination:
        destination = EXAMPLES_PATH
    local_paths = []
    _download_file("pyaedt/nissan", "30DH_20C_smooth.tab", destination, local_paths)
    _download_file("pyaedt/nissan", "BH_Arnold_Magnetics_N30UH_80C.tab", destination, local_paths)

    return local_paths[0], local_paths[1]


def download_custom_reports(force_download=False, destination=None):
    """Download an example of CISPR25 with customer reports json template files.

    Examples files are downloaded to a persistent cache to avoid
    re-downloading the same file twice.

    Parameters
    ----------
    force_download : bool
        Force to delete cache and download files again.
    destination : str, optional
        Path for downloading files. The default is the user's temp folder.

    Returns
    -------
    str
        Path to the example folder containing all example files.

    Examples
    --------
    Download an example result file and return the path of the file.
    >>> import ansys.aedt.core
    >>> path = ansys.aedt.core.downloads.download_custom_reports(force_download=True)
    >>> path
    'C:/Users/user/AppData/local/temp/custom_reports'
    """
    if not destination:
        destination = EXAMPLES_PATH
    if force_download:
        local_path = os.path.join(destination, "custom_reports")
        if os.path.exists(local_path):
            shutil.rmtree(local_path, ignore_errors=True)
    download_file("pyaedt/custom_reports", destination=destination)

    return os.path.join(destination, "custom_reports")


def download_3dcomponent(force_download=False, destination=None):
    """Download an example of 3d component array with json template files.

    Examples files are downloaded to a persistent cache to avoid
    re-downloading the same file twice.

    Parameters
    ----------
    force_download : bool
        Force to delete cache and download files again.
    destination : str, optional
        Path for downloading files. The default is the user's temp folder.

    Returns
    -------
    str
        Path to the example folder containing all example files.

    Examples
    --------
    Download an example result file and return the path of the file.
    >>> import ansys.aedt.core
    >>> path = ansys.aedt.core.downloads.download_3dcomponent(force_download=True)
    >>> path
    'C:/Users/user/AppData/local/temp/array_3d_component'
    """
    if not destination:
        destination = EXAMPLES_PATH
    if force_download:
        local_path = os.path.join(destination, "array_3d_component")
        if os.path.exists(local_path):
            shutil.rmtree(local_path, ignore_errors=True)
    download_file("pyaedt/array_3d_component", destination=destination)
    return os.path.join(destination, "array_3d_component")


def download_FSS_3dcomponent(force_download=False, destination=None):
    """Download an example of 3d component array with json template files.

    Examples files are downloaded to a persistent cache to avoid
    re-downloading the same file twice.

    Parameters
    ----------
    force_download : bool
        Force to delete cache and download files again.
    destination : str, optional
        Path for downloading files. The default is the user's temp folder.

    Returns
    -------
    str
        Path to the example folder containing all example files.

    Examples
    --------
    Download an example result file and return the path of the file.
    >>> import ansys.aedt.core
    >>> path = ansys.aedt.core.downloads.download_FSS_3dcomponent(force_download=True)
    >>> path
    'C:/Users/user/AppData/local/temp/array_3d_component'
    """
    if not destination:  # pragma: no cover
        destination = EXAMPLES_PATH
    if force_download:  # pragma: no cover
        local_path = os.path.join(destination, "fss_3d_component")
        if os.path.exists(local_path):  # pragma: no cover
            shutil.rmtree(local_path, ignore_errors=True)
    download_file("pyaedt/fss_3d_component", destination=destination)
    return os.path.join(destination, "fss_3d_component")


def download_multiparts(destination=None):
    """Download an example of 3DComponents Multiparts.

    Examples files are downloaded to a persistent cache to avoid
    re-downloading the same file twice.

    Parameters
    ----------
    destination : str, optional
        Path for downloading files. The default is the user's temp folder.

    Returns
    -------
    str
        Path to the example file.

    Examples
    --------
    Download an example result file and return the path of the file.

    >>> import ansys.aedt.core
    >>> path = ansys.aedt.core.downloads.download_multiparts()
    >>> path
    'C:/Users/user/AppData/local/temp/multiparts/library'
    """
    if not destination:
        destination = EXAMPLES_PATH
    dest_folder = os.path.join(destination, "multiparts")
    if os.path.exists(os.path.join(dest_folder, "library")):
        shutil.rmtree(os.path.join(dest_folder, "library"), ignore_errors=True)
    _download_file("pyaedt/multiparts", "library.zip", destination)
    if os.path.exists(os.path.join(destination, "multiparts", "library.zip")):
        unzip(os.path.join(destination, "multiparts", "library.zip"), dest_folder)
    return os.path.join(dest_folder, "library")


def download_twin_builder_data(file_name, force_download=False, destination=None):
    """Download a Twin Builder example data file.

    Examples files are downloaded to a persistent cache to avoid
    downloading the same file twice.

    Parameters
    ----------
    file_name : str
        Path of the file in the Twin Builder folder.
    force_download : bool, optional
        Force to delete file and download file again. Default value is ``False``.
    destination : str, optional
        Path to download files to. The default is the user's temporary folder.

    Returns
    -------
    str
        Path to the folder containing all Twin Builder example data files.

    Examples
    --------
    Download an example result file and return the path of the file.
    >>> import ansys.aedt.core
    >>> path = ansys.aedt.core.downloads.download_twin_builder_data(file_name="Example1.zip",force_download=True)
    >>> path
    'C:/Users/user/AppData/local/temp/twin_builder'
    """
    if not destination:
        destination = EXAMPLES_PATH
    if force_download:
        local_path = os.path.join(destination, os.path.join("twin_builder", file_name))
        if os.path.exists(local_path):
            os.unlink(local_path)
    _download_file("pyaedt/twin_builder", file_name, destination)
    return os.path.join(destination, "twin_builder")


@pyaedt_function_handler(filename="name", directory="source")
def download_file(source, name=None, destination=None):
    """
    Download a file or files from the online examples repository.

    Files are downloaded from the
    :ref:`example-data<https://github.com/ansys/example-data/tree/main/pyaedt>`_ repository
    to a local destination. If ``name`` is not specified, the full directory path
    will be copied to the local drive.

    Parameters
    ----------
    source : str
        Directory name in the Ansys ``example-data`` repository from which the example
        data is to be retrieved. If the ``pyaedt/`` prefix
        is not part of ``directory`` the path will be automatically prepended.
    name : str, optional
        File name to download. By default all files in ``directory``
        will be downloaded.
    destination : str, optional
        Path where the files will be saved locally. Default is the user temp folder.

    Returns
    -------
    str
        Path to the local example file or folder.

    Examples
    --------
    Download an example result file and return the path of the file.

    >>> import ansys.aedt.core
    >>> path = ansys.aedt.core.downloads.download_file("motorcad", "IPM_Vweb_Hairpin.mot")
    >>> path
    'C:/Users/user/AppData/local/temp/PyAEDTExamples/motorcad'
    """
    local_paths = []
    _download_file(source, name, destination, local_paths)
    if name:
        return list(set(local_paths))[0]
    else:
        if not destination:
            destination = EXAMPLES_PATH
        destination_dir = os.path.join(destination, source)
        return destination_dir


def unzip(source_filename, dest_dir):
    with zipfile.ZipFile(source_filename) as zf:
        zf.extractall(dest_dir)
