# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 - 2026 ANSYS, Inc. and/or its affiliates.
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

import os
from pathlib import Path
import signal
import socket
import sys
import tempfile
import time

import rpyc
from rpyc import Connection
from rpyc.core import consts
from rpyc.utils.server import OneShotServer
from rpyc.utils.server import ThreadedServer

from ansys.aedt.core.aedt_logger import pyaedt_logger as logger
from ansys.aedt.core.generic.settings import settings
from ansys.aedt.core.internal.aedt_versions import aedt_versions

# import sys
from ansys.aedt.core.internal.errors import AEDTRuntimeError
from ansys.aedt.core.rpc.rpyc_services import FileManagement
from ansys.aedt.core.rpc.rpyc_services import GlobalService
from ansys.aedt.core.rpc.rpyc_services import ServiceManager
from ansys.aedt.core.rpc.rpyc_services import _AEDTGrpcInfo
from ansys.aedt.core.rpc.rpyc_services import check_port

# Maximum Stream message size. Set to 256MB
consts.STREAM_CHUNK = 256000000


safe_attrs = {
    "__abs__",
    "__add__",
    "__and__",
    "__bool__",
    "__class__",
    "__code__",
    "__contains__",
    "__delitem__",
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
    "__fspath__",
    "__getitem__",
    "__gt__",
    "__hash__",
    "__iadd__",
    "__iand__",
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
    "__lshift__",
    "__lt__",
    "__mod__",
    "__mul__",
    "__name__",
    "__ne__",
    "__neg__",
    "__new__",
    "__or__",
    "__pos__",
    "__pow__",
    "__radd__",
    "__rand__",
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
    "__str__",
    "__sub__",
    "__truediv__",
    "__xor__",
    "__length_hint__",
    "__enter__",
    "__exit__",
    "__next__",
    "__format__",
}


