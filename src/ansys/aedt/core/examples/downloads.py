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

from pathlib import Path
import shutil
import ssl
import tempfile
from typing import Callable
from typing import Optional
from typing import Tuple
from typing import Union
from urllib.parse import quote
from urllib.parse import urljoin
from urllib.parse import urlparse
import urllib.request
import zipfile

from ansys.aedt.core.aedt_logger import pyaedt_logger
from ansys.aedt.core.generic.general_methods import pyaedt_function_handler
from ansys.aedt.core.generic.settings import settings
from ansys.aedt.core.internal.errors import AEDTRuntimeError

EXAMPLES_DATA_REPO = "https://github.com/ansys/example-data/raw/main"
EXAMPLES_PATH = Path(tempfile.gettempdir()) / "PyAEDTExamples"


def delete_downloads():
    """Delete all downloaded examples to free space or update the files."""
    shutil.rmtree(EXAMPLES_PATH, ignore_errors=True)


def _build_safe_url(github_relative_path: str) -> str:
    """Safely construct a URL using the user-provided input.

    This function ensures that the user-provided path does not contain an unsupported scheme
    (like 'file://', 'ftp://', or a full URL), preventing the risk of overriding the base
    or accessing unintended resources.

    Parameters
    ----------
    github_relative_path : str
        A relative path provided by the user, such as ``"pyaedt/sbr/Cassegrain.aedt"``.

    Returns
    -------
    str
        The safely constructed URL combining the hardcoded base and the user path.
    """
    # Strip dangerous schemes
    parsed = urlparse(github_relative_path)
    if parsed.scheme:  # pragma: no cover
        raise ValueError(f"User path contains a scheme: {parsed.scheme}")

    url = urljoin(EXAMPLES_DATA_REPO + "/", quote(github_relative_path) + "/")

    return url


def _download_file(
    github_relative_path: str,
    local_path: Optional[Union[str, Path]] = None,
    strip_prefix: Optional[Union[str, Path]] = None,
) -> Path:
    """Download a file from a URL."""
    url = _build_safe_url(github_relative_path)
    relative_path: Path = Path(github_relative_path.strip("/"))

    if strip_prefix:
        relative_path = relative_path.relative_to(Path(strip_prefix))

    if not local_path:
        local_path = EXAMPLES_PATH / relative_path
    else:
        local_path = Path(local_path) / relative_path
    local_path.parent.mkdir(parents=True, exist_ok=True)

    try:
        if not local_path.exists():
            ssl_context = ssl.create_default_context()
            pyaedt_logger.debug(f"Downloading file from URL {url}")
            with (
                urllib.request.urlopen(url, context=ssl_context) as response,  # nosec
                open(local_path, "wb") as out_file,
            ):
                shutil.copyfileobj(response, out_file)
        else:
            pyaedt_logger.debug(f"File already exists in {local_path}. Skipping download.")
    except Exception as e:
        raise AEDTRuntimeError(f"Failed to download file from URL {url}.") from e

    return local_path.resolve()


def _copy_local_example(
    source_relative_path: str,
    target_path: Optional[Union[str, Path]] = None,
) -> Path:  # pragma: no cover
    """Copy a folder from a local copy of the examples repo."""
    dst = Path(target_path) / Path(source_relative_path).name
    dst.mkdir(parents=True, exist_ok=True)
    pyaedt_logger.debug(f"Retrieving local folder from '{settings.local_example_folder}'")
    source_folder = Path(settings.local_example_folder) / source_relative_path
    for p in source_folder.rglob("*"):
        target = dst / p.relative_to(source_folder)
        if p.is_dir():
            target.mkdir(parents=True, exist_ok=True)
        else:
            try:
                shutil.copy2(p, target)
            except Exception as e:
                raise AEDTRuntimeError(f"Failed to copy {str(p)}.") from e
    return dst


