import socket
import os
import sys
import time

from pyaedt import is_ironpython
if is_ironpython:
    pyaedt_path = os.path.normpath(os.path.abspath(os.path.dirname(__file__)))
    sys.path.append(os.path.join(pyaedt_path, "third_party", "ironpython"))

import rpyc
from rpyc.utils.server import ThreadedServer
from pyaedt.rpc.rpyc_services import GlobalService
import rpyc.core.consts

# Maximum Stream message size. Set to 256MB
rpyc.core.consts.STREAM_CHUNK = 256000000

def launch_server(port=18000, ansysem_path=None, non_graphical=False):
    """Starts an rpyc servers an start listening on specified port. This method has to run on server machine.

    Parameters
    ----------
    port : int, optional
        Port rpyc_server will listen.
    ansysem_path : str, optional
        Full path to the AEDT installation directory. This parameter is needed for
        IronPython on Linux only.
    non_graphical : bool, optional
        Either to start AEDT in graphical or non-graphical mode. This
        setting is needed for IronPython on Linux connections only.
    Examples
    --------
    >>> from pyaedt.common_rpc import launch_server
    >>> launch_server( port=18000)

    """
    if os.name == "posix":
        os.environ["PYAEDT_SERVER_AEDT_PATH"] = ansysem_path
        os.environ["PYAEDT_SERVER_AEDT_NG"] = str(non_graphical)
    hostname = socket.gethostname()
    safe_attrs = {'__abs__', '__add__', '__and__', '__bool__', '__class__', '__code__', '__cmp__', '__contains__',
                  '__delitem__', '__delslice__', '__div__', '__divmod__', '__doc__', '__eq__', '__float__',
                  '__floordiv__', '__func__', '__ge__', "__getmodule", "__cache", "__weakref__", '__dict__',
                  '__getitem__', '__getslice__', '__gt__', '__hash__', '__hex__', '__iadd__', '__iand__', '__idiv__',
                  '__ifloordiv__',
                  '__ilshift__', '__imod__', '__imul__', '__index__', '__int__', '__invert__', '__ior__', '__ipow__',
                  '__irshift__', '__isub__', '__iter__', '__itruediv__', '__ixor__', '__le__', '__len__', '__long__',
                  '__lshift__', '__lt__', '__mod__', '__mul__', '__name__', '__ne__', '__neg__', '__new__',
                  '__nonzero__',
                  '__oct__', '__or__', '__pos__', '__pow__', '__radd__', '__rand__', '__rdiv__', '__rdivmod__',
                  '__repr__',
                  '__rfloordiv__', '__rlshift__', '__rmod__', '__rmul__', '__ror__', '__rpow__', '__rrshift__',
                  '__rshift__', '__rsub__', '__rtruediv__', '__rxor__', '__setitem__', '__setslice__', '__str__',
                  '__sub__',
                  '__truediv__', '__xor__', 'next', '__length_hint__', '__enter__', '__exit__', '__next__',
                  '__format__'}
    t = ThreadedServer(GlobalService, hostname=hostname, port=port,
                       protocol_config={'sync_request_timeout': None, 'allow_public_attrs': True, 'allow_setattr': True,
                                        'safe_attrs': safe_attrs,
                                        'allow_delattr': True})
    print("Starting Server on Port {} on {}.".format(port, hostname))
    t.start()


def connect(server_name, aedt_client_port):
    """Connect to an existing aedt server session.

    Parameters
    ----------
    server_name : str
        name of the remote machine to connect.
    aedt_client_port : int
        port on which rpyc_server is running inside AEDT

    Returns
    -------
    rpyc object.
    """
    try:
        return rpyc.connect(server_name, aedt_client_port, config={'sync_request_timeout': None})
    except:
        return "Error. No connection. Check if AEDT is running and if the port number is correct."


