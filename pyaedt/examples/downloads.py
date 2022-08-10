"""Download example datasets from https://github.com/pyansys/example-data"""
import os
import shutil
import tempfile
import zipfile

from pyaedt.generic.general_methods import is_ironpython
from pyaedt.misc import list_installed_ansysem

if is_ironpython:
    import urllib
else:
    import urllib.request

tmpfold = tempfile.gettempdir()
EXAMPLE_REPO = "https://github.com/pyansys/example-data/raw/master/pyaedt/"
EXAMPLES_PATH = os.path.join(tmpfold, "PyAEDTExamples")


def delete_downloads():
    """Delete all downloaded examples to free space or update the files."""
    shutil.rmtree(EXAMPLES_PATH, ignore_errors=True)


def _get_file_url(directory, filename):
    if not filename:
        return EXAMPLE_REPO + "/".join([directory])
    else:
        return EXAMPLE_REPO + "/".join([directory, filename])


def _retrieve_file(url, filename, directory, destination=None):
    """Download a file from a url"""
    # First check if file has already been downloaded
    if not destination:
        destination = EXAMPLES_PATH
    local_path = os.path.join(destination, directory, os.path.basename(filename))
    local_path_no_zip = local_path.replace(".zip", "")
    if os.path.isfile(local_path_no_zip) or os.path.isdir(local_path_no_zip):
        return local_path_no_zip

    # grab the correct url retriever
    if is_ironpython:
        urlretrieve = urllib.urlretrieve
    else:
        urlretrieve = urllib.request.urlretrieve

    dirpath = os.path.dirname(local_path)
    if not os.path.isdir(destination):
        os.mkdir(destination)
    if not os.path.isdir(dirpath):
        os.makedirs(dirpath)

    # Perform download
    if os.name == "posix":
        command = "wget {} -O {}".format(url, local_path)
        os.system(command)
    elif is_ironpython:
        versions = list_installed_ansysem()
        if versions:
            cpython = os.listdir(os.path.join(os.getenv(versions[0]), "commonfiles", "CPython"))
            command = (
                '"'
                + os.path.join(
                    os.getenv(versions[0]),
                    "commonfiles",
                    "CPython",
                    cpython[0],
                    "winx64",
                    "Release",
                    "python",
                    "python.exe",
                )
                + '"'
            )
            commandargs = os.path.join(os.path.dirname(local_path), "download.py")
            command += ' "' + commandargs + '"'
            with open(os.path.join(os.path.dirname(local_path), "download.py"), "w") as f:
                f.write("import urllib.request\n")
                f.write("urlretrieve = urllib.request.urlretrieve\n")
                f.write("import urllib.request\n")
                f.write('url = r"{}"\n'.format(url))
                f.write('local_path = r"{}"\n'.format(local_path))
                f.write("urlretrieve(url, local_path)\n")
            print(command)
            os.system(command)
    else:
        _, resp = urlretrieve(url, local_path)
    return local_path


def _download_file(directory, filename, destination=None):
    url = _get_file_url(directory, filename)
    local_path = _retrieve_file(url, filename, directory, destination)

    return local_path


###############################################################################
# front-facing functions


def download_aedb(destination=None):
    """Download an example of AEDB File and return the def path.

    Examples files are downloaded to a persistent cache to avoid
    re-downloading the same file twice.

    Parameters
    ----------
    destination : str, optional
        Path where files will be downloaded. Optional. Default is user temp folder.

    Returns
    -------
    str
        Path to the example file.

    Examples
    --------
    Download an example result file and return the path of the file
    >>> from pyaedt import examples
    >>> path = examples.download_aedb()
    >>> path
    'C:/Users/user/AppData/local/temp/Galileo.aedb'
    """
    _download_file("edb/Galileo.aedb", "GRM32ER72A225KA35_25C_0V.sp", destination)

    return _download_file("edb/Galileo.aedb", "edb.def", destination)