def _download_folder(
    github_relative_path: str,
    local_path: Optional[Union[str, Path]] = None,
    filter_func: Optional[Callable[[str], bool]] = None,
    strip_prefix: Optional[Union[str, Path]] = None,
) -> Path:
    """Download a folder from the example data repository."""
    import json
    import re

    url = _build_safe_url(github_relative_path)
    relative_path: Path = Path(github_relative_path.strip("/"))

    if strip_prefix:
        relative_path = relative_path.relative_to(Path(strip_prefix))

    if not local_path:
        local_path = EXAMPLES_PATH
    else:
        local_path = Path(local_path)

    base_local_path = local_path / relative_path
    base_local_path.mkdir(parents=True, exist_ok=True)

    ssl_context = ssl.create_default_context()
    with urllib.request.urlopen(url, context=ssl_context) as response:  # nosec
        data = response.read().decode("utf-8").splitlines()

    try:
        tree = [i for i in data if '"payload"' in i][0]
        match = re.search(r'>({"payload".+)</script>', tree)
        json_data = json.loads(match.group(1))
        items = json_data["payload"]["tree"]["items"]
        for item in items:
            # Skip if filter_func is provided and returns False
            if filter_func and filter_func(item["path"]):
                pyaedt_logger.debug(f"Skipping {item['path']} due to filter")
                continue
            if item["contentType"] == "directory":
                pyaedt_logger.debug(f"Calling download folder {item['path']} into {local_path}")
                _download_folder(item["path"], local_path, filter_func=filter_func, strip_prefix=strip_prefix)
            else:
                pyaedt_logger.debug(f"Calling download file {item['path']} into {local_path}")
                _download_file(item["path"], local_path, strip_prefix=strip_prefix)
    except Exception as e:
        raise AEDTRuntimeError(f"Failed to download {relative_path}.") from e

    return base_local_path


###############################################################################


@pyaedt_function_handler(destination="local_path")
def download_aedb(local_path: Optional[Union[str, Path]] = None) -> str:
    """Download an example of AEDB file and return the def path.

    If example files have already been downloaded, the download is
    skipped.

    Parameters
    ----------
    local_path : str or :class:`pathlib.Path`, optional
        Path for downloading files. The default is the user's temp folder.

    Returns
    -------
    str
        Path to the example folder containing example files.

    Examples
    --------
    Download an example result file and return the path of the file.
    >>> import ansys.aedt.core
    >>> path = ansys.aedt.core.examples.downloads.download_aedb()
    >>> path
    r'C:/Users/user/AppData/Local/Temp/PyAEDTExamples/ANSYS-HSD_V1.aedbb'
    """
    from ansys.aedt.core.examples.downloads import _download_file

    _download_file("pyaedt/edb/ANSYS-HSD_V1.aedb/GRM32ER72A225KA35_25C_0V.sp", local_path, strip_prefix="pyaedt/edb")
    edbdef_path = _download_file("pyaedt/edb/ANSYS-HSD_V1.aedb/edb.def", local_path, strip_prefix="pyaedt/edb")
    return str(edbdef_path.parent)


@pyaedt_function_handler(destination="local_path")
def download_edb_merge_utility(force_download: bool = False, local_path: Optional[Union[str, Path]] = None) -> str:
    """Download an example of WPF Project which allows to merge 2aedb files.

    If example files have already been downloaded, the download is
    skipped.

    Parameters
    ----------
    force_download : bool
        Force to delete cache and download files again.
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
    >>> path = ansys.aedt.core.examples.downloads.download_edb_merge_utility(force_download=True)
    >>> path
    'C:/Users/user/AppData/Local/Temp/PyAEDTExamples/wpf_edb_merge/merge_wizard.py'
    """
    if not local_path:
        local_path = EXAMPLES_PATH
    local_path = Path(local_path)

    if force_download:
        path_to_remove = local_path / "wpf_edb_merge"
        if path_to_remove.exists():
            pyaedt_logger.debug(f"Deleting {path_to_remove} to force download.")
            shutil.rmtree(path_to_remove, ignore_errors=True)

    local_path = _download_folder(
        "pyaedt/wpf_edb_merge", local_path, filter_func=lambda f: f.endswith(".gitignore"), strip_prefix="pyaedt"
    )
    script_path = local_path / "merge_wizard.py"
    return str(script_path)