def client(server_name, server_port=18000, beta_options=None):
    """Starts an rpyc client and connects to a remote machine.

    Parameters
    ----------
    server_name : str
        name of the remote machine to connect.
    server_port : int, optional
        port on which rpyc_server is running.
    beta_options : list, optional
        list of beta options to apply to new service.

    Returns
    -------
    rpyc object.

    Examples
    --------
    Windows CPython Example.

    >>> from pyaedt.common_rpc import client
    >>> cl1 = client(server_name="server_name")
    >>> hfss = cl1.root.hfss(specified_version="2021.2")

    Linux Ironpython CPython Example.

    >>> from pyaedt.common_rpc import client
    >>> cl1 = client(server_name="server_name", ansysem_path="path/to/aedt/executable/folder", non_graphical=True)
    >>> hfss = cl1.root.hfss()

    Linux CPython Example.
    >>> from pyaedt.common_rpc import client
    >>> cl2 = client("my_server")
    >>> script_to_run = ["from pyaedt import Hfss", "hfss =Hfss()"]
    >>> cl2.root.run_script(script_to_run, ansysem_path = "/path/to/AnsysEMxxx/Linux64")

    Linux CPython Example 2.
    >>> from pyaedt.common_rpc import client
    >>> cl2 = client("my_server")
    >>> script_to_run = "/path/to/script.py"
    >>> cl2.root.run_script(script_to_run, ansysem_path = "/path/to/AnsysEMxxx/Linux64")

    """
    c = rpyc.connect(server_name, server_port, config={'sync_request_timeout': None})
    port = c.root.start_service(server_name, beta_options)
    if not port:
        return "Error Connecting to the Server. Check the server name and port and retry."
    print("Connecting to new session of Electronics Desktop on port {}. Please Wait.".format(port))
    if port:
        time.sleep(20)
        timeout = 30
        while timeout > 0:
            try:
                c1 = rpyc.connect(server_name, port, config={'sync_request_timeout': None})
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
    #else:
    #    return rpyc.connect(server_name, port, config={'sync_request_timeout': None})


def upload(localpath, remotepath, server_name, server_port=18000):
    """Uploads a file or a directory to the given remote path.

    Parameters
    ----------
    localpath : str
        The local file or directory.
    remotepath : str
        The remote path.
    server_name : str
        Name of the server to which connect.
    server_port : int
        Port Number.
    """
    if os.path.isdir(localpath):
        _upload_dir(localpath, remotepath, server_name, server_port)
    elif os.path.isfile(localpath):
        _upload_file(localpath, remotepath, server_name, server_port)


def download(remotepath, localpath, server_name, server_port=18000):
    """Download a file or a directory from given remote path to local path.

    Parameters
    ----------
    remotepath : str
        The remote path.
    localpath : str
        The local file or directory.
    server_name : str
        Name of the server to which connect.
    server_port : int
        Port Number.
    """
    if os.path.isdir(remotepath):
        _download_dir(remotepath, localpath, server_name, server_port)
    elif os.path.isfile(remotepath):
        _download_file(localpath, remotepath, server_name, server_port)


def _upload_file(local_file, remote_file, server_name, server_port=18000):
    c = rpyc.connect(server_name, server_port, config={'sync_request_timeout': None})
    if c.root.path_exists(remote_file):
        return "File already existing on the server."
    with open(local_file, 'rb') as f:
        lines = f.readlines()
        new_file = c.root.create(remote_file)
        for line in lines:
            new_file.write(line)
        new_file.close()


def _upload_dir(localpath, remotepath, server_name, server_port=18000):
    c = rpyc.connect(server_name, server_port, config={'sync_request_timeout': None})
    if c.root.path_exists(remotepath):
        return "Folder already existing on the server."
    c.root.makedirs(remotepath)
    for fn in os.listdir(localpath):
        lfn = os.path.join(localpath, fn)
        rfn = os.path.join(remotepath, fn)
        _upload_file(lfn, rfn, server_name, server_port=18000)


def _download_file(remote_file, local_file, server_name, server_port=18000):
    c = rpyc.connect(server_name, server_port, config={'sync_request_timeout': None})
    if os.path.exists(local_file):
        return "File already existing on the server."
    remote = c.root.open(remote_file)
    lines = remote.readlines()
    with open(local_file, 'wb') as new_file:
        for line in lines:
            new_file.write(line)
        new_file.close()


def _download_dir(remotepath, localpath,  server_name, server_port=18000):
    c = rpyc.connect(server_name, server_port, config={'sync_request_timeout': None})
    if os.path.exists(localpath):
        return "Folder already existing on the local machine."
    if not os.path.isdir(localpath):
        os.makedirs(localpath)
    for fn in c.root.listdir(remotepath):
        lfn = os.path.join(localpath, fn)
        rfn = os.path.join(remotepath, fn)
        _download_file(rfn, lfn, server_name, server_port=18000)