def pyaedt_service_manager(
    host: str | None = None,
    port: int = 17878,
    aedt_version: str | None = None,
    student_version: bool | None = False,
) -> None:
    """Start the PyAEDT service manager using RPyC server on CPython.

    This method, which must run on a server machine, is used as a service on the
    server machine to listen on a dedicated port for inbound requests to launch
    a new server connection and launch AEDT.

    Parameters
    ----------
    host: str, optional
        Host name or IP address to bind the server to.
        Default is ``None`` in which case the AEDT_HOST variable is used or the
        machine's host name.
    port : int, optional
        Port that the RPyC server is to listen on.
        Default is ``17878``.
    aedt_version : str, optional
        Version of AEDT to instantiate with server.
        Default is latest available version installed on the machine.
    student_version : bool, optional
        Either to initialize Student version AEDT or Commercial version.
        Default is ``False`` which means Commercial version.

    Examples
    --------
    >>> from ansys.aedt.core.common_rpc import pyaedt_service_manager
    >>> pyaedt_service_manager()

    """
    from ansys.aedt.core.generic.general_methods import _normalize_version_to_string

    port1 = check_port(port)
    if port1 == 0:
        raise RuntimeError(f"Provided port {port} cannot be used.")
    if port1 != port:
        logger.info(f"Port {port} is already in use. Starting the server on port {port1}.")

    installed_versions: dict[str, str] = aedt_versions.installed_versions

    if aedt_version:
        version = _normalize_version_to_string(aedt_version)
        if student_version:
            version += "SV"
        if version not in installed_versions:
            begin_msg = "Student version" if student_version else "Version"
            raise RuntimeError(f"{begin_msg} {aedt_version} is not installed on this machine.")
    else:
        if student_version:
            version = next((key for key in installed_versions if key.endswith("SV")))
        version = next(iter(installed_versions.keys()))

    ansysem_path = installed_versions[version]
    logger.info(f"AEDT located at {ansysem_path} will be used.")
    os.environ["PYAEDT_SERVER_AEDT_PATH"] = ansysem_path
    os.environ["PYAEDT_SERVER_AEDT_NG"] = "True"
    os.environ["ANS_NODEPCHECK"] = str(1)

    if host is None:
        logger.debug("No host provided. Using AEDT_HOST environment variable or machine's host.")
        default_host = socket.gethostname()
        host = os.getenv("AEDT_HOST", default_host)

    server = ThreadedServer(
        ServiceManager,
        hostname=host,
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
    logger.info(f"Starting the service manager on port {port} on {host}.")
    server.start()


def launch_server(
    host: str | None = None,
    port: int = 18000,
    ansysem_path: str | None = None,
    non_graphical: bool | None = False,
    threaded: bool = True,
    secure: bool = True,
    listen_all: bool = False,
) -> bool:  # pragma: no cover
    """Start an RPyC server and listens on a specified port.

    This method must run on a server machine only.

    Parameters
    ----------
    host : str, optional
        Host name or IP address to bind the server to.
        Default is ``None`` in which case the AEDT_HOST variable is used or the
        machine's host name.
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
    >>> from ansys.aedt.core.common_rpc import launch_server
    >>> launch_server()

    """
    port1 = check_port(port)
    if port1 == 0:
        raise RuntimeError(f"Provided port {port} cannot be used.")
    if port1 != port:
        logger.info(f"Port {port} is already in use. Starting the server on port {port1}.")

    if not ansysem_path:
        installed_versions: dict[str, str] = aedt_versions.installed_versions
        try:
            ansysem_path = next(iter(installed_versions.values()))
        except StopIteration as e:
            raise Exception("No ANSYSEM_ROOTXXX environment variable defined.") from e

    logger.info(f"AEDT located at {ansysem_path} will be used.")
    os.environ["PYAEDT_SERVER_AEDT_PATH"] = ansysem_path
    os.environ["PYAEDT_SERVER_AEDT_NG"] = str(non_graphical)
    os.environ["ANS_NO_MONO_CLEANUP"] = "1"
    os.environ["ANS_NODEPCHECK"] = "1"

    # RPyC servers are by definition remote, so grpc_local must be False.
    # Otherwise GlobalService.aedt_grpc() will reject the call.
    logger.info("Setting PyAEDT's grpc settings for RPyC server.")
    settings.grpc_local = False
    settings.grpc_secure_mode = secure
    settings.grpc_listen_all = listen_all

    if host is None:
        logger.debug("Host not provided. Using AEDT_HOST environment variable or machine's host name.")
        default_host = socket.gethostname()
        host = os.getenv("AEDT_HOST", default_host)
    if host == "0.0.0.0":  # nosec
        logger.warning("The service is exposed on all network interfaces. This is a security risk.")

    if threaded:
        service = ThreadedServer
    else:
        service = OneShotServer
    server = service(
        GlobalService,
        hostname=host,
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
    signal.signal(signal.SIGINT, lambda signum, frame: server.close())
    signal.signal(signal.SIGTERM, lambda signum, frame: server.close())
    logger.info(f"Starting the global service on port '{port}' on '{host}'.")
    server.start()


def create_session(
    host: str,
    client_port: int | None = None,
    launch_aedt_on_server: bool | None = False,
    aedt_port: int | None = None,
    non_graphical: bool | None = False,
    secure: bool | None = True,
    listen_all: bool | None = False,
) -> Connection:  # pragma: no cover
    """Connect to an existing server session and create a new client session from it.

    Parameters
    ----------
    host : str
        Host name or IP address to bind the server to.
    client_port : int
        Port that the RPyC server will run.
    launch_aedt_on_server : bool, optional
        Either if the method has to start AEDT after the connection is established or not. Default is  `False`.
    aedt_port : int, optional
        AEDT gRPC port on remote.
    non_graphical : bool, optional
        AEDT non-graphical flag.
    secure : bool, optional
        Whether to use secure connection to the server.
        Default is ``True``.
    listen_all : bool, optional
        Whether the server is listening on all network interfaces.
        Default is ``False``.

    Returns
    -------
    RPyC client object.
    """
    try:
        client = rpyc.connect(
            host,
            settings.remote_rpc_service_manager_port,
            config={"allow_public_attrs": True, "sync_request_timeout": None},
        )

        if not client_port:
            client_port = client.root.check_port()
        port = client.root.start_service(host, client_port, secure=secure, listen_all=listen_all)
        time.sleep(1)

        cl = connect(host, port)
        logger.info("Created new session on port %s", port)
        # NOTE: Keep the ServiceManager connection alive by attaching it to the
        # GlobalService client object.  If this reference is dropped, Python's GC
        # will close the ServiceManager connection which triggers on_disconnect and
        # terminates every GlobalService subprocess it spawned – closing the stream
        # underneath cl and making it unusable.
        cl._service_manager_connection = client
        if "host" not in dir(cl):
            cl.host = host
        if "aedt_port" not in dir(cl):
            cl.aedt_port = None

        if launch_aedt_on_server:
            logger.info(f"Launching AEDT on {host}.")
            if not aedt_port:
                aedt_port = client.root.check_port()

            aedt_grpc_info: _AEDTGrpcInfo = cl.aedt(
                host=host, port=aedt_port, non_graphical=non_graphical, secure=secure, listen_all=listen_all
            )

            logger.info(f"AEDT {aedt_grpc_info.version} started on port {aedt_grpc_info.port}")
            # Updating client with AEDT information.
            cl.aedt_port = aedt_grpc_info.port
            cl.aedt_version = aedt_grpc_info.version

        return cl
    except Exception:
        msg = (
            "Failed to create a new session on the server. "
            "Please check your settings, if the PyAEDT service manager "
            "is running, and if the port number is correct."
        )
        logger.error(msg)
        raise


def connect(host: str, aedt_client_port: int) -> Connection:  # pragma: no cover
    """Connect to an existing server session.

    Parameters
    ----------
    host : str
        Host name or IP address.
    aedt_client_port : int
        Port that the RPyC server is running on.

    Returns
    -------
    RPyC client object.
    """
    try:
        client = rpyc.connect(host, aedt_client_port, config={"allow_public_attrs": True, "sync_request_timeout": None})

        # Redirect server stdout to the local stdout
        client.root.redirect(sys.stdout)
        # Attach a helper for remote file operations
        client.filemanager = FileManagement(client)

        # NOTE: Map commonly used remote entry points to the client object if present.
        # This monkey-patching is admittedly a bit hacky, but it allows us to expose commonly
        # used server methods directly on the client object for easier access.
        # We can revisit this design if it proves problematic.
        try:
            client.aedt = client.root.aedt_grpc  # Method to launch AEDT via gRPC
            client.open_file = client.root.open
            client.create_file = client.root.create
            client.list_dir = client.root.listdir
            client.makedirs = client.root.makedirs
            client.pathexists = client.root.pathexists
            client.close_session = client.root.stop
            client.aedt_port = client.root.aedt_port
            client.aedt_version = client.root.aedt_version
            client.student_version = client.root.student_version
            client.host = client.root.host
        except AttributeError:
            logger.debug("Remote service does not expose all expected attributes; some helpers were not attached.")

        # Register session and create a session-scoped temp folder
        settings.remote_rpc_session = client
        temp_folder = Path(tempfile.gettempdir()) / f"{host}_{aedt_client_port}"
        settings.remote_rpc_session_temp_folder = temp_folder
        try:
            temp_folder.mkdir(parents=True, exist_ok=True)
        except Exception:
            logger.warning("Could not create remote session temp folder %s", temp_folder)

        return client
    except Exception as exc:
        raise AEDTRuntimeError(f"Failed to connect to remote service at {host}:{aedt_client_port}.") from exc