@pyaedt_function_handler(destination="local_path")
def download_netlist(local_path: Optional[Union[str, Path]] = None) -> str:
    """Download an example of netlist File and return the def path.

    If example files have already been downloaded, the download is
    skipped.

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
    >>> path = ansys.aedt.core.examples.downloads.download_netlist()
    >>> path
    'C:/Users/user/AppData/Local/Temp/PyAEDTExamples/netlist_small.cir'
    """
    cir_file_path = _download_file(
        "pyaedt/netlist/netlist_small.cir", local_path=local_path, strip_prefix="pyaedt/netlist"
    )
    return str(cir_file_path)


@pyaedt_function_handler(destination="local_path")
def download_antenna_array(local_path: Optional[Union[str, Path]] = None) -> str:
    """Download an example of Antenna Array and return the def path.

    If example files have already been downloaded, the download is
    skipped.

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
    >>> path = ansys.aedt.core.examples.downloads.download_antenna_array()
    >>> path
    'C:/Users/user/AppData/Local/Temp/PyAEDTExamples/FiniteArray_Radome_77GHz_3D_CADDM.aedt'
    """
    aedt_file_path = _download_file(
        "pyaedt/array_antenna/FiniteArray_Radome_77GHz_3D_CADDM.aedt", local_path, strip_prefix="pyaedt/array_antenna"
    )
    return str(aedt_file_path)


@pyaedt_function_handler(destination="local_path")
def download_sbr(local_path: Optional[Union[str, Path]] = None) -> str:
    """Download an example of SBR+ Array and return the def path.

    If example files have already been downloaded, the download is
    skipped.

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
    >>> path = ansys.aedt.core.examples.downloads.download_antenna_array()
    >>> path
    'C:/Users/user/AppData/Local/Temp/PyAEDTExamples/sbr/Cassegrain.aedt'
    """
    aedt_file_path = _download_file("pyaedt/sbr/Cassegrain.aedt", local_path, strip_prefix="pyaedt")
    return str(aedt_file_path)


@pyaedt_function_handler(destination="local_path")
def download_sbr_time(local_path: Optional[Union[str, Path]] = None) -> str:
    """Download an example of SBR+ Time domain animation and return the def path.

    If example files have already been downloaded, the download is
    skipped.

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
    >>> path = ansys.aedt.core.examples.downloads.download_sbr_time()
    >>> path
    'C:/Users/user/AppData/Local/Temp/PyAEDTExamples/sbr/poc_scat_small.aedt'
    """
    aedt_file_path = _download_file("pyaedt/sbr/poc_scat_small.aedt", local_path=local_path, strip_prefix="pyaedt")
    return str(aedt_file_path)


@pyaedt_function_handler(destination="local_path")
def download_icepak(local_path: Optional[Union[str, Path]] = None) -> str:
    """Download an example of Icepak Array and return the def path.

    If example files have already been downloaded, the download is
    skipped.

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
    >>> path = ansys.aedt.core.examples.downloads.download_icepak()
    >>> pathavoid
    'C:/Users/user/AppData/Local/Temp/PyAEDTExamples/Graphic_Card.aedt'
    """
    aedt_file_path = _download_file(
        "pyaedt/icepak/Graphics_card.aedt", local_path=local_path, strip_prefix="pyaedt/icepak"
    )
    return str(aedt_file_path)


@pyaedt_function_handler(destination="local_path")
def download_icepak_3d_component(local_path: Optional[Union[str, Path]] = None) -> str:  # pragma: no cover
    """Download an example of Icepak Array and return the def pathsw.

    If example files have already been downloaded, the download is
    skipped.

    Parameters
    ----------
    local_path : str or :class:`pathlib.Path`, optional
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
    >>> path1, path2 = ansys.aedt.core.examples.downloads.download_icepak_3d_component()
    >>> path1
    'C:/Users/user/AppData/Local/Temp/PyAEDTExamples/PCBAssembly.aedt'
    >>> path2
    'C:/Users/user/AppData/Local/Temp/PyAEDTExamples/QFP2.aedt'
    """
    folder_path = _download_folder("pyaedt/icepak_3dcomp", local_path=local_path, strip_prefix="pyaedt/icepak_3dcomp")
    return str(folder_path / "PCBAssembly.aedt"), str(folder_path / "QFP2.aedt")