def download_edb_merge_utility(force_download=False, destination=None):
    """Download an example of WPF Project which allows to merge 2aedb files.

    Examples files are downloaded to a persistent cache to avoid
    re-downloading the same file twice.

    Parameters
    ----------
    force_download : bool
        Force to delete cache and download files again.
    destination : str, optional
        Path where files will be downloaded. Optional. Default is user temp folder.

    Returns
    -------
    str
        Path to the example file.

    Examples
    --------
    Download an example result file and return the path of the file
    >>> from pyaedt import examples
    >>> path = examples.download_edb_merge_utility(force_download=True)
    >>> path
    'C:/Users/user/AppData/local/temp/wpf_edb_merge/merge_wizard.py'
    """
    if not destination:
        destination = EXAMPLES_PATH
    if force_download:
        local_path = os.path.join(destination, "wpf_edb_merge")
        if os.path.exists(local_path):
            shutil.rmtree(local_path, ignore_errors=True)
    _download_file("wpf_edb_merge/board.aedb", "edb.def", destination)
    _download_file("wpf_edb_merge/package.aedb", "edb.def", destination)
    _download_file("wpf_edb_merge", "merge_wizard_settings.json", destination)

    return _download_file("wpf_edb_merge", "merge_wizard.py", destination)


def download_netlist(destination=None):
    """Download an example of netlist File and return the def path.
    Examples files are downloaded to a persistent cache to avoid
    re-downloading the same file twice.

    Parameters
    ----------
    destination : str, optional
        Path where files will be downloaded. Optional. Default is user temp folder.

    Returns
    -------
    str
        Path to the example file.

    Examples
    --------
    Download an example result file and return the path of the file

    >>> from pyaedt import examples
    >>> path = examples.download_netlist()
    >>> path
    'C:/Users/user/AppData/local/temp/pyaedtexamples/netlist_small.cir'
    """

    return _download_file("netlist", "netlist_small.cir", destination)


def download_antenna_array(destination=None):
    """Download an example of Antenna Array and return the def path.

    Examples files are downloaded to a persistent cache to avoid
    re-downloading the same file twice.

    Parameters
    ----------
    destination : str, optional
        Path where files will be downloaded. Optional. Default is user temp folder.

    Returns
    -------
    str
        Path to the example file.

    Examples
    --------

    Download an example result file and return the path of the file

    >>> from pyaedt import examples
    >>> path = examples.download_antenna_array()
    >>> path
    'C:/Users/user/AppData/local/temp/pyaedtexamples/FiniteArray_Radome_77GHz_3D_CADDM.aedt'
    """

    return _download_file("array_antenna", "FiniteArray_Radome_77GHz_3D_CADDM.aedt", destination)


def download_sbr(destination=None):
    """Download an example of SBR+ Array and return the def path.

    Examples files are downloaded to a persistent cache to avoid
    re-downloading the same file twice.

    Parameters
    ----------
    destination : str, optional
        Path where files will be downloaded. Optional. Default is user temp folder.

    Returns
    -------
    str
        Path to the example file.

    Examples
    --------
    Download an example result file and return the path of the file

    >>> from pyaedt import examples
    >>> path = examples.download_antenna_array()
    >>> path
    'C:/Users/user/AppData/local/temp/pyaedtexamples/FiniteArray_Radome_77GHz_3D_CADDM.aedt'
    """

    return _download_file("sbr", "Cassegrain.aedt", destination)


def download_sbr_time(destination=None):
    """Download an example of SBR+ Time domain animation and return the def path.

    Examples files are downloaded to a persistent cache to avoid
    re-downloading the same file twice.

    Parameters
    ----------
    destination : str, optional
        Path where files will be downloaded. Optional. Default is user temp folder.

    Returns
    -------
    str
        Path to the example file.

    Examples
    --------
    Download an example result file and return the path of the file

    >>> from pyaedt import examples
    >>> path = examples.download_sbr_time()
    >>> path
    'C:/Users/user/AppData/local/temp/pyaedtexamples/sbr/poc_scat_small.aedt'
    """

    return _download_file("sbr", "poc_scat_small.aedt", destination)


