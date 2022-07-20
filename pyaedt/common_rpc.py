import logging
import os
import shutil
import socket
import sys
import time

from pyaedt import is_ironpython
from pyaedt.generic.general_methods import convert_remote_object
from pyaedt.misc import list_installed_ansysem

logging.basicConfig(stream=sys.stderr, level=logging.INFO)
logger = logging.getLogger(__name__)
# import sys

if is_ironpython:
    pyaedt_path = os.path.normpath(os.path.abspath(os.path.dirname(__file__)))
    # sys.path.insert(0, os.path.join(pyaedt_path, "third_party", "ironpython"))
    from pyaedt.rpc.rpyc_services import GlobalService
    from pyaedt.rpc.rpyc_services import check_port
    from pyaedt.third_party.ironpython import rpyc_27 as rpyc
    from pyaedt.third_party.ironpython.rpyc_27.core import consts
    from pyaedt.third_party.ironpython.rpyc_27.utils.server import ThreadedServer
else:
    import rpyc
    from rpyc.core import consts
    from rpyc.utils.server import ThreadedServer

    from pyaedt.rpc.rpyc_services import GlobalService
    from pyaedt.rpc.rpyc_services import check_port

# Maximum Stream message size. Set to 256MB
consts.STREAM_CHUNK = 256000000

from pyaedt import is_ironpython

if os.name == "posix" and is_ironpython:
    import subprocessdotnet as subprocess
else:
    import subprocess


def launch_server(port=18000, ansysem_path=None, non_graphical=False):
    """Starts an RPyC server and listens on a specified port.

    This method must run on a server machine.

    Parameters
    ----------
    port : int, optional
        Port that the RPyC server is to listen on.
    ansysem_path : str, optional
        Full path to the AEDT installation directory. The default is
        ``None``. This parameter is needed for IronPython on Linux
        connections only.
    non_graphical : bool, optional
        Whether to start AEDT in non-graphical mode. The default is ``False``,
        which means AEDT starts in graphical mode. This parameter is needed
        for IronPython on Linux connections only.

    Examples
    --------
    >>> from pyaedt.common_rpc import launch_server
    >>> launch_server( port=18000)

    """
    port1 = check_port(port)
    if port == 0:
        print("Error. No ports are available.")
        return False
    if port1 != port:
        print("Port {} is already in use. Starting the server on port {}.".format(port, port1))
    if os.name == "posix":
        if not ansysem_path:
            aa = list_installed_ansysem()
            if aa:
                ansysem_path = os.environ[aa[0]]
            else:
                raise Exception("no ANSYSEM_ROOTXXX environment variable defined.")
        os.environ["PYAEDT_SERVER_AEDT_PATH"] = ansysem_path
        os.environ["PYAEDT_SERVER_AEDT_NG"] = str(non_graphical)
        os.environ["ANS_NO_MONO_CLEANUP"] = str(1)
        os.environ["ANS_NODEPCHECK"] = str(1)

    hostname = socket.gethostname()
    safe_attrs = {
        "__abs__",
        "__add__",
        "__and__",
        "__bool__",
        "__class__",
        "__code__",
        "__cmp__",
        "__contains__",
        "__delitem__",
        "__delslice__",
        "__div__",
        "__divmod__",
        "__doc__",
        "__eq__",
        "__float__",
        "__floordiv__",
        "__func__",
        "__ge__",
        "__getmodule",
        "__cache",
        "__weakref__",
        "__dict__",
        "__getitem__",
        "__getslice__",
        "__gt__",
        "__hash__",
        "__hex__",
        "__iadd__",
        "__iand__",
        "__idiv__",
        "__ifloordiv__",
        "__ilshift__",
        "__imod__",
        "__imul__",
        "__index__",
        "__int__",
        "__invert__",
        "__ior__",
        "__ipow__",
        "__irshift__",
        "__isub__",
        "__iter__",
        "__itruediv__",
        "__ixor__",
        "__le__",
        "__len__",
        "__long__",
        "__lshift__",
        "__lt__",
        "__mod__",
        "__mul__",
        "__name__",
        "__ne__",
        "__neg__",
        "__new__",
        "__nonzero__",
        "__oct__",
        "__or__",
        "__pos__",
        "__pow__",
        "__radd__",
        "__rand__",
        "__rdiv__",
        "__rdivmod__",
        "__repr__",
        "__rfloordiv__",
        "__rlshift__",
        "__rmod__",
        "__rmul__",
        "__ror__",
        "__rpow__",
        "__rrshift__",
        "__rshift__",
        "__rsub__",
        "__rtruediv__",
        "__rxor__",
        "__setitem__",
        "__setslice__",
        "__str__",
        "__sub__",
        "__truediv__",
        "__xor__",
        "next",
        "__length_hint__",
        "__enter__",
        "__exit__",
        "__next__",
        "__format__",
    }
    t = ThreadedServer(
        GlobalService,
        hostname=hostname,
        port=port1,
        protocol_config={
            "sync_request_timeout": None,
            "allow_public_attrs": True,
            "allow_setattr": True,
            "safe_attrs": safe_attrs,
            "allow_delattr": True,
            "logger": logger,
        },
    )
    print("Starting the server on port {} on {}.".format(port, hostname))
    t.start()