@pyaedt_function_handler(destination="local_path")
def download_via_wizard(local_path: Optional[Union[str, Path]] = None) -> str:
    """Download an example of Hfss Via Wizard and return the def path.

    If example files have already been downloaded, the download is
    skipped.

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
    >>> path = ansys.aedt.core.examples.downloads.download_via_wizard()
    >>> path
    'C:/Users/user/AppData/Local/Temp/PyAEDTExamples/viawizard_vacuum_FR4.aedt'
    """
    aedt_file = _download_file(
        "pyaedt/via_wizard/viawizard_vacuum_FR4.aedt", local_path=local_path, strip_prefix="pyaedt/via_wizard"
    )
    return str(aedt_file)


@pyaedt_function_handler(destination="local_path")
def download_touchstone(local_path: Optional[Union[str, Path]] = None) -> str:
    """Download an example of touchstone File and return the def path.

    If example files have already been downloaded, the download is
    skipped.

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
    >>> path = ansys.aedt.core.examples.downloads.download_touchstone()
    >>> path
    'C:/Users/user/AppData/Local/Temp/PyAEDTExamples/SSN_ssn.s6p'
    """
    s6p_file = _download_file("pyaedt/touchstone/SSN_ssn.s6p", local_path=local_path, strip_prefix="pyaedt/touchstone")
    return str(s6p_file)


@pyaedt_function_handler(destination="local_path")
def download_sherlock(local_path: Optional[Union[str, Path]] = None) -> str:
    """Download an example of sherlock needed files and return the def path.

    If example files have already been downloaded, the download is
    skipped.

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
    >>> path = ansys.aedt.core.examples.downloads.download_sherlock()
    >>> path
    'C:/Users/user/AppData/Local/Temp/PyAEDTExamples/sherlock'
    """
    folder_path = _download_folder(
        "pyaedt/sherlock", local_path=local_path, filter_func=lambda f: "SherkockTutorial" in f, strip_prefix="pyaedt"
    )
    return str(folder_path)


@pyaedt_function_handler(destination="local_path")
def download_leaf(local_path: Optional[Union[str, Path]] = None) -> Tuple[str, str]:
    """Download an example of Nissan leaf files and return the def path.

    If example files have already been downloaded, the download is
    skipped.

    Parameters
    ----------
    local_path : str or :class:`pathlib.Path`, optional
        Path for downloading files. The default is the user's temp folder.

    Returns
    -------
    (str, str)
        Path to the 30DH_20C_smooth and BH_Arnold_Magnetics_N30UH_80C tabular material data file file.

    Examples
    --------
    Download an example result file and return the path of the file.

    >>> import ansys.aedt.core
    >>> path = ansys.aedt.core.examples.downloads.download_leaf(r"c:\temp")
    >>> path
    ('C:/temp/30DH_20C_smooth.tab', 'C:/temp/BH_Arnold_Magnetics_N30UH_80C.tab')
    """
    smooth_tab_path = _download_file("pyaedt/nissan/30DH_20C_smooth.tab", local_path, strip_prefix="pyaedt/nissan")
    magnetics_tab_path = _download_file(
        "pyaedt/nissan/BH_Arnold_Magnetics_N30UH_80C.tab", local_path, strip_prefix="pyaedt/nissan"
    )
    return str(smooth_tab_path), str(magnetics_tab_path)


