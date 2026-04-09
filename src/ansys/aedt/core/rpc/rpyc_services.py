from __future__ import annotations

from dataclasses import dataclass
import logging
import os
from pathlib import Path
import shutil
import signal
import socket
import subprocess  # nosec
import sys
import tempfile
import time

import rpyc

from ansys.aedt.core import is_windows
from ansys.aedt.core.base import PyAedtBase
from ansys.aedt.core.desktop import _ServerArgs, _get_grpcsrv_args
from ansys.aedt.core.generic.general_methods import is_grpc_session_active
from ansys.aedt.core.generic.settings import is_linux
from ansys.aedt.core.internal.aedt_versions import aedt_versions
from ansys.aedt.core.internal.filesystem import is_safe_path

logging.basicConfig(stream=sys.stderr, level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class _AEDTGrpcInfo:
    """Class to store information about the AEDT gRPC server."""
    host: str
    port: int
    version: str

class FileManagement(PyAedtBase):
    """Class to manage file transfer."""

    def __init__(self, client) -> None:
        self.client = client

    def upload(self, localpath: str, remotepath: str, overwrite: bool=False) -> None:
        """Upload a file or a directory to the given remote path.

        Parameters
        ----------
        localpath : str
            Path to the local file or directory.
        remotepath : str
            Remote path.
        overwrite : bool, optional
            Either if overwrite the local file or not.
        """
        if os.path.isdir(localpath):
            self._upload_dir(localpath, remotepath)
        elif os.path.isfile(localpath):
            self._upload_file(localpath, remotepath)

    def download_folder(self, remotepath: str, localpath: str, overwrite: bool=True) -> None:
        """Download a directory from a given remote path to the local path.

        Parameters
        ----------
        remotepath : str
            Remote path.
        localpath : str
            Path to the local file or directory.
        overwrite : bool, optional
            Either if overwrite the local file or not.
        """
        self._download_dir(remotepath, localpath, overwrite=True)

    def download_file(self, remotepath: str, localpath: str, overwrite: bool=True) -> None:
        """Download a file from a given remote path to the local path.

        Parameters
        ----------
        remotepath : str
            Remote path.
        localpath : str
            Path to the local file or directory.
        overwrite : bool, optional
            Either if overwrite the local file or not.
        """
        self._download_file(remotepath, localpath, overwrite=overwrite)

    def _upload_file(self, local_file, remote_file, overwrite: bool=False) -> bool:
        if self.client.root.pathexists(remote_file):
            if overwrite:
                logger.warning("File already exists on server. Overwriting it.")
            else:
                logger.error("File already exists on the server. Skipping it")
                return False
        new_file = self.client.root.create(remote_file)
        local = open(local_file, "rb")
        shutil.copyfileobj(local, new_file)
        new_file.close()
        logger.info("File %s uploaded to %s", local_file, remote_file)

    def _upload_dir(self, localpath, remotepath, overwrite: bool=False):
        if self.client.root.pathexists(remotepath):
            logger.warning("Folder already exists on the server.")
        self.client.root.makedirs(remotepath)
        i = 0
        for fn in os.listdir(localpath):
            lfn = os.path.join(localpath, fn)
            rfn = remotepath + "/" + fn
            if os.path.isdir(rfn):
                self._upload_dir(lfn, rfn, overwrite=overwrite)
            else:
                self._upload_file(lfn, rfn, overwrite=overwrite)
            i += 1
        logger.info("Directory %s uploaded. %s files copied", localpath, i)

    def _download_file(self, remote_file, local_file, overwrite: bool=True):
        if self.client.root.pathexists(local_file):
            if overwrite:
                logger.warning("File already exists on the client. Overwriting it.")
            else:
                logger.warning("File already exists on the client, skipping it.")
                return
        remote = self.client.root.open(remote_file)
        new_file = open(local_file, "wb")
        shutil.copyfileobj(remote, new_file)
        logger.info("File %s downloaded to %s", remote_file, local_file)

    def _download_dir(self, remotepath, localpath, overwrite: bool=True):
        if os.path.exists(localpath):
            logger.warning("Folder already exists on the local machine.")
        if not os.path.isdir(localpath):
            os.makedirs(localpath)
        i = 0
        for fn in self.client.root.listdir(remotepath):
            lfn = os.path.join(localpath, fn)
            rfn = remotepath + "/" + fn
            if self.client.root.isdir(rfn):
                self._download_dir(rfn, lfn, overwrite=overwrite)
            else:
                self._download_file(rfn, lfn, overwrite=overwrite)
            i += 1
        logger.info("Directory %s downloaded. %s files copied", localpath, i)

    def open_file(self, remote_file: str, open_options: str="r", encoding: str = None) :
        return self.client.root.open(remote_file, open_options=open_options, encoding=encoding)

    def create_file(self, remote_file: str, create_options: str="w", encoding: str = None, override: bool = True):
        return self.client.root.create(remote_file, open_options=create_options, encoding=encoding, override=override)

    def makedirs(self, remotepath: str) -> str:
        if self.client.root.pathexists(remotepath):
            return "Directory Exists!"
        self.client.root.makedirs(remotepath)
        return "Directory created."

    def walk(self, remotepath: str):
        if self.client.root.pathexists(remotepath):
            return self.client.root.walk(remotepath)

    def listdir(self, remotepath: str):
        if self.client.root.pathexists(remotepath):
            return self.client.root.listdir(remotepath)
        return []

    def pathexists(self, remotepath: str) -> bool:
        if self.client.root.pathexists(remotepath):
            return True
        return False

    def unlink(self, remotepath: str) -> bool:
        if self.client.root.unlink(remotepath):
            return True
        return False

    def normpath(self, remotepath: str) -> str:
        return self.client.root.normpath(remotepath)

    def isdir(self, remotepath: str) -> bool:
        return self.client.root.isdir(remotepath)

    def temp_dir(self) -> str:
        return self.client.root.temp_dir()


def check_port(port: int) -> int:
    """Check for an available port on the machine starting from input port.

    Parameters
    ----------
    port : int
        Ports to search.

    Returns
    -------
    int
        Next Port available.
    """
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    check = False
    while not check:
        try:
            s.bind(("127.0.0.1", port))
            check = True
        except socket.error:
            port += 1
            # stop search at port 30000 (range search 18000 30000 is more then enough for rpc)
            if port > 29999:
                return 0
    s.close()
    return port

class GlobalService(rpyc.Service, PyAedtBase):
    """RPyC service dedicated to a single client session.

    Each ``GlobalService`` runs in its own subprocess (spawned by ``ServiceManager``)
    and exposes AEDT launch and remote file operations to the connected client.
    """

    def on_connect(self, connection):
        """Initiate the service when a connection is created.
        
        This method is called when the connection is established.
        """
        self.connection = connection

    def on_disconnect(self, connection):
        """Finalize the service when the connection is closed.
        
        This method is called when the connection had already terminated for cleanup.
        """
        if is_windows:
            sys.stdout = sys.__stdout__

    @staticmethod
    def exposed_stop() -> None:
        from ansys.aedt.core.generic.settings import settings

        settings.remote_rpc_session = None

        pid = os.getpid()
        os.kill(pid, signal.SIGTERM)

    def exposed_redirect(self, stdout):
        sys.stdout = stdout

    def exposed_restore(self) -> None:
        sys.stdout = sys.__stdout__

    @staticmethod
    def aedt_grpc(
        host: str | None = None,
        port: int | None = None,
        beta_options: list[str] | None = None,
        use_aedt_relative_path: bool = False,
        non_graphical: bool = True,
        secure: bool = True,
        listen_all: bool = False,
    ) -> _AEDTGrpcInfo:
        """Start a new AEDT session on a specified gRPC port.

        .. warning::

            Do not execute this function with untrusted function argument, environment
            variables or pyaedt global settings.
            See the :ref:`security guide<ref_security_consideration>` for details.

        Parameters
        ----------
        host : str, optional
            Host name or IP address to bind the server to.
        port : int, optional
            gRPC port on which the AEDT session will start.
        beta_options : list[str], optional
            List of beta features to enable.
        use_aedt_relative_path : bool, optional
            Whether to use the AEDT executable relative path.
        non_graphical : bool, optional
            Whether to start AEDT in non-graphical mode.
        secure : bool, optional
            Whether to use a secure connection.
        listen_all : bool, optional
            Whether to listen on all network interfaces.

        Returns
        -------
        info : _AEDTGrpcInfo
            Information about the AEDT gRPC session.
        """
        from ansys.aedt.core.generic.general_methods import grpc_active_sessions
        from ansys.aedt.core.generic.settings import settings

        if not port:
            import secrets

            secure_random = secrets.SystemRandom()
            port = check_port(secure_random.randint(18500, 20000))

        sessions = grpc_active_sessions()
        if port == 0:
            raise RuntimeError(f"Provided port {port} cannot be used.")
        elif port in sessions:
            raise RuntimeError(f"AEDT already running on port {port}.")

        ansysem_path = os.getenv("PYAEDT_SERVER_AEDT_PATH", "")
        if is_linux:
            executable = "ansysedt"
        else:
            executable = "ansysedt.exe"
        if ansysem_path and not use_aedt_relative_path:
            aedt_exe = os.path.join(ansysem_path, executable)
            if not is_safe_path(aedt_exe):
                raise RuntimeError("Ansys EM path is not safe.")
        else:
            aedt_exe = executable

        if non_graphical:
            ng_feature = "-features=SF6694_NON_GRAPHICAL_COMMAND_EXECUTION,SF159726_SCRIPTOBJECT"
        else:
            ng_feature = "-features=SF159726_SCRIPTOBJECT"

        if beta_options:
            for option in beta_options:
                if option not in ng_feature:
                    ng_feature += f",{option}"

        # NOTE: Update PyAEDT settings to launch AEDT according to the provided arguments.
        # This approach alignes with how the Desktop class launches AEDT.
        logger.info("Setting PyAEDT's grpc settings to launch AEDT.")
        settings.grpc_secure_mode = secure
        settings.grpc_listen_all = listen_all
        settings.grpc_local = False

        server_args: _ServerArgs = _get_grpcsrv_args(host, port)
        command = [aedt_exe, "-grpcsrv", str(server_args)]
        # NOTE: Update command if PYAEDT_USE_PRE_GRPC_ARGS is set to allow working
        # with previous SP where grpc transport mode were not available
        if os.environ.get("PYAEDT_USE_PRE_GRPC_ARGS", "False") == "True":
            command[-1] = str(port)

        command.append(ng_feature)

        if non_graphical:
            command.append("-ng")

        logger.info(f"Launching AEDT server with gRPC transport mode: {server_args.mode}")
        logger.debug(f"Launching AEDT server with command: {' '.join(command)}")

        process = subprocess.Popen(command)  # nosec

        timeout = settings.desktop_launch_timeout
        while timeout > 0:
            if is_grpc_session_active(port):
                # Find AEDT version key for the current AEDT path
                aedt_version = next((version for version, path in aedt_versions.installed_versions.items() if path == ansysem_path))
                # Settings PYAEDT_DESKTOP_VERSION environment variable to allow using it
                # in the client side. This allows one to not pass the version when calling
                # an AEDT application like `Hfss(host=..., port=...)`.
                os.environ["PYAEDT_DESKTOP_VERSION"] = aedt_version

                res = _AEDTGrpcInfo(
                    version=aedt_version,
                    port=port,
                    host=host
                )
                return res
            # NOTE: Heartbeat to check if the process is still alive is set to 5 to avoid
            # too manynetwork calls while waiting for AEDT to start.
            timeout -= 5
            time.sleep(5)

        process.terminate()
        raise RuntimeError(f"Service did not start within the timeout of {settings.desktop_launch_timeout} seconds.")

    @property
    def aedt_port(self) -> int:
        """AEDT active port.

        Returns
        -------
        int
        """
        from ansys.aedt.core.internal.desktop_sessions import _desktop_sessions

        if _desktop_sessions:
            return list(_desktop_sessions.values())[0].port
        return 0

    @property
    def aedt_version(self) -> str:
        """AEDT Version.

        Returns
        -------
        str
        """
        from ansys.aedt.core.internal.desktop_sessions import _desktop_sessions

        if _desktop_sessions:
            return list(_desktop_sessions.values())[0].aedt_version_id
        return ""

    @property
    def student_version(self) -> bool:
        """Student version flag.

        Returns
        -------
        bool
        """
        from ansys.aedt.core.internal.desktop_sessions import _desktop_sessions

        if _desktop_sessions:
            return list(_desktop_sessions.values())[0].student_version
        return False

    @property
    def host(self) -> str:
        """Machine name.

        Returns
        -------
        str
        """
        import socket

        return socket.getfqdn()

    @staticmethod
    def exposed_open(filename, open_options: str="rb", encoding=None):
        f = open(filename, open_options, encoding=encoding)
        return rpyc.restricted(f, ["read", "readlines", "close"], [])

    @staticmethod
    def exposed_create(filename, create_options: str="wb", encoding=None, override: bool=True):
        if os.path.exists(filename) and not override:
            return "File already exists"
        f = open(filename, create_options, encoding=encoding)
        return rpyc.restricted(f, ["read", "readlines", "write", "writelines", "close"], [])

    @staticmethod
    def exposed_makedirs(remotepath) -> str:
        if os.path.exists(remotepath):
            return "Directory Exists!"
        os.makedirs(remotepath)
        return "Directory created!"

    @staticmethod
    def exposed_listdir(remotepath):
        if os.path.exists(remotepath):
            return os.listdir(remotepath)
        return []

    @staticmethod
    def exposed_pathexists(remotepath) -> bool:
        if os.path.exists(remotepath):
            return True
        return False

    @staticmethod
    def exposed_unlink(remotepath) -> bool:
        if os.unlink(remotepath):
            return True
        return False

    @staticmethod
    def exposed_isdir(remotepath):
        return os.path.isdir(remotepath)

    @staticmethod
    def exposed_tempdir():
        return tempfile.gettempdir()

    @staticmethod
    def normpath(remotepath):
        return os.path.normpath(remotepath)


class ServiceManager(rpyc.Service, PyAedtBase):
    """RPyC service that acts as a dispatcher for PyAEDT remote sessions.

    The ``ServiceManager`` listens on a well-known port (default 17878) and
    handles requests to spawn or stop per-client ``GlobalService`` workers,
    each running in its own subprocess on a dedicated port.
    """

    def on_connect(self, connection):
        """Initiate the service when a connection is created.
        
        This method is called when the connection is established.
        """
        self.connection = connection
        self.__processes: dict[int, subprocess.Popen] = {}

    def on_disconnect(self, connection):
        """Finalize the service when the connection is closed.
        
        This method is called when the connection had already terminated for cleanup.
        """
        for process in self.__processes.values():
            try:
                process.terminate()
            except Exception as e:
                logger.error(f"Error terminating process with PID {process.pid}: {e}")

    def start_service(self, host: str, port: int, secure: bool = True, listen_all: bool = False) -> int | bool:
        """Connect to remove service manager and run a new server on specified port.

        .. warning::

            Do not execute this function with untrusted function argument, environment
            variables or pyaedt global settings.
            See the :ref:`security guide<ref_security_consideration>` for details.

        Parameters
        ----------
        host : str
            Host name or IP address to bind the server to.
        port : int
            Port that the RPyC server is running on inside AEDT.
        secure : bool, optional
            Whether to use a secure connection.
            Default is ``True``.
        listen_all : bool, optional
            Whether the server is listening on all network interfaces.
            Default is ``False``.

        Returns
        -------
        RPyC object.
        """
        try:
            port = check_port(port)
            ansysem_path = os.getenv("PYAEDT_SERVER_AEDT_PATH")
            if ansysem_path and not Path(ansysem_path).exists():
                raise FileNotFoundError(f"The ANSYSEM path '{ansysem_path}' does not exist.")
            elif not ansysem_path:
                version_list = aedt_versions.list_installed_ansysem
                if version_list:
                    ansysem_path = os.environ[version_list[0]]
                else:
                    raise Exception("No ANSYSEM_ROOTXXX environment variable is defined.")

            script_path = Path(__file__).resolve().parent / "local_server.py"
            command = [
                sys.executable, str(script_path),
                "--host", host,
                "--ansysem-path", ansysem_path,
                "--port", str(port),
                "--non-graphical",
            ]
            # Specify grpc related arguments
            if not secure:
                command.append("--no-secure")
            else:
                command.append("--secure")
            if listen_all:
                command.append("--listen-all")

            logger.debug(f"Starting a RPyC GlobalService worker with command: {command}")
            p = subprocess.Popen(command)  # nosec
            time.sleep(2)
            
            self.__processes[port] = p
            return port
        except Exception:
            logger.error("Error. No connection exists. Check if AEDT is running and if the port number is correct.")
            return False

    def stop_service(self, port: int) -> bool:
        """Stops a given Pyaedt Service on specified port.

        Parameters
        ----------
        port : int
            Port id on which there is the service to kill.

        Returns
        -------
        bool
        """
        if port in self.__processes.keys():
            try:
                self.__processes[port].terminate()
                return True
            except Exception:
                return False

        return True

    @staticmethod
    def exposed_check_port() -> int:
        """Check if a random port is available."""
        import secrets

        secure_random = secrets.SystemRandom()
        port = check_port(secure_random.randint(18500, 20000))
        return port
