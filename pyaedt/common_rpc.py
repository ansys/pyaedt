import os
import signal
import socket
import sys
import tempfile
import time

from pyaedt import AedtLogger
from pyaedt import is_ironpython
from pyaedt import settings
from pyaedt.generic.general_methods import convert_remote_object
from pyaedt.misc import list_installed_ansysem

# import sys
from pyaedt.rpc.rpyc_services import FileManagement
from pyaedt.rpc.rpyc_services import GlobalService
from pyaedt.rpc.rpyc_services import ServiceManager
from pyaedt.rpc.rpyc_services import check_port

if is_ironpython:
    pyaedt_path = os.path.normpath(os.path.abspath(os.path.dirname(__file__)))
    from pyaedt.third_party.ironpython import rpyc_27 as rpyc
    from pyaedt.third_party.ironpython.rpyc_27.core import consts
    from pyaedt.third_party.ironpython.rpyc_27.utils.server import OneShotServer
    from pyaedt.third_party.ironpython.rpyc_27.utils.server import ThreadedServer

else:
    import rpyc
    from rpyc.core import consts
    from rpyc.utils.server import OneShotServer
    from rpyc.utils.server import ThreadedServer


logger = AedtLogger()
# Maximum Stream message size. Set to 256MB
consts.STREAM_CHUNK = 256000000

from pyaedt import is_ironpython

if os.name == "posix" and is_ironpython:
    import subprocessdotnet as subprocess
else:
    import subprocess


def pyaedt_service_manager(port=17878, aedt_version=None, student_version=False):
    """Starts an RPyC server on CPython and listens on a specified port.

    This method must run on a server machine.

    Parameters
    ----------
    port : int, optional
        Port that the RPyC server is to listen on.
    aedt_version : str, optional
        Version of Aedt to instantiate with server. Default is latest available version installed on the machine.
    student_version : bool, optional
        Either to initialize Student version AEDT or Commercial version.

    Examples
    --------
    >>> from pyaedt.common_rpc import pyaedt_service_manager
    >>> pyaedt_service_manager()

    """
    port1 = check_port(port)
    if port == 0:
        print("Error. No ports are available.")
        return False
    if port1 != port:
        print("Port {} is already in use. Starting the server on port {}.".format(port, port1))
    aa = list_installed_ansysem()
    if aedt_version:
        if student_version:
            v = "ANSYSEMSV_ROOT{}".format(aedt_version[-4:].replace(".", ""))
        else:
            v = "ANSYSEM_ROOT{}".format(aedt_version[-4:].replace(".", ""))

        valid_version = v
    else:
        if aa:
            valid_version = aa[0]
        else:
            raise Exception("no ANSYSEM_ROOTXXX environment variable defined.")

    os.environ["PYAEDT_SERVER_AEDT_PATH"] = os.environ[valid_version]
    os.environ["PYAEDT_SERVER_AEDT_NG"] = "True"
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
        ServiceManager,
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
    logger.info("Starting the server on port {} on {}.".format(port, hostname))
    t.start()


def launch_server(port=18000, ansysem_path=None, non_graphical=False, threaded=True):
    """Starts an RPyC server and listens on a specified port.

    This method must run on a server machine only.

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
    threaded : bool, optional

    Examples
    --------
    >>> from pyaedt.common_rpc import launch_server
    >>> launch_server()

    """
    port1 = check_port(port)
    if port == 0:
        print("Error. No ports are available.")
        return False
    if port1 != port:
        print("Port {} is already in use. Starting the server on port {}.".format(port, port1))
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
    if threaded:
        service = ThreadedServer
    else:
        service = OneShotServer
    t = service(
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
    signal.signal(signal.SIGINT, lambda signum, frame: t.close())
    signal.signal(signal.SIGTERM, lambda signum, frame: t.close())

    t.start()


def create_session(server_name, client_port=None):
    """
    Connect to an existing AEDT server session.

    Parameters
    ----------
    server_name : str
        Name of the remote machine to connect to.
    client_port : int
        Port that the RPyC server will run.

    Returns
    -------
    RPyC object.
    """
    try:
        client = rpyc.connect(
            server_name,
            settings.remote_rpc_service_manager_port,
            config={"allow_public_attrs": True, "sync_request_timeout": None},
        )
        if not client_port:
            client_port = client.root.check_port()
        port = client.root.start_service(client_port)
        time.sleep(1)
        cl = connect(server_name, port)
        logger.info("Created new session on port %s", port)

        return cl
    except:
        msg = "Error. No connection exists."
        msg += " Check if pyaedt_service_manager is running and if the port number is correct."
        logger.error(msg)
        return False


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
        try:
            client.aedt = client.root.aedt_grpc
            client.edb = client.root.edb
            client.open_file = client.root.open
            client.create_file = client.root.create
            client.list_dir = client.root.listdir
            client.makedirs = client.root.makedirs
            client.pathexists = client.root.pathexists
            client.close_session = client.root.stop
        except AttributeError:
            pass
        settings.remote_rpc_session = client
        settings.remote_rpc_session_temp_folder = os.path.join(
            tempfile.gettempdir(), server_name + "_" + str(aedt_client_port)
        )
        if not os.path.exists(settings.remote_rpc_session_temp_folder):
            os.makedirs(settings.remote_rpc_session_temp_folder)
        return client
    except:
        logger.error("Error. No connection exists. Check if AEDT is running and if the port number is correct.")
        return False


def client(server_name, server_port=18000, beta_options=None, use_aedt_relative_path=False):
    """Starts an RPyC client and connects to a remote machine.

    .. deprecated:: 0.5.0
        No need to use it anymore from 0.5.0 anymore.

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


def launch_ironpython_server(
    aedt_path=None, non_graphical=False, port=18000, launch_client=True, use_aedt_relative_path=False
):
    """Start a process in IronPython and launch the RPyC server on the specified port given an AEDT path on Linux.

    .. deprecated:: 0.5.0
        No need to use it anymore from 0.5.0 since pyaedt supports now CPython.

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