@pyaedt_function_handler(destination="local_path")
def download_custom_reports(force_download: bool = False, local_path: Optional[Union[str, Path]] = None) -> str:
    """Download an example of CISPR25 with customer reports json template files.

    If example files have already been downloaded, the download is
    skipped.

    Parameters
    ----------
    force_download : bool
        Force to delete cache and download files again.
    local_path : str or :class:`pathlib.Path`, optional
        Path for downloading files. The default is the user's temp folder.

    Returns
    -------
    str
        Path to the example folder containing all example files.

    Examples
    --------
    Download an example result file and return the path of the file.

    >>> import ansys.aedt.core
    >>> path = ansys.aedt.core.examples.downloads.download_custom_reports(force_download=True)
    >>> path
    'C:/Users/user/AppData/Local/Temp/PyAEDTExamples/custom_reports'
    """
    if not local_path:
        local_path = EXAMPLES_PATH
    local_path = Path(local_path)

    if force_download:
        path_to_remove = local_path / "custom_reports"
        if path_to_remove.exists():
            pyaedt_logger.debug(f"Deleting {path_to_remove} to force download.")
            shutil.rmtree(path_to_remove, ignore_errors=True)

    folder_path = _download_folder("pyaedt/custom_reports", local_path=local_path, strip_prefix="pyaedt")
    return str(folder_path)


@pyaedt_function_handler(destination="local_path")
def download_3dcomponent(force_download=False, local_path: Optional[Union[str, Path]] = None) -> str:
    """Download an example of 3d component array with json template files.

    If example files have already been downloaded, the download is
    skipped.

    Parameters
    ----------
    force_download : bool
        Force to delete cache and download files again.
    local_path : str or :class:`pathlib.Path`, optional
        Path for downloading files. The default is the user's temp folder.

    Returns
    -------
    str
        Path to the example folder containing all example files.

    Examples
    --------
    Download an example result file and return the path of the file.
    >>> import ansys.aedt.core
    >>> path = ansys.aedt.core.examples.downloads.download_3dcomponent(force_download=True)
    >>> path
    'C:/Users/user/AppData/Local/Temp/PyAEDTExamples/array_3d_component'
    """
    if not local_path:
        local_path = EXAMPLES_PATH
    local_path = Path(local_path)

    if force_download:
        path_to_remove = local_path / "array_3d_component"
        if path_to_remove.exists():
            pyaedt_logger.debug(f"Deleting {path_to_remove} to force download.")
            shutil.rmtree(path_to_remove, ignore_errors=True)

    folder_path = _download_folder("pyaedt/array_3d_component", local_path=local_path, strip_prefix="pyaedt")
    return str(folder_path)


@pyaedt_function_handler(destination="local_path")
def download_fss_3dcomponent(force_download=False, local_path: Optional[Union[str, Path]] = None) -> str:
    """Download an example of 3d component array with json template files.

    If example files have already been downloaded, the download is
    skipped.

    Parameters
    ----------
    force_download : bool
        Force to delete cache and download files again.
    local_path : str or :class:`pathlib.Path`, optional
        Path for downloading files. The default is the user's temp folder.

    Returns
    -------
    str
        Path to the example folder containing all example files.

    Examples
    --------
    Download an example result file and return the path of the file.
    >>> import ansys.aedt.core
    >>> path = ansys.aedt.core.examples.downloads.download_FSS_3dcomponent(force_download=True)
    >>> path
    'C:/Users/user/AppData/Local/Temp/PyAEDTExamples/fss_3d_component'
    """
    if not local_path:
        local_path = EXAMPLES_PATH
    local_path = Path(local_path)

    if force_download:
        path_to_remove = local_path / "fss_3d_component"
        if path_to_remove.exists():
            pyaedt_logger.debug(f"Deleting {path_to_remove} to force download.")
            shutil.rmtree(path_to_remove, ignore_errors=True)

    fodler_path = _download_folder("pyaedt/fss_3d_component", local_path=local_path, strip_prefix="pyaedt")
    return str(fodler_path)


@pyaedt_function_handler(destination="local_path")
def download_multiparts(local_path: Optional[Union[str, Path]] = None) -> str:
    """Download an example of 3DComponents Multiparts.

    If example files have already been downloaded, the download is
    skipped.

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
    >>> path = ansys.aedt.core.examples.downloads.download_multiparts()
    >>> path
    'C:/Users/user/AppData/Local/Temp/PyAEDTExamples/multiparts/library'
    """
    if not local_path:
        local_path = EXAMPLES_PATH
    local_path = Path(local_path)

    if (local_path / "multiparts" / "library").exists():
        pyaedt_logger.debug(f"Deleting {local_path / 'multiparts' / 'library'} to force download.")
        shutil.rmtree(local_path / "multiparts" / "library", ignore_errors=True)

    zip_file = _download_file("pyaedt/multiparts/library.zip", local_path=local_path, strip_prefix="pyaedt")
    unzip(zip_file, local_path / "multiparts")
    return str(local_path / "multiparts" / "library")


