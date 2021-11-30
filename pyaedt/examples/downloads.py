"""Download example datasets from https://github.com/pyansys/example-data"""
import os
import os.path
import shutil
import zipfile
import tempfile

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


def _retrieve_file(url, filename, directory):
    """Download a file from a url"""
    # First check if file has already been downloaded
    local_path = os.path.join(EXAMPLES_PATH, directory, os.path.basename(filename))
    local_path_no_zip = local_path.replace(".zip", "")
    if os.path.isfile(local_path_no_zip) or os.path.isdir(local_path_no_zip):
        return local_path_no_zip

    # grab the correct url retriever
    if is_ironpython:
        urlretrieve = urllib.urlretrieve
    else:
        urlretrieve = urllib.request.urlretrieve

    dirpath = os.path.dirname(local_path)
    if not os.path.isdir(EXAMPLES_PATH):
        os.mkdir(EXAMPLES_PATH)
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
            command = "\"" + os.path.join(os.getenv(versions[0]), "commonfiles", "CPython", cpython[0], "winx64",
                                          "Release", "python", "python.exe") + "\""
            commandargs = os.path.join(os.path.dirname(local_path), "download.py")
            command += " \"" + commandargs + "\""
            with open(os.path.join(os.path.dirname(local_path), "download.py"), "w") as f:
                f.write("import urllib.request\n")
                f.write("urlretrieve = urllib.request.urlretrieve\n")
                f.write("import urllib.request\n")
                f.write("url = r\"{}\"\n".format(url))
                f.write("local_path = r\"{}\"\n".format(local_path))
                f.write("urlretrieve(url, local_path)\n")
            print(command)
            os.system(command)
    else:
        _, resp = urlretrieve(url, local_path)
    return local_path


def _download_file(directory, filename):
    url = _get_file_url(directory, filename)
    local_path = _retrieve_file(url, filename, directory)

    return local_path


###############################################################################
# front-facing functions


def download_aedb():
    """Download an example of AEDB File and return the def path.

    Examples files are downloaded to a persistent cache to avoid
    re-downloading the same file twice.

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
    _download_file("edb/Galileo.aedb", "GRM32ER72A225KA35_25C_0V.sp")

    return _download_file("edb/Galileo.aedb", "edb.def")


def download_netlist():
    """Download an example of netlist File and return the def path.
    Examples files are downloaded to a persistent cache to avoid
    re-downloading the same file twice.

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

    return _download_file("netlist", "netlist_small.cir")


def download_antenna_array():
    """Download an example of Antenna Array and return the def path.

    Examples files are downloaded to a persistent cache to avoid
    re-downloading the same file twice.

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

    return _download_file("array_antenna", "FiniteArray_Radome_77GHz_3D_CADDM.aedt")


def download_sbr():
    """Download an example of SBR+ Array and return the def path.

    Examples files are downloaded to a persistent cache to avoid
    re-downloading the same file twice.

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

    return _download_file("sbr", "Cassegrain.aedt")


def download_icepak():
    """Download an example of Icepak Array and return the def path.

    Examples files are downloaded to a persistent cache to avoid
    re-downloading the same file twice.

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

    return _download_file("icepak", "Graphics_card.aedt")

def download_via_wizard():
    """Download an example of Hfss Via Wizard and return the def path.

    Examples files are downloaded to a persistent cache to avoid
    re-downloading the same file twice.

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

    return _download_file("via_wizard", "viawizard_vacuum_FR4.aedt")

def download_touchstone():
    """Download an example of touchstone File and return the def path.

    Examples files are downloaded to a persistent cache to avoid
    re-downloading the same file twice.

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

    return _download_file("touchstone", "SSN_ssn.s6p")


def download_sherlock():
    """Download an example of sherlock needed files and return the def path.

    Examples files are downloaded to a persistent cache to avoid
    re-downloading the same file twice.

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
    _download_file("sherlock", "MaterialExport.csv")
    _download_file("sherlock", "TutorialBoardPartsList.csv")
    _download_file("sherlock", "SherlockTutorial.aedt")
    _download_file("sherlock", "TutorialBoard.stp")
    _download_file("sherlock/SherlockTutorial.aedb", "edb.def")

    return os.path.join(EXAMPLES_PATH, "sherlock")


def download_multiparts():
    """Download an example of 3DComponents Multiparts.

    Examples files are downloaded to a persistent cache to avoid
    re-downloading the same file twice.

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
    dest_folder = os.path.join(EXAMPLES_PATH, "multiparts")
    if os.path.exists(os.path.join(dest_folder, "library")):
        shutil.rmtree(os.path.join(dest_folder, "library"), ignore_errors=True)
    _download_file("multiparts", "library.zip")
    if os.path.exists(os.path.join(EXAMPLES_PATH, "multiparts", "library.zip")):
        unzip(os.path.join(EXAMPLES_PATH, "multiparts", "library.zip"), dest_folder)
    return os.path.join(dest_folder, "library")


def unzip(source_filename, dest_dir):
    with zipfile.ZipFile(source_filename) as zf:
        zf.extractall(dest_dir)