def download_icepak(destination=None):
    """Download an example of Icepak Array and return the def path.

    Examples files are downloaded to a persistent cache to avoid
    re-downloading the same file twice.

    Parameters
    ----------
    destination : str, optional
        Path where files will be downloaded. Optional. Default is user temp folder.

    Returns
    -------
    str
        Path to the example file.

    Examples
    --------
    Download an example result file and return the path of the file

    >>> from pyaedt import examples
    >>> path = examples.download_icepak()
    >>> path
    'C:/Users/user/AppData/local/temp/pyaedtexamples/Graphic_Card.aedt'
    """

    return _download_file("icepak", "Graphics_card.aedt", destination)


def download_via_wizard(destination=None):
    """Download an example of Hfss Via Wizard and return the def path.

    Examples files are downloaded to a persistent cache to avoid
    re-downloading the same file twice.

    Parameters
    ----------
    destination : str, optional
        Path where files will be downloaded. Optional. Default is user temp folder.

    Returns
    -------
    str
        Path to the example file.

    Examples
    --------
    Download an example result file and return the path of the file

    >>> from pyaedt import examples
    >>> path = examples.download_via_wizard()
    >>> path
    'C:/Users/user/AppData/local/temp/pyaedtexamples/Graphic_Card.aedt'
    """

    return _download_file("via_wizard", "viawizard_vacuum_FR4.aedt", destination)


def download_touchstone(destination=None):
    """Download an example of touchstone File and return the def path.

    Examples files are downloaded to a persistent cache to avoid
    re-downloading the same file twice.

    Parameters
    ----------
    destination : str, optional
        Path where files will be downloaded. Optional. Default is user temp folder.

    Returns
    -------
    str
        Path to the example file.

    Examples
    --------
    Download an example result file and return the path of the file
    >>> from pyaedt import examples
    >>> path = examples.download_touchstone()
    >>> path
    'C:/Users/user/AppData/local/temp/pyaedtexamples/ssn_ssn.s6p'
    """
    return _download_file("touchstone", "SSN_ssn.s6p", destination)


def download_sherlock(destination=None):
    """Download an example of sherlock needed files and return the def path.

    Examples files are downloaded to a persistent cache to avoid
    re-downloading the same file twice.

    Parameters
    ----------
    destination : str, optional
        Path where files will be downloaded. Optional. Default is user temp folder.

    Returns
    -------
    str
        Path to the example file.

    Examples
    --------
    Download an example result file and return the path of the file

    >>> from pyaedt import examples
    >>> path = examples.download_sherlock()
    >>> path
    'C:/Users/user/AppData/local/temp/Galileo.aedb'
    """
    if not destination:
        destination = EXAMPLES_PATH
    _download_file("sherlock", "MaterialExport.csv", destination)
    _download_file("sherlock", "TutorialBoardPartsList.csv", destination)
    _download_file("sherlock", "SherlockTutorial.aedt", destination)
    _download_file("sherlock", "TutorialBoard.stp", destination)
    _download_file("sherlock/SherlockTutorial.aedb", "edb.def", destination)

    return os.path.join(destination, "sherlock")


def download_leaf(destination=None):
    """Download an example of Nissan leaf files and return the def path.

    Examples files are downloaded to a persistent cache to avoid
    re-downloading the same file twice.

    Parameters
    ----------
    destination : str, optional
        Path where files will be downloaded. Optional. Default is user temp folder.

    Returns
    -------
    (str, str)
        Path to the 30DH_20C_smooth and BH_Arnold_Magnetics_N30UH_80C tabular material data file file.

    Examples
    --------
    Download an example result file and return the path of the file

    >>> from pyaedt import examples
    >>> path = examples.download_leaf(r"c:\temp")
    >>> path
    ('C:/temp/BH_Arnold_Magnetics_N30UH_80C.tab', 'C:/temp/BH_Arnold_Magnetics_N30UH_80C.tab')
    """
    if not destination:
        destination = EXAMPLES_PATH
    file1 = _download_file("nissan", "30DH_20C_smooth.tab", destination)
    file2 = _download_file("nissan", "BH_Arnold_Magnetics_N30UH_80C.tab", destination)

    return file1, file2