@pyaedt_function_handler(destination="local_path")
def download_twin_builder_data(
    file_name: Optional[str] = None, force_download=False, local_path: Optional[Union[str, Path]] = None
) -> str:
    """Download a Twin Builder example data file.

    Examples files are downloaded to a persistent cache to avoid
    downloading the same file twice.

    Parameters
    ----------
    file_name : str, optional
        Name of the file to download. If not specified, all files in the folder.
    force_download : bool, optional
        Force to delete file and download file again. Default value is ``False``.
    local_path : str or :class:`pathlib.Path`, optional
        Path to download files to. The default is the user's temporary folder.

    Returns
    -------
    str
        Path to the folder containing all Twin Builder example data files.

    Examples
    --------
    Download an example result file and return the path of the file.
    >>> import ansys.aedt.core
    >>> path = ansys.aedt.core.examples.downloads.download_twin_builder_data(force_download=True)
    >>> path
    'C:/Users/user/AppData/Local/Temp/PyAEDTExamples/twin_builder'
    """
    if not local_path:
        local_path = EXAMPLES_PATH
    local_path = Path(local_path)

    if force_download:
        path_to_remove = local_path / "twin_builder"
        if file_name:
            path_to_remove = path_to_remove / file_name
        if path_to_remove.exists():
            pyaedt_logger.debug(f"Deleting {path_to_remove} to force download.")
            shutil.rmtree(path_to_remove, ignore_errors=True)

    if file_name:

        def filter_func(f):
            return not f.endswith(file_name)

    else:
        filter_func = None

    folder_path = _download_folder(
        "pyaedt/twin_builder", local_path=local_path, filter_func=filter_func, strip_prefix="pyaedt"
    )

    if file_name:
        return str(folder_path / file_name)
    return str(folder_path)


@pyaedt_function_handler(filename="name", directory="source")
def download_file(source: str, name: Optional[str] = None, local_path: Optional[Union[str, Path]] = None) -> str:
    """Download a file or files from the online examples repository.

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
    local_path : str or :class:`pathlib.Path`, optional
        Path where the files will be saved locally. Default is the user temp folder.

    Returns
    -------
    str
        Path to the local example file or folder.

    Examples
    --------
    Download an example result file and return the path of the file.

    >>> import ansys.aedt.core
    >>> path = ansys.aedt.core.examples.downloads.download_file("motorcad", "IPM_Vweb_Hairpin.mot")
    >>> path
    'C:/Users/user/AppData/local/temp/PyAEDTExamples/motorcad/IPM_Vweb_Hairpin.mot'
    """
    if not source.startswith("pyaedt/"):
        source = "pyaedt/" + source
    if settings.use_local_example_data:  # pragma: no cover
        # Use a local copy (i.e. repo) of the examples folder.
        if name:
            source = source + "/" + name
        path = _copy_local_example(source, local_path)
    else:
        if not name:  # Download all files in the folder if name is not provided.
            path = _download_folder(source, local_path, strip_prefix="pyaedt")
        else:
            source = source + "/" + name
            path = _download_file(source, local_path, strip_prefix="pyaedt")

    if settings.remote_rpc_session:  # pragma: no cover
        path = Path(settings.remote_rpc_session_temp_folder) / path.name
        if not settings.remote_rpc_session.filemanager.pathexists(settings.remote_rpc_session_temp_folder):
            settings.remote_rpc_session.filemanager.makedirs(settings.remote_rpc_session_temp_folder)
        settings.remote_rpc_session.filemanager.upload(local_path, path)

    return str(path)


def unzip(source_filename, dest_dir):
    with zipfile.ZipFile(source_filename) as zf:
        zf.extractall(dest_dir)
    print(dest_dir)
