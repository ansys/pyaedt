"""Download example datasets from https://github.com/pyansys/example-data"""
import shutil
import os
import urllib.request

from pyaedt.generic.general_methods import  generate_unique_name
EXAMPLE_REPO = 'https://github.com/pyansys/example-data/raw/master/pyaedt/'
EXAMPLES_PATH = os.path.join(os.environ["TEMP"], "PyAEDTExamples")


def delete_downloads():
    """Delete all downloaded examples to free space or update the files"""
    shutil.rmtree(EXAMPLES_PATH, ignore_errors=True)


def _get_file_url(directory, filename):
    if not filename:
        return EXAMPLE_REPO + '/'.join([directory])
    else:
        return EXAMPLE_REPO + '/'.join([directory, filename])


def _retrieve_file(url, filename, directory):
    """Download a file from a url"""
    # First check if file has already been downloaded
    local_path = os.path.join(EXAMPLES_PATH, directory, os.path.basename(filename))
    local_path_no_zip = local_path.replace('.zip', '')
    if os.path.isfile(local_path_no_zip) or os.path.isdir(local_path_no_zip):
        return local_path_no_zip

    # grab the correct url retriever
    urlretrieve = urllib.request.urlretrieve

    dirpath = os.path.dirname(local_path)
    if not os.path.isdir(EXAMPLES_PATH):
        os.mkdir(EXAMPLES_PATH)
    if not os.path.isdir(dirpath):
        os.makedirs(dirpath, exist_ok=True)

    # Perform download
    _, resp = urlretrieve(url, local_path)
    return local_path


def _download_file(directory, filename):
    url = _get_file_url(directory, filename)
    local_path = _retrieve_file(url, filename, directory)

    return local_path

###############################################################################
# front-facing functions

def download_aedb() -> str:
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
    _download_file('edb/Galileo.aedb', 'GRM32ER72A225KA35_25C_0V.sp')

    return _download_file('edb/Galileo.aedb', 'edb.def')

def download_netlist() -> str:
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

    return _download_file('netlist', 'netlist_small.cir')


def download_touchstone() -> str:
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

    return _download_file('touchstone', 'SSN_ssn.s6p')


def download_sherlock() -> str:
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
    _download_file('sherlock', 'MaterialExport.csv')
    _download_file('sherlock', 'TutorialBoardPartsList.csv')
    _download_file('sherlock', 'SherlockTutorial.aedt')
    _download_file('sherlock', 'TutorialBoard.stp')
    _download_file('sherlock/SherlockTutorial.aedb', 'edb.def')

    return os.path.join(EXAMPLES_PATH, "sherlock")