def connect(server_name, aedt_client_port):
    """
    Connect to an existing AEDT server session.

    Parameters
    ----------
    server_name : str
        Name of the remote machine to connect to.
    aedt_client_port : int
        Port that the RPyC server is running on inside AEDT.

    Returns
    -------
    RPyC object.
    """
    try:
        client = rpyc.connect(
            server_name, aedt_client_port, config={"allow_public_attrs": True, "sync_request_timeout": None}
        )
        client.root.redirect(sys.stdout)
        client.filemanager = FileManagement(client)
        return client
    except:
        return "Error. No connection exists. Check if AEDT is running and if the port number is correct."


def client(server_name, server_port=18000, beta_options=None, use_aedt_relative_path=False):
    """Starts an RPyC client and connects to a remote machine.

    Parameters
    ----------
    server_name : str
        Name of the remote machine to connect.
    server_port : int, optional
        Port that the RPyC server is running on.
    beta_options : list, optional
        List of beta options to apply to the new service. The default is ``None``.
    use_aedt_relative_path : bool, optional
        Whether to use AEDT executable full path or relative path call. This parameter is needed
        if a Linux environment is defined.
    Returns
    -------
    RPyC object.

    Examples
    --------
    Windows CPython Example:

    >>> from pyaedt.common_rpc import client
    >>> cl1 = client(server_name="server_name")
    >>> hfss = cl1.root.hfss(specified_version="2021.2")

    Linux IronPython CPython Example:

    >>> from pyaedt.common_rpc import client
    >>> cl1 = client(server_name="server_name", ansysem_path="path/to/aedt/executable/folder", non_graphical=True)
    >>> hfss = cl1.root.hfss()

    Linux CPython Example 1:

    >>> from pyaedt.common_rpc import client
    >>> cl2 = client("my_server")
    >>> script_to_run = ["from pyaedt import Hfss", "hfss =Hfss()"]
    >>> cl2.root.run_script(script_to_run, ansysem_path = "/path/to/AnsysEMxxx/Linux64")

    Linux CPython Example 2:

    >>> from pyaedt.common_rpc import client
    >>> cl2 = client("my_server")
    >>> script_to_run = "/path/to/script.py"
    >>> cl2.root.run_script(script_to_run, ansysem_path = "/path/to/AnsysEMxxx/Linux64")

    """
    t = 120
    c = None
    while t > 0:
        try:
            c = rpyc.connect(server_name, server_port, config={"sync_request_timeout": None})
            if c.root:
                t = 0
        except:
            t -= 1
            time.sleep(1)
    if not c:
        print("Failed to connect to {} on port {}. Check the settings".format(server_name, server_port))
        return False
    port = c.root.start_service(server_name, beta_options, use_aedt_relative_path=use_aedt_relative_path)
    if not port:
        return "Error connecting to the server. Check the server name and port and retry."
    print("Connecting to a new session of AEDT on port {}. Wait.".format(port))
    if port:
        time.sleep(20)
        timeout = 80
        while timeout > 0:
            try:
                c1 = rpyc.connect(server_name, port, config={"sync_request_timeout": None})
                c1.convert_remote_object = convert_remote_object
                if c1:
                    if beta_options:
                        c1._beta_options = beta_options
                    return c1
            except:
                time.sleep(2)
                timeout -= 2
        return "Error. No connection."
    else:
        return "Error. No connection."