def download_custom_reports(force_download=False, destination=None):
    """Download an example of CISPR25 with customer reports json template files.

    Examples files are downloaded to a persistent cache to avoid
    re-downloading the same file twice.

    Parameters
    ----------
    force_download : bool
        Force to delete cache and download files again.
    destination : str, optional
        Path where files will be downloaded. Optional. Default is user temp folder.

    Returns
    -------
    str
        Path to the example folder containing all example files.

    Examples
    --------
    Download an example result file and return the path of the file
    >>> from pyaedt import examples
    >>> path = examples.download_custom_reports(force_download=True)
    >>> path
    'C:/Users/user/AppData/local/temp/custom_reports'
    """
    if not destination:
        destination = EXAMPLES_PATH
    if force_download:
        local_path = os.path.join(destination, "custom_reports")
        if os.path.exists(local_path):
            shutil.rmtree(local_path, ignore_errors=True)
    _download_file("custom_reports", "CISPR25_Radiated_Emissions_Example22R1.aedtz", destination)
    _download_file("custom_reports", "EyeDiagram_CISPR_Basic.json", destination)
    _download_file("custom_reports", "EyeDiagram_CISPR_Custom.json", destination)
    _download_file("custom_reports", "Spectrum_CISPR_Basic.json", destination)
    _download_file("custom_reports", "Spectrum_CISPR_Custom.json", destination)
    _download_file("custom_reports", "Transient_CISPR_Basic.json", destination)
    _download_file("custom_reports", "Transient_CISPR_Custom.json", destination)
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
        Path where files will be downloaded. Optional. Default is user temp folder.

    Returns
    -------
    str
        Path to the example folder containing all example files.

    Examples
    --------
    Download an example result file and return the path of the file
    >>> from pyaedt import examples
    >>> path = examples.download_3dcomponent(force_download=True)
    >>> path
    'C:/Users/user/AppData/local/temp/array_3d_component'
    """
    if not destination:
        destination = EXAMPLES_PATH
    if force_download:
        local_path = os.path.join(destination, "array_3d_component")
        if os.path.exists(local_path):
            shutil.rmtree(local_path, ignore_errors=True)
    _download_file("array_3d_component", "Circ_Patch_5GHz.a3dcomp", destination)
    _download_file("array_3d_component", "Circ_Patch_5GHz_hex.a3dcomp", destination)
    _download_file("array_3d_component", "array_simple.json", destination)
    return os.path.join(destination, "array_3d_component")


def download_multiparts(destination=None):
    """Download an example of 3DComponents Multiparts.

    Examples files are downloaded to a persistent cache to avoid
    re-downloading the same file twice.

    Parameters
    ----------
    destination : str, optional
        Path where files will be downloaded. Optional. Default is user temp folder.

    Returns
    -------
    str
        Path to the example file.

    Examples
    --------
    Download an example result file and return the path of the file

    >>> from pyaedt import examples
    >>> path = examples.download_multiparts()
    >>> path
    'C:/Users/user/AppData/local/temp/multiparts/library'
    """
    if not destination:
        destination = EXAMPLES_PATH
    dest_folder = os.path.join(destination, "multiparts")
    if os.path.exists(os.path.join(dest_folder, "library")):
        shutil.rmtree(os.path.join(dest_folder, "library"), ignore_errors=True)
    _download_file("multiparts", "library.zip", destination)
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
    Download an example result file and return the path of the file
    >>> from pyaedt import examples
    >>> path = examples.download_twin_builder_data(file_name="Example1.zip",force_download=True)
    >>> path
    'C:/Users/user/AppData/local/temp/twin_builder'
    """
    if not destination:
        destination = EXAMPLES_PATH
    if force_download:
        local_path = os.path.join(destination, os.path.join("twin_builder", file_name))
        if os.path.exists(local_path):
            os.unlink(local_path)
    _download_file("twin_builder", file_name, destination)
    return os.path.join(destination, "twin_builder")


def unzip(source_filename, dest_dir):
    with zipfile.ZipFile(source_filename) as zf:
        zf.extractall(dest_dir)