class FileManagement(object):
    """Class to manage file transfer."""

    def __init__(self, client):
        self.client = client

    def upload(self, localpath, remotepath):
        """Upload a file or a directory to the given remote path.

        Parameters
        ----------
        localpath : str
            Path to the local file or directory.
        remotepath : str
            Remote path.
        """
        if os.path.isdir(localpath):
            self._upload_dir(localpath, remotepath)
        elif os.path.isfile(localpath):
            self._upload_file(localpath, remotepath)

    def download_folder(self, remotepath, localpath):
        """Download a directory from a given remote path to the local path.

        Parameters
        ----------
        remotepath : str
            Remote path.
        localpath : str
            Path to the local file or directory.
        """
        self._download_dir(remotepath, localpath)

    def download_file(self, remotepath, localpath):
        """Download a file from a given remote path to the local path.

        Parameters
        ----------
        remotepath : str
            Remote path.
        localpath : str
            Path to the local file or directory.
        """
        self._download_file(remotepath, localpath)

    def _upload_file(self, local_file, remote_file):
        if self.client.root.path_exists(remote_file):
            logger.error("File already exists on the server.")
            return False
        new_file = self.client.root.create(remote_file)
        local = open(local_file, "rb")
        shutil.copyfileobj(local, new_file)
        logger.info("File %s uploaded to %s", local_file, remote_file)

    def _upload_dir(self, localpath, remotepath):
        if self.client.root.path_exists(remotepath):
            logger.warning("Folder already exists on the server.")
        self.client.root.makedirs(remotepath)
        i = 0
        for fn in os.listdir(localpath):
            lfn = os.path.join(localpath, fn)
            rfn = remotepath + "/" + fn
            if os.path.isdir(rfn):
                self._upload_dir(lfn, rfn)
            else:
                self._upload_file(lfn, rfn)
            i += 1
        logger.info("Directory %s uploaded. %s files copied", localpath, i)

    def _download_file(self, remote_file, local_file):
        if os.path.exists(local_file):
            logger.warning("File already exists on the client.")
        remote = self.client.root.open(remote_file)
        new_file = open(local_file, "wb")
        shutil.copyfileobj(remote, new_file)
        logger.info("File %s downloaded to %s", remote_file, local_file)

    def _download_dir(self, remotepath, localpath):
        if os.path.exists(localpath):
            logger.warning("Folder already exists on the local machine.")
        if not os.path.isdir(localpath):
            os.makedirs(localpath)
        i = 0
        for fn in self.client.root.listdir(remotepath):
            lfn = os.path.join(localpath, fn)
            rfn = remotepath + "/" + fn
            if self.client.root.isdir(rfn):
                self._download_dir(rfn, lfn)
            else:
                self._download_file(rfn, lfn)
            i += 1
        logger.info("Directory %s downloaded. %s files copied", localpath, i)


def launch_ironpython_server(
    aedt_path=None, non_graphical=False, port=18000, launch_client=True, use_aedt_relative_path=False
):
    """Start a process in IronPython and launch the RPyC server on the specified port given an AEDT path on Linux.

    .. warning::
        Remote CPython to IronPython may have some limitations.
        Known issues are in the returned list and dictionary.
        For these known issues, using the method `client.conver_remote_object` is recommended.

    Parameters
    ----------
    aedt_path : str, optional
        AEDT path on Linux. The default is ``None``, in which case an ANSYSEM_ROOT2xx
        must be set up.
    non_graphical : bool, optional
        Whether to start AEDT in non-graphical mode. The default is ``False``, in which case
        AEDT is started in graphical mode.
    port : int, optional
        Port on which the RPyC server is to listen on. The default is ``18000``.
    launch_client : bool, optional
        Whether to launch the client. The default is ``True``.
    use_aedt_relative_path : bool, optional
       Whether to use the relative path to AEDT. The default is ``False``.
    port : int, optional
        Port number. The default is ``18000``.
    launch_client : bool, optional
        Whether to launch the client. The default is ``True.``
    use_aedt_relative_path : bool, optional
        Whether to use the AEDT executable full path or relative path call. This parameter is needed
        if the Linux environment is defined. The ``aedt_path`` parameter is still needed because it
        is necessary to retrieve the ``ipy64.exe`` full path.

    Returns
    -------
    RPyC object.

    Examples
    --------
    >>> from pyaedt.common_rpc import launch_ironpython_server
    >>> client = launch_ironpython_server("/path/to/AEDT/Linux64")
    >>> hfss = client.root.hfss()
    >>> box = hfss.modeler.create_box([0,0,0], [1,1,1])
    >>> my_face_list = client.convert_remote_object(box.faces)

    """
    if not aedt_path:
        aa = list_installed_ansysem()
        if aa:
            aedt_path = os.environ[aa[0]]
        else:
            raise Exception("No ANSYSEM_ROOTXXX environment variable is defined.")
    port1 = check_port(port)
    if port1 == 0:
        print("Error. No ports are available.")
        return False
    if non_graphical:
        val = 1
    else:
        val = 0
    command = [
        os.path.join(aedt_path, "common", "mono", "Linux64", "bin", "mono"),
        os.path.join(aedt_path, "common", "IronPython", "ipy64.exe"),
        os.path.join(os.path.dirname(__file__), "rpc", "local_server.py"),
        aedt_path,
        str(val),
        str(port1),
    ]
    if not os.path.exists(os.path.join(aedt_path, "common", "IronPython", "ipy64.exe")):
        print("Check the AEDT path and retry.")
        return False
    proc = subprocess.Popen(" ".join(command), shell=True)
    print("Process {} started on {}".format(proc.pid, socket.getfqdn()))
    print("Using port {}".format(port1))
    print("Warning: Remote CPython to IronPython may have some limitations.")
    print("Known issues are in the returned list and dictionary.")
    print("For these known issues, using the method client.convert_remote_object is recommended.")
    if proc and launch_client:
        return client(server_name=socket.getfqdn(), server_port=port1, use_aedt_relative_path=use_aedt_relative_path)
    return False
